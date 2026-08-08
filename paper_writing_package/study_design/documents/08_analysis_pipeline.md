# Analysis Pipeline

## 1. Purpose and freeze boundary

This document defines the result-independent transformation and metric pipeline for RQ1–RQ4.
The implementation is frozen before primary outcomes are inspected. It consumes only independently
validated, terminal inference and evaluation runs and an independently validated Decision
adjudication batch when invalid separate Decisions exist. For `study-v0.4.0`, this is intentionally a
composite lineage: validated v0.2.0 Initial/Direct Revision/Decision sources, validated v0.3.0
Critique/Planning/CR/CPR sources, and validated v0.4.0 `SC-*` sources. The pipeline never treats the
three inference registries as one raw run.

The pipeline has three layers:

1. immutable registry records and validated run manifests,
2. one versioned canonical processed dataset,
3. one independently validated output directory per research question.

No paper-facing number is entered manually. Generated files are not silently overwritten; a changed
input, rule, or script requires a new dataset or analysis identifier.

The existing v0.3.0 implementation remains the reproducible seven-protocol analysis path. The
twelve-protocol v0.4.0 builder and all four RQ executors are implemented and validated. Reporting
version `primary-analysis-2026-08-08-r4` merges the former stage-composition and transition-balance
questions into RQ1 without changing the underlying metrics or estimands.

## 2. Canonical processed dataset

`analysis_tools/build_processed_dataset.py` creates:

```text
data/processed/<dataset-id>/
├── outcomes.jsonl
├── stage_calls.jsonl
├── data_dictionary.json
├── manifest.json
└── validation.json
```

`outcomes.jsonl` has one row for every planned model-task-protocol combination across Direct, `R`,
`CR`, `CPR`, `DR`, `DCR`, `DCPR`, `SC-CR`, `SC-CPR`, `SC-DR`, `SC-DCR`, and `SC-DCPR`. A failed call, missing candidate, unresolved Decision, final
timeout, or evaluation infrastructure failure does not remove its row. Such a row carries an explicit
analysis status and no invented functional outcome. The primary end-to-end success field is separate
from evaluator functional correctness: a completed `PASS` is 1, a completed functional `FAIL` or
model-attributable `malformed_candidate` is 0, and timeout/evaluator failure remains null.

`stage_calls.jsonl` has one row for every actual model-call attempt. It preserves retry lineage,
status, stage, input/output tokens, and whether the attempt is the effective logical call. This table
is the source for Experimental Token Consumption and prevents repeated per-protocol rows from
double-counting physically executed calls.

The manifest records the study and analysis versions, every source inference/evaluation/adjudication identifier,
source manifest and validation hashes, producer commit, row counts, status counts, and checksum of
every derived data file. The validator requires a complete `models × tasks × 12 protocols` grid and
checks functional missingness, row uniqueness, schema versions, and file hashes.
The v0.2.0 broad-role CR/CPR outcomes remain a separately labeled formative/reference dataset and do
not enter v0.3.0 paper-facing CR/CPR estimates. Direct, `R`, and their evaluations may be reused only
through their exact candidate IDs and hashes; new CR/CPR rows must point to v0.3.0 candidates.

Single-call rows point only to v0.4.0 candidates and their exact v0.2.0 initial references. For
`SC-D*`, the main row uses emitted code regardless of the reported Decision label. Separate fields
record exact/invalid label parsing and exact/normalized code change. Optional label-enforced rows are
supplementary derived outcomes and never replace the main 12-protocol grid.

The processed dataset preserves the role-separated information path: Critique determines whether a
functional problem exists and diagnoses it; Planning converts the stored diagnosis into change
instructions; CR consumes Critique; and CPR consumes Plan without direct Critique input. A no-problem
Critique and no-change Plan remain observed artifacts rather than missing stages. Analysis does not
retroactively correct an upstream diagnosis, infer an unobserved plan, or remove role-crossing text.
Accordingly, RQ1 contrasts estimate complete protocol paths, not independently labeled semantic
accuracy of Critique or Planning.

## 3. Correctness and missingness

Only a final evaluation resolution with `status=completed` and functional outcome `PASS` or `FAIL`
contributes binary correctness. Final `TIMEOUT`, evaluation failure, exclusion, missing resolution,
and unresolved Decision remain separate nonfunctional states.

Primary protocol success rates and paired contrasts use `end_to_end_success`, so malformed model
outputs remain in the denominator as unsuccessful without being mislabeled as evaluator functional
`FAIL`. Conditional functional pass rates retain only completed evaluator `PASS`/`FAIL` resolutions.
Both views always report total rows, malformed candidates, timeouts, evaluation failures, and other
exclusions. TIMEOUT and evaluator/infrastructure failure are never imputed as zero.

Initial-to-final transitions are defined only when both outcomes are determinate:

- `FAIL → PASS`: Repair
- `PASS → FAIL`: Correct-to-Incorrect Regression
- `PASS → PASS`: Functional Preservation
- `FAIL → FAIL`: Unrepaired Failure

Malformed initial candidates have no functional transition and are reported separately. They do not
enter repair/regression denominators because no benchmark evaluation established their initial state.

Candidate change is recorded twice. Exact change compares stored source bytes as text. Normalized
change only converts line endings to LF, removes trailing whitespace on each line, and removes outer
blank lines. It does not change indentation, internal blank lines, syntax, or program content.

## 4. Token accounting

Every token measure retains input, output, and total components.

- Initial Generation Cost is the shared Direct Generation call.
- Incremental Protocol Cost contains the calls logically required after the shared initial.
- End-to-End Protocol Cost is Initial Generation Cost plus Incremental Protocol Cost.
- Experimental Token Consumption sums every returned call attempt physically executed for one
  model-task pair exactly once from `stage_calls.jsonl`.
- Protocol-Implied Token Cost uses the logical path of one protocol, even though shared artifacts were
  generated once for the experiment.
- Decision overhead is the Refinement-Need Decision call.
- Avoided Refinement Tokens are the corresponding always-refine calls skipped by `PRESERVE`.
- Net Token Saving is always-refine end-to-end cost minus Decision-conditioned end-to-end cost.

For `R`, the refinement cost is Direct Revision. For `CR`, it is Critique Generation plus
Critique-Conditioned Revision. For `CPR`, it is Critique Generation plus Revision Planning plus
Plan-Conditioned Revision. A Decision-conditioned cost is Decision only for `PRESERVE`, and Decision
plus the corresponding refinement path for `REFINE`.

Each `SC-*` protocol has one incremental model call. Its Decision-like label does not alter the main
candidate cost because code is always emitted by that same call.

Token comparisons are made within a model. Tokenizer-specific totals are not treated as absolute
compute comparisons between models.

## 5. RQ-specific outputs

`analysis_tools/run_rq_analysis.py` runs one RQ at a time and writes JSON metrics, CSV tables, a
machine-generated review report, a provenance manifest, and an independent validation report below
`results/summaries/<analysis-id>/<rq>/`.

### RQ1

- final pass-rate and refinement-gain summaries for Direct, `R`, `CR`, and `CPR`,
- Direct versus `R`, `R` versus `CR`, and `CR` versus `CPR` paired contrasts,
- deterministic 10,000-resample task-level paired bootstrap 95% confidence intervals,
- improved, worsened, unchanged counts and supplementary exact two-sided McNemar p-values,
- all four initial-to-final transition counts for every protocol,
- repair rate among initially incorrect candidates,
- regression and preservation rates among initially correct candidates,
- repair-minus-regression count and net-gain rate,
- exact and normalized candidate-change cross-tabs,
- an integrated performance table that places pass rate beside repair, regression, preservation,
  malformed output, and cost so that pass-rate differences are not interpreted in isolation.

### RQ2

- `R` versus `DR`, `CR` versus `DCR`, and `CPR` versus `DCPR`,
- correct-`PRESERVE` and incorrect-`REFINE` rates,
- Prevented Regression, Safe Preservation, Missed Repair, and Unsuccessful Refinement Skipped,
- always-refine와 Decision-conditioned 조건의 repair 및 regression count/rate를 동일한
  functional-transition complete-case 분모에서 직접 비교하고, 방지된 regression과 놓친
  repair로 correctness difference를 재구성한 decomposition,
- correctness difference and Net Token Saving by model-benchmark combination,
- all-resolved results and exact-Decision-only sensitivity results,
- descriptive Pearson and Spearman relationships with observed initial pass rate.

The correlation output is descriptive, not causal. An additional inferential regression model is not
silently selected after results are seen; adopting one would require a prospective decision and new
analysis version.

### RQ3

- paired `CR` versus `SC-CR` and `CPR` versus `SC-CPR` correctness comparisons,
- paired `DR` versus `SC-DR`, `DCR` versus `SC-DCR`, and `DCPR` versus `SC-DCPR`,
- repair/regression/preservation decomposition for every pair,
- reported Decision label by exact and normalized candidate change,
- `PRESERVE`-changed and `REFINE`-unchanged counts,
- main emitted-code and supplementary label-enforced outcomes kept separate.

### RQ4

- input/output/total tokens by model, benchmark, and stage,
- protocol-level incremental and end-to-end cost,
- physical Experimental Token Consumption,
- Decision overhead, avoided refinement cost, and Net Token Saving,
- common-complete-case correctness-cost Pareto frontiers within each model-benchmark combination,
- incremental tokens per additional correct solution when the correctness increment is positive.

Undefined efficiency ratios remain null with a reason rather than using zero or infinity.

## 6. Statistical reproducibility

The configuration is versioned in `analysis_tools/analysis_config.toml`. Each bootstrap group obtains
a stable seed derived from the frozen base seed and its RQ/model/benchmark/contrast identity. The
bootstrap samples paired tasks, not aggregate rates. CSV and JSON ordering is deterministic.

## 7. Paper and replication package path

The processed manifest and each RQ manifest provide the source fields needed for the later
`paper_result_manifest`: RQ, source run identifiers, canonical dataset, analysis configuration,
script/output directory, validation, checksums, and producer commit.

The accepted final RQ results are promoted by an allowlist-based package step that includes their validated
processed data, scripts, tables, report, and manifest to `paper_writing_package`. Only final accepted
results and redistributable/sanitized inputs may then be exported to `replication_package`. Pilot,
invalidated, superseded, private-path, model-weight, cache, and debugging artifacts are excluded.

The minimum public result-reproduction path will be:

```text
accepted raw records → build processed dataset → validate dataset
                     → run one RQ analysis → validate RQ output
```

Experiment reproduction remains a separate, more resource-intensive path.

## Exploratory Mechanism Follow-up

`analysis_tools/followup_analysis.py`는 frozen
`analysis_tools/followup_analysis_config.toml`을 사용해 accepted outcome gzip과 validated
role-separated registry를 직접 읽는다. 다음 immutable tables를 생성한다.

- `task_set_overlap.csv`와 `topology_net_decomposition.csv`
- `decision_mediation.csv`
- `reachability_summary.csv`, `reachability_multiplicity.csv`,
  `reachability_protocol_contribution.csv`
- `artifact_chain_detail.csv`와 `artifact_chain_summary.csv`

Artifact label은 exact frozen phrase에 기반한 conservative surface classification이다.
`problem_or_other`는 functional problem의 semantic truth가 아니며 `change_or_other`도 실제 change
instruction의 완전한 판정이 아니다. Blinded annotation audit 전에는 진단 정확도로 해석하지
않는다. Manifest는 source hashes, configuration hash, producer commit, table hashes와 row counts를
기록하며 별도 validator가 이를 확인한다.

## 8. Non-paper-facing progress snapshots

While the frozen evaluation campaign is in its deferred timeout-confirmation phase, an operator may
create an explicitly provisional snapshot to inspect coverage and prepare every RQ output. This does
not relax the terminal validation gate above. The snapshot is written under `data/interim/`, records
the SHA-256 and identity of every evaluation attempt visible at one capture time, synthesizes
resolutions only for completed primary/confirmation evidence under the already frozen timeout
policy, and leaves every pending confirmation without an evaluation resolution.

The complete `models × tasks × 12 protocols` grid is retained. Thus pending confirmations appear as
explicit indeterminate rows rather than disappearing from denominators. Provisional dataset and RQ
manifests require `result_status=provisional` and `paper_facing=false`; RQ execution additionally
requires an explicit `--allow-provisional` acknowledgement. `provisional_review.json` reports
pending confirmations, missingness by model/benchmark/protocol, and exact evaluator/infrastructure
failures. These outputs can guide implementation checks, but cannot be promoted to the paper-writing
package or cited as final results.

After the evaluation attempts reached terminal state and passed independent validation, accepted
four-RQ dataset `primary-final-v04-20260808-r5` was rebuilt from registry
`EvaluationResolutionRecord` artifacts under a new dataset identifier. No provisional synthetic
resolution was copied or promoted. `analysis_tools/build_final_processed_dataset.py` performs the
three-lineage join and superseding-remediation check, reads the analysis version from the same frozen
configuration whose hash it records, and is rejected by validation if those versions disagree;
`build_paper_assets.py` produces validated compact table and chart source data. Interpretation and
exact accepted paths are recorded in `09_results_analysis.md`.
