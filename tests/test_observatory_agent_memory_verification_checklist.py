from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.conversation_memory_renderer import (
    render_conversation_memory_markdown,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-agent-memory-verification-checklist-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-agent-memory-verification-checklist-v0/"
    "review.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_verification_checklist_slice_is_registered_and_gated() -> None:
    doc = _read(DOC)
    readme = _read(README)
    review = json.loads(_read(REVIEW))

    assert "Observatory Agent Memory Verification Checklist" in readme
    assert "observatory-agent-memory-verification-checklist-v0.md" in readme
    assert "Decision gate: `proceed_to_agent_memory_source_locator_spike`" in doc
    assert review["decision_gate"] == "proceed_to_agent_memory_source_locator_spike"
    assert review["implemented"]["claim_verification_checklist_rendered"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False


def test_renderer_checklist_is_a_source_inspection_index() -> None:
    markdown = render_conversation_memory_markdown(
        {
            "case": {
                "case_id": "sample-case",
                "run_id": "20260707T000000Z_test",
                "decision_situation": "Whether to launch the beta after a mixed review.",
            },
            "conversation_interpretation": {
                "synthesized_position": "Launch only if a narrow gate passes.",
            },
            "advice_delta": {
                "changed_advice_summary": [
                    "Add a launch gate before relying on the enterprise signal."
                ],
                "main_counter_pressure": "The launch gate was under-specified.",
            },
            "decision_summary": {
                "revised_answer": "Launch only if the gate passes.",
            },
            "open_questions": {
                "items": [
                    {
                        "question": "Who owns the launch gate?",
                        "source_refs": ["agent_result.json"],
                        "evidence_label": "source",
                    }
                ],
            },
            "run_health": {
                "evaluation_overall": "warn",
                "trace_adequacy_status": "thin",
                "future_review_ready": False,
            },
        }
    )

    assert markdown.index("## Cold Reader Orientation") < markdown.index(
        "## Claim Verification Checklist"
    )
    assert markdown.index("## Claim Verification Checklist") < markdown.index(
        "## What This File Is"
    )
    assert "Evidence label: `synthesis_to_verify`" in markdown
    assert "Use this as a checking index, not as a conclusion." in markdown
    assert "does not prove any claim, certify advice, or replace source inspection" in markdown
    assert "| Claim / item to verify | Best evidence in this file | Still verify before relying |" in markdown
    assert "Decision situation: Whether to launch the beta after a mixed review." in markdown
    assert "Generated synthesized position: Launch only if a narrow gate passes." in markdown
    assert "Changed advice summary: Add a launch gate before relying on the enterprise signal." in markdown
    assert "Main counter-pressure: The launch gate was under-specified." in markdown
    assert "Revised answer exists: Launch only if the gate passes." in markdown
    assert "Open question: Who owns the launch gate?" in markdown
    assert "Run readiness: evaluation=warn, trace=thin, future_review_ready=false" in markdown
    assert "Treat as generated synthesis; verify against source conversation and current context." in markdown
    assert "do not infer advice correctness" in markdown
    assert "The correct interpretation is" not in markdown
    assert "The proven recommendation is" not in markdown


def test_verification_checklist_boundary_and_non_claims() -> None:
    doc = _read(DOC)
    review_text = _read(REVIEW)
    review = json.loads(review_text)

    for phrase in [
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not create a new run",
        "does not wire skill runtime behavior",
        "does not mutate archives",
        "does not edit `observatory/build`",
        "does not touch `SKILL.md`",
        "does not touch `scripts/skill/*`",
        "does not touch `scripts/archive_run.py`",
        "does not claim product proof",
        "does not claim human validation",
        "does not claim answer correctness",
        "does not claim advice correctness",
    ]:
        assert phrase in doc

    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["creates_new_run"] is False
    assert review["boundary"]["wires_skill_runtime_behavior"] is False
    assert review["boundary"]["mutates_archives"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False

    combined = doc + review_text
    assert "/" + "Users/" not in combined
    assert "Desktop/" + "Apps" not in combined
    assert "product_proof\": true" not in combined
    assert "human_validated\": true" not in combined
    assert "answer_correctness\": true" not in combined
    assert "advice_correctness\": true" not in combined
    assert "action_authorized\": true" not in combined
