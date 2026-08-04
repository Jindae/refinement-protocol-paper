# Project Status

## Last Updated

2026-08-04 (Asia/Seoul)

## Active Study Version

- Study design: `study-v0.2.0` (six-model panel adopted in `DEC-20260804-28`; no primary data exist under the superseded four-model scope)
- Data schema: `3.0.0` (`v1` and `v2` exports preserved; no pilot or primary records require migration)
- EvalPlus benchmark manifest: `evalplus-benchmarks-2026-08-03-r4` (163 included HumanEval+ tasks, 378 MBPP+ tasks, `self-refinement-isolated-v3`, global 8 GiB candidate-process limit)
- BigCodeBench benchmark manifest: `bigcodebench-instruct-2026-08-03-r6` (1,136 included tasks, four pre-experiment exclusions, and isolated Python 3.10.12 `standalone-local-v3` adapter)
- Model manifest: `model-checkpoints-2026-08-04-r2` pins the adopted six-model panel; all six exact snapshots are downloaded and validated. The old four-model `r1` manifest and StarCoder2 snapshot remain historical evidence.
- Primary inference: common TP=2, batch-invariant greedy decoding, 16,384 context, and stage output caps remain required. Exact serving environment and six-model configuration are temporarily unfrozen pending Devstral/Gemma compatibility validation; prior `primary-inference-2026-08-03-r2` remains valid only as four-model pilot history.
- Candidate timeout configuration: `candidate-timeouts-2026-08-04-r2` (common 10-second primary; common `max(120 seconds, 1.5 × primary)` confirmation; 16 reference-only primary overrides; three predeclared 180-second HumanEval+ confirmation overrides; exact `r1` archived)
- Experiment configuration: six-model inference/campaign versions are blocked until the three new snapshots and one common serving path validate; prompt draft3 is implemented but not yet primary-frozen
- Execution schedule: `model-resident-all-benchmark-2026-08-03-r1` (one model per campaign; separate all-benchmark Direct, Decision, and refinement phases; derived D protocols make no calls)
- Prompt set: replacement-pilot `primary-prompts-2026-08-04-draft3` implemented and context-validated; one common exact-single-Python-fence candidate extractor and non-empty mixed-text Critique/Plan parser; primary freeze awaits a new cross-model pilot
- Pilot scope: `pilot-public-length-quantiles-2026-08-03-r1` (3 public-length positions per benchmark, 9 tasks total; the replacement run will apply the same public-only tasks to all six models)

## Current Phase

The four-model draft3 inference/evaluation/review is terminal historical pilot evidence. Adopted
`DEC-20260804-28` resolves its StarCoder2 blocker by excluding that checkpoint and expands the
primary panel to six models. The three added snapshots are independently validated; current work tests
Qwen2.5-Coder-7B, Devstral-Small-2-24B, and Gemma-4-31B-QAT-W4A16 in the unchanged common vLLM
environment before preparing the full six-model serving configuration and replacement pilot. No
structured Decision or length-stop policy change was adopted.

## Completed Work

- Created the Python 3.12 project structure and complete dependency lock.
- Added conservative exclusions for generated data, caches, model weights, secrets, and generated paper artifacts.
- Implemented canonical hashing and stable, domain-separated identifiers.
- Implemented typed version `3.0.0` records and committed JSON Schema exports while preserving `v1` and `v2`; `v3` adds an explicit model-call finish reason before any pilot data exists.
- Implemented a write-once local registry with raw-response integrity checks, resume reuse, explicit retries, and run-manifest lineage.
- Added a single validation command covering formatting, lint, strict typing, schema freshness, and tests.
- Passed `./scripts/validate.sh` on 2026-08-02 after BigCodeBench partial-adapter implementation: formatting, lint, strict typing, schema freshness, and all 22 tests passed.
- Pinned EvalPlus `0.3.1`, HumanEval+ `v0.1.10`, and MBPP+ `v0.2.0` with exact release hashes.
- Loaded all 164 HumanEval+ and 378 MBPP+ tasks through a typed adapter that separates public specifications from hidden evaluation data.
- Added namespace- and process-isolated EvalPlus evaluation with explicit functional failure, timeout, and evaluator-failure states.
- Validated repeated reference outcomes and intentionally incorrect outcomes for both EvalPlus benchmarks using `scripts/validate_evalplus.py`.
- Pinned BigCodeBench-Instruct dataset `v0.1.4` (exact repository revision and Parquet SHA-256), evaluator `0.2.5` (source and wheel hashes), and its official evaluation-requirements hash.
- Loaded all 1,140 BigCodeBench tasks with stable identifiers and a typed boundary that exposes only Instruct prompts while retaining code prompts, reference solutions, tests, and declared libraries in evaluation-only records.
- Implemented the exact upstream calibrated candidate composition and a namespace-isolated local `unittest` adapter that separates missing dependencies and timeouts from functional `FAIL`.
- Repeated BigCodeBench reference checks passed for stdlib, NumPy, and pandas samples; an intentionally incorrect candidate failed functionally.
- Adopted `DEC-20260802-03`: Python 3.12 remains the primary orchestration, inference, storage, analysis, and EvalPlus environment; only BigCodeBench candidate execution uses isolated Python 3.10.12.
- Converted the BigCodeBench worker to a standalone Python 3.10-compatible entrypoint and added immutable background environment setup with durable status and logs.
- Added repository-level `AGENTS.md` instructions that standardize every long-running background job, including durable attempts, atomic status, PID-namespace-safe diagnosis, retry preservation, user monitoring, and completion validation.
- Diagnosed failed environment attempt `setup-20260802T134237531534Z`: all evaluation requirements installed, but the unused BigCodeBench distribution metadata made `pip check` require model-serving and remote-API packages. Adopted `DEC-20260802-05`, preserved the failed attempt, and added a provenance-only wheel policy plus a regression test.
- Passed `./scripts/validate.sh` after the setup correction: formatting, lint, strict typing, schema freshness, and all 25 tests passed.
- Completed linked setup attempt `setup-20260802T140114502890Z`: Python 3.10.12, official evaluator wheel and requirements provenance, `pip check`, canonical environment promotion, and package-freeze checksum all validated. Committed the exact 168-package resolution as `requirements-bigcodebench.lock` for subsequent rebuilds.
- Resolved `ISSUE-20260802-04` by providing an isolated writable home and cache directories inside the BigCodeBench sandbox. Direct representative validation completed in 28 seconds: stdlib, NumPy, pandas, matplotlib, scikit-learn, and SciPy references each passed twice, and a known-incorrect candidate failed functionally. Repository validation passes all 26 tests.
- Adopted `DEC-20260802-07`: task timeouts will be calibrated only from repeated official-reference timing, with pre-frozen slow-task overrides and exactly one longer confirmation evaluation for primary-timeout candidates. Implemented typed immutable timing observations and collection for all three benchmarks; no quantitative timeout has been selected yet.
- Passed `./scripts/validate.sh` with formatting, lint, strict typing, schema freshness, and all 29 tests. Direct pinned EvalPlus validation also passed after confirming timing variability is preserved without weakening classification determinism (`ISSUE-20260802-05`).
- Added a compact `--count` view for long count-based audits and made concise progress commands part of the background-job handoff standard. Repository validation now passes all 30 tests.
- Completed BigCodeBench audit `timing-bigcodebench-20260802-r1`: all 1,140 tasks were evaluated three times, producing 3,420 immutable observations and raw outputs. Independent terminal, count, schema, observation-hash, raw-output-hash, repetition, and recomputed-summary validation passed. Of these, 3,315 observations passed; 105 anomalies belonged to the same 35 tasks in all three repetitions.
- Added `scripts/validate_reference_timing_audit.py` and regression coverage so a terminal process status alone cannot certify a reference audit.
- Passed `./scripts/validate.sh` on 2026-08-03: formatting, lint, strict typing, schema freshness, and all 32 tests passed.
- Identified the four `InvalidEvaluatorOutput` anomalies as a worker protocol defect: reference subprocesses inherited and contaminated stdout used for JSON. `standalone-local-v2` now writes through a reserved descriptor while redirecting descendant output, preserves bounded evaluator-only failure traces, and passes a subprocess-noise regression test. No model experiment was affected.
- Passed `./scripts/validate.sh` after the adapter correction: formatting, lint, strict typing, schema freshness, and all 33 tests passed.
- Pinned and inspected the exact upstream `v0.2.5` source revision. Its evaluation Dockerfile provides `/bin` plus system tools including `zip`, `unzip`, `procps`, and R; the local sandbox had omitted `/bin`, explaining three shell-reference failures. Adapter `v2` now binds `/bin` read-only and validates that boundary. System-tool parity beyond `/bin` remains under investigation.
- Passed `./scripts/validate.sh` after the `/bin` parity correction: formatting, lint, strict typing, schema freshness, and all 34 tests passed.
- Corrected the network namespace so it retains external-network isolation while explicitly bringing up loopback and exposing only `/etc/hosts` and `/etc/nsswitch.conf` read-only. This targets the two official references that use local client/server sockets without granting generated code internet access.
- Passed `./scripts/validate.sh` after the loopback correction: formatting, lint, strict typing, schema freshness, and all 35 tests passed.
- Identified two apparent reference/test disagreements as a sandbox identity defect: unlike the official non-root container user, the worker was root inside its user namespace and could bypass file permissions or create root-owned paths. Adapter `v2` now executes candidate/tests as fixed UID/GID 65534 with only `/tmp` writable and records the worker identity in raw evaluator output.
- Targeted non-root diagnostic `diagnostic-20260803-r7-nonroot` made the restricted-file task pass but showed the synthetic sandbox root was still writable. The root mount is now explicitly mode 0555 after setup while `/tmp` remains 1777, with a regression test that rejects candidate root-path creation.
- Passed `./scripts/validate.sh` after the read-only-root correction: formatting, lint, strict typing, schema freshness, and all 36 tests passed.
- Integrated evaluator-only diagnostic `diagnostic-20260803-r9-integrated-v2` reran all 35 prior anomalies under commit `7421e85`: 12 now pass and 23 fail. The report SHA-256 is `53045d9229f73ddb483202310847f8f02d4aaf27b9cffcae76263a9549e457db`. The remaining cases divide into missing NLTK/TextBlob resources (17) and network-touching references (6).
- Rechecked all six network-touching official references three times with host networking in evaluator-only diagnostic `network-feasibility-20260803-r1`: `/101`, `/176`, `/314`, and `/1012` passed 3/3; `/590` and `/1005` failed 3/3 with HTTP 403 behavior. Report SHA-256 is `5498b971fde426fff8d5a7385b06aeef1fe837fb6a690d7cc9da3593f6319416`. This invalidates the blanket inference that all six must be excluded; it does not justify live egress for generated candidates.
- Passed `./scripts/validate.sh` after revising the proposed network-task policy: formatting, lint, strict typing, schema freshness, and all 36 tests passed.
- Adopted `DEC-20260803-09`: exclude `/101`, `/590`, `/1005`, and `/1012`; retain `/176` with pinned resolver data and `/314` with a loopback-only TLS handshake fixture; and keep all generated candidates offline. Manifest `r6` exposes exactly 1,136 included tasks and exclusion-aware audit scope.
- Pinned four NLTK archives to revision `550b6625...c6b2a`, verified both archive and extracted regular-file tree hashes, and mounted the data read-only. Preserved the first smoke failure caused by archive-only `punkt` lookup; replacement `diagnostic-20260803-r11-resource-smoke-extracted` passes all six representatives.
- Passed `./scripts/validate.sh` after the `v3` resource and exclusion implementation: formatting, lint, strict typing, schema freshness, and all 40 tests passed.
- Completed targeted `v3` diagnostic `diagnostic-20260803-r12-targeted-v3`: all 31 included formerly anomalous references passed all three repetitions (93/93). Report SHA-256 is `9a013068555cbf5895c2795e1e87372cf6e07f1db54f683a98ac33cd3d3d532b`; `/1104` and `/1040` were the slowest, at maximum 73.16 and 60.16 seconds respectively.
- Completed and independently validated corrective BigCodeBench audit `timing-bigcodebench-20260803-r2-v3`: all 1,136 included tasks and 3,408 reference observations passed with zero anomalies. Observation-index SHA-256 is `0f615816d8cf1b17ae5d037b73f74ed323d4f62c800b127e36a3aa75b63f32a3`; summary SHA-256 is `39b8276dc3b3773e29dc4a300b5e979d48af3ab28a9e9e48fdd5e9cae9d2ed81`. The end-to-end median was 0.3988 seconds, p95 1.9071 seconds, p99 11.4009 seconds, and maximum 155.8370 seconds; the audit itself did not select a timeout.
- Adopted `DEC-20260803-15` and froze `candidate-timeouts-2026-08-03-r1`: every benchmark uses a 10-second primary default; 16 tasks whose accepted reference maximum exceeded 10 seconds receive coarse 30/60/120/240-second overrides; primary timeouts are collected until the complete primary batch and then confirmed once at 1.5x. Independent policy validation matched the exact accepted summary hashes, task counts, observation counts, and task maxima. Schema `2.0.0`, evaluator configuration adapters, immutable raw evaluator storage, complete-batch gating, linked confirmation, and final resolution are implemented; `./scripts/validate.sh` passes all 66 tests.
- Adopted `DEC-20260803-10` and manifest `model-checkpoints-2026-08-03-r1`, pinning exact commits for the four already-selected official model repositories. Added a durable batch downloader with immutable attempt output, live byte/model progress, remote size and LFS verification, complete local SHA-256 manifests, and atomic canonical promotion. Full repository validation passes 44 tests.
- Completed model batch `models-20260803-r1` in 21 minutes 17 seconds: four exact snapshots, 63 files, and 124,084,848,411 snapshot bytes. Downloader-side LFS/local SHA-256 checks and independent terminal, manifest, revision, size, and canonical-link validation passed. Remote/local manifest SHA-256 values are `6b80ac825505cf81f08faf5f89d55260e3f863ba3cce12cab0578fb1c6c8d41b` and `5c466a7f1737eea1b9bcc12ad75f3ea876f6f9c90a0a8dc0a39b78f9664e0642`.
- Diagnosed `HumanEval/32`: EvalPlus 0.3.1's `find_zero` branch skips success-detail/progress recording, and seven plus inputs make the pinned canonical solution exceed the special oracle's `1e-4` residual tolerance. Base has zero residual failures; plus failures are indexes 119, 177, 185, 399, 616, 650, and 694.
- Diagnosed `Mbpp/255`: plus input index 85 requests 1,663,740 length-77 combinations from five items. With all 2,015,941 expected tuples retained, candidate allocation raises `MemoryError` under 4 GiB; the unchanged official path passes at 5, 6, and 8 GiB.
- Adopted `DEC-20260803-11`: EvalPlus adapter `v3` applies one 8 GiB memory ceiling globally. This retains finite containment, gives margin above the observed 5 GiB passing boundary, and avoids task-specific resource branching.
- Completed confirmation diagnostic `diagnostic-20260803-r1-confirmation` at report SHA-256 `8ba8b7cc7ddaac73cf1706ab8530986ffc277338337fa3f2c58d23754a40db58`: `Mbpp/255` passed 3/3 under isolated adapter `v3`, while every HumanEval cross-condition check confirmed the same upstream `HumanEval/32` incompatibility independently of local environment settings.
- Resolved `ISSUE-20260803-04`: the first model-hash launcher invocation failed before attempt creation because direct-script imports differed from the test `PYTHONPATH`. The exact documented entrypoint now has subprocess regression coverage, the operational checklist is strengthened, and repository validation passes 48 tests before retry `model-hash-20260803-r2`.
- Completed full duplicate hash validation `model-hash-20260803-r2`: all 63 files and 124,084,848,411 snapshot bytes independently matched the pinned local and remote LFS hashes. Terminal status, counts, canonical links, and manifest metadata passed; report SHA-256 is `7b8f5bb5a1d5ada552bfb523c601fe430e28958266ccf26a35722fdf7a894f65`.
- Adopted `DEC-20260803-12` before model inference: manifest `evalplus-benchmarks-2026-08-03-r4` excludes only `HumanEval/32`, retains the immutable 164-task source release, and exposes exactly 163 HumanEval+ tasks. Loader and audit configuration validate the exclusion identifier, reason, membership, and included count without patching the oracle.
- Completed `vllm-setup-20260803-r1`: vLLM 0.26.0 and PyTorch 2.11.0+cu130 passed exact wheel, `pip check`, CUDA import, and two-RTX-4090 capability checks. The 196-package freeze is committed as `requirements-vllm.lock` with SHA-256 `f1f66f8127dc916c576fd847d2478b1793b9a6443050c5f974104ec60a76092a`.
- Preserved failed validation attempt `vllm-smoke-20260803-r1`: StarCoder2 weights loaded, but FlashInfer preparation failed before generation because `.venv-vllm/bin` was absent from the child `PATH` and its installed `ninja` executable could not be found. No per-model result or experiment artifact was produced. `ISSUE-20260803-06` records the diagnosis and runner correction.
- Preserved failed validation attempt `vllm-smoke-20260803-r2`: corrected executable lookup reached bfloat16 weight loading, tensor parallel initialization, FlashAttention 2, torch compilation, and CUDA graph capture, then FlashInfer sampling JIT rejected the host CUDA 11.8 toolkit. No per-model result was produced. `ISSUE-20260803-07` and validation-only `DEC-20260803-14` record the supported PyTorch-native fallback.
- Completed and independently validated `vllm-smoke-20260803-r3`: StarCoder2-15B-Instruct, Qwen2.5-Coder-14B-Instruct, DeepSeek-Coder-V2-Lite-Instruct, and Qwen3-Coder-30B-A3B-Instruct-FP8 all loaded with TP=2 and produced two identical greedy response/token sequences. Exact result, configuration, and summary hashes are recorded in `documents/EXPERIMENT_RUNS.md`; post-run GPU inspection found no compute process.
- Adopted `DEC-20260803-16` and froze `primary-inference-2026-08-03-r1`: all models and stages share deterministic greedy decoding, native 16,384 context, no prompt truncation, and bounded 4,096/2,048/64 stage outputs. Exact model and tokenizer configuration hashes, precision, context support, stage coverage, prompt-budget rejection, and all 73 repository tests pass; replacement four-model runtime validation is planned as `vllm-primary-smoke-20260803-r2`.
- Preserved failed `vllm-primary-smoke-20260803-r1`: the isolated vLLM child could not import the newly referenced project package and stopped before weight loading with zero results. `ISSUE-20260803-08` records the implementation-only diagnosis; the direct entrypoint is now tested under the actual vLLM interpreter before replacement `r2`.
- Adopted `DEC-20260803-17` and execution schedule `model-resident-all-benchmark-2026-08-03-r1`: each checkpoint normally loads once, then separate Direct, Decision, `R`, shared Critique, `CR`, shared Plan, and `CPR` phases each cover all 1,677 included tasks without benchmark-by-benchmark handoff. `DR`, `DCR`, and `DCPR` remain stored-artifact derivations with no model calls. Documentation consistency and all 73 repository tests passed through `./scripts/validate.sh`.
- Completed and independently validated `vllm-batch-invariance-probe-20260803-r1`: StarCoder2 produced two exactly identical 34-token responses under TP=2 batch-invariant mode, retained 6.84 maximum 16K concurrency, and cleaned both GPUs. `DEC-20260803-19` advances primary configuration to `r2` with batch invariance common to every model/stage; no pilot candidate exists under `r1`.
- Completed and independently validated `vllm-primary-smoke-20260803-r3`: all four checkpoints loaded with adopted primary `r2`, and each produced two exactly identical batch-invariant raw responses/token sequences. Terminal configuration/model-manifest provenance, result/summary hashes, 16K budgets, and post-run GPU cleanup passed; `ISSUE-20260803-09` is resolved.
- Implemented hash-pinned external prompt set `primary-prompts-2026-08-03-draft1`, exact stage-input enforcement, stable rendered/prompt hashes, one strict candidate extractor across Direct/`R`/`CR`/`CPR`, and strict Decision/critique/plan parsers. Four exact snapshot tokenizers validated all 1,677 public task specifications and conservative full-upstream-cap context envelopes; the tightest case was StarCoder2 CPR with 2,478 tokens remaining. `./scripts/validate.sh` passes all 89 tests.
- Implemented one common raw-first inference interface and resident vLLM adapter for all four checkpoints. It enforces frozen decoding, resident-model identity, stage-homogeneous batches, exact prompt budgets, per-call immutable raw/token/finish-reason records, malformed-output separation, and explicit overflow/backend/protocol failure records. Active schema `3.0.0` preserves `stop` versus `length`; `./scripts/validate.sh` passes all 99 tests.
- Implemented `ProtocolCampaignRunner` with the adopted seven-phase model-resident order, all-three-benchmark scope validation, task-level batching, immutable candidate/Decision/critique/plan builders, completed-call resume, crash-gap artifact recovery, aggregate/per-benchmark terminal counts, lineage validation, and derived-only `DR`/`DCR`/`DCPR`. Three-benchmark integration tests verify 21 independent calls, exact shared artifacts, 9 derived outcomes, zero-call resume, and task-local failure blocking; `./scripts/validate.sh` passes all 104 tests.
- Implemented the durable production campaign boundary: a Python 3.12 parent exports a hash-checked public-only scope and provenance records, launches one vLLM child per checkpoint sequentially, keeps each model resident across all seven phases, writes atomic batch-level status/count data, creates versioned run manifests, and supports explicit same-run resume through a new attempt. The full-scope configuration remains execution-gated while prompts are draft. A host-level preflight passed all 1,677 public tasks, four exact snapshots, Python 3.12.13, vLLM 0.26.0, 14.59 TB free disk, and two clear GPUs without loading a model or creating an experiment run.
- Froze public-only pilot scope `pilot-public-length-quantiles-2026-08-03-r1`: shortest, median, and longest included specification per benchmark, nine tasks total, with no hidden evaluator data used for selection. Host preflight passed the exact scope, all four snapshots, Python 3.12.13, vLLM 0.26.0, and two clear GPUs without loading weights.
- Implemented separate durable candidate evaluation with complete-primary gating, frozen timeout assignment, timeout-only confirmation, final resolution, raw-output immutability, task-level resume, status/count monitoring, and independent validation. Added automated pilot review summaries and `EXPERIMENT_RUNBOOK.md` with copy-and-paste commands for pilot, resume, review, gated primary inference, and primary evaluation.
- Final repository validation passes formatting, lint, strict typing, schema freshness, and all 125 tests.
- Completed pilot inference `run_2ee6e3449b478af4e56a509f`: three models produced 189 completed calls, 108 candidates, 27 Decisions, and 81 derived outcomes; StarCoder2 produced nine immutable Direct extraction failures because every response added prose outside its Python fence.
- Completed and independently validated evaluation descendant `run_408b9ad39cdae36bacca33ae`: 108/108 resolutions, comprising 61 `PASS`, 42 functional `FAIL`, and five confirmed final `TIMEOUT` results with exactly one 1.5x confirmation each.
- Corrected the pilot review gate so schema-valid confirmed final timeout resolutions are reported for manual inspection rather than rejected as impossible; added regression coverage and explicit candidate paths.
- Generated corrected report `pilot-review-20260804-r2` (SHA-256 `36b009f7dbe3d5b9d8e11feb09650d2fe727776af1c516aa185ca72f44533d44`). Its automated gate is `review_required` because of the StarCoder2 extraction failures and dependent missing artifacts, not the five confirmed timeouts.
- Adopted `DEC-20260804-23` and created `primary-prompts-2026-08-04-draft2`: all four candidate-producing stages use the same stronger response-only fence wording for every model, while Decision/critique/plan bytes, strict parsers, public-only inputs, inference settings, and evaluation remain unchanged. The first pilot and draft1 configuration are preserved.
- Validated draft2 hashes, canonical input fields, and conservative 16K envelopes over all 1,677 public tasks with all four exact tokenizers. The tightest case remains StarCoder2 CPR, with 2,433 tokens free after reserving the full upstream/output caps and 64-token boundary margin.
- Resolved `ISSUE-20260804-03`: replacement preflight had hard-coded the draft1 prompt path. It now retains exact primary inference/model checks while validating the versioned prompt selected by the campaign; the failed preflight created no attempt or artifact.
- Host-level clean-worktree preflight passed replacement campaign `pilot-campaign-2026-08-04-r2`: execution gate enabled, exact four models and nine-task scope, all configuration hashes, Python 3.12.13, vLLM 0.26.0, 14.59 TB free disk, and both GPUs clear at 15 MiB. No model was loaded and no run was created.
- Implemented a separate final-timeout diagnostic runner with explicit timeout, optional candidate filtering/per-candidate execution, exact task/source deduplication, immutable raw/results, foreground and durable background modes, compact monitoring, and independent validation. It never mutates or reclassifies the source evaluation run. Latest replacement-pilot evaluation preflight selects 10 final timeouts as four unique HumanEval+ task/source executions at a user-specified 60 seconds.
- Adopted timeout policy `r2` after 60/120-second diagnostics: preserve common 10-second primary and all reference-slow overrides, use a common 120-second confirmation floor, and assign 180-second confirmation to `HumanEval/38`, `/50`, and `/53` because their pinned EvalPlus internal bound is 126 seconds. The exact `r1` policy remains archived under its original SHA-256.
- Active-policy validation matches all 5,031 accepted observations, 16 primary overrides, and three confirmation overrides. Full repository formatting, lint, strict typing, schema freshness, and all 131 tests pass.
- Pilot review schema `v3` traces every primary timeout through its confirmation, including cases that ultimately pass or fail, with exact timeout/elapsed values and immutable evaluator-record/raw-output paths.
- Adopted and implemented `DEC-20260804-26`: candidate extraction accepts exactly one complete Python fence with optional surrounding prose; Critique/Plan accept non-empty mixed text and may use focused code snippets while their prompts prohibit complete revised solutions. Draft3 hashes are frozen for the replacement pilot, all 133 tests pass, and four-tokenizer context validation covers all 1,677 public tasks with a 2,456-token tightest remaining margin.
- Adopted `DEC-20260804-28`: removed StarCoder2 from future scope, expanded the panel to six models including one general-purpose Gemma control, advanced the study to `study-v0.2.0`, and pinned exact revisions/snapshot sizes in `model-checkpoints-2026-08-04-r2`. Existing pilot and StarCoder2 artifacts remain immutable.
- Extended the durable downloader and independent validator to accept a manifest-pinned model subset while preserving order, exact remote revision/size checks, immutable attempts, and canonical-link refusal. This permits downloading only the three new snapshots without touching the retained snapshots; full repository validation passes all 136 tests.
- Completed and independently validated `models-20260804-r2-new-three`: all three exact revisions, 45 files, and 90,160,652,791 snapshot bytes passed terminal, manifest, size, and canonical-link checks. Remote/local manifest SHA-256 values are `2b1ca753144eb7f98a279b992fbb95dd3401990abf9e001d660ff5c2fd23dc6f` and `64a1f27fa82e65394d72847bb1e17c4dd2947ce774a91dabd05186318742d528`.

## Work in Progress

Corrected compatibility attempt `vllm-smoke-new-models-20260804-r2` passed all three new models under
unchanged vLLM 0.26.0 with canonical direct chat-template token IDs, 16K TP=2 batch invariance, exact
repeated responses/tokens, candidate-fence compliance, and complete GPU cleanup. It resolves
`ISSUE-20260804-07`; invalidated `r1` remains immutable. Current work freezes one six-model primary
configuration with exact tokenizer/processor/chat-template provenance and validates all prompt
context envelopes before the replacement pilot.

## Blockers

Primary execution is blocked until exact tokenizer/config provenance, common vLLM compatibility,
six-model context envelopes, and a replacement pilot pass.
`ISSUE-20260804-06` is resolved by the pre-primary model-scope change; candidate/intermediate format
issue `ISSUE-20260804-05` and timeout issue `ISSUE-20260804-04` remain resolved.

## Active Runs

No experiment run is active. Draft3 inference `run_856e8d87f7ed9bec7dec9a5c`, evaluation
`run_5b4f4a5a93f86c60a7efe19c`, and review report are terminal and preserved. Operational preparation
attempt `models-20260804-r2-new-three` is terminal and independently validated; it is not an
experiment run. Compatibility `r2` is terminal and validated, while invalidated `r1` remains
preserved. No GPU smoke is active at this documentation checkpoint. Primary has not started.

## Validated Data Available

Pilot validation data exist but no primary or paper-facing result exists. Every four-model pilot and
evaluation descendant remains immutable validation evidence and must not enter primary estimates.
All six primary-panel snapshots and the excluded historical StarCoder2 snapshot have independent
manifest/file integrity validation. Final accepted calibration inputs comprise
3,408 BigCodeBench, 489 HumanEval+, and 1,134 MBPP+ passing reference observations with zero anomalies.
Superseded partial audits remain preserved but are not calibration inputs.

Validated serving preparation includes vLLM 0.26.0, PyTorch 2.11.0+cu130, Transformers 5.14.1, CUDA 13.0 driver/runtime visibility, two RTX 4090 devices at compute capability 8.9, and exact 196-package lock SHA-256 `f1f66f8127dc916c576fd847d2478b1793b9a6443050c5f974104ec60a76092a`. The separate host compiler toolkit is CUDA 11.8 and cannot build FlashInfer 0.6.14 sampling JIT; validation therefore records vLLM's PyTorch-native sampler explicitly.

## Immediate Next Actions

1. Freeze and validate all six models under common 16K batch-invariant settings with exact tokenizer/processor/chat-template provenance and full prompt context envelopes.
2. Run one complete six-model runtime smoke using the frozen configuration and direct token-ID input.
3. Prepare and run the complete six-model replacement pilot, including Decision-format and output-limit review.
4. After the pilot passes, freeze primary prompt/parser/inference/campaign configurations and update the operator runbook for monitored full-scope execution.
