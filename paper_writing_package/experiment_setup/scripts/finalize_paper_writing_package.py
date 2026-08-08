#!/usr/bin/env python3
"""Build the allowlisted final analysis paper-writing package."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis_tools.common import read_json, sha256_file  # noqa: E402
from self_refinement.packaging.paper_package import (  # noqa: E402
    validate_package,
    validate_package_id,
)


def _copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _copy_tree(source: Path, target: Path) -> None:
    shutil.copytree(
        source,
        target,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )


def _gzip(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with (
        source.open("rb") as input_handle,
        target.open("wb") as raw,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as output_handle,
    ):
        shutil.copyfileobj(input_handle, output_handle, length=1024 * 1024)


def _entries(root: Path) -> list[dict[str, Any]]:
    excluded = {"package_manifest.json", "CHECKSUMS.sha256", "validation.json"}
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name not in excluded
    ]


def build(
    dataset: Path,
    analysis: Path,
    assets: Path,
    target: Path,
    *,
    package_id: str,
    exploratory: Path | None = None,
) -> Path:
    validate_package_id(package_id)
    manifest = read_json(dataset / "manifest.json")
    if (
        manifest.get("paper_facing") is not True
        or read_json(dataset / "validation.json").get("validation_result") != "passed"
    ):
        raise RuntimeError("processed dataset is not accepted and validated")
    if read_json(assets / "validation.json").get("validation_result") != "passed":
        raise RuntimeError("paper assets are not validated")
    for rq in ("rq1", "rq2", "rq3", "rq4"):
        if read_json(analysis / rq / "validation.json").get("validation_result") != "passed":
            raise RuntimeError(f"{rq} is not validated")
    exploratory_manifest: dict[str, Any] | None = None
    if exploratory is not None:
        exploratory_manifest = read_json(exploratory / "manifest.json")
        if (
            exploratory_manifest.get("result_status") != "exploratory_post_hoc"
            or read_json(exploratory / "validation.json").get("validation_result") != "passed"
        ):
            raise RuntimeError("exploratory supplement is not labeled and validated")
    git_status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    if git_status:
        raise RuntimeError("final package requires a clean committed worktree")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    build_root = target.parent / f".{target.name}.final-building"
    backup = target.parent / f".{target.name}.previous"
    if build_root.exists() or backup.exists():
        raise RuntimeError("package build or backup path already exists")
    build_root.mkdir(parents=True)
    for section in (
        "study_design",
        "experiment_setup",
        "data",
        "process_record",
        "provenance",
        "source",
        "results",
    ):
        (build_root / section).mkdir()

    for name in (
        "README.md",
        "EXPERIMENT_EXECUTION_GUIDELINES.md",
        "EXPERIMENT_RUNBOOK.md",
        "pyproject.toml",
        "requirements.lock",
        "requirements-bigcodebench.lock",
        "requirements-vllm.lock",
    ):
        _copy(ROOT / name, build_root / "study_design" / name)
    _copy_tree(ROOT / "documents", build_root / "study_design/documents")
    _copy_tree(ROOT / "analysis_tools", build_root / "experiment_setup/analysis_tools")
    for script in ("finalize_paper_writing_package.py",):
        _copy(ROOT / "scripts" / script, build_root / "experiment_setup/scripts" / script)
    for config in ("configs/analysis",):
        source = ROOT / config
        if source.exists():
            _copy_tree(source, build_root / "experiment_setup" / config)
    _copy(
        ROOT / "analysis_tools/analysis_config.toml",
        build_root / "experiment_setup/analysis_config.toml",
    )

    processed_target = build_root / "data/canonical_processed"
    for name in ("manifest.json", "validation.json", "data_dictionary.json"):
        _copy(dataset / name, processed_target / name)
    for name in ("outcomes.jsonl", "stage_calls.jsonl", "derived_selections.jsonl"):
        _gzip(dataset / name, processed_target / f"{name}.gz")
    _copy_tree(analysis, build_root / "results/rq_analysis")
    _copy_tree(assets, build_root / "results/paper_assets")
    if exploratory is not None:
        _copy_tree(exploratory, build_root / "results/exploratory_mechanism")
    _copy(
        ROOT / "documents/09_results_analysis.md", build_root / "results/FINAL_RESULTS_ANALYSIS.md"
    )

    source_locations = {
        "schema_version": "final-result-source-locations-v1",
        "source_runs": manifest["source_runs"],
        "working_registry_root": "runs/registry/<run_id>",
        "processed_dataset_id": manifest["dataset_id"],
        "source_files": manifest["source_files"],
        "raw_registry_bytes_included": False,
        "note": (
            "Raw registries remain in immutable working storage; the complete canonical processed "
            "dataset is included in deterministic gzip form."
        ),
    }
    (build_root / "provenance/source_locations.json").write_text(
        json.dumps(source_locations, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    availability = {
        "schema_version": "paper-package-availability-v1",
        "package_stage": "final_results",
        "validated_primary_inference_raw": False,
        "validated_decision_resolution": True,
        "accepted_reference_timing_raw": False,
        "candidate_evaluation_raw": False,
        "canonical_processed_dataset": True,
        "rq_results": True,
        "paper_tables": True,
        "paper_figures": False,
        "paper_figure_source_data": True,
        "exploratory_post_hoc_results": exploratory is not None,
    }
    (build_root / "provenance/availability.json").write_text(
        json.dumps(availability, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (build_root / "provenance/paper_result_manifest.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(
            (
                "result_id",
                "research_question",
                "processed_data",
                "analysis_output",
                "paper_asset",
                "validation_status",
            )
        )
        for rq in ("rq1", "rq2", "rq3", "rq4"):
            writer.writerow(
                (
                    rq,
                    rq.upper(),
                    "data/canonical_processed/outcomes.jsonl.gz",
                    f"results/rq_analysis/{rq}",
                    "results/paper_assets",
                    "passed",
                )
            )
    exploratory_id = (
        str(exploratory_manifest["analysis_id"])
        if exploratory_manifest is not None
        else "not included"
    )
    readme = f"""# Final paper-writing package

This allowlisted internal package contains the accepted `study-v0.4.0` design, complete compressed
canonical processed data, validated RQ1-RQ4 outputs, compact paper table/chart source CSVs, analysis
code, and the final findings narrative.

- Dataset: `{manifest["dataset_id"]}` ({manifest["row_counts"]["outcomes"]:,} outcome rows)
- RQ analysis: `{read_json(analysis / "rq1/manifest.json")["analysis_id"]}`
- Paper assets: `{assets.name}`
- Exploratory supplement: `{exploratory_id}`
- Source commit: `{commit}`

The three `.jsonl.gz` files are deterministic gzip streams and can be read directly by Python,
pandas, R, or command-line gzip tools. Raw experiment registries are not duplicated; exact run IDs,
source validation files, and SHA-256 values are recorded in `provenance/source_locations.json`.
Rendered figures are intentionally not frozen yet; `results/paper_assets/figure_data_*.csv` are the
accepted plotting inputs.
"""
    (build_root / "README.md").write_text(readme, encoding="utf-8")
    (build_root / "results/README.md").write_text(
        "# Results\n\nValidated RQ outputs, paper-ready CSV assets, and the accepted "
        "findings narrative are included.\n",
        encoding="utf-8",
    )
    (build_root / "source/repository_revision.json").write_text(
        json.dumps(
            {
                "schema_version": "paper-package-source-revision-v1",
                "git_commit": commit,
                "git_clean": True,
                "complete_repository_source_included": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (build_root / "process_record/README.md").write_text(
        "# Process record\n\nSource attempts and validations are linked through the processed "
        "manifest and provenance index.\n",
        encoding="utf-8",
    )

    entries = _entries(build_root)
    package_manifest = {
        "schema_version": "paper-writing-package-manifest-v1",
        "package_id": package_id,
        "profile_version": package_id,
        "package_stage": "final_results",
        "content_mode": "final_analysis_compact",
        "created_at": datetime.now(UTC).isoformat(),
        "source_git_commit": commit,
        "source_git_clean": True,
        "source_inference_run_id": manifest["source_runs"]["base_inference"],
        "evaluation_raw_included": False,
        "availability": availability,
        "data_selection": {
            "mode": "final_analysis_compact",
            "complete_processed_dataset_included": True,
            "raw_registries_included": False,
        },
        "file_count": len(entries),
        "total_file_bytes": sum(item["size_bytes"] for item in entries),
        "files": entries,
    }
    (build_root / "package_manifest.json").write_text(
        json.dumps(package_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    checksum_rows = [f"{item['sha256']}  {item['path']}" for item in entries]
    checksum_rows.append(
        f"{sha256_file(build_root / 'package_manifest.json')}  package_manifest.json"
    )
    (build_root / "CHECKSUMS.sha256").write_text("\n".join(checksum_rows) + "\n", encoding="utf-8")
    if target.exists():
        os.replace(target, backup)
    try:
        os.replace(build_root, target)
        validate_package(target)
    except Exception:
        if target.exists():
            shutil.rmtree(target)
        if backup.exists():
            os.replace(backup, target)
        raise
    if backup.exists():
        shutil.rmtree(backup)
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--assets-dir", type=Path, required=True)
    parser.add_argument("--exploratory-dir", type=Path)
    parser.add_argument("--package-id", required=True)
    parser.add_argument("--target", type=Path, default=ROOT / "paper_writing_package")
    args = parser.parse_args()
    print(
        build(
            args.dataset_dir.resolve(),
            args.analysis_dir.resolve(),
            args.assets_dir.resolve(),
            args.target.resolve(),
            package_id=args.package_id,
            exploratory=args.exploratory_dir.resolve() if args.exploratory_dir else None,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
