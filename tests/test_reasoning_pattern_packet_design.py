from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "docs/conversation-understanding/reasoning-pattern-packet-v0.json"
DOC_PATH = REPO_ROOT / "docs/conversation-understanding/reasoning-pattern-packet-v0.md"
EXAMPLE_PATH = REPO_ROOT / "tests/fixtures/core_semantic_validation/case_01_enterprise_logo_beta/reasoning-pattern-packet.example.json"


def test_reasoning_pattern_packet_keeps_graph_projection_fact_free_by_shape() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    routing = schema["properties"]["routing_projection"]["properties"]
    node = schema["$defs"]["routing_node"]

    assert schema["$id"] == "lolla.reasoning_pattern_packet.v0"
    assert routing["contains_case_context"]["const"] is False
    assert set(node["properties"]) == {
        "pattern_id",
        "mechanism_id",
        "subject_scope",
        "state",
    }
    for forbidden in ("quote", "text", "entity", "date", "amount", "case_id", "source_ref"):
        assert forbidden not in node["properties"]


def test_example_projection_contains_only_controlled_mechanisms() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    mechanisms = set(schema["$defs"]["mechanism_id"]["enum"])

    assert example["packet_metadata"]["graph_runtime_modified"] is False
    assert example["routing_projection"]["contains_case_context"] is False
    assert example["fact_boundary"] == {
        "raw_text_included": False,
        "quotes_included": False,
        "entities_included": False,
        "case_quantities_included": False,
        "dates_included": False,
        "desired_outcome_included": False,
        "topic_labels_included": False,
    }
    for node in example["routing_projection"]["pattern_nodes"]:
        assert node["mechanism_id"] in mechanisms
        assert set(node) == {"pattern_id", "mechanism_id", "subject_scope", "state"}


def test_packet_design_explicitly_defers_graph_integration() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "Graph status: unchanged" in text
    assert "The graph must not receive this surface." in text
    assert "Before any graph integration" in text
    assert "not describe this as deterministic end to end" in text
    assert "That shortcut is now blocked." in text
    assert "it is" in text
    assert "not itself the reconsideration prompt" in text
    assert "transcript-only strong" in text
    assert "reconsideration control" in text
