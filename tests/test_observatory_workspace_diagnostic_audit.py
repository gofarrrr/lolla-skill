from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-workspace-diagnostic-audit-v0.md"
SUMMARY = REPO_ROOT / "docs/product/observatory-workspace-diagnostic-audit-v0.json"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-diagnostic-audit-v0/review.json"
)

SURFACES = [
    "Root / Outcome",
    "Learn",
    "Models",
    "Relations",
    "Map",
    "Receipts",
    "Review Guide",
    "Model Page",
    "Relation Page",
    "Technical Audit Routes",
]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_diagnostic_audit_is_indexed_and_records_browser_scope() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    summary = _load_json(SUMMARY)

    assert "Observatory Workspace Diagnostic Audit" in readme
    assert "observatory-workspace-diagnostic-audit-v0.md" in readme
    assert "observatory-workspace-diagnostic-audit-v0.json" in readme
    assert summary["browser_grounded"] is True

    for route in [
        "/",
        "/workspace?case_id=launch-public-enterprise-beta#outcome",
        "/workspace?case_id=launch-public-enterprise-beta#learn",
        "/workspace?case_id=launch-public-enterprise-beta#models",
        "/workspace?case_id=launch-public-enterprise-beta#relations",
        "/workspace?case_id=launch-public-enterprise-beta#map",
        "/workspace?case_id=launch-public-enterprise-beta#receipts",
        "/review/observatory-workspace?case_id=launch-public-enterprise-beta",
        "/models/authority-bias?case_id=launch-public-enterprise-beta",
        "/relations/authority-bias__first-principles-thinking__antagonist?case_id=launch-public-enterprise-beta",
        "/audit/extraction",
        "/usage",
        "/audit",
    ]:
        assert route in doc
        assert route in summary["routes_checked"]

    assert summary["controls_checked"] == [
        "map_relation_filter",
        "map_model_search",
        "map_reset",
    ]


def test_audit_defines_progression_and_information_layers() -> None:
    doc = DOC.read_text(encoding="utf-8")
    summary = _load_json(SUMMARY)

    assert summary["decision_gate"] == (
        "needs_information_hierarchy_revision_before_expansion"
    )
    assert summary["current_progression"] == [
        "Outcome",
        "Learn",
        "Models",
        "Relations",
        "Map",
        "Receipts",
    ]

    layers = summary["information_layers"]
    assert "reasoning_move" in layers["first_class_product_information"]
    assert "relation_story" in layers["first_class_product_information"]
    assert "model_detail_pages" in layers["supporting_knowledge_information"]
    assert "map_neighborhood" in layers["supporting_knowledge_information"]
    assert "advanced_audit_index" in layers["inspection_information"]
    assert "telemetry_style_evidence" in layers["inspection_information"]

    for phrase in [
        "First-class product information",
        "Supporting knowledge information",
        "Inspection information",
        "This is the product.",
        "This layer should answer: what can I open next, and why?",
        "This layer should answer: what exists, what is missing",
    ]:
        assert phrase in doc


def test_surface_audit_records_every_current_surface_and_role() -> None:
    summary = _load_json(SUMMARY)

    surface_names = [item["surface"] for item in summary["surface_audit"]]
    assert surface_names == SURFACES

    by_surface = {item["surface"]: item for item in summary["surface_audit"]}
    assert by_surface["Root / Outcome"]["classification"] == (
        "first_class_product_information"
    )
    assert "missing_revised_answer_state" in by_surface["Root / Outcome"]["data_shown"]
    assert by_surface["Learn"]["desired_role"] == "primary_teaching_value"
    assert by_surface["Models"]["main_risk"] == (
        "primary_supporting_optional_model_roles_are_not_visually_distinct"
    )
    assert by_surface["Map"]["desired_role"] == "wayfinding_and_data_selection"
    assert "non_proof_copy" in by_surface["Map"]["data_shown"]
    assert by_surface["Receipts"]["classification"] == "inspection_information"
    assert by_surface["Technical Audit Routes"]["desired_role"] == (
        "optional_builder_inspection"
    )


def test_audit_doc_states_critical_findings_and_next_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = _load_json(REVIEW)

    for phrase in [
        "The strongest unresolved UX issue is not missing data. It is hierarchy.",
        "Make Outcome resilient when the answer artifact is missing.",
        "Label model roles.",
        "Add a visible Library / Run-context distinction on model pages.",
        "Keep technical audit behind Receipts.",
        "Preserve the map as navigation.",
        "selected run -> reasoning move -> model stack -> relation story -> graph",
        "needs_information_hierarchy_revision_before_expansion",
    ]:
        assert phrase in doc

    assert review["decision_gate"] == (
        "needs_information_hierarchy_revision_before_expansion"
    )
    assert review["implemented"]["diagnostic_audit_doc"] is True
    assert review["implemented"]["machine_readable_audit_summary"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False
    assert review["surfaces_audited"] == SURFACES
    assert review["information_layers"] == [
        "first_class_product_information",
        "supporting_knowledge_information",
        "inspection_information",
    ]


def test_audit_boundary_and_non_claims_remain_closed() -> None:
    summary = _load_json(SUMMARY)
    review = _load_json(REVIEW)

    for payload in [summary, review]:
        assert payload["boundary"]["runs_lolla"] is False
        assert payload["boundary"]["invokes_lolla_skill"] is False
        assert payload["boundary"]["calls_provider_or_model"] is False
        assert payload["boundary"]["creates_new_run"] is False
        assert payload["boundary"]["wires_skill_runtime_behavior"] is False
        assert payload["boundary"]["compiled_spa_bundle_changed"] is False
        assert payload["boundary"]["touches_skill_md"] is False
        assert payload["boundary"]["touches_scripts_skill"] is False
        assert payload["boundary"]["touches_archive_run"] is False
        assert payload["non_claims"]["product_proof"] is False
        assert payload["non_claims"]["human_validated"] is False
        assert payload["non_claims"]["answer_correctness"] is False
        assert payload["non_claims"]["advice_correctness"] is False
        assert payload["non_claims"]["action_authorized"] is False
        assert payload["non_claims"]["graph_edges_are_proof"] is False


def test_audit_links_and_privacy_markers_are_clean() -> None:
    missing = []
    for path in [DOC, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    text = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC, SUMMARY, REVIEW]
    )

    assert missing == []
    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
