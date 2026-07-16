#!/usr/bin/env python3
"""Build the provider-free, card-first Atlas truthfulness repair.

This package is additive. It freezes the Phase 1 v1 artifacts, embeds the exact
canonical Abstraction Markdown once, and keeps compiled knowledge-graph and
relationship-graph material in explicitly separate layers.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from scripts.product.build_mental_model_atlas_phase1_projection import (
    EXPECTED_SOURCE_HASHES,
    NON_CLAIMS,
    AtlasProjectionError,
    _relation_record,
    sha256_bytes,
    sha256_path,
)


CARD_FIRST_SCHEMA_VERSION = "lolla.atlas_model_page.v2"
MANIFEST_SCHEMA_VERSION = "lolla.atlas_card_first_manifest.v1"
CANONICAL_PARENT = "0eec520dc0937cdeeb4ae89195b6f38a035303a4"
SOURCE_PATH = "data/model_sources/abstraction_rag.md"
OUTPUT_RELATIVE = "apps/mental-model-atlas/public/data/card-first-v1"
SOURCE_SHA256 = "6d689abd7ae1f8022e2450b045b0f03ffc57700f8298ff858018d808845f5650"
KG_RECORD_SHA256 = "ec28ee731944e7760dd574a401593d4dac1373ad69d3d080f9e58a4ebd19daef"

LEGACY_BOUNDARY_HASHES = {
    "apps/mental-model-atlas/public/data/phase1/manifest.json": (
        "203999a61dbe9c2e943bbcb9f5b4dd87779d4557ea9fcfbd50b3e9d59e816c52"
    ),
    "apps/mental-model-atlas/public/data/phase1/pages/model-abstraction.json": (
        "8cc07cbbf68f399dcd5787df9067bd3a3646068b59ed691ca043ffc9e9ce406f"
    ),
}

TITLE_LINE = 1
H2_LINES = {7, 25, 47, 77, 101}
H3_LINES = {15, 29, 37, 49, 65, 81, 91, 109, 120}
HEADING_LINES = {TITLE_LINE, *H2_LINES, *H3_LINES}
PARAGRAPH_LINES = {3, 9, 11, 13, 27, 51, 79, 111}
ORDERED_ITEM_LINES = {17, 19, 21, 53, 55, 57, 59, 61, 63, 67, 69, 71, 73}
BULLET_ITEM_LINES = {31, 33, 35, 39, 41, 43, 83, 85, 87, 89, 93, 95, 97, 103, 105, 107, 122, 124, 126}
TABLE_TEXT_LINES = {113, 115, 116, 117, 118}
SUBSTANTIVE_LINES = (
    HEADING_LINES | PARAGRAPH_LINES | ORDERED_ITEM_LINES | BULLET_ITEM_LINES | TABLE_TEXT_LINES
)
RULE_LINES = {5, 23, 45, 75, 99}
TABLE_DELIMITER_LINE = 114
INCIDENT_RELATION_INDICES = [0, 1, 2, 3, 4, 51, 456, 534, 810, 1115, 1151, 1283]
READER_CHAPTERS = [
    {
        "chapter_id": "understand",
        "step": 1,
        "navigation_label": "Understand the idea",
        "orientation": "What abstraction is, why it works, and the analogies that make it memorable.",
        "start_line": 3,
        "end_line": 23,
        "heading_line": 7,
    },
    {
        "chapter_id": "use",
        "step": 2,
        "navigation_label": "Use it in practice",
        "orientation": "Move from the definition to concrete frameworks, decisions, and communication.",
        "start_line": 25,
        "end_line": 45,
        "heading_line": 25,
    },
    {
        "chapter_id": "judge",
        "step": 3,
        "navigation_label": "Know its limits",
        "orientation": "Recognize where abstraction creates leverage and where it detaches from reality.",
        "start_line": 47,
        "end_line": 75,
        "heading_line": 47,
    },
    {
        "chapter_id": "connect",
        "step": 4,
        "navigation_label": "See the connections",
        "orientation": "Understand the models that strengthen, challenge, or correct abstraction.",
        "start_line": 77,
        "end_line": 99,
        "heading_line": 77,
        "after_chapter_action": "open_exact_relationship_neighborhood",
    },
    {
        "chapter_id": "apply-safely",
        "step": 5,
        "navigation_label": "Apply it safely",
        "orientation": "Use risks, mitigations, and premortem questions to re-ground the model.",
        "start_line": 109,
        "end_line": 126,
        "heading_line": 109,
        "after_chapter_action": "open_operational_guidance",
    },
]
READER_APPENDIX = {
    "appendix_id": "source-curation-notes",
    "label": "Original relationship curation notes",
    "start_line": 101,
    "end_line": 107,
    "heading_line": 101,
    "default_state": "collapsed",
    "reason": (
        "Dated slug-form relationship maintenance text is preserved exactly for source "
        "custody but is not part of the primary human learning sequence. The separately "
        "rendered relationship layer provides the current readable connection view."
    ),
    "review_authority": "founder_product_feedback_2026-07-16",
}
READER_ORIENTATION_CUES = [
    {
        "label": "What it does",
        "text": "simplify reality, extract patterns, and move efficiently between the conceptual and the concrete",
        "source_line": 3,
    },
    {
        "label": "Best used when",
        "text": "reality is too noisy to reason about directly",
        "source_line": 59,
    },
    {
        "label": "Watch for",
        "text": "the model is elegant enough to feel complete but no longer stays anchored to concrete evidence",
        "source_line": 73,
    },
]
RELATION_SOURCE_FIELDS = {
    "source_model_id",
    "target_model_id",
    "edge_type",
    "source_description",
    "target_description",
    "is_reciprocal",
    "tension_depth",
    "composition_affinity",
    "source_quote",
    "extraction_type",
    "confidence",
    "curated",
    "affinity_rationale",
    "activation_condition",
    "tension_type",
}


def canonical_json_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def build_card_first_package(root: Path) -> dict[str, Any]:
    root = root.resolve()
    _verify_inputs(root)
    source_bytes = (root / SOURCE_PATH).read_bytes()
    source_text = source_bytes.decode("utf-8")
    knowledge_graph = _load_json(root / "data/knowledge_graph.json")
    relationship_graph = _load_json(root / "data/relationship_graph.json")
    model = copy.deepcopy(knowledge_graph["models"]["abstraction"])

    page = {
        "schema_version": CARD_FIRST_SCHEMA_VERSION,
        "page_id": "model-abstraction-card-v2",
        "page_status": "local_founder_review_only",
        "predecessor": {
            "path": "data/phase1/pages/model-abstraction.json",
            "schema_version": "lolla.atlas_model_page.v1",
            "sha256": LEGACY_BOUNDARY_HASHES[
                "apps/mental-model-atlas/public/data/phase1/pages/model-abstraction.json"
            ],
        },
        "model": {
            "model_id": "abstraction",
            "slug": model["slug"],
            "display_name": model["display_name"],
        },
        "source_card": _source_card(source_text, source_bytes),
        "operational_curation": _operational_curation(model),
        "connections": _connections(root, relationship_graph),
        "coverage": {
            "status": "partial",
            "components": [
                {"component": "authoritative_source_card", "status": "complete"},
                {"component": "operational_knowledge_graph_record", "status": "complete"},
                {"component": "incident_relationship_record_set", "status": "complete"},
                {"component": "relationship_source_field_projection", "status": "partial"},
                {
                    "component": "reviewed_runtime_affordance_projection",
                    "status": "available_not_projected",
                    "render_disposition": "outside_current_repair_scope",
                },
                {
                    "component": "distinct_reviewed_practice_prompts",
                    "status": "missing",
                    "render_disposition": "not_authored_or_reviewed",
                },
                {
                    "component": "curated_teacher_journeys",
                    "status": "missing",
                    "render_disposition": "outside_current_repair_scope",
                },
            ],
        },
        "source_custody": {
            "canonical_parent": CANONICAL_PARENT,
            "legacy_boundary": [
                {"path": path, "sha256": sha256}
                for path, sha256 in sorted(LEGACY_BOUNDARY_HASHES.items())
            ],
        },
        "status": {
            "source": "verified_hash_bound",
            "curation": "source_card_plus_separate_checked_in_curated_layers",
            "human_review": "pending_founder_guided_reader_review",
            "licensing": "unknown",
            "publication": "blocked_pending_rights_review",
            "missingness": "partial",
            "content_generation": "exact_source_plus_deterministic_presentation_only",
        },
        "missingness": {
            "status": "partial",
            "missing_fields": [
                "distinct_reviewed_practice_prompts",
                "curated_teacher_journeys",
            ],
            "notes": [
                "Reviewed runtime affordances exist but are intentionally not projected by this repair.",
                "Complete source-card custody does not make the full learning-page inventory complete.",
            ],
        },
        "non_claims": [
            *NON_CLAIMS,
            "not_graph_substitute_for_source_card",
            "not_operational_projection_equivalent_to_source_document",
            "not_complete_teacher_journey",
            "not_runtime_affordance_projection",
        ],
    }
    validate_card_first_page(page)
    artifacts = {"pages/model-abstraction.json": page}
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "package_id": "lolla-mental-model-atlas-card-first-repair-v1",
        "status": "local_founder_review_only",
        "canonical_parent": CANONICAL_PARENT,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "legacy_boundary": page["source_custody"]["legacy_boundary"],
        "artifacts": [
            {
                "artifact_type": "card_first_model_page",
                "path": relative,
                "schema_version": payload["schema_version"],
                "sha256": sha256_bytes(canonical_json_bytes(payload)),
            }
            for relative, payload in artifacts.items()
        ],
        "scope": {
            "model_count": 1,
            "model_ids": ["abstraction"],
            "full_source_card_count": 1,
            "atlas_phase2_authorized": False,
            "teacher_journey_authorized": False,
            "runtime_or_observatory_integration": False,
            "publication_authorized": False,
        },
    }
    return {"artifacts": artifacts, "manifest": manifest}


def _source_card(source_text: str, source_bytes: bytes) -> dict[str, Any]:
    line_map = _line_map(source_text)
    return {
        "label": "Authoritative source card",
        "content_role": "authoritative_educational_source",
        "source_ref": {
            "source_type": "canonical_model_markdown",
            "path": SOURCE_PATH,
            "sha256": SOURCE_SHA256,
            "bytes": len(source_bytes),
            "encoding": "utf-8",
            "line_ending": "LF",
            "terminal_newline": True,
            "line_count": len(line_map),
        },
        "source_text": source_text,
        "line_map": line_map,
        "reader_projection": _reader_projection(source_text, line_map),
        "coverage": {
            "status": "complete",
            "physical_line_count": len(line_map),
            "accounted_line_count": len(line_map),
            "substantive_line_count": len(SUBSTANTIVE_LINES),
            "rendered_substantive_line_count": len(SUBSTANTIVE_LINES),
            "omitted_substantive_line_count": 0,
            "title_and_heading_count": len(HEADING_LINES),
            "rendered_title_and_heading_count": len(HEADING_LINES),
            "omitted_title_and_heading_count": 0,
            "word_count": len(source_text.split()),
            "presentation_normalization": [
                "Markdown emphasis markers become semantic strong elements.",
                "Blank lines become layout spacing.",
                "Horizontal rules become semantic separators.",
                "The Markdown table delimiter becomes HTML table structure.",
            ],
        },
    }


def _reader_projection(source_text: str, line_map: list[dict[str, Any]]) -> dict[str, Any]:
    lines = source_text.splitlines()
    substantive = {
        item["line_number"]
        for item in line_map
        if item["render_disposition"] == "rendered_verbatim"
    }
    hero_lines = {TITLE_LINE}
    primary_lines = {
        number
        for chapter in READER_CHAPTERS
        for number in range(chapter["start_line"], chapter["end_line"] + 1)
        if number in substantive
    }
    appendix_lines = {
        number
        for number in range(READER_APPENDIX["start_line"], READER_APPENDIX["end_line"] + 1)
        if number in substantive
    }
    if hero_lines | primary_lines | appendix_lines != substantive:
        raise AtlasProjectionError("reader projection does not account for every substantive line")
    if hero_lines & primary_lines or hero_lines & appendix_lines or primary_lines & appendix_lines:
        raise AtlasProjectionError("reader projection assigns one substantive line twice")
    for cue in READER_ORIENTATION_CUES:
        if cue["text"] not in lines[cue["source_line"] - 1]:
            raise AtlasProjectionError(f"reader orientation cue drift: {cue['label']}")
    return {
        "schema_version": "lolla.atlas_human_reader_projection.v1",
        "status": "reviewed_for_abstraction_local_founder_validation",
        "interaction_mode": "single_open_chapter_with_persistent_orientation",
        "default_chapter_id": "understand",
        "orientation_cues": copy.deepcopy(READER_ORIENTATION_CUES),
        "chapters": copy.deepcopy(READER_CHAPTERS),
        "source_appendix": copy.deepcopy(READER_APPENDIX),
        "substantive_line_accounting": {
            "total": len(substantive),
            "hero": sorted(hero_lines),
            "primary_learning_sequence": sorted(primary_lines),
            "source_appendix": sorted(appendix_lines),
            "unassigned": [],
            "duplicated": [],
        },
        "non_claims": [
            "not_a_rewrite_of_the_source_card",
            "not_a_corpus_wide_heading_classifier",
            "not_permission_to_delete_appendix_source_lines",
            "not_teacher_journey_completion",
        ],
    }


def _line_map(source_text: str) -> list[dict[str, Any]]:
    lines = source_text.splitlines()
    if len(lines) != 126:
        raise AtlasProjectionError("Abstraction source must contain exactly 126 lines")
    line_map: list[dict[str, Any]] = []
    for number, text in enumerate(lines, 1):
        heading_level: int | None = None
        if number == TITLE_LINE:
            kind, heading_level, disposition = "title", 1, "rendered_verbatim"
        elif number in H2_LINES:
            kind, heading_level, disposition = "heading", 2, "rendered_verbatim"
        elif number in H3_LINES:
            kind, heading_level, disposition = "heading", 3, "rendered_verbatim"
        elif number in PARAGRAPH_LINES:
            kind, disposition = "paragraph", "rendered_verbatim"
        elif number in ORDERED_ITEM_LINES:
            kind, disposition = "ordered_list_item", "rendered_verbatim"
        elif number in BULLET_ITEM_LINES:
            kind, disposition = "unordered_list_item", "rendered_verbatim"
        elif number in TABLE_TEXT_LINES:
            kind, disposition = "table_text_row", "rendered_verbatim"
        elif number in RULE_LINES:
            kind, disposition = "horizontal_rule", "rendered_as_rule"
        elif number == TABLE_DELIMITER_LINE:
            kind, disposition = "table_delimiter", "consumed_as_table_structure"
        else:
            if text != "":
                raise AtlasProjectionError(f"unreviewed substantive source line {number}")
            kind, disposition = "blank", "spacing_normalized"
        record = {
            "line_number": number,
            "kind": kind,
            "render_disposition": disposition,
        }
        if heading_level is not None:
            record["heading_level"] = heading_level
        line_map.append(record)
    return line_map


def _operational_curation(model: dict[str, Any]) -> dict[str, Any]:
    record_hash = sha256_bytes(canonical_json_bytes(model))
    if record_hash != KG_RECORD_SHA256:
        raise AtlasProjectionError(f"Abstraction knowledge-graph record drift: {record_hash}")
    return {
        "label": "Operational guidance — compiled knowledge graph",
        "content_role": "compiled_operational_projection",
        "not_source_card": True,
        "description": (
            "The complete checked-in Abstraction record used by Lolla's operational "
            "substrate. It is derived curation, not the source card above."
        ),
        "source_ref": {
            "source_type": "compiled_checked_in_curation",
            "path": "data/knowledge_graph.json",
            "json_pointer": "/models/abstraction",
            "sha256": EXPECTED_SOURCE_HASHES["data/knowledge_graph.json"],
        },
        "record_sha256": record_hash,
        "record": model,
        "field_coverage": {
            "status": "complete",
            "source_field_count": len(model),
            "projected_field_count": len(model),
            "omitted_fields": [],
        },
    }


def _connections(root: Path, graph: list[dict[str, Any]]) -> dict[str, Any]:
    actual_indices = [
        index
        for index, raw in enumerate(graph)
        if raw["source_model_id"] == "abstraction" or raw["target_model_id"] == "abstraction"
    ]
    if actual_indices != INCIDENT_RELATION_INDICES:
        raise AtlasProjectionError("Abstraction incident relation set drift")
    records: list[dict[str, Any]] = []
    raw_fields: set[str] = set()
    for index in actual_indices:
        raw = graph[index]
        raw_fields.update(raw)
        relation = _relation_record(root, raw, index)
        relation["focus_direction"] = (
            "outgoing" if raw["source_model_id"] == "abstraction" else "incoming"
        )
        records.append(relation)
    type_counts = {
        kind: sum(item["relation_type"] == kind for item in records)
        for kind in ("ally", "antagonist", "tension")
    }
    included = [
        "source_model_id",
        "target_model_id",
        "edge_type→relation_type",
        "source_description→summary",
        "is_reciprocal",
        "confidence",
        "curated→curation_status",
    ]
    omitted = sorted(raw_fields - {
        "source_model_id", "target_model_id", "edge_type", "source_description",
        "is_reciprocal", "confidence", "curated",
    })
    return {
        "label": "Curated relationship-graph connections — navigation, not relevance proof",
        "content_role": "exact_curated_relation_index",
        "description": (
            "All exact relationship-graph records touching Abstraction, in canonical "
            "source order. Membership is complete; the public field projection is partial."
        ),
        "focus_model_id": "abstraction",
        "source_ref": {
            "source_type": "curated_relationship_graph",
            "path": "data/relationship_graph.json",
            "sha256": EXPECTED_SOURCE_HASHES["data/relationship_graph.json"],
        },
        "ordering": "source_record_index",
        "eligible_record_count": len(records),
        "shown_record_count": len(records),
        "omitted_record_count": 0,
        "incoming_count": sum(item["focus_direction"] == "incoming" for item in records),
        "outgoing_count": sum(item["focus_direction"] == "outgoing" for item in records),
        "relation_type_counts": type_counts,
        "records": records,
        "record_coverage": {"status": "complete"},
        "source_field_projection": {
            "status": "partial",
            "included_or_transformed_fields": included,
            "omitted_fields": [
                {
                    "field": field,
                    "reason": (
                        "forbidden_visual_or_importance_weight"
                        if field == "composition_affinity"
                        else "not_required_by_bounded_public_relation_card"
                    ),
                }
                for field in omitted
            ],
        },
    }


def validate_card_first_page(page: dict[str, Any]) -> None:
    if page.get("schema_version") != CARD_FIRST_SCHEMA_VERSION:
        raise AtlasProjectionError("card-first model page schema is invalid")
    if page.get("model") != {
        "model_id": "abstraction", "slug": "abstraction", "display_name": "Abstraction"
    }:
        raise AtlasProjectionError("card-first model identity drift")
    card = page.get("source_card")
    if not isinstance(card, dict) or not isinstance(card.get("source_text"), str):
        raise AtlasProjectionError("card-first source card is missing")
    source_bytes = card["source_text"].encode("utf-8")
    if hashlib.sha256(source_bytes).hexdigest() != SOURCE_SHA256 or len(source_bytes) != 14518:
        raise AtlasProjectionError("card-first source bytes or hash drift")
    if not card["source_text"].endswith("\n") or card["source_text"].endswith("\n\n"):
        raise AtlasProjectionError("card-first source terminal LF drift")
    expected_map = _line_map(card["source_text"])
    if card.get("line_map") != expected_map:
        raise AtlasProjectionError("card-first source line map drift")
    coverage = card.get("coverage", {})
    expected_coverage = {
        "status": "complete",
        "physical_line_count": 126,
        "accounted_line_count": 126,
        "substantive_line_count": 60,
        "rendered_substantive_line_count": 60,
        "omitted_substantive_line_count": 0,
        "title_and_heading_count": 15,
        "rendered_title_and_heading_count": 15,
        "omitted_title_and_heading_count": 0,
    }
    for key, expected in expected_coverage.items():
        if coverage.get(key) != expected:
            raise AtlasProjectionError(f"card-first source coverage drift: {key}")
    if card.get("reader_projection") != _reader_projection(card["source_text"], expected_map):
        raise AtlasProjectionError("card-first human reader projection drift")

    operational = page.get("operational_curation", {})
    if sha256_bytes(canonical_json_bytes(operational.get("record"))) != KG_RECORD_SHA256:
        raise AtlasProjectionError("card-first operational record drift")
    fields = operational.get("field_coverage", {})
    if fields.get("status") != "complete" or fields.get("source_field_count") != 12:
        raise AtlasProjectionError("card-first operational field coverage drift")
    if fields.get("projected_field_count") != 12 or fields.get("omitted_fields") != []:
        raise AtlasProjectionError("card-first operational fields are incomplete")

    connections = page.get("connections", {})
    records = connections.get("records")
    if not isinstance(records, list) or len(records) != 12:
        raise AtlasProjectionError("card-first connection membership drift")
    indices = [record.get("source_record_index") for record in records]
    if indices != INCIDENT_RELATION_INDICES:
        raise AtlasProjectionError("card-first connection order or index drift")
    ids = [record.get("relation_id") for record in records]
    if len(ids) != len(set(ids)):
        raise AtlasProjectionError("card-first relation IDs must remain unique")
    expected_counts = {
        "eligible_record_count": 12,
        "shown_record_count": 12,
        "omitted_record_count": 0,
        "incoming_count": 7,
        "outgoing_count": 5,
    }
    for key, expected in expected_counts.items():
        if connections.get(key) != expected:
            raise AtlasProjectionError(f"card-first connection count drift: {key}")
    if connections.get("relation_type_counts") != {"ally": 7, "antagonist": 1, "tension": 4}:
        raise AtlasProjectionError("card-first relation-type count drift")
    forbidden = {"composition_affinity", "rank", "score", "weight"}
    if any(forbidden.intersection(record) for record in records):
        raise AtlasProjectionError("forbidden visual score field in card-first relation")
    if connections.get("source_field_projection", {}).get("status") != "partial":
        raise AtlasProjectionError("relationship source-field projection must remain partial")

    components = page.get("coverage", {}).get("components", [])
    if page.get("coverage", {}).get("status") != "partial":
        raise AtlasProjectionError("overall card-first page coverage must remain partial")
    if not any(item.get("status") in {"partial", "missing", "available_not_projected"} for item in components):
        raise AtlasProjectionError("page cannot claim full coverage with declared omissions")
    if page.get("missingness", {}).get("status") != "partial":
        raise AtlasProjectionError("page missingness must remain partial")


def _verify_inputs(root: Path) -> None:
    expected = {
        **LEGACY_BOUNDARY_HASHES,
        SOURCE_PATH: SOURCE_SHA256,
        "data/knowledge_graph.json": EXPECTED_SOURCE_HASHES["data/knowledge_graph.json"],
        "data/relationship_graph.json": EXPECTED_SOURCE_HASHES["data/relationship_graph.json"],
    }
    for relative, expected_hash in expected.items():
        actual = sha256_path(root / relative)
        if actual != expected_hash:
            raise AtlasProjectionError(f"card-first input hash drift: {relative}: {actual}")


def write_card_first_package(root: Path, output: Path) -> None:
    package = build_card_first_package(root)
    output.mkdir(parents=True, exist_ok=True)
    for relative, payload in package["artifacts"].items():
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canonical_json_bytes(payload))
    (output / "manifest.json").write_bytes(canonical_json_bytes(package["manifest"]))


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AtlasProjectionError(f"could not load {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / OUTPUT_RELATIVE
    package = build_card_first_package(root)
    if not args.validate_only:
        write_card_first_package(root, output)
    print(json.dumps({
        "artifact_count": len(package["artifacts"]),
        "output": str(output),
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "status": "valid" if args.validate_only else "written",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
