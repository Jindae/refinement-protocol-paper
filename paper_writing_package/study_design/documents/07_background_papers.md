# 코드 생성 Self-Refinement 문헌 통합 요약

## 1. 통합 결과

두 보고서에서 제목과 출판본 중복을 제거한 기존 44개 후보에 Decision 분리와
selective refinement를 직접 다루는 ART, GLoRe, DeCRIM을 추가하면 47개의 고유 후보가
남는다.
이 중 SelfRACG는 initial candidate의 검토, 수정, 보존, 또는 선택을 다루지 않는 retrieval-augmented code generation 연구이므로 현재 연구의 Background에서는 제외했다.
나머지 46편을 현재 문헌 지도에 유지한다.

46편을 현재 연구와의 관련성에 따라 다시 분류하면 다음과 같다.

| 분류 | 수 | 용도 |
|---|---:|---|
| 핵심 문헌 | 15 | Background의 주요 논지와 research gap을 직접 뒷받침 |
| 보조 문헌 | 19 | execution-guided refinement, stage decomposition, verification, agent workflow의 범위를 설명할 때 선택적으로 사용 |
| 주변 문헌 | 12 | 전체 문헌 지도에는 포함하지만 현재 논문의 Background에서는 원칙적으로 생략 |
| 제외 | 1 | 현재 연구와의 연결이 약하여 bibliography에서도 제외 |

이 분류는 논문의 품질이나 영향력에 대한 평가가 아니다.
현재 연구의 조건인 code generation, shared initial candidate, execution-feedback-free inference, explicit stage composition, correct-to-incorrect regression, Refinement-Need Decision, token cost와의 관련성을 기준으로 한 분류다.

## 2. 검증 과정에서 수정한 정보

| 논문 | 보고서의 문제 | 검증 후 정보 |
|---|---|---|
| CodeChat-Eval | 제목에서 `Large Language Models`가 `LLMs`로 축약됨 | 공식 제목은 *CodeChat-Eval: Evaluating Large Language Models in Multi-Turn Code Refinement Dialogues* |
| ReChisel | 출판 venue 미확정 preprint로 기재 | DAC 2025 출판본 확인, DOI `10.1109/DAC63849.2025.11132940` |
| ART | 기존 코드 중심 문헌 지도에서 누락됨 | NAACL 2024 출판본을 확인했다. 학습된 Asker가 refinement 필요성을 별도 판단하고 필요한 사례만 Refine으로 보내며, 이후 Truster가 initial과 refined output을 선택한다. GSM8K와 StrategyQA를 평가하고 code generation은 평가하지 않는다 (`shridhar-etal-2024-art`; [ACL Anthology](https://aclanthology.org/2024.naacl-long.327/)) |
| GLoRe | 기존 코드 중심 문헌 지도에서 누락됨 | refinement를 when, where, how로 명시적으로 분해한다. ORM이 when, SORM이 where, global/local refiner가 how를 담당하며 GSM8K와 SVAMP 수학 추론을 평가한다 (`havrilla2024glore`; [arXiv](https://arxiv.org/abs/2402.10963)) |
| DeCRIM | 기존 코드 중심 문헌 지도에서 누락됨 | Critic이 multi-constraint response의 refinement 필요성과 위치를 판단한 뒤 Refiner가 수정한다. RealInstruct와 IFEval instruction following을 평가하고 code generation은 별도 평가하지 않는다 (`palmeira-ferraz-etal-2024-llm`; [ACL Anthology](https://aclanthology.org/2024.findings-emnlp.458/)) |
| ReVISE | code benchmark 포함 여부가 불명확하게 기술됨 | MBPP 실험을 포함함. 다만 주된 실험과 논지는 일반 reasoning 및 학습된 intrinsic verification에 있음 |
| CRITIC | code refinement 문헌처럼 분류될 여지가 있음 | code interpreter를 사용하지만 주요 code-related task는 mathematical program synthesis에 가까움. 일반적인 자연어-to-code refinement의 핵심 근거로 사용하지 않는 편이 안전함 |
| RefineCoder | inference-time candidate refinement와 가까운 것으로 분류됨 | external critic과 LLM-as-a-judge를 이용해 training data와 model series를 개선하는 연구임. 현재 protocol의 직접 선행연구로 보기 어려움 |
| FunCoder | refinement 및 planning 문헌으로 분류됨 | initial candidate를 수정하기보다 generation 과정에서 recursive function decomposition과 consensus를 사용하는 방법임 |
| RethinkMCTS | code revision 연구로 분류될 여지가 있음 | execution feedback으로 pre-generation reasoning thought를 수정하는 search framework이며, 생성된 initial code의 post-hoc revision과는 다름 |
| Efficient Hallucination Detection | selective refinement 방법처럼 기술됨 | detector와 dataset이 핵심이며, detector를 사용한 end-to-end preserve/refine protocol은 직접 평가하지 않음 |

기존 문헌 메타데이터에 반영한 출판 상태도 유지한다.
SCoRe는 ICLR 2025, Teaching Large Language Models to Self-Debug는 ICLR 2024, OpenCodeInterpreter는 Findings of ACL 2024, InterCode는 NeurIPS 2023, TraceCoder는 ICSE 2026, CYCLE은 PACMPL 8(OOPSLA1) 출판본을 사용한다.

## 3. Background에서 사용할 핵심 연구 흐름

### 3.1 Execution feedback 없는 self-refinement와 explicit critique

Self-Refine은 동일 모델이 output을 생성하고, natural-language self-feedback을 만든 뒤, 그 feedback을 사용해 output을 수정하는 일반 프레임워크를 제시했다 (`madaan2023selfrefine`).
현재 연구의 `CR`과 가장 가까운 개념적 출발점이지만, code task에 대한 shared-initial functional transition이나 critique stage의 독립적인 증분 효과가 중심은 아니다.
Self-Refine의 feedback은 actionable suggestion을 포함할 수 있으므로 Critique 뒤에 별도
Planning을 두는 현재 CPR의 역할 분리를 그대로 정당화하지는 않는다. 이 때문에 현재
설계는 Critique를 root-cause/location, Planning을 change method, Revision을 code execution으로
명시하고 CPR Revision에는 plan만 직접 전달한다.

후속 연구는 self-correction을 prompting만의 문제가 아니라 학습 문제로 다뤘다.
SCoRe는 external evaluator feedback 없이 multi-turn self-correction을 강화학습으로 학습하고 HumanEval을 포함해 평가했다 (`kumar2025score`).
CoCoS는 small code models가 correct outputs를 보존하면서 incorrect outputs를 수정하도록 학습하고, incorrect-to-correct와 correct-to-incorrect transition을 구분했다 (`cho-etal-2025-self`).
ReflexiCoder는 initial code, reflection, corrected code를 포함하는 trajectory를 학습해 inference-time execution engine 없이 correction을 수행한다 (`jiang-etal-2026-reflexicoder`).
ReVISE는 모델이 refinement를 계속할지 종료할지를 intrinsic self-verification으로 판단하도록 학습하고 MBPP에서도 평가했다 (`pmlr-v267-lee25ab`).

Critique artifact 자체의 역할을 다룬 연구도 있다.
RCO는 critique의 표면적 품질이 아니라 downstream refinement를 얼마나 개선하는지를 reward로 사용하며 code generation을 포함한 여러 task에서 평가했다 (`yu-etal-2025-training`).
SCOPE는 code candidate에 대해 subgoal, gap analysis, robustness checklist로 구성된 structured critique를 생성하고 이를 revision에 사용한다 (`zhang2026scope`).
다만 두 연구 모두 현재 연구의 `R`, `CR`, `CPR` 누적 비교와는 설계가 다르다.

### 3.2 Execution-guided code refinement

Code refinement의 다수 연구는 test result, compiler output, runtime state, 또는 execution trace를 correctness signal로 사용한다.
Teaching Large Language Models to Self-Debug은 explanation과 unit-test 또는 execution result를 결합한 iterative debugging을 제시했다 (`chen2024selfdebug`).
Self-Edit, CYCLE, LeDex, OpenCodeInterpreter는 execution outcome을 code editing 또는 학습된 refinement에 연결한다 (`zhang-etal-2023-self`, `ding2024cycle`, `jiang2024ledex`, `zheng-etal-2024-opencodeinterpreter`).
Revisit Self-Debugging은 self-generated tests의 bias와 post-execution 및 in-execution debugging을 비교한다 (`chen-etal-2025-revisit`).
LDB와 TraceCoder는 더 세밀한 runtime state와 trace를 diagnosis 및 repair에 사용한다 (`zhong-etal-2024-debug`, `huang2026tracecoder`).

이 흐름은 execution feedback이 code refinement에 강한 정보를 제공한다는 점을 보여준다.
동시에 이러한 방법은 모델이 task specification, initial candidate, self-generated critique와 plan만을 받는 현재 연구와 구분해야 한다.
Self-generated tests도 실행 후 얻은 결과를 모델에 제공한다면 현재 연구에서 정의한 execution-feedback-free 조건에 해당하지 않는다.

### 3.3 Regression, preservation, and selective refinement

Decision을 revision과 분리하는 construct는 현재 연구만의 임의적인 stage 구성이 아니다.
ART는 학습된 소형 Asker가 initial output의 refinement 필요성을 별도 판단하고, 필요하다고
판정한 사례만 Refine stage로 보낸다 (`shridhar-etal-2024-art`). 필요하지 않으면 initial
output을 반환하며, refinement 뒤에는 별도 Truster가 initial과 refined output을 다시
선택한다. 이는 Decision과 Revision을 물리적으로 분리한 가장 직접적인 system-level
선례다. 다만 GSM8K와 StrategyQA를 대상으로 하며, Asker의 subquestions가 refinement
입력에 전달되고 post-refinement selection도 수행하므로 현재의 독립 binary Decision과는
다르다.

GLoRe는 refinement 문제를 when, where, how로 명시적으로 분해한다
(`havrilla2024glore`). 학습된 ORM이 final-answer correctness를 평가하는 when 기능을,
SORM이 첫 오류 위치를 찾는 where 기능을, global/local refinement model이 how 기능을
담당한다. 이 연구는 수정 필요성 판단과 수정 내용 생성을 서로 다른 기능으로 취급해야
한다는 construct-level 근거를 제공한다. 그러나 main evaluation에서는 draft마다 global과
local refinement를 생성한 뒤 ORM이 draft를 포함한 세 후보를 rerank한다. 따라서 GLoRe의
when은 현재 연구처럼 refinement call을 사전에 생략하는 execution gate라기보다 refinement
수용과 candidate selection에 가깝다. 실험도 GSM8K와 SVAMP 수학 추론에 한정된다.

DeCRIM도 Critic이 각 instruction constraint를 검사하여 when과 where를 결정한 뒤 Refiner가
수정하는 구조를 사용한다 (`palmeira-ferraz-etal-2024-llm`). 이는 Decision-like assessment와
Revision의 stage separation을 뒷받침하지만, 일반 instruction following을 대상으로 하며
상세 critique가 revision에 직접 전달된다.

Self-Refine의 일반 algorithm에도 feedback call 뒤의 조건부 분기가 있다
(`madaan2023selfrefine`). Feedback에서 task-specific stop indicator를 추출할 수 있고, stop
condition이 충족되면 다음 Refine call을 실행하지 않는다. 그러나 이 feedback call은
수정 필요성만 판정하는 독립 Decision이 아니라 actionable critique도 함께 생성하며, stop하지
않을 때 그 전체 feedback이 Refine prompt에 전달된다. 또한 이 연구의 code tasks는 code
optimization과 readability improvement이며, 자연어 명세로 standalone function의 functional
correctness를 평가하는 conventional code generation과는 다르다.

CoCoS는 repair와 regression을 직접 분리해 보고하므로 현재 연구의 transition analysis와 가장 가까운 선행연구다 (`cho-etal-2025-self`).
그러나 CoCoS의 목적은 correction-preserving model training이며, 별도 model call로 구현된 Critique Generation, Revision Planning, Refinement-Need Decision의 효과를 비교하지 않는다.

CodeChat-Eval은 외부에서 주어진 multi-turn refinement instruction을 따르는 동안 initially correct code의 functional correctness가 손상될 수 있음을 보였다 (`guo2026codechateval`).
이는 code editing의 preservation 문제를 직접 다루지만, instruction이 self-generated critique가 아니고 repair가 필요한 candidate를 판별하는 실험도 아니다.

Are LLMs Reliable Code Reviewers?는 requirement conformance 판단에서 correct code를 잘못 reject하는 overcorrection을 분석했다 (`jin2026reliable`).
이 결과는 Refinement-Need Decision이 initially correct candidate에 불필요한 refinement를 적용할 위험을 설명하는 데 유용하다.
다만 이 연구의 outcome은 review judgment의 false rejection이며, revised code의 correct-to-incorrect transition과 동일하지 않다.

Conventional code generation에서 가장 가까운 직접 선례는 ReVISE다. ReVISE는 모델이
`[eos]` 또는 `[refine]`을 예측해 refinement를 종료하거나 계속하도록 학습하고 MBPP에서
평가한다 (`pmlr-v267-lee25ab`). 첫 curriculum stage는 correct trajectory 뒤에서 `[eos]`를,
incorrect trajectory 뒤에서 `[refine]`을 선호하도록 SFT와 DPO loss를 함께 최적화한다.
두 번째 stage는 같은 objective를 사용해 incorrect trajectory 뒤의
`[refine] + correct trajectory` 생성을 학습한다. 추론 시에는 동일 모델이 initial trajectory
뒤에서 두 control token 중 하나를 다음 토큰으로 예측하고, `[refine]`이면 그 토큰에 조건화해
수정 trajectory를 계속 생성한다. 따라서 verification과 correction은 curriculum과 control
token 수준에서는 분리되지만 독립 model call이나 독립 prompt로 분리되지 않는다. ReVISE의
보고 성능에는 이 두 학습 stage와 verification-confidence-aware voting이 함께 포함되므로,
이를 selective execution 또는 Decision만의 효과로 해석할 수 없다.

RubricRefine은 pre-execution rubric으로 code-mode tool-use candidate를 검사하여 최고 점수면
종료하고 그렇지 않으면 수정한다 (`levine2026rubricrefine`). 넓은 의미에서는 code를
선택적으로 수정하지만, 자연어 명세에서 standalone function을 생성하는 conventional code
generation보다 agentic tool-use contract 검증에 가깝다.

CodeT와 LEVER는 candidate를 수정하지 않고 generated tests 또는 execution-aware verifier로 여러 candidates를 선택한다 (`chen2023codet`, `pmlr-v202-ni23b`).
이 연구들은 selective computation과 candidate preservation의 인접 근거지만 refinement
필요성을 판단한 뒤 하나의 initial candidate를 수정하는 protocol은 아니다.

이 차이는 다음처럼 정리한다.

| 연구 | 판단과 수정의 실행 경계 | 판단 출력 및 후속 사용 | 실제 refinement-call gating | 현재 연구와의 핵심 차이 |
|---|---|---|---|---|
| Self-Refine | Feedback과 Refine이 별도 prompt/call | stop indicator와 actionable feedback; 계속할 때 feedback을 Refine에 전달 | Framework 수준에서 가능 | Decision과 Critique가 결합됨 |
| ART | 학습된 Asker와 base-LLM Refine이 별도 모델/stage | Yes/No 판단과 subquestions; subquestions를 Refine에 전달 | Yes | 수학·QA, 학습된 Asker, 후속 Truster 사용 |
| DeCRIM | Critic과 Refiner가 별도 model call | constraint별 만족 여부와 자연어 feedback; feedback을 Refiner에 전달 | Yes | instruction following, Decision과 Critique가 결합됨 |
| GLoRe | ORM/SORM/refiner가 기능적으로 분리 | ORM score와 error location; refinement 생성 후 candidate reranking | Main evaluation에서는 No | 수학 추론, learned verifier와 post-generation selection |
| ReVISE | 한 모델의 연속 generation 안에서 control token으로 구분 | `[eos]` 또는 `[refine]`; `[refine]`이 correction continuation을 직접 조건화 | 별도 call 관점에서는 No | SFT+DPO 기반 integrated mechanism |
| 현재 연구 | Decision과 각 refinement stage가 별도 prompt/call | `PRESERVE` 또는 `REFINE`; Decision 내용은 C/P/Revision에 전달하지 않음 | Protocol-implied execution은 Yes; 실험 수집은 No | training-free standalone Decision의 효과를 shared-initial counterfactual로 분석 |

따라서 “Decision call로 후속 refinement 실행 여부를 정한다”는 system pattern 자체는 code
generation 밖에서 더 명시적인 선례를 찾을 수 있다. 다만 기존 사례는 대체로 판단과 critique를
한 artifact에 결합해 그 내용을 refiner에 전달하거나, learned verifier와 post-generation
selection을 사용한다. 현재 연구처럼 binary Decision을 독립 call로 관찰하면서 그 내용을
후속 refinement에 전달하지 않고, 동일 initial candidate의 always-refine 결과까지 물리적으로
수집해 Decision의 counterfactual consequence를 분석하는 설계와는 구분된다.
현재 실험에서 `REFINE`만 실제 생성하는 것은 아니다. `R`, `CR`, `CPR` candidate는 모든
valid initial candidate에 대해 물리적으로 수집하고, 저장된 Decision으로 `DR`, `DCR`,
`DCPR`을 사후 파생한다. `PRESERVE`일 때 refinement call을 생략한다는 설명은 배포 가능한
Decision-conditioned protocol과 protocol-implied token cost를 뜻한다. 이 counterfactual
수집이 있어야 `PRESERVE`가 prevented regression인지 missed repair인지 직접 구분할 수 있다.

따라서 관련 근거는 세 층으로 구분한다. ART, GLoRe, DeCRIM은 일반 reasoning과 instruction
following에서 Decision-like assessment를 Revision과 분리한 구조적 선례를 제공한다.
ReVISE는 conventional code generation에서 refine-or-stop을 적용한 가장 가까운 직접
선례이고, RubricRefine은 code-mode tool use의 인접 선례다. 현재 연구는 selective
refinement 자체의 최초 제안을 주장하지 않는다. 대신 standalone Decision을 관찰 가능한
별도 call로 구현하고, shared initial candidate에서 그 Decision이 만든 prevented regression,
missed repair, exact preservation, token saving을 여러 refinement path에 걸쳐 분리해
측정한다.

### 3.4 Stage composition and cost

기존 연구는 critique, explanation, planning, localization, repair를 여러 형태로 분리한다.
Code Reffix는 broad reflection generation과 reflection-guided repair를 별도 task로 평가하고 (`di-etal-2026-code`), CodeReviewQA는 code review comprehension을 change type recognition, localization, solution identification으로 분해한다 (`lin-etal-2025-codereviewqa`).
COAST는 debugging을 localization, identification, repair 등의 능력으로 나누어 학습 데이터를 구성한다 (`yang-etal-2025-coast`).
이들은 intermediate stage를 구분할 필요성을 뒷받침하지만, natural-language specification에서 모델이 생성한 initial candidate를 shared-initial design으로 수정하는 실험은 아니다.
따라서 Critique와 Plan의 구체적 분리는 본 연구가 책임져야 하는 construct choice이며,
v0.2.0의 broad Critique+Plan 중첩 결과는 참고용으로 남기고 결과 확인 뒤 소급해 최종
설계로 정당화하지 않는다. 수정된 prompt bytes와 입력 경계는 v0.3.0 outcome 생성 전에 고정한다.

추가 computation의 가치가 항상 보장되는 것도 아니다.
Is Self-Repair a Silver Bullet for Code Generation?은 repair call의 배분과 independent resampling을 비교하여 반복 repair가 항상 더 효율적이지 않음을 보였다 (`olausson2024selfrepair`).
Feedback Over Form은 small local models에서 execution feedback과 early stopping이 pipeline topology보다 중요할 수 있다고 보고한다 (`mcandrews2026feedback`).
AgentCoder와 RepairAgent는 token 또는 monetary cost를 보고하지만, multi-agent execution workflow와 repository-level repair를 다룬다 (`huang2023agentcoder`, `bouzenia2025repairagent`).
현재 연구는 같은 local model과 shared initial candidate 안에서 stage별 token consumption을 측정하므로 이들과 다른 비용 질문에 답한다.

## 4. 핵심 문헌 요약표

| Citation key | 핵심 기여 | 현재 연구와의 연결 | 중요한 차이 |
|---|---|---|---|
| `shridhar-etal-2024-art` | 별도 Asker가 refinement 필요성을 판단하고 필요한 사례만 Refine으로 보낸 뒤 Truster가 결과 선택 | Decision과 Revision을 물리적으로 분리한 가장 직접적인 구조적 선례 | 수학·QA, 학습된 별도 모델, subquestion 전달, post-refinement selection |
| `havrilla2024glore` | refinement를 when, where, how로 분해하고 각각 ORM, SORM, refiner로 구현 | Decision을 Critique/Revision과 다른 기능으로 정의하는 construct 근거 | 수학 추론; main evaluation은 사전 gate가 아니라 refinement 생성 후 reranking |
| `madaan2023selfrefine` | same-model feedback followed by revision | `CR`의 개념적 출발점 | code-specific paired transition과 stage ablation이 중심이 아님 |
| `cho-etal-2025-self` | small models의 feedback-free correction, repair와 regression 분리 | preservation과 transition analysis에 가장 가까움 | training-based이며 `R/CR/CPR` 비교와 standalone Decision 없음 |
| `kumar2025score` | external-feedback-free self-correction training | intrinsic self-correction의 대표 연구 | proprietary trained models, explicit critique와 plan 없음 |
| `jiang-etal-2026-reflexicoder` | execution-free reflection and correction trajectory | open-weight feedback-free code correction | stages가 separate calls가 아니라 하나의 learned trajectory |
| `pmlr-v267-lee25ab` | SFT+DPO curriculum으로 intrinsic verification과 correction을 학습하고 MBPP 평가 | conventional code generation의 가장 가까운 Decision 선례 | `[eos]`/`[refine]`이 한 generation에 통합되며 standalone call과 Decision-only effect 분석이 아님 |
| `yu-etal-2025-training` | downstream refinement utility로 critic 학습 | Critique Generation의 효용과 직접 연결 | general framework이며 code는 여러 task 중 하나 |
| `zhang2026scope` | structured subgoal critique for code revision | critique content와 revision 연결 | 2026 preprint, trained critic과 execution-based reward 사용 |
| `chen2024selfdebug` | explanation 및 execution-guided iterative debugging | explanation과 revision을 분리한 대표 연구 | 주요 code conditions가 execution feedback 사용 |
| `olausson2024selfrepair` | repair와 resampling의 budget allocation 비교 | 추가 call의 실용적 가치와 비용 | failing candidates와 execution feedback 중심 |
| `guo2026codechateval` | multi-turn editing의 functional regression | correct-code preservation의 직접 근거 | 외부 developer instruction이며 self-generated critique가 아님 |
| `jin2026reliable` | correct code의 false rejection과 overcorrection | 불필요한 refinement 위험 | review judgment이며 code transition은 아님 |
| `mcandrews2026feedback` | local small models에서 feedback, topology, early stopping 비교 | local inference와 stage-cost 논의 | single-author preprint, execution-guided setting |
| `levine2026rubricrefine` | training-free pre-execution rubric refinement | execution 전 self-review와 selective repair | tool-use agent reliability가 중심인 preprint |

## 5. 보조 문헌

### Execution-guided refinement and debugging

- `ding2024cycle`: execution feedback을 이용한 small code model self-refinement training.
- `jiang2024ledex`: explanation과 refinement trajectory를 학습한 self-debugging.
- `shinn2023reflexion`: environment feedback을 verbal reflection과 episodic memory로 변환.
- `zhang-etal-2023-self`: example-test result를 fault-aware editor에 제공.
- `zheng-etal-2024-opencodeinterpreter`: generation, execution, feedback, refinement를 결합한 open code system.
- `chen-etal-2025-revisit`: self-generated test bias와 execution-state 제공 방식 분석.
- `zhong-etal-2024-debug`: basic-block runtime state를 이용한 debugging.
- `huang2026tracecoder`: trace-driven diagnosis, repair, rollback을 사용하는 multi-agent system.

### Critique, review, and stage decomposition

- `palmeira-ferraz-etal-2024-llm`: Critic이 multi-constraint response의 refinement 필요성과 위치를 판단한 뒤 Refiner가 수정하는 instruction-following pipeline.
- `di-etal-2026-code`: reflection generation과 repair를 분리한 benchmark.
- `lin-etal-2025-codereviewqa`: review comprehension을 recognition, localization, solution identification으로 분해.
- `yang-etal-2025-coast`: debugging 능력을 여러 stage로 분해한 data synthesis와 training.
- `le2024indict`: security와 helpfulness critic의 internal dialogue를 code generation에 사용.

### Verification, agents, and cost context

- `chen2023codet`: generated tests와 execution agreement를 이용한 candidate selection.
- `pmlr-v202-ni23b`: execution result를 입력으로 받는 learned verifier와 reranking.
- `huang2023agentcoder`: test generation과 execution을 분리한 multi-agent refinement 및 token overhead.
- `islam-etal-2024-mapcoder`: retrieval, planning, coding, debugging으로 구성된 multi-agent code generation.
- `bouzenia2025repairagent`: repository-level autonomous repair와 token 및 monetary cost.
- `xia2024agentless`: localization, repair, validation으로 단순화한 repository-level workflow와 비용 효율.

## 6. 주변 문헌과 사용 제한

다음 논문은 문헌 지도에는 포함하지만, 현재 Background가 길어지는 것을 막기 위해 특별한 논지가 없는 한 인용하지 않는 편이 적절하다.

| Citation key | 제한 이유 |
|---|---|
| `yang2023intercode` | interactive coding benchmark이며 refinement method가 아님 |
| `zhou2025refinecoder` | inference candidate가 아니라 training data와 model series를 refinement |
| `ding2024semcoder` | semantic reasoning training이 핵심이며 protocol comparison이 아님 |
| `gou2024critic` | general tool-assisted self-correction이며 conventional code generation evidence가 약함 |
| `huang2024effilearner` | functional correctness가 아니라 runtime 및 memory efficiency가 목표 |
| `chen2024funcoder` | post-generation revision이 아니라 pre-generation decomposition과 consensus |
| `niu2025rechisel` | hardware description language와 compiler 및 simulator feedback이라는 특수 domain |
| `li-etal-2025-rethinkmcts` | generated code가 아니라 pre-generation reasoning thought를 수정 |
| `yang2024sweagent` | agent-computer interface와 repository interaction이 중심 |
| `liu-etal-2026-mdeval` | multilingual debugging benchmark이며 self-refinement protocol이 아님 |
| `andriushchenko-etal-2026-efficient` | hallucination detector가 핵심이며 end-to-end refinement를 평가하지 않음 |
| `wen-etal-2026-coderise` | ultra-low-resource language를 위한 training curriculum이 중심 |

SelfRACG는 retrieval requirement를 생성하고 외부 code knowledge를 검색하는 연구다.
Initial candidate의 review, preservation, revision과 직접 연결되지 않으므로 현재 bibliography에서 제외했다.

## 7. Background 작성에 사용할 연구 공백

검토한 문헌은 다음 사항을 각각 다룬다.

- same-model self-feedback과 revision
- execution-guided debugging과 test-generated feedback
- self-correction을 위한 training
- code editing 중 functional regression
- correct code의 false rejection
- refinement 필요성 판단과 revision의 기능적 분리
- learned refine-or-stop behavior와 candidate verification
- multi-stage agents와 additional inference cost

그러나 검토한 문헌 중 다음 조건을 하나의 controlled experiment에서 함께 다룬 연구는 확인하지 못했다.

1. Locally deployable open-weight code models만을 평가한다.
2. 모든 protocol이 exact same initial candidate를 사용한다.
3. 모델 입력에서 execution feedback과 external verifier feedback을 제외한다.
4. Direct Revision, Critique-Conditioned Revision, Critique-and-Plan-Conditioned Revision을 누적 stage composition으로 비교한다.
5. Initially incorrect candidates의 Repair와 initially correct candidates의 Correct-to-Incorrect Regression을 함께 측정한다.
6. Refinement-Need Decision이 만든 Prevented Regression과 Missed Repair를 구분한다.
7. 각 stage의 token consumption과 final correctness를 함께 비교한다.

따라서 현재 연구의 공백은 "code self-refinement 연구가 없다"는 것이 아니다.
Decision과 Revision의 분리 역시 현재 연구가 처음 제안하는 construct가 아니다.
더 정확한 주장은, 기존 연구가 general reasoning 또는 instruction following에서 이러한
분리를 사용했거나, ReVISE처럼 code generation에서 학습된 integrated refine-or-stop
mechanism의 전체 성능을 보고했다는 것이다. Standalone Decision의 효과를 execution
feedback 없는 local code generation에서 shared-initial counterfactual로 분리하여 prevented
regression, missed repair, exact preservation, token saving까지 함께 분석한 근거는 제한적이다.

## 8. 권장 Background 구성

실제 논문의 Background는 별도 subsection을 많이 만들기보다 다음 네 문단 정도로 압축하는 것이 적절하다.

1. **Self-refinement의 기본 구조**: Self-Refine을 중심으로 same-model critique와 revision을 정의하고, SCoRe, CoCoS, ReflexiCoder를 이용해 feedback-free self-correction과 training-based approaches를 소개한다.
2. **Code refinement에서 execution feedback의 역할**: Teaching Large Language Models to Self-Debug, CYCLE, OpenCodeInterpreter, Revisit Self-Debugging을 묶어 execution-guided 계열을 설명하고 현재 연구의 input boundary를 명확히 한다.
3. **Decision 분리와 selective refinement**: ART와 GLoRe로 whether-to-refine와 how-to-refine의 기능적 분리 근거를 제시하고, DeCRIM을 일반 instruction-following 사례로 짧게 보완한다. ReVISE는 MBPP를 평가한 가장 가까운 conventional code-generation 선례로 구분하고, RubricRefine은 code-mode tool-use 인접 사례로만 기술한다. CoCoS, CodeChat-Eval, Are LLMs Reliable Code Reviewers?는 preservation과 regression 위험의 근거로 연결한다.
4. **Research gap**: Decision 분리 자체의 신규성을 주장하지 않는다. 기존 연구가 standalone Decision의 candidate-level consequences를 `R/CR/CPR`, shared initial candidate, prevented regression, missed repair, exact preservation, stage token cost와 함께 비교하지 않았다는 제한된 공백을 제시한다.

Self-Repair와 Feedback Over Form은 cost paragraph나 research gap 마지막 문단에서 한두 문장으로 추가할 수 있다.
나머지 보조 문헌은 모든 연구를 나열하기보다 특정 주장에 필요한 경우에만 선택적으로 인용하는 편이 안전하다.
