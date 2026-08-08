# Self-Refinement Protocol

## 1. Protocol의 기본 정의

본 연구에서 self-refinement는 동일한 모델이 task specification, 자신이 생성한 initial candidate, 자신이 생성한 intermediate artifact만을 이용하여 candidate를 보존하거나 수정하는 과정이다.
모델에는 테스트 결과, 실행 결과, 컴파일 오류, runtime trace 또는 외부 평가자의 feedback을 제공하지 않는다.

전체 개념적 흐름은 다음과 같다.

```text
Task Specification
        |
        v
Direct Generation
        |
        v
Initial Candidate
        |
        v
Decision (stored once; used only for derived selection)

Initial Candidate -> Direct Revision                         (R)
Initial Candidate -> Critique -> Critique-based Revision    (CR)
Initial Candidate -> Critique -> Plan -> Plan-based Revision (CPR)

Initial Candidate -> one call explicitly sequencing C-R       (SC-CR)
Initial Candidate -> one call explicitly sequencing C-P-R     (SC-CPR)
Initial Candidate -> one call explicitly sequencing D-R       (SC-DR)
Initial Candidate -> one call explicitly sequencing D-C-R     (SC-DCR)
Initial Candidate -> one call explicitly sequencing D-C-P-R   (SC-DCPR)
```

`D`, `C`, `P`, `R`은 모델 내부의 숨겨진 reasoning 단계를 의미하지 않는다.
각 항목은 별도의 prompt와 model call로 구현한 Refinement Stage다.

## 2. Direct Generation

**Direct Generation**은 task specification만을 이용해 initial candidate를 생성하는 과정이다.
이 결과는 모든 refinement protocol의 공통 시작점이다.

Direct Generation의 출력은 다음 역할을 갖는다.

- 모델이 스스로 생성한 refinement 대상
- refinement 전 기능적 정확성을 측정하는 기준
- 모든 protocol에서 재사용되는 shared initial candidate
- Decision이 `PRESERVE`를 반환할 때 그대로 채택되는 candidate

## 3. Refinement-Need Decision (D)

**Refinement-Need Decision**은 initial candidate를 그대로 보존할지 refinement를 수행할지 결정하는 stage다.
Decision은 task specification과 initial candidate만을 입력으로 받는다.

Decision의 출력은 다음 두 값 중 하나다.

- `PRESERVE`: initial candidate를 수정하지 않고 최종 결과로 사용
- `REFINE`: 평가 중인 Always-Refine Protocol을 수행

Decision은 결함의 상세 원인이나 수정 방법을 생성하지 않는다.
이 stage는 candidate의 결함을 설명하는 것이 아니라, initial candidate를 보존할지 refinement를 실행할지만 결정한다.

### 3.1 Decision parsing과 제한적 의미 판정

모델 call은 제약 없는 동일한 generation 설정을 사용하며, primary parser는 주변 공백을
제외한 응답 전체가 정확히 `PRESERVE` 또는 `REFINE`일 때만 Decision artifact를 만든다.
설명문을 일반 parser가 keyword 검색이나 heuristic으로 자동 변환하지 않는다.

모든 모델의 Decision call이 끝난 뒤에도 parse되지 않은 응답이 있으면, candidate
evaluation을 시작하기 전에 그 응답 전부를 한 번의 별도 adjudication 단계에서 검토한다.
검토자는 고정된 rubric에 따라 모델이 이미 표현한 방향만 다음과 같이 코딩한다.

- 응답이 candidate가 기능적으로 맞고 specification을 충족하며 기능 변경이 필요 없다고
  명백히 말하면 `PRESERVE`
- 응답이 기능적 결함을 명백히 지적하거나 기능적 revision이 필요하다고 명백히 말하면
  `REFINE`
- 양쪽 신호가 섞였거나, 서로 모순되거나, 단순 설명에 그치거나, 방향을 판단할 수 없게
  잘린 경우에는 `UNRESOLVED`

검토에는 raw Decision response와 해당 call이 원래 볼 수 있었던 task specification 및
exact initial candidate만 사용할 수 있다. Reference solution, hidden tests, benchmark
evaluation, compiler/runtime diagnostic, timeout 및 이후 refinement 결과는 사용할 수 없다.
원래 ModelCall의 `invalid_response`, raw bytes, finish reason과 token counts는 변경하지 않으며,
판정 결과와 rationale은 별도 versioned artifact로 저장한다. `UNRESOLVED`는 어느 값으로도
대체하지 않으며 해당 Decision-conditioned outcomes는 unavailable로 남긴다.

응답 전체가 `PRESERVE.` 또는 `REFINE.`인 경우에 한해 주변 공백과 마지막 ASCII 마침표
하나만 제거하는 결정적 정규화를 먼저 적용한다. 이는 의미 판정과 구분해 `normalized`로
기록한다. 그 밖의 응답만 위 rubric으로 판정하며 `adjudicated`로 기록한다. 원본 call은
두 경우 모두 `invalid_response`인 채 보존된다.

`PRESERVE`는 exact initial candidate를 반환한다는 의미다.
새로운 코드 생성 call을 수행하거나 initial candidate를 다시 출력하게 하지 않는다.
이 규칙은 보존 결정 이후의 불필요한 코드 변화와 추가 비용을 방지한다.

## 4. Critique Generation (C)

**Critique Generation**은 task specification과 initial candidate를 검토하여 기능적 문제가
있는지 판단하고, 발견한 문제의 root cause와 관련 코드 위치를 자연어로 식별하는 stage다.
오류의 존재를 전제하지 않으며, 기능 문제가 없다고 판단하면 그 사실을 명시한다.

Critique는 다음 내용에 집중한다.

- Task specification과 candidate 동작 사이의 기능적 불일치
- 각 문제의 root cause와 관련 코드 위치
- 문제가 발견되지 않았다는 명시적 진술

Critique prompt의 핵심 지시는 문제의 원인과 위치를 분석하는 것이다. 관련 코드 일부나
code fence가 포함되어도 artifact를 거부하지 않으며, 모델이 부수적으로 수정 방향을
언급해도 parser가 삭제하거나 invalid 처리하지 않는다. 역할 분리는 장문의 금지 목록이
아니라 후속 입력 경계로 보장한다. Revision Planning은 critique를 받아 수정 방법을
구체화하고, Plan-Conditioned Revision은 critique 원문이 아니라 plan만 받는다.

Critique artifact는 Code Revision 또는 Revision Planning의 입력으로 사용한다.
연구에서는 critique 자체에 독립적인 correctness label을 부여하지 않는다.
Critique를 포함한 protocol의 가치는 최종 candidate의 기능적 결과로 평가한다.

## 5. Revision Planning (P)

**Revision Planning**은 task specification, initial candidate, critique artifact를 이용하여 candidate 수정 계획을 작성하는 stage다.

Plan은 다음을 포함할 수 있다.

- 수정해야 할 코드 동작 또는 논리
- 변경할 조건, 계산, 자료구조 처리 또는 반환 동작
- 기존에 유지해야 할 동작
- 수정 후 task specification을 만족시키기 위한 단계

Plan은 완성된 revised solution 전체를 직접 생성하지 않는다. 변경 위치와 방법을 명확히
하기 위한 focused code snippet 또는 code fence는 허용한다.
Revision Planning은 candidate를 처음부터 다시 검토하는 단계가 아니라, critique artifact의 내용을 실행 가능한 수정 방향으로 구체화하는 단계다.
따라서 Critique가 기능 문제를 식별하면 Planning은 그 진단을 입력으로 받아 해결 방법을
계획하고, Critique가 기능 문제가 없다고 하면 Planning도 변경이 필요 없다고 기록한다.
Planning prompt는 Critique의 진단이 맞는지 독립적으로 재판정하거나 새로운 결함을 탐색하는
두 번째 Critique를 요구하지 않는다.

본 연구에서 Plan은 Critique 이후에만 사용한다.
Critique 없이 바로 Plan을 생성하는 별도 protocol은 정의하지 않는다.
Critique가 없는 Plan은 결함 식별과 수정 계획을 하나의 call에 함께 요구하므로, Critique 이후 Plan과 동일한 stage로 해석하기 어렵기 때문이다.

## 6. Code Revision (R)

**Code Revision**은 task specification, initial candidate, 그리고 해당 protocol이 직접
제공하는 하나의 intermediate artifact를 입력으로 받아 revised candidate를 생성하는 stage다.

Revision의 입력은 protocol에 따라 달라진다.

- `R`: task specification, initial candidate
- `CR`: task specification, initial candidate, critique
- `CPR`: task specification, initial candidate, plan

Revision의 책임도 입력 경로에 따라 다르다.

- Direct Revision인 `R`은 선행 분석 artifact가 없으므로 initial candidate를 직접 검토하고,
  필요한 경우에만 수정한다.
- `CR`의 Revision은 Critique가 식별한 기능 문제를 해결한다. Critique가 기능 문제가 없다고
  하면 initial candidate를 변경 없이 다시 출력하며, 오류 존재 여부를 독립적으로 다시
  검토하라는 지시를 받지 않는다.
- `CPR`의 Revision은 supplied Plan을 구현한다. Plan이 변경 불필요를 나타내면 initial
  candidate를 변경 없이 다시 출력하며, Critique를 보거나 분석·계획을 다시 수행하지 않는다.

모든 Revision stage는 동일한 출력 요구사항을 사용한다.
모델은 최종적으로 평가 가능한 revised code를 정확히 하나의 완전한 `python` fence 안에
포함해야 한다. Fence 밖의 설명문은 candidate artifact에 포함하지 않으며, 다중 fence,
불완전 fence, unfenced code에는 candidate를 선택하는 추측이나 구문 수정을 적용하지 않는다.
이 규칙을 충족하지 못해 candidate artifact가 만들어지지 않은 결과는 정제·보고 단계에서
`malformed_candidate`로 부른다. 완전한 단일 fence에서 추출된 코드는 문법·실행·논리 오류가
있더라도 그대로 candidate이며 evaluator가 판정한다. Conditioned Revision의 no-change
경로는 선행 Critique 또는 Plan이 변경 불필요를 나타낼 때 적용한다. 모델이 지시를 벗어나
선행 artifact를 재판정하거나 다른 역할의 내용을 생성해도 raw response를 수정하지 않으며,
그 결과는 해당 protocol의 실제 동작으로 남긴다.

## 7. Always-Refine Protocol

**Always-Refine Protocol**은 모든 initial candidate에 해당 protocol의 Refinement Stages를 실행한다.

### R: Direct Revision

```text
Initial Candidate -> Revision -> Final Candidate
```

모델이 별도의 critique나 plan 없이 task specification과 initial candidate를 다시 보고 final candidate를 생성한다.

### CR: Critique-Conditioned Revision

```text
Initial Candidate -> Critique -> Revision -> Final Candidate
```

별도의 Critique Generation call을 수행하고, root cause와 위치를 담은 critique artifact를
Code Revision에 직접 전달한다.

### CPR: Critique-and-Plan-Conditioned Revision

```text
Initial Candidate -> Critique -> Plan -> Revision -> Final Candidate
```

Critique 이후 별도의 Revision Planning call을 수행한다. Planning은 critique의 진단을
구체적이고 최소한의 수정 방법으로 변환한다. 마지막 Revision에는 plan만 직접 전달하며
critique 원문은 전달하지 않는다. CPR candidate가 critique record를 lineage로 보존하는 것은
plan을 통한 간접 provenance를 나타내며 prompt input을 뜻하지 않는다.

`R`, `CR`, `CPR`은 동일 initial candidate에서 revision을 유도하는 정보 경로를 비교한다.
`CR`은 별도 진단을 Revision에 직접 제공하고, `CPR`은 그 진단을 Planning이 매개한 뒤
plan만 Revision에 제공한다. 따라서 `CR`과 `CPR`의 차이는 call 하나뿐 아니라 revision에
전달되는 artifact의 역할 분리까지 포함한다.

## 8. Decision-Conditioned Refinement

**Decision-Conditioned Refinement**는 Refinement-Need Decision에 따라 Always-Refine Protocol을 선택적으로 적용하는 방식이다.

엄격 parser가 만든 Decision 또는 위 절차에서 명백하게 판정된 Decision이 `PRESERVE`이면
final candidate는 exact initial candidate다. `REFINE`이면 지정된 Always-Refine Protocol의
final candidate를 사용한다. `UNRESOLVED`이면 해당 세 Decision-conditioned outcomes를
구성하지 않는다.

이에 따라 다음 세 구성이 정의된다.

- `DR`: Decision-Conditioned Direct Revision
- `DCR`: Decision-Conditioned Critique-Conditioned Revision
- `DCPR`: Decision-Conditioned Critique-and-Plan-Conditioned Revision

Decision 결과는 Critique Generation, Revision Planning, Code Revision prompt에 전달하지 않는다.
Decision은 initial candidate를 보존할지, 대응하는 Always-Refine Protocol의 revised candidate를 사용할지만 결정한다.
논리적인 protocol 적용에서는 `PRESERVE`가 후속 refinement calls를 생략하고 `REFINE`이
대응 경로를 실행한다. 그러나 본 실험의 물리적 데이터 수집에서는 모든 Always-Refine
candidate를 생성한 뒤 Decision-conditioned final candidate를 파생한다. 이는 `PRESERVE`
사례에서도 발생했을 repair 또는 regression을 관찰하기 위한 것이며, Decision을 후속 prompt
입력으로 사용하는 것과는 다르다.

## 9. Single-Call Role Protocols

`study-v0.4.0`은 multi-call role separation과 비교하기 위해 다섯 generated candidate
conditions를 추가한다.

- `SC-CR`: 한 call 안에서 문제 분석과 revision을 순서대로 지시
- `SC-CPR`: 한 call 안에서 문제 분석, revision planning, revision을 순서대로 지시
- `SC-DR`: 한 call 안에서 Decision과 direct revision path를 순서대로 지시
- `SC-DCR`: 한 call 안에서 Decision, critique 역할, revision을 순서대로 지시
- `SC-DCPR`: 한 call 안에서 Decision, critique 역할, planning 역할, revision을 순서대로 지시

모든 조건은 task specification과 exact initial candidate만 직접 입력으로 받으며 한 번의
model call에서 최종 code를 생성한다. `SC-CR`과 `SC-CPR`은 최종 code만 요구한다.
`SC-DR`, `SC-DCR`, `SC-DCPR`은 첫 non-empty line에 `DECISION: PRESERVE` 또는
`DECISION: REFINE`을 쓰고, 같은 response에 최종 code를 출력하도록 요구한다.

Single-call Decision label은 다음 call을 실제로 중단시키지 않는다. 주 outcome은 label과
관계없이 그 call이 emitted한 code다. 따라서 `PRESERVE` label과 changed code 또는 `REFINE`
label과 unchanged code가 함께 관찰될 수 있다. Label과 code는 독립적으로 parse하며, valid
code와 invalid label은 code candidate를 유지하고 label만 invalid로 기록한다. Malformed code와
valid label은 candidate 없이 label record를 유지한다. 별도 Decision처럼 사람 판독으로 label을
대체하지 않는다.

Supplementary label-enforced outcome은 새 model call 없이 `PRESERVE`이면 exact initial,
`REFINE`이면 emitted code를 선택한다. 이는 main single-call candidate가 아니라 integrated
label을 selection gate처럼 적용했을 때의 파생 결과다.

Single-call prompt에 역할 순서를 적는 것은 내부 reasoning trace가 실제로 그 순서를 따랐음을
증명하지 않는다. `SC-*`와 multi-call protocol의 비교 대상은 prompt-and-call topology 전체다.

## 10. Protocol의 해석 범위

본 연구에서 stage 추가의 효과는 해당 stage를 포함한 전체 protocol과 포함하지 않은 protocol의 차이를 의미한다.
예를 들어 `CR`과 `R`의 차이는 Critique Generation call, 생성된 critique artifact, 추가 token consumption이 결합된 효과다.
Critique artifact의 의미적 정확성이나 모델의 critique 능력을 독립적으로 평가하는 것으로 해석하지 않는다.

마찬가지로 `CPR`과 `CR`의 차이는 Revision Planning을 추가한 전체 protocol의 효과다.
이 비교는 Planning artifact의 독립적인 의미 정확도를 측정하지 않으며, Critique의 진단을
Planning이 변환하고 Revision이 실행하는 전체 정보 경로의 결과다. Upstream artifact의
오진, 역할 미준수 또는 no-change 판단도 downstream 결과와 분리해 임의로 교정하지 않는다.
Decision-Conditioned Refinement의 효과는 Decision의 classification accuracy만이 아니라, prevented regression, missed repair, 생략한 refinement calls를 포함한다.

`study-v0.2.0`에서 사용한 broad Critique 및 Critique+Plan 동시 CPR 입력은 참고용 선행
실행으로 보존한다. `study-v0.3.0`은 역할 분리된 multi-call estimate를 제공한다.
현재 paper-facing `study-v0.4.0`은 그 validated artifacts를 재사용하고 다섯 `SC-*` 조건을
추가한다. 세 버전의 서로 다른 CR/CPR construct를 하나의 protocol estimate로 혼합하지 않는다.

## 11. Post-hoc Option-A Follow-up Boundary

`study-v0.5.0-option-a-pilot`은 accepted protocol panel을 바꾸지 않는 후속 prompt ablation이다.

- `REGEN-NO-INIT`: task specification만으로 처음부터 다시 생성한다.
- `DRAFT-CR-FINAL`: 한 response 안에서 observable draft, 그 draft의 critique, final code를
  순서대로 생성하며 draft와 final을 별도 candidate로 보존한다.
- `C-GENERATE-NO-INITIAL`: task specification과 frozen stored Critique만 받고, Critique가
  원래 다룬 initial code는 받지 않은 채 처음부터 solution을 생성한다.

세 조건 모두 기존 exact initial을 분석 기준과 provenance로만 연결한다. 그 source code는
prompt input이 아니다. `C-GENERATE-NO-INITIAL`의 Critique 자체가 initial에서 파생되고 focused
snippet을 포함할 수 있으므로 candidate-independent generation으로 해석하지 않고
candidate-code-omitted generation으로 한정한다.
