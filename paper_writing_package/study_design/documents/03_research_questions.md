# Research Questions

## 연구 질문 구성 원칙

연구 질문은 특정 결과를 전제하지 않고, self-refinement protocol을 구성할 때 필요한 선택을 개념적인 수준에서 다룬다.
각 질문은 shared initial candidate, paired execution outcomes, token consumption을 이용해 답할 수 있도록 구성한다.

모델과 benchmark는 protocol 효과를 관찰하는 조건을 제공한다.
모델 간 절대 성능 순위보다 각 model-benchmark combination 안에서 protocol을 비교하고, 그 결과가 combinations 사이에서 어떻게 달라지는지 분석한다.

## RQ1. Refinement Stage Composition

**RQ1. How does the stage composition of self-refinement affect final code correctness?**

### Motivation

Self-refinement는 initial candidate를 바로 수정하는 방식과, 수정 전에 critique 또는 revision plan을 별도로 생성하는 방식으로 구성할 수 있다.
Critique Generation이나 Revision Planning을 추가하면 검토 과정이 구조화될 수 있지만, 추가 model calls가 더 나은 final candidate로 이어지는지는 명확하지 않다.
각 stage의 추가 효과를 확인하려면 동일한 initial candidate에서 `R`, `CR`, `CPR`을 비교해야 한다.
여기서 Critique는 기능 문제의 root cause와 위치를 식별하고, Planning은 그 진단을 수정
방법으로 변환하며, CPR의 Revision은 plan만 직접 받는다. 이 입력 경계는 stage 이름만
분리하고 역할은 중복시키는 해석을 피하기 위해 결과 확인 전에 고정한다.
Critique는 오류가 반드시 있다고 가정하지 않고 no-problem 결론을 허용한다. Planning과
conditioned Revision은 같은 candidate를 다시 독립적으로 review하는 단계가 아니라 각각
upstream 진단을 계획으로 변환하고 supplied artifact를 실행한다. Direct Revision만 선행
artifact가 없으므로 review와 수정 필요성 판단을 자체적으로 수행한다.

### Empirical Scope

RQ1은 다음 paired protocol comparison을 중심으로 분석한다.

- `R`과 `CR`: 별도의 Critique Generation 추가 효과
- `CR`과 `CPR`: Critique 이후 Revision Planning 추가 효과
- Direct Generation과 `R`: 추가 revision call 자체의 효과

### Evidence Used to Answer the RQ

- Protocol별 final pass rate
- Initial candidate 대비 refinement gain
- 동일 task에서 protocol 간 final correctness transition
- Model-benchmark combination별 paired difference와 confidence interval

### Intended Discussion

결과에서는 stage가 많을수록 성능이 증가하는지 여부를 단순히 확인하는 데 그치지 않는다.
어떤 stage를 추가했을 때 final correctness가 개선되거나 감소하는지, 그 효과가 model-benchmark combination에 따라 달라지는지를 논의한다.
다만 `R`-`CR` 및 `CR`-`CPR` 차이는 각각 완전한 정보 경로의 효과이며, Critique 또는 Plan의
의미 정확성을 독립적으로 식별한 인과 효과로 해석하지 않는다. Upstream 오진과 downstream
지시 이행 실패는 해당 protocol의 관찰된 성능에 포함된다.

## RQ2. Repair and Regression Balance

**RQ2. How do alternative refinement protocols balance repairs of initially incorrect candidates and regressions of initially correct candidates?**

### Motivation

동일한 Refinement Gain은 서로 다른 Repair와 Correct-to-Incorrect Regression 조합에서 발생할 수 있다.
Final pass rate만 비교하면 protocol이 initial failures를 효과적으로 수정했는지, 또는 correct candidates를 보존했기 때문에 좋은 결과를 얻었는지 구분하기 어렵다.
Self-refinement의 실용적 가치는 incorrect candidate를 repair하는 능력과 correct candidate를 보존하는 능력을 함께 고려해야 한다.

### Empirical Scope

Initial candidate와 final candidate의 paired correctness outcome을 다음 네 transition으로 분류한다.

- Incorrect-to-Correct: Repair
- Correct-to-Incorrect: Regression
- Correct-to-Correct: Functional Preservation
- Incorrect-to-Incorrect: Unrepaired Failure

Always-Refine Protocol과 Decision-Conditioned Refinement를 모두 이 transition 기준으로 분석한다.

### Evidence Used to Answer the RQ

- Repair count와 repair rate
- Regression count와 regression rate
- Functional preservation rate
- Unrepaired failure rate
- Candidate change 여부와 functional transition의 관계
- Protocol별 repair-regression balance

### Intended Discussion

결과에서는 Refinement Gain을 Repair와 Correct-to-Incorrect Regression으로 분해한다.
Critique Generation과 Revision Planning이 repair와 regression에 각각 어떤 영향을 주는지, Decision-Conditioned Refinement가 regression을 줄이는 대신 repair를 놓치는지, 동일한 refinement gain이 서로 다른 repair-regression balance에서 발생하는지를 논의한다.

## RQ3. Initial Pass Rate and Decision-Conditioned Refinement

**RQ3. How does the value of decision-conditioned refinement vary across model-benchmark combinations with different initial pass rates?**

### Motivation

Refinement-Need Decision은 각 initial candidate를 보존할지, 대응하는 Always-Refine Protocol의 revised candidate를 사용할지 결정한다.
이러한 Decision의 분리는 임의적인 stage 추가가 아니다. 선행연구는 별도 Asker나 reward
model로 whether-to-refine을 판단하거나, self-verification token으로 refine-or-stop을
결정하여 수정 필요성 판단과 수정 생성을 서로 다른 기능으로 다뤘다. 본 연구는 이 분리
자체의 신규성을 주장하지 않고, execution-feedback-free code generation에서 Decision을
독립적이고 관찰 가능한 call로 구현했을 때의 효과를 분석한다.
구현 방식은 동일하지 않다. ART와 DeCRIM은 별도 판단 stage가 실제 refinement 실행을
조건부로 제어하지만 판단 과정에서 생성한 subquestion 또는 feedback을 refiner에 전달한다.
GLoRe의 main evaluation은 refinement 후보를 먼저 생성한 뒤 learned verifier로 선택하며,
ReVISE는 SFT와 DPO로 학습한 `[eos]`/`[refine]` token을 동일 generation 안에서 사용한다.
본 연구의 Decision은 binary output만 반환하는 별도 model call이고 그 내용은 이후
Critique, Planning, Revision에 전달되지 않는다.
다만 실험에서는 Decision이 generation schedule을 중단시키지 않는다. 모든 always-refine
candidate를 수집한 뒤 Decision-conditioned outcome을 파생하며, `REFINE`일 때만 후속 call을
실행한다는 조건은 protocol-implied execution과 cost에 적용한다.
Benchmark-level 결과는 Decision output뿐 아니라 initially correct candidates와 initially incorrect candidates의 수에 따라 달라진다.
Initial pass rate가 높은 combination에서는 correct candidate를 보존하여 regression과 token consumption을 줄일 기회가 많다.
Initial pass rate가 낮은 combination에서는 incorrect candidate를 보존하여 repair 기회를 놓칠 가능성이 커진다.

### Empirical Scope

각 Always-Refine Protocol에 동일한 Decision 결과를 적용하여 `DR`, `DCR`, `DCPR`을 구성한다.
Model-benchmark combination별 initial pass rate와 Decision-Conditioned Refinement의 correctness 및 token-cost difference를 함께 분석한다.

### Evidence Used to Answer the RQ

- Correct candidates에 대한 `PRESERVE` 비율
- Incorrect candidates에 대한 `REFINE` 비율
- Prevented regression count
- Missed repair count
- Safe preservation count
- Unsuccessful refinement skipped count
- Initial pass rate와 Decision-Conditioned Refinement가 만든 final pass-rate difference의 관계
- Initial pass rate와 Net Token Saving의 관계

### Intended Discussion

결과에서는 Decision의 binary accuracy보다 `PRESERVE`와 `REFINE`이 만든 실제 outcome에 중점을 둔다.
어떤 combination에서 prevented regression과 token saving이 발생하는지, 어떤 combination에서 missed repair가 더 큰 손실이 되는지, initial pass rate가 이러한 tradeoff와 어떤 관계를 갖는지를 논의한다.

## RQ4. Cost-Effectiveness

**RQ4. Do the correctness effects of additional refinement stages justify their token costs?**

### Motivation

Critique와 Plan을 별도 call로 추가하면 더 많은 input 및 output token이 필요하다.
Decision은 추가 call을 요구하지만 `PRESERVE`된 candidate에서는 refinement calls를 실행하지 않는다.
따라서 protocol의 비용은 call count만으로 판단할 수 없으며, benchmark에서 `PRESERVE`와 `REFINE`이 각각 얼마나 발생하는지 함께 고려해야 한다.

### Empirical Scope

Cost analysis는 candidate level과 benchmark level로 구분한다.
Candidate level에서는 Decision이 refinement tokens를 절약하면서 regression을 방지했는지, 또는 repair를 놓쳤는지 확인한다.
Benchmark level에서는 이러한 결과를 합산하여 total tokens와 total correct solutions를 비교한다.

### Evidence Used to Answer the RQ

- Stage별 input tokens와 output tokens
- Protocol별 token cost per candidate
- Benchmark total tokens
- Mean 및 median tokens per task
- Decision overhead
- Avoided refinement tokens
- Net token saving
- Correctness-cost Pareto comparison
- Tokens per additional correct solution

### Intended Discussion

결과에서는 가장 높은 pass rate를 제공하는 protocol과 가장 효율적인 protocol을 구분한다.
추가 stage가 final correctness를 높이지만 token consumption도 크게 늘리는 경우, correctness를 유지하면서 token consumption을 줄이는 경우, 더 많은 tokens를 사용하면서 correctness도 낮아지는 경우를 구분한다.
Token count는 tokenizer가 다른 모델 사이의 절대 계산량 비교보다 동일 모델 내부의 protocol comparison에 우선 사용한다.

## Research Question to Analysis Mapping

| Research Question | Comparison | Main Outcomes |
|---|---|---|
| RQ1 | Direct, `R`, `CR`, `CPR` | Final pass rate, refinement gain, paired correctness difference |
| RQ2 | Initial-to-final transitions for all protocols | Repair, regression, preservation, unrepaired failure |
| RQ3 | `R` vs `DR`, `CR` vs `DCR`, `CPR` vs `DCPR` across model-benchmark combinations | Prevented regression, missed repair, Decision-Conditioned Refinement effect |
| RQ4 | Correctness and token consumption of all protocols | Total and per-task tokens, net token saving, correctness-cost tradeoff |
