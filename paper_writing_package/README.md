# Final paper-writing package

This allowlisted internal package contains the accepted `study-v0.4.0` design, complete compressed
canonical processed data, validated RQ1-RQ4 outputs, compact paper table/chart source CSVs, analysis
code, and the final findings narrative.

- Dataset: `primary-final-v04-20260808-r5` (120,744 outcome rows)
- RQ analysis: `primary-final-four-rq-20260808-r3`
- Paper assets: `primary-final-four-rq-20260808-r3`
- Exploratory supplement: `mechanism-followup-2026-08-08-r3`
- Source commit: `f2b90131f9cd55060d8ac8bfdf4adf8ebf93268e`

The three `.jsonl.gz` files are deterministic gzip streams and can be read directly by Python,
pandas, R, or command-line gzip tools. Raw experiment registries are not duplicated; exact run IDs,
source validation files, and SHA-256 values are recorded in `provenance/source_locations.json`.
Rendered figures are intentionally not frozen yet; `results/paper_assets/figure_data_*.csv` are the
accepted plotting inputs.
