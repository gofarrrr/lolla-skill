from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import engine.system_b.decision_work_brief_runtime_attachment as runtime_attachment
from engine.system_b.decision_work_brief_safe_case_registry import (
    DecisionWorkBriefSafeCaseRegistryError,
    load_safe_case_registry,
)
from engine.system_b.decision_work_brief_safe_supply_resolver import (
    resolve_decision_work_brief_safe_supply,
    write_resolver_json,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-hook-registry-fixture-review-v0.md"
)
REVIEW_JSON = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-brief-runtime-hook-registry-fixture-review-v0/review.json"
)
REGISTRY_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-checked-in-safe-case-registry-v0.json"
)
PR175_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-checked-in-safe-case-registry-v0.md"
)
FLAG = runtime_attachment.DECISION_WORK_RUNTIME_ATTACHMENT_FLAG
MODE_ENV = runtime_attachment.DECISION_WORK_RESOLVER_MODE_ENV
EXPECTED_SCHEMA = (
    "lolla.decision_work_brief_runtime_hook_registry_fixture_review.v0"
)
EXPECTED_FIXTURES = {
    "flag_off_registry_present",
    "registry_hit_launch_beta",
    "registry_hit_deploy_intake",
    "registry_hit_cofounder_high_risk",
    "registry_miss_unknown_case",
    "registry_entry_missing_ref",
    "registry_entry_privacy_marker",
    "registry_direct_runtime_interpretation_forbidden",
}
EXPECTED_CASES = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
}
ALLOWED_DECISION_GATES = {
    "runtime_attached_v1_package_refresh",
    "runtime_attachment_product_surface_patch",
    "offline_interpretation_queue_contract",
    "checked_in_safe_registry_patch",
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


def _load_review() -> dict[str, Any]:
    return json.loads(REVIEW_JSON.read_text(encoding="utf-8"))


def _fixture_reviews(review: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        fixture["fixture_name"]: fixture
        for fixture in review["fixture_reviews"]
        if isinstance(fixture, dict)
    }


def _write_completed_archive_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True)
    for name in (
        "agent_result.json",
        "evaluation.json",
        "reasoning_trace.json",
        "extraction.json",
        "result.json",
    ):
        (run_dir / name).write_text(
            json.dumps({"schema_version": "fixture.v0", "artifact": name}),
            encoding="utf-8",
        )
    (run_dir / "revised.txt").write_text(
        "Safe revised-answer placeholder for fixture use only.",
        encoding="utf-8",
    )


def _install_registry_resolver(monkeypatch: pytest.MonkeyPatch, *, case_key: str) -> None:
    def build_registry_resolver_output(
        *,
        run_path: Path,
        environ: dict[str, str] | None,
        resolver_work_dir: Path,
        created_at: str | None,
    ) -> Path:
        del environ
        result = resolve_decision_work_brief_safe_supply(
            run_dir=run_path,
            mode="checked_in_safe_case_registry",
            case_registry_path=REGISTRY_PATH,
            case_key=case_key,
            created_at=created_at,
        )
        resolver_output_path = resolver_work_dir / "safe_supply_resolver.json"
        write_resolver_json(resolver_output_path, result, pretty=True)
        return resolver_output_path

    monkeypatch.setattr(
        runtime_attachment,
        "_build_hook_resolver_output",
        build_registry_resolver_output,
    )


def _run_registry_hook_fixture(
    *,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case_key: str,
) -> tuple[Path, dict[str, Any]]:
    run_dir = tmp_path / case_key / "run"
    _write_completed_archive_run(run_dir)
    with monkeypatch.context() as patch_context:
        _install_registry_resolver(patch_context, case_key=case_key)
        result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
            run_dir=run_dir,
            environ={FLAG: "1"},
            created_at="2026-07-02T00:00:00Z",
        )
    return run_dir, result


def _status(run_dir: Path) -> dict[str, Any]:
    return json.loads(
        (run_dir / "decision_work/attachment_status.json").read_text(encoding="utf-8")
    )


def _resolver_output(run_dir: Path) -> dict[str, Any]:
    return json.loads(
        (run_dir / "decision_work/safe_supply_resolver.json").read_text(
            encoding="utf-8"
        )
    )


def _receipt_state(run_dir: Path) -> str:
    receipt_path = run_dir / "decision_work/user_receipt.md"
    if not receipt_path.exists():
        return "not_written"
    receipt = receipt_path.read_text(encoding="utf-8")
    if "Decision Work Brief: available for agent inspection" in receipt:
        return "available_for_agent_inspection"
    if "Decision Work Brief: available with caveats" in receipt:
        return "available_with_caveats"
    if "Decision Work Brief: available" in receipt:
        return "available"
    if "Decision Work Brief: deferred" in receipt:
        return "deferred"
    if "Decision Work Brief: blocked" in receipt:
        return "blocked"
    if "Decision Work Brief: failed closed" in receipt:
        return "failed_closed"
    return "unknown"


def _sidecar_text(run_dir: Path) -> str:
    sidecar = run_dir / "decision_work"
    if not sidecar.exists():
        return ""
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(sidecar.iterdir())
        if path.is_file()
    )


def _assert_no_private_or_local_content(run_dir: Path, tmp_path: Path) -> None:
    rendered = _sidecar_text(run_dir)
    assert str(tmp_path) not in rendered
    for marker in PRIVACY_MARKERS:
        assert marker not in rendered


def _actual_registry_fixture_summary(run_dir: Path, result: dict[str, Any]) -> dict[str, Any]:
    status = _status(run_dir)
    resolver = _resolver_output(run_dir)
    return {
        "registry_case_key": resolver["case_registry"]["case_key"],
        "resolver_mode": status["resolver_summary"]["resolver_mode"],
        "resolver_status": status["resolver_summary"]["resolver_status"],
        "attachment_status": status["attachment_state"],
        "receipt_state": _receipt_state(run_dir),
        "sidecar_written": (run_dir / "decision_work").exists(),
        "agent_handoff_written": (
            run_dir / "decision_work/agent_handoff_packet.json"
        ).exists(),
        "hook_result_state": result["attachment_state"],
    }


def test_review_json_shape_and_conservative_flags() -> None:
    review = _load_review()

    assert review["schema_version"] == EXPECTED_SCHEMA
    assert review["reviewed_stage"] == "PR175"
    assert set(review["fixture_modes_reviewed"]) == EXPECTED_FIXTURES
    assert review["registry_ref"] == (
        "docs/conversation-understanding/"
        "decision-work-brief-runtime-checked-in-safe-case-registry-v0.json"
    )
    assert set(review["registry_entries_reviewed"]) == EXPECTED_CASES
    assert review["human_validated"] is False
    assert review["product_proof"] is False
    assert review["model_calls"] == 0
    assert review["runtime_invoked"] is False
    assert review["local_hook_code_paths_invoked_in_tests"] is True
    assert review["skill_invoked"] is False
    assert review["archive_mutated"] is False
    assert review["prompt_changed"] is False
    assert review["skill_files_changed"] is False
    assert review["answer_quality_scored"] is False
    assert review["agent_action_authorized"] is False
    assert review["automatic_action_authorized"] is False


def test_review_covers_registry_fixtures_and_non_runnable_states() -> None:
    fixtures = _fixture_reviews(_load_review())

    assert set(fixtures) == EXPECTED_FIXTURES
    for fixture in fixtures.values():
        assert fixture["model_calls"] == 0
        assert fixture["archive_completion_blocked"] is False
        assert fixture["unsafe_content_copied"] is False
        assert fixture["local_absolute_paths_exported"] is False
        assert fixture["finding"]
        assert "blocker_or_caveat" in fixture

    for fixture_name in (
        "registry_miss_unknown_case",
        "registry_entry_missing_ref",
        "registry_entry_privacy_marker",
    ):
        assert fixtures[fixture_name]["runnable_in_pr176"] is False
        assert "not runnable" in fixtures[fixture_name]["blocker_or_caveat"]


def test_registry_entries_are_reviewed_through_hook_fixture_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    review_fixtures = _fixture_reviews(_load_review())

    fixture_names = {
        "launch-public-enterprise-beta": "registry_hit_launch_beta",
        "deploy-assisted-intake-routing": "registry_hit_deploy_intake",
        "ceo-remove-founding-cofounder": "registry_hit_cofounder_high_risk",
    }
    for case_key, fixture_name in fixture_names.items():
        run_dir, result = _run_registry_hook_fixture(
            tmp_path=tmp_path,
            monkeypatch=monkeypatch,
            case_key=case_key,
        )
        actual = _actual_registry_fixture_summary(run_dir, result)
        expected = review_fixtures[fixture_name]

        assert actual["registry_case_key"] == case_key
        assert actual["resolver_mode"] == expected["resolver_mode"]
        assert actual["resolver_status"] == expected["resolver_status"]
        assert actual["attachment_status"] == expected["attachment_status"]
        assert actual["receipt_state"] == expected["receipt_state"]
        assert actual["sidecar_written"] is expected["sidecar_written"]
        assert actual["agent_handoff_written"] is expected["agent_handoff_written"]
        assert actual["hook_result_state"] == expected["attachment_status"]
        _assert_no_private_or_local_content(run_dir, tmp_path)


def test_flag_off_registry_present_does_not_lookup_or_write_sidecar(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_dir = tmp_path / "flag-off-registry-present/run"
    _write_completed_archive_run(run_dir)

    def fail_if_called(*args: Any, **kwargs: Any) -> Path:
        raise AssertionError("registry resolver should not run when flag is off")

    monkeypatch.setattr(
        runtime_attachment,
        "_build_hook_resolver_output",
        fail_if_called,
    )

    result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=run_dir,
        environ={},
        created_at="2026-07-02T00:00:00Z",
    )

    assert result["attachment_state"] == "not_requested"
    assert result["sidecar_written"] is False
    assert not (run_dir / "decision_work").exists()


def test_non_runnable_registry_error_states_are_reviewed(tmp_path: Path) -> None:
    fixtures = _fixture_reviews(_load_review())

    with pytest.raises(DecisionWorkBriefSafeCaseRegistryError):
        load_safe_case_registry(_registry_with_missing_ref(tmp_path))

    privacy_registry, unsafe_ref = _registry_with_private_marker_ref(tmp_path)
    try:
        with pytest.raises(DecisionWorkBriefSafeCaseRegistryError):
            load_safe_case_registry(privacy_registry)
    finally:
        unsafe_ref.unlink(missing_ok=True)

    result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=_completed_run_for_direct_block(tmp_path),
        environ={
            FLAG: "1",
            MODE_ENV: "future_direct_runtime_interpretation_not_allowed",
        },
        created_at="2026-07-02T00:00:00Z",
    )
    status = _status(_completed_run_for_direct_block(tmp_path))

    assert fixtures["registry_miss_unknown_case"]["resolver_status"] == (
        "registry_entry_not_found_before_hook"
    )
    assert fixtures["registry_entry_missing_ref"]["resolver_status"] == (
        "registry_ref_missing_before_hook"
    )
    assert fixtures["registry_entry_privacy_marker"]["resolver_status"] == (
        "blocked_privacy_risk_before_hook"
    )
    assert result["attachment_state"] == "blocked"
    assert status["resolver_summary"]["resolver_status"] == (
        "blocked_direct_runtime_interpretation"
    )


def _registry_base() -> dict[str, Any]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _registry_with_missing_ref(tmp_path: Path) -> Path:
    payload = _registry_base()
    payload["entries"] = [dict(payload["entries"][0])]
    payload["entries"][0]["safe_artifact_refs"] = dict(
        payload["entries"][0]["safe_artifact_refs"]
    )
    payload["entries"][0]["safe_artifact_refs"]["rendered_brief_markdown_ref"] = (
        "docs/conversation-understanding/missing-pr176-registry-ref.md"
    )
    path = tmp_path / "registry-missing-ref.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _registry_with_private_marker_ref(tmp_path: Path) -> tuple[Path, Path]:
    unsafe_ref = (
        REPO_ROOT
        / "docs/conversation-understanding/"
        "unsafe-pr176-registry-fixture.md"
    )
    unsafe_ref.write_text("unsafe " + "raw_message" + "_content\n", encoding="utf-8")
    payload = _registry_base()
    payload["entries"] = [dict(payload["entries"][0])]
    payload["entries"][0]["safe_artifact_refs"] = dict(
        payload["entries"][0]["safe_artifact_refs"]
    )
    payload["entries"][0]["safe_artifact_refs"]["rendered_brief_markdown_ref"] = (
        "docs/conversation-understanding/unsafe-pr176-registry-fixture.md"
    )
    path = tmp_path / "registry-privacy-marker.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path, unsafe_ref


def _completed_run_for_direct_block(tmp_path: Path) -> Path:
    run_dir = tmp_path / "direct-runtime-interpretation/run"
    if not run_dir.exists():
        _write_completed_archive_run(run_dir)
    return run_dir


def test_review_decision_gate_and_non_claims() -> None:
    review = _load_review()
    rendered = json.dumps(review, sort_keys=True).lower()

    assert review["decision_gate"] in ALLOWED_DECISION_GATES
    assert review["decision_gate"] == "runtime_attached_v1_package_refresh"
    assert review["recommended_next_pr"]
    assert "not_customer_readiness" in review["non_claims"]
    assert "not_default_on_runtime_behavior" in review["non_claims"]
    assert "not_product_proof" in review["non_claims"]
    assert "not_human_validation" in review["non_claims"]
    assert "not_answer_quality_scoring" in review["non_claims"]
    assert "not_agent_action_authorization" in review["non_claims"]
    assert "customer ready" not in rendered
    assert "default-on" not in rendered
    assert "advice is correct" not in rendered
    assert "lolla improved decisions as fact" not in rendered


def test_pr176_review_artifacts_are_private_safe() -> None:
    rendered = REVIEW_DOC.read_text(encoding="utf-8") + REVIEW_JSON.read_text(
        encoding="utf-8"
    )
    lowered = rendered.lower()

    for marker in PRIVACY_MARKERS:
        assert marker not in rendered
    assert "/tmp/" not in rendered
    assert "is product proof" not in lowered
    assert "is human validation" not in lowered
    assert "authorizes action" not in lowered
    assert "scores answer quality" not in lowered


def test_pr176_docs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([REVIEW_DOC, REVIEW_JSON, PR175_DOC])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
