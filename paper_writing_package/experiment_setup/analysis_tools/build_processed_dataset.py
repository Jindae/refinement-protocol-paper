#!/usr/bin/env python3
"""CLI for the immutable raw-to-processed transformation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis_tools.processed_dataset import (  # noqa: E402
    INTERIM_ROOT,
    PROCESSED_ROOT,
    build_processed_dataset,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inference-run-id", required=True)
    parser.add_argument("--evaluation-run-id", required=True)
    parser.add_argument("--decision-adjudication-id")
    parser.add_argument(
        "--provisional-evaluation-attempt-id",
        help=(
            "capture an active confirmation phase as a non-paper-facing provisional snapshot; "
            "the ordinary terminal-validation gate remains unchanged"
        ),
    )
    parser.add_argument("--dataset-id", required=True)
    arguments = parser.parse_args()
    path = build_processed_dataset(
        inference_run_id=arguments.inference_run_id,
        evaluation_run_id=arguments.evaluation_run_id,
        decision_adjudication_id=arguments.decision_adjudication_id,
        provisional_evaluation_attempt_id=arguments.provisional_evaluation_attempt_id,
        dataset_id=arguments.dataset_id,
        output_root=(
            INTERIM_ROOT
            if arguments.provisional_evaluation_attempt_id is not None
            else PROCESSED_ROOT
        ),
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
