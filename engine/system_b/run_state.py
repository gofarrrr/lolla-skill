"""Run identity helpers for Lolla runtime artifacts.

The ordinary skill defaults to ``/tmp/lolla_<run_id>_<artifact>`` files. Tests
and controlled operators may set ``LOLLA_TMP_DIR``. This module keeps the
runtime root, run-id parsing, and expected-run validation in one place so a
stale convenience pointer cannot silently mix two runs.
"""
from __future__ import annotations

import datetime as _dt
import os
import re
import secrets
from pathlib import Path
from typing import Iterable


RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

_KNOWN_ARTIFACT_SUFFIXES = tuple(
    sorted(
        {
            "conversation",
            "extraction",
            "extraction_calls",
            "extraction_terminal",
            "conversation_processing_view",
            "provider_budget",
            "result",
            "revised",
            "memo",
            "memo_note",
            "gapcheck",
            "gapcheck_lanes",
            "v60_ledger_skeleton",
            "v60_ledger",
            "pre_step6_shadow_portfolio",
            "pre_step6_private_table",
            "pre_step6_private_table_ledger",
            "live_transcript",
            "operator",
            "consumer_readback",
            "consumer_reconsideration",
            "consumer_verification",
            "user_usefulness_review",
            "outcome_review",
            "run_events",
        },
        key=len,
        reverse=True,
    )
)


def make_run_id(
    *,
    now: _dt.datetime | None = None,
    suffix_bytes: int = 3,
) -> str:
    """Return a collision-resistant run id like ``20260623T113203Z_c4df83``."""
    stamp_source = now or _dt.datetime.now(_dt.timezone.utc)
    if stamp_source.tzinfo is None:
        stamp_source = stamp_source.replace(tzinfo=_dt.timezone.utc)
    stamp = stamp_source.astimezone(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = secrets.token_hex(max(1, int(suffix_bytes)))
    return f"{stamp}_{suffix}"


def is_valid_run_id(run_id: str) -> bool:
    """Return True iff ``run_id`` is safe to interpolate into scratch paths."""
    return bool(run_id) and bool(RUN_ID_PATTERN.fullmatch(run_id))


def runtime_tmp_dir() -> Path:
    """Return the declared runtime-artifact root (``/tmp`` by default)."""

    return Path(os.getenv("LOLLA_TMP_DIR", "/tmp")).expanduser()


def infer_run_id_from_lolla_path(raw_path: str | os.PathLike[str] | None) -> str:
    """Infer run id from ``lolla_<run_id>_<artifact>`` filenames.

    Run ids may contain underscores, so a naive ``split("_")[1]`` is wrong.
    This parser removes a known artifact suffix from the right side instead.
    """
    if not raw_path:
        return ""
    stem = Path(raw_path).stem
    if not stem.startswith("lolla_"):
        return ""
    rest = stem[len("lolla_") :]
    for suffix in _KNOWN_ARTIFACT_SUFFIXES:
        marker = f"_{suffix}"
        if rest.endswith(marker):
            candidate = rest[: -len(marker)]
            return candidate if is_valid_run_id(candidate) else ""
    return ""


def validate_expected_run_state(
    *,
    expected_run_id: str | None = None,
    actual_run_id: str | None = None,
    artifact_paths: Iterable[str | os.PathLike[str] | None] = (),
    phase: str = "run",
) -> list[str]:
    """Return run-state mismatch messages.

    ``LOLLA_EXPECTED_RUN_ID`` is intentionally optional for backward
    compatibility. Once it is present, every guarded script must agree with it.
    """
    expected = (expected_run_id if expected_run_id is not None else os.getenv("LOLLA_EXPECTED_RUN_ID", "")).strip()
    if not expected:
        return []
    actual = (actual_run_id if actual_run_id is not None else os.getenv("LOLLA_RUN_ID", "")).strip()
    errors: list[str] = []
    if not is_valid_run_id(expected):
        errors.append(f"{phase}: invalid LOLLA_EXPECTED_RUN_ID {expected!r}")
    if not actual:
        errors.append(f"{phase}: LOLLA_EXPECTED_RUN_ID is {expected!r} but LOLLA_RUN_ID is unset")
    elif actual != expected:
        errors.append(
            f"{phase}: run state mismatch: expected {expected!r}, active LOLLA_RUN_ID is {actual!r}"
        )

    for raw_path in artifact_paths:
        inferred = infer_run_id_from_lolla_path(raw_path)
        if inferred and inferred != expected:
            errors.append(
                f"{phase}: artifact path {Path(raw_path).name!r} belongs to run {inferred!r}, expected {expected!r}"
            )
    return errors


def assert_expected_run_state(
    *,
    expected_run_id: str | None = None,
    actual_run_id: str | None = None,
    artifact_paths: Iterable[str | os.PathLike[str] | None] = (),
    phase: str = "run",
) -> None:
    """Raise ``SystemExit`` when expected-run validation fails."""
    errors = validate_expected_run_state(
        expected_run_id=expected_run_id,
        actual_run_id=actual_run_id,
        artifact_paths=artifact_paths,
        phase=phase,
    )
    if errors:
        raise SystemExit("FATAL: " + "\nFATAL: ".join(errors))
