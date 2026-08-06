# Experiment Execution Guidelines

이 문서는 primary experiment와 그에 선행하는 pilot의 **물리적 실행 순서**를 정의한다.
연구 construct, protocol 정의, 입력 의존성은 `documents/`가 정의하며, 이 지침은 그
설계를 바꾸지 않고 GPU 상주 시간, 재개 가능성, 진행 확인을 최적화한다.

## 1. 실행 계층

정상적인 실행 계층은 다음 순서를 따른다.

1. frozen experiment version과 manifest
2. model-resident campaign
3. protocol 또는 shared-artifact phase
4. 세 benchmark의 included task 전체
5. 개별 model call과 immutable artifact

모델을 최외곽 실행 단위로 둔다. 하나의 exact checkpoint를 두 GPU에 한 번 로드한 뒤
그 모델에 필요한 모든 inference phase를 완료하고, completeness gate를 통과한 뒤에만
모델을 내리고 다음 checkpoint를 로드한다. 정상 경로에서 protocol이나 benchmark가
바뀐다는 이유로 같은 모델을 다시 로드하지 않는다.

각 phase는 HumanEval+ 163개, MBPP+ 378개, BigCodeBench-Instruct 1,136개, 합계
1,677개의 included task를 한 background session 안에서 모두 처리한다. 내부 benchmark
순서는 고정할 수 있지만 HumanEval+ 완료 후 사용자 확인을 기다렸다가 MBPP+를 별도
실행하는 식으로 campaign을 분할하지 않는다.

## 2. 모델 하나의 필수 phase 순서

한 모델을 로드한 worker는 다음 phase를 순서대로 수행한다. Phase 전환은 status와
manifest에 기록하는 checkpoint이지, 사용자 개입이나 모델 reload 지점이 아니다.

1. **Direct Generation** (`direct_initial`): 전체 1,677개 task의 exact initial candidate 저장
2. **Refinement-Need Decision** (`decision`): 저장되고 검증된 exact initial candidate에 대한 Decision 생성
3. **Direct Revision** (`r_revision`): 저장된 initial candidate에서 `R` candidate 생성
4. **Critique Generation** (`shared_critique`): 저장된 initial candidate의 critique 생성
5. **Critique-Conditioned Revision** (`cr_revision`): 동일한 stored critique를 이용해 `CR` candidate 생성
6. **Revision Planning** (`shared_plan`): 동일한 stored critique를 이용한 revision plan 생성
7. **Plan-Conditioned Revision** (`cpr_revision`): 동일한 stored critique와 plan을 이용해 `CPR` candidate 생성
8. 모든 phase의 completeness/provenance 검증 후 model unload

Direct Generation과 Refinement-Need Decision은 각각 독립된 전 범위 phase다. Initial candidate를 다른 phase나
protocol에서 재생성해서는 안 되며, Decision도 protocol별로 다시 호출하지 않는다.
Critique는 `CR`과 plan 생성에 공유하고 plan은 `CPR`에 공유한다.

`DR`, `DCR`, `DCPR`은 inference phase가 아니다. 저장된 하나의 Decision과 각각의
`R`, `CR`, `CPR` candidate를 결합해 나중에 파생한다. `PRESERVE`는 exact initial
candidate를 선택하고 `REFINE`은 해당 always-refine candidate를 선택한다. 이 과정에서
추가 model call은 없다.

## 2.1 전체 Decision adjudication 단계

모든 모델 campaign과 Decision call이 끝난 뒤 strict parser가 거부한 Decision response가
하나라도 있으면, benchmark evaluation보다 먼저 하나의 adjudication batch를 실행한다.
일부 model이나 benchmark만 임의로 골라 보지 않고 invalid Decision 전부를 검토한다.

- 검토 입력은 raw Decision response와 그 call의 task specification 및 exact initial
  candidate로 제한한다.
- reference solution, tests, evaluator output, correctness, timeout, runtime, 이후 critique,
  plan 또는 revised candidate를 열람하거나 판정 근거로 사용하지 않는다.
- versioned rubric에 따라 명백한 보존 의도는 `PRESERVE`, 명백한 기능 수정 의도는
  `REFINE`, 나머지는 `UNRESOLVED`로 기록한다.
- 원래 call/status/raw artifact는 그대로 두고 별도 immutable 판독 기록과, 판독된
  Decision에 따라 어떤 저장 후보를 선택했는지 나타내는 D 프로토콜 후보 선택 기록만 추가한다.
- adjudication 완료/전체, resolved/unresolved 수를 status와 count 출력에서 확인할 수
  있어야 한다.
- `UNRESOLVED`를 고정값으로 대체하지 않으며, 해당 D 프로토콜 후보 선택 기록이 생성되지
  않았음을 명시한다.

Primary experiment에서는 evaluation descendant가 이미 존재하는 inference run에
`pre_evaluation` 판정을 기록할 수 없다. Pilot처럼 평가가 먼저 존재했던 과거 validation
run을 진단적으로 판정할 때는 그 사실을 provenance에 기록하며 paper-facing estimate에
사용하지 않는다.

## 3. 평가와 분석 경계

Benchmark evaluation은 model inference와 별도 campaign으로 실행한다. 모델 상주
campaign 도중 candidate를 평가하여 다음 phase의 진행 여부나 prompt를 바꾸지 않는다.
평가 결과, timeout, diagnostic, compiler/runtime 정보는 어떤 후속 model call에도
전달하지 않는다.

생성 조건은 Direct, `R`, `CR`, `CPR`뿐이다. 각 candidate condition의 평가 batch도
대상 model과 protocol에 속한 세 benchmark 전체를 한 실행 범위로 삼는다. Primary
evaluation의 모든 예정 candidate가 처리될 때까지 timeout은 잠정 상태로 모은 다음,
frozen timeout policy에 따라 timeout candidate만 별도 confirmation batch에서 한 번
재평가한다.

Benchmark 하나가 끝난 시점의 산출물은 진행 정보일 뿐 분석 dataset이 아니다. 대상
model/phase 또는 model/protocol의 세 benchmark가 모두 completeness gate를 통과한 뒤
한 번에 검증하고 분석한다. 부분 결과를 보고 prompt, decoding, task scope, phase 순서를
조정하지 않는다.

## 4. Background attempt와 진행 상태

Model-resident campaign과 전체 평가 batch는 장기 작업이므로 `AGENTS.md`의 durable
background attempt 규칙을 따른다. 한 campaign worker가 phase와 benchmark 경계를
연속해서 진행하며, 정상적인 중간 경계에서 별도 launcher나 사용자 handoff를 요구하지
않는다.

`status.json`에는 `AGENTS.md`의 공통 필드와 함께 최소한 다음 진행 정보를 둔다.

- `model_id`와 exact checkpoint revision
- `phase`
- 현재 `benchmark_id`
- phase 전체 `completed`, `failed`, `total`과 백분율
- benchmark별 `completed`, `failed`, `total`
- 마지막으로 완료된 task와 artifact timestamp

Count command는 기본적으로 현재 모델과 phase, 전체 `completed/1677`, 백분율, 실패 수를
한 줄로 보여주고 이어서 benchmark별 count를 간결하게 표시한다. 상세 오류는 count가
아니라 immutable record와 log에서 확인한다.

개별 task가 성공하거나 명시적 실패 상태에 도달할 때마다 raw response를 먼저 보존하고
record를 atomic하게 기록한다. 한 task의 실패가 사라지거나 전체 worker를 무조건
종료시키지 않게 하되, 공통 parser나 prompt 구성 결함처럼 downstream 전체를 오염시킬
수 있는 systemic failure는 해당 phase와 의존 phase를 중단한다.

## 5. Resume, retry, completeness

중단 후 재개할 때 schema, hash, provenance가 유효한 completed artifact는 재사용한다.
누락되었거나 재실행이 명시적으로 승인된 logical call만 새 attempt/record lineage로
실행한다. Host 재시작이나 process failure 때문에 모델을 다시 로드하는 것은 허용되지만,
이미 검증된 candidate, Decision, critique 또는 plan을 다시 생성하는 근거가 되지 않는다.

실패 attempt와 partial output은 보존하고 replacement attempt를 predecessor와 연결한다.
동일 canonical target에 concurrent writer를 두지 않는다. Resume preflight는 phase의
upstream artifact count와 hash를 먼저 검증하고, 의존 artifact가 불완전하면 downstream
phase를 시작하지 않는다.

Clean-worktree preflight는 실행 코드, configuration, dependency lock과 해당 job이 실제로
읽는 입력 경로에 적용한다. 실행과 무관한 untracked 연구 노트 때문에 사용자 파일을
이동·삭제하거나 임의로 commit하지 않는다. 반대로 `scripts/`, `src/`, `configs/` 또는
dependency lock의 tracked/untracked 변경은 반드시 launch를 차단한다.

Phase 완료는 process exit만으로 판단하지 않는다. 다음 조건이 모두 필요하다.

- frozen scope와 일치하는 1,677개 task가 success 또는 명시적 terminal failure record를 가짐
- 성공 record의 raw response, parsed artifact, token count, identifier와 hash가 검증됨
- benchmark별 count가 163, 378, 1,136과 정확히 일치함
- duplicate, conflicting, orphaned artifact가 없음
- shared initial, Decision, critique, plan의 reuse 관계가 검증됨

모델을 정상적으로 unload하기 전 전체 campaign manifest에 phase별 completeness를
기록한다. Model campaign이 완료되면 같은 절차로 다음 모델을 로드한다.

## 6. 구현 및 pilot 요구사항

Protocol runner는 task 하나를 Direct부터 CPR까지 끝내는 end-to-end loop가 아니라,
model-resident phase scheduler로 구현한다. Pilot은 작은 frozen task subset을 사용하지만
동일한 계층, phase 순서, artifact reuse, status/count, resume 동작을 검증해야 한다.

Primary 실행 전 integration test는 최소한 다음을 입증한다.

- 모델 load/unload 경계가 model campaign 바깥에 있음
- 각 phase가 pilot에 포함된 모든 benchmark task를 처리한 뒤 다음 phase로 이동함
- phase resume가 completed call을 중복 생성하지 않음
- Decision-conditioned outcome 생성 중 model call이 발생하지 않음
- benchmark evaluation data가 inference input에 포함되지 않음
