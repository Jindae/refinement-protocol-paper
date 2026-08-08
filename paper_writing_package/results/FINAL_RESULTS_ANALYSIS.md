# Final Results Analysis

## 1. Analysis identity and evidence boundary

The accepted analysis is `primary-analysis-2026-08-08-r4` over processed dataset
`primary-final-v04-20260808-r5`. The dataset contains the complete logical grid of six models,
1,677 tasks, and 12 protocols (120,744 outcome rows). It combines:

- v0.2.0 Direct, Decision, and R artifacts and evaluations;
- the independently validated v0.2.0 remediation resolution that supersedes the sole evaluator
  failure without mutating the original record;
- v0.3.0 role-separated CR and CPR artifacts and evaluations; and
- v0.4.0 SC-CR, SC-CPR, SC-DR, SC-DCR, and SC-DCPR artifacts and evaluations.

The effective v0.2.0 evaluation view has 40,075 completed resolutions, 131 final timeouts, and zero
evaluator failures. Role-separated evaluation has 20,025 completed and 68 timeout resolutions;
single-call evaluation has 49,426 completed and 143 timeout resolutions. TIMEOUT and evaluator or
infrastructure outcomes remain indeterminate. Model-attributable malformed candidates remain
distinct from functional FAIL but count as zero in the predeclared end-to-end success measure.

## 2. Analysis methods

The primary analysis unit is one model-task-protocol outcome. Correctness comparisons are paired on
the exact initial candidate. For each model-benchmark combination, the analysis reports paired
differences, deterministic 10,000-resample paired bootstrap 95% confidence intervals, improved and
worsened counts, and supplementary exact two-sided McNemar tests. RQ1 jointly decomposes each
complete initial/final pair into repair, regression, functional preservation, or unrepaired failure;
no pass-rate finding is interpreted without this transition balance. RQ2
reports all resolved Decisions and an exact-parser-only sensitivity analysis, plus descriptive
Pearson and Spearman relationships across the 18 model-benchmark combinations. These correlations
are descriptive rather than causal.

The compact paper tables pool model-task rows only to provide an overall magnitude and plotting
input. The model-by-benchmark RQ tables are the primary heterogeneity evidence; pooled confidence
intervals must not be presented as a hierarchical model or as accounting for dependence between
different models on the same benchmark task. No post-hoc regression model or multiple-comparison
procedure was introduced after observing the results.

Candidate cost includes the shared initial generation plus protocol-implied incremental calls.
Paper-facing physical experimental consumption includes only the final design's 12 stages: v0.2.0
Direct/Decision/R, v0.3.0 role-separated C/CR/P/CPR, and the five v0.4.0 single calls. Superseded
v0.2.0 C/CR/P/CPR calls are excluded. Token comparisons are meaningful within models and are not
treated as cross-tokenizer compute equivalence.

## 3. RQ1 — Refinement performance and repair–regression balance

R produced the highest overall determinate pass rate (56.79%), compared with 56.44% for Direct.
On 10,032 pooled complete pairs, R improved 56 cases and worsened 22, a +0.34 percentage-point
difference (pooled bootstrap 95% CI +0.16 to +0.52; exact McNemar p=0.00015). The effect was small
and heterogeneous: 11 of 18 model-benchmark combinations were positive, three negative, and four
zero; only one combination had p<0.05 on its own.

Adding an external Critique before revision was harmful overall. In the paired stage contrast, CR
was 4.26 points below R (95% CI −4.81 to −3.71; 188 pairwise improvements versus 615 worsenings)
and was negative in 17 of 18 model-benchmark combinations. Relative to the shared initial candidate,
however, CR still repaired 222 failures; its lower final pass rate arose because 610 initially
correct programs regressed. Adding a separate Plan was harmful again: CPR was 1.24 points below CR
(95% CI −1.61 to −0.87; 112 pairwise improvements versus 236 worsenings), negative in 14 of 18
combinations. CPR repaired 209 initial failures but regressed 725 initially correct programs.

This joint view changes the interpretation. CR and CPR did not fail because they were unable to
repair code; each repaired roughly four times as many initial failures as R. Their net performance
was worse because the additional repair activity was accompanied by roughly 28 and 33 times as many
regressions as R, respectively. The paired stage counts and initial-to-final transition counts use
different contrasts and therefore should not be substituted for one another. Both support the same
mechanism-level result: pass-rate loss was dominated by damage to previously correct behavior.
These are whole-protocol effects and do not identify whether an upstream artifact was wrong or a
downstream revision failed to follow a correct artifact.

**Finding RQ1:** a direct second-pass revision achieved a small positive repair–regression balance
(56 repairs, 22 regressions), whereas externalized Critique and Planning increased raw repairs but
increased regressions much more sharply (CR: 222/610; CPR: 209/725). The principal performance
difference is therefore regression control, not repair count alone.

## 4. RQ2 — Decision-conditioned refinement

The shared Decision was conservative: 9,244 of 10,054 resolved model-task Decisions (91.94%) were
PRESERVE and 810 were REFINE. For R, gating prevented 18 regressions but missed 31 repairs, producing
a small, non-significant −0.13 point difference from always-R (95% CI −0.27 to 0.00; McNemar
p=0.085). It saved 1.93 million protocol-implied tokens, about 192 per model-task.

For the more destructive artifact chains, the same conservative gate was strongly beneficial. DCR
prevented 540 regressions while missing 149 repairs and exceeded CR by 3.95 points (95% CI +3.45 to
+4.45; p<10^-53), saving 11.59 million tokens (mean 1,153). DCPR prevented 646 regressions while
missing 136 repairs and exceeded CPR by 5.10 points (95% CI +4.55 to +5.65; p<10^-79), saving
18.84 million tokens (mean 1,874). DCR was positive in 17 of 18 model-benchmark combinations and
DCPR in all 18.

Removing 46 adjudicated and 156 deterministically normalized Decisions left the conclusions nearly
unchanged: exact-only differences were −0.13 points for DR, +4.01 for DCR, and +5.15 for DCPR.
Across the 18 combinations, initial pass rate had little descriptive association with DCR/DCPR
correctness gains (absolute Pearson r<0.15). Net savings for CR/CPR gating were moderately negatively
associated with initial pass rate (Pearson about −0.53), showing that model-specific token cost and
Decision behavior matter more than a simple "more initially correct means more savings" account.

**Finding RQ2:** Decision gating is most valuable when the downstream refinement path is
regression-prone. It nearly preserves R's correctness while saving cost, and it recovers much of the
large CR/CPR correctness loss while saving substantially more tokens.

## 5. RQ3 — Single-call versus multi-call topology

SC-CR exceeded multi-call CR by 3.95 points (95% CI +3.41 to +4.49; p<10^-44), and SC-CPR exceeded
multi-call CPR by 3.21 points (95% CI +2.58 to +3.83; p<10^-23). SC-CR was positive in 17 of 18
model-benchmark combinations; SC-CPR was positive in 16 and negative in two. This supports an
end-to-end topology claim, not a claim that hidden critique or planning was actually performed.

Once an explicit Decision boundary was present, the topology differences essentially disappeared:
SC-DR versus DR was +0.07 points, SC-DCR versus DCR +0.05, and SC-DCPR versus DCPR −0.09; every
pooled CI included zero and every McNemar p exceeded 0.49. The exact single-call Decision labels did
not perfectly describe code behavior. PRESERVE-with-changed-code plus REFINE-with-unchanged-code
occurred in 8.49% of SC-DR, 8.81% of SC-DCR, and 4.09% of SC-DCPR exact-label responses. Enforcing
those labels after the call changed net correct counts by only +2, +5, and −2 respectively on the
complete sensitivity subsets.

**Finding RQ3:** combining C/P with revision in one call avoided much of the multi-call artifact
chain's correctness loss. For Decision-bearing protocols, however, single- and multi-call outcomes
were statistically indistinguishable overall; the separate Decision boundary mainly offers exact,
auditable preservation semantics rather than a clear aggregate correctness advantage.

## 6. RQ4 — Cost-effectiveness

The final physical experiment consumed 91,816,683 tokens: 65,295,167 input and 26,521,516 output.
On the 10,006 model-task units complete for every protocol, only Direct, DR, and R were on the pooled
correctness-cost Pareto frontier. Direct used 460 tokens per model-task with 56.58% correct; DR used
974 tokens with 56.79%; R used 1,166 tokens with 56.92%. All other protocols were dominated in the
pooled common-complete view. In particular, SC-DR was slightly less correct and more expensive than
R, and DCR/DCPR added cost without exceeding DR or R.

R versus Direct added 34 correct outcomes at about 7.06 million additional tokens on the common
subset (about 208 thousand tokens per additional correct outcome). DR versus Direct added 21 correct
at about 5.14 million additional tokens (about 245 thousand per additional correct). These ratios
describe token accounting, not monetary cost or hardware-normalized compute.

**Finding RQ4:** Direct is the low-cost anchor, R is the highest-correctness pooled option, and DR is
the intermediate frontier point. The external Critique/Planning chains and all single-call variants
do not justify their additional token cost in the pooled panel, even where single-call topology
substantially improves over its matched multi-call counterpart.

## 7. Reproducibility and paper-use map

- Canonical processed data: `data/processed/primary-final-v04-20260808-r5/`
- Model-by-benchmark RQ outputs: `results/summaries/primary-final-four-rq-20260808-r3/rq1/`
  through `rq4/`
- Compact table and chart source data: `results/paper_assets/primary-final-four-rq-20260808-r3/`
- Builders: `analysis_tools/build_final_processed_dataset.py`,
  `analysis_tools/run_all_rq_analysis.py`, and `analysis_tools/build_paper_assets.py`
- Frozen analysis configuration: `analysis_tools/analysis_config.toml`

Every directory above contains a manifest and validation result. Paper claims should cite the
model-by-benchmark output when discussing heterogeneity and use the compact paper assets only for
aggregate tables and plotting.
