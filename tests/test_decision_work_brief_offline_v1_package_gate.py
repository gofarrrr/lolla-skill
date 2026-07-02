from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-offline-v1-package-gate-v0.md"
)
MANIFEST_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-offline-v1-package-manifest-v0.json"
)
BASE_MANIFEST_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-pr114-pr144-package-manifest-v0.json"
)
PR157_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-offline-v1-closure-gate-v0/review.json"
)
SCHEMA_VERSION = "lolla.decision_work_brief_offline_v1_package_manifest.v0"
FORBIDDEN_PREFIXES = (
    "SKILL.md",
    "scripts/skill/",
    "plans/",
    "reviews/synthetic/",
    "archive/",
)
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


def _pr157_review() -> dict[str, Any]:
    return json.loads(PR157_REVIEW_PATH.read_text(encoding="utf-8"))


def _manifest_paths() -> list[str]:
    paths: list[str] = []
    for group_paths in _manifest()["included_files"].values():
        paths.extend(group_paths)
    return list(dict.fromkeys(paths))


def test_manifest_schema_boundary_and_base_package_ref() -> None:
    manifest = _manifest()

    assert manifest["schema_version"] == SCHEMA_VERSION
    assert manifest["phase"] == "decision_work_brief_offline_v1"
    assert manifest["base_package"]["base_manifest_ref"] == str(
        BASE_MANIFEST_PATH.relative_to(REPO_ROOT)
    )
    assert manifest["base_package"]["included_by_reference"] is True
    assert BASE_MANIFEST_PATH.exists()

    boundary = manifest["boundary"]
    assert boundary["offline_v1_functional"] is True
    assert boundary["human_calibration_deferred"] is True
    assert boundary["codex_assisted_provisional"] is True
    assert boundary["model_calls"] == 0
    for field in (
        "runtime_integrated",
        "human_validated",
        "human_review_completed",
        "product_proof",
        "answer_quality_scored",
        "agent_action_authorized",
        "automatic_action_authorized",
        "archive_mutated",
        "runtime_invoked",
        "skill_invoked",
        "raw_private_content_included",
        "provider_text_included",
        "local_absolute_paths_included",
        "automatic_labels_created",
    ):
        assert boundary[field] is False


def test_pr157_allows_offline_v1_packaging() -> None:
    review = _pr157_review()

    assert review["decision_gate"] == "package_offline_v1"
    assert review["functional_v1_claim"]["offline_v1_functional"] is True
    assert review["functional_v1_claim"]["runtime_integrated"] is False
    assert review["functional_v1_claim"]["human_validated"] is False
    assert review["functional_v1_claim"]["product_proof"] is False


def test_every_manifest_listed_path_exists_and_excludes_forbidden_paths() -> None:
    paths = _manifest_paths()

    assert paths
    assert str(MANIFEST_PATH.relative_to(REPO_ROOT)) in paths
    assert str(DOC_PATH.relative_to(REPO_ROOT)) in paths
    for path in paths:
        assert not path.startswith(FORBIDDEN_PREFIXES), path
        assert not path.startswith("docs/lolla-"), path
        assert not Path(path).is_absolute(), path
        assert (REPO_ROOT / path).exists(), path


def test_manifest_includes_automatic_triage_and_offline_v1_files() -> None:
    paths = set(_manifest_paths())

    required = {
        "engine/system_b/decision_work_automatic_triage_packets.py",
        "scripts/evals/build_decision_work_automatic_triage_packets.py",
        "docs/conversation-understanding/decision-work-automatic-triage-contract-v0.json",
        "docs/conversation-understanding/decision-work-automatic-triage-packet-builder-v0.md",
        "reviews/codex-assisted/decision-work-automatic-triage-provisional-read-v0/read.json",
        "docs/conversation-understanding/decision-work-brief-offline-v1-closure-gate-v0.md",
        "reviews/codex-assisted/decision-work-brief-offline-v1-closure-gate-v0/review.json",
        "docs/conversation-understanding/decision-work-brief-offline-v1-package-gate-v0.md",
        "docs/conversation-understanding/decision-work-brief-offline-v1-package-manifest-v0.json",
    }
    assert required <= paths


def test_manifest_listed_json_files_parse() -> None:
    json_paths = [path for path in _manifest_paths() if path.endswith(".json")]

    assert json_paths
    for path in json_paths:
        json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_package_docs_and_manifest_preserve_limitations_and_non_claims() -> None:
    text = DOC_PATH.read_text(encoding="utf-8") + "\n" + MANIFEST_PATH.read_text(
        encoding="utf-8"
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for fragment in (
        '"human_validated": true',
        '"product_proof": true',
        '"answer_quality_scored": true',
        '"agent_action_authorized": true',
        '"automatic_action_authorized": true',
        '"runtime_integrated": true',
        "safe_for_agent_use",
    ):
        assert fragment not in text
    lowered = text.lower()
    assert "offline v1" in lowered
    assert "not runtime integration" in lowered
    assert "human validation" in lowered
    assert "product proof" in lowered


def test_package_manifest_and_docs_pass_product_delta_boundary_lint() -> None:
    lint_paths = [
        REPO_ROOT / path
        for path in _manifest_paths()
        if path.endswith((".md", ".json"))
    ]
    report = lint_product_delta_paths([DOC_PATH, MANIFEST_PATH, *lint_paths])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
