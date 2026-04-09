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

def _serialize_result(result) -> dict:
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

    # Audit summary with companion diagnostics
    output["audit_summary"] = {
        "triage_scores": [
            {"tendency_id": s.tendency_id, "score": s.score, "evidence": s.evidence}
            for s in result.audit.triage_scores
        ],
        "triggered_tendencies": list(result.audit.triggered_tendencies),
        "boundary_call_count": len(result.audit.boundary_calls),
        "warnings": list(result.audit.warnings),
        "companion_fingerprint_raw": list(result.audit.companion_fingerprint_raw),
        "companion_fingerprint_validated": list(result.audit.companion_fingerprint_validated),
        "companion_fingerprint_dropped": list(result.audit.companion_fingerprint_dropped),
        "companion_detected_models": list(result.audit.companion_detected_models),
        "companion_rejected_models": list(result.audit.companion_rejected_models),
    }

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

    config = PipelineConfig(
        enable_companion=True,
        enable_frame_pressure=True,
        enable_embeddings=has_embeddings,
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
    serialized = _serialize_result(result)

    # Include query and vanilla_answer in output (for Observatory)
    serialized["query"] = query
    serialized["vanilla_answer"] = vanilla_answer

    # Revision step — run the three cards through a second LLM to produce
    # a revised answer that incorporates the structural pressure.
    # Skipped when --skip-revision is set (skill flow uses Claude's own revision).
    revised_answer = None
    if not args.skip_revision and result.delta_card and result.delta_card.findings:
        try:
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
            revised_answer = revision_result.get("revised_answer")
        except Exception as exc:
            print(
                json.dumps({"warning": f"Revision step failed (non-fatal): {exc}"}),
                file=sys.stderr,
            )

    serialized["revised_answer"] = revised_answer

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
