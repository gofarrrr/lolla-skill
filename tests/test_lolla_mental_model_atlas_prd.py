from __future__ import annotations

import hashlib
import json
import re
import subprocess
import struct
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/evals/lolla-mental-model-atlas-prd-v1.json"
PRD_PATH = ROOT / "docs/product/lolla-mental-model-atlas-and-teacher-prd-v1.md"
REFERENCE_PATH = ROOT / "docs/product/lolla-mental-model-atlas-marble-reference-2026-07-15.md"
PLAN_PATH = ROOT / "plans/lolla-mental-model-atlas-tracer-bullet-plan-2026-07-15.md"
VIBRANT_EVIDENCE_PATH = (
    ROOT / "docs/evals/lolla-mental-model-atlas-vibrant-editorial-refinement-evidence-v1.json"
)
VIBRANT_RESULT_PATH = (
    ROOT / "docs/product/lolla-mental-model-atlas-vibrant-editorial-refinement-result-2026-07-16.md"
)
VIBRANT_PLAN_PATH = (
    ROOT / "plans/lolla-mental-model-atlas-vibrant-editorial-refinement-plan-2026-07-16.md"
)
MONOCHROME_EVIDENCE_PATH = (
    ROOT / "docs/evals/lolla-mental-model-atlas-monochrome-structure-study-evidence-v1.json"
)
MONOCHROME_RESULT_PATH = (
    ROOT / "docs/product/lolla-mental-model-atlas-monochrome-structure-study-result-2026-07-16.md"
)
MONOCHROME_PLAN_PATH = (
    ROOT / "plans/lolla-mental-model-atlas-monochrome-structure-study-plan-2026-07-16.md"
)
GUIDED_ENTRY_EVIDENCE_PATH = (
    ROOT / "docs/evals/lolla-mental-model-atlas-guided-entry-repair-evidence-v1.json"
)
GUIDED_ENTRY_RESULT_PATH = (
    ROOT / "docs/product/lolla-mental-model-atlas-guided-entry-repair-result-2026-07-16.md"
)
VIBRANT_REVIEWED_CHECKPOINT = "82313ff2c571503a13ab6a719e8f29450bec654f"
MONOCHROME_IMPLEMENTATION_CHECKPOINT = "5dab11434dc49d84326f05bc41f34bb7b117c157"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _png_size(path: Path) -> tuple[int, int]:
    payload = path.read_bytes()[:24]
    assert payload[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", payload[16:24])


def _historical_text(checkpoint: str, relative: str) -> str:
    """Read superseded visual evidence without keeping it in the active app."""
    return subprocess.run(
        ["git", "show", f"{checkpoint}:{relative}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def test_atlas_prd_contract_is_grounded_in_the_canonical_substrate() -> None:
    contract = _json(CONTRACT_PATH)
    baseline = contract["source_baseline"]

    manifest_path = ROOT / baseline["model_source_manifest"]["path"]
    knowledge_path = ROOT / baseline["knowledge_graph"]["path"]
    relationship_path = ROOT / baseline["relationship_graph"]["path"]
    affordance_path = ROOT / baseline["v60_affordances"]["path"]

    manifest = _json(manifest_path)
    knowledge = _json(knowledge_path)
    relationships = _json(relationship_path)
    affordances = _json(affordance_path)

    assert contract["canonical_planning_base"] == "2f05fd1ca7081f602317d670faad8d1293d5b0ff"
    assert contract["status"] == "phase1_relational_editorial_tracer_founder_gate_pending"

    assert _sha256(manifest_path) == baseline["model_source_manifest"]["sha256"]
    assert _sha256(knowledge_path) == baseline["knowledge_graph"]["sha256"]
    assert _sha256(relationship_path) == baseline["relationship_graph"]["sha256"]
    assert _sha256(affordance_path) == baseline["v60_affordances"]["sha256"]

    manifest_ids = [item["model_id"] for item in manifest["files"]]
    assert len(manifest_ids) == 222
    assert len(set(manifest_ids)) == 222
    assert len({item["sha256"] for item in manifest["files"]}) == 222
    assert set(manifest_ids) == set(knowledge["models"])

    assert len(knowledge["models"]) == 222
    assert len(knowledge["tendencies"]) == 25
    assert len(knowledge["edges"]) == 1742
    assert len(knowledge["prerequisite_edges"]) == 15
    assert len(knowledge["reframing_routing"]) == 15
    assert len(knowledge["structural_coverage_routing"]["dimension_ids"]) == 15

    page_material = baseline["knowledge_graph"]["model_page_material"]
    assert sum(len(model["select_when"]) for model in knowledge["models"].values()) == page_material["select_when_records"]
    assert sum(len(model["danger_when"]) for model in knowledge["models"].values()) == page_material["danger_when_records"]
    assert sum(len(model["failure_modes"]) for model in knowledge["models"].values()) == page_material["failure_mode_records"]
    assert sum(len(model["premortem_questions"]) for model in knowledge["models"].values()) == page_material["premortem_question_records"]
    assert sum(len(model["heuristics"]) for model in knowledge["models"].values()) == page_material["heuristic_records"]
    assert sum(len(model["reasoning_types"]) for model in knowledge["models"].values()) == page_material["reasoning_type_assignments"]
    assert all(
        model[field]
        for model in knowledge["models"].values()
        for field in (
            "select_when",
            "danger_when",
            "failure_modes",
            "premortem_questions",
            "heuristics",
            "reasoning_types",
        )
    )

    relation_counts = Counter(item["edge_type"] for item in relationships)
    confidence_counts = Counter(item["confidence"] for item in relationships)
    assert len(relationships) == 1358
    assert relation_counts == Counter({"ally": 523, "tension": 491, "antagonist": 344})
    assert confidence_counts == Counter({"high": 1337, "medium": 21})
    assert all(item["curated"] is True for item in relationships)
    assert all(item["is_reciprocal"] is False for item in relationships)

    family_files = sorted((ROOT / "data/family_semantics").glob("*.json"))
    family_members = [member for path in family_files for member in _json(path)["members"]]
    family_member_counts = Counter(family_members)
    assert len(family_files) == 24
    assert len(family_members) == 141
    assert len(family_member_counts) == 75
    assert 222 - len(family_member_counts) == 147
    assert sum(count > 1 for count in family_member_counts.values()) == 24

    assert len(affordances["model_records"]) == 222
    assert len(affordances["affordances"]) == 306
    assert len(affordances["absence_records"]) == 697
    assert affordances["status"] == "draft_review_only"


def test_atlas_contract_preserves_direction_parallel_records_and_hub_missingness() -> None:
    contract = _json(CONTRACT_PATH)
    relationships = _json(ROOT / "data/relationship_graph.json")

    mixed = {
        item["edge_type"]
        for item in relationships
        if item["source_model_id"] == "abstraction"
        and item["target_model_id"] == "first-principles-thinking"
    }
    assert mixed == {"ally", "tension"}

    directions = {
        (item["source_model_id"], item["target_model_id"])
        for item in relationships
        if {item["source_model_id"], item["target_model_id"]}
        == {"active-listening", "prisoners-dilemma"}
    }
    assert directions == {
        ("active-listening", "prisoners-dilemma"),
        ("prisoners-dilemma", "active-listening"),
    }

    incident = [
        item
        for item in relationships
        if "confirmation-bias" in {item["source_model_id"], item["target_model_id"]}
    ]
    neighbors = {
        item["target_model_id"]
        if item["source_model_id"] == "confirmation-bias"
        else item["source_model_id"]
        for item in incident
    }
    assert len(incident) == 233
    assert len(neighbors) == 159

    interaction = contract["interaction_contract"]
    architecture = contract["architecture"]
    assert interaction["idle_nodes_visible"] == 222
    assert interaction["idle_edges_visible"] == 0
    assert interaction["focused_edge_page_size_maximum"] == 40
    assert interaction["exact_available_visible_omitted_counts_required"] is True
    assert interaction["direction_preserved"] is True
    assert interaction["parallel_relation_records_preserved"] is True
    assert interaction["selected_and_hover_state_must_be_independent"] is True
    assert architecture["family_is_default_layout_partition"] is False
    assert architecture["default_node_size"] == "uniform_except_interaction_state"
    assert architecture["default_node_color"] == "neutral_until_explicit_reviewed_overlay"
    assert architecture["raw_affinity_used_for_visual_weight_or_distance"] is False
    assert architecture["embedding_rank_exposed_as_relation"] is False


def test_atlas_prd_defines_a_complete_but_unauthed_product_lane() -> None:
    contract = _json(CONTRACT_PATH)
    routes = {surface["route"] for surface in contract["surfaces"]}
    required_routes = {
        "/atlas",
        "/models",
        "/models/:slug",
        "/relations/:relationId",
        "/learn",
        "/learn/:journeyId",
    }
    assert routes == required_routes

    phases = contract["tracer_bullet_phases"]
    assert [phase["phase"] for phase in phases] == [1, 2, 3, 4, 5, 6]
    assert phases[0]["status"] == (
        "implemented_local_relational_editorial_tracer_founder_gate_pending"
    )
    assert all(phase["status"] == "not_authorized" for phase in phases[1:])

    lifecycle = contract["current_lifecycle"]
    boundaries = contract["boundaries"]
    assert lifecycle["disposition"] == "park"
    assert lifecycle["founder_selected_user_job_now_defined"] is True
    assert lifecycle["real_user_evidence_plan_now_defined"] is True
    assert lifecycle["lifecycle_change_authorized"] is False
    assert lifecycle["implementation_authorized"] is False
    assert lifecycle["phase1_implementation_completed"] is True
    assert lifecycle["phase1_authorization_consumed"] is True
    assert lifecycle["founder_visual_acceptance"] == (
        "pending_relational_editorial_tracer_review"
    )
    correction = contract["phase1_card_first_correction"]
    assert correction["historical_v1_modified"] is False
    assert correction["human_reader_projection"] == (
        "five_reviewed_single_open_source_chapters_with_full_source_inspection_mode"
    )
    assert correction["source_curator_appendix_default"] == "collapsed"
    assert correction["connection_presentation"] == (
        "compact_group_index_plus_one_selected_source_typed_line_target_detail_with_exact_records_preserved"
    )
    assert correction["relationship_visual_grammar"] == (
        "written_labels_plus_solid_ally_dotted_tension_dashed_cross_antagonist"
    )
    assert correction["visual_scope"] == (
        "abstraction_model_route_only_not_global_svg_or_canvas"
    )
    assert correction["authoritative_source_card_coverage"] == "complete"
    assert correction["operational_knowledge_graph_record_coverage"] == (
        "complete_separately_labelled"
    )
    assert correction["incident_relationship_record_membership"] == (
        "complete_separately_labelled"
    )
    assert correction["aggregate_learning_page_coverage"] == "partial"
    assert correction["runtime_affordance_projection"] == "available_not_projected"
    assert correction["distinct_reviewed_practice_prompts"] == "missing"
    assert correction["curated_teacher_journeys"] == "missing"
    assert boundaries["provider_calls_authorized"] == 0
    assert boundaries["provider_cost_authorized_usd"] == 0.0
    assert boundaries["runtime_integration_authorized"] is False
    assert boundaries["observatory_expansion_authorized"] is False
    assert boundaries["public_deployment_authorized"] is False
    assert boundaries["r4_or_r5_restart_authorized"] is False
    assert contract["provider_calls"] == 0
    assert contract["provider_cost_usd"] == 0.0

    expected_nonclaims = {
        "not_product_proof",
        "not_human_validation",
        "not_market_validation",
        "not_publication_rights_clearance",
        "not_runtime_integration",
        "not_observatory_ownership",
        "not_r4_or_decision_trail_restart",
        "not_action_authorization",
        "not_graph_relevance_proof",
        "not_relation_truth_certification",
        "not_mastery_certification",
        "not_provider_authorization",
        "not_implementation_authorization",
    }
    assert set(contract["nonclaims"]) == expected_nonclaims

    required_accessibility = {
        "synchronized_semantic_node_list",
        "complete_directed_relation_table",
        "parallel_records_not_collapsed",
        "prefers_reduced_motion_and_explicit_pause",
        "no_essential_hover_only_information",
        "webgl_failure_fallback",
    }
    assert required_accessibility <= set(contract["accessibility_requirements"])


def test_atlas_prd_and_handoffs_are_present_and_label_the_reference_honestly() -> None:
    contract = _json(CONTRACT_PATH)
    for path in (PRD_PATH, REFERENCE_PATH, PLAN_PATH):
        assert path.is_file()
        assert path.read_text(encoding="utf-8").strip()

    reference = contract["reference"]
    video = reference["local_founder_video"]
    assert reference["marble_repository"] == "https://github.com/withmarbleapp/os-taxonomy"
    assert reference["marble_explorer"] == "https://withmarble.com/curriculum/"
    assert video["sha256"] == "910bdb4f96e4af499ae62bce493d75c2b831b7d5ce128a4019563030b0ed6370"
    assert video["committed"] is False
    assert video["repository_dependency"] is False

    prd = PRD_PATH.read_text(encoding="utf-8")
    plan = PLAN_PATH.read_text(encoding="utf-8")
    reference_doc = REFERENCE_PATH.read_text(encoding="utf-8")
    assert "Atlas shows the territory" in prd
    assert "Teacher guides a journey" in prd
    assert "Mental Model Teacher remains" in plan
    assert "No Marble code, data, taxonomy, text, screenshots" in reference_doc


def test_vibrant_editorial_refinement_is_token_bound_truthful_and_reproducible() -> None:
    evidence = _json(VIBRANT_EVIDENCE_PATH)
    assert evidence["status"] == "local_founder_validation_ready_unpublished"
    assert evidence["decision"] == (
        "vibrant_editorial_abstraction_tracer_ready_for_founder_validation"
    )
    assert evidence["implementation_parent"] == (
        "b9caec54ee444e306c6383fef78fa1d0347e514a"
    )
    assert evidence["provider_calls"] == 0
    assert evidence["provider_cost_usd"] == 0.0
    assert evidence["publication_authorized"] is False

    scope = evidence["scope"]
    assert scope == {
        "route": "/models/abstraction",
        "route_scoped": True,
        "other_model_pages_changed": False,
        "global_svg_canvas_changed": False,
        "source_or_graph_artifacts_changed": False,
    }

    art = evidence["art_direction"]
    assert art["name"] == "vibrant_editorial_field_guide"
    assert art["signature_element"] == "four_stop_functional_page_signal_path"
    assert art["palette_roles"] == {
        "structural_ink": "#060761",
        "primary_action": "#41FFA7",
        "source_and_current_selection": "#C4FF4D",
        "derived_relationship_layer": "#BA8CFF",
        "quiet_field": "#E7E8E4",
        "surface": "#F7F7F2",
        "error_only": "#A5163A",
    }
    assert art["color_encodes_relationship_type"] is False
    assert art["color_encodes_rank_confidence_relevance_or_truth"] is False

    relationship = evidence["relationship_contract"]
    assert relationship["exact_records"] == 12
    assert relationship["authored_outward"] == 5
    assert relationship["authored_inward"] == 7
    assert relationship["relation_type_counts"] == {
        "ally": 7,
        "tension": 4,
        "antagonist": 1,
    }
    assert relationship["parallel_records_preserved"] is True
    assert relationship["authored_direction_preserved"] is True
    assert relationship["grayscale_distinction_checked"] is True

    screenshots = evidence["screenshots"]
    assert len(screenshots) == 12
    assert len({item["path"] for item in screenshots}) == 12
    for item in screenshots:
        path = ROOT / item["path"]
        assert path.is_file()
        assert _sha256(path) == item["sha256"]
        assert _png_size(path) == (item["width"], item["height"])

    css = _historical_text(
        VIBRANT_REVIEWED_CHECKPOINT,
        "apps/mental-model-atlas/src/styles.css",
    )
    marker = "/* Founder-palette refinement for the Abstraction tracer."
    assert css.count(marker) == 1
    active_route_layer = css[css.index(marker):].lower()
    for token in ("#060761", "#41ffa7", "#c4ff4d", "#ba8cff"):
        assert token in active_route_layer
    for superseded in ("#a4471e", "#1d6f67", "#6e56cf", "#c65a1e"):
        assert superseded not in active_route_layer
    assert '"inter"' not in active_route_layer
    assert "@media (forced-colors: active)" in active_route_layer
    assert '.relation-antagonist .connection-tab-line::after' in active_route_layer
    assert 'content: "";' in active_route_layer
    assert '.motion-control .motion-label' in css
    assert "display: inline;" in css

    app = (ROOT / "apps/mental-model-atlas/src/App.tsx").read_text(encoding="utf-8")
    assert 'aria-label={motionControlLabel}' in app
    assert 'aria-pressed={effectiveMotionPaused}' not in app
    assert '"Resume motion"' in app
    assert 'data-motion-state={effectiveMotionPaused ? "paused" : "running"}' in app

    historical_result = VIBRANT_RESULT_PATH.read_text(encoding="utf-8")
    for label in (
        "Learn the source",
        "Put it to work",
        "Read the relations",
        "Keep judging",
    ):
        assert label in historical_result

    connections = (
        ROOT / "apps/mental-model-atlas/src/components/ModelConnections.tsx"
    ).read_text(encoding="utf-8")
    for label in ("Solid line", "Dotted line", "Dashed line with a cross"):
        assert label in connections

    for path in (VIBRANT_RESULT_PATH, VIBRANT_PLAN_PATH):
        assert path.is_file()
        assert "vibrant editorial" in path.read_text(encoding="utf-8").lower()


def test_monochrome_structure_study_is_achromatic_additive_and_reproducible() -> None:
    evidence = _json(MONOCHROME_EVIDENCE_PATH)
    assert evidence["status"] == "local_founder_validation_ready_unpublished"
    assert evidence["decision"] == (
        "monochrome_structure_study_ready_for_founder_validation"
    )
    assert evidence["implementation_parent"] == (
        "82313ff2c571503a13ab6a719e8f29450bec654f"
    )
    assert evidence["provider_calls"] == 0
    assert evidence["provider_cost_usd"] == 0.0
    assert evidence["publication_authorized"] is False

    scope = evidence["scope"]
    assert scope["routes"] == ["/atlas", "/models", "/models/abstraction"]
    assert scope["source_or_graph_artifacts_changed"] is False
    assert scope["graph_geometry_or_relationship_semantics_changed"] is False
    assert scope["future_color_system_selected"] is False

    art = evidence["art_direction"]
    assert art["name"] == "monochrome_structural_field_guide"
    assert art["color_mode"] == "achromatic_only"
    assert art["rendered_chromatic_pixels_per_screenshot"] == 0
    assert art["relationship_type_uses_hue"] is False
    assert art["selection_uses_hue"] is False

    relationship = evidence["relationship_contract"]
    assert relationship["exact_model_page_records"] == 12
    assert relationship["authored_outward"] == 5
    assert relationship["authored_inward"] == 7
    assert relationship["relation_type_counts"] == {
        "ally": 7,
        "tension": 4,
        "antagonist": 1,
    }
    assert relationship["parallel_records_preserved"] is True
    assert relationship["authored_direction_preserved"] is True

    screenshots = evidence["screenshots"]
    assert len(screenshots) == 8
    assert len({item["path"] for item in screenshots}) == 8
    for item in screenshots:
        path = ROOT / item["path"]
        assert path.is_file()
        assert _sha256(path) == item["sha256"]
        assert _png_size(path) == (item["width"], item["height"])
        assert item["chromatic_pixels"] == 0

    css = _historical_text(
        MONOCHROME_IMPLEMENTATION_CHECKPOINT,
        "apps/mental-model-atlas/src/restraint.css",
    )
    literals = re.findall(r"#[0-9a-fA-F]{3,8}\b", css)
    assert literals
    for literal in literals:
        value = literal[1:]
        if len(value) == 3:
            value = "".join(character * 2 for character in value)
        red, green, blue = (
            int(value[0:2], 16),
            int(value[2:4], 16),
            int(value[4:6], 16),
        )
        assert red == green == blue, literal
    assert "--ally: #171717" in css
    assert "--antagonist: #171717" in css
    assert "--tension: #171717" in css

    main = _historical_text(
        MONOCHROME_IMPLEMENTATION_CHECKPOINT,
        "apps/mental-model-atlas/src/main.tsx",
    )
    assert main.index('import "./styles.css"') < main.index('import "./restraint.css"')

    model_page = (ROOT / "apps/mental-model-atlas/src/routes/ModelPage.tsx").read_text(
        encoding="utf-8"
    )
    for label in ("Understand", "Use it", "Connections", "Perspective"):
        assert label in model_page

    connections = (
        ROOT / "apps/mental-model-atlas/src/components/ModelConnections.tsx"
    ).read_text(encoding="utf-8")
    assert "Line form and direction carry the meaning." in connections
    assert "color is only a cue" not in connections.lower()

    for path in (MONOCHROME_RESULT_PATH, MONOCHROME_PLAN_PATH):
        assert path.is_file()
        assert "monochrome" in path.read_text(encoding="utf-8").lower()


def test_guided_entry_repair_removes_redundancy_without_losing_source_custody() -> None:
    evidence = _json(GUIDED_ENTRY_EVIDENCE_PATH)
    assert evidence["status"] == "local_founder_validation_ready_unpublished"
    assert evidence["decision"] == (
        "breadcrumb_aligned_redundant_source_intro_removed"
    )
    assert evidence["implementation_parent"] == (
        "5dab11434dc49d84326f05bc41f34bb7b117c157"
    )
    assert evidence["provider_calls"] == 0
    assert evidence["provider_cost_usd"] == 0.0
    assert evidence["publication_authorized"] is False

    layout = evidence["layout_contract"]
    assert layout["breadcrumb_text_y_desktop"] == [110.578125] * 3
    assert layout["breadcrumb_text_y_mobile"] == [172.96875] * 3
    assert layout["mobile_document_width_px"] == 390
    assert layout["redundant_source_heading_count"] == 0
    assert layout["redundant_source_title_box_count"] == 0

    custody = evidence["source_custody"]
    assert custody["guided_mode_source_title_visible"] is False
    assert custody["full_source_mode_source_title_visible"] is True
    assert custody["full_source_mode_visible_chapters"] == 5
    assert custody["source_line_one_preserved"] is True
    assert custody["source_or_graph_artifacts_changed"] is False

    screenshots = evidence["screenshots"]
    assert len(screenshots) == 4
    for item in screenshots:
        path = ROOT / item["path"]
        assert path.is_file()
        assert _sha256(path) == item["sha256"]
        assert _png_size(path) == (item["width"], item["height"])
        assert item["chromatic_pixels"] == 0

    assert GUIDED_ENTRY_RESULT_PATH.is_file()
    result = GUIDED_ENTRY_RESULT_PATH.read_text(encoding="utf-8")
    assert "No product reason justified keeping it" in result
    assert "complete-source mode" in result
