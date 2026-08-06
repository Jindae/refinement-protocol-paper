# Glossary

## 1. 사용 원칙

이 문서는 실험 코드, 분석 결과, 논문 본문, 표, 그림에서 사용할 canonical terminology를 정의한다.
동일한 개념에 여러 표현을 혼용하지 않는다.
구현 과정에서 사용한 임시 표현보다 아래 용어를 우선한다.

영문 논문에서는 **Canonical Term** 열의 표기를 사용한다.
약어는 최초 등장 시 full term과 함께 정의한 후 사용한다.
불필요한 수식어를 붙이지 않으며, 용어만으로 의미가 명확하지 않으면 대상이나 계산 방식을 직접 설명한다.

## 2. Study Scope and Design

| Canonical Term | Definition | Usage Notes | Avoid |
|---|---|---|---|
| **Self-Refinement** | 동일한 모델이 execution feedback 없이 자신이 생성한 initial candidate를 검토하고 보존하거나 수정하는 과정 | 모델 입력은 task specification, initial candidate, self-generated critique와 revision plan으로 제한 | self-debugging, execution-guided refinement와 혼용 |
| **Execution Feedback** | Test result, runtime output, exception, compiler diagnostic, execution trace 등 code execution에서 얻은 정보 | 본 연구에서는 candidate 평가에만 사용하고 모델에는 제공하지 않음 | feedback만 사용하여 critique와 혼동 |
| **Refinement Stage** | 별도의 prompt와 model call로 구현한 Refinement-Need Decision, Critique Generation, Revision Planning, Code Revision 중 하나 | 모델 내부 reasoning step이 아니라 실험에서 직접 관찰되는 call | internal stage, hidden reasoning stage |
| **Stage Composition** | Protocol에 포함된 Refinement Stage와 그 순서 | `R`, `CR`, `CPR`의 차이를 설명할 때 사용 | protocol complexity, pipeline complexity |
| **Shared-Initial Design** | 동일한 model-task pair의 모든 protocol이 같은 initial candidate를 재사용하는 실험 설계 | Protocol 차이를 initial generation 차이와 분리 | shared mode, controlled mode |
| **Self-Generated Initial Candidate** | 평가 대상 모델이 직접 생성하고 같은 모델이 refine하는 initial candidate | 다른 모델이 생성한 candidate와 구분할 때 사용 | model-independent candidate, common candidate pool |
| **Model-Benchmark Combination** | 하나의 model과 하나의 benchmark로 구성된 분석 단위 | 여섯 모델과 세 benchmark는 총 18개 combinations를 구성 | setting, cell, model-benchmark cell |

## 3. Candidates and Correctness

| Canonical Term | Definition | Usage Notes | Avoid |
|---|---|---|---|
| **Direct Generation** | Task specification만으로 initial candidate를 생성하는 과정 | Refinement call을 포함하지 않음 | initial run, base call |
| **Initial Candidate** | Direct Generation으로 생성되고 모든 protocol의 공통 입력이 되는 code candidate | `C_0`로 표기 가능 | original answer, base code |
| **Revised Candidate** | Code Revision이 생성한 code candidate | `R`, `CR`, `CPR`의 code output | refined answer |
| **Final Candidate** | 특정 protocol에서 최종 평가에 사용하는 candidate | Always-Refine Protocol에서는 revised candidate, `PRESERVE`에서는 initial candidate | output code처럼 출처가 불명확한 표현 |
| **Functional Correctness** | 해당 benchmark의 전체 evaluation tests를 통과하는 상태 | Binary `PASS` 또는 `FAIL`로 기록 | correct-looking, plausible code |
| **Initial Pass Rate** | 전체 tasks 중 initial candidate가 functionally correct한 비율 | Model-benchmark combination별로 보고 | baseline accuracy와 정의 없이 혼용 |
| **Final Pass Rate** | 특정 protocol의 final candidate가 functionally correct한 비율 | Protocol별로 보고 | refined accuracy |
| **Refinement Gain** | Final pass rate에서 initial pass rate를 뺀 absolute percentage-point difference | Percentage points로 보고 | relative improvement와 혼용 |
| **Candidate Change** | Revised candidate의 normalized code가 initial candidate와 다른 상태 | Candidate change rate 계산에 사용 | edit success |
| **Exact Preservation** | Final candidate로 저장된 initial candidate를 그대로 사용하는 상태 | `PRESERVE`는 새 code generation 없이 exact preservation을 보장 | no change만 사용하여 의미를 불명확하게 표현 |
| **Functional Preservation** | Initially correct candidate가 final evaluation에서도 correct한 상태 | Code text는 달라질 수 있음 | exact preservation과 혼용 |

## 4. Refinement Stages

| Canonical Term | Abbreviation | Definition | Output |
|---|---:|---|---|
| **Refinement-Need Decision** | `D` | Initial candidate를 그대로 보존할지 refinement를 수행할지 결정하는 stage | `PRESERVE` or `REFINE` |
| **Non-Exact Decision Direction Reading** | - | Strict exact parser가 거부한 Decision 설명문을 benchmark 평가 전에 평가결과 없이 고정 rubric으로 읽어 방향을 기록하는 별도 비-model-call 절차 | `PRESERVE`, `REFINE`, or `UNRESOLVED` |
| **Critique Generation** | `C` | 기능 문제 존재 여부를 판단하고 발견한 문제의 root cause와 관련 위치를 식별하는 stage | Critique artifact 또는 명시적 no-problem statement |
| **Revision Planning** | `P` | Critique의 진단을 구체적이고 최소한의 수정 방법 및 보존 조건으로 변환하는 stage | Revision plan 또는 명시적 no-change statement |
| **Code Revision** | `R` | Direct에서는 자체 review 후 필요시 수정하고, CR에서는 Critique를 반영하며, CPR에서는 Plan을 구현하여 revised candidate를 생성하는 stage | Revised candidate |

### Stage Terminology Notes

- 최초 등장 시 **Refinement-Need Decision**을 사용하고 이후 문맥이 명확하면 **Decision**으로 줄일 수 있다.
- Stage를 의미할 때 **Critique Generation**, 산출물을 의미할 때 **critique artifact**를 사용한다.
- Stage를 의미할 때 **Revision Planning**, 산출물을 의미할 때 **revision plan**을 사용한다.
- Stage를 의미할 때 **Code Revision**, 산출물을 의미할 때 **revised candidate**를 사용한다.
- `gate`, `gating`, `decision gate`는 사용하지 않는다.
- Revision Planning은 Critique Generation 이후에만 수행한다.
- Revision Planning은 Critique를 독립적으로 다시 판정하지 않는다. Critique가 no-problem을
  나타내면 no-change plan을 생성한다.
- Critique-Conditioned Revision은 Critique가 no-problem을 나타낼 때, Plan-Conditioned
  Revision은 Plan이 no-change를 나타낼 때 exact initial source를 다시 출력하도록 요구한다.
- Plan-Conditioned Revision은 revision plan만 직접 입력받는다. Critique record linkage는
  plan을 통한 간접 provenance이며 직접 prompt input을 뜻하지 않는다.
- Decision은 C, P 또는 어느 Code Revision prompt에도 전달하지 않는다.

## 5. Protocols

| Canonical Term | Abbreviation | Definition |
|---|---:|---|
| **Always-Refine Protocol** | - | 모든 initial candidate에 `R`, `CR`, 또는 `CPR`의 stage sequence를 실행하는 방식 |
| **Direct Revision** | `R` | Initial candidate에서 바로 Code Revision을 수행 |
| **Critique-Conditioned Revision** | `CR` | Critique Generation 후 critique artifact를 이용해 Code Revision 수행 |
| **Critique-and-Plan-Conditioned Revision** | `CPR` | Critique Generation과 Revision Planning 후 revision plan만 직접 이용해 Code Revision 수행 |
| **Decision-Conditioned Refinement** | - | Refinement-Need Decision이 `PRESERVE`이면 initial candidate를 사용하고, `REFINE`이면 대응하는 Always-Refine Protocol의 revised candidate를 사용하는 방식 |
| **Decision-Conditioned Direct Revision** | `DR` | `PRESERVE`이면 initial candidate, `REFINE`이면 `R` candidate 사용 |
| **Decision-Conditioned Critique-Conditioned Revision** | `DCR` | `PRESERVE`이면 initial candidate, `REFINE`이면 `CR` candidate 사용 |
| **Decision-Conditioned Critique-and-Plan-Conditioned Revision** | `DCPR` | `PRESERVE`이면 initial candidate, `REFINE`이면 `CPR` candidate 사용 |

### Protocol Terminology Notes

- `DR`, `DCR`, `DCPR`을 위해 별도의 revised candidate를 생성하지 않는다.
- 각 outcome은 하나의 Decision 결과와 대응하는 Always-Refine Protocol의 revised candidate를 결합하여 구성한다.
- `R`, `CR`, `CPR`은 누적 call composition을 비교하지만, `CPR` Revision의 직접 입력은
  Critique가 아니라 Plan으로 대체된다. 따라서 `CR`-`CPR` 차이는 call count와 입력 경계를
  함께 포함한다.

## 6. Outcome Transitions

| Canonical Term | Transition | Definition |
|---|---:|---|
| **Repair** | `FAIL -> PASS` | Initially incorrect candidate가 final candidate에서 correct가 된 사례 |
| **Repair Rate** | - | Initially incorrect candidates 중 Repair가 발생한 비율 |
| **Correct-to-Incorrect Regression** | `PASS -> FAIL` | Initially correct candidate가 final candidate에서 incorrect가 된 사례 |
| **Regression Rate** | - | Initially correct candidates 중 Correct-to-Incorrect Regression이 발생한 비율 |
| **Functional Preservation** | `PASS -> PASS` | Initial correctness가 final candidate에서도 유지된 사례 |
| **Unrepaired Failure** | `FAIL -> FAIL` | Initially incorrect candidate가 final candidate에서도 incorrect인 사례 |
| **Repair-Regression Balance** | - | 한 protocol에서 발생한 Repair와 Correct-to-Incorrect Regression의 수와 비율 | 

### Outcome Terminology Notes

- 최초 등장 시 **Correct-to-Incorrect Regression**으로 정의한 후 문맥이 명확하면 `regression`으로 줄일 수 있다.
- Refinement Gain만 보고하지 않고 Repair와 Correct-to-Incorrect Regression을 함께 보고한다.

## 7. Decision Outcomes

| Canonical Term | Conditions | Definition |
|---|---|---|
| **Prevented Regression** | Initial `PASS`, Always-Refine `FAIL`, Decision `PRESERVE` | Initial candidate를 보존하여 발생하지 않게 된 Correct-to-Incorrect Regression |
| **Safe Preservation** | Initial `PASS`, Always-Refine `PASS`, Decision `PRESERVE` | Final correctness를 유지하면서 refinement calls를 실행하지 않은 사례 |
| **Missed Repair** | Initial `FAIL`, Always-Refine `PASS`, Decision `PRESERVE` | Initial candidate를 보존하여 가능한 Repair를 사용하지 못한 사례 |
| **Unsuccessful Refinement Skipped** | Initial `FAIL`, Always-Refine `FAIL`, Decision `PRESERVE` | Final correctness를 바꾸지 못할 refinement calls를 건너뛴 사례 |
| **Unnecessary Refinement** | Initial `PASS`, Decision `REFINE` | Initially correct candidate에 Always-Refine Protocol을 실행한 사례. Regression 발생 여부는 별도로 기록 |
| **Repair Opportunity Retained** | Initial `FAIL`, Decision `REFINE` | Initially incorrect candidate에 Always-Refine Protocol을 실행한 사례 |

### Decision Terminology Notes

- Decision의 효과를 binary classification accuracy만으로 설명하지 않는다.
- Exact-parsed, deterministically normalized, separately read Decision을 구분해 보고한다. Non-exact
  response direction reading은 새 model call이나 parser repair가 아니며, 원래 invalid response를
  변경하지 않는다.
- `UNRESOLVED`는 `PRESERVE`나 `REFINE`으로 impute하지 않는다.
- `PRESERVE`된 initially incorrect candidate라도 Always-Refine Protocol이 이를 repair하지 못했다면 final correctness 손실은 없다.
- 따라서 **Missed Repair**와 **Unsuccessful Refinement Skipped**를 구분한다.

### Malformed Candidate

정확히 하나의 완전한 Python fence라는 공통 출력 계약을 모델 응답이 충족하지 못해
candidate artifact를 만들 수 없는 상태다. 이는 parser나 evaluator의 추출 실패가 아니라
모델 출력 형식 실패를 가리키며, functional `FAIL`과 구분한다. 원본 registry enum이 역사적
호환성을 위해 `extraction_failure`를 유지하더라도 정제 데이터와 논문에서는
`malformed_candidate`를 사용한다. Model-task는 제외하지 않고 end-to-end success를 0으로
계산하며, timeout 및 evaluator/infrastructure failure는 여기에 포함하지 않는다.

## 8. Cost Terms

| Canonical Term | Definition | Usage Notes |
|---|---|---|
| **Input Token Consumption** | Model call에 입력된 token 수 | Stage별로 기록 |
| **Output Token Consumption** | Model call이 생성한 token 수 | Stage별로 기록 |
| **Stage Token Cost** | 하나의 Refinement Stage에서 소비한 input plus output tokens | Monetary cost를 의미하지 않음 |
| **Refinement Token Cost** | `R`, `CR`, 또는 `CPR`을 실행하는 데 필요한 token 수 | Decision call은 포함하지 않음 |
| **Decision Overhead** | 모든 candidates에 Refinement-Need Decision을 실행하는 데 필요한 token 수 | Decision-Conditioned Refinement의 고정 추가 비용 |
| **Experimental Token Consumption** | 모든 protocol outcome을 구성하기 위해 실험에서 실제로 실행한 model calls의 token 수 | 실험 자원 보고에 사용 |
| **Protocol Token Cost** | 해당 protocol을 candidate에 적용할 때 필요한 token 수 | Cost-effectiveness 분석에 사용 |
| **Avoided Refinement Tokens** | `PRESERVE`로 인해 실행하지 않은 것으로 계산하는 refinement calls의 token 수 | Decision-Conditioned Refinement 분석에 사용 |
| **Net Token Saving** | Avoided Refinement Tokens에서 Decision Overhead를 뺀 값 | Positive이면 token saving 발생 |
| **Additional Token Cost** | 비교 기준 protocol보다 추가로 소비한 token 수 | Stage를 추가한 비교에 사용 |
| **Tokens per Additional Correct Solution** | Additional Token Cost를 증가한 correct solutions 수로 나눈 값 | Correct solutions 수가 증가한 경우에만 계산 |
| **Correctness-Cost Pareto Frontier** | 더 높은 final correctness와 더 낮은 Protocol Token Cost를 동시에 제공하는 다른 protocol이 없는 protocol 집합 | Model-benchmark combination별 또는 benchmark 전체로 제시 |

### Cost Terminology Notes

- `Cost`를 사용할 때 token cost인지 monetary cost인지 명시한다.
- 본 연구의 주요 비용 지표는 token consumption이다.
- Model tokenizer가 다르므로 모델 간 raw token count를 동일한 compute unit으로 해석하지 않는다.
- Cost comparison은 같은 모델 안의 protocol comparison을 중심으로 수행한다.

## 9. Analysis Levels

| Canonical Term | Definition |
|---|---|
| **Candidate-Level Analysis** | 하나의 initial candidate에서 protocol 또는 Decision이 만든 correctness와 token 결과를 분석하는 것 |
| **Benchmark-Level Analysis** | 모든 tasks의 final correctness와 Protocol Token Cost를 합산하여 분석하는 것 |
| **Transition Analysis** | Initial candidate와 final candidate의 Functional Correctness를 paired transition으로 분류하는 것 |
| **Protocol Comparison** | 동일한 initial candidates를 사용한 두 protocol의 결과를 paired 방식으로 비교하는 것 |

## 10. Capitalization and Formatting

- Stage 이름은 개념을 지칭할 때 대문자로 시작한다: `Refinement-Need Decision`, `Critique Generation`, `Revision Planning`, `Code Revision`.
- 일반적인 동작을 지칭할 때는 소문자를 사용할 수 있다: `the model critiques the candidate`.
- Protocol abbreviation은 code font 또는 수식 표기를 사용한다: `R`, `CR`, `CPR`, `DR`, `DCR`, `DCPR`.
- Transition은 prose에서 `incorrect-to-correct`와 `correct-to-incorrect`로 쓰고, 표에서는 `FAIL -> PASS`, `PASS -> FAIL`을 사용할 수 있다.
- Pass-rate difference는 absolute percentage points로 보고한다.
