#!/usr/bin/env python3
"""Validate and summarize a complete provisional RQ1-RQ4 snapshot."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis_tools.common import (  # noqa: E402
    AnalysisError,
    read_json,
    read_jsonl,
    repository_relative,
    sha256_file,
    write_json,
    write_once,
)
from analysis_tools.processed_dataset import validate_processed_dataset  # noqa: E402
from analysis_tools.rq_metrics import validate_rq_output  # noqa: E402


def _dimension_counts(rows: list[dict[str, Any]], field: str, statuses: set[str]) -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(row[field]) for row in rows if row.get("analysis_status") in statuses
            ).items()
        )
    )


def review_provisional_analysis(*, dataset_dir: Path, analysis_dir: Path) -> dict[str, Any]:
    dataset_validation = validate_processed_dataset(dataset_dir)
    manifest = read_json(dataset_dir / "manifest.json")
    if manifest.get("result_status") != "provisional" or manifest.get("paper_facing") is not False:
        raise AnalysisError("review requires an explicitly non-paper-facing provisional dataset")

    rq_validations = {
        rq: validate_rq_output(analysis_dir / rq) for rq in ("rq1", "rq2", "rq3", "rq4")
    }
    if any(item.get("validation_result") != "passed" for item in rq_validations.values()):
        raise AnalysisError("one or more provisional RQ outputs failed validation")

    snapshot = read_json(dataset_dir / "evaluation_snapshot.json")
    evaluation_records = read_jsonl(dataset_dir / "evaluation_record_index.jsonl")
    outcomes = read_jsonl(dataset_dir / "outcomes.jsonl")
    missing_statuses = {
        "missing_evaluation_resolution",
        "initial_timeout",
        "final_timeout",
        "initial_evaluation_failure",
        "final_evaluation_failure",
    }
    evaluation_failures = [
        row for row in evaluation_records if row.get("status") == "evaluation_failure"
    ]
    report = {
        "schema_version": "provisional-analysis-review-v1",
        "result_status": "provisional",
        "paper_facing": False,
        "dataset_id": manifest["dataset_id"],
        "analysis_id": read_json(analysis_dir / "rq1" / "manifest.json")["analysis_id"],
        "dataset_path": repository_relative(dataset_dir),
        "analysis_path": repository_relative(analysis_dir),
        "dataset_manifest_sha256": sha256_file(dataset_dir / "manifest.json"),
        "dataset_validation": dataset_validation,
        "rq_validations": rq_validations,
        "evaluation_snapshot": {
            key: snapshot[key]
            for key in (
                "captured_at",
                "primary_count",
                "primary_timeout_count",
                "captured_confirmation_count",
                "pending_confirmation_count",
                "synthetic_resolution_count",
                "record_count",
            )
        },
        "analysis_status_counts": dict(
            sorted(Counter(str(row["analysis_status"]) for row in outcomes).items())
        ),
        "indeterminate_or_pending_rows_by_model": _dimension_counts(
            outcomes, "model_id", missing_statuses
        ),
        "indeterminate_or_pending_rows_by_benchmark": _dimension_counts(
            outcomes, "benchmark_id", missing_statuses
        ),
        "indeterminate_or_pending_rows_by_protocol": _dimension_counts(
            outcomes, "protocol", missing_statuses
        ),
        "evaluation_failures": evaluation_failures,
        "warnings": [
            (
                f"{snapshot['pending_confirmation_count']} primary timeout confirmations were "
                "not yet available at capture time; affected comparisons use only determinate "
                "paired cases."
            ),
            (
                "This snapshot is progress evidence only. Rebuild the final dataset from the "
                "terminal, independently validated evaluation run before paper-facing analysis."
            ),
            *(
                [
                    f"{len(evaluation_failures)} evaluator/infrastructure failure(s) remain "
                    "indeterminate and require separate resolution; they are not functional FAIL."
                ]
                if evaluation_failures
                else []
            ),
        ],
    }
    write_json(analysis_dir / "provisional_review.json", report)
    lines = [
        "# Provisional RQ1-RQ4 review",
        "",
        "This is a progress snapshot, not a paper-facing result.",
        "",
        f"- Dataset: `{report['dataset_id']}`",
        f"- Primary evaluations: {snapshot['primary_count']}",
        f"- Primary timeouts: {snapshot['primary_timeout_count']}",
        f"- Confirmations captured: {snapshot['captured_confirmation_count']}",
        f"- Confirmations pending: {snapshot['pending_confirmation_count']}",
        f"- Evaluation infrastructure failures: {len(evaluation_failures)}",
        "",
        "## Validation",
        "",
        "The complete model-task-protocol grid and all four RQ outputs passed "
        "integrity validation.",
        "",
        "## Warnings",
        "",
        *[f"- {warning}" for warning in report["warnings"]],
        "",
        "See `provisional_review.json` for status counts, missingness by dimension, and exact "
        "evaluation-failure records.",
        "",
    ]
    write_once(analysis_dir / "provisional_review.md", "\n".join(lines).encode("utf-8"))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--analysis-dir", type=Path, required=True)
    arguments = parser.parse_args()
    report = review_provisional_analysis(
        dataset_dir=arguments.dataset_dir.resolve(),
        analysis_dir=arguments.analysis_dir.resolve(),
    )
    print(arguments.analysis_dir.resolve() / "provisional_review.json")
    if report["evaluation_failures"]:
        print(
            f"warning: {len(report['evaluation_failures'])} evaluation failure(s)",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
