"""Small deterministic IO and statistics helpers used by every RQ analysis."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import subprocess
import tempfile
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from random import Random
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class AnalysisError(RuntimeError):
    """Raised when source data or derived outputs violate the frozen contract."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_identifier(prefix: str, *parts: object) -> str:
    payload = canonical_json_bytes([prefix, *parts])
    return f"{prefix}_{sha256_bytes(payload)[:24]}"


def repository_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError as error:
        raise AnalysisError(f"path is outside the repository: {resolved}") from error


def git_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def write_once(path: Path, content: bytes) -> None:
    """Atomically create immutable bytes, or reuse exactly identical bytes."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() == content:
            return
        raise AnalysisError(f"refusing to overwrite derived artifact: {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if path.read_bytes() != content:
                raise AnalysisError(f"concurrent derived-artifact conflict: {path}") from None
        os.chmod(path, 0o444)
    finally:
        temporary.unlink(missing_ok=True)


def write_json(path: Path, value: Any) -> None:
    content = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
    write_once(path, (content + "\n").encode("utf-8"))


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    """Atomically stream JSONL without duplicating full-scope outputs in memory."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise AnalysisError(f"refusing to overwrite derived artifact: {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            for row in rows:
                handle.write(canonical_json_bytes(dict(row)))
                handle.write(b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o444)
        try:
            os.link(temporary, path)
        except FileExistsError:
            raise AnalysisError(f"concurrent derived-artifact conflict: {path}") from None
    finally:
        temporary.unlink(missing_ok=True)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AnalysisError(f"expected a JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                raise AnalysisError(f"blank JSONL line at {path}:{line_number}")
            value = json.loads(line)
            if not isinstance(value, dict):
                raise AnalysisError(f"non-object JSONL row at {path}:{line_number}")
            rows.append(value)
    return rows


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise AnalysisError(f"refusing to overwrite derived artifact: {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fields,
                extrasaction="raise",
                lineterminator="\n",
            )
            writer.writeheader()
            for row in rows:
                writer.writerow({field: _csv_value(row.get(field)) for field in fields})
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o444)
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, dict | list | tuple):
        return canonical_json_bytes(value).decode("utf-8")
    return value


def normalize_source(source: str) -> str:
    """Apply only comparison-safe whitespace normalization, never syntax repair."""

    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = [line.rstrip() for line in lines]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def quantile(values: Sequence[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def mean(values: Sequence[float]) -> float | None:
    return sum(values) / len(values) if values else None


def deterministic_seed(base_seed: int, *parts: str) -> int:
    suffix = int(sha256_bytes(canonical_json_bytes(parts))[:16], 16)
    return base_seed ^ suffix


def paired_bootstrap_ci(
    differences: Sequence[int],
    *,
    confidence_level: float,
    resamples: int,
    seed: int,
) -> tuple[float | None, float | None]:
    """Percentile CI for a mean paired binary difference.

    Differences are -1, 0, or 1. A multinomial draw avoids materializing task-sized
    resamples while remaining an exact nonparametric task-level bootstrap.
    """

    if not differences:
        return None, None
    if any(value not in {-1, 0, 1} for value in differences):
        raise AnalysisError("paired bootstrap expects only -1, 0, and 1")
    negative = sum(value == -1 for value in differences)
    positive = sum(value == 1 for value in differences)
    total = len(differences)
    random = Random(seed)
    draws: list[float] = []
    for _ in range(resamples):
        positive_draw = random.binomialvariate(total, positive / total)
        remaining = total - positive_draw
        negative_probability = negative / (total - positive) if total != positive else 0.0
        negative_draw = random.binomialvariate(remaining, negative_probability)
        draws.append((positive_draw - negative_draw) / total)
    alpha = (1 - confidence_level) / 2
    return quantile(draws, alpha), quantile(draws, 1 - alpha)


def exact_mcnemar_p_value(improved: int, worsened: int) -> float | None:
    discordant = improved + worsened
    if discordant == 0:
        return None
    smaller = min(improved, worsened)
    tail = sum(math.comb(discordant, index) for index in range(smaller + 1)) / (2**discordant)
    return float(min(1.0, 2 * tail))


def pearson(values_x: Sequence[float], values_y: Sequence[float]) -> float | None:
    if len(values_x) != len(values_y) or len(values_x) < 2:
        return None
    mean_x = sum(values_x) / len(values_x)
    mean_y = sum(values_y) / len(values_y)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(values_x, values_y, strict=True))
    denominator_x = sum((x - mean_x) ** 2 for x in values_x)
    denominator_y = sum((y - mean_y) ** 2 for y in values_y)
    denominator = math.sqrt(denominator_x * denominator_y)
    return numerator / denominator if denominator else None


def average_ranks(values: Sequence[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(indexed):
        end = start + 1
        while end < len(indexed) and indexed[end][1] == indexed[start][1]:
            end += 1
        rank = (start + 1 + end) / 2
        for index, _ in indexed[start:end]:
            ranks[index] = rank
        start = end
    return ranks


def spearman(values_x: Sequence[float], values_y: Sequence[float]) -> float | None:
    if len(values_x) != len(values_y):
        return None
    return pearson(average_ranks(values_x), average_ranks(values_y))


def require_keys(row: Mapping[str, Any], keys: Iterable[str], *, context: str) -> None:
    missing = sorted(set(keys) - set(row))
    if missing:
        raise AnalysisError(f"{context} is missing required fields: {missing}")
