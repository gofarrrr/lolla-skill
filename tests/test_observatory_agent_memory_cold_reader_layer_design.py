from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = (
    REPO_ROOT
    / "docs/product/observatory-agent-memory-cold-reader-layer-design-v0.md"
)
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-agent-memory-cold-reader-layer-design-v0/"
    "review.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_cold_reader_design_is_registered_and_gated() -> None:
    doc = _read(DOC)
    readme = _read(README)
    review = json.loads(_read(REVIEW))

    assert "Observatory Agent Memory Cold Reader Layer Design" in readme
    assert "observatory-agent-memory-cold-reader-layer-design-v0.md" in readme
    assert "Decision gate: `proceed_to_agent_memory_orientation_renderer_spike`" in doc
    assert review["decision_gate"] == (
        "proceed_to_agent_memory_orientation_renderer_spike"
    )
    assert review["implemented"]["design_only"] is True
    assert review["implemented"]["future_renderer_behavior_changed"] is False
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False


def test_design_names_artifact_poisoning_and_orientation_rule() -> None:
    doc = _read(DOC)
    review = json.loads(_read(REVIEW))

    for phrase in [
        "Orientation, not conclusion.",
        "summary_anchoring_or_artifact_poisoning",
        "The top layer must help a cold reader know how to read the artifact",
        "must not replace the reader's own inspection",
        "hypothesis to verify",
        "Do not treat this as ground truth",
        "transcript remains the primary source object",
    ]:
        assert phrase in doc

    assert review["implemented"]["summary_anchoring_risk_named"] is True
    assert review["implemented"]["orientation_not_conclusion_rule"] is True
    assert review["design_constraints"]["orientation_must_be_hypothesis_to_verify"] is True
    assert review["design_constraints"]["transcript_remains_primary_source"] is True


def test_design_allows_orientation_but_rejects_answer_shaped_summary() -> None:
    doc = _read(DOC)

    for phrase in [
        "identify the file as a generated reasoning-audit memory view",
        "provide a suggested reading order",
        "list the system's synthesis only as a hypothesis to verify",
        "explain why run-health labels can coexist",
        "repeat privacy warnings before any raw transcript section",
    ]:
        assert phrase in doc

    for phrase in [
        "declare the final interpretation as correct",
        "label a recommendation as proven",
        "hide, replace, or shorten the full transcript",
        "add new business facts not present in source artifacts",
        "convert inferred open questions into system-supplied facts",
        "treat selected mental models as proof",
        "treat suppressed models as noise",
    ]:
        assert phrase in doc


def test_design_records_cold_read_experiment_without_claiming_validation() -> None:
    doc = _read(DOC)
    review = json.loads(_read(REVIEW))

    for phrase in [
        "Three context-free agents",
        "they understood it as a private conversation-memory export",
        "they recovered the public-beta versus private-pilot decision",
        "they recovered the 900-person versus 220-person prospect path",
        "the current recommendation is spread across several sections",
        "open questions are empty even when the transcript implies unresolved questions",
        "run-health labels need plain-language interpretation",
    ]:
        assert phrase in doc

    assert review["cold_read_experiment"]["subagents_used"] == 3
    assert review["cold_read_experiment"]["context_free_read"] is True
    assert review["cold_read_experiment"]["artifact_understood_as_memory_export"] is True
    assert review["cold_read_experiment"]["summary_anchoring_risk_identified"] is True
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False


def test_design_boundary_stays_document_only() -> None:
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
    ]:
        assert phrase in doc

    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["creates_new_run"] is False
    assert review["boundary"]["wires_skill_runtime_behavior"] is False
    assert review["boundary"]["mutates_archives"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False

    combined = doc + review_text
    assert "/" + "Users/" not in combined
    assert "Desktop/" + "Apps" not in combined
    assert "product_proof\": true" not in combined
    assert "human_validated\": true" not in combined
    assert "answer_correctness\": true" not in combined
    assert "advice_correctness\": true" not in combined
    assert "action_authorized\": true" not in combined
