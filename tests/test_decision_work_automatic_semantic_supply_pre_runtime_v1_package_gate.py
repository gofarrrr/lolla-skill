from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-automatic-semantic-supply-pre-runtime-v1-package-gate-v0.md"
)
MANIFEST_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-automatic-semantic-supply-pre-runtime-v1-package-manifest-v0.json"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
PR199_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-resolver-supply-review-v0.md"
)
PR199_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-resolver-supply-review-v0/review.json"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
EXPECTED_SCHEMA = (
    "lolla.decision_work_automatic_semantic_supply_pre_runtime_v1_package_manifest.v0"
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
    "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md",
    "docs/conversation-understanding/decision-work-offline-interpretation-queue-contract-v0.json",
    "engine/system_b/decision_work_offline_interpretation_queue.py",
    "scripts/evals/build_decision_work_offline_interpretation_queue.py",
    "engine/system_b/decision_work_generated_interpretation_read_intake.py",
    "scripts/evals/validate_decision_work_generated_interpretation_read.py",
    "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json",
    "reviews/codex-assisted/decision-work-generated-read-second-brief-rendering-pilot-v0/read.json",
    "engine/system_b/decision_work_generated_read_brief_supply.py",
    "scripts/evals/build_decision_work_generated_read_brief_supply.py",
    "engine/system_b/decision_work_generated_read_brief_renderer.py",
    "scripts/evals/render_decision_work_generated_read_brief.py",
    "docs/conversation-understanding/decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md",
    "docs/conversation-understanding/decision-work-generated-read-rendered-deploy-assisted-intake-routing-v0.md",
    "engine/system_b/decision_work_generated_read_triage_supply.py",
    "scripts/evals/build_decision_work_generated_read_triage_supply.py",
    "reviews/codex-assisted/decision-work-generated-read-triage-generation-pilot-v0/triage.json",
    "reviews/codex-assisted/decision-work-generated-read-second-triage-pilot-v0/triage.json",
    "engine/system_b/decision_work_generated_read_resolver_supply.py",
    "scripts/evals/build_decision_work_generated_read_resolver_supply.py",
    "docs/conversation-understanding/decision-work-generated-read-resolver-supply-review-v0.md",
    "reviews/codex-assisted/decision-work-generated-read-resolver-supply-review-v0/review.json",
    "docs/conversation-understanding/decision-work-automatic-semantic-supply-pre-runtime-v1-package-gate-v0.md",
    "docs/conversation-understanding/decision-work-automatic-semantic-supply-pre-runtime-v1-package-manifest-v0.json",
    "tests/test_decision_work_automatic_semantic_supply_pre_runtime_v1_package_gate.py",
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
    assert metadata["included_pr_range"] == "PR178-PR200"
    assert metadata["pre_runtime_v1_functional"] is True
    assert metadata["offline_only"] is True
    assert metadata["checked_in_safe_scope"] is True
    assert metadata["runtime_attachment"] is False
    assert metadata["runtime_sidecar_updates"] is False
    assert metadata["runtime_wiring"] is False
    assert metadata["resolver_refs_approved"] is False
    assert metadata["resolver_refs_marked_usable"] is False
    assert metadata["default_on_runtime_behavior"] is False
    assert metadata["arbitrary_run_production_automation"] is False
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


def test_manifest_groups_code_clis_reviews_and_package_files() -> None:
    manifest = _load_manifest()
    included = manifest["included_files"]

    assert "engine/system_b/decision_work_generated_interpretation_read_intake.py" in (
        included["code_modules"]
    )
    assert "engine/system_b/decision_work_generated_read_brief_supply.py" in (
        included["code_modules"]
    )
    assert "engine/system_b/decision_work_generated_read_triage_supply.py" in (
        included["code_modules"]
    )
    assert "engine/system_b/decision_work_generated_read_resolver_supply.py" in (
        included["code_modules"]
    )
    assert "scripts/evals/build_decision_work_generated_read_resolver_supply.py" in (
        included["cli_scripts"]
    )
    assert (
        "reviews/codex-assisted/decision-work-generated-read-resolver-supply-review-v0/review.json"
        in included["reviews"]
    )
    assert MANIFEST_PATH.relative_to(REPO_ROOT).as_posix() in (
        included["package_gate_files"]
    )
    assert PACKAGE_DOC.relative_to(REPO_ROOT).as_posix() in (
        included["package_gate_files"]
    )


def test_package_claim_is_pre_runtime_and_non_overclaiming() -> None:
    manifest = _load_manifest()
    claim = manifest["package_claim"]
    claim_text = json.dumps(claim, sort_keys=True).lower()

    assert "pre-runtime" in claim["claim"].lower()
    assert "offline" in claim["claim"].lower()
    assert "resolver-supply candidate packets" in claim["claim"]
    assert "generated_read_intake_validation" in claim["allowed_claims"]
    assert "two_case_generated_read_triage_pilots" in claim["allowed_claims"]
    assert "generated_read_resolver_supply_candidate_packets" in (
        claim["allowed_claims"]
    )
    assert "not_runtime_attachment" in claim["claim_limits"]
    assert "not_resolver_approval" in claim["claim_limits"]
    assert "not_runtime_sidecar_update" in claim["claim_limits"]
    assert "not_answer_quality_scoring" in claim["claim_limits"]
    assert "customer-ready" not in claim_text
    assert "default-on" not in claim_text


def test_case_coverage_and_non_claims_are_conservative() -> None:
    manifest = _load_manifest()
    cases = manifest["case_coverage"]
    non_claims = set(manifest["non_claims"])
    resolver_statuses = {
        case["case_id"]: case["resolver_supply_status"]
        for case in cases["resolver_supply_cases"]
    }

    assert set(cases["generated_read_pilot_cases"]) == {
        "launch-public-enterprise-beta",
        "deploy-assisted-intake-routing",
    }
    assert resolver_statuses["launch-public-enterprise-beta"] == (
        "ready_for_resolver_candidate_packet"
    )
    assert resolver_statuses["deploy-assisted-intake-routing"] == (
        "candidate_packet_with_runtime_block"
    )
    for case in cases["resolver_supply_cases"]:
        assert case["resolver_refs_approved"] is False
        assert case["runtime_sidecar_update_allowed"] is False
    assert "not_resolver_approval" in non_claims
    assert "not_runtime_sidecar_update" in non_claims
    assert "not_runtime_wiring" in non_claims
    assert "not_answer_quality_scoring" in non_claims
    assert "not_advice_correctness" in non_claims
    assert "not_agent_action_authorization" in non_claims
    assert "not_automatic_action_authorization" in non_claims


def test_package_doc_records_functionality_limits_and_next_step() -> None:
    text = PACKAGE_DOC.read_text(encoding="utf-8")

    assert "# Decision Work Automatic Semantic Supply Pre-Runtime v1 Package Gate v0" in text
    assert "Narrow Pre-Runtime v1 Claim" in text
    assert "Functional Chain" in text
    assert "What Is Functional" in text
    assert "What Remains Missing" in text
    assert "automatic_semantic_supply_pre_runtime_v1_packaged" in text
    assert "PR201 Resolver Candidate To Runtime Sidecar Update Plan v0" in text
    assert "Do not implement PR201" in text
    assert "resolver-supply candidate, not approved resolver refs" not in text
    assert "resolver approval" in text
    assert "runtime sidecar updates" in text


def test_discoverability_docs_reference_pr200() -> None:
    expected = "Decision Work Automatic Semantic Supply Pre-Runtime v1 Package Gate"
    for path in (
        PACKAGE_DOC,
        PR199_DOC,
        PRD_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_manifest_and_package_doc_are_private_safe() -> None:
    rendered = (
        MANIFEST_PATH.read_text(encoding="utf-8")
        + PACKAGE_DOC.read_text(encoding="utf-8")
        + PR199_REVIEW.read_text(encoding="utf-8")
    )

    for marker in PRIVATE_MARKERS:
        assert marker not in rendered
    assert str(REPO_ROOT) not in rendered


def test_pr200_docs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [
            PACKAGE_DOC,
            MANIFEST_PATH,
            PR199_DOC,
            PR199_REVIEW,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
