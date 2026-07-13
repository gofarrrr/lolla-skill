from __future__ import annotations

import hashlib
import json
from pathlib import Path

from engine.system_b.reasoning_pressure_handoff import (
    validate_reasoning_pressure_handoff,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests/fixtures/core_semantic_validation/case_01_enterprise_logo_beta"
RESEARCH = REPO_ROOT / "research/reasoning-pressure-handoff-v0-2026-07-10"
SHADOW_PATH = (
    REPO_ROOT
    / "research/core-semantic-sk3-2026-07-10/case-01-enterprise-logo-beta/shadow-01.json"
)
BRIDGE_PATH = (
    REPO_ROOT
    / "research/end-to-end-evidence-bridge-2026-07-10/five-person-saas-company.json"
)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _json_hash(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _semantic_ids(shadow: dict[str, object]) -> set[str]:
    values: set[str] = set()
    for events in shadow["semantic_events"].values():
        for event in events:
            for field in ("event_id", "issue_id", "stance_id"):
                value = event.get(field)
                if isinstance(value, str) and value:
                    values.add(value)
    return values


def test_checked_in_shadow_handoff_has_recomputable_safe_lineage() -> None:
    handoff = _load(RESEARCH / "lineage-backed-handoff.json")
    validation = _load(RESEARCH / "lineage-validation.json")
    shadow = _load(SHADOW_PATH)
    pattern_path = FIXTURE / "reasoning-pattern-packet.example.json"
    pattern = _load(pattern_path)
    bridge = _load(BRIDGE_PATH)

    inventory = {
        item["artifact"]: item["sha256"]
        for item in bridge["source_run"]["artifact_inventory"]
    }
    selected_models = bridge["capabilities"]["c4_c5_pressure_and_graph"][
        "selected_model_ids"
    ]
    graph_refs = {
        f"graph_survival.model.{model_id}" for model_id in selected_models
    }
    conversation_hash = _file_hash(FIXTURE / "conversation.txt")
    pattern_hash = _file_hash(pattern_path)
    graph_hash = inventory["graph_survival_report.json"]
    routing_hash = _json_hash(pattern["routing_projection"])

    report = validate_reasoning_pressure_handoff(
        handoff,
        known_source_event_ids=_semantic_ids(shadow),
        known_graph_trace_refs=graph_refs,
        expected_conversation_sha256=conversation_hash,
        expected_reasoning_pattern_packet_sha256=pattern_hash,
        expected_graph_version="lolla.graph_survival_report.v0.1",
        expected_graph_trace_artifact_sha256=graph_hash,
        expected_routing_projection_sha256=routing_hash,
    )
    assert report["status"] == "valid_for_shadow_evaluation_only"
    assert validation["lineage"]["semantic_shadow_sha256"] == _file_hash(
        SHADOW_PATH
    )
    assert validation["lineage"]["graph_trace_artifact_sha256"] == graph_hash
    assert validation["semantic_relevance_validated"] is False
    assert validation["answer_quality_validated"] is False
    assert validation["runtime_integration_authorized"] is False


def test_human_review_template_is_blank_and_covers_every_handoff_item() -> None:
    handoff = _load(RESEARCH / "lineage-backed-handoff.json")
    review = _load(RESEARCH / "human-review-template.json")
    expected_ids = {
        item["pressure_id"] for item in handoff["pressure_items"]
    } | {
        item["preservation_id"] for item in handoff["preservation_items"]
    }
    assert review["review_status"] == "not_reviewed"
    assert review["reviewer"] == ""
    assert review["reviewed_at"] is None
    assert {item["item_id"] for item in review["item_reviews"]} == expected_ids
    assert review["packet_level"]["verdict"] == "not_reviewed"
    for item in review["item_reviews"]:
        assert item["source_grounded"] is None
        assert item["case_locally_relevant"] is None
        if item["item_kind"] == "pressure":
            assert item["likely_marginal_job_beyond_strong_fresh_baseline"] is None
        else:
            assert item["preservation_needed_to_avoid_lost_value"] is None
