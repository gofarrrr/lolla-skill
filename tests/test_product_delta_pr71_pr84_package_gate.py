from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "docs/evals/product-delta-pr71-pr84-package-manifest-v0.json"
DOC_PATH = REPO_ROOT / "docs/evals/product-delta-pr71-pr84-packaging-gate-v0.md"
PR81_PACKETS_PATH = (
    REPO_ROOT / "reviews/codex-assisted/product-delta-specialist-packets-v0/packets.json"
)
PR83_REVIEW_PATH = REPO_ROOT / "reviews/codex-assisted/specialist-review-batch-v0/review.json"
PR84_REPORT_PATH = (
    REPO_ROOT / "reviews/codex-assisted/fan-in-disagreement-report-v0/report.json"
)
PR75_REVIEW_PATH = (
    REPO_ROOT / "reviews/codex-assisted/product-delta-provisional-run-v0/review.json"
)
PR76_REVIEW_PATH = REPO_ROOT / "reviews/codex-assisted/product-delta-batch-v0/review.json"

EXPECTED_SCHEMA_VERSION = "lolla.product_delta_pr71_pr84_package_manifest.v0"
EXPECTED_PR_NUMBERS = set(range(71, 85))
BOUNDARY_FALSE_FIELDS = {
    "human_validated",
    "ground_truth",
    "judge_calibration_eligible",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "archive_mutated",
    "runtime_invoked",
    "skill_invoked",
}
FORBIDDEN_AUTHORITY_FIELDS = {
    "safe_for_agent_use",
    "quality_score",
    "answer_quality_score",
    "improvement_score",
    "judge_score",
    "winner",
    "approved",
    "certified",
    "pass_fail",
}
PRIVACY_MARKERS = (
    "/Users/",
    "SECRET",
    "raw_message_content",
    "fabricated_passages",
    "FULL ASSISTANT REASONING",
    "client_secret",
    "api_key",
    "password",
)
SOURCE_REF_KEYS = {
    "artifact_ref",
    "checked_artifacts",
    "input_packet_ref",
    "input_refs",
    "prior_broad_read_ref",
    "pr76_source_artifact",
    "pr83_source_artifact",
    "reviewed_artifacts",
    "schema_ref",
    "source_artifacts",
    "source_ref",
    "source_refs",
    "source_shell_batch",
}
REPO_REF_PREFIXES = (
    "docs/",
    "engine/",
    "reviews/",
    "scripts/",
    "tests/",
)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest() -> dict[str, Any]:
    return _json(MANIFEST_PATH)


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_walk_keys(child))
    return keys


def _included_files() -> list[str]:
    manifest = _manifest()
    files: list[str] = []
    for group in manifest["included_files"].values():
        files.extend(group)
    return files


def _json_artifact_paths() -> list[Path]:
    manifest = _manifest()
    json_paths = (
        manifest["included_files"]["json_artifacts"]
        + manifest["included_files"]["review_fixtures"]
        + [str(MANIFEST_PATH.relative_to(REPO_ROOT))]
    )
    return [REPO_ROOT / path for path in json_paths]


def _lint_paths() -> list[Path]:
    manifest = _manifest()
    paths = [DOC_PATH, MANIFEST_PATH]
    for group_name in ("docs", "json_artifacts", "review_fixtures"):
        paths.extend(REPO_ROOT / path for path in manifest["included_files"][group_name])
    return paths


def _collect_strings(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, str):
        refs.append(value)
    elif isinstance(value, list):
        for item in value:
            refs.extend(_collect_strings(item))
    elif isinstance(value, dict):
        for item in value.values():
            refs.extend(_collect_strings(item))
    return refs


def _looks_like_repo_ref(value: str) -> bool:
    path_part = value.split("#", 1)[0]
    return path_part.startswith(REPO_REF_PREFIXES) and " " not in path_part


def _collect_repo_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "archive_relpath":
                continue
            if key in SOURCE_REF_KEYS or key.endswith("_ref"):
                for candidate in _collect_strings(child):
                    if _looks_like_repo_ref(candidate):
                        refs.add(candidate)
            refs.update(_collect_repo_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_collect_repo_refs(child))
    return refs


def _resolve_json_pointer(payload: Any, pointer: str) -> Any:
    if pointer in ("", "/"):
        return payload
    current = payload
    for raw_part in pointer.lstrip("/").split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    return current


def _assert_ref_resolves(ref: str) -> None:
    path_part, _, pointer = ref.partition("#")
    path = REPO_ROOT / path_part
    assert path.exists(), ref
    if pointer and path.suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        _resolve_json_pointer(payload, pointer)


def test_package_manifest_json_parses_and_has_expected_version() -> None:
    payload = _manifest()

    assert payload["schema_version"] == EXPECTED_SCHEMA_VERSION
    assert payload["phase"] == "product_delta_evidence_pr71_pr84"
    assert payload["status"] == "packaging_gate"


def test_boundary_metadata_is_conservative() -> None:
    boundary = _manifest()["boundary"]

    for field in BOUNDARY_FALSE_FIELDS:
        assert boundary[field] is False, field
    assert boundary["model_calls"] == 0


def test_manifest_includes_pr71_through_pr84_exactly() -> None:
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
    for relpath in _included_files() + _manifest()["packaging_gate_files"]:
        path = REPO_ROOT / relpath
        assert path.exists(), relpath


def test_manifest_does_not_include_unrelated_untracked_files() -> None:
    included = set(_included_files())

    assert "docs/lolla-pitch-and-invitation-kopia.md" not in included
    assert not any(path.startswith("plans/") for path in included)
    assert not any(path.startswith("reviews/synthetic/") for path in included)


def test_no_forbidden_authority_field_names_exist() -> None:
    keys = _walk_keys(_manifest())

    assert not (FORBIDDEN_AUTHORITY_FIELDS & keys)


def test_manifest_records_key_downgrade() -> None:
    signal = _manifest()["phase_summary"]["strongest_useful_signal"]

    assert signal["case_id"] == "accept-operations-role-startup"
    assert signal["from_candidate"] == "material_improvement_candidate"
    assert signal["to_candidate"] == "partial_improvement_candidate"
    assert signal["source_refs"]


def test_manifest_records_thinness_and_selection_limits() -> None:
    limits = _manifest()["known_limits"]
    strongest_risk = _manifest()["phase_summary"]["strongest_unresolved_risk"]

    for payload in (limits, strongest_risk):
        assert payload["real_case_count"] == 2
        assert payload["prior_positive_fixture_cases"] is True
        assert payload["no_real_case_no_change_noise_worse_or_inconclusive"] is True
        assert payload["positive_distribution_risk_acknowledged"] is True
        assert payload["no_raw_private_content_read"] is True
    assert limits["human_review_available"] is False
    assert strongest_risk["human_validation_available"] is False


def test_pr84_report_remains_static_over_existing_pr76_pr83_review() -> None:
    report = _json(PR84_REPORT_PATH)
    method = report["method"]

    assert method["new_specialist_reads_created"] is False
    assert method["new_codex_review_created"] is False
    assert method["semantic_read_source"] == "pr83_existing_review_only"


def test_pr83_actual_shape_is_referenced_correctly() -> None:
    paths = _manifest()["source_reference_policy"]["actual_shape_paths"]

    assert paths["pr83_traps"] == "trap_discipline_pass.results"
    assert (
        paths["pr83_pr76_comparison"]
        == "real_case_specialist_pass.cases[*].case_summary.pr76_comparison"
    )
    assert (
        paths["pr83_net_read"]
        == "real_case_specialist_pass.cases[*].case_summary.pr83_net_decision_read_candidate"
    )
    assert paths["pr83_specialist_reads"] == (
        "real_case_specialist_pass.cases[*].specialist_reads"
    )


def test_all_package_json_artifacts_parse() -> None:
    for path in _json_artifact_paths():
        json.loads(path.read_text(encoding="utf-8"))


def test_source_reference_paths_and_json_pointers_resolve() -> None:
    payloads = [
        _manifest(),
        _json(PR81_PACKETS_PATH),
        _json(PR83_REVIEW_PATH),
        _json(PR84_REPORT_PATH),
        _json(PR75_REVIEW_PATH),
        _json(PR76_REVIEW_PATH),
    ]
    refs: set[str] = set()
    for payload in payloads:
        refs.update(_collect_repo_refs(payload))

    assert "reviews/codex-assisted/product-delta-batch-v0/review.json#/cases/1" in refs
    assert (
        "reviews/codex-assisted/product-delta-specialist-packets-v0/packets.json#/cases/1"
        in refs
    )
    assert "reviews/human/corpus-batch-v0/review.json#/records/1" in refs
    assert refs
    for ref in sorted(refs):
        _assert_ref_resolves(ref)


def test_pr78_lint_passes_pr85_and_pr71_pr84_product_delta_surface() -> None:
    report = lint_product_delta_paths(_lint_paths())

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_pr85_docs_and_manifest_have_no_privacy_markers() -> None:
    rendered_manifest = json.dumps(_manifest(), sort_keys=True)
    rendered_doc = DOC_PATH.read_text(encoding="utf-8")

    for marker in PRIVACY_MARKERS:
        assert marker not in rendered_manifest
        assert marker not in rendered_doc
