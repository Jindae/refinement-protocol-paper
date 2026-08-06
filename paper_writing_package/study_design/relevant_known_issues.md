# Selected known issues relevant to interpretation

## ISSUE-20260806-14: Primary model outputs include malformed candidates and non-exact Decisions

- First observed: 2026-08-06 after terminal primary inference validation
- Status: Mitigated; raw behavior retained for analysis
- Severity: Major
- Description: Eight Direct responses and ten revision responses violate the common single-complete-Python-fence contract. In addition, 202 Decision responses fail the strict exact parser: 156 are exact categorical values followed only by a period and 46 are directionally unambiguous explanations.
- Affected tasks/models/benchmarks/runs: Primary inference `run_c99d3b1d562acc3e80026e48`; malformed candidates occur in DeepSeek, Devstral, Qwen3, and Gemma outputs. Invalid Decisions occur in DeepSeek (156) and Qwen3 (46).
- Impact on results: Eight malformed initials block 48 dependent model calls and leave 32 generated candidate-condition artifacts unavailable. Ten further revision outputs lack candidate artifacts. Excluding these rows would bias model comparisons; calling them evaluator `FAIL` would claim tests ran when they did not.
- Evidence: Independent inference validation passes 70,386 model-call/raw-response records. The difference from 70,434 scheduled task-phase units is exactly the 48 blocked dependents. Seven malformed Direct responses are length-capped with an incomplete fence and one has multiple fenced blocks.
- Resolution or mitigation: `DEC-20260806-33` separates 156 deterministic normalizations from 46 blinded semantic adjudications. `DEC-20260806-34` preserves legacy raw statuses, reports candidate format failures as `malformed_candidate`, retains all rows, assigns only the separate end-to-end success measure a zero, and leaves functional transitions unevaluated. No response is salvaged or regenerated.
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
