# 실험 계획

## 1. 실험 목적

실험은 self-refinement에서 Critique Generation, Revision Planning, Refinement-Need Decision의 도입이 final correctness와 token consumption에 미치는 영향을 측정한다.
Intermediate artifact의 정확성을 직접 평가하지 않고, 주요 outcome을 final candidate의 execution result와 model call의 token usage로 측정한다.

실험의 기본 단위는 하나의 model-task pair다.
각 모델은 각 task에 대해 자신의 initial candidate를 생성하며, 해당 candidate는 모든 protocol에서 동일하게 재사용된다.

현재 paper-facing protocol 실행은 `study-v0.4.0`이다. `study-v0.2.0`의 전체 실행은 prompt
역할 중복을 발견하게 한 참고용 결과 및 재현 근거로 보존한다. 새 버전은 검증된 v0.2.0의
exact Initial Candidate, Direct Revision, Decision과 그 평가를 재사용하며, Critique,
Critique-Conditioned Revision, Revision Planning, Plan-Conditioned Revision은 v0.3.0의
role-separated 실행을 재사용한다. v0.4.0에서는 다섯 single-call conditions만 새로 호출한다.

## 2. 실험 대상 Protocol

### 2.1 Baseline

- **Direct Generation**: initial candidate를 수정하지 않고 최종 결과로 사용

### 2.2 Always-Refine Protocol

- **R**: Direct Revision
- **CR**: Critique Generation 후 Critique-Conditioned Revision
- **CPR**: Critique Generation, Revision Planning, Plan-Conditioned Revision

### 2.3 Decision-Conditioned Refinement

- **DR**: Decision이 `PRESERVE`이면 initial candidate, `REFINE`이면 `R` 결과 사용
- **DCR**: Decision이 `PRESERVE`이면 initial candidate, `REFINE`이면 `CR` 결과 사용
- **DCPR**: Decision이 `PRESERVE`이면 initial candidate, `REFINE`이면 `CPR` 결과 사용

`DR`, `DCR`, `DCPR`을 위한 별도의 revision generation은 수행하지 않는다.
하나의 Decision output과 이미 생성한 revised candidate를 결합하여 final outcome과 Protocol Token Cost를 구성한다.

### 2.4 Single-Call Role Protocols

- **SC-CR**: 한 call에 C-R 역할을 명시하고 emitted code를 평가
- **SC-CPR**: 한 call에 C-P-R 역할을 명시하고 emitted code를 평가
- **SC-DR**: 한 call에 D-R 역할을 명시하고 Decision label과 emitted code를 함께 저장
- **SC-DCR**: 한 call에 D-C-R 역할을 명시하고 label과 emitted code를 함께 저장
- **SC-DCPR**: 한 call에 D-C-P-R 역할을 명시하고 label과 emitted code를 함께 저장

`SC-D*`의 주 final candidate는 reported Decision label과 무관하게 같은 call이 emitted한
code다. Label-enforced selection은 별도 supplementary derived outcome으로만 구성한다.
Single-call protocols에는 external Critique 또는 Plan artifact가 없으며, 그 역할의 내부
수행 여부를 별도 artifact correctness로 해석하지 않는다.

### 2.5 Role responsibility and no-change contract

| Stage | Primary responsibility | No-change behavior | Not a primary responsibility or direct input |
|---|---|---|---|
| Direct Revision | Initial candidate를 직접 검토하고 필요한 경우 수정 | 변경이 필요 없으면 source 또는 동작 보존 | Critique, Plan, Decision |
| Critique Generation | 기능 문제 존재 여부와 발견된 문제의 root cause/location 진단 | 문제가 없음을 명시 | Decision, 수정 계획 수립, code implementation |
| Revision Planning | Stored Critique를 최소 변경과 보존할 동작으로 변환 | Critique가 문제없다고 하면 변경 불필요 명시 | Decision, 독립적인 재검토, code implementation |
| Critique-Conditioned Revision | Stored Critique가 식별한 문제를 code에 반영 | Critique가 문제없다고 하면 exact initial source 재출력 | Decision, 별도 Planning call |
| Plan-Conditioned Revision | Stored Plan을 code에 구현 | Plan이 변경 불필요라고 하면 exact initial source 재출력 | Decision, Critique 원문, 독립적인 review/planning |

이 표는 모델 응답의 특정 단어를 사후 삭제하거나 역할을 위반한 text artifact를 자동
거부하는 content filter가 아니다. 역할은 prompt의 primary instruction과 직접 입력 경계로
정의하며, 모델의 실제 미준수는 raw response와 finish reason을 포함해 그대로 보존한다.

## 3. Model-Task Pair별 논리적 의존 순서

각 model-task pair에는 다음 artifact와 evaluation record가 필요하다. 아래 Step 번호는
필요한 record의 설명 순서이며 물리적 실행 순서나 model-call dependency를 뜻하지 않는다.
실제 실행은 task 하나를 끝까지 처리하지 않고 Section 4의 model-resident phase
schedule을 따른다.

### Step 1. Direct Generation

Task specification을 모델에 제공하여 initial candidate를 한 번 생성한다.
생성된 source code, raw response, extraction result, token usage, model configuration을 저장한다.

### Step 2. Initial Evaluation (별도 evaluation campaign)

Initial candidate를 benchmark의 전체 evaluation tests로 실행한다.
결과를 `PASS` 또는 `FAIL`로 기록하고, initial pass rate 계산에 사용한다.
Test outcome은 이후 model calls에 제공하지 않는다.
이 번호는 분석상 initial correctness의 역할을 나타낸다. 물리적 실행은 모든 model
inference와 Decision adjudication이 끝난 뒤 Step 9의 candidate들과 같은 별도 evaluation
campaign에서 수행하며, adjudication보다 먼저 실행하지 않는다.

### Step 3. Refinement-Need Decision

Task specification과 exact initial candidate를 입력으로 제공한다.
모델은 `PRESERVE` 또는 `REFINE`만 반환한다.
Decision response와 token usage를 저장한다.

Decision은 `R`, `CR`, `CPR` 중 어떤 protocol이 적용될지 알지 못하며, critique artifact나 revision plan도 입력으로 받지 않는다.
동일한 Decision output을 사용하여 `DR`, `DCR`, `DCPR` outcome을 구성한다.

모든 모델의 Decision generation이 완료된 뒤 strict exact parser가 거부한 응답 전부를
한 번의 pre-evaluation adjudication 단계에서 검토한다. 검토자는 versioned rubric과
prompt-visible task specification, exact initial candidate, raw Decision response만 사용하여
명백한 보존 의도는 `PRESERVE`, 명백한 기능 수정 의도는 `REFINE`, 그 밖은
`UNRESOLVED`로 기록한다. 원래 invalid call과 raw response는 수정하지 않는다.

### Step 4. Direct Revision

Task specification과 exact initial candidate를 입력으로 제공하여 `R` candidate를 생성한다.
선행 분석 artifact가 없으므로 모델이 candidate를 검토하고 필요한 경우 수정하며, 변경이
필요 없으면 기존 source 또는 동작을 보존할 수 있다.
Output code와 token usage를 저장한다.

### Step 5. Critique Generation

Task specification과 exact initial candidate를 입력으로 제공하여 critique를 생성한다.
Critique prompt는 기능 문제의 존재 여부, root cause와 관련 코드 위치에 집중하며 오류가
없으면 그 사실을 명시하도록 한다. Code snippet,
code fence 또는 부수적인 수정 언급이 있어도 text artifact를 삭제·거부하지 않는다.
생성된 critique와 token usage를 저장한다.

### Step 6. Critique-Conditioned Revision

Task specification, exact initial candidate, stored critique를 입력으로 제공하여 `CR` candidate를 생성한다.
Revision은 Critique가 식별한 문제를 반영하며, Critique가 기능 문제를 식별하지 않으면
exact initial candidate를 다시 출력하도록 요구한다. 새로운 독립 review나 Planning은
요구하지 않는다.
Output code와 token usage를 저장한다.

### Step 7. Revision Planning

Task specification, exact initial candidate, stored critique를 입력으로 제공하여 revision plan을 생성한다.
Plan prompt는 critique가 식별한 문제를 해결할 구체적이고 최소한의 변경과 유지해야 할
기존 동작을 기술한다. Critique가 문제없다고 하면 변경 불필요를 기록하며, candidate를
독립적으로 다시 진단하지 않는다. 완전한 revised code가 아니라 revision plan을 반환하도록 요구한다.
생성된 plan과 token usage를 저장한다.

### Step 8. Plan-Conditioned Revision

Task specification, exact initial candidate, stored plan을 입력으로 제공하여 `CPR` candidate를
생성한다. Stored critique는 plan의 lineage로 추적하지만 이 Revision call에는 직접 제공하지 않는다.
Revision은 supplied Plan을 구현하고, Plan이 변경 불필요를 나타내면 exact initial candidate를
다시 출력하도록 요구한다. 별도 review나 Planning은 요구하지 않는다.
Output code와 token usage를 저장한다.

### Step 9. Final Evaluation

`R`, `CR`, `CPR` candidate를 각각 benchmark의 전체 evaluation tests로 실행한다.
모든 protocol에서 동일한 evaluator, task별 timeout policy, dependency environment, code extraction rule을 사용한다. Candidate response에는 정확히 하나의 완전한 `python` fence가 있어야 하며, 공통 extractor는 fence 밖 텍스트를 제외하고 그 내부만 저장한다. 다중 또는 불완전 fence와 unfenced code는 추측하거나 수리하지 않는다.

이 계약을 충족하지 못한 모델 출력은 원본 record의 기존 status를 변경하지 않고 분석에서
`malformed_candidate`로 보고한다. 해당 model-task는 scope와 분모에서 제외하지 않는다.
Candidate가 없어 평가할 수 없는 경우 functional `FAIL`을 만들지는 않지만, 모델 귀책의
end-to-end success는 0으로 둔다. Initial candidate가 malformed이면 그 candidate를 요구하는
후속 phase는 실행하지 않고 `blocked_by_initial`로 보존한다. TIMEOUT 및 evaluator/infrastructure
failure는 이 규칙의 0에 포함하지 않고 별도 미결정 상태로 유지한다.

실험 orchestration, model inference, artifact storage, analysis, HumanEval+ 및 MBPP+ 평가는 Python 3.12 환경을 사용한다.
모든 model call은 고정된 vLLM batch-invariant mode, greedy decoding, model/task ordering과 동일한 TP=2 topology를 사용한다. Resume로 batch 구성이 달라져도 completed logical call은 재생성하지 않으며, 새 call에는 같은 batch-invariant configuration을 적용한다.
BigCodeBench-Instruct의 candidate execution만 upstream evaluator dependency와의 호환성을 위해 별도로 고정한 Python 3.10.12 환경에서 수행한다.
이 환경은 network와 host process namespace에서 격리하며, model call process와 Python package environment를 공유하지 않는다.
경계를 통과하는 입력은 task identifier와 평가할 exact candidate source이고, 평가 결과나 diagnostic은 이후 model call에 전달하지 않는다.
동일 task의 initial 및 모든 final candidates에는 model과 protocol에 관계없이 동일한 environment identifier, package lock, task별 timeout 및 sandbox configuration을 적용한다.

### Step 10. Single-Call Candidate Generation and Evaluation

`SC-CR`, `SC-CPR`, `SC-DR`, `SC-DCR`, `SC-DCPR`은 각각 task specification과 exact initial
candidate를 입력으로 받는 독립 model call이다. 모든 call은 최종 code를 한 complete Python
fence에 출력한다. `SC-D*`는 첫 non-empty line에 exact Decision label도 출력한다. Code와
label parser는 독립적이며 raw response를 먼저 저장한다.

Single-call inference는 v0.3.0 평가 결과를 입력으로 요구하지 않는다. 검증된 v0.2.0 exact
initial candidate만 참조하므로 v0.3.0 inference가 terminal validation을 통과한 뒤에는 그
evaluation 완료 전에도 시작할 수 있다. 다만 wall-time evaluation의 server-load 오염을
피하기 위해 GPU inference와 benchmark evaluation을 기본 schedule에서 동시에 실행하지 않는다.
Single-call candidate evaluation은 inference와 분리하고 `evaluation_workers=2`로 제한한다.

Task별 primary timeout은 model candidate를 생성하기 전에 official reference solution을 고정된 evaluator environment에서 세 번 실행한 timing audit으로 정한다.
세 benchmark의 공통 default primary timeout은 10초다. Accepted reference의 최대 관측 시간이 10초를 넘은 task만 사전 override 대상으로 삼고, 그 최대값이 `(10, 20]`, `(20, 40]`, `(40, 80]`, `(80, 160]`초에 속하면 각각 30, 60, 120, 240초를 적용한다. 이 규칙은 HumanEval+ 0개, MBPP+ 1개, BigCodeBench-Instruct 15개 override를 만든다.
Reference summary hash, 최대 관측값, 산정식 및 primary override 목록은 보존한다. 공통
confirmation limit은 120초와 primary limit의 1.5배 중 큰 값이다. EvalPlus의 base/plus
내부 실행 상한 합계가 120초를 넘을 수 있는 `HumanEval/38`, `/50`, `/53`은 confirmation만
180초로 사전 지정한다. 이 규칙은 model output과 무관하게
`candidate-timeouts-2026-08-04-r2`로 main experiment 전에 고정한다.

Primary evaluation 중에는 timeout candidate를 즉시 재실행하지 않고 잠정 `TIMEOUT`으로 저장한다. 예정된 primary evaluation batch가 모두 기록된 후 그 timeout candidate만 위에서 사전 지정한 confirmation timeout으로 정확히 한 번 재평가한다.
Confirmation evaluation이 완료되면 그 functional outcome을 최종 판정으로 사용하고, 두 번째 실행도 timeout인 경우에만 최종 evaluation status를 `TIMEOUT`으로 확정한다.
EvalPlus의 candidate-process 전체 상한뿐 아니라 입력별 `time_limit` 초과도 functional
`FAIL`이 아니라 이 timeout 경로에 포함한다. 고정된 EvalPlus 0.3.1의 test input, expected
output, special oracle 및 canonical solution은 수정하지 않고, 실행 wrapper가 입력별
`TimeoutException` 발생 index를 raw evaluator output에 기록한다. 한 suite의 false detail이
전부 해당 timeout index로 설명될 때만 그 suite를 `TIMEOUT`으로 판정한다. 다른 입력의
명백한 assertion 또는 일반 예외가 하나라도 있으면 functional `FAIL`이 이미 확정되므로
`FAIL`이 timeout보다 우선한다.
두 evaluation attempt의 raw output, configuration, elapsed time, status와 lineage를 모두 저장하며, candidate별 결과나 일시적 server load를 보고 limit을 추가 조정하거나 세 번째 실행을 수행하지 않는다.
Reference timing과 timeout 결과를 포함한 benchmark execution 정보는 model prompt 또는 이후 refinement call에 전달하지 않는다.

## 4. Versioned Phase Schedule과 Artifact Reuse

`study-v0.2.0`의 재현 경로는 한 모델을 상주시켜 일곱 phase를 모두 수행하는 기존
model-resident schedule을 그대로 보존한다. 현재 `study-v0.3.0` follow-up은 이미 검증된
Initial Candidate, Decision, Direct Revision을 재사용하므로 다음 네 phase만 새로 수행한다.

1. 전체 Critique Generation (`shared_critique`)
2. stored critique를 직접 사용하는 전체 Critique-Conditioned Revision (`cr_revision`)
3. 같은 stored critique를 수정 방법으로 변환하는 전체 Revision Planning (`shared_plan`)
4. stored plan만 직접 사용하는 전체 Plan-Conditioned Revision (`cpr_revision`)

여기서 “전체”는 HumanEval+ 163개, MBPP+ 378개, BigCodeBench-Instruct 1,136개를
합친 1,677개 included task를 의미한다. 각 phase는 세 benchmark를 하나의 background
phase attempt에서 연속 처리하며 benchmark 하나가 끝났다는 이유로 중간 실행을 종료하거나
사용자 확인을 기다리지 않는다. 네 phase는 각각 독립 status, log, summary, validation과
재실행 경계를 갖는다. Supervisor는 검증된 phase만 다음 phase로 자동 연결하고 실패 시
중단한다. 이 restart isolation을 위해 phase 사이의 model reload 비용은 의도적으로 수용한다.

Benchmark evaluation은 inference campaign과 분리한다. Candidate 결과를 다음 model-call
phase의 입력이나 진행 결정에 사용하지 않으며, 한 model/protocol의 세 benchmark 범위가
완료된 뒤 completeness를 검증하고 함께 분석한다. 구체적인 background status, count,
resume와 failure 규칙은 repository-level `EXPERIMENT_EXECUTION_GUIDELINES.md`를 따른다.
새 CR/CPR evaluation은 네 phase와 lineage validation이 완료된 뒤 별도 campaign으로 수행한다.

`study-v0.4.0` single-call campaign은 model을 최외곽 상주 단위로 둔다. 한 exact checkpoint를
TP=2로 한 번 로드한 뒤 다음 다섯 condition을 각각 세 benchmark 전체에 대해 batch size
32로 순서대로 처리하고 model을 내린다.

1. `SC-CR`
2. `SC-CPR`
3. `SC-DR`
4. `SC-DCR`
5. `SC-DCPR`

Condition을 batch 안에서 섞지 않는다. 각 `(model, condition)` 경계는 immutable record와
progress checkpoint를 가지며, 중단 후에는 completed logical call을 재사용한다. 이 순서는
condition을 최외곽에 둘 때 필요한 최대 30회 model load를 6회로 줄인다. Full execution
전에 같은 six-model, nine-task scope에서 prompt 형식, code/label 독립 parsing, candidate
lineage와 resume를 검증한다. Full configuration은 pilot review 전까지 execution-gated다.

### 4.1 Independent model calls

전체 연구 construct에는 Direct Generation, Refinement-Need Decision, Direct Revision,
Critique Generation, Critique-Conditioned Revision, Revision Planning, Plan-Conditioned
Revision의 일곱 독립 model-call 종류가 있다. v0.3.0 replacement execution에서 새로 수행하는
call은 다음 네 개다.

1. Critique Generation
2. Critique-Conditioned Revision
3. Revision Planning
4. Plan-Conditioned Revision

Critique는 `CR`과 Revision Planning에서 재사용한다.
Revision Plan은 `CPR`에서 재사용한다.
Decision은 `DR`, `DCR`, `DCPR` 구성에 공통으로 사용한다.
Initial Candidate, Decision, Direct Revision은 source run
`run_c99d3b1d562acc3e80026e48`에서 exact record/hash로 참조한다. 새 raw response나 source
record로 복사해 가장하지 않으며 새 run manifest가 source run을 parent로 기록한다.

v0.4.0에는 다음 다섯 독립 single-call 종류가 추가된다.

1. Single-Call Critique and Revision
2. Single-Call Critique, Planning, and Revision
3. Single-Call Decision and Revision
4. Single-Call Decision, Critique, and Revision
5. Single-Call Decision, Critique, Planning, and Revision

각 model-task-condition은 한 call만 수행하므로 full scope에는 최대
`6 × 1,677 × 5 = 50,310` task-condition units가 있다. Malformed source initial로 blocked된
unit에는 call을 만들지 않으며 분모와 explicit blocked status는 유지한다.

이 구조는 각 protocol을 처음부터 독립적으로 실행하는 경우 발생하는 중복 call을 제거한다.
동일한 critique artifact와 revision plan을 재사용하므로 protocol 비교에 artifact별 sampling 차이가 추가되지 않는다.

### 4.2 Derived Decision-conditioned outcomes

`DR`, `DCR`, `DCPR`은 물리적 inference phase가 아니다. 전체 Decision phase에서 저장한
exact-parsed Decision 또는 별도 adjudication artifact의 resolved Decision 하나와 해당
always-refine candidate를 결합한다. 따라서 Decision 결과를 받은 뒤 각 D protocol을 위해
모델을 다시 호출하거나 모델을 다시 로드하지 않는다. `UNRESOLVED`인 model-task pair에는
세 derived outcome을 만들지 않는다.

## 5. Decision-Conditioned Outcome 구성

Candidate `i`의 initial correctness를 `I_i`, Always-Refine Protocol `p`의 final correctness를 `Y_i,p`, Decision을 `D_i`라고 한다.
Decision-Conditioned Refinement의 final correctness는 다음과 같이 구성한다.

```text
if D_i == PRESERVE:
    final_candidate = initial_candidate
else:
    final_candidate = always_refine_candidate[p]
```

Decision이 `PRESERVE`인 사례를 분석에서 제거하지 않는다.
해당 사례의 final candidate를 exact initial candidate로 대체한다.
이 방식으로 prevented regression과 missed repair를 직접 계산할 수 있다.

## 6. Correctness Outcome

각 initial-final pair는 다음 네 transition 중 하나로 분류한다.

| Initial | Final | Outcome |
|---|---|---|
| FAIL | PASS | Repair |
| PASS | FAIL | Correct-to-Incorrect Regression |
| PASS | PASS | Functional Preservation |
| FAIL | FAIL | Unrepaired Failure |

### Correctness Metrics

- Initial pass rate
- Final pass rate
- Refinement gain in percentage points
- Repair count
- Repair rate among initially incorrect candidates
- Regression count
- Regression rate among initially correct candidates
- Functional preservation rate
- Candidate change rate

`R`, `CR`, `CPR`은 동일 initial candidate를 사용하므로 task-level paired comparison을 수행한다.
`DR`, `DCR`, `DCPR`도 동일 Decision과 대응하는 Always-Refine Protocol의 revised candidate를 사용하므로 task-level paired comparison을 수행할 수 있다.

## 7. Decision Outcome Analysis

Decision이 `PRESERVE`인 사례는 initial correctness와 Always-Refine outcome을 이용하여 다음과 같이 분류한다.

| Initial Outcome | Always-Refine Outcome | Decision Outcome |
|---|---|---|
| PASS | FAIL | Prevented Regression |
| PASS | PASS | Safe Preservation |
| FAIL | PASS | Missed Repair |
| FAIL | FAIL | Unsuccessful Refinement Skipped |

Decision이 `REFINE`인 경우 Decision-Conditioned Refinement는 해당 Always-Refine Protocol과 동일한 final candidate를 사용한다.
이 경우 correctness difference는 없지만 Decision call의 token overhead가 추가된다.

Decision analysis에서는 다음 값을 보고한다.

- `PRESERVE` rate among initially correct candidates
- `REFINE` rate among initially incorrect candidates
- Prevented regression count and rate
- Missed repair count and rate
- Safe preservation count
- Unsuccessful refinement skipped count
- exact-parsed, adjudicated, `UNRESOLVED` Decision 수와 비율을 model별로 구분한 값
- adjudication rationale category와 adjudicated 사례를 제외한 민감도 분석

## 8. Token Cost Accounting

모든 model call에 대해 input tokens와 output tokens를 별도로 기록한다.
Adjudicated Decision도 원래 자유 생성 call의 실제 input/output token 수를 그대로 사용한다.
사람의 의미 판정은 model token으로 환산하지 않고 별도의 운영 개입 횟수와 비율로 보고한다.
Token consumption은 두 종류로 구분한다.

### 8.1 Experimental Token Consumption

모든 protocol outcome을 구성하기 위해 실험에서 실제로 실행한 model calls의 token consumption이다.
이는 실험 자원과 reproducibility를 보고하는 데 사용한다.

### 8.2 Protocol Token Cost

해당 protocol을 각 candidate에 적용할 때 필요한 token 수다.
Cost-effectiveness 분석에는 이 값을 사용한다.

Always-Refine Protocol의 candidate-level cost는 다음과 같다.

```text
Cost(R)   = Revision call
Cost(CR)  = Critique call + Critique-Conditioned Revision call
Cost(CPR) = Critique call + Plan call + Plan-Conditioned Revision call
Cost(SC-CR)   = one SC-CR call
Cost(SC-CPR)  = one SC-CPR call
Cost(SC-DR)   = one SC-DR call
Cost(SC-DCR)  = one SC-DCR call
Cost(SC-DCPR) = one SC-DCPR call
```

Decision-Conditioned Refinement의 candidate-level cost는 다음과 같다.

```text
if Decision == PRESERVE:
    Cost(Dp) = Decision call
else:
    Cost(Dp) = Decision call + Cost(p)
```

Decision-Conditioned Refinement의 benchmark-level net token saving은 다음 두 항목의 차이로 계산한다.

- `PRESERVE` cases에서 실행하지 않은 refinement calls의 tokens
- 모든 task에서 수행한 Decision call의 tokens

### Cost Metrics

- Input tokens per stage
- Output tokens per stage
- Total tokens per candidate
- Benchmark total tokens
- Mean and median tokens per task
- Decision overhead
- Avoided refinement tokens
- Net token saving
- Tokens per additional correct solution

Model마다 tokenizer가 다르므로 raw token count는 같은 모델 안의 protocol comparison에 사용한다.
모델 간 token count는 직접적인 compute equivalence로 해석하지 않는다.

## Exploratory Mechanism Supplement and Staged Follow-up

### Existing-data supplement

Accepted `primary-final-v04-20260808-r5` outcome grid와 validated v0.3.0 C/P artifacts를 이용해
task-set overlap, Decision mediation, empirical reachability, artifact-chain surface analysis를
실행한다. 결과는 `exploratory_post_hoc`으로 표시하고 accepted four-RQ outputs와 혼합하지 않는다.

### Option A: initial-code and within-call conditioning pilot

첫 실행 범위는 DeepSeek-Coder-V2-Lite, Qwen3-Coder-30B-A3B, Gemma-4-31B의 세 모델과 기존
public-only 9-task pilot scope다. 한 모델을 한 번 load한 뒤 `REGEN-NO-INIT`,
`DRAFT-CR-FINAL`, `C-GENERATE-NO-INITIAL`을 세 benchmark 전체에 대해 순서대로 처리한다.
총 81 model calls이며 `DRAFT-CR-FINAL`은 두 code candidates와 critique를 보존한다.

Pilot acceptance는 exact prompt/hash/source lineage, raw-first storage, parser/malformed accounting,
resume, token/finish metadata, candidate count를 검증한다. Candidate evaluation은 inference와
별도 attempt로 수행하며, inference validation 전에 시작하지 않는다. 이 pilot의 결과는 prompt
및 mechanism feasibility이지 six-model population estimate가 아니다.

### Deferred options

- Option B: `DRAFT-CPR-FINAL`, Plan-only code-omitted generation 등 Planning ablation
- Option C: 동일 call/token budget의 independent samples와 refinement branches를 비교하는
  stochastic capability-envelope experiment

두 옵션은 option-A inference/evaluation/review가 모두 validated된 뒤 새로운 user decision과
versioned configuration 없이는 실행하지 않는다.

## 9. Model-Benchmark Combination별 분석

여섯 모델과 세 benchmark는 총 18개의 model-benchmark combinations를 구성한다.
각 combination에서 다음을 보고한다.

- Initial pass rate
- Protocol별 final pass rate
- Repair rate
- Regression rate
- Protocol token cost
- Decision outcome counts

Initial pass rate는 combinations를 easy, medium, hard로 임의 분류하지 않고 연속적인 변수로 사용한다.
Decision-Conditioned Refinement의 correctness difference와 net token saving이 initial pass rate에 따라 어떻게 달라지는지 비교한다.

Benchmark는 specification style, library usage, task complexity도 다르므로 initial pass rate와 benchmark 자체의 차이를 구분하여 해석한다.
동일 benchmark에서 model별 결과와 동일 model에서 benchmark별 결과를 함께 확인한다.

## 10. RQ별 분석 절차

### RQ1: Refinement Performance and Repair–Regression Balance

- Direct Generation과 `R` 비교
- `R`과 `CR` 비교
- `CR`과 `CPR` 비교
- Model-benchmark combination별 paired pass-rate difference 계산
- 각 stage를 추가했을 때 효과의 방향과 크기 비교
- 각 protocol의 initial-final transition matrix 생성
- Initially incorrect candidates에서 repair rate 비교
- Initially correct candidates에서 regression rate 비교
- pass-rate difference를 repair와 regression의 순차이로 재구성
- 최종 성능을 pass rate만으로 해석하지 않고 repair/regression/preservation과 함께 논의

### RQ2: Initial Pass Rate and Decision-Conditioned Refinement

- `R`과 `DR`, `CR`과 `DCR`, `CPR`과 `DCPR` 비교
- Prevented regression과 missed repair 계산
- Combination별 initial pass rate와 Decision-Conditioned Refinement effect 비교
- Candidate-level outcome과 benchmark-level result를 분리하여 보고

### RQ3: Single-Call versus Multi-Call Role Realization

- `CR` 대 `SC-CR`, `CPR` 대 `SC-CPR` paired comparison
- `DR` 대 `SC-DR`, `DCR` 대 `SC-DCR`, `DCPR` 대 `SC-DCPR` paired comparison
- Final correctness와 repair/regression/preservation 비교
- Single-call Decision label과 exact/normalized code change consistency 비교
- Main emitted-code outcome과 supplementary label-enforced outcome 구분

### RQ4: Cost-Effectiveness

- 각 stage의 additional token cost 계산
- Multi-call 및 single-call protocol 전체의 final correctness와 benchmark total tokens 비교
- Correctness-cost Pareto comparison 수행
- 동일 correctness에서 더 낮은 비용을 제공하는 protocol과, 추가 비용에도 correctness가 개선되지 않는 protocol 식별

## 11. Statistical Analysis

모든 주요 protocol comparison은 동일 task와 동일 initial candidate를 이용한 paired design으로 수행한다.
Pass/fail outcome difference에는 task-level paired bootstrap을 이용하여 95% confidence interval을 계산한다.
필요한 경우 paired binary outcome에 대한 McNemar test를 보조적으로 사용한다.

Repair rate와 regression rate는 각각 initially incorrect subset과 initially correct subset에서 계산한다.
표본 수가 작은 model-benchmark combination에서는 point estimate와 confidence interval을 함께 보고하고 작은 차이를 과도하게 해석하지 않는다.

Protocol result와 initial pass rate의 관계는 18개 combinations의 descriptive results와 model 및 benchmark를 고려한 regression analysis를 함께 사용할 수 있다.
이 분석에서는 benchmark 차이를 initial pass rate만으로 설명하지 않는다.

## 12. Reproducibility와 기록

각 model call에 대해 다음 정보를 저장한다.

- Exact model checkpoint
- Inference engine and version
- Precision or quantization
- Decoding parameters
- Prompt template and stage identifier
- Raw response
- Extracted code or artifact
- Input and output token counts
- Task identifier
- Initial candidate identifier and hash
- Evaluation result and failure metadata

모든 protocol artifact는 initial candidate identifier로 연결한다.
Code extraction 또는 evaluation failure는 별도 상태로 기록하고, 동일한 처리 규칙을 모든 모델과 protocol에 적용한다.
