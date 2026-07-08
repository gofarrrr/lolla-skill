from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-library-graph-scope-decision-v0.md"
DECISION = REPO_ROOT / "docs/product/observatory-library-graph-scope-decision-v0.json"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-library-graph-scope-decision-v0/"
    "review.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    return json.loads(_read(path))


def test_library_graph_scope_decision_files_exist_and_are_indexed() -> None:
    assert DOC.exists()
    assert DECISION.exists()
    assert REVIEW.exists()

    readme = _read(README)
    assert "Observatory Library Graph Scope And Coverage Decision" in readme
    assert "observatory-library-graph-scope-decision-v0.md" in readme
    assert "observatory-library-graph-scope-decision-v0.json" in readme


def test_library_graph_scope_decision_reconciles_prd_package_state() -> None:
    doc = _read(DOC)
    decision = _json(DECISION)

    for phrase in [
        "PR-P1 through PR-P10",
        "PR-P11",
        "PR-P12",
        "PR-P13",
        "package gate exists",
        "Full-corpus graph planning is not the next default surface.",
        "Full-corpus graph pilot is not authorized by the package gate.",
    ]:
        assert phrase in doc

    package = decision["teacher_prd_package_state"]
    assert package["done_through_pr_p11"] is True
    assert package["pr_p1_through_pr_p10"] == "published"
    assert package["pr_p11"] == "package_gate_exists"
    assert package["pr_p12"]["status"] == "deferred"
    assert package["pr_p13"]["status"] == "deferred"
    assert package["product_proof_claimed"] is False
    assert package["human_validation_claimed"] is False
    assert package["runtime_integration_authorized"] is False


def test_library_graph_scope_decision_reconciles_counts() -> None:
    doc = _read(DOC)
    decision = _json(DECISION)
    review = _json(REVIEW)

    for phrase in [
        "48 is the accountability universe.",
        "36 is the prior exposure-audit rollup.",
        "29 is the current Receipts/UI inventory.",
        "8 is the first-read product path.",
    ]:
        assert phrase in doc

    counts = decision["coverage_counts"]
    assert counts["broad_visibility_matrix_families"] == 48
    assert counts["data_exposure_audit_items"] == 36
    assert counts["current_run_inventory_ui_families"] == 29
    assert counts["first_read_product_path_families"] == 8
    assert counts["flatten_into_one_screen"] is False
    assert review["coverage_counts"] == {
        "broad_visibility_matrix_families": 48,
        "data_exposure_audit_items": 36,
        "current_run_inventory_ui_families": 29,
        "first_read_product_path_families": 8,
        "flatten_into_one_screen": False,
    }


def test_library_graph_scope_decision_defines_five_graph_modes() -> None:
    doc = _read(DOC)
    decision = _json(DECISION)

    modes = {mode["id"]: mode for mode in decision["graph_modes"]}
    assert list(modes) == [
        "selected_run_learning_map",
        "model_detail_reviewed_local_neighborhood",
        "model_detail_visual_neighborhood",
        "filtered_library_graph",
        "full_corpus_graph",
    ]

    assert modes["selected_run_learning_map"]["status"] == "present"
    assert modes["model_detail_reviewed_local_neighborhood"]["status"] == (
        "present_as_cards_not_visual_graph"
    )
    assert modes["model_detail_visual_neighborhood"]["status"] == (
        "recommended_next_ui_build"
    )
    assert modes["filtered_library_graph"]["status"] == "future"
    assert modes["full_corpus_graph"]["status"] == "future_not_first_surface"

    for phrase in [
        "Selected-run learning map",
        "Model-detail reviewed local neighborhood",
        "present as cards, not visual graph",
        "Model-detail visual neighborhood",
        "recommended next UI build",
        "Filtered library graph",
        "Full corpus graph",
        "future, not first surface",
        "edges are navigation, not proof",
    ]:
        assert phrase in doc


def test_library_graph_scope_decision_keeps_teacher_inside_observatory() -> None:
    doc = _read(DOC)
    decision = _json(DECISION)

    assert "Teacher is not a separate main product path right now." in doc
    assert "Teacher lives inside Observatory" in doc
    assert decision["teacher_surface_decision"] == {
        "observatory_is_portable_presentation_surface": True,
        "standalone_teacher_main_path_for_current_phase": False,
        "teacher_lives_inside_observatory": True,
        "teacher_surface_parts": [
            "Learn",
            "Models",
            "Relations",
            "Map",
            "Receipts",
        ],
    }
    assert decision["product_thesis"] == [
        "selected run is the anchor",
        "outcome is the first read",
        "Teacher is the practice layer",
        "models are reusable concepts",
        "relations are model-pair lessons",
        "map is navigation",
        "receipts are accountability",
        "Download MD is private agent memory",
        "Advanced Audit is technical inspection",
    ]


def test_library_graph_scope_decision_assigns_data_exposure_layers() -> None:
    doc = _read(DOC)
    decision = _json(DECISION)

    layers = {layer["layer"]: layer for layer in decision["data_exposure_policy"]}
    assert list(layers) == [
        "default_first_read",
        "primary_product_surfaces",
        "expandable_product_detail",
        "explicit_export",
        "optional_technical_inspection",
        "operator_only_inspection",
        "future_design",
        "private_hidden",
    ]
    assert "selected run context" in layers["default_first_read"]["shown"]
    assert "reviewed model-neighborhood cards" in layers[
        "expandable_product_detail"
    ]["shown"]
    assert "conversation memory Markdown through Download MD" in layers[
        "explicit_export"
    ]["shown"]
    assert "raw 1:1 transcript in normal UI" in layers["private_hidden"][
        "not_shown"
    ]

    for phrase in [
        "Default first read",
        "Primary product surfaces",
        "Expandable product detail",
        "Explicit export",
        "Optional technical inspection",
        "Operator-only inspection",
        "Future design",
        "Private hidden",
        "Raw transcript belongs only in explicit private Markdown export",
    ]:
        assert phrase in doc


def test_library_graph_scope_decision_confirms_agent_memory_and_next_pr() -> None:
    doc = _read(DOC)
    decision = _json(DECISION)
    review = _json(REVIEW)

    agent_memory = decision["agent_memory"]
    assert agent_memory["download_md_is_current_agent_memory_path"] is True
    assert agent_memory["raw_transcript_default_ui"] is False
    assert agent_memory["raw_transcript_explicit_private_markdown_export"] is True
    assert agent_memory["archive_mutation_required"] is False
    assert agent_memory["provider_or_model_calls_required"] is False

    next_pr = decision["recommended_next_pr"]
    assert next_pr["title"] == "Observatory Model Detail Visual Neighborhood v0"
    assert next_pr["must_use_existing_reviewed_neighborhood"] is True
    assert next_pr["must_remain_model_detail_local"] is True
    assert next_pr["full_corpus_graph_allowed"] is False
    assert next_pr["raw_affinity_allowed"] is False
    assert next_pr["embedding_similarity_as_relation_semantics_allowed"] is False
    assert review["recommended_next_pr"] == (
        "Add Observatory model detail visual neighborhood"
    )

    for phrase in [
        "Download MD is the current private agent-memory export path.",
        "The raw 1:1 transcript stays out of normal UI",
        "Observatory Model Detail Visual Neighborhood v0",
        "I clicked Authority Bias. What else is directly connected to it, and why?",
        "do not build the full corpus graph",
    ]:
        assert phrase in doc


def test_library_graph_scope_decision_review_json_records_boundaries() -> None:
    review = _json(REVIEW)
    decision = _json(DECISION)

    assert review["review_id"] == "observatory-library-graph-scope-decision-v0"
    assert review["status"] == "implemented"
    assert review["decision_gate"] == (
        "proceed_to_observatory_model_detail_visual_neighborhood_v0"
    )
    assert review["implemented"]["coverage_counts_reconciled"] is True
    assert review["implemented"]["graph_modes_defined"] is True
    assert review["implemented"]["teacher_inside_observatory_confirmed"] is True
    assert review["implemented"]["full_corpus_graph_deferred"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False

    for key, value in review["graph_mode_decisions"].items():
        mode = next(mode for mode in decision["graph_modes"] if mode["id"] == key)
        assert mode["status"] == value

    for key in [
        "runs_lolla",
        "invokes_lolla_skill",
        "calls_provider_or_model",
        "creates_new_run",
        "generates_sidecars",
        "wires_runtime_or_default_skill_behavior",
        "mutates_archives",
        "touches_skill_md",
        "touches_scripts_skill",
        "touches_archive_run",
        "touches_compiled_observatory_build",
    ]:
        assert review["boundary"][key] is False
        assert decision["boundary"][key] is False

    for key in [
        "product_proof",
        "human_validated",
        "answer_correctness",
        "advice_correctness",
        "runtime_integration_authorized",
        "action_authorized",
        "graph_edges_are_proof",
        "embedding_similarity_is_validated_relation_semantics",
    ]:
        assert review["non_claims"][key] is False
        assert decision["non_claims"][key] is False


def test_library_graph_scope_decision_links_and_private_markers_are_clean() -> None:
    missing = []
    for path in [DOC, README]:
        text = _read(path)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    combined = "\n".join(_read(path) for path in [DOC, DECISION, REVIEW])

    assert missing == []
    assert "/" + "Users/" not in combined
    assert "Desktop/" + "Apps" not in combined
    assert "product_proof\": true" not in combined
    assert "human_validated\": true" not in combined
    assert "answer_correctness\": true" not in combined
    assert "advice_correctness\": true" not in combined
    assert "runtime_integration_authorized\": true" not in combined
    assert "action_authorized\": true" not in combined
