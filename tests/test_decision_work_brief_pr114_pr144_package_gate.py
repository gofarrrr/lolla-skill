from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-pr114-pr144-package-manifest-v0.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-pr114-pr144-packaging-gate-v0.md"
)
EXPECTED_SCHEMA_VERSION = "lolla.decision_work_brief_pr114_pr144_package_manifest.v0"
EXPECTED_PR_NUMBERS = set(range(114, 145))
BOUNDARY_FALSE_FIELDS = {
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "archive_mutated",
    "runtime_invoked",
    "skill_invoked",
    "runtime_integration_implemented",
    "new_lolla_run_created",
    "new_interpretation_read_created",
    "raw_private_content_included",
    "provider_text_included",
    "local_absolute_paths_included",
    "automatic_labels_created",
}
FORBIDDEN_INCLUDED_PREFIXES = (
    "plans/",
    "reviews/synthetic/",
    "scripts/skill/",
)
FORBIDDEN_INCLUDED_FILES = {
    "SKILL.md",
    "docs/lolla-current-state-code-grounded-report-2026-06-27.md",
    "docs/lolla-decision-labs-prd-v0.md",
    "docs/lolla-human-exception-sense-design-note.md",
    "docs/lolla-pitch-and-invitation-kopia.md",
}
REQUIRED_NON_CLAIMS = {
    "package_gate_is_not_product_proof",
    "package_gate_is_not_human_validation",
    "package_gate_is_not_runtime_integration",
    "package_gate_is_not_answer_quality_scoring",
    "package_gate_is_not_agent_action_authorization",
    "clean_artifacts_do_not_imply_good_advice",
    "one_offline_package_is_not_general_evidence",
    "future_human_review_required",
}
PRIVACY_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _included_files() -> list[str]:
    manifest = _manifest()
    files: list[str] = []
    for group in manifest["included_files"].values():
        files.extend(group)
    return files


def _package_paths() -> list[Path]:
    manifest = _manifest()
    paths = [DOC_PATH, MANIFEST_PATH]
    for relpath in _included_files() + manifest["packaging_gate_files"]:
        paths.append(REPO_ROOT / relpath)
    return paths


def _lint_paths() -> list[Path]:
    manifest = _manifest()
    paths = [DOC_PATH, MANIFEST_PATH]
    lint_groups = (
        "docs",
        "schemas_and_contracts",
        "review_artifacts",
        "rendered_and_enriched_examples",
    )
    for group_name in lint_groups:
        paths.extend(REPO_ROOT / relpath for relpath in manifest["included_files"][group_name])
    return paths


def _json_artifact_paths() -> list[Path]:
    manifest = _manifest()
    json_paths = (
        manifest["included_files"]["schemas_and_contracts"]
        + manifest["included_files"]["review_artifacts"]
        + [str(MANIFEST_PATH.relative_to(REPO_ROOT))]
    )
    return [REPO_ROOT / path for path in json_paths]


def _collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(_collect_strings(item))
        return strings
    if isinstance(value, dict):
        strings = []
        for item in value.values():
            strings.extend(_collect_strings(item))
        return strings
    return []


def _collect_repo_refs(value: Any) -> set[str]:
    refs = set()
    for candidate in _collect_strings(value):
        if candidate.startswith(("docs/", "engine/", "reviews/", "scripts/", "tests/")):
            path_part = candidate.split("#", 1)[0]
            if " " not in path_part and "*" not in path_part:
                refs.add(path_part)
    return refs


def test_package_manifest_json_parses_and_has_expected_version() -> None:
    manifest = _manifest()

    assert manifest["schema_version"] == EXPECTED_SCHEMA_VERSION
    assert manifest["phase"] == "decision_work_brief_offline_pr114_pr144"
    assert manifest["status"] == "packaging_gate"


def test_boundary_metadata_is_conservative() -> None:
    boundary = _manifest()["boundary"]

    for field in BOUNDARY_FALSE_FIELDS:
        assert boundary[field] is False, field
    assert boundary["model_calls"] == 0


def test_manifest_includes_pr114_through_pr144_exactly() -> None:
    prs = _manifest()["included_prs"]

    assert {item["pr_number"] for item in prs} == EXPECTED_PR_NUMBERS
    assert len(prs) == len(EXPECTED_PR_NUMBERS)
    for item in prs:
        assert item["title"]
        assert item["kind"]
        assert item["primary_files"]
        assert item["what_it_added"]
        assert item["what_it_did_not_do"]


def test_manifest_included_files_exist_on_disk() -> None:
    for path in _package_paths():
        assert path.exists(), str(path.relative_to(REPO_ROOT))


def test_manifest_excludes_unrelated_files_and_runtime_surface() -> None:
    included = set(_included_files() + _manifest()["packaging_gate_files"])

    for forbidden in FORBIDDEN_INCLUDED_FILES:
        assert forbidden not in included
    for relpath in included:
        assert not relpath.startswith(FORBIDDEN_INCLUDED_PREFIXES), relpath
        assert not relpath.startswith("archive/"), relpath
        assert "__pycache__" not in relpath
    assert "scripts/skill/*" in _manifest()["explicit_staging_list"]["do_not_stage"]
    assert "SKILL.md" in _manifest()["explicit_staging_list"]["do_not_stage"]


def test_manifest_records_key_package_signal_and_risk() -> None:
    summary = _manifest()["phase_summary"]

    assert summary["strongest_useful_signal"]["evidence_refs"]
    assert "offline chain" in summary["strongest_useful_signal"]["summary"]
    assert summary["strongest_unresolved_risk"]["risk_refs"]
    assert "source depth" in summary["strongest_unresolved_risk"]["summary"]


def test_manifest_records_boundary_and_staging_guidance() -> None:
    manifest = _manifest()
    boundary = manifest["boundary_summary"]
    staging = manifest["explicit_staging_list"]

    assert boundary["offline_downstream_only"] is True
    assert boundary["runtime_integration_not_implemented"] is True
    assert boundary["human_validation_absent"] is True
    assert boundary["product_proof_absent"] is True
    assert boundary["agent_action_not_authorized"] is True
    assert "packaging_gate_files" in staging["stage_package_file_groups"]
    assert "raw/private transcripts, memos, revised answers, ledgers, provider text, or secrets" in staging["do_not_stage"]


def test_suggested_pr_description_remains_lower_claim() -> None:
    description = _manifest()["suggested_pr_description"]

    assert "No runtime integration." in description["boundaries"]
    assert "No model calls." in description["boundaries"]
    assert "No product proof." in description["boundaries"]
    assert "No human validation." in description["boundaries"]
    assert "No answer-quality scoring." in description["boundaries"]
    assert "No agent action authorization." in description["boundaries"]
    assert "source depth" in description["strongest_risk"].lower()


def test_non_claims_are_complete() -> None:
    assert set(_manifest()["non_claims"]) >= REQUIRED_NON_CLAIMS


def test_all_json_artifacts_parse() -> None:
    for path in _json_artifact_paths():
        json.loads(path.read_text(encoding="utf-8"))


def test_repo_refs_resolve_where_manifest_names_files() -> None:
    refs = _collect_repo_refs(_manifest())

    assert refs
    for ref in refs:
        if ref in {"scripts/skill/"}:
            continue
        assert (REPO_ROOT / ref).exists(), ref


def test_package_files_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(_lint_paths())

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_package_files_do_not_include_private_markers() -> None:
    for path in _package_paths() + [Path(__file__)]:
        text = path.read_text(encoding="utf-8")
        for marker in PRIVACY_MARKERS:
            assert marker not in text
