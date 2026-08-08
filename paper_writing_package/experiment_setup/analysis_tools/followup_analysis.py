"""Exploratory mechanism analyses over the accepted study-v0.4.0 evidence."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
import tomllib
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis_tools.common import (  # noqa: E402
    AnalysisError,
    git_commit,
    sha256_file,
    write_csv,
    write_json,
    write_once,
)

CONFIG_PATH = PROJECT_ROOT / "analysis_tools" / "followup_analysis_config.toml"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "results" / "summaries"


def _config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _read_gzip_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                raise AnalysisError(f"blank JSONL line at {path}:{line_number}")
            value = json.loads(line)
            if not isinstance(value, dict):
                raise AnalysisError(f"non-object JSONL row at {path}:{line_number}")
            rows.append(value)
    return rows


def _success(row: dict[str, Any]) -> int | None:
    value = row.get("end_to_end_success")
    return int(value) if value in {0, 1} else None


def _index(rows: Iterable[dict[str, Any]]) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    result: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (
            str(row["model_id"]),
            str(row["benchmark_id"]),
            str(row["task_record_id"]),
            str(row["protocol"]),
        )
        if key in result:
            raise AnalysisError(f"duplicate processed outcome: {key}")
        result[key] = row
    return result


def _units(index: dict[tuple[str, str, str, str], dict[str, Any]]) -> list[tuple[str, str, str]]:
    return sorted({key[:3] for key in index})


def _row(
    index: dict[tuple[str, str, str, str], dict[str, Any]],
    unit: tuple[str, str, str],
    protocol: str,
) -> dict[str, Any] | None:
    return index.get((*unit, protocol))


Unit = tuple[str, str, str]
Scope = tuple[str, str | None, str | None, list[Unit]]


def _scopes(units: list[Unit]) -> list[Scope]:
    result: list[Scope] = [("pooled", None, None, units)]
    grouped: dict[tuple[str, str], list[tuple[str, str, str]]] = defaultdict(list)
    for unit in units:
        grouped[(unit[0], unit[1])].append(unit)
    result.extend(
        ("model_benchmark", model, benchmark, values)
        for (model, benchmark), values in sorted(grouped.items())
    )
    return result


def _transition_sets(
    index: dict[tuple[str, str, str, str], dict[str, Any]],
    units: list[tuple[str, str, str]],
    left: str,
    right: str,
) -> tuple[list[Unit], set[Unit], set[Unit], set[Unit], set[Unit]]:
    complete = []
    for unit in units:
        direct = _row(index, unit, "direct")
        lhs = _row(index, unit, left)
        rhs = _row(index, unit, right)
        if (
            direct is not None
            and lhs is not None
            and rhs is not None
            and _success(direct) in {0, 1}
            and _success(lhs) in {0, 1}
            and _success(rhs) in {0, 1}
        ):
            complete.append(unit)
    left_repairs = {
        unit
        for unit in complete
        if _success(_row(index, unit, "direct") or {}) == 0
        and _success(_row(index, unit, left) or {}) == 1
    }
    right_repairs = {
        unit
        for unit in complete
        if _success(_row(index, unit, "direct") or {}) == 0
        and _success(_row(index, unit, right) or {}) == 1
    }
    left_regressions = {
        unit
        for unit in complete
        if _success(_row(index, unit, "direct") or {}) == 1
        and _success(_row(index, unit, left) or {}) == 0
    }
    right_regressions = {
        unit
        for unit in complete
        if _success(_row(index, unit, "direct") or {}) == 1
        and _success(_row(index, unit, right) or {}) == 0
    }
    return complete, left_repairs, right_repairs, left_regressions, right_regressions


def _jaccard(left: set[Any], right: set[Any]) -> float | None:
    union = left | right
    return len(left & right) / len(union) if union else None


def task_set_overlap(
    index: dict[tuple[str, str, str, str], dict[str, Any]], config: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    overlap: list[dict[str, Any]] = []
    net: list[dict[str, Any]] = []
    all_units = _units(index)
    for scope, model, benchmark, units in _scopes(all_units):
        for contrast in config["topology_contrasts"]:
            left, right = str(contrast["multi"]), str(contrast["single"])
            complete, lr, rr, lg, rg = _transition_sets(index, units, left, right)
            initial_fail = sum(
                _success(_row(index, unit, "direct") or {}) == 0 for unit in complete
            )
            initial_correct = len(complete) - initial_fail
            overlap.append(
                {
                    "scope": scope,
                    "model_id": model,
                    "benchmark_id": benchmark,
                    "left_protocol": left,
                    "right_protocol": right,
                    "common_complete": len(complete),
                    "initially_incorrect": initial_fail,
                    "left_repairs": len(lr),
                    "right_repairs": len(rr),
                    "repair_both": len(lr & rr),
                    "repair_left_only": len(lr - rr),
                    "repair_right_only": len(rr - lr),
                    "repair_jaccard": _jaccard(lr, rr),
                    "initially_correct": initial_correct,
                    "left_regressions": len(lg),
                    "right_regressions": len(rg),
                    "regression_both": len(lg & rg),
                    "regression_left_only": len(lg - rg),
                    "regression_right_only": len(rg - lg),
                    "regression_jaccard": _jaccard(lg, rg),
                }
            )
            avoided_regressions = len(lg - rg)
            new_regressions = len(rg - lg)
            lost_repairs = len(lr - rr)
            new_repairs = len(rr - lr)
            net.append(
                {
                    "scope": scope,
                    "model_id": model,
                    "benchmark_id": benchmark,
                    "left_protocol": left,
                    "right_protocol": right,
                    "common_complete": len(complete),
                    "avoided_left_regressions": avoided_regressions,
                    "new_right_regressions": new_regressions,
                    "lost_left_repairs": lost_repairs,
                    "new_right_repairs": new_repairs,
                    "regression_control_contribution": avoided_regressions - new_regressions,
                    "repair_churn_contribution": new_repairs - lost_repairs,
                    "net_correct_difference_count": (
                        avoided_regressions - new_regressions + new_repairs - lost_repairs
                    ),
                }
            )
    return overlap, net


def decision_mediation(
    index: dict[tuple[str, str, str, str], dict[str, Any]], config: dict[str, Any]
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    all_units = _units(index)
    for scope, model, benchmark, units in _scopes(all_units):
        for family in config["decision_families"]:
            protocols = [
                str(family["always"]),
                str(family["separate_decision"]),
                str(family["single_decision"]),
            ]
            complete = [
                unit
                for unit in units
                if _success(_row(index, unit, "direct") or {}) in {0, 1}
                and all(
                    _success(_row(index, unit, protocol) or {}) in {0, 1} for protocol in protocols
                )
            ]
            for protocol in protocols:
                repairs = sum(
                    _success(_row(index, unit, "direct") or {}) == 0
                    and _success(_row(index, unit, protocol) or {}) == 1
                    for unit in complete
                )
                regressions = sum(
                    _success(_row(index, unit, "direct") or {}) == 1
                    and _success(_row(index, unit, protocol) or {}) == 0
                    for unit in complete
                )
                output.append(
                    {
                        "scope": scope,
                        "model_id": model,
                        "benchmark_id": benchmark,
                        "always_protocol": protocols[0],
                        "separate_decision_protocol": protocols[1],
                        "single_decision_protocol": protocols[2],
                        "reported_protocol": protocol,
                        "common_complete": len(complete),
                        "initially_incorrect": sum(
                            _success(_row(index, unit, "direct") or {}) == 0 for unit in complete
                        ),
                        "repair": repairs,
                        "initially_correct": sum(
                            _success(_row(index, unit, "direct") or {}) == 1 for unit in complete
                        ),
                        "regression": regressions,
                        "repair_minus_regression": repairs - regressions,
                    }
                )
    return output


def reachability(
    index: dict[tuple[str, str, str, str], dict[str, Any]], config: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    protocols = [str(value) for value in config["generated_protocols"]]
    summaries: list[dict[str, Any]] = []
    multiplicity: list[dict[str, Any]] = []
    contributions: list[dict[str, Any]] = []
    all_units = _units(index)
    for scope, model, benchmark, units in _scopes(all_units):
        complete = [
            unit
            for unit in units
            if _success(_row(index, unit, "direct") or {}) == 0
            and all(_success(_row(index, unit, protocol) or {}) in {0, 1} for protocol in protocols)
        ]
        repair_sets = {
            protocol: {
                unit for unit in complete if _success(_row(index, unit, protocol) or {}) == 1
            }
            for protocol in protocols
        }
        union = set().union(*repair_sets.values()) if repair_sets else set()
        summaries.append(
            {
                "scope": scope,
                "model_id": model,
                "benchmark_id": benchmark,
                "generated_protocol_count": len(protocols),
                "common_complete_initial_failures": len(complete),
                "repaired_by_any": len(union),
                "repaired_by_any_rate": len(union) / len(complete) if complete else None,
                "never_repaired": len(complete) - len(union),
            }
        )
        distribution = Counter(
            sum(unit in repair_sets[protocol] for protocol in protocols) for unit in complete
        )
        for count, units_at_count in sorted(distribution.items()):
            multiplicity.append(
                {
                    "scope": scope,
                    "model_id": model,
                    "benchmark_id": benchmark,
                    "repairing_protocol_count": count,
                    "model_task_units": units_at_count,
                }
            )
        for protocol in protocols:
            other_union = set().union(
                *(repair_sets[other] for other in protocols if other != protocol)
            )
            contributions.append(
                {
                    "scope": scope,
                    "model_id": model,
                    "benchmark_id": benchmark,
                    "protocol": protocol,
                    "repairs": len(repair_sets[protocol]),
                    "unique_repairs": len(repair_sets[protocol] - other_union),
                    "share_of_union": (len(repair_sets[protocol]) / len(union) if union else None),
                }
            )
    return summaries, multiplicity, contributions


def _surface_label(text: str, patterns: list[str], positive: str, other: str) -> str:
    lowered = " ".join(text.lower().split())
    return positive if any(pattern in lowered for pattern in patterns) else other


def artifact_chain(
    index: dict[tuple[str, str, str, str], dict[str, Any]], config: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    role_root = PROJECT_ROOT / str(config["role_registry"])
    role_launch = json.loads((role_root / "launch.json").read_text(encoding="utf-8"))
    if set(role_launch["model_configuration_record_ids"]) != set(
        source_index := json.loads(
            (role_root / "source_initial_candidates.json").read_text(encoding="utf-8")
        )
    ):
        raise AnalysisError("role model identities differ from the source-initial index")
    unit_by_initial = {
        candidate_id: (model_id, task_id)
        for model_id, task_map in source_index.items()
        for task_id, candidate_id in task_map.items()
    }
    critique_by_unit: dict[tuple[str, str], dict[str, Any]] = {}
    critique_unit_by_id: dict[str, tuple[str, str]] = {}
    for path in sorted((role_root / "records" / "critique_artifact").glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        unit = unit_by_initial.get(value["initial_candidate"]["candidate_record_id"])
        if unit is None:
            raise AnalysisError("critique references an unknown source initial")
        if unit in critique_by_unit:
            raise AnalysisError(f"duplicate critique for {unit}")
        critique_by_unit[unit] = value
        critique_unit_by_id[value["record_id"]] = unit
    plan_by_unit: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted((role_root / "records" / "revision_plan_artifact").glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        unit = critique_unit_by_id.get(value["critique_record_id"])
        if unit is None:
            raise AnalysisError("plan references an unknown critique")
        if unit in plan_by_unit:
            raise AnalysisError(f"duplicate plan for {unit}")
        plan_by_unit[unit] = value
    task_metadata = {
        json.loads(path.read_text(encoding="utf-8"))["record_id"]: json.loads(
            path.read_text(encoding="utf-8")
        )
        for path in sorted((role_root / "records" / "task_metadata").glob("*.json"))
    }
    critique_patterns = [
        str(value)
        for value in config["surface_classification"]["critique_explicit_no_problem_patterns"]
    ]
    plan_patterns = [
        str(value) for value in config["surface_classification"]["plan_explicit_no_change_patterns"]
    ]
    detail: list[dict[str, Any]] = []
    for unit, critique in sorted(critique_by_unit.items()):
        model_id, task_id = unit
        metadata = task_metadata[task_id]
        benchmark = str(metadata["benchmark_id"])
        direct = _row(index, (model_id, benchmark, task_id), "direct")
        cr = _row(index, (model_id, benchmark, task_id), "cr")
        cpr = _row(index, (model_id, benchmark, task_id), "cpr")
        plan = plan_by_unit.get(unit)
        detail.append(
            {
                "model_id": model_id,
                "benchmark_id": benchmark,
                "task_record_id": task_id,
                "upstream_task_id": metadata["upstream_task_id"],
                "initial_success": _success(direct or {}),
                "critique_surface_label": _surface_label(
                    str(critique["critique"]),
                    critique_patterns,
                    "explicit_no_problem",
                    "problem_or_other",
                ),
                "plan_surface_label": (
                    None
                    if plan is None
                    else _surface_label(
                        str(plan["plan"]),
                        plan_patterns,
                        "explicit_no_change",
                        "change_or_other",
                    )
                ),
                "cr_candidate_changed_normalized": (
                    None if cr is None else cr.get("candidate_changed_normalized")
                ),
                "cr_transition": None if cr is None else cr.get("transition"),
                "cpr_candidate_changed_normalized": (
                    None if cpr is None else cpr.get("candidate_changed_normalized")
                ),
                "cpr_transition": None if cpr is None else cpr.get("transition"),
                "critique_record_id": critique["record_id"],
                "plan_record_id": None if plan is None else plan["record_id"],
            }
        )
    summary: list[dict[str, Any]] = []
    detail_scopes: list[tuple[str, str | None, str | None, list[dict[str, Any]]]] = [
        ("pooled", None, None, detail),
        *(
            ("model_benchmark", model, benchmark, rows)
            for (model, benchmark), rows in sorted(
                _group_detail(detail, "model_id", "benchmark_id").items()
            )
        ),
    ]
    for scope, scope_model, scope_benchmark, scope_rows in detail_scopes:
        summary_counter: Counter[tuple[Any, ...]] = Counter(
            (
                row["initial_success"],
                row["critique_surface_label"],
                row["plan_surface_label"],
                row["cr_transition"],
                row["cpr_transition"],
            )
            for row in scope_rows
        )
        summary.extend(
            {
                "scope": scope,
                "model_id": scope_model,
                "benchmark_id": scope_benchmark,
                "initial_success": key[0],
                "critique_surface_label": key[1],
                "plan_surface_label": key[2],
                "cr_transition": key[3],
                "cpr_transition": key[4],
                "count": count,
            }
            for key, count in sorted(
                summary_counter.items(),
                key=lambda item: tuple(str(value) for value in item[0]),
            )
        )
    return detail, summary


def _group_detail(
    rows: list[dict[str, Any]], *fields: str
) -> dict[tuple[str, ...], list[dict[str, Any]]]:
    result: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        result[tuple(str(row[field]) for field in fields)].append(row)
    return dict(result)


TABLE_FIELDS: dict[str, list[str]] = {
    "task_set_overlap": [
        "scope",
        "model_id",
        "benchmark_id",
        "left_protocol",
        "right_protocol",
        "common_complete",
        "initially_incorrect",
        "left_repairs",
        "right_repairs",
        "repair_both",
        "repair_left_only",
        "repair_right_only",
        "repair_jaccard",
        "initially_correct",
        "left_regressions",
        "right_regressions",
        "regression_both",
        "regression_left_only",
        "regression_right_only",
        "regression_jaccard",
    ],
    "topology_net_decomposition": [
        "scope",
        "model_id",
        "benchmark_id",
        "left_protocol",
        "right_protocol",
        "common_complete",
        "avoided_left_regressions",
        "new_right_regressions",
        "lost_left_repairs",
        "new_right_repairs",
        "regression_control_contribution",
        "repair_churn_contribution",
        "net_correct_difference_count",
    ],
    "decision_mediation": [
        "scope",
        "model_id",
        "benchmark_id",
        "always_protocol",
        "separate_decision_protocol",
        "single_decision_protocol",
        "reported_protocol",
        "common_complete",
        "initially_incorrect",
        "repair",
        "initially_correct",
        "regression",
        "repair_minus_regression",
    ],
    "reachability_summary": [
        "scope",
        "model_id",
        "benchmark_id",
        "generated_protocol_count",
        "common_complete_initial_failures",
        "repaired_by_any",
        "repaired_by_any_rate",
        "never_repaired",
    ],
    "reachability_multiplicity": [
        "scope",
        "model_id",
        "benchmark_id",
        "repairing_protocol_count",
        "model_task_units",
    ],
    "reachability_protocol_contribution": [
        "scope",
        "model_id",
        "benchmark_id",
        "protocol",
        "repairs",
        "unique_repairs",
        "share_of_union",
    ],
    "artifact_chain_detail": [
        "model_id",
        "benchmark_id",
        "task_record_id",
        "upstream_task_id",
        "initial_success",
        "critique_surface_label",
        "plan_surface_label",
        "cr_candidate_changed_normalized",
        "cr_transition",
        "cpr_candidate_changed_normalized",
        "cpr_transition",
        "critique_record_id",
        "plan_record_id",
    ],
    "artifact_chain_summary": [
        "scope",
        "model_id",
        "benchmark_id",
        "initial_success",
        "critique_surface_label",
        "plan_surface_label",
        "cr_transition",
        "cpr_transition",
        "count",
    ],
}


def _report(tables: dict[str, list[dict[str, Any]]], config: dict[str, Any]) -> str:
    pooled_overlap = [row for row in tables["task_set_overlap"] if row["scope"] == "pooled"]
    pooled_reach = next(row for row in tables["reachability_summary"] if row["scope"] == "pooled")
    lines = [
        "# Exploratory mechanism follow-up",
        "",
        f"Analysis: `{config['analysis_version']}`",
        "",
        "This is a post-hoc exploratory supplement over the accepted study-v0.4.0 dataset. "
        "It does not replace or silently modify the four accepted RQ estimates.",
        "",
        "## Pooled task-set overlap",
        "",
    ]
    for row in pooled_overlap:
        lines.append(
            f"- {row['left_protocol']} vs {row['right_protocol']}: repairs "
            f"{row['left_repairs']} vs {row['right_repairs']} "
            f"(Jaccard {row['repair_jaccard']:.3f}); regressions "
            f"{row['left_regressions']} vs {row['right_regressions']} "
            f"(Jaccard {row['regression_jaccard']:.3f})."
        )
    lines.extend(
        [
            "",
            "## Empirical reachability",
            "",
            f"Among {pooled_reach['common_complete_initial_failures']} initially incorrect "
            f"common-complete model-task units, {pooled_reach['repaired_by_any']} "
            f"({pooled_reach['repaired_by_any_rate']:.2%}) were repaired by at least one "
            "generated refinement condition.",
            "",
            "## Artifact-chain interpretation boundary",
            "",
            "Critique and Plan categories are conservative surface labels based on exact frozen "
            "phrases. `problem_or_other` and `change_or_other` are not semantic correctness "
            "labels. "
            "A blinded annotation audit is required before treating them as diagnosis accuracy.",
        ]
    )
    return "\n".join(lines) + "\n"


def run(output_root: Path, analysis_id: str, config_path: Path = CONFIG_PATH) -> Path:
    config = _config(config_path)
    if analysis_id != config["analysis_version"]:
        raise AnalysisError("analysis ID must equal the frozen follow-up analysis version")
    outcomes_path = PROJECT_ROOT / str(config["source_outcomes"])
    role_status = PROJECT_ROOT / str(config["role_status"])
    if sha256_file(outcomes_path) != config["source_outcomes_sha256"]:
        raise AnalysisError("accepted outcome source hash differs from the frozen pin")
    if sha256_file(role_status) != config["role_status_sha256"]:
        raise AnalysisError("role-separated status hash differs from the frozen pin")
    status = json.loads(role_status.read_text(encoding="utf-8"))
    if status.get("state") != "completed" or status.get("validation_result") != "passed":
        raise AnalysisError("role-separated source is not completed and validated")
    rows = _read_gzip_jsonl(outcomes_path)
    index = _index(rows)
    overlap, net = task_set_overlap(index, config)
    reach_summary, reach_multi, reach_contrib = reachability(index, config)
    chain_detail, chain_summary = artifact_chain(index, config)
    tables = {
        "task_set_overlap": overlap,
        "topology_net_decomposition": net,
        "decision_mediation": decision_mediation(index, config),
        "reachability_summary": reach_summary,
        "reachability_multiplicity": reach_multi,
        "reachability_protocol_contribution": reach_contrib,
        "artifact_chain_detail": chain_detail,
        "artifact_chain_summary": chain_summary,
    }
    output = output_root / analysis_id
    output.mkdir(parents=True, exist_ok=False)
    for name, table in tables.items():
        write_csv(output / f"{name}.csv", table, TABLE_FIELDS[name])
    write_once(output / "report.md", _report(tables, config).encode("utf-8"))
    files = {
        path.name: sha256_file(path)
        for path in sorted(output.iterdir())
        if path.is_file() and path.name not in {"manifest.json", "validation.json"}
    }
    manifest = {
        "schema_version": "followup-analysis-manifest-v1",
        "analysis_id": analysis_id,
        "analysis_version": config["analysis_version"],
        "result_status": config["result_status"],
        "source_dataset_id": config["source_dataset_id"],
        "source_outcomes": config["source_outcomes"],
        "source_outcomes_sha256": config["source_outcomes_sha256"],
        "role_run_id": config["role_run_id"],
        "configuration_path": str(config_path.relative_to(PROJECT_ROOT)),
        "configuration_sha256": sha256_file(config_path),
        "producer_commit": git_commit(),
        "row_counts": {name: len(table) for name, table in tables.items()},
        "files": files,
    }
    write_json(output / "manifest.json", manifest)
    validation = validate(output)
    write_json(output / "validation.json", validation)
    return output


def validate(output: Path) -> dict[str, Any]:
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("result_status") != "exploratory_post_hoc":
        raise AnalysisError("follow-up output lost its exploratory status")
    for name, expected_count in manifest["row_counts"].items():
        path = output / f"{name}.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            count = sum(1 for _ in csv.DictReader(handle))
        if count != expected_count:
            raise AnalysisError(f"row-count mismatch for {name}")
    for name, expected_hash in manifest["files"].items():
        if sha256_file(output / name) != expected_hash:
            raise AnalysisError(f"file hash mismatch: {name}")
    return {
        "schema_version": "followup-analysis-validation-v1",
        "analysis_id": manifest["analysis_id"],
        "validation_result": "passed",
        "validated_files": len(manifest["files"]),
        "validated_rows": sum(manifest["row_counts"].values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--validate", action="store_true")
    parser.add_argument("--analysis-id", default="mechanism-followup-2026-08-08-r3")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--output-dir", type=Path)
    arguments = parser.parse_args()
    if arguments.run:
        print(run(arguments.output_root.resolve(), arguments.analysis_id))
    else:
        output = arguments.output_dir or (arguments.output_root / arguments.analysis_id)
        print(json.dumps(validate(output.resolve()), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
