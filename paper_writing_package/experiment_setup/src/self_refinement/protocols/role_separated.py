"""Frozen configuration and source-lineage checks for the role-separated follow-up."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator, model_validator

from self_refinement.hashing import sha256_file
from self_refinement.protocols.runner import CampaignPhase

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ROLE_SEPARATED_CONFIGURATION_PATH = (
    PROJECT_ROOT / "configs" / "experiments" / "role_separated_campaign.toml"
)
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
ROLE_SEPARATED_PHASE_ORDER: tuple[CampaignPhase, ...] = (
    CampaignPhase.SHARED_CRITIQUE,
    CampaignPhase.CR_REVISION,
    CampaignPhase.SHARED_PLAN,
    CampaignPhase.CPR_REVISION,
)


class RoleSeparatedCampaignConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_version: Literal["role-separated-campaign-configuration-v1"]
    configuration_version: str = Field(min_length=3)
    study_version: Literal["study-v0.3.0"]
    schedule_version: str = Field(min_length=3)
    execution_gate: Literal["blocked", "enabled"]
    batch_size: PositiveInt
    scope_configuration: str
    inference_configuration: str
    prompt_configuration: str
    model_manifest: str
    source_run_id: str = Field(pattern=r"^run_[0-9a-f]{24}$")
    source_attempt_id: str = Field(min_length=3)
    source_manifest_record_id: str = Field(pattern=r"^run_manifest_[0-9a-f]{24}$")
    source_validation_path: str
    source_validation_sha256: Sha256
    decision_adjudication_id: str = Field(min_length=3)
    decision_adjudication_validation_path: str
    decision_adjudication_validation_sha256: Sha256
    phase_order: tuple[CampaignPhase, ...]
    model_order: tuple[str, ...]

    @field_validator("phase_order", mode="before")
    @classmethod
    def freeze_phases(cls, value: object) -> object:
        if isinstance(value, list):
            return tuple(CampaignPhase(item) for item in value)
        return value

    @field_validator("model_order", mode="before")
    @classmethod
    def freeze_models(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def validate_contract(self) -> Self:
        if self.phase_order != ROLE_SEPARATED_PHASE_ORDER:
            raise ValueError(
                "role-separated phase order must be Critique, CR Revision, Planning, CPR Revision"
            )
        if len(self.model_order) != 6 or len(set(self.model_order)) != 6:
            raise ValueError("role-separated campaign requires the six frozen models")
        for value in (
            self.scope_configuration,
            self.inference_configuration,
            self.prompt_configuration,
            self.model_manifest,
            self.source_validation_path,
            self.decision_adjudication_validation_path,
        ):
            path = Path(value)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("configuration paths must be repository-relative")
        return self

    def resolve(self, value: str) -> Path:
        return (PROJECT_ROOT / value).resolve()

    @property
    def source_registry_path(self) -> Path:
        return PROJECT_ROOT / "runs" / "registry" / self.source_run_id


def load_role_separated_configuration(
    path: Path = DEFAULT_ROLE_SEPARATED_CONFIGURATION_PATH,
) -> RoleSeparatedCampaignConfiguration:
    with path.open("rb") as handle:
        payload: dict[str, Any] = tomllib.load(handle)
    return RoleSeparatedCampaignConfiguration.model_validate(payload)


def role_separated_configuration_hashes(
    path: Path, configuration: RoleSeparatedCampaignConfiguration
) -> dict[str, str]:
    return {
        "campaign": sha256_file(path),
        "scope": sha256_file(configuration.resolve(configuration.scope_configuration)),
        "inference": sha256_file(configuration.resolve(configuration.inference_configuration)),
        "prompts": sha256_file(configuration.resolve(configuration.prompt_configuration)),
        "models": sha256_file(configuration.resolve(configuration.model_manifest)),
        "source_validation": sha256_file(
            configuration.resolve(configuration.source_validation_path)
        ),
        "decision_adjudication_validation": sha256_file(
            configuration.resolve(configuration.decision_adjudication_validation_path)
        ),
    }
