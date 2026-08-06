# 모델 및 벤치마크

## 1. 선정 원칙

본 연구는 locally deployable open-weight instruct models의 Python code-generation
self-refinement를 조사한다. 모델 선정은 frontier proprietary model과의 성능 경쟁이
아니라, 공통된 workstation-scale local inference budget에서 code-specialized panel의
protocol effects를 비교하고 general-purpose instruct control과의 차이를 관찰하는 데
목적이 있다.

모델은 다음 기준에 따라 선정한다.

- Publicly available open-weight checkpoint
- Code generation 또는 code instruction following을 주요 목적으로 하는 instruct model이거나, 사전에 지정한 general-purpose instruct control
- 외부 API 없이 local inference 가능
- 2개의 NVIDIA RTX 4090 GPU로 구성된 공통 실행 환경에서 배포 가능
- 서로 다른 model family와 architecture를 포함
- HumanEval+, MBPP+, BigCodeBench-Instruct에서 서로 다른 initial pass rates를 보일 가능성이 있는 규모와 세대
- 모든 protocol에서 동일 checkpoint와 inference configuration을 고정할 수 있음

모델 간 raw final pass rate를 refinement capability의 직접적인 순위로 해석하지 않는다.
각 모델은 서로 다른 initial candidates를 생성하므로 initial pass rate도 다를 수 있다.
Main comparison은 동일 모델과 benchmark 안에서 protocol을 변경했을 때의 paired difference다.

## 2. 평가 모델

| Display Name | Official Checkpoint | Architecture and Size | Planned Precision | Role in the Study |
|---|---|---|---|---|
| Qwen2.5-Coder-7B-Instruct | `Qwen/Qwen2.5-Coder-7B-Instruct` | Code-specialized dense, approximately 7.6B parameters | BF16 | 소형 code-specialized model |
| Qwen2.5-Coder-14B-Instruct | `Qwen/Qwen2.5-Coder-14B-Instruct` | Code-specialized dense, 14.7B parameters | BF16 | 동일 계열의 중간 규모 code-specialized model |
| DeepSeek-Coder-V2-Lite-Instruct | `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct` | Code-specialized MoE, 16B total and 2.4B active parameters | BF16 | Qwen 계열과 다른 효율적 MoE code model |
| Devstral-Small-2-24B-Instruct | `mistralai/Devstral-Small-2-24B-Instruct-2512` | SWE-specialized dense, 24B parameters | Official FP8 checkpoint | Mistral 계열의 code 및 software-engineering model |
| Qwen3-Coder-30B-A3B-Instruct | `Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8` | Code-specialized MoE, 30.5B total and 3.3B active parameters | Official FP8 checkpoint | 상대적으로 강한 code-specialized model |
| Gemma 4 31B Instruct QAT W4A16 | `google/gemma-4-31B-it-qat-w4a16-ct` | General-purpose dense, 31B parameters | Official QAT W4A16 compressed-tensors checkpoint | Code-specialized panel과 비교하는 general-purpose control |

Qwen2.5-Coder-7B-Instruct와 14B-Instruct는 같은 code-specialized family 안에서 규모가
다른 dense comparison을 제공하며 Apache 2.0 license로 공개되어 있다.[^qwen25-7b][^qwen25]
DeepSeek-Coder-V2-Lite-Instruct는 16B total parameters와 2.4B active parameters를 사용하는 MoE code model이며 128K context를 지원한다.[^deepseek]
Devstral-Small-2-24B-Instruct는 software-engineering agent use case를 중심으로 학습된
24B dense instruct model이며, 공식 repository의 FP8 checkpoint와 Apache 2.0 license를
사용한다.[^devstral]
Qwen3-Coder-30B-A3B-Instruct-FP8은 30.5B total parameters와 3.3B active parameters를 사용하며, official FP8 checkpoint와 non-thinking instruct mode를 제공한다.[^qwen3]
Gemma 4 31B Instruct는 code-specialized model이 아닌 general-purpose instruct comparison이며,
2 × RTX 4090 환경에 맞추어 Google이 vLLM/SGLang용으로 배포한 official QAT W4A16
compressed-tensors checkpoint를 사용한다.[^gemma4][^gemma4-qat]

StarCoder2-15B-Instruct는 세 차례 pilot에서 candidate fence와 categorical Decision에
대해 반복적인 instruction-compliance failure를 보였고, primary experiment 전에 패널에서
제외하였다. 기존 StarCoder2 pilot artifacts는 parser와 pilot history의 immutable validation
evidence로 보존하지만 primary estimate나 최종 six-model comparison에는 포함하지 않는다.

### 2.1 모델 표기 원칙

논문 본문과 표에서는 다음 display name을 일관되게 사용한다.

- Qwen2.5-Coder-7B
- Qwen2.5-Coder-14B
- DeepSeek-Coder-V2-Lite
- Devstral-Small-2-24B
- Qwen3-Coder-30B-A3B
- Gemma-4-31B-QAT-W4A16

Methodology의 model table에는 official checkpoint identifier, precision, license, serving configuration을 함께 제시한다.
`Qwen3-Coder-30B-A3B`와 `Devstral-Small-2-24B`를 본문에서 사용할 때 실제 실험
checkpoint가 FP8임을, `Gemma-4-31B-QAT-W4A16`에는 4-bit weights와 16-bit activation을
사용함을 model table과 reproducibility artifact에 명확히 기록한다.

### 2.2 공통 실행 환경

six-model panel이 유지할 공통 생성 contract는 다음과 같다. 기존 네 checkpoint에 사용한
`vllm-environment-2026-08-03-r1`과 vLLM 0.26.0이 신규 세 architecture 및 전체 six-model
sequential smoke를 모두 통과했으므로, 이 하나의 environment를 replacement pilot에
동결한다. 모델별 serving environment는 사용하지 않는다.

- 2 × NVIDIA RTX 4090
- 총 48GB nominal GPU memory
- 공통 vLLM 0.26.0, tensor parallel size 2, GPU memory utilization 0.85
- BF16 for both Qwen2.5-Coder sizes and DeepSeek-Coder-V2-Lite; official FP8 for Devstral and Qwen3-Coder; official QAT W4A16 for Gemma 4
- PyTorch-native sampler, `VLLM_BATCH_INVARIANT=1`, `temperature=0`, `n=1`, seed 0, penalty 없음
- 여섯 모델에 공통인 native context maximum 16,384 tokens
- checkpoint에 포함된 tokenizer와 chat template, automatic prompt truncation 금지
- 코드 candidate call 4,096, Critique와 Plan call 2,048, Decision call 64 output tokens

모델별 precision이 완전히 동일하지 않으므로 모델 간 raw score 차이를 precision-independent model ranking으로 해석하지 않는다.
각 모델 안에서는 모든 protocol이 동일 checkpoint와 precision을 사용하므로 model configuration을 고정한 상태에서 protocol을 비교할 수 있다.
Batch-invariant execution은 batch size, order, scheduling 변화에 따른 numerical output drift를 줄이고 task-level resume가 candidate를 바꾸지 않게 하기 위해 모든 모델과 stage에 공통 적용한다. 이 모드는 일부 kernel과 collective를 deterministic path로 바꾸므로 inference throughput과 KV-cache capacity에 미치는 영향을 serving validation에 함께 기록한다.
공통 context 16,384는 six-model panel의 가장 작은 validated native limit를 넘지 않도록
유지한다. 더 긴 context를 지원하는 checkpoint에도 model-specific RoPE 또는 tokenizer
extrapolation을 사용하지 않는다. 모든 rendered prompt는 model call 전에
`prompt tokens + stage output cap <= 16,384`를 검증하며, 초과 입력을 잘라내거나
stage별로 임의 축약하지 않는다. 신규 세 checkpoint 및 전체 panel의 exact tokenizer,
chat template, direct token-ID input, 16K allocation과 batch-invariant vLLM compatibility는
replacement pilot 전에 별도 smoke로 검증했으며, full-panel attempt는 6/6 exact repeated
response/token equality와 GPU cleanup을 통과했다.

## 3. 평가 벤치마크

본 연구는 Python code generation의 서로 다른 task family와 initial pass-rate range를 확보하기 위해 HumanEval+, MBPP+, BigCodeBench-Instruct를 사용한다.

| Benchmark | Tasks | Task Format | Role in the Study |
|---|---:|---|---|
| HumanEval+ | 164 release tasks; 163 included | Function signatures와 docstrings를 이용한 function-level code generation, EvalPlus augmented tests | 비교적 간결한 function-level specification에서 protocol effects 평가 |
| MBPP+ | 378 tasks | Natural-language programming problems와 examples를 이용한 function-level code generation, EvalPlus augmented tests | HumanEval+와 다른 specification style 및 task distribution 제공 |
| BigCodeBench-Instruct | 1,140 release tasks; 1,136 included | Natural-language instructions, diverse standard 및 third-party library calls, unittest-based evaluation | 더 다양한 library usage와 compositional requirements를 포함하는 task 제공 |

HumanEval+와 MBPP+는 EvalPlus의 강화된 test suites를 이용하여 functional correctness를 평가한다.[^evalplus]
현재 EvalPlus release는 HumanEval+ 164 tasks와 MBPP+ 378 tasks를 제공한다.[^evalplus-count]
본 연구는 model inference 전에 `HumanEval/32`를 제외하고 HumanEval+ 163 tasks를 사용한다.
고정된 공식 canonical solution이 EvalPlus 0.3.1의 `find_zero` special oracle 및
success-progress bookkeeping과 양립하지 않는 것이 독립 진단에서 확인되었기 때문이다.
Oracle, tolerance, canonical solution은 수정하지 않으며, 제외는 모든 model과 protocol에
동일하게 적용한다.
EvalPlus candidate process에는 전역 8 GiB memory 상한을 적용한다. 이는 pathological
allocation을 제한하면서 공식 MBPP+ 기준답안이 요구하는 대규모 정답 출력을 허용하는
pre-experiment resource policy이며, 모든 model과 protocol에 동일하게 적용한다.
Adapter `self-refinement-isolated-v4`는 EvalPlus 0.3.1의 benchmark tests와 oracle을
변경하지 않고, upstream evaluator가 일반 false detail로 합치는 입력별 timeout을 별도
계측한다. Timeout만으로 설명되는 미완료 판정은 `TIMEOUT`으로 confirmation에 보내며,
timeout과 별개인 failing detail이 확인되면 functional `FAIL`을 유지한다.
BigCodeBench는 Complete와 Instruct variant를 제공한다.[^bigcodebench]
본 연구는 natural-language-oriented instruction을 사용하는 BigCodeBench-Instruct release의 1,140 tasks를 출발점으로 하되, main experiment 전에 채택한 외부-content 재현성 규칙에 따라 `BigCodeBench/101`, `/590`, `/1005`, `/1012`를 제외하고 1,136 tasks를 사용한다.

### 3.1 Benchmark Evaluation Environments

실험 orchestration, local model inference, artifact storage, analysis, HumanEval+ 및 MBPP+ 평가는 고정된 Python 3.12 환경을 사용한다.
BigCodeBench-Instruct의 candidate execution은 공식 local evaluator가 사용하는 dependency range를 재현하기 위해 별도의 Python 3.10.12 환경에서 수행한다.
두 환경은 package state와 process namespace를 공유하지 않으며, BigCodeBench execution environment는 network가 차단된 sandbox 안에서만 candidate와 hidden tests를 실행한다.

Benchmark별 interpreter 차이는 protocol별로 달라지는 treatment가 아니다.
동일 task의 Direct, `R`, `CR`, `CPR` 및 Decision-Conditioned final candidate는 모두 동일한 benchmark-specific evaluator environment에서 평가한다.
환경 identifier, Python patch version, complete package lock, sandbox 및 timeout configuration을 모든 evaluation record와 run manifest에 연결한다.
Benchmark execution 결과와 diagnostic은 model prompt 또는 이후 refinement call에 전달하지 않는다.

세 benchmark 모두 10초를 default primary wall timeout으로 사용한다.
Main experiment 전에 official reference solution을 task별로 세 번 실행하여 end-to-end runtime을 수집하고, accepted reference의 최대 관측 시간이 10초를 넘은 task만 사전 override한다. 최대값 구간 `(10, 20]`, `(20, 40]`, `(40, 80]`, `(80, 160]`초에는 각각 30, 60, 120, 240초를 부여하며, 고정 목록은 HumanEval+ 0개, MBPP+ 1개, BigCodeBench-Instruct 15개다.
동일 task에는 model과 protocol에 관계없이 같은 primary 및 confirmation timeout을 적용한다.
전체 primary batch를 끝낸 뒤 잠정 timeout candidate만 한 번 재확인한다. 공통 confirmation은
120초와 primary limit의 1.5배 중 큰 값이며, EvalPlus 내부 실행 상한 때문에 사전 지정한
`HumanEval/38`, `/50`, `/53`은 180초다. 두 attempt가 모두 timeout일 때만 최종
`TIMEOUT`으로 분류한다.

### 3.2 전체 task 사용 원칙

Main experiment는 선택한 benchmark release에서 사전에 고정한 재현성 exclusion을 제외한 전체 task를 대상으로 한다.
Critique 또는 test representation이 단순한 task만 선택하는 subset sampling은 사용하지 않는다.

Task exclusion은 다음 조건에 한정한다.

- Official evaluator 또는 benchmark oracle의 재현 가능한 오류
- 실험 환경에서 모든 모델과 protocol에 공통으로 발생하는 평가 불가능 상태
- 외부 서비스 또는 비결정적 환경으로 인해 반복 가능한 evaluation이 불가능한 task

제외 규칙은 main experiment 전에 고정하고 모든 모델과 protocol에 동일하게 적용한다.
제외 task identifier와 사유를 공개한다.
단순히 task가 어렵거나 특정 모델이 실패한다는 이유로 제외하지 않는다.
BigCodeBench-Instruct에는 `DEC-20260803-09`에서 model inference 전에 고정한 네 개의 external-content exclusion을 적용하며, model 또는 protocol outcome에 따라 이 목록을 변경하지 않는다.

## 4. Model-Benchmark Combinations

여섯 모델과 세 benchmark는 총 18개의 **model-benchmark combinations**를 구성한다.

```text
6 models × 3 benchmarks = 18 model-benchmark combinations
```

각 combination에서 해당 모델이 모든 task의 initial candidate를 직접 생성한다.
동일 combination 안에서 Direct Generation, `R`, `CR`, `CPR`, Decision-Conditioned Refinement는 동일 initial candidate를 공유한다.

Model-benchmark combination은 benchmark difficulty를 나타내는 category가 아니다.
각 combination은 initial pass rate, repair, regression, token cost를 보고하는 분석 단위다.
HumanEval+, MBPP+, BigCodeBench-Instruct를 사전에 easy, medium, hard로 명명하지 않는다.
Task difficulty와 refinement 결과는 initial pass rate, repair rate, regression rate를 이용해 설명한다.

## 5. Initial Candidate Strategy

각 모델은 자신의 initial candidate를 생성하고 동일 모델이 해당 candidate를 refine한다.
이 전략은 동일한 모델이 자신의 candidate를 수정한다는 연구 범위를 유지한다.

모든 protocol에서 동일 candidate를 사용해야 하므로 initial generation은 protocol별로 반복하지 않는다.
각 model-task pair에 대해 initial candidate를 한 번 생성하고 candidate identifier와 source hash를 부여한다.
모든 Decision, Critique, Plan, Revision artifact는 이 identifier에 연결한다.

모델 간 candidate pool은 공통화하지 않는다.
다른 모델이 생성한 candidate를 공통 입력으로 사용하면 동일한 모델이 자신의 candidate를 수정하는 본 연구의 범위를 벗어난다.
따라서 모델 간 raw final pass rate보다 각 모델 안의 protocol comparison과 model-benchmark combination별 결과에 중점을 둔다.

## 6. Benchmark Tests의 사용

Benchmark tests와 그 실행 결과는 모델에 제공하지 않는다.
이들은 다음 용도로만 사용한다.

- Initial candidate correctness 판정
- Final candidate correctness 판정
- Repair 및 regression transition 계산
- Benchmark-level pass rate 계산

Test execution과 model inference는 분리된 process로 운영한다.
Model prompt에는 public examples로 원래 task specification에 포함된 내용 외의 test information을 추가하지 않는다.

## 7. Source Links

[^qwen25-7b]: [Qwen/Qwen2.5-Coder-7B-Instruct official model card](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct)
[^qwen25]: [Qwen/Qwen2.5-Coder-14B-Instruct official model card](https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct)
[^deepseek]: [deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct official model card](https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct)
[^devstral]: [mistralai/Devstral-Small-2-24B-Instruct-2512 official model card](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512)
[^qwen3]: [Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8 official model card](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8)
[^gemma4]: [Google Gemma 4 model overview](https://ai.google.dev/gemma/docs/core)
[^gemma4-qat]: [Google Gemma 4 official QAT collection](https://huggingface.co/collections/google/gemma-4-qat-q4-0)
[^evalplus]: [EvalPlus official repository](https://github.com/evalplus/evalplus)
[^evalplus-count]: [EvalPlus release notes documenting the 378-task MBPP+ release](https://github.com/evalplus/evalplus/releases)
[^bigcodebench]: [BigCodeBench official dataset card](https://huggingface.co/datasets/bigcode/bigcodebench)
