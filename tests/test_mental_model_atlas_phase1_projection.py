from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.product.build_mental_model_atlas_phase1_projection import (
    EXPECTED_SOURCE_HASHES,
    AtlasProjectionError,
    build_phase1_package,
    canonical_json_bytes,
    sha256_bytes,
    validate_projection,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "apps/mental-model-atlas/public/data/phase1"
EVIDENCE_PATH = (
    ROOT / "docs/evals/lolla-mental-model-atlas-phase1-evidence-v1.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_checked_in_phase1_package_rebuilds_byte_for_byte() -> None:
    package = build_phase1_package(ROOT)

    expected_paths = {
        "ordinary-navigation.json",
        "mixed-parallel-relations.json",
        "explicit-bidirectionality.json",
        "medium-confidence-relation.json",
        *{
            f"confirmation-bias-hub-page-{page_number}.json"
            for page_number in range(1, 7)
        },
        "pages/model-abstraction.json",
        "pages/relation-abstraction-first-principles-thinking-ally.json",
    }
    assert set(package["artifacts"]) == expected_paths

    for relative_path, payload in package["artifacts"].items():
        checked_in = DATA_DIR / relative_path
        assert checked_in.is_file()
        assert checked_in.read_bytes() == canonical_json_bytes(payload)

    assert (DATA_DIR / "manifest.json").read_bytes() == canonical_json_bytes(
        package["manifest"]
    )


def test_source_custody_is_hash_bound_and_model_sources_are_verified() -> None:
    package = build_phase1_package(ROOT)
    custody = package["manifest"]["source_custody"]

    assert custody["source_hash_status"] == "verified"
    assert custody["canonical_data_commit"] == (
        "2f05fd1ca7081f602317d670faad8d1293d5b0ff"
    )
    assert {
        item["path"]: item["sha256"] for item in custody["sources"]
    } == EXPECTED_SOURCE_HASHES

    ordinary = package["artifacts"]["ordinary-navigation.json"]
    for model in ordinary["models"]:
        source_ref = model["source_ref"]
        assert source_ref["sha256"] == hashlib.sha256(
            (ROOT / source_ref["path"]).read_bytes()
        ).hexdigest()


def test_ordinary_projection_has_frozen_models_exact_records_and_stable_layout() -> None:
    ordinary = build_phase1_package(ROOT)["artifacts"]["ordinary-navigation.json"]

    assert ordinary["schema_version"] == "lolla.atlas_projection.v1"
    assert ordinary["fixture_id"] == "ordinary_navigation"
    assert len(ordinary["models"]) == 16
    assert all(model["summary"]["text"] for model in ordinary["models"])
    assert all(model["summary"]["provenance"] for model in ordinary["models"])
    assert all(model["helps_notice"]["text"] for model in ordinary["models"])
    for model in ordinary["models"]:
        summary = model["summary"]["text"]
        assert not set(summary) <= {"-", "_", "*", " "}
        assert "Core Principles" not in summary
        assert len(summary.split()) >= 8
        assert "**" not in summary
        assert model["summary"]["status"] == "source_format_normalized"
    assert ordinary["page"] == {
        "after_count": 33,
        "before_count": 0,
        "eligible_count": 73,
        "omitted_count": 33,
        "ordering": (
            "source_model_id,target_model_id,relation_type,source_record_index"
        ),
        "page_number": 1,
        "page_size": 40,
        "relation_ids": [item["relation_id"] for item in ordinary["relations"]],
        "shown_count": 40,
    }
    assert {item["relation_type"] for item in ordinary["relations"]} == {
        "ally",
        "antagonist",
        "tension",
    }

    layout = ordinary["layout"]
    assert layout["algorithm"] == "deterministic_concentric_fixture"
    assert layout["configuration"]["relation_weight_policy"] == "uniform"
    assert len(layout["coordinates"]) == 16
    assert len(layout["configuration_sha256"]) == 64
    assert len(layout["coordinate_sha256"]) == 64
    assert layout["coordinate_sha256"] == hashlib.sha256(
        canonical_json_bytes(layout["coordinates"])
    ).hexdigest()


def test_mixed_pair_preserves_parallel_ally_and_tension_records() -> None:
    fixture = build_phase1_package(ROOT)["artifacts"][
        "mixed-parallel-relations.json"
    ]

    assert fixture["page"]["eligible_count"] == 2
    assert [item["relation_type"] for item in fixture["relations"]] == [
        "ally",
        "tension",
    ]
    assert {
        (item["source_model_id"], item["target_model_id"])
        for item in fixture["relations"]
    } == {("abstraction", "first-principles-thinking")}
    assert len({item["relation_id"] for item in fixture["relations"]}) == 2


def test_bidirectional_pair_preserves_two_nonreciprocal_directed_records() -> None:
    fixture = build_phase1_package(ROOT)["artifacts"][
        "explicit-bidirectionality.json"
    ]

    assert fixture["page"]["eligible_count"] == 2
    assert {
        (item["source_model_id"], item["target_model_id"])
        for item in fixture["relations"]
    } == {
        ("active-listening", "prisoners-dilemma"),
        ("prisoners-dilemma", "active-listening"),
    }
    assert all(item["is_reciprocal"] is False for item in fixture["relations"])
    assert all(item["direction"] == "source_authored" for item in fixture["relations"])


def test_confirmation_bias_hub_discloses_exact_page_and_omissions() -> None:
    artifacts = build_phase1_package(ROOT)["artifacts"]
    fixtures = [
        artifacts[f"confirmation-bias-hub-page-{page_number}.json"]
        for page_number in range(1, 7)
    ]
    fixture = fixtures[0]

    assert fixture["scope"]["focus_model_id"] == "confirmation-bias"
    assert fixture["scope"]["unique_neighbor_count"] == 159
    assert fixture["page"]["eligible_count"] == 233
    assert fixture["page"]["shown_count"] == 40
    assert fixture["page"]["omitted_count"] == 193
    assert fixture["page"]["after_count"] == 193
    assert len(fixture["relations"]) == 40
    assert len(fixture["page"]["relation_ids"]) == 40
    assert "irrelevant" not in json.dumps(fixture).lower()

    all_relation_ids = [
        relation_id
        for page in fixtures
        for relation_id in page["page"]["relation_ids"]
    ]
    assert len(all_relation_ids) == 233
    assert len(set(all_relation_ids)) == 233
    relationship_graph = _load(ROOT / "data/relationship_graph.json")
    canonical_incident = sorted(
        (
            item["source_model_id"],
            item["target_model_id"],
            item["edge_type"],
            index,
        )
        for index, item in enumerate(relationship_graph)
        if item["source_model_id"] == "confirmation-bias"
        or item["target_model_id"] == "confirmation-bias"
    )
    assert all_relation_ids == [
        f"{source}__{target}__{relation_type}"
        for source, target, relation_type, _index in canonical_incident
    ]
    source_pointers = [
        relation["source_refs"][0]["json_pointer"]
        for page in fixtures
        for relation in page["relations"]
    ]
    assert source_pointers == [
        f"/{index}" for _source, _target, _relation_type, index in canonical_incident
    ]
    assert [page["page"]["page_number"] for page in fixtures] == list(
        range(1, 7)
    )
    assert [page["page"]["shown_count"] for page in fixtures] == [
        40,
        40,
        40,
        40,
        40,
        33,
    ]
    assert [page["page"]["before_count"] for page in fixtures] == [
        0,
        40,
        80,
        120,
        160,
        200,
    ]
    assert [page["page"]["after_count"] for page in fixtures] == [
        193,
        153,
        113,
        73,
        33,
        0,
    ]
    hub_coordinates = [
        next(
            item
            for item in page["layout"]["coordinates"]
            if item["model_id"] == "confirmation-bias"
        )
        for page in fixtures
    ]
    assert hub_coordinates == [hub_coordinates[0]] * 6
    assert len(
        {
            page["layout"]["configuration"]["layout_universe_sha256"]
            for page in fixtures
        }
    ) == 1
    coordinates_by_model: dict[str, set[tuple[float, float]]] = {}
    for page in fixtures:
        for coordinate in page["layout"]["coordinates"]:
            coordinates_by_model.setdefault(
                coordinate["model_id"], set()
            ).add((coordinate["x"], coordinate["y"]))
    assert all(len(coordinates) == 1 for coordinates in coordinates_by_model.values())


def test_medium_confidence_fixture_preserves_caution_without_certification() -> None:
    fixture = build_phase1_package(ROOT)["artifacts"][
        "medium-confidence-relation.json"
    ]

    assert fixture["scope"]["semantic_fixture"] == (
        "medium_confidence_not_certification"
    )
    assert fixture["page"]["eligible_count"] == 1
    assert fixture["relations"][0]["confidence"] == "medium"
    assert fixture["relations"][0]["relation_id"] == (
        "authenticity__rationalization__antagonist"
    )
    assert "not_relation_truth_certification" in fixture["non_claims"]
    relation = fixture["relations"][0]
    canonical = _load(ROOT / "data/relationship_graph.json")[79]
    assert relation["source_refs"][0]["json_pointer"] == "/79"
    assert relation["source_refs"][0]["sha256"] == EXPECTED_SOURCE_HASHES[
        "data/relationship_graph.json"
    ]
    assert relation["source_model_id"] == canonical["source_model_id"]
    assert relation["target_model_id"] == canonical["target_model_id"]
    assert relation["relation_type"] == canonical["edge_type"]
    assert relation["summary"] == canonical["source_description"]
    assert relation["direction"] == "source_authored"
    assert {
        "affinity",
        "composition_affinity",
        "rank",
        "score",
        "weight",
    }.isdisjoint(relation)


def test_relation_records_keep_source_indices_and_forbid_visual_scores() -> None:
    package = build_phase1_package(ROOT)
    forbidden = {"affinity", "composition_affinity", "rank", "score", "weight"}

    for path, payload in package["artifacts"].items():
        if payload["schema_version"] != "lolla.atlas_projection.v1":
            continue
        for relation in payload["relations"]:
            assert forbidden.isdisjoint(relation)
            graph_ref = relation["source_refs"][0]
            assert graph_ref["path"] == "data/relationship_graph.json"
            assert graph_ref["json_pointer"].startswith("/")
            assert graph_ref["sha256"] == EXPECTED_SOURCE_HASHES[
                "data/relationship_graph.json"
            ]


def test_complete_model_and_relation_pages_are_source_backed_without_generated_copy() -> None:
    package = build_phase1_package(ROOT)
    model_page = package["artifacts"]["pages/model-abstraction.json"]
    relation_page = package["artifacts"][
        "pages/relation-abstraction-first-principles-thinking-ally.json"
    ]

    assert model_page["schema_version"] == "lolla.atlas_model_page.v1"
    assert model_page["model"]["model_id"] == "abstraction"
    assert set(model_page["sections"]) == {
        "definition",
        "use_when",
        "avoid_when",
        "reasoning_profile",
        "failure_modes",
        "premortem_questions",
        "heuristics",
    }
    assert all(
        section["provenance"] for section in model_page["sections"].values()
    )
    assert model_page["status"]["content_generation"] == (
        "source_copied_or_format_normalized_only"
    )
    assert model_page["status"]["publication"] == "blocked_pending_rights_review"

    assert relation_page["schema_version"] == "lolla.atlas_relation_page.v1"
    relation = relation_page["relation"]
    assert relation["relation_id"] == (
        "abstraction__first-principles-thinking__ally"
    )
    assert relation["source_model_id"] == "abstraction"
    assert relation["target_model_id"] == "first-principles-thinking"
    assert set(relation_page["sections"]) == {
        "relation_summary",
        "why_it_matters",
        "misread_risk",
        "activation_condition",
        "source_excerpt",
        "parallel_record_context",
    }
    assert relation_page["sections"]["why_it_matters"]["text"]
    assert relation_page["sections"]["misread_risk"]["text"]
    assert relation_page["sections"]["parallel_record_context"][
        "parallel_relation_ids"
    ] == [
        "abstraction__first-principles-thinking__ally",
        "abstraction__first-principles-thinking__tension",
    ]
    assert relation_page["status"]["content_generation"] == "source_copied_only"


def test_manifest_binds_every_artifact_and_layout() -> None:
    package = build_phase1_package(ROOT)
    manifest = package["manifest"]

    assert manifest["schema_version"] == "lolla.atlas_projection_manifest.v1"
    assert len(manifest["artifacts"]) == 12
    for entry in manifest["artifacts"]:
        payload = package["artifacts"][entry["path"]]
        assert entry["sha256"] == hashlib.sha256(
            canonical_json_bytes(payload)
        ).hexdigest()
        if entry["artifact_type"] == "projection":
            assert entry["coordinate_sha256"] == payload["layout"][
                "coordinate_sha256"
            ]


def test_projection_validation_rejects_count_and_coordinate_drift() -> None:
    projection = build_phase1_package(ROOT)["artifacts"]["ordinary-navigation.json"]

    count_drift = json.loads(json.dumps(projection))
    count_drift["page"]["omitted_count"] += 1
    with pytest.raises(AtlasProjectionError, match="page counts"):
        validate_projection(count_drift)

    coordinate_drift = json.loads(json.dumps(projection))
    coordinate_drift["layout"]["coordinates"][0]["x"] += 1
    with pytest.raises(AtlasProjectionError, match="coordinate hash"):
        validate_projection(coordinate_drift)


def test_phase1_evidence_receipt_binds_screenshots_and_open_human_gates() -> None:
    evidence = _load(EVIDENCE_PATH)

    assert evidence["status"] == (
        "local_implementation_complete_founder_gate_pending"
    )
    assert evidence["projection_manifest"]["provider_calls"] == 0
    assert evidence["projection_manifest"]["provider_cost_usd"] == 0.0
    assert evidence["scope_boundaries"]["teacher_disposition"] == "park"
    assert evidence["scope_boundaries"]["phase_2"] == "not_authorized"
    assert evidence["interaction_evidence"][
        "manual_native_screen_reader_review"
    ] == "pending_human"
    assert evidence["interaction_evidence"][
        "founder_composition_and_motion_review"
    ] == "pending_founder"
    assert len(evidence["screenshots"]) == 20
    for screenshot in evidence["screenshots"]:
        path = ROOT / screenshot["path"]
        assert path.is_file()
        assert sha256_bytes(path.read_bytes()) == screenshot["sha256"]

    manifest = ROOT / evidence["projection_manifest"]["path"]
    assert sha256_bytes(manifest.read_bytes()) == evidence[
        "projection_manifest"
    ]["sha256"]
