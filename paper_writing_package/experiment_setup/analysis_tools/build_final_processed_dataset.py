#!/usr/bin/env python3
"""Build the final 12-protocol composite processed dataset."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from analysis_tools.final_dataset import build_final_processed_dataset  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    for name in (
        "dataset-id",
        "base-inference-run-id",
        "base-evaluation-run-id",
        "remediation-run-id",
        "role-inference-run-id",
        "role-evaluation-run-id",
        "single-inference-run-id",
        "single-evaluation-run-id",
        "decision-adjudication-id",
        "base-attempt-id",
        "remediation-attempt-id",
        "role-attempt-id",
        "single-attempt-id",
    ):
        p.add_argument(f"--{name}", required=True)
    a = vars(p.parse_args())
    print(build_final_processed_dataset(**{k.replace("-", "_"): v for k, v in a.items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
