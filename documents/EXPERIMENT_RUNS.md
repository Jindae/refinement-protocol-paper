# Experiment Runs

The first and draft2 replacement model pilots and their candidate-evaluation descendants completed on 2026-08-04. They are validation evidence only and are not part of the primary estimates. Primary inference has not started.

Repository formatting, type checking, schema export checks, and unit tests are implementation validation and are not registered as experiment runs.

## vllm-smoke-new-models-20260804-r2

- Purpose: Replace invalidated `r1` with canonical direct chat-template token-ID validation for the three newly added checkpoints under the unchanged common vLLM environment.
- Status: Completed and independently validated.
- Start and end time: 2026-08-04 11:21:35 to 11:23:50 Asia/Seoul.
- Git commit: `a95ad7927817a04504da25d6ba26074a7c12ad4f`.
- Environment identifier: `vllm-environment-2026-08-03-r1`; vLLM 0.26.0, TP=2, PyTorch-native sampler, batch invariance enabled.
- Configuration and prompt versions: `vllm-new-model-compatibility-2026-08-04-r2`, configuration SHA-256 `b61cdfd793a544f4dc5c8774ccd03be966d1574fbb4f5745d83449d23de81997`; model manifest `model-checkpoints-2026-08-04-r2` SHA-256 `eb87e51762c69d248f57a9cbd08748ab3f7d868a7b566cab5534e32d6cd30d66`.
- Models and benchmarks: Qwen2.5-Coder-7B-Instruct BF16, Devstral-Small-2-24B-Instruct official FP8, and Gemma-4-31B-Instruct-QAT-W4A16; no benchmark was executed.
- Task scope: One validation-only function-generation prompt repeated twice per model; no experiment candidate.
- Output location: `runs/logs/vllm-model-smoke/vllm-smoke-new-models-20260804-r2/`.
- Machine-readable manifest: Terminal `status.json`, summary SHA-256 `81c7c6febd17f38add9b63263ad6fd847e4e09427838c1d2eb91bebbbc58e824`, and result SHA-256 values `1fbc0e9c...23aed52`, `113f23c1...07e10a`, and `4032a92b...5d09b` in manifest order.
- Completeness summary: 3/3 models loaded at 16K and produced exact repeated responses/token IDs under `prompt_input_mode=chat-template-token-ids`. Prompt/output counts were Qwen2.5 103/17, Devstral 81/17, and Gemma 87/37. Candidate-fence parsing passed for every response.
- Validation result: Passed terminal metadata, committed/captured configuration, manifest and architecture/precision provenance, direct token-input mode, exact repeated tokens, raw responses, token counts, and candidate-fence contract. Post-run GPUs were both 15 MiB and 0% utilization with no compute process.
- Known issues: Resolves `ISSUE-20260804-07`; normal vLLM shutdown/JIT warnings did not affect completeness or leave a process.
- Parent, replacement, or superseded run: Replaces invalidated `vllm-smoke-new-models-20260804-r1`; historical `r1` remains immutable.
- Notes: Existing vLLM 0.26.0 supports all three new architectures. No environment upgrade or model-specific engine is needed.

## vllm-smoke-new-models-20260804-r1

- Purpose: Validate loading, 16K allocation, batch-invariant deterministic generation, token accounting, and candidate-fence compliance for the three newly added checkpoints under the existing common vLLM environment.
- Status: Invalidated as common serving certification after terminal completion.
- Start and end time: 2026-08-04 11:05:41 to 11:11:33 Asia/Seoul.
- Git commit: `e479bde4417200c44c91c34dc7b452883f833018`.
- Environment identifier: `vllm-environment-2026-08-03-r1`; vLLM 0.26.0, TP=2, PyTorch-native sampler, batch invariance enabled.
- Configuration and prompt versions: `vllm-new-model-compatibility-2026-08-04-r1`, configuration SHA-256 `9fafcc77bc023507de6de5f2d4f885fe9b67c4cbafafad03cd4ce934cf6ce8f4`; model manifest `model-checkpoints-2026-08-04-r2` SHA-256 `eb87e51762c69d248f57a9cbd08748ab3f7d868a7b566cab5534e32d6cd30d66`.
- Models and benchmarks: Qwen2.5-Coder-7B-Instruct BF16, Devstral-Small-2-24B-Instruct official FP8, and Gemma-4-31B-Instruct-QAT-W4A16; no benchmark was executed.
- Task scope: One validation-only function-generation prompt repeated twice per model; no experiment candidate.
- Output location: `runs/logs/vllm-model-smoke/vllm-smoke-new-models-20260804-r1/`.
- Machine-readable manifest: Terminal `status.json`, `summary.json` SHA-256 `8c5304f21aa4fcb4e0851caaf8e2eb9d1530b8e26997b7b893eefb60f9ea24e9`, and three immutable result records.
- Completeness summary: Process completed 3/3 models. All loaded at 16K, produced exact repeated response/token equality, met the candidate fence contract, and released both GPUs to 15 MiB and 0% utilization.
- Validation result: Invalidated for serving freeze. Qwen2.5 and Gemma stored token IDs exactly match direct chat-template tokenization, but Devstral canonical/stored prompt IDs differ at 81 versus 88 because `tokenize=False` output was retokenized.
- Known issues: `ISSUE-20260804-07`.
- Parent, replacement, or superseded run: Replacement `vllm-smoke-new-models-20260804-r2` is required; `r1` remains immutable architecture-loading evidence only.
- Notes: No inference environment change is required. The defect is confined to the shared prompt preparation path and was found before any six-model pilot or primary run.

## evaluation-pilot-draft3-20260803T234541Z

- Purpose: Evaluate all 144 exact candidates from the complete draft3 four-model pilot under adopted timeout policy `r2`, independently of inference.
- Status: Completed and independently validated.
- Start and end time: 2026-08-04 08:45:50 to 09:03:20 Asia/Seoul.
- Git commit: `07e04f1ba109dd874029862e0f56a83a28246a0e`.
- Environment identifier: Python 3.12 orchestration with isolated EvalPlus `self-refinement-isolated-v3` and BigCodeBench `standalone-local-v3`.
- Configuration and prompt versions: Timeout policy `candidate-timeouts-2026-08-04-r2`, SHA-256 `b8482c2173ed0d98c29012bcf66f33fae11e8a3725040cb20a380de2f05570ba`; inherited `primary-prompts-2026-08-04-draft3`.
- Models and benchmarks: 144 stored Direct, `R`, `CR`, and `CPR` candidates from all four models across all three pilot benchmarks.
- Task scope: Exact candidate set from parent inference `run_856e8d87f7ed9bec7dec9a5c`; 36 candidates per protocol and 36 per model.
- Output location: `runs/registry/run_5b4f4a5a93f86c60a7efe19c/`; operational attempt `runs/logs/evaluation-campaign/evaluation-pilot-draft3-20260803T234541Z/`.
- Machine-readable manifest: Terminal manifest `run_manifest_6702f15d9ce942996fe472e4`; summary SHA-256 `38033dfd803fa780696538877c5ce3138f353793506022735e9751cd05a512f1`; validation SHA-256 `3d5be2e216da84753ea0ebe05e8cb4995e044193cf2e70e2d5bb0c48473b7144`.
- Completeness summary: 144/144 primary attempts and resolutions, 18 timeout-only confirmations, and 162 immutable raw evaluator outputs. Final outcomes are 62 `PASS`, 73 functional `FAIL`, and nine `TIMEOUT`, with zero evaluator failures.
- Validation result: Passed source lineage, exact counts, schemas, raw-output integrity, terminal manifest, frozen `r2` assignments, and timeout-only confirmation completeness.
- Known issues: Evaluation itself has no unresolved issue and completes the candidate-format verification in `ISSUE-20260804-05`. Parent inference Decision behavior is separately tracked by `ISSUE-20260804-06`.
- Parent, replacement, or superseded run: Child of `run_856e8d87f7ed9bec7dec9a5c`; replaces no prior draft3 evaluation because none exists.
- Notes: Evaluation is separate from inference and no result enters a model prompt.

## pilot-review-draft3-20260804T000600Z

- Purpose: Final automated and manual-evidence review of the complete draft3 four-model inference and independently validated `r2` evaluation.
- Status: Completed; automated gate is `review_required` and primary remains blocked.
- Start and end time: 2026-08-04 09:06 Asia/Seoul; foreground report generation completed in one invocation.
- Git commit: `17936a6a86c8dfb04e1bd218a0d3fd542e3bab18`; source inference/evaluation retain their own recorded commits.
- Environment identifier: Main Python 3.12 project environment; read-only access to independently validated inference/evaluation registries.
- Configuration and prompt versions: Report schema `pilot-review-v3`; `primary-prompts-2026-08-04-draft3`; timeout policy `candidate-timeouts-2026-08-04-r2`.
- Models and benchmarks: All stored records from inference `run_856e8d87f7ed9bec7dec9a5c` and evaluation `run_5b4f4a5a93f86c60a7efe19c` across the frozen nine-task, three-benchmark pilot.
- Task scope: Four models × nine tasks × seven calls, 144 generated candidates, and every generated-candidate evaluation.
- Output location: `runs/logs/pilot-review/pilot-review-draft3-20260804T000600Z/report.json`.
- Machine-readable manifest: Report SHA-256 `af70a292b1c0112f2e555605e3ab6e149f1cf64335a27f9829ab226333d21e90`.
- Completeness summary: Accounts for all 252 model calls, 144 candidates, 27 parseable Decisions, 81 derived outcomes, and 144 evaluation resolutions. It traces all 18 primary timeouts and nine final timeouts.
- Validation result: Candidate, critique, plan, evaluation, and provenance behavior passed. The gate blocks on nine StarCoder2 invalid Decision responses, their 27 missing derived outcomes, and ten recorded length finishes; nine length finishes are those invalid Decisions and one is a parse-complete repetitive plan.
- Known issues: `ISSUE-20260804-06`; user choice is required by proposed `DEC-20260804-27` before Decision generation or length-stop acceptance changes.
- Parent, replacement, or superseded run: Reviews draft3 inference `run_856e8d87f7ed9bec7dec9a5c` and evaluation `run_5b4f4a5a93f86c60a7efe19c`; all prior reports remain immutable.
- Notes: No existing response is reparsed or retried. Pilot artifacts are validation-only and do not enter primary estimates.

## campaign-pilot-draft3-20260803T231356Z

- Purpose: Complete four-model replacement pilot of the adopted exact-single-Python-fence candidate extractor and mixed-text Critique/Plan contract.
- Status: Completed and independently validated; candidate evaluation pending.
- Start and end time: 2026-08-04 08:14:11 to 08:40:44 Asia/Seoul.
- Git commit: `191e8ab6e72e677d96f1b2ece7bcc712a742cc95`.
- Environment identifier: `vllm-environment-2026-08-03-r1`; primary inference `primary-inference-2026-08-03-r2`; vLLM 0.26.0, TP=2 batch-invariant PyTorch-native greedy inference.
- Configuration and prompt versions: Campaign `pilot-campaign-2026-08-04-r3` SHA-256 `19fc42b18f7447f5902cbc05cc3d3435b9c636336050cc66361c418dfced1e1b`; prompt `primary-prompts-2026-08-04-draft3` manifest SHA-256 `ecf957cc0d2ed3f5eac33ee70162d1ecdf5b137b0c64d21cb25fedb6add20e63`; scope `pilot-public-length-quantiles-2026-08-03-r1`.
- Models and benchmarks: All four pinned checkpoints over three HumanEval+, three MBPP+, and three BigCodeBench-Instruct pilot tasks.
- Task scope: Four models × nine tasks × seven planned phases = 252 task-phase units.
- Output location: `runs/registry/run_856e8d87f7ed9bec7dec9a5c/`; operational attempt `runs/logs/model-campaign/campaign-pilot-draft3-20260803T231356Z/`.
- Machine-readable manifest: Terminal manifest `run_manifest_493e77db7617871328a4ebae`; summary SHA-256 `57c428519c2ac838e49f1488e98d0da7f5bf42665b4300db31bc63cc93ee8817`; validation SHA-256 `afe26e69db778af19a701ddfc9ed8f78c260db74e383a36d93b06adb5c0ff1e2`.
- Completeness summary: 252/252 model calls and raw responses, 144 candidates (36 each Direct, `R`, `CR`, `CPR`), 36 Decisions, 36 critiques, 36 plans, and 108 derived outcomes. All four models completed all seven phases with zero failed or blocked units.
- Validation result: Passed exact model/task/phase counts, raw-response hashes, token/finish metadata, candidate and shared-artifact lineage, derived-only D outcomes, terminal manifest, and GPU cleanup.
- Known issues: Draft3 inference resolves the format-compatibility evidence required by mitigated `ISSUE-20260804-05`; final closure awaits candidate evaluation and review. No new issue observed.
- Parent, replacement, or superseded run: Prospective replacement for draft2 inference `run_143681f34a6855eb1902bd4b`; prior artifacts remain immutable and are not reparsed.
- Notes: No evaluator result is available to this inference worker. Candidate and intermediate artifact rules apply identically to every model.

## evaluation-pilot-r2-20260803T224319Z

- Purpose: Re-evaluate every exact draft2 replacement-pilot candidate under adopted timeout policy `r2`, independently of inference.
- Status: Completed and independently validated.
- Start and end time: 2026-08-04 07:43:32 to 07:53:38 Asia/Seoul.
- Git commit: `bd5b2620d8517485349636afa5fbbb1011c1d0c9`.
- Environment identifier: Python 3.12 orchestration with isolated EvalPlus `self-refinement-isolated-v3` and BigCodeBench `standalone-local-v3`.
- Configuration and prompt versions: Timeout policy `candidate-timeouts-2026-08-04-r2`, SHA-256 `b8482c2173ed0d98c29012bcf66f33fae11e8a3725040cb20a380de2f05570ba`; inherited `primary-prompts-2026-08-04-draft2`.
- Models and benchmarks: 107 stored Direct, `R`, `CR`, and `CPR` candidates over all three pilot benchmarks and four configured models where candidate artifacts exist.
- Task scope: Exact candidate set from parent inference `run_143681f34a6855eb1902bd4b`; protocol counts Direct 27, `R` 27, `CR` 27, and `CPR` 26.
- Output location: `runs/registry/run_6b1f457a1462deac2ffabf52/`; operational attempt `runs/logs/evaluation-campaign/evaluation-pilot-r2-20260803T224319Z/`.
- Machine-readable manifest: Terminal manifest `run_manifest_0527859e3f3dc360b63bdc4c`; summary SHA-256 `1f4028ef8eeaf97e682fa801315b44e9f19640765cb84249c061e57dc1da157d`; validation SHA-256 `2c313ae53473714302d2d47e32e91d951588c69ab37ea004628327154112b21d`.
- Completeness summary: 107/107 primary attempts and resolutions, 10 timeout-only confirmations, and 117 immutable raw evaluator outputs. Final outcomes are 58 `PASS`, 44 functional `FAIL`, and five `TIMEOUT`, with zero evaluator failures.
- Validation result: Passed source lineage, exact counts, schemas, raw-output integrity, terminal manifest, frozen `r2` assignments, and timeout-only confirmation completeness.
- Known issues: Resolves `ISSUE-20260804-04`. The five remaining final timeouts are EvalPlus internal `CandidateTimeout` outcomes at approximately 65.5 seconds, not outer 120-second wall-limit expirations.
- Parent, replacement, or superseded run: Child of `run_143681f34a6855eb1902bd4b`; replacement for superseded-policy evaluation `run_2a7f94f41cc4951f78892906`.
- Notes: No result is supplied to a model prompt. Pilot review schema `v3` will trace every primary timeout and confirmation after validation.

## pilot-review-r2-20260803T225500Z

- Purpose: Automated and manual-evidence review of the draft2 replacement inference and its independently validated `r2` evaluation.
- Status: Completed; automated gate is `review_required` and primary remains blocked.
- Start and end time: 2026-08-04 07:55 Asia/Seoul; foreground report generation completed in one invocation.
- Git commit: `585884b6a9a42e2c3989c84d768d29f281c94798` with review implementation from `bd5b2620d8517485349636afa5fbbb1011c1d0c9`.
- Environment identifier: Main Python 3.12 project environment; read-only access to independently validated inference/evaluation registries.
- Configuration and prompt versions: Report schema `pilot-review-v3`; `primary-prompts-2026-08-04-draft2`; timeout policy `candidate-timeouts-2026-08-04-r2`.
- Models and benchmarks: All stored records from inference `run_143681f34a6855eb1902bd4b` and evaluation `run_6b1f457a1462deac2ffabf52` across the frozen nine-task, three-benchmark pilot.
- Task scope: Expected four models × nine tasks × seven calls, four generated candidate protocols per model-task pair, and every actually generated candidate evaluation.
- Output location: `runs/logs/pilot-review/pilot-review-r2-20260803T225500Z/report.json`.
- Machine-readable manifest: Report SHA-256 `be44bee2b0ca7c65dfbf0f30b98987167d59e0f53872ffcf65f0683ebe0be205`.
- Completeness summary: Accounts for 197 model calls, 107 candidates, 27 Decisions, 80 derived outcomes, and 107 evaluation resolutions. All ten primary timeout traces include exact primary/confirmation timing and raw paths; five resolved to functional `FAIL` and five remained internal candidate timeouts.
- Validation result: Evaluation behavior and representative completed responses passed review. The gate blocks on nine systematic StarCoder2 Direct extraction failures and one isolated Qwen2.5 invalid revision plan; all returned calls ended with `finish_reason=stop`.
- Known issues: `ISSUE-20260804-05`; user choice is required by proposed `DEC-20260804-26` before changing extraction or acceptance policy.
- Parent, replacement, or superseded run: Reviews replacement inference `run_143681f34a6855eb1902bd4b` and replacement evaluation `run_6b1f457a1462deac2ffabf52`; prior reports remain immutable.
- Notes: No old response is reparsed or repaired. Pilot artifacts remain validation-only and do not enter primary estimates.

## evaluation-pilot-20260803T205500Z

- Purpose: Evaluate every candidate from the draft2 replacement pilot under the then-active timeout policy `r1`, independently of inference.
- Status: Completed and independently validated; retained as superseded-policy pilot evidence and not eligible for final pilot freeze.
- Start and end time: 2026-08-04 05:55:01 to 06:00:35 Asia/Seoul.
- Git commit: `7192ecadc6886c6bbe685590f560d15fc4c2e24f`.
- Environment identifier: Python 3.12 orchestration with isolated EvalPlus `self-refinement-isolated-v3` and BigCodeBench `standalone-local-v3`.
- Configuration and prompt versions: Timeout policy `candidate-timeouts-2026-08-03-r1`, SHA-256 `8dbcb6b1697d14e23e6862ee473d27e256c79c3abea9450e3671a11e4815991a`; inherited `primary-prompts-2026-08-04-draft2`.
- Models and benchmarks: 107 stored Direct, `R`, `CR`, and `CPR` candidates over the three benchmarks and four configured models where extraction/dependency artifacts existed.
- Task scope: Exact candidate set from parent inference `run_143681f34a6855eb1902bd4b`; protocol counts Direct 27, `R` 27, `CR` 27, and `CPR` 26.
- Output location: `runs/registry/run_2a7f94f41cc4951f78892906/`; operational attempt `runs/logs/evaluation-campaign/evaluation-pilot-20260803T205500Z/`.
- Machine-readable manifest: Terminal manifest `run_manifest_6e290966c8110469c50db49e`; summary SHA-256 `b5725a5a6660738715ef57f96df4e06c350e185e1315f1667b1215c0c6a9fab4`; validation SHA-256 `46d5b2487893f201a4005037c6d2aa53592242ee555d9b857c3ed7d35c89ceb6`.
- Completeness summary: 107/107 primary attempts and resolutions, 10 timeout-only confirmations, 117 immutable raw evaluator outputs, 97 completed outcomes, zero evaluator failures, and 10 final timeouts.
- Validation result: Passed source lineage, exact counts, schemas, raw-output integrity, terminal manifest, and timeout-only confirmation completeness.
- Known issues: `ISSUE-20260804-04`; all ten final timeouts are `HumanEval/129`. Longer diagnostics found determinate functional failures hidden by the `r1` 15-second confirmation interval.
- Parent, replacement, or superseded run: Child of `run_143681f34a6855eb1902bd4b`. A new evaluation descendant under policy `r2` is required; this run remains immutable.
- Notes: No result was fed to a model prompt. The policy change does not require inference regeneration.

## campaign-pilot-20260803T202912Z

- Purpose: Full four-model replacement pilot using the common draft2 response-format prompt on the frozen nine-task scope.
- Status: Partial for pilot acceptance; durable execution and independent artifact validation completed, but strict parser failures remain.
- Start and end time: 2026-08-04 05:29:17 to 05:51:41 Asia/Seoul.
- Git commit: `7192ecadc6886c6bbe685590f560d15fc4c2e24f`.
- Environment identifier: `vllm-environment-2026-08-03-r1`; primary inference `primary-inference-2026-08-03-r2`; vLLM 0.26.0, TP=2 batch-invariant PyTorch-native greedy inference.
- Configuration and prompt versions: Campaign `pilot-campaign-2026-08-04-r2`; prompt `primary-prompts-2026-08-04-draft2`; scope `pilot-public-length-quantiles-2026-08-03-r1`.
- Models and benchmarks: All four pinned checkpoints over three HumanEval+, three MBPP+, and three BigCodeBench-Instruct pilot tasks.
- Task scope: Four models × nine tasks × seven planned phases = 252 task-phase units.
- Output location: `runs/registry/run_143681f34a6855eb1902bd4b/`; operational attempt `runs/logs/model-campaign/campaign-pilot-20260803T202912Z/`.
- Machine-readable manifest: Terminal manifest `run_manifest_a49be61802a3066aba62b058`; summary SHA-256 `8c73dc1a463c5f518c4278d27a0a616001afd1d53295e034448ab35d9830eea7`; validation SHA-256 `babebcd4c128c58b79047fa9180434a4dd702334557e02d26608ea0d04d870f3`.
- Completeness summary: 197 model-call records: 187 completed, nine extraction failures, and one invalid response. The run contains 107 candidates, 27 Decisions, 27 critiques, 26 plans, and 80 derived outcomes; every returned response and token count passed integrity validation.
- Validation result: Operational and record completeness passed for every explicit success/failure path. Pilot acceptance remains pending manual review of the strict parser results.
- Known issues: `ISSUE-20260804-02` remains open; one additional invalid revision-plan response blocked one CPR lineage.
- Parent, replacement, or superseded run: Replacement for first draft1 pilot `run_2ee6e3449b478af4e56a509f`; neither run enters primary estimates.
- Notes: Exact candidates are reusable for the required timeout-policy `r2` evaluation; no model inference rerun is needed for the timeout decision.

## pilot-review-20260804-r2

- Purpose: Corrected automated and manual-inspection handoff for the first pilot after the original review invocation incorrectly rejected confirmed final timeout resolutions.
- Status: Completed; automated gate is `review_required`.
- Start and end time: 2026-08-04 Asia/Seoul; foreground analysis completed in one invocation.
- Git commit: `c21ddc9c1abd903abee9259bad84c422cb553028`.
- Environment identifier: Main Python 3.12 project environment; read-only access to the two independently validated pilot registries.
- Configuration and prompt versions: Report schema `pilot-review-v2`; inherited `primary-prompts-2026-08-03-draft1` and pilot scope `pilot-public-length-quantiles-2026-08-03-r1`.
- Models and benchmarks: All stored records from inference `run_2ee6e3449b478af4e56a509f` and evaluation `run_408b9ad39cdae36bacca33ae`.
- Task scope: Expected four models × nine tasks × seven calls, with four generated candidate protocols per model-task pair.
- Output location: `runs/logs/pilot-review/pilot-review-20260804-r2/report.json`.
- Machine-readable manifest: Report SHA-256 `36b009f7dbe3d5b9d8e11feb09650d2fe727776af1c516aa185ca72f44533d44`.
- Completeness summary: The report accounts for 198 model calls, 108 candidates, 27 Decisions, 81 derived outcomes, and 108 evaluation resolutions. It lists 30 raw-response inspection paths and five confirmed-timeout candidate paths.
- Validation result: Report generation completed without mutating either source run. The gate correctly treats five confirmation-sourced final timeouts as valid terminal outcomes and blocks on nine StarCoder2 extraction failures plus their missing dependent artifacts.
- Known issues: `ISSUE-20260804-01` is resolved by this report. `ISSUE-20260804-02` remains open and requires a prompt decision before primary execution.
- Parent, replacement, or superseded run: Corrected replacement for the failed report request that produced no report artifact; analyzes the first pilot inference and evaluation pair.
- Notes: Manual inspection confirms the five timeout candidates use combinatorial path enumeration on `HumanEval/129`; the timeout classification is consistent with candidate behavior rather than an evaluator or environment failure.

## evaluation-pilot-20260803T152740Z

- Purpose: Evaluate every candidate produced by the first nine-task, four-model pilot without feeding evaluator information back into inference.
- Status: Completed and independently validated; pilot review remains blocked by the parent inference run's StarCoder2 extraction failures, not by evaluation infrastructure.
- Start and end time: 2026-08-04 00:27:41 to 00:31:14 Asia/Seoul.
- Git commit: `abe2016d32a872cfa20cf99cc3de1a4c6ee25393`.
- Environment identifier: Frozen benchmark-specific evaluators from the pilot source manifest; Python 3.12 orchestration, isolated EvalPlus `self-refinement-isolated-v3`, and BigCodeBench `standalone-local-v3`.
- Configuration and prompt versions: Timeout policy `candidate-timeouts-2026-08-03-r1`; inherited prompt version `primary-prompts-2026-08-03-draft1` through parent run `run_2ee6e3449b478af4e56a509f`.
- Models and benchmarks: 108 stored Direct, `R`, `CR`, and `CPR` candidates from Qwen2.5-Coder-14B-Instruct, DeepSeek-Coder-V2-Lite-Instruct, and Qwen3-Coder-30B-A3B-Instruct-FP8 across all nine pilot tasks. StarCoder2 produced no parseable candidate and therefore had nothing to evaluate.
- Task scope: Every generated candidate from the parent pilot run; 27 candidates per protocol and 36 per successfully completed model.
- Output location: `runs/registry/run_408b9ad39cdae36bacca33ae/`; operational attempt `runs/logs/evaluation-campaign/evaluation-pilot-20260803T152740Z/`.
- Machine-readable manifest: Terminal run manifest `run_manifest_4554dded3575355e9c27f8a8`; summary SHA-256 `49f6e59f5f2a4d80d161cc41bc1a516b54b78e258f78e19ef498c4d435c80c13`; validation SHA-256 `1eaf1c1d6508be6f8bc16a6bbfa5d7a906eb08be435fc0a26fa277b9531d052f`.
- Completeness summary: 108/108 primary attempts and resolutions; 103 completed outcomes (61 `PASS`, 42 functional `FAIL`) and five primary timeouts. All five received the one required 15-second confirmation after their 10-second primary attempt, and all five remained final `TIMEOUT`.
- Validation result: Passed exact source lineage, primary/resolution counts, five timeout-only confirmations, schema validation, and 113 immutable raw-evaluator hashes.
- Known issues: All five confirmed final timeouts are on `HumanEval/129`: Qwen2.5 Direct and Qwen3 Direct/`R`/`CR`/`CPR`. They are valid terminal classifications under the frozen policy, not evaluator failures or unconfirmed work. `ISSUE-20260804-01` records the review-tool defect that initially rejected them.
- Parent, replacement, or superseded run: Descends from inference run `run_2ee6e3449b478af4e56a509f` (`campaign-pilot-20260803T145409Z`).
- Notes: Evaluator results were created only after inference completed and were never inserted into model prompts.

## campaign-pilot-20260803T145409Z

- Purpose: First cross-model functional pilot of the draft prompt/parser and model-resident seven-phase inference campaign on the frozen public-only nine-task scope.
- Status: Partial for pilot acceptance. Durable execution and independent artifact validation completed, but StarCoder2 failed strict extraction on all nine Direct responses and could not enter dependent phases.
- Start and end time: 2026-08-03 23:54:13 to 2026-08-04 00:16:44 Asia/Seoul.
- Git commit: `abe2016d32a872cfa20cf99cc3de1a4c6ee25393`.
- Environment identifier: `vllm-environment-2026-08-03-r1`; primary inference `primary-inference-2026-08-03-r2`; vLLM 0.26.0, TP=2, batch-invariant PyTorch-native greedy inference on two RTX 4090 GPUs.
- Configuration and prompt versions: Campaign `pilot-campaign-2026-08-03-r1`; scope `pilot-public-length-quantiles-2026-08-03-r1`; prompt draft `primary-prompts-2026-08-03-draft1`.
- Models and benchmarks: All four pinned models were attempted on HumanEval+ `/53`, `/108`, `/129`; MBPP+ `/127`, `/131`, `/721`; and BigCodeBench-Instruct `/737`, `/103`, `/764`.
- Task scope: Nine tasks × four models × seven planned independent stages = 252 task-phase units. Three models completed all 63 calls each. StarCoder2 returned nine Direct responses with prose outside an otherwise complete Python fence; strict parsing stored all raw responses as `extraction_failure` and blocked its dependent calls.
- Output location: `runs/registry/run_2ee6e3449b478af4e56a509f/`; operational attempt `runs/logs/model-campaign/campaign-pilot-20260803T145409Z/`.
- Machine-readable manifest: Terminal run manifest `run_manifest_86f4815b0f4dfe6471e78e53`; summary SHA-256 `d516fad1d7099b98aa3e4b3bbb6eaf43669758c5a443e972956f114bd0bd9d71`; validation SHA-256 `28f7e3fcda943fd5cec4927e9de145cd92bbcf5131dcceaee57a2b29575dcac5`.
- Completeness summary: 198 model-call records (189 completed and nine StarCoder2 extraction failures), 108 candidates, 27 Decisions, and 81 derived outcomes. Every returned response has immutable raw bytes, input/output token counts, and `stop` finish reason.
- Validation result: Operational attempt and stored-record integrity passed. Pilot acceptance did not pass because the strict common parser correctly rejected all nine StarCoder2 initial responses, leaving 54 dependent calls and 36 expected candidates unavailable.
- Known issues: `ISSUE-20260804-02`. This is a systematic draft-prompt compliance result, not a parser ambiguity or infrastructure failure; the raw responses begin with variants of “Here's how you can implement…” before the fenced code.
- Parent, replacement, or superseded run: First pilot; any prompt correction requires a new version and new pilot rather than mutation or same-construct retry.
- Notes: Pilot artifacts are retained as validation evidence and do not enter primary estimates.

## vllm-primary-smoke-20260803-r3

- Purpose: Validate all four pinned checkpoints under adopted batch-invariant primary inference configuration `r2` after focused StarCoder2 feasibility passed.
- Status: Completed.
- Start and end time: 2026-08-03 20:49:35 to 21:05:12 Asia/Seoul.
- Git commit: `e88e6b909ec29115b07fe0163fbe10024b7b0d38`.
- Environment identifier: `vllm-environment-2026-08-03-r1`; Python 3.12.13; vLLM 0.26.0; PyTorch 2.11.0+cu130; two RTX 4090 GPUs; TP=2; batch-invariant PyTorch-native sampler.
- Configuration and prompt versions: `primary-inference-2026-08-03-r2`; configuration SHA-256 `f608fafb5e629d6b60ee3525e27345c68b9958754b119649ba6116bde8b8b8cf`; fixed validation-only prompt, common 16,384 context, and 4,096 code-stage output ceiling.
- Models and benchmarks: Four exact pinned checkpoints sequentially; no benchmark task, evaluator output, pilot candidate, or primary candidate.
- Task scope: For each model, render the same prompt with its pinned chat template and generate two simultaneous batch-invariant greedy responses that must match exactly in text and token IDs.
- Output location: `runs/logs/vllm-primary-inference-smoke/vllm-primary-smoke-20260803-r3/`.
- Machine-readable manifest: Captured `configuration.json`, `command.json`, terminal atomic `status.json`, append-only `smoke.log`, four result records, and `summary.json`.
- Completeness summary: 4/4 models passed. Every result records batch invariance and two exactly identical raw responses/token sequences. Prompt/output token counts and worker elapsed seconds were StarCoder2 53/31/49.116, Qwen2.5-Coder 49/17/301.495, DeepSeek-Coder-V2-Lite 28/19/278.371, and Qwen3-Coder FP8 28/17/243.997.
- Validation result: Independent validation passed terminal status/provenance, exact captured configuration, all four model IDs and settings, batch-invariant flag, raw-response equality, token-ID equality/counts, 16K prompt budgets, and summary completeness. Summary SHA-256 is `a3a1ed0d1c7495398ceff0cf2896451d29d7802734eda49f09670e3efe8672c4`. Result SHA-256 values are StarCoder2 `bcd26e6814fd674f20a4be0626dbdb2ba22ef28e576b4362a8bc79ae35cf7070`, Qwen2.5-Coder `c31b2c54c1cf48829e4c3dec0662256d4af2cfae23c52106208ba57fda28836f`, DeepSeek-Coder-V2-Lite `f95712dd0dae519ab0b6846da69e7e6f6d609a45acaaabdafe817a8225e725cb`, and Qwen3-Coder FP8 `19da8118f8a14577b65af126826b7ca73be687007a2ca5b5ae51d36448073004`. Post-run host inspection found no compute process and both GPUs at 15 MiB/0%.
- Known issues: Resolves `ISSUE-20260803-09`. Terminal status retained the configuration/model-manifest provenance required by the `ISSUE-20260803-10` correction. Logs contain non-fatal compilation, kernel-performance, and worker teardown warnings; all results and subsequent model starts completed successfully.
- Parent, replacement, or superseded run: Linked replacement for failed `vllm-primary-smoke-20260803-r2`; informed by completed focused probe `vllm-batch-invariance-probe-20260803-r1`.
- Notes: Pre-experiment validation only; these responses are not experiment candidates. This run certifies one common batch-invariant primary inference path for all four models.

## vllm-batch-invariance-probe-20260803-r1

- Purpose: Focused validation-only feasibility and runtime probe of vLLM 0.26.0 batch-invariant execution after primary smoke `r2` exposed divergent simultaneous greedy outputs.
- Status: Completed.
- Start and end time: 2026-08-03 20:40:18 to 20:42:31 Asia/Seoul.
- Git commit: `986143c704cec8a8b1b871d8cce7f988a22b7fea`.
- Environment identifier: `vllm-environment-2026-08-03-r1`; Python 3.12.13; vLLM 0.26.0; PyTorch 2.11.0+cu130; two RTX 4090 GPUs; TP=2; `VLLM_BATCH_INVARIANT=1`; PyTorch-native sampler.
- Configuration and prompt versions: Validation-only `vllm-batch-invariance-probe-2026-08-03-r1`; configuration SHA-256 `1132b60ad5eb8a2da4fd64c31c2eae8710760aa2c9eb9c46d0d29f1f10178a1c`; unchanged fixed non-benchmark prompt, 16,384 context, and 4,096 maximum output tokens.
- Models and benchmarks: StarCoder2-15B-Instruct only; no benchmark task, evaluator result, or experiment candidate.
- Task scope: Load the pinned StarCoder2 checkpoint on both GPUs and submit two identical prompts simultaneously. Preserve both raw responses/token sequences before requiring exact equality.
- Output location: `runs/logs/vllm-batch-invariance-probe/vllm-batch-invariance-probe-20260803-r1/`.
- Machine-readable manifest: Captured `configuration.json`, `command.json`, terminal atomic `status.json`, append-only `smoke.log`, one result, and `summary.json`.
- Completeness summary: 1/1 model passed. The two raw responses and both 34-token sequences are exactly identical. Worker elapsed time was 110.0725 seconds; batch-invariant initialization used 4.28 GiB KV cache per GPU and reported 112,050 KV-cache tokens with 6.84 maximum concurrency at 16,384 tokens.
- Validation result: Independent validator passed captured configuration equality, committed configuration SHA-256, terminal state, exact result scope/settings, raw response and token equality, token counts, summary, and result hashes. Result SHA-256 is `edf297862268f3900e84c1681b2da201c961bf103b14ef1e5add3e94f3599c17`; summary SHA-256 is `dc404cbd64dee23771f3ad75b08bd57a45cb21c2daefc0072a5a7144f253a280`. Host cleanup found both GPUs at 15 MiB/0% with no compute process. Terminal status omitted its redundant configuration hash, but captured configuration and summary carry and independently match it; `ISSUE-20260803-10` records the fixed status-transition defect.
- Known issues: Tests the recommended mitigation for `ISSUE-20260803-09`; a pass does not by itself adopt the setting for primary inference or establish compatibility for the other three models.
- Parent, replacement, or superseded run: Diagnostic successor to failed primary smoke `vllm-primary-smoke-20260803-r2`; it is not the four-model replacement `r3`.
- Notes: Durable background attempt under `DEC-20260803-18`. Batch invariance added about 39 seconds to the compile/warmup portion observed in `r2` and reduced KV capacity by about 5%, while retaining ample 16K capacity. Cold-vs-warm checkpoint caching prevents a valid end-to-end throughput ratio from the two attempts.

## vllm-primary-smoke-20260803-r2

- Purpose: Replacement four-model validation of the frozen primary inference configuration after correcting the isolated child interpreter's project import path.
- Status: Failed (validation; StarCoder2 loaded at 16K, but repeated batched greedy outputs diverged).
- Start and end time: 2026-08-03 20:08:00 to 20:13:00 Asia/Seoul.
- Git commit: `4cec8dff52c1b80867b42f9e5cee9a52254cde26`.
- Environment identifier: Unchanged `vllm-environment-2026-08-03-r1`; Python 3.12.13; vLLM 0.26.0; PyTorch 2.11.0+cu130; two RTX 4090 GPUs; tensor parallel size two.
- Configuration and prompt versions: Unchanged `primary-inference-2026-08-03-r1` at SHA-256 `835f14cee9b900fdea694bcb21dbbe4fb77b9754f24c064c3597b4c79f415c00`.
- Models and benchmarks: The same four pinned checkpoints and fixed non-benchmark prompt as `r1`; no benchmark or evaluator information.
- Task scope: Four models sequentially, two identical greedy generations each, 16,384 context allocation and 4,096 code-stage output ceiling.
- Output location: `runs/logs/vllm-primary-inference-smoke/vllm-primary-smoke-20260803-r2/`.
- Machine-readable manifest: Preserved `configuration.json`, `command.json`, terminal atomic `status.json`, and append-only `smoke.log`; no per-model result or summary exists because the pre-fix worker rejected unequal responses before writing them.
- Completeness summary: Zero of four model result records. StarCoder2 loaded successfully with 14.86 GiB of weights per rank, 4.51 GiB KV cache per GPU, 118,140 aggregate KV-cache tokens, and reported maximum concurrency 7.21 at 16,384 tokens per request. The first two-request, 4,096-output-token greedy batch then produced non-identical outputs.
- Validation result: Failed with exit code 1 on the exact repeated-output assertion. This establishes StarCoder2 16K memory fit but not deterministic primary generation or four-model completion. A post-failure host check found both GPUs at 15 MiB, 0% utilization, and no compute process.
- Known issues: `ISSUE-20260803-08` is resolved because this attempt reached model generation. `ISSUE-20260803-09` tracks default vLLM batch variance and the missing failed-response artifact.
- Parent, replacement, or superseded run: Replacement for `vllm-primary-smoke-20260803-r1`.
- Notes: This remains pre-experiment validation, not a benchmark or protocol run. Preserve the attempt unchanged; do not select a deterministic-inference mitigation or launch `r3` until its outcome/performance consequences are adopted.

## vllm-primary-smoke-20260803-r1

- Purpose: Validate all four pinned checkpoints under the frozen primary inference configuration, including the 16,384-token context allocation and 4,096-token code-output ceiling.
- Status: Failed (infrastructure; zero model results).
- Start and end time: 2026-08-03 20:05:01 Asia/Seoul (failed immediately).
- Git commit: `089f99e9717f4c6706df84a3976a90a353397127`.
- Environment identifier: `vllm-environment-2026-08-03-r1`; Python 3.12.13; vLLM 0.26.0; PyTorch 2.11.0+cu130; two RTX 4090 GPUs; tensor parallel size two.
- Configuration and prompt versions: `primary-inference-2026-08-03-r1`; configuration SHA-256 `835f14cee9b900fdea694bcb21dbbe4fb77b9754f24c064c3597b4c79f415c00`; 16,384 context, GPU utilization 0.85, PyTorch-native greedy sampling, seed 0, and validation through the 4,096-token code-stage ceiling.
- Models and benchmarks: The four checkpoints in `model-checkpoints-2026-08-03-r1`; one fixed non-benchmark coding prompt, no benchmark tests or evaluator feedback.
- Task scope: Each model loads sequentially on both GPUs, renders the same prompt using its pinned local chat template, and must produce two identical response strings and token-ID sequences.
- Output location: `runs/logs/vllm-primary-inference-smoke/vllm-primary-smoke-20260803-r1/`.
- Machine-readable manifest: Preserved `configuration.json`, `command.json`, terminal `status.json`, and `smoke.log`; no result or summary exists.
- Completeness summary: Zero of four model result records. StarCoder2 weights did not begin loading.
- Validation result: Failed with exit code 1 when `.venv-vllm/bin/python` could not import `self_refinement` from the direct script. Post-failure GPUs were both 15 MiB and idle with no compute process.
- Known issues: `ISSUE-20260803-08`; this is an entrypoint/import defect, not a primary-configuration or GPU-fit result.
- Parent, replacement, or superseded run: Follows compatibility smoke `vllm-smoke-20260803-r3`; replaced by planned `vllm-primary-smoke-20260803-r2` after the runner fix.
- Notes: Immutable failure evidence is retained. No generated text, model candidate, or protocol artifact exists.

## vllm-smoke-20260803-r3

- Purpose: Replacement sequential compatibility validation of all four pinned checkpoints using vLLM's explicit PyTorch-native sampler fallback.
- Status: Completed.
- Start and end time: 2026-08-03 18:33:45 to 18:50:06 Asia/Seoul.
- Git commit: `1bd5c7c81411a01c3b9ccc85940918a08159f72e`.
- Environment identifier: `vllm-environment-2026-08-03-r1`; Python 3.12.13; vLLM 0.26.0; PyTorch 2.11.0+cu130; two RTX 4090 GPUs; tensor parallel size two.
- Configuration and prompt versions: `vllm-four-model-smoke-2026-08-03-r2`; validation-only 4,096-token context ceiling, 0.85 GPU-memory utilization, PyTorch-native sampler, greedy temperature 0, seed 0, and 64 maximum output tokens. These are not frozen experiment decoding settings.
- Models and benchmarks: The four checkpoints in `model-checkpoints-2026-08-03-r1`; no benchmark tasks or evaluator feedback.
- Task scope: Each model loads in its pinned precision, renders the same non-benchmark coding prompt through its local chat template, and generates two repeated outputs whose text and token IDs must match. Models execute sequentially in separate child processes.
- Output location: `runs/logs/vllm-model-smoke/vllm-smoke-20260803-r3/`.
- Machine-readable manifest: `runs/logs/vllm-model-smoke/vllm-smoke-20260803-r3/configuration.json` and `summary.json` when complete.
- Completeness summary: Four of four expected result records are present. All models loaded at their pinned precision and generated two identical greedy response strings and token-ID sequences. Prompt/output token counts were StarCoder2 53/34, Qwen2.5-Coder 49/17, DeepSeek-Coder-V2-Lite 28/19, and Qwen3-Coder FP8 28/17.
- Validation result: Passed terminal status, exit code, exact configuration equality, model order/scope, schema and provenance fields, repeated raw-response equality, repeated token-ID equality, recomputed token counts, explicit PyTorch-native sampler records, and post-run GPU cleanup. Configuration SHA-256 is `58a9b2aed0967632f58b34bc418206f01297dc037282371ea74c763bfa368fbc`; summary SHA-256 is `eb7334cdbce590e667753cda24dab9b19b98e4c1386a1a285d1332d9cce556f8`. Result SHA-256 values are StarCoder2 `271b92ccf659305ece2ecd7b6d069efd5de92cb575331dec025a47e29eb02761`, Qwen2.5-Coder `9ab22e69f0c721526bb01f223ccb902d1689eb253071a3b2bc71576c5d2a003c`, DeepSeek-Coder-V2-Lite `efef18a3aea9dc9899da5f45471548b8ba56bc7249e56cdbb9f2ab44d4b2a022`, and Qwen3-Coder FP8 `ce84361a2eeb865eab7b16e1e0be781fb0dd8a691d15a7157ad208643d11ef9c`.
- Known issues: `ISSUE-20260803-07` was resolved for compatibility validation through the supported opt-out; `DEC-20260803-16` subsequently adopted that PyTorch-native path for the primary configuration. Logs contain non-fatal first-shape Triton JIT and default FP8/MoE performance warnings, plus vLLM worker grace-period SIGTERM messages during per-model teardown. All generations and subsequent model starts passed, and final host inspection found both GPUs at 15 MiB, zero utilization, with no compute process.
- Parent, replacement, or superseded run: Replaces failed `vllm-smoke-20260803-r2`; models, prompt, precision, topology, and greedy decoding are unchanged.
- Notes: Raw smoke responses were stored before any downstream parsing and are never used as experiment candidates or prompts. This run certifies one common vLLM engine path across all four models; the sampler choice applies to compatibility validation only.

## vllm-smoke-20260803-r2

- Purpose: Replacement sequential compatibility validation of all four pinned checkpoints after correcting child executable-path propagation.
- Status: Failed (infrastructure; zero model results).
- Start and end time: 2026-08-03 18:24:24 to 18:26:30 Asia/Seoul.
- Git commit: `aaddd845fc5e7fe880cf56a46ab354793b86645a`.
- Environment identifier: `vllm-environment-2026-08-03-r1`; Python 3.12.13; vLLM 0.26.0; PyTorch 2.11.0+cu130; two RTX 4090 GPUs; tensor parallel size two.
- Configuration and prompt versions: Unchanged `vllm-four-model-smoke-2026-08-03-r1`; validation-only 4,096-token context ceiling, 0.85 GPU-memory utilization, greedy temperature 0, seed 0, and 64 maximum output tokens. These are not frozen experiment decoding settings.
- Models and benchmarks: The four checkpoints in `model-checkpoints-2026-08-03-r1`; no benchmark tasks or evaluator feedback.
- Task scope: Each model loads in its pinned precision, renders the same non-benchmark coding prompt through its local chat template, and generates two repeated outputs whose text and token IDs must match. Models execute sequentially in separate child processes.
- Output location: `runs/logs/vllm-model-smoke/vllm-smoke-20260803-r2/`.
- Machine-readable manifest: `runs/logs/vllm-model-smoke/vllm-smoke-20260803-r2/configuration.json`; no summary was produced.
- Completeness summary: Zero of four models produced a result record. StarCoder2 weights and engine warmup completed before sampling initialization failed.
- Validation result: Failed with exit code 1. The repaired path located and ran `ninja`, but FlashInfer 0.6.14 rejected the host CUDA 11.8 compiler while building its sampling extension. No GPU process remained afterward.
- Known issues: `ISSUE-20260803-06` is resolved by successful executable lookup; the distinct runtime-toolchain issue is `ISSUE-20260803-07`.
- Parent, replacement, or superseded run: Replaces failed `r1`; superseded for compatibility validation by `vllm-smoke-20260803-r3` using the supported PyTorch-native sampler.
- Notes: Immutable status and raw log are retained. No model response, candidate, benchmark result, or downstream prompt was created.

## vllm-smoke-20260803-r1

- Purpose: Sequential compatibility validation of all four pinned checkpoints in the isolated vLLM 0.26.0 environment on two RTX 4090 GPUs.
- Status: Failed (infrastructure; zero model results).
- Start and end time: 2026-08-03 17:48:52 to 17:53:58 Asia/Seoul.
- Git commit: `ada6cb29c20543021c15f6613609c74d926433c5`.
- Environment identifier: `vllm-environment-2026-08-03-r1`; Python 3.12.13; vLLM 0.26.0; PyTorch 2.11.0+cu130; two RTX 4090 GPUs; tensor parallel size two.
- Configuration and prompt versions: `vllm-four-model-smoke-2026-08-03-r1`; validation-only 4,096-token context ceiling, 0.85 GPU-memory utilization, greedy temperature 0, seed 0, and 64 maximum output tokens. These are not frozen experiment decoding settings.
- Models and benchmarks: The four checkpoints in `model-checkpoints-2026-08-03-r1`; no benchmark tasks or evaluator feedback.
- Task scope: Each model loads in its pinned precision, renders the same non-benchmark coding prompt through its local chat template, and generates two repeated outputs whose text and token IDs must match. Models execute sequentially in separate child processes.
- Output location: `runs/logs/vllm-model-smoke/vllm-smoke-20260803-r1/`.
- Machine-readable manifest: `runs/logs/vllm-model-smoke/vllm-smoke-20260803-r1/configuration.json`; no summary was produced.
- Completeness summary: Zero of four models produced a result record. The first checkpoint loaded, but engine initialization stopped before generation.
- Validation result: Failed with exit code 1. Both tensor-parallel workers reported that the `ninja` executable could not be found during FlashInfer kernel preparation. Post-failure inspection found no surviving GPU compute process.
- Known issues: `ISSUE-20260803-06`. This is a runner environment-propagation defect, not checkpoint compatibility evidence.
- Parent, replacement, or superseded run: Follows completed environment preparation `vllm-setup-20260803-r1`; superseded for compatibility validation by `vllm-smoke-20260803-r2`.
- Notes: Immutable status and raw log are retained. No model response, candidate, benchmark result, or downstream prompt was created.

## timing-humaneval-20260803-r2-v3

- Purpose: Final pre-experiment reference timing audit of the 163 manifest-included HumanEval+ tasks after adopting the `HumanEval/32` exclusion.
- Status: Completed.
- Start and end time: 2026-08-03 16:22:39 to 16:31:27 Asia/Seoul.
- Git commit: `dacca01c0f97504b5f35b24a80732d1af4b2e059`.
- Environment identifier: Python 3.12.13 main environment; EvalPlus 0.3.1; isolated adapter `self-refinement-isolated-v3` with global 8 GiB candidate-process limit.
- Configuration and prompt versions: `evalplus-benchmarks-2026-08-03-r4`; three repetitions; 180-second audit safety wall timeout; no prompts or model calls.
- Models and benchmarks: No model; HumanEval+ `v0.1.10` official references only.
- Task scope: 163 included tasks × 3 repetitions = 489 sequential observations; manifest excludes only `HumanEval/32` for the adopted upstream incompatibility reason.
- Output location: `runs/logs/reference-timing-audit/humaneval_plus/timing-humaneval-20260803-r2-v3/`.
- Machine-readable manifest: `runs/logs/reference-timing-audit/humaneval_plus/timing-humaneval-20260803-r2-v3/configuration.json`.
- Completeness summary: 163/163 tasks, 489/489 observations, and 489/489 raw outputs are present; all observations pass with zero anomalies. End-to-end median was 0.9439 seconds, p95 1.3044 seconds, p99 4.2301 seconds, and maximum 6.5765 seconds.
- Validation result: Independent validation passed terminal metadata, exact task/repetition counts, observation schemas, raw-output hashes, inclusion scope, stored index SHA-256 `052772d0c9b102bc6a388ab6d644ce1393e2ec4fa03d989f45a4388cc403cb98`, and recomputed summary SHA-256 `e0f41fdd39a19fcce79d81ee4f27bd9ad0a3d6b510a799cf0b1cb80ee9822656`.
- Known issues: `ISSUE-20260803-02` is resolved by the adopted exclusion and this accepted replacement audit. `ISSUE-20260803-05` records and resolves a post-run validator namespace defect that did not alter audit artifacts.
- Parent, replacement, or superseded run: Replacement for partial audit `timing-humaneval-20260803-r1`; the prior audit remains immutable.
- Notes: This audit must not overlap MBPP+ reference timing collection or vLLM model serving. Evaluator outputs never enter model prompts.

## timing-mbpp-20260803-r2-v3

- Purpose: Final pre-experiment reference timing audit of the complete 378-task MBPP+ release under the adopted global 8 GiB EvalPlus adapter `v3` policy.
- Status: Completed.
- Start and end time: 2026-08-03 16:35:52 to 16:56:53 Asia/Seoul.
- Git commit: `444c5a9a22e6f89cc7a3e41a19fd7b96e1fad3ed`.
- Environment identifier: Python 3.12.13 main environment; EvalPlus 0.3.1; isolated adapter `self-refinement-isolated-v3` with global 8 GiB candidate-process limit.
- Configuration and prompt versions: `evalplus-benchmarks-2026-08-03-r4`; three repetitions; 180-second audit safety wall timeout; no prompts or model calls.
- Models and benchmarks: No model; MBPP+ `v0.2.0` official references only.
- Task scope: Complete release, 378 tasks × 3 repetitions = 1,134 sequential observations; no exclusions.
- Output location: `runs/logs/reference-timing-audit/mbpp_plus/timing-mbpp-20260803-r2-v3/`.
- Machine-readable manifest: `runs/logs/reference-timing-audit/mbpp_plus/timing-mbpp-20260803-r2-v3/configuration.json`.
- Completeness summary: 378/378 tasks, 1,134/1,134 observations, and 1,134/1,134 raw outputs are present; all observations pass with zero anomalies. End-to-end median was 0.9286 seconds, p95 1.2340 seconds, p99 4.8032 seconds, and maximum 27.7711 seconds. `Mbpp/255` passed all three repetitions from 5.9949 to 6.3092 seconds.
- Validation result: Independent validation passed terminal metadata, exact task/repetition counts, observation schemas, raw-output hashes, stored index SHA-256 `b67615098c2cf460d000b3da9c16e8fda6c20e5251e21e87511cd4610b55a9e8`, and recomputed summary SHA-256 `8691dc3a6c6443593e2f913d5cf3823d70ce71618ccf80c7a94810ff036efc62`.
- Known issues: `ISSUE-20260803-03` is resolved by the adopted 8 GiB policy and this accepted replacement audit.
- Parent, replacement, or superseded run: Replacement for partial audit `timing-mbpp-20260803-r1`; the prior audit remains immutable.
- Notes: Started only after the HumanEval+ replacement audit completed and passed independent validation. Evaluator outputs never enter model prompts.

## diagnostic-20260803-r1-confirmation

- Purpose: Independently confirm whether the `HumanEval/32` anomaly depends on local isolation or memory settings, and validate `Mbpp/255` under the adopted global 8 GiB EvalPlus adapter `v3` policy.
- Status: Completed.
- Start and end time: 2026-08-03 13:37:55 to 13:38:22 Asia/Seoul.
- Git commit: `ff6432a6142112b82f0b5b26a416de41cd034a91`.
- Environment identifier: Python 3.12.13 main environment; EvalPlus 0.3.1; NumPy version recorded in the report; isolated adapter `self-refinement-isolated-v3`.
- Configuration and prompt versions: `evalplus-benchmarks-2026-08-03-r3`; global 8 GiB limit; three isolated repetitions; no prompts or model calls.
- Models and benchmarks: No model; HumanEval+ `HumanEval/32` and MBPP+ `Mbpp/255` official references only.
- Task scope: Two previously anomalous tasks. HumanEval additionally used one no-network-namespace evaluation and direct official checks at 4 GiB, 8 GiB, and unlimited memory.
- Output location: `runs/logs/evalplus-reference-diagnostics/diagnostic-20260803-r1-confirmation/`.
- Machine-readable manifest: `runs/logs/evalplus-reference-diagnostics/diagnostic-20260803-r1-confirmation/report.json`.
- Completeness summary: All eight asserted diagnostic conditions passed. `Mbpp/255` passed all three isolated 8 GiB repetitions. `HumanEval/32` reproduced base `fail`/0 details and plus `fail`/7 details in every isolation and memory condition; its seven plus residual failures remained indexes 119, 177, 185, 399, 616, 650, and 694.
- Validation result: Completed report SHA-256 is `8ba8b7cc7ddaac73cf1706ab8530986ffc277338337fa3f2c58d23754a40db58`. The canonical HumanEval output exactly matched separately generated trusted output for all inputs, excluding nondeterminism, memory, and network isolation as causes. Static inspection of the pinned EvalPlus function confirms that `find_zero` success takes `continue` before success progress is recorded.
- Known issues: `ISSUE-20260803-03` is mitigated and targeted validation passed, but replacement full-release validation remains. `ISSUE-20260803-02` is confirmed as an upstream reference-oracle incompatibility; adopted `DEC-20260803-12` excludes only `HumanEval/32` from future model and replacement-audit scope.
- Parent, replacement, or superseded run: Diagnostic follow-up to partial audits `timing-humaneval-20260803-r1` and `timing-mbpp-20260803-r1`; it does not replace their full-release timing data.
- Notes: Evaluator-only inputs, outcomes, and diagnostics never enter model prompts. No oracle, dataset, or prior audit artifact was modified.

## timing-mbpp-20260803-r1

- Purpose: Pre-experiment reference timing audit of the complete pinned MBPP+ release in the exact isolated EvalPlus environment.
- Status: Partial (artifact collection complete; benchmark acceptance failed).
- Start and end time: 2026-08-03 09:22:16 to 09:41:11 Asia/Seoul.
- Git commit: `5f533c2d4019da3ae803747759722392447b9e23`.
- Environment identifier: `main-python-3.12.13-3f53565ca1cdb569`.
- Configuration and prompt versions: `evalplus-benchmarks-2026-08-02-r2`; `self-refinement-isolated-v2`; three repetitions; 180-second audit safety wall timeout; no prompts.
- Models and benchmarks: No model; MBPP+ `v0.2.0`, dataset SHA-256 `af43697e8791c4c149bdfd6b489d8b5412507551ac20e28a439f650b8225db63`.
- Task scope: Complete release, 378 tasks × 3 reference repetitions = 1,134 sequential observations; no exclusions.
- Output location: `runs/logs/reference-timing-audit/mbpp_plus/timing-mbpp-20260803-r1/`.
- Machine-readable manifest: `runs/logs/reference-timing-audit/mbpp_plus/timing-mbpp-20260803-r1/configuration.json`.
- Completeness summary: 378/378 tasks, 1,134/1,134 observations, and 1,134/1,134 raw outputs are present. There are 1,131 passing observations and three functional anomalies, all from `Mbpp/255`. Observation-index SHA-256 is `1e1c72a88fa3028e76fd6e8dfaecaea155e647dbe6248e844ee124449e055a61`; summary SHA-256 is `3a384c914713b67c6f616b75c438ab00938fb75e665cb5a0596eef8b06c30585`.
- Validation result: Artifact integrity passed `scripts/validate_reference_timing_audit.py`, including terminal metadata, exact counts, schemas, observation and raw-output hashes, repetition sets, and recomputed summary. Benchmark acceptance failed because the official `Mbpp/255` reference passed base inputs but returned plus functional `fail` in all three repetitions. Among passing observations, median was 0.8486 seconds, p95 1.0633 seconds, p99 4.2926 seconds, and maximum 25.1983 seconds.
- Known issues: `ISSUE-20260803-03` now diagnoses the deterministic `Mbpp/255` failure as `MemoryError` on plus input 85 under the 4 GiB guard; the unchanged official path passes at 5 GiB. A memory-policy decision and replacement validation remain required before acceptance.
- Parent, replacement, or superseded run: None.
- Notes: This audit started only after HumanEval+ terminated. It is complete and immutable reference-only validation data, but it is partial rather than accepted and never enters model prompts.

## timing-humaneval-20260803-r1

- Purpose: Pre-experiment reference timing audit of the complete pinned HumanEval+ release in the exact isolated EvalPlus environment.
- Status: Partial (artifact collection complete; benchmark acceptance failed).
- Start and end time: 2026-08-03 09:12:47 to 09:20:47 Asia/Seoul.
- Git commit: `d386fc59b84747a4048d14f03555c802ac2bd934`.
- Environment identifier: `main-python-3.12.13-3f53565ca1cdb569`.
- Configuration and prompt versions: `evalplus-benchmarks-2026-08-02-r2`; `self-refinement-isolated-v2`; three repetitions; 180-second audit safety wall timeout; no prompts.
- Models and benchmarks: No model; HumanEval+ `v0.1.10`, dataset SHA-256 `272720b90ac375502c8ed23cd791c2a93dfb22a911641a494da74a426c09f101`.
- Task scope: Complete release, 164 tasks × 3 reference repetitions = 492 sequential observations; no exclusions.
- Output location: `runs/logs/reference-timing-audit/humaneval_plus/timing-humaneval-20260803-r1/`.
- Machine-readable manifest: `runs/logs/reference-timing-audit/humaneval_plus/timing-humaneval-20260803-r1/configuration.json`.
- Completeness summary: 164/164 tasks, 492/492 observations, and 492/492 raw outputs are present. There are 489 passing observations and three functional anomalies, all from `HumanEval/32`. Observation-index SHA-256 is `b35d09a3c63f45ceb764de749d06d621bf56cecb48d3c5019ed4d68c919f50d3`; summary SHA-256 is `4429e77e6d687c5abf979276c4b0c2bd2ed3f93226c77821f486024c3917e992`.
- Validation result: Artifact integrity passed `scripts/validate_reference_timing_audit.py`, including terminal metadata, exact counts, schemas, observation and raw-output hashes, repetition sets, and recomputed summary. Benchmark acceptance failed because the official `HumanEval/32` reference returned base and plus functional `fail` in all three repetitions. Among passing observations, median was 0.8638 seconds, p95 1.0761 seconds, p99 3.9239 seconds, and maximum 5.7962 seconds.
- Known issues: `ISSUE-20260803-02` diagnoses the deterministic `HumanEval/32` failure as an upstream `find_zero` success-bookkeeping defect plus seven canonical-solution/oracle tolerance disagreements. Adopted `DEC-20260803-12` excludes that task without modifying this immutable audit; a 163-task replacement audit remains required.
- Parent, replacement, or superseded run: None.
- Notes: This audit did not overlap another benchmark timing audit. It is complete and immutable reference-only validation data, but it is partial rather than accepted and never enters model prompts.

## timing-bigcodebench-20260803-r2-v3

- Purpose: Final pre-experiment reference timing audit of the 1,136 manifest-included BigCodeBench-Instruct tasks under the adopted `standalone-local-v3` resource, sandbox, and exclusion policy.
- Status: Completed.
- Start and end time: 2026-08-03 07:50:25 to 08:57:34 Asia/Seoul.
- Git commit: `66fb1da5a9135fc99ff3533a5fbd89e22b90b12e`.
- Environment identifier: `bigcodebench-python-3.10.12-4ac45c30001a7c3c-standalone-local-v3`.
- Configuration and prompt versions: `bigcodebench-instruct-2026-08-03-r6`; three repetitions; 300-second audit safety wall timeout; no prompts.
- Models and benchmarks: No model; BigCodeBench-Instruct `v0.1.4`.
- Task scope: 1,136 included tasks × 3 reference repetitions = 3,408 sequential observations. Manifest exclusions are `/101`, `/590`, `/1005`, and `/1012` with reasons frozen before model inference.
- Output location: `runs/logs/reference-timing-audit/bigcodebench_instruct/timing-bigcodebench-20260803-r2-v3/`.
- Machine-readable manifest: `runs/logs/reference-timing-audit/bigcodebench_instruct/timing-bigcodebench-20260803-r2-v3/configuration.json`.
- Completeness summary: 1,136/1,136 tasks, 3,408/3,408 observations, and 3,408/3,408 raw outputs are present. Every observation passed and anomaly count is zero. Observation-index SHA-256 is `0f615816d8cf1b17ae5d037b73f74ed323d4f62c800b127e36a3aa75b63f32a3`; summary SHA-256 is `39b8276dc3b3773e29dc4a300b5e979d48af3ab28a9e9e48fdd5e9cae9d2ed81`.
- Validation result: Passed `scripts/validate_reference_timing_audit.py`, including terminal metadata, exact manifest-included task scope, schemas, observation and raw-output hashes, repetition sets, index and summary hashes, and recomputed summary. End-to-end median was 0.3988 seconds, p95 1.9071 seconds, p99 11.4009 seconds, and maximum 155.8370 seconds.
- Known issues: None for audit acceptance. `ISSUE-20260803-01` is resolved by this corrective run. Exact timeout values remain deliberately unselected pending analysis and the other benchmark audits.
- Parent, replacement, or superseded run: Corrective successor to partial validation-data audit `timing-bigcodebench-20260802-r1`; the predecessor remains immutable and is not overwritten.
- Notes: This is reference-only validation data, not a model experiment or paper-facing result. It is accepted as input to timeout calibration but does not itself freeze a timeout policy.

## timing-bigcodebench-20260802-r1

- Purpose: Pre-experiment validation-data audit of all 1,140 BigCodeBench-Instruct official reference solutions, repeated three times sequentially, to measure evaluator runtime distributions and identify reference failures before freezing timeout and exclusion policy.
- Status: Partial (artifact collection complete; benchmark acceptance failed)
- Start and end time: 2026-08-02 23:59:07 to 2026-08-03 01:07:26 Asia/Seoul.
- Git commit: `f5de677de79a458e96f12de114bc41a012674efc`.
- Environment identifier: `bigcodebench-python-3.10.12-4ac45c30001a7c3c-standalone-local-v1`.
- Configuration and prompt versions: `bigcodebench-instruct-2026-08-02-r4`; reference timing observation schema `reference-timing-observation-v1`; three repetitions; 300-second audit safety wall timeout; no prompts.
- Models and benchmarks: No model; BigCodeBench-Instruct `v0.1.4`.
- Task scope: All 1,140 tasks × 3 reference repetitions = 3,420 sequential observations.
- Output location: `runs/logs/reference-timing-audit/bigcodebench_instruct/timing-bigcodebench-20260802-r1/`.
- Machine-readable manifest: `runs/logs/reference-timing-audit/bigcodebench_instruct/timing-bigcodebench-20260802-r1/configuration.json`.
- Completeness summary: 1,140/1,140 tasks and 3,420/3,420 observations completed. All 3,420 observation files and corresponding raw evaluator outputs exist. Observation-index SHA-256 is `6856e2b9528df9741dbc8ac754887508135027abb9b0a32218e1045db3a193b8`; summary SHA-256 is `8ef12d5a25dd20632a63ee1523a4cc88b74ed6dd135a746f264baf07beebeaa5`.
- Validation result: Artifact integrity passed via `scripts/validate_reference_timing_audit.py`, including terminal metadata, exact counts, schemas, hashes, task repetition sets, and recomputed summary. Benchmark acceptance did not pass: 3,315 observations passed, while 105 anomalies came from the same 35 tasks in all three repetitions. Among passing observations, end-to-end median was 0.3574 seconds, p95 was 1.8338 seconds, p99 was 10.2260 seconds, and maximum was 155.8199 seconds. No timeout has been selected from these data.
- Known issues: This run preserves the original 35 deterministic reference failures tracked by now-resolved `ISSUE-20260803-01`; it therefore remains unsuitable for timeout calibration. Adopted `DEC-20260803-09` and completed corrective audit `timing-bigcodebench-20260803-r2-v3` resolve benchmark acceptance without altering this immutable `v1` run. `ISSUE-20260802-02` is also resolved by the accepted isolated environment.
- Parent, replacement, or superseded run: None.
- Notes: Reference evaluations were sequential to avoid parallel-load distortion. This validation-data audit contains no generated model candidates and no paper-facing result. It is complete and immutable, but it is not a fully accepted benchmark-validation run; any corrective rerun must receive a new linked attempt identifier.
