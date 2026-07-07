from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.conversation_memory_renderer import (
    render_conversation_memory_markdown,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = (
    REPO_ROOT
    / "docs/product/observatory-agent-memory-orientation-renderer-spike-v0.md"
)
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-agent-memory-orientation-renderer-spike-v0/"
    "review.json"
)
RENDERER = REPO_ROOT / "engine/system_b/conversation_memory_renderer.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_orientation_renderer_spike_is_registered_and_gated() -> None:
    doc = _read(DOC)
    readme = _read(README)
    review = json.loads(_read(REVIEW))

    assert "Observatory Agent Memory Orientation Renderer Spike" in readme
    assert "observatory-agent-memory-orientation-renderer-spike-v0.md" in readme
    assert "Decision gate: `proceed_to_agent_memory_verification_checklist_spike`" in doc
    assert review["decision_gate"] == (
        "proceed_to_agent_memory_verification_checklist_spike"
    )
    assert review["implemented"]["cold_reader_orientation_rendered"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False


def test_spike_records_ab_experiment_and_v1_failure() -> None:
    doc = _read(DOC)
    review = json.loads(_read(REVIEW))

    for phrase in [
        "summary_anchoring_or_artifact_poisoning",
        "baseline",
        "oriented v1",
        "oriented v2",
        "This was a useful failure.",
        "The implementation was revised before commit.",
        "does not include a top-level generated-answer bullet",
    ]:
        assert phrase in doc

    assert review["artifact_comparison"]["baseline_lines"] == 698
    assert review["artifact_comparison"]["oriented_v1_lines"] == 732
    assert review["artifact_comparison"]["oriented_v2_lines"] == 740
    assert review["artifact_comparison"]["top_generated_synthesis_bullet_present_in_v2"] is False
    assert review["cold_read_experiment"]["oriented_v1_readers_flagged_top_synthesis_anchoring"] is True


def test_renderer_orientation_avoids_top_generated_answer() -> None:
    renderer = _read(RENDERER)
    markdown = render_conversation_memory_markdown(
        {
            "case": {
                "case_id": "sample-case",
                "run_id": "20260707T000000Z_test",
                "decision_situation": "Whether to launch the beta after a mixed review.",
            },
            "artifact_status": {"missing_count": 0},
            "privacy": {"raw_conversation_included": True},
            "run_health": {
                "evaluation_overall": "pass",
                "caller_readiness": "usable_after_inspection",
                "future_review_ready": False,
            },
        }
    )

    assert "Cold Reader Orientation" in markdown
    assert "Orientation, not conclusion." in markdown
    assert "Generated synthesis appears later" in markdown
    assert "hypotheses to verify, not ground truth" in markdown
    assert "Do not treat this orientation as the answer." in markdown
    assert "Key Checks Before Trusting Any Interpretation" in markdown
    assert "- Generated synthesis:" not in markdown
    assert '"- Generated synthesis:"' not in renderer
    assert "The correct interpretation is" not in markdown
    assert "The proven recommendation is" not in markdown


def test_orientation_spike_boundary_and_non_claims() -> None:
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
