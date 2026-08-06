#!/usr/bin/env python3
"""Run the four role-separated follow-up phases as durable, restartable attempts."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from scripts.run_model_campaign import (  # noqa: E402
    ENVIRONMENT_PYTHON,
    MODEL_ROOT,
    REGISTRY_ROOT,
    _atomic_json,
    _git_commit,
    _phase_payload,
    _put_manifest,
    _require_clear_gpus,
    _worker_environment,
    _write_once_bytes,
)
from self_refinement.hashing import sha256_file, sha256_json  # noqa: E402
from self_refinement.identifiers import run_id as make_run_id  # noqa: E402
from self_refinement.inference.configuration import (  # noqa: E402
    load_primary_inference_configuration,
    validate_primary_snapshot_provenance,
)
from self_refinement.inference.interface import ModelCallExecutor  # noqa: E402
from self_refinement.protocols.campaign import (  # noqa: E402
    build_model_configuration_records,
    build_prompt_metadata_records,
)
from self_refinement.protocols.prompts import load_prompt_manifest  # noqa: E402
from self_refinement.protocols.role_separated import (  # noqa: E402
    DEFAULT_ROLE_SEPARATED_CONFIGURATION_PATH,
    ROLE_SEPARATED_PHASE_ORDER,
    RoleSeparatedCampaignConfiguration,
    load_role_separated_configuration,
    role_separated_configuration_hashes,
)
from self_refinement.protocols.runner import (  # noqa: E402
    CampaignContext,
    CampaignPhase,
    PhaseReport,
    ProtocolCampaignRunner,
    TaskArtifacts,
)
from self_refinement.protocols.scope import (  # noqa: E402
    export_public_scope,
    load_public_scope,
    public_scope_json,
)
from self_refinement.schemas.models import (  # noqa: E402
    CandidateKind,
    CandidateRecord,
    CritiqueArtifact,
    ModelCallRecord,
    Provenance,
    RevisionPlanArtifact,
    RunManifest,
    RunStatus,
    Stage,
    TaskMetadata,
)
from self_refinement.storage.registry import LocalRunRegistry  # noqa: E402

SEQUENCE_ROOT = PROJECT_ROOT / "runs" / "logs" / "role-separated-sequence"
PHASE_ROOT = PROJECT_ROOT / "runs" / "logs" / "role-separated-phase"
PRODUCER = "scripts/run_role_separated_campaign.py"
EXECUTION_WORKTREE_PATHS = (
    "scripts",
    "src",
    "configs",
    "prompts",
    "pyproject.toml",
    "requirements.lock",
    "requirements-vllm.lock",
)
PHASE_LABELS = {
    CampaignPhase.SHARED_CRITIQUE: "critique_generation",
    CampaignPhase.CR_REVISION: "critique_conditioned_revision",
    CampaignPhase.SHARED_PLAN: "revision_planning",
    CampaignPhase.CPR_REVISION: "plan_conditioned_revision",
}
PHASE_PREREQUISITES = {
    CampaignPhase.SHARED_CRITIQUE: (),
    CampaignPhase.CR_REVISION: (CampaignPhase.SHARED_CRITIQUE,),
    CampaignPhase.SHARED_PLAN: (CampaignPhase.SHARED_CRITIQUE,),
    CampaignPhase.CPR_REVISION: (CampaignPhase.SHARED_PLAN,),
}


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _status_path(attempt: Path) -> Path:
    return attempt / "status.json"


def _write_status(attempt: Path, value: dict[str, Any]) -> None:
    _atomic_json(_status_path(attempt), {**value, "updated_at": _utc_now()})


def _update_status(attempt: Path, **changes: Any) -> None:
    current = json.loads(_status_path(attempt).read_text(encoding="utf-8"))
    if not isinstance(current, dict):
        raise RuntimeError("attempt status is not a JSON object")
    _write_status(attempt, {**current, **changes})


def _safe_attempt_id(value: str, prefix: str) -> None:
    if not value.startswith(prefix) or not all(
        character.isalnum() or character in {"-", "_"} for character in value
    ):
        raise ValueError(f"attempt ID must start with {prefix!r} and contain safe characters")


def _git_changes() -> list[str]:
    return subprocess.run(
        ["git", "status", "--porcelain", "--", *EXECUTION_WORKTREE_PATHS],
        check=True,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    ).stdout.splitlines()


def _source_validation(
    configuration: RoleSeparatedCampaignConfiguration,
) -> dict[str, Any]:
    source_path = configuration.resolve(configuration.source_validation_path)
    if sha256_file(source_path) != configuration.source_validation_sha256:
        raise RuntimeError("source inference validation hash differs from the frozen pin")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if (
        source.get("validation_result") != "passed"
        or source.get("run_id") != configuration.source_run_id
        or source.get("attempt_id") != configuration.source_attempt_id
        or source.get("manifest_record_id") != configuration.source_manifest_record_id
    ):
        raise RuntimeError("source inference validation does not match the frozen lineage")
    adjudication_path = configuration.resolve(configuration.decision_adjudication_validation_path)
    if sha256_file(adjudication_path) != configuration.decision_adjudication_validation_sha256:
        raise RuntimeError("Decision processing validation hash differs from the frozen pin")
    adjudication = json.loads(adjudication_path.read_text(encoding="utf-8"))
    if adjudication.get("validation_result") != "passed":
        raise RuntimeError("Decision processing source is not validated")
    return {"inference": source, "decision_processing": adjudication}


def _preflight(
    configuration_path: Path, *, require_execution_enabled: bool, require_clear_gpu: bool
) -> dict[str, Any]:
    configuration = load_role_separated_configuration(configuration_path)
    if require_execution_enabled and configuration.execution_gate != "enabled":
        raise RuntimeError("role-separated campaign execution is disabled")
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError("campaign orchestration requires Python 3.12")
    if not ENVIRONMENT_PYTHON.is_file():
        raise RuntimeError("validated vLLM environment is missing")
    source_validation = _source_validation(configuration)
    if not configuration.source_registry_path.is_dir():
        raise RuntimeError("validated source inference registry is missing")
    inference = load_primary_inference_configuration(
        configuration.resolve(configuration.inference_configuration)
    )
    prompts = load_prompt_manifest(configuration.resolve(configuration.prompt_configuration))
    scope = export_public_scope(configuration.resolve(configuration.scope_configuration))
    if scope.study_version != configuration.study_version or len(scope.tasks) != 1677:
        raise RuntimeError("role-separated scope does not match the frozen full scope")
    source_scope = load_public_scope(configuration.source_registry_path / "scope.json")
    source_task_fingerprints = {
        (task.task_record_id, task.specification_sha256) for task in source_scope.tasks
    }
    current_task_fingerprints = {
        (task.task_record_id, task.specification_sha256) for task in scope.tasks
    }
    if source_task_fingerprints != current_task_fingerprints:
        raise RuntimeError("role-separated scope differs from the source task bytes")
    cpr_inputs = prompts.template(Stage.PLAN_CONDITIONED_REVISION).input_fields
    if cpr_inputs != ("task_specification", "initial_candidate", "revision_plan"):
        raise RuntimeError("role-separated CPR must receive the plan but not the critique")
    snapshot_validation = validate_primary_snapshot_provenance(
        inference,
        manifest_path=configuration.resolve(configuration.model_manifest),
        model_root=MODEL_ROOT,
    )
    build_model_configuration_records(
        campaign=cast(Any, configuration),
        inference=inference,
        checkpoint_manifest_path=configuration.resolve(configuration.model_manifest),
        run_id="run_000000000000000000000000",
        producer=PRODUCER,
    )
    version_lines = subprocess.run(
        [
            str(ENVIRONMENT_PYTHON),
            "-c",
            "import platform, vllm; print(platform.python_version()); print(vllm.__version__)",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env=_worker_environment(),
    ).stdout.splitlines()
    if (
        len(version_lines) != 2
        or not version_lines[0].startswith("3.12.")
        or version_lines[1] != inference.inference_engine_version
    ):
        raise RuntimeError(f"unexpected vLLM environment versions: {version_lines}")
    gpu_memory = _require_clear_gpus() if require_clear_gpu else None
    changes = _git_changes()
    if require_execution_enabled and changes:
        raise RuntimeError("campaign launch requires clean committed execution inputs")
    disk = shutil.disk_usage(PROJECT_ROOT)
    return {
        "schema_version": "role-separated-preflight-v1",
        "validation_result": "passed",
        "configuration_version": configuration.configuration_version,
        "study_version": configuration.study_version,
        "phase_order": [phase.value for phase in configuration.phase_order],
        "task_count": len(scope.tasks),
        "model_order": list(configuration.model_order),
        "source_run_id": configuration.source_run_id,
        "source_validation": source_validation,
        "configuration_hashes": role_separated_configuration_hashes(
            configuration_path, configuration
        ),
        "prompt_hashes": {
            template.stage.value: template.template_sha256 for template in prompts.templates
        },
        "snapshot_validation": snapshot_validation,
        "orchestration_python": ".".join(str(item) for item in sys.version_info[:3]),
        "vllm_python": version_lines[0],
        "vllm_version": version_lines[1],
        "gpu_used_memory_mib": gpu_memory,
        "disk_free_bytes": disk.free,
        "git_clean": not changes,
    }


def _latest_manifest(registry: LocalRunRegistry) -> RunManifest:
    manifests = [
        item
        for item in registry.records_of_type(RunManifest.RECORD_TYPE)
        if isinstance(item, RunManifest)
    ]
    if not manifests:
        raise RuntimeError("target registry has no run manifest")
    return max(manifests, key=lambda item: item.manifest_revision)


def _put_target_manifest(
    *,
    registry: LocalRunRegistry,
    configuration: RoleSeparatedCampaignConfiguration,
    launch: dict[str, Any],
    status: RunStatus,
    git_commit: str,
    failure_summary: str | None = None,
) -> RunManifest:
    return _put_manifest(
        registry=registry,
        run_id=launch["run_id"],
        study_version=configuration.study_version,
        status=status,
        started_at=datetime.fromisoformat(launch["run_started_at"]),
        git_commit=git_commit,
        configuration_versions=launch["configuration_versions"],
        configuration_hashes=launch["configuration_hashes"],
        prompt_version=launch["prompt_version"],
        prompt_hashes=launch["prompt_hashes"],
        models=configuration.model_order,
        scope_version=launch["scope_version"],
        failure_summary=failure_summary,
        parent_run_id=configuration.source_run_id,
    )


def _build_source_initial_index(
    configuration: RoleSeparatedCampaignConfiguration,
    scope_task_ids: set[str],
) -> dict[str, dict[str, str]]:
    source_registry = LocalRunRegistry(configuration.source_registry_path)
    source_launch = json.loads(
        (configuration.source_registry_path / "launch.json").read_text(encoding="utf-8")
    )
    source_model_ids = source_launch.get("model_configuration_record_ids")
    if not isinstance(source_model_ids, dict) or set(source_model_ids) != set(
        configuration.model_order
    ):
        raise RuntimeError("source launch model identities do not match the new campaign")
    model_by_configuration = {value: key for key, value in source_model_ids.items()}
    index: dict[str, dict[str, str]] = {model_id: {} for model_id in configuration.model_order}
    for record in source_registry.records_of_type(CandidateRecord.RECORD_TYPE):
        if (
            not isinstance(record, CandidateRecord)
            or record.candidate_kind is not CandidateKind.INITIAL
        ):
            continue
        model_id = model_by_configuration.get(record.model_configuration_record_id)
        if model_id is None or record.task_record_id not in scope_task_ids:
            continue
        if record.task_record_id in index[model_id]:
            raise RuntimeError("source registry contains duplicate initial candidates")
        index[model_id][record.task_record_id] = record.record_id
    if sum(len(items) for items in index.values()) != 10054:
        raise RuntimeError("source initial candidate count differs from the validated 10,054")
    return index


def _initialize_target(
    configuration_path: Path,
    *,
    run_id: str,
    started_at: datetime,
    git_commit: str,
) -> tuple[LocalRunRegistry, dict[str, Any]]:
    configuration = load_role_separated_configuration(configuration_path)
    registry = LocalRunRegistry(REGISTRY_ROOT / run_id)
    scope = export_public_scope(configuration.resolve(configuration.scope_configuration))
    scope_path = registry.root / "scope.json"
    _write_once_bytes(scope_path, public_scope_json(scope))
    inference = load_primary_inference_configuration(
        configuration.resolve(configuration.inference_configuration)
    )
    prompts = load_prompt_manifest(configuration.resolve(configuration.prompt_configuration))
    model_records = build_model_configuration_records(
        campaign=cast(Any, configuration),
        inference=inference,
        checkpoint_manifest_path=configuration.resolve(configuration.model_manifest),
        run_id=run_id,
        producer=PRODUCER,
    )
    prompt_records = build_prompt_metadata_records(
        study_version=configuration.study_version,
        run_id=run_id,
        producer=PRODUCER,
        prompts=prompts,
    )
    now = datetime.now(UTC)
    for task in scope.tasks:
        registry.put_record(
            TaskMetadata(
                record_id=task.task_record_id,
                provenance=Provenance(
                    study_version=configuration.study_version,
                    run_id=run_id,
                    created_at=now,
                    producer=PRODUCER,
                ),
                benchmark_id=task.benchmark_id,
                benchmark_revision=task.benchmark_revision,
                upstream_task_id=task.upstream_task_id,
                task_specification=task.task_specification,
                specification_sha256=task.specification_sha256,
            )
        )
    for model_record in model_records:
        registry.put_record(model_record)
    for prompt_record in prompt_records:
        registry.put_record(prompt_record)
    source_index = _build_source_initial_index(
        configuration, {task.task_record_id for task in scope.tasks}
    )
    source_index_path = registry.root / "source_initial_candidates.json"
    _write_once_bytes(
        source_index_path,
        (json.dumps(source_index, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    hashes = role_separated_configuration_hashes(configuration_path, configuration)
    launch = {
        "schema_version": "role-separated-launch-v1",
        "run_id": run_id,
        "run_started_at": started_at.isoformat(),
        "git_commit": git_commit,
        "configuration_path": str(configuration_path),
        "configuration_versions": {
            "campaign": configuration.configuration_version,
            "schedule": configuration.schedule_version,
            "scope": scope.scope_version,
            "inference": inference.configuration_version,
        },
        "configuration_hashes": hashes,
        "prompt_version": prompts.prompt_set_version,
        "prompt_hashes": {
            template.stage.value: template.template_sha256 for template in prompts.templates
        },
        "scope_version": scope.scope_version,
        "scope_sha256": scope.content_sha256,
        "source_run_id": configuration.source_run_id,
        "source_manifest_record_id": configuration.source_manifest_record_id,
        "source_initial_index_path": str(source_index_path),
        "source_initial_index_sha256": sha256_file(source_index_path),
        "decision_adjudication_id": configuration.decision_adjudication_id,
        "model_configuration_record_ids": {
            model_id: record.record_id
            for model_id, record in zip(configuration.model_order, model_records, strict=True)
        },
    }
    _write_once_bytes(
        registry.root / "launch.json",
        (json.dumps(launch, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    _put_target_manifest(
        registry=registry,
        configuration=configuration,
        launch=launch,
        status=RunStatus.IN_PROGRESS,
        git_commit=git_commit,
    )
    return registry, launch


def _load_target(
    configuration_path: Path, run_id: str
) -> tuple[RoleSeparatedCampaignConfiguration, LocalRunRegistry, dict[str, Any]]:
    configuration = load_role_separated_configuration(configuration_path)
    registry = LocalRunRegistry(REGISTRY_ROOT / run_id)
    launch_path = registry.root / "launch.json"
    if not launch_path.is_file():
        raise RuntimeError("role-separated target registry or launch metadata is missing")
    launch = json.loads(launch_path.read_text(encoding="utf-8"))
    if launch.get("run_id") != run_id or launch.get("source_run_id") != configuration.source_run_id:
        raise RuntimeError("target launch lineage differs from the frozen configuration")
    current_hashes = role_separated_configuration_hashes(configuration_path, configuration)
    if launch.get("configuration_hashes") != current_hashes:
        raise RuntimeError("target configuration hashes differ from the frozen launch")
    source_index_path = Path(launch["source_initial_index_path"])
    if sha256_file(source_index_path) != launch["source_initial_index_sha256"]:
        raise RuntimeError("source initial candidate index failed integrity validation")
    return configuration, registry, launch


def _phase_completion_path(
    registry: LocalRunRegistry, phase: CampaignPhase, attempt_id: str
) -> Path:
    return registry.root / "phase_completions" / phase.value / f"{attempt_id}.json"


def _latest_phase_completion_path(registry: LocalRunRegistry, phase: CampaignPhase) -> Path:
    pointer = registry.root / "phase_completions" / phase.value / "latest.json"
    payload = json.loads(pointer.read_text(encoding="utf-8"))
    path = Path(payload["completion_path"])
    if not path.is_file():
        raise RuntimeError(f"phase completion pointer is broken: {phase.value}")
    if sha256_file(path) != payload.get("completion_sha256"):
        raise RuntimeError(f"phase completion hash mismatch: {phase.value}")
    return path


def _require_phase_prerequisites(registry: LocalRunRegistry, phase: CampaignPhase) -> None:
    for prerequisite in PHASE_PREREQUISITES[phase]:
        try:
            path = _latest_phase_completion_path(registry, prerequisite)
        except FileNotFoundError:
            raise RuntimeError(
                f"{phase.value} requires validated completion of {prerequisite.value}"
            ) from None
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("validation_result") != "passed":
            raise RuntimeError(f"prerequisite is not validated: {prerequisite.value}")


def _seed_artifacts(
    *,
    configuration: RoleSeparatedCampaignConfiguration,
    registry: LocalRunRegistry,
    launch: dict[str, Any],
    model_id: str,
    task_ids: tuple[str, ...],
) -> tuple[dict[str, TaskArtifacts], LocalRunRegistry]:
    source_registry = LocalRunRegistry(configuration.source_registry_path)
    source_index = json.loads(
        Path(launch["source_initial_index_path"]).read_text(encoding="utf-8")
    )[model_id]
    seeds = {task_id: TaskArtifacts() for task_id in task_ids}
    initial_to_task: dict[str, str] = {}
    for task_id, candidate_id in source_index.items():
        record = source_registry.load_record(CandidateRecord.RECORD_TYPE, candidate_id)
        if (
            not isinstance(record, CandidateRecord)
            or record.candidate_kind is not CandidateKind.INITIAL
        ):
            raise RuntimeError("source initial index points to a non-initial record")
        seeds[task_id].initial = record
        initial_to_task[record.record_id] = task_id
    for record in registry.records_of_type(CritiqueArtifact.RECORD_TYPE):
        if not isinstance(record, CritiqueArtifact):
            continue
        task_id = initial_to_task.get(record.initial_candidate.candidate_record_id)
        if task_id is None:
            continue
        if seeds[task_id].critique is not None:
            raise RuntimeError("target registry contains duplicate Critique artifacts")
        seeds[task_id].critique = record
    for record in registry.records_of_type(RevisionPlanArtifact.RECORD_TYPE):
        if not isinstance(record, RevisionPlanArtifact):
            continue
        task_id = initial_to_task.get(record.initial_candidate.candidate_record_id)
        if task_id is None:
            continue
        if seeds[task_id].plan is not None:
            raise RuntimeError("target registry contains duplicate Planning artifacts")
        seeds[task_id].plan = record
    return seeds, source_registry


def _model_worker(arguments: argparse.Namespace) -> int:
    attempt = arguments.attempt_directory.resolve()
    configuration, registry, launch = _load_target(
        arguments.campaign_configuration.resolve(), arguments.run_id
    )
    phase = CampaignPhase(arguments.phase)
    scope = load_public_scope(registry.root / "scope.json").to_campaign_scope()
    inference = load_primary_inference_configuration(
        configuration.resolve(configuration.inference_configuration)
    )
    prompts = load_prompt_manifest(configuration.resolve(configuration.prompt_configuration))
    model_id = str(arguments.model_id)
    seeds, source_registry = _seed_artifacts(
        configuration=configuration,
        registry=registry,
        launch=launch,
        model_id=model_id,
        task_ids=tuple(task.task_record_id for task in scope.tasks),
    )
    vllm = importlib.import_module("vllm")
    llm = vllm.LLM(
        model=str(MODEL_ROOT / model_id),
        tensor_parallel_size=inference.tensor_parallel_size,
        dtype=inference.dtype,
        quantization=None,
        tokenizer_mode=inference.tokenizer_mode,
        trust_remote_code=inference.trust_remote_code,
        seed=inference.decoding.seed,
        gpu_memory_utilization=inference.gpu_memory_utilization,
        max_model_len=inference.max_model_len,
        max_num_seqs=configuration.batch_size,
        disable_log_stats=True,
    )
    from self_refinement.inference.vllm_backend import VllmResidentBackend

    backend = VllmResidentBackend(
        model_id=model_id, llm=llm, sampling_params_factory=vllm.SamplingParams
    )
    executor = ModelCallExecutor(registry=registry, backend=backend, configuration=inference)

    def progress(report: PhaseReport) -> None:
        _update_status(
            attempt,
            state="running",
            phase=phase.value,
            current_phase=_phase_payload(report),
            completed_task_units=(arguments.model_index * len(scope.tasks) + report.terminal),
        )

    runner = ProtocolCampaignRunner(
        context=CampaignContext(
            study_version=configuration.study_version,
            run_id=arguments.run_id,
            producer=PRODUCER,
            model_id=model_id,
            model_configuration_record_id=launch["model_configuration_record_ids"][model_id],
        ),
        scope=scope,
        registry=registry,
        prompts=prompts,
        executor=executor,
        batch_size=configuration.batch_size,
        retry_failed=arguments.retry_failed,
        progress_callback=progress,
        seed_artifacts=seeds,
        source_registry=source_registry,
    )
    report = runner.run_phase(phase)
    runner.validate_artifact_lineage()
    _atomic_json(
        arguments.output_path,
        {
            "schema_version": "role-separated-model-phase-result-v1",
            "run_id": arguments.run_id,
            "model_id": model_id,
            "phase": phase.value,
            "result": _phase_payload(report),
            "validation_result": "passed",
        },
    )
    return 0


def _phase_worker(arguments: argparse.Namespace) -> int:
    attempt = arguments.attempt_directory.resolve()
    configuration_path = arguments.campaign_configuration.resolve()
    phase = CampaignPhase(arguments.phase)
    completed_models: list[str] = []
    current_model: str | None = None
    try:
        configuration, registry, launch = _load_target(configuration_path, arguments.run_id)
        _source_validation(configuration)
        _require_phase_prerequisites(registry, phase)
        if _git_changes():
            raise RuntimeError("each phase must start from clean committed execution inputs")
        phase_git_commit = _git_commit()
        scope = load_public_scope(registry.root / "scope.json")
        _update_status(
            attempt,
            state="running",
            phase="preparing_models",
            git_commit=phase_git_commit,
        )
        environment = _worker_environment()
        results: list[dict[str, Any]] = []
        for index, model_id in enumerate(configuration.model_order):
            current_model = model_id
            _require_clear_gpus()
            _update_status(
                attempt,
                phase="loading_model",
                current_model_id=model_id,
                current_model_index=index + 1,
                completed_models=len(completed_models),
            )
            output = attempt / "results" / f"{model_id}.json"
            command = [
                str(ENVIRONMENT_PYTHON),
                str(Path(__file__).resolve()),
                "--model-worker",
                "--attempt-directory",
                str(attempt),
                "--campaign-configuration",
                str(configuration_path),
                "--run-id",
                arguments.run_id,
                "--phase",
                phase.value,
                "--model-id",
                model_id,
                "--model-index",
                str(index),
                "--output-path",
                str(output),
            ]
            if arguments.retry_failed:
                command.append("--retry-failed")
            subprocess.run(command, check=True, cwd=PROJECT_ROOT, env=environment)
            result = json.loads(output.read_text(encoding="utf-8"))
            if result.get("validation_result") != "passed":
                raise RuntimeError(f"model phase validation failed: {model_id}")
            results.append(result)
            completed_models.append(model_id)
            _update_status(
                attempt,
                completed_models=len(completed_models),
                completed_task_units=len(completed_models) * len(scope.tasks),
            )
        totals = {
            key: sum(int(result["result"][key]) for result in results)
            for key in ("total", "completed", "reused", "failed", "blocked", "terminal")
        }
        summary = {
            "schema_version": "role-separated-phase-summary-v1",
            "attempt_id": attempt.name,
            "run_id": arguments.run_id,
            "phase": phase.value,
            "stage": PHASE_LABELS[phase],
            "git_commit": phase_git_commit,
            "models": list(configuration.model_order),
            "task_count": len(scope.tasks),
            "totals": totals,
            "model_results": [
                str(attempt / "results" / f"{item}.json") for item in completed_models
            ],
            "validation_result": "passed",
        }
        _atomic_json(attempt / "summary.json", summary)
        completion = {
            **summary,
            "summary_sha256": sha256_file(attempt / "summary.json"),
            "configuration_hashes": launch["configuration_hashes"],
        }
        completion_path = _phase_completion_path(registry, phase, attempt.name)
        _write_once_bytes(
            completion_path,
            (json.dumps(completion, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
        _atomic_json(
            completion_path.parent / "latest.json",
            {
                "attempt_id": attempt.name,
                "completion_path": str(completion_path),
                "completion_sha256": sha256_file(completion_path),
            },
        )
        manifest = _put_target_manifest(
            registry=registry,
            configuration=configuration,
            launch=launch,
            status=(
                RunStatus.COMPLETED
                if phase is CampaignPhase.CPR_REVISION
                else RunStatus.IN_PROGRESS
            ),
            git_commit=phase_git_commit,
        )
        _update_status(
            attempt,
            state="completed",
            phase="completed",
            ended_at=_utc_now(),
            exit_code=0,
            validation_result="passed",
            completed_models=len(completed_models),
            completed_task_units=len(configuration.model_order) * len(scope.tasks),
            current_model_id=None,
            terminal_manifest_record_id=manifest.record_id,
        )
        return 0
    except BaseException as error:
        try:
            configuration, registry, launch = _load_target(configuration_path, arguments.run_id)
            manifest = _put_target_manifest(
                registry=registry,
                configuration=configuration,
                launch=launch,
                status=RunStatus.FAILED,
                git_commit=_git_commit(),
                failure_summary=f"{type(error).__name__}: {error}",
            )
            manifest_id: str | None = manifest.record_id
        except BaseException:
            manifest_id = None
        _update_status(
            attempt,
            state="failed",
            phase="failed",
            ended_at=_utc_now(),
            exit_code=1,
            validation_result="failed",
            completed_models=len(completed_models),
            current_model_id=current_model,
            error_type=type(error).__name__,
            error_message=str(error),
            terminal_manifest_record_id=manifest_id,
        )
        print(f"failed: {type(error).__name__}: {error}", file=sys.stderr, flush=True)
        return 1


def _phase_base_status(
    *, attempt: Path, run_id: str, phase: CampaignPhase, log_path: Path, parent: str | None
) -> dict[str, Any]:
    now = _utc_now()
    return {
        "schema_version": "role-separated-phase-status-v1",
        "job_kind": "role-separated-phase",
        "attempt_id": attempt.name,
        "attempt_directory": str(attempt),
        "run_id": run_id,
        "role_phase": phase.value,
        "state": "starting",
        "phase": "launching",
        "started_at": now,
        "updated_at": now,
        "pid": None,
        "cwd": str(PROJECT_ROOT),
        "git_commit": _git_commit(),
        "log_path": str(log_path),
        "output_paths": [str(REGISTRY_ROOT / run_id), str(attempt / "summary.json")],
        "parent_sequence_attempt_id": parent,
        "expected_models": 6,
        "completed_models": 0,
        "expected_task_units": 6 * 1677,
        "completed_task_units": 0,
    }


def _create_phase_attempt(
    *,
    attempt_id: str,
    run_id: str,
    phase: CampaignPhase,
    parent: str | None,
    retry_failed: bool,
    configuration_path: Path,
) -> tuple[Path, list[str]]:
    _safe_attempt_id(attempt_id, "role-phase-")
    attempt = PHASE_ROOT / attempt_id
    attempt.mkdir(parents=True, exist_ok=False)
    log_path = attempt / "run.log"
    log_path.touch(exist_ok=False)
    status = _phase_base_status(
        attempt=attempt, run_id=run_id, phase=phase, log_path=log_path, parent=parent
    )
    status["retry_failed"] = retry_failed
    status["campaign_configuration"] = str(configuration_path)
    _write_status(attempt, status)
    _atomic_json(PHASE_ROOT / "latest.json", {"attempt_directory": str(attempt)})
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--phase-worker",
        "--attempt-directory",
        str(attempt),
        "--campaign-configuration",
        str(configuration_path),
        "--run-id",
        run_id,
        "--phase",
        phase.value,
    ]
    if retry_failed:
        command.append("--retry-failed")
    _atomic_json(attempt / "command.json", {"command": command, "cwd": str(PROJECT_ROOT)})
    return attempt, command


def _sequence_worker(arguments: argparse.Namespace) -> int:
    attempt = arguments.attempt_directory.resolve()
    completed: list[str] = []
    current_phase: CampaignPhase | None = None
    try:
        for index, phase in enumerate(ROLE_SEPARATED_PHASE_ORDER, start=1):
            current_phase = phase
            sequence_label = attempt.name.removeprefix("role-sequence-")
            child_id = f"role-phase-{sequence_label}-{index:02d}-{phase.value}"
            child, command = _create_phase_attempt(
                attempt_id=child_id,
                run_id=arguments.run_id,
                phase=phase,
                parent=attempt.name,
                retry_failed=arguments.retry_failed,
                configuration_path=arguments.campaign_configuration.resolve(),
            )
            _update_status(
                attempt,
                state="running",
                phase=phase.value,
                current_phase_attempt_id=child.name,
                current_phase_status_path=str(_status_path(child)),
                current_phase_log_path=str(child / "run.log"),
                completed_phases=list(completed),
            )
            with (child / "run.log").open("ab", buffering=0) as log:
                process = subprocess.Popen(
                    command,
                    stdin=subprocess.DEVNULL,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    cwd=PROJECT_ROOT,
                )
                _update_status(child, pid=process.pid)
                return_code = process.wait()
            child_status = json.loads(_status_path(child).read_text(encoding="utf-8"))
            if (
                return_code != 0
                or child_status.get("state") != "completed"
                or child_status.get("validation_result") != "passed"
            ):
                raise RuntimeError(f"phase attempt did not validate: {child.name}")
            completed.append(phase.value)
            _update_status(attempt, completed_phases=list(completed))
        validation_command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--validate",
            "--campaign-configuration",
            str(arguments.campaign_configuration.resolve()),
            "--resume-run-id",
            arguments.run_id,
        ]
        subprocess.run(validation_command, check=True, cwd=PROJECT_ROOT)
        summary = {
            "schema_version": "role-separated-sequence-summary-v1",
            "attempt_id": attempt.name,
            "run_id": arguments.run_id,
            "phase_order": [phase.value for phase in ROLE_SEPARATED_PHASE_ORDER],
            "completed_phases": completed,
            "run_validation_path": str(REGISTRY_ROOT / arguments.run_id / "validation.json"),
            "validation_result": "passed",
        }
        _atomic_json(attempt / "summary.json", summary)
        _update_status(
            attempt,
            state="completed",
            phase="completed",
            ended_at=_utc_now(),
            exit_code=0,
            validation_result="passed",
            completed_phases=completed,
            current_phase_attempt_id=None,
        )
        return 0
    except BaseException as error:
        _update_status(
            attempt,
            state="failed",
            phase="failed",
            ended_at=_utc_now(),
            exit_code=1,
            validation_result="failed",
            completed_phases=completed,
            failed_phase=None if current_phase is None else current_phase.value,
            error_type=type(error).__name__,
            error_message=str(error),
        )
        print(f"failed: {type(error).__name__}: {error}", file=sys.stderr, flush=True)
        return 1


def _assert_no_active(root: Path) -> None:
    latest = root / "latest.json"
    if not latest.is_file():
        return
    attempt = Path(json.loads(latest.read_text(encoding="utf-8"))["attempt_directory"])
    status_path = _status_path(attempt)
    if not status_path.is_file():
        return
    status = json.loads(status_path.read_text(encoding="utf-8"))
    pid = status.get("pid")
    if status.get("state") in {"starting", "running"} and isinstance(pid, int):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        raise RuntimeError(f"active role-separated attempt already exists: {attempt}")


def _start_sequence(arguments: argparse.Namespace) -> int:
    configuration_path = arguments.campaign_configuration.resolve()
    preflight = _preflight(
        configuration_path, require_execution_enabled=True, require_clear_gpu=True
    )
    _assert_no_active(SEQUENCE_ROOT)
    _assert_no_active(PHASE_ROOT)
    _safe_attempt_id(arguments.attempt_id, "role-sequence-")
    attempt = SEQUENCE_ROOT / arguments.attempt_id
    attempt.mkdir(parents=True, exist_ok=False)
    started = datetime.now(UTC)
    git_commit = _git_commit()
    run_id = make_run_id("study-v0.3.0", started, arguments.attempt_id)
    _, launch = _initialize_target(
        configuration_path, run_id=run_id, started_at=started, git_commit=git_commit
    )
    log_path = attempt / "run.log"
    log_path.touch(exist_ok=False)
    status = {
        "schema_version": "role-separated-sequence-status-v1",
        "job_kind": "role-separated-sequence",
        "attempt_id": attempt.name,
        "attempt_directory": str(attempt),
        "run_id": run_id,
        "state": "starting",
        "phase": "launching",
        "started_at": started.isoformat(),
        "updated_at": started.isoformat(),
        "pid": None,
        "cwd": str(PROJECT_ROOT),
        "git_commit": git_commit,
        "log_path": str(log_path),
        "output_paths": [str(REGISTRY_ROOT / run_id), str(attempt / "summary.json")],
        "expected_phases": [phase.value for phase in ROLE_SEPARATED_PHASE_ORDER],
        "completed_phases": [],
        "campaign_configuration": str(configuration_path),
        "configuration_hashes": launch["configuration_hashes"],
        "preflight": preflight,
    }
    _write_status(attempt, status)
    _atomic_json(SEQUENCE_ROOT / "latest.json", {"attempt_directory": str(attempt)})
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--sequence-worker",
        "--attempt-directory",
        str(attempt),
        "--campaign-configuration",
        str(configuration_path),
        "--run-id",
        run_id,
    ]
    if arguments.retry_failed:
        command.append("--retry-failed")
    _atomic_json(attempt / "command.json", {"command": command, "cwd": str(PROJECT_ROOT)})
    with log_path.open("ab", buffering=0) as log:
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            cwd=PROJECT_ROOT,
            start_new_session=True,
        )
    if process.poll() is not None:
        raise RuntimeError(f"sequence worker exited during launch: {process.returncode}")
    _update_status(attempt, pid=process.pid)
    print(
        json.dumps(
            {
                "attempt_id": attempt.name,
                "run_id": run_id,
                "pid": process.pid,
                "status_path": str(_status_path(attempt)),
                "log_path": str(log_path),
                "status_command": (
                    ".venv/bin/python scripts/run_role_separated_campaign.py --status"
                ),
                "count_command": ".venv/bin/python scripts/run_role_separated_campaign.py --count",
                "tail_command": f"tail -f {log_path}",
            },
            indent=2,
        )
    )
    return 0


def _start_phase(arguments: argparse.Namespace) -> int:
    if not arguments.resume_run_id or not arguments.phase:
        raise ValueError("standalone phase start requires --resume-run-id and --phase")
    configuration_path = arguments.campaign_configuration.resolve()
    _preflight(configuration_path, require_execution_enabled=True, require_clear_gpu=True)
    _assert_no_active(PHASE_ROOT)
    phase = CampaignPhase(arguments.phase)
    configuration, registry, _ = _load_target(configuration_path, arguments.resume_run_id)
    if phase not in configuration.phase_order:
        raise ValueError("phase is not part of the role-separated campaign")
    _require_phase_prerequisites(registry, phase)
    attempt, command = _create_phase_attempt(
        attempt_id=arguments.attempt_id,
        run_id=arguments.resume_run_id,
        phase=phase,
        parent=None,
        retry_failed=arguments.retry_failed,
        configuration_path=configuration_path,
    )
    with (attempt / "run.log").open("ab", buffering=0) as log:
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            cwd=PROJECT_ROOT,
            start_new_session=True,
        )
    if process.poll() is not None:
        raise RuntimeError(f"phase worker exited during launch: {process.returncode}")
    _update_status(attempt, pid=process.pid)
    print(
        json.dumps(
            {
                "attempt_id": attempt.name,
                "run_id": arguments.resume_run_id,
                "pid": process.pid,
                "status_path": str(_status_path(attempt)),
                "log_path": str(attempt / "run.log"),
            },
            indent=2,
        )
    )
    return 0


def _latest_attempt(root: Path) -> Path:
    return Path(json.loads((root / "latest.json").read_text(encoding="utf-8"))["attempt_directory"])


def _show_status(*, count_only: bool) -> int:
    sequence = _latest_attempt(SEQUENCE_ROOT)
    status = json.loads(_status_path(sequence).read_text(encoding="utf-8"))
    child_status: dict[str, Any] | None = None
    child_path = status.get("current_phase_status_path")
    if isinstance(child_path, str) and Path(child_path).is_file():
        child_status = json.loads(Path(child_path).read_text(encoding="utf-8"))
    if count_only:
        completed_phases = len(status.get("completed_phases", []))
        phase_name = status.get("phase", "-")
        base = f"{status['state']} | phases {completed_phases}/4 | current {phase_name}"
        if child_status is not None:
            completed = int(child_status.get("completed_task_units", 0))
            expected = int(child_status.get("expected_task_units", 0))
            percent = 100 * completed / expected if expected else 0.0
            model = child_status.get("current_model_id") or "-"
            child_phase = child_status.get("phase", "-")
            detail = f"{completed}/{expected} ({percent:.2f}%) | model {model} | {child_phase}"
            current = child_status.get("current_phase")
            if isinstance(current, dict):
                detail += (
                    f" | failed {current.get('failed', 0)} blocked {current.get('blocked', 0)}"
                )
            print(f"{base} | {detail}")
        else:
            print(base)
        return 0
    for payload in (status, child_status):
        if payload is None:
            continue
        log_path = Path(payload["log_path"])
        if log_path.is_file():
            stat = log_path.stat()
            payload["observation"] = {
                "log_size_bytes": stat.st_size,
                "log_modified_at": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
            }
    print(json.dumps({"sequence": status, "current_phase": child_status}, indent=2, sort_keys=True))
    return 0


def _validate_run(arguments: argparse.Namespace) -> int:
    run_id = arguments.resume_run_id
    if not run_id:
        sequence = _latest_attempt(SEQUENCE_ROOT)
        run_id = json.loads(_status_path(sequence).read_text(encoding="utf-8"))["run_id"]
    configuration, registry, launch = _load_target(
        arguments.campaign_configuration.resolve(), run_id
    )
    completions: dict[str, Any] = {}
    for phase in configuration.phase_order:
        path = _latest_phase_completion_path(registry, phase)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("validation_result") != "passed":
            raise RuntimeError(f"phase completion is not validated: {phase.value}")
        completions[phase.value] = payload
    calls = [
        record
        for record in registry.records_of_type(ModelCallRecord.RECORD_TYPE)
        if isinstance(record, ModelCallRecord)
    ]
    allowed_stages = {
        Stage.CRITIQUE_GENERATION,
        Stage.CRITIQUE_CONDITIONED_REVISION,
        Stage.REVISION_PLANNING,
        Stage.PLAN_CONDITIONED_REVISION,
    }
    if any(call.stage not in allowed_stages for call in calls):
        raise RuntimeError("target registry contains a model call outside the four new phases")
    raw_count = 0
    for call in calls:
        if call.raw_response is not None:
            registry.read_raw(call.raw_response)
            raw_count += 1
    manifest = _latest_manifest(registry)
    if (
        manifest.status is not RunStatus.COMPLETED
        or manifest.parent_run_id != configuration.source_run_id
    ):
        raise RuntimeError("role-separated run manifest is not completed with source lineage")
    validation = {
        "schema_version": "role-separated-run-validation-v1",
        "validation_result": "passed",
        "run_id": run_id,
        "source_run_id": configuration.source_run_id,
        "terminal_manifest_record_id": manifest.record_id,
        "phase_completions": completions,
        "model_call_records": len(calls),
        "raw_responses_validated": raw_count,
        "configuration_hashes": launch["configuration_hashes"],
        "content_sha256": sha256_json(
            {"run_id": run_id, "calls": sorted(item.record_id for item in calls)}
        ),
    }
    path = registry.root / "validation.json"
    _atomic_json(path, validation)
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--start-sequence", action="store_true")
    mode.add_argument("--start-phase", action="store_true")
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--status", action="store_true")
    mode.add_argument("--count", action="store_true")
    mode.add_argument("--validate", action="store_true")
    mode.add_argument("--show-run-id", action="store_true")
    mode.add_argument("--sequence-worker", action="store_true", help=argparse.SUPPRESS)
    mode.add_argument("--phase-worker", action="store_true", help=argparse.SUPPRESS)
    mode.add_argument("--model-worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--attempt-id", default="role-sequence-primary-20260806-r1")
    parser.add_argument("--resume-run-id")
    parser.add_argument("--phase", choices=[phase.value for phase in ROLE_SEPARATED_PHASE_ORDER])
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument(
        "--campaign-configuration",
        type=Path,
        default=DEFAULT_ROLE_SEPARATED_CONFIGURATION_PATH,
    )
    parser.add_argument("--attempt-directory", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--run-id", help=argparse.SUPPRESS)
    parser.add_argument("--model-id", help=argparse.SUPPRESS)
    parser.add_argument("--model-index", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--output-path", type=Path, help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    if arguments.status or arguments.count:
        return _show_status(count_only=arguments.count)
    if arguments.show_run_id:
        attempt = _latest_attempt(SEQUENCE_ROOT)
        print(json.loads(_status_path(attempt).read_text(encoding="utf-8"))["run_id"])
        return 0
    if arguments.preflight:
        print(
            json.dumps(
                _preflight(
                    arguments.campaign_configuration.resolve(),
                    require_execution_enabled=False,
                    require_clear_gpu=False,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if arguments.validate:
        return _validate_run(arguments)
    if arguments.start_sequence:
        return _start_sequence(arguments)
    if arguments.start_phase:
        return _start_phase(arguments)
    if arguments.sequence_worker:
        return _sequence_worker(arguments)
    if arguments.phase_worker:
        return _phase_worker(arguments)
    return _model_worker(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
