# 프로젝트 개요

## 1. 연구 배경

코드 생성용 대규모 언어 모델은 자연어 명세로부터 실행 가능한 프로그램을 생성할 수 있지만, 로컬 환경에서 배포 가능한 open-weight 모델의 초기 생성 결과는 모든 문제에서 안정적으로 정확하지는 않다.
로컬 실행은 코드와 명세를 사용자 통제 환경에 유지하고, 고정된 모델 버전과 추론 설정을 사용할 수 있다는 장점이 있다.
그러나 모델을 교체하거나 추가 학습하지 않고 초기 생성 성능을 개선할 수 있는 실용적인 방법은 여전히 필요하다.

Self-refinement는 동일한 모델이 자신의 초기 코드를 다시 검토하고 수정하도록 하여 추가 학습 없이 성능을 높이려는 방법이다.
코드 생성 refinement 연구에서는 테스트 실패, 실행 결과, 컴파일 오류, 실행 trace와 같은 execution feedback을 이용하는 방법이 활발히 연구되어 왔다.
반면 execution feedback을 사용할 수 없거나 사용하지 않는 조건에서는 모델이 task specification과 자신의 코드만을 바탕으로 수정 필요성, 문제점, 수정 방향을 판단해야 한다.
이 조건에서 어떤 refinement 구성이 실제로 유효한지에 대한 체계적인 비교는 상대적으로 제한적이다.

이러한 self-refinement는 단순히 모델 호출을 한 번 더 수행하는 방식부터, critique와 revision planning을 명시적인 호출로 분리하는 방식까지 여러 형태로 구성할 수 있다.
각 단계를 추가하면 모델이 문제를 더 구조적으로 검토할 가능성이 있지만, 추가 토큰과 추론 비용이 발생하고 이미 정확한 코드를 손상시키는 correct-to-incorrect regression도 발생할 수 있다.
따라서 단계가 많을수록 성능이 좋아진다고 가정할 수 없으며, 각 단계를 추가했을 때 final correctness와 token cost가 어떻게 달라지는지 확인할 필요가 있다.

## 2. 해결하려는 연구 공백

기존 연구는 execution feedback을 이용한 code refinement, self-generated tests, compiler-guided repair, execution-conditioned training 등을 폭넓게 다루고 있다.
Execution feedback 없이 수행되는 self-refinement도 제안되어 왔지만, 많은 연구가 하나의 고정된 self-refinement 절차를 평가하거나 최종 성능만 보고한다.
Locally deployable open-weight instruct models를 대상으로 명시적인 refinement stage의 포함
여부를 통제하고, 각 구성이 repair, regression, final pass rate, token consumption에 미치는
영향을 비교한 근거는 충분하지 않다. 본 연구의 panel은 code-specialized models를 중심으로
구성하되 general-purpose instruct control 하나를 포함한다.

특히 다음 사항을 함께 다룰 필요가 있다.

- Direct revision 앞에 별도의 critique를 추가하는 것이 실제로 이득을 주는가
- Critique와 revision 사이에 별도의 revision planning을 추가하는 것이 추가 비용을 정당화하는가
- Refinement-Need Decision이 candidate를 보존하여 regression과 token consumption을 줄이는가
- Refinement-Need Decision이 incorrect candidate의 repair 기회를 얼마나 놓치는가
- Initial pass rate가 다른 model-benchmark combination에서 동일한 protocol의 가치가 어떻게 달라지는가
- Candidate 수준의 이익과 손실이 benchmark 전체의 correctness와 token cost로 어떻게 누적되는가

본 연구는 intermediate critique나 plan의 의미적 정확성을 직접 평가하지 않는다.
대신 각 stage를 별도의 model call로 구성하고, stage를 추가했을 때 final candidate의 테스트 결과가 어떻게 달라지는지 측정한다.
이 선택은 final candidate의 실행 결과를 모든 주요 outcome의 공통 평가 기준으로 사용하기 위한 것이다.

## 3. 연구 목표

본 연구의 목적은 locally deployable open-weight instruct models에서 code generation
self-refinement protocol을 구성하는 실용적인 방법을 조사하는 것이다.
구체적으로 다음을 목표로 한다.

1. Direct revision, critique-conditioned revision, critique-and-plan-conditioned revision의 최종 correctness를 비교한다.
2. 각 protocol의 Refinement Gain을 Repair와 Correct-to-Incorrect Regression으로 분해한다.
3. Decision-Conditioned Refinement가 candidate별 결과와 benchmark 전체 결과에 미치는 영향을 분석한다.
4. Model과 benchmark에 따라 달라지는 initial pass rate가 protocol의 효용에 어떤 관계를 갖는지 분석한다.
5. 추가 stage가 소비하는 토큰과 얻는 correctness improvement를 함께 비교하여 각 protocol의 cost-effectiveness를 평가한다.

## 4. 연구 범위

연구 대상은 workstation-scale local inference environment에서 실행할 수 있는 open-weight
instruct models로 제한하며, 주된 code-specialized panel과 general-purpose control을 같은
Python code-generation protocol로 평가한다.
Frontier proprietary models는 평가 대상이나 비교 기준에 포함하지 않는다.
연구의 목적은 local refinement가 proprietary model을 대체할 수 있는지 판단하는 것이 아니라, 고정된 local model의 출력을 개선하기 위해 추가 inference를 어떻게 구성하는 것이 유효한지 확인하는 것이다.

모델에는 benchmark test, execution result, compiler diagnostic, runtime trace 또는 외부 verifier feedback을 제공하지 않는다.
Benchmark tests는 initial candidate와 final candidate의 기능적 정확성을 사후 평가하는 데만 사용한다.
각 모델은 자신의 initial candidate를 생성하고 동일한 모델이 Decision, Critique, Plan, Revision을 수행한다.
따라서 다른 모델이 생성한 candidate를 수정하는 경우는 연구 범위에 포함하지 않는다.

모든 refinement protocol은 동일한 model-task pair에서 생성된 동일 initial candidate를 재사용한다.
Protocol 간 차이는 initial generation 차이가 아니라 stage composition 차이로 해석한다.
모델 간 raw final pass rate 순위보다 각 모델 안에서 protocol을 비교하고, 그 결과가 model-benchmark combination에 따라 어떻게 달라지는지 분석한다.

## 5. 전반적인 연구 개요

연구는 네 개의 local code model과 세 개의 Python code-generation benchmark를 사용한다.
각 모델은 각 task에 대해 initial candidate를 한 번 생성한다.
이 candidate는 Direct Generation 결과이자 모든 refinement protocol의 공통 입력으로 사용된다.

Always-Refine Protocol은 다음의 누적 구조로 구성한다.

- `R`: task specification과 initial candidate를 이용한 Direct Revision
- `CR`: Critique Generation 후 Critique-Conditioned Revision
- `CPR`: Critique Generation, Revision Planning, Plan-Conditioned Revision

각 candidate에 대해서는 Refinement-Need Decision도 한 번 생성한다.
Decision이 `PRESERVE`이면 Decision-Conditioned Refinement의 final candidate는 exact initial candidate가 된다.
Decision이 `REFINE`이면 해당 Always-Refine Protocol의 final candidate를 사용한다.
이에 따라 `DR`, `DCR`, `DCPR` 결과는 별도의 revision call 없이 사후 구성할 수 있다.

Initial candidate와 각 final candidate는 benchmark의 전체 evaluation tests로 평가한다.
주요 correctness outcome은 initial pass rate, final pass rate, refinement gain, repair, correct-to-incorrect regression이다.
Decision의 결과는 prevented regression, missed repair, safe preservation, unsuccessful refinement avoidance로 분석한다.

비용은 candidate 수준과 benchmark 수준으로 나누어 분석한다.
Candidate 수준에서는 Decision이 refinement calls를 생략함으로써 correctness와 token cost에 어떤 결과를 만드는지 확인한다.
Benchmark 수준에서는 candidate-level 결과를 합산하여 total tokens, mean tokens per task, final correct count, prevented regressions, missed repairs를 분석한다.

## 6. 기대되는 연구 결과

본 연구는 특정 protocol이 항상 우수하다고 가정하지 않는다.
연구에서 기대하는 결과는 다음과 같은 실증적 근거다.

- Critique Generation과 Revision Planning을 추가하는 것이 Direct Revision보다 유효한 조건과 유효하지 않은 조건
- 각 protocol이 initial failure를 repair하는 정도와 initial success를 regression시키는 정도
- Refinement-Need Decision이 candidate를 보존하거나 refine하면서 만드는 correctness와 token-cost의 이익 및 손실
- Initial pass rate가 다른 model-benchmark combination에서 protocol의 유용성이 달라지는 양상
- 추가 token consumption이 final correctness improvement를 정당화하는 protocol과 그렇지 않은 protocol
- Locally deployable code model을 위한 self-refinement protocol 선택에 사용할 수 있는 경험적 지침

연구 결과는 self-refinement의 절대적 우수성을 주장하기보다, stage composition과 Decision-Conditioned Refinement가 어떤 조건에서 유효한지를 제한된 범위 안에서 설명하는 데 목적이 있다.
