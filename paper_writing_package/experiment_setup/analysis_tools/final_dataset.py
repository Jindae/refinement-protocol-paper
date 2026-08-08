"""Build the final study-v0.4 composite outcome dataset.

The paper-facing design reuses Direct/R/Decision from v0.2, CR/CPR from the
role-separated v0.3 run, and the five single-call protocols from v0.4.  This
module joins those immutable registries by logical model and upstream task,
while retaining every source record identifier needed to audit the join.
"""

from __future__ import annotations

import re
import tomllib
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from analysis_tools.common import (
    PROJECT_ROOT,
    AnalysisError,
    git_commit,
    normalize_source,
    read_json,
    sha256_file,
    write_json,
    write_jsonl,
)
from analysis_tools.processed_dataset import CONFIG_PATH, PROCESSED_ROOT, validate_processed_dataset

REGISTRY_ROOT = PROJECT_ROOT / "runs/registry"
LOG_ROOT = PROJECT_ROOT / "runs/logs"

PROTOCOLS = (
    "direct",
    "r",
    "cr",
    "cpr",
    "dr",
    "dcr",
    "dcpr",
    "sc_cr",
    "sc_cpr",
    "sc_dr",
    "sc_dcr",
    "sc_dcpr",
)
GENERATED = {"direct", "r", "cr", "cpr", "sc_cr", "sc_cpr", "sc_dr", "sc_dcr", "sc_dcpr"}
DERIVED = {"dr": "r", "dcr": "cr", "dcpr": "cpr"}
SINGLE_DECISION = {"sc_dr", "sc_dcr", "sc_dcpr"}
SELECTED_STAGES = {
    "base": {"direct_generation", "refinement_need_decision", "direct_revision"},
    "role": {
        "critique_generation",
        "critique_conditioned_revision",
        "revision_planning",
        "plan_conditioned_revision",
    },
    "single": {
        "single_call_cr",
        "single_call_cpr",
        "single_call_dr",
        "single_call_dcr",
        "single_call_dcpr",
    },
}
PROTOCOL_STAGES = {
    "direct": (),
    "r": ("direct_revision",),
    "cr": ("critique_generation", "critique_conditioned_revision"),
    "cpr": ("critique_generation", "revision_planning", "plan_conditioned_revision"),
    "sc_cr": ("single_call_cr",),
    "sc_cpr": ("single_call_cpr",),
    "sc_dr": ("single_call_dr",),
    "sc_dcr": ("single_call_dcr",),
    "sc_dcpr": ("single_call_dcpr",),
}


def _analysis_version() -> str:
    with CONFIG_PATH.open("rb") as handle:
        value = tomllib.load(handle).get("analysis_version")
    if not isinstance(value, str) or not value:
        raise AnalysisError("analysis configuration has no valid analysis_version")
    return value


def _records(run_id: str, record_type: str) -> list[dict[str, Any]]:
    root = REGISTRY_ROOT / run_id / "records" / record_type
    return [read_json(path) for path in sorted(root.glob("*.json"))]


def _unique(items: Iterable[dict[str, Any]], key: Any, label: str) -> dict[Any, dict[str, Any]]:
    result: dict[Any, dict[str, Any]] = {}
    for item in items:
        value = key(item)
        if value in result:
            raise AnalysisError(f"duplicate {label}: {value}")
        result[value] = item
    return result


def _validated_attempt(path: Path, *, identities: dict[str, str]) -> list[Path]:
    status_path, validation_path = path / "status.json", path / "validation.json"
    status, validation = read_json(status_path), read_json(validation_path)
    if status.get("state") != "completed" or status.get("validation_result") != "passed":
        raise AnalysisError(f"source attempt is not completed and validated: {path}")
    if validation.get("validation_result") != "passed":
        raise AnalysisError(f"source validation did not pass: {path}")
    for field, expected in identities.items():
        observed = validation.get(field, status.get(field))
        if observed != expected:
            raise AnalysisError(f"source identity mismatch for {field}: {path}")
    return [status_path, validation_path]


def _launch_models(run_id: str) -> tuple[dict[str, str], dict[str, str]]:
    payload = read_json(REGISTRY_ROOT / run_id / "launch.json")
    forward = payload.get("model_configuration_record_ids")
    if not isinstance(forward, dict) or len(forward) != 6:
        raise AnalysisError(f"invalid model mapping for {run_id}")
    return (
        {str(k): str(v) for k, v in forward.items()},
        {str(v): str(k) for k, v in forward.items()},
    )


def _task_maps(run_id: str) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    tasks = _records(run_id, "task_metadata")
    logical = _unique(tasks, lambda x: (x["benchmark_id"], x["upstream_task_id"]), "logical task")
    by_id = {item["record_id"]: key for key, item in logical.items()}
    return logical, by_id


def _effective_calls(
    run_id: str, record_to_model: dict[str, str], task_by_id: dict[str, tuple[str, str]]
) -> tuple[dict[tuple[str, tuple[str, str], str], dict[str, Any]], list[dict[str, Any]]]:
    calls = _records(run_id, "model_call")
    grouped: dict[tuple[str, tuple[str, str], str], list[dict[str, Any]]] = defaultdict(list)
    for call in calls:
        key = (
            record_to_model[call["model_configuration_record_id"]],
            task_by_id[call["task_record_id"]],
            call["stage"],
        )
        grouped[key].append(call)
    effective: dict[tuple[str, tuple[str, str], str], dict[str, Any]] = {}
    for key, values in grouped.items():
        completed = [x for x in values if x["status"] == "completed"]
        if len(completed) > 1:
            raise AnalysisError(f"multiple completed calls: {key}")
        effective[key] = (
            completed[0]
            if completed
            else max(values, key=lambda x: (x["attempt_number"], x["record_id"]))
        )
    return effective, calls


def _triplet(call: dict[str, Any] | None) -> dict[str, int] | None:
    if call is None or call.get("input_tokens") is None or call.get("output_tokens") is None:
        return None
    inp, out = int(call["input_tokens"]), int(call["output_tokens"])
    return {"input": inp, "output": out, "total": inp + out}


def _sum_cost(values: Iterable[dict[str, int] | None]) -> dict[str, int] | None:
    parts = list(values)
    if any(value is None for value in parts):
        return None
    return {
        key: sum(value[key] for value in parts if value is not None)
        for key in ("input", "output", "total")
    }


def _sub_cost(left: dict[str, int] | None, right: dict[str, int] | None) -> dict[str, int] | None:
    if left is None or right is None:
        return None
    return {key: left[key] - right[key] for key in ("input", "output", "total")}


def _outcome(resolution: dict[str, Any] | None) -> str | None:
    if resolution is None or resolution.get("status") != "completed":
        return None
    value = resolution.get("functional_outcome")
    return str(value) if value in {"pass", "fail"} else None


def _transition(initial: str | None, final: str | None) -> str | None:
    return {
        ("fail", "pass"): "repair",
        ("pass", "fail"): "regression",
        ("pass", "pass"): "functional_preservation",
        ("fail", "fail"): "unrepaired_failure",
    }.get((initial, final))


def _resolution_fields(value: dict[str, Any] | None, prefix: str) -> dict[str, Any]:
    return {
        f"{prefix}_evaluation_resolution_record_id": None if value is None else value["record_id"],
        f"{prefix}_evaluation_status": None if value is None else value["status"],
        f"{prefix}_functional_outcome": _outcome(value),
        f"{prefix}_evaluation_total_elapsed_seconds": None
        if value is None
        else value["total_elapsed_seconds"],
    }


def _candidate_index(
    run_id: str, record_to_model: dict[str, str], task_by_id: dict[str, tuple[str, str]]
) -> tuple[dict[tuple[str, tuple[str, str], str], dict[str, Any]], dict[str, dict[str, Any]]]:
    candidates = _records(run_id, "candidate")
    logical = _unique(
        candidates,
        lambda x: (
            record_to_model[x["model_configuration_record_id"]],
            task_by_id[x["task_record_id"]],
            x["protocol"],
        ),
        "candidate",
    )
    return logical, {x["record_id"]: x for x in candidates}


def _analysis_status(
    initial: dict[str, Any] | None,
    final: dict[str, Any] | None,
    initial_resolution: dict[str, Any] | None,
    final_resolution: dict[str, Any] | None,
    final_call: dict[str, Any] | None,
) -> str:
    if initial is None:
        return "malformed_initial"
    if final is None:
        if final_call is not None and final_call.get("status") in {
            "extraction_failure",
            "invalid_response",
        }:
            return "malformed_final_candidate"
        return "missing_final_candidate"
    if initial_resolution is None or final_resolution is None:
        return "missing_evaluation_resolution"
    if initial_resolution["status"] != "completed":
        return f"initial_{initial_resolution['status']}"
    if final_resolution["status"] != "completed":
        return f"final_{final_resolution['status']}"
    return "complete"


def build_final_processed_dataset(
    *,
    dataset_id: str,
    base_inference_run_id: str,
    base_evaluation_run_id: str,
    remediation_run_id: str,
    role_inference_run_id: str,
    role_evaluation_run_id: str,
    single_inference_run_id: str,
    single_evaluation_run_id: str,
    decision_adjudication_id: str,
    base_attempt_id: str,
    remediation_attempt_id: str,
    role_attempt_id: str,
    single_attempt_id: str,
    output_root: Path = PROCESSED_ROOT,
) -> Path:
    if re.fullmatch(r"[a-z][a-z0-9-]{2,79}", dataset_id) is None:
        raise AnalysisError("dataset ID must be a lowercase, hyphenated identifier")
    target = output_root / dataset_id
    if target.exists():
        raise AnalysisError(f"processed dataset already exists: {target}")

    source_paths: list[Path] = []
    source_paths += _validated_attempt(
        LOG_ROOT / "model-campaign" / base_attempt_id, identities={"run_id": base_inference_run_id}
    )
    source_paths += _validated_attempt(
        LOG_ROOT / "evaluation-remediation" / remediation_attempt_id,
        identities={"remediation_run_id": remediation_run_id},
    )
    source_paths += _validated_attempt(
        LOG_ROOT / "evaluation-campaign" / role_attempt_id,
        identities={"evaluation_run_id": role_evaluation_run_id},
    )
    source_paths += _validated_attempt(
        LOG_ROOT / "evaluation-campaign" / single_attempt_id,
        identities={"evaluation_run_id": single_evaluation_run_id},
    )
    adjudication_root = LOG_ROOT / "decision-adjudication" / decision_adjudication_id
    source_paths += _validated_attempt(
        adjudication_root, identities={"attempt_id": decision_adjudication_id}
    )

    runs = {
        "base": base_inference_run_id,
        "role": role_inference_run_id,
        "single": single_inference_run_id,
    }
    model_maps: dict[str, dict[str, str]] = {}
    reverse_models: dict[str, dict[str, str]] = {}
    task_maps: dict[str, dict[tuple[str, str], dict[str, Any]]] = {}
    task_reverse: dict[str, dict[str, tuple[str, str]]] = {}
    calls: dict[str, dict[tuple[str, tuple[str, str], str], dict[str, Any]]] = {}
    all_calls: dict[str, list[dict[str, Any]]] = {}
    candidates: dict[str, dict[tuple[str, tuple[str, str], str], dict[str, Any]]] = {}
    candidates_by_id: dict[str, dict[str, dict[str, Any]]] = {}
    for source, run_id in runs.items():
        model_maps[source], reverse_models[source] = _launch_models(run_id)
        task_maps[source], task_reverse[source] = _task_maps(run_id)
        if set(task_maps[source]) != set(task_maps.get("base", task_maps[source])):
            raise AnalysisError(f"task scope differs for {source}")
        calls[source], all_calls[source] = _effective_calls(
            run_id, reverse_models[source], task_reverse[source]
        )
        candidates[source], candidates_by_id[source] = _candidate_index(
            run_id, reverse_models[source], task_reverse[source]
        )
    if any(set(model_maps[source]) != set(model_maps["base"]) for source in runs):
        raise AnalysisError("model scope differs across composite sources")

    base_resolutions = {
        x["candidate"]["candidate_record_id"]: x
        for x in _records(base_evaluation_run_id, "evaluation_resolution")
    }
    replacements = _records(remediation_run_id, "evaluation_resolution")
    for replacement in replacements:
        superseded = replacement["provenance"].get("supersedes_record_id")
        candidate_id = replacement["candidate"]["candidate_record_id"]
        if (
            candidate_id not in base_resolutions
            or base_resolutions[candidate_id]["record_id"] != superseded
        ):
            raise AnalysisError("remediation does not supersede the effective base resolution")
        base_resolutions[candidate_id] = replacement
    resolution_sets = {
        "base": base_resolutions,
        "role": {
            x["candidate"]["candidate_record_id"]: x
            for x in _records(role_evaluation_run_id, "evaluation_resolution")
        },
        "single": {
            x["candidate"]["candidate_record_id"]: x
            for x in _records(single_evaluation_run_id, "evaluation_resolution")
        },
    }
    if Counter(x["status"] for x in base_resolutions.values()) != Counter(
        {"completed": 40075, "timeout": 131}
    ):
        raise AnalysisError("effective base evaluation counts differ from validated remediation")

    exact_decisions = {
        x["initial_candidate"]["candidate_record_id"]: x
        for x in _records(base_inference_run_id, "decision_artifact")
    }
    adjudication_input = read_json(adjudication_root / "input.json")
    adjudication_source = {
        x["call_id"]: x.get("resolution_source", "adjudicated")
        for x in adjudication_input["decisions"]
    }
    adjudications = {
        x["invalid_model_call_record_id"]: x
        for x in [read_json(p) for p in sorted((adjudication_root / "records").glob("*.json"))]
    }
    single_decisions = {
        x["model_call_record_id"]: x
        for x in _records(single_inference_run_id, "single_call_decision_artifact")
    }

    stage_rows: list[dict[str, Any]] = []
    selected_physical_calls: dict[tuple[str, tuple[str, str]], list[dict[str, Any]]] = defaultdict(
        list
    )
    for source, values in calls.items():
        for (model_id, task_key, stage), call in values.items():
            if stage not in SELECTED_STAGES[source]:
                continue
            selected_physical_calls[(model_id, task_key)].append(call)
            stage_rows.append(
                {
                    "schema_version": "processed-stage-calls-v3",
                    "source": source,
                    "inference_run_id": runs[source],
                    "model_id": model_id,
                    "model_configuration_record_id": call["model_configuration_record_id"],
                    "benchmark_id": task_key[0],
                    "task_record_id": task_maps["base"][task_key]["record_id"],
                    "upstream_task_id": task_key[1],
                    "stage": stage,
                    "model_call_record_id": call["record_id"],
                    "logical_call_id": call["logical_call_id"],
                    "attempt_number": call["attempt_number"],
                    "status": call["status"],
                    "reported_status": "malformed_candidate"
                    if call["status"] == "extraction_failure"
                    else call["status"],
                    "is_effective_attempt": True,
                    "input_tokens": call.get("input_tokens"),
                    "output_tokens": call.get("output_tokens"),
                    "total_tokens": None if _triplet(call) is None else _triplet(call)["total"],
                    "finish_reason": call.get("finish_reason"),
                    "elapsed_seconds": call["elapsed_seconds"],
                    "raw_response_sha256": None
                    if call.get("raw_response") is None
                    else call["raw_response"]["sha256"],
                    "supersedes_call_record_id": call.get("supersedes_call_record_id"),
                }
            )

    model_configs = {
        x["record_id"]: x for x in _records(base_inference_run_id, "model_configuration")
    }
    rows: list[dict[str, Any]] = []
    selections: list[dict[str, Any]] = []
    for model_id in sorted(model_maps["base"]):
        display_name = model_configs[model_maps["base"][model_id]]["display_name"]
        for task_key, task in sorted(task_maps["base"].items()):
            pair = (model_id, task_key)
            initial = candidates["base"].get((*pair, "direct"))
            initial_resolution = (
                None if initial is None else resolution_sets["base"].get(initial["record_id"])
            )
            initial_outcome = _outcome(initial_resolution)
            direct_call = calls["base"].get((*pair, "direct_generation"))
            decision_call = calls["base"].get((*pair, "refinement_need_decision"))
            decision_value = decision_record_id = None
            decision_source = "missing"
            if initial is not None and initial["record_id"] in exact_decisions:
                decision = exact_decisions[initial["record_id"]]
                decision_value, decision_record_id, decision_source = (
                    decision["decision"],
                    decision["record_id"],
                    "exact",
                )
            elif decision_call is not None and decision_call["record_id"] in adjudications:
                decision = adjudications[decision_call["record_id"]]
                if decision["status"] == "resolved":
                    decision_value, decision_record_id = (
                        decision["decision"],
                        decision["adjudication_record_id"],
                    )
                    decision_source = str(adjudication_source[decision_call["record_id"]])
                else:
                    decision_source = "unresolved"
            initial_cost, decision_cost = _triplet(direct_call), _triplet(decision_call)
            physical_cost = _sum_cost(_triplet(x) for x in selected_physical_calls.get(pair, []))

            generated_map = {
                "direct": ("base", initial),
                "r": ("base", candidates["base"].get((*pair, "r"))),
                "cr": ("role", candidates["role"].get((*pair, "cr"))),
                "cpr": ("role", candidates["role"].get((*pair, "cpr"))),
                **{
                    protocol: ("single", candidates["single"].get((*pair, protocol)))
                    for protocol in SINGLE_DECISION | {"sc_cr", "sc_cpr"}
                },
            }
            always_costs: dict[str, dict[str, int] | None] = {
                "direct": {"input": 0, "output": 0, "total": 0}
            }
            for protocol, stages in PROTOCOL_STAGES.items():
                if protocol == "direct":
                    continue
                source = (
                    "base" if protocol == "r" else "role" if protocol in {"cr", "cpr"} else "single"
                )
                always_costs[protocol] = _sum_cost(
                    _triplet(calls[source].get((*pair, stage))) for stage in stages
                )

            for protocol in PROTOCOLS:
                always_protocol = DERIVED.get(protocol)
                if protocol in GENERATED:
                    source, final = generated_map[protocol]
                    final_call = (
                        direct_call
                        if protocol == "direct"
                        else calls[source].get((*pair, PROTOCOL_STAGES[protocol][-1]))
                    )
                    final_selection = None
                else:
                    source = "base" if always_protocol == "r" else "role"
                    always = generated_map[always_protocol][1]
                    if decision_value == "preserve":
                        final, final_selection, final_call = initial, "exact_initial", decision_call
                    elif decision_value == "refine":
                        final, final_selection = always, "always_refine"
                        final_call = calls[source].get(
                            (*pair, PROTOCOL_STAGES[always_protocol][-1])
                        )
                    else:
                        final = final_selection = None
                        final_call = decision_call
                    selections.append(
                        {
                            "model_id": model_id,
                            "benchmark_id": task_key[0],
                            "upstream_task_id": task_key[1],
                            "protocol": protocol,
                            "decision": decision_value,
                            "decision_source": decision_source,
                            "final_selection": final_selection,
                            "initial_candidate_record_id": None
                            if initial is None
                            else initial["record_id"],
                            "always_refine_candidate_record_id": None
                            if always is None
                            else always["record_id"],
                            "final_candidate_record_id": None
                            if final is None
                            else final["record_id"],
                        }
                    )
                final_resolution = (
                    None
                    if final is None
                    else resolution_sets[
                        source
                        if protocol not in DERIVED or final_selection == "always_refine"
                        else "base"
                    ].get(final["record_id"])
                )
                final_outcome = _outcome(final_resolution)
                always_candidate = (
                    None if always_protocol is None else generated_map[always_protocol][1]
                )
                always_resolution = (
                    None
                    if always_candidate is None
                    else resolution_sets[source].get(always_candidate["record_id"])
                )
                always_outcome = _outcome(always_resolution)
                decision_consequence = None
                if (
                    always_protocol is not None
                    and decision_value is not None
                    and initial_outcome is not None
                    and always_outcome is not None
                ):
                    decision_consequence = (
                        "refinement_executed"
                        if decision_value == "refine"
                        else {
                            ("pass", "fail"): "prevented_regression",
                            ("pass", "pass"): "safe_preservation",
                            ("fail", "pass"): "missed_repair",
                            ("fail", "fail"): "unsuccessful_refinement_skipped",
                        }[(initial_outcome, always_outcome)]
                    )
                refinement_cost = always_costs[always_protocol or protocol]
                if protocol in GENERATED:
                    incremental = refinement_cost
                elif decision_value == "preserve":
                    incremental = decision_cost
                elif decision_value == "refine":
                    incremental = _sum_cost((decision_cost, refinement_cost))
                else:
                    incremental = None
                end_cost = _sum_cost((initial_cost, incremental))
                always_end = (
                    None if always_protocol is None else _sum_cost((initial_cost, refinement_cost))
                )
                net_saving = None if always_end is None else _sub_cost(always_end, end_cost)
                avoided = (
                    None
                    if always_protocol is None
                    else (
                        refinement_cost
                        if decision_value == "preserve"
                        else {"input": 0, "output": 0, "total": 0}
                        if decision_value == "refine"
                        else None
                    )
                )
                status = _analysis_status(
                    initial, final, initial_resolution, final_resolution, final_call
                )
                success = (
                    0
                    if status in {"malformed_initial", "malformed_final_candidate"}
                    else (None if final_outcome is None else int(final_outcome == "pass"))
                )
                row = {
                    "schema_version": "processed-outcomes-v3",
                    "dataset_id": dataset_id,
                    "study_version": "study-v0.4.0",
                    "base_inference_run_id": base_inference_run_id,
                    "role_inference_run_id": role_inference_run_id,
                    "single_inference_run_id": single_inference_run_id,
                    "base_evaluation_run_id": base_evaluation_run_id,
                    "role_evaluation_run_id": role_evaluation_run_id,
                    "single_evaluation_run_id": single_evaluation_run_id,
                    "decision_adjudication_id": decision_adjudication_id,
                    "model_id": model_id,
                    "model_display_name": display_name,
                    "model_configuration_record_id": model_maps["base"][model_id],
                    "benchmark_id": task_key[0],
                    "benchmark_revision": task["benchmark_revision"],
                    "task_record_id": task["record_id"],
                    "upstream_task_id": task_key[1],
                    "protocol": protocol,
                    "always_refine_protocol": always_protocol,
                    "candidate_source_run": source,
                    "initial_candidate_record_id": None
                    if initial is None
                    else initial["record_id"],
                    "initial_source_sha256": None if initial is None else initial["source_sha256"],
                    "final_candidate_record_id": None if final is None else final["record_id"],
                    "final_source_sha256": None if final is None else final["source_sha256"],
                    "always_refine_candidate_record_id": None
                    if always_protocol is None or generated_map[always_protocol][1] is None
                    else generated_map[always_protocol][1]["record_id"],
                    "derived_outcome_record_id": None,
                    "decision_record_id": decision_record_id,
                    "decision": decision_value,
                    "decision_source": decision_source if protocol in DERIVED else "not_applicable",
                    "final_selection": final_selection,
                    "analysis_status": status,
                    "initial_candidate_status": "available"
                    if initial is not None
                    else "malformed_candidate",
                    "final_candidate_status": "available"
                    if final is not None
                    else "malformed_candidate"
                    if status in {"malformed_initial", "malformed_final_candidate"}
                    else None,
                    **_resolution_fields(initial_resolution, "initial"),
                    **_resolution_fields(final_resolution, "final"),
                    "end_to_end_success": success,
                    "transition": _transition(initial_outcome, final_outcome),
                    "candidate_changed_exact": None
                    if initial is None or final is None
                    else initial["source_code"] != final["source_code"],
                    "candidate_changed_normalized": None
                    if initial is None or final is None
                    else normalize_source(initial["source_code"])
                    != normalize_source(final["source_code"]),
                    "decision_consequence": decision_consequence,
                    "initial_generation_tokens": initial_cost,
                    "decision_tokens": decision_cost if protocol in DERIVED else None,
                    "refinement_tokens": refinement_cost,
                    "incremental_protocol_tokens": incremental,
                    "end_to_end_protocol_tokens": end_cost,
                    "experimental_token_consumption": physical_cost,
                    "avoided_refinement_tokens": avoided,
                    "net_token_saving": net_saving,
                    "single_call_decision_record_id": None,
                    "single_call_decision_parse_status": None,
                    "single_call_decision": None,
                    "label_enforced_final_candidate_record_id": None,
                    "label_enforced_final_functional_outcome": None,
                    "label_enforced_end_to_end_success": None,
                    "label_enforced_transition": None,
                    "label_enforced_candidate_changed_normalized": None,
                    "label_change_consistency": None,
                }
                if protocol in SINGLE_DECISION:
                    artifact = (
                        None
                        if final_call is None
                        else single_decisions.get(final_call["record_id"])
                    )
                    if artifact is not None:
                        label = artifact.get("decision")
                        label_final = (
                            initial if label == "preserve" else final if label == "refine" else None
                        )
                        label_resolution = (
                            None
                            if label_final is None
                            else (
                                resolution_sets["base"].get(label_final["record_id"])
                                if label == "preserve"
                                else final_resolution
                            )
                        )
                        label_outcome = _outcome(label_resolution)
                        label_changed = (
                            None
                            if initial is None or label_final is None
                            else normalize_source(initial["source_code"])
                            != normalize_source(label_final["source_code"])
                        )
                        emitted_changed = row["candidate_changed_normalized"]
                        consistency = (
                            None
                            if label is None or emitted_changed is None
                            else f"{label}_{'changed' if emitted_changed else 'unchanged'}"
                        )
                        row.update(
                            {
                                "single_call_decision_record_id": artifact["record_id"],
                                "single_call_decision_parse_status": artifact["parse_status"],
                                "single_call_decision": label,
                                "label_enforced_final_candidate_record_id": None
                                if label_final is None
                                else label_final["record_id"],
                                "label_enforced_final_functional_outcome": label_outcome,
                                "label_enforced_end_to_end_success": None
                                if label_outcome is None
                                else int(label_outcome == "pass"),
                                "label_enforced_transition": _transition(
                                    initial_outcome, label_outcome
                                ),
                                "label_enforced_candidate_changed_normalized": label_changed,
                                "label_change_consistency": consistency,
                            }
                        )
                rows.append(row)

    rows.sort(
        key=lambda x: (
            x["model_id"],
            x["benchmark_id"],
            x["upstream_task_id"],
            PROTOCOLS.index(x["protocol"]),
        )
    )
    stage_rows.sort(
        key=lambda x: (x["model_id"], x["benchmark_id"], x["upstream_task_id"], x["stage"])
    )
    target.mkdir(parents=True)
    write_jsonl(target / "outcomes.jsonl", rows)
    write_jsonl(target / "stage_calls.jsonl", stage_rows)
    write_jsonl(target / "derived_selections.jsonl", selections)
    dictionary = {
        "schema_version": "processed-data-dictionary-v2",
        "unit_of_analysis": "one logical model-task-protocol",
        "protocols": list(PROTOCOLS),
        "primary_success_measure": (
            "end_to_end_success; malformed model candidates are zero, "
            "timeouts/infrastructure are null"
        ),
        "single_call_primary_semantics": (
            "emitted code is primary irrespective of emitted Decision label"
        ),
        "single_call_supplementary_semantics": (
            "label_enforced_* selects exact initial on PRESERVE and emitted code on REFINE"
        ),
        "token_boundary": (
            "v0.2 Direct/Decision/R + v0.3 role-separated C/CR/P/CPR + v0.4 five "
            "single-call stages; superseded v0.2 C/CR/P/CPR excluded"
        ),
    }
    write_json(target / "data_dictionary.json", dictionary)
    source_paths += [REGISTRY_ROOT / run_id / "launch.json" for run_id in runs.values()]
    files = {
        name: sha256_file(target / name)
        for name in (
            "outcomes.jsonl",
            "stage_calls.jsonl",
            "derived_selections.jsonl",
            "data_dictionary.json",
        )
    }
    manifest = {
        "schema_version": "processed-dataset-manifest-v2",
        "dataset_id": dataset_id,
        "result_status": "final",
        "paper_facing": True,
        "analysis_version": _analysis_version(),
        "analysis_configuration_path": str(CONFIG_PATH.relative_to(PROJECT_ROOT)),
        "analysis_configuration_sha256": sha256_file(CONFIG_PATH),
        "study_version": "study-v0.4.0",
        "source_runs": {
            "base_inference": base_inference_run_id,
            "base_evaluation": base_evaluation_run_id,
            "base_remediation": remediation_run_id,
            "role_inference": role_inference_run_id,
            "role_evaluation": role_evaluation_run_id,
            "single_inference": single_inference_run_id,
            "single_evaluation": single_evaluation_run_id,
        },
        "pending_confirmation_count": 0,
        "decision_adjudication_id": decision_adjudication_id,
        "source_files": [
            {"path": str(path.relative_to(PROJECT_ROOT)), "sha256": sha256_file(path)}
            for path in sorted(set(source_paths))
        ],
        "producer_git_commit": git_commit(),
        "row_counts": {
            "outcomes": len(rows),
            "stage_calls": len(stage_rows),
            "derived_selections": len(selections),
            "tasks": len(task_maps["base"]),
            "models": len(model_maps["base"]),
            "protocols": len(PROTOCOLS),
        },
        "status_counts": dict(sorted(Counter(row["analysis_status"] for row in rows).items())),
        "files": files,
    }
    write_json(target / "manifest.json", manifest)
    validate_processed_dataset(target, write_report=True)
    return target
