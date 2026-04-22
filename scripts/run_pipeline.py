#!/usr/bin/env python3
"""Run the full Lolla pipeline against an extracted conversation.

Takes extraction JSON (with query + vanilla_answer fields) and runs all
three lanes (structural pressure, model companion, frame pressure) via
OpenRouter.

Usage:
    python3 scripts/run_pipeline.py --extraction-file /tmp/extraction.json
    python3 scripts/run_pipeline.py --extraction-json '{"query":"...","vanilla_answer":"..."}'

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


def _extract_user_turns(conversation_path: Path) -> str:
    """Extract user messages from a conversation transcript.

    Returns the full text of all user turns, giving the BI judge
    visibility into what facts were established in conversation.
    """
    import re
    text = conversation_path.read_text(encoding="utf-8")
    parts = re.split(r"\[Turn \d+\] (USER|ASSISTANT):", text)
    user_texts = []
    for i in range(1, len(parts) - 1, 2):
        role = parts[i].strip()
        content = parts[i + 1].strip()
        if role == "USER" and content:
            user_texts.append(content)
    return "\n\n".join(user_texts)


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
        "boundary_calls": [
            {
                "stage": bc.stage,
                "tendency_id": bc.tendency_id,
                "provider_name": bc.provider_name,
                "model": bc.model,
                "status": bc.status,
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
        "deep_check_results": [
            {
                "tendency_id": dcr.tendency_id,
                "tendency_name": dcr.tendency_name,
                "detected": dcr.detected,
                "confidence": dcr.confidence,
                "sub_pattern": dcr.sub_pattern,
                "specific_passage": dcr.specific_passage[:200] if dcr.specific_passage else "",
                "severity": dcr.severity,
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

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Lolla pipeline against extracted conversation"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--extraction-file", help="Path to extraction JSON file")
    group.add_argument("--extraction-json", help="Extraction JSON as string")
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
        help="Path to raw conversation transcript (provides full context for BI evaluation)",
    )
    args = parser.parse_args()

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

    # Support both raw {query, vanilla_answer} and wrapped {critique_request: {...}}
    if "critique_request" in extraction:
        cr = extraction["critique_request"]
    else:
        cr = extraction

    query = cr.get("query", "")
    vanilla_answer = cr.get("vanilla_answer", "")

    # Load full conversation context for BI evaluation if available
    _conversation_context = ""
    if args.conversation_file:
        conv_path = Path(args.conversation_file)
        if conv_path.exists():
            _conversation_context = _extract_user_turns(conv_path)

    # Read upstream capture diagnostics (from run_extract.py)
    _capture_health = extraction.get("capture_health", "unknown")
    _capture_warnings = extraction.get("capture_warnings", [])
    _capture_manifest = extraction.get("capture_manifest")
    _quote_validation = extraction.get("extraction", {}).get("_quote_validation", {}) or {}
    _quote_fabricated_count = int(_quote_validation.get("fabricated", 0) or 0)
    _quote_retry_attempted = bool(_quote_validation.get("retry_attempted", False))

    if not query or not vanilla_answer:
        print(json.dumps({
            "status": "error",
            "error": "Extraction must contain non-empty 'query' and 'vanilla_answer' fields",
        }))
        return 1

    # Resolve data root and load pipeline
    data_root = _resolve_data_root()

    from system_b.pipeline import SystemBPipeline, CritiqueRequest, PipelineConfig

    has_embeddings = bool(os.environ.get("OPENAI_API_KEY", ""))

    _tiebreaker_env = os.environ.get("LOLLA_ACTIVATION_TIEBREAKER", "").strip().lower()
    if _tiebreaker_env in ("0", "false", "no", "off"):
        activation_tiebreaker_enabled = False
    else:
        activation_tiebreaker_enabled = True

    config = PipelineConfig(
        enable_companion=True,
        enable_frame_pressure=True,
        enable_structural_coverage=True,
        enable_embeddings=has_embeddings,
        activation_tiebreaker_enabled=activation_tiebreaker_enabled,
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

    # Capture diagnostics for audit output
    _embedding_active = pipeline._embedding_retriever is not None
    _compiled_chunk_count = 0
    if pipeline._bundle_selector is not None:
        _compiled_chunk_count = len(pipeline._bundle_selector._substrate.all_chunks())

    # Run pipeline
    request = CritiqueRequest(query=query, vanilla_answer=vanilla_answer)

    try:
        result = pipeline.run(request)
    except Exception as exc:
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

    # Include query and vanilla_answer in output (for Observatory)
    serialized["query"] = query
    serialized["vanilla_answer"] = vanilla_answer

    # Revision step + Bullshit Index — run in parallel.
    # Revision: three cards through a second LLM to produce a revised answer.
    # BI: four-subtype detector on the vanilla answer (always-on).
    from concurrent.futures import ThreadPoolExecutor, as_completed

    revised_answer = None
    bullshit_profile_payload = None

    def _run_revision():
        if args.skip_revision or not (result.delta_card and result.delta_card.findings):
            return None
        from system_b.testing_harness import build_revision_prompt
        from system_b.boundary_provider import load_boundary_client_from_env

        revision_prompt = build_revision_prompt(
            query=query,
            vanilla_answer=vanilla_answer,
            delta_card=result.delta_card,
            companion_card=result.companion_card,
            companion_cheat_sheet=result.companion_cheat_sheet,
        )
        client = load_boundary_client_from_env("openrouter")
        revision_result = client.run_json(
            system_prompt="You revise answers after reasoning pressure. Return strict JSON.",
            user_prompt=revision_prompt,
        )
        return revision_result.get("revised_answer")

    def _run_bullshit_index():
        from system_b.boundary_provider import load_boundary_client_from_env
        from system_b.bullshit_index import evaluate_text

        client = load_boundary_client_from_env("openrouter")
        # Prefer structured fact registry from extraction (compact, precise).
        # Fall back to raw conversation truncation when extraction unavailable.
        fact_registry = _build_fact_registry(extraction)
        if fact_registry:
            bi_context = fact_registry
        elif _conversation_context:
            bi_context = _conversation_context[:4000]
        else:
            bi_context = query
        profile = evaluate_text(
            vanilla_answer,
            client,
            context_summary=bi_context,
        )
        return profile.to_payload()

    with ThreadPoolExecutor(max_workers=2) as post_pool:
        revision_future = post_pool.submit(_run_revision)
        bi_future = post_pool.submit(_run_bullshit_index)

        try:
            revised_answer = revision_future.result()
        except Exception as exc:
            print(
                json.dumps({"warning": f"Revision step failed (non-fatal): {exc}"}),
                file=sys.stderr,
            )

        try:
            bullshit_profile_payload = bi_future.result()
        except Exception as exc:
            print(
                json.dumps({"warning": f"Bullshit index failed (non-fatal): {exc}"}),
                file=sys.stderr,
            )

    serialized["revised_answer"] = revised_answer
    serialized["bullshit_profile"] = bullshit_profile_payload

    # Decomposed run health
    _substrate_ok = _compiled_chunk_count > 0
    _fingerprint_ok = len(result.audit.companion_fingerprint_validated) > 0
    _has_findings = bool(result.delta_card and result.delta_card.findings)
    _warnings = list(result.audit.warnings)

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
