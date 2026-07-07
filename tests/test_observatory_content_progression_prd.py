from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-content-progression-prd-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-content-progression-prd-v0/review.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    return json.loads(_read(path))


def test_content_progression_prd_files_exist_and_are_indexed() -> None:
    assert DOC.exists()
    assert REVIEW.exists()

    readme = _read(README)
    assert "Observatory Content Progression PRD" in readme
    assert "observatory-content-progression-prd-v0.md" in readme


def test_content_progression_prd_records_core_counts_and_grouping() -> None:
    text = _read(DOC)
    review = _json(REVIEW)

    for phrase in [
        "48 broad data/source families",
        "29 current run-inventory UI families",
        "8 first-read product-path families",
        "show the 8 product-path families",
        "account for the other 21 current UI families",
        "preserve the broader 48-family matrix",
    ]:
        assert phrase in text

    assert review["data_family_accounting"]["broad_visibility_matrix_families"] == 48
    assert review["data_family_accounting"]["current_run_inventory_ui_families"] == 29
    assert review["data_family_accounting"]["first_read_product_path_families"] == 8
    assert review["data_family_accounting"]["current_inventory_groups"] == {
        "first_read_product_path": 8,
        "conversation_and_interpretation": 4,
        "memory_receipts_and_sidecars": 4,
        "technical_and_operator_inspection": 8,
        "library_substrate_accounted_for": 5,
    }

    for group in [
        "First-read product path",
        "Conversation and interpretation",
        "Memory, receipts, and sidecars",
        "Technical and operator inspection",
        "Library substrate accounted for",
    ]:
        assert f"| {group} |" in text


def test_content_progression_prd_defines_surface_responsibilities() -> None:
    text = _read(DOC)

    for surface in [
        "Header and run picker",
        "Outcome",
        "Learn",
        "Models",
        "Relations",
        "Map",
        "Receipts",
        "Download MD",
        "Advanced Audit",
        "Operator inspection",
    ]:
        assert f"| {surface} |" in text

    for phrase in [
        "Outcome is the first read",
        "Teacher is the practice layer",
        "models are reusable concepts",
        "relations are model-pair lessons",
        "map is navigation",
        "receipts are accountability",
        "Download MD is private agent memory",
        "Advanced Audit is technical inspection",
    ]:
        assert phrase in text


def test_content_progression_prd_defines_expansion_ladder() -> None:
    text = _read(DOC)

    for depth in [
        "| 0 | First read |",
        "| 1 | Primary surface |",
        "| 2 | Product detail |",
        "| 3 | Receipt |",
        "| 4 | Private export |",
        "| 5 | Technical inspection |",
        "| 6 | Operator inspection |",
        "| 7 | Future design |",
    ]:
        assert depth in text

    for phrase in [
        "This ladder lets us \"show everything\" without placing everything on the same screen.",
        "raw 1:1 transcript when present",
        "private ledgers, provider-private bodies, embeddings/vectors",
        "global graph, semantic-neighbor browsing, V60 affordance pages",
    ]:
        assert phrase in text


def test_content_progression_prd_distinguishes_teacher_models_and_relations() -> None:
    text = _read(DOC)

    for phrase in [
        "Teacher information is case anchored.",
        "What reasoning move can the user practice because of this run?",
        "Model information is concept anchored.",
        "What does this mental model help me notice",
        "Relation information is interaction anchored.",
        "What does this pair of models teach together?",
        "Relation pages should lead with plain-language story",
    ]:
        assert phrase in text


def test_content_progression_prd_records_missingness_and_graph_behavior() -> None:
    text = _read(DOC)

    for phrase in [
        "Missingness is not failure if it is clear and honest.",
        "Outcome still renders from the selected run when a result exists",
        "the UI must not invent a lesson, model page, relation story, or graph",
        "If `revised_answer` is absent",
        "Raw transcript exists",
        "model detail pages show reviewed local neighborhoods",
        "relation pages remain the target for edge meaning",
        "global graph remains future design",
    ]:
        assert phrase in text


def test_content_progression_prd_review_json_records_rules_and_boundaries() -> None:
    review = _json(REVIEW)

    assert review["decision_gate"] == (
        "proceed_to_observatory_content_progression_implementation"
    )
    assert review["implemented"]["content_progression_prd"] is True
    assert review["implemented"]["ui_code_changed"] is False

    for key in [
        "outcome_is_default_first_read",
        "teacher_is_case_anchored_practice_layer",
        "models_are_reusable_concepts",
        "relations_are_model_pair_lessons",
        "map_is_navigation_not_proof",
        "receipts_are_accountability_not_primary_copy",
        "download_md_is_private_agent_export",
        "advanced_audit_is_optional_technical_inspection",
        "operator_inspection_is_not_normal_user_ui",
    ]:
        assert review["product_rules"][key] is True

    for key in [
        "runs_lolla",
        "invokes_lolla_skill",
        "calls_provider_or_model",
        "creates_new_run",
        "generates_sidecars",
        "wires_skill_runtime_behavior",
        "mutates_archives",
        "touches_skill_md",
        "touches_scripts_skill",
        "touches_archive_run",
        "touches_compiled_spa_bundle",
    ]:
        assert review["boundary"][key] is False

    for key in [
        "product_proof",
        "human_validated",
        "answer_correctness",
        "advice_correctness",
        "action_authorized",
        "graph_edges_are_proof",
        "embedding_similarity_is_validated_relation_semantics",
    ]:
        assert review["non_claims"][key] is False


def test_content_progression_prd_artifacts_are_clean() -> None:
    missing = []
    for path in [DOC, README]:
        text = _read(path)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    combined = _read(DOC) + _read(REVIEW)

    assert missing == []
    assert "/" + "Users/" not in combined
    assert "Desktop/" + "Apps" not in combined
    assert "product_proof\": true" not in combined
    assert "human_validated\": true" not in combined
    assert "answer_correctness\": true" not in combined
    assert "advice_correctness\": true" not in combined
