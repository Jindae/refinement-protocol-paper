# Project Status

## Last Updated

2026-08-08 (Asia/Seoul)

## Active Study Version

- Study design: `study-v0.4.0` single-call versus multi-call extension. Validated `study-v0.2.0` artifacts and
  execution path remain immutable formative/reference evidence.
- Data schema: `3.0.0` (`v1` and `v2` exports preserved; no pilot or primary records require migration)
- EvalPlus benchmark manifest: `evalplus-benchmarks-2026-08-04-r5` (163 included HumanEval+ tasks, 378 MBPP+ tasks, `self-refinement-isolated-v4`, unchanged tests/oracles, global 8 GiB candidate-process limit, and explicit per-input timeout attribution); exact `r4` bytes are archived
- BigCodeBench benchmark manifest: `bigcodebench-instruct-2026-08-03-r6` (1,136 included tasks, four pre-experiment exclusions, and isolated Python 3.10.12 `standalone-local-v3` adapter)
- Model manifest: `model-checkpoints-2026-08-04-r2` pins the adopted six-model panel; all six exact snapshots are downloaded and validated. The old four-model `r1` manifest and StarCoder2 snapshot remain historical evidence.
- 본실험 model-serving configuration: frozen `primary-inference-2026-08-04-r3` pins all six models under common `vllm-environment-2026-08-03-r1`, vLLM 0.26.0, TP=2, batch-invariant greedy decoding, direct chat-template token IDs, 16,384 context, and common stage output caps. Here `inference` names the serving configuration, not the Direct-only initial-candidate phase. Static provenance, full context validation, and all-six runtime smoke pass. Prior `primary-inference-2026-08-03-r2` remains four-model pilot history only.
- Candidate timeout configuration: `candidate-timeouts-2026-08-04-r2` (common 10-second primary; common `max(120 seconds, 1.5 × primary)` confirmation; 16 reference-only primary overrides; three predeclared 180-second HumanEval+ confirmation overrides; exact `r1` archived)
- Experiment configuration: enabled `role-separated-followup-2026-08-06-r1` uses all 1,677 tasks,
  the same six-model/inference settings, exact v0.2.0 source lineage, and only four replacement phases.
  Enabled `single-call-comparison-2026-08-07-r2` adds five model-resident conditions after its
  nine-task pilot passed review. `single-call-through-evaluation-2026-08-07-r2` runs full inference
  concurrently with independent role evaluation, then runs the dependent single-call evaluation.
  `model-campaign-2026-08-04-r2` remains for reproduction.
- Execution schedule: `phase-separated-resumable-2026-08-06-r1` (four separately durable attempts:
  Critique Generation, Critique-Conditioned Revision, Revision Planning, Plan-Conditioned Revision)
- Prompt set: frozen `role-separated-prompts-2026-08-06-r1`; Direct Generation, Decision, and Direct
  Revision reuse exact v3 bytes, while v4 C/P/CR/CPR roles are separated and CPR receives only Plan.
  The `prompts/v4/` directory also contains byte-identical copies of the three reused templates so it
  is a complete seven-template snapshot; the active frozen manifest retains the original v3 paths as
  immutable execution provenance. `single-call-prompts-2026-08-07-r1` and complete `prompts/v5/` add
  the five v0.4.0 conditions without changing v3/v4 bytes.
- Role contract: Critique does not presume an error and records no-problem when appropriate; Planning
  transforms stored Critique without a second independent review; CR acts on Critique; CPR implements
  Plan only; conditioned no-change paths reproduce the initial source; Decision is absent from all
  C/P/Revision prompts and is applied only when deriving final candidate selections.
- Pilot scope: `pilot-public-length-quantiles-2026-08-04-r2` (same exact 3 public-length positions per benchmark and 9 task IDs as historical `r1`, versioned under `study-v0.2.0` for all six models)
- Non-exact Decision response processing: primary rubric `decision-adjudication-2026-08-06-r2` retains free generation and strict parsing, separates deterministic terminal-period normalization from evaluation-result-free direction reading, and keeps `UNRESOLVED` available
- Analysis: accepted `primary-analysis-2026-08-08-r4` builds the complete 12-protocol v0.4.0 grid, applies the validated superseding remediation resolution, integrates pass rate with repair/regression balance in RQ1, assigns Decision conditioning to RQ2, topology to RQ3, and cost to RQ4, reports model-attributable malformed candidates as end-to-end zero, and keeps functional `FAIL`, TIMEOUT, and evaluator failure distinct.
- Exploratory follow-up: `mechanism-followup-2026-08-08-r3` validates task-set overlap, Decision
  mediation, empirical candidate reachability, and artifact-chain surface analyses without changing
  accepted RQ results. Option-A attempt `option-a-pilot-20260808-r1` failed before its first model
  call and remains excluded from paper-facing evidence. The Mapping-compatible correction and exact
  three-tokenizer preflight are validated; replacement attempt `option-a-pilot-20260808-r2` is
  running as registry run `run_e34fd10203b5a9e7009137cf`.

## Current Phase

The validated v0.2.0 inference `run_c99d3b1d562acc3e80026e48` supplies exact Initial Candidates,
Direct Revision candidates, Decisions, and their lineage. Its evaluation remains formative/reference
evidence. The v0.3.0 child inference `run_1dd46dd4a0ae265ab7a184a9` completed all four phases and
passed independent validation; its CR/CPR evaluation `run_1e4f588e7975f8b97a71400f` also validated
all 20,093 resolutions with zero evaluator failures. Full single-call inference
`run_5a4129eed4283cd222e2de9e` completed and passed validation, and its two-worker candidate
evaluation `run_7e4ee0647f99f8eb90c1aecd` also completed and validated 49,569 resolutions with
49,426 completed, 143 final timeouts, and zero evaluator failures. The full parent sequence passed.
Corrected v0.2.0 remediation `run_cfde994451c10e10b850905f` independently validated the sole prior
evaluator failure as functional `FAIL`; effective status counts are now 40,075 completed, 131 final
timeouts, and zero evaluator failures.

Final processed dataset `primary-final-v04-20260808-r5` and four-RQ analysis
`primary-final-four-rq-20260808-r3` are accepted. The dataset has 120,744 outcome rows and 120,656
selected paper-facing stage-call rows. RQ1–RQ4 outputs and paper assets of the same analysis
identifier are generated from the committed four-RQ implementation. Refreshed final package
`paper-writing-final-v04-20260808-r3` contains 107 validated files and 28,372,993 bytes with source
commit `1503e14`. It adds the validated post-hoc mechanism supplement and current Option-A failure
boundary without changing accepted RQ1–RQ4; raw evaluator and failed pilot responses remain excluded.
Package validation passed at manifest SHA-256
`0a6cda229913f0c09da4d1e2906f93398f6f2aaeac12966469006a68785ee499`. Findings and the complete
statistical/missingness contract are recorded in `documents/09_results_analysis.md`.
The accepted study remains in paper drafting. A separate post-hoc mechanism supplement is complete.
The first independently versioned option-A prompt-ablation attempt failed at 0/81 after model
warm-up and before generation. `ISSUE-20260808-22` records the tokenizer return-type defect and its
validated correction. The unique r2 replacement is running from commit `1503e14`; its immediate
handoff was 0/81 calls while loading DeepSeek-Coder-V2-Lite. Options B/C remain plan-only until
option-A inference, evaluation, and review are validated.

## Completed Work

- Created the Python 3.12 project structure and complete dependency lock.
- Added conservative exclusions for generated data, caches, model weights, secrets, and generated paper artifacts.
- Implemented canonical hashing and stable, domain-separated identifiers.
- Implemented typed version `3.0.0` records and committed JSON Schema exports while preserving `v1` and `v2`; `v3` adds an explicit model-call finish reason before any pilot data exists.
- Implemented a write-once local registry with raw-response integrity checks, resume reuse, explicit retries, and run-manifest lineage.
- Added a single validation command covering formatting, lint, strict typing, schema freshness, and tests.
- Adopted and implemented complete-case reading of non-exact Decision response directions without benchmark evaluation results, using a frozen rubric, separate typed provenance, `UNRESOLVED` protection, independent validation, D-protocol candidate-selection records, and processing-aware pilot review; the single pilot case resolved to `PRESERVE` without changing its invalid call.
- Repository validation passes formatting, lint, strict typing, schema freshness, and all 151 tests after the Decision-adjudication change.
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
- Adopted `DEC-20260803-17` and execution schedule `model-resident-all-benchmark-2026-08-03-r1`: each checkpoint normally loads once, then Direct Generation, Refinement-Need Decision, Direct Revision (`R`), Critique Generation, Critique-Conditioned Revision (`CR`), Revision Planning, and Plan-Conditioned Revision (`CPR`) each cover all 1,677 included tasks without benchmark-by-benchmark handoff. `DR`, `DCR`, and `DCPR` remain stored-artifact derivations with no model calls. Documentation consistency and all 73 repository tests passed through `./scripts/validate.sh`.
- Completed and independently validated `vllm-batch-invariance-probe-20260803-r1`: StarCoder2 produced two exactly identical 34-token responses under TP=2 batch-invariant mode, retained 6.84 maximum 16K concurrency, and cleaned both GPUs. `DEC-20260803-19` advances primary configuration to `r2` with batch invariance common to every model/stage; no pilot candidate exists under `r1`.
- Completed and independently validated `vllm-primary-smoke-20260803-r3`: all four checkpoints loaded with adopted primary `r2`, and each produced two exactly identical batch-invariant raw responses/token sequences. Terminal configuration/model-manifest provenance, result/summary hashes, 16K budgets, and post-run GPU cleanup passed; `ISSUE-20260803-09` is resolved.
- Implemented hash-pinned external prompt set `primary-prompts-2026-08-03-draft1`, exact stage-input enforcement, stable rendered/prompt hashes, one strict candidate extractor across Direct/`R`/`CR`/`CPR`, and strict Decision/critique/plan parsers. Four exact snapshot tokenizers validated all 1,677 public task specifications and conservative full-upstream-cap context envelopes; the tightest case was StarCoder2 CPR with 2,478 tokens remaining. `./scripts/validate.sh` passes all 89 tests.
- Implemented one common raw-first inference interface and resident vLLM adapter for all four checkpoints. It enforces frozen decoding, resident-model identity, stage-homogeneous batches, exact prompt budgets, per-call immutable raw/token/finish-reason records, malformed-output separation, and explicit overflow/backend/protocol failure records. Active schema `3.0.0` preserves `stop` versus `length`; `./scripts/validate.sh` passes all 99 tests.
- Implemented `ProtocolCampaignRunner` with the adopted seven-phase model-resident order, all-three-benchmark scope validation, task-level batching, immutable candidate/Decision/critique/plan builders, completed-call resume, crash-gap artifact recovery, aggregate/per-benchmark terminal counts, lineage validation, and derived-only `DR`/`DCR`/`DCPR`. Three-benchmark integration tests verify 21 independent calls, exact shared artifacts, 9 derived outcomes, zero-call resume, and task-local failure blocking; `./scripts/validate.sh` passes all 104 tests.
- Implemented the durable production campaign boundary: a Python 3.12 parent exports a hash-checked public-only scope and provenance records, launches one vLLM child per checkpoint sequentially, keeps each model resident across all seven phases, writes atomic batch-level status/count data, creates versioned run manifests, and supports explicit same-run resume through a new attempt. The full-scope configuration remains execution-gated while prompts are draft. A host-level preflight passed all 1,677 public tasks, four exact snapshots, Python 3.12.13, vLLM 0.26.0, 14.59 TB free disk, and two clear GPUs without loading a model or creating an experiment run.
- Froze public-only pilot scope `pilot-public-length-quantiles-2026-08-03-r1`: shortest, median, and longest included specification per benchmark, nine tasks total, with no hidden evaluator data used for selection. Host preflight passed the exact scope, all four snapshots, Python 3.12.13, vLLM 0.26.0, and two clear GPUs without loading weights.
- Implemented separate durable candidate evaluation with complete first-pass gating, frozen timeout assignment, timeout-only confirmation, final resolution, raw-output immutability, task-level resume, status/count monitoring, and independent validation. Added automated pilot review summaries and `EXPERIMENT_RUNBOOK.md` with copy-and-paste commands for pilot, resume, review, full-scope model-artifact generation, and candidate evaluation.
- Final repository validation passes formatting, lint, strict typing, schema freshness, and all 125 tests.
- Completed pilot inference `run_2ee6e3449b478af4e56a509f`: three models produced 189 completed calls, 108 candidates, 27 Decisions, and 81 derived outcomes; StarCoder2 produced nine immutable Direct extraction failures because every response added prose outside its Python fence.
- Completed and independently validated evaluation descendant `run_408b9ad39cdae36bacca33ae`: 108/108 resolutions, comprising 61 `PASS`, 42 functional `FAIL`, and five confirmed final `TIMEOUT` results with exactly one 1.5x confirmation each.
- Corrected the pilot review gate so schema-valid confirmed final timeout resolutions are reported for manual inspection rather than rejected as impossible; added regression coverage and explicit candidate paths.
- Generated corrected report `pilot-review-20260804-r2` (SHA-256 `36b009f7dbe3d5b9d8e11feb09650d2fe727776af1c516aa185ca72f44533d44`). Its automated gate is `review_required` because of the StarCoder2 extraction failures and dependent missing artifacts, not the five confirmed timeouts.
- Adopted `DEC-20260804-23` and created `primary-prompts-2026-08-04-draft2`: all four candidate-producing stages use the same stronger response-only fence wording for every model, while Decision/critique/plan bytes, strict parsers, public-only inputs, inference settings, and evaluation remain unchanged. The first pilot and draft1 configuration are preserved.
- Validated draft2 hashes, canonical input fields, and conservative 16K envelopes over all 1,677 public tasks with all four exact tokenizers. The tightest case remains StarCoder2 CPR, with 2,433 tokens free after reserving the full upstream/output caps and 64-token boundary margin.
- Resolved `ISSUE-20260804-03`: replacement preflight had hard-coded the draft1 prompt path. It now retains exact main-experiment serving/model checks while validating the versioned prompt selected by the campaign; the failed preflight created no attempt or artifact.
- Host-level clean-worktree preflight passed replacement campaign `pilot-campaign-2026-08-04-r2`: execution gate enabled, exact four models and nine-task scope, all configuration hashes, Python 3.12.13, vLLM 0.26.0, 14.59 TB free disk, and both GPUs clear at 15 MiB. No model was loaded and no run was created.
- Implemented a separate final-timeout diagnostic runner with explicit timeout, optional candidate filtering/per-candidate execution, exact task/source deduplication, immutable raw/results, foreground and durable background modes, compact monitoring, and independent validation. It never mutates or reclassifies the source evaluation run. Latest replacement-pilot evaluation preflight selects 10 final timeouts as four unique HumanEval+ task/source executions at a user-specified 60 seconds.
- Adopted timeout policy `r2` after 60/120-second diagnostics: preserve common 10-second primary and all reference-slow overrides, use a common 120-second confirmation floor, and assign 180-second confirmation to `HumanEval/38`, `/50`, and `/53` because their pinned EvalPlus internal bound is 126 seconds. The exact `r1` policy remains archived under its original SHA-256.
- Active-policy validation matches all 5,031 accepted observations, 16 primary overrides, and three confirmation overrides. Full repository formatting, lint, strict typing, schema freshness, and all 131 tests pass.
- Pilot review schema `v3` traces every primary timeout through its confirmation, including cases that ultimately pass or fail, with exact timeout/elapsed values and immutable evaluator-record/raw-output paths.
- Adopted and implemented `DEC-20260804-26`: candidate extraction accepts exactly one complete Python fence with optional surrounding prose; Critique/Plan accept non-empty mixed text and may use focused code snippets while their prompts prohibit complete revised solutions. Draft3 hashes are frozen for the replacement pilot, all 133 tests pass, and four-tokenizer context validation covers all 1,677 public tasks with a 2,456-token tightest remaining margin.
- Adopted `DEC-20260804-28`: removed StarCoder2 from future scope, expanded the panel to six models including one general-purpose Gemma control, advanced the study to `study-v0.2.0`, and pinned exact revisions/snapshot sizes in `model-checkpoints-2026-08-04-r2`. Existing pilot and StarCoder2 artifacts remain immutable.
- Extended the durable downloader and independent validator to accept a manifest-pinned model subset while preserving order, exact remote revision/size checks, immutable attempts, and canonical-link refusal. This permits downloading only the three new snapshots without touching the retained snapshots; full repository validation passes all 136 tests.
- Completed and independently validated `models-20260804-r2-new-three`: all three exact revisions, 45 files, and 90,160,652,791 snapshot bytes passed terminal, manifest, size, and canonical-link checks. Remote/local manifest SHA-256 values are `2b1ca753144eb7f98a279b992fbb95dd3401990abf9e001d660ff5c2fd23dc6f` and `64a1f27fa82e65394d72847bb1e17c4dd2947ce774a91dabd05186318742d528`.
- Completed and independently validated six-model replacement inference `campaign-pilot-six-models-20260804-r1`: 378/378 model calls and raw responses, all 216 Direct/`R`/`CR`/`CPR` candidates, 54 critiques, 54 plans, 53/54 Decisions, and 159/162 derived outcomes are present. The sole invalid Decision is preserved as `ISSUE-20260804-08`; no candidate-producing call failed.
- Scoped the evaluation launch cleanliness gate to committed execution inputs (`scripts/`, `src/`, `configs/`, project metadata, and evaluation dependency locks), consistent with the repository execution guidelines. Unrelated research notes no longer block evaluation launch; full validation passes all 145 tests.
- Completed six-model candidate evaluation `run_5b5b7b1dae795ad7f35db0da`: 216 primary attempts, 27 confirmations, 216 resolutions, and 243 raw outputs are internally complete, with 133 `PASS`, 77 functional `FAIL`, six confirmed `TIMEOUT`, and no evaluator failure. The run is invalidated as freeze evidence because all evaluation provenance incorrectly says `study-v0.1.6` (`ISSUE-20260804-11`); no record is repaired.
- Corrected pilot review's obsolete four-model expectation (`ISSUE-20260804-09`) and generated immutable six-model report `pilot-review-six-models-20260804-r2`. Representative model-stage raw review passed the adopted candidate and mixed-text contracts; the gate now blocks only on `ISSUE-20260804-08`.
- Corrected completed evaluation monitoring to distinguish 27 primary timeouts from six final timeouts (`ISSUE-20260804-10`). The 27 confirmations resolve to 20 `FAIL`, one `PASS`, and six final `TIMEOUT`; the six are all `HumanEval/129` internal `CandidateTimeout` outcomes near 65 seconds.
- Completed and independently validated corrected-provenance evaluation `run_286f0e7dc35e0e66fe23e95d`: 216 primary attempts, 11 confirmations, 216 resolutions, 227 raw outputs, 132 `PASS`, 78 `FAIL`, six final `TIMEOUT`, zero evaluator failures, and exact `study-v0.2.0` lineage. Decision-processing-aware review `pilot-review-six-models-20260804-r3` passed its automated count/artifact gate with 53 exact plus one separately read Decision and 159 original plus three added D-protocol candidate-selection records.
- Diagnosed `ISSUE-20260804-12` after exact-candidate cross-run comparison found one Qwen3 `HumanEval/129` Direct result changing from `PASS` to `FAIL`. EvalPlus 0.3.1 discards per-input timeout cause into a false detail. Adapter `self-refinement-isolated-v4` now records timed-out indexes, maps only timeout-explained false details to `TIMEOUT`, preserves conclusive non-timeout failures, and is covered by synthetic regression tests without changing benchmark data or oracle.
- Full repository validation passes formatting, lint, strict typing, schema freshness, and all 153 tests under adapter `v4`. Direct representative EvalPlus validation still reports reference `PASS` and intentionally incorrect `FAIL` for both HumanEval+ and MBPP+; replacement evaluation preflight resolves 216 candidates, the validated Decision adjudication, EvalPlus manifest `r5`, BigCodeBench manifest `r6`, and both exact manifest hashes.
- Completed and independently validated adapter-v4 evaluation `run_38cf240201dfb892765eccc2`: 216 primary attempts, 11 confirmations, 216 resolutions, 227 raw outputs, 133 `PASS`, 78 `FAIL`, five final `TIMEOUT`, zero evaluator failures, exact evaluator manifest hashes, and source-matching `study-v0.2.0` provenance.
- Generated final review `pilot-review-six-models-20260804-r4` (SHA-256 `f2cdf64bc9ccc30cdd3548c3538a395a72fe68b4ccb63498877ed7d0f5997c26`). Automated counts and lineage pass with no blocking reason; the unchanged representative raw-response set retains its completed manual review, and all new timeout raw traces were directly inspected.
- Adopted `DEC-20260804-31`, froze the reviewed prompt bytes as `primary-prompts-2026-08-04-r1`, and created enabled full-scope campaign `model-campaign-2026-08-04-r2`. Exact frozen manifest SHA-256 values and copy-and-paste primary execution/adjudication/evaluation commands are recorded in the decision log and `EXPERIMENT_RUNBOOK.md`.
- Canonical operator-facing phase names are Direct Generation, Refinement-Need Decision, Direct Revision, Critique Generation, Critique-Conditioned Revision, Revision Planning, and Plan-Conditioned Revision. `R`, `CR`, and `CPR` identify candidate conditions/protocol paths rather than phases. A separate read-only operator monitor maps the unchanged status machine identifiers to the full phase names without entering the experiment execution path.
- Full repository validation passes formatting, lint, strict typing, schema freshness, and all 158 tests after adding the read-only canonical phase monitor. The active campaign's model-worker source files remain byte-identical to its recorded commit `8a04c51`.
- Host-level full-scope preflight at commit `a5eaf7e` passed `model-campaign-2026-08-04-r2`: 1,677 tasks, six exact snapshots, frozen configuration/prompt hashes, Python 3.12.13, vLLM 0.26.0, 14.50 TB free disk, and two GPUs at 15 MiB each. No model was loaded and no run was created.
- Implemented the versioned raw-to-processed and RQ1–RQ4 analysis pipeline under `analysis_tools/` without changing active campaign execution inputs. It preserves a complete outcome grid, nonfunctional missingness, Decision provenance, actual-versus-implied token cost, deterministic paired statistics, common-case Pareto analysis, immutable manifests, and direct-script validation. Seven focused tests pass, and an accepted-pilot structural smoke generated and independently validated 378 outcome rows, 378 stage-call rows, and all four RQ output families under `/tmp`; no pilot number is promoted as a result.
- Full repository validation after the analysis freeze passes formatting, lint, existing strict typing, schema freshness, and all 165 tests. A separate strict mypy check of all nine analysis/tooling test source files also passes with no issues.
- Implemented a recurring paper-writing snapshot exporter under versioned inclusion profiles. Author
  review rejected completed but independently unvalidated full-registry snapshot `r1` as too broad.
  Compact profile `r2` instead writes one provenance/token CSV for all model calls, one JSONL per parsed
  artifact type, raw bytes only for model-format exceptions, compact Decision/timing/process evidence,
  explicit unavailable-result placeholders, lineage, hashes, and an independent validation record.
  Ordinary raw responses, benchmark bytes, repository tar, full work history, and active evaluation raw
  data are excluded; exact working-source paths and hashes remain traceable.
- Completed and independently validated compact pre-results snapshot
  `paper-writing-pre-results-20260806-r2`: 350 files, 227,397,605 manifest bytes, 70,386 call inventory
  rows, 101,405 consolidated parsed artifacts, 220 model-format-exception raw responses, 202 non-exact
  Decision direction records, and 605 added D-protocol candidate selections. It contains no tar archive,
  active evaluation raw data, outcome-processed dataset, RQ result, table, or figure. The first validator
  invocation exposed only an implementation assumption about the Decision record ID field and wrote no
  validation artifact; corrected schema-aware validation passed without changing the package.
- Published that validated compact snapshot directly at the Git-tracked `paper_writing_package/`
  root. Its README, seven content sections, manifest, checksums, and validation are immediately visible
  without a package-ID or `latest` wrapper directory. Future exports build inside their durable attempt
  and replace the root only after independent validation. Rejected r1 retains small attempt metadata and
  review evidence; its 683 MiB derived package copy was retired without modifying immutable source data.
- Resolved the stable-root tooling boundary found by the first post-publication check: repository Ruff
  traversal is explicitly excluded from the validated package tree, preventing nested cache creation or
  formatter scope drift. The unlisted cache contained no research data and was removed before commit;
  repository and direct package validation are both required completion gates.
- Implemented and froze the v0.3.0 role-separated prompt/configuration/runner path. Existing v0.2.0
  inputs remain reproducible; the new runner reads exact Initial Candidates from the validated parent,
  writes new records to a child registry, gives C/CR/P/CPR separate durable attempts, advances them
  automatically, and supports phase-only retry. Formatting, Ruff, strict mypy, schema freshness, and
  all 187 tests pass.
- Generated, independently validated, and published authoring snapshot
  `paper-writing-v03-progress-20260807-r3` from committed source `5baaab8`. Its 366 files and
  143,053,140 manifest bytes contain 50,278 selected paper-facing call rows, 61,609 parsed artifacts,
  and 225 exactly covered format-exception raw responses. It includes only reused Direct/Decision/`R`
  plus validated v0.3.0 Critique/`CR`; active Plan/`CPR`, unvalidated evaluation records, provisional
  RQ outputs, tables, and figures are explicitly unavailable. Stable-root and attempt validation both
  pass at manifest SHA-256 `82d0207e7eff3f7f5a447afcbb6fd8be3011112ea0b903b4faecd1396d2bb58a`.
- Generated, independently validated, and published planning-inclusive authoring snapshot
  `paper-writing-v03-progress-20260807-r4` from committed source `e87fab8`. Its 369 files and
  169,810,587 manifest bytes contain 60,332 selected call rows, 71,663 parsed artifacts, and 225
  selected raw format exceptions. It adds the validated v0.3.0 Planning phase and the revised
  planning/background writing guidance while excluding active CPR, unvalidated evaluation records,
  processed RQs, tables, and figures. Attempt and stable-root validation both pass at manifest
  SHA-256 `ef87de171b7509665ac1a5b3a39ffb0f7b2afcd20e70d2cfc6b34b59eb91f1a3`.

## Final Analysis State

All experiment, remediation, composite-data, and RQ analysis gates are complete. Accepted outputs
are `primary-final-v04-20260808-r5` (processed data), `primary-final-four-rq-20260808-r3`
(RQ1–RQ4), and paper assets `primary-final-four-rq-20260808-r3`. The preceding five-RQ output is
retained as immutable history but superseded for paper reporting. The remaining work is paper
drafting and optional rendered-figure design from the validated CSV inputs.

`DEC-20260807-41` added five single-call conditions as a prospective call-topology axis and then moved
cost-effectiveness to RQ5. Reporting decision `DEC-20260808-49` subsequently merges the former RQ1
and RQ2 and renumbers topology and cost to RQ3 and RQ4 without changing any experiment or estimand.
The complete v5 prompts, typed code/Decision parsing, model-resident
five-condition runner, nine-task pilot configuration, and two-worker evaluation path are implemented.
Pilot attempt `single-call-pilot-20260807-r1` completed and independently validated all 270 calls,
with 266 parsed candidates, zero invalid integrated Decision labels, and four explicit multiple-fence
model-format failures. `DEC-20260807-42` accepts that evidence without changing the prompt, parser, or
retry policy and enables the full gate. One durable supervisor now runs and validates full v0.4.0
single-call inference concurrently with completed v0.3.0 role-separated candidate evaluation at two
workers, then evaluates the new v0.4.0 candidates with two workers after both branches validate.

The v0.2.0 provisional analysis exposed construct overlap: broad Critique already contained much of
Planning's role and CPR Revision received both artifacts. Those results are retained but will not be
the paper-facing CR/CPR estimate. The frozen v0.3.0 prompts assign diagnosis to Critique, change method
to Planning, and code execution to Revision; CR receives Critique while CPR receives Plan only.

Primary Decision response processing `decision-adjudication-primary-20260806-r1` is complete and
independently validated: 156 deterministic terminal-period normalizations, 46 evaluation-result-free
readings of non-exact response directions (44 `REFINE`, two `PRESERVE`), zero unresolved, and 605
D-protocol candidate-selection records constructed from resolved Decisions. Analysis version
`primary-analysis-2026-08-06-r2` is committed. Separate evaluation of all 40,206 existing v0.2.0
candidates exited after 387 deferred confirmations. Its stored resolution counts are 40,074 completed,
131 final timeouts, and one evaluator failure. Corrected remediation `r4` preserves those source
records and adds an independently validated superseding resolution; the effective view is 40,075
completed, 131 final timeouts, and zero evaluator failures. A non-paper-facing full-scope
snapshot path prepared and validated RQ1–RQ4 from
only the evaluation attempts present at one capture time while retaining pending confirmations as
indeterminate. These snapshots are historical and are superseded by the terminal validated final
dataset and accepted four-RQ results named above.
The first committed-code provisional build exceeded one managed foreground execution slice after one
168 MB JSONL file; no application memory error was established. `ISSUE-20260806-18` replaced its
avoidable full-output byte duplication with streaming atomic writes. Fresh snapshot
`primary-provisional-20260806t121946z-r2` captured 40,206 primary and 45 confirmation records, retained
342 pending confirmations, and passed its complete-grid/file/record-hash validation. All four outputs
under `primary-provisional-analysis-20260806t121946z-r2` independently validate and remain explicitly
non-paper-facing. Reporting-only successor `primary-provisional-analysis-20260806t121946z-r3` uses
the same frozen snapshot and adds the predeclared RQ3 repair/regression decomposition: pooled
all-resolved `R→DR` loses 31 repairs and prevents 18 regressions, `CR→DCR` loses 180 and prevents
605, and `CPR→DCPR` loses 195 and prevents 919. Its RQ1–RQ4 outputs and consolidated review all
validate. No experiment record was written or changed.

Role-separated evaluation `evaluation-role-separated-primary-20260807-r1` completed and independently
validated 20,093 CR/CPR resolutions plus 221 confirmation attempts. Final statuses are 20,025
completed, 68 timeout, and zero evaluator failures. Full single-call inference and its dependent
two-worker evaluation also completed and validated; the latter has 49,426 completed resolutions,
143 final timeouts, and zero evaluator failures.

The user adopted `DEC-20260807-44` for the isolated v0.2.0 evaluator failure and explicitly permitted
one concurrent attempt under `DEC-20260807-45`. Attempt
`evaluation-remediation-v02-20260807-r1` completed and independently validated, but remains
`unresolved`: the managed sandbox denied a required netlink socket after 1.758 seconds, producing
empty evaluator stdout and no functional outcome. This differs from the original memory error and
does not test the transient-load hypothesis. `DEC-20260807-46` therefore authorizes an immutable
host-context `r2` linked to `r1`. That attempt started the evaluator correctly but reproduced
`OSError: [Errno 12] Cannot allocate memory` after 33.380 seconds and independently validated as
`unresolved`. Preflight recorded about 96.6 GB available host memory, so total host exhaustion is not
established. Full formatting, lint, strict typing, schema-export validation, and all 202 repository
tests pass.

After the full evaluation released all workers, isolated remediation
`evaluation-remediation-v02-20260808-r3` ran with no concurrency override and about 104.3 GB memory
available. It reproduced the same `ENOMEM` at the worker-owned `/tmp/bigcodebench-*` creation step
after 26.170 seconds and independently validated as `unresolved`. Candidate and hidden-test code do
not create that path, but a later separate host `screen` diagnostic corrected the interpretation of
the traceback: the exact task reference passed 5/5 in 0.264 seconds under the same sandbox and
limits, while the candidate repeatedly concatenates non-empty mocked `recv` data until memory
exhaustion. `TemporaryDirectory` cleanup then raises `ENOMEM` on the same path and masks the already
collected unittest result. Concurrent evaluator load and directory creation are not the cause.

`DEC-20260808-48` therefore adds a remediation-only cleanup policy that ignores errors while removing
the disposable worker tmpfs. Candidate and hidden-test bytes, the 120-second timeout, 30 GiB address
space limit, network isolation, and the default evaluator path remain unchanged. Focused regression
tests pass. Corrected host-screen attempt `evaluation-remediation-v02-20260808-r4` completed the retry
as functional `FAIL` in 26.673 seconds and independently validated as `resolved`. Its immutable run is
`run_cfde994451c10e10b850905f`; effective counts are 40,075 completed, 131 timeout, and zero evaluator
failures.

## Blockers

None for final result analysis. The full inference-through-evaluation sequence, twelve-protocol
processed dataset, RQ1–RQ4 analysis, and paper-ready CSV assets are complete and validated.

## Active Runs

Model-artifact run `run_c99d3b1d562acc3e80026e48` is completed and validated under durable attempt
`campaign-primary-20260804T104734Z`. It records commit `8a04c51`, six models, 1,677 tasks, and 70,434
planned task-phase units. Candidate evaluation `evaluation-full-candidates-20260806-r1` exited as
evaluation run `run_b25b1ec137928799f30217af`, with 40,206 primary attempts and resolutions, but its
source status and records remain immutable. Its one captured BigCodeBench/1042 confirmation retains
the original evaluator `ENOMEM`; resolved remediation `run_cfde994451c10e10b850905f` supplies the
separately validated superseding functional `FAIL`. The effective reference view uses that explicit
lineage rather than relabeling the source record and has no evaluator failures.
Accepted pilot evidence remains inference `run_4b0bdec98ae531232cfe9f30`,
adjudication `run_387a281ce89a3147e1d4b0da`, evaluation `run_38cf240201dfb892765eccc2`, and review
`pilot-review-six-models-20260804-r4`. Invalidated prior evaluations and reviews remain immutable.

Role-separated sequence `role-sequence-primary-20260806-r1` completed and independently validated as
child inference `run_1dd46dd4a0ae265ab7a184a9`. It contains 40,216 calls, 10,054 Critiques, 10,040
Critique-Conditioned Revision candidates, 10,054 Plans, and 10,053 Plan-Conditioned Revision
candidates. Its terminal validation hash is
`5cd6c4bad0ed60c9aeecddc77b2971a04ad2adf7be7207b19d62c987c532dd81`.

Single-call pilot `single-call-pilot-20260807-r1` completed and passed independent validation as run
`run_b7b3feb52ce8f9e98df3fcfa`. The approved validation hash is
`0cd515db553b7bfee723b6a06b744345f5afc3588adb3d8fea8671ae5d6bd31e`.

Role-separated evaluation `evaluation-role-separated-primary-20260807-r1` completed and validated as
`run_1e4f588e7975f8b97a71400f`. Full single-call inference
`run_5a4129eed4283cd222e2de9e` and evaluation `run_7e4ee0647f99f8eb90c1aecd` also validated;
parent sequence `single-call-sequence-primary-20260807-r2` is terminal and passed. No evaluation is
active. Remediation run
`run_81f775bdba8796358ce73b4d` is terminal, independently validated, and unresolved because its
managed sandbox prevented evaluator startup. Host replacement `run_3b69aaca71b22ef25fd62d9b` is also
terminal, independently validated, and unresolved after reproducing the original memory error class.
Isolated successor `run_218265fd6821b56de3e6753b` is likewise validated and unresolved after the
same worker-setup failure with no concurrent evaluator; none is an accepted result replacement.

## Validated Data Available

Validated primary inference, role-separated inference/evaluation, and single-call inference data,
the complete twelve-protocol processed dataset, and four paper-facing RQ outputs now exist.
The primary run contains 70,386 calls/raw responses and 40,206 candidate artifacts. Pilot
validation data remain separate. The six-model replacement
inference contributes 378 validated model calls/raw responses and 216 candidates; its isolated
Decision noncompliance remains explicit and separately adjudicated. Adapter-v4 evaluation `r3` is the
accepted final pilot evaluation. Every earlier six-model evaluation and every four-model pilot
descendant remains immutable validation evidence and must not enter primary estimates.
All six primary-panel snapshots and the excluded historical StarCoder2 snapshot have independent
manifest/file integrity validation. Final accepted calibration inputs comprise
3,408 BigCodeBench, 489 HumanEval+, and 1,134 MBPP+ passing reference observations with zero anomalies.
Superseded partial audits remain preserved but are not calibration inputs.

Validated serving preparation includes vLLM 0.26.0, PyTorch 2.11.0+cu130, Transformers 5.14.1, CUDA 13.0 driver/runtime visibility, two RTX 4090 devices at compute capability 8.9, and exact 196-package lock SHA-256 `f1f66f8127dc916c576fd847d2478b1793b9a6443050c5f974104ec60a76092a`. The separate host compiler toolkit is CUDA 11.8 and cannot build FlashInfer 0.6.14 sampling JIT; validation therefore records vLLM's PyTorch-native sampler explicitly.

## Immediate Next Actions

1. Launch, monitor, independently validate, and evaluate option-A pilot outputs.
2. Review option-A results before deciding whether to instantiate option B or C.
3. Continue paper drafting from accepted v0.4.0 outputs without mixing exploratory estimates.
4. Build the separate public replication package when redistribution scope is decided.
