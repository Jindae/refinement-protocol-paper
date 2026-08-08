# Research Questions

## 연구 질문 구성 원칙

연구 질문은 특정 결과를 전제하지 않고, self-refinement protocol을 구성할 때 필요한 선택을 개념적인 수준에서 다룬다.
각 질문은 shared initial candidate, paired execution outcomes, token consumption을 이용해 답할 수 있도록 구성한다.

모델과 benchmark는 protocol 효과를 관찰하는 조건을 제공한다.
모델 간 절대 성능 순위보다 각 model-benchmark combination 안에서 protocol을 비교하고, 그 결과가 combinations 사이에서 어떻게 달라지는지 분석한다.

## RQ1. Refinement Performance and Repair–Regression Balance

**RQ1. How does the stage composition of self-refinement affect final code correctness, and how is
that effect explained by repairs of initially incorrect candidates and regressions of initially
correct candidates?**

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
이러한 Planning의 도입은 임의적인 stage 추가로만 보지 않는다. Code generation 선행연구는
solution plan을 code implementation 전에 명시적인 artifact와 phase로 분리했고, verified
plan을 initial generation과 후속 refinement에 재사용한 workflow도 평가했다. 그러나 이들은
주로 initial code 이전에 planning을 수행하고, post-hoc diagnosis와 revision suggestion을
분리하지 않는다. 본 연구는 이 motivation을 independently generated Critique 이후의
Revision Planning으로 옮겨 그 증분 효과를 평가한다.

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
- Repair count와 initially incorrect candidate 기준 repair rate
- Regression count와 initially correct candidate 기준 regression rate
- Functional Preservation과 Unrepaired Failure
- Candidate change 여부와 functional transition의 관계

### Intended Discussion

결과에서는 stage가 많을수록 성능이 증가하는지 또는 pass rate가 달라지는지만 독립적으로
논의하지 않는다. 각 pass-rate/refinement-gain 차이를 Repair와 Correct-to-Incorrect
Regression으로 함께 분해하여, 개선이 더 많은 repair에서 비롯됐는지 또는 correct
candidate 보존에서 비롯됐는지 설명한다. Functional Preservation, Unrepaired Failure,
malformed output도 같은 결과 경계 안에서 함께 보고한다.
다만 `R`-`CR` 및 `CR`-`CPR` 차이는 각각 완전한 정보 경로의 효과이며, Critique 또는 Plan의
의미 정확성을 독립적으로 식별한 인과 효과로 해석하지 않는다. Upstream 오진과 downstream
지시 이행 실패는 해당 protocol의 관찰된 성능에 포함된다.
특히 `CR`-`CPR` 결과는 code generation의 explicit Planning 선행연구와 비교하되, physical
call separation이 항상 유리하다고 전제하지 않는다. Self-Planning의 reported variant에서는
one-phase plan+code가 two-phase보다 약간 높았으므로, CPR이 CR보다 낮거나 같은 경우에도
Planning construct의 부재로 단정하지 않고 context transformation, error propagation,
plan-following failure, token cost를 함께 검토한다. 반대로 CPR이 높더라도 post-critique
Planning의 전체 protocol effect로 제한하여 해석한다.

Initial candidate와 final candidate의 paired correctness는 `Repair`, `Regression`, `Functional
Preservation`, `Unrepaired Failure`의 네 transition으로 분류한다. Decision-conditioned
protocol의 세부 gating tradeoff는 RQ2에서 always-refine counterpart와 직접 비교한다.

## RQ2. Initial Pass Rate and Decision-Conditioned Refinement

**RQ2. How does the value of decision-conditioned refinement vary across model-benchmark combinations with different initial pass rates?**

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

## RQ3. Single-Call versus Multi-Call Role Realization

**RQ3. How does realizing refinement roles within one model call versus externalizing them across multiple calls affect correctness and preservation?**

### Motivation

`CR`, `CPR`, `DR`, `DCR`, `DCPR`은 역할을 별도 call과 observable artifact 또는 exact
selection으로 외부화한다. 같은 역할을 한 prompt 안에 순서대로 명시하면 intermediate
artifact를 다시 입력하는 비용과 정보 변환은 줄지만, stage boundary와 exact preservation은
보장되지 않는다. 선행 planning 연구에서도 one-phase와 two-phase realization의 결과가
항상 같은 방향은 아니므로, stage composition과 call topology를 별개의 설계 축으로 본다.

### Empirical Scope

동일한 exact initial candidate에서 다음 paired comparison을 수행한다.

- `CR`과 `SC-CR`: C와 R을 두 call로 외부화하거나 한 call에 명시한 차이
- `CPR`과 `SC-CPR`: C, P, R을 세 call로 외부화하거나 한 call에 명시한 차이
- `DR`과 `SC-DR`: 별도 Decision selection과 한 call의 D-R 지시 차이
- `DCR`과 `SC-DCR`: 별도 D/C/R 경계와 한 call의 D-C-R 지시 차이
- `DCPR`과 `SC-DCPR`: 별도 D/C/P/R 경계와 한 call의 D-C-P-R 지시 차이

Single-call 조건은 hidden reasoning stage의 실제 수행을 입증하지 않는다. Treatment는
prompt에 명시된 역할 순서와 물리적 call topology 전체다.

### Evidence Used to Answer the RQ

- Final pass rate와 refinement gain
- Repair, Correct-to-Incorrect Regression, Functional Preservation, Unrepaired Failure
- Exact 및 normalized candidate change
- Single-call Decision label과 emitted code change의 교차표
- `PRESERVE`와 changed code, `REFINE`과 unchanged code의 불일치
- Paired correctness difference와 confidence interval

### Intended Discussion

결과는 “single-call 내부에서 C/P/D가 실제로 수행되었다”는 해석이 아니라, 동일 역할을
한 prompt에 명시한 protocol과 별도 call로 외부화한 protocol의 end-to-end 차이로 제한한다.
Single-call Decision 조건의 주 outcome은 label과 무관하게 같은 응답에서 emitted된 code다.
Label이 `PRESERVE`인데 code가 바뀐 사례는 별도 Decision의 exact-selection 경계가 제공하는
보존 효과와 대비한다. Label에 따라 exact initial 또는 emitted code를 선택한 결과는
추가 model call이 없는 supplementary analysis로만 보고한다.

## RQ4. Cost-Effectiveness

**RQ4. Do the correctness effects of alternative refinement protocols justify their token costs?**

### Motivation

별도 Critique, Plan, Decision call은 token consumption을 늘리지만 observable artifact와 exact
selection 경계를 제공한다. Single-call protocols는 call과 intermediate-input tokens를 줄일
수 있지만 correctness 또는 preservation이 달라질 수 있다. 따라서 전체 protocol panel에서
correctness와 실제 및 protocol-implied token cost를 함께 비교해야 한다.

### Empirical Scope

Candidate level과 benchmark level에서 multi-call 및 single-call protocol 전체를 비교한다.
물리적으로 실행한 Experimental Token Consumption과 한 protocol을 적용할 때의
Protocol-Implied Token Cost를 분리한다.

### Evidence Used to Answer the RQ

- Stage/call별 input, output, total tokens
- Protocol별 incremental 및 end-to-end token cost
- Benchmark total tokens와 task당 mean/median
- Decision overhead, avoided refinement tokens, net token saving
- Correctness-cost Pareto comparison
- Tokens per additional correct solution

### Intended Discussion

가장 높은 pass rate와 가장 효율적인 protocol을 구분하고, call separation이 제공하는
correctness/preservation 변화가 추가 token을 정당화하는지 분석한다. Token count는 같은
모델 안의 protocol comparison을 우선하며 모델 간 compute equivalence로 해석하지 않는다.

## Research Question to Analysis Mapping

| Research Question | Comparison | Main Outcomes |
|---|---|---|
| RQ1 | Direct, `R`, `CR`, `CPR`; initial-to-final transitions for all protocols | Pass rate and paired correctness together with repair, regression, preservation, and unrepaired failure |
| RQ2 | `R` vs `DR`, `CR` vs `DCR`, `CPR` vs `DCPR` across model-benchmark combinations | Prevented regression, missed repair, Decision-Conditioned Refinement effect |
| RQ3 | `CR`/`CPR`/`DR`/`DCR`/`DCPR` vs 대응 `SC-*` 조건 | Paired correctness, repair/regression, preservation and Decision-code consistency |
| RQ4 | Correctness and token consumption of all protocols | Total and per-task tokens, net token saving, correctness-cost tradeoff |

## Exploratory Mechanism Supplement and Follow-up Questions

Accepted RQ1–RQ4를 변경하지 않고 다음 네 post-hoc 분석을 별도 versioned supplement로 수행한다.

1. Protocol별 repair/regression model-task 집합의 교집합, 차집합, Jaccard overlap
2. Always-refine, separate Decision, integrated single-call Decision의 repair/regression mediation
3. 여러 generated condition의 cumulative empirical candidate reachability와 unique repair
4. Critique의 explicit no-problem 및 Plan의 explicit no-change surface signal에서 candidate
   change와 CR/CPR transition으로 이어지는 artifact chain

Prospective option-A pilot은 다음 질문을 진단한다: initial code 없이 다시 생성해도 repair가
나오는가, 한 response의 draft가 뒤의 critique/final token을 조건화하는가, stored Critique의
정보가 original code 없이도 유용한가. 이는 소규모 mechanism pilot이며 population-level
effect estimate가 아니다. Option B의 Planning ablation과 Option C의 matched-budget stochastic
capability envelope는 option-A 결과 검토 후에만 구체화한다.
