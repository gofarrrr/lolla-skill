from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-update-packet-prewrite-package-gate-v0.md"
)
MANIFEST_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-update-packet-prewrite-package-manifest-v0.json"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
PR203_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-sidecar-update-packet-review-v0.md"
)
PR203_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-sidecar-update-packet-review-v0/review.json"
)
ADAPTER_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-resolver-candidate-sidecar-update-packet-adapter-v0.md"
)
HISTORICAL_DISCOVERY_PATH = REPO_ROOT / "docs/history/decision-work-product-delta-discoverability.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
EXPECTED_SCHEMA = (
    "lolla.decision_work_sidecar_update_packet_prewrite_package_manifest.v0"
)
FORBIDDEN_PREFIXES = (
    "scripts/skill/",
    "plans/",
    "reviews/synthetic/",
    "docs/lolla-",
    "docs/semantica-",
    "docs/thoughtbox-",
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
REQUIRED_FILES = {
    "docs/conversation-understanding/decision-work-resolver-candidate-sidecar-update-plan-v0.md",
    "reviews/codex-assisted/decision-work-resolver-candidate-sidecar-update-plan-v0/review.json",
    "docs/conversation-understanding/decision-work-resolver-candidate-sidecar-update-packet-adapter-v0.md",
    "engine/system_b/decision_work_resolver_candidate_sidecar_update_packet.py",
    "scripts/evals/build_decision_work_resolver_candidate_sidecar_update_packet.py",
    "tests/test_decision_work_resolver_candidate_sidecar_update_packet.py",
    "docs/conversation-understanding/decision-work-sidecar-update-packet-review-v0.md",
    "reviews/codex-assisted/decision-work-sidecar-update-packet-review-v0/review.json",
    "tests/test_decision_work_sidecar_update_packet_review.py",
    "docs/conversation-understanding/decision-work-sidecar-update-packet-prewrite-package-gate-v0.md",
    "docs/conversation-understanding/decision-work-sidecar-update-packet-prewrite-package-manifest-v0.json",
    "tests/test_decision_work_sidecar_update_packet_prewrite_package_gate.py",
}


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
    assert metadata["included_pr_range"] == "PR201-PR204"
    assert metadata["dependency_pr_range_by_reference"] == "PR178-PR200"
    assert metadata["prewrite_v1_functional"] is True
    assert metadata["offline_only"] is True
    assert metadata["deterministic_only"] is True
    assert metadata["checked_in_safe_scope"] is True
    assert metadata["actual_sidecar_writes"] is False
    assert metadata["archive_mutation"] is False
    assert metadata["runtime_wiring"] is False
    assert metadata["resolver_refs_approved"] is False
    assert metadata["resolver_refs_marked_usable"] is False
    assert metadata["default_on_runtime_behavior"] is False
    assert metadata["direct_runtime_interpretation"] is False
    assert metadata["queue_workers_or_daemons"] is False
    assert metadata["provider_model_calls"] == 0
    assert metadata["human_validated"] is False
    assert metadata["product_proof"] is False
    assert metadata["answer_quality_scored"] is False
    assert metadata["advice_correctness_claimed"] is False
    assert metadata["agent_action_authorized"] is False
    assert metadata["automatic_action_authorized"] is False


def test_manifest_includes_required_files_and_all_exist() -> None:
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
    assert "docs/semantica-*" in manifest["excluded_paths"]
    assert "docs/thoughtbox-*" in manifest["excluded_paths"]
    for ref in files:
        assert ref not in FORBIDDEN_EXACT
        assert not any(ref.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)


def test_manifest_groups_packet_adapter_reviews_and_package_files() -> None:
    manifest = _load_manifest()
    included = manifest["included_files"]

    assert "engine/system_b/decision_work_resolver_candidate_sidecar_update_packet.py" in (
        included["code_modules"]
    )
    assert (
        "scripts/evals/build_decision_work_resolver_candidate_sidecar_update_packet.py"
        in included["cli_scripts"]
    )
    assert (
        "reviews/codex-assisted/decision-work-sidecar-update-packet-review-v0/review.json"
        in included["review_artifacts"]
    )
    assert MANIFEST_PATH.relative_to(REPO_ROOT).as_posix() in (
        included["package_gate_files"]
    )
    assert PACKAGE_DOC.relative_to(REPO_ROOT).as_posix() in (
        included["package_gate_files"]
    )


def test_package_claim_is_prewrite_and_non_overclaiming() -> None:
    manifest = _load_manifest()
    claim = manifest["package_claim"]
    claim_text = json.dumps(claim, sort_keys=True).lower()

    assert "pre-write" in claim["claim"].lower()
    assert "offline" in claim["claim"].lower()
    assert "proposed sidecar update packets" in claim["claim"]
    assert "deterministic_sidecar_update_packet_adapter" in claim["allowed_claims"]
    assert "deploy_packet_with_runtime_block" in claim["allowed_claims"]
    assert "not_actual_sidecar_write" in claim["claim_limits"]
    assert "not_archive_mutation" in claim["claim_limits"]
    assert "not_resolver_approval" in claim["claim_limits"]
    assert "not_runtime_wiring" in claim["claim_limits"]
    assert "customer-ready" not in claim_text
    assert "default-on" not in claim_text


def test_case_coverage_and_non_claims_are_conservative() -> None:
    manifest = _load_manifest()
    cases = manifest["case_coverage"]["sidecar_update_packet_cases"]
    statuses = {
        case["case_id"]: case["sidecar_update_packet_status"] for case in cases
    }
    non_claims = set(manifest["non_claims"])

    assert statuses["launch-public-enterprise-beta"] == (
        "ready_for_sidecar_update_packet"
    )
    assert statuses["deploy-assisted-intake-routing"] == (
        "packet_with_runtime_block"
    )
    for case in cases:
        assert case["resolver_refs_approved"] is False
        assert case["actual_sidecar_write_performed"] is False
        assert case["archive_mutated"] is False
        assert case["runtime_wiring_changed"] is False
    assert "not_actual_sidecar_write" in non_claims
    assert "not_archive_mutation" in non_claims
    assert "not_runtime_wiring" in non_claims
    assert "not_resolver_approval" in non_claims
    assert "not_answer_quality_scoring" in non_claims
    assert "not_advice_correctness" in non_claims
    assert "not_agent_action_authorization" in non_claims
    assert "not_automatic_action_authorization" in non_claims


def test_package_doc_records_functionality_limits_and_next_step() -> None:
    text = PACKAGE_DOC.read_text(encoding="utf-8")

    assert "# Decision Work Sidecar Update Packet Pre-Write Package Gate v0" in text
    assert "Narrow Pre-Write v1 Claim" in text
    assert "Functional Chain" in text
    assert "What Is Functional" in text
    assert "What Remains Missing" in text
    assert "sidecar_update_packet_prewrite_v1_packaged" in text
    assert "PR205 Runtime Sidecar Write Plan v0" in text
    assert "Do not implement sidecar write code" in text
    assert "actual sidecar writes" in text
    assert "archive mutation" in text
    assert "resolver approval" in text


def test_discoverability_docs_reference_pr204() -> None:
    expected = "Decision Work Sidecar Update Packet Pre-Write Package Gate"
    for path in (
        PACKAGE_DOC,
        PR203_DOC,
        PRD_PATH,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr204_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            PACKAGE_DOC,
            MANIFEST_PATH,
            PR203_DOC,
            PR203_REVIEW,
            ADAPTER_DOC,
            PRD_PATH,
            HISTORICAL_DISCOVERY_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_manifest_and_docs_contain_no_forbidden_markers() -> None:
    for path in (
        PACKAGE_DOC,
        MANIFEST_PATH,
        PR203_DOC,
        PR203_REVIEW,
        ADAPTER_DOC,
        PRD_PATH,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for marker in PRIVATE_MARKERS:
            assert marker not in text, (path, marker)
