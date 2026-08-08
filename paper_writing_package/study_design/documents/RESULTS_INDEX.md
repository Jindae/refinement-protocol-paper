# Results Index

## Accepted paper-facing results

The accepted final analysis is `primary-analysis-2026-08-08-r4`.

| Artifact | Identifier or path | Status |
|---|---|---|
| Canonical processed dataset | `data/processed/primary-final-v04-20260808-r5/` | Passed validation; 120,744 rows |
| RQ analysis | `results/summaries/primary-final-four-rq-20260808-r3/rq1/` … `rq4/` | All four passed validation |
| Paper table/chart data | `results/paper_assets/primary-final-four-rq-20260808-r3/` | Passed validation; 12 CSV inputs |
| Findings and methods | `documents/09_results_analysis.md` | Accepted analysis narrative |
| Compact findings | `results/summaries/primary-final-four-rq-20260808-r3/FINDINGS.md` | Paper-drafting summary |
| Paper-writing package | `paper_writing_package/` (`paper-writing-final-v04-20260808-r2`) | Passed validation; 95 files, 25,656,062 bytes |

The processed grid is six models × 1,677 tasks × 12 protocols. Its effective base-evaluation view
uses remediation `run_cfde994451c10e10b850905f` to supersede the sole failed evaluator resolution;
the original record remains immutable. The final source evaluations contain zero unresolved
evaluator failures. TIMEOUT remains indeterminate and model-attributable malformed output remains a
separate end-to-end zero as frozen before final analysis.

The paper assets contain one integrated RQ1 performance/repair-regression table, RQ1 stage contrasts,
RQ2 Decision tradeoffs, RQ3 topology and label consistency, RQ4 correctness-cost Pareto analysis,
and corresponding chart data. Model-by-benchmark tables in the RQ directories are the primary
heterogeneity evidence.

## Superseded or formative results

The v0.2.0 provisional snapshots under `data/interim/` and their RQ1–RQ4 summaries remain
non-paper-facing reference evidence. Their C/P/CR/CPR construct overlaps roles and is superseded by
the v0.3.0 role-separated execution. Paper-asset attempt
`results/paper_assets/primary-final-v04-20260808-r1/` is a superseded aggregate build whose task key
omitted model identity; it must not be cited. Its corrected five-RQ successor was `r2`, which is now
also superseded for paper organization by the accepted four-RQ assets above.

The validated five-RQ reporting set `results/summaries/primary-final-v04-20260808-r1/`, its dataset
`data/processed/primary-final-v04-20260808-r2/`, and corrected assets
`results/paper_assets/primary-final-v04-20260808-r2/` remain reproducible but are superseded by the
four-RQ accepted set above. Their numeric metrics are not invalid; their RQ organization and
paper-facing identifiers are obsolete after `DEC-20260808-49`.

Intermediate four-RQ dataset `primary-final-v04-20260808-r3` and analysis/assets
`primary-final-four-rq-20260808-r1` are excluded because the final composite manifest retained the
preceding human-readable analysis-version label. Corrected pre-commit validation builds dataset `r4`
and analysis/assets `r2` are also superseded so accepted manifests identify the exact committed
producer. `ISSUE-20260808-21` records both provenance corrections; only dataset `r5` and
analysis/assets `r3` are accepted.

## Exploratory mechanism supplement

| Artifact | Identifier or path | Status |
|---|---|---|
| Mechanism follow-up | `results/summaries/mechanism-followup-2026-08-08-r3/` | Passed validation; exploratory/post-hoc; 9 files and 11,044 rows |

This supplement uses accepted dataset `primary-final-v04-20260808-r5` plus validated role-separated
C/P artifacts. It formalizes task-set overlap, topology net decomposition, Decision mediation,
empirical reachability, and conservative artifact-chain surface labels. It does not replace the
accepted four RQs or enter paper-facing claims without an explicit promotion decision. Preceding
`mechanism-followup-2026-08-08-r1` is a validated implementation precursor whose artifact summary
lacked a pooled row; `r2` is the current exploratory result.
