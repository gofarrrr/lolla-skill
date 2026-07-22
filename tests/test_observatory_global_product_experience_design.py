import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-global-product-experience-and-data-flow-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-global-product-experience-and-data-flow-v0/review.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_global_design_doc_exists_and_is_indexed() -> None:
    assert DOC.exists()
    assert REVIEW.exists()

    readme = _read(README)
    assert "Observatory Global Product Experience And Data Flow" in readme
    assert "observatory-global-product-experience-and-data-flow-v0.md" in readme


def test_global_design_declares_one_observatory_workspace() -> None:
    text = _read(DOC)

    for phrase in [
        "Observatory is the single product shell.",
        "Teacher is not a second application.",
        "one selected run",
        "Outcome | Learn | Models | Relations | Map | Receipts",
        "Advanced Audit",
        "case is the anchor",
        "reasoning move is the subject",
        "model relationship is the lesson",
        "practice rep is the product value",
    ]:
        assert phrase in text


def test_global_design_covers_required_perspectives() -> None:
    text = _read(DOC)

    for heading in [
        "### Normal User",
        "### Learner",
        "### Library Browser",
        "### Reviewer Or Maintainer",
        "### System And Custody",
        "### Implementation Owner",
    ]:
        assert heading in text


def test_global_design_assigns_surface_ownership() -> None:
    text = _read(DOC)

    required_rows = [
        "| Outcome | What happened in this run? |",
        "| Learn | What reasoning move can I learn? |",
        "| Models | What does this mental model mean? |",
        "| Relations | What does this model pair teach? |",
        "| Map | How can I navigate the neighborhood? |",
        "| Receipts | What can I trust, inspect, or treat as missing? |",
        "| Advanced Audit | What happened inside the system? |",
    ]
    for row in required_rows:
        assert row in text

    for row in [
        "| Revised answer | Outcome | Receipts, memo, Advanced Audit | Teacher lesson body |",
        "| Teacher reasoning move | Learn | Outcome summary, Models backlinks, Relations backlinks | telemetry panel copy |",
        "| Canonical model explanation | Models | Outcome, Learn, Relations, Map | model activation evidence |",
        "| Relation explanation | Relations | Learn, Map | graph edge label only |",
        "| Conversation Understanding status | Receipts | Outcome header, Advanced Audit | Teacher lesson body |",
    ]:
        assert row in text


def test_global_design_classifies_data_priority() -> None:
    text = _read(DOC)

    for phrase in [
        "| First-class product data |",
        "| Second-class support data |",
        "| Receipts and review data |",
        "| Internal-only data |",
        "| Future or suggestion-only data |",
        "raw conversation",
        "raw embeddings",
        "semantic neighbors",
        "AI-discovered relations",
    ]:
        assert phrase in text


def test_global_design_defines_safe_data_flow_and_view_models() -> None:
    text = _read(DOC)

    for phrase in [
        "raw run artifacts",
        "read-only adapters",
        "product-safe view models",
        "Observatory UI surfaces",
        "`selected_run_summary`",
        "`outcome_summary`",
        "`learning_packet`",
        "`model_page`",
        "`relation_page`",
        "`graph_neighborhood`",
        "`receipt_summary`",
        "`advanced_audit_index`",
        "Primary UI surfaces consume product-safe view models.",
        "Advanced Audit can consume raw telemetry.",
    ]:
        assert phrase in text


def test_global_design_defines_search_switching_and_user_flows() -> None:
    text = _read(DOC)

    for phrase in [
        "Run picker",
        "Tab switcher",
        "Model search",
        "Relation search",
        "Backlinks",
        "Map filters",
        "Receipts links",
        "### Flow 1: Open A Run",
        "### Flow 2: Learn From The Run",
        "### Flow 3: Click A Mental Model",
        "### Flow 4: Click A Relation",
        "### Flow 5: Explore The Map",
        "### Flow 6: Inspect Receipts",
    ]:
        assert phrase in text


def test_global_design_defines_source_ownership_decision() -> None:
    text = " ".join(_read(DOC).split())

    for phrase in [
        "The current repository has a portable Python Observatory server and a compiled frontend bundle.",
        "The source of the compiled bundle is not present in this repo.",
        "Source Ownership Decision Resolved",
        "`observatory/serve_result.py` owns the active portable skill-presentation surface",
        "no external frontend workspace is an active source or build dependency",
        "the current product direction is portable Python/server-rendered Observatory",
        "not port the global shell to Svelte",
        "proceed_to_observatory_portable_server_view_model_contracts",
    ]:
        assert phrase in text


def test_global_design_has_incremental_sequence_and_stop_conditions() -> None:
    text = _read(DOC)

    planned = re.findall(r"^### PR-G\d+", text, flags=re.MULTILINE)
    assert planned == [
        "### PR-G1",
        "### PR-G2",
        "### PR-G3",
        "### PR-G4",
        "### PR-G5",
        "### PR-G6",
        "### PR-G7",
        "### PR-G8",
    ]

    for phrase in [
        "Stop before UI changes.",
        "Stop before UI rebuild.",
        "Stop before rendering.",
        "Stop before legacy bundle edits.",
        "Stop before full corpus graph.",
        "running Lolla",
        "invoking the Lolla skill",
        "provider/model API calls",
        "wiring or changing runtime behavior",
        "claiming product proof",
        "claiming human validation",
        "claiming answer or advice correctness",
        "treating graph edges as proof",
    ]:
        assert phrase in text


def test_review_json_records_gate_surfaces_data_flow_and_non_claims() -> None:
    data = json.loads(_read(REVIEW))

    assert (
        data["schema"]
        == "lolla.observatory_global_product_experience_and_data_flow_review.v0"
    )
    assert data["artifact"] == (
        "docs/product/observatory-global-product-experience-and-data-flow-v0.md"
    )
    assert (
        data["decision_gate"]
        == "proceed_to_observatory_portable_server_view_model_contracts"
    )
    assert data["product_decision"]["one_shell"] == "Observatory"
    assert data["product_decision"]["primary_workspace"] == "selected_run"
    assert data["product_decision"]["teacher_position"] == "Learn"
    assert (
        data["product_decision"]["current_rendering_direction"]
        == "portable_python_server_rendered_html"
    )
    assert (
        data["product_decision"]["legacy_svelte_source_is_future_owner_by_default"]
        is False
    )
    assert data["product_decision"]["standalone_teacher_app"] is False
    assert (
        data["product_decision"]["compiled_bundle_manual_editing_as_strategy"]
        is False
    )
    assert data["primary_surfaces"] == [
        "Outcome",
        "Learn",
        "Models",
        "Relations",
        "Map",
        "Receipts",
    ]
    assert data["single_home_rules"]["canonical_model_explanation"] == "Models"
    assert data["single_home_rules"]["relation_explanation"] == "Relations"
    assert data["single_home_rules"]["conversation_understanding_status"] == "Receipts"
    assert data["data_flow"]["raw_run_artifacts_to_read_only_adapters"] is True
    assert data["data_flow"]["product_safe_view_models_required"] is True
    assert data["data_flow"]["primary_ui_consumes_product_view_models"] is True
    assert data["data_flow"]["advanced_audit_may_consume_raw_telemetry"] is True

    boundary = data["boundary"]
    assert boundary["runs_lolla"] is False
    assert boundary["invokes_lolla_skill"] is False
    assert boundary["provider_or_model_calls"] is False
    assert boundary["runtime_behavior_changed"] is False
    assert boundary["compiled_bundle_manually_edited"] is False

    non_claims = data["non_claims"]
    assert non_claims["product_proof"] is False
    assert non_claims["human_validated"] is False
    assert non_claims["answer_correctness"] is False
    assert non_claims["advice_correctness"] is False
    assert non_claims["action_authorized"] is False
    assert non_claims["graph_edges_are_proof"] is False
    assert (
        non_claims["embedding_similarity_is_validated_relation_semantics"]
        is False
    )


def test_markdown_links_resolve_for_global_design_doc() -> None:
    text = _read(DOC)
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    for link in links:
        if "://" in link or link.startswith("#"):
            continue
        assert (DOC.parent / link).exists(), link


def test_global_design_artifacts_have_no_local_paths_or_authority_claims() -> None:
    text = _read(DOC) + _read(REVIEW)

    for forbidden in [
        "/" + "Users/",
        "Desktop/" + "Apps",
        "product_proof\": true",
        "human_validated\": true",
        "answer_correctness\": true",
        "advice_correctness\": true",
        "action_authorized\": true",
        "runtime_behavior_changed\": true",
        "archives_mutated\": true",
        "compiled_bundle_manually_edited\": true",
        "raw_private_conversation_exposed_as_product_copy\": true",
    ]:
        assert forbidden not in text
