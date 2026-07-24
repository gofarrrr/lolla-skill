#!/usr/bin/env python3
"""Run the full Lolla pipeline against an extracted conversation.

Takes extraction JSON plus a raw conversation transcript and runs all four
lanes via OpenRouter. The runtime contract is ConversationContext-only.

Usage:
    python3 scripts/run_pipeline.py --extraction-file /tmp/extraction.json --conversation-file /tmp/conversation.txt

Output: JSON to stdout with delta_card, companion_cheat_sheet, frame_pressure_card.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from collections import Counter
from dataclasses import asdict
from pathlib import Path


def _write_private_text(path: Path, text: str) -> None:
    """Atomically persist a conversation-derived artifact for its owner only."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            os.chmod(handle.name, 0o600)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        os.replace(temporary, path)
        path.chmod(0o600)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Path resolution — find pipeline package
# ---------------------------------------------------------------------------

SKILL_ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = SKILL_ROOT / "engine"
MAX_POSTPROCESSING_ASSISTANT_CHARS = 40_000

if (ENGINE_DIR / "system_b" / "__init__.py").exists():
    # The live package is historically imported as ``system_b``, while a
    # bounded set of bundled modules still use ``engine.system_b``.  A Codex
    # session may invoke this script from any working directory, so expose the
    # bundled skill root explicitly instead of relying on the caller's cwd.
    sys.path.insert(0, str(SKILL_ROOT))
    sys.path.insert(0, str(ENGINE_DIR))
elif os.environ.get("LOLLA_REPO_ROOT"):
    sys.path.insert(0, os.environ["LOLLA_REPO_ROOT"])
else:
    print(
        "ERROR: Cannot find the Lolla engine. "
        "Expected at: " + str(ENGINE_DIR / "system_b"),
        file=sys.stderr,
    )
    sys.exit(1)

from system_b.audit_mode import (  # noqa: E402
    AuditModeError,
    apply_risk_mode_metadata,
    audit_mode_from_env,
)
from system_b.capture_adequacy import build_capture_adequacy  # noqa: E402
from system_b.provider_boundary_health import refresh_provider_boundary_health  # noqa: E402
from system_b.run_state import assert_expected_run_state, infer_run_id_from_lolla_path  # noqa: E402


# ---------------------------------------------------------------------------
# .env loader
# ---------------------------------------------------------------------------

def _load_env_file(path: Path) -> list[str]:
    if not path.exists():
        return []
    loaded: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key not in os.environ:
            os.environ[key] = value
            loaded.append(key)
    return loaded


def _build_fact_registry(extraction: dict) -> str:
    """Build a structured fact registry from the extraction JSON.

    Produces a compact, explicitly provisional extraction scaffold for the BI
    judge. The complete available user turns are supplied separately and remain
    authoritative. Dropped-thread interpretations are intentionally excluded:
    repeating one global thread in every passage check created a systematic
    false-positive pressure.
    """
    ext = extraction.get("extraction", extraction)
    parts: list[str] = []

    # Decision situation as opening context
    situation = ext.get("decision_situation", "")
    if situation:
        parts.append(f"Decision: {situation}")

    # Live constraints
    constraints = ext.get("live_constraints", [])
    if constraints:
        parts.append("\nExtracted candidate constraints:")
        for c in constraints:
            constraint = c.get("constraint", "")
            weight = c.get("weight", "")
            status = c.get("status", "")
            if constraint:
                parts.append(f"- {constraint} (weight: {weight}, status: {status})")

    return "\n".join(parts) if parts else ""


def _build_bi_context(
    *,
    extraction: dict,
    user_context_text: str,
    user_turn_count: int,
    fallback_context_text: str = "",
) -> tuple[str, dict[str, object]]:
    """Build source-complete passage-check context with explicit custody."""

    user_context = user_context_text.strip()
    sections: list[str] = []
    if user_context:
        sections.append(
            "Complete available user turns (authoritative for user-stated facts):\n"
            + user_context
        )

    fact_registry = _build_fact_registry(extraction)
    if fact_registry:
        sections.append(
            "Provisional extracted decision scaffold (may be incomplete):\n"
            + fact_registry
        )

    if not sections and fallback_context_text.strip():
        sections.append(
            "Fallback decision context (complete user turns unavailable):\n"
            + fallback_context_text.strip()
        )

    context = "\n\n".join(sections)
    custody = {
        "schema_version": "lolla.bullshit_index_context_custody.v1",
        "source": (
            "complete_available_user_turns_plus_provisional_extraction"
            if user_context
            else "provisional_extraction_or_fallback"
        ),
        "complete_available_user_turns": bool(user_context),
        "user_turn_count": int(user_turn_count),
        "user_context_char_count": len(user_context),
        "user_context_sha256": hashlib.sha256(
            user_context.encode("utf-8")
        ).hexdigest(),
        "passage_context_char_count": len(context),
        "passage_context_sha256": hashlib.sha256(
            context.encode("utf-8")
        ).hexdigest(),
        "dropped_threads_in_passage_context": False,
    }
    return context, custody


def _joined_turn_text(ctx, speaker: str) -> str:
    """Join non-empty turn bodies for one speaker from ConversationContext."""
    return "\n\n".join(
        t.text.strip()
        for t in ctx.turns
        if t.speaker == speaker and t.text.strip()
    )


def _build_case_focus_from_context(ctx) -> str:
    """Derive a compact post-processing focus from ConversationContext.

    This replaces the legacy CLI-level `query` requirement. It is only used
    by post-processing surfaces such as revision, BI fallback context, and
    inspection; the pipeline lanes already receive the full ConversationContext.
    """
    ext = ctx.extraction
    parts: list[str] = []

    if ext.decision_situation.strip():
        parts.append(ext.decision_situation.strip())

    if ext.live_constraints:
        constraint_lines = []
        for constraint in ext.live_constraints:
            status = constraint.status or "active"
            weight = constraint.weight or "situational"
            tag = (
                f"{status.upper()}/{weight.upper()}"
                if status != "active"
                else status.upper()
            )
            constraint_lines.append(f"- [{tag}] {constraint.constraint}")
        parts.append("Constraints stated during conversation:\n" + "\n".join(constraint_lines))

    if ext.original_framing.strip():
        parts.append(f"Original framing: {ext.original_framing.strip()}")

    if ext.dropped_threads:
        thread_lines = []
        for thread in ext.dropped_threads:
            line = (
                f"- {thread.thread} (raised by {thread.raised_by}, "
                f"status: {thread.status})"
            )
            if thread.superseded_by:
                line += f" -> superseded by: {thread.superseded_by}"
            thread_lines.append(line)
        parts.append("Dropped threads (raised but unresolved):\n" + "\n".join(thread_lines))

    if not parts:
        user_turns = _joined_turn_text(ctx, "user")
        if user_turns:
            parts.append(user_turns)

    return "\n\n".join(parts).strip()


def _legacy_seed_from_extraction(extraction: dict) -> tuple[str, str]:
    """Read deprecated artifact seed fields as a fallback only.

    `audit_seed` is the new explicit artifact shape. `critique_request` and
    raw top-level `query` / `vanilla_answer` remain accepted so older captured
    artifacts can still run.
    """
    audit_seed = extraction.get("audit_seed")
    if isinstance(audit_seed, dict):
        case_focus = str(audit_seed.get("case_focus", "") or "")
        audit_target = str(audit_seed.get("audit_target_assistant_text", "") or "")
        if case_focus or audit_target:
            return case_focus, audit_target

    critique_request = extraction.get("critique_request")
    if isinstance(critique_request, dict):
        cr = critique_request
    else:
        cr = extraction

    return (
        str(cr.get("query", "") or ""),
        str(cr.get("vanilla_answer", "") or ""),
    )


def _derive_postprocessing_seed(extraction: dict, ctx) -> dict[str, str]:
    """Derive post-processing text from ConversationContext first.

    This keeps the runtime contract conversation-native while preserving old
    artifact compatibility if a malformed/older context lacks the needed text.
    """
    legacy_case_focus, legacy_audit_target = _legacy_seed_from_extraction(extraction)

    case_focus = _build_case_focus_from_context(ctx) or legacy_case_focus
    audit_target = (
        _joined_turn_text(ctx, "assistant")
        or ctx.extraction.synthesized_position.strip()
        or legacy_audit_target
    )

    if len(audit_target) > MAX_POSTPROCESSING_ASSISTANT_CHARS:
        audit_target = audit_target[:MAX_POSTPROCESSING_ASSISTANT_CHARS]

    return {
        "case_focus": case_focus,
        "audit_target_assistant_text": audit_target,
    }


def _env_flag_enabled(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _env_flag_disabled(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in {"0", "false", "no", "off"}


def _v60_mode_enabled(mode: str) -> bool:
    if mode == "on":
        return True
    if mode == "off":
        return False
    return not _env_flag_disabled("LOLLA_V60_ENRICHMENT")


def _derive_run_id_from_path(raw_path: str | None) -> str:
    """Pull <run_id> out of a path like ``lolla_<run_id>_*.{json,txt}``."""
    return infer_run_id_from_lolla_path(raw_path)


def _boundary_record_dict(record: object) -> dict[str, object]:
    if isinstance(record, dict):
        return dict(record)
    if hasattr(record, "to_dict"):
        value = record.to_dict()
        return value if isinstance(value, dict) else {}
    if hasattr(record, "__dict__"):
        return dict(vars(record))
    return {}


def _reasoning_detail_warning(records: list[object]) -> tuple[str, dict[str, object]]:
    leak_records: list[dict[str, object]] = []
    models: set[str] = set()
    stages: set[str] = set()
    for record in records:
        rec = _boundary_record_dict(record)
        if not rec:
            continue
        try:
            reasoning_tokens = int(rec.get("reasoning_tokens") or 0)
        except (TypeError, ValueError):
            reasoning_tokens = 0
        if not bool(rec.get("reasoning_disabled")):
            continue
        if not (bool(rec.get("reasoning_details_present")) or reasoning_tokens > 0):
            continue
        leak_records.append(rec)
        model = str(rec.get("served_model") or rec.get("model") or "").strip()
        stage = str(rec.get("stage") or "").strip()
        if model:
            models.add(model)
        if stage:
            stages.add(stage)
    if not leak_records:
        return "", {
            "detected": False,
            "count": 0,
            "models": [],
            "stages": [],
        }
    count = len(leak_records)
    warning = (
        "Boundary response returned reasoning details despite reasoning being disabled "
        f"({count} call{'s' if count != 1 else ''})."
    )
    return warning, {
        "detected": True,
        "count": count,
        "models": sorted(models),
        "stages": sorted(stages),
    }


def _provider_call_failure_warning(
    records: list[object],
) -> tuple[str, dict[str, object]]:
    """Summarize attempted boundary calls that ended without usable output.

    Provider-boundary privacy health is intentionally a separate concern. This
    helper owns execution completeness: an attempted call with any non-``ok``
    terminal status is partial semantic coverage even when other lanes still
    produce findings and the pipeline can safely continue.
    """

    failures: list[dict[str, object]] = []
    statuses: Counter[str] = Counter()
    error_types: Counter[str] = Counter()
    error_codes: Counter[str] = Counter()
    stages: set[str] = set()
    tendency_ids: set[str] = set()
    providers: set[str] = set()
    models: set[str] = set()

    for record in records:
        rec = _boundary_record_dict(record)
        if not rec or not bool(rec.get("provider_attempted")):
            continue
        status = str(rec.get("status") or "").strip()
        if not status or status == "ok":
            continue
        failures.append(rec)
        statuses[status] += 1
        error_type = str(rec.get("provider_error_type") or "").strip()
        error_code = str(rec.get("provider_error_code") or "").strip()
        stage = str(rec.get("stage") or "").strip()
        tendency_id = str(rec.get("tendency_id") or "").strip()
        provider = str(
            rec.get("served_provider_name") or rec.get("provider_name") or ""
        ).strip()
        model = str(rec.get("served_model") or rec.get("model") or "").strip()
        if error_type:
            error_types[error_type] += 1
        if error_code:
            error_codes[error_code] += 1
        if stage:
            stages.add(stage)
        if tendency_id:
            tendency_ids.add(tendency_id)
        if provider:
            providers.add(provider)
        if model:
            models.add(model)

    if not failures:
        return "", {
            "status": "clean",
            "failed_call_count": 0,
            "attempted_failed_call_count": 0,
            "stages": [],
            "tendency_ids": [],
            "status_counts": {},
            "provider_error_type_counts": {},
            "provider_error_code_counts": {},
            "providers": [],
            "models": [],
        }

    count = len(failures)
    warning = (
        f"{count} provider-backed reasoning call"
        f"{'s' if count != 1 else ''} ended without a usable result; "
        "the incomplete semantic coverage was preserved without automatic retry."
    )
    return warning, {
        "status": "partial",
        "failed_call_count": count,
        "attempted_failed_call_count": count,
        "stages": sorted(stages),
        "tendency_ids": sorted(tendency_ids),
        "status_counts": dict(sorted(statuses.items())),
        "provider_error_type_counts": dict(sorted(error_types.items())),
        "provider_error_code_counts": dict(sorted(error_codes.items())),
        "providers": sorted(providers),
        "models": sorted(models),
    }


_HEALTH_SEVERITY_RANK = {
    "info": 0,
    "optional_off": 0,
    "partial": 1,
    "degraded": 2,
    "critical": 3,
}

_HEALTH_ISSUE_DEFAULTS = {
    "substrate_empty": {
        "severity": "degraded",
        "axis": "substrate",
        "trust_impact": "Compiled substrate was empty, so deterministic model routing had no substrate to consult.",
    },
    "embeddings_off": {
        "severity": "optional_off",
        "axis": "retrieval",
        "trust_impact": "Embedding recall was unavailable by mode; deterministic and lexical paths still ran.",
    },
    "no_fingerprint": {
        "severity": "degraded",
        "axis": "companion",
        "trust_impact": "Companion routing produced no validated fingerprint, reducing confidence in model custody.",
    },
    "companion_verification_parse_failed": {
        "severity": "partial",
        "axis": "companion",
        "trust_impact": (
            "Lane 2 companion verification returned malformed output; an empty companion card "
            "may mean verifier signal was lost, not that no companion models applied."
        ),
    },
    "pipeline_warnings": {
        "severity": "partial",
        "axis": "pipeline",
        "trust_impact": "Pipeline warnings were emitted; inspect warnings before comparing this run.",
    },
    "vendor_boundary_reasoning_leak": {
        "severity": "partial",
        "axis": "vendor_boundary",
        "trust_impact": (
            "A model provider returned reasoning details despite reasoning being disabled; "
            "product output may still be clean, but model-boundary comparisons need caution."
        ),
    },
    "provider_call_terminal_loss": {
        "severity": "partial",
        "axis": "provider_call",
        "trust_impact": (
            "At least one attempted provider-backed reasoning call ended without usable "
            "output, so the affected semantic check is incomplete even if other lanes "
            "still produced findings."
        ),
    },
    "capture_critical": {
        "severity": "critical",
        "axis": "capture",
        "trust_impact": "Conversation capture was critically incomplete or malformed.",
    },
    "capture_degraded": {
        "severity": "degraded",
        "axis": "capture",
        "trust_impact": "Conversation capture had quality problems that may affect reasoning coverage.",
    },
    "quote_fabrication": {
        "severity": "degraded",
        "axis": "extraction",
        "trust_impact": "Extraction retained fabricated quotes after validation/retry.",
    },
    "capture_truncated": {
        "severity": "degraded",
        "axis": "capture",
        "trust_impact": "Legacy compatibility code for a partial bounded extraction view.",
    },
    "extraction_processing_view_partial": {
        "severity": "degraded",
        "axis": "extraction",
        "trust_impact": (
            "The authoritative conversation is preserved, but initial semantic extraction used "
            "a bounded view that omitted middle turns; extracted scaffolding may therefore miss "
            "constraints or changes introduced there."
        ),
    },
    "lane3_all_dropped": {
        "severity": "partial",
        "axis": "lane3",
        "trust_impact": "Frame pressure detected candidates but all failed validation, so Lane 3 contributed no reframings.",
    },
    "bullshit_index_partial": {
        "severity": "partial",
        "axis": "postprocessing",
        "trust_impact": "Some Bullshit Index passage evaluations failed, leaving a partial profile.",
    },
    "stakeholder_check_failed": {
        "severity": "degraded",
        "axis": "stakeholder_check",
        "trust_impact": "A triggered stakeholder assumption check failed instead of producing a usable result.",
    },
    "v60_enrichment_failed": {
        "severity": "degraded",
        "axis": "v60",
        "trust_impact": "V60 private enrichment was enabled but did not produce an active enrichment payload.",
    },
}


def _health_issue_detail(
    code: str,
    *,
    severity: str | None = None,
    axis: str | None = None,
    trust_impact: str | None = None,
    **metadata: object,
) -> dict[str, object]:
    defaults = _HEALTH_ISSUE_DEFAULTS.get(code, {})
    detail: dict[str, object] = {
        "code": code,
        "severity": severity or str(defaults.get("severity") or "degraded"),
        "axis": axis or str(defaults.get("axis") or "pipeline"),
        "trust_impact": trust_impact or str(defaults.get("trust_impact") or "Inspect this run before comparison."),
    }
    for key, value in metadata.items():
        if value is not None:
            detail[key] = value
    return detail


def _overall_health_from_issue_details(issue_details: list[dict[str, object]]) -> str:
    highest = 0
    overall = "healthy"
    for detail in issue_details:
        severity = str(detail.get("severity") or "")
        rank = _HEALTH_SEVERITY_RANK.get(severity, _HEALTH_SEVERITY_RANK["degraded"])
        if rank > highest:
            highest = rank
            overall = severity
    return "healthy" if highest == 0 else overall


def _health_issue_axis_counts(issue_details: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for detail in issue_details:
        axis = str(detail.get("axis") or "pipeline")
        counts[axis] = counts.get(axis, 0) + 1
    return dict(sorted(counts.items()))


# ---------------------------------------------------------------------------
# Data root resolution
# ---------------------------------------------------------------------------

def _resolve_data_root() -> Path:
    """Determine the root directory for pipeline data loading.

    The engine expects ``root/build/knowledge_graph.json``.
    Creates a temp dir with a symlink build/ -> data/ so the engine
    finds data files at the expected path.
    """
    skill_data = SKILL_ROOT / "data"
    if not skill_data.exists():
        print(
            f"ERROR: Skill data directory not found at {skill_data}",
            file=sys.stderr,
        )
        sys.exit(1)

    tmp_root = Path(tempfile.mkdtemp(prefix="lolla_pipeline_"))
    os.symlink(str(skill_data), str(tmp_root / "build"))
    return tmp_root


# ---------------------------------------------------------------------------
# Result serialization
# ---------------------------------------------------------------------------

def _serialize_conversation_context(ctx) -> dict:
    """Serialize a ConversationContext to a JSON-safe dict for result.json.

    Observatory + render_memo derive their displayed case focus / assistant
    audit target from this block, and use decision_situation for case naming.
    Carries the full conversation shape so consumers don't need a separate
    channel for the source data.
    """
    ext = ctx.extraction
    return {
        "decision_situation": ext.decision_situation,
        "original_framing": ext.original_framing,
        "synthesized_position": ext.synthesized_position,
        "reasoning_passages": list(ext.reasoning_passages),
        "turns": [
            {"turn_index": t.turn_index, "speaker": t.speaker, "text": t.text}
            for t in ctx.turns
        ],
        "live_constraints": [
            {
                "constraint": c.constraint,
                "introduced_turn": c.introduced_turn,
                "status": c.status,
                "weight": c.weight,
                "canonical_key": c.canonical_key,
            }
            for c in ext.live_constraints
        ],
        "dropped_threads": [
            {
                "thread": d.thread,
                "raised_by": d.raised_by,
                "raised_turn": d.raised_turn,
                "status": d.status,
                "superseded_by": d.superseded_by,
            }
            for d in ext.dropped_threads
        ],
    }


def _serialize_result(result, *, embedding_active: bool = False, compiled_chunk_count: int = 0) -> dict:
    """Serialize PipelineResult to a JSON-compatible dict."""
    from system_b.testing_harness import delta_card_to_payload, companion_card_to_payload

    output: dict = {
        "detected_tendencies": list(result.detected_tendencies),
    }

    # Delta card (Lane 1)
    output["delta_card"] = delta_card_to_payload(result.delta_card)

    # Companion cheat sheet (Lane 2)
    if result.companion_cheat_sheet is not None:
        output["companion_cheat_sheet"] = result.companion_cheat_sheet.to_payload()
    else:
        output["companion_cheat_sheet"] = None

    # Companion card raw (Lane 2 raw detected models)
    output["companion_card"] = companion_card_to_payload(result.companion_card)

    # R2 deterministic survival portfolio. This is built before the legacy
    # probabilistic verifier and therefore remains independent of its
    # accepted/rejected/omitted judgments.
    output["constitutional_graph_survival"] = (
        dict(result.constitutional_graph_survival)
        if result.constitutional_graph_survival is not None
        else None
    )

    # Frame pressure card (Lane 3)
    if result.frame_pressure_card is not None:
        output["frame_pressure_card"] = result.frame_pressure_card.to_payload()
    else:
        output["frame_pressure_card"] = None

    # Structural coverage card (Lane 4)
    if result.structural_coverage_card is not None:
        output["structural_coverage_card"] = result.structural_coverage_card.to_payload()
    else:
        output["structural_coverage_card"] = None

    # Audit summary with companion diagnostics
    from system_b.testing_harness import summarize_boundary_calls
    output["audit_summary"] = {
        "triage_scores": [
            {"tendency_id": s.tendency_id, "score": s.score, "evidence": s.evidence}
            for s in result.audit.triage_scores
        ],
        "triggered_tendencies": [tt.tendency_id for tt in result.audit.triggered_tendencies],
        "triggered_tendency_sources": [
            {"tendency_id": tt.tendency_id, "source": tt.source, "score": tt.score}
            for tt in result.audit.triggered_tendencies
        ],
        "boundary_call_count": len(result.audit.boundary_calls),
        "boundary_summary": summarize_boundary_calls(result.audit.boundary_calls),
        "boundary_calls": [
            {
                "stage": bc.stage,
                "tendency_id": bc.tendency_id,
                "provider_name": bc.provider_name,
                "served_provider_name": bc.served_provider_name,
                "requested_model": bc.requested_model,
                "served_model": bc.served_model,
                "model": bc.model,
                "model_attribution_status": bc.model_attribution_status,
                "status": bc.status,
                "finish_reason": bc.finish_reason,
                "provider_error_source": bc.provider_error_source,
                "provider_error_type": bc.provider_error_type,
                "provider_error_code": bc.provider_error_code,
                "provider_error_provider_code": bc.provider_error_provider_code,
                "provider_error_message_sha256": bc.provider_error_message_sha256,
                "retry_after_seconds": bc.retry_after_seconds,
                "raw_message_content": bc.raw_message_content,
                "temperature": bc.temperature,
                "prompt_tokens": bc.prompt_tokens,
                "completion_tokens": bc.completion_tokens,
                "total_tokens": bc.total_tokens,
                "cached_tokens": bc.cached_tokens,
                "cache_write_tokens": bc.cache_write_tokens,
                "reasoning_tokens": bc.reasoning_tokens,
                "reasoning_disabled": bc.reasoning_disabled,
                "reasoning_details_present": bc.reasoning_details_present,
                "provider_attempted": bc.provider_attempted,
                "response_id": bc.response_id,
                "exact_cost_usd": bc.exact_cost_usd,
                "request_max_output_tokens": bc.request_max_output_tokens,
                "request_max_price_prompt": bc.request_max_price_prompt,
                "request_max_price_completion": bc.request_max_price_completion,
                "request_provider_order": list(bc.request_provider_order),
                "request_allow_fallbacks": bc.request_allow_fallbacks,
                "request_require_parameters": bc.request_require_parameters,
                "request_data_collection": bc.request_data_collection,
                "request_zdr": bc.request_zdr,
                "run_max_provider_calls": bc.run_max_provider_calls,
                "run_max_cost_usd": bc.run_max_cost_usd,
                "maximum_call_cost_usd": bc.maximum_call_cost_usd,
                "budget_reservation_id": bc.budget_reservation_id,
                "pricing_table_version": bc.pricing_table_version,
                "pricing_table_stale": bc.pricing_table_stale,
            }
            for bc in result.audit.boundary_calls
        ],
        "warnings": list(result.audit.warnings),
        "embedding_swiss_cheese_active": embedding_active,
        "compiled_substrate_chunk_count": compiled_chunk_count,
        "companion_fingerprint_raw": list(result.audit.companion_fingerprint_raw),
        "companion_fingerprint_validated": list(result.audit.companion_fingerprint_validated),
        "companion_fingerprint_dropped": list(result.audit.companion_fingerprint_dropped),
        "companion_detected_models": list(result.audit.companion_detected_models),
        "companion_rejected_models": list(result.audit.companion_rejected_models),
        # Lane 2 attribution surfaces (research/lane2-attribution-design-2026-04-26.md):
        # - companion_candidates: full recall input to verifier (with per-source ranks)
        # - companion_verification_accepted_before_cap: full LLM-accepted set
        # - companion_verification_capped_models: accepted-but-not-surfaced (top-5 budget)
        # - companion_verification_quote_repairs: accepted entries rescued by literal quote repair
        # - companion_candidate_cap: explicit recall cap in effect
        # - embedding_mode: "on" or "off" so reports group cleanly without env inspection
        "companion_candidates": list(result.audit.companion_candidates),
        "companion_verification_accepted_before_cap": list(result.audit.companion_verification_accepted_before_cap),
        "companion_verification_capped_models": list(result.audit.companion_verification_capped_models),
        "companion_verification_duplicate_accepts": list(result.audit.companion_verification_duplicate_accepts),
        "companion_verification_quote_repairs": list(result.audit.companion_verification_quote_repairs),
        "companion_verification_silently_omitted": list(result.audit.companion_verification_silently_omitted),
        "companion_verification_status": getattr(
            result.audit, "companion_verification_status", "not_run"
        ),
        "companion_verification_issue_code": getattr(
            result.audit, "companion_verification_issue_code", ""
        ),
        "companion_verification_issue_detail": dict(
            getattr(result.audit, "companion_verification_issue_detail", {}) or {}
        ),
        "companion_candidate_cap": result.audit.companion_candidate_cap,
        "embedding_mode": result.audit.embedding_mode,
        "embedding_tendency_ranks": list(result.audit.embedding_tendency_ranks),
        "deep_check_results": [
            {
                "tendency_id": dcr.tendency_id,
                "tendency_name": dcr.tendency_name,
                "detected": dcr.detected,
                "confidence": dcr.confidence,
                "evidence": dcr.evidence,
                "sub_pattern": dcr.sub_pattern,
                "specific_passage": dcr.specific_passage[:200] if dcr.specific_passage else "",
                "severity": dcr.severity,
                "reason": dcr.reason,
            }
            for dcr in result.audit.deep_check_results
        ],
        "routing_decisions": [
            {
                "tendency_id": rd.tendency.tendency_id,
                "primary_model_id": rd.primary_model_id,
                "primary_activation_context": rd.primary_activation_context,
                "sub_pattern": rd.sub_pattern,
                "antidote_model_ids": list(rd.antidote_model_ids),
                "supporting_model_ids": list(rd.supporting_model_ids),
                "risk_model_ids": list(rd.risk_model_ids),
                "supporting_candidate_trace": [
                    asdict(item) for item in rd.supporting_candidate_trace
                ],
                "risk_candidate_trace": [
                    asdict(item) for item in rd.risk_candidate_trace
                ],
                "tiebreaker_supporting": (
                    asdict(rd.tiebreaker_supporting) if rd.tiebreaker_supporting else None
                ),
                "tiebreaker_risk": (
                    asdict(rd.tiebreaker_risk) if rd.tiebreaker_risk else None
                ),
            }
            for rd in result.audit.routing_decisions
        ],
    }
    from system_b.route_trace import build_route_trace_payload
    output["audit_summary"]["route_trace"] = build_route_trace_payload(output)

    # Prompt versions (from hardening sprint)
    if result.prompt_versions:
        output["prompt_versions"] = dict(result.prompt_versions)

    return output


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _contract_error(args: argparse.Namespace) -> str | None:
    """Return a CLI contract error message, or None when flags are coherent."""
    if args.extraction_json and args.new_contract:
        return (
            "--extraction-json cannot be used with --new-contract; "
            "ConversationContext requires --extraction-file and --conversation-file"
        )

    if args.extraction_json:
        return (
            "--extraction-json is no longer supported; use --extraction-file "
            "together with --conversation-file"
        )

    if args.new_contract and not (args.extraction_file and args.conversation_file):
        return "--new-contract requires both --extraction-file and --conversation-file"

    if args.extraction_file and not args.conversation_file:
        return (
            "--extraction-file requires --conversation-file for the "
            "ConversationContext runtime"
        )

    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run Lolla pipeline. File-based extraction + conversation inputs "
            "use ConversationContext by default."
        )
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--extraction-file", help="Path to extraction JSON file")
    group.add_argument(
        "--extraction-json",
        help="Deprecated compatibility input. Use --extraction-file and --conversation-file instead.",
    )
    parser.add_argument(
        "--env-file",
        help="Optional .env file path",
    )
    parser.add_argument(
        "--output",
        choices=("full", "summary"),
        default="full",
        help="Output mode: full JSON or markdown summary",
    )
    parser.add_argument(
        "--output-file",
        help="Write output JSON to this file instead of stdout",
    )
    parser.add_argument(
        "--skip-revision",
        action="store_true",
        help="Skip the OpenRouter revision step (use when Claude provides its own revision)",
    )
    parser.add_argument(
        "--conversation-file",
        help=(
            "Path to raw conversation transcript. With --extraction-file, this "
            "selects the default ConversationContext runtime."
        ),
    )
    parser.add_argument(
        "--new-contract",
        action="store_true",
        help=(
            "Deprecated compatibility alias for the default ConversationContext "
            "contract. No longer needed for file-based conversation runs."
        ),
    )
    parser.add_argument(
        "--embeddings",
        choices=("auto", "on", "off"),
        default="auto",
        help=(
            "Embedding-mode control for Lane 2 attribution: "
            "'auto' (default) enables embeddings when OPENAI_API_KEY is set; "
            "'on' requires the key and fails if absent; "
            "'off' disables embeddings regardless of env. The chosen mode is "
            "persisted in audit_summary.embedding_mode so reports can group "
            "without inspecting environment variables after the fact."
        ),
    )
    parser.add_argument(
        "--companion-candidate-cap",
        type=int,
        default=None,
        help=(
            "Override the Lane 2 candidate cap (default: 60). Diagnostic knob; "
            "do not tune this in production runs without an attribution-driven "
            "rationale (see research/lane2-attribution-design-2026-04-26.md)."
        ),
    )
    parser.add_argument(
        "--v60-enrichment",
        choices=("auto", "on", "off"),
        default="auto",
        help=(
            "Private V60 enrichment attached to result.json for the skill "
            "orchestrator. Default auto is ON unless LOLLA_V60_ENRICHMENT=off."
        ),
    )
    parser.add_argument(
        "--v60-affordances-path",
        type=Path,
        default=SKILL_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v60.json",
        help="Explicit V60 affordance artifact path. No latest-artifact selection.",
    )
    parser.add_argument(
        "--v60-max-cards",
        type=int,
        default=8,
        help="Maximum private V60 cards to attach to result.json.",
    )
    parser.add_argument(
        "--pre-step6-portfolio",
        choices=("off", "shadow", "step6_private"),
        default=None,
        help=(
            "Pre-Step-6 portfolio mode. 'shadow' records cached-card policy "
            "evidence only; 'step6_private' writes a private thinking-table "
            "sidecar for Step 6 without live deck generation or reviewer calls."
        ),
    )
    parser.add_argument(
        "--pre-step6-portfolio-cache-dir",
        type=Path,
        default=None,
        help=(
            "Directory containing precomputed pre-Step-6 card decks. Shadow mode "
            "does not generate decks when the cache misses."
        ),
    )
    parser.add_argument(
        "--pre-step6-portfolio-cache-ref",
        type=Path,
        default=None,
        help=(
            "Explicit precomputed pre-Step-6 card deck to load if the exact "
            "compiled-key cache file is absent. Intended for controlled "
            "operator-selected cache-hit tests."
        ),
    )
    args = parser.parse_args()

    contract_error = _contract_error(args)
    if contract_error:
        print(json.dumps({"status": "error", "error": contract_error}))
        return 1

    # Load env: explicit flag -> bundled skill .env -> global config.
    if args.env_file:
        _load_env_file(Path(args.env_file))
    else:
        for candidate in [
            SKILL_ROOT / ".env",
            Path.home() / ".config" / "lolla" / ".env",
        ]:
            if candidate.exists():
                _load_env_file(candidate)
                break

    try:
        risk_mode = audit_mode_from_env()
    except AuditModeError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 1

    if args.pre_step6_portfolio is None:
        env_mode = os.environ.get("LOLLA_PRE_STEP6_PORTFOLIO", "off").strip().lower()
        args.pre_step6_portfolio = (
            env_mode if env_mode in {"off", "shadow", "step6_private"} else "off"
        )
    if args.pre_step6_portfolio_cache_dir is None:
        env_cache_dir = os.environ.get("LOLLA_PRE_STEP6_PORTFOLIO_CACHE_DIR", "").strip()
        if env_cache_dir:
            args.pre_step6_portfolio_cache_dir = Path(env_cache_dir)
    if args.pre_step6_portfolio_cache_ref is None:
        env_cache_ref = os.environ.get("LOLLA_PRE_STEP6_PORTFOLIO_CACHE_REF", "").strip()
        if env_cache_ref:
            args.pre_step6_portfolio_cache_ref = Path(env_cache_ref)

    run_id_for_guard = (
        os.getenv("LOLLA_RUN_ID", "")
        or _derive_run_id_from_path(args.output_file)
        or _derive_run_id_from_path(args.extraction_file)
        or _derive_run_id_from_path(args.conversation_file)
    )
    try:
        assert_expected_run_state(
            actual_run_id=run_id_for_guard,
            artifact_paths=[
                args.extraction_file,
                args.conversation_file,
                args.output_file,
            ],
            phase="run_pipeline",
        )
    except SystemExit as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 1

    # Parse extraction
    if args.extraction_file:
        extraction_path = Path(args.extraction_file)
        if not extraction_path.exists():
            print(json.dumps({"status": "error", "error": f"File not found: {extraction_path}"}))
            return 1
        extraction = json.loads(extraction_path.read_text(encoding="utf-8"))
    else:
        extraction = json.loads(args.extraction_json)

    # Read upstream capture diagnostics (from run_extract.py)
    _capture_health = extraction.get("capture_health", "unknown")
    _capture_warnings = extraction.get("capture_warnings", [])
    _capture_manifest = extraction.get("capture_manifest")
    _capture_adequacy = extraction.get("capture_adequacy") or {}
    _processing_view = extraction.get("conversation_processing_view") or {}
    if not isinstance(_capture_adequacy, dict) or not _capture_adequacy:
        _capture_adequacy = build_capture_adequacy(
            conversation_text=Path(args.conversation_file).read_text(encoding="utf-8")
            if args.conversation_file
            else "",
            run_id=run_id_for_guard,
            capture_manifest=_capture_manifest,
            capture_health=str(_capture_health or ""),
            capture_warnings=_capture_warnings if isinstance(_capture_warnings, list) else [],
        )
    _quote_validation = extraction.get("extraction", {}).get("_quote_validation", {}) or {}
    _quote_fabricated_count = int(_quote_validation.get("fabricated", 0) or 0)
    _quote_retry_attempted = bool(_quote_validation.get("retry_attempted", False))
    _truncation_applied = bool(
        (_capture_manifest or {}).get("truncation_applied", False)
    )
    _omitted_turns = int((_capture_manifest or {}).get("omitted_turns", 0) or 0)
    _processing_view_status = str(
        (_processing_view or {}).get("status")
        or ("partial" if _truncation_applied else "full")
    )
    _preservation_value = (_processing_view or {}).get(
        "authoritative_conversation_preserved"
    )
    _authoritative_conversation_preserved = (
        bool(_preservation_value) if _preservation_value is not None else None
    )

    # Resolve data root and load pipeline
    data_root = _resolve_data_root()

    from system_b.pipeline import SystemBPipeline, PipelineConfig

    # Resolve embedding mode from explicit flag, falling back to env-driven auto.
    has_key = bool(os.environ.get("OPENAI_API_KEY", ""))
    if args.embeddings == "on":
        if not has_key:
            print(json.dumps({"status": "error", "error": "--embeddings on requires OPENAI_API_KEY"}))
            return 1
        enable_embeddings = True
    elif args.embeddings == "off":
        enable_embeddings = False
    else:  # auto
        enable_embeddings = has_key

    _tiebreaker_env = os.environ.get("LOLLA_ACTIVATION_TIEBREAKER", "").strip().lower()
    if _tiebreaker_env in ("0", "false", "no", "off"):
        activation_tiebreaker_enabled = False
    else:
        activation_tiebreaker_enabled = True

    candidate_cap = args.companion_candidate_cap if args.companion_candidate_cap is not None else 60

    config = PipelineConfig(
        enable_companion=True,
        enable_frame_pressure=True,
        enable_structural_coverage=True,
        enable_embeddings=enable_embeddings,
        activation_tiebreaker_enabled=activation_tiebreaker_enabled,
        companion_candidate_cap=candidate_cap,
    )

    try:
        pipeline = SystemBPipeline.load_live(
            root=data_root,
            provider_name="openrouter",
            config=config,
        )
    except Exception as exc:
        print(json.dumps({
            "status": "error",
            "error": f"Failed to load pipeline: {exc}",
        }))
        return 1

    # Capture diagnostics for audit output. Gate on config as well as retriever
    # presence so `--embeddings off` is reflected accurately even when an
    # OPENAI_API_KEY is set (retriever may be loaded but unused).
    _embedding_active = pipeline._embedding_retriever is not None and config.enable_embeddings
    _compiled_chunk_count = 0
    if pipeline._bundle_selector is not None:
        _compiled_chunk_count = len(pipeline._bundle_selector._substrate.all_chunks())

    from system_b.conversation_loader import load_conversation_context

    pipeline_input = load_conversation_context(
        extraction_path=Path(args.extraction_file),
        conversation_path=Path(args.conversation_file),
    )
    postprocessing_seed = _derive_postprocessing_seed(extraction, pipeline_input)
    case_focus = postprocessing_seed["case_focus"]
    audit_target_assistant_text = postprocessing_seed["audit_target_assistant_text"]
    user_context_text = _joined_turn_text(pipeline_input, "user")

    # Open a per-run embedding-usage scope. Every OpenAI embedding/expansion
    # call inside this scope is auto-recorded into ``embedding_usage_records``;
    # outside the scope, calls are silent. ContextVar-based, so per-run
    # isolation holds even under threading.
    from system_b.embedding_retriever import capture_usage as _capture_embedding_usage

    embedding_usage_records: list[dict] = []
    _embedding_capture_cm = _capture_embedding_usage()
    embedding_usage_records = _embedding_capture_cm.__enter__()

    try:
        result = pipeline.run(pipeline_input)
    except Exception as exc:
        _embedding_capture_cm.__exit__(None, None, None)
        print(json.dumps({
            "status": "error",
            "error": f"Pipeline execution failed: {exc}",
        }))
        return 1

    # Serialize
    serialized = _serialize_result(
        result,
        embedding_active=_embedding_active,
        compiled_chunk_count=_compiled_chunk_count,
    )
    apply_risk_mode_metadata(serialized, risk_mode)

    # Include the full conversation context as `extraction` for Observatory
    # + render_memo. They derive displayed case focus / audit target from the
    # joined turns and use decision_situation for case naming.
    serialized["extraction"] = _serialize_conversation_context(pipeline_input)

    # Revision step + Bullshit Index — run in parallel.
    # Revision: three cards through a second LLM to produce a revised answer.
    # BI: four-subtype detector on the assistant audit target (always-on).
    from concurrent.futures import ThreadPoolExecutor, as_completed

    revised_answer = None
    bullshit_profile_payload = None
    revision_call_log: list = []
    bi_call_log: list = []

    def _run_revision():
        if (
            args.skip_revision
            or not audit_target_assistant_text
            or not (result.delta_card and result.delta_card.findings)
        ):
            return None, []
        from system_b.testing_harness import build_revision_prompt
        from system_b.boundary_provider import load_boundary_client_from_env

        revision_prompt = build_revision_prompt(
            query=case_focus,
            vanilla_answer=audit_target_assistant_text,
            delta_card=result.delta_card,
            companion_card=result.companion_card,
            companion_cheat_sheet=result.companion_cheat_sheet,
        )
        client = load_boundary_client_from_env("openrouter")
        revision_result = client.run_json(
            system_prompt="You revise answers after reasoning pressure. Return strict JSON.",
            user_prompt=revision_prompt,
            stage="revision",
        )
        return revision_result.get("revised_answer"), list(getattr(client, "call_log", ()))

    def _run_bullshit_index():
        from system_b.boundary_provider import load_boundary_client_from_env
        from system_b.bullshit_index import evaluate_text

        client = load_boundary_client_from_env("openrouter")
        bi_context, context_custody = _build_bi_context(
            extraction=extraction,
            user_context_text=user_context_text,
            user_turn_count=sum(
                1 for turn in pipeline_input.turns if turn.speaker == "user"
            ),
            fallback_context_text=case_focus,
        )
        profile = evaluate_text(
            audit_target_assistant_text,
            client,
            context_summary=bi_context,
        )
        profile_payload = profile.to_payload()
        profile_payload["context_custody"] = context_custody
        return profile_payload, list(getattr(client, "call_log", ()))

    with ThreadPoolExecutor(max_workers=2) as post_pool:
        revision_future = post_pool.submit(_run_revision)
        bi_future = post_pool.submit(_run_bullshit_index)

        try:
            revised_answer, revision_call_log = revision_future.result()
        except Exception as exc:
            print(
                json.dumps({"warning": f"Revision step failed (non-fatal): {exc}"}),
                file=sys.stderr,
            )

        try:
            bullshit_profile_payload, bi_call_log = bi_future.result()
        except Exception as exc:
            print(
                json.dumps({"warning": f"Bullshit index failed (non-fatal): {exc}"}),
                file=sys.stderr,
            )

    serialized["revised_answer"] = revised_answer
    serialized["bullshit_profile"] = bullshit_profile_payload

    # Private V60 enrichment — product-runtime transport layer.
    #
    # This does not decide final wording and it is not a user-facing card
    # product. It attaches a compact, source-backed "silver platter" to
    # result.json so the skill-using LLM can consider, reject, defer, or keep
    # chunks private while writing Step 6. The SKILL persists the downstream
    # consideration ledger after the model has actually used or rejected it.
    from system_b.v60_enrichment import (
        build_v60_enrichment,
        disabled_v60_enrichment,
        error_v60_enrichment,
    )

    v60_enabled = _v60_mode_enabled(args.v60_enrichment)
    if not v60_enabled:
        serialized["v60_enrichment"] = disabled_v60_enrichment(
            "disabled_by_cli_or_LOLLA_V60_ENRICHMENT"
        )
    else:
        try:
            serialized["v60_enrichment"] = build_v60_enrichment(
                root=SKILL_ROOT,
                result_payload=serialized,
                conversation_context=pipeline_input,
                affordances_path=Path(args.v60_affordances_path),
                embedding_retriever=pipeline._embedding_retriever if enable_embeddings else None,
                embedding_api_key=os.environ.get("OPENAI_API_KEY", ""),
                enable_embeddings=enable_embeddings,
                max_cards=max(0, int(args.v60_max_cards)),
            )
        except Exception as exc:
            serialized["v60_enrichment"] = error_v60_enrichment(
                f"{type(exc).__name__}: {exc}"
            )

    stakeholder_check_call_log: list = []
    stakeholder_check_payload = None
    if _env_flag_enabled("LOLLA_STAKEHOLDER_CHECK"):
        try:
            from system_b.boundary_provider import load_boundary_client_from_env
            from system_b.stakeholder_assumption_check import (
                run_stakeholder_assumption_check,
            )

            stakeholder_boundary = load_boundary_client_from_env("openrouter")
            stakeholder_check_payload, stakeholder_check_call_log = (
                run_stakeholder_assumption_check(
                    extraction=serialized.get("extraction") or {},
                    result=serialized,
                    conversation_text=Path(args.conversation_file).read_text(encoding="utf-8"),
                    boundary=stakeholder_boundary,
                )
            )
        except Exception as exc:
            stakeholder_check_payload = {
                "status": "skipped_error",
                "triggered": True,
                "surface": False,
                "critical_actors": [],
                "chat_actors": [],
                "error": str(exc),
            }
            stakeholder_check_call_log = []
        serialized["stakeholder_assumption_check"] = stakeholder_check_payload

    # Close the embedding-usage scope. All embedding/expansion calls made
    # during pipeline + post-processing are now in ``embedding_usage_records``.
    _embedding_capture_cm.__exit__(None, None, None)

    # Build the canonical per-run usage_summary block from four streams:
    #   1. result.audit.boundary_calls — pipeline lane calls (already labeled)
    #   2. bi_call_log                  — Bullshit Index (auto-labeled "bullshit_index")
    #   3. revision_call_log            — Revision (labeled "revision")
    #   4. extraction sidecar           — Extraction (labeled "extraction" / "extraction_retry")
    # Plus embedding_usage_records and (later) Step-7 subagent records.
    from system_b.usage_summary import build_usage_summary, is_valid_run_id, load_extraction_sidecar

    # Resolve run_id with three fallbacks. The third (extraction_file) covers
    # the standard headless invocation in the docstring, where only
    # --extraction-file and --conversation-file are passed; without it,
    # load_extraction_sidecar("") returns [] and extraction's calls drop
    # silently from usage_summary.
    _run_id = (
        os.getenv("LOLLA_RUN_ID", "")
        or _derive_run_id_from_path(args.output_file)
        or _derive_run_id_from_path(args.extraction_file)
    )

    if args.pre_step6_portfolio == "step6_private":
        try:
            from system_b.pre_step6_private_table import (
                build_pre_step6_private_table,
                write_pre_step6_private_table_sidecars,
            )

            pre_step6_table, rendered_table = build_pre_step6_private_table(
                result_payload=serialized,
                cache_dir=args.pre_step6_portfolio_cache_dir,
                cache_ref=args.pre_step6_portfolio_cache_ref,
            )
            if _run_id and is_valid_run_id(_run_id):
                write_pre_step6_private_table_sidecars(
                    pre_step6_table,
                    rendered_table,
                    run_id=_run_id,
                )
            serialized["pre_step6_private_table"] = pre_step6_table
        except Exception as exc:
            serialized["pre_step6_private_table"] = {
                "schema_version": "pre_step6_private_table.v2",
                "status": "error",
                "runtime_policy": "step6_private_context",
                "promotion_effect": "none_private_context_only",
                "error": f"{type(exc).__name__}: {exc}",
                "gates": {
                    "step6_private_context_allowed": True,
                    "live_card_generation_allowed": False,
                    "normal_runtime_reviewer_calls": 0,
                    "code_visible_answer_selection_allowed": False,
                },
                "cost_envelope": {
                    "normal_runtime_reviewer_calls": 0,
                    "live_card_generation_allowed": False,
                    "net_new_llm_calls": 0,
                },
            }
    elif args.pre_step6_portfolio == "shadow":
        try:
            from system_b.pre_step6_shadow_portfolio import (
                build_pre_step6_shadow_portfolio,
                write_pre_step6_shadow_portfolio_sidecar,
            )

            pre_step6_shadow = build_pre_step6_shadow_portfolio(
                result_payload=serialized,
                mode="shadow",
                cache_dir=args.pre_step6_portfolio_cache_dir,
                cache_ref=args.pre_step6_portfolio_cache_ref,
            )
            serialized["pre_step6_shadow_portfolio"] = pre_step6_shadow
            if _run_id and is_valid_run_id(_run_id):
                write_pre_step6_shadow_portfolio_sidecar(
                    pre_step6_shadow,
                    run_id=_run_id,
                )
        except Exception as exc:
            serialized["pre_step6_shadow_portfolio"] = {
                "schema_version": "pre_step6_shadow_portfolio.v1",
                "status": "shadow_error",
                "mode": "shadow",
                "promotion_effect": "none_shadow_only",
                "error": f"{type(exc).__name__}: {exc}",
                "shadow_visibility_decision": {
                    "result": "current_step6_visible_shadow_error",
                    "why": "Shadow portfolio recorder failed; visible output remains unchanged.",
                    "cognitive_signal_source": "not_run",
                    "normal_runtime_reviewer_calls": 0,
                    "applied_to_user_visible_output": False,
                },
                "gates": {
                    "runtime_wiring_allowed": False,
                    "skill_update_allowed": False,
                    "visible_behavior_change_allowed": False,
                },
            }

    _v60_skeleton = (
        (serialized.get("v60_enrichment") or {}).get("consideration_ledger_skeleton")
        if isinstance(serialized.get("v60_enrichment"), dict)
        else None
    )
    if _run_id and is_valid_run_id(_run_id) and isinstance(_v60_skeleton, dict):
        try:
            _write_private_text(
                Path(f"/tmp/lolla_{_run_id}_v60_ledger_skeleton.json"),
                json.dumps(_v60_skeleton, indent=2, ensure_ascii=False),
            )
        except OSError as exc:
            _warnings_for_skeleton = serialized.setdefault("warnings", [])
            if isinstance(_warnings_for_skeleton, list):
                _warnings_for_skeleton.append(f"V60 ledger skeleton sidecar write failed: {exc}")

    extraction_boundary_calls = load_extraction_sidecar(_run_id)
    all_chat_boundary_records = (
        list(getattr(result.audit, "boundary_calls", ()))
        + list(bi_call_log)
        + list(revision_call_log)
        + list(stakeholder_check_call_log)
        + list(extraction_boundary_calls)
    )
    _reasoning_warning, _reasoning_warning_meta = _reasoning_detail_warning(
        all_chat_boundary_records
    )
    if _reasoning_warning:
        audit_warnings = serialized.setdefault("audit_summary", {}).setdefault("warnings", [])
        if isinstance(audit_warnings, list) and _reasoning_warning not in audit_warnings:
            audit_warnings.append(_reasoning_warning)
    _provider_failure_warning, _provider_failure_meta = _provider_call_failure_warning(
        all_chat_boundary_records
    )
    if _provider_failure_warning:
        audit_warnings = serialized.setdefault("audit_summary", {}).setdefault("warnings", [])
        if isinstance(audit_warnings, list) and _provider_failure_warning not in audit_warnings:
            audit_warnings.append(_provider_failure_warning)

    serialized["usage_summary"] = build_usage_summary(
        run_id=_run_id,
        pipeline_boundary_calls=getattr(result.audit, "boundary_calls", ()),
        bi_boundary_calls=bi_call_log,
        revision_boundary_calls=revision_call_log,
        stakeholder_check_boundary_calls=stakeholder_check_call_log,
        extraction_boundary_calls=extraction_boundary_calls,
        embedding_records=embedding_usage_records,
        # subagent_calls are added by SKILL.md Step 8b after sub-agents return.
        subagent_calls=(),
    )

    # Decomposed run health
    _substrate_ok = _compiled_chunk_count > 0
    _fingerprint_ok = len(result.audit.companion_fingerprint_validated) > 0
    _has_findings = bool(result.delta_card and result.delta_card.findings)
    _warnings = list(result.audit.warnings)
    if _reasoning_warning and _reasoning_warning not in _warnings:
        _warnings.append(_reasoning_warning)
    if _provider_failure_warning and _provider_failure_warning not in _warnings:
        _warnings.append(_provider_failure_warning)
    _lane3_drops_count = len(getattr(result.frame_pressure_card, "dropped_frame_elements", ()) or ())
    _lane3_kept_count = len(getattr(result.frame_pressure_card, "frame_elements", ()) or ())
    _bi_evaluation_failures = int(
        ((bullshit_profile_payload or {}).get("summary", {}) or {}).get("evaluation_failures", 0) or 0
    )
    _bi_evaluation_count = int(
        ((bullshit_profile_payload or {}).get("summary", {}) or {}).get(
            "evaluation_passage_count", 0
        )
        or 0
    )
    # All frame elements dropped = Lane 3 effectively disabled by validation.
    # Partial drops are tolerated (some elements kept).
    _lane3_all_dropped = _lane3_drops_count > 0 and _lane3_kept_count == 0

    _health_issue_details: list[dict[str, object]] = []
    if not _substrate_ok:
        _health_issue_details.append(_health_issue_detail("substrate_empty"))
    if not _embedding_active:
        _health_issue_details.append(
            _health_issue_detail(
                "embeddings_off",
                severity="degraded" if config.enable_embeddings else "optional_off",
                trust_impact=(
                    "Embedding mode expected an active retriever, but none was available."
                    if config.enable_embeddings
                    else None
                ),
                mode=args.embeddings,
                enabled_by_config=config.enable_embeddings,
                openai_key_present=has_key,
            )
        )
    if not _fingerprint_ok and config.enable_companion:
        _health_issue_details.append(_health_issue_detail("no_fingerprint"))
    _companion_verification_status = str(
        (serialized.get("audit_summary") or {}).get("companion_verification_status") or ""
    )
    if _companion_verification_status == "malformed":
        _companion_issue = dict(
            (serialized.get("audit_summary") or {}).get("companion_verification_issue_detail")
            or {}
        )
        _health_issue_details.append(
            _health_issue_detail(
                "companion_verification_parse_failed",
                reason=_companion_issue.get("reason"),
                candidate_count=_companion_issue.get("candidate_count"),
                raw_message_content_present=_companion_issue.get(
                    "raw_message_content_present"
                ),
                raw_message_char_count=_companion_issue.get("raw_message_char_count"),
                raw_content_has_accepted_token=_companion_issue.get(
                    "raw_content_has_accepted_token"
                ),
                raw_content_has_rejected_token=_companion_issue.get(
                    "raw_content_has_rejected_token"
                ),
            )
        )
    if bool(_reasoning_warning_meta.get("detected")):
        _health_issue_details.append(
            _health_issue_detail(
                "vendor_boundary_reasoning_leak",
                leak_count=int(_reasoning_warning_meta.get("count") or 0),
                models=list(_reasoning_warning_meta.get("models") or []),
                stages=list(_reasoning_warning_meta.get("stages") or []),
            )
        )
    if int(_provider_failure_meta.get("failed_call_count") or 0) > 0:
        _health_issue_details.append(
            _health_issue_detail(
                "provider_call_terminal_loss",
                failed_call_count=int(
                    _provider_failure_meta.get("failed_call_count") or 0
                ),
                attempted_failed_call_count=int(
                    _provider_failure_meta.get("attempted_failed_call_count") or 0
                ),
                stages=list(_provider_failure_meta.get("stages") or []),
                tendency_ids=list(_provider_failure_meta.get("tendency_ids") or []),
                status_counts=dict(
                    _provider_failure_meta.get("status_counts") or {}
                ),
                provider_error_type_counts=dict(
                    _provider_failure_meta.get("provider_error_type_counts") or {}
                ),
                provider_error_code_counts=dict(
                    _provider_failure_meta.get("provider_error_code_counts") or {}
                ),
                providers=list(_provider_failure_meta.get("providers") or []),
                models=list(_provider_failure_meta.get("models") or []),
            )
        )
    _non_boundary_warnings = [
        warning
        for warning in _warnings
        if warning
        and warning != _reasoning_warning
        and warning != _provider_failure_warning
    ]
    if _non_boundary_warnings:
        _health_issue_details.append(_health_issue_detail("pipeline_warnings"))
    _capture_adequacy_status = str(_capture_adequacy.get("status") or "")
    if _capture_health == "critical" or _capture_adequacy_status == "critical":
        _health_issue_details.append(_health_issue_detail("capture_critical"))
    elif _capture_health == "degraded" or (
        _capture_adequacy_status == "warn" and not _truncation_applied
    ):
        _health_issue_details.append(_health_issue_detail("capture_degraded"))
    if _quote_fabricated_count > 0:
        # Fabricated passages survived the extraction retry (if any was attempted).
        # Surface so Step 4 chat can warn the user about partial extraction quality.
        _health_issue_details.append(
            _health_issue_detail("quote_fabrication", fabricated_count=_quote_fabricated_count)
        )
    if _truncation_applied:
        # The authoritative conversation remains intact. Only the initial
        # semantic extraction call used the bounded first-N + last-N view;
        # later conversation-native lanes still receive the full source.
        _health_issue_details.append(
            _health_issue_detail(
                "extraction_processing_view_partial",
                omitted_turns=_omitted_turns,
                authoritative_conversation_preserved=_authoritative_conversation_preserved,
            )
        )
    if _lane3_all_dropped:
        # Every frame element failed validation — Lane 3 produced no reframings
        # despite the extractor attempting. Different from "no frame elements
        # detected" (which is a legitimate zero); this is "all detected but all
        # dropped by the evidence_quote/pattern validator."
        _health_issue_details.append(
            _health_issue_detail("lane3_all_dropped", dropped_count=_lane3_drops_count)
        )
    if _bi_evaluation_failures:
        # Passage-level BI calls can fail and still produce a profile for the
        # remaining passages. Surface partial evaluator loss in run health.
        _health_issue_details.append(
            _health_issue_detail(
                "bullshit_index_partial",
                evaluation_failures=_bi_evaluation_failures,
                evaluation_count=_bi_evaluation_count,
            )
        )
    if (
        stakeholder_check_payload
        and stakeholder_check_payload.get("status") == "skipped_error"
        and stakeholder_check_payload.get("triggered")
    ):
        _health_issue_details.append(_health_issue_detail("stakeholder_check_failed"))
    _v60 = serialized.get("v60_enrichment") or {}
    _v60_status = str(_v60.get("status") or "")
    if v60_enabled and _v60_status != "active":
        _health_issue_details.append(
            _health_issue_detail("v60_enrichment_failed", v60_status=_v60_status or "unknown")
        )
    _pre_step6_shadow = serialized.get("pre_step6_shadow_portfolio") or {}
    _pre_step6_shadow_status = (
        str(_pre_step6_shadow.get("status") or "")
        if isinstance(_pre_step6_shadow, dict)
        else ""
    )

    _health_issues = [str(detail["code"]) for detail in _health_issue_details]
    _overall = _overall_health_from_issue_details(_health_issue_details)

    serialized["run_health"] = {
        "overall": _overall,
        "capture": _capture_health,
        "substrate": "ok" if _substrate_ok else "empty",
        "embeddings": "active" if _embedding_active else "off",
        "fingerprint": "ok" if _fingerprint_ok else "empty",
        "findings_produced": _has_findings,
        "quote_fabrication_count": _quote_fabricated_count,
        "quote_retry_attempted": _quote_retry_attempted,
        # Deprecated compatibility alias. This means the bounded extraction
        # view was partial; it does not mean conversation.txt was truncated.
        "capture_truncated": _truncation_applied,
        "omitted_turns": _omitted_turns,
        "authoritative_conversation_preserved": _authoritative_conversation_preserved,
        "extraction_processing_view_status": _processing_view_status,
        "processing_view_omitted_turns": _omitted_turns,
        "lane3_frame_drops_count": _lane3_drops_count,
        "lane3_frame_kept_count": _lane3_kept_count,
        "bullshit_index_evaluation_failures": _bi_evaluation_failures,
        "bullshit_index_evaluation_count": _bi_evaluation_count,
        "issues": _health_issues,
        "issue_details": _health_issue_details,
        "issue_axis_counts": _health_issue_axis_counts(_health_issue_details),
        "partial_health_causes": [
            str(detail["code"])
            for detail in _health_issue_details
            if str(detail.get("severity") or "") == "partial"
        ],
        "warnings": _warnings + _capture_warnings,
        "boundary_reasoning_leak_detected": bool(_reasoning_warning_meta.get("detected")),
        "boundary_reasoning_leak_count": int(_reasoning_warning_meta.get("count") or 0),
        "boundary_reasoning_leak_models": list(_reasoning_warning_meta.get("models") or []),
        "boundary_reasoning_leak_stages": list(_reasoning_warning_meta.get("stages") or []),
        "provider_call_health": str(
            _provider_failure_meta.get("status") or "unknown"
        ),
        "provider_failed_call_count": int(
            _provider_failure_meta.get("failed_call_count") or 0
        ),
        "provider_failed_call_stages": list(
            _provider_failure_meta.get("stages") or []
        ),
        "provider_failed_tendency_ids": list(
            _provider_failure_meta.get("tendency_ids") or []
        ),
        "provider_failed_status_counts": dict(
            _provider_failure_meta.get("status_counts") or {}
        ),
        "activation_tiebreaker": "on" if activation_tiebreaker_enabled else "off",
        "v60_enrichment": _v60_status or "unknown",
        "v60_selected_chunk_count": int(
            ((_v60.get("telemetry") or {}).get("selected_chunk_count", 0) or 0)
        ),
    }
    if _pre_step6_shadow_status:
        serialized["run_health"]["pre_step6_shadow_portfolio"] = _pre_step6_shadow_status
    _pre_step6_private = serialized.get("pre_step6_private_table") or {}
    _pre_step6_private_status = (
        str(_pre_step6_private.get("status") or "")
        if isinstance(_pre_step6_private, dict)
        else ""
    )
    if _pre_step6_private_status:
        serialized["run_health"]["pre_step6_private_table"] = _pre_step6_private_status
    if stakeholder_check_payload:
        serialized["run_health"]["stakeholder_assumption_check"] = stakeholder_check_payload.get("status")
    if _capture_manifest:
        serialized["run_health"]["capture_manifest"] = _capture_manifest
    if _capture_adequacy:
        serialized["run_health"]["capture_adequacy"] = _capture_adequacy
    refresh_provider_boundary_health(serialized["run_health"])

    # Output
    if args.output == "summary":
        from system_b.operator_summary import (
            render_pipeline_summary_markdown,
            summarize_pipeline_result,
        )
        full_payload = dict(serialized)
        full_payload["audit"] = asdict(result.audit)
        summary = summarize_pipeline_result(full_payload, root=data_root)
        markdown = render_pipeline_summary_markdown(summary)
        output = {
            "status": "ok",
            "format": "markdown",
            "markdown": markdown,
            "detected_tendencies": list(result.detected_tendencies),
            "revised_answer": revised_answer,
        }
    else:
        output = {
            "status": "ok",
            "format": "json",
            **serialized,
        }

    output_text = json.dumps(output, indent=2, ensure_ascii=False)
    if args.output_file:
        _write_private_text(Path(args.output_file), output_text)
        print(f"Pipeline result written to {args.output_file}")
    else:
        print(output_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
