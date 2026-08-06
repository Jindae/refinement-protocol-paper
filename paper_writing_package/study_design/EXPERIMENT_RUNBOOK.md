# Experiment Operator Runbook

이 문서는 pilot부터 본실험의 모델 산출물 생성과 candidate 평가 완료까지 실행자가 명령을 순서대로
복사해 실행하기 위한 운영 절차다. 연구 설계는 `documents/`가 정의하며, 이 문서는
그 설계를 실행하는 명령만 제공한다.

## 1. 공통 규칙

- 모든 명령은 `/data/refinement-protocol`에서 실행한다.
- `--start`는 장기 작업을 분리된 background session으로 시작한 뒤 즉시 반환한다.
- 완료를 기다리는 polling loop나 `sleep`을 실행하지 않는다. 필요할 때 `--count` 또는
  `--status`를 한 번씩 실행한다.
- `state=completed`만으로 다음 단계로 넘어가지 않는다. 반드시 해당 `--validate`가
  성공해 `validation_result=passed`가 된 뒤 진행한다.
- 실패 attempt는 삭제하거나 같은 attempt ID로 덮어쓰지 않는다. 아래 resume 절차로
  새 attempt를 만든다.
- Pilot inference 결과를 검토하고 prompt freeze 결정을 기록하기 전에는 primary를
  시작하지 않는다.
- 실행기는 `scripts/`, `src/`, `configs/`, project metadata와 dependency lock 등 실제 실행
  input이 commit된 상태만 허용한다. 다음 명령으로 전체 상태를 검토하되, 실행에서 읽지
  않는 별도 untracked 연구 노트는 launcher가 차단하지 않는다. 실행 input 경로에는
  출력이 없어야 한다.

```bash
cd /data/refinement-protocol
./scripts/validate.sh
git status --short
```

### 1.1 실행 단계 용어

이 runbook에서 단계 이름은 다음 의미로만 사용한다.

- **전체 범위 모델 산출물 생성 campaign**: 여섯 모델과 1,677개 task에 대해 아래의
  canonical model-call phase를 모두 수행한다.

Canonical phase 순서는 다음과 같다.

1. Direct Generation
2. Refinement-Need Decision
3. Direct Revision
4. Critique Generation
5. Critique-Conditioned Revision
6. Revision Planning
7. Plan-Conditioned Revision

- **Initial candidate 생성 phase**: 위 campaign의 첫 phase인 Direct Generation이며 initial
  candidate만 생성한다. 이것만을 전체 campaign과 같은 뜻으로 부르지 않는다.
- **Invalid Decision 판정**: 전체 모델 산출물 생성이 끝난 뒤 strict parser가 거부한
  Decision만 benchmark 평가결과를 보지 않고 고정 rubric으로 방향을 판독하는 별도 비모델 단계다.
- **전체 candidate 평가 campaign**: 저장된 Direct, `R`, `CR`, `CPR` candidate를
  benchmark evaluator로 실행하는 별도 단계다. 이때 `primary` evaluation은 본실험이라는
  뜻이 아니라 timeout confirmation에 앞선 **1차 평가 attempt**를 뜻한다.
- **본실험**: pilot이 아닌 전체 frozen scope 실행 전체를 가리키며, 특정 phase의 이름이
  아니다.

`R`, `CR`, `CPR`은 phase 이름이 아니라 candidate condition 또는 protocol 표기다.
Direct Revision이 `R` candidate를 만들고, Critique Generation과 Critique-Conditioned
Revision의 결과가 `CR`이다. `CPR`은 Critique Generation, Revision Planning,
Plan-Conditioned Revision을 거쳐 생성된다.

Configuration identifier `primary-inference-...`의 `inference`는 본실험용 model-serving
설정이라는 뜻이다. Direct-only 실행 단계 이름이 아니다.
Status JSON의 `phase`는 resume/provenance 호환성을 위한 machine identifier다. 별도의
read-only operator monitor가 이를 위 canonical phase 이름으로 표시하며 experiment worker나
저장 artifact를 변경하지 않는다.

### 1.2 Replacement-model serving gate

새 모델 세 snapshot은 독립 검증을 통과했다. Pilot을 준비하기 전에 기존 공통 vLLM
0.26.0 환경에서 새 모델 3종을 순차 로드하고, 16K·TP=2·batch-invariant generation과
현재 candidate fence contract를 검증한다. 이 단계는 validation-only이며 benchmark
task나 실험 candidate를 생성하지 않는다.

```bash
.venv/bin/python scripts/smoke_vllm_models.py --start \
  --attempt-id vllm-smoke-new-models-20260804-r2 \
  --configuration-path configs/inference/vllm_new_models_smoke_r2.toml
```

진행률과 상세 상태는 필요할 때 한 번씩 확인한다.

```bash
.venv/bin/python scripts/smoke_vllm_models.py --count \
  --configuration-path configs/inference/vllm_new_models_smoke_r2.toml
.venv/bin/python scripts/smoke_vllm_models.py --status \
  --configuration-path configs/inference/vllm_new_models_smoke_r2.toml
tail -f runs/logs/vllm-model-smoke/vllm-smoke-new-models-20260804-r2/smoke.log
```

`completed` 뒤에는 반드시 독립 검증을 통과시킨다.

```bash
.venv/bin/python scripts/validate_vllm_model_smoke.py \
  runs/logs/vllm-model-smoke/vllm-smoke-new-models-20260804-r2 \
  --configuration configs/inference/vllm_new_models_smoke_r2.toml
```

Terminal `r1`은 Devstral의 rendered-string retokenization이 canonical chat-template ID와
다른 것을 발견해 serving certification으로 invalidated했다. `r2`는 모든 모델에 대해
`tokenize=True`의 exact token IDs를 generation input으로 직접 사용한다.

실제 weight load가 실패하기 전에는 환경을 변경하지 않는다. 실패하면 기존 attempt와
raw log를 보존하고 원인을 분석한 뒤, 필요한 경우에만 여섯 모델 전체에 적용할 하나의
replacement serving environment를 준비한다.

## 2. Pilot inference

Pilot은 hidden test를 사용하지 않고 각 benchmark의 public specification 길이에서
최소·중앙·최대 항목을 선택한 3개씩, 총 9개 task를 사용한다. Adopted `study-v0.2.0`의
replacement pilot은 여섯 모델 모두 같은 9개 task와 동일한 7개 phase를 실행한다.
Candidate response의 정확히 하나인 Python fence만 공통 추출하고, critique/plan의
focused code snippet을 허용하는 `primary-prompts-2026-08-04-draft3` contract는 유지한다.
이전 `draft1`/`draft2`/four-model `draft3` configuration과 artifacts는 변경하거나 새
scope로 재해석하지 않는다.

Full-panel runtime smoke가 6/6 통과했으므로 `primary-inference-2026-08-04-r3`와 기존
vLLM 0.26.0 environment는 replacement pilot에 동결되었다. 현재 실행 대상은
`pilot_campaign_six_models.toml`이며, 이전 `pilot_campaign_draft3.toml`은 terminal
four-model history로서 다시 실행하지 않는다.

### 2.1 Preflight

이 명령은 six-model checkpoint hash, Python/vLLM, GPU 여유, prompt/configuration hash와
정확한 9-task public scope를 검사하지만 model weight를 로드하지 않는다.

```bash
.venv/bin/python scripts/run_model_campaign.py --preflight \
  --campaign-configuration configs/experiments/pilot_campaign_six_models.toml
```

`validation_result`가 `passed`, `execution_gate`가 `enabled`, `task_count`가 `9`인지
확인한다.

### 2.2 Background 시작

```bash
export PILOT_INFERENCE_ATTEMPT="campaign-pilot-six-models-$(date -u +%Y%m%dT%H%M%SZ)"
.venv/bin/python scripts/run_model_campaign.py --start \
  --attempt-id "$PILOT_INFERENCE_ATTEMPT" \
  --campaign-configuration configs/experiments/pilot_campaign_six_models.toml
```

출력되는 attempt ID, run ID, PID, status path, log path를 보관한다.

### 2.3 진행 확인

간단한 count:

```bash
.venv/bin/python scripts/run_model_campaign.py --count
```

상세 status와 log 갱신 시각:

```bash
.venv/bin/python scripts/run_model_campaign.py --status
```

실시간 log가 필요할 때만 start 출력의 `tail -f .../run.log` 명령을 사용하고,
종료할 때 `Ctrl-C`를 누른다. 이는 experiment worker를 중단하지 않는다.

### 2.4 완료 검증과 run ID 저장

`--count`가 `completed`라고 표시한 뒤 실행한다.

```bash
.venv/bin/python scripts/run_model_campaign.py --validate
export PILOT_INFERENCE_RUN_ID="$(.venv/bin/python scripts/run_model_campaign.py --show-run-id)"
printf '%s\n' "$PILOT_INFERENCE_RUN_ID"
```

`--validate`가 실패하면 evaluation을 시작하지 않는다.

### 2.5 Invalid Decision 일괄 판정

Evaluation preflight 전에 strict parser가 거부한 Decision 수와 검토 경로를 확인한다.

```bash
.venv/bin/python scripts/adjudicate_decisions.py \
  --inference-run-id "$PILOT_INFERENCE_RUN_ID" \
  --list-invalid
```

`invalid_decision_count`가 0이면 바로 3단계로 간다. 1 이상이면 출력에 있는 raw response,
task record, exact initial candidate만 `configs/adjudication/decision_rubric.toml`에 따라
검토한다. Evaluation, reference solution, tests, runtime, timeout, critique, plan과 revised
candidate는 열람하지 않는다. 모든 invalid call을 포함한
`decision-adjudication-input-v1` JSON을 준비하고 다음 foreground 명령으로 한 번 기록한다.
명백한 방향이 없으면 `status`를 `unresolved`로 두고 `decision`을 생략한다.

```bash
export DECISION_ADJUDICATION_ID="decision-adjudication-$(date -u +%Y%m%dT%H%M%SZ)"
.venv/bin/python scripts/adjudicate_decisions.py \
  --inference-run-id "$PILOT_INFERENCE_RUN_ID" \
  --adjudication-id "$DECISION_ADJUDICATION_ID" \
  --input /absolute/path/to/decision-adjudication-input.json
.venv/bin/python scripts/validate_decision_adjudication.py \
  --adjudication-id "$DECISION_ADJUDICATION_ID"
```

Evaluation preflight는 invalid Decision이 있는데 independently validated adjudication이
없으면 거부한다. Primary scope에서는 평가 descendant가 생긴 뒤 `pre_evaluation` 판정을
소급 기록하는 것도 거부한다. Pilot review 명령에서 사용할
`DECISION_ADJUDICATION_ID`를 보관한다.

## 3. Pilot candidate evaluation

이 단계는 Direct, `R`, `CR`, `CPR`로 실제 생성된 모든 candidate를 대상으로 세
benchmark를 한 background session에서 평가한다. 먼저 10초 기본값과 frozen slow-task
override로 primary batch 전체를 완료하고, primary timeout만 사전 고정된 confirmation
timeout으로 한 번 확인한 뒤 final resolution을 만든다. 기본 confirmation은
`max(120초, 1.5 × primary)`이며 `HumanEval/38`, `/50`, `/53`은 180초다. Evaluation
결과는 inference prompt로 돌아가지 않는다.

EvalPlus adapter `self-refinement-isolated-v4`는 benchmark input, expected output, oracle을
수정하지 않는다. EvalPlus 0.3.1이 일반 false detail로 합치는 입력별 timeout index만 raw
output에 추가로 기록하고, false detail이 전부 timeout으로 설명될 때 provisional
`TIMEOUT`으로 보내 confirmation에서 다시 확인한다. Timeout과 별개인 failing detail이
하나라도 있으면 functional `FAIL`이 우선한다. Preflight 출력에서 EvalPlus manifest
`evalplus-benchmarks-2026-08-04-r5`, adapter `v4`, 두 evaluator manifest hash를 확인한다.

새 shell을 열었다면 inference run ID를 다시 읽는다.

```bash
export PILOT_INFERENCE_RUN_ID="$(.venv/bin/python scripts/run_model_campaign.py --show-run-id)"
```

### 3.1 Preflight

```bash
.venv/bin/python scripts/run_evaluation_campaign.py --preflight \
  --source-run-id "$PILOT_INFERENCE_RUN_ID"
```

source scope, candidate 수, protocol별 수, timeout policy가 예상과 일치하는지 확인한다.

### 3.2 Background 시작

```bash
export PILOT_EVALUATION_ATTEMPT="evaluation-pilot-$(date -u +%Y%m%dT%H%M%SZ)"
.venv/bin/python scripts/run_evaluation_campaign.py --start \
  --attempt-id "$PILOT_EVALUATION_ATTEMPT" \
  --source-run-id "$PILOT_INFERENCE_RUN_ID"
```

### 3.3 진행 확인

```bash
.venv/bin/python scripts/run_evaluation_campaign.py --count
.venv/bin/python scripts/run_evaluation_campaign.py --status
```

Count는 현재 `first_pass_evaluation` 또는 `confirmation` phase, timeout 수, evaluator
failure 수와 benchmark별 완료 수를 표시한다. 완료 시 `first_pass_timeout`과
`final_timeout`을 구분한다.

### 3.4 완료 검증과 run ID 저장

```bash
.venv/bin/python scripts/run_evaluation_campaign.py --validate
export PILOT_EVALUATION_RUN_ID="$(.venv/bin/python scripts/run_evaluation_campaign.py --show-run-id)"
printf '%s\n' "$PILOT_EVALUATION_RUN_ID"
```

## 4. Pilot review gate

다음 명령은 model/stage별 parser 상태, output-limit 종료, candidate/Decision/derived
artifact 수, final evaluation resolution과 대표 raw-response 경로를 한 보고서로 만든다.
또한 10초 primary에서 timeout이 발생한 모든 candidate를 최종 결과와 무관하게 별도
목록으로 남기고, primary/confirmation 각각의 timeout, 실제 elapsed time, status,
functional outcome, evaluation record와 raw evaluator output 경로를 함께 기록한다.

```bash
export PILOT_REVIEW_ID="pilot-review-$(date -u +%Y%m%dT%H%M%SZ)"
.venv/bin/python scripts/review_pilot.py \
  --inference-run-id "$PILOT_INFERENCE_RUN_ID" \
  --evaluation-run-id "$PILOT_EVALUATION_RUN_ID" \
  --decision-adjudication-id "$DECISION_ADJUDICATION_ID" \
  --report-id "$PILOT_REVIEW_ID"
```

Invalid Decision이 0개여서 adjudication을 만들지 않았다면
`--decision-adjudication-id` 줄을 생략한다.

출력된 `report.json`에서 다음을 확인한다.

1. `automated_gate`가 `passed`인지 확인한다.
2. `manual_raw_response_review_paths`의 model/stage 대표 응답을 읽는다.
3. 지시 준수, 불필요한 반복, code fence, critique/plan 품질을 검토한다.
4. `primary_timeout_confirmations` 필드에서 짧은 1차 평가 timeout이 120/180초 confirmation에서
   `PASS`, `FAIL`, `TIMEOUT` 중 무엇으로 확정되었는지와 실제 시간을 확인한다.
5. `automated_gate=review_required`이면 원인을 해결하고 새 pilot version과 새 run을 만든다.
6. Prompt를 그대로 채택하거나 수정할지 decision log에 기록한다.

Pilot functional `FAIL`은 정상적인 모델 결과이므로 그 자체로 gate 실패가 아니다.
반면 evaluator failure, 미확정 timeout, malformed response, 누락 artifact 또는
output-limit 종료는 primary 실행 전에 검토해야 한다.

## 5. Final-timeout diagnostic

이 도구는 independently validated evaluation run의 최종 `TIMEOUT`만 사용자가 지정한
wall timeout으로 다시 실행한다. 기존 evaluation attempt, resolution, functional outcome은
수정하거나 재분류하지 않으며 diagnostic raw output과 report를 별도 attempt에 보존한다.
기본값은 같은 task와 exact source SHA-256을 한 번만 실행하고 해당 결과가 대표하는 모든
candidate ID를 report에 기록한다. `--per-candidate`를 추가하면 중복 source도 candidate별로
각각 실행한다.

### 5.1 대상과 최대 실행시간 확인

```bash
export TIMEOUT_DIAGNOSTIC_SECONDS=60
export TIMEOUT_DIAGNOSTIC_ID="timeout-diagnostic-$(date -u +%Y%m%dT%H%M%SZ)"
.venv/bin/python scripts/diagnose_candidate_timeouts.py --preflight \
  --evaluation-run-id "$PILOT_EVALUATION_RUN_ID" \
  --timeout-seconds "$TIMEOUT_DIAGNOSTIC_SECONDS"
```

`diagnostic_execution_count × timeout_seconds`가 5분 이하이면 foreground 실행을 사용한다.

```bash
.venv/bin/python scripts/diagnose_candidate_timeouts.py --run \
  --attempt-id "$TIMEOUT_DIAGNOSTIC_ID" \
  --evaluation-run-id "$PILOT_EVALUATION_RUN_ID" \
  --timeout-seconds "$TIMEOUT_DIAGNOSTIC_SECONDS"
```

10분 이상 걸릴 수 있거나 session 종료 후에도 계속되어야 하면 background로 시작한다.

```bash
.venv/bin/python scripts/diagnose_candidate_timeouts.py --start \
  --attempt-id "$TIMEOUT_DIAGNOSTIC_ID" \
  --evaluation-run-id "$PILOT_EVALUATION_RUN_ID" \
  --timeout-seconds "$TIMEOUT_DIAGNOSTIC_SECONDS"
```

### 5.2 모니터링과 검증

```bash
.venv/bin/python scripts/diagnose_candidate_timeouts.py --count
.venv/bin/python scripts/diagnose_candidate_timeouts.py --status
.venv/bin/python scripts/diagnose_candidate_timeouts.py --validate
```

한 candidate만 확인하려면 `--candidate-record-id candidate_...`를 preflight와 실행 명령에
동일하게 추가한다. Diagnostic에서 더 긴 timeout으로 `PASS`가 나오더라도 기존 최종
`TIMEOUT`을 바꾸지 않는다. Primary 전에 timeout construct를 변경하려면 별도 decision,
새 policy version 및 해당 policy로 생성한 새 evaluation run이 필요하다.

## 6. 실패 후 resume

### 6.1 Inference resume

먼저 원인을 수정하고 repository validation과 commit을 완료한다. Process 중단 때문에
record가 누락된 경우에는 아래 명령에서 `--retry-failed`를 빼고 실행한다. 이미 명시적
inference/extraction failure record가 있으며 같은 frozen construct 아래 구현 결함만
고쳐 재시도하는 경우에는 아래처럼 `--retry-failed`를 포함한다.

```bash
export INFERENCE_RUN_ID="$(.venv/bin/python scripts/run_model_campaign.py --show-run-id)"
export FAILED_INFERENCE_ATTEMPT="$PILOT_INFERENCE_ATTEMPT"
export RESUME_INFERENCE_ATTEMPT="campaign-pilot-resume-$(date -u +%Y%m%dT%H%M%SZ)"
.venv/bin/python scripts/run_model_campaign.py --start \
  --attempt-id "$RESUME_INFERENCE_ATTEMPT" \
  --resume-run-id "$INFERENCE_RUN_ID" \
  --predecessor-attempt-id "$FAILED_INFERENCE_ATTEMPT" \
  --retry-failed \
  --campaign-configuration configs/experiments/pilot_campaign_draft3.toml
```

검증된 completed call은 `--retry-failed`가 있어도 재생성되지 않는다. Configuration이나
public scope hash가 달라졌다면 resume가 거부되며, 결과에 영향을 주는 변경에는 새
version과 새 run이 필요하다.

### 6.2 Evaluation resume

Evaluation resume는 host/process 중단으로 일부 record가 아예 없는 경우에만 사용한다.
이미 `evaluation_failure` record가 저장된 경우에는 기존 run을 보존하고, 원인 해결 후
새 evaluation attempt를 `--resume-evaluation-run-id` 없이 시작하여 replacement run을
만든다.

```bash
export EVALUATION_RUN_ID="$(.venv/bin/python scripts/run_evaluation_campaign.py --show-run-id)"
export FAILED_EVALUATION_ATTEMPT="$PILOT_EVALUATION_ATTEMPT"
export RESUME_EVALUATION_ATTEMPT="evaluation-pilot-resume-$(date -u +%Y%m%dT%H%M%SZ)"
.venv/bin/python scripts/run_evaluation_campaign.py --start \
  --attempt-id "$RESUME_EVALUATION_ATTEMPT" \
  --resume-evaluation-run-id "$EVALUATION_RUN_ID" \
  --predecessor-attempt-id "$FAILED_EVALUATION_ATTEMPT" \
  --source-run-id "$PILOT_INFERENCE_RUN_ID"
```

이미 저장된 primary/confirmation/resolution record는 재사용되고 누락된 대상만 이어서
처리된다. 같은 evaluation run 안에서 기록된 evaluator failure를 덮어쓰거나 재평가하지
않는다.

## 6. Primary freeze 상태

Six-model replacement pilot의 inference, Decision adjudication, adapter-v4 evaluation 및
review가 모두 독립 검증을 통과했다. `DEC-20260804-31`은 검토된 draft3 template bytes를
`primary-prompts-2026-08-04-r1`로 동결하고, full scope campaign
`model-campaign-2026-08-04-r2`를 활성화한다.

Primary가 읽는 exact configuration은 다음 두 파일이다.

- `configs/prompts/primary_frozen.toml`
- `configs/experiments/model_campaign_six_models.toml`

기존 `configs/experiments/model_campaign.toml`은 `study-v0.1.6` four-model history의 exact
bytes를 보존하므로 primary에 사용하지 않는다. Frozen prompt, model panel, scope,
inference, evaluator, timeout, Decision rubric 또는 parser의 outcome-affecting 변경은 이
campaign에 적용하지 않고 새 study/configuration version과 pilot impact assessment를 만든다.

## 7. 전체 범위 모델 산출물 생성 campaign

Section 6의 freeze commit 이후에만 실행한다.

```bash
./scripts/validate.sh
git status --short
.venv/bin/python scripts/run_model_campaign.py --preflight \
  --campaign-configuration configs/experiments/model_campaign_six_models.toml
```

Preflight의 scope가 1,677개이고 gate가 enabled인지 확인한 후:

```bash
export MODEL_ARTIFACT_ATTEMPT="campaign-full-artifacts-$(date -u +%Y%m%dT%H%M%SZ)"
.venv/bin/python scripts/run_model_campaign.py --start \
  --attempt-id "$MODEL_ARTIFACT_ATTEMPT" \
  --campaign-configuration configs/experiments/model_campaign_six_models.toml
```

모니터링과 검증:

```bash
.venv/bin/python operator_tools/model_campaign_progress.py --count
.venv/bin/python operator_tools/model_campaign_progress.py --status
.venv/bin/python scripts/run_model_campaign.py --validate
export MODEL_ARTIFACT_RUN_ID="$(.venv/bin/python scripts/run_model_campaign.py --show-run-id)"
printf '%s\n' "$MODEL_ARTIFACT_RUN_ID"
```

`--validate`는 `completed` 이후에만 실행한다.

## 8. Primary Decision adjudication과 candidate evaluation

### 8.1 Invalid Decision 일괄 판정

Inference validation 직후, evaluation을 시작하기 전에 invalid Decision 전체를 확인한다.

```bash
.venv/bin/python scripts/adjudicate_decisions.py \
  --inference-run-id "$MODEL_ARTIFACT_RUN_ID" \
  --list-invalid
```

0개이면 adjudication 없이 8.2로 간다. 1개 이상이면 Section 2.5와 동일하게 오직 raw
Decision response, prompt-visible task specification, exact initial candidate만 사용하여
모든 invalid case를 하나의 input JSON에 기록한다. Evaluation/reference/test/runtime과
후속 artifact는 보지 않는다.

```bash
export PRIMARY_DECISION_ADJUDICATION_ID="decision-adjudication-primary-$(date -u +%Y%m%dT%H%M%SZ)"
.venv/bin/python scripts/adjudicate_decisions.py \
  --inference-run-id "$MODEL_ARTIFACT_RUN_ID" \
  --adjudication-id "$PRIMARY_DECISION_ADJUDICATION_ID" \
  --input /absolute/path/to/decision-adjudication-input.json
.venv/bin/python scripts/validate_decision_adjudication.py \
  --adjudication-id "$PRIMARY_DECISION_ADJUDICATION_ID"
```

Invalid case가 남아 있는데 이 validation을 통과하지 않으면 evaluation preflight가
거부된다. `UNRESOLVED`는 임의의 binary label로 대체하지 않는다.

### 8.2 Candidate evaluation

```bash
.venv/bin/python scripts/run_evaluation_campaign.py --preflight \
  --source-run-id "$MODEL_ARTIFACT_RUN_ID"
export CANDIDATE_EVALUATION_ATTEMPT="evaluation-full-candidates-$(date -u +%Y%m%dT%H%M%SZ)"
.venv/bin/python scripts/run_evaluation_campaign.py --start \
  --attempt-id "$CANDIDATE_EVALUATION_ATTEMPT" \
  --source-run-id "$MODEL_ARTIFACT_RUN_ID"
```

모니터링과 검증:

```bash
.venv/bin/python scripts/run_evaluation_campaign.py --count
.venv/bin/python scripts/run_evaluation_campaign.py --status
.venv/bin/python scripts/run_evaluation_campaign.py --validate
export CANDIDATE_EVALUATION_RUN_ID="$(.venv/bin/python scripts/run_evaluation_campaign.py --show-run-id)"
printf '%s\n' "$CANDIDATE_EVALUATION_RUN_ID"
```

이 검증까지 통과하면 model generation 및 generated-candidate evaluation data collection이
완료된다. 그 다음에는 validated inference/evaluation run ID를 입력으로 Section 9의
analysis dataset 생성과 RQ별 분석을 수행한다. 분석 코드는 primary 결과를 보기 전에
별도 version으로 동결하며, 부분 결과를 보고 분석 정의를 변경하지 않는다.

## 9. Primary processed dataset과 RQ별 순차 분석

`documents/08_analysis_pipeline.md`와 `analysis_tools/analysis_config.toml`이 분석 정의와
결측·통계 정책을 고정한다. 먼저 primary 전체를 한 번만 정제한다.

```bash
export PRIMARY_PROCESSED_DATASET_ID="primary-processed-$(date -u +%Y%m%dT%H%M%SZ)"
.venv/bin/python analysis_tools/build_processed_dataset.py \
  --inference-run-id "$MODEL_ARTIFACT_RUN_ID" \
  --evaluation-run-id "$CANDIDATE_EVALUATION_RUN_ID" \
  --decision-adjudication-id "$PRIMARY_DECISION_ADJUDICATION_ID" \
  --dataset-id "$PRIMARY_PROCESSED_DATASET_ID"
.venv/bin/python analysis_tools/validate_processed_dataset.py \
  --dataset-dir "data/processed/$PRIMARY_PROCESSED_DATASET_ID"
```

Invalid Decision이 0개여서 adjudication을 실행하지 않았다면 위 build command에서
`--decision-adjudication-id ...` 한 줄만 생략한다. Builder는 invalid Decision이 있는데
adjudication이 없거나, source run이 terminal/independently validated 상태가 아니면 거부한다.

같은 processed dataset에서 RQ를 하나씩 실행하고 검토한다. 먼저 RQ1만 실행한다.

```bash
export PRIMARY_ANALYSIS_ID="primary-analysis-$(date -u +%Y%m%dT%H%M%SZ)"
.venv/bin/python analysis_tools/run_rq_analysis.py \
  --dataset-dir "data/processed/$PRIMARY_PROCESSED_DATASET_ID" \
  --rq rq1 \
  --analysis-id "$PRIMARY_ANALYSIS_ID"
.venv/bin/python analysis_tools/validate_rq_output.py \
  --output-dir "results/summaries/$PRIMARY_ANALYSIS_ID/rq1"
```

RQ1의 denominator, missingness, metric과 간략 보고서를 검토해 수용한 후에만 같은
`PRIMARY_ANALYSIS_ID`로 `--rq rq2`, 이어서 `rq3`, `rq4`를 각각 실행한다. 각 단계의
`metrics.json`, CSV, `report.md`, `manifest.json`, `validation.json`을 함께 확인한다. 결과를
보고 분석 규칙을 바꾸지 않으며, 정당한 변경이 필요하면 새 analysis version, dataset 또는
analysis ID와 supersession 관계를 만든다.

## 10. 각 장기 단계 완료 후 기록

각 `--validate` 통과 후 다음 정보를 `documents/EXPERIMENT_RUNS.md`에 기록한다.

- attempt ID와 logical run ID
- start/end time와 Git commit
- configuration/prompt/scope version 및 hash
- status, summary, validation, registry의 absolute path
- expected/observed count와 failure 분류
- predecessor/resume 관계

실행 중에는 문서나 configuration을 수정하지 않는다. 기록 변경은 해당 단계가 완전히
종료되고 validation을 통과한 뒤 별도 coherent commit으로 남긴다.
