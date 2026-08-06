#!/usr/bin/env python3
"""Run exactly one frozen research-question analysis."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis_tools.rq_metrics import run_rq_analysis  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--rq", choices=("rq1", "rq2", "rq3", "rq4"), required=True)
    parser.add_argument("--analysis-id", required=True)
    arguments = parser.parse_args()
    output = run_rq_analysis(
        dataset_dir=arguments.dataset_dir.resolve(),
        rq=arguments.rq,
        analysis_id=arguments.analysis_id,
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
