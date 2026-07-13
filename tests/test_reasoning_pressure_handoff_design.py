from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA = REPO_ROOT / "docs/conversation-understanding/reasoning-pressure-handoff-v0.json"
DISPOSITION_SCHEMA = (
    REPO_ROOT
    / "docs/conversation-understanding/reasoning-pressure-disposition-ledger-v0.json"
)
DOC = REPO_ROOT / "docs/conversation-understanding/reasoning-pressure-handoff-v0.md"
EXAMPLE = (
    REPO_ROOT
    / "tests/fixtures/core_semantic_validation/case_01_enterprise_logo_beta/reasoning-pressure-handoff.example.json"
)


def test_handoff_is_small_and_excludes_semantic_inventory_and_scores() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    pressure = schema["properties"]["pressure_items"]
    preservation = schema["properties"]["preservation_items"]
    boundary = schema["properties"]["boundary"]["properties"]
    assert schema["$id"] == "lolla.reasoning_pressure_handoff.v0"
    assert pressure["maxItems"] == 4
    assert preservation["maxItems"] == 4
    assert boundary["full_semantic_inventory_included"]["const"] is False
    assert boundary["full_graph_candidate_catalog_included"]["const"] is False
    assert boundary["quality_score_included"]["const"] is False


def test_pressure_items_require_application_and_set_aside_boundaries() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    lineage_required = set(schema["properties"]["lineage"]["required"])
    required = set(schema["$defs"]["pressure_item"]["required"])
    assert "graph_trace_artifact_sha256" in lineage_required
    assert {
        "source_event_ids",
        "challenge",
        "applicability_condition",
        "decision_effect",
        "consequence_if_true",
        "set_aside_condition",
        "graph_trace_refs",
    } <= required


def test_example_preserves_full_conversation_authority_and_no_expected_answer() -> None:
    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    assert example["source"]["authoritative_full_conversation_reattached"] is True
    assert example["source"]["original_answer_reattached"] is True
    assert example["boundary"]["expected_answer_included"] is False
    assert len(example["pressure_items"]) == 3
    assert len(example["preservation_items"]) == 2
    for item in example["pressure_items"]:
        assert item["applicability_condition"]
        assert item["set_aside_condition"]


def test_doc_keeps_semantic_selection_probabilistic_and_runtime_unchanged() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "The graph does not write the final pressure." in text
    assert "LLM or human responsibilities" in text
    assert "Forbidden deterministic behavior" in text
    assert "A longer," in text
    assert "more structured, or more cautious answer is not a win." in text
    assert "No paid call" in text
    assert "runtime path changes" in text
    assert "contract exists." in text


def test_disposition_schema_requires_exact_identity_and_separate_effect_review() -> None:
    schema = json.loads(DISPOSITION_SCHEMA.read_text(encoding="utf-8"))
    assert schema["$id"] == "lolla.reasoning_pressure_disposition_ledger.v0"
    assert schema["properties"]["items"]["maxItems"] == 4
    required = set(schema["$defs"]["disposition_item"]["required"])
    assert {
        "pressure_id",
        "strongest_plausible_application",
        "disposition",
        "visible_effect",
        "private_guardrail",
        "risk_if_forced",
        "risk_if_ignored",
    } <= required
    review_required = set(schema["$defs"]["semantic_effect_review"]["required"])
    assert {"status", "reviewer", "reviewed_output_sha256", "findings"} <= review_required
