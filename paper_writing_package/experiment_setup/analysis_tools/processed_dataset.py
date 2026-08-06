"""Build and validate the canonical model-task-protocol analysis dataset."""

from __future__ import annotations

import re
import tomllib
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from analysis_tools.common import (
    PROJECT_ROOT,
    AnalysisError,
    git_commit,
    normalize_source,
    read_json,
    read_jsonl,
    repository_relative,
    sha256_file,
    write_json,
    write_jsonl,
)
from self_refinement.adjudication.decisions import (
    AdjudicationStatus,
    DecisionAdjudicationRecord,
)
from self_refinement.evaluation.timeouts import (
    DEFAULT_TIMEOUT_POLICY_PATH,
    load_timeout_policy,
    resolve_evaluation_attempts,
)
from self_refinement.identifiers import evaluation_resolution_id
from self_refinement.schemas.models import (
    CandidateRecord,
    CritiqueArtifact,
    DecisionArtifact,
    DecisionValue,
    DerivedProtocolOutcome,
    EvaluationAttemptStage,
    EvaluationRecord,
    EvaluationResolutionRecord,
    EvaluationStatus,
    ModelCallRecord,
    ModelCallStatus,
    ModelConfiguration,
    Protocol,
    Provenance,
    RevisionPlanArtifact,
    RunManifest,
    RunStatus,
    Stage,
    TaskMetadata,
)
from self_refinement.storage.registry import LocalRunRegistry

REGISTRY_ROOT = PROJECT_ROOT / "runs" / "registry"
LOG_ROOT = PROJECT_ROOT / "runs" / "logs"
PROCESSED_ROOT = PROJECT_ROOT / "data" / "processed"
INTERIM_ROOT = PROJECT_ROOT / "data" / "interim"
CONFIG_PATH = Path(__file__).with_name("analysis_config.toml")
PROTOCOL_ORDER = (
    Protocol.DIRECT,
    Protocol.R,
    Protocol.CR,
    Protocol.CPR,
    Protocol.DR,
    Protocol.DCR,
    Protocol.DCPR,
)
GENERATED_PROTOCOLS = (Protocol.DIRECT, Protocol.R, Protocol.CR, Protocol.CPR)
DERIVED_TO_ALWAYS = {
    Protocol.DR: Protocol.R,
    Protocol.DCR: Protocol.CR,
    Protocol.DCPR: Protocol.CPR,
}
PROTOCOL_STAGES = {
    Protocol.DIRECT: (),
    Protocol.R: (Stage.DIRECT_REVISION,),
    Protocol.CR: (Stage.CRITIQUE_GENERATION, Stage.CRITIQUE_CONDITIONED_REVISION),
    Protocol.CPR: (
        Stage.CRITIQUE_GENERATION,
        Stage.REVISION_PLANNING,
        Stage.PLAN_CONDITIONED_REVISION,
    ),
}


@dataclass(frozen=True)
class ValidatedRun:
    registry: LocalRunRegistry
    manifest: RunManifest
    validation_path: Path
    manifest_path: Path


@dataclass(frozen=True)
class ProvisionalEvaluationSnapshot:
    registry: LocalRunRegistry
    manifest: RunManifest
    manifest_path: Path
    resolutions: tuple[EvaluationResolutionRecord, ...]
    record_index: tuple[dict[str, Any], ...]
    metadata: dict[str, Any]


def _config() -> dict[str, Any]:
    with CONFIG_PATH.open("rb") as handle:
        return tomllib.load(handle)


def _latest_manifest(registry: LocalRunRegistry, run_id: str) -> tuple[RunManifest, Path]:
    manifest = registry.latest_run_manifest(run_id)
    if manifest is None:
        raise AnalysisError(f"run has no manifest: {run_id}")
    path = registry.records_root / RunManifest.RECORD_TYPE / f"{manifest.record_id}.json"
    if manifest.status not in {RunStatus.COMPLETED, RunStatus.ACCEPTED}:
        raise AnalysisError(f"run is not completed: {run_id} ({manifest.status.value})")
    return manifest, path


def _validated_attempt(job_kind: str, id_field: str, run_id: str, manifest_record_id: str) -> Path:
    matches: list[Path] = []
    for path in (LOG_ROOT / job_kind).glob("*/validation.json"):
        payload = read_json(path)
        if (
            payload.get("validation_result") == "passed"
            and payload.get(id_field) == run_id
            and payload.get("manifest_record_id") == manifest_record_id
        ):
            status_path = path.parent / "status.json"
            status = read_json(status_path)
            if status.get("state") == "completed" and status.get("validation_result") == "passed":
                matches.append(path)
    if not matches:
        raise AnalysisError(f"no validated {job_kind} attempt found for {run_id}")
    return sorted(matches, key=lambda path: path.as_posix())[-1]


def _validated_inference_run(inference_run_id: str) -> ValidatedRun:
    inference_registry = LocalRunRegistry(REGISTRY_ROOT / inference_run_id)
    inference_manifest, inference_manifest_path = _latest_manifest(
        inference_registry, inference_run_id
    )
    inference_validation = _validated_attempt(
        "model-campaign", "run_id", inference_run_id, inference_manifest.record_id
    )
    return ValidatedRun(
        inference_registry,
        inference_manifest,
        inference_validation,
        inference_manifest_path,
    )


def validate_source_runs(
    inference_run_id: str, evaluation_run_id: str
) -> tuple[ValidatedRun, ValidatedRun]:
    inference = _validated_inference_run(inference_run_id)
    evaluation_registry = LocalRunRegistry(REGISTRY_ROOT / evaluation_run_id)
    evaluation_manifest, evaluation_manifest_path = _latest_manifest(
        evaluation_registry, evaluation_run_id
    )
    if evaluation_manifest.parent_run_id != inference_run_id:
        raise AnalysisError("evaluation run is not a child of the supplied inference run")
    if evaluation_manifest.provenance.study_version != inference.manifest.provenance.study_version:
        raise AnalysisError("inference and evaluation study versions differ")
    if evaluation_manifest.models != inference.manifest.models:
        raise AnalysisError("inference and evaluation model scopes differ")
    if evaluation_manifest.benchmarks != inference.manifest.benchmarks:
        raise AnalysisError("inference and evaluation benchmark scopes differ")
    evaluation_validation = _validated_attempt(
        "evaluation-campaign",
        "evaluation_run_id",
        evaluation_run_id,
        evaluation_manifest.record_id,
    )
    return (
        inference,
        ValidatedRun(
            evaluation_registry,
            evaluation_manifest,
            evaluation_validation,
            evaluation_manifest_path,
        ),
    )


def _provisional_evaluation_snapshot(
    *,
    inference: ValidatedRun,
    evaluation_run_id: str,
    attempt_id: str,
) -> ProvisionalEvaluationSnapshot:
    attempt = LOG_ROOT / "evaluation-campaign" / attempt_id
    status_path = attempt / "status.json"
    status_before = read_json(status_path)
    if status_before.get("evaluation_run_id") != evaluation_run_id:
        raise AnalysisError("provisional evaluation attempt belongs to another evaluation run")
    if status_before.get("source_run_id") != inference.manifest.run_id:
        raise AnalysisError("provisional evaluation attempt belongs to another inference run")
    if status_before.get("state") != "running" or status_before.get("phase") != "confirmation":
        raise AnalysisError("provisional analysis requires an active confirmation phase")
    preflight = status_before.get("preflight")
    if not isinstance(preflight, dict) or preflight.get("validation_result") != "passed":
        raise AnalysisError("provisional evaluation attempt lacks a passed preflight")
    if preflight.get("timeout_policy_sha256") != sha256_file(DEFAULT_TIMEOUT_POLICY_PATH):
        raise AnalysisError("active evaluation uses a different timeout-policy hash")

    registry = LocalRunRegistry(REGISTRY_ROOT / evaluation_run_id)
    manifest = registry.latest_run_manifest(evaluation_run_id)
    if manifest is None:
        raise AnalysisError("provisional evaluation run has no manifest")
    manifest_path = registry.records_root / RunManifest.RECORD_TYPE / f"{manifest.record_id}.json"
    if manifest.status is not RunStatus.IN_PROGRESS:
        raise AnalysisError("provisional evaluation manifest is not in progress")
    if manifest.parent_run_id != inference.manifest.run_id:
        raise AnalysisError("provisional evaluation manifest has the wrong parent run")
    if manifest.provenance.study_version != inference.manifest.provenance.study_version:
        raise AnalysisError("provisional evaluation study version differs from inference")
    if (
        manifest.models != inference.manifest.models
        or manifest.benchmarks != inference.manifest.benchmarks
    ):
        raise AnalysisError("provisional evaluation scope differs from inference")

    captured_at = datetime.now(UTC)
    record_paths = sorted((registry.records_root / EvaluationRecord.RECORD_TYPE).glob("*.json"))
    records: list[EvaluationRecord] = []
    record_index: list[dict[str, Any]] = []
    for path in record_paths:
        record = EvaluationRecord.model_validate_json(path.read_bytes())
        if record.provenance.run_id != evaluation_run_id:
            raise AnalysisError("provisional evaluation record belongs to another run")
        records.append(record)
        record_index.append(
            {
                "record_id": record.record_id,
                "attempt_stage": record.attempt_stage.value,
                "benchmark_id": record.benchmark_id,
                "upstream_task_id": record.upstream_task_id,
                "candidate_record_id": record.candidate.candidate_record_id,
                "status": record.status.value,
                "functional_outcome": (
                    None if record.functional_outcome is None else record.functional_outcome.value
                ),
                "elapsed_seconds": record.elapsed_seconds,
                "timeout_seconds": record.timeout_seconds,
                "failure_type": record.failure_type,
                "failure_message": record.failure_message,
                "path": repository_relative(path),
                "sha256": sha256_file(path),
            }
        )
    status_after = read_json(status_path)
    primary = [
        record for record in records if record.attempt_stage is EvaluationAttemptStage.PRIMARY
    ]
    confirmations = [
        record for record in records if record.attempt_stage is EvaluationAttemptStage.CONFIRMATION
    ]
    expected_primary = preflight.get("candidate_count")
    if not isinstance(expected_primary, int) or len(primary) != expected_primary:
        raise AnalysisError("provisional snapshot does not contain the complete primary batch")
    primary_by_candidate = _unique_index(
        primary, lambda item: item.candidate.candidate_record_id, "provisional primary evaluation"
    )
    confirmation_by_candidate = _unique_index(
        confirmations,
        lambda item: item.candidate.candidate_record_id,
        "provisional confirmation evaluation",
    )
    primary_timeouts = [record for record in primary if record.status is EvaluationStatus.TIMEOUT]
    if not set(confirmation_by_candidate).issubset(primary_by_candidate):
        raise AnalysisError("provisional confirmation has no primary evaluation")
    if any(
        primary_by_candidate[candidate_id].status is not EvaluationStatus.TIMEOUT
        for candidate_id in confirmation_by_candidate
    ):
        raise AnalysisError("provisional confirmation targets a non-timeout primary")

    policy = load_timeout_policy()
    resolutions: list[EvaluationResolutionRecord] = []
    for primary_record in primary:
        confirmation = confirmation_by_candidate.get(primary_record.candidate.candidate_record_id)
        if primary_record.status is EvaluationStatus.TIMEOUT and confirmation is None:
            continue
        sources = [primary_record.record_id]
        if confirmation is not None:
            sources.append(confirmation.record_id)
        resolution_id = evaluation_resolution_id(
            primary_record.candidate.candidate_record_id,
            primary_record.task_record_id,
            primary_record.timeout_policy_version,
            primary_record.record_id,
            None if confirmation is None else confirmation.record_id,
        )
        resolutions.append(
            resolve_evaluation_attempts(
                record_id=resolution_id,
                provenance=Provenance(
                    study_version=inference.manifest.provenance.study_version,
                    run_id=evaluation_run_id,
                    created_at=captured_at,
                    producer="analysis_tools/processed_dataset.py:provisional_snapshot",
                    source_record_ids=tuple(sources),
                ),
                primary=primary_record,
                confirmation=confirmation,
                policy=policy,
            )
        )
    pending = len(primary_timeouts) - len(confirmations)
    metadata = {
        "schema_version": "provisional-evaluation-snapshot-v1",
        "result_status": "provisional",
        "paper_facing": False,
        "captured_at": captured_at.isoformat(),
        "attempt_id": attempt_id,
        "evaluation_run_id": evaluation_run_id,
        "source_state": "running_confirmation",
        "primary_count": len(primary),
        "primary_timeout_count": len(primary_timeouts),
        "captured_confirmation_count": len(confirmations),
        "pending_confirmation_count": pending,
        "synthetic_resolution_count": len(resolutions),
        "record_count": len(records),
        "status_before_capture": status_before,
        "status_after_capture": status_after,
    }
    return ProvisionalEvaluationSnapshot(
        registry=registry,
        manifest=manifest,
        manifest_path=manifest_path,
        resolutions=tuple(resolutions),
        record_index=tuple(record_index),
        metadata=metadata,
    )


def _adjudication(
    adjudication_id: str | None,
    inference_run_id: str,
) -> tuple[
    dict[str, DecisionAdjudicationRecord],
    list[DerivedProtocolOutcome],
    list[Path],
    dict[str, str],
]:
    if adjudication_id is None:
        return {}, [], [], {}
    root = LOG_ROOT / "decision-adjudication" / adjudication_id
    validation_path = root / "validation.json"
    report_path = root / "report.json"
    validation = read_json(validation_path)
    report = read_json(report_path)
    input_path = root / "input.json"
    input_payload = read_json(input_path)
    if validation.get("validation_result") != "passed":
        raise AnalysisError("Decision adjudication has not passed independent validation")
    if report.get("source_inference_run_id") != inference_run_id:
        raise AnalysisError("Decision adjudication belongs to another inference run")
    records: dict[str, DecisionAdjudicationRecord] = {}
    paths = [validation_path, report_path, input_path]
    resolution_sources = {
        str(item["call_id"]): str(item.get("resolution_source", "adjudicated"))
        for item in input_payload.get("decisions", [])
    }
    for path in sorted((root / "records").glob("*.json")):
        record = DecisionAdjudicationRecord.model_validate_json(path.read_bytes())
        if record.invalid_model_call_record_id in records:
            raise AnalysisError("duplicate adjudication for one invalid Decision call")
        records[record.invalid_model_call_record_id] = record
        paths.append(path)
    outcomes: list[DerivedProtocolOutcome] = []
    for path in sorted((root / "derived_outcomes").glob("*.json")):
        outcomes.append(DerivedProtocolOutcome.model_validate_json(path.read_bytes()))
        paths.append(path)
    if len(records) != report.get("invalid_decisions"):
        raise AnalysisError("adjudication record count differs from its report")
    if set(resolution_sources) != set(records):
        raise AnalysisError("adjudication input resolution sources do not cover its records")
    return records, outcomes, paths, resolution_sources


def _reported_call_status(call: ModelCallRecord | None) -> str | None:
    if call is None:
        return None
    if call.status is ModelCallStatus.EXTRACTION_FAILURE:
        return "malformed_candidate"
    return call.status.value


def _end_to_end_success(
    *,
    status: str,
    final_resolution: EvaluationResolutionRecord | None,
) -> int | None:
    if status in {"malformed_initial", "malformed_final_candidate"}:
        return 0
    if final_resolution is None or final_resolution.status is not EvaluationStatus.COMPLETED:
        return None
    if final_resolution.functional_outcome is None:
        return None
    return 1 if final_resolution.functional_outcome.value == "pass" else 0


def _unique_index(records: list[Any], key: Any, label: str) -> dict[Any, Any]:
    index: dict[Any, Any] = {}
    for record in records:
        item_key = key(record)
        if item_key in index:
            raise AnalysisError(f"duplicate {label}: {item_key}")
        index[item_key] = record
    return index


def _token_triplet(calls: list[ModelCallRecord]) -> dict[str, int] | None:
    if any(call.input_tokens is None or call.output_tokens is None for call in calls):
        return None
    input_tokens = sum(int(call.input_tokens) for call in calls if call.input_tokens is not None)
    output_tokens = sum(int(call.output_tokens) for call in calls if call.output_tokens is not None)
    return {"input": input_tokens, "output": output_tokens, "total": input_tokens + output_tokens}


def _add_triplets(*values: dict[str, int] | None) -> dict[str, int] | None:
    if any(value is None for value in values):
        return None
    return {
        key: sum(value[key] for value in values if value is not None)
        for key in ("input", "output", "total")
    }


def _subtract_triplets(
    left: dict[str, int] | None, right: dict[str, int] | None
) -> dict[str, int] | None:
    if left is None or right is None:
        return None
    return {key: left[key] - right[key] for key in ("input", "output", "total")}


def _resolution_fields(
    resolution: EvaluationResolutionRecord | None,
    prefix: str,
) -> dict[str, Any]:
    if resolution is None:
        return {
            f"{prefix}_evaluation_resolution_record_id": None,
            f"{prefix}_evaluation_status": None,
            f"{prefix}_functional_outcome": None,
            f"{prefix}_evaluation_total_elapsed_seconds": None,
        }
    return {
        f"{prefix}_evaluation_resolution_record_id": resolution.record_id,
        f"{prefix}_evaluation_status": resolution.status.value,
        f"{prefix}_functional_outcome": (
            None if resolution.functional_outcome is None else resolution.functional_outcome.value
        ),
        f"{prefix}_evaluation_total_elapsed_seconds": resolution.total_elapsed_seconds,
    }


def _analysis_status(
    *,
    protocol: Protocol,
    initial: CandidateRecord | None,
    final: CandidateRecord | None,
    initial_resolution: EvaluationResolutionRecord | None,
    final_resolution: EvaluationResolutionRecord | None,
    decision_source: str,
) -> str:
    if initial is None:
        return "missing_initial_candidate"
    if protocol in DERIVED_TO_ALWAYS and decision_source == "unresolved":
        return "unresolved_decision"
    if protocol in DERIVED_TO_ALWAYS and decision_source == "missing":
        return "missing_decision"
    if final is None:
        return "missing_final_candidate"
    if initial_resolution is None or final_resolution is None:
        return "missing_evaluation_resolution"
    if initial_resolution.status is EvaluationStatus.TIMEOUT:
        return "initial_timeout"
    if initial_resolution.status is EvaluationStatus.EVALUATION_FAILURE:
        return "initial_evaluation_failure"
    if initial_resolution.status is not EvaluationStatus.COMPLETED:
        return f"initial_{initial_resolution.status.value}"
    if final_resolution.status is EvaluationStatus.TIMEOUT:
        return "final_timeout"
    if final_resolution.status is EvaluationStatus.EVALUATION_FAILURE:
        return "final_evaluation_failure"
    if final_resolution.status is not EvaluationStatus.COMPLETED:
        return f"final_{final_resolution.status.value}"
    return "complete"


def _transition(initial: str | None, final: str | None) -> str | None:
    transitions: dict[tuple[str, str], str] = {
        ("fail", "pass"): "repair",
        ("pass", "fail"): "regression",
        ("pass", "pass"): "functional_preservation",
        ("fail", "fail"): "unrepaired_failure",
    }
    if initial is None or final is None:
        return None
    return transitions.get((initial, final))


def _decision_consequence(
    initial_outcome: str | None,
    always_outcome: str | None,
    decision: DecisionValue | None,
) -> str | None:
    if decision is not DecisionValue.PRESERVE:
        return "refinement_selected" if decision is DecisionValue.REFINE else None
    consequences: dict[tuple[str, str], str] = {
        ("pass", "fail"): "prevented_regression",
        ("pass", "pass"): "safe_preservation",
        ("fail", "pass"): "missed_repair",
        ("fail", "fail"): "unsuccessful_refinement_skipped",
    }
    if initial_outcome is None or always_outcome is None:
        return None
    return consequences.get((initial_outcome, always_outcome))


def build_processed_dataset(
    *,
    inference_run_id: str,
    evaluation_run_id: str,
    dataset_id: str,
    decision_adjudication_id: str | None = None,
    provisional_evaluation_attempt_id: str | None = None,
    output_root: Path = PROCESSED_ROOT,
) -> Path:
    if re.fullmatch(r"[a-z][a-z0-9-]{2,79}", dataset_id) is None:
        raise AnalysisError("dataset ID must be a lowercase, hyphenated identifier")
    target = output_root / dataset_id
    if target.exists():
        raise AnalysisError(f"processed dataset already exists: {target}")
    provisional: ProvisionalEvaluationSnapshot | None = None
    if provisional_evaluation_attempt_id is None:
        inference, evaluation = validate_source_runs(inference_run_id, evaluation_run_id)
    else:
        inference = _validated_inference_run(inference_run_id)
        provisional = _provisional_evaluation_snapshot(
            inference=inference,
            evaluation_run_id=evaluation_run_id,
            attempt_id=provisional_evaluation_attempt_id,
        )
        evaluation = ValidatedRun(
            registry=provisional.registry,
            manifest=provisional.manifest,
            validation_path=LOG_ROOT
            / "evaluation-campaign"
            / provisional_evaluation_attempt_id
            / "status.json",
            manifest_path=provisional.manifest_path,
        )
    adjudications, supplemental_outcomes, adjudication_paths, adjudication_sources = _adjudication(
        decision_adjudication_id, inference_run_id
    )
    records = inference.registry
    tasks = [
        record
        for record in records.records_of_type(TaskMetadata.RECORD_TYPE)
        if isinstance(record, TaskMetadata)
    ]
    models = [
        record
        for record in records.records_of_type(ModelConfiguration.RECORD_TYPE)
        if isinstance(record, ModelConfiguration)
    ]
    calls = [
        record
        for record in records.records_of_type(ModelCallRecord.RECORD_TYPE)
        if isinstance(record, ModelCallRecord)
    ]
    candidates = [
        record
        for record in records.records_of_type(CandidateRecord.RECORD_TYPE)
        if isinstance(record, CandidateRecord)
    ]
    decisions = [
        record
        for record in records.records_of_type(DecisionArtifact.RECORD_TYPE)
        if isinstance(record, DecisionArtifact)
    ]
    critiques = [
        record
        for record in records.records_of_type(CritiqueArtifact.RECORD_TYPE)
        if isinstance(record, CritiqueArtifact)
    ]
    plans = [
        record
        for record in records.records_of_type(RevisionPlanArtifact.RECORD_TYPE)
        if isinstance(record, RevisionPlanArtifact)
    ]
    original_outcomes = [
        record
        for record in records.records_of_type(DerivedProtocolOutcome.RECORD_TYPE)
        if isinstance(record, DerivedProtocolOutcome)
    ]
    resolutions = (
        list(provisional.resolutions)
        if provisional is not None
        else [
            record
            for record in evaluation.registry.records_of_type(
                EvaluationResolutionRecord.RECORD_TYPE
            )
            if isinstance(record, EvaluationResolutionRecord)
        ]
    )
    invalid_decision_calls = [
        call
        for call in calls
        if call.stage is Stage.REFINEMENT_NEED_DECISION
        and call.status is not ModelCallStatus.COMPLETED
    ]
    if invalid_decision_calls and decision_adjudication_id is None:
        raise AnalysisError(
            "the inference run has invalid Decisions; supply the validated adjudication ID"
        )
    if set(adjudications) != {call.record_id for call in invalid_decision_calls}:
        raise AnalysisError("adjudication does not cover every and only invalid Decision call")

    task_index = _unique_index(tasks, lambda item: item.record_id, "task")
    model_index = _unique_index(models, lambda item: item.record_id, "model configuration")
    candidate_index = _unique_index(
        candidates,
        lambda item: (item.model_configuration_record_id, item.task_record_id, item.protocol),
        "model-task-protocol candidate",
    )
    candidate_by_id = _unique_index(candidates, lambda item: item.record_id, "candidate record")
    resolution_index = _unique_index(
        resolutions,
        lambda item: item.candidate.candidate_record_id,
        "candidate evaluation resolution",
    )
    call_by_id = _unique_index(calls, lambda item: item.record_id, "model call")
    decision_by_initial = _unique_index(
        decisions,
        lambda item: item.initial_candidate.candidate_record_id,
        "parsed Decision",
    )
    _unique_index(
        critiques,
        lambda item: item.initial_candidate.candidate_record_id,
        "critique",
    )
    _unique_index(
        plans,
        lambda item: item.initial_candidate.candidate_record_id,
        "revision plan",
    )
    outcome_index = _unique_index(
        [*original_outcomes, *supplemental_outcomes],
        lambda item: (
            item.initial_candidate.candidate_record_id,
            item.protocol,
        ),
        "derived protocol outcome",
    )
    calls_by_pair: dict[tuple[str, str], list[ModelCallRecord]] = defaultdict(list)
    effective_call_by_stage: dict[tuple[str, str, Stage], ModelCallRecord] = {}
    for call in calls:
        pair = (call.model_configuration_record_id, call.task_record_id)
        calls_by_pair[pair].append(call)
    for pair, pair_calls in calls_by_pair.items():
        by_stage: dict[Stage, list[ModelCallRecord]] = defaultdict(list)
        for call in pair_calls:
            by_stage[call.stage].append(call)
        for stage, stage_calls in by_stage.items():
            completed = [call for call in stage_calls if call.status is ModelCallStatus.COMPLETED]
            if len(completed) > 1:
                raise AnalysisError(f"multiple completed calls for {pair} at {stage.value}")
            selected = (
                completed[0]
                if completed
                else max(stage_calls, key=lambda item: (item.attempt_number, item.record_id))
            )
            effective_call_by_stage[(*pair, stage)] = selected

    model_ids_by_record: dict[str, str] = {}
    launch = read_json(inference.registry.root / "launch.json")
    launch_models = launch.get("model_configuration_record_ids")
    if not isinstance(launch_models, dict):
        raise AnalysisError("inference launch metadata lacks model configuration mapping")
    for model_id, record_id in launch_models.items():
        if not isinstance(model_id, str) or not isinstance(record_id, str):
            raise AnalysisError("invalid model configuration mapping")
        model_ids_by_record[record_id] = model_id
    if set(model_ids_by_record) != set(model_index):
        raise AnalysisError("model configuration records differ from launch metadata")

    stage_rows: list[dict[str, Any]] = []
    for call in sorted(
        calls,
        key=lambda item: (
            model_ids_by_record[item.model_configuration_record_id],
            task_index[item.task_record_id].benchmark_id,
            task_index[item.task_record_id].upstream_task_id,
            item.stage.value,
            item.attempt_number,
        ),
    ):
        pair_stage = (call.model_configuration_record_id, call.task_record_id, call.stage)
        task = task_index[call.task_record_id]
        stage_rows.append(
            {
                "schema_version": _config()["stage_call_schema_version"],
                "inference_run_id": inference_run_id,
                "model_id": model_ids_by_record[call.model_configuration_record_id],
                "model_configuration_record_id": call.model_configuration_record_id,
                "benchmark_id": task.benchmark_id,
                "task_record_id": task.record_id,
                "upstream_task_id": task.upstream_task_id,
                "stage": call.stage.value,
                "model_call_record_id": call.record_id,
                "logical_call_id": call.logical_call_id,
                "attempt_number": call.attempt_number,
                "status": call.status.value,
                "reported_status": _reported_call_status(call),
                "is_effective_attempt": effective_call_by_stage[pair_stage].record_id
                == call.record_id,
                "input_tokens": call.input_tokens,
                "output_tokens": call.output_tokens,
                "total_tokens": (
                    None
                    if call.input_tokens is None or call.output_tokens is None
                    else call.input_tokens + call.output_tokens
                ),
                "finish_reason": None if call.finish_reason is None else call.finish_reason.value,
                "elapsed_seconds": call.elapsed_seconds,
                "raw_response_sha256": (
                    None if call.raw_response is None else call.raw_response.sha256
                ),
                "supersedes_call_record_id": call.supersedes_call_record_id,
            }
        )

    outcome_rows: list[dict[str, Any]] = []
    for model_record_id, model in sorted(
        model_index.items(), key=lambda item: model_ids_by_record[item[0]]
    ):
        model_id = model_ids_by_record[model_record_id]
        for task in sorted(tasks, key=lambda item: (item.benchmark_id, item.upstream_task_id)):
            pair = (model_record_id, task.record_id)
            initial = candidate_index.get((*pair, Protocol.DIRECT))
            initial_resolution = (
                None if initial is None else resolution_index.get(initial.record_id)
            )
            direct_call = effective_call_by_stage.get((*pair, Stage.DIRECT_GENERATION))
            initial_cost = None if direct_call is None else _token_triplet([direct_call])
            actual_calls = calls_by_pair.get(pair, [])
            tokenized_actual_calls = [
                call
                for call in actual_calls
                if call.input_tokens is not None and call.output_tokens is not None
            ]
            experimental_cost = _token_triplet(tokenized_actual_calls)
            # No returned call is unknown consumption, not a zero-token experiment.
            if not tokenized_actual_calls:
                experimental_cost = None
            decision = None if initial is None else decision_by_initial.get(initial.record_id)
            adjudication = None
            decision_call = None
            decision_source = "not_applicable"
            decision_value: DecisionValue | None = None
            decision_record_id: str | None = None
            if decision is not None:
                decision_source = "exact"
                decision_value = decision.decision
                decision_record_id = decision.record_id
                decision_call = call_by_id[decision.model_call_record_id]
            elif initial is not None:
                invalid_calls = [
                    call
                    for call in actual_calls
                    if call.stage is Stage.REFINEMENT_NEED_DECISION
                    and call.status is not ModelCallStatus.COMPLETED
                ]
                if len(invalid_calls) > 1:
                    raise AnalysisError(f"multiple invalid effective Decisions for {pair}")
                if invalid_calls:
                    decision_call = invalid_calls[0]
                    adjudication = adjudications.get(decision_call.record_id)
                    if adjudication is None:
                        decision_source = "missing"
                    elif adjudication.status is AdjudicationStatus.UNRESOLVED:
                        decision_source = "unresolved"
                        decision_record_id = adjudication.adjudication_record_id
                    else:
                        decision_source = adjudication_sources[decision_call.record_id]
                        decision_value = adjudication.decision
                        decision_record_id = adjudication.adjudication_record_id
                else:
                    decision_source = "missing"
            decision_cost = None if decision_call is None else _token_triplet([decision_call])

            stage_call_cost: dict[Stage, dict[str, int] | None] = {}
            for stage in Stage:
                stage_call = effective_call_by_stage.get((*pair, stage))
                stage_call_cost[stage] = (
                    None if stage_call is None else _token_triplet([stage_call])
                )
            always_costs = {
                protocol: _add_triplets(*(stage_call_cost[stage] for stage in stages))
                for protocol, stages in PROTOCOL_STAGES.items()
            }
            # Direct has no incremental refinement call, hence a defined zero cost.
            always_costs[Protocol.DIRECT] = {"input": 0, "output": 0, "total": 0}

            for protocol in PROTOCOL_ORDER:
                always_protocol = DERIVED_TO_ALWAYS.get(protocol)
                final: CandidateRecord | None
                derived: DerivedProtocolOutcome | None = None
                if protocol in GENERATED_PROTOCOLS:
                    final = candidate_index.get((*pair, protocol))
                elif initial is None:
                    final = None
                else:
                    derived = outcome_index.get((initial.record_id, protocol))
                    final = (
                        None
                        if derived is None
                        else candidate_by_id.get(derived.final_candidate.candidate_record_id)
                    )
                final_resolution = None if final is None else resolution_index.get(final.record_id)
                cost_protocol = protocol if protocol in GENERATED_PROTOCOLS else always_protocol
                if cost_protocol is None:
                    raise AnalysisError(f"protocol has no cost path: {protocol.value}")
                refinement_cost = always_costs[cost_protocol]
                if protocol in GENERATED_PROTOCOLS:
                    incremental_cost = refinement_cost
                elif decision_value is DecisionValue.PRESERVE:
                    incremental_cost = decision_cost
                elif decision_value is DecisionValue.REFINE:
                    incremental_cost = _add_triplets(decision_cost, refinement_cost)
                else:
                    incremental_cost = None
                end_to_end_cost = _add_triplets(initial_cost, incremental_cost)
                avoided_cost = (
                    refinement_cost
                    if protocol in DERIVED_TO_ALWAYS and decision_value is DecisionValue.PRESERVE
                    else (
                        {"input": 0, "output": 0, "total": 0}
                        if protocol in DERIVED_TO_ALWAYS
                        else None
                    )
                )
                always_end_to_end = (
                    None
                    if always_protocol is None
                    else _add_triplets(initial_cost, always_costs[always_protocol])
                )
                net_saving = (
                    None
                    if always_end_to_end is None or end_to_end_cost is None
                    else _subtract_triplets(always_end_to_end, end_to_end_cost)
                )
                initial_outcome = (
                    None
                    if initial_resolution is None or initial_resolution.functional_outcome is None
                    else initial_resolution.functional_outcome.value
                )
                final_outcome = (
                    None
                    if final_resolution is None or final_resolution.functional_outcome is None
                    else final_resolution.functional_outcome.value
                )
                always_candidate = (
                    None
                    if always_protocol is None
                    else candidate_index.get((*pair, always_protocol))
                )
                always_resolution = (
                    None
                    if always_candidate is None
                    else resolution_index.get(always_candidate.record_id)
                )
                always_outcome = (
                    None
                    if always_resolution is None or always_resolution.functional_outcome is None
                    else always_resolution.functional_outcome.value
                )
                status = _analysis_status(
                    protocol=protocol,
                    initial=initial,
                    final=final,
                    initial_resolution=initial_resolution,
                    final_resolution=final_resolution,
                    decision_source=decision_source,
                )
                final_candidate_status = "available" if final is not None else None
                if initial is None and _reported_call_status(direct_call) == "malformed_candidate":
                    status = "malformed_initial"
                    final_candidate_status = "malformed_candidate"
                elif final is None:
                    final_stage = {
                        Protocol.R: Stage.DIRECT_REVISION,
                        Protocol.CR: Stage.CRITIQUE_CONDITIONED_REVISION,
                        Protocol.CPR: Stage.PLAN_CONDITIONED_REVISION,
                        Protocol.DR: Stage.DIRECT_REVISION,
                        Protocol.DCR: Stage.CRITIQUE_CONDITIONED_REVISION,
                        Protocol.DCPR: Stage.PLAN_CONDITIONED_REVISION,
                    }.get(protocol)
                    failed_call = (
                        None
                        if final_stage is None
                        else effective_call_by_stage.get((*pair, final_stage))
                    )
                    if _reported_call_status(failed_call) == "malformed_candidate":
                        status = "malformed_final_candidate"
                        final_candidate_status = "malformed_candidate"
                row = {
                    "schema_version": _config()["processed_schema_version"],
                    "dataset_id": dataset_id,
                    "study_version": inference.manifest.provenance.study_version,
                    "inference_run_id": inference_run_id,
                    "evaluation_run_id": evaluation_run_id,
                    "decision_adjudication_id": decision_adjudication_id,
                    "model_id": model_id,
                    "model_display_name": model.display_name,
                    "model_configuration_record_id": model_record_id,
                    "benchmark_id": task.benchmark_id,
                    "benchmark_revision": task.benchmark_revision,
                    "task_record_id": task.record_id,
                    "upstream_task_id": task.upstream_task_id,
                    "protocol": protocol.value,
                    "always_refine_protocol": (
                        None if always_protocol is None else always_protocol.value
                    ),
                    "initial_candidate_record_id": None if initial is None else initial.record_id,
                    "initial_source_sha256": None if initial is None else initial.source_sha256,
                    "final_candidate_record_id": None if final is None else final.record_id,
                    "final_source_sha256": None if final is None else final.source_sha256,
                    "always_refine_candidate_record_id": (
                        None if always_candidate is None else always_candidate.record_id
                    ),
                    "derived_outcome_record_id": None if derived is None else derived.record_id,
                    "decision_record_id": decision_record_id,
                    "decision": None if decision_value is None else decision_value.value,
                    "decision_source": (
                        "not_applicable" if protocol in GENERATED_PROTOCOLS else decision_source
                    ),
                    "final_selection": None if derived is None else derived.final_selection.value,
                    "analysis_status": status,
                    "initial_candidate_status": (
                        "available" if initial is not None else _reported_call_status(direct_call)
                    ),
                    "final_candidate_status": final_candidate_status,
                    **_resolution_fields(initial_resolution, "initial"),
                    **_resolution_fields(final_resolution, "final"),
                    "end_to_end_success": _end_to_end_success(
                        status=status,
                        final_resolution=final_resolution,
                    ),
                    "transition": _transition(initial_outcome, final_outcome),
                    "candidate_changed_exact": (
                        None
                        if initial is None or final is None
                        else initial.source_code != final.source_code
                    ),
                    "candidate_changed_normalized": (
                        None
                        if initial is None or final is None
                        else normalize_source(initial.source_code)
                        != normalize_source(final.source_code)
                    ),
                    "decision_consequence": (
                        None
                        if protocol not in DERIVED_TO_ALWAYS
                        else _decision_consequence(initial_outcome, always_outcome, decision_value)
                    ),
                    "initial_generation_tokens": initial_cost,
                    "decision_tokens": decision_cost if protocol in DERIVED_TO_ALWAYS else None,
                    "refinement_tokens": refinement_cost,
                    "incremental_protocol_tokens": incremental_cost,
                    "end_to_end_protocol_tokens": end_to_end_cost,
                    "experimental_token_consumption": experimental_cost,
                    "avoided_refinement_tokens": avoided_cost,
                    "net_token_saving": net_saving,
                }
                outcome_rows.append(row)

    outcome_rows.sort(
        key=lambda row: (
            row["model_id"],
            row["benchmark_id"],
            row["upstream_task_id"],
            [protocol.value for protocol in PROTOCOL_ORDER].index(row["protocol"]),
        )
    )
    target.mkdir(parents=True, exist_ok=False)
    outcomes_path = target / "outcomes.jsonl"
    stage_calls_path = target / "stage_calls.jsonl"
    write_jsonl(outcomes_path, outcome_rows)
    write_jsonl(stage_calls_path, stage_rows)
    data_dictionary = _data_dictionary()
    data_dictionary["result_status"] = "provisional" if provisional is not None else "final"
    data_dictionary["paper_facing"] = provisional is None
    write_json(target / "data_dictionary.json", data_dictionary)
    if provisional is not None:
        write_json(target / "evaluation_snapshot.json", provisional.metadata)
        write_jsonl(target / "evaluation_record_index.jsonl", provisional.record_index)
    source_paths = [
        inference.manifest_path,
        inference.validation_path,
        evaluation.manifest_path,
        inference.registry.root / "launch.json",
        inference.registry.root / "scope.json",
        *adjudication_paths,
    ]
    if provisional is None:
        source_paths.append(evaluation.validation_path)
    result_status = "provisional" if provisional is not None else "final"
    derived_files = {
        "outcomes.jsonl": sha256_file(outcomes_path),
        "stage_calls.jsonl": sha256_file(stage_calls_path),
        "data_dictionary.json": sha256_file(target / "data_dictionary.json"),
    }
    if provisional is not None:
        derived_files.update(
            {
                "evaluation_snapshot.json": sha256_file(target / "evaluation_snapshot.json"),
                "evaluation_record_index.jsonl": sha256_file(
                    target / "evaluation_record_index.jsonl"
                ),
            }
        )
    manifest = {
        "schema_version": "processed-dataset-manifest-v1",
        "dataset_id": dataset_id,
        "result_status": result_status,
        "paper_facing": provisional is None,
        "analysis_version": _config()["analysis_version"],
        "analysis_configuration_path": repository_relative(CONFIG_PATH),
        "analysis_configuration_sha256": sha256_file(CONFIG_PATH),
        "study_version": inference.manifest.provenance.study_version,
        "inference_run_id": inference_run_id,
        "evaluation_run_id": evaluation_run_id,
        "provisional_evaluation_attempt_id": provisional_evaluation_attempt_id,
        "pending_confirmation_count": (
            0 if provisional is None else int(provisional.metadata["pending_confirmation_count"])
        ),
        "decision_adjudication_id": decision_adjudication_id,
        "source_manifests": {
            "inference": inference.manifest.record_id,
            "evaluation": evaluation.manifest.record_id,
        },
        "source_files": [
            {"path": repository_relative(path), "sha256": sha256_file(path)}
            for path in sorted(set(source_paths))
        ],
        "producer_git_commit": git_commit(),
        "row_counts": {
            "outcomes": len(outcome_rows),
            "stage_calls": len(stage_rows),
            "tasks": len(tasks),
            "models": len(models),
            "protocols": len(PROTOCOL_ORDER),
        },
        "status_counts": dict(
            sorted(Counter(row["analysis_status"] for row in outcome_rows).items())
        ),
        "files": derived_files,
    }
    write_json(target / "manifest.json", manifest)
    validate_processed_dataset(target, write_report=True)
    return target


def _data_dictionary() -> dict[str, Any]:
    return {
        "schema_version": "processed-data-dictionary-v1",
        "unit_of_analysis": "one model-task-protocol outcome row",
        "protocols": [protocol.value for protocol in PROTOCOL_ORDER],
        "functional_outcomes": ["pass", "fail"],
        "primary_success_measure": {
            "field": "end_to_end_success",
            "one": "candidate received a completed PASS evaluation",
            "zero": (
                "candidate received a completed FAIL evaluation or the model produced a "
                "malformed candidate"
            ),
            "null": (
                "timeout, evaluator/infrastructure failure, exclusion, or unresolved non-model "
                "outcome"
            ),
        },
        "nonfunctional_states": [
            "timeout",
            "evaluation_failure",
            "excluded_task",
            "missing artifact or resolution",
            "malformed_candidate (model-attributable, end_to_end_success=0)",
            "unresolved Decision",
        ],
        "transition_values": [
            "repair",
            "regression",
            "functional_preservation",
            "unrepaired_failure",
        ],
        "decision_source_values": [
            "not_applicable",
            "exact",
            "normalized",
            "adjudicated",
            "unresolved",
            "missing",
        ],
        "token_measures": {
            "initial_generation_tokens": "Direct Generation call used by every condition",
            "incremental_protocol_tokens": (
                "calls logically implied after the shared initial generation"
            ),
            "end_to_end_protocol_tokens": "initial generation plus incremental protocol calls",
            "experimental_token_consumption": (
                "all returned model-call attempts actually executed for the pair; never sum this "
                "repeated field across protocol rows"
            ),
            "avoided_refinement_tokens": "always-refine calls skipped by a PRESERVE Decision",
            "net_token_saving": (
                "always-refine end-to-end cost minus Decision-conditioned end-to-end cost"
            ),
        },
        "missingness_policy": (
            "Model-attributable malformed candidates remain distinct from functional FAIL but "
            "count as zero in end_to_end_success. TIMEOUT and evaluation infrastructure failure "
            "remain indeterminate; paired primary-success metrics report exclusions."
        ),
        "source_normalization": (
            "normalize CRLF/CR to LF, remove trailing line whitespace, and remove outer blank "
            "lines only"
        ),
    }


def validate_processed_dataset(dataset_dir: Path, *, write_report: bool = False) -> dict[str, Any]:
    manifest = read_json(dataset_dir / "manifest.json")
    outcomes = read_jsonl(dataset_dir / "outcomes.jsonl")
    stage_calls = read_jsonl(dataset_dir / "stage_calls.jsonl")
    config = _config()
    if manifest.get("analysis_configuration_sha256") != sha256_file(CONFIG_PATH):
        raise AnalysisError("processed dataset uses a different analysis configuration")
    result_status = manifest.get("result_status", "final")
    if result_status not in {"final", "provisional"}:
        raise AnalysisError("processed dataset has an invalid result status")
    if manifest.get("paper_facing", result_status == "final") is not (result_status == "final"):
        raise AnalysisError("processed dataset result status and paper-facing flag disagree")
    pending_confirmation_count = manifest.get("pending_confirmation_count", 0)
    if not isinstance(pending_confirmation_count, int) or pending_confirmation_count < 0:
        raise AnalysisError("processed dataset has an invalid pending-confirmation count")
    if result_status == "final" and pending_confirmation_count != 0:
        raise AnalysisError("final processed dataset cannot have pending confirmations")
    if result_status == "provisional":
        snapshot = read_json(dataset_dir / "evaluation_snapshot.json")
        record_index = read_jsonl(dataset_dir / "evaluation_record_index.jsonl")
        if (
            snapshot.get("result_status") != "provisional"
            or snapshot.get("paper_facing") is not False
        ):
            raise AnalysisError("provisional evaluation snapshot has invalid status flags")
        if snapshot.get("pending_confirmation_count") != pending_confirmation_count:
            raise AnalysisError("provisional pending-confirmation counts disagree")
        if snapshot.get("record_count") != len(record_index):
            raise AnalysisError("provisional evaluation record count differs from its index")
        record_ids: set[str] = set()
        for item in record_index:
            record_id = str(item.get("record_id"))
            if record_id in record_ids:
                raise AnalysisError(f"duplicate provisional evaluation record: {record_id}")
            record_ids.add(record_id)
            record_path = PROJECT_ROOT / str(item.get("path"))
            if sha256_file(record_path) != item.get("sha256"):
                raise AnalysisError(f"provisional evaluation record hash mismatch: {record_id}")
    for source in manifest.get("source_files", []):
        if not isinstance(source, dict):
            raise AnalysisError("processed dataset has a malformed source-file entry")
        source_path = PROJECT_ROOT / str(source.get("path"))
        if sha256_file(source_path) != source.get("sha256"):
            raise AnalysisError(f"processed source file hash mismatch: {source_path}")
    for name, expected_hash in manifest.get("files", {}).items():
        path = dataset_dir / name
        if sha256_file(path) != expected_hash:
            raise AnalysisError(f"processed file hash mismatch: {name}")
    counts = manifest.get("row_counts", {})
    if counts.get("outcomes") != len(outcomes) or counts.get("stage_calls") != len(stage_calls):
        raise AnalysisError("processed row counts differ from manifest")
    expected_outcomes = (
        counts.get("models", 0) * counts.get("tasks", 0) * counts.get("protocols", 0)
    )
    if len(outcomes) != expected_outcomes:
        raise AnalysisError("processed dataset is not a complete model-task-protocol grid")
    keys: set[tuple[str, str, str]] = set()
    for row in outcomes:
        if row.get("schema_version") != config["processed_schema_version"]:
            raise AnalysisError("outcome row schema version mismatch")
        key = (str(row.get("model_id")), str(row.get("task_record_id")), str(row.get("protocol")))
        if key in keys:
            raise AnalysisError(f"duplicate outcome row: {key}")
        keys.add(key)
        initial = row.get("initial_functional_outcome")
        final = row.get("final_functional_outcome")
        if initial not in {None, "pass", "fail"} or final not in {None, "pass", "fail"}:
            raise AnalysisError("invalid functional outcome in processed row")
        if row.get("analysis_status") == "complete" and row.get("transition") is None:
            raise AnalysisError("complete outcome lacks a functional transition")
        if row.get("final_evaluation_status") != "completed" and final is not None:
            raise AnalysisError("non-completed evaluation was assigned functional correctness")
        end_to_end = row.get("end_to_end_success")
        if end_to_end not in {None, 0, 1}:
            raise AnalysisError("invalid end-to-end success value")
        if row.get("analysis_status") in {"malformed_initial", "malformed_final_candidate"} and (
            end_to_end != 0 or final is not None
        ):
            raise AnalysisError("malformed candidate row must be a nonfunctional zero")
    call_ids: set[str] = set()
    for row in stage_calls:
        if row.get("schema_version") != config["stage_call_schema_version"]:
            raise AnalysisError("stage-call row schema version mismatch")
        call_id = str(row.get("model_call_record_id"))
        if call_id in call_ids:
            raise AnalysisError(f"duplicate stage-call row: {call_id}")
        call_ids.add(call_id)
    report = {
        "schema_version": "processed-dataset-validation-v1",
        "validation_result": "passed",
        "dataset_id": manifest["dataset_id"],
        "manifest_sha256": sha256_file(dataset_dir / "manifest.json"),
        "outcome_rows": len(outcomes),
        "stage_call_rows": len(stage_calls),
        "complete_grid": True,
        "functional_missingness_preserved": True,
        "result_status": result_status,
        "paper_facing": result_status == "final",
        "pending_confirmation_count": pending_confirmation_count,
        "validation_scope": (
            "terminal_source_and_derived_integrity"
            if result_status == "final"
            else "provisional_snapshot_and_derived_integrity"
        ),
    }
    if write_report:
        write_json(dataset_dir / "validation.json", report)
    return report
