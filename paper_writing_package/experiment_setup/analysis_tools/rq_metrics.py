"""Deterministic RQ1-RQ4 metric computation over the canonical processed dataset."""

from __future__ import annotations

import re
import tomllib
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

from analysis_tools.common import (
    PROJECT_ROOT,
    AnalysisError,
    deterministic_seed,
    exact_mcnemar_p_value,
    git_commit,
    mean,
    paired_bootstrap_ci,
    pearson,
    read_json,
    read_jsonl,
    repository_relative,
    sha256_file,
    spearman,
    write_csv,
    write_json,
    write_once,
)
from analysis_tools.processed_dataset import CONFIG_PATH, validate_processed_dataset

RESULTS_ROOT = PROJECT_ROOT / "results" / "summaries"
RQ_VALUES = {"rq1", "rq2", "rq3", "rq4"}
PROTOCOL_ORDER = ("direct", "r", "cr", "cpr", "dr", "dcr", "dcpr")


def _config() -> dict[str, Any]:
    with CONFIG_PATH.open("rb") as handle:
        return tomllib.load(handle)


def _group(
    rows: list[dict[str, Any]], fields: tuple[str, ...]
) -> dict[tuple[str, ...], list[dict[str, Any]]]:
    result: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        result[tuple(str(row[field]) for field in fields)].append(row)
    return dict(result)


def _functional(value: Any) -> int | None:
    if value == "pass":
        return 1
    if value == "fail":
        return 0
    return None


def _success(row: dict[str, Any]) -> int | None:
    value = row.get("end_to_end_success")
    if value in {0, 1}:
        return int(value)
    # Backwards-compatible unit fixtures and archived r1 datasets.
    return _functional(row.get("final_functional_outcome"))


def _final_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes = [_success(row) for row in rows]
    determinate = [value for value in outcomes if value is not None]
    status_counts = Counter(str(row.get("final_evaluation_status")) for row in rows)
    passes = sum(value == 1 for value in determinate)
    initial_final = [
        (
            _functional(row.get("initial_functional_outcome")),
            _functional(row.get("final_functional_outcome")),
        )
        for row in rows
    ]
    paired = [
        (initial, final)
        for initial, final in initial_final
        if initial is not None and final is not None
    ]
    return {
        "total_rows": len(rows),
        "determinate_final": len(determinate),
        "pass": passes,
        "fail": len(determinate) - passes,
        "pass_rate": passes / len(determinate) if determinate else None,
        "success_measure": "end_to_end_success",
        "malformed_candidate": sum(
            row.get("analysis_status") in {"malformed_initial", "malformed_final_candidate"}
            for row in rows
        ),
        "paired_initial_final": len(paired),
        "initial_pass_rate_on_paired": (
            sum(initial for initial, _ in paired) / len(paired) if paired else None
        ),
        "refinement_gain": (
            sum(final - initial for initial, final in paired) / len(paired) if paired else None
        ),
        "timeout": status_counts["timeout"],
        "evaluation_failure": status_counts["evaluation_failure"],
        "missing_or_other": len(rows)
        - len(determinate)
        - status_counts["timeout"]
        - status_counts["evaluation_failure"],
    }


def _paired_contrast(
    rows: list[dict[str, Any]],
    lhs: str,
    rhs: str,
    *,
    seed_parts: tuple[str, ...],
) -> dict[str, Any]:
    index = {(str(row["task_record_id"]), str(row["protocol"])): row for row in rows}
    task_ids = sorted({str(row["task_record_id"]) for row in rows})
    differences: list[int] = []
    excluded: Counter[str] = Counter()
    for task_id in task_ids:
        left = index.get((task_id, lhs))
        right = index.get((task_id, rhs))
        if left is None or right is None:
            excluded["missing_row"] += 1
            continue
        left_outcome = _success(left)
        right_outcome = _success(right)
        if left_outcome is None or right_outcome is None:
            excluded["indeterminate_functional_outcome"] += 1
            continue
        differences.append(right_outcome - left_outcome)
    improved = sum(value == 1 for value in differences)
    worsened = sum(value == -1 for value in differences)
    config = _config()
    low, high = paired_bootstrap_ci(
        differences,
        confidence_level=float(config["confidence_level"]),
        resamples=int(config["bootstrap_resamples"]),
        seed=deterministic_seed(int(config["bootstrap_seed"]), *seed_parts, lhs, rhs),
    )
    return {
        "lhs_protocol": lhs,
        "rhs_protocol": rhs,
        "total_tasks": len(task_ids),
        "paired_complete": len(differences),
        "excluded": sum(excluded.values()),
        "excluded_reasons": dict(sorted(excluded.items())),
        "paired_difference": sum(differences) / len(differences) if differences else None,
        "bootstrap_ci_low": low,
        "bootstrap_ci_high": high,
        "improved": improved,
        "worsened": worsened,
        "unchanged": len(differences) - improved - worsened,
        "mcnemar_exact_two_sided_p": exact_mcnemar_p_value(improved, worsened),
    }


def _contrast_with_pass_rates(
    rows: list[dict[str, Any]], lhs: str, rhs: str, *, seed_parts: tuple[str, ...]
) -> dict[str, Any]:
    result = _paired_contrast(rows, lhs, rhs, seed_parts=seed_parts)
    index = {(str(row["task_record_id"]), str(row["protocol"])): row for row in rows}
    paired: list[tuple[int, int]] = []
    for task_id in sorted({str(row["task_record_id"]) for row in rows}):
        left = index.get((task_id, lhs))
        right = index.get((task_id, rhs))
        if left is None or right is None:
            continue
        left_value = _success(left)
        right_value = _success(right)
        if left_value is not None and right_value is not None:
            paired.append((left_value, right_value))
    result["lhs_pass_rate"] = sum(left for left, _ in paired) / len(paired) if paired else None
    result["rhs_pass_rate"] = sum(right for _, right in paired) / len(paired) if paired else None
    return result


def compute_rq1(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    always = [row for row in rows if row["protocol"] in {"direct", "r", "cr", "cpr"}]
    summaries: list[dict[str, Any]] = []
    contrasts: list[dict[str, Any]] = []
    grouped = _group(always, ("model_id", "benchmark_id"))
    for (model_id, benchmark_id), group_rows in sorted(grouped.items()):
        by_protocol = _group(group_rows, ("protocol",))
        for protocol in ("direct", "r", "cr", "cpr"):
            summaries.append(
                {
                    "model_id": model_id,
                    "benchmark_id": benchmark_id,
                    "protocol": protocol,
                    **_final_summary(by_protocol.get((protocol,), [])),
                }
            )
        for value in _config()["rq1"]["contrasts"]:
            lhs, rhs = str(value).split(":", maxsplit=1)
            contrasts.append(
                {
                    "model_id": model_id,
                    "benchmark_id": benchmark_id,
                    **_contrast_with_pass_rates(
                        group_rows, lhs, rhs, seed_parts=("rq1", model_id, benchmark_id)
                    ),
                }
            )
    return {"protocol_summary": summaries, "paired_contrasts": contrasts}


def compute_rq2(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    transition_rows: list[dict[str, Any]] = []
    change_rows: list[dict[str, Any]] = []
    grouped = _group(rows, ("model_id", "benchmark_id", "protocol"))
    for (model_id, benchmark_id, protocol), group_rows in sorted(grouped.items()):
        counts = Counter(str(row["transition"]) for row in group_rows if row.get("transition"))
        initial_pass = counts["regression"] + counts["functional_preservation"]
        initial_fail = counts["repair"] + counts["unrepaired_failure"]
        complete = initial_pass + initial_fail
        transition_rows.append(
            {
                "model_id": model_id,
                "benchmark_id": benchmark_id,
                "protocol": protocol,
                "total_rows": len(group_rows),
                "complete_transitions": complete,
                "excluded": len(group_rows) - complete,
                "repair": counts["repair"],
                "repair_denominator_initial_fail": initial_fail,
                "repair_rate": counts["repair"] / initial_fail if initial_fail else None,
                "regression": counts["regression"],
                "regression_denominator_initial_pass": initial_pass,
                "regression_rate": counts["regression"] / initial_pass if initial_pass else None,
                "functional_preservation": counts["functional_preservation"],
                "functional_preservation_rate": (
                    counts["functional_preservation"] / initial_pass if initial_pass else None
                ),
                "unrepaired_failure": counts["unrepaired_failure"],
                "unrepaired_failure_rate": (
                    counts["unrepaired_failure"] / initial_fail if initial_fail else None
                ),
                "repair_minus_regression": counts["repair"] - counts["regression"],
                "net_gain_rate": (
                    (counts["repair"] - counts["regression"]) / complete if complete else None
                ),
            }
        )
        cross = Counter(
            (
                str(row["transition"]),
                str(row["candidate_changed_normalized"]),
                str(row["candidate_changed_exact"]),
            )
            for row in group_rows
            if row.get("transition") is not None
        )
        for (transition, normalized, exact), count in sorted(cross.items()):
            change_rows.append(
                {
                    "model_id": model_id,
                    "benchmark_id": benchmark_id,
                    "protocol": protocol,
                    "transition": transition,
                    "candidate_changed_normalized": normalized.lower(),
                    "candidate_changed_exact": exact.lower(),
                    "count": count,
                }
            )
    return {"transition_summary": transition_rows, "candidate_change_cross_tab": change_rows}


def _resolved_decision_rows(rows: list[dict[str, Any]], sensitivity: str) -> list[dict[str, Any]]:
    allowed = {"exact"} if sensitivity == "exact_only" else {"exact", "normalized", "adjudicated"}
    return [row for row in rows if row.get("decision_source") in allowed]


def _repair_regression_decomposition(
    always_rows: list[dict[str, Any]], decision_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    always_by_task = {str(row["task_record_id"]): row for row in always_rows}
    complete: list[tuple[int, int, int]] = []
    for decision in decision_rows:
        always = always_by_task.get(str(decision["task_record_id"]))
        if always is None:
            continue
        initial = _functional(decision.get("initial_functional_outcome"))
        always_final = _functional(always.get("final_functional_outcome"))
        decision_final = _functional(decision.get("final_functional_outcome"))
        if initial is not None and always_final is not None and decision_final is not None:
            complete.append((initial, always_final, decision_final))

    initially_incorrect = [values for values in complete if values[0] == 0]
    initially_correct = [values for values in complete if values[0] == 1]
    always_repairs = sum(always_final == 1 for _, always_final, _ in initially_incorrect)
    decision_repairs = sum(decision_final == 1 for _, _, decision_final in initially_incorrect)
    always_regressions = sum(always_final == 0 for _, always_final, _ in initially_correct)
    decision_regressions = sum(decision_final == 0 for _, _, decision_final in initially_correct)
    lost_repairs = always_repairs - decision_repairs
    prevented_regressions = always_regressions - decision_regressions
    if lost_repairs < 0 or prevented_regressions < 0:
        raise AnalysisError(
            "Decision-conditioned candidate selection violated always-refine outcome nesting"
        )
    incorrect_count = len(initially_incorrect)
    correct_count = len(initially_correct)
    return {
        "common_functional_transition_tasks": len(complete),
        "excluded_from_functional_transition_comparison": len(decision_rows) - len(complete),
        "initially_incorrect_common": incorrect_count,
        "always_refine_repairs": always_repairs,
        "decision_conditioned_repairs": decision_repairs,
        "always_refine_repair_rate": (
            always_repairs / incorrect_count if incorrect_count else None
        ),
        "decision_conditioned_repair_rate": (
            decision_repairs / incorrect_count if incorrect_count else None
        ),
        "repair_rate_difference": (
            (decision_repairs - always_repairs) / incorrect_count if incorrect_count else None
        ),
        "lost_repairs": lost_repairs,
        "initially_correct_common": correct_count,
        "always_refine_regressions": always_regressions,
        "decision_conditioned_regressions": decision_regressions,
        "always_refine_regression_rate": (
            always_regressions / correct_count if correct_count else None
        ),
        "decision_conditioned_regression_rate": (
            decision_regressions / correct_count if correct_count else None
        ),
        "regression_rate_difference": (
            (decision_regressions - always_regressions) / correct_count if correct_count else None
        ),
        "prevented_regressions": prevented_regressions,
        "always_refine_net_gain_count": always_repairs - always_regressions,
        "decision_conditioned_net_gain_count": decision_repairs - decision_regressions,
        "net_correct_difference_count": prevented_regressions - lost_repairs,
        "net_correct_difference_rate": (
            (prevented_regressions - lost_repairs) / len(complete) if complete else None
        ),
    }


def compute_rq3(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    contrast_pairs = [
        tuple(str(value).split(":", maxsplit=1)) for value in _config()["rq3"]["contrasts"]
    ]
    summary_rows: list[dict[str, Any]] = []
    decomposition_rows: list[dict[str, Any]] = []
    relationship_rows: list[dict[str, Any]] = []
    grouped = _group(rows, ("model_id", "benchmark_id"))
    for sensitivity in _config()["rq3"]["decision_sensitivity"]:
        for (model_id, benchmark_id), group_rows in sorted(grouped.items()):
            for always_protocol, decision_protocol in contrast_pairs:
                derived_all = [row for row in group_rows if row["protocol"] == decision_protocol]
                derived = _resolved_decision_rows(derived_all, str(sensitivity))
                task_ids = {str(row["task_record_id"]) for row in derived}
                always = [
                    row
                    for row in group_rows
                    if row["protocol"] == always_protocol and str(row["task_record_id"]) in task_ids
                ]
                paired_rows = [*always, *derived]
                contrast = _contrast_with_pass_rates(
                    paired_rows,
                    always_protocol,
                    decision_protocol,
                    seed_parts=("rq3", str(sensitivity), model_id, benchmark_id),
                )
                initial_values = [
                    _functional(row.get("initial_functional_outcome")) for row in derived_all
                ]
                determinate_initial = [value for value in initial_values if value is not None]
                correct_decisions = [
                    row for row in derived if row.get("initial_functional_outcome") == "pass"
                ]
                incorrect_decisions = [
                    row for row in derived if row.get("initial_functional_outcome") == "fail"
                ]
                consequences = Counter(
                    str(row["decision_consequence"])
                    for row in derived
                    if row.get("decision_consequence") is not None
                )
                savings = [
                    int(row["net_token_saving"]["total"])
                    for row in derived
                    if isinstance(row.get("net_token_saving"), dict)
                ]
                row = {
                    "sensitivity": sensitivity,
                    "model_id": model_id,
                    "benchmark_id": benchmark_id,
                    "always_refine_protocol": always_protocol,
                    "decision_protocol": decision_protocol,
                    "initial_determinate": len(determinate_initial),
                    "initial_pass_rate": (
                        sum(determinate_initial) / len(determinate_initial)
                        if determinate_initial
                        else None
                    ),
                    "resolved_decisions_in_sensitivity": len(derived),
                    "excluded_adjudicated": (
                        sum(row.get("decision_source") == "adjudicated" for row in derived_all)
                        if sensitivity == "exact_only"
                        else 0
                    ),
                    "excluded_normalized": (
                        sum(row.get("decision_source") == "normalized" for row in derived_all)
                        if sensitivity == "exact_only"
                        else 0
                    ),
                    "unresolved_or_missing_decisions": sum(
                        row.get("decision_source") in {"unresolved", "missing"}
                        for row in derived_all
                    ),
                    "correct_preserve": sum(
                        row.get("decision") == "preserve" for row in correct_decisions
                    ),
                    "correct_decision_denominator": len(correct_decisions),
                    "correct_preserve_rate": (
                        sum(row.get("decision") == "preserve" for row in correct_decisions)
                        / len(correct_decisions)
                        if correct_decisions
                        else None
                    ),
                    "incorrect_refine": sum(
                        row.get("decision") == "refine" for row in incorrect_decisions
                    ),
                    "incorrect_decision_denominator": len(incorrect_decisions),
                    "incorrect_refine_rate": (
                        sum(row.get("decision") == "refine" for row in incorrect_decisions)
                        / len(incorrect_decisions)
                        if incorrect_decisions
                        else None
                    ),
                    "prevented_regression": consequences["prevented_regression"],
                    "safe_preservation": consequences["safe_preservation"],
                    "missed_repair": consequences["missed_repair"],
                    "unsuccessful_refinement_skipped": consequences[
                        "unsuccessful_refinement_skipped"
                    ],
                    "net_token_saving_total": sum(savings) if savings else None,
                    "net_token_saving_mean": mean(savings),
                    **contrast,
                }
                summary_rows.append(row)
                decomposition_rows.append(
                    {
                        "sensitivity": sensitivity,
                        "model_id": model_id,
                        "benchmark_id": benchmark_id,
                        "always_refine_protocol": always_protocol,
                        "decision_protocol": decision_protocol,
                        **_repair_regression_decomposition(always, derived),
                    }
                )
                relationship_rows.append(
                    {
                        "sensitivity": sensitivity,
                        "model_id": model_id,
                        "benchmark_id": benchmark_id,
                        "always_refine_protocol": always_protocol,
                        "decision_protocol": decision_protocol,
                        "initial_pass_rate": row["initial_pass_rate"],
                        "correctness_difference": row["paired_difference"],
                        "net_token_saving_mean": row["net_token_saving_mean"],
                    }
                )
    correlations: list[dict[str, Any]] = []
    for sensitivity in _config()["rq3"]["decision_sensitivity"]:
        for always_protocol, decision_protocol in contrast_pairs:
            selected = [
                row
                for row in relationship_rows
                if row["sensitivity"] == sensitivity
                and row["always_refine_protocol"] == always_protocol
                and row["initial_pass_rate"] is not None
            ]
            for outcome_field in ("correctness_difference", "net_token_saving_mean"):
                complete = [row for row in selected if row[outcome_field] is not None]
                x = [float(row["initial_pass_rate"]) for row in complete]
                y = [float(row[outcome_field]) for row in complete]
                correlations.append(
                    {
                        "sensitivity": sensitivity,
                        "always_refine_protocol": always_protocol,
                        "decision_protocol": decision_protocol,
                        "outcome": outcome_field,
                        "combination_count": len(complete),
                        "pearson_descriptive": pearson(x, y),
                        "spearman_descriptive": spearman(x, y),
                    }
                )
    return {
        "decision_contrast_summary": summary_rows,
        "repair_regression_decomposition": decomposition_rows,
        "combination_relationships": relationship_rows,
        "descriptive_correlations": correlations,
    }


def _token_value(row: dict[str, Any], field: str) -> int | None:
    return _token_component(row, field, "total")


def _token_component(row: dict[str, Any], field: str, component: str) -> int | None:
    value = row.get(field)
    if not isinstance(value, dict) or not isinstance(value.get(component), int):
        return None
    return int(value[component])


def compute_rq4(
    rows: list[dict[str, Any]], stage_calls: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    stage_summary: list[dict[str, Any]] = []
    for (model_id, benchmark_id, stage), group_rows in sorted(
        _group(stage_calls, ("model_id", "benchmark_id", "stage")).items()
    ):
        tokenized = [row for row in group_rows if row.get("total_tokens") is not None]
        stage_summary.append(
            {
                "model_id": model_id,
                "benchmark_id": benchmark_id,
                "stage": stage,
                "call_attempts": len(group_rows),
                "tokenized_attempts": len(tokenized),
                "input_tokens_total": sum(int(row["input_tokens"]) for row in tokenized),
                "output_tokens_total": sum(int(row["output_tokens"]) for row in tokenized),
                "tokens_total": sum(int(row["total_tokens"]) for row in tokenized),
                "tokens_mean": mean([int(row["total_tokens"]) for row in tokenized]),
                "tokens_median": median([int(row["total_tokens"]) for row in tokenized])
                if tokenized
                else None,
                "status_counts": dict(
                    sorted(Counter(str(row["status"]) for row in group_rows).items())
                ),
            }
        )
    protocol_summary: list[dict[str, Any]] = []
    for (model_id, benchmark_id, protocol), group_rows in sorted(
        _group(rows, ("model_id", "benchmark_id", "protocol")).items()
    ):
        cost_components = {
            component: [
                value
                for row in group_rows
                if (value := _token_component(row, "end_to_end_protocol_tokens", component))
                is not None
            ]
            for component in ("input", "output", "total")
        }
        incremental_components = {
            component: [
                value
                for row in group_rows
                if (value := _token_component(row, "incremental_protocol_tokens", component))
                is not None
            ]
            for component in ("input", "output", "total")
        }
        decision_tokens = [
            value
            for row in group_rows
            if (value := _token_value(row, "decision_tokens")) is not None
        ]
        avoided_tokens = [
            value
            for row in group_rows
            if (value := _token_value(row, "avoided_refinement_tokens")) is not None
        ]
        net_savings = [
            value
            for row in group_rows
            if (value := _token_value(row, "net_token_saving")) is not None
        ]
        costs = cost_components["total"]
        final = [_success(row) for row in group_rows]
        determinate = [value for value in final if value is not None]
        protocol_summary.append(
            {
                "model_id": model_id,
                "benchmark_id": benchmark_id,
                "protocol": protocol,
                "total_rows": len(group_rows),
                "cost_determinate": len(costs),
                "end_to_end_tokens_total": sum(costs) if costs else None,
                "end_to_end_tokens_mean": mean(costs),
                "end_to_end_tokens_median": median(costs) if costs else None,
                "end_to_end_input_tokens_total": (
                    sum(cost_components["input"]) if cost_components["input"] else None
                ),
                "end_to_end_input_tokens_mean": mean(cost_components["input"]),
                "end_to_end_input_tokens_median": (
                    median(cost_components["input"]) if cost_components["input"] else None
                ),
                "end_to_end_output_tokens_total": (
                    sum(cost_components["output"]) if cost_components["output"] else None
                ),
                "end_to_end_output_tokens_mean": mean(cost_components["output"]),
                "end_to_end_output_tokens_median": (
                    median(cost_components["output"]) if cost_components["output"] else None
                ),
                "incremental_tokens_total": (
                    sum(incremental_components["total"])
                    if incremental_components["total"]
                    else None
                ),
                "incremental_input_tokens_total": (
                    sum(incremental_components["input"])
                    if incremental_components["input"]
                    else None
                ),
                "incremental_output_tokens_total": (
                    sum(incremental_components["output"])
                    if incremental_components["output"]
                    else None
                ),
                "decision_overhead_tokens_total": (
                    sum(decision_tokens) if decision_tokens else None
                ),
                "avoided_refinement_tokens_total": (
                    sum(avoided_tokens) if avoided_tokens else None
                ),
                "net_token_saving_total": sum(net_savings) if net_savings else None,
                "determinate_final": len(determinate),
                "correct": sum(determinate),
                "pass_rate": sum(determinate) / len(determinate) if determinate else None,
            }
        )
    experimental_summary: list[dict[str, Any]] = []
    for (model_id, benchmark_id), group_rows in sorted(
        _group(stage_calls, ("model_id", "benchmark_id")).items()
    ):
        tokenized = [row for row in group_rows if row.get("total_tokens") is not None]
        experimental_summary.append(
            {
                "model_id": model_id,
                "benchmark_id": benchmark_id,
                "model_call_attempts": len(group_rows),
                "tokenized_attempts": len(tokenized),
                "experimental_input_tokens": sum(int(row["input_tokens"]) for row in tokenized),
                "experimental_output_tokens": sum(int(row["output_tokens"]) for row in tokenized),
                "experimental_total_tokens": sum(int(row["total_tokens"]) for row in tokenized),
            }
        )
    pareto_rows: list[dict[str, Any]] = []
    grouped = _group(rows, ("model_id", "benchmark_id"))
    protocols = [str(value) for value in _config()["rq4"]["pareto_protocols"]]
    for (model_id, benchmark_id), group_rows in sorted(grouped.items()):
        index = {(str(row["task_record_id"]), str(row["protocol"])): row for row in group_rows}
        task_ids = sorted({str(row["task_record_id"]) for row in group_rows})
        common_tasks = [
            task_id
            for task_id in task_ids
            if all(
                (row := index.get((task_id, protocol))) is not None
                and _success(row) is not None
                and _token_value(row, "end_to_end_protocol_tokens") is not None
                for protocol in protocols
            )
        ]
        points: dict[str, tuple[int, int]] = {}
        for protocol in protocols:
            correct = sum(
                int(_success(index[(task_id, protocol)]) or 0) for task_id in common_tasks
            )
            cost = sum(
                int(_token_value(index[(task_id, protocol)], "end_to_end_protocol_tokens") or 0)
                for task_id in common_tasks
            )
            points[protocol] = (cost, correct)
        for protocol in protocols:
            cost, correct = points[protocol]
            dominators = [
                other
                for other, (other_cost, other_correct) in points.items()
                if other != protocol
                and other_cost <= cost
                and other_correct >= correct
                and (other_cost < cost or other_correct > correct)
            ]
            pareto_rows.append(
                {
                    "model_id": model_id,
                    "benchmark_id": benchmark_id,
                    "protocol": protocol,
                    "total_tasks": len(task_ids),
                    "common_complete_tasks": len(common_tasks),
                    "excluded_tasks": len(task_ids) - len(common_tasks),
                    "correct": correct,
                    "end_to_end_tokens": cost,
                    "pareto_efficient": not dominators,
                    "dominated_by": dominators,
                }
            )
    efficiency_rows: list[dict[str, Any]] = []
    contrasts = [
        *(tuple(str(value).split(":", maxsplit=1)) for value in _config()["rq1"]["contrasts"]),
        *(tuple(str(value).split(":", maxsplit=1)) for value in _config()["rq3"]["contrasts"]),
    ]
    for (model_id, benchmark_id), group_rows in sorted(grouped.items()):
        index = {(str(row["task_record_id"]), str(row["protocol"])): row for row in group_rows}
        task_ids = sorted({str(row["task_record_id"]) for row in group_rows})
        for lhs, rhs in contrasts:
            common = []
            for task_id in task_ids:
                left = index.get((task_id, lhs))
                right = index.get((task_id, rhs))
                if left is None or right is None:
                    continue
                if (
                    _success(left) is None
                    or _success(right) is None
                    or _token_value(left, "end_to_end_protocol_tokens") is None
                    or _token_value(right, "end_to_end_protocol_tokens") is None
                ):
                    continue
                common.append((left, right))
            delta_correct = sum(
                int(_success(right) or 0) - int(_success(left) or 0) for left, right in common
            )
            delta_tokens = sum(
                int(_token_value(right, "end_to_end_protocol_tokens") or 0)
                - int(_token_value(left, "end_to_end_protocol_tokens") or 0)
                for left, right in common
            )
            efficiency_rows.append(
                {
                    "model_id": model_id,
                    "benchmark_id": benchmark_id,
                    "lhs_protocol": lhs,
                    "rhs_protocol": rhs,
                    "common_complete_tasks": len(common),
                    "additional_correct": delta_correct,
                    "additional_tokens": delta_tokens,
                    "tokens_per_additional_correct": (
                        delta_tokens / delta_correct if delta_correct > 0 else None
                    ),
                    "undefined_reason": (
                        None if delta_correct > 0 else "no_positive_increment_in_correct_solutions"
                    ),
                }
            )
    return {
        "stage_token_summary": stage_summary,
        "protocol_cost_summary": protocol_summary,
        "experimental_token_consumption": experimental_summary,
        "pareto_common_complete_case": pareto_rows,
        "incremental_efficiency": efficiency_rows,
    }


def _csv_fields(rows: list[dict[str, Any]]) -> list[str]:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    return fields


def _report(
    rq: str,
    dataset_id: str,
    tables: dict[str, list[dict[str, Any]]],
    *,
    result_status: str,
    pending_confirmation_count: int,
) -> str:
    lines = [
        f"# {rq.upper()} generated review report",
        "",
        f"Processed dataset: `{dataset_id}`",
        "",
        f"Result status: `{result_status}`",
        "",
        "This report is generated mechanically from the frozen processed dataset. "
        "It does not convert timeout or evaluation-infrastructure outcomes into functional "
        "failures.",
        "",
        "## Output tables",
        "",
    ]
    if result_status == "provisional":
        lines.extend(
            [
                "This is a non-paper-facing progress snapshot. "
                f"{pending_confirmation_count} timeout confirmations were pending at capture; "
                "all metrics and denominators may change after terminal evaluation.",
                "",
            ]
        )
    for name, rows in tables.items():
        lines.append(f"- `{name}.csv`: {len(rows)} rows")
    lines.extend(
        [
            "",
            "## Review boundary",
            "",
            "Interpretation should begin only after the output validation passes and the displayed "
            "denominators, missingness, and source-run lineage are reviewed. Statistical "
            "associations in RQ3 are descriptive and are not causal estimates.",
            "",
        ]
    )
    return "\n".join(lines)


def _path_reference(path: Path) -> tuple[str, bool]:
    try:
        return repository_relative(path), True
    except AnalysisError:
        return str(path.resolve()), False


def run_rq_analysis(
    *,
    dataset_dir: Path,
    rq: str,
    analysis_id: str,
    output_root: Path = RESULTS_ROOT,
    allow_provisional: bool = False,
) -> Path:
    rq = rq.lower()
    if rq not in RQ_VALUES:
        raise AnalysisError(f"unknown research question: {rq}")
    if re.fullmatch(r"[a-z][a-z0-9-]{2,79}", analysis_id) is None:
        raise AnalysisError("analysis ID must be a lowercase, hyphenated identifier")
    validate_processed_dataset(dataset_dir)
    dataset_manifest = read_json(dataset_dir / "manifest.json")
    result_status = str(dataset_manifest.get("result_status", "final"))
    if result_status == "provisional" and not allow_provisional:
        raise AnalysisError(
            "provisional processed data require explicit allow_provisional acknowledgement"
        )
    outcomes = read_jsonl(dataset_dir / "outcomes.jsonl")
    stage_calls = read_jsonl(dataset_dir / "stage_calls.jsonl")
    if rq == "rq1":
        tables = compute_rq1(outcomes)
    elif rq == "rq2":
        tables = compute_rq2(outcomes)
    elif rq == "rq3":
        tables = compute_rq3(outcomes)
    else:
        tables = compute_rq4(outcomes, stage_calls)
    target = output_root / analysis_id / rq
    if target.exists():
        raise AnalysisError(f"analysis output already exists: {target}")
    target.mkdir(parents=True, exist_ok=False)
    for name, table_rows in tables.items():
        write_csv(target / f"{name}.csv", table_rows, _csv_fields(table_rows))
    metrics = {
        "schema_version": _config()["metrics_schema_version"],
        "rq": rq,
        "analysis_id": analysis_id,
        "dataset_id": dataset_manifest["dataset_id"],
        "result_status": result_status,
        "paper_facing": result_status == "final",
        "pending_confirmation_count": int(dataset_manifest.get("pending_confirmation_count", 0)),
        "tables": tables,
    }
    write_json(target / "metrics.json", metrics)
    write_once(
        target / "report.md",
        _report(
            rq,
            str(dataset_manifest["dataset_id"]),
            tables,
            result_status=result_status,
            pending_confirmation_count=int(dataset_manifest.get("pending_confirmation_count", 0)),
        ).encode("utf-8"),
    )
    files = sorted(path for path in target.iterdir() if path.is_file())
    processed_manifest_path, processed_manifest_portable = _path_reference(
        dataset_dir / "manifest.json"
    )
    manifest = {
        "schema_version": "rq-analysis-manifest-v1",
        "analysis_id": analysis_id,
        "rq": rq,
        "dataset_id": dataset_manifest["dataset_id"],
        "result_status": result_status,
        "paper_facing": result_status == "final",
        "pending_confirmation_count": int(dataset_manifest.get("pending_confirmation_count", 0)),
        "processed_manifest_path": processed_manifest_path,
        "processed_manifest_portable": processed_manifest_portable,
        "processed_manifest_sha256": sha256_file(dataset_dir / "manifest.json"),
        "analysis_configuration_path": repository_relative(CONFIG_PATH),
        "analysis_configuration_sha256": sha256_file(CONFIG_PATH),
        "producer_git_commit": git_commit(),
        "files": {path.name: sha256_file(path) for path in files},
    }
    write_json(target / "manifest.json", manifest)
    validate_rq_output(target, write_report=True)
    return target


def validate_rq_output(output_dir: Path, *, write_report: bool = False) -> dict[str, Any]:
    manifest = read_json(output_dir / "manifest.json")
    if manifest.get("rq") not in RQ_VALUES:
        raise AnalysisError("RQ output manifest has an invalid research question")
    if manifest.get("analysis_configuration_sha256") != sha256_file(CONFIG_PATH):
        raise AnalysisError("RQ output configuration hash mismatch")
    processed_manifest = PROJECT_ROOT / str(manifest["processed_manifest_path"])
    if sha256_file(processed_manifest) != manifest.get("processed_manifest_sha256"):
        raise AnalysisError("RQ output processed-dataset provenance mismatch")
    for name, expected_hash in manifest.get("files", {}).items():
        if sha256_file(output_dir / name) != expected_hash:
            raise AnalysisError(f"RQ output hash mismatch: {name}")
    metrics = read_json(output_dir / "metrics.json")
    if metrics.get("rq") != manifest.get("rq") or metrics.get("analysis_id") != manifest.get(
        "analysis_id"
    ):
        raise AnalysisError("RQ metrics identity differs from its manifest")
    processed = read_json(processed_manifest)
    result_status = str(processed.get("result_status", "final"))
    if manifest.get("result_status", "final") != result_status:
        raise AnalysisError("RQ output result status differs from processed data")
    if metrics.get("result_status", "final") != result_status:
        raise AnalysisError("RQ metrics result status differs from processed data")
    if manifest.get("paper_facing", result_status == "final") is not (result_status == "final"):
        raise AnalysisError("RQ output paper-facing flag is inconsistent")
    report = {
        "schema_version": "rq-analysis-validation-v1",
        "validation_result": "passed",
        "analysis_id": manifest["analysis_id"],
        "rq": manifest["rq"],
        "dataset_id": manifest["dataset_id"],
        "manifest_sha256": sha256_file(output_dir / "manifest.json"),
        "file_count": len(manifest["files"]),
        "result_status": result_status,
        "paper_facing": result_status == "final",
        "pending_confirmation_count": int(processed.get("pending_confirmation_count", 0)),
        "validation_scope": (
            "terminal_rq_output_integrity"
            if result_status == "final"
            else "provisional_rq_output_integrity"
        ),
    }
    if write_report:
        write_json(output_dir / "validation.json", report)
    return report
