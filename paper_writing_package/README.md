# Paper-writing package snapshot: paper-writing-pre-results-20260806-r2

This is an internal authoring snapshot for study `study-v0.2.0`, created before terminal primary
candidate-evaluation results exist. It is deliberately not a complete raw-data or replication
archive.

## Included evidence

- adopted study/method/analysis documents, prompts, configurations, environment locks, and selected
  implementation evidence;
- 70,386 model-call provenance and token rows in one CSV, each linked to the
  immutable working-registry call record and raw-response SHA-256;
- strictly parsed model artifacts consolidated by type into JSONL rather than hundreds of thousands
  of individual files;
- raw response bytes only for 220 model-format exceptions where the
  original response itself is necessary to inspect the failure;
- complete validated non-exact Decision direction records and the D-protocol candidate selections
  constructed from them;
- accepted reference-timing summaries and the frozen timeout configuration, but not every timing
  observation file;
- selected adopted decisions and relevant known issues, not the complete working chronology.

## Excluded boundary

Complete ordinary raw model responses, benchmark release bytes, the full repository archive, full
reference-observation trees, active candidate-evaluation raw data, processed outcome data, RQ
results, tables, and figures are excluded. Their immutable source identifiers and hashes remain
traceable from this package. Candidate evaluation attempt `evaluation-full-candidates-20260806-r1` was
`running` at export and is not a result in this snapshot.

The JSONL model artifacts are inference outputs after strict parsing; they are not the later
outcome-processed RQ dataset. Nothing in this pre-results snapshot supports a paper-facing empirical
result claim.
