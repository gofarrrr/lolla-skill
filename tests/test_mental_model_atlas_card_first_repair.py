from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from scripts.product.build_mental_model_atlas_custody_v2 import (
    build_card_first_custody_v2_package as build_card_first_package,
)
from scripts.product.build_mental_model_atlas_card_first_repair import (
    BULLET_ITEM_LINES,
    CARD_FIRST_SCHEMA_VERSION,
    H2_LINES,
    H3_LINES,
    INCIDENT_RELATION_INDICES,
    KG_RECORD_SHA256,
    LEGACY_BOUNDARY_HASHES,
    ORDERED_ITEM_LINES,
    PARAGRAPH_LINES,
    SOURCE_SHA256,
    SUBSTANTIVE_LINES,
    TABLE_TEXT_LINES,
    AtlasProjectionError,
    canonical_json_bytes,
    validate_card_first_page,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "apps/mental-model-atlas/public/data/card-first-v2"
SOURCE_PATH = ROOT / "data/model_sources/abstraction_rag.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _page() -> dict:
    return build_card_first_package(ROOT)["artifacts"]["pages/model-abstraction.json"]


def test_prior_phase1_projection_and_model_page_remain_byte_identical() -> None:
    for relative, expected_hash in LEGACY_BOUNDARY_HASHES.items():
        assert _sha256(ROOT / relative) == expected_hash


def test_card_first_package_rebuilds_byte_for_byte_and_costs_zero() -> None:
    first = build_card_first_package(ROOT)
    second = build_card_first_package(ROOT)
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert first["manifest"]["provider_calls"] == 0
    assert first["manifest"]["provider_cost_usd"] == 0.0
    for relative, payload in first["artifacts"].items():
        assert (OUTPUT_DIR / relative).read_bytes() == canonical_json_bytes(payload)
    assert (OUTPUT_DIR / "manifest.json").read_bytes() == canonical_json_bytes(first["manifest"])


def test_source_card_is_one_exact_hash_bound_authority() -> None:
    page = _page()
    card = page["source_card"]
    source = SOURCE_PATH.read_bytes()
    assert page["schema_version"] == CARD_FIRST_SCHEMA_VERSION
    assert card["source_text"].encode("utf-8") == source
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA256
    assert len(source) == 14_518
    assert card["source_ref"] == {
        "source_type": "canonical_model_markdown",
        "path": "data/model_sources/abstraction_rag.md",
        "sha256": SOURCE_SHA256,
        "bytes": 14_518,
        "encoding": "utf-8",
        "line_ending": "LF",
        "terminal_newline": True,
        "line_count": 126,
    }
    assert "sections" not in card
    assert "blocks" not in card


def test_exact_line_map_accounts_for_every_physical_and_substantive_line() -> None:
    card = _page()["source_card"]
    line_map = card["line_map"]
    assert [item["line_number"] for item in line_map] == list(range(1, 127))
    rendered = {
        item["line_number"]
        for item in line_map
        if item["render_disposition"] == "rendered_verbatim"
    }
    assert rendered == SUBSTANTIVE_LINES
    assert len(rendered) == 60
    assert {item["line_number"] for item in line_map if item.get("heading_level") == 1} == {1}
    assert {item["line_number"] for item in line_map if item.get("heading_level") == 2} == H2_LINES
    assert {item["line_number"] for item in line_map if item.get("heading_level") == 3} == H3_LINES
    assert {item["line_number"] for item in line_map if item["kind"] == "paragraph"} == PARAGRAPH_LINES
    assert {item["line_number"] for item in line_map if item["kind"] == "ordered_list_item"} == ORDERED_ITEM_LINES
    assert {item["line_number"] for item in line_map if item["kind"] == "unordered_list_item"} == BULLET_ITEM_LINES
    assert {item["line_number"] for item in line_map if item["kind"] == "table_text_row"} == TABLE_TEXT_LINES
    assert card["coverage"]["physical_line_count"] == 126
    assert card["coverage"]["substantive_line_count"] == 60
    assert card["coverage"]["omitted_substantive_line_count"] == 0
    assert card["coverage"]["title_and_heading_count"] == 15


def test_human_reader_projection_partitions_source_into_five_chapters_and_one_appendix() -> None:
    projection = _page()["source_card"]["reader_projection"]
    assert projection["interaction_mode"] == "single_open_chapter_with_persistent_orientation"
    assert [
        (item["chapter_id"], item["step"], item["start_line"], item["end_line"], item["heading_line"])
        for item in projection["chapters"]
    ] == [
        ("understand", 1, 3, 23, 7),
        ("use", 2, 25, 45, 25),
        ("judge", 3, 47, 75, 47),
        ("connect", 4, 77, 99, 77),
        ("apply-safely", 5, 109, 126, 109),
    ]
    assert projection["source_appendix"] == {
        "appendix_id": "source-curation-notes",
        "label": "Original relationship curation notes",
        "start_line": 101,
        "end_line": 107,
        "heading_line": 101,
        "default_state": "collapsed",
        "reason": (
            "Dated slug-form relationship maintenance text is preserved exactly for source custody but is not "
            "part of the primary human learning sequence. The separately rendered relationship layer provides "
            "the current readable connection view."
        ),
        "review_authority": "founder_product_feedback_2026-07-16",
    }
    accounting = projection["substantive_line_accounting"]
    assert accounting["total"] == 60
    assert accounting["hero"] == [1]
    assert len(accounting["primary_learning_sequence"]) == 55
    assert accounting["source_appendix"] == [101, 103, 105, 107]
    assert accounting["unassigned"] == accounting["duplicated"] == []
    assert set(accounting["hero"] + accounting["primary_learning_sequence"] + accounting["source_appendix"]) == SUBSTANTIVE_LINES
    source_lines = _page()["source_card"]["source_text"].splitlines()
    for cue in projection["orientation_cues"]:
        assert cue["text"] in source_lines[cue["source_line"] - 1]


@pytest.mark.parametrize(
    "mutation",
    [
        lambda page: page["source_card"]["line_map"].pop(12),
        lambda page: page["source_card"]["line_map"].insert(12, copy.deepcopy(page["source_card"]["line_map"][11])),
        lambda page: page["source_card"]["line_map"].__setitem__(slice(6, 8), list(reversed(page["source_card"]["line_map"][6:8]))),
        lambda page: page["source_card"]["line_map"][6].__setitem__("heading_level", 3),
        lambda page: page["source_card"].__setitem__("source_text", page["source_card"]["source_text"].replace("Abstraction", "AbstraXtion", 1)),
        lambda page: page["source_card"]["line_map"][8].__setitem__("render_disposition", "omitted"),
        lambda page: page["source_card"]["coverage"].__setitem__("rendered_substantive_line_count", 59),
        lambda page: page["source_card"]["reader_projection"]["chapters"][2].__setitem__("end_line", 73),
        lambda page: page["source_card"]["reader_projection"]["source_appendix"].__setitem__("start_line", 99),
        lambda page: page["source_card"]["reader_projection"]["orientation_cues"][0].__setitem__("text", "invented"),
        lambda page: page["source_card"]["reader_projection"]["substantive_line_accounting"]["primary_learning_sequence"].pop(),
    ],
)
def test_source_line_or_coverage_mutations_fail_closed(mutation) -> None:
    page = _page()
    mutation(page)
    with pytest.raises(AtlasProjectionError):
        validate_card_first_page(page)


def test_complete_operational_record_is_separate_and_exact() -> None:
    page = _page()
    operational = page["operational_curation"]
    canonical = json.loads((ROOT / "data/knowledge_graph.json").read_text())["models"]["abstraction"]
    assert operational["not_source_card"] is True
    assert operational["record"] == canonical
    assert len(canonical) == 12
    assert operational["record_sha256"] == KG_RECORD_SHA256
    assert hashlib.sha256(canonical_json_bytes(canonical)).hexdigest() == KG_RECORD_SHA256
    assert operational["field_coverage"] == {
        "status": "complete",
        "source_field_count": 12,
        "projected_field_count": 12,
        "omitted_fields": [],
    }
    assert operational["source_ref"]["json_pointer"] == "/models/abstraction"


def test_all_exact_incident_connections_survive_without_ranking_fields() -> None:
    connections = _page()["connections"]
    records = connections["records"]
    assert [item["source_record_index"] for item in records] == INCIDENT_RELATION_INDICES
    assert connections["eligible_record_count"] == connections["shown_record_count"] == 12
    assert connections["omitted_record_count"] == 0
    assert connections["incoming_count"] == 7
    assert connections["outgoing_count"] == 5
    assert connections["relation_type_counts"] == {"ally": 7, "antagonist": 1, "tension": 4}
    assert len({item["relation_id"] for item in records}) == 12
    assert [
        item["relation_type"]
        for item in records
        if item["source_model_id"] == "abstraction" and item["target_model_id"] == "first-principles-thinking"
    ] == ["ally", "tension"]
    forbidden = {"composition_affinity", "rank", "score", "weight"}
    assert all(forbidden.isdisjoint(item) for item in records)
    assert connections["record_coverage"]["status"] == "complete"
    assert connections["source_field_projection"]["status"] == "partial"
    omitted = {item["field"] for item in connections["source_field_projection"]["omitted_fields"]}
    assert "composition_affinity" in omitted


def test_page_truthfully_remains_partial_even_with_complete_source_card() -> None:
    page = _page()
    statuses = {item["component"]: item["status"] for item in page["coverage"]["components"]}
    assert page["source_card"]["coverage"]["status"] == "complete"
    assert page["operational_curation"]["field_coverage"]["status"] == "complete"
    assert page["connections"]["record_coverage"]["status"] == "complete"
    assert page["coverage"]["status"] == "partial"
    assert statuses["relationship_source_field_projection"] == "partial"
    assert statuses["reviewed_runtime_affordance_projection"] == "available_not_projected"
    assert statuses["distinct_reviewed_practice_prompts"] == "missing"
    assert statuses["curated_teacher_journeys"] == "missing"
    assert page["missingness"]["status"] == "partial"
    assert page["status"]["publication"] == "blocked_pending_rights_review"
