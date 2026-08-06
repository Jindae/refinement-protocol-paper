# Selected known issues relevant to interpretation

## ISSUE-20260806-19: v0.2.0 Critique and Planning roles overlap

- First observed: 2026-08-06 during interpretation of the non-paper-facing full-scope snapshot
- Status: Resolved prospectively; historical evidence retained
- Severity: Major construct-validity issue for v0.2.0 CR/CPR interpretation
- Description: The v0.2.0 Critique prompt combined diagnosis, location, and reasons while Planning
  repeated changes and locations. CPR Revision then received both Critique and Plan. Consequently its
  CR/CPR contrast could not isolate a distinct planning role, and a different role assignment could
  plausibly produce a different result.
- Affected tasks/models/benchmarks/runs: All v0.2.0 Critique, Planning, CR, and CPR artifacts in
  `run_c99d3b1d562acc3e80026e48` and their provisional analyses. Initial, Decision, Direct Revision,
  benchmark data, and evaluator behavior are not affected.
- Impact on results: v0.2.0 CR/CPR outcomes remain descriptive formative evidence but are not the
  paper-facing answer to the role-separated stage-composition RQ.
- Resolution or mitigation: `DEC-20260806-40` freezes v0.3.0 role-separated prompts and direct-input
  boundaries before replacement inference. Old inputs/results remain immutable and reproducible.
- Required reruns or regenerated artifacts: Regenerate C, CR, P, CPR; evaluate new CR/CPR only; join
  them with exact reused Direct/R/Decision evidence in a new processed dataset.
- Related decision: `DEC-20260806-40`.


## ISSUE-20260806-17: One BigCodeBench confirmation could not allocate evaluator memory

- First observed: 2026-08-06 during the active primary candidate timeout-confirmation phase
- Status: Investigating; immutable failure preserved
- Severity: Major for final completeness; isolated to one captured evaluation attempt so far
- Description: Confirmation evaluation `evaluation_35c22095e76c4f35ba2a28be` for
  `BigCodeBench/1042` ended after 69.811 seconds with worker `OSError: [Errno 12] Cannot allocate
  memory: '/tmp/bigcodebench-41t_5bzj'`. The failure arose while the isolated evaluator worker was
  creating its private temporary directory and produced no functional outcome.
- Affected tasks/models/benchmarks/runs: Candidate `candidate_0b876d790d64fddd621dbe81` in active
  evaluation run `run_b25b1ec137928799f30217af`; the prior primary attempt is preserved as a timeout.
  No model inference, candidate bytes, benchmark tests, timeout configuration, or other evaluation
  record is changed.
- Impact on results: The candidate is indeterminate. Treating this record as functional `FAIL` or as
  a confirmed final `TIMEOUT` would violate the analysis contract. It currently produces explicit
  evaluator-failure missingness in a provisional snapshot and prevents final acceptance until
  separately resolved.
- Evidence: The typed record and raw output preserve evaluator version `0.2.5`, configuration SHA-256
  `9a5c2eda274b56fab01523a83d466e85ac4964cd4d9fcc51c9f908ee591a1f13`, 120-second wall limit,
  error type/message, and prior evaluation lineage. At inspection time the host had substantial free
  memory and disk, so the historical cause cannot be reduced to a persistent disk-capacity problem;
  transient host pressure or candidate/evaluator resource behavior remains possible.
- Temporary action: Do not alter the active campaign or relabel the immutable record. Surface the
  exact failure in every provisional review.
- Resolution or mitigation: After the campaign reaches a terminal state, inspect all evaluator
  failures and decide the remediation before final analysis. The conservative candidate is a
  separately versioned targeted retry of the exact candidate/task under the same frozen evaluator
  and timeout policy, preserving this failed attempt. Because adopting retry semantics can affect
  final coverage, it requires an explicit recorded decision rather than an automatic relabel.
- Required reruns or regenerated artifacts: Pending the terminal failure inventory and explicit
  remediation decision. No inference rerun is indicated.
- Related decision: `DEC-20260806-38` (provisional analysis treatment only).


## ISSUE-20260806-14: Primary model outputs include malformed candidates and non-exact Decisions

- First observed: 2026-08-06 after terminal primary inference validation
- Status: Mitigated; raw behavior retained for analysis
- Severity: Major
- Description: Eight Direct responses and ten revision responses violate the common single-complete-Python-fence contract. In addition, 202 Decision responses fail the strict exact parser: 156 are exact categorical values followed only by a period and 46 are directionally unambiguous explanations.
- Affected tasks/models/benchmarks/runs: Primary inference `run_c99d3b1d562acc3e80026e48`; malformed candidates occur in DeepSeek, Devstral, Qwen3, and Gemma outputs. Invalid Decisions occur in DeepSeek (156) and Qwen3 (46).
- Impact on results: Eight malformed initials block 48 dependent model calls and leave 32 generated candidate-condition artifacts unavailable. Ten further revision outputs lack candidate artifacts. Excluding these rows would bias model comparisons; calling them evaluator `FAIL` would claim tests ran when they did not.
- Evidence: Independent inference validation passes 70,386 model-call/raw-response records. The difference from 70,434 scheduled task-phase units is exactly the 48 blocked dependents. Seven malformed Direct responses are length-capped with an incomplete fence and one has multiple fenced blocks.
- Resolution or mitigation: `DEC-20260806-33` separates 156 deterministic normalizations from 46 evaluation-result-free readings of non-exact Decision response directions. `DEC-20260806-34` preserves legacy raw statuses, reports candidate format failures as `malformed_candidate`, retains all rows, assigns only the separate end-to-end success measure a zero, and leaves functional transitions unevaluated. No response is salvaged or regenerated.
- Required reruns or regenerated artifacts: No inference rerun. One complete pre-evaluation Decision resolution batch and evaluation of the 40,206 existing candidate artifacts are required.
- Related decision: `DEC-20260806-33`, `DEC-20260806-34`.


## ISSUE-20260804-12: EvalPlus hides per-input timeout as functional failure

- First observed: 2026-08-04
- Status: Resolved
- Severity: Major
- Description: EvalPlus 0.3.1 catches per-input `TimeoutException` together with assertions and ordinary candidate exceptions, stores a false detail, and returns functional `FAIL`. Its raw result has no timeout-cause field. The same deterministic Qwen3 Direct candidate on `HumanEval/129` consequently changed from `PASS` in six-model evaluation `r1` to plus-suite `FAIL` in `r2` under the same evaluator-configuration hash.
- Affected tasks/models/benchmarks/runs: Direct candidate `candidate_bbca1f4d7f568806f0569478` (`HumanEval/129`, Qwen3-Coder-30B-A3B-Instruct-FP8), six-model evaluations `run_5b5b7b1dae795ad7f35db0da` and `run_286f0e7dc35e0e66fe23e95d`, and pilot review `pilot-review-six-models-20260804-r3`. Other EvalPlus functional failures in adapter `v3` are conservatively affected because old raw files cannot establish whether a swallowed timeout occurred.
- Impact on results: Evaluation `r2` is complete and provenance-correct but cannot be used to freeze the pilot or report functional outcomes. Replacement `r3` is the accepted pilot evidence. A transient resource delay can otherwise become a false `FAIL` without entering the confirmation path. Inference, Decision adjudication, candidate bytes, BigCodeBench outcomes, benchmark data, and accepted reference audits are unaffected.
- Evidence: Candidate source SHA-256 is `a65c9ce7d5b6f3e5ef39a27594958069e8a3b65ccdd87ab39474006ba39d404e`. Evaluation `r1` record `evaluation_058c72c9ba9c05fdc9e317f5` passed base 10/10 and plus 189/189 in 6.365 seconds; `r2` record `evaluation_1c7328622fe2a1911b4c0360` passed base 10/10 but returned plus `FAIL` after 6.993 seconds. Both use evaluator-configuration SHA-256 `1e8602cd12488e0e6e4eae6f0caf8cffb95855073b6e4e43e8c200efa12b25c7`. Static inspection of the pinned upstream handler confirms the swallowed exception path; repeated same-candidate diagnostics at the one-second per-input floor passed, so timeout is a supported inference rather than a retrospective fact encoded in old raw output.
- Temporary action: Preserve both evaluation registries and review unchanged, block the pilot freeze, and do not relabel old records.
- Resolution or mitigation: Adopted `DEC-20260804-30` adds input-index timeout tracking without changing benchmark tests or oracle. Adapter `self-refinement-isolated-v4` maps only timeout-explained false details to `TIMEOUT`, gives any independent failing detail precedence, and preserves the indexes in raw output. Synthetic regression tests cover timeout-only, ordinary incorrect, mixed failure/timeout, and outer-wall timeout paths. Replacement evaluation `run_38cf240201dfb892765eccc2` independently validated all 216 resolutions and all 11 confirmation traces under adapter `v4`; every confirmation records the relevant timeout indexes, while six mixed cases with an independent false detail remain functional `FAIL` as specified.
- Required reruns or regenerated artifacts: Complete. Evaluation attempt `evaluation-pilot-six-models-20260804-r3` and review `pilot-review-six-models-20260804-r4` replace `r2`/`r3` as freeze evidence. No inference or Decision adjudication was rerun.
- Related decision: `DEC-20260804-30` (Adopted).


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
