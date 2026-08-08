#!/usr/bin/env python3
"""Create compact, paper-ready table and figure data from validated RQ outputs."""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis_tools.common import (  # noqa: E402
    AnalysisError,
    read_json,
    read_jsonl,
    sha256_file,
    write_csv,
    write_json,
)
from analysis_tools.processed_dataset import validate_processed_dataset  # noqa: E402
from analysis_tools.rq_metrics import _contrast_with_pass_rates, validate_rq_output  # noqa: E402


def _cost(row: dict[str, Any]) -> int | None:
    value = row.get("end_to_end_protocol_tokens")
    return (
        int(value["total"])
        if isinstance(value, dict) and isinstance(value.get("total"), int)
        else None
    )


def _success(row: dict[str, Any]) -> int | None:
    value = row.get("end_to_end_success")
    return int(value) if value in {0, 1} else None


def _fields(rows: list[dict[str, Any]]) -> list[str]:
    return list(dict.fromkeys(key for row in rows for key in row))


def _write(path: Path, rows: list[dict[str, Any]]) -> None:
    write_csv(path, rows, _fields(rows))


def _aggregate_contrast(rows: list[dict[str, Any]], lhs: str, rhs: str, rq: str) -> dict[str, Any]:
    # rq_metrics groups by model and benchmark before calling its task-key contrast.  The
    # paper aggregate must retain model identity in that key to avoid collapsing six models.
    keyed = [
        {**row, "task_record_id": f"{row['model_id']}::{row['task_record_id']}"} for row in rows
    ]
    return _contrast_with_pass_rates(keyed, lhs, rhs, seed_parts=("paper", rq))


def build_assets(dataset: Path, analysis: Path, output: Path) -> Path:
    if output.exists():
        raise AnalysisError(f"paper asset output exists: {output}")
    validate_processed_dataset(dataset)
    for rq in ("rq1", "rq2", "rq3", "rq4"):
        validate_rq_output(analysis / rq)
    rows = read_jsonl(dataset / "outcomes.jsonl")
    output.mkdir(parents=True)

    by_protocol: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_protocol[str(row["protocol"])].append(row)
    overview: list[dict[str, Any]] = []
    for protocol, selected in sorted(by_protocol.items()):
        outcomes = [_success(row) for row in selected]
        determinate = [value for value in outcomes if value is not None]
        costs = [_cost(row) for row in selected]
        tokenized = [value for value in costs if value is not None]
        transitions = Counter(str(row.get("transition")) for row in selected)
        initial_fail = transitions["repair"] + transitions["unrepaired_failure"]
        initial_pass = transitions["regression"] + transitions["functional_preservation"]
        overview.append(
            {
                "protocol": protocol,
                "model_task_rows": len(selected),
                "determinate": len(determinate),
                "correct": sum(determinate),
                "pass_rate": sum(determinate) / len(determinate) if determinate else None,
                "timeout_or_indeterminate": len(selected) - len(determinate),
                "malformed_candidate": sum(
                    str(row.get("analysis_status")).startswith("malformed") for row in selected
                ),
                "complete_transitions": initial_fail + initial_pass,
                "repair": transitions["repair"],
                "repair_rate": transitions["repair"] / initial_fail if initial_fail else None,
                "regression": transitions["regression"],
                "regression_rate": (
                    transitions["regression"] / initial_pass if initial_pass else None
                ),
                "functional_preservation": transitions["functional_preservation"],
                "unrepaired_failure": transitions["unrepaired_failure"],
                "repair_minus_regression": transitions["repair"] - transitions["regression"],
                "end_to_end_tokens_total": sum(tokenized),
                "end_to_end_tokens_mean": mean(tokenized) if tokenized else None,
                "end_to_end_tokens_median": median(tokenized) if tokenized else None,
            }
        )
    _write(output / "table_rq1_performance_balance.csv", overview)

    rq1: list[dict[str, Any]] = []
    for lhs, rhs in (("direct", "r"), ("r", "cr"), ("cr", "cpr")):
        rq1.append(_aggregate_contrast(rows, lhs, rhs, "rq1"))
    _write(output / "table_rq1_stage_contrasts.csv", rq1)

    rq2: list[dict[str, Any]] = []
    for always, decision in (("r", "dr"), ("cr", "dcr"), ("cpr", "dcpr")):
        selected = by_protocol[decision]
        contrast = _aggregate_contrast(rows, always, decision, "rq2")
        consequences = Counter(str(row.get("decision_consequence")) for row in selected)
        savings = [
            row["net_token_saving"]["total"]
            for row in selected
            if isinstance(row.get("net_token_saving"), dict)
        ]
        rq2.append(
            {
                "always_refine_protocol": always,
                "decision_protocol": decision,
                "preserve": sum(row.get("decision") == "preserve" for row in selected),
                "refine": sum(row.get("decision") == "refine" for row in selected),
                "prevented_regression": consequences["prevented_regression"],
                "missed_repair": consequences["missed_repair"],
                "safe_preservation": consequences["safe_preservation"],
                "unsuccessful_refinement_skipped": consequences["unsuccessful_refinement_skipped"],
                "net_token_saving_total": sum(savings),
                "net_token_saving_mean": mean(savings) if savings else None,
                **contrast,
            }
        )
    _write(output / "table_rq2_decision_tradeoff.csv", rq2)

    rq3: list[dict[str, Any]] = []
    for multi, single in (
        ("cr", "sc_cr"),
        ("cpr", "sc_cpr"),
        ("dr", "sc_dr"),
        ("dcr", "sc_dcr"),
        ("dcpr", "sc_dcpr"),
    ):
        rq3.append(
            {
                "multi_call_protocol": multi,
                "single_call_protocol": single,
                **_aggregate_contrast(rows, multi, single, "rq3"),
            }
        )
    _write(output / "table_rq3_topology.csv", rq3)
    labels: list[dict[str, Any]] = []
    for protocol in ("sc_dr", "sc_dcr", "sc_dcpr"):
        selected = by_protocol[protocol]
        counts = Counter(str(row.get("label_change_consistency")) for row in selected)
        exact = sum(row.get("single_call_decision_parse_status") == "exact" for row in selected)
        invalid = sum(row.get("single_call_decision_parse_status") == "invalid" for row in selected)
        emitted = enforced = complete = 0
        for row in selected:
            a, b = _success(row), row.get("label_enforced_end_to_end_success")
            if a in {0, 1} and b in {0, 1}:
                emitted += int(a)
                enforced += int(b)
                complete += 1
        labels.append(
            {
                "protocol": protocol,
                "exact_label": exact,
                "invalid_label": invalid,
                "preserve_changed": counts["preserve_changed"],
                "refine_unchanged": counts["refine_unchanged"],
                "behavior_label_inconsistency": counts["preserve_changed"]
                + counts["refine_unchanged"],
                "behavior_label_inconsistency_rate": (
                    counts["preserve_changed"] + counts["refine_unchanged"]
                )
                / exact
                if exact
                else None,
                "label_sensitivity_complete": complete,
                "emitted_correct": emitted,
                "label_enforced_correct": enforced,
                "label_enforced_minus_emitted": (enforced - emitted) / complete
                if complete
                else None,
            }
        )
    _write(output / "table_rq3_label_consistency.csv", labels)

    protocols = [item["protocol"] for item in overview]
    index = {
        (str(row["model_id"]), str(row["task_record_id"]), str(row["protocol"])): row
        for row in rows
    }
    units = sorted({(str(row["model_id"]), str(row["task_record_id"])) for row in rows})
    common = [
        unit
        for unit in units
        if all(
            _success(index[(*unit, protocol)]) is not None
            and _cost(index[(*unit, protocol)]) is not None
            for protocol in protocols
        )
    ]
    points: dict[str, tuple[int, int]] = {}
    for protocol in protocols:
        points[protocol] = (
            sum(_cost(index[(*unit, protocol)]) or 0 for unit in common),
            sum(_success(index[(*unit, protocol)]) or 0 for unit in common),
        )
    rq4: list[dict[str, Any]] = []
    for protocol in protocols:
        cost, correct = points[protocol]
        dominators = [
            other
            for other, (oc, ok) in points.items()
            if other != protocol and oc <= cost and ok >= correct and (oc < cost or ok > correct)
        ]
        rq4.append(
            {
                "protocol": protocol,
                "common_complete_model_tasks": len(common),
                "correct": correct,
                "pass_rate": correct / len(common) if common else None,
                "end_to_end_tokens": cost,
                "tokens_per_model_task": cost / len(common) if common else None,
                "pareto_efficient": not dominators,
                "dominated_by": dominators,
            }
        )
    _write(output / "table_rq4_cost_pareto.csv", rq4)

    for source, target in (
        (overview, "figure_data_rq1_performance_balance.csv"),
        (rq1, "figure_data_rq1_stage_contrasts.csv"),
        (rq2, "figure_data_rq2_decision_tradeoff.csv"),
        (rq3, "figure_data_rq3_topology_effects.csv"),
        (overview, "figure_data_rq4_cost_correctness.csv"),
    ):
        _write(output / target, source)
    readme = (
        "# Paper-ready empirical assets\n\nAll CSVs are mechanically derived from the "
        "validated 12-protocol dataset. Table files are compact aggregate inputs; figure_data "
        "files are plotting inputs. Model-by-benchmark detail remains in the validated RQ "
        "directories. TIMEOUT and infrastructure outcomes are excluded from paired correctness "
        "denominators, while malformed model candidates count as end-to-end zero.\n"
    )
    (output / "README.md").write_text(readme, encoding="utf-8")
    files = {path.name: sha256_file(path) for path in sorted(output.iterdir()) if path.is_file()}
    manifest = {
        "schema_version": "paper-assets-manifest-v1",
        "validation_result": "passed",
        "dataset_id": read_json(dataset / "manifest.json")["dataset_id"],
        "analysis_id": read_json(analysis / "rq1/manifest.json")["analysis_id"],
        "common_complete_rq4_model_tasks": len(common),
        "source_dataset_manifest_sha256": sha256_file(dataset / "manifest.json"),
        "source_rq_manifest_sha256": {
            rq: sha256_file(analysis / rq / "manifest.json") for rq in ("rq1", "rq2", "rq3", "rq4")
        },
        "files": files,
    }
    write_json(output / "manifest.json", manifest)
    write_json(
        output / "validation.json",
        {
            "schema_version": "paper-assets-validation-v1",
            "validation_result": "passed",
            "file_count": len(files),
            "manifest_sha256": sha256_file(output / "manifest.json"),
        },
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(
        build_assets(
            args.dataset_dir.resolve(), args.analysis_dir.resolve(), args.output_dir.resolve()
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
