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
import json
import os
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Path resolution — find pipeline package
# ---------------------------------------------------------------------------

SKILL_ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = SKILL_ROOT / "engine"
MAX_POSTPROCESSING_ASSISTANT_CHARS = 40_000

if (ENGINE_DIR / "system_b" / "__init__.py").exists():
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

    Produces a compact context string for the BI judge, replacing raw
    conversation truncation with structured facts the user established.
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
        parts.append("\nEstablished facts:")
        for c in constraints:
            constraint = c.get("constraint", "")
            weight = c.get("weight", "")
            status = c.get("status", "")
            if constraint:
                parts.append(f"- {constraint} (weight: {weight}, status: {status})")

    # Dropped threads
    threads = ext.get("dropped_threads", [])
    if threads:
        parts.append("\nDropped threads:")
        for t in threads:
            thread = t.get("thread", "")
            status = t.get("status", "")
            if thread:
                parts.append(f"- DROPPED: {thread} (status: {status})")

    return "\n".join(parts) if parts else ""


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
                "model": bc.model,
                "status": bc.status,
                "finish_reason": bc.finish_reason,
                "raw_message_content": bc.raw_message_content,
                "temperature": bc.temperature,
                "prompt_tokens": bc.prompt_tokens,
                "completion_tokens": bc.completion_tokens,
                "total_tokens": bc.total_tokens,
                "cached_tokens": bc.cached_tokens,
                "cache_write_tokens": bc.cache_write_tokens,
                "reasoning_tokens": bc.reasoning_tokens,
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
                "sub_pattern": rd.sub_pattern,
                "antidote_model_ids": list(rd.antidote_model_ids),
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
    args = parser.parse_args()

    contract_error = _contract_error(args)
    if contract_error:
        print(json.dumps({"status": "error", "error": contract_error}))
        return 1

    # Load env: explicit flag → project .claude/lolla.env → repo .env → ~/.config/lolla/.env
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
    _quote_validation = extraction.get("extraction", {}).get("_quote_validation", {}) or {}
    _quote_fabricated_count = int(_quote_validation.get("fabricated", 0) or 0)
    _quote_retry_attempted = bool(_quote_validation.get("retry_attempted", False))
    _truncation_applied = bool(
        (_capture_manifest or {}).get("truncation_applied", False)
    )
    _omitted_turns = int((_capture_manifest or {}).get("omitted_turns", 0) or 0)

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
        # Prefer structured fact registry from extraction (compact, precise).
        # Fall back to raw conversation truncation when extraction unavailable.
        fact_registry = _build_fact_registry(extraction)
        if fact_registry:
            bi_context = fact_registry
        elif user_context_text:
            bi_context = user_context_text[:4000]
        else:
            bi_context = case_focus
        profile = evaluate_text(
            audit_target_assistant_text,
            client,
            context_summary=bi_context,
        )
        return profile.to_payload(), list(getattr(client, "call_log", ()))

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

    # Close the embedding-usage scope. All embedding/expansion calls made
    # during pipeline + post-processing are now in ``embedding_usage_records``.
    _embedding_capture_cm.__exit__(None, None, None)

    # Build the canonical per-run usage_summary block from four streams:
    #   1. result.audit.boundary_calls — pipeline lane calls (already labeled)
    #   2. bi_call_log                  — Bullshit Index (auto-labeled "bullshit_index")
    #   3. revision_call_log            — Revision (labeled "revision")
    #   4. extraction sidecar           — Extraction (labeled "extraction" / "extraction_retry")
    # Plus embedding_usage_records and (later) Step-7 subagent records.
    from system_b.usage_summary import build_usage_summary, load_extraction_sidecar

    def _derive_run_id_from_path(raw_path: str | None) -> str:
        """Pull <run_id> out of a path like ``lolla_<run_id>_*.{json,txt}``."""
        if not raw_path:
            return ""
        stem = Path(raw_path).stem
        parts = stem.split("_")
        if len(parts) >= 2 and parts[0] == "lolla":
            return parts[1]
        return ""

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

    serialized["usage_summary"] = build_usage_summary(
        run_id=_run_id,
        pipeline_boundary_calls=getattr(result.audit, "boundary_calls", ()),
        bi_boundary_calls=bi_call_log,
        revision_boundary_calls=revision_call_log,
        extraction_boundary_calls=load_extraction_sidecar(_run_id),
        embedding_records=embedding_usage_records,
        # subagent_calls are added by SKILL.md Step 8b after sub-agents return.
        subagent_calls=(),
    )

    # Decomposed run health
    _substrate_ok = _compiled_chunk_count > 0
    _fingerprint_ok = len(result.audit.companion_fingerprint_validated) > 0
    _has_findings = bool(result.delta_card and result.delta_card.findings)
    _warnings = list(result.audit.warnings)
    _lane3_drops_count = len(getattr(result.frame_pressure_card, "dropped_frame_elements", ()) or ())
    _lane3_kept_count = len(getattr(result.frame_pressure_card, "frame_elements", ()) or ())
    _bi_evaluation_failures = int(
        ((bullshit_profile_payload or {}).get("summary", {}) or {}).get("evaluation_failures", 0) or 0
    )
    # All frame elements dropped = Lane 3 effectively disabled by validation.
    # Partial drops are tolerated (some elements kept).
    _lane3_all_dropped = _lane3_drops_count > 0 and _lane3_kept_count == 0

    _health_issues = []
    if not _substrate_ok:
        _health_issues.append("substrate_empty")
    if not _embedding_active:
        _health_issues.append("embeddings_off")
    if not _fingerprint_ok and config.enable_companion:
        _health_issues.append("no_fingerprint")
    if _warnings:
        _health_issues.append("pipeline_warnings")
    if _capture_health == "critical":
        _health_issues.append("capture_critical")
    elif _capture_health == "degraded":
        _health_issues.append("capture_degraded")
    if _quote_fabricated_count > 0:
        # Fabricated passages survived the extraction retry (if any was attempted).
        # Surface so Step 4 chat can warn the user about partial extraction quality.
        _health_issues.append("quote_fabrication")
    if _truncation_applied:
        # Conversation was truncated to fit the 80K char cap. Middle turns
        # dropped; audit ran on first-N + last-N slices.
        _health_issues.append("capture_truncated")
    if _lane3_all_dropped:
        # Every frame element failed validation — Lane 3 produced no reframings
        # despite the extractor attempting. Different from "no frame elements
        # detected" (which is a legitimate zero); this is "all detected but all
        # dropped by the evidence_quote/pattern validator."
        _health_issues.append("lane3_all_dropped")
    if _bi_evaluation_failures:
        # Passage-level BI calls can fail and still produce a profile for the
        # remaining passages. Surface partial evaluator loss in run health.
        _health_issues.append("bullshit_index_partial")

    # Overall health: critical if capture is critical, degraded if any issues
    if "capture_critical" in _health_issues:
        _overall = "critical"
    elif _health_issues:
        _overall = "degraded"
    else:
        _overall = "healthy"

    serialized["run_health"] = {
        "overall": _overall,
        "capture": _capture_health,
        "substrate": "ok" if _substrate_ok else "empty",
        "embeddings": "active" if _embedding_active else "off",
        "fingerprint": "ok" if _fingerprint_ok else "empty",
        "findings_produced": _has_findings,
        "quote_fabrication_count": _quote_fabricated_count,
        "quote_retry_attempted": _quote_retry_attempted,
        "capture_truncated": _truncation_applied,
        "omitted_turns": _omitted_turns,
        "lane3_frame_drops_count": _lane3_drops_count,
        "lane3_frame_kept_count": _lane3_kept_count,
        "bullshit_index_evaluation_failures": _bi_evaluation_failures,
        "issues": _health_issues,
        "warnings": _warnings + _capture_warnings,
        "activation_tiebreaker": "on" if activation_tiebreaker_enabled else "off",
    }
    if _capture_manifest:
        serialized["run_health"]["capture_manifest"] = _capture_manifest

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
        Path(args.output_file).write_text(output_text, encoding="utf-8")
        print(f"Pipeline result written to {args.output_file}")
    else:
        print(output_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
