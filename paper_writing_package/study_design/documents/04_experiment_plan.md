# 실험 계획

## 1. 실험 목적

실험은 self-refinement에서 Critique Generation, Revision Planning, Refinement-Need Decision의 도입이 final correctness와 token consumption에 미치는 영향을 측정한다.
Intermediate artifact의 정확성을 직접 평가하지 않고, 주요 outcome을 final candidate의 execution result와 model call의 token usage로 측정한다.

실험의 기본 단위는 하나의 model-task pair다.
각 모델은 각 task에 대해 자신의 initial candidate를 생성하며, 해당 candidate는 모든 protocol에서 동일하게 재사용된다.

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
Output code와 token usage를 저장한다.

### Step 5. Critique Generation

Task specification과 exact initial candidate를 입력으로 제공하여 critique를 생성한다.
Critique prompt는 완성된 revised solution과 completed revision plan을 생성하지 않도록
제한한다. Fault localization 또는 설명에 필요한 focused code snippet과 code fence는
허용한다.
생성된 critique와 token usage를 저장한다.

### Step 6. Critique-Conditioned Revision

Task specification, exact initial candidate, stored critique를 입력으로 제공하여 `CR` candidate를 생성한다.
Output code와 token usage를 저장한다.

### Step 7. Revision Planning

Task specification, exact initial candidate, stored critique를 입력으로 제공하여 revision plan을 생성한다.
Plan prompt는 완성된 revised solution 전체를 생성하지 않도록 제한하되, 변경 위치와
방법을 설명하는 focused code snippet과 code fence는 허용한다.
생성된 plan과 token usage를 저장한다.

### Step 8. Plan-Conditioned Revision

Task specification, exact initial candidate, stored critique, stored plan을 입력으로 제공하여 `CPR` candidate를 생성한다.
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

## 4. Model-Resident Phase Schedule과 Artifact Reuse

GPU model-loading overhead를 줄이기 위해 모델을 최외곽 실행 단위로 사용한다. 한 exact
checkpoint를 한 번 로드한 정상적인 model campaign 안에서 다음 phase를 순서대로
진행한 뒤 모델을 내리고 다음 모델로 이동한다.

1. 전체 benchmark scope의 Direct Generation
2. 저장된 exact initial candidates에 대한 전체 Refinement-Need Decision
3. 전체 Direct Revision
4. 전체 Critique Generation
5. stored critique를 사용한 전체 Critique-Conditioned Revision
6. 동일한 stored critique를 사용한 전체 Revision Planning
7. stored critique와 plan을 사용한 전체 Plan-Conditioned Revision
8. 모든 모델에서 parse되지 않은 Decision을 한 번에 검토하는 blinded adjudication 단계

여기서 “전체”는 HumanEval+ 163개, MBPP+ 378개, BigCodeBench-Instruct 1,136개를
합친 1,677개 included task를 의미한다. 각 phase는 세 benchmark를 하나의 background
session에서 연속 처리하며 benchmark 하나가 끝났다는 이유로 중간 실행을 종료하거나
사용자 확인을 기다리지 않는다. Phase 경계에서는 immutable task artifacts와 progress를
checkpoint하지만 정상 경로에서는 모델을 reload하지 않는다.

Benchmark evaluation은 inference campaign과 분리한다. Candidate 결과를 다음 model-call
phase의 입력이나 진행 결정에 사용하지 않으며, 한 model/protocol의 세 benchmark 범위가
완료된 뒤 completeness를 검증하고 함께 분석한다. 구체적인 background status, count,
resume와 failure 규칙은 repository-level `EXPERIMENT_EXECUTION_GUIDELINES.md`를 따른다.
Candidate evaluation은 8번 단계가 완료되어 모든 invalid Decision이 `PRESERVE`, `REFINE`,
또는 `UNRESOLVED`로 명시되기 전에는 시작하지 않는다.

### 4.1 Independent model calls

각 model-task pair에서 refinement와 관련하여 독립적으로 수행하는 call은 다음 여섯 개다.

1. Refinement-Need Decision
2. Direct Revision
3. Critique Generation
4. Critique-Conditioned Revision
5. Revision Planning
6. Plan-Conditioned Revision

Critique는 `CR`과 Revision Planning에서 재사용한다.
Revision Plan은 `CPR`에서 재사용한다.
Decision은 `DR`, `DCR`, `DCPR` 구성에 공통으로 사용한다.

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

### RQ1: Refinement Stage Composition

- Direct Generation과 `R` 비교
- `R`과 `CR` 비교
- `CR`과 `CPR` 비교
- Model-benchmark combination별 paired pass-rate difference 계산
- 각 stage를 추가했을 때 효과의 방향과 크기 비교

### RQ2: Repair and Regression Balance

- 각 protocol의 initial-final transition matrix 생성
- Initially incorrect candidates에서 repair rate 비교
- Initially correct candidates에서 regression rate 비교
- Similar refinement gain을 가진 protocol의 repair-regression balance 비교

### RQ3: Initial Pass Rate and Decision-Conditioned Refinement

- `R`과 `DR`, `CR`과 `DCR`, `CPR`과 `DCPR` 비교
- Prevented regression과 missed repair 계산
- Combination별 initial pass rate와 Decision-Conditioned Refinement effect 비교
- Candidate-level outcome과 benchmark-level result를 분리하여 보고

### RQ4: Cost-Effectiveness

- 각 stage의 additional token cost 계산
- Protocol별 final correctness와 benchmark total tokens 비교
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
