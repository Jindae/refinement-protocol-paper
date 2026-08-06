# 코드 생성 Self-Refinement 문헌 통합 요약

## 1. 통합 결과

두 보고서에서 제목과 출판본 중복을 제거하면 44개의 고유 후보가 남는다.
이 중 SelfRACG는 initial candidate의 검토, 수정, 보존, 또는 선택을 다루지 않는 retrieval-augmented code generation 연구이므로 현재 연구의 Background에서는 제외했다.
나머지 43편은 `references.bib`에 수록했다.

43편을 현재 연구와의 관련성에 따라 다시 분류하면 다음과 같다.

| 분류 | 수 | 용도 |
|---|---:|---|
| 핵심 문헌 | 13 | Background의 주요 논지와 research gap을 직접 뒷받침 |
| 보조 문헌 | 18 | execution-guided refinement, stage decomposition, verification, agent workflow의 범위를 설명할 때 선택적으로 사용 |
| 주변 문헌 | 12 | 전체 문헌 지도에는 포함하지만 현재 논문의 Background에서는 원칙적으로 생략 |
| 제외 | 1 | 현재 연구와의 연결이 약하여 bibliography에서도 제외 |

이 분류는 논문의 품질이나 영향력에 대한 평가가 아니다.
현재 연구의 조건인 code generation, shared initial candidate, execution-feedback-free inference, explicit stage composition, correct-to-incorrect regression, Refinement-Need Decision, token cost와의 관련성을 기준으로 한 분류다.

## 2. 검증 과정에서 수정한 정보

| 논문 | 보고서의 문제 | 검증 후 정보 |
|---|---|---|
| CodeChat-Eval | 제목에서 `Large Language Models`가 `LLMs`로 축약됨 | 공식 제목은 *CodeChat-Eval: Evaluating Large Language Models in Multi-Turn Code Refinement Dialogues* |
| ReChisel | 출판 venue 미확정 preprint로 기재 | DAC 2025 출판본 확인, DOI `10.1109/DAC63849.2025.11132940` |
| ReVISE | code benchmark 포함 여부가 불명확하게 기술됨 | MBPP 실험을 포함함. 다만 주된 실험과 논지는 일반 reasoning 및 학습된 intrinsic verification에 있음 |
| CRITIC | code refinement 문헌처럼 분류될 여지가 있음 | code interpreter를 사용하지만 주요 code-related task는 mathematical program synthesis에 가까움. 일반적인 자연어-to-code refinement의 핵심 근거로 사용하지 않는 편이 안전함 |
| RefineCoder | inference-time candidate refinement와 가까운 것으로 분류됨 | external critic과 LLM-as-a-judge를 이용해 training data와 model series를 개선하는 연구임. 현재 protocol의 직접 선행연구로 보기 어려움 |
| FunCoder | refinement 및 planning 문헌으로 분류됨 | initial candidate를 수정하기보다 generation 과정에서 recursive function decomposition과 consensus를 사용하는 방법임 |
| RethinkMCTS | code revision 연구로 분류될 여지가 있음 | execution feedback으로 pre-generation reasoning thought를 수정하는 search framework이며, 생성된 initial code의 post-hoc revision과는 다름 |
| Efficient Hallucination Detection | selective refinement 방법처럼 기술됨 | detector와 dataset이 핵심이며, detector를 사용한 end-to-end preserve/refine protocol은 직접 평가하지 않음 |

기존 `references.bib`에서 이미 반영한 출판 상태도 유지했다.
SCoRe는 ICLR 2025, Teaching Large Language Models to Self-Debug는 ICLR 2024, OpenCodeInterpreter는 Findings of ACL 2024, InterCode는 NeurIPS 2023, TraceCoder는 ICSE 2026, CYCLE은 PACMPL 8(OOPSLA1) 출판본을 사용했다.

## 3. Background에서 사용할 핵심 연구 흐름

### 3.1 Execution feedback 없는 self-refinement와 explicit critique

Self-Refine은 동일 모델이 output을 생성하고, natural-language self-feedback을 만든 뒤, 그 feedback을 사용해 output을 수정하는 일반 프레임워크를 제시했다 (`madaan2023selfrefine`).
현재 연구의 `CR`과 가장 가까운 개념적 출발점이지만, code task에 대한 shared-initial functional transition이나 critique stage의 독립적인 증분 효과가 중심은 아니다.

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

CoCoS는 repair와 regression을 직접 분리해 보고하므로 현재 연구의 transition analysis와 가장 가까운 선행연구다 (`cho-etal-2025-self`).
그러나 CoCoS의 목적은 correction-preserving model training이며, 별도 model call로 구현된 Critique Generation, Revision Planning, Refinement-Need Decision의 효과를 비교하지 않는다.

CodeChat-Eval은 외부에서 주어진 multi-turn refinement instruction을 따르는 동안 initially correct code의 functional correctness가 손상될 수 있음을 보였다 (`guo2026codechateval`).
이는 code editing의 preservation 문제를 직접 다루지만, instruction이 self-generated critique가 아니고 repair가 필요한 candidate를 판별하는 실험도 아니다.

Are LLMs Reliable Code Reviewers?는 requirement conformance 판단에서 correct code를 잘못 reject하는 overcorrection을 분석했다 (`jin2026reliable`).
이 결과는 Refinement-Need Decision이 initially correct candidate에 불필요한 refinement를 적용할 위험을 설명하는 데 유용하다.
다만 이 연구의 outcome은 review judgment의 false rejection이며, revised code의 correct-to-incorrect transition과 동일하지 않다.

ReVISE는 learned refine-or-stop mechanism을 사용하며 (`pmlr-v267-lee25ab`), RubricRefine은 pre-execution rubric으로 tool-use code를 검사하고 수정한다 (`levine2026rubricrefine`).
CodeT와 LEVER는 candidate를 수정하지 않고 generated tests 또는 execution-aware verifier로 여러 candidates를 선택한다 (`chen2023codet`, `pmlr-v202-ni23b`).
이 연구들은 selective computation과 candidate preservation의 인접 근거지만, 현재 연구의 exact preservation을 수행하는 standalone Decision과는 다르다.

### 3.4 Stage composition and cost

기존 연구는 critique, explanation, planning, localization, repair를 여러 형태로 분리한다.
Code Reffix는 reflection generation과 reflection-guided repair를 별도 task로 평가하고 (`di-etal-2026-code`), CodeReviewQA는 code review comprehension을 change type recognition, localization, solution identification으로 분해한다 (`lin-etal-2025-codereviewqa`).
COAST는 debugging을 localization, identification, repair 등의 능력으로 나누어 학습 데이터를 구성한다 (`yang-etal-2025-coast`).
이들은 intermediate stage를 구분할 필요성을 뒷받침하지만, natural-language specification에서 모델이 생성한 initial candidate를 shared-initial design으로 수정하는 실험은 아니다.

추가 computation의 가치가 항상 보장되는 것도 아니다.
Is Self-Repair a Silver Bullet for Code Generation?은 repair call의 배분과 independent resampling을 비교하여 반복 repair가 항상 더 효율적이지 않음을 보였다 (`olausson2024selfrepair`).
Feedback Over Form은 small local models에서 execution feedback과 early stopping이 pipeline topology보다 중요할 수 있다고 보고한다 (`mcandrews2026feedback`).
AgentCoder와 RepairAgent는 token 또는 monetary cost를 보고하지만, multi-agent execution workflow와 repository-level repair를 다룬다 (`huang2023agentcoder`, `bouzenia2025repairagent`).
현재 연구는 같은 local model과 shared initial candidate 안에서 stage별 token consumption을 측정하므로 이들과 다른 비용 질문에 답한다.

## 4. 핵심 문헌 요약표

| Citation key | 핵심 기여 | 현재 연구와의 연결 | 중요한 차이 |
|---|---|---|---|
| `madaan2023selfrefine` | same-model feedback followed by revision | `CR`의 개념적 출발점 | code-specific paired transition과 stage ablation이 중심이 아님 |
| `cho-etal-2025-self` | small models의 feedback-free correction, repair와 regression 분리 | preservation과 transition analysis에 가장 가까움 | training-based이며 `R/CR/CPR` 비교와 standalone Decision 없음 |
| `kumar2025score` | external-feedback-free self-correction training | intrinsic self-correction의 대표 연구 | proprietary trained models, explicit critique와 plan 없음 |
| `jiang-etal-2026-reflexicoder` | execution-free reflection and correction trajectory | open-weight feedback-free code correction | stages가 separate calls가 아니라 하나의 learned trajectory |
| `pmlr-v267-lee25ab` | intrinsic verification을 통한 refine-or-stop | Refinement-Need Decision의 개념적 인접 연구 | training-based integrated token, 주요 분석은 reasoning 중심 |
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

다음 논문은 `references.bib`에는 포함했지만, 현재 Background가 길어지는 것을 막기 위해 특별한 논지가 없는 한 인용하지 않는 편이 적절하다.

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
더 정확한 주장은, 기존 연구가 feedback source, training method, agent architecture, 또는 final performance 개선에 주로 초점을 두었으며, execution feedback이 없는 local code generation에서 explicit refinement stage를 하나씩 추가했을 때의 correctness와 token-cost 효과를 shared-initial design으로 분리한 근거가 제한적이라는 것이다.

## 8. 권장 Background 구성

실제 논문의 Background는 별도 subsection을 많이 만들기보다 다음 네 문단 정도로 압축하는 것이 적절하다.

1. **Self-refinement의 기본 구조**: Self-Refine을 중심으로 same-model critique와 revision을 정의하고, SCoRe, CoCoS, ReflexiCoder를 이용해 feedback-free self-correction과 training-based approaches를 소개한다.
2. **Code refinement에서 execution feedback의 역할**: Teaching Large Language Models to Self-Debug, CYCLE, OpenCodeInterpreter, Revisit Self-Debugging을 묶어 execution-guided 계열을 설명하고 현재 연구의 input boundary를 명확히 한다.
3. **Regression과 selective refinement**: CoCoS, CodeChat-Eval, Are LLMs Reliable Code Reviewers?, ReVISE를 이용해 repair뿐 아니라 preservation과 refinement decision이 필요함을 설명한다.
4. **Research gap**: 기존 연구가 `R/CR/CPR`, shared initial candidate, Decision consequences, stage token cost를 함께 비교하지 않았다는 제한된 공백을 제시한다.

Self-Repair와 Feedback Over Form은 cost paragraph나 research gap 마지막 문단에서 한두 문장으로 추가할 수 있다.
나머지 보조 문헌은 모든 연구를 나열하기보다 특정 주장에 필요한 경우에만 선택적으로 인용하는 편이 안전하다.
