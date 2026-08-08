# Four-RQ Findings

Analysis `primary-final-four-rq-20260808-r3` uses validated dataset
`primary-final-v04-20260808-r5` and configuration `primary-analysis-2026-08-08-r4`.

## RQ1 — Refinement performance and repair–regression balance

R produced the highest pooled determinate pass rate (56.79%) and improved over Direct by 0.34
percentage points (95% bootstrap CI +0.16 to +0.52). That small gain was the net of 56 repairs and
22 regressions. CR and CPR repaired far more initially incorrect programs (222 and 209), but
regressed 610 and 725 initially correct programs; their lower final correctness is therefore driven
by regression growth, not an absence of repairs. Stage-comparison counts and initial-to-final
transition counts use different paired contrasts and must be reported separately but interpreted
together.

## RQ2 — Decision-conditioned refinement

The Decision gate preserved 91.94% of resolved candidates. It made R 0.13 points lower while saving
1.93 million protocol-implied tokens, but improved the regression-prone CR and CPR paths by 3.95 and
5.10 points while saving 11.59 and 18.84 million tokens. Exact-parser-only sensitivity preserved the
conclusions. Across 18 model-benchmark combinations, initial pass rate had little descriptive
association with DCR/DCPR correctness gains; the gate's value is better explained by downstream
regression risk than by initial pass rate alone.

## RQ3 — Single-call versus multi-call topology

SC-CR and SC-CPR exceeded their multi-call counterparts by 3.95 and 3.21 points, consistent with
less damage from inter-call artifact chains. Decision-bearing single- and multi-call protocols were
statistically indistinguishable overall. Exact single-call Decision labels sometimes disagreed with
emitted code change, so separate Decision calls retain an auditable exact-preservation advantage even
without a pooled correctness advantage.

## RQ4 — Cost-effectiveness

The final physical experiment consumed 91,816,683 tokens. On the 10,006 common-complete model-task
units, only Direct, DR, and R were on the pooled correctness-cost Pareto frontier. Direct is the
low-cost anchor, R the highest-correctness pooled option, and DR the intermediate point. Other
protocols were dominated in the pooled panel even when their matched topology comparison was
favorable.

Use model-by-benchmark CSVs inside each RQ directory for heterogeneity claims. Use
`results/paper_assets/primary-final-four-rq-20260808-r3/` for compact tables and plotting only.
