#!/usr/bin/env python3
"""Run the frozen RQ1-RQ4 analyses over one processed dataset."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis_tools.rq_metrics import RESULTS_ROOT, run_rq_analysis  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--analysis-id", required=True)
    parser.add_argument(
        "--allow-provisional",
        action="store_true",
        help="explicitly allow non-paper-facing metrics from a provisional snapshot",
    )
    arguments = parser.parse_args()
    outputs = []
    for rq in ("rq1", "rq2", "rq3", "rq4"):
        outputs.append(
            run_rq_analysis(
                dataset_dir=arguments.dataset_dir.resolve(),
                rq=rq,
                analysis_id=arguments.analysis_id,
                output_root=RESULTS_ROOT,
                allow_provisional=arguments.allow_provisional,
            )
        )
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
