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
Decision -> Critique -> Plan -> Revision
   D          C          P        R
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

`PRESERVE`는 exact initial candidate를 반환한다는 의미다.
새로운 코드 생성 call을 수행하거나 initial candidate를 다시 출력하게 하지 않는다.
이 규칙은 보존 결정 이후의 불필요한 코드 변화와 추가 비용을 방지한다.

## 4. Critique Generation (C)

**Critique Generation**은 task specification과 initial candidate를 검토하여 잠재적인 기능적 문제를 자연어로 기술하는 stage다.

Critique는 다음 내용에 집중한다.

- Task specification에서 요구하는 동작과 candidate가 구현한 동작 사이의 잠재적 불일치
- 누락된 조건 또는 잘못 처리될 수 있는 edge case
- 수정이 필요하다고 판단되는 이유
- 문제가 발견되지 않은 경우 initial candidate를 유지하라는 recommendation

Critique Generation은 완성된 revised solution 전체를 생성하지 않는다. Fault localization과
설명을 위해 관련 코드 일부를 인용하거나 code fence를 사용하는 것은 허용한다.
또한 구체적인 edit sequence를 완성된 revision plan 형태로 작성하지 않는다.
이 제한은 Critique와 Revision Planning의 역할을 구분하기 위한 것이다.

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

본 연구에서 Plan은 Critique 이후에만 사용한다.
Critique 없이 바로 Plan을 생성하는 별도 protocol은 정의하지 않는다.
Critique가 없는 Plan은 결함 식별과 수정 계획을 하나의 call에 함께 요구하므로, Critique 이후 Plan과 동일한 stage로 해석하기 어렵기 때문이다.

## 6. Code Revision (R)

**Code Revision**은 task specification, initial candidate, 그리고 protocol에서 제공하는 critique artifact와 revision plan을 입력으로 받아 revised candidate를 생성하는 stage다.

Revision의 입력은 protocol에 따라 달라진다.

- `R`: task specification, initial candidate
- `CR`: task specification, initial candidate, critique
- `CPR`: task specification, initial candidate, critique, plan

모든 Revision stage는 동일한 출력 요구사항을 사용한다.
모델은 최종적으로 평가 가능한 revised code를 정확히 하나의 완전한 `python` fence 안에
포함해야 한다. Fence 밖의 설명문은 candidate artifact에 포함하지 않으며, 다중 fence,
불완전 fence, unfenced code에는 candidate를 선택하는 추측이나 구문 수정을 적용하지 않는다.
Critique나 plan이 수정을 제안하더라도, 모델은 candidate가 이미 적절하다고 판단하면 initial candidate를 변경하지 않을 수 있다.

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

별도의 Critique Generation call을 수행하고, critique artifact를 Code Revision에 전달한다.

### CPR: Critique-and-Plan-Conditioned Revision

```text
Initial Candidate -> Critique -> Plan -> Revision -> Final Candidate
```

Critique 이후 별도의 Revision Planning call을 수행하고, critique와 plan을 모두 Revision에 전달한다.

`R`, `CR`, `CPR`은 stage를 차례로 추가하는 구조다.
`CR`은 `R`에 Critique Generation을 추가하고, `CPR`은 `CR`에 Revision Planning을 추가한다.

## 8. Decision-Conditioned Refinement

**Decision-Conditioned Refinement**는 Refinement-Need Decision에 따라 Always-Refine Protocol을 선택적으로 적용하는 방식이다.

Decision이 `PRESERVE`이면 final candidate는 exact initial candidate다.
Decision이 `REFINE`이면 지정된 Always-Refine Protocol의 final candidate를 사용한다.

이에 따라 다음 세 구성이 정의된다.

- `DR`: Decision-Conditioned Direct Revision
- `DCR`: Decision-Conditioned Critique-Conditioned Revision
- `DCPR`: Decision-Conditioned Critique-and-Plan-Conditioned Revision

Decision 결과는 Critique Generation, Revision Planning, Code Revision prompt에 전달하지 않는다.
Decision은 initial candidate를 보존할지, 대응하는 Always-Refine Protocol의 revised candidate를 사용할지만 결정한다.
따라서 Always-Refine Protocol과 Decision-Conditioned Refinement의 차이는 candidate별 refinement 실행 여부에 있다.

## 9. Protocol의 해석 범위

본 연구에서 stage 추가의 효과는 해당 stage를 포함한 전체 protocol과 포함하지 않은 protocol의 차이를 의미한다.
예를 들어 `CR`과 `R`의 차이는 Critique Generation call, 생성된 critique artifact, 추가 token consumption이 결합된 효과다.
Critique artifact의 의미적 정확성이나 모델의 critique 능력을 독립적으로 평가하는 것으로 해석하지 않는다.

마찬가지로 `CPR`과 `CR`의 차이는 Revision Planning을 추가한 전체 protocol의 효과다.
Decision-Conditioned Refinement의 효과는 Decision의 classification accuracy만이 아니라, prevented regression, missed repair, 생략한 refinement calls를 포함한다.
