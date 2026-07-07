from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.conversation_memory_renderer import (
    render_conversation_memory_markdown,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-agent-memory-source-locator-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-agent-memory-source-locator-v0/"
    "review.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_source_locator_slice_is_registered_and_gated() -> None:
    doc = _read(DOC)
    readme = _read(README)
    review = json.loads(_read(REVIEW))

    assert "Observatory Agent Memory Source Locator" in readme
    assert "observatory-agent-memory-source-locator-v0.md" in readme
    assert "Decision gate: `proceed_to_agent_memory_download_ux_review`" in doc
    assert review["decision_gate"] == "proceed_to_agent_memory_download_ux_review"
    assert review["implemented"]["stable_section_anchors_rendered"] is True
    assert review["implemented"]["packet_schema_changed"] is False
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False


def test_renderer_adds_stable_section_and_source_locators() -> None:
    markdown = render_conversation_memory_markdown(
        {
            "case": {
                "case_id": "sample-case",
                "run_id": "20260707T000000Z_test",
                "decision_situation": "Whether to launch the beta after a mixed review.",
            },
            "privacy": {"raw_conversation_included": True},
            "source_conversation": {"text": "User: Should we launch?\nAssistant: Check gates."},
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
                "memo_markdown": "Memo body.",
                "revised_answer": "Launch only if the gate passes.",
            },
            "open_questions": {"items": []},
            "run_health": {
                "evaluation_overall": "warn",
                "trace_adequacy_status": "thin",
                "future_review_ready": False,
            },
        }
    )

    assert '<a id="cm-section-claim-verification-checklist"></a>' in markdown
    assert '<a id="cm-section-conversation-interpretation"></a>' in markdown
    assert '<a id="cm-section-what-changed"></a>' in markdown
    assert '<a id="cm-section-open-questions"></a>' in markdown
    assert '<a id="cm-section-run-health-and-readiness"></a>' in markdown
    assert '<a id="cm-section-artifact-custody"></a>' in markdown
    assert '<a id="cm-source-full-transcript"></a>' in markdown
    assert '<a id="cm-source-memo"></a>' in markdown
    assert '<a id="cm-source-revised-answer"></a>' in markdown
    assert "Source locator" in markdown
    assert "[Transcript](#cm-source-full-transcript)" in markdown
    assert "[Memo](#cm-source-memo)" in markdown
    assert "[Revised Answer](#cm-source-revised-answer)" in markdown
    assert "[Artifact Custody](#cm-section-artifact-custody)" in markdown
    assert "No structured open-question rows were supplied." in markdown
    assert "no line-level" not in markdown.lower()


def test_source_locator_boundary_and_non_claims() -> None:
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
