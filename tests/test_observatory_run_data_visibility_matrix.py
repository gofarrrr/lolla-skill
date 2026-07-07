from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-run-data-visibility-matrix-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-run-data-visibility-matrix-v0/review.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    return json.loads(_read(path))


def test_visibility_matrix_files_exist_and_are_indexed() -> None:
    assert DOC.exists()
    assert REVIEW.exists()

    readme = _read(README)
    assert "Observatory Run Data Visibility Matrix" in readme
    assert "observatory-run-data-visibility-matrix-v0.md" in readme


def test_visibility_matrix_has_user_value_and_flow_columns() -> None:
    text = _read(DOC)

    for heading in [
        "Data we gather",
        "How it comes in",
        "What it helps us see",
        "User value",
        "How it should go out",
        "What the user can do",
        "Disclosure guardrail",
    ]:
        assert heading in text

    assert "how the data comes into the system" in text
    assert "why a user might care" in text
    assert "where the user discovers that this data exists" in text
    assert "what the user can do with it" in text
    assert "what needs a summary, expansion, technical route" in text


def test_visibility_matrix_has_discovery_map_for_user_surfaces() -> None:
    text = _read(DOC)

    assert "Discovery Map" in text
    assert "we gather it, so where does the user find it" in text

    for place in [
        "Run header / picker",
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
        assert f"| {place} |" in text

    assert "Run inventory receipt" in text
    assert "raw-transcript/export status" in text


def test_visibility_matrix_uses_show_everything_in_layers_principle() -> None:
    text = _read(DOC)

    for phrase in [
        "Show Everything, But In Layers",
        "If we gather it, the user should be able to account for it.",
        "visible summary",
        "expandable detail",
        "technical inspection route",
        "explicit file export",
        "receipt that says the artifact exists",
        "At what depth, in what form, with what warning, and for what user action?",
    ]:
        assert phrase in text


def test_visibility_matrix_covers_current_run_product_flow() -> None:
    text = _read(DOC)

    for phrase in [
        "selected run",
        "what changed",
        "what reasoning move can I learn",
        "what models and relations explain it",
        "where can I navigate",
        "what exists, what is missing, and what is not claimed",
        "optional technical inspection or agent export",
    ]:
        assert phrase in text

    for surface in [
        "Outcome",
        "Learn",
        "Models",
        "Relations",
        "Map",
        "Receipts",
        "Advanced Audit",
        "Download MD",
    ]:
        assert surface in text


def test_visibility_matrix_covers_required_artifact_families() -> None:
    text = _read(DOC)

    for source in [
        "result.json",
        "agent_result.json",
        "extraction.json",
        "reasoning_trace.json",
        "evaluation.json",
        "memo.md",
        "user_receipt.md",
        "usage summary",
        "run_events.json",
        "Teacher learning packet",
        "Decision Work sidecars",
        "data/model_sources/*.md",
        "data/model_sources/manifest.json",
        "data/curation/*.json",
        "data/curation/intervention_semantics/*.json",
        "data/curation/relation_semantics/*.json",
        "data/relationship_graph.json",
        "data/knowledge_graph.json",
        "data/curated/*.json",
        "data/family_semantics/*.json",
        "data/compiled/model_affordances/affordances_v60.json",
        "data/model_affordances/**/*.json",
        "data/schemas/*.json",
        "data/treatment_audits/*.json",
        "data/evaluations/gate4_edge_probes/*.json",
        "graph survival reports",
        "data/embeddings.db",
        "conversation.txt",
    ]:
        assert source in text


def test_visibility_matrix_classifies_show_expand_export_and_inspection_layers() -> None:
    text = _read(DOC)

    for layer in [
        "show_by_default",
        "primary_surface",
        "expandable_detail",
        "technical_inspection",
        "agent_export",
        "future_design",
        "operator_inspection",
        "explicit_private_export",
    ]:
        assert layer in text

    expected_rows = [
        ("Outcome summary", "primary_surface"),
        ("Canonical model Markdown", "expandable_detail"),
        ("Model-detail local neighborhood", "expandable_detail"),
        ("Relationship graph substrate", "expandable_detail"),
        ("Usage telemetry", "technical_inspection"),
        ("Treatment audits", "technical_inspection"),
        ("Conversation memory Markdown", "agent_export"),
        ("Knowledge graph", "future_design"),
        ("Non-V60 model affordance files", "operator_inspection"),
        ("Raw embeddings/vectors", "operator_inspection"),
        ("Raw 1:1 conversation transcript", "explicit_private_export"),
    ]
    for row_name, layer in expected_rows:
        row = next(line for line in text.splitlines() if line.startswith(f"| {row_name} |"))
        assert layer in row


def test_visibility_matrix_avoids_dual_canonical_output_layers() -> None:
    text = _read(DOC)

    matrix_started = False
    rows = []
    for line in text.splitlines():
        if line == "## Run Data Visibility Matrix":
            matrix_started = True
            continue
        if matrix_started and line.startswith("## "):
            break
        if matrix_started and line.startswith("| ") and not line.startswith("| ---"):
            rows.append(line)

    data_rows = [row for row in rows if not row.startswith("| Data we gather |")]
    assert data_rows

    for row in data_rows:
        cells = row.split("|")
        how_it_should_go_out = cells[5]
        assert "` or `" not in how_it_should_go_out, row
        assert " or `technical_inspection`" not in how_it_should_go_out, row
        assert " or `operator_inspection`" not in how_it_should_go_out, row


def test_visibility_matrix_records_product_boundaries_and_open_questions() -> None:
    text = _read(DOC)

    for phrase in [
        "The first screen should not try to be the archive",
        "Graph is a map, not proof.",
        "Agent memory is an explicit export.",
        "Should model pages lead with selected-run context or durable canonical model meaning?",
        "Should the next graph slice be a model-detail local neighborhood",
        "Should raw transcript remain only in `Download MD`",
        "agent-useful but human-overwhelming",
        "run inventory receipt",
        "Do not collapse `show_by_default` into `primary_surface` yet",
        "Do not collapse `operator_inspection` into `technical_inspection` yet",
    ]:
        assert phrase in text

    for phrase in [
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not touch `SKILL.md`",
        "does not touch `scripts/skill/*`",
        "does not touch `scripts/archive_run.py`",
        "does not claim product proof",
        "does not claim human validation",
    ]:
        assert phrase in text


def test_visibility_matrix_review_json_is_waiting_for_user_review() -> None:
    review = _json(REVIEW)

    assert review["review_id"] == "observatory-run-data-visibility-matrix-v0"
    assert review["status"] == "ready_for_user_review"
    assert review["decision_gate"] == "await_user_review_of_run_data_visibility_matrix"
    assert review["implemented"]["reviewable_visibility_matrix_doc"] is True
    assert review["implemented"]["progressive_disclosure_principle_added"] is True
    assert review["implemented"]["disclosure_guardrails_added"] is True
    assert review["implemented"]["red_team_review_incorporated"] is True
    assert review["implemented"]["discovery_map_added"] is True
    assert review["implemented"]["missing_artifact_families_added"] is True
    assert review["implemented"]["dual_canonical_layers_removed"] is True
    assert review["implemented"]["run_inventory_receipt_next_slice_identified"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False
    assert "Disclosure guardrail" in review["matrix_columns"]
    assert "Discovery Map" in review["supporting_sections"]
    assert "operator_inspection" in review["visibility_layers"]
    assert "explicit_private_export" in review["visibility_layers"]
    assert "progressively inspectable" in review["strongest_useful_signal"]
    assert review["recommended_next_pr"] == "Add Observatory run inventory receipt panel"

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
    ]:
        assert review["boundary"][key] is False

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


def test_visibility_matrix_links_and_private_markers_are_clean() -> None:
    missing = []
    for path in [DOC, README]:
        text = _read(path)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    combined = "\n".join(_read(path) for path in [DOC, REVIEW])

    assert missing == []
    assert "/" + "Users/" not in combined
    assert "Desktop/" + "Apps" not in combined
    assert "product_proof\": true" not in combined
    assert "human_validated\": true" not in combined
    assert "answer_correctness\": true" not in combined
    assert "advice_correctness\": true" not in combined
    assert "runtime_integration_authorized\": true" not in combined
    assert "action_authorized\": true" not in combined
