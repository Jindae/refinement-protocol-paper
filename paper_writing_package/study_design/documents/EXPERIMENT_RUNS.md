# Experiment Runs

The pilot runs below are validation evidence only. Full-scope v0.2.0 inference, paper-facing v0.3.0
role-separated inference/evaluation and the complete v0.4.0 single-call sequence have completed and
passed independent validation. Three immutable v0.2.0 remediation attempts are validated but
unresolved. A separate host-screen reference diagnostic localized their apparent setup `ENOMEM` to
cleanup masking after candidate-induced memory exhaustion; corrected remediation `r4` completed and
independently validated the candidate as functional `FAIL` with zero remaining evaluator failures.

Repository formatting, type checking, schema export checks, and unit tests are implementation validation and are not registered as experiment runs.

## mechanism-followup-20260808-r3 (exploratory analysis run)

- Purpose: Analyze task-set churn, Decision mediation, empirical candidate reachability, and the
  role-separated Critique/Plan-to-revision chain without new model calls.
- Status: Completed and independently validated; exploratory/post-hoc, not accepted primary RQ.
- Start and end time: 2026-08-08; foreground derived analysis.
- Git commit: `01b5e734e5bc243e809ab66a2bf2bc6020398d86` (the manifest also records the
  pre-commit producer revision used for the immutable derived bytes).
- Environment identifier: Project Python 3.12 analysis environment.
- Configuration and prompt versions: `mechanism-followup-2026-08-08-r3`; no model prompt used.
- Models and benchmarks: Accepted six-model, three-benchmark v0.4.0 grid.
- Task scope: All common-complete units required by each analysis.
- Output location: `results/summaries/mechanism-followup-2026-08-08-r3/`.
- Machine-readable manifest: `manifest.json` in the output directory.
- Completeness summary: Nine hashed files and 11,044 table rows.
- Validation result: Passed file-hash and row-count validation.
- Known issues: Surface artifact categories are not semantic correctness annotations.
- Parent, replacement, or superseded run: Uses accepted `primary-final-v04-20260808-r5` and role run
  `run_1dd46dd4a0ae265ab7a184a9`; supersedes exploratory precursor `r1`.
- Notes: Does not modify accepted paper-facing estimates.

## option-a-pilot-20260808-r1

- Purpose: Three-condition prompt-ablation pilot for regeneration without initial code, observable
  within-call draft/critique/final refinement, and critique-conditioned generation without initial
  code.
- Status: Failed before the first model call; immutable attempt retained.
- Start and end time: 2026-08-08 11:16:38 to 11:21:18 Asia/Seoul.
- Git commit: `01b5e734e5bc243e809ab66a2bf2bc6020398d86`.
- Environment identifier: Frozen vLLM 0.26.0 environment, TP=2, batch-invariant greedy decoding.
- Configuration and prompt versions: `option-a-pilot-2026-08-08-r1` and
  `option-a-prompts-2026-08-08-r1`.
- Models and benchmarks: DeepSeek-Coder-V2-Lite, Qwen3-Coder-30B-A3B, Gemma-4-31B; three tasks from
  each of HumanEval+, MBPP+, and BigCodeBench-Instruct.
- Task scope: 27 model-task units × three calls = 81 calls; draft condition can yield 108 total
  candidate artifacts across all conditions.
- Output location: attempt `runs/logs/option-a-campaign/option-a-pilot-20260808-r1/`; registry
  `runs/registry/run_70e600425ec0ca9b094dd11c/`.
- Machine-readable manifest: immutable `launch.json`, atomic `status.json`, per-call/candidate
  records, and terminal validation. Worker PID at launch: `1573194`.
- Completeness summary: 0/81 calls and zero candidate artifacts. DeepSeek-Coder-V2-Lite loaded, but
  the worker rejected the first rendered prompt token IDs before backend generation.
- Validation result: Failed; no inference summary or candidate evaluation is eligible.
- Known issues: `ISSUE-20260808-22`; candidate evaluation was not started.
- Parent, replacement, or superseded run: Reuses v0.2.0 exact initial lineage and v0.3.0 Critiques.
- Notes: Options B/C remain unlaunched pending this pilot's validated review.

## option-a-pilot-20260808-r2

- Purpose and scope: Unique replacement for r1 with the same frozen 3-model, 9-task, 3-condition,
  81-call design; no scientific input changes.
- Status: Running; detached worker passed the immediate host-context liveness check.
- Start and end time: Started 2026-08-08 12:19:22 Asia/Seoul; end pending.
- Git commit: `1503e14a8e177ae8fc44c5bf584b747d61394510` (Option-A fix commit `30e5bdf`).
- Parent or predecessor: Failed attempt `option-a-pilot-20260808-r1`; no output is reused.
- Execution change: Accept Mapping-based tokenizer results and preflight all three exact tokenizer
  snapshots and Option-A template families before GPU launch.
- Output and validation: attempt `runs/logs/option-a-campaign/option-a-pilot-20260808-r2/`;
  registry `runs/registry/run_e34fd10203b5a9e7009137cf/`; launch PID `1580561`. Immediate handoff
  state was `running`, phase `loading_model`, 0/81 calls.
- Notes: Options B/C and candidate evaluation remain blocked pending validated r2 inference.

## primary-final-four-rq-20260808-r3 (accepted analysis run)

- Purpose: Reorganize the completed 12-protocol results into four paper-facing RQs, with stage
  performance and repair/regression balance jointly analyzed in RQ1.
- Status: Completed and validated; accepted for paper reporting.
- Source runs: Identical validated source inference, evaluation, remediation, and adjudication runs
  used by the preceding five-RQ analysis; no experiment was rerun and no source record changed.
- Configuration: `primary-analysis-2026-08-08-r4`; 10,000 paired bootstrap resamples, seed
  20260804, 95% confidence, supplementary exact McNemar tests, and four RQ seed namespaces.
- Output: processed dataset `data/processed/primary-final-v04-20260808-r5/`, RQ results
  `results/summaries/primary-final-four-rq-20260808-r3/`, and paper assets
  `results/paper_assets/primary-final-four-rq-20260808-r3/`.
- Completeness: 120,744 outcome rows (6×1,677×12), 120,656 selected paper-facing stage-call rows,
  four validated RQ directories, and 12 validated compact paper CSV inputs.
- Missingness: Unchanged. TIMEOUT and infrastructure remain indeterminate; malformed model
  candidates remain separate end-to-end zeros; effective base evaluator failures are zero.
- Notes: RQ1 contains stage pass-rate contrasts, initial-to-final transition balance, and candidate
  change together. Former RQ3–RQ5 become RQ2–RQ4. This is a reporting/provenance rebuild, not a new
  empirical run. Intermediate dataset `r3` exposed a stale hard-coded analysis-version label in the
  final composite builder; the builder and validator were corrected. Corrected dataset `r4` and
  analysis/assets `r2` served as pre-commit validation only; accepted `r5`/analysis `r3` identify
  the exact committed producer.

## primary-final-v04-20260808-r1 (analysis run)

- Purpose: Construct the accepted 12-protocol composite dataset, run RQ1–RQ5, and generate compact
  paper table/chart inputs after all source evaluations and remediation validated.
- Status: Completed and validated; superseded for paper reporting by the four-RQ analysis above.
- Source runs: v0.2.0 inference `run_c99d3b1d562acc3e80026e48`, base evaluation
  `run_b25b1ec137928799f30217af`, superseding remediation `run_cfde994451c10e10b850905f`, v0.3.0
  inference/evaluation `run_1dd46dd4a0ae265ab7a184a9`/`run_1e4f588e7975f8b97a71400f`, and v0.4.0
  inference/evaluation `run_5a4129eed4283cd222e2de9e`/`run_7e4ee0647f99f8eb90c1aecd`.
- Configuration: `primary-analysis-2026-08-08-r3`; 10,000 paired bootstrap resamples, seed
  20260804, 95% confidence, supplementary exact McNemar tests.
- Output: processed dataset `data/processed/primary-final-v04-20260808-r2/`, RQ results
  `results/summaries/primary-final-v04-20260808-r1/`, and corrected paper assets
  `results/paper_assets/primary-final-v04-20260808-r2/`.
- Completeness: 120,744 outcome rows (6×1,677×12), 120,656 selected paper-facing stage-call rows,
  five validated RQ directories, and 11 compact paper CSV inputs.
- Missingness: TIMEOUT and infrastructure remain indeterminate; malformed model candidates are
  separate end-to-end zeros. Effective base evaluator failures are zero after explicit supersession.
- Notes: paper-asset attempt `primary-final-v04-20260808-r1` is superseded because its pooled task key
  omitted model identity; corrected `r2` includes model identity and is the only accepted asset set.

## single-call-sequence-primary-20260807-r2

- Purpose: Unattended full v0.4.0 single-call inference concurrent with independent role-separated
  evaluation, followed by single-call evaluation after both branches validate.
- Status: Completed and independently validated.
- Start and end time: 2026-08-07T02:06:17Z to 2026-08-07T20:44:13Z.
- Git commit: `220d4b838dafaf32ec6b6d447c7716fcea77cd2c` at sequence launch.
- Environment identifier: Frozen vLLM inference environment; Python 3.12/EvalPlus and isolated
  Python 3.10.12 BigCodeBench evaluation environments.
- Configuration and prompt versions: `single-call-through-evaluation-2026-08-07-r2`,
  `single-call-comparison-2026-08-07-r2`, `single-call-prompts-2026-08-07-r1`, timeout policy `r2`.
- Models and benchmarks: Six frozen models; 163 HumanEval+, 378 MBPP+, 1,136 BigCodeBench tasks.
- Task scope: Up to 50,310 single-call inference units, followed by all generated v0.3.0 CR/CPR and
  v0.4.0 `SC-*` candidates.
- Output location: Parent `runs/logs/single-call-full-sequence/single-call-sequence-primary-20260807-r2/`;
  independently durable child attempts are pinned in the sequence configuration.
- Machine-readable manifest: Validated inference child `run_5a4129eed4283cd222e2de9e`; validated
  role evaluation child `run_1e4f588e7975f8b97a71400f`; validated single-call evaluation child
  `run_7e4ee0647f99f8eb90c1aecd`.
- Completeness summary: Full single-call inference completed; role evaluation contains 20,093
  resolutions and 221 confirmations. Single-call evaluation contains 49,569 primary attempts and
  resolutions, 440 confirmations, 49,426 completed resolutions, 143 final timeouts, and zero evaluator
  failures.
- Validation result: Passed for all three children and the terminal parent sequence.
- Known issues: Four pilot multi-fence malformed candidates are accepted model noncompliance; no retry
  or parser repair is applied.
- Parent, replacement, or superseded run: Uses v0.3.0 source `run_1dd46dd4a0ae265ab7a184a9` and exact
  v0.2.0 initials from `run_c99d3b1d562acc3e80026e48`; replaces only parent sequence `r1` while
  attaching to its unchanged inference child `single-call-primary-20260807-r1`.
- Notes: Role-separated evaluation uses two workers alongside inference. Single-call evaluation uses
  two workers and begins only after inference and role-separated evaluation both validate.

## evaluation-remediation-v02-20260807-r1

- Purpose: Retry the complete terminal confirmation-stage evaluator-failure inventory from the
  v0.2.0 candidate evaluation exactly once under `DEC-20260807-44`.
- Status: Completed and independently validated as unresolved; no functional outcome was produced.
- Start and end time: 2026-08-07T11:11:41Z to 2026-08-07T11:11:45Z.
- Git commit: `cce5be2b38c4b6f1f427a70a7487d1d3179591ae`.
- Environment identifier: Pinned Python 3.10.12 BigCodeBench environment and
  `standalone-local-v3` adapter invoked from the managed command sandbox; the sandbox denied a
  required netlink socket before benchmark execution.
- Configuration and prompt versions: Remediation policy
  `retry-confirmation-evaluator-failures-once-2026-08-07-r1`; source timeout policy
  `candidate-timeouts-2026-08-04-r2`; prompts are provenance only and never evaluator inputs.
- Models and benchmarks: One Devstral-Small-2-24B-Instruct CPR candidate on
  `BigCodeBench/1042` selected from the complete failure inventory.
- Task scope: Candidate `candidate_0b876d790d64fddd621dbe81`; exact 120-second confirmation retry.
- Output location: Operational attempt
  `runs/logs/evaluation-remediation/evaluation-remediation-v02-20260807-r1/`; immutable registry
  `runs/registry/run_81f775bdba8796358ce73b4d/`.
- Machine-readable manifest: Terminal `run_manifest_5a19b240d4751e557e62c10d`.
- Completeness summary: One retry and one replacement resolution; retry
  `evaluation_85ee74cd36a0223e5963cbe9` ended after 1.758 seconds with
  `InvalidEvaluatorOutput`, empty stdout, and stderr `Cannot open netlink socket: Operation not
  permitted`. Effective counts remain 40,074 completed, 131 timeout, and one evaluator failure.
- Validation result: Passed raw hash, evaluator configuration, count, manifest, and supersession
  validation; `remediation_result=unresolved`.
- Known issues: `ISSUE-20260806-17`; this attempt tested the explicit concurrency path but cannot
  distinguish candidate behavior because its execution sandbox prevented evaluator startup.
- Parent, replacement, or superseded run: Parent evaluation `run_b25b1ec137928799f30217af`; the new
  immutable failed confirmation/resolution supersede only the original failure lineage.
- Notes: No automatic retry follows. Wait for the active evaluation, then decide whether to launch a
  fresh host-context attempt with a new identifier.

## evaluation-remediation-v02-20260807-r2

- Purpose: Replace sandbox-blocked `r1` in the approved host evaluator context while preserving its
  complete predecessor lineage.
- Status: Completed and independently validated as unresolved.
- Start and end time: 2026-08-07T11:19:51Z to 2026-08-07T11:20:26Z.
- Git commit: `52f2d20e3ce7d0dffd4855960e0580ec2145512d`.
- Environment identifier: Pinned Python 3.10.12 BigCodeBench environment and
  `standalone-local-v3` adapter in the approved host execution context.
- Configuration and prompt versions: Same remediation and timeout policies as `r1`; no prompt input.
- Models and benchmarks: Exact `BigCodeBench/1042` candidate selected by the frozen inventory.
- Task scope: One 120-second confirmation evaluation.
- Output location: Attempt
  `runs/logs/evaluation-remediation/evaluation-remediation-v02-20260807-r2/`; immutable registry
  `runs/registry/run_3b69aaca71b22ef25fd62d9b/`.
- Machine-readable manifest: Terminal `run_manifest_920b74d991db512ea6fcdc36`.
- Completeness summary: One host-context retry and replacement resolution. Evaluation
  `evaluation_69c19d9b2f57cf832f02683d` ran 33.380 seconds, then returned
  `OSError: [Errno 12] Cannot allocate memory` while creating `/tmp/bigcodebench-br1ilgbb`; no
  functional outcome was produced.
- Validation result: Passed raw hash, evaluator configuration, count, manifest, and supersession
  validation; `remediation_result=unresolved`. Effective counts remain 40,074 completed, 131 timeout,
  and one evaluator failure.
- Known issues: `ISSUE-20260806-17`; correct host startup reproduces the original error class despite
  about 96.6 GB host memory available at preflight.
- Parent, replacement, or superseded run: Predecessor
  `evaluation-remediation-v02-20260807-r1`; source evaluation
  `run_b25b1ec137928799f30217af` remains immutable.
- Notes: Stop further retries until the active evaluation finishes, as required by the user decision.

## evaluation-remediation-v02-20260808-r3

- Purpose: Test the concurrent-load hypothesis by rerunning the exact v0.2.0 failure after every other
  evaluation worker and the parent sequence completed and validated.
- Status: Completed and independently validated as unresolved.
- Start and end time: 2026-08-07T20:54:04Z to 2026-08-07T20:54:31Z.
- Git commit: `8315ca195221247b27c5e0c96819225c55ef0f0b`.
- Environment identifier: Pinned Python 3.10.12 BigCodeBench environment and
  `standalone-local-v3` adapter in approved host context; no concurrent evaluation.
- Configuration and prompt versions: Same frozen remediation and timeout policy; prompts are not
  evaluator inputs.
- Models and benchmarks: Exact Devstral CPR candidate for `BigCodeBench/1042`.
- Task scope: One 120-second confirmation evaluation, predecessor
  `evaluation-remediation-v02-20260807-r2`.
- Output location: Attempt
  `runs/logs/evaluation-remediation/evaluation-remediation-v02-20260808-r3/`; immutable registry
  `runs/registry/run_218265fd6821b56de3e6753b/`.
- Machine-readable manifest: Terminal `run_manifest_4ef63dd87eec5d8af6324b98`.
- Completeness summary: Evaluation `evaluation_77c94751d8713c0b7d38b24f` returned
  `OSError: [Errno 12] Cannot allocate memory` after 26.170 seconds while creating
  `/tmp/bigcodebench-vys7djhz`; no functional outcome was produced.
- Validation result: Passed raw hash, evaluator configuration, count, manifest, predecessor, and
  supersession checks; `remediation_result=unresolved`. Effective counts remain 40,074 completed,
  131 timeout, and one evaluator failure.
- Known issues: `ISSUE-20260806-17`; isolated reproduction refutes concurrent evaluator load as a
  necessary cause. The later reference diagnostic corrects the initial pre-execution interpretation:
  cleanup of the same path can mask an already collected unittest result.
- Parent, replacement, or superseded run: Predecessor `r2`; source evaluation
  `run_b25b1ec137928799f30217af` remains immutable.
- Notes: `DEC-20260808-48` authorizes a corrected remediation-only cleanup policy and replacement
  attempt `r4`; this attempt remains immutable.

## evaluation-remediation-v02-20260808-r4

- Purpose: Preserve the exact candidate's functional evaluator result when cleanup of its disposable
  private tmpfs encounters `ENOMEM`, correcting the result-masking defect diagnosed after `r3`.
- Status: Completed and independently validated as resolved.
- Start and end time: 2026-08-07T21:10:30Z to 2026-08-07T21:10:59Z.
- Git commit: `47756ac0f819397ae207b1323b6598487df3c99e`.
- Environment identifier: Pinned Python 3.10.12 BigCodeBench environment and
  `standalone-local-v3` adapter in a separate approved host `screen` session.
- Configuration and prompt versions: Remediation policy
  `retry-confirmation-evaluator-failures-once-2026-08-08-r2`; worker cleanup policy
  `ignore-disposable-sandbox-cleanup-errors-2026-08-08-r1`; source timeout policy unchanged.
- Models and benchmarks: Exact Devstral CPR candidate for `BigCodeBench/1042`.
- Task scope: One 120-second confirmation evaluation, predecessor
  `evaluation-remediation-v02-20260808-r3`.
- Output location: Attempt
  `runs/logs/evaluation-remediation/evaluation-remediation-v02-20260808-r4/`; immutable registry
  `runs/registry/run_cfde994451c10e10b850905f/`.
- Machine-readable manifest: Terminal `run_manifest_8da0e5386253160851fad16d`.
- Completeness summary: Retry `evaluation_3382ae3ef97f6810efd484ed` completed in 26.673 seconds as
  functional `FAIL`; replacement resolution `evaluation_resolution_29683c8264d47534ce9c9ec2`
  explicitly supersedes the failed lineage. Effective counts are 40,075 completed, 131 timeout, and
  zero evaluator failures.
- Validation result: Passed retry/replacement counts, raw artifact hash, corrected evaluator
  configuration, manifest, predecessor, supersession, and effective-status checks;
  `remediation_result=resolved`.
- Known issues: `ISSUE-20260806-17` is resolved. No candidate, hidden-test, timeout, resource-limit,
  or network-isolation input changed.
- Parent, replacement, or superseded run: Predecessor `r3`; source evaluation
  `run_b25b1ec137928799f30217af` remains immutable.
- Notes: This is a functional benchmark failure, not an evaluator failure or timeout. The three
  unresolved predecessor attempts remain immutable diagnostic evidence and are not effective results.

## evaluation-role-separated-primary-20260807-r1

- Purpose: Evaluate every valid paper-facing v0.3.0 CR/CPR candidate.
- Status: Completed and independently validated.
- Start and end time: 2026-08-07T02:06:24Z to 2026-08-07T07:12:18Z.
- Git commit: `220d4b838dafaf32ec6b6d447c7716fcea77cd2c`.
- Environment identifier: Python 3.12 EvalPlus and isolated Python 3.10.12 BigCodeBench;
  exactly two evaluator workers.
- Configuration and prompt versions: Timeout policy `candidate-timeouts-2026-08-04-r2`; source
  inference `role-separated-followup-2026-08-06-r1` and prompt provenance `r1`.
- Models and benchmarks: Six frozen models; 163 HumanEval+, 378 MBPP+, and 1,136 BigCodeBench tasks.
- Task scope: 20,093 candidates: 10,040 CR and 10,053 CPR.
- Output location: Registry `runs/registry/run_1e4f588e7975f8b97a71400f/`; operational attempt
  `runs/logs/evaluation-campaign/evaluation-role-separated-primary-20260807-r1/`.
- Machine-readable manifest: Terminal `run_manifest_cc5f39cb9500cc164442bf71`.
- Completeness summary: 20,093 primary attempts/resolutions, 221 confirmations, 20,025 completed
  resolutions, 68 final timeouts, and zero evaluator failures; 20,314 raw artifacts validated.
- Validation result: Passed count, lineage, schema, raw hash, timeout confirmation, configuration,
  and terminal-manifest validation.
- Known issues: None in evaluation infrastructure; model-format failures remain source artifacts.
- Parent, replacement, or superseded run: Child of v0.3.0 inference
  `run_1dd46dd4a0ae265ab7a184a9`.
- Notes: DCR/DCPR derivation and composite processed-data generation remain separate pending tasks.

## single-call-sequence-primary-20260807-r1

- Purpose: Original sequential parent for full v0.4.0 inference and the two pending evaluations.
- Status: Running at this documentation freeze; scheduled for exact-parent cancellation and replacement
  by `r2` without cancelling or altering its active inference child.
- Start and end time: Started 2026-08-07T01:16:36Z; terminal transition pending successor launch.
- Git commit: `a89fc2787be6a21cbc91eb373648d1768310d16e`.
- Configuration and prompt versions: `single-call-through-evaluation-2026-08-07-r1`,
  `single-call-comparison-2026-08-07-r2`, `single-call-prompts-2026-08-07-r1`.
- Output location: `runs/logs/single-call-full-sequence/single-call-sequence-primary-20260807-r1/`.
- Validation result: Not applicable to the parent after replacement; child inference validation remains
  required and will be observed by `r2`.
- Parent, replacement, or superseded run: Replaced operationally by
  `single-call-sequence-primary-20260807-r2`; its inference child and registry are reused exactly.

## single-call-pilot-20260807-r1

- Purpose: Validate all five v0.4.0 single-call prompts, independent code/Decision parsing, lineage,
  model-resident scheduling, and malformed-output accounting before full execution.
- Status: Completed, independently validated, and accepted.
- Start and end time: 2026-08-07T00:15:11Z to 2026-08-07T00:46:55Z.
- Git commit: `3fc614f58d910170ac1b952fea07c41adb0ab074`.
- Environment identifier: Frozen `vllm-environment-2026-08-03-r1`, vLLM 0.26.0, TP=2.
- Configuration and prompt versions: `single-call-pilot-2026-08-07-r1`,
  `single-call-prompts-2026-08-07-r1`, serving `primary-inference-2026-08-04-r3`.
- Models and benchmarks: Six frozen models; three tasks from each benchmark.
- Task scope: Six models × nine tasks × five conditions = 270 calls.
- Output location: Registry `runs/registry/run_b7b3feb52ce8f9e98df3fcfa/`; attempt
  `runs/logs/single-call-campaign/single-call-pilot-20260807-r1/`.
- Machine-readable manifest: Terminal `run_manifest_0d8b5d39fed30bb5e8709a63`; validation SHA-256
  `0cd515db553b7bfee723b6a06b744345f5afc3588adb3d8fea8671ae5d6bd31e`.
- Completeness summary: 270 logical calls/raw responses, 266 valid candidates, and 162 integrated
  Decision artifacts. Four responses contain multiple Python fences (DeepSeek one, Qwen3 three).
- Validation result: Passed call/raw/candidate/Decision/manifest completeness and lineage; all 162
  Decision labels parse exactly. Review accepts the four malformed candidates under the frozen policy.
- Known issues: Model format noncompliance only; no inference failure, timeout, invalid Decision label,
  parser defect, or infrastructure failure.
- Parent, replacement, or superseded run: Validation-only child of exact v0.2.0 initial source
  `run_c99d3b1d562acc3e80026e48`; no pilot candidate enters primary estimates.

## evaluation-full-candidates-20260806-r1

- Purpose: Evaluate all 40,206 available Direct, `R`, `CR`, and `CPR` candidates from the validated
  v0.2.0 primary inference under the frozen evaluator and two-stage timeout policy.
- Status: Partial; process completed successfully, but independent validation and resolution of one
  evaluator infrastructure failure remain pending.
- Start and end time: 2026-08-05T22:04:29Z to 2026-08-06T15:28:35Z.
- Git commit: `7233ff24560bee2edecd69a2d126ea95c4b71722`.
- Environment identifier: Python 3.12 orchestration and EvalPlus evaluation; isolated Python 3.10.12
  BigCodeBench adapter `standalone-local-v3`.
- Configuration and prompt versions: `candidate-timeouts-2026-08-04-r2`, EvalPlus manifest `r5`,
  BigCodeBench manifest `r6`; source study `study-v0.2.0`.
- Models and benchmarks: Six frozen models; 163 HumanEval+, 378 MBPP+, and 1,136 BigCodeBench tasks.
- Task scope: 40,206 candidates: 10,054 Direct, 10,053 `R`, 10,049 `CR`, and 10,050 `CPR`.
- Output location: Registry `runs/registry/run_b25b1ec137928799f30217af/`; operational attempt
  `runs/logs/evaluation-campaign/evaluation-full-candidates-20260806-r1/`.
- Machine-readable manifest: Terminal `run_manifest_f799892783bcd7fba66a9221`; independent validation pending.
- Completeness summary: 40,206 primary attempts and resolutions; 387 confirmations; final stored
  statuses comprise 40,074 completed, 131 timeout, and one evaluation failure.
- Validation result: `pending_independent_validation`; no result is paper-facing.
- Known issues: `ISSUE-20260806-17` affects one BigCodeBench/1042 confirmation and remains an
  infrastructure failure rather than functional `FAIL` or final `TIMEOUT`.
- Parent, replacement, or superseded run: Child of v0.2.0 inference `run_c99d3b1d562acc3e80026e48`.
- Notes: The historical v0.2.0 `CR`/`CPR` outcomes are formative only under `DEC-20260806-40`.

## role-sequence-primary-20260806-r1

- Purpose: Generate the four replacement role-separated artifacts for paper-facing `study-v0.3.0`
  while reusing exact validated v0.2.0 Initial Candidates, Direct Revision candidates, and Decisions.
- Status: Completed and independently validated.
- Start and end time: 2026-08-06T14:29:34Z to 2026-08-07T00:00:44Z.
- Git commit: Sequence and completed phases started from `4902b6b8eeb0abce544a4e98141abc94a8101610`.
- Environment identifier: Frozen `vllm-environment-2026-08-03-r1`, Python 3.12.13, vLLM 0.26.0,
  two-GPU tensor parallel execution.
- Configuration and prompt versions: `role-separated-followup-2026-08-06-r1`,
  `role-separated-prompts-2026-08-06-r1`, and `primary-inference-2026-08-04-r3`.
- Models and benchmarks: Six frozen models; 163 HumanEval+, 378 MBPP+, and 1,136
  BigCodeBench-Instruct tasks.
- Task scope: 1,677 tasks × six models × four replacement phases = 40,248 scheduled task-phase
  units, with eight malformed source Initial Candidates explicitly blocking dependent calls.
- Output location: `runs/registry/run_1dd46dd4a0ae265ab7a184a9/`; operational sequence
  `runs/logs/role-separated-sequence/role-sequence-primary-20260806-r1/` and independently durable
  child phase attempts under `runs/logs/role-separated-phase/`.
- Machine-readable manifest: Child inference `run_1dd46dd4a0ae265ab7a184a9`; terminal
  `run_manifest_cff8e43492d1a252eb04599e`.
- Completeness summary: Critique Generation produced 10,054 artifacts with zero failed calls and
  eight blocks. Critique-Conditioned Revision produced 10,040 candidates, retained 14 explicit
  model-format failures, and inherited eight blocks. Revision Planning produced 10,054 Plan artifacts
  and inherited the same eight blocks. CPR produced 10,053 candidates with one format failure and
  eight source blocks. The registry contains 40,216 model calls/raw responses.
- Validation result: All four child phases and sequence-level validation passed; validation content
  SHA-256 is `5cd6c4bad0ed60c9aeecddc77b2971a04ad2adf7be7207b19d62c987c532dd81`.
- Known issues: Some completed Critiques ended at the configured output limit; 14 CR and one CPR
  response did not produce valid candidate format. Raw responses and finish reasons remain immutable;
  neither condition is an infrastructure failure.
- Parent, replacement, or superseded run: Child of validated v0.2.0 inference
  `run_c99d3b1d562acc3e80026e48`; replaces only its C/P/CR/CPR constructs for paper-facing analysis.
- Notes: `prompts/v4/` is now a complete directory snapshot, but the frozen manifest and this run
  retain the original v3 paths for the three byte-identical reused templates.

## decision-adjudication-primary-20260806-r1

- Purpose: Resolve every strict-parser-invalid primary Decision before any candidate evaluation.
- Status: Completed and independently validated.
- Git commit: `1f7ed03`.
- Configuration and prompt versions: Rubric `decision-adjudication-2026-08-06-r2`; deterministic rule `decision-terminal-period-2026-08-06-r1`; source prompt remains frozen `primary-prompts-2026-08-04-r1`.
- Task scope: All 202 invalid Decisions in inference `run_c99d3b1d562acc3e80026e48`.
- Output location: `runs/logs/decision-adjudication/decision-adjudication-primary-20260806-r1/`.
- Machine-readable manifest: Adjudication run `run_ecbe59d47824d8b4b21745c7`; report SHA-256 `d670419809b2f9ddea39734ecc481d7cd59d2e1ebb5c191cb6901bc38b3db644`; validation SHA-256 `69fc783d3307071046ac7bffac35abdd8796f454030b9bed1df12639a0df3a3a`.
- Completeness summary: 202 resolved, zero unresolved; 156 deterministically normalized `PRESERVE`, 46 non-exact response directions read without benchmark evaluation results (44 `REFINE`, two `PRESERVE`), and 605 D-protocol candidate-selection records constructed from those resolved Decisions. One potential DCPR selection is unavailable because its corresponding CPR candidate is malformed.
- Validation result: Complete invalid-call coverage, raw-response hashes, initial-candidate references, normalization rule, reviewer evidence boundary, records, and available-candidate-derived outcome counts pass. `evaluation_descendant_existed=false` and `evaluation_feedback_used=false`.
- Known issues: The original 202 model calls remain invalid and reportable; no raw response or model-compliance rate is changed.
- Parent, replacement, or superseded run: Child of primary inference `run_c99d3b1d562acc3e80026e48`; does not mutate or replace it.

## campaign-primary-20260804T104734Z

- Purpose: Generate every independent model artifact for the frozen six-model, three-benchmark primary scope.
- Status: Completed and independently validated.
- Start and end time: 2026-08-04T10:47:51Z to 2026-08-05T21:16:11Z.
- Git commit: `8a04c51251e671fb87d5cf33febc602ada1e94ce`.
- Configuration and prompt versions: `model-campaign-2026-08-04-r2`, `primary-inference-2026-08-04-r3`, `primary-prompts-2026-08-04-r1`, study `study-v0.2.0`.
- Models and benchmarks: Six frozen models; 163 HumanEval+, 378 MBPP+, and 1,136 BigCodeBench-Instruct tasks.
- Task scope: 1,677 tasks × six models × seven independent phases = 70,434 scheduled task-phase units.
- Output location: `runs/registry/run_c99d3b1d562acc3e80026e48/`; operational attempt `runs/logs/model-campaign/campaign-primary-20260804T104734Z/`.
- Machine-readable manifest: `run_manifest_c8942708e851989a5e1303fa`; validation SHA-256 `af01d879eddfe16242f24520d375b299556a7a1cf7782655ed3434595b67fb68`.
- Completeness summary: 70,386 calls and raw responses, 40,206 candidates, 10,054 critiques, 10,054 plans, 9,852 exact Decisions, and 29,547 original derived outcomes. Eight malformed initial candidates cause exactly 48 explicit downstream blocks. The immutable calls additionally contain ten malformed revision outputs and 202 invalid Decisions.
- Validation result: Terminal status, manifest, model/task/phase counts, every typed call, and every raw-response hash pass. No benchmark evaluation result was available to any model call.
- Known issues: `ISSUE-20260806-13` (performance-only, resolved) and `ISSUE-20260806-14` (model output behavior, mitigated prospectively without artifact mutation).
- Parent, replacement, or superseded run: First accepted full-scope primary inference; pilot inference remains validation-only.

## pilot-review-six-models-20260804-r4

- Purpose: Final adjudication-aware pilot review of the adapter-v4 replacement evaluation and unchanged six-model inference artifacts before primary freeze.
- Status: Completed; automated gate passed with zero blocking reason, and the required manual review is complete.
- Start and end time: 2026-08-04 Asia/Seoul; foreground report generation completed after independent evaluation validation.
- Git commit: Evaluation and report consume implementation commit `ac2dd65056dff660c76fe8369d0c0de0863ebc8f`; the source inference remains commit `30ca842`.
- Environment identifier: Main Python 3.12 project environment; read-only access to inference, evaluation, and adjudication artifacts.
- Configuration and prompt versions: Report schema `pilot-review-v3`; prompt `primary-prompts-2026-08-04-draft3`; timeout policy `candidate-timeouts-2026-08-04-r2`; EvalPlus adapter `self-refinement-isolated-v4`.
- Models and benchmarks: All six adopted models over three tasks from each of HumanEval+, MBPP+, and BigCodeBench-Instruct.
- Task scope: 378 model calls, 216 candidates, 54 effective Decisions, 162 effective derived outcomes, and 216 evaluation resolutions.
- Output location: `runs/logs/pilot-review/pilot-review-six-models-20260804-r4/report.json`.
- Machine-readable manifest: Report SHA-256 `f2cdf64bc9ccc30cdd3548c3538a395a72fe68b4ccb63498877ed7d0f5997c26`.
- Completeness summary: Observed 377 completed plus one preserved invalid model call; 53 exact-parsed plus one separately read Decision; 159 original plus three added D-protocol candidate-selection records; and 133 `PASS`, 78 functional `FAIL`, and five final `TIMEOUT` resolutions. Finish reasons are 377 `stop` and one `length`.
- Validation result: Automated source validations, expected counts, raw paths, evaluation lineage, and Decision adjudication completeness pass. Representative raw-response paths are byte-identical to review `r3` and retain its completed manual inspection. Every new adapter-v4 timeout trace was reviewed directly: five confirmations remain timeout-only and six have an independent false detail that correctly takes functional `FAIL` precedence.
- Known issues: None blocking primary freeze. The one adjudicated Decision remains separately disclosed and must be excluded in the prespecified sensitivity analysis. Critique/Plan code snippets remain accepted under `DEC-20260804-26` and are reportable instruction-compliance behavior.
- Parent, replacement, or superseded run: Reviews inference `run_4b0bdec98ae531232cfe9f30`, evaluation `run_38cf240201dfb892765eccc2`, and adjudication `run_387a281ce89a3147e1d4b0da`. Replaces review `r3` as the final pilot-freeze evidence without mutating any prior report.
- Notes: `DEC-20260804-31` uses this report to freeze the exact prompt bytes and prospective full-scope campaign; no pilot candidate enters primary estimates.

## evaluation-pilot-six-models-20260804-r3

- Purpose: Re-evaluate the same 216 exact six-model pilot candidates with explicit EvalPlus per-input timeout attribution after `ISSUE-20260804-12`.
- Status: Completed and independently validated; accepted final candidate-evaluation evidence for the primary freeze.
- Start and end time: 2026-08-04 18:31:19 to 18:44:52 Asia/Seoul.
- Git commit: `ac2dd65056dff660c76fe8369d0c0de0863ebc8f`.
- Environment identifier: Python 3.12.13 orchestration; EvalPlus isolated adapter `self-refinement-isolated-v4`; BigCodeBench Python 3.10.12 adapter `standalone-local-v3`.
- Configuration and prompt versions: Timeout policy `candidate-timeouts-2026-08-04-r2`; EvalPlus manifest `evalplus-benchmarks-2026-08-04-r5` SHA-256 `f9d20de1f288f676ffb76419faa31896468e68a00bf403d832d27c921f433c9b`; BigCodeBench manifest `bigcodebench-instruct-2026-08-03-r6` SHA-256 `321304b78a18e8ae8ac29432878b2a54f94cb8c35df483b2261165b27e3766b9`; source study `study-v0.2.0`.
- Models and benchmarks: All six adopted checkpoints; three HumanEval+, three MBPP+, and three BigCodeBench-Instruct pilot tasks per model.
- Task scope: The same 216 immutable candidates from inference `run_4b0bdec98ae531232cfe9f30`, 54 each for Direct, `R`, `CR`, and `CPR`.
- Output location: Registry `runs/registry/run_38cf240201dfb892765eccc2/`; operational attempt `runs/logs/evaluation-campaign/evaluation-pilot-six-models-20260804-r3/`.
- Machine-readable manifest: Terminal `run_manifest_95862efe6badbea8455e0f85`; summary SHA-256 `f44c167de5c7db69200bb78ff15edeaadfab77e86dceecf98d7da092a59a7ebe`; validation SHA-256 `abc13909fa7c87938cf1f1fdc4f985e4d68891ab7a73fd670cb990fe4a44db52`.
- Completeness summary: 216/216 primary attempts and final resolutions, 11 timeout-only confirmations, and 227 immutable raw evaluator outputs. Final outcomes are 133 `PASS`, 78 functional `FAIL`, and five `TIMEOUT`, with zero evaluator failures. Primary status comprises 205 completed and 11 timeout; confirmation resolves six mixed cases to conclusive `FAIL` and leaves five timeout-only cases as final `TIMEOUT`.
- Validation result: Passed exact source/candidate lineage, typed schemas, raw hashes, timeout confirmation completeness, terminal manifest, evaluator manifest provenance, and exact `study-v0.2.0` equality. All 11 confirmation raw outputs explicitly record per-input timeout indexes.
- Known issues: None affecting this accepted run. Compared with adapter-v3 evaluation `r2`, Qwen3 Direct `HumanEval/129` changes from ambiguous `FAIL` to reproducible `PASS`, while Qwen7 CPR remains `FAIL` because its base suite contains an independent false detail in addition to timeouts.
- Parent, replacement, or superseded run: Replaces `run_286f0e7dc35e0e66fe23e95d` as pilot-freeze evidence; both prior registries remain immutable. Source inference and Decision adjudication are reused without any model call.
- Notes: Logical evaluation run ID is `run_38cf240201dfb892765eccc2`. No benchmark result or timeout diagnostic was inserted into a model prompt.

## pilot-review-six-models-20260804-r3

- Purpose: Review the corrected-provenance six-model evaluation together with the complete Decision adjudication and all immutable inference artifacts.
- Status: Completed; automated gate passed, but subsequently invalidated as primary-freeze evidence by `ISSUE-20260804-12`.
- Start and end time: 2026-08-04 Asia/Seoul; foreground report generation completed after independent evaluation validation.
- Git commit: Review generated from evaluation commit `b02d09c`; Decision adjudication implementation commit `8f50180`.
- Environment identifier: Main Python 3.12 project environment; read-only access to inference, evaluation, and adjudication artifacts.
- Configuration and prompt versions: Report schema `pilot-review-v3`; prompt `primary-prompts-2026-08-04-draft3`; timeout policy `candidate-timeouts-2026-08-04-r2`; EvalPlus adapter `self-refinement-isolated-v3` inherited from the reviewed evaluation.
- Models and benchmarks: All six adopted models over three tasks from each of HumanEval+, MBPP+, and BigCodeBench-Instruct.
- Task scope: 378 model calls, 216 candidates, 54 effective Decisions, 162 effective derived outcomes, and 216 evaluation resolutions.
- Output location: `runs/logs/pilot-review/pilot-review-six-models-20260804-r3/report.json`.
- Machine-readable manifest: Report SHA-256 `1c504117fb0d61d442cdd1d19b767070ca084265674c94c6386b79b7efa58efc`.
- Completeness summary: Observed 377 completed plus one preserved invalid model call; 53 exact-parsed plus one separately read Decision; 159 original plus three added D-protocol candidate-selection records; and 132 `PASS`, 78 functional `FAIL`, and six final `TIMEOUT` evaluation resolutions.
- Validation result: Automated counts, source validations, raw paths, timeout lineage, and adjudication completeness passed with zero blocking reason. The report correctly discloses one adjudicated Decision and requires manual raw review.
- Known issues: After report creation, exact-candidate comparison found Qwen3 Direct candidate `candidate_bbca1f4d7f568806f0569478` changed from `PASS` in evaluation `r1` to `FAIL` in `r2`. `ISSUE-20260804-12` shows adapter `v3` cannot distinguish a swallowed EvalPlus per-input timeout from functional failure, so this report cannot freeze primary.
- Parent, replacement, or superseded run: Reviews inference `run_4b0bdec98ae531232cfe9f30`, evaluation `run_286f0e7dc35e0e66fe23e95d`, and adjudication `run_387a281ce89a3147e1d4b0da`. A new report after adapter-`v4` evaluation must replace it; all current artifacts remain immutable.
- Notes: Manual inspection confirmed the adopted one-fence candidate extraction and mixed-text Critique/Plan parser behavior. The one adjudicated Decision remains reported separately from the 53 exact-parsed Decisions.

## decision-adjudication-pilot-six-models-20260804-r2

- Purpose: Apply the adopted fixed rubric once to every invalid Decision in the completed six-model pilot without changing the original model call or raw response.
- Status: Completed and independently validated.
- Start and end time: 2026-08-04 Asia/Seoul; foreground semantic review and validation completed in one work session.
- Git commit: `8f50180` (source pilot remains commit `30ca842`).
- Environment identifier: Main Python 3.12 project environment; no model or evaluator process.
- Configuration and prompt versions: Rubric `decision-adjudication-2026-08-04-r1`, SHA-256 `786c1f3ece0d3315b7d3beceb5525dbafa43ae50ef04c7f9992e2776a5e31554`; source prompt `primary-prompts-2026-08-04-draft3` remains unchanged.
- Models and benchmarks: The single invalid DeepSeek-Coder-V2-Lite Decision on `BigCodeBench/764`; all other 53 pilot Decisions were exact-parsed and not reviewed.
- Task scope: Complete set of invalid Decisions from inference `run_4b0bdec98ae531232cfe9f30`, one of one.
- Output location: `runs/logs/decision-adjudication/decision-adjudication-pilot-six-models-20260804-r2/`.
- Machine-readable manifest: Report SHA-256 `b4ab2cf4a5eb90953a49d01c33f8a2d917bdef5a682b128cee0fbf0d0235a48d`; adjudication run ID `run_387a281ce89a3147e1d4b0da`.
- Completeness summary: One invalid response reviewed, one resolved as `PRESERVE`, zero unresolved, and three supplemental `DR`/`DCR`/`DCPR` outcomes created. The source registry remains at 53 parsed Decisions and 159 derived outcomes.
- Validation result: Passed source-call/raw-hash/initial-candidate provenance, complete invalid-call coverage, rubric/input hashes, schema validation, and exactly three typed D-protocol candidate-selection records. Record-index SHA-256 is `7a2da9248106ae599e9e5a6998fde41234da0f7e1cd12050d512e4a4c37a899e`; outcome-index SHA-256 is `942f691d0e652c226c49597f8e378cbb39f27d179a66dd81ae3b17576fc4a955`.
- Known issues: Evaluation descendants existed before adoption, so provenance says `evaluation_existed_not_consulted`; no evaluation, reference, test, runtime, timeout, critique, plan, or revised candidate was used. This validation-only pilot does not enter paper estimates.
- Parent, replacement, or superseded run: Child operational artifact of inference `run_4b0bdec98ae531232cfe9f30`; it does not replace or mutate the inference run. It supersedes preserved pre-commit attempt `decision-adjudication-pilot-six-models-20260804-r1`, which recorded the same label but an older repository commit in status.
- Notes: The raw explanation states that the initial candidate is well structured and adheres to the task specification and identifies no functional defect, which maps unambiguously to `PRESERVE` under the frozen rubric.

## evaluation-pilot-six-models-20260804-r2

- Purpose: Replace invalidated six-model evaluation `r1` by evaluating the same 216 exact candidates with source-inherited `study-v0.2.0` provenance and strengthened independent validation.
- Status: Completed and independently validated; invalidated as primary-freeze evidence by `ISSUE-20260804-12`.
- Start and end time: 2026-08-04 16:50:06 to 17:18:12 Asia/Seoul; independent validation completed 17:44:03.
- Git commit: `b02d09ca7284693a579b3fde0e721fb992b272d3`.
- Environment identifier: Python 3.12.13 orchestration; EvalPlus isolated adapter `self-refinement-isolated-v3`; BigCodeBench Python 3.10.12 adapter `standalone-local-v3`.
- Configuration and prompt versions: Timeout policy `candidate-timeouts-2026-08-04-r2`, SHA-256 `b8482c2173ed0d98c29012bcf66f33fae11e8a3725040cb20a380de2f05570ba`; source study version `study-v0.2.0` inherited from terminal inference manifest.
- Models and benchmarks: All six adopted checkpoints; three HumanEval+, three MBPP+, and three BigCodeBench-Instruct pilot tasks per model.
- Task scope: The same 216 immutable candidates from source inference `run_4b0bdec98ae531232cfe9f30`, 54 each for Direct, `R`, `CR`, and `CPR`.
- Output location: Registry `runs/registry/run_286f0e7dc35e0e66fe23e95d/`; operational attempt `runs/logs/evaluation-campaign/evaluation-pilot-six-models-20260804-r2/`.
- Machine-readable manifest: Terminal `run_manifest_f1dc261747b6cda8841c9e9f`; summary SHA-256 `cc733db680c6ccc8c52de81162f308232119abe62c5aa5aabb6c301308b51644`; validation SHA-256 `311b5663667046183a0eba301933dc93dafb5c9f1d17f0789e1d29c41503ddc1`.
- Completeness summary: 216/216 primary attempts and resolutions, 11 timeout-only confirmations, and 227 immutable raw outputs. Final outcomes are 132 `PASS`, 78 functional `FAIL`, and six `TIMEOUT`, with zero evaluator failures.
- Validation result: Passed exact source lineage, all counts, schemas, raw hashes, confirmation completeness, terminal manifest, and `study-v0.2.0` equality for manifest, summary, attempts, and resolutions. This completes the rerun required by `ISSUE-20260804-11`; later cross-run stability analysis invalidates freeze use for the separate evaluator issue below.
- Known issues: `ISSUE-20260804-12`. EvalPlus adapter `v3` cannot reveal whether a false detail came from its swallowed per-input timeout. One identical deterministic candidate differs from the prior run, so the 78 functional failures cannot be frozen without adapter-`v4` replacement evaluation. Source Decision issue `ISSUE-20260804-08` does not affect the 216 generated candidates.
- Parent, replacement, or superseded run: Replaces invalidated attempt `evaluation-pilot-six-models-20260804-r1` / run `run_5b5b7b1dae795ad7f35db0da`; no old evaluation record is resumed, copied, or mutated.
- Notes: Logical evaluation run ID is `run_286f0e7dc35e0e66fe23e95d`. Monitoring distinguishes 11 primary from six final timeouts. No record is reclassified in place, and evaluator information never enters a model prompt.

## pilot-review-six-models-20260804-r2

- Purpose: Review complete six-model replacement inference and candidate evaluation with model/task-scope-derived expectations, representative raw-response inspection, and complete primary-timeout lineage.
- Status: Completed; automated gate is `review_required` and primary remains blocked.
- Start and end time: 2026-08-04 Asia/Seoul; foreground report generation completed in one invocation after evaluation validation.
- Git commit: Review-count correction `4034e9e`; source inference and evaluation retain their own recorded commits.
- Environment identifier: Main Python 3.12 project environment; read-only access to the inference/evaluation registries.
- Configuration and prompt versions: Report schema `pilot-review-v3`; `primary-prompts-2026-08-04-draft3`; timeout policy `candidate-timeouts-2026-08-04-r2`.
- Models and benchmarks: Six adopted models and all three benchmarks on the frozen nine-task pilot scope.
- Task scope: 378 model calls, 216 generated candidates, and every generated-candidate evaluation from inference `run_4b0bdec98ae531232cfe9f30` and evaluation `run_5b5b7b1dae795ad7f35db0da`.
- Output location: `runs/logs/pilot-review/pilot-review-six-models-20260804-r2/report.json`.
- Machine-readable manifest: Report SHA-256 `f0b3620d0b8b8b51159665d6adf4c0129f5a7e2617b4ae71e990f6fad06c0b66`.
- Completeness summary: Correctly expects and observes 378 calls and 216 candidates; expects 54 Decisions/162 derived outcomes but observes 53/159. It traces 27 primary timeouts through confirmation: 20 resolve to functional `FAIL`, one to `PASS`, and six remain confirmed final `TIMEOUT`.
- Validation result: Representative model-stage raw responses satisfy the adopted candidate and mixed-text artifact contracts. The gate blocks only on one DeepSeek `BigCodeBench/764` categorical Decision length-stop and its three unavailable derived outcomes. Evaluation outcomes are diagnostic only because `ISSUE-20260804-11` subsequently found incorrect study-version provenance in the parent evaluation.
- Known issues: `ISSUE-20260804-08`, `ISSUE-20260804-09`, and `ISSUE-20260804-11`.
- Parent, replacement, or superseded run: Supersedes report `pilot-review-six-models-20260804-r1`, whose immutable SHA-256 `b36775f1e58cc3f636cb3226f6f8c39afab0765c65549edb032c47a618df0651` used obsolete hard-coded four-model expectations. A new review is required after replacement evaluation.
- Notes: The six final timeouts are all `HumanEval/129` EvalPlus internal `CandidateTimeout` outcomes near 65 seconds, not exhaustion of the 120-second outer confirmation limit. Functional outcomes never enter model prompts.

## evaluation-pilot-six-models-20260804-r1

- Purpose: Evaluate every generated Direct, `R`, `CR`, and `CPR` candidate from the complete six-model replacement inference, separately from model inference and without exposing evaluator information to any model.
- Status: Invalidated for study-version provenance after terminal completion and independent artifact/count validation.
- Start and end time: 2026-08-04 16:01:29 to 16:33:52 Asia/Seoul.
- Git commit: `75a323c521bec7db18713c7e54d76cf571bd0248`.
- Environment identifier: Python 3.12.13 orchestration; EvalPlus isolated adapter `self-refinement-isolated-v3`; BigCodeBench Python 3.10.12 adapter `standalone-local-v3`.
- Configuration and prompt versions: Timeout policy `candidate-timeouts-2026-08-04-r2`, SHA-256 `b8482c2173ed0d98c29012bcf66f33fae11e8a3725040cb20a380de2f05570ba`; candidate prompt versions are inherited as provenance only and are not evaluator inputs.
- Models and benchmarks: All six adopted checkpoints; three HumanEval+, three MBPP+, and three BigCodeBench-Instruct pilot tasks per model.
- Task scope: 216 candidates from source scope `pilot-public-length-quantiles-2026-08-04-r2`: 54 each for Direct, `R`, `CR`, and `CPR`.
- Output location: Registry `runs/registry/run_5b5b7b1dae795ad7f35db0da/`; operational attempt `runs/logs/evaluation-campaign/evaluation-pilot-six-models-20260804-r1/`.
- Machine-readable manifest: Terminal `run_manifest_3ec07ce4f711ecfbed266b6a`; summary SHA-256 `fec416f203f28ba67a2355ceed41666c70f881d8c1b4c3d196da6167c6bd6773`; first validation report SHA-256 `926c4753f5b23653553affdeba276ea0fb152d0575e7ee578ff0741eabd64353`.
- Completeness summary: 216/216 primary attempts and resolutions, 27 timeout-only confirmations, and 243 immutable raw evaluator outputs. Final outcomes are 133 `PASS`, 77 functional `FAIL`, and six `TIMEOUT`, with zero evaluator failures.
- Validation result: Record counts, lineage, schemas, raw hashes, and timeout confirmation completeness passed under the prior validator. The strengthened validator rejects the run because its manifest, evaluation records, and resolutions carry hard-coded `study-v0.1.6` instead of source inference `study-v0.2.0`; immutable records are not repaired.
- Known issues: `ISSUE-20260804-11` invalidates this run as final pilot evidence. `ISSUE-20260804-10` records the corrected monitoring-label ambiguity. Source inference issue `ISSUE-20260804-08` does not affect its 216 candidate evaluations.
- Parent, replacement, or superseded run: Parent inference `run_4b0bdec98ae531232cfe9f30`; a new evaluation run under source-inherited `study-v0.2.0` must replace it.
- Notes: Logical evaluation run ID is `run_5b5b7b1dae795ad7f35db0da`. The functional results remain useful only as diagnostic evidence; they are not relabeled, copied into new records, or exposed to model prompts.

## campaign-pilot-six-models-20260804-r1

- Purpose: Complete replacement pilot inference for the adopted six-model panel using the unchanged nine public-only task IDs and seven model-resident phases.
- Status: Completed and independently validated.
- Start and end time: 2026-08-04 12:50:42 to 15:34:10 Asia/Seoul.
- Git commit: `30ca842ad2cf7c2c422a827245ebc7dfae5f3a65`.
- Environment identifier: `vllm-environment-2026-08-03-r1`; vLLM 0.26.0, Python 3.12.13, TP=2 batch-invariant PyTorch-native greedy inference.
- Configuration and prompt versions: Campaign `pilot-campaign-2026-08-04-r4` SHA-256 `5af37eaf34fe5a693b57d3d94036fb8b736e5191a5a12232012d2796cda405d7`; inference `primary-inference-2026-08-04-r3` SHA-256 `d136c5af178ace0480209be85e1c6725d24742e92208e1864c6a9cbfa324d09e`; prompt `primary-prompts-2026-08-04-draft3` SHA-256 `ecf957cc0d2ed3f5eac33ee70162d1ecdf5b137b0c64d21cb25fedb6add20e63`; scope configuration SHA-256 `ea69cbb306838ae4052e3d313e2fdaedcc1c700b5aab71e0c1493a7261c53805`.
- Models and benchmarks: All six adopted checkpoints; three HumanEval+, three MBPP+, and three BigCodeBench-Instruct tasks per model.
- Task scope: `pilot-public-length-quantiles-2026-08-04-r2`, public export SHA-256 `9beec376c3d55f367356ba637e26b23bbcce373ba7813232223a33a6d69204c3`; 6 models × 9 tasks × 7 phases = 378 planned task-phase units.
- Output location: Registry `runs/registry/run_4b0bdec98ae531232cfe9f30/`; operational attempt `runs/logs/model-campaign/campaign-pilot-six-models-20260804-r1/`.
- Machine-readable manifest: Terminal `run_manifest_086a0feb15b4d987ab63a0e7`; summary SHA-256 `a4cea28e7f180cc83e2f72759da39748d1ec3a5ac8225deadec836be144dbe37`; independent validation SHA-256 `6498c0f1e79a43c5f787bbaa4590d1baae87b19bed36356cdc6e9b8eb248d6ae`.
- Completeness summary: All 378 planned model calls and raw responses are present across six models, nine tasks, and seven phases. Records comprise 377 completed calls and one invalid Decision response; 216 candidates (54 each Direct/`R`/`CR`/`CPR`), 54 critiques, 54 plans, 53 Decisions, and 159 derived D-protocol outcomes are preserved.
- Validation result: Passed terminal metadata, exact model/task/phase counts, manifest lineage, model-call schemas, and all 378 raw-response hashes. Both GPUs were clear after completion.
- Known issues: `ISSUE-20260804-08`: DeepSeek-Coder-V2-Lite reached the 64-token Decision cap on `BigCodeBench/764` with explanatory prose instead of the required categorical value. This leaves only that model-task pair's three derived D outcomes unavailable and does not block evaluation of the 216 generated candidates.
- Parent, replacement, or superseded run: Prospective six-model replacement for historical four-model draft3 inference `run_856e8d87f7ed9bec7dec9a5c`; no prior artifact is mutated or reused as a candidate.
- Notes: Logical run ID is `run_4b0bdec98ae531232cfe9f30`. No evaluator result was available to the inference worker, and no malformed response was repaired or reparsed.

## vllm-primary-smoke-six-models-20260804-r1

- Purpose: Certify one common frozen serving path for the complete adopted six-model panel using the exact primary inference configuration and direct canonical chat-template token IDs.
- Status: Completed and independently validated.
- Start and end time: 2026-08-04 11:56:25 to 12:15:37 Asia/Seoul.
- Git commit: `53c9f4a30335e15a00fcabd851abf2283ad34696`.
- Environment identifier: `vllm-environment-2026-08-03-r1`; vLLM 0.26.0, PyTorch 2.11.0+cu130, TP=2, PyTorch-native sampler, batch invariance enabled.
- Configuration and prompt versions: `primary-inference-2026-08-04-r3`, SHA-256 `d136c5af178ace0480209be85e1c6725d24742e92208e1864c6a9cbfa324d09e`; model manifest `model-checkpoints-2026-08-04-r2`, SHA-256 `eb87e51762c69d248f57a9cbd08748ab3f7d868a7b566cab5534e32d6cd30d66`; fixed validation-only prompt.
- Models and benchmarks: All six adopted checkpoints in manifest order; no benchmark task or evaluator was executed.
- Task scope: One validation-only function-generation request repeated twice per model under the common 16,384-token context and 4,096-token candidate output cap.
- Output location: `runs/logs/vllm-primary-inference-smoke/vllm-primary-smoke-six-models-20260804-r1/`.
- Machine-readable manifest: Terminal `status.json`; summary SHA-256 `a12728be4f3f341c678a699f0dcb749746146d5ad15a30b7fa08e37290c6f225`; independent `validation.json` SHA-256 `b7e46cd97267a1f8d84d53bda7afc83e0c01aac798e59e133c9784b579eb6681`; six exact result hashes are recorded in that report.
- Completeness summary: 6/6 models loaded at 16K and generated two byte/token-identical greedy responses using `prompt_input_mode=chat-template-token-ids`; all result records include exact prompt/output token IDs and counts.
- Validation result: Passed terminal metadata, captured/committed configuration equality, six-model order, snapshot provenance, common decoding/sampler settings, prompt budget, raw-response equality, token equality, and result hashes. Post-run GPUs were both 15 MiB and 0% utilization with no compute process.
- Known issues: None. Normal vLLM worker shutdown warnings left no incomplete result or GPU process.
- Parent, replacement, or superseded run: Full-panel successor to corrected new-architecture compatibility attempt `vllm-smoke-new-models-20260804-r2`; neither contains experiment candidates.
- Notes: This freezes the existing common vLLM 0.26.0 environment and `primary-inference-2026-08-04-r3` for the six-model replacement pilot. No model-specific serving environment is used.

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
