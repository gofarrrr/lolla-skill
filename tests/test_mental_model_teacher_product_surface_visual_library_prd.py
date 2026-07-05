import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCT_INDEX = REPO_ROOT / "docs/product/README.md"
PRD = REPO_ROOT / "docs/product/mental-model-teacher-product-surface-and-visual-library-prd-v0.md"
CURRENT_SUBSTRATE = REPO_ROOT / "docs/product/mental-model-teacher-current-substrate-inventory-v0.md"
REFERENCE_PATTERNS = REPO_ROOT / "docs/product/mental-model-teacher-product-surface-reference-patterns-v0.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-product-surface-and-visual-library-prd-v0/review.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_product_planning_files_exist() -> None:
    assert PRODUCT_INDEX.exists()
    assert PRD.exists()
    assert CURRENT_SUBSTRATE.exists()
    assert REFERENCE_PATTERNS.exists()
    assert REVIEW.exists()


def test_prd_keeps_teacher_separate_from_existing_lanes() -> None:
    text = _read(PRD)

    for phrase in [
        "Observatory",
        "Decision Work",
        "Product Delta",
        "a second advice engine",
        "a replacement for the Lolla skill",
        "The product lane should sit next to the existing systems",
    ]:
        assert phrase in text


def test_prd_uses_existing_source_assets_instead_of_new_graph_magic() -> None:
    text = _read(PRD)

    for phrase in [
        "data/model_sources/*.md",
        "data/model_sources/manifest.json",
        "data/curation/*.json",
        "data/curation/intervention_semantics/*.json",
        "data/curation/relation_semantics/*.json",
        "data/knowledge_graph.json",
        "data/relationship_graph.json",
        "data/embeddings.db",
        "data/curated/*.json",
        "data/family_semantics/*.json",
        "data/compiled/model_affordances/affordances_v60.json",
        "canonical Markdown is source of truth",
        "visual pages and graphs are product renderings",
    ]:
        assert phrase in text


def test_current_substrate_inventory_covers_existing_lolla_lanes() -> None:
    text = _read(CURRENT_SUBSTRATE)

    for phrase in [
        "Canonical Markdown",
        "Activation curation",
        "Intervention semantics",
        "Relation semantics",
        "Compiled relationship graph",
        "Knowledge graph",
        "Embeddings DB",
        "V60 affordances",
        "Graph survival reports",
        "Treatment audits",
        "Runtime Graph Lane",
        "Model-Affordance Lane",
        "Graph Survival And Eval Lane",
        "Teacher Lane",
    ]:
        assert phrase in text


def test_current_substrate_inventory_has_exposure_policy() -> None:
    text = _read(CURRENT_SUBSTRATE)

    for phrase in [
        "Product Exposure Policy",
        "Do not expose",
        "embedding ranks as product explanation",
        "raw ranking internals as user-facing truth",
        "evaluation data as product marketing",
        "The relation page is the lesson.",
    ]:
        assert phrase in text


def test_prd_defines_user_facing_surfaces() -> None:
    text = _read(PRD)

    for phrase in [
        "Mental Model Library Home",
        "Mental Model Page",
        "Relation Page",
        "Teacher Lesson Page",
        "Run Neighborhood Graph",
        "Global Model Graph",
    ]:
        assert phrase in text


def test_prd_preserves_probabilistic_and_guardrail_philosophy() -> None:
    text = _read(PRD)

    for phrase in [
        "We should not try to make messy conversation deterministic.",
        "interpret, synthesize, explain, and relate ideas",
        "deterministic rails",
        "The graph should not say \"this is true.\"",
    ]:
        assert phrase in text


def test_prd_has_implementation_pr_sequence_for_junior_coder() -> None:
    text = _read(PRD)
    planned = re.findall(r"^### PR-P\d+", text, flags=re.MULTILINE)

    assert len(planned) == 11
    assert "PR-P2 Current Substrate Inventory And Exposure Contract" in text
    assert "Optional PR-P12 Full Corpus Graph Plan" in text
    assert "Optional PR-P13 Full Corpus Library Pilot" in text
    assert "Stop before:" in text
    assert "Junior Coder Handoff" in text


def test_prd_preserves_non_claims() -> None:
    text = _read(PRD)

    for phrase in [
        "product proof",
        "human validation",
        "answer correctness",
        "advice correctness",
        "customer readiness",
        "runtime integration",
        "resolver approval",
        "action authorization",
        "that a graph proves a reasoning move",
    ]:
        assert phrase in text


def test_reference_patterns_cover_user_requested_inspiration_set() -> None:
    text = _read(REFERENCE_PATTERNS)

    for project in [
        "Logseq",
        "SiYuan",
        "Foam",
        "Reor",
        "TriliumNext",
        "Dendron",
        "AppFlowy",
        "Anytype",
        "Notesnook",
        "Pubsidian",
        "Flowershow",
        "Neurite",
        "knowledge_graph",
        "Graphify",
        "Quartz",
        "Obsidian Digital Garden",
        "Cytoscape.js",
        "Sigma.js",
    ]:
        assert project in text


def test_reference_patterns_preserve_design_lessons_not_dependencies() -> None:
    text = _read(REFERENCE_PATTERNS)

    for phrase in [
        "The goal is not to clone any of these projects.",
        "Focused neighborhood before full corpus",
        "Relations need pages, not only edges.",
        "AI-discovered links should be suggestions until reviewed.",
        "Full-corpus publishing waits until the subset product works.",
    ]:
        assert phrase in text


def test_review_json_matches_prd_boundary() -> None:
    data = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert data["schema"] == "lolla.mental_model_teacher_product_surface_visual_library_prd_review.v0"
    assert data["decision_gate"] == "proceed_to_current_substrate_inventory_exposure_contract"
    assert data["recommended_next_pr"] == "Mental Model Teacher Current Substrate Inventory And Exposure Contract v0"
    assert "Decision Work" in data["product_lane"]["separate_from"]
    assert "data/knowledge_graph.json" in data["source_assets"]
    assert "data/relationship_graph.json" in data["source_assets"]
    assert "data/compiled/model_affordances/affordances_v60.json" in data["source_assets"]
    assert len(data["planned_prs"]) >= 11

    non_claims = data["non_claims"]
    assert non_claims["product_proof"] is False
    assert non_claims["human_validated"] is False
    assert non_claims["runtime_integration_authorized"] is False
    assert non_claims["graph_proves_reasoning_move"] is False


def test_new_docs_do_not_include_local_absolute_paths() -> None:
    forbidden_user_path = "/" + "Users/"
    forbidden_apps_path = "Desktop/" + "Apps"
    for path in [PRODUCT_INDEX, PRD, CURRENT_SUBSTRATE, REFERENCE_PATTERNS, REVIEW]:
        text = _read(path)
        assert forbidden_user_path not in text
        assert forbidden_apps_path not in text
