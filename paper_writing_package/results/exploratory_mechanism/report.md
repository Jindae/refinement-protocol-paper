# Exploratory mechanism follow-up

Analysis: `mechanism-followup-2026-08-08-r3`

This is a post-hoc exploratory supplement over the accepted study-v0.4.0 dataset. It does not replace or silently modify the four accepted RQ estimates.

## Pooled task-set overlap

- cr vs sc_cr: repairs 222 vs 86 (Jaccard 0.194); regressions 615 vs 83 (Jaccard 0.067).
- cpr vs sc_cpr: repairs 209 vs 94 (Jaccard 0.232); regressions 726 vs 289 (Jaccard 0.104).
- dr vs sc_dr: repairs 25 vs 64 (Jaccard 0.328); regressions 4 vs 36 (Jaccard 0.081).
- dcr vs sc_dcr: repairs 73 vs 68 (Jaccard 0.226); regressions 70 vs 60 (Jaccard 0.102).
- dcpr vs sc_dcpr: repairs 73 vs 96 (Jaccard 0.271); regressions 79 vs 111 (Jaccard 0.152).

## Empirical reachability

Among 4353 initially incorrect common-complete model-task units, 337 (7.74%) were repaired by at least one generated refinement condition.

## Artifact-chain interpretation boundary

Critique and Plan categories are conservative surface labels based on exact frozen phrases. `problem_or_other` and `change_or_other` are not semantic correctness labels. A blinded annotation audit is required before treating them as diagnosis accuracy.
