"""Default-off post-archive Decision Work Brief runtime attachment hook."""
from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_brief_agent_handoff import (
    build_decision_work_brief_agent_handoff,
    render_agent_handoff_json,
)
from engine.system_b.decision_work_brief_runtime_bundle import (
    ATTACHMENT_STATUS_SCHEMA_VERSION,
    SIDECAR_ROOT,
    build_decision_work_brief_runtime_bundle,
)
from engine.system_b.decision_work_brief_runtime_eligibility import (
    evaluate_runtime_attachment_eligibility,
)
from engine.system_b.decision_work_brief_runtime_receipt import (
    render_receipt_from_status,
)
from engine.system_b.decision_work_brief_safe_supply_resolver import (
    resolve_decision_work_brief_safe_supply,
    write_resolver_json,
)


DECISION_WORK_RUNTIME_ATTACHMENT_FLAG = "LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE"
DECISION_WORK_RESOLVER_MODE_ENV = "LOLLA_DECISION_WORK_BRIEF_RESOLVER_MODE"
REPO_ROOT = Path(__file__).resolve().parents[2]
DECISION_WORK_SAFE_REF_ENVS = {
    "LOLLA_DECISION_WORK_BRIEF_JSON_REF": (
        "brief_json_path",
        "decision_work_brief.json",
    ),
    "LOLLA_DECISION_WORK_BRIEF_REF": (
        "brief_markdown_path",
        "decision_work_brief.md",
    ),
    "LOLLA_DECISION_WORK_BRIEF_ENRICHED_REF": (
        "enriched_brief_path",
        "decision_work_brief_enriched.md",
    ),
    "LOLLA_DECISION_WORK_BRIEF_INTERPRETATION_READ_REF": (
        "interpretation_read_path",
        "interpretation_read.json",
    ),
    "LOLLA_DECISION_WORK_BRIEF_TRIAGE_PACKET_REF": (
        "triage_packet_path",
        "automatic_triage_packet.json",
    ),
    "LOLLA_DECISION_WORK_BRIEF_TRIAGE_READ_REF": (
        "triage_read_path",
        "automatic_triage_read.json",
    ),
}
ENABLED_VALUES = {"1", "true", "on", "yes"}
NON_CLAIMS = (
    "not_runtime_default",
    "not_customer_readiness",
    "not_human_validation",
    "not_product_proof",
    "not_answer_quality_scoring",
    "not_advice_correctness",
    "not_lolla_improvement_proof",
    "not_agent_action_authorization",
    "not_automatic_action_authorization",
    "triage_is_routing_not_scoring",
)


def decision_work_runtime_attachment_enabled(
    environ: dict[str, str] | None = None,
) -> bool:
    env = environ if environ is not None else os.environ
    return env.get(DECISION_WORK_RUNTIME_ATTACHMENT_FLAG, "").strip().lower() in (
        ENABLED_VALUES
    )


def run_post_archive_decision_work_brief_attachment(
    *,
    run_dir: Path | str,
    environ: dict[str, str] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Run the default-off, non-blocking post-archive attachment path."""

    run_path = Path(run_dir).expanduser()
    if not decision_work_runtime_attachment_enabled(environ):
        return {
            "enabled": False,
            "flag": DECISION_WORK_RUNTIME_ATTACHMENT_FLAG,
            "attachment_state": "not_requested",
            "sidecar_written": False,
            "non_blocking": True,
        }

    try:
        with tempfile.TemporaryDirectory(
            prefix="lolla_decision_work_resolver_"
        ) as resolver_tmp:
            resolver_output_path = _build_hook_resolver_output(
                run_path=run_path,
                environ=environ,
                resolver_work_dir=Path(resolver_tmp),
                created_at=created_at,
            )
            status = build_decision_work_brief_runtime_bundle(
                run_dir=run_path,
                output_dir=run_path,
                allow_archive_sidecar=True,
                resolver_output_path=resolver_output_path,
                created_at=created_at,
            )
        eligibility = evaluate_runtime_attachment_eligibility(
            run_dir=run_path,
            requested=True,
            attachment_status=status,
            created_at=created_at,
        )
        status["eligibility_result"] = {
            "schema_version": eligibility["schema_version"],
            "attachment_state": eligibility["attachment_state"],
            "hard_blockers": eligibility["hard_blockers"],
            "soft_triage_blockers": eligibility["soft_triage_blockers"],
            "agent_inspection_only": eligibility["agent_inspection_only"],
        }
        handoff = build_decision_work_brief_agent_handoff(
            source_run_ref=str(status.get("source_run_ref") or run_path.name),
            attachment_status=status,
            eligibility_result=eligibility,
            created_at=created_at,
        )
        sidecar_dir = run_path / SIDECAR_ROOT
        handoff_path = sidecar_dir / "agent_handoff_packet.json"
        handoff_path.write_text(
            render_agent_handoff_json(handoff, pretty=True),
            encoding="utf-8",
        )
        status["generated_artifacts"]["agent_handoff_packet"] = (
            f"{SIDECAR_ROOT}/agent_handoff_packet.json"
        )
        status["missing_artifacts"].pop("agent_handoff_packet", None)
        _write_status_and_receipt(run_path, status)
        return {
            "enabled": True,
            "flag": DECISION_WORK_RUNTIME_ATTACHMENT_FLAG,
            "attachment_state": status["attachment_state"],
            "sidecar_written": True,
            "non_blocking": True,
            "generated_artifacts": dict(status["generated_artifacts"]),
        }
    except Exception:  # noqa: BLE001 - runtime hook must fail closed.
        status = _failed_closed_status(run_path=run_path, created_at=created_at)
        _write_status_and_receipt(run_path, status)
        return {
            "enabled": True,
            "flag": DECISION_WORK_RUNTIME_ATTACHMENT_FLAG,
            "attachment_state": "failed_closed",
            "sidecar_written": True,
            "non_blocking": True,
            "failed_closed_reason": "runtime_attachment_hook_failed",
        }


def _build_hook_resolver_output(
    *,
    run_path: Path,
    environ: dict[str, str] | None,
    resolver_work_dir: Path,
    created_at: str | None,
) -> Path:
    env = environ if environ is not None else os.environ
    supplied_refs = _resolver_ref_kwargs(env=env, resolver_work_dir=resolver_work_dir)
    resolver_mode = _resolver_mode(env=env, supplied_refs=supplied_refs)
    resolver_result = resolve_decision_work_brief_safe_supply(
        run_dir=run_path,
        mode=resolver_mode,
        created_at=created_at,
        **supplied_refs,
    )
    resolver_output_path = resolver_work_dir / "safe_supply_resolver.json"
    write_resolver_json(resolver_output_path, resolver_result, pretty=True)
    return resolver_output_path


def _resolver_mode(
    *,
    env: dict[str, str],
    supplied_refs: dict[str, Path | None],
) -> str:
    configured = env.get(DECISION_WORK_RESOLVER_MODE_ENV, "").strip()
    if configured:
        return configured
    if any(value is not None for value in supplied_refs.values()):
        return "manual_ref_supply_only"
    return "archive_local_safe_resolver"


def _resolver_ref_kwargs(
    *,
    env: dict[str, str],
    resolver_work_dir: Path,
) -> dict[str, Path | None]:
    kwargs: dict[str, Path | None] = {}
    resolver_work_dir.mkdir(parents=True, exist_ok=True)
    for env_name, (kwarg_name, copied_name) in DECISION_WORK_SAFE_REF_ENVS.items():
        raw = env.get(env_name, "").strip()
        kwargs[kwarg_name] = (
            _prepared_resolver_ref(
                raw_value=raw,
                copied_name=copied_name,
                resolver_work_dir=resolver_work_dir,
            )
            if raw
            else None
        )
    return kwargs


def _prepared_resolver_ref(
    *,
    raw_value: str,
    copied_name: str,
    resolver_work_dir: Path,
) -> Path:
    source = Path(raw_value).expanduser()
    if not source.is_absolute():
        source = (REPO_ROOT / source).resolve(strict=False)
    if not source.exists() or not source.is_file():
        return source
    destination = resolver_work_dir / copied_name
    shutil.copyfile(source, destination)
    return destination


def _failed_closed_status(*, run_path: Path, created_at: str | None) -> dict[str, Any]:
    return {
        "schema_version": ATTACHMENT_STATUS_SCHEMA_VERSION,
        "attachment_metadata": {
            "created_at": created_at or _utc_now(),
            "builder": "engine.system_b.decision_work_brief_runtime_attachment",
            "mode": "flagged_post_archive",
            "post_archive_only": True,
            "input_archive_mutated": False,
            "sidecar_written_inside_archive": True,
            "archive_core_artifacts_mutated": False,
        },
        "source_run_ref": run_path.name or "unknown",
        "attachment_mode": "flagged_post_archive",
        "attachment_state": "failed_closed",
        "generated_artifacts": {},
        "missing_artifacts": {
            "decision_work_brief_markdown": "not_generated",
            "decision_work_brief_enriched_markdown": "not_generated",
            "automatic_triage_read": "not_generated",
            "agent_handoff_packet": "not_generated",
        },
        "blocked_reasons": [],
        "deferred_reasons": [],
        "failed_closed_reasons": ["runtime_attachment_hook_failed"],
        "custody_flags": _custody_flags(),
        "privacy_export_policy": {
            "raw_conversation_text_included": False,
            "raw_revised_answer_text_included": False,
            "raw_memo_text_included": False,
            "provider_text_included": False,
            "private_ledgers_included": False,
            "local_absolute_paths_included": False,
            "source_refs_only_by_default": True,
        },
        "non_claims": list(NON_CLAIMS),
    }


def _write_status_and_receipt(run_path: Path, status: dict[str, Any]) -> None:
    sidecar_dir = run_path / SIDECAR_ROOT
    sidecar_dir.mkdir(parents=True, exist_ok=True)
    status_path = sidecar_dir / "attachment_status.json"
    status["generated_artifacts"]["attachment_status"] = (
        f"{SIDECAR_ROOT}/attachment_status.json"
    )
    receipt = render_receipt_from_status(status)
    receipt_path = sidecar_dir / "user_receipt.md"
    receipt_path.write_text(receipt, encoding="utf-8")
    status["generated_artifacts"]["user_receipt"] = f"{SIDECAR_ROOT}/user_receipt.md"
    status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")


def _custody_flags() -> dict[str, Any]:
    return {
        "human_validated": False,
        "human_review_completed": False,
        "product_proof": False,
        "model_calls": 0,
        "runtime_invoked": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "answer_quality_scored": False,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
        "raw_private_content_included": False,
        "provider_text_included": False,
        "local_absolute_paths_included": False,
    }


def _utc_now() -> str:
    return _dt.datetime.now(tz=_dt.UTC).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )
