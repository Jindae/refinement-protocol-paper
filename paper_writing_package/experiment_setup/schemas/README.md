# Data schemas

`v1/` preserves experiment schema version `1.0.0`. `v2/` preserves version
`2.0.0`, which introduced evaluation-attempt stage, timeout provenance,
deferred confirmation lineage, and final resolution. `v3/` is the active
schema version `3.0.0`; it adds an explicit model-call finish reason so normal
EOS and output-limit termination are distinguishable without inference from
token counts. Typed source models live in
`src/self_refinement/schemas/models.py`. Compatibility-preserving changes
increment the minor version; breaking changes require a new major-version
directory and an explicit migration before a full experiment uses them.
Existing raw records are never rewritten in place.
No migration artifact is needed for either pre-experiment major-version
transition because the registry contained no pilot or primary experiment
records when `v2` or `v3` became active.

Pre-experiment operational audit schemas are versioned independently under `audit/`; their filenames include the complete audit schema version. Blinded semantic coding of invalid Decisions uses the independent `adjudication/decision-adjudication-v1.schema.json` contract, leaving the active experiment record schema and original invalid model calls unchanged.
