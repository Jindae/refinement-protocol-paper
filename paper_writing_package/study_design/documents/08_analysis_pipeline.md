# Analysis Pipeline

## 1. Purpose and freeze boundary

This document defines the result-independent transformation and metric pipeline for RQ1–RQ4.
The implementation is frozen before primary outcomes are inspected. It consumes only independently
validated, terminal inference and evaluation runs and an independently validated Decision
adjudication batch when invalid Decisions exist.

The pipeline has three layers:

1. immutable registry records and validated run manifests,
2. one versioned canonical processed dataset,
3. one independently validated output directory per research question.

No paper-facing number is entered manually. Generated files are not silently overwritten; a changed
input, rule, or script requires a new dataset or analysis identifier.

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
`CR`, `CPR`, `DR`, `DCR`, and `DCPR`. A failed call, missing candidate, unresolved Decision, final
timeout, or evaluation infrastructure failure does not remove its row. Such a row carries an explicit
analysis status and no invented functional outcome. The primary end-to-end success field is separate
from evaluator functional correctness: a completed `PASS` is 1, a completed functional `FAIL` or
model-attributable `malformed_candidate` is 0, and timeout/evaluator failure remains null.

`stage_calls.jsonl` has one row for every actual model-call attempt. It preserves retry lineage,
status, stage, input/output tokens, and whether the attempt is the effective logical call. This table
is the source for Experimental Token Consumption and prevents repeated per-protocol rows from
double-counting physically executed calls.

The manifest records the study and analysis versions, inference/evaluation/adjudication identifiers,
source manifest and validation hashes, producer commit, row counts, status counts, and checksum of
every derived data file. The validator requires a complete `models × tasks × 7 protocols` grid and
checks functional missingness, row uniqueness, schema versions, and file hashes.

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
- improved, worsened, unchanged counts and supplementary exact two-sided McNemar p-values.

### RQ2

- all four initial-to-final transition counts for every protocol,
- repair rate among initially incorrect candidates,
- regression and preservation rates among initially correct candidates,
- repair-minus-regression count and net-gain rate,
- exact and normalized candidate-change cross-tabs.

### RQ3

- `R` versus `DR`, `CR` versus `DCR`, and `CPR` versus `DCPR`,
- correct-`PRESERVE` and incorrect-`REFINE` rates,
- Prevented Regression, Safe Preservation, Missed Repair, and Unsuccessful Refinement Skipped,
- correctness difference and Net Token Saving by model-benchmark combination,
- all-resolved results and exact-Decision-only sensitivity results,
- descriptive Pearson and Spearman relationships with observed initial pass rate.

The correlation output is descriptive, not causal. An additional inferential regression model is not
silently selected after results are seen; adopting one would require a prospective decision and new
analysis version.

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

After the user accepts an RQ result, an allowlist-based package step may promote its validated
processed data, scripts, tables, report, and manifest to `paper_writing_package`. Only final accepted
results and redistributable/sanitized inputs may then be exported to `replication_package`. Pilot,
invalidated, superseded, private-path, model-weight, cache, and debugging artifacts are excluded.

The minimum public result-reproduction path will be:

```text
accepted raw records → build processed dataset → validate dataset
                     → run one RQ analysis → validate RQ output
```

Experiment reproduction remains a separate, more resource-intensive path.
