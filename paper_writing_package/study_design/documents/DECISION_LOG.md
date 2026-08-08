# Decision Log

## DEC-20260802-01: Versioned typed records and append-only local storage

- Date: 2026-08-02
- Status: Adopted
- Context: The repository foundation requires auditable schemas, stable provenance, immutable raw responses, resumability, and traceable reruns before inference or benchmark execution begins.
- Decision: Use frozen Pydantic models with schema version `1.0.0`, committed JSON Schema exports, exact UTF-8 or canonical-JSON SHA-256 hashes, domain-separated stable identifiers, and a filesystem registry that never replaces conflicting raw or record bytes. Run status changes use linked manifest revisions. A normal resume reuses one completed logical call; a retry or deliberate rerun creates a linked attempt.
- Rationale: The approach is small enough to audit locally while enforcing the shared-initial, exact-preservation, token-accounting, failure-separation, and supersession constraints at validation and storage boundaries.
- Alternatives considered: Standard-library dataclasses with hand-maintained validation; a mutable SQLite registry; overwrite-in-place JSON manifests. Dataclasses would duplicate schema and validation machinery, while mutable stores and manifests would make raw-history preservation less explicit at this phase.
- Consequences: Schema changes require versioning and regenerated schema files. Callers must store returned raw bytes before constructing a completed or parseable model-call record. Multiple completed records for one logical call are treated as a registry conflict rather than silently selected.
- Affected files/configurations/runs: `pyproject.toml`, `requirements.lock`, `schemas/v1/`, `src/self_refinement/hashing.py`, `src/self_refinement/identifiers.py`, `src/self_refinement/schemas/`, `src/self_refinement/storage/`, and related tests. No experiment runs are affected.
- Supersedes or superseded by: None.

## DEC-20260802-02: Pinned EvalPlus releases and namespace-isolated evaluation

- Date: 2026-08-02
- Status: Adopted
- Context: HumanEval+ and MBPP+ preparation requires reproducible task loading and safe separation between prompt-visible specifications and hidden tests. The pinned MBPP+ release also represents the absent additional tests for `Mbpp/793` as an empty JSON object rather than a list.
- Decision: Use EvalPlus `0.3.1`, HumanEval+ `v0.1.10`, and MBPP+ `v0.2.0`; verify downloaded gzip bytes against committed SHA-256 values; expose task specifications through a public typed object while retaining oracle data in a separate evaluation-only object; and execute candidate code in a network namespace and minimal read-only bubblewrap filesystem with process, memory, per-test, and parent wall limits. Normalize only the official empty `plus_input` object for `Mbpp/793` to an empty input sequence, matching EvalPlus iteration behavior.
- Rationale: Version and content pins prevent upstream changes from silently altering the task set. The typed boundary makes accidental prompt leakage harder. Namespace isolation adds a security boundary beyond EvalPlus's documented reliability guard, while explicit timeout and evaluator-failure states preserve the study's distinction from functional `FAIL`.
- Alternatives considered: Let EvalPlus download mutable defaults into its user cache; store tests and specifications in one general task object; execute EvalPlus directly in the main process; reject `Mbpp/793`; or silently coerce arbitrary mappings to input lists. These alternatives weaken reproducibility, prompt isolation, execution containment, task completeness, or parser strictness.
- Consequences: Linux `unshare` and `bubblewrap` are required for evaluation. Dataset files remain ignored and must be fetched with the committed script. A host that disables unprivileged user or network namespaces cannot evaluate candidates until an equivalent sandbox backend is configured. `Mbpp/793` remains included and has no additional plus inputs, as in the pinned release.
- Affected files/configurations/runs: `configs/benchmarks/evalplus.toml`, `pyproject.toml`, `requirements.lock`, `scripts/fetch_evalplus_data.py`, `scripts/validate_evalplus.py`, `src/self_refinement/benchmarks/`, `src/self_refinement/evaluation/`, and related tests. No experiment runs are affected.
- Supersedes or superseded by: None.

## DEC-20260802-03: BigCodeBench Python 3.12 evaluation environment strategy

- Date: 2026-08-02
- Status: Adopted
- Context: BigCodeBench `0.2.5` uses dataset `v0.1.4`, but its official local-evaluation Dockerfile uses Python 3.10 and its tagged evaluation requirements pin NumPy `1.21.2` and Numba `0.55.0`, both of which require Python `<3.11`; TensorFlow `2.11.0` also has no Python 3.12 wheel. The adopted study requires Python 3.12. Installing modern substitutes could alter numerical, plotting, ML, or library-specific test behavior, so this is not a routine implementation preference.
- Decision: Keep experiment orchestration, model inference, artifact storage, analysis, and EvalPlus evaluation on the primary Python 3.12 environment. Execute only BigCodeBench candidate code and hidden tests in a separately pinned Python 3.10.12 environment matching the upstream local evaluator dependency range. Isolate that environment from network and host process namespaces; pass only the task identifier, exact candidate source, hidden test source, declared dependencies, and resource limits into the evaluation worker. Never return evaluator results or diagnostics to a model call.
- Rationale: This preserves the Python 3.12 environment already validated for the study infrastructure and inference stack while avoiding outcome-changing substitutions for BigCodeBench's older scientific and ML dependencies. Because every candidate condition for a task uses the same benchmark-specific evaluator environment, the interpreter split is not a protocol-level treatment. It also more closely follows the upstream BigCodeBench local evaluation environment than modernizing its dependencies under Python 3.12.
- Alternatives considered: (A) preserve Python 3.12 and create a separately locked set of closest compatible library versions, then require all included canonical solutions to pass repeated validation; (B) adopt a narrowly scoped Python 3.10 exception for the BigCodeBench evaluator and reproduce the official pinned environment; (C) use the official remote evaluator, accepting external-service and environment-opacity risks; (D) remove BigCodeBench-Instruct from scope, changing benchmark coverage.
- Consequences: The project has two explicitly versioned runtime environments and must record the benchmark-specific environment identifier on every evaluation. The Python 3.10.12 package lock and system dependencies must be preserved for long-term replication because Python 3.10 reaches upstream end of life in October 2026. BigCodeBench validation and task-exclusion freezing remain pending until representative and full-reference checks pass in the completed environment. Raw correctness should not be interpreted across benchmarks without acknowledging their official-compatible evaluator environments.
- Affected files/configurations/runs: `documents/04_experiment_plan.md`, `documents/05_models_and_benchmarks.md`, `configs/benchmarks/bigcodebench.toml`, `src/self_refinement/benchmarks/bigcodebench.py`, `src/self_refinement/evaluation/bigcodebench.py`, `scripts/setup_bigcodebench_eval_env.py`, `scripts/validate_bigcodebench.py`, `TASKS.md`, and `ISSUE-20260802-02`. Study design advances from `study-v0.1.0` to `study-v0.1.1`; no experiment runs exist or require invalidation.
- Supersedes or superseded by: None.

## DEC-20260802-04: Durable attempt protocol for long-running background jobs

- Date: 2026-08-02
- Status: Adopted
- Context: Dependency installation and source builds exposed recurring operational ambiguity: temporary status paths could disappear, persisted `running` state lacked live progress, managed command sandboxes could hide host PIDs, and a launcher could report success without proving detached-process survival. The project will run many long model, evaluation, download, and analysis jobs, so one-off fixes are insufficient.
- Decision: Require every potentially long-running job to follow the repository-level `AGENTS.md` protocol: unique immutable attempt directories under `runs/logs/`, status creation before launch, atomic state updates, durable stdout/stderr logs, verified detached execution, PID-namespace-aware liveness checks, explicit user monitoring commands, terminal-state metadata, output validation, and new linked attempts for retries. Do not use `/tmp` for required status, do not wait with `sleep` or polling loops, and do not treat process exit as validated completion.
- Rationale: A common lifecycle makes progress observable across reboots and agent sessions, prevents false stopped/running diagnoses, preserves evidence for failures, and keeps reruns auditable without coupling the implementation to one benchmark or installer.
- Alternatives considered: Continue adding job-specific monitoring fixes; rely on terminal multiplexers without machine-readable status; run all commands in the foreground; use `/tmp` marker files. These approaches do not provide consistent recovery, provenance, or agent handoff.
- Consequences: Launchers require more preflight and metadata, but long-running work becomes resumable and diagnosable. Existing job-specific scripts should be brought into conformance when touched. Experiment runs retain their additional manifest and operational-document requirements.
- Affected files/configurations/runs: `AGENTS.md`, `CODEX_CONTINUATION_PROMPT.md`, `README.md`, `TASKS.md`, and long-running scripts. No experiment runs are affected.
- Supersedes or superseded by: None.

## DEC-20260802-05: Separate BigCodeBench evaluator provenance from package installation

- Date: 2026-08-02
- Status: Adopted
- Context: The first isolated Python 3.10.12 environment attempt installed the official BigCodeBench `0.2.5` wheel with `--no-deps` plus the tagged evaluation requirements. All evaluation requirements installed successfully, but `pip check` failed because the wheel metadata also declares model generation, serving, and remote-API clients such as vLLM, Transformers, OpenAI, and Anthropic as mandatory dependencies. The repository's standalone local evaluation worker imports none of the BigCodeBench package.
- Decision: Continue to download and SHA-256 verify the pinned official wheel as evaluator provenance, but do not install the distribution into the candidate-execution environment. Install and validate the exact tagged `Requirements/requirements-eval.txt` set used for task execution, and record the standalone adapter identity, wheel hash, requirements hash, full package freeze, and package-installation policy in versioned configuration and attempt provenance.
- Rationale: This keeps the actual candidate execution dependency set faithful and auditable without adding unused inference engines, GPU stacks, or remote-service clients that increase conflicts and attack surface. It also lets `pip check` detect genuine inconsistencies among the packages that candidate tests can import.
- Alternatives considered: Install every package dependency declared by BigCodeBench, including vLLM and remote clients; retain the package but ignore a failing `pip check`; or remove wheel provenance entirely. The first expands and may destabilize the evaluator environment, the second masks real dependency problems, and the third weakens reproducibility evidence.
- Consequences: The environment is an official-requirements-compatible standalone execution adapter rather than an installation of the BigCodeBench CLI package. Any future adapter change requires a new adapter and manifest version. The failed setup attempt remains preserved and the corrected setup uses a linked new attempt.
- Affected files/configurations/runs: `configs/benchmarks/bigcodebench.toml` revision `bigcodebench-instruct-2026-08-02-r4`, `requirements-bigcodebench.lock`, `src/self_refinement/benchmarks/bigcodebench.py`, `scripts/setup_bigcodebench_eval_env.py`, setup tests, `README.md`, `TASKS.md`, `PROJECT_STATUS.md`, and `ISSUE-20260802-03`. Setup attempt `setup-20260802T134237531534Z` failed and linked attempt `setup-20260802T140114502890Z` completed; no experiment run or result is affected.
- Supersedes or superseded by: None.

## DEC-20260802-06: Operational threshold for background jobs

- Date: 2026-08-02
- Status: Adopted
- Context: Applying the durable background protocol to a representative validation that completed in 28 seconds added unnecessary launcher code and required the user to report a terminal state. The durable protocol remains necessary for genuinely large work, but a one-minute threshold was too aggressive for normal repository validation.
- Decision: Execute work expected to finish within five minutes directly and confirm its result in the same turn. For predictable work between five and ten minutes, prefer direct execution when same-turn results are useful. Use durable background attempts for work likely to take at least ten minutes, work with a realistic chance of exceeding that duration, or work that must survive the current session. Large experiments remain subject to their run-manifest requirements independently of execution duration.
- Rationale: The threshold avoids operational overhead and repeated user handoffs for ordinary checks while preserving durable monitoring, resumability, and evidence for genuinely long or interruption-sensitive jobs.
- Alternatives considered: Keep the one-minute threshold; use five minutes as a hard background cutoff; or make every command discretionary without a baseline. These respectively overproduce launchers, remain too aggressive for bounded checks, or make behavior inconsistent across sessions.
- Consequences: Unit tests, representative smoke checks, and similar bounded validations normally complete in the foreground. Ten-minute-plus jobs use the immutable status/log protocol. Work in the intermediate range requires a concrete runtime and interruption-risk judgment rather than automatic backgrounding.
- Affected files/configurations/runs: `AGENTS.md` and future operational execution. No experiment run, benchmark result, configuration, or study design is affected.
- Supersedes or superseded by: Refines the duration boundary of `DEC-20260802-04`; all other requirements of that decision remain active.

## DEC-20260802-07: Reference-calibrated two-stage candidate timeout policy

- Date: 2026-08-02
- Status: Adopted
- Context: A globally generous candidate timeout makes nonterminating or pathological generated code the evaluator bottleneck. For example, thirty candidates reaching a two-minute limit consume one hour even before useful evaluations are counted. A globally tight limit, however, can misclassify legitimately slow tasks unless it is grounded in the benchmark's reference behavior.
- Decision: Before model inference, run each official reference solution repeatedly in the exact benchmark evaluator environment and retain task-level end-to-end timing, evaluator-internal reference timing where available, variability, environment provenance, and failures. Freeze a common primary-timeout rule plus reference-evidence-based task overrides before the main experiment. Any candidate that reaches its primary timeout is evaluated exactly once more with a longer, separately frozen confirmation timeout. Use the confirmation functional outcome if it completes; classify final `TIMEOUT` only when both attempts time out. Store both attempts and never expose timing or evaluation information to a model call.
- Rationale: Reference-only calibration makes the fast path tight without adapting limits to any model or protocol outcome. A single longer confirmation prevents the optimization cutoff from becoming the final correctness boundary, while bounding worst-case retries and preserving paired fairness.
- Alternatives considered: One generous global timeout; one tight global timeout without confirmation; derive per-task limits from generated candidates; or retry timed-out candidates repeatedly. These respectively waste substantial time, risk false timeouts, make evaluation candidate-dependent, or create unbounded and potentially protocol-dependent evaluation cost.
- Consequences: Timeout configuration has a primary and confirmation stage, optional task overrides, and attempt lineage. The same task-level configuration applies to every model and protocol. Quantitative formulas and values remain intentionally unfrozen until the reference timing audits complete; no candidate evaluation for the experiment may begin before they are versioned. Evaluation schemas and runners must preserve both attempts and distinguish final timeout from infrastructure failure.
- Affected files/configurations/runs: `documents/04_experiment_plan.md`, `documents/05_models_and_benchmarks.md`, `configs/benchmarks/evalplus.toml` revision `evalplus-benchmarks-2026-08-02-r2`, `scripts/audit_reference_timings.py`, `src/self_refinement/auditing/reference_timings.py`, evaluator timing outputs, `TASKS.md`, and `PROJECT_STATUS.md`. Study design advances from `study-v0.1.1` to `study-v0.1.2`; no model inference or experiment runs exist or require invalidation.
- Supersedes or superseded by: None.

## DEC-20260803-08: Align and isolate the BigCodeBench worker

- Date: 2026-08-03
- Status: Adopted
- Context: In full audit `timing-bigcodebench-20260802-r1`, four official references that execute child processes produced `InvalidEvaluatorOutput` in all three repetitions. Their descendants inherited stdout and wrote archive listings or script output before the worker's JSON, corrupting the control protocol even though the tests had run. The existing Python-level output redirection does not affect subprocess file descriptors.
- Decision: Before executing candidate and test code, duplicate a result-only stdout descriptor that is not inherited by descendants. Redirect process-level stdout and stderr to a temporary sink during candidate execution, then write exactly one JSON record through the reserved descriptor. Retain bounded unittest failure and error traces in the raw evaluator response for evaluator-only diagnosis. Expose the pinned official container's `/bin` directory and minimal localhost resolver files read-only alongside the existing system-library bindings. In the isolated network namespace, bring up loopback for local client/server tests while leaving all external interfaces absent. Run the worker as fixed nonprivileged UID/GID 65534, make the synthetic root read-only after mount setup, and leave only its temporary filesystem writable, matching the official container's non-root execution semantics. Mark this behavior as `standalone-local-v2` in BigCodeBench manifest `bigcodebench-instruct-2026-08-03-r5`; evaluator raw output and diagnostics must never enter model prompts.
- Rationale: A dedicated descriptor makes framing unambiguous even when reference or generated code launches noisy subprocesses. It preserves functional execution while preventing candidate-controlled stdout from masquerading as evaluator metadata. Bounded raw traces make preparation defects diagnosable without weakening the prompt-visible hidden-test boundary.
- Alternatives considered: Parse the last stdout line as JSON; forbid or mock subprocess output; omit failure details; or keep the `v1` classification and exclude the four tasks. Last-line parsing remains ambiguous with leaked descendants, suppressing subprocess behavior changes the benchmark, omitting traces prevents reliable environment diagnosis, and exclusion would hide an implementation defect.
- Consequences: The `v1` audit remains immutable validation evidence but cannot be the final exact-environment timeout audit. After remaining anomaly causes are corrected, all BigCodeBench references require a new linked audit under the final adapter. No model inference or experiment result is affected because none has started.
- Affected files/configurations/runs: `configs/benchmarks/bigcodebench.toml`, `src/self_refinement/benchmarks/bigcodebench.py`, `src/self_refinement/evaluation/bigcodebench_worker.py`, `scripts/audit_reference_timings.py`, `scripts/diagnose_bigcodebench_references.py`, evaluator tests, `TASKS.md`, `PROJECT_STATUS.md`, and `ISSUE-20260803-01`. Validation-data audit `timing-bigcodebench-20260802-r1` used `standalone-local-v1` and remains partial for benchmark acceptance.
- Supersedes or superseded by: Refines the standalone adapter implementation adopted in `DEC-20260802-05`; the evaluator environment strategy in `DEC-20260802-03` is unchanged.

## DEC-20260803-09: BigCodeBench data-resource and live-network policy

- Date: 2026-08-03
- Status: Adopted
- Context: After all implementation-only corrections in `standalone-local-v2`, integrated diagnostic `diagnostic-20260803-r9-integrated-v2` makes 12 of the 35 formerly anomalous official references pass. Seventeen remaining references require NLTK/TextBlob data packages (`punkt`, `stopwords`, `words`, or `averaged_perceptron_tagger`) that are not installed by the pinned Python requirements or downloaded by the upstream `v0.2.5` Dockerfile. Six references (`BigCodeBench/101`, `/176`, `/314`, `/590`, `/1005`, and `/1012`) attempt DNS or external-service access. Follow-up evaluator-only diagnostic `network-feasibility-20260803-r1` ran every one of those official references three times with host networking: `/101`, `/176`, `/314`, and `/1012` passed 3/3, while `/590` and `/1005` failed 3/3 because their Python download clients received HTTP 403 responses. The six-task count therefore describes network-touching references, not six evidence-backed exclusions. Allowing generated candidates unrestricted internet access would still reduce reproducibility and expose external systems to untrusted code.
- Decision: Pin `punkt`, `stopwords`, `words`, and `averaged_perceptron_tagger` to `nltk_data` revision `550b6625bcef1f2abff2ff770a5a0d272c9c6b2a`; verify every archive SHA-256 and extracted regular-file tree SHA-256; and mount the validated tree read-only. Keep external networking disabled. Retain `/176` using checksum-pinned resolver entries and retain `/314` using a task-scoped TLS-handshake server that runs only inside its isolated network namespace. Pre-exclude `/101`, `/590`, `/1005`, and `/1012` with explicit external-content reasons before any model inference. Record the four exclusions in manifest `bigcodebench-instruct-2026-08-03-r6`, use only its 1,136 included tasks in final reference audits and experiments, and identify the resource-aware evaluator as `standalone-local-v3`.
- Rationale: The resolver and handshake fixtures preserve the APIs exercised by `/176` and `/314` without serving task content or granting egress. The other four tasks require third-party content downloads; retaining two more tasks would require substantially broader HTTP(S) response emulation for only 0.18% of the release. Four total exclusions remove 0.35% of the 1,140-task release and are fixed independently of every model and protocol outcome. Live-network success for some references establishes availability, not reproducibility, while repeated 403 failures show that egress alone is insufficient.
- Alternatives considered: (A) Retain `/176` and `/314` with narrow deterministic fixtures and exclude `/101`, `/590`, `/1005`, and `/1012`, matching a conservative four-exclusion boundary; (B) pilot checksum-pinned local HTTP(S) fixtures for all six, potentially avoiding every network exclusion at higher implementation and validation cost; (C) exclude all six, which is simpler but overstates the evidence; (D) allow outbound network access, accepting nondeterminism, security risk, HTTP-client blocking, and external side effects; (E) use the official remote evaluator, losing local environment control and evaluator transparency. The user adopted alternative A before model inference.
- Consequences: BigCodeBench task scope is frozen at 1,136 included and four excluded tasks. Resource revisions, archive and extracted-tree hashes, resolver entries, certificates, and fixture implementation identity are evaluator provenance. Targeted diagnostic `diagnostic-20260803-r12-targeted-v3` passed all 31 formerly anomalous included tasks in all three repetitions. Corrective audit `timing-bigcodebench-20260803-r2-v3` subsequently passed and independently validated all 3,408 observations with zero anomalies, resolving the benchmark-acceptance issue. Any future reference failure returns to diagnosis rather than becoming candidate `FAIL` or an unrecorded exclusion.
- Affected files/configurations/runs: `documents/05_models_and_benchmarks.md`, `configs/benchmarks/bigcodebench.toml`, `resources/bigcodebench/offline_network/`, `scripts/fetch_bigcodebench_resources.py`, sandbox resource mounts and TLS launcher, exclusion-aware audit tooling, `TASKS.md`, `PROJECT_STATUS.md`, and `ISSUE-20260803-01`. Smoke diagnostic `diagnostic-20260803-r11-resource-smoke-extracted` passed all six representative resource/fixture references; targeted report `diagnostic-20260803-r12-targeted-v3` has SHA-256 `9a013068555cbf5895c2795e1e87372cf6e07f1db54f683a98ac33cd3d3d532b`. The immutable `v1` audit remains partial and no model experiment exists.
- Supersedes or superseded by: Finalizes the previously proposed mixed resource/network policy in this entry.

## DEC-20260803-10: Pin and download the four adopted model snapshots before engine selection

- Date: 2026-08-03
- Status: Adopted
- Context: The canonical model design already selects four official checkpoints and their planned precisions. Each complete snapshot is approximately 30 GB, while model-serving engine selection and installation remain pending. The server has sufficient storage, the checkpoints are public and ungated, and exact Hugging Face safetensor snapshots are reusable across compatible local engines. Downloading them while evaluator diagnosis proceeds uses otherwise idle time without starting model inference.
- Decision: Pin the current exact commit of each already-adopted official repository in manifest `model-checkpoints-2026-08-03-r1`: StarCoder2 `ffb8dd9776ba9a66d655ecd962e882f3013e9f7c`, Qwen2.5-Coder `aedcc2d42b622764e023cf882b6652e646b95671`, DeepSeek-Coder-V2-Lite `e434a23f91ba5b4923cf6c9d9a238eb4a08e3a11`, and Qwen3-Coder FP8 `dcaee4d4dfc5ee71ad501f01f530e5652438fde0`. Download complete snapshots into one durable sequential batch with attempt-specific bytes, remote file metadata, LFS SHA-256 verification, complete local SHA-256 manifests, and canonical promotion only after every model validates. Do not select or install an inference engine as part of this download.
- Rationale: Exact revisions prevent upstream drift, while official Hugging Face snapshot files remain engine-independent inputs for vLLM, SGLang, or Transformers compatibility work. Attempt-specific storage preserves partial failure evidence and avoids silently mixing bytes across reruns. Separating download from engine selection prevents dependency choices from changing the already-adopted model construct.
- Alternatives considered: Download only one model; download all repositories without revisions; install an engine before obtaining weights; or download converted third-party quantizations. These respectively leave idle bandwidth unused, permit drift, unnecessarily serialize independent preparation, or change checkpoint provenance and planned precision.
- Consequences: The batch requires 124,084,848,411 snapshot bytes plus attempt metadata and temporary space. Checkpoint availability does not certify engine compatibility, GPU fit, tokenizer behavior, or inference correctness; those remain Section 7 validation tasks. A model or precision change would require a separate adopted design decision and new manifest rather than relabeling these bytes.
- Affected files/configurations/runs: `configs/models/checkpoints.toml`, `scripts/download_model_snapshots.py`, downloader tests, `README.md`, `TASKS.md`, and `PROJECT_STATUS.md`. No model call or experiment run is created by downloading weights.
- Supersedes or superseded by: None.

## DEC-20260803-11: Raise the global EvalPlus memory limit to 8 GiB

- Date: 2026-08-03
- Status: Adopted
- Context: The complete MBPP+ reference audit failed only for `Mbpp/255`. Its augmented input 85 requests 1,663,740 tuples, while all augmented expected outputs retain 2,015,941 tuples. The official reference reproducibly raises `MemoryError` under the prior 4 GiB limit and passes at 5, 6, and 8 GiB. The host has 125 GiB physical memory and evaluations are independently resource-bounded.
- Decision: Set the global EvalPlus candidate-process memory limit to 8 GiB for both HumanEval+ and MBPP+, identify the evaluator as `self-refinement-isolated-v3`, and advance the benchmark manifest to `evalplus-benchmarks-2026-08-03-r3`. Retain all other EvalPlus execution, timeout, oracle, and isolation behavior unchanged.
- Rationale: A global 8 GiB ceiling is simpler and less error-prone than a task-specific branch, provides headroom above the observed 5 GiB passing boundary, and remains a finite containment limit. It does not allocate memory eagerly; ordinary tasks continue to use only what they need. Applying one pre-frozen limit to all models and protocols preserves fairness.
- Alternatives considered: Keep 4 GiB and exclude `Mbpp/255`; use a 5 or 6 GiB global limit with less headroom; add a task-specific override; or remove the memory limit. Exclusion would discard a reproducible task solely because of a local resource setting, a narrow boundary provides little margin, a special branch adds avoidable configuration complexity, and no limit weakens containment.
- Consequences: Prior EvalPlus timing audits under adapter `v2` remain immutable but cannot certify the final `v3` environment. Targeted confirmation `diagnostic-20260803-r1-confirmation` passed `Mbpp/255` in all three isolated repetitions. Complete HumanEval+/MBPP+ timing datasets still require replacement audits after the independent `HumanEval/32` decision. Higher concurrency must account for an 8 GiB per-process ceiling even though typical processes use much less.
- Affected files/configurations/runs: `configs/benchmarks/evalplus.toml`, `src/self_refinement/evaluation/evalplus.py`, `src/self_refinement/benchmarks/evalplus.py`, `documents/05_models_and_benchmarks.md`, EvalPlus validation tooling and tests, and future replacement audits. Existing audits `timing-humaneval-20260803-r1` and `timing-mbpp-20260803-r1` are not modified.
- Supersedes or superseded by: Refines the resource limit of `DEC-20260802-02`; all isolation and dataset-pin decisions remain in effect.

## DEC-20260803-12: Exclude HumanEval/32 for upstream reference-oracle incompatibility

- Date: 2026-08-03
- Status: Adopted
- Context: `HumanEval/32` uses EvalPlus's `find_zero` special oracle. Confirmation diagnostic `diagnostic-20260803-r1-confirmation` reproduced the same base `fail` with zero recorded details and plus `fail` with seven recorded details under three isolated repetitions, with and without a separate network namespace, and under 4 GiB, 8 GiB, and unlimited memory. The official canonical source produces exactly the same deterministic outputs as EvalPlus trusted execution, but seven augmented inputs exceed the dataset's `1e-4` polynomial-residual tolerance. EvalPlus 0.3.1 also executes `continue` in the `find_zero` branch before its common success-detail/progress update, so all successful inputs are omitted from progress. Report SHA-256 is `8ba8b7cc7ddaac73cf1706ab8530986ffc277338337fa3f2c58d23754a40db58`.
- Decision: Pre-exclude only `HumanEval/32` before model inference, retain the remaining 163 HumanEval+ tasks, and record the exact upstream reference-oracle incompatibility as the exclusion reason. Do not patch the oracle, relax its tolerance, or use exact canonical-output equality as an alternative acceptance path.
- Rationale: The anomaly is independent of the local network and memory configuration, deterministic, and present in the pinned official evaluator/data combination. Any oracle modification would create a local functional-correctness definition for this task. One pre-experiment exclusion is more conservative and auditable than silently changing acceptance semantics.
- Alternatives considered: Patch only the missing progress update; accept exact equality with the trusted canonical output; relax the special-oracle tolerance; replace the canonical solution; or retain the task while treating the official reference failure as expected. Each alternative either leaves the seven oracle failures unresolved, changes task correctness semantics, changes benchmark data, or prevents complete reference validation.
- Consequences: HumanEval+ scope is 163 tasks for all models and protocols, and a complete 163-task reference audit under manifest `evalplus-benchmarks-2026-08-03-r4` is required. The original 164-task audit remains immutable and partial. The exclusion is fixed before model inference and is unrelated to model or protocol outcomes. Study design advances from `study-v0.1.2` to `study-v0.1.3`.
- Affected files/configurations/runs: `configs/benchmarks/evalplus.toml`, `documents/05_models_and_benchmarks.md`, loader/audit scope validation, project-state documents, and future replacement HumanEval+ audits. Diagnostic evidence is `runs/logs/evalplus-reference-diagnostics/diagnostic-20260803-r1-confirmation/report.json`; no existing run is modified.
- Supersedes or superseded by: None.

## DEC-20260803-13: Provision an isolated pinned vLLM compatibility environment

- Date: 2026-08-03
- Status: Adopted
- Context: All four exact checkpoint snapshots and all three final reference timing datasets are validated. The host exposes two idle NVIDIA GeForce RTX 4090 GPUs (24,564 MiB each, compute capability 8.9) through driver 580.159.03 with CUDA 13.0 compatibility. Official vLLM documentation supports Python 3.12, these GPU capabilities, and all four checkpoint architectures. PyPI resolution for stable vLLM 0.26.0 selects a prebuilt CUDA 13/PyTorch 2.11 stack without requiring the absent host `nvcc` toolchain.
- Decision: Provision compatibility candidate `vllm-environment-2026-08-03-r1` in a separate `.venv-vllm` using Python 3.12.13, vLLM 0.26.0, PyTorch 2.11.0, and binary-only packages. Pin the vLLM and PyTorch wheel SHA-256 values before installation. Retain the complete pip install report, freeze, inspect output, GPU inventory, CUDA import result, status, and log in an immutable attempt. Promote the canonical environment only after `pip check`, exact primary-wheel validation, CUDA availability, two-GPU visibility, and compute-capability checks pass. Use tensor parallel size two as the planned loading-smoke topology.
- Rationale: A separate environment prevents vLLM's fast-moving CUDA, PyTorch, Transformers, and serving dependencies from changing the already validated EvalPlus orchestration environment. Binary-only installation avoids an unpinned local CUDA build, while package and wheel evidence makes the initial resolution auditable before a complete lock is committed.
- Alternatives considered: Install vLLM into the main `.venv`; use an unpinned latest release; build from source without host `nvcc`; use Docker immediately; or select model-specific engines before testing a common engine. These respectively risk evaluator dependency drift, version drift, guaranteed build failure, add a second container/runtime boundary before it is needed, or abandon the simpler common-engine design prematurely.
- Consequences: Environment completion certifies package and GPU-import compatibility only. It does not yet certify checkpoint loading, numerical behavior, tokenizer/chat-template behavior, memory fit, context length, decoding parameters, or vLLM as the final primary engine. Those settings remain unfrozen until all four sequential loading/generation smoke tests pass. The successful 196-package freeze is committed as `requirements-vllm.lock` at SHA-256 `f1f66f8127dc916c576fd847d2478b1793b9a6443050c5f974104ec60a76092a`, and subsequent rebuilds validate and install that exact lock.
- Affected files/configurations/runs: `configs/inference/vllm.toml`, `.gitignore`, `scripts/setup_vllm_env.py`, setup tests, `README.md`, `TASKS.md`, `documents/PROJECT_STATUS.md`, and durable attempt `runs/logs/vllm-environment/vllm-setup-20260803-r1/`. This is preparation, not a model call or experiment run.
- Supersedes or superseded by: Refines the common local inference environment planned in `documents/05_models_and_benchmarks.md`; final engine and inference configuration remain pending compatibility evidence.

## DEC-20260803-14: Use the supported PyTorch-native sampler for vLLM compatibility smoke

- Date: 2026-08-03
- Status: Adopted for compatibility validation only
- Context: Replacement smoke `vllm-smoke-20260803-r2` resolved executable lookup and reached StarCoder2 weight loading, tensor parallel initialization, FlashAttention 2 selection, torch compilation, and CUDA graph capture. It then failed when vLLM's default FlashInfer 0.6.14 sampler attempted runtime compilation with the host `/usr/local/cuda` toolkit, which is CUDA 11.8 despite the driver and binary PyTorch stack supporting CUDA 13.0. FlashInfer's bundled CCCL rejects CUDA versions below 12. vLLM 0.26.0 explicitly supports `VLLM_USE_FLASHINFER_SAMPLER=0`, which selects its PyTorch-native sampler path.
- Decision: Set `VLLM_USE_FLASHINFER_SAMPLER=0` explicitly in validation-only smoke configuration `vllm-four-model-smoke-2026-08-03-r2`, record `sampling_backend=pytorch-native` in the configuration and every model result, and rerun all four checkpoints without changing model weights, precision, tensor parallelism, prompt, seed, or greedy decoding. Do not install or repoint a host CUDA toolkit for this smoke.
- Rationale: The supported fallback avoids an unpinned system-toolchain change and tests the common vLLM engine using its binary CUDA runtime and an explicit reproducible sampler. Attempt `r2` establishes that the failing JIT was isolated to FlashInfer sampling; attention already selected FlashAttention 2. Greedy validation remains suitable for loading and deterministic token-generation checks.
- Alternatives considered: Install CUDA 13 toolkit system-wide; install a CUDA 12 toolkit and compile against a different major version than the PyTorch wheel; define CCCL's deprecated-CUDA suppression macro for unsupported CUDA 11.8 compilation; or abandon vLLM. These respectively add a large host mutation, retain a toolchain mismatch, suppress an explicit compatibility guard, or reject an engine before testing its documented fallback.
- Consequences: The smoke can certify vLLM compatibility only with the PyTorch-native sampler. It does not freeze the primary experiment's sampling backend or decoding configuration. Before any pilot, that backend must be versioned and applied identically across every model and protocol; changing it later requires renewed deterministic inference validation.
- Affected files/configurations/runs: `configs/inference/vllm_smoke.toml`, `scripts/smoke_vllm_models.py`, smoke tests, `vllm-smoke-20260803-r2`, replacement `vllm-smoke-20260803-r3`, and project-state documents. No benchmark or model experiment result is affected.
- Supersedes or superseded by: Refines only the compatibility-validation stage of `DEC-20260803-13`; final engine and experiment inference settings remain pending.
- Outcome: Replacement `vllm-smoke-20260803-r3` passed all four pinned checkpoints with TP=2, explicit PyTorch-native sampling, and repeated greedy response/token equality. This certifies vLLM 0.26.0 as the common primary engine without freezing the experiment sampler or decoding configuration.

## DEC-20260803-15: Freeze simple deferred candidate timeout policy

- Date: 2026-08-03
- Status: Superseded (confirmation assignment only; primary calibration retained by `DEC-20260804-25`)
- Context: Accepted final audits contain 5,031 passing reference observations for all 1,677 included tasks. Other workloads can temporarily reduce available server resources, so a reference-tight timeout with many task-specific values would be brittle and difficult to explain. Conversely, a generous limit on every task would make nonterminating generated code a major evaluation bottleneck.
- Decision: Freeze `candidate-timeouts-2026-08-03-r1`. Use a 10-second primary wall timeout for every benchmark. Override only tasks whose maximum among three accepted reference observations exceeded 10 seconds: maximum intervals `(10, 20]`, `(20, 40]`, `(40, 80]`, and `(80, 160]` seconds receive primary limits 30, 60, 120, and 240 seconds respectively. This yields 0 HumanEval+, 1 MBPP+, and 15 BigCodeBench-Instruct overrides. Do not immediately retry primary timeouts. Complete the planned primary evaluation batch, preserve each primary timeout as provisional, then evaluate exactly those timeout candidates once with 1.5 times their frozen primary limit. A completed confirmation supplies the final functional outcome; only two timeouts produce final `TIMEOUT`. Evaluator failure and other non-timeout infrastructure states are not selected by this confirmation rule.
- Rationale: The 10-second default is generous relative to nearly all accepted references and leaves simple benchmark-wide semantics. Four coarse override tiers provide at least 1.5x headroom over every observed slow reference. Deferring confirmation until after the primary batch separates ordinary evaluation from possible transient contention and permits one auditable timeout-only rerun without adapting limits to a model or protocol result.
- Alternatives considered: Benchmark-specific defaults; a per-task reference multiplier for every task; immediate retry after each timeout; one global 120-second limit; or repeated adaptive retries. These add explanation and scheduling complexity, couple retry timing more closely to transient load, waste time on pathological candidates, or make evaluation cost and stopping behavior outcome-dependent.
- Consequences: Confirmation limits are 15, 45, 90, 180, or 360 seconds according to the task's primary limit. Attempt records must preserve raw evaluator output, exact timeout, policy version, stage, predecessor, and provisional status; a separate resolution record represents the final outcome. The active record schema advances to `2.0.0`. Schema `1.0.0` JSON exports remain immutable, and no migration is required because no pilot or primary record exists under `runs/registry`, `runs/raw`, or `runs/evaluations`. Study design advances from `study-v0.1.3` to `study-v0.1.4` before model inference.
- Affected files/configurations/runs: `configs/evaluation/timeouts.toml` (SHA-256 `8dbcb6b1697d14e23e6862ee473d27e256c79c3abea9450e3671a11e4815991a`), `documents/04_experiment_plan.md`, `documents/05_models_and_benchmarks.md`, schema `2.0.0`, evaluator timeout configuration adapters, deferred-confirmation coordinator, registry raw-evaluation storage, tests, `TASKS.md`, and `PROJECT_STATUS.md`. Accepted audit artifacts are inputs and remain unchanged; no experiment run was started.
- Supersedes or superseded by: Refines `DEC-20260802-07` by freezing its quantitative limits and changing confirmation scheduling from unspecified/immediate behavior to one deferred post-primary batch. Its 1.5x-only confirmation assignment is superseded by `DEC-20260804-25`; the reference-only primary calibration and exactly-one-confirmation construct are retained.

## DEC-20260803-16: Freeze common deterministic primary inference settings

- Date: 2026-08-03
- Status: Adopted
- Context: Compatibility smoke `vllm-smoke-20260803-r3` proved that all four checkpoints load and generate through vLLM 0.26.0 with TP=2 and the PyTorch-native sampler, but deliberately used validation-only 4,096-token context and 64-token output settings. The official model repositories recommend different sampling values, which would make generation policy model-specific. The user selected one common reproducible configuration and noted that an earlier 8K experiment was tight and that some models repeat meaningless text until the output ceiling. Local tokenizer analysis across all 1,677 included tasks found a maximum public specification of 1,368 tokens and maximum official-reference source of 1,696 tokens.
- Decision: Freeze `primary-inference-2026-08-03-r1` for all four models and all independent model-call stages. Use vLLM 0.26.0, TP=2, GPU memory utilization 0.85, its explicit PyTorch-native sampler, `n=1`, temperature 0, top-p 1, top-k 0, min-p 0, no presence/frequency/repetition penalty, seed 0, and normal EOS stopping. Use each exact checkpoint's tokenizer and chat template with `trust_remote_code=false` and offline access. Set the common context ceiling to 16,384 tokens and forbid automatic prompt truncation. Cap Direct Generation and every code-revision call at 4,096 output tokens, Critique Generation and Revision Planning at 2,048, and the Decision call at 64. Validate `prompt tokens + stage cap` before every call.
- Rationale: Greedy decoding removes seed-dependent sampling variance while preserving the study's one-candidate design and paired protocol comparisons. A finite stage-specific ceiling bounds pathological repetition without imposing the short categorical Decision limit on code or the full code limit on intermediate text. 16,384 is the largest native context shared by all four configurations: StarCoder2's model limit and DeepSeek's pinned tokenizer limit are both 16,384. Raising a common limit further would require model-specific extrapolation and change model behavior, not merely consume more GPU memory. The observed task lengths and finite upstream artifact caps leave substantial room for the longest CPR prompt, which will be checked again against exact rendered templates before the pilot.
- Alternatives considered: Use each model card's sampling defaults; use one nonzero common temperature with a fixed seed; retain the earlier 8K ceiling; use model-specific 32K or larger contexts; remove output limits; or truncate overflowing prompts. These introduce model-dependent generation policies or sampling variance, repeat the previously observed context pressure, alter only some models through extrapolation, allow unbounded repetitive output, or silently change the information supplied to selected calls.
- Consequences: The experiment configuration is semantically frozen, subject to a new four-model GPU smoke at 16,384 context before pilot use. An overflow is an explicit inference/preflight failure and may motivate a separately adopted design revision before the pilot; it is never silently truncated. Output-limit termination remains a returned model response and must be identifiable from token counts/finish reason in the future common inference interface. Study design advances from `study-v0.1.4` to `study-v0.1.5`; no pilot or primary candidate exists under an earlier inference configuration.
- Affected files/configurations/runs: `configs/inference/primary.toml` (SHA-256 `835f14cee9b900fdea694bcb21dbbe4fb77b9754f24c064c3597b4c79f415c00`), `src/self_refinement/inference/configuration.py`, vLLM smoke and validation tooling, inference tests, `documents/05_models_and_benchmarks.md`, `TASKS.md`, `PROJECT_STATUS.md`, and planned validation `vllm-primary-smoke-20260803-r1`.
- Supersedes or superseded by: Finalizes the experiment settings left open by `DEC-20260803-13` and promotes the PyTorch-native backend used only for compatibility in `DEC-20260803-14` to the primary configuration. It does not make validation smoke outputs experiment candidates.

## DEC-20260803-17: Adopt model-resident all-benchmark phase scheduling

- Date: 2026-08-03
- Status: Adopted
- Context: The primary experiment requires seven independent model-call stages over 1,677 included tasks for each of four checkpoints. Reloading the same model between benchmarks or protocols would add avoidable GPU initialization overhead. Running one task end-to-end would also mix phases, make shared artifact completeness harder to inspect, and encourage benchmark-by-benchmark intervention. The user requested separate Direct Generation and Refinement-Need Decision passes, stored Decision reuse, model-major execution, and protocol-level background sessions spanning every benchmark.
- Decision: Adopt execution schedule `model-resident-all-benchmark-2026-08-03-r1`. Treat one loaded exact checkpoint as the outermost inference unit. Within that resident model campaign, run separate full-scope phases in this order: Direct Generation, Refinement-Need Decision, Direct Revision, Critique Generation, Critique-Conditioned Revision, Revision Planning, and Plan-Conditioned Revision. Every phase covers the frozen 163 HumanEval+, 378 MBPP+, and 1,136 BigCodeBench-Instruct tasks in one background session without benchmark-by-benchmark user handoff. Direct Revision produces the `R` candidate; the critique-conditioned path produces `CR`; and the critique-plus-planning path produces `CPR`. Record task-level immutable checkpoints and phase-level completeness. Only after all phases validate does the normal path unload that model and advance to the next. Build `DR`, `DCR`, and `DCPR` later from the one stored Decision and corresponding stored always-refine candidate without any additional model call. Keep benchmark evaluation as a separate campaign and never use its outputs to control or inform inference.
- Rationale: Model-major residency amortizes weight loading while phase-major batching preserves the exact shared initial, Decision, critique, and plan relationships and provides simple aggregate progress. One continuous worker can traverse benchmark boundaries automatically, while task-level atomic records still allow safe resume after interruption. Separating evaluation prevents accidental feedback leakage and avoids competing with the resident inference model for resources.
- Alternatives considered: Reload a model for each benchmark; execute every task end-to-end; launch one process per protocol and model with repeated loads; or interleave candidate evaluation between model-call phases. These respectively waste loading time, obscure phase completeness, duplicate model initialization, or create unnecessary feedback-leakage and resource-contention risk.
- Consequences: The protocol runner must be a model-resident phase scheduler, expose aggregate and per-benchmark counts, checkpoint every task, validate upstream completeness before dependent phases, and reuse completed artifacts on resume. Host or worker failure may require reloading a model, but never justifies regenerating a validated logical call. The scheduling decision changes neither the seven independent call definitions nor any protocol outcome, prompt, decoding setting, benchmark scope, or statistical construct, so study version `study-v0.1.5` remains unchanged.
- Affected files/configurations/runs: `EXPERIMENT_EXECUTION_GUIDELINES.md`, `AGENTS.md`, `CODEX_CONTINUATION_PROMPT.md`, `documents/04_experiment_plan.md`, `TASKS.md`, `README.md`, and future pilot/primary orchestration. The running validation-only `vllm-primary-smoke-20260803-r2` is unaffected.
- Supersedes or superseded by: Operationally refines the model-task dependency order in `documents/04_experiment_plan.md`; it does not supersede any protocol definition or prior decision.

## DEC-20260803-18: Probe batch-invariant inference before primary adoption

- Date: 2026-08-03
- Status: Adopted
- Context: Primary smoke `vllm-primary-smoke-20260803-r2` successfully loaded StarCoder2 at TP=2 and 16,384 context, but two identical prompts in one 4,096-token greedy batch diverged despite temperature 0 and seed 0. vLLM 0.26.0 leaves batch-invariant execution disabled by default and documents deterministic offline scheduling or batch invariance as additional reproducibility mechanisms. The primary campaign will batch many tasks and must resume without silently making candidates depend on a changed batch composition.
- Decision: Run a focused validation-only RTX 4090 TP=2 feasibility/throughput probe of vLLM 0.26.0 `VLLM_BATCH_INVARIANT=1` on StarCoder2 with the same 16,384 context, two identical simultaneous prompts, and 4,096-token ceiling that exposed `r2`. Preserve exact outputs before comparing them. Do not yet enable batch invariance in the primary configuration; if the focused probe passes, review its runtime and then validate all four architectures before a separate primary-setting adoption.
- Rationale: Batch invariance most directly targets dependence on batch size, order, and scheduling, which is the failure observed and the property needed for task-level resume. However, it changes kernels and collective settings, is not enabled in the currently frozen configuration, and may reduce throughput; compatibility on Ada SM89 and all four selected architectures must be measured rather than assumed.
- Alternatives considered: (A) Enable vLLM batch invariance after a four-model compatibility and throughput probe; (B) disable V1 engine-core multiprocessing and freeze a deterministic offline batch plan, which addresses scheduling but may not remove numerical batch-position effects and makes partial resume harder to reproduce; (C) keep current greedy settings as best-effort reproducibility, freeze task ordering/batches, and accept that resumed or differently batched calls can diverge; or (D) force single-request inference, which reduces batch-composition variance but sacrifices throughput and still does not provide a general batch-invariance guarantee.
- Consequences: Probe configuration `vllm-batch-invariance-probe-2026-08-03-r1` is not a primary experiment configuration and cannot generate pilot candidates. A passing StarCoder2 probe is necessary but not sufficient for adoption because all four architectures and the throughput tradeoff still require review. Any later primary adoption requires a new primary-inference configuration version, regression tests, linked four-model smoke, and synchronized canonical/model documents. No existing model experiment result is invalidated because none exists; validation attempts `r1` and `r2` remain immutable.
- Affected files/configurations/runs: `configs/inference/vllm_batch_invariance_probe.toml`, vLLM smoke runner and validator, tests, focused attempt `vllm-batch-invariance-probe-20260803-r1`, and operational documents. Primary configuration `configs/inference/primary.toml` remains unchanged.
- Supersedes or superseded by: Would refine deterministic claims in `DEC-20260803-16`; no change is adopted yet.
- Outcome: Focused attempt `vllm-batch-invariance-probe-20260803-r1` passed exact two-response and token-sequence equality on StarCoder2. Worker elapsed time was 110.0725 seconds. Relative to failed `r2`, compile/warmup increased by about 39 seconds and reported KV capacity decreased from 7.21 to 6.84 concurrent 16K requests (about 5%), while remaining adequate. Checkpoint cache state prevents a valid total-runtime ratio. These results satisfy the condition to prepare common primary adoption and four-model validation.

## DEC-20260803-19: Adopt batch-invariant primary inference

- Date: 2026-08-03
- Status: Adopted
- Context: Frozen greedy primary configuration `r1` did not make two identical simultaneous StarCoder2 requests identical under default vLLM batching. Focused probe `vllm-batch-invariance-probe-20260803-r1` enabled vLLM 0.26.0 batch invariance on the fixed RTX 4090 TP=2 topology and produced byte-identical text and token sequences. It retained 6.84 maximum 16K requests of KV capacity versus 7.21 in the default-mode observation, while adding about 39 seconds to one-time compile/warmup. The experiment schedule keeps a model resident across all phases, amortizing that setup cost.
- Decision: Advance the primary configuration to `primary-inference-2026-08-03-r2` and require `VLLM_BATCH_INVARIANT=1` for every model and independent call stage. Retain all other `r1` settings exactly: vLLM 0.26.0, TP=2, GPU utilization 0.85, PyTorch-native sampler, pinned precision/tokenizer/chat template, 16,384 context, no prompt truncation, greedy decoding and seed 0, normal EOS, and 4,096/2,048/64 stage output ceilings. Record batch-invariant mode in every call/result and preserve raw output before validation. Validate the new common setting on all four checkpoints before pilot inference.
- Rationale: Batch invariance directly addresses the observed dependence on simultaneous batch execution and supports task-level resume without requiring exact reconstruction of prior batch composition. Its measured one-time initialization and roughly 5% KV-capacity costs are acceptable under model-resident campaigns and leave substantial two-GPU capacity.
- Alternatives considered: Disable only V1 engine-core multiprocessing; freeze exact batches and accept best-effort greedy reproducibility; use one request at a time; or keep default batching. These do not directly guarantee independence from batch composition, make partial resume brittle, substantially sacrifice throughput, or retain the reproduced failure mode.
- Consequences: Primary configuration SHA-256 becomes `f608fafb5e629d6b60ee3525e27345c68b9958754b119649ba6116bde8b8b8cf`. Study design advances from `study-v0.1.5` to `study-v0.1.6` before any pilot or primary candidate exists. Four-model primary smoke `vllm-primary-smoke-20260803-r3` must pass exact repeated output/token equality, configuration provenance, context allocation, and cleanup. A failure in any architecture returns to diagnosis rather than allowing model-specific deterministic settings.
- Affected files/configurations/runs: `configs/inference/primary.toml`, typed inference configuration, vLLM worker environment/results, primary validators/tests, `documents/04_experiment_plan.md`, `documents/05_models_and_benchmarks.md`, `TASKS.md`, `PROJECT_STATUS.md`, and planned `vllm-primary-smoke-20260803-r3`.
- Supersedes or superseded by: Refines deterministic execution in `DEC-20260803-16`; all other `r1` inference choices remain adopted. Completes the conditional primary-setting step prepared by `DEC-20260803-18`.
- Outcome: Four-model attempt `vllm-primary-smoke-20260803-r3` completed 4/4 under configuration SHA-256 `f608fafb5e629d6b60ee3525e27345c68b9958754b119649ba6116bde8b8b8cf`. Every checkpoint produced exactly identical repeated response text and token IDs. Independent validation and post-run GPU cleanup passed, resolving `ISSUE-20260803-09` and certifying `primary-inference-2026-08-03-r2` for prompt/runner development and later pilot use.

## DEC-20260803-20: Adopt strict draft prompt and parsing contracts for pilot review

- Date: 2026-08-03
- Status: Adopted
- Context: The seven canonical model-call stages require versioned external prompts and uniform, auditable parsing before the common inference interface and pilot can be implemented. Searching prose for a likely code block or repairing malformed output would add model- and output-dependent behavior that is not part of the study construct. Future critique and plan content cannot be completely classified semantically without another evaluator, but clear structural violations can be rejected consistently.
- Decision: Adopt `primary-prompts-2026-08-03-draft1` for implementation and pilot review. Declare only the canonical input fields for each stage. Require Decision to contain only uppercase `PRESERVE` or `REFINE` after removing surrounding whitespace. Require Direct, `R`, `CR`, and `CPR` responses to consist of exactly one complete `python` fenced block with no outside text, and use one extractor for all four. Treat empty critique/plan output or any fenced code in those text artifacts as an explicit invalid response. Never syntax-repair extracted source or infer functional correctness while parsing. Before inference, count the exact rendered chat prompt and reject overflow without truncation. For preflight only, validate all 1,677 public tasks using every upstream stage's full output cap plus a fixed 64-token boundary margin; the exact runtime check remains authoritative.
- Rationale: The rule is deterministic, identical across candidate conditions, preserves malformed responses as observable failures, and avoids silent model-output repair. Exact input allowlists reinforce the public benchmark boundary. A deliberately conservative envelope tests 16K feasibility before artifacts exist while the per-call exact check handles actual tokenization.
- Alternatives considered: Accept raw unfenced source; extract the first or largest code fence from prose; use language-specific heuristics or AST repair; accept arbitrary critique/plan text including fenced revisions; or estimate all prompt sizes only from character counts. These make ambiguous choices, vary behavior by response shape, blur malformed and functional failure, weaken stage separation, or fail to use the pinned tokenizer/chat template.
- Consequences: Manifest SHA-256 is `2f83cbaa941d4476c2e26dfca57f3288039f5e69a97274971749bfbba39d8dd1`. Four-tokenizer validation passed with the smallest conservative remaining input budget of 2,478 tokens for StarCoder2 CPR. The common inference interface must store raw bytes and token counts before invoking these parsers and map their typed errors to explicit statuses. This prompt set is a pilot-review draft, not the primary freeze; parser compliance and prompt behavior must be reviewed across all four models before adoption of a final primary prompt version. No study-version change occurs until such a result-affecting primary freeze or revision is adopted.
- Affected files/configurations/runs: `configs/prompts/primary.toml`, `prompts/v1/`, prompt renderer/parser/token-budget modules, validation/export scripts, tests, `TASKS.md`, `README.md`, and `PROJECT_STATUS.md`. No pilot or primary run exists.
- Supersedes or superseded by: Complements `DEC-20260803-16` and `DEC-20260803-19`; a later pilot-review decision will freeze or supersede this draft for the primary experiment.

## DEC-20260803-21: Record backend finish reason in active model-call schema

- Date: 2026-08-03
- Status: Adopted
- Context: The frozen inference configuration deliberately caps every stage to prevent unbounded repetitive output. Output token count alone cannot reliably distinguish a normal EOS completion from a backend length termination, especially when tokenizer or backend behavior changes at a boundary. The version `2.0.0` model-call record had no explicit finish-reason field. No pilot or primary record exists, so the provenance gap can be corrected without migrating experimental data.
- Decision: Advance the active record schema to `3.0.0` and require every returned model response—whether parseable, invalid, or an extraction failure—to record the backend finish reason as `stop` or `length`. A call without a returned response cannot carry a finish reason. Preserve all `v1` and `v2` JSON Schema exports unchanged. Use one common stage-homogeneous interface for every selected resident model: apply only frozen primary decoding, count the exact chat-formatted prompt, store exact raw UTF-8 response bytes before parsing, record input/output token counts, and isolate preflight or backend failures into explicit per-call records.
- Rationale: Explicit backend provenance makes output-cap effects directly auditable and avoids post hoc inference from token counts. A model-independent batch contract preserves fairness while per-call records allow later batches and resume logic to continue without making infrastructure failure a functional `FAIL`.
- Alternatives considered: Infer length termination whenever output tokens equal the configured cap; place finish reason only in logs; preserve v2 and add an untyped metadata mapping; or wait until after the pilot. These are ambiguous, hard to validate, weaken the typed record contract, or would require migration or pilot invalidation later.
- Consequences: `schemas/v3/` becomes active and `ModelCallRecord` requires finish reason for all returned responses. There is no migration artifact because `runs/registry` contains no pilot or primary records. Study version `study-v0.1.6` is unchanged because this adds provenance without changing prompts, model behavior, protocol calls, task scope, evaluation, or analysis constructs. The future runner must use `ModelCallExecutor` and may treat `length` as an analysis/diagnostic attribute; it must not silently repair or regenerate the response.
- Affected files/configurations/runs: Schema models and `schemas/v3/`, common inference and resident vLLM adapters, schema/registry/interface tests, `TASKS.md`, `README.md`, `schemas/README.md`, and `PROJECT_STATUS.md`. No experiment run is affected.
- Supersedes or superseded by: Extends model-call provenance in `DEC-20260803-16` and implements the raw-first requirement in `DEC-20260803-20`; it supersedes only the active-schema designation of `v2`, whose files and historical decision remain preserved.

## DEC-20260803-22: Freeze a public-only nine-task cross-model pilot scope

- Date: 2026-08-03
- Status: Adopted
- Context: The draft prompt/parser contract and complete execution pipeline require a small pilot before any primary generation. The pilot must cover all three benchmarks and expose variation in prompt size without selecting tasks from hidden tests, reference outcomes, known model behavior, or functional difficulty labels.
- Decision: Freeze pilot scope `pilot-public-length-quantiles-2026-08-03-r1`. For each included benchmark scope, sort tasks by `(len(public task specification), upstream task ID)` and select the shortest, middle-index, and longest entries. This yields HumanEval `/53`, `/108`, `/129`; MBPP `/127`, `/131`, `/721`; and BigCodeBench `/737`, `/103`, `/764`. Run the same nine tasks through all four models, all seven inference phases, all four generated-candidate evaluations, deferred timeout confirmation, and pilot review. Pilot artifacts are validation evidence and do not enter primary estimates.
- Rationale: Public specification length directly stresses prompt construction and context handling while remaining independent of hidden evaluator content and model outcomes. Three tasks per benchmark keep the four-model pilot inexpensive enough to rerun after a prompt defect while covering short, typical, and long public inputs.
- Alternatives considered: One arbitrary task per benchmark, which gives weak parser/prompt coverage; a random sample, which adds a seed and may miss length extremes; a larger difficulty-stratified sample, which requires outcome- or test-adjacent labels and costs more; or selecting known problematic benchmark tasks, which would confound pipeline validation with evaluator anomalies.
- Consequences: Pilot campaign `pilot-campaign-2026-08-03-r1` is execution-enabled and uses batch size nine, the largest possible common batch for this scope. Batch-invariant inference keeps candidate identity independent of later primary batch composition. The full 1,677-task configuration remains blocked until pilot review adopts a final prompt version. Any pilot failure requires a new version/run rather than mutating this scope or its artifacts.
- Affected files/configurations/runs: `configs/experiments/pilot_scope.toml`, `configs/experiments/pilot_campaign.toml`, campaign/evaluation launchers, pilot review, `EXPERIMENT_RUNBOOK.md`, `TASKS.md`, and `PROJECT_STATUS.md`. No pilot run has started.
- Supersedes or superseded by: Complements `DEC-20260803-20`; it does not freeze the primary prompt or change the primary benchmark scope.

## DEC-20260804-23: Strengthen the common candidate response-format instruction for a replacement pilot

- Date: 2026-08-04
- Status: Adopted
- Context: In the first nine-task cross-model pilot, StarCoder2 returned a complete `python` fence for every Direct task but prefixed all nine responses with explanatory prose. The other three models complied with the same draft1 format. The strict parser behaved as adopted and exposed a systematic instruction-compliance problem before primary execution. Accepting text outside the fence after observing one model would weaken the unambiguous whole-response contract and silently reinterpret existing failures.
- Decision: Create `primary-prompts-2026-08-04-draft2` and a separate replacement campaign `pilot-campaign-2026-08-04-r2`. For Direct, `R`, `CR`, and `CPR`, put one common mandatory format paragraph at the beginning: the entire response must begin with the literal opening Python code fence, end immediately after its closing fence, and contain no introduction, explanation, label, or other outside text. Apply identical wording to every model and candidate-producing condition. Keep Decision, critique, and plan template bytes unchanged. Keep the strict parsers, stage inputs, inference configuration, model configurations, pilot scope, and evaluation policy unchanged. Preserve draft1, the first pilot, and its evaluation artifacts; do not parse, repair, resume, or regenerate them under draft2.
- Rationale: Moving and making the already intended output contract explicit addresses the observed failure while retaining a simple, auditable, model-independent parser. A new version and run prevent post hoc repair and allow the same nine public tasks to test whether the correction works across all four models.
- Alternatives considered: Loosen the parser to extract a single fence surrounded by prose; add StarCoder2-only parsing or chat-template instructions; retry only the nine failed calls inside the original run; exclude StarCoder2; or retain draft1. These would change the response construct after observing output, create model-specific treatment, mix prompt versions within one pilot, change the selected model scope, or knowingly carry a systematic pilot failure into primary execution.
- Consequences: Draft2 must pass full hash/input/context-budget validation and a new complete four-model pilot before any primary prompt freeze. The prompt-manifest SHA-256 is `113d7cb619343c62bb8e7ca738fbf1214ea662d25bd3c5014e16cd7ba6e8d5d7`; replacement campaign configuration SHA-256 is `de69a186d21d13bc7bbbabfa50439d544b369e054508a5924608c838dcfa96fc`. This is a pre-primary pilot prompt revision, so study version remains `study-v0.1.6`; any later primary adoption requires a separate freeze decision.
- Affected files/configurations/runs: `prompts/v2/`, `configs/prompts/primary_draft2.toml`, `configs/experiments/pilot_campaign_draft2.toml`, prompt validation/tests, `EXPERIMENT_RUNBOOK.md`, `TASKS.md`, `PROJECT_STATUS.md`, and `ISSUE-20260804-02`. First pilot inference `run_2ee6e3449b478af4e56a509f`, evaluation `run_408b9ad39cdae36bacca33ae`, and report `pilot-review-20260804-r2` remain immutable.
- Supersedes or superseded by: Supersedes draft1 only for the replacement pilot. It does not supersede the strict parsing decision in `DEC-20260803-20`, the pilot scope in `DEC-20260803-22`, or any primary prompt freeze because none exists yet.
- Outcome: Manifest/input/hash validation and the complete 1,677-task four-tokenizer context-envelope check passed. The smallest conservative remaining context is 2,433 tokens for StarCoder2 CPR. Repository formatting, lint, strict typing, schema freshness, and all 125 tests pass. Corrected host-level clean-worktree preflight passed all exact configuration hashes, four checkpoints, nine-task scope, Python/vLLM versions, disk, and clear-GPU checks without loading a model or creating a run.

## DEC-20260804-24: Separate exploratory long-timeout diagnostics from frozen evaluation resolution

- Date: 2026-08-04
- Status: Adopted
- Context: A candidate can be functionally correct but exceed the frozen primary and confirmation wall limits because the benchmark does not independently impose an algorithmic performance criterion. Replacement-pilot evaluation produced ten confirmed final timeouts, motivating an operator-controlled longer run to distinguish slow completion from practical nontermination. Reusing the evaluation campaign with an ad hoc timeout would mix policies, overwrite the meaning of its final resolution, or invite outcome-dependent retries.
- Decision: Add a separate timeout-diagnostic workflow that reads only independently validated final `TIMEOUT` resolutions and accepts an explicit positive finite wall timeout. Never add its results to the source evaluation registry, never replace or reclassify its resolution, and never expose them to model prompts. Preserve diagnostic raw evaluator output, evaluator configuration, source hashes, represented candidate/resolution IDs, status, report, and validation under a unique attempt. By default execute each exact `(task_record_id, source_sha256)` once and map the result to all duplicate candidate records; allow explicit per-candidate or candidate-ID selection. Support foreground execution for bounded short checks and durable background execution for long checks.
- Rationale: The diagnostic supplies evidence about timeout sensitivity without silently changing the pre-frozen estimator or multiplying identical work. Exact source deduplication is valid for exploratory diagnosis because evaluator inputs are the same task and bytes, while the report retains every candidate lineage. Separating the namespace and report makes clear that a later `PASS` is sensitivity evidence, not the experiment outcome.
- Alternatives considered: Add `--timeout-seconds` directly to the frozen evaluation campaign; edit `timeouts.toml` in place; resume completed timeout records; automatically replace final outcomes; or prohibit longer checks. These respectively create mixed-policy runs, destroy configuration provenance, violate immutable resume semantics, introduce outcome-dependent reclassification, or leave the functional-correctness concern unexamined.
- Consequences: A longer-timeout diagnostic can justify considering a new timeout policy before primary execution, but adopting that change requires a separate decision, new policy version, and new evaluation run. It cannot retroactively change pilot or primary records. The operator must use background mode when the execution-count × timeout bound can exceed the long-running threshold.
- Affected files/configurations/runs: `scripts/diagnose_candidate_timeouts.py`, shared local evaluator adapter, timeout diagnostic selection/tests, `EXPERIMENT_RUNBOOK.md`, `README.md`, `TASKS.md`, and `PROJECT_STATUS.md`. No diagnostic run has started.
- Supersedes or superseded by: Complements `DEC-20260803-15`; it does not change `candidate-timeouts-2026-08-03-r1` or its exactly-one-confirmation rule.
- Outcome: Latest replacement-pilot preflight identifies ten final timeout resolutions represented by four unique HumanEval+ task/source executions at 60 seconds. Formatting, lint, strict typing, schema freshness, focused tests, and all 129 repository tests pass. No diagnostic evaluator execution was started while implementing the facility.

## DEC-20260804-25: Adopt a common 120-second confirmation floor with three evaluator-bound exceptions

- Date: 2026-08-04
- Status: Adopted
- Context: Replacement-pilot policy `r1` used a 10-second primary limit and 15-second confirmation for default tasks, leaving ten `HumanEval/129` candidates as final timeouts. Immutable 60- and 120-second diagnostics over four unique sources showed two sources finish as functional `FAIL` at approximately 16.7 and 26.5 seconds, while two reach EvalPlus internal timeout at approximately 65.5 seconds. No diagnostic source passed. Inspection of EvalPlus 0.3.1 showed that its base and plus checks each have an internal task cap; accepted timing artifacts establish a combined theoretical 126-second bound for `HumanEval/38`, `/50`, and `/53`, while every MBPP+ task is at most 73 seconds and other HumanEval+ tasks are at most 92 seconds under the same formula.
- Decision: Supersede the active `r1` policy with `candidate-timeouts-2026-08-04-r2` before primary execution. Retain the common 10-second primary default and all 16 reference-derived primary overrides. For all three benchmarks, assign confirmation as `max(120 seconds, 1.5 × primary timeout)`. Predeclare confirmation-only 180-second overrides for `HumanEval/38`, `/50`, and `/53`; their primary limit remains 10 seconds. Continue to perform exactly one deferred confirmation only after the complete primary batch.
- Rationale: A 120-second floor is a common, paper-explainable rule that materially separates confirmation from the efficient primary screen. The three exceptions prevent the outer wall limit from preceding the pinned evaluator's own theoretical bound. Because the limit is only an upper bound, fast candidates incur no corresponding delay. The same assignment is independent of model and protocol and does not use generated-candidate outcomes to select task exceptions.
- Alternatives considered: Keep 10/15; use 180 seconds for every confirmation; use benchmark-specific floors; raise every primary limit; add a third retry; or make post-hoc per-candidate exceptions. The first does not resolve slow determinate results, the second increases BigCodeBench worst-case cost, benchmark-specific rules reduce cross-benchmark uniformity, a larger primary delays every pathological candidate, a third retry complicates the construct, and post-hoc exceptions are outcome-dependent.
- Consequences: Default confirmation may consume up to 120 seconds for a nonterminating candidate; slow-primary tasks use 120, 180, or 360 seconds according to the common maximum rule. The three HumanEval exceptions use 180 seconds. Existing `r1` inference/evaluation/diagnostic artifacts remain immutable and cannot be relabeled. Replacement-pilot inference candidates may be reused exactly, but pilot review requires a new evaluation run under `r2`.
- Affected files/configurations/runs: Active `configs/evaluation/timeouts.toml` (SHA-256 `b8482c2173ed0d98c29012bcf66f33fae11e8a3725040cb20a380de2f05570ba`), archived byte-identical `configs/evaluation/timeouts_r1.toml` (SHA-256 `8dbcb6b1697d14e23e6862ee473d27e256c79c3abea9450e3671a11e4815991a`), timeout assignment/validation/tests, canonical experiment/model documents, execution documentation, and replacement-pilot evaluation `run_2a7f94f41cc4951f78892906` as immutable `r1` evidence.
- Supersedes or superseded by: Supersedes the confirmation assignment in `DEC-20260803-15`; retains its primary calibration, complete-batch gate, exactly-one-confirmation rule, and failure separation. Complements diagnostic boundary `DEC-20260804-24`.
- Outcome: Active-policy validation matched all three accepted audit summary hashes, 5,031 observations, 16 primary overrides, and three confirmation overrides. Exact `r1` assignment regression tests pass, and full repository formatting, lint, strict typing, schema freshness, and all 130 tests pass. No `r2` evaluation has started.

## DEC-20260804-26: Define prospective handling of unambiguous format noncompliance

- Date: 2026-08-04
- Status: Adopted
- Context: Draft2 moved a common mandatory whole-response Python-fence instruction to the start of every candidate-producing prompt. Nevertheless, StarCoder2 prefixed explanatory prose to all nine Direct responses in replacement pilot `run_143681f34a6855eb1902bd4b`; every response otherwise contained exactly one complete Python fence and ended normally. Separately, one of 27 Qwen2.5 revision-plan responses included a fenced code example despite the plain-text-only instruction. The runner, raw-first storage, strict parsers, dependency blocking, and evaluation all behaved as designed. Requiring zero malformed output in a pilot would make isolated model noncompliance an experiment-wide infrastructure gate, while retaining the current candidate parser makes the selected StarCoder2 checkpoint systematically unevaluable.
- Decision: Prospectively adopt one common deterministic candidate extractor for Direct, `R`, `CR`, and `CPR`: accept a response only when it contains exactly one complete `python` fenced block, store only that block's content as the candidate, and ignore surrounding non-fenced text. Continue to reject multiple or incomplete fences, non-`python` or unfenced code, empty extracted code, and any case requiring fence selection, syntax repair, or model-specific logic. For Critique and Revision Planning, accept any non-empty text artifact including prose plus inline or fenced focused code snippets. Their prompts prohibit a **complete revised solution**, rather than prohibiting all code. This semantic stage boundary is prompt-defined; the parser does not guess whether a snippet constitutes a full solution. Apply every rule identically across models and relevant stages. Create draft3 prompt/parser/campaign versions and run a new complete four-model pilot; never reparse draft1/draft2 artifacts.
- Rationale: The study evaluates generated code rather than whether a model suppresses harmless presentation prose. Exactly one complete Python fence makes the candidate selection deterministic without code repair or model-specific treatment. Critique and plan commonly use code excerpts for fault localization and actionable explanation; rejecting the entire artifact merely because it contains a fence creates avoidable downstream missingness and is stronger than the intended separation between analysis/planning and complete revision generation.
- Alternatives considered: Retain the whole-response candidate parser; add a common assistant prefill/stopping contract; add StarCoder-specific prompting or parsing; exclude StarCoder2; keep rejecting every fenced critique/plan; or attempt to heuristically distinguish a focused snippet from a complete solution. These respectively leave one selected model systematically unavailable, alter generation mechanics, create model-specific treatment, change model scope, discard useful intermediate artifacts, or introduce an unreliable semantic classifier.
- Consequences: This supersedes the whole-response candidate rule and critique/plan fence prohibition in `DEC-20260803-20` while preserving raw-first storage, exact one-fence disambiguation, no syntax repair, strict Decision parsing, stage input boundaries, and common treatment. Prompt set `primary-prompts-2026-08-04-draft3` and campaign `pilot-campaign-2026-08-04-r3` require hash, context, unit, full pilot inference, evaluation, and review validation before primary freeze. Existing draft1/draft2 records remain immutable and retain their original parser meanings.
- Affected files/configurations/runs: Prospective parser and prompt configuration, campaign configuration, pilot review acceptance logic, canonical experiment/model documents if adopted, `TASKS.md`, `PROJECT_STATUS.md`, `KNOWN_ISSUES.md`, replacement inference `run_143681f34a6855eb1902bd4b`, evaluation `run_6b1f457a1462deac2ffabf52`, and report `pilot-review-r2-20260803T225500Z`.
- Supersedes or superseded by: Supersedes the whole-response candidate extraction rule and blanket critique/plan fence prohibition in `DEC-20260803-20`, and supersedes draft2 mitigation `DEC-20260804-23` for future runs. All raw-first, no-repair, stage-input, common-treatment, and complete-revision separation rules remain.
- Outcome: Implemented prompt set `primary-prompts-2026-08-04-draft3` (manifest SHA-256 `ecf957cc0d2ed3f5eac33ee70162d1ecdf5b137b0c64d21cb25fedb6add20e63`) and pilot campaign `pilot-campaign-2026-08-04-r3` (SHA-256 `19fc42b18f7447f5902cbc05cc3d3435b9c636336050cc66361c418dfced1e1b`). Full repository formatting, lint, strict typing, schema freshness, and all 133 tests pass. Four-tokenizer validation passed all 1,677 public tasks; the tightest conservative 16K envelope is StarCoder2 CPR with 2,456 tokens remaining. A clean-worktree campaign preflight and new complete pilot remain required.

## DEC-20260804-27: Constrain the categorical Decision and interpret parse-complete length stops

- Date: 2026-08-04
- Status: Superseded
- Context: Draft3 pilot inference completed all 252 calls and all 144 candidate artifacts, but StarCoder2 produced explanatory prose for all nine Refinement-Need Decision calls until the 64-token cap. None contained a parseable exact `PRESERVE` or `REFINE`, leaving all 27 StarCoder2 decision-conditioned outcomes unavailable. One separate StarCoder2 revision-plan response repeated the same sentence until the deliberate 2,048-token cap; it remained non-empty, was stored exactly, and was supplied unchanged to CPR. The common vLLM 0.26.0 engine supports `StructuredOutputsParams(choice=[...])` for offline sampling.
- Decision: Pending user selection before changing Decision generation, finish-reason acceptance, inference configuration, pilot review, or primary execution.
- Rationale: Forcing a categorical choice changes the generated Decision distribution, while treating parse-complete length-stopped artifacts as usable changes pilot acceptance. Both can affect protocol outcomes and must be explicit before primary freeze.
- Alternatives considered: **Recommended:** apply vLLM structured choice `PRESERVE`/`REFINE` identically to every model only for the categorical Decision stage, retain the exact parser, and record the constrained decoding configuration in every run; separately treat `finish_reason=length` as diagnostic rather than automatically blocking whenever the stage parser produced its required artifact, while preserving the exact truncated raw response and token count. Validate the common constraint on all four models and rerun the complete pilot. **Prompt/cap only:** further strengthen the Decision wording or raise its cap, which does not guarantee a choice and encourages more prose. **Heuristic parsing:** infer a choice from explanatory prose, which is ambiguous when both terms or no final conclusion appear. **Missingness:** retain the current rule and accept all StarCoder2 D-protocol outcomes as missing. **Model/scope change:** exclude StarCoder2 or remove Decision-conditioned comparisons for it. **Length-zero tolerance:** reject every length-stopped artifact even when deterministically parseable, causing missing downstream results from the output bound that was introduced to contain repetition.
- Consequences: The recommended Decision constraint operationalizes the already categorical construct and avoids model-specific handling, but requires a new versioned inference configuration, backend support/tests, four-model validation, and replacement pilot before primary freeze. Accepting parse-complete length stops preserves model behavior under the frozen finite output budget; incomplete candidate fences and invalid Decisions still fail parsing, and every length stop remains visible in provenance and review warnings. Existing draft3 artifacts are immutable and are not regenerated or reinterpreted.
- Affected files/configurations/runs: Primary inference/backend configuration, parser/review acceptance documentation, model smoke or focused structured-choice validation, pilot campaign configuration, `TASKS.md`, `PROJECT_STATUS.md`, `KNOWN_ISSUES.md`, inference `run_856e8d87f7ed9bec7dec9a5c`, evaluation `run_5b4f4a5a93f86c60a7efe19c`, and review `pilot-review-draft3-20260804T000600Z`.
- Supersedes or superseded by: Superseded by adopted `DEC-20260804-28`, which selects the documented model/scope-change alternative and removes StarCoder2 before primary execution. No structured Decision constraint or length-stop acceptance change from this proposal is adopted; any such behavior in the replacement panel remains subject to pilot review.

## DEC-20260804-28: Replace StarCoder2 and expand the primary model panel to six models

- Date: 2026-08-04
- Status: Adopted
- Context: StarCoder2 failed the common candidate response contract in both draft1 and draft2 pilots, then completed draft3 candidate generation only after the common one-fence extractor was adopted but failed all 9/9 categorical Decision calls. Its repeated instruction-compliance failures became the principal source of model-specific design pressure before any primary data existed. The user chose to remove it rather than add constrained Decision generation or accept systematic missing D-protocol outcomes, and expanded the panel to cover scale, architecture, software-engineering specialization, and one general-purpose control.
- Decision: Exclude `bigcode/starcoder2-15b-instruct-v0.1` from every future primary and replacement-pilot model scope. Adopt the ordered six-model panel: `Qwen/Qwen2.5-Coder-7B-Instruct` (BF16), `Qwen/Qwen2.5-Coder-14B-Instruct` (BF16), `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct` (BF16), `mistralai/Devstral-Small-2-24B-Instruct-2512` (official FP8), `Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8` (official FP8), and `google/gemma-4-31B-it-qat-w4a16-ct` (official QAT W4A16 compressed-tensors). Treat Gemma 4 as the predeclared general-purpose instruct control; the other five models form the code/SWE-specialized panel. Advance the design to `study-v0.2.0` and pin the exact repositories, revisions, full snapshot byte counts, and planned precision in `model-checkpoints-2026-08-04-r2`.
- Rationale: Removing the systematically noncompliant checkpoint avoids model-specific parser or decoding treatment and restores complete Decision-conditioned comparisons. Qwen2.5 7B/14B supplies a within-family scale contrast; DeepSeek and Qwen3 provide distinct efficient MoE code architectures; Devstral supplies a Mistral-family SWE-specialized dense model; and Gemma supplies a general-purpose dense control. All six remain locally deployable on the fixed two-RTX-4090 workstation using their declared precision.
- Alternatives considered: Retain StarCoder2 with common structured Decision choices; retain it with missing Decision-conditioned outcomes; remove only Decision-conditioned protocols for StarCoder2; replace it one-for-one; or adopt the six-model expansion selected by the user. The first three retain model-specific pressure or incomplete paired outcomes, while a one-for-one replacement provides less coverage of scale and specialization than the adopted panel.
- Consequences: The experiment now has 18 model-benchmark combinations. Existing StarCoder2 weights, raw responses, run registries, evaluations, and reports remain immutable historical pilot evidence but are ineligible for primary estimates. The three retained checkpoints and their prior compatibility evidence remain valid, but the changed panel requires a new complete six-model serving validation, full tokenizer/context-envelope validation, and replacement pilot before prompt/primary freeze. Existing vLLM 0.26.0 is only the first compatibility target: if Devstral or Gemma 4 requires a newer version, one common environment must be frozen and validated for all six rather than adopting a model-specific engine. No structured Decision decoding or parse-complete length-stop acceptance change is adopted by this decision.
- Affected files/configurations/runs: Canonical project/model/experiment/glossary documents; `configs/models/checkpoints_v2.toml`; future inference, smoke, campaign, and pilot configurations; downloader subset support; `TASKS.md`; `PROJECT_STATUS.md`; `KNOWN_ISSUES.md`; and all future pilot/primary runs. Historical pilot runs `run_2ee6e3449b478af4e56a509f`, `run_143681f34a6855eb1902bd4b`, and `run_856e8d87f7ed9bec7dec9a5c` remain unchanged.
- Supersedes or superseded by: Supersedes the four-model scope in `DEC-20260803-10`, later four-model serving/pilot requirements where they refer to future execution, and proposed `DEC-20260804-27`. It does not supersede the common parser contract in `DEC-20260804-26`, shared-initial protocol design, evaluation policy, or model-resident scheduling.
- Outcome: All six exact snapshots, actual vLLM tokenizer context envelopes, and one common sequential runtime path passed. Attempt `vllm-primary-smoke-six-models-20260804-r1` independently validated 6/6 models under unchanged `vllm-environment-2026-08-03-r1` and `primary-inference-2026-08-04-r3`; the full 1,677-task prompt check retains at least 2,460 context tokens. Replacement pilot campaign `pilot-campaign-2026-08-04-r4` uses the unchanged nine public-only task IDs under versioned `study-v0.2.0` scope.

## DEC-20260804-29: Adjudicate rare invalid free-generated Decisions before evaluation

- Date: 2026-08-04
- Status: Adopted
- Context: Six-model replacement inference completed 378/378 calls and all 216 always-generated candidates, but one of 54 DeepSeek-Coder-V2-Lite Decision calls used the full 64-token cap for explanatory prose instead of returning exact `PRESERVE` or `REFINE`. The other 53 Decisions are valid. This leaves three derived outcomes unavailable in the pilot. Under the 1,677-task primary scope, accepting free-generation invalidity creates potentially non-random missingness in `DR`, `DCR`, and `DCPR`; changing Decision generation or missing-data treatment can change experimental outcomes and therefore requires an explicit prospective choice.
- Decision: Retain unconstrained common Decision generation and the strict exact parser. After all models finish Decision generation and before any candidate evaluation, review every invalid Decision response once under frozen rubric `decision-adjudication-2026-08-04-r1`. Use only the raw response and prompt-visible task specification and exact initial candidate. Code `PRESERVE` only when the response unambiguously says the candidate is functionally correct or needs no functional change; code `REFINE` only when it unambiguously identifies a functional defect or required functional revision; otherwise record `UNRESOLVED`. Preserve the original invalid call and raw artifact unchanged, store the label and rationale in a separate immutable adjudication artifact, and create derived outcomes only for resolved labels. Report counts/rates by model and a sensitivity analysis excluding adjudicated cases. Never use reference code, tests, evaluation outcomes, diagnostics, runtime, timeout, critique, plan, or revised candidates during review.
- Rationale: Structured choice would alter the model's generation distribution, while a fixed replacement value would deterministically bias preservation or refinement. Limited semantic coding recovers the model's already expressed intent only when it is unambiguous, and `UNRESOLVED` prevents the reviewer from manufacturing a binary choice. The pre-evaluation evidence boundary prevents functional results from influencing the code.
- Alternatives considered: **Common structured choice:** rejected because it changes generation for all Decisions to solve rare free-generation noncompliance. **Fixed `PRESERVE` or fixed `REFINE`:** rejected because either direction systematically distorts all invalid cases. **Prespecified missingness:** retained as the behavior for `UNRESOLVED` cases but not imposed on explanations that state a clear direction. **Automatic heuristic parsing:** rejected because keywords and mixed prose can be ambiguous and would hide interpretive intervention. **Prompt/cap change or model removal:** rejected as disproportionate to the isolated replacement-panel failure.
- Consequences: Primary evaluation is now blocked until one all-invalid Decision adjudication batch is complete. Exact-parsed and adjudicated labels remain distinguishable; the original token cost and invalid status remain reportable. Human coding becomes a disclosed operational intervention and potential validity threat, controlled by the frozen rubric, complete-case review, evidence restriction, preserved rationale, unresolved category, per-model reporting, and sensitivity analysis. The current validation-only pilot is labeled `evaluation_existed_not_consulted` because evaluation descendants already existed when this policy was adopted; it does not enter primary estimates. No Decision-specific model rerun is required.
- Affected files/configurations/runs: Canonical protocol/experiment/execution documents, rubric configuration, independent adjudication schema/tools, pilot review, `TASKS.md`, `PROJECT_STATUS.md`, `KNOWN_ISSUES.md`, and canonical adjudication `decision-adjudication-pilot-six-models-20260804-r2` / `run_387a281ce89a3147e1d4b0da`. Existing inference `run_4b0bdec98ae531232cfe9f30`, its invalid call, and every raw response remain unchanged. Pre-commit implementation attempt `r1` is preserved but superseded by `r2` for provenance.
- Supersedes or superseded by: Prospectively refines the unconstrained categorical Decision execution retained by `DEC-20260804-28`; does not alter `DEC-20260804-26` candidate/Critique/Plan handling.

## DEC-20260804-30: Classify EvalPlus per-input limit exhaustion as timeout

- Date: 2026-08-04
- Status: Adopted
- Context: The same deterministic Qwen3 Direct candidate for `HumanEval/129` passed in six-model evaluation `r1` but failed only the plus suite in corrected-provenance evaluation `r2`, despite identical source and evaluator-configuration hashes. EvalPlus 0.3.1 catches its per-input `TimeoutException` in the same broad handler as assertion and ordinary candidate exceptions, records only `details[i] = False`, and later returns functional `FAIL`. Existing raw output therefore cannot distinguish a time-limited input from an incorrect result. Repeated diagnostics completed the same candidate successfully, making transient per-input limit exhaustion the conservative explanation, although the old raw record cannot prove the exact cause retrospectively.
- Decision: Keep the pinned datasets, inputs, expected outputs, canonical solutions, tolerances, and special oracles byte-for-byte unchanged. In adapter `self-refinement-isolated-v4`, instrument only the official per-input timer wrapper and preserve every timed-out input index in raw evaluator output. Convert an upstream suite `FAIL` to `TIMEOUT` only when all observed false details are explained by those timeout indexes. If any non-timeout false detail exists in either base or plus suite, classify the candidate as functional `FAIL`; a known failure takes precedence over an unresolved timeout in the other suite. Feed provisional `TIMEOUT` through the already frozen one-confirmation policy.
- Rationale: Time-limit exhaustion does not establish functional incorrectness, and the confirmation stage exists specifically to resolve this uncertainty under a longer limit. Input-level attribution avoids converting a candidate with an independently proven wrong result into a timeout. Keeping the evaluator data and oracle unchanged preserves the benchmark construct while correcting a local classification loss in the execution wrapper.
- Alternatives considered: Disable or inflate EvalPlus's internal limits; modify the installed evaluator or benchmark tests; retain the swallowed timeout as `FAIL`; mark every mixed failure/timeout as `TIMEOUT`; or reclassify old records in place. These respectively weaken resource control, alter upstream semantics, risk false functional failures, ignore already conclusive failures, or violate immutable raw-record lineage.
- Consequences: EvalPlus manifest advances to `evalplus-benchmarks-2026-08-04-r5`, adapter `v4`, SHA-256 `f9d20de1f288f676ffb76419faa31896468e68a00bf403d832d27c921f433c9b`; exact `r4` bytes remain archived with SHA-256 `9aa437375b60cd507b097ed6e1251e27128bd9be9d301afdb905bc9ad514afc6`. Evaluator configuration records the classification mode and evaluation-run manifests pin both benchmark manifest versions/adapters and exact hashes. The validated six-model `r2` evaluation and its review remain immutable but cannot freeze the experiment because their functional `FAIL` set may include an unobservable internal timeout. The same 216 candidates require a clean replacement evaluation; no model call, prompt, Decision, candidate, benchmark test, or reference timing audit is regenerated.
- Affected files/configurations/runs: EvalPlus worker/adapter/configuration, benchmark manifest and archived `r4`, evaluation campaign provenance/validation, primary scope `r2`, canonical evaluation documents, tests, six-model evaluations `r1`/`r2`, and pilot review `r3`.
- Supersedes or superseded by: Refines the failure/timeout separation in `DEC-20260802-02`, `DEC-20260802-07`, and `DEC-20260804-25`; timeout values and the exactly-one-confirmation rule are unchanged.

## DEC-20260804-31: Freeze the six-model primary experiment configuration

- Date: 2026-08-04
- Status: Adopted
- Context: The complete six-model replacement inference, separately validated Decision adjudication, and adapter-v4 candidate evaluation now satisfy the pilot gate. Evaluation `run_38cf240201dfb892765eccc2` preserves all 216 exact candidates, 216 primary attempts, 11 timeout confirmations, 216 final resolutions, and 227 raw evaluator outputs with zero evaluator failures. Review `pilot-review-six-models-20260804-r4` observes the expected 378 model calls, 216 candidates, 54 effective Decisions, and 162 effective derived outcomes and passes with no automated blocker. Representative response paths are byte-identical to the previously reviewed inference artifacts; direct review of all new timeout traces confirms the adopted timeout-only versus independent-failure precedence rule.
- Decision: Adopt the exact draft3 template bytes as frozen prompt set `primary-prompts-2026-08-04-r1` without changing any template, parser, stage input, or output cap. Freeze the primary experiment at schema `3.0.0`; study `study-v0.2.0`; six-model manifest `model-checkpoints-2026-08-04-r2`; inference `primary-inference-2026-08-04-r3`; public scope `primary-scope-2026-08-04-r2`; EvalPlus manifest `evalplus-benchmarks-2026-08-04-r5`; BigCodeBench manifest `bigcodebench-instruct-2026-08-03-r6`; timeout policy `candidate-timeouts-2026-08-04-r2`; Decision rubric `decision-adjudication-2026-08-04-r1`; and model-resident schedule `model-resident-all-benchmark-2026-08-03-r1`. Enable prospective full-scope campaign `model-campaign-2026-08-04-r2` with the common batch-invariant serving path and operational batch size 32.
- Rationale: The pilot validates complete artifact production for every candidate-producing stage, common parser treatment across all six models, exact initial/critique/plan reuse, Decision adjudication without evaluation feedback, evaluator separation, and explicit timeout attribution. Assigning a new frozen prompt-set identity makes the prospective primary boundary explicit while retaining exactly the reviewed template hashes. Batch size affects scheduling and throughput rather than the generated distribution under the validated batch-invariant path and is common to all models and stages.
- Alternatives considered: Change prompt wording after observing pilot responses; use the draft3 label directly as a primary identity; retain the old blocked four-model campaign file; lower the primary batch size to the nine-task pilot size; or delay freeze for another pilot. Prompt changes would require another version and pilot, reusing a draft label would obscure the freeze boundary, mutating the historical campaign would break configuration provenance, batch size nine would unnecessarily restrict throughput, and no unresolved construct or implementation blocker justifies another pilot.
- Consequences: Primary inference may now start only from `configs/experiments/model_campaign_six_models.toml`. The older `model_campaign.toml`, all prior prompt manifests, pilots, evaluations, and reviews remain immutable history. Invalid Decisions, if any, must be read as one complete batch after inference validation and before evaluation, using only prompt-visible inputs and never benchmark evaluation results; exact and separately read cases remain distinguishable and sensitivity analysis excludes the latter. Critique/Plan can contain focused code and fences under `DEC-20260804-26`; their prompts still prohibit a complete revised solution, and model compliance is reported rather than semantically guessed by the parser. Any post-freeze change capable of affecting candidates, selections, evaluation outcomes, task scope, or comparisons requires a new configuration/study version, impact assessment, and any necessary replacement run.
- Affected files/configurations/runs: `configs/prompts/primary_frozen.toml` (SHA-256 `402ade307a4959f326558d3612d163b8eb96bcc5c34f7a70fb438fa83a47ba77`), `configs/experiments/model_campaign_six_models.toml` (SHA-256 `05fc9a14156804931b7ee7411a1eb2d2aaefafd262ce11646a1c41036dbda95d`), `configs/experiments/primary_scope_v2.toml` (SHA-256 `fb8af6b3cf5a17c63d2e7174af65ee22bd9bd8db8614f6978a0d94c2035873f5`), `configs/inference/primary_six_models.toml` (SHA-256 `d136c5af178ace0480209be85e1c6725d24742e92208e1864c6a9cbfa324d09e`), evaluator/timeout/rubric manifests, `TASKS.md`, `PROJECT_STATUS.md`, `KNOWN_ISSUES.md`, `EXPERIMENT_RUNBOOK.md`, evaluation `run_38cf240201dfb892765eccc2`, and review `pilot-review-six-models-20260804-r4`.
- Supersedes or superseded by: Completes the pre-primary gates required by `DEC-20260804-26`, `DEC-20260804-28`, `DEC-20260804-29`, and `DEC-20260804-30`. It does not alter those decisions or rehabilitate invalidated historical evaluation runs.

## DEC-20260804-32: Freeze the raw-to-processed and RQ analysis contract before primary results

- Date: 2026-08-04
- Status: Adopted
- Context: Full-scope model-artifact generation is active, but no primary evaluation or result dataset exists. RQ1–RQ4 already define paired correctness, repair/regression, Decision-conditioned effects, and token cost, while the implementation still needed explicit rules for nonfunctional outcomes, retry-aware token accounting, confidence intervals, candidate-change normalization, Decision adjudication sensitivity, and package-ready provenance. These rules must be fixed without consulting partial primary outcomes.
- Decision: Adopt `analysis_tools/analysis_config.toml` and `documents/08_analysis_pipeline.md` as analysis version `primary-analysis-2026-08-04-r1`. Build a complete model-task-protocol grid from only terminal independently validated inference/evaluation runs and a validated complete Decision adjudication when required. Keep final `TIMEOUT`, evaluation failure, missing artifacts, and unresolved Decisions distinct from functional `FAIL`; use paired complete cases with explicit excluded counts. Record exact and conservative whitespace-normalized candidate change. Separate actual attempt-level Experimental Token Consumption from Protocol-Implied incremental and end-to-end costs. Use deterministic 10,000-resample task-level paired bootstrap 95% confidence intervals and supplementary exact two-sided McNemar tests. Report RQ3 for all resolved Decisions and an exact-only sensitivity excluding adjudicated cases; treat initial-pass-rate Pearson/Spearman relationships as descriptive. Use common-complete-case tasks for within-model correctness-cost Pareto comparisons, and leave tokens-per-additional-correct undefined unless the correctness increment is positive. Generate immutable checksummed processed/RQ manifests suitable for later allowlist promotion into paper and replication packages.
- Rationale: Explicit missingness prevents resource or infrastructure outcomes from becoming false correctness labels. Paired complete-case comparisons preserve the shared-task design, while exclusion counts expose any loss of coverage. Attempt-level and logical protocol-level cost tables answer different questions and must not be conflated. Deterministic seeds, conservative normalization, and immutable manifests make every number reproducible and traceable without adding analysis dependencies during the active experiment.
- Alternatives considered: Count final timeouts as functional failures; use all-row denominators with imputed outcomes; compare unpaired aggregate rates; normalize code with a formatter or AST; count the seven physically generated calls separately for every protocol; omit adjudicated cases entirely; fit a post hoc regression after seeing outcomes; or use protocol-specific available cases for Pareto frontiers. These respectively alter correctness, obscure missingness, discard pairing, risk semantic source changes, multiply shared experimental cost, lose the adopted complete-case Decision recovery, invite researcher degrees of freedom, or compare costs/correctness on different task sets.
- Consequences: Primary results cannot be processed until both source runs pass independent validation. A primary processed dataset is created once per analysis/input version, then RQ1, RQ2, RQ3, and RQ4 are generated and reviewed sequentially under distinct immutable output directories. Any outcome-informed metric change requires a new analysis version and documented supersession. Additional inferential regression is not part of this frozen version. This operationalizes the existing RQs and does not change the study version, model calls, benchmark scope, evaluator, or generated candidate construct.
- Affected files/configurations/runs: `analysis_tools/`, `documents/08_analysis_pipeline.md`, `EXPERIMENT_RUNBOOK.md`, package staging READMEs, `TASKS.md`, and `documents/PROJECT_STATUS.md`. Accepted pilot inference/evaluation/adjudication were used only for an ephemeral `/tmp` structural smoke test; no pilot metric is promoted or indexed as a result. Active primary inference `run_c99d3b1d562acc3e80026e48` is not read or modified by the analysis implementation.
- Supersedes or superseded by: Operationalizes the statistical and metric plan in `documents/03_research_questions.md` and `documents/04_experiment_plan.md`; supersedes no study construct or prior result because no primary processed result exists. Its malformed-candidate missingness rule is refined prospectively by `DEC-20260806-34`.

## DEC-20260806-33: Separate deterministic Decision normalization from non-exact response reading

- Date: 2026-08-06
- Status: Adopted
- Context: Terminal primary inference contains 202 strict-parser-invalid Decisions. DeepSeek produced 156 responses whose complete trimmed content is exactly `PRESERVE.`; Qwen3 produced 46 length-capped explanations that begin with and unambiguously support one categorical direction. No primary candidate evaluation existed when these responses were inspected.
- Decision: Preserve every original invalid call and raw response. Under rubric `decision-adjudication-2026-08-06-r2`, first apply only `decision-terminal-period-2026-08-06-r1`: trim surrounding whitespace and remove one final ASCII period iff the whole response is `PRESERVE.` or `REFINE.`. Record those cases as `normalized`. Review every remaining invalid response once with only the raw response, task specification, and exact initial candidate, recording `adjudicated` or `UNRESOLVED`; never consult evaluation, tests, diagnostics, timeouts, critique, plan, or revision output.
- Rationale: Punctuation removal is deterministic formatting normalization rather than semantic interpretation. Keeping it distinct from the evaluation-result-free reading of non-exact responses exposes the intervention while avoiding a fixed-value bias. The strict primary parser and raw model-compliance statistics remain unchanged.
- Consequences: Primary evaluation remains gated on one complete independently validated resolution batch. RQ3 reports exact, normalized, and separately read sources; exact-only sensitivity excludes both non-exact groups. A D-protocol candidate-selection record is created only when the Decision is resolved and the corresponding always-refine candidate exists.
- Supersedes or superseded by: Refines `DEC-20260804-29` for the terminal primary response patterns without changing generation or the original parser.

## DEC-20260806-34: Retain malformed candidates as model-attributable end-to-end failures

- Date: 2026-08-06
- Status: Adopted
- Context: Primary inference produced eight Direct responses and ten revision responses that violate the common exact-single-complete-Python-fence contract. Seven Direct cases reached the output cap with an unclosed fence and one used multiple fenced blocks. Creating or selecting code would require an unplanned repair. Excluding their model-task rows would favor models that fail to produce a usable candidate.
- Decision: Do not salvage incomplete, missing, or multiple fences and do not rerun or exclude the affected model-task pairs. Preserve legacy raw statuses, but use `malformed_candidate` in processed data and reporting. A complete single-fenced payload remains a candidate even when syntactically or functionally wrong. Do not fabricate evaluator functional `FAIL`; instead set the separate end-to-end success measure to 0 for a model-attributable malformed initial or final candidate. Keep TIMEOUT and evaluator/infrastructure failures indeterminate. Initial-to-final functional transitions remain restricted to actually evaluated candidates.
- Rationale: This keeps the intended denominator and attributes instruction/output failure to the model without claiming that benchmark tests established functional incorrectness. It also keeps timeout treatment conservative and avoids outcome-dependent code repair.
- Consequences: Analysis advances to `primary-analysis-2026-08-06-r2`. The archived r1 contract remains reproducible. RQ1 and correctness-cost comparisons use end-to-end success as primary and report conditional evaluator pass rates/malformed counts separately; RQ2 reports malformed initials outside repair/regression transitions.
- Supersedes or superseded by: Refines the missingness portion of `DEC-20260804-32`; it does not change the frozen inference artifacts, candidate extractor, evaluator, timeout policy, or task scope.

## DEC-20260806-35: Export immutable versioned paper-writing snapshots

- Date: 2026-08-06
- Status: Adopted
- Context: Validated primary model responses and Decision-response processing now exist while candidate evaluation is still active. Paper writing already needs the adopted design, exact setup, original responses, and execution provenance, but copying the working directory would mix accepted inputs with pilots, failures, active partial results, caches, and local-only material. The package will be regenerated repeatedly as evaluation and RQ results become independently validated.
- Decision: Generate each internal `paper_writing_package` snapshot from an explicit versioned inclusion profile and a unique never-reused package ID. Require a clean committed source revision and independently validated terminal source attempts. Copy selected readable documents/configurations and archive selected large validated raw sources deterministically; include the exact committed repository source as implementation provenance. Record data lineage, run/attempt identifiers, source validation hashes, availability flags, every exported file's SHA-256, and the state of related active work. Exclude active or unvalidated result raw data rather than promoting partial outcomes. Build in a separate directory and atomically promote it without overwriting. Accept an export only after a separate validator checks the complete file set, hashes, archive member paths, required sections, and result-availability declarations and records `validation_result=passed` in both package and durable export attempt.
- Rationale: A frozen allowlisted snapshot lets authors inspect how available evidence was produced without treating incomplete evaluation as a result. Deterministic archives keep hundreds of thousands of immutable registry files manageable, while readable design and provenance sections avoid forcing authors to reconstruct the study from raw storage. A new profile and ID for each later snapshot makes changes visible and prevents silent replacement.
- Alternatives considered: Copy the full working directory; export only narrative documents; link to mutable raw directories; or wait until all results exist. These approaches respectively mix invalid history and local material, omit the evidence needed to audit methods, allow later mutation to change package meaning, or delay method and validity review unnecessarily.
- Consequences: Pre-results profile `paper-writing-pre-results-2026-08-06-r1` may include validated primary inference, non-exact Decision direction records, accepted reference timing, frozen settings, and preparation evidence. It explicitly excludes the active candidate-evaluation registry, processed data, RQ outputs, tables, and figures and therefore cannot support paper result claims. Later accepted data require a new profile version and package ID. This is an internal authoring package, not the sanitized public replication package.
- Affected files/configurations/runs: `configs/packages/paper_writing_pre_results_v1.toml`, `src/self_refinement/packaging/`, `scripts/export_paper_writing_package.py`, `scripts/validate_paper_writing_package.py`, `paper_writing_package/README.md`, package export attempts under `runs/logs/paper-package-export/`, `TASKS.md`, and `documents/PROJECT_STATUS.md`. No model call, candidate, evaluation record, analysis result, or study construct is changed.
- Supersedes or superseded by: Operationalizes `documents/PACKAGE_PREPRATION_GUIDELINE.md`; its full-registry inclusion scope is superseded by `DEC-20260806-36` after author review.

## DEC-20260806-36: Keep the paper-writing package author-facing rather than replication-complete

- Date: 2026-08-06
- Status: Adopted
- Context: Initial pre-results export `paper-writing-pre-results-20260806-r1` completed before independent validation and occupied 683 MiB. Its primary-inference tar contained 242,179 registry files: 70,386 ordinary raw responses, 70,386 model-call records, and parsed/derived artifacts. The 40,206 evaluated candidates are only one subset of that registry. Complete raw responses largely duplicate strictly parsed candidates, critiques, plans, and Decisions, while the paper author mainly needs method settings, concise provenance/token data, inspectable model artifacts, and traceability to immutable working sources. Full raw preservation is more appropriate for the working repository and later replication package.
- Decision: Do not accept or independently validate `r1` as the authoring package. Adopt compact authoring profile `paper-writing-pre-results-2026-08-06-r2`. Exclude ordinary raw model responses, benchmark release bytes, the complete repository archive, complete reference-observation trees, and the full chronological task/run/issue logs. Consolidate task/model/prompt/run metadata and strictly parsed candidates, critiques, plans, exact Decisions, and D-protocol candidate selections into one JSONL file per artifact type. Replace individual model-call records with one CSV row per call containing model/task/stage identifiers, status, finish reason, token counts, elapsed time, prompt/request hashes, immutable call-record path/hash, and raw-response path/hash. Copy raw response bytes only for model-format exceptions (`malformed_candidate` and non-exact Decision responses), because their original text is needed to inspect why no ordinary parsed artifact exists. Include complete compact records of the separately performed non-exact Decision direction readings. Include accepted reference-timing configuration/status/summary files but not every observation file. Export only explicitly selected adopted decisions and interpretation-relevant issues.
- Rationale: The authoring package should optimize comprehension and evidence lookup, not duplicate durable storage. Consolidated files make quantitative inspection practical, while source paths and cryptographic hashes retain exact traceability. Keeping the small format-exception raw subset preserves the evidence required to discuss model compliance and malformed outputs without copying every successful response.
- Alternatives considered: Retain the complete validated registry; omit all model outputs; include only aggregate counts; or move every raw file into the compact package as compressed data. These respectively conflate authoring with replication, prevent qualitative inspection, weaken auditability, or reduce storage without reducing conceptual clutter.
- Consequences: Package `r1` remains completed export evidence with pending validation plus a separate `review.json` disposition of `not_accepted`; it must not be cited or treated as accepted. Its full derived copy was later retired under `DEC-20260806-37`, while small manifest/review evidence and all source raw inference remain preserved. Package `r2` must independently validate its one-row-per-call inventory, token arithmetic, record uniqueness, exact exception-raw coverage, consolidated JSONL counts, hashes, and explicit absence of full tar archives before acceptance. Later evaluation/RQ snapshots follow the same compact-authoring principle, while the replication package may include or retrieve complete raw sources under a separate public-release policy.
- Affected files/configurations/runs: `configs/packages/paper_writing_pre_results_v2.toml`, paper-package exporter/validator, `paper_writing_package/README.md`, `TASKS.md`, `documents/PROJECT_STATUS.md`, completed but non-accepted export `paper-package-pre-results-20260806-r1`, and its compact successor. No model, benchmark, prompt, candidate, evaluation, or analysis construct changes.
- Supersedes or superseded by: Supersedes only the paper-package content-selection portion of `DEC-20260806-35`; immutable/versioned/atomic/independently validated export rules remain adopted.

## DEC-20260806-37: Keep one Git-tracked paper-writing package at the stable root

- Date: 2026-08-06
- Status: Adopted
- Context: The first exporter placed complete snapshots under `paper_writing_package/data/<package-id>/`, which made the authoring directory look like a version archive rather than the current set of materials for writing the paper. The package will be refreshed repeatedly, while Git already records changes to repository content. Keeping full old snapshots beside the current one duplicates hundreds of MiB and makes it unclear which tree an author should use.
- Decision: Make `paper_writing_package/` itself the only current authoring snapshot. Place its `README.md`, `study_design/`, `experiment_setup/`, `data/`, `process_record/`, `provenance/`, `source/`, `results/`, manifest, checksums, and validation directly below that root. Track this tree in Git. Continue assigning a unique package ID internally and build every new export in its durable attempt; independently validate the complete build before replacing the stable root. Do not retain version-named snapshot directories or a `latest/` directory inside `paper_writing_package/`. Preserve only small publication metadata in attempts; rely on Git for prior authoring-tree contents and on immutable working storage for source raw artifacts.
- Rationale: A paper author can always open one obvious directory and see the current package, while Git provides ordinary change history without parallel directory trees. Attempt-local construction and validation prevent an incomplete package from becoming current. Separating compact authoring history from immutable experimental raw storage keeps publication replacement from altering research evidence.
- Alternatives considered: Keep `data/<package-id>/` snapshots; add a `latest/` directory or symlink; retain every validated snapshot under the package root; or overwrite files in place before validation. These retain unnecessary navigation or duplication, create pointer ambiguity, or expose partially generated contents.
- Consequences: Validated compact package `paper-writing-pre-results-20260806-r2` is published directly at `paper_writing_package/` and remains identified by its manifest rather than its directory name. Rejected r1 retains its review, status, manifest, checksum index, and README in its durable attempt, but its 683 MiB regenerable derived copy is removed. The source inference registry, raw responses, candidate evaluation, and all experiment artifacts are untouched. Future independent validation with an attempt ID publishes the validated attempt-local snapshot to the stable root and marks the prior attempt as replaced.
- Affected files/configurations/runs: `paper_writing_package/`, `.gitignore`, package exporter/validator/publication code, `paper-package-pre-results-20260806-r1`, `paper-package-pre-results-20260806-r2`, `TASKS.md`, `documents/PACKAGE_PREPRATION_GUIDELINE.md`, and `documents/PROJECT_STATUS.md`. No study construct, model call, benchmark, candidate, evaluator outcome, or analysis result changes.
- Supersedes or superseded by: Supersedes the multiple-full-snapshot and never-replace publication portions of `DEC-20260806-35`; unique IDs, attempt-local immutable builds, allowlisted contents, independent validation, and atomic promotion remain adopted. It does not change the compact content boundary in `DEC-20260806-36`.

## DEC-20260806-38: Permit explicit non-paper-facing progress analysis during timeout confirmation

- Date: 2026-08-06
- Status: Adopted
- Context: The complete 40,206-candidate primary evaluation batch is available, while 387 deferred timeout confirmations may take many hours. The frozen RQ pipeline deliberately rejects nonterminal evaluation runs, but implementation and missingness checks benefit from extracting every RQ over the currently determinate subset before final completion.
- Decision: Keep the terminal independently validated gate unchanged for every final processed dataset and paper-facing result. Separately permit an explicit provisional mode only while the named evaluation attempt is actively in `confirmation`: freeze the identity and SHA-256 of every evaluation record present at one capture time; require the complete primary batch; synthesize in-memory timeout-policy resolutions only where the primary result is non-timeout or its one confirmation is already present; leave pending confirmations unresolved; retain the complete model-task-protocol grid; write only under `data/interim`; require `result_status=provisional`, `paper_facing=false`, and an explicit RQ opt-in; and generate a consolidated report of pending coverage and evaluator failures.
- Rationale: A frozen record index makes the progress view reproducible even as the campaign continues. Explicit indeterminate rows expose selection-by-confirmation-order and prevent partial coverage from masquerading as final evidence, while running all RQs now tests the complete transformation and metric machinery before the terminal handoff.
- Alternatives considered: Weaken the ordinary source-run validator; copy active registry resolutions into `data/processed`; classify pending confirmations using primary timeout; wait without exercising full-scope analysis; or recompute a mutable dashboard in place. These respectively risk accepting partial results, mix provisional and canonical data, create false final outcomes, defer error discovery, or destroy capture provenance.
- Consequences: Provisional RQ numbers may change as confirmations finish and cannot be promoted, cited, or added to the paper-writing package. The final evaluation must still reach terminal state, pass independent validation, and be transformed again under new dataset/analysis identifiers using stored `EvaluationResolutionRecord` artifacts. Evaluator/infrastructure failures stay indeterminate and require separate resolution rather than imputation.
- Affected files/configurations/runs: `analysis_tools/`, `documents/08_analysis_pipeline.md`, `EXPERIMENT_RUNBOOK.md`, `TASKS.md`, project-state documents, and active attempt `evaluation-full-candidates-20260806-r1`. No active evaluation record, model artifact, timeout policy, benchmark input, or study construct is changed.
- Supersedes or superseded by: Complements `DEC-20260804-32`; it does not relax or supersede its final-analysis gate.

## DEC-20260806-39: Display RQ3 correctness difference as repair-regression decomposition

- Date: 2026-08-06
- Status: Adopted
- Context: The first non-paper-facing progress snapshot makes the integrated `R`/`DR`, `CR`/`DCR`, and `CPR`/`DCPR` correctness differences easy to inspect, but an integrated difference alone does not show how much Decision conditioning prevents regression versus loses repair. RQ2 already predeclares repair/regression balance for every protocol, and RQ3 already predeclares Prevented Regression and Missed Repair as primary evidence.
- Decision: Add an explicit RQ3 output table, without changing the underlying estimand or analysis version. For each model-benchmark, protocol pair, and Decision-provenance sensitivity, restrict to tasks with determinate initial, always-refine final, and Decision-conditioned final functional outcomes. On this same subset, report both repair counts/rates among initially incorrect tasks, both regression counts/rates among initially correct tasks, lost repairs, prevented regressions, each condition's repair-minus-regression count, and the identity `net correctness difference = prevented regressions − lost repairs`. Keep the existing end-to-end paired contrast, malformed-candidate treatment, and missingness reporting unchanged.
- Rationale: Using one common functional-transition subset makes the two mechanisms directly comparable without imputation. This is a clearer presentation of outcomes already frozen in RQ2/RQ3, not a result-selected new hypothesis, covariate, subgroup, or test.
- Alternatives considered: Report only integrated pass-rate difference; compare repair/regression rates on protocol-specific available subsets; count timeout or evaluator failure as incorrect; or introduce a new post-hoc inferential model. These respectively obscure mechanism, change denominators, violate outcome semantics, or expand researcher degrees of freedom.
- Consequences: RQ3 gains one machine-readable CSV/JSON table and regression tests. Existing provisional output remains immutable and is superseded for review by a new analysis ID over the same frozen processed snapshot. The final terminal dataset will use the same decomposition. No model call, evaluation, timeout resolution, processed row, or study construct changes.
- Affected files/configurations/runs: `analysis_tools/rq_metrics.py`, RQ analysis tests, `documents/08_analysis_pipeline.md`, `TASKS.md`, project-state documents, and future RQ3 outputs.
- Supersedes or superseded by: Clarifies the presentation of `DEC-20260804-32`; it changes no adopted estimator.

## DEC-20260806-40: Replace overlapping Critique/Planning roles with a role-separated follow-up

- Date: 2026-08-06
- Status: Adopted
- Context: Non-paper-facing v0.2.0 results showed no clear benefit from adding Critique or Planning,
  but the frozen prompts did not isolate their roles: Critique requested problems, locations, and
  reasons; Planning repeated changes and locations; CPR Revision received both artifacts. Because a
  different Planning construct could plausibly change the result, that run cannot cleanly answer the
  intended stage-composition question.
- Decision: Retain every v0.2.0 artifact, script, prompt, configuration, and provisional result as
  immutable formative/reference evidence. Advance the paper-facing protocol to `study-v0.3.0`.
  Reuse exact validated Initial Candidates, Direct Revision candidates, Decisions, Decision readings,
  and their evaluations. Regenerate only Critique, Critique-Conditioned Revision, Revision Planning,
  and Plan-Conditioned Revision. Critique identifies functional root cause/location; Planning converts
  that diagnosis into concrete minimal changes and preserved behavior; CR Revision receives Critique;
  CPR Revision receives Plan only. Text artifacts remain raw non-empty model outputs even if they
  incidentally cross a role boundary. Freeze prompt bytes before new outcomes.
- Rationale: The direct input boundary gives each stage one primary responsibility without a long
  prohibition list or post-hoc content deletion. Reusing exact unaffected artifacts preserves pairing,
  avoids unnecessary model calls, and prevents result-dependent resampling.
- Alternatives considered: Treat v0.2.0 as final; remove Planning; ask for Plan without Critique;
  pass both Critique and Plan again; or invalidate text artifacts that mention another role. These
  leave the construct ambiguity, answer a different question, preserve redundant inputs, or introduce
  subjective parsing.
- Consequences: v0.3.0 uses a composite lineage and requires new CR/CPR evaluation plus analysis
  tooling that joins two validated inference sources. The four new phases run as independently
  restartable attempts in order C, CR, P, CPR under one automatically advancing supervisor. Phase
  reload overhead is accepted for failure isolation. Historical v0.2.0 CR/CPR estimates must never be
  pooled with v0.3.0 estimates.
- Affected files/configurations/runs: canonical design documents, `prompts/v4/`,
  `configs/prompts/role_separated_frozen.toml`, `configs/experiments/primary_scope_v3.toml`,
  `configs/experiments/role_separated_campaign.toml`, the dedicated runner, and future child run of
  `run_c99d3b1d562acc3e80026e48`.
- Supersedes or superseded by: Supersedes v0.2.0 C/P/CR/CPR as the paper-facing construct; does not
  alter the source Direct/Decision/R calls, evaluator, benchmark scope, model panel, or inference settings.

## DEC-20260807-41: Add a single-call versus multi-call protocol axis

- Date: 2026-08-07
- Status: Adopted
- Context: The role-separated v0.3.0 design externalizes Critique, Planning, Decision, and Revision
  across observable calls and artifacts. Related planning work also motivates asking whether the same
  roles perform differently when their order is stated in one prompt. This is a prospective RQ
  motivated by study positioning rather than by accepting the still-incomplete v0.3.0 outcomes.
- Decision: Advance the paper-facing composite design to `study-v0.4.0`. Retain and reuse exact
  v0.2.0 Initial/Direct Revision/Decision artifacts and role-separated v0.3.0 C/P/CR/CPR artifacts.
  Add five one-call generated conditions: `SC-CR`, `SC-CPR`, `SC-DR`, `SC-DCR`, and `SC-DCPR`.
  Each receives only the task specification and exact initial candidate. `SC-CR` and `SC-CPR`
  emit code. `SC-D*` emit an exact first-line Decision field and code in the same response. The main
  candidate is emitted code regardless of the label; label-enforced selection is supplementary.
  Parse the code and label independently and retain malformed/invalid components explicitly. Do not
  manually adjudicate invalid integrated labels. Define this comparison as RQ4 and renumber the
  whole-panel correctness/token cost question to RQ5.
- Rationale: This adds call topology as a controlled protocol axis while preserving shared initials,
  model panel, benchmarks, inference settings, and feedback-free inputs. Evaluating emitted code makes
  `PRESERVE`-with-change observable and directly contrasts the exact-selection guarantee of a separate
  Decision. It avoids claiming that unobserved internal reasoning followed the named roles.
- Alternatives considered: Compare only C-R and C-P-R; omit integrated Decision conditions; treat
  `SC-DR` as identical to `R`; enforce the label before the main evaluation; or ask for separate C/P
  text inside one response. These lose aligned comparisons, hide Decision/code inconsistency, conflate
  an explicit label with implicit review, replace the generated candidate post hoc, or change the
  final-output contract and token path.
- Consequences: The new run adds at most 50,310 task-condition units and candidate evaluations. Keep
  one model resident across all five conditions with batch size 32, reducing normal model loads from
  30 to six. Run a six-model nine-task pilot before opening the full gate. Candidate evaluation is a
  separate campaign with exactly two workers, and the default schedule does not overlap GPU inference
  with CPU evaluation. The analysis pipeline must join three validated inference lineages and expand
  from seven to twelve main protocol rows per model-task pair.
- Affected files/configurations/runs: canonical design documents, `prompts/v5/`,
  `configs/prompts/single_call_frozen.toml`, `configs/experiments/single_call_*`, schemas, protocol and
  evaluation runners, runbook, analysis plan, and future pilot/full v0.4.0 runs. No existing raw record,
  model response, candidate, evaluation, or v0.2.0/v0.3.0 configuration is modified.
- Supersedes or superseded by: Extends `DEC-20260806-40`; it does not supersede the role-separated
  multi-call construct, which becomes the comparison baseline. Renumbers the prior RQ4 cost analysis
  to RQ5 without changing its metrics.

## DEC-20260807-42: Approve the single-call pilot and chain full inference through evaluation

- Date: 2026-08-07
- Status: Adopted
- Context: The six-model nine-task single-call pilot completed all 270 calls with immutable raw
  responses, zero inference failures/timeouts, and 162/162 exact integrated Decision labels. Four
  responses (one DeepSeek, three Qwen3) returned multiple complete Python fences despite the explicit
  one-fence contract, leaving 266 valid candidates. This is observable model format noncompliance,
  not parser or infrastructure failure. Full single-call inference and both still-pending v0.3.0 and
  v0.4.0 candidate evaluations are long-running and should not require manual handoff between stages.
- Decision: Accept the pilot without changing prompt or parser bytes. Retain the four malformed
  candidates as model-attributable failures in their planned denominators. Enable full configuration
  `single-call-comparison-2026-08-07-r2`. Run one durable supervisor in the fixed order full
  single-call inference, independent inference validation, role-separated CR/CPR evaluation with two
  workers and validation, then single-call evaluation with two workers and validation. Do not overlap
  GPU inference with either CPU evaluation. Preserve every child as an independently restartable
  attempt and stop the supervisor immediately if a child fails validation.
- Rationale: The pilot demonstrated that every failure mode is already represented by the frozen raw
  record and malformed-candidate policy. Strengthening the prompt after observing these responses
  would create a new treatment without evidence that it eliminates the behavior. A waiting supervisor
  removes manual gaps while preserving the intended no-overlap schedule and phase-level recovery.
- Alternatives considered: Reject the pilot and revise prompts; extract one of multiple fences;
  silently retry malformed responses; start evaluations concurrently with inference; or require a
  user handoff after every stage. These respectively alter the frozen treatment, introduce ambiguous
  post-processing, change deterministic calls, risk timeout contamination, or add avoidable idle time.
- Consequences: The full run may retain model-format failures and reports them by model/protocol.
  Evaluation uses exactly two workers. The supervisor is operational only: it changes no model input,
  decoding, benchmark, evaluator, timeout, or analysis construct.
- Affected files/configurations/runs: `configs/experiments/single_call_campaign.toml`,
  `configs/experiments/single_call_full_sequence.toml`, the single-call and evaluation launchers,
  `scripts/run_single_call_full_sequence.py`, runbook/status documents, pilot
  `single-call-pilot-20260807-r1`, and future full/evaluation attempts.
- Supersedes or superseded by: Operationalizes the pilot gate required by `DEC-20260807-41`; it does
  not supersede that protocol decision.

## DEC-20260807-43: Overlap independent role-separated evaluation with single-call inference

- Date: 2026-08-07
- Status: Adopted
- Context: Full single-call inference started before the already-independent v0.3.0 CR/CPR
  evaluation. The earlier no-overlap schedule treated inference as a reason to defer all evaluation,
  although the server can receive comparable external load during any evaluation and the adopted
  two-worker bound is intended to be safe under that realistic constraint. Deferring the independent
  evaluation therefore adds idle critical-path time without satisfying a stronger isolation guarantee.
- Decision: Run full single-call inference and the v0.3.0 role-separated CR/CPR evaluation
  concurrently. Keep exactly two evaluator workers, immutable separate registries, the frozen timeout
  and confirmation policy, and no evaluator-to-model feedback. Start single-call evaluation only after
  both concurrent branches independently validate because that evaluation depends on the new
  candidates. When converting the already-running sequence, terminate and supersede only its waiting
  parent supervisor; preserve and attach to the exact running inference attempt.
- Rationale: The role-separated evaluation has no data dependency on v0.4.0 inference. Two evaluator
  workers are the adopted realistic server-sharing limit, and timeout confirmation remains the
  mechanism for candidates affected by transient wall-time load. Parallelizing only independent work
  shortens the critical path without changing any model call, candidate, evaluator input, or outcome
  rule.
- Alternatives considered: Keep the prior fully sequential schedule; restart inference under a new
  parent; increase evaluator workers; or start dependent single-call evaluation before inference
  validation. These respectively waste independent execution time, discard valid work, increase
  resource pressure, or violate data dependencies.
- Consequences: Configuration advances to
  `single-call-through-evaluation-2026-08-07-r2`. The supervisor records both active child statuses,
  can attach to the existing inference attempt, and advances to single-call evaluation only after both
  branches pass validation. The replaced parent attempt is marked `cancelled_by_successor`, while its
  inference child and registry remain unchanged.
- Affected files/configurations/runs: `configs/experiments/single_call_full_sequence.toml`,
  `scripts/run_single_call_full_sequence.py`, execution documentation, sequence
  `single-call-sequence-primary-20260807-r1`, its successor, inference
  `single-call-primary-20260807-r1`, and role evaluation
  `evaluation-role-separated-primary-20260807-r1`.
- Supersedes or superseded by: Supersedes only the no-overlap ordering in `DEC-20260807-42`; pilot
  acceptance, malformed-candidate handling, worker count, child validation, and all study constructs
  remain unchanged.

## DEC-20260807-44: Retry terminal confirmation evaluator failures exactly once

- Date: 2026-08-07
- Status: Adopted
- Context: Full v0.2.0 evaluation produced one terminal infrastructure failure among 40,206
  candidates. `BigCodeBench/1042` candidate `candidate_0b876d790d64fddd621dbe81` first reached the
  frozen 10-second primary timeout; its 120-second confirmation then failed before producing a
  functional outcome with `OSError: [Errno 12] Cannot allocate memory` while creating the isolated
  worker's private temporary directory. The host later showed ample memory and disk, so transient
  server pressure is plausible but not proven. Treating the result as `FAIL` or confirmed `TIMEOUT`
  would violate the frozen analysis contract.
- Decision: For a terminal evaluation run, select the complete inventory of confirmation-stage
  `evaluation_failure` resolutions without inspecting candidate correctness and retry each exactly
  once in a separately versioned remediation run. Use the identical candidate/task bytes, evaluator
  version and configuration, timeout-policy version, and frozen confirmation timeout. Preserve the
  primary, failed confirmation, and failed resolution; write a new confirmation and replacement
  resolution whose provenance explicitly supersedes the failed records. Require independent raw,
  schema, hash, count, configuration, manifest, and supersession validation before the replacement is
  used. Refuse launch while any other evaluation campaign is active. If the one retry also has an
  evaluator failure, stop for a new decision rather than retrying again.
- Rationale: Selection on infrastructure status is independent of the unknown functional outcome,
  while a single bounded retry addresses plausible transient load without creating adaptive
  correctness-based retries. Isolating execution from the active two-worker campaign avoids adding
  the same contention suspected in the original failure. Immutable supersession retains full audit
  history and prevents silent relabeling.
- Alternatives considered: Count the case as functional `FAIL`; count it as final `TIMEOUT`; leave it
  permanently missing; rerun all 40,206 candidates; run the targeted retry concurrently with the
  active evaluation; or retry until determinate. These respectively invent a functional result,
  invent a confirmation result, unnecessarily lose coverage, repeat substantial validated work,
  risk contaminating another frozen run, or introduce unbounded outcome-dependent evaluation.
- Consequences: The operational policy is
  `retry-confirmation-evaluator-failures-once-2026-08-07-r1`. A generic durable remediation launcher
  and independent validator are required. The current source run remains immutable and ineligible for
  paper-facing analysis until remediation reports `resolved`, validation passes, and the processed
  dataset records the replacement index. This is an evaluation-completeness rule, not a protocol,
  prompt, benchmark, model, or timeout-policy change; the study version does not change.
- Affected files/configurations/runs: `scripts/remediate_evaluation_failures.py`, focused tests,
  `EXPERIMENT_EXECUTION_GUIDELINES.md`, `EXPERIMENT_RUNBOOK.md`, operational documents,
  `evaluation-full-candidates-20260806-r1`, `run_b25b1ec137928799f30217af`, and planned remediation
  `evaluation-remediation-v02-20260807-r1`.
- Supersedes or superseded by: Complements `DEC-20260802-07`, `DEC-20260803-15`, and
  `DEC-20260804-25`; it does not change their ordinary two-attempt timeout policy.

## DEC-20260807-45: Permit the one-candidate remediation beside the active evaluation

- Date: 2026-08-07
- Status: Adopted
- Context: The isolated-launch rule in `DEC-20260807-44` blocked the targeted v0.2.0 remediation
  while the two-worker v0.4.0 evaluation remained active. Before launch, the host reported about
  96 GB available memory, 24.7 GB free swap, and 14.5 TB free disk. The remediation inventory is
  exactly one already-captured candidate with one frozen 120-second confirmation attempt. The user
  explicitly accepted concurrent execution and requested that a repeated evaluator failure stop the
  process until the active evaluation finishes.
- Decision: Permit this remediation attempt to use an explicit
  `--allow-concurrent-evaluation` launch override. Keep the default active-evaluation guard for all
  other launches. Record the active attempts, resource snapshot, and override in immutable preflight
  and command metadata. Do not change the two-worker campaign, candidate bytes, evaluator, timeout,
  selection, resolution, or validation rules. If the retry is also an evaluator failure, validate and
  retain it as `unresolved` and do not launch another retry while the campaign remains active.
- Rationale: This is one bounded evaluator process rather than another campaign worker pool, and the
  observed resource headroom makes a controlled attempt reasonable. An explicit opt-in preserves the
  conservative default and the audit trail.
- Alternatives considered: Wait for the active campaign; disable the guard globally; add campaign
  workers; or retry repeatedly. Waiting remains the fallback after a repeated infrastructure failure;
  the other choices unnecessarily broaden load or retry policy.
- Consequences: The exact remediation may overlap the active campaign once. Any determinate result is
  independently validated before use. A repeated evaluator failure causes a stop, not an automatic
  follow-up attempt.
- Affected files/configurations/runs: `scripts/remediate_evaluation_failures.py`, its focused tests,
  `evaluation-single-call-primary-20260807-r1`, and
  `evaluation-remediation-v02-20260807-r1`.
- Supersedes or superseded by: Supersedes only the isolation/no-overlap clause of
  `DEC-20260807-44` for this explicit one-candidate attempt; all other clauses remain in force.
- Outcome: Attempt `evaluation-remediation-v02-20260807-r1` used the explicit override and validated
  as `unresolved`. It did not reproduce the original memory error: the managed sandbox denied the
  evaluator's netlink socket before benchmark execution. Per the adopted stop rule, no further retry
  was launched while the active campaign continued.

## DEC-20260807-46: Replace the sandbox-blocked remediation in host context

- Date: 2026-08-07
- Status: Adopted
- Context: `evaluation-remediation-v02-20260807-r1` produced no evaluator stdout and failed after
  1.758 seconds with `Cannot open netlink socket: Operation not permitted`. The failure occurred in
  the managed command sandbox before benchmark execution and therefore does not reproduce either the
  original memory failure or candidate behavior. The user identified the execution session as the
  likely cause and requested use of a different environment.
- Decision: Preserve validated unresolved `r1`, then launch `r2` through the approved host execution
  context with `r1` recorded as predecessor. Use the same source candidate, evaluator environment,
  configuration hash, 120-second timeout, and explicit one-target concurrency override. Treat `r2`
  as the scientifically meaningful remediation attempt because `r1` never started benchmark
  evaluation. If `r2` produces an evaluator failure after correct host startup, stop as previously
  decided.
- Rationale: A sandbox capability denial is an orchestration defect, not outcome-dependent evidence.
  Correcting the execution context restores equivalence with the source evaluation while immutable
  predecessor linkage retains the failed attempt for audit.
- Alternatives considered: Wait and retain `r1` as the only retry; relabel `r1`; or delete it. These
  would respectively leave a known correctable execution defect unresolved, invent an outcome, or
  destroy evidence.
- Consequences: The replacement uses a new attempt and run identity. Only a determinate, independently
  validated `r2` resolution can update the effective v0.2.0 result.
- Affected files/configurations/runs: `scripts/remediate_evaluation_failures.py`, focused tests,
  `evaluation-remediation-v02-20260807-r1`, and planned
  `evaluation-remediation-v02-20260807-r2`.
- Supersedes or superseded by: Clarifies the stop rule in `DEC-20260807-44` and `DEC-20260807-45`:
  the sandbox-blocked attempt is preserved but is not the policy's benchmark retry.
- Outcome: Host-context `evaluation-remediation-v02-20260807-r2` started the evaluator correctly but
  reproduced `OSError: [Errno 12] Cannot allocate memory` after 33.380 seconds. Independent validation
  passed with `remediation_result=unresolved`. Further retries stopped while the active evaluation
  continues.

## DEC-20260808-47: Run one isolated post-campaign remediation attempt

- Date: 2026-08-08
- Status: Adopted
- Context: The v0.4.0 two-worker evaluation and its parent sequence completed and independently
  validated. The user requested the previously deferred retry after all evaluator workers had exited,
  allowing the concurrent-load hypothesis to be tested without changing candidate, evaluator, or
  timeout inputs.
- Decision: Launch one host-context attempt with no concurrency override, record validated unresolved
  `r2` as predecessor, and retain the identical source candidate, task, evaluator configuration hash,
  and 120-second confirmation timeout. Validate the new raw output, records, manifest, and
  supersession independently. Do not launch another retry automatically.
- Rationale: Removing all other evaluator workers is the narrowest diagnostic change and directly
  tests whether the prior memory failure depended on campaign concurrency.
- Alternatives considered: Accept `r2` without isolation, change the memory limit, edit the candidate,
  or run repeated retries. These respectively leave the concurrency hypothesis unresolved or change
  frozen evaluation inputs before locating the infrastructure failure.
- Consequences: Isolated attempt `evaluation-remediation-v02-20260808-r3` completed and validated as
  `unresolved`. It reproduced `OSError: [Errno 12] Cannot allocate memory` after 26.170 seconds while
  creating `/tmp/bigcodebench-vys7djhz`, with no other evaluation active and about 104.3 GB memory
  available at preflight. This refutes evaluator concurrency as a necessary cause. The initial
  interpretation that the path proved pre-candidate failure is corrected by `DEC-20260808-48`:
  `TemporaryDirectory` cleanup uses the same path after candidate execution. Effective v0.2.0 counts
  remain unchanged.
- Affected files/configurations/runs: `evaluation-remediation-v02-20260807-r2`,
  `evaluation-remediation-v02-20260808-r3`, `run_218265fd6821b56de3e6753b`, and operational status
  documents.
- Supersedes or superseded by: Extends only the diagnostic sequence after `DEC-20260807-46`; it does
  not alter the frozen evaluator or ordinary timeout policy.

## DEC-20260808-48: Prevent disposable sandbox cleanup from masking functional results

- Date: 2026-08-08
- Status: Adopted
- Context: Isolated `r3` ruled out concurrent evaluator load but still reported `ENOMEM` on the
  worker-owned `/tmp/bigcodebench-*` path. A separate host `screen` session evaluated the exact
  `BigCodeBench/1042` reference solution under the same task, sandbox, 30 GiB limits, and hidden tests;
  it passed 5/5 in 0.264 seconds. The failed candidate's `receive_all` repeatedly concatenates a
  non-empty mocked `recv` value until memory exhaustion. `TemporaryDirectory.__exit__` can then raise
  during cleanup and overwrite the already collected unittest result. The entire `/tmp` is a private
  bubblewrap tmpfs destroyed with the worker process, so this cleanup is not needed for cross-candidate
  isolation.
- Decision: Add a remediation-only evaluator configuration that passes
  `ignore_cleanup_errors=True` to the worker's `TemporaryDirectory`. Keep strict cleanup as the normal
  adapter default. Version the remediation policy as
  `retry-confirmation-evaluator-failures-once-2026-08-08-r2`, include the cleanup policy in evaluator
  configuration hashing and run provenance, preserve `r1`–`r3`, and run a new predecessor-linked
  attempt. Do not modify candidate bytes, hidden tests, RLIMIT values, timeout, network isolation, or
  functional classification rules.
- Rationale: Cleanup of a process-private tmpfs is containment housekeeping, not part of benchmark
  correctness. Allowing it to replace an existing unittest result creates false missingness. The
  narrow opt-in exposes the candidate's actual pass/fail/timeout outcome while retaining all execution
  limits and sandbox destruction.
- Alternatives considered: Raise/remove the 30 GiB limit; change the candidate; classify the existing
  record manually; run without bubblewrap; or ignore cleanup errors globally. These change resource
  policy, model output, outcome evidence, isolation, or unrelated evaluations.
- Consequences: A regression test freezes that cleanup failure cannot mask a completed unittest
  result. Corrected remediation `r4` ran in a separate host `screen` session and independently
  validated as `resolved`: the exact retry completed as functional `FAIL` in 26.673 seconds. Its
  superseding resolution removes the sole effective evaluator failure; status counts become 40,075
  completed, 131 timeout, and zero evaluator failures. Legacy remediation validators continue to
  reconstruct the old configuration hash without the new field.
- Affected files/configurations/runs: BigCodeBench configuration/worker/local adapter, remediation
  launcher and tests, reference diagnostic `reference-1042-20260808-r1`, completed remediation
  `evaluation-remediation-v02-20260808-r4`, and registry `run_cfde994451c10e10b850905f`.
- Supersedes or superseded by: Corrects only result masking discovered after `DEC-20260808-47`; the
  frozen benchmark tests, candidate, timeout, and general v3 adapter behavior remain unchanged.

## DEC-20260808-49: Integrate performance and repair–regression balance into one RQ

- Date: 2026-08-08
- Status: Adopted
- Context: The completed results show that final pass rate alone obscures the main performance
  mechanism. CR and CPR repair more initially incorrect candidates than R, yet regress many more
  initially correct candidates. Treating stage-composition performance and repair/regression balance
  as separate research questions would split one empirical explanation across two result sections.
- Decision: Merge the former RQ1 (stage composition) and RQ2 (repair/regression balance) into a new
  RQ1, and require pass rate, paired stage contrasts, repair, regression, preservation, unrepaired
  failure, malformed output, and candidate change to be interpreted together. Renumber the former
  Decision-conditioned RQ3, topology RQ4, and cost RQ5 as RQ2, RQ3, and RQ4. Publish a new immutable
  analysis configuration, processed-dataset build, RQ output set, paper-asset set, and authoring
  package under the four-RQ identifiers.
- Rationale: The merged RQ directly explains whether a correctness difference comes from creating
  repairs or avoiding regressions and prevents high repair counts or transition-only summaries from
  being mistaken for deployable end-to-end performance. Keeping four RQs preserves the study's main
  design axes without duplicating the same outcome evidence.
- Alternatives considered: Retain five RQs; merge only the prose while keeping separate manifests;
  or replace pass rate with a single repair-minus-regression statistic. These would respectively
  fragment the explanation, leave research-question identity inconsistent across artifacts, or hide
  distinct initial-correct and initial-incorrect denominators and malformed outputs.
- Consequences: `primary-analysis-2026-08-08-r4` changes reporting organization and deterministic
  seed namespaces, but not source records, protocol definitions, missingness rules, metrics,
  estimands, bootstrap count, or experiment execution. The preceding five-RQ results remain
  reproducible history and are marked superseded for paper use. RQ1 now emits both stage-performance
  and transition/candidate-change tables, and paper assets provide one integrated performance-balance
  table.
- Affected files/configurations/runs: `analysis_tools/analysis_config.toml`, RQ executors and tests,
  research/analysis/result documents, processed dataset `primary-final-v04-20260808-r5`, analysis
  `primary-final-four-rq-20260808-r3`, and its paper assets and writing package.
- Supersedes or superseded by: Supersedes the five-RQ reporting numbering introduced by
  `DEC-20260807-41` and used by `primary-analysis-2026-08-08-r3`; it does not supersede that
  decision's single-call experimental design or any frozen data-collection rule.

## DEC-20260808-50: Add a mechanism supplement and staged prompt-ablation follow-up

- Date: 2026-08-08
- Status: Adopted
- Context: Accepted RQ3 results show that SC-CR/SC-CPR outperform their multi-call counterparts,
  while Decision-bearing aggregate differences are near zero. Aggregate correctness does not reveal
  whether this comes from regression control, whether the same model-task units change outcome, or
  whether refinement only elicits candidates already within an empirical generation envelope.
- Decision: Preserve `study-v0.4.0` and its four paper-facing RQs unchanged. Add a versioned post-hoc
  exploratory supplement with four analyses: task-set overlap, Decision mediation, empirical
  candidate reachability, and role-separated artifact-chain surface classification. Plan three
  prospective experiment options, but initially execute only option A as
  `study-v0.5.0-option-a-pilot`: `REGEN-NO-INIT`, observable `DRAFT-CR-FINAL`, and
  `C-GENERATE-NO-INITIAL`. Retain options B (Planning extensions) and C (matched-budget stochastic
  capability envelope) as gated plans requiring review of option-A results.
- Rationale: Existing immutable outcomes can answer the task-churn and regression-control questions
  without additional inference. The three option-A conditions isolate independent regeneration,
  within-response draft conditioning, and critique information without the original code. A small
  three-model, nine-task prompt/parser pilot limits GPU and evaluation cost before any population
  estimate or six-model extension.
- Alternatives considered: Immediately rerun all six models at full scope; treat equal aggregate
  accuracy as equal task behavior; add Planning and stochastic sampling in the first campaign; or
  revise the accepted RQ definitions. These respectively spend resources before mechanism checks,
  hide outcome churn, confound several interventions, or rewrite completed prospective analysis.
- Consequences: The supplement remains explicitly exploratory/post-hoc. Option-A raw responses use a
  dedicated immutable schema so the accepted primary schema and registries do not change.
  `DRAFT-CR-FINAL` preserves and parses draft, critique, and final separately. No option-B/C model
  call may start until option-A inference, evaluation, and review validate and the user chooses the
  next design.
- Affected files/configurations/runs: `analysis_tools/followup_analysis*`,
  `results/summaries/mechanism-followup-2026-08-08-r3/`, `prompts/v6_option_a/`,
  `configs/prompts/option_a_pilot_frozen.toml`, `configs/experiments/option_a_*`,
  `scripts/run_option_a_campaign.py`, canonical/operational documents, and the future
  `option-a-pilot-20260808-r1` attempt.
- Supersedes or superseded by: Extends `DEC-20260807-41` and `DEC-20260808-49`; it does not supersede
  `study-v0.4.0`, its accepted estimates, or its frozen prompts.
