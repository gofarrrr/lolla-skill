from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-attached-internal-v1-package-refresh-v0.md"
)
MANIFEST_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-attached-internal-v1-package-manifest-v0.json"
)
PR176_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-hook-registry-fixture-review-v0.md"
)
PR176_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-brief-runtime-hook-registry-fixture-review-v0/review.json"
)
EXPECTED_SCHEMA = (
    "lolla.decision_work_brief_runtime_attached_internal_v1_package_manifest.v0"
)
REQUIRED_FILES = {
    "scripts/archive_run.py",
    "engine/system_b/decision_work_brief_runtime_attachment.py",
    "engine/system_b/decision_work_brief_runtime_bundle.py",
    "engine/system_b/decision_work_brief_runtime_eligibility.py",
    "engine/system_b/decision_work_brief_runtime_receipt.py",
    "engine/system_b/decision_work_brief_agent_handoff.py",
    "engine/system_b/decision_work_brief_safe_supply_resolver.py",
    "engine/system_b/decision_work_brief_safe_case_registry.py",
    "scripts/evals/build_decision_work_brief_runtime_bundle.py",
    "scripts/evals/render_decision_work_brief_runtime_receipt.py",
    "scripts/evals/build_decision_work_brief_agent_handoff.py",
    "scripts/evals/resolve_decision_work_brief_safe_supply.py",
    "scripts/evals/resolve_decision_work_brief_safe_case_registry.py",
    "docs/conversation-understanding/decision-work-brief-runtime-hook-registry-fixture-review-v0.md",
    "reviews/codex-assisted/decision-work-brief-runtime-hook-registry-fixture-review-v0/review.json",
    "docs/conversation-understanding/decision-work-brief-runtime-attachment-review-v0.md",
    "docs/conversation-understanding/decision-work-brief-runtime-attached-v1-package-manifest-v0.json",
    "docs/conversation-understanding/decision-work-brief-runtime-attached-internal-v1-package-refresh-v0.md",
    "docs/conversation-understanding/decision-work-brief-runtime-attached-internal-v1-package-manifest-v0.json",
    "tests/test_decision_work_brief_runtime_attached_internal_v1_package_refresh.py",
}
FORBIDDEN_PREFIXES = (
    "scripts/skill/",
    "plans/",
    "reviews/synthetic/",
    "docs/lolla-",
    "archive/",
    "runs/",
    "tmp/",
)
FORBIDDEN_EXACT = {"SKILL.md"}
PRIVATE_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _manifest_files(manifest: dict[str, Any]) -> list[str]:
    files: list[str] = []
    for group in manifest["included_files"].values():
        assert isinstance(group, list)
        files.extend(item for item in group if isinstance(item, str))
    return files


def test_manifest_schema_and_package_metadata() -> None:
    manifest = _load_manifest()
    metadata = manifest["package_metadata"]

    assert manifest["schema_version"] == EXPECTED_SCHEMA
    assert metadata["included_pr_range"] == "PR160-PR177"
    assert metadata["runtime_attached_internal_v1_functional"] is True
    assert metadata["internal_only"] is True
    assert metadata["default_off"] is True
    assert metadata["flag_name"] == "LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE"
    assert set(metadata["enabled_values"]) == {"1", "true", "on", "yes"}
    assert metadata["customer_ready"] is False
    assert metadata["default_on_runtime_behavior"] is False
    assert metadata["arbitrary_run_semantic_coverage"] is False
    assert metadata["direct_runtime_interpretation"] is False
    assert metadata["model_calls"] == 0
    assert metadata["human_validated"] is False
    assert metadata["product_proof"] is False
    assert metadata["answer_quality_scored"] is False
    assert metadata["agent_action_authorized"] is False
    assert metadata["automatic_action_authorized"] is False


def test_manifest_includes_expected_package_files_and_all_exist() -> None:
    manifest = _load_manifest()
    files = set(_manifest_files(manifest))

    assert REQUIRED_FILES <= files
    for ref in sorted(files):
        assert (REPO_ROOT / ref).exists(), ref


def test_manifest_excludes_forbidden_paths() -> None:
    manifest = _load_manifest()
    files = _manifest_files(manifest)

    assert "SKILL.md" in manifest["excluded_paths"]
    assert "scripts/skill/*" in manifest["excluded_paths"]
    assert "plans/*" in manifest["excluded_paths"]
    assert "reviews/synthetic/*" in manifest["excluded_paths"]
    assert "docs/lolla-*" in manifest["excluded_paths"]
    for ref in files:
        assert ref not in FORBIDDEN_EXACT
        assert not any(ref.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)


def test_manifest_groups_runtime_modules_clis_registry_and_pr176_review() -> None:
    manifest = _load_manifest()
    included = manifest["included_files"]

    assert "scripts/archive_run.py" in included["runtime_code_modules"]
    assert "engine/system_b/decision_work_brief_runtime_attachment.py" in (
        included["runtime_code_modules"]
    )
    assert "engine/system_b/decision_work_brief_safe_supply_resolver.py" in (
        included["runtime_code_modules"]
    )
    assert "engine/system_b/decision_work_brief_safe_case_registry.py" in (
        included["runtime_code_modules"]
    )
    assert "scripts/evals/resolve_decision_work_brief_safe_supply.py" in (
        included["cli_scripts"]
    )
    assert "scripts/evals/resolve_decision_work_brief_safe_case_registry.py" in (
        included["cli_scripts"]
    )
    assert (
        "docs/conversation-understanding/decision-work-brief-runtime-checked-in-safe-case-registry-v0.json"
        in included["registry_artifacts"]
    )
    assert (
        "reviews/codex-assisted/decision-work-brief-runtime-hook-registry-fixture-review-v0/review.json"
        in included["review_artifacts"]
    )
    assert (
        "tests/test_decision_work_brief_runtime_hook_registry_fixture_review.py"
        in included["tests"]
    )


def test_package_claim_is_internal_default_off_and_non_overclaiming() -> None:
    manifest = _load_manifest()
    claim = manifest["package_claim"]
    claim_text = json.dumps(claim, sort_keys=True).lower()

    assert "internal" in claim["claim"].lower()
    assert "default-off" in claim["claim"].lower()
    assert "post-archive" in claim["claim"].lower()
    assert "internal_v1_package_coherence" in claim["allowed_claims"]
    assert "resolver_aware_bundle_path" in claim["allowed_claims"]
    assert "registry_backed_fixture_repeatability" in claim["allowed_claims"]
    assert "not_customer_readiness" in claim["claim_limits"]
    assert "not_default_on_readiness" in claim["claim_limits"]
    assert "not_arbitrary_run_semantic_coverage" in claim["claim_limits"]
    assert "not_direct_runtime_interpretation" in claim["claim_limits"]
    assert "not_runtime_model_calls" in claim["claim_limits"]
    assert "customer ready" not in claim_text
    assert "default-on" not in claim_text


def test_non_claims_and_supply_limits_are_preserved() -> None:
    manifest = _load_manifest()
    non_claims = set(manifest["non_claims"])
    supply = manifest["supply_status"]

    assert "not_product_proof" in non_claims
    assert "not_human_validation" in non_claims
    assert "not_answer_quality_scoring" in non_claims
    assert "not_advice_correctness" in non_claims
    assert "not_agent_action_authorization" in non_claims
    assert "not_automatic_action_authorization" in non_claims
    assert "not_direct_runtime_interpretation" in non_claims
    assert supply["manual_safe_refs_supported"] is True
    assert supply["checked_in_safe_registry_supported"] is True
    assert set(supply["registry_cases_reviewed"]) == {
        "launch-public-enterprise-beta",
        "deploy-assisted-intake-routing",
        "ceo-remove-founding-cofounder",
    }
    assert supply["production_hook_registry_lookup_added"] is False
    assert supply["arbitrary_completed_runs_normally_defer_without_safe_semantic_refs"]
    assert supply["offline_interpretation_queue_implemented"] is False


def test_manifest_and_package_doc_are_private_safe() -> None:
    rendered = (
        MANIFEST_PATH.read_text(encoding="utf-8")
        + PACKAGE_DOC.read_text(encoding="utf-8")
    )

    for marker in PRIVATE_MARKERS:
        assert marker not in rendered
    assert str(REPO_ROOT) not in rendered


def test_pr177_docs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [
            PACKAGE_DOC,
            MANIFEST_PATH,
            PR176_DOC,
            PR176_REVIEW,
        ]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
