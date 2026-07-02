from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_brief_runtime_attachment import (
    DECISION_WORK_RUNTIME_ATTACHMENT_FLAG,
    decision_work_runtime_attachment_enabled,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-attached-v1-package-manifest-v0.json"
)
PACKAGE_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-attached-v1-package-gate-v0.md"
)
REVIEW_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-attachment-review-v0.md"
)
REVIEW_JSON_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-runtime-attachment-review-v0/review.json"
)
EXPECTED_MANIFEST_SCHEMA = (
    "lolla.decision_work_brief_runtime_attached_v1_package_manifest.v0"
)
EXPECTED_REVIEW_SCHEMA = "lolla.decision_work_brief_runtime_attachment_review.v0"
FORBIDDEN_PATH_PREFIXES = (
    "SKILL.md",
    "scripts/skill/",
    "plans/",
    "reviews/synthetic/",
    "archive/",
    "/",
)
REQUIRED_FALSE_REVIEW_FIELDS = {
    "human_validated",
    "human_review_completed",
    "product_proof",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
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


def _read_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _read_review() -> dict[str, Any]:
    return json.loads(REVIEW_JSON_PATH.read_text(encoding="utf-8"))


def _manifest_paths() -> list[str]:
    manifest = _read_manifest()
    paths: list[str] = []
    for group in manifest["included_files"].values():
        paths.extend(group)
    return list(dict.fromkeys(paths))


def test_manifest_schema_scope_and_non_claims() -> None:
    manifest = _read_manifest()
    metadata = manifest["package_metadata"]

    assert manifest["schema_version"] == EXPECTED_MANIFEST_SCHEMA
    assert metadata["runtime_attached_internal_v1_functional"] is True
    assert metadata["default_on_runtime_behavior"] is False
    assert metadata["customer_ready"] is False
    assert metadata["human_validated"] is False
    assert metadata["product_proof"] is False
    assert metadata["answer_quality_scored"] is False
    assert metadata["agent_action_authorized"] is False
    assert metadata["automatic_action_authorized"] is False
    assert metadata["model_calls"] == 0
    assert manifest["decision_gate"] == "runtime_attached_internal_v1_packaged"


def test_manifest_paths_exist_and_exclude_forbidden_surfaces() -> None:
    paths = _manifest_paths()

    assert "scripts/archive_run.py" in paths
    assert "scripts/skill/finalize_and_archive.sh" not in paths
    assert "SKILL.md" not in paths
    assert len(paths) == len(set(paths))
    for path in paths:
        assert not path.startswith(FORBIDDEN_PATH_PREFIXES), path
        assert (REPO_ROOT / path).exists(), path


def test_review_json_is_conservative_and_covers_runtime_hook() -> None:
    review = _read_review()

    assert review["schema_version"] == EXPECTED_REVIEW_SCHEMA
    assert review["model_calls"] == 0
    for field in REQUIRED_FALSE_REVIEW_FIELDS:
        assert review[field] is False
    assert review["runtime_hook_changed"] is True
    assert review["flag"]["name"] == DECISION_WORK_RUNTIME_ATTACHMENT_FLAG
    assert review["flag"]["default_off"] is True
    assert review["runtime_attached_internal_v1_claim"]["functional_internal_v1"] is True
    assert review["runtime_attached_internal_v1_claim"]["default_on"] is False
    assert review["decision_gate"] == "package_runtime_attached_internal_v1"


def test_review_covers_available_blocked_agent_only_and_default_off_cases() -> None:
    coverage = _read_review()["case_coverage"]

    assert coverage["generated_available_case"]["status"] == "covered_by_safe_fixture"
    assert coverage["blocked_hard_failure_case"]["status"] == "covered_by_safe_fixture"
    assert coverage["agent_only_or_caveated_case"]["status"] == (
        "covered_by_safe_fixture"
    )
    assert coverage["default_off_case"]["status"] == "covered_by_safe_fixture"
    assert decision_work_runtime_attachment_enabled({}) is False


def test_review_and_manifest_have_no_private_markers_or_forbidden_authority() -> None:
    rendered = (
        MANIFEST_PATH.read_text(encoding="utf-8")
        + "\n"
        + REVIEW_JSON_PATH.read_text(encoding="utf-8")
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in rendered
    forbidden_fragments = (
        '"human_validated": true',
        '"product_proof": true',
        '"answer_quality_scored": true',
        '"agent_action_authorized": true',
        '"automatic_action_authorized": true',
        "safe_for_agent_use",
        '"quality_score"',
        '"winner"',
    )
    for fragment in forbidden_fragments:
        assert fragment not in rendered


def test_package_docs_and_json_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [MANIFEST_PATH, PACKAGE_DOC_PATH, REVIEW_DOC_PATH, REVIEW_JSON_PATH]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
