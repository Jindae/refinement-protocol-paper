# Known Issues

## ISSUE-20260804-07: Devstral chat template was rendered and retokenized unsafely

- First observed: 2026-08-04
- Status: Resolved
- Severity: Major
- Description: Completed compatibility attempt `vllm-smoke-new-models-20260804-r1` called the vLLM tokenizer with `apply_chat_template(tokenize=False)` and then encoded the rendered string. vLLM's `MistralCommonBackend` explicitly warns that this path is unsafe. The exact Devstral prompt produced 88 stored IDs through that path but 81 IDs through canonical `apply_chat_template(tokenize=True)`, with nonmatching sequences. Qwen2.5 and Gemma produced exact matches through both paths.
- Affected tasks/models/benchmarks/runs: Validation-only Devstral result in `vllm-smoke-new-models-20260804-r1`; the shared `VllmResidentBackend` implementation before correction. No benchmark task, six-model pilot, primary candidate, evaluator result, or paper-facing result exists under the affected implementation.
- Impact on results: The attempt proves that all three architectures load and that the observed outputs are deterministic under the bytes actually supplied, but it cannot certify correct common prompt tokenization for Devstral or freeze the six-model serving path. Its prior independent validator checked stored token consistency but not the token-input construction mode, so that validation claim is superseded.
- Evidence: Terminal attempt status is 3/3 completed with exit code 0 and summary SHA-256 `8c5304f21aa4fcb4e0851caaf8e2eb9d1530b8e26997b7b893eefb60f9ea24e9`. Offline comparison using vLLM's actual tokenizer registry reports Devstral `MistralTokenizer` canonical/stored counts 81/88 and unequal IDs, while Qwen2.5 and Gemma both match exactly at 103 and 87 IDs. The raw log preserves the `apply_chat_template(..., tokenize=False) is unsafe` warning.
- Temporary action: Invalidate `r1` as common serving certification, preserve all status/log/result artifacts unchanged, and keep pilot/primary execution blocked.
- Resolution or mitigation: The common backend and smoke worker now call `apply_chat_template(tokenize=True)` and pass the exact resulting `prompt_token_ids` directly to vLLM generation. Result validation requires `prompt_input_mode=chat-template-token-ids`; unit coverage verifies the direct token request and rejects the old result shape. Replacement `vllm-smoke-new-models-20260804-r2` completed and independently validated all three models. Devstral records the canonical 81 IDs, no unsafe-template warning appears, and Qwen2.5/Gemma record 103/87 IDs respectively.
- Required reruns or regenerated artifacts: Complete. Replacement `r2` is the accepted three-model compatibility evidence. No model candidate or evaluation artifact required regeneration.
- Related decision: `DEC-20260804-28` (Adopted).

## ISSUE-20260804-06: StarCoder2 does not emit the categorical Decision value

- First observed: 2026-08-04
- Status: Resolved
- Severity: Major
- Description: In complete draft3 pilot `run_856e8d87f7ed9bec7dec9a5c`, all nine StarCoder2 Decision calls generated task analysis until the 64-token cap instead of returning exact `PRESERVE` or `REFINE`. The strict parser correctly stored nine `invalid_response` records. A separate StarCoder2 plan repeated text to its 2,048-token cap but remained a non-empty stored plan artifact.
- Affected tasks/models/benchmarks/runs: StarCoder2 on all nine pilot tasks for Decision and one HumanEval+ task for Revision Planning; inference `run_856e8d87f7ed9bec7dec9a5c`, evaluation `run_5b4f4a5a93f86c60a7efe19c`, and review `pilot-review-draft3-20260804T000600Z`.
- Impact on results: All 144 always-refine candidates are present and evaluated, but 27 StarCoder2 `DR`/`DCR`/`DCPR` outcomes cannot be derived. The draft3 automated pilot gate remains `review_required`; none of these validation-only artifacts enter primary estimates.
- Evidence: Inference validation passed 252 raw/model-call records. Status counts are 243 completed and nine invalid responses; finish reasons are 242 stop and ten length. Every invalid response is a StarCoder2 Decision ending at 64 tokens. The plan-length response is repetitive but parse-complete. Review report SHA-256 is `af70a292b1c0112f2e555605e3ab6e149f1cf64335a27f9829ab226333d21e90`.
- Temporary action: Preserve all artifacts unchanged and keep primary gated during model-panel replacement.
- Resolution or mitigation: Adopted `DEC-20260804-28` removes StarCoder2 from future pilot and primary scope rather than changing Decision generation for one systematically noncompliant model. Proposed `DEC-20260804-27` is superseded; no existing response is retried, reparsed, or imputed.
- Required reruns or regenerated artifacts: Run a new complete six-model compatibility validation and replacement pilot after the three new exact checkpoints are downloaded and configured. Existing draft3 artifacts remain immutable historical evidence.
- Related decision: `DEC-20260803-16`, `DEC-20260803-20`, `DEC-20260804-26`, superseded `DEC-20260804-27`, and adopted `DEC-20260804-28`.

## ISSUE-20260804-05: Replacement pilot retains two forms of model format noncompliance

- First observed: 2026-08-04
- Status: Resolved
- Severity: Major
- Description: Replacement pilot draft2 did not change StarCoder2's systematic outside-fence introduction: all nine Direct responses still contained exactly one complete Python fence preceded by explanatory prose. One Qwen2.5 revision-plan response also included a fenced code example despite the plain-text-only plan contract. All calls ended normally with `finish_reason=stop`; raw storage and typed parser classification are correct.
- Affected tasks/models/benchmarks/runs: StarCoder2 Direct on all nine tasks and Qwen2.5 revision planning on one HumanEval+ pilot task in inference `run_143681f34a6855eb1902bd4b`; downstream artifact counts and review `pilot-review-r2-20260803T225500Z`.
- Impact on results: The current strict gate cannot freeze the primary prompt. StarCoder2 has no candidates, and the one invalid plan prevents its dependent CPR candidate. No primary data exist and no malformed response was evaluated as code.
- Evidence: Independently validated inference has 197 call records: 187 completed, nine `extraction_failure`, and one `invalid_response`; all 197 returned calls have `finish_reason=stop`. Review report SHA-256 is `be44bee2b0ca7c65dfbf0f30b98987167d59e0f53872ffcf65f0683ebe0be205`.
- Temporary action: Keep primary execution gated. Preserve both prior pilot versions and do not reparse or repair their artifacts.
- Resolution or mitigation: Adopted `DEC-20260804-26` defines one common exact-single-Python-fence extractor and accepts non-empty mixed-text critique/plan artifacts while prohibiting complete revised solutions in their prompts. Draft3 implementation and context validation pass.
- Required reruns or regenerated artifacts: Complete. Draft3 inference produced all 144 candidates with zero candidate/critique/plan parse failures, and evaluation validated all 144 resolutions. The distinct categorical Decision issue is tracked separately as `ISSUE-20260804-06`.
- Related decision: `DEC-20260803-20`, `DEC-20260804-23`, and `DEC-20260804-26` (Adopted).

## ISSUE-20260804-04: Default 15-second confirmation preempts determinate slow evaluation

- First observed: 2026-08-04
- Status: Resolved
- Severity: Major
- Description: Replacement-pilot timeout policy `r1` confirmed default-task primary timeouts at only 15 seconds. Longer immutable diagnostics showed two exact `HumanEval/129` sources terminate deterministically as functional `FAIL` at approximately 16.7 and 26.5 seconds, so the narrow confirmation interval preserved avoidable final timeout outcomes. Two other sources reached pinned EvalPlus internal timeout at approximately 65.5 seconds; none passed.
- Affected tasks/models/benchmarks/runs: Ten final timeout resolutions on `HumanEval/129` in evaluation run `run_2a7f94f41cc4951f78892906`, represented by four unique sources from DeepSeek-Coder-V2-Lite, Qwen2.5-Coder, and Qwen3-Coder conditions. The 60- and 120-second diagnostic attempts are `timeout-diagnostic-20260803T212750Z` and `timeout-diagnostic-20260803T213335Z-120sec`.
- Impact on results: The `r1` evaluation is internally valid for its frozen policy but is not suitable for the final pilot freeze because its confirmation limit can hide a determinate functional outcome. It does not affect inference candidates or any model prompt. No primary experiment has started.
- Evidence: The 60-second report SHA-256 is `c438505d64e382065c43a69fd3b097c7ef350714d4b9bf1d3b1f89a9bc399c5b`; the independently validated 120-second report SHA-256 is `8be8e28ac9c53d90eddef1afd677fe5324ed701f3e00c85e9ea21f15900992b4`. Exact `r1` policy bytes are preserved with SHA-256 `8dbcb6b1697d14e23e6862ee473d27e256c79c3abea9450e3671a11e4815991a`.
- Temporary action: Preserve the completed `r1` evaluation and diagnostics without reclassification. Do not freeze the pilot review or start primary evaluation from those outcomes.
- Resolution or mitigation: `DEC-20260804-25` adopts policy `r2`: common 10-second primary, common `max(120 seconds, 1.5 × primary)` confirmation, and predeclared 180-second confirmation for the three HumanEval+ tasks with a 126-second EvalPlus internal bound.
- Required reruns or regenerated artifacts: Complete. Evaluation `run_6b1f457a1462deac2ffabf52` passed independent validation with 107/107 resolutions and 117/117 raw evaluator artifacts.
- Related decision: `DEC-20260803-15`, `DEC-20260804-24`, and `DEC-20260804-25` (Adopted).

## ISSUE-20260804-03: Campaign preflight hard-coded the draft1 prompt path

- First observed: 2026-08-04
- Status: Resolved
- Severity: Minor
- Description: The first clean-worktree preflight request for replacement campaign `pilot-campaign-2026-08-04-r2` rejected its versioned, hash-valid draft2 prompt manifest because the launcher required every campaign to reference the original `configs/prompts/primary.toml` path.
- Affected tasks/models/benchmarks/runs: Replacement-pilot preflight only. The check stopped before model loading, attempt creation, registry creation, or generation; no experimental artifact was affected.
- Impact on results: None. The restriction prevented the adopted versioned pilot prompt from reaching its own configured validation path but did not alter or accept any prompt.
- Evidence: Preflight reported `campaign does not reference active primary configurations` while listing the correct frozen inference/model paths and `configs/prompts/primary_draft2.toml`. Independent manifest/hash/input and four-tokenizer context validation had already passed.
- Temporary action: Do not start the replacement pilot until launcher correction, regression tests, full validation, commit, and a clean-worktree preflight pass.
- Resolution or mitigation: Preflight continues to require the one active primary inference configuration and exact model manifest, while loading and hash-validating the prompt manifest explicitly selected by the versioned campaign. Regression tests verify draft2 acceptance and rejection of a non-primary inference path; all 125 tests pass.
- Required reruns or regenerated artifacts: Complete. Host-level clean-worktree preflight passed for `pilot-campaign-2026-08-04-r2`; no attempt or experiment rerun was required because none had started.
- Related decision: `DEC-20260804-23` (Adopted).

## ISSUE-20260804-02: StarCoder2 adds prose outside every pilot code fence

- First observed: 2026-08-04
- Status: Open
- Severity: Major
- Description: In the first cross-model pilot, all nine StarCoder2 Direct responses contained a complete `python` fence but prefixed it with explanatory prose such as “Here's how you can implement this”. The adopted strict common parser therefore recorded nine `extraction_failure` calls and correctly blocked every dependent phase for those model-task pairs.
- Affected tasks/models/benchmarks/runs: StarCoder2-15B-Instruct on all nine tasks in inference run `run_2ee6e3449b478af4e56a509f` / attempt `campaign-pilot-20260803T145409Z`. The other three models completed all seven phases.
- Impact on results: The pilot cannot freeze the draft prompt for primary use. StarCoder2 has no pilot candidate or evaluation outcome, and the missing artifacts must not be imputed or recovered by silently loosening the parser.
- Evidence: All nine calls ended with backend finish reason `stop`, immutable raw responses, and the identical typed error `code response must be exactly one complete fenced Python block`. Manual inspection confirms outside prose in every response; this is systematic model instruction noncompliance rather than truncation, backend failure, or ambiguous extraction.
- Temporary action: Keep primary execution gated and preserve the first pilot and raw responses unchanged.
- Resolution or mitigation: `DEC-20260804-23` adopts common draft2 prompts that put the mandatory whole-response fence contract first and explicitly forbid introductions, labels, explanations, and trailing text. The strict common parser is unchanged; no old output is salvaged. Replacement configuration `pilot-campaign-2026-08-04-r2` is prepared for all four models.
- Required reruns or regenerated artifacts: Replacement pilot completed and confirmed that draft2 did not resolve the StarCoder2 behavior. The issue remains open and is now jointly tracked with the isolated Qwen2.5 plan violation in `ISSUE-20260804-05`; another run requires the decision proposed in `DEC-20260804-26`.
- Related decision: `DEC-20260803-20`, `DEC-20260803-22`, and `DEC-20260804-23` (Adopted).

## ISSUE-20260804-01: Pilot review rejected valid confirmed final timeouts

- First observed: 2026-08-04
- Status: Resolved
- Severity: Minor
- Description: `scripts/review_pilot.py` raised `RuntimeError: final pilot resolution cannot remain a timeout` when the evaluated pilot contained five candidates that timed out in both the frozen primary and confirmation attempts.
- Affected tasks/models/benchmarks/runs: Review tooling for evaluation run `run_408b9ad39cdae36bacca33ae`; the five candidates are all on `HumanEval/129`. No inference, evaluation attempt, resolution, or raw artifact was modified.
- Impact on results: None. The review report was not written, but the evaluation campaign had already completed and independently validated all 108 resolutions and 113 raw attempts.
- Evidence: Every final timeout links a 10-second primary timeout to exactly one 15-second confirmation timeout, uses `source_attempt=confirmation`, and retains matching candidate identity and hashes. This is precisely the terminal state allowed by `DEC-20260803-15`, `documents/04_experiment_plan.md`, and schema `3.0.0`. Corrected report `pilot-review-20260804-r2` has SHA-256 `36b009f7dbe3d5b9d8e11feb09650d2fe727776af1c516aa185ca72f44533d44`.
- Temporary action: Preserve the requested failed review invocation and use a new report identifier after correcting and validating the tool.
- Resolution or mitigation: The review gate now reports confirmed timeouts with benchmark, task, model, protocol, candidate path, and both attempt IDs. Confirmed final timeout and functional `FAIL` do not independently block the automated gate; unconfirmed primary timeout remains impossible in a validated resolution set.
- Required reruns or regenerated artifacts: Complete. Corrected report `pilot-review-20260804-r2` was generated; inference and evaluation were not rerun.
- Related decision: `DEC-20260803-15` (Adopted).

## ISSUE-20260803-10: Terminal smoke status dropped launch provenance fields

- First observed: 2026-08-03
- Status: Resolved
- Severity: Minor
- Description: The first independent validation of completed batch-invariance probe `vllm-batch-invariance-probe-20260803-r1` rejected terminal `status.json` because the runner reconstructed status at every transition and omitted the launch-time configuration hash in its completed update. Captured `configuration.json` and `summary.json` both retained and matched the committed hash.
- Affected tasks/models/benchmarks/runs: Post-run validation of the StarCoder2 validation-only probe. No model experiment candidate, benchmark task, evaluator result, or generated response was altered.
- Impact on results: None. Exact raw responses, token IDs, result, configuration, summary, terminal exit metadata, and log were complete and immutable. The first validator invocation failed only because it demanded redundant provenance in terminal status.
- Evidence: Terminal status is completed with exit code 0 and 1/1 models. Captured and summary configuration SHA-256 both equal `1132b60ad5eb8a2da4fd64c31c2eae8710760aa2c9eb9c46d0d29f1f10178a1c`; the status field is absent rather than conflicting. After the contract correction, independent validation passed with result SHA-256 `edf297862268f3900e84c1681b2da201c961bf103b14ef1e5add3e94f3599c17` and summary SHA-256 `dc404cbd64dee23771f3ad75b08bd57a45cb21c2daefc0072a5a7144f253a280`.
- Temporary action: Preserve the completed probe unchanged; do not edit its terminal status to add the missing redundant field.
- Resolution or mitigation: Future running, completed, and failed smoke status transitions now retain configuration and model-manifest paths and SHA-256 values. The validator accepts a missing legacy terminal status hash only when captured configuration and summary independently match, while rejecting any present conflicting hash. Regression tests cover the legacy case.
- Required reruns or regenerated artifacts: None. The probe itself is valid; future primary smoke attempts use the corrected status writer.
- Related decision: `DEC-20260803-18` (Adopted).

## ISSUE-20260803-09: Primary batched greedy outputs are not batch invariant

- First observed: 2026-08-03
- Status: Resolved
- Severity: Major
- Description: Primary smoke `vllm-primary-smoke-20260803-r2` loaded StarCoder2 successfully with the frozen TP=2, BF16, PyTorch-native sampler, 16,384 context, and 4,096 output-token cap, but two identical prompts submitted together produced different response/token sequences despite temperature 0 and seed 0. vLLM 0.26.0 does not enable batch-invariant execution by default. Its official reproducibility guidance states that offline V1 requires deterministic scheduling or batch invariance, and its batch-invariance mode changes kernels/collectives with a performance tradeoff. The runner also checked equality before writing the result, so the two raw responses were not persisted in this attempt.
- Affected tasks/models/benchmarks/runs: Validation-only `vllm-primary-smoke-20260803-r2`, first model `starcoder2-15b-instruct`. No benchmark task, pilot candidate, primary candidate, evaluator result, or paper-facing result exists.
- Impact on results: The frozen 16K allocation fits StarCoder2, but the current configuration has not demonstrated repeatable outputs under batched inference. Proceeding unchanged could make a candidate depend on batch composition or scheduling, especially after resume. Enabling a deterministic mode can change generated candidates and throughput, so it must be selected before pilot inference rather than silently patched.
- Evidence: The immutable log records successful model loading, 4.51 GiB KV cache per GPU, 118,140 KV-cache tokens, maximum 7.21 concurrency at 16,384 tokens, completed compile/warmup, and then `RuntimeError: repeated greedy outputs are not identical`. Terminal status records exit code 1 and 0/4 completed models. Host cleanup inspection found both GPUs at 15 MiB and 0% utilization with no compute process. Local vLLM 0.26.0 contains `VLLM_BATCH_INVARIANT` and `VLLM_ENABLE_V1_MULTIPROCESSING`; neither was enabled in `r2`.
- Temporary action: Preserve `r2` and do not reinterpret it as a model, memory, or context-length failure. The worker atomically stores unequal raw responses and token IDs before failing. Focused probe `vllm-batch-invariance-probe-20260803-r1` passed exact equality and adequate 16K capacity.
- Resolution or mitigation: `DEC-20260803-18` validated batch invariance on StarCoder2, and `DEC-20260803-19` adopted it in primary configuration `r2`. The observed one-time compile overhead and roughly 5% StarCoder2 KV-capacity reduction are acceptable for model-resident campaigns. Replacement `vllm-primary-smoke-20260803-r3` subsequently passed and independently validated exact repeated output/token equality for all four models.
- Required reruns or regenerated artifacts: Complete. Never reuse `r2`; use validated `r3` as the primary runtime evidence. No pilot or primary candidate requires regeneration because none existed.
- Related decision: `DEC-20260803-16` (Adopted settings require refinement before pilot).

## ISSUE-20260803-08: Primary smoke child could not import the project package

- First observed: 2026-08-03
- Status: Resolved
- Severity: Minor
- Description: Primary configuration attempt `vllm-primary-smoke-20260803-r1` launched correctly, but the first child process executed the smoke script with `.venv-vllm/bin/python` and failed immediately on `ModuleNotFoundError: self_refinement`. Extending the runner to import the new primary configuration at module load introduced a project-package dependency; the main editable environment and repository tests masked that the isolated vLLM environment does not install the orchestration package.
- Affected tasks/models/benchmarks/runs: Validation-only `vllm-primary-smoke-20260803-r1` before StarCoder2 weight loading. No benchmark task, model candidate, prompt artifact, evaluator outcome, pilot, or primary experiment was involved.
- Impact on results: None. The attempt produced zero of four model result records and no summary. It provides no evidence about 16K GPU fit or checkpoint behavior.
- Evidence: Immutable `smoke.log` contains only the child `ModuleNotFoundError` and the parent `CalledProcessError`; terminal status records exit code 1 and zero completed models. Post-failure inspection found both GPUs at 15 MiB and zero utilization with no compute process.
- Temporary action: Preserve `r1` unchanged and do not retry its directory or identifier.
- Resolution or mitigation: Anchor the repository `src/` directory on `sys.path` before project imports in the direct script, and add a regression test that executes the exact smoke `--help` entrypoint with `.venv-vllm/bin/python`, not only the main `.venv`. Strengthen `AGENTS.md` so direct entrypoints are tested under every actual launcher/worker interpreter.
- Required reruns or regenerated artifacts: Completed for the import defect. Replacement `r2` reached StarCoder2 loading and generation, then failed for the independent batch-variance issue tracked as `ISSUE-20260803-09`.
- Related decision: `DEC-20260803-16` (Adopted).

## ISSUE-20260803-07: Host CUDA 11.8 cannot compile the default FlashInfer sampler

- First observed: 2026-08-03
- Status: Resolved
- Severity: Minor
- Description: Compatibility batch `vllm-smoke-20260803-r2` reached StarCoder2 engine warmup but vLLM's default FlashInfer 0.6.14 sampler attempted a JIT build using `/usr/local/cuda`, which points to CUDA toolkit 11.8. FlashInfer's bundled CCCL requires CUDA 12 or newer, whereas the installed binary PyTorch/vLLM stack uses CUDA 13.0 runtime libraries.
- Affected tasks/models/benchmarks/runs: Validation-only attempt `vllm-smoke-20260803-r2`, during the first model `starcoder2-15b-instruct`. No benchmark task, candidate, evaluator outcome, pilot, or primary experiment was involved.
- Impact on results: None. The attempt produced zero of four result records and no summary. It confirms several earlier initialization stages but is not model compatibility certification.
- Evidence: The immutable log records successful bfloat16 weight loading, two-rank tensor parallel setup, FlashAttention 2, torch compilation, and CUDA graph capture, followed by `#error CUDA versions below 12 are not supported` from `/usr/local/cuda/bin/nvcc`. Host inspection identifies CUDA 11.8.89; PyTorch reports `2.11.0+cu130` and `torch.version.cuda=13.0`. The vLLM opt-out probe logs selection of `VLLM_USE_FLASHINFER_SAMPLER=0` and returns `flashinfer_sampler_supported False`.
- Temporary action: Preserve `r2` unchanged and do not interpret the JIT failure as a checkpoint failure.
- Resolution or mitigation: `DEC-20260803-14` selects vLLM's explicit PyTorch-native sampling fallback for compatibility smoke `r3`. Configuration and result records carry the backend choice. No unsupported compiler guard is suppressed and no host toolkit is modified.
- Required reruns or regenerated artifacts: Compatibility validation is complete in `vllm-smoke-20260803-r3`. `DEC-20260803-16` freezes the same PyTorch-native backend for primary inference, whose separate 16K configuration validation is tracked independently.
- Related decision: `DEC-20260803-14` and `DEC-20260803-16` (Adopted).

## ISSUE-20260803-06: vLLM smoke worker omitted the environment executable path

- First observed: 2026-08-03
- Status: Resolved
- Severity: Minor
- Description: Compatibility batch `vllm-smoke-20260803-r1` loaded the first StarCoder2 checkpoint but failed during FlashInfer sampling-kernel preparation because the batch worker invoked the isolated Python without prepending `.venv-vllm/bin` to the child `PATH`. The installed `ninja` Python package and executable were therefore unavailable to vLLM's subprocess lookup.
- Affected tasks/models/benchmarks/runs: Validation-only attempt `vllm-smoke-20260803-r1`, during the first model `starcoder2-15b-instruct`. No benchmark task, model candidate, evaluator outcome, pilot, or primary experiment was involved.
- Impact on results: None. The attempt produced zero of four per-model result records and no summary; it is an infrastructure failure, not evidence of model incompatibility. The checkpoint loaded successfully before kernel initialization failed.
- Evidence: The immutable log ends with `FileNotFoundError: [Errno 2] No such file or directory: 'ninja'` from both tensor-parallel workers. `.venv-vllm/bin/ninja --version` succeeds with `1.13.0.git.kitware.jobserver-pipe-1`. Terminal status records exit code 1. Post-failure GPU inspection found no remaining compute process or material allocation.
- Temporary action: Preserve `vllm-smoke-20260803-r1` unchanged and do not classify the first checkpoint as failed compatibility validation.
- Resolution or mitigation: The runner now constructs an explicit child environment with `.venv-vllm/bin` first on `PATH`, validates that lookup resolves to the pinned environment executable before attempt creation and worker execution, and preserves batch scope/current-model fields in future terminal failures. Regression tests cover executable-path propagation and failed count formatting. Replacement `r2` found and ran that exact `ninja`, resolving the path defect; its later CUDA 11.8 compiler incompatibility is separately tracked as `ISSUE-20260803-07`.
- Required reruns or regenerated artifacts: Complete. Path-specific validation succeeded in `r2`, and replacement `r3` subsequently passed all four model smokes after separately mitigating `ISSUE-20260803-07`.
- Related decision: `DEC-20260803-13` (Adopted).

## ISSUE-20260803-05: Reference audit validator assumed BigCodeBench task namespace

- First observed: 2026-08-03
- Status: Resolved
- Severity: Minor
- Description: The first independent validation of completed HumanEval+ replacement audit `timing-humaneval-20260803-r2-v3` rejected its otherwise complete artifacts because the manifest-included scope validator constructed every expected identifier with the `BigCodeBench/` namespace.
- Affected tasks/models/benchmarks/runs: Post-run validation of `timing-humaneval-20260803-r2-v3` only. No observation, raw evaluator output, benchmark execution, model, or experiment result was changed.
- Impact on results: None. The audit retained 489/489 immutable observations and raw outputs with zero anomalies; completion was withheld until the validator was corrected and rerun.
- Evidence: Initial validation raised `observed tasks do not match the configured inclusion policy`. The immutable configuration correctly records `benchmark_id=humaneval_plus`, 164 release tasks, exclusion `HumanEval/32`, and 163 expected tasks.
- Temporary action: Preserve the completed attempt unchanged and do not start the MBPP+ replacement audit until independent validation passes.
- Resolution or mitigation: The validator now selects `HumanEval/` or `BigCodeBench/` from the configured benchmark identifier. Regression tests cover accepted HumanEval manifest scope and rejection of the wrong namespace. Independent validation then passed all 163 tasks, three repetitions, 489 observations, 489 raw outputs, and stored/recomputed hashes.
- Required reruns or regenerated artifacts: None. The validator defect did not affect collection or stored artifacts.
- Related decision: `DEC-20260803-12` (Adopted).

## ISSUE-20260803-04: Model hash launcher direct invocation could not import scripts

- First observed: 2026-08-03
- Status: Resolved
- Severity: Minor
- Description: The first requested start of `model-hash-20260803-r1` stopped before attempt creation because the background launcher's documented direct-script invocation could not import `scripts.validate_model_download`. Repository tests supplied the project root through `PYTHONPATH`, masking the entrypoint-specific import defect.
- Affected tasks/models/benchmarks/runs: Full duplicate hash validation launcher only. No attempt directory, worker, hash read, model file, benchmark, model call, or experiment run was created or affected.
- Impact on results: None. The failure occurred before status or output creation and no validation result was claimed.
- Evidence: `.venv/bin/python scripts/run_model_hash_validation.py --start --attempt-id model-hash-20260803-r1` raised `ModuleNotFoundError: No module named 'scripts'`; read-only inspection confirmed `runs/logs/model-hash-validation/model-hash-20260803-r1/` did not exist.
- Temporary action: Do not reuse the failed requested identifier; prepare retry `model-hash-20260803-r2` only after the launcher fix, direct entrypoint smoke check, complete repository validation, and commit.
- Resolution or mitigation: The launcher now anchors the project root before importing its sibling module. A subprocess regression test executes the exact documented direct-script `--help` entrypoint, and `AGENTS.md` now requires smoke-testing documented entrypoint commands before long-job launch. Full repository validation passes 48 tests. Replacement attempt `model-hash-20260803-r2` completed 63/63 full hashes with report SHA-256 `7b8f5bb5a1d5ada552bfb523c601fe430e28958266ccf26a35722fdf7a894f65`.
- Required reruns or regenerated artifacts: Complete. Requested identifier `r1` has no artifact; successful replacement `r2` is the retained validation evidence.
- Related decision: `DEC-20260802-04` and `DEC-20260802-06` (Adopted).

## ISSUE-20260803-03: Mbpp/255 official reference exceeds the 4 GiB EvalPlus guard

- First observed: 2026-08-03
- Status: Resolved
- Severity: Major
- Description: Complete MBPP+ timing audit `timing-mbpp-20260803-r1` produced a functional `FAIL` for the pinned official reference of `Mbpp/255` in all three repetitions. Focused diagnosis identifies plus input index 85 as the only failing input under the configured 4 GiB guard.
- Affected tasks/models/benchmarks/runs: MBPP+ task `Mbpp/255` and audit `timing-mbpp-20260803-r1`. No model candidate, pilot, or experiment run is affected.
- Impact on results: The run's artifact integrity is valid, but its 1,131 passing and three anomalous observations cannot yet form an accepted complete-release timeout-calibration dataset. Treating the official-reference anomaly as a generated-candidate `FAIL` or silently excluding the task would be invalid.
- Evidence: The audit contains all 378 tasks, 1,134 schema-valid observations, and 1,134 raw outputs. Independent validation passed with observation-index SHA-256 `1e1c72a88fa3028e76fd6e8dfaecaea155e647dbe6248e844ee124449e055a61` and summary SHA-256 `3a384c914713b67c6f616b75c438ab00938fb75e665cb5a0596eef8b06c30585`. Official-path detail isolates plus index 85, input `[['Dog', 'Cat', 'CatBird', 'Bird', 'Fish'], 77]`, which creates 1,663,740 tuples; all plus inputs retain 2,015,941 expected tuples. Reproduction under 4 GiB raises `MemoryError`. Confirmation report SHA-256 `8ba8b7cc7ddaac73cf1706ab8530986ffc277338337fa3f2c58d23754a40db58` records 3/3 isolated passes under the adopted global 8 GiB adapter `v3` policy.
- Temporary action: Preserve the complete audit unchanged and do not use it to freeze MBPP+ timeouts. Any additional failure detail remains evaluator-only and must never enter model prompts.
- Resolution or mitigation: `DEC-20260803-11` adopts a global 8 GiB limit in manifest `evalplus-benchmarks-2026-08-03-r4` and adapter `self-refinement-isolated-v3`. Targeted confirmation passed 3/3, and replacement audit `timing-mbpp-20260803-r2-v3` subsequently passed all 1,134/1,134 observations with zero anomalies; `Mbpp/255` passed all three repetitions.
- Required reruns or regenerated artifacts: Complete. No further MBPP+ reference rerun is required unless the evaluator environment changes.
- Related decision: `DEC-20260802-07` and `DEC-20260803-11` (Adopted).

## ISSUE-20260803-02: HumanEval/32 canonical solution conflicts with its special oracle

- First observed: 2026-08-03
- Status: Resolved
- Severity: Major
- Description: Complete HumanEval+ timing audit `timing-humaneval-20260803-r1` produced a functional `FAIL` for the pinned official reference of `HumanEval/32` in all three repetitions. Diagnosis found two upstream EvalPlus 0.3.1 behaviors: its `find_zero` branch continues before recording successful detail/progress, and seven plus inputs make the official canonical Newton iteration exceed the oracle residual tolerance.
- Affected tasks/models/benchmarks/runs: HumanEval+ task `HumanEval/32` and audit `timing-humaneval-20260803-r1`. No model candidate, pilot, or experiment run is affected.
- Impact on results: The run's artifact integrity is valid, but its 489 passing and three anomalous observations cannot yet form an accepted complete-release timeout-calibration dataset. Treating the official-reference anomaly as a generated-candidate `FAIL` or silently excluding the task would be invalid.
- Evidence: The audit contains all 164 tasks, 492 schema-valid observations, and 492 raw outputs. Independent validation passed with observation-index SHA-256 `b35d09a3c63f45ceb764de749d06d621bf56cecb48d3c5019ed4d68c919f50d3` and summary SHA-256 `4429e77e6d687c5abf979276c4b0c2bd2ed3f93226c77821f486024c3917e992`. Confirmation diagnostic report SHA-256 `8ba8b7cc7ddaac73cf1706ab8530986ffc277338337fa3f2c58d23754a40db58` reproduces the same outcome in three isolated repetitions, without a network namespace, and at 4 GiB, 8 GiB, and unlimited memory. The canonical source exactly matches independently generated trusted output on every input. Zero base residuals and seven plus residuals at indexes 119, 177, 185, 399, 616, 650, and 694, combined with the pinned `continue`-before-success-update code, establish an upstream canonical-solution/special-oracle and bookkeeping incompatibility rather than a local environment defect.
- Temporary action: Preserve the complete 164-task audit unchanged and do not use it to freeze HumanEval+ timeouts. Any additional failure detail remains evaluator-only and must never enter model prompts.
- Resolution or mitigation: Independent confirmation excludes memory, networking, isolation, and nondeterminism as causes. Adopted `DEC-20260803-12` pre-excludes only `HumanEval/32` under manifest `evalplus-benchmarks-2026-08-03-r4`, leaving the official dataset and oracle unchanged and exposing 163 included tasks.
- Required reruns or regenerated artifacts: Complete. Replacement audit `timing-humaneval-20260803-r2-v3` passed all 489/489 observations with zero anomalies and independent artifact validation.
- Related decision: `DEC-20260802-07` and `DEC-20260803-12` (Adopted).

## ISSUE-20260802-01: System Python 3.12 pip was incomplete

- First observed: 2026-08-02
- Status: Resolved
- Severity: Minor
- Description: The host-level `python3.12 -m pip` failed because its distribution lacked `distutils`.
- Affected tasks/models/benchmarks/runs: Initial environment setup only; no models, benchmarks, artifacts, or experiment runs were affected.
- Impact on results: None. No experiment execution occurred.
- Evidence: The host command failed with `ModuleNotFoundError: No module named 'distutils'`; `.venv/bin/python -m pip --version` succeeded with pip 25.0.1.
- Temporary action: Created the required project-local Python 3.12 virtual environment using `python3.12 -m venv .venv`.
- Resolution or mitigation: All documented setup and validation commands use `.venv/bin/python`. The complete environment is pinned in `requirements.lock`.
- Required reruns or regenerated artifacts: None.
- Related decision: `DEC-20260802-01`.

## ISSUE-20260802-02: Official BigCodeBench evaluation pins conflict with Python 3.12

- First observed: 2026-08-02
- Status: Resolved
- Severity: Major
- Description: BigCodeBench `0.2.5` declares a large unsegmented package dependency set and its official tagged `Requirements/requirements-eval.txt` pins packages that cannot reproduce the official local environment under Python 3.12. In particular, official PyPI metadata for NumPy `1.21.2` and Numba `0.55.0` requires Python `<3.11`; TensorFlow `2.11.0` provides no Python 3.12 wheel. The upstream evaluation Dockerfile uses Python 3.10.
- Affected tasks/models/benchmarks/runs: All 1,140 BigCodeBench-Instruct tasks; no models or experiment runs have started.
- Impact on results: A silent dependency upgrade could change reference and candidate outcomes. The adopted benchmark-specific Python 3.10.12 execution boundary and exact lock prevent that drift; no model experiment was run before complete environment validation.
- Evidence: `configs/benchmarks/bigcodebench.toml` pins evaluator source revision `9bd90fedee89d7dc3676838c75d9642cb0cd0702`, requirements SHA-256 `a4d01fb12cbce5223b51f982265cb7975bea770b758cd85cc91b803d3293e39f`, and the exact 168-package Python 3.10.12 lock. Corrected representative validation passed major dependency categories. Final adapter `v3` audit `timing-bigcodebench-20260803-r2-v3` independently validated all 1,136 included tasks and 3,408 observations with zero anomalies; summary SHA-256 is `39b8276dc3b3773e29dc4a300b5e979d48af3ab28a9e9e48fdd5e9cae9d2ed81`.
- Temporary action: BigCodeBench candidate evaluation remained blocked until the isolated environment and final task scope passed complete reference validation.
- Resolution or mitigation: `DEC-20260802-03` adopted an isolated Python 3.10.12 environment only for BigCodeBench candidate execution. The standalone worker, exact lock, immutable setup attempts, resource policy, and sandbox were validated by the complete corrective audit; Python 3.12 remains required everywhere else.
- Required reruns or regenerated artifacts: Complete. The partial `v1` audit remains immutable, and corrective audit `timing-bigcodebench-20260803-r2-v3` is the accepted validation dataset.
- Related decision: `DEC-20260802-03` (Adopted).

## ISSUE-20260802-03: BigCodeBench package metadata invalidated evaluator-only pip check

- First observed: 2026-08-02
- Status: Resolved
- Severity: Minor
- Description: Setup attempt `setup-20260802T134237531534Z` installed the official BigCodeBench wheel without its dependencies and then installed the complete tagged evaluation requirements. The final `pip check` failed because the distribution metadata also requires unrelated generation, serving, and remote-API packages, including vLLM, Transformers, OpenAI, and Anthropic.
- Affected tasks/models/benchmarks/runs: BigCodeBench Python 3.10.12 environment setup only. No candidate evaluation, model inference, experiment run, or result was produced.
- Impact on results: None. The partial environment was never promoted to the canonical path and cannot be used by the evaluator.
- Evidence: The immutable status and log under `runs/logs/bigcodebench-environment/setup-20260802T134237531534Z/` record successful installation of the tagged evaluation requirements followed by a `CalledProcessError` from `pip check`; the missing packages exactly match unused BigCodeBench distribution dependencies.
- Temporary action: Preserve the failed attempt, raw log, and partial build directory. Do not promote or silently reuse the partial environment.
- Resolution or mitigation: `DEC-20260802-05` separates evaluator provenance from package installation. Linked attempt `setup-20260802T140114502890Z` completed with Python 3.10.12, passed `pip check`, and produced freeze SHA-256 `2a02d160f4c4e8f37850f6955ee697bef1325216ed3a6b4aeef82110fc597e9b`. Its 168-package environment is committed as `requirements-bigcodebench.lock`; future setup verifies and installs that exact lock.
- Required reruns or regenerated artifacts: The corrected environment rerun is complete. Representative and full-reference BigCodeBench validation remain required as benchmark-preparation tasks, not as remediation of this issue.
- Related decision: `DEC-20260802-05` (Adopted).

## ISSUE-20260802-04: BigCodeBench sandbox omitted a writable home directory

- First observed: 2026-08-02
- Status: Resolved
- Severity: Minor
- Description: Representative validation attempt `validation-20260802T141736405162Z` classified the official matplotlib reference for `BigCodeBench/69` as functional `FAIL` with `RuntimeError: Could not determine home directory`. The minimal bubblewrap environment did not provide `HOME`, while the sandbox deliberately omitted the host home directory.
- Affected tasks/models/benchmarks/runs: The matplotlib representative check and potentially other BigCodeBench tasks whose libraries resolve a user home or cache directory. No model inference or experiment run has started.
- Impact on results: None. The failure occurred during evaluator preparation and the affected environment was not used for experiment candidates. Treating the infrastructure-induced exception as candidate failure in an experiment would have been invalid.
- Evidence: The preserved failed validation report under `runs/logs/bigcodebench-validation/validation-20260802T141736405162Z/` shows every other category passing twice and only matplotlib failing with the home-directory error. After setting the isolated home and cache paths, direct validation report `validation-20260802T142600-home-fix/report.json` records all six categories passing twice and the known-incorrect candidate failing functionally.
- Temporary action: Stop downstream full-reference evaluation until the sandbox environment is corrected and representative validation passes.
- Resolution or mitigation: Set deterministic sandbox-only `HOME=/tmp`, `XDG_CACHE_HOME=/tmp/.cache`, and `MPLCONFIGDIR=/tmp/matplotlib`; no host home or cache is exposed. Added a regression test for these environment invariants. The corrected representative validation completed in 28 seconds with no incomplete dependency categories.
- Required reruns or regenerated artifacts: The representative validation was rerun successfully. No experiment artifacts require regeneration; the full 1,140-reference audit remains a planned preparation task.
- Related decision: None; this is an implementation-only sandbox correction that does not change the study construct.

## ISSUE-20260802-05: EvalPlus representative validation compared volatile timing values

- First observed: 2026-08-02
- Status: Resolved
- Severity: Minor
- Description: After evaluator-internal reference timings were added to EvalPlus results for timeout calibration, the representative validator's whole-object equality check treated normal sub-millisecond timing variation as nondeterministic behavior.
- Affected tasks/models/benchmarks/runs: HumanEval+ and MBPP+ representative implementation validation only. No timing audit, model inference, experiment run, or result was affected.
- Impact on results: None. Functional status, outcome, checked-input counts, and failure classification were stable; only newly exposed runtime measurements differed.
- Evidence: The first direct `scripts/validate_evalplus.py` invocation stopped on the HumanEval+ repeat comparison. After separating classification fields from timing fields, the pinned HumanEval+ and MBPP+ references passed and intentionally incorrect candidates failed.
- Temporary action: Stop the timing-audit launch until the validator distinguishes classification determinism from expected timing variability.
- Resolution or mitigation: Compare only evaluation status, functional outcome, base/plus status, checked-input counts, and failure type for deterministic classification. Preserve every measured timing value independently in the audit. Added a regression assertion that timing-only variation leaves the classification tuple unchanged.
- Required reruns or regenerated artifacts: Representative EvalPlus validation was rerun successfully. No generated audit or experiment artifacts require replacement.
- Related decision: `DEC-20260802-07` (Adopted).

## ISSUE-20260803-01: Thirty-five BigCodeBench references fail reproducibly

- First observed: 2026-08-03
- Status: Resolved
- Severity: Major
- Description: Full reference audit `timing-bigcodebench-20260802-r1` completed all three repetitions, but the same 35 of 1,140 official reference tasks were anomalous in every repetition. Adapter `standalone-local-v2` corrected four result-channel, four system-path, two isolated-loopback, and two non-root filesystem cases. Integrated rerun `diagnostic-20260803-r9-integrated-v2` confirms those 12 references pass. Of the remaining cases, 17 require NLTK/TextBlob data absent from both the lock and upstream Dockerfile, and six attempt DNS or external-service access. The six are network-touching tasks, but follow-up live-network checks show they are not one homogeneous six-task exclusion class.
- Affected tasks/models/benchmarks/runs: BigCodeBench-Instruct tasks `14`, `15`, `16`, `101`, `176`, `177`, `290`, `314`, `332`, `334`, `376`, `383`, `459`, `460`, `590`, `633`, `635`, `655`, `658`, `726`, `734`, `806`, `808`, `812`, `832`, `849`, `940`, `1005`, `1012`, `1038`, `1040`, `1101`, `1103`, `1104`, and `1109`; audit `timing-bigcodebench-20260802-r1`. No model or generated candidate is affected because inference has not started.
- Impact on results: The `v1` audit cannot support timeout calibration, but it affected no model result because inference had not started. The frozen four-task exclusion and resource policy prevent its infrastructure anomalies from being misclassified as candidate functional `FAIL`.
- Evidence: The audit contains 3,420/3,420 schema-valid observations and raw outputs. Independent validation passed with observation-index SHA-256 `6856e2b9528df9741dbc8ac754887508135027abb9b0a32218e1045db3a193b8` and summary SHA-256 `8ef12d5a25dd20632a63ee1523a4cc88b74ed6dd135a746f264baf07beebeaa5`. The summary records 3,315 passes and 105 anomalies, exactly three anomalies for each affected task. Tasks `16`, `1101`, `1103`, and `1104` produced invalid evaluator output; tasks `290`, `376`, `655`, `658`, `726`, `806`, `808`, and `849` explicitly reported missing NLTK corpora. Evaluator-only report `network-feasibility-20260803-r1` (SHA-256 `5498b971fde426fff8d5a7385b06aeef1fe837fb6a690d7cc9da3593f6319416`) records three live-network repetitions per task: `/101`, `/176`, `/314`, and `/1012` passed all repetitions; `/590` consistently had three HTTP 403 errors across six tests, and `/1005` consistently had four 403-derived failures across five tests. This check used official references only, not generated candidates.
- Temporary action: The completed `v1` audit was preserved unchanged, four exclusions were applied before evaluation, and model-candidate evaluation remained blocked until the corrective audit passed. Evaluator diagnostics remain evaluation-only and must never enter model prompts.
- Resolution or mitigation: `standalone-local-v3` retains every `v2` containment correction, mounts four revision- and checksum-pinned NLTK resources read-only, binds deterministic resolver data for `/176`, and starts a loopback-only TLS handshake fixture for `/314`. Adopted `DEC-20260803-09` pre-excludes `/101`, `/590`, `/1005`, and `/1012`; no generated candidate receives live egress. Targeted diagnostic `diagnostic-20260803-r12-targeted-v3` passed 93/93 evaluations, and corrective audit `timing-bigcodebench-20260803-r2-v3` then passed all 3,408 observations with zero anomalies. Its independently verified index and summary SHA-256 values are `0f615816d8cf1b17ae5d037b73f74ed323d4f62c800b127e36a3aa75b63f32a3` and `39b8276dc3b3773e29dc4a300b5e979d48af3ab28a9e9e48fdd5e9cae9d2ed81`.
- Required reruns or regenerated artifacts: Complete. Never overwrite or relabel the original 3,420 `v1` observations or diagnostic reports; use the corrective `v3` audit for accepted reference timing analysis.
- Related decision: `DEC-20260802-03`, `DEC-20260802-07`, `DEC-20260803-08`, and `DEC-20260803-09` (Adopted).
