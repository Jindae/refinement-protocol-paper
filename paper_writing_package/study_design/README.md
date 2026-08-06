# Feedback-Free Self-Refinement Study

This repository contains the implementation and operational records for an empirical study of feedback-free self-refinement in locally deployable open-weight code models. The files under `documents/` are the source of truth for the adopted study design. Implementation choices must not silently redefine them.

Contributors and automated agents must read `AGENTS.md`. It defines the durable
status, logging, PID-namespace, retry, and validation rules for every
long-running background job. Experiment campaigns additionally follow
`EXPERIMENT_EXECUTION_GUIDELINES.md`: one model stays resident while separate
Direct, Decision, and refinement phases each cover all three benchmarks, and
Decision-conditioned protocols are derived from stored artifacts.

## Environment setup

Python 3.12 is required for orchestration, model inference, storage, analysis,
and EvalPlus evaluation. The main lock file captures that tested environment.
BigCodeBench candidate execution uses a separate, isolated Python 3.10.12
environment matching the upstream evaluator dependency range.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --requirement requirements.lock
.venv/bin/python -m pip install --no-deps --editable .
.venv/bin/python --version
```

Do not download benchmark suites or model weights as part of repository setup.

The adopted six-model panel is pinned to exact public revisions in
`configs/models/checkpoints_v2.toml`; `configs/models/checkpoints.toml` preserves
the superseded four-model pilot manifest. Model downloads are an explicit,
durable operation rather than part of environment setup. The three retained
snapshots are already present, so the replacement-panel download selects only
the three new model IDs:

```bash
.venv/bin/python scripts/download_model_snapshots.py --start \
  --configuration-path configs/models/checkpoints_v2.toml \
  --model-id qwen2.5-coder-7b-instruct \
  --model-id devstral-small-2-24b-instruct \
  --model-id gemma-4-31b-it-qat-w4a16
.venv/bin/python scripts/download_model_snapshots.py --status
.venv/bin/python scripts/download_model_snapshots.py --count
.venv/bin/python scripts/validate_model_download.py \
  runs/logs/model-download/<attempt-id> \
  --configuration configs/models/checkpoints_v2.toml
```

The downloader writes into an immutable attempt-specific directory, validates
the remote revision and expected snapshot size, computes local file SHA-256
values, and only then promotes stable snapshot links. Partial downloads and raw
logs are retained; model bytes remain excluded from Git.

The independent validation command checks terminal metadata, manifest hashes,
exact revisions, file sets and sizes, and canonical links. Its optional
`--full-file-hashes` mode rereads every snapshot byte; for the 124 GB batch,
run that mode only through the durable background launcher:

```bash
.venv/bin/python scripts/run_model_hash_validation.py --start
.venv/bin/python scripts/run_model_hash_validation.py --status
.venv/bin/python scripts/run_model_hash_validation.py --count
```

The model-serving stack is built in a separate Python 3.12 environment so its
CUDA/PyTorch dependencies cannot alter the evaluator environment:

```bash
.venv/bin/python scripts/setup_vllm_env.py --start --attempt-id vllm-setup-20260803-r1
.venv/bin/python scripts/setup_vllm_env.py --status
```

The launcher pins the vLLM and PyTorch wheel hashes, refuses source builds,
installs the exact `requirements-vllm.lock`, records the complete install report
and package inventory, and promotes
`.venv-vllm` only after `pip check`, CUDA import, and both RTX 4090 checks pass.
Model loading and generation smoke tests are a separate validation stage.

The following four-checkpoint smoke command documents the completed historical
serving validation. Do not rerun it as the replacement-panel smoke:

```bash
.venv/bin/python scripts/smoke_vllm_models.py --start --attempt-id vllm-smoke-20260803-r1
.venv/bin/python scripts/smoke_vllm_models.py --status
.venv/bin/python scripts/smoke_vllm_models.py --count
```

The smoke configuration is validation-only and does not freeze experiment
decoding or context settings. It explicitly records vLLM's PyTorch-native
sampler because the host CUDA 11.8 compiler cannot build the optional
FlashInfer 0.6.14 sampling JIT used by the CUDA 13 wheel stack. Each model runs
in an isolated child process with offline model access and preserves its raw
repeated response and token IDs.

The three added snapshots independently validated as 45 files and
90,160,652,791 snapshot bytes. Their first compatibility gate deliberately
reuses `vllm-environment-2026-08-03-r1` rather than changing the serving stack.
It loads one TP=2 model at a time with the required 16K, batch-invariant,
PyTorch-native path and checks repeated token equality plus the common
candidate-fence response contract:

```bash
.venv/bin/python scripts/smoke_vllm_models.py --start \
  --attempt-id vllm-smoke-new-models-20260804-r2 \
  --configuration-path configs/inference/vllm_new_models_smoke_r2.toml
.venv/bin/python scripts/smoke_vllm_models.py --count \
  --configuration-path configs/inference/vllm_new_models_smoke_r2.toml
.venv/bin/python scripts/smoke_vllm_models.py --status \
  --configuration-path configs/inference/vllm_new_models_smoke_r2.toml
.venv/bin/python scripts/validate_vllm_model_smoke.py \
  runs/logs/vllm-model-smoke/vllm-smoke-new-models-20260804-r2 \
  --configuration configs/inference/vllm_new_models_smoke_r2.toml
```

Attempt `r1` is immutable architecture-loading evidence but not serving
certification: it exposed unsafe rendered-string retokenization for Devstral.
Corrected `r2` passes canonical chat-template token IDs directly to vLLM for
all models and records that input mode for independent validation.

Only a preserved, diagnosed loading failure may motivate a serving-environment
change. A replacement environment, if required, must be common to all six
models rather than model-specific.

The historical four-model primary configuration is `configs/inference/primary.toml` and is
preserved for prior pilot provenance. The frozen six-model replacement is
`configs/inference/primary_six_models.toml`. It pins all serving and tokenizer
assets, direct chat-template token-ID input, common TP=2 batch-invariant greedy
decoding, a 16K context, and the common stage output caps. Static provenance and
the full 1,677-task prompt envelope and sequential six-model GPU smoke pass.

```bash
.venv/bin/python scripts/validate_primary_inference.py \
  --configuration configs/inference/primary_six_models.toml
.venv/bin/python scripts/smoke_vllm_models.py --start \
  --attempt-id vllm-primary-smoke-six-models-<attempt-id> \
  --configuration-path configs/inference/primary_six_models.toml
.venv/bin/python scripts/smoke_vllm_models.py --status \
  --configuration-path configs/inference/primary_six_models.toml
.venv/bin/python scripts/smoke_vllm_models.py --count \
  --configuration-path configs/inference/primary_six_models.toml
```

After completion, independently validate terminal metadata, the captured
configuration, all six deterministic result records, token counts, and
sampling settings:

```bash
.venv/bin/python scripts/validate_vllm_primary_smoke.py \
  runs/logs/vllm-primary-inference-smoke/<attempt-id> \
  --configuration configs/inference/primary_six_models.toml \
  --output runs/logs/vllm-primary-inference-smoke/<attempt-id>/validation.json
```

If the frozen smoke exposes batch-dependent greedy output, test vLLM's
batch-invariant mode only through the committed StarCoder2 validation probe;
this command does not change the primary configuration:

```bash
.venv/bin/python scripts/smoke_vllm_models.py --start \
  --attempt-id vllm-batch-invariance-probe-20260803-r1 \
  --configuration-path configs/inference/vllm_batch_invariance_probe.toml
.venv/bin/python scripts/smoke_vllm_models.py --status \
  --configuration-path configs/inference/vllm_batch_invariance_probe.toml
.venv/bin/python scripts/smoke_vllm_models.py --count \
  --configuration-path configs/inference/vllm_batch_invariance_probe.toml
.venv/bin/python scripts/validate_vllm_batch_invariance_probe.py \
  runs/logs/vllm-batch-invariance-probe/<attempt-id>
```

HumanEval+ and MBPP+ evaluation additionally requires Linux `unshare` (from
`util-linux`) and `bubblewrap`. Fetch the two pinned, checksum-verified releases
only when doing benchmark work:

```bash
.venv/bin/python scripts/fetch_evalplus_data.py
.venv/bin/python scripts/validate_evalplus.py
```

The fetch command reuses a byte-identical dataset and refuses to replace
conflicting bytes. Dataset files remain ignored; their release URLs, versions,
SHA-256 values, and expected task counts are committed in
`configs/benchmarks/evalplus.toml`.

BigCodeBench-Instruct data preparation is independently pinned to dataset
`v0.1.4` at an exact Hugging Face repository revision and to evaluator `0.2.5`:

```bash
.venv/bin/python scripts/fetch_bigcodebench_data.py
.venv/bin/python scripts/fetch_bigcodebench_resources.py
.venv/bin/python scripts/setup_bigcodebench_eval_env.py --start
.venv/bin/python scripts/setup_bigcodebench_eval_env.py --status
```

The setup command creates its status file before launching the long installation
in the background. It prints durable status and log paths under
`runs/logs/bigcodebench-environment/`; inspect those paths directly rather than
waiting in a foreground shell. The status command also reports the latest log
size and modification time because source wheel builds can remain in one phase
for several minutes. The official evaluator wheel is checksum-verified for
provenance but is not installed: the standalone local execution adapter uses the
official evaluation requirements without BigCodeBench's unrelated model-serving
and remote-API dependencies. The successful exact resolution is committed in
`requirements-bigcodebench.lock` for subsequent rebuilds. Raw attempt logs are
retained.

The resource fetch pins the four NLTK archives and their extracted file-tree
hashes. The archives and extracted data remain ignored under `data/external/`;
the committed manifest contains their exact upstream revision and hashes. The
evaluator mounts them read-only and provides only deterministic loopback data
for the two retained network-touching tasks. Generated candidates never receive
external network access.

After the status becomes `completed`, run:

```bash
.venv/bin/python scripts/validate_bigcodebench.py
```

## Repository structure

- `configs/`: versioned model, benchmark, prompt, and experiment settings
- `documents/`: canonical design and operational project records
- `prompts/`: version-controlled prompt templates (not embedded in Python)
- `schemas/`: exported, versioned JSON schemas
- `src/self_refinement/`: experiment library
- `tests/`: unit and integration tests
- `data/`: external, intermediate, processed, and manifest data locations
- `runs/`: immutable registry records, raw responses, evaluations, and logs
- `results/`: generated tables, figures, and summaries
- `paper_writing_package/` and `replication_package/`: curated package staging areas

Generated data, model weights, benchmark caches, and secrets are ignored by Git. Placeholder files retain the intended directory topology.

For copy-and-paste pilot and primary execution commands, monitoring, independent
validation, and failure-resume procedures, follow
[`EXPERIMENT_RUNBOOK.md`](EXPERIMENT_RUNBOOK.md). Do not skip its pilot review
gate or enable the full primary configuration while the prompt version is still
a draft.

The common inference layer in `src/self_refinement/inference/` accepts
stage-homogeneous batches for any already-loaded selected checkpoint. It applies
the frozen decoding configuration, rejects individual overflowing prompts
without truncation, stores exact raw response bytes before parsing, and records
input/output token counts plus the backend `stop` or `length` finish reason.
Malformed output and inference infrastructure failures remain distinct from
functional benchmark `FAIL`.

`ProtocolCampaignRunner` in `src/self_refinement/protocols/runner.py` consumes
one already-loaded resident backend and executes Direct, Decision, `R`, shared
Critique, `CR`, shared Plan, and `CPR` as seven all-benchmark phases. Its scope
requires all three benchmark counts, it checkpoints model calls and artifacts
per task, reconstructs a missing artifact from an already completed immutable
raw response, and reuses completed work on resume. `DR`, `DCR`, and `DCPR` are
then derived from the stored Decision and candidates without backend calls.
`scripts/run_model_campaign.py` provides the durable outer lifecycle. The main
Python 3.12 process exports a hash-checked public-only scope and creates typed
provenance records, then one detached parent invokes four sequential vLLM
workers. Each worker loads one checkpoint once, runs all seven phases, writes
batch-level atomic progress, and exits before the next checkpoint loads. Inspect
the frozen inputs without loading weights with:

```bash
.venv/bin/python scripts/run_model_campaign.py --preflight
```

The committed full-scope configuration is deliberately gated while the prompt
set is a pilot-review draft, so `--start` refuses to launch it. After a pilot is
explicitly frozen, a new enabled configuration must be committed before using
`--start`; active jobs expose `--status` and compact `--count` views. A failed
attempt resumes the same immutable registry only through an explicit new
attempt and `--resume-run-id`.

## Validation

Run all repository checks with:

```bash
./scripts/validate.sh
```

The command checks formatting, lint, static types, exported JSON schemas, and unit tests. Run only tests with:

```bash
.venv/bin/python -m pytest
```

The full EvalPlus release check is separate because it requires downloaded
benchmark data. It loads all 164 HumanEval+ and 378 MBPP+ tasks, then checks a
reference and an intentionally incorrect candidate from each benchmark twice
where needed to verify deterministic classification.

Validate the external prompt manifest and the conservative 16K context
envelope with the exact snapshot tokenizers in two isolated steps. The
first command exports only manifest-included public task IDs/specifications;
the second uses the vLLM environment's pinned tokenizer and chat-template
stack. The temporary index contains no tests, reference solutions, or evaluator
outputs.

```bash
.venv/bin/python scripts/export_public_prompt_tasks.py \
  --output /tmp/refinement-public-prompt-tasks-draft3.json
.venv-vllm/bin/python scripts/validate_prompt_protocol.py \
  --task-index /tmp/refinement-public-prompt-tasks-draft3.json \
  --prompt-configuration configs/prompts/primary_draft3.toml \
  --inference-configuration configs/inference/primary_six_models.toml
```

This preflight reserves every upstream artifact's full configured output cap
plus a 64-token concatenation margin. Every real model call must additionally
apply the exact rendered-token check immediately before inference; overflow is
an explicit failure and prompts are never truncated.

The BigCodeBench full representative check is also separate. It requires
reference solutions to pass
twice in stdlib, NumPy, pandas, matplotlib, scikit-learn, and SciPy categories,
and requires a known-incorrect candidate to fail functionally.

Candidate timeout policy `candidate-timeouts-2026-08-04-r2` preserves the
10-second primary default and reference-derived slow-task tiers, then applies a
common 120-second confirmation floor with three predeclared 180-second
HumanEval+ internal-bound exceptions. Superseded policy `r1` is preserved at
`configs/evaluation/timeouts_r1.toml`. The policies use three immutable
reference runtime observations per task. Full audits are long-running and therefore use
durable background attempts:

Final experiment `TIMEOUT` results can be investigated without mutating their
records by using `scripts/diagnose_candidate_timeouts.py`. It accepts an
explicit diagnostic timeout, deduplicates exact task/source pairs by default,
stores separate immutable raw outputs and reports, and supports foreground or
durable background execution with `--count`, `--status`, and `--validate`.

```bash
.venv/bin/python scripts/audit_reference_timings.py --start --benchmark bigcodebench_instruct
.venv/bin/python scripts/audit_reference_timings.py --status
.venv/bin/python scripts/audit_reference_timings.py --count
```

The same launcher supports `humaneval_plus` and `mbpp_plus`. Audit summaries
describe timing distributions and anomalies but do not themselves choose a
timeout. Validate the frozen 10-second default, 16 reference-only primary
overrides, common 120-second confirmation floor, three 180-second confirmation
overrides, and 1.5x slow-primary lower bound with:

```bash
.venv/bin/python scripts/validate_timeout_policy.py
```

After an audit reports `completed`, independently verify its terminal status,
counts, schemas, observation hashes, raw-output hashes, and recomputed summary:

```bash
.venv/bin/python scripts/validate_reference_timing_audit.py \
  runs/logs/reference-timing-audit/<benchmark>/<attempt-id>
```

Use `--count` for a compact one-line view of completed/expected observations,
percentage, current task, and repetition. For a self-refreshing terminal view:

```bash
watch -n 5 .venv/bin/python scripts/audit_reference_timings.py --count
```

## Raw-record policy

Raw responses and registry records are write-once. Repeating an identical write reuses the existing validated artifact; conflicting content is rejected. Resume reuses completed calls and will not retry a recorded failure without an explicit retry request. A retry or deliberate rerun receives a new attempt identifier and links to the prior attempt or run. Infrastructure and parsing failures are explicit statuses and are never converted into a functional `FAIL` evaluation.
