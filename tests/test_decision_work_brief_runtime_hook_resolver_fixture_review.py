from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import engine.system_b.decision_work_brief_runtime_attachment as runtime_attachment
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-hook-resolver-fixture-review-v0.md"
)
REVIEW_JSON = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-brief-runtime-hook-resolver-fixture-review-v0/review.json"
)
PR173_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-hook-resolver-wiring-v0.md"
)
FLAG = runtime_attachment.DECISION_WORK_RUNTIME_ATTACHMENT_FLAG
MODE_ENV = runtime_attachment.DECISION_WORK_RESOLVER_MODE_ENV
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
EXPECTED_SCHEMA = "lolla.decision_work_brief_runtime_hook_resolver_fixture_review.v0"
EXPECTED_FIXTURES = {
    "flag_off",
    "flag_on_no_safe_refs",
    "flag_on_safe_refs_available",
    "flag_on_safe_brief_only_agent_or_caveated",
    "direct_runtime_interpretation_blocked",
    "unsafe_private_marker_blocked",
    "bundle_exception_failed_closed",
}
ALLOWED_DECISION_GATES = {
    "checked_in_safe_case_registry",
    "offline_interpretation_queue_contract",
    "runtime_attachment_product_surface_patch",
    "runtime_attached_v1_package_refresh",
}


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


def _write_markdown(path: Path, text: str = "Safe Decision Work Brief fixture.") -> Path:
    path.write_text(text + "\n", encoding="utf-8")
    return path


def _write_json(path: Path, schema_version: str) -> Path:
    path.write_text(
        json.dumps({"schema_version": schema_version, "fixture": True}),
        encoding="utf-8",
    )
    return path


def _status(run_dir: Path) -> dict[str, Any]:
    return json.loads(
        (run_dir / "decision_work/attachment_status.json").read_text(encoding="utf-8")
    )


def _sidecar_text(run_dir: Path) -> str:
    sidecar = run_dir / "decision_work"
    if not sidecar.exists():
        return ""
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(sidecar.iterdir())
        if path.is_file()
    )


def _receipt_state(run_dir: Path) -> str:
    receipt_path = run_dir / "decision_work/user_receipt.md"
    if not receipt_path.exists():
        return "not_written"
    receipt = receipt_path.read_text(encoding="utf-8")
    if "Decision Work Brief: available for agent inspection" in receipt:
        return "available_for_agent_inspection"
    if "Decision Work Brief: available" in receipt:
        return "available"
    if "Decision Work Brief: deferred" in receipt:
        return "deferred"
    if "Decision Work Brief: blocked" in receipt:
        return "blocked"
    if "Decision Work Brief: failed closed" in receipt:
        return "failed_closed"
    return "unknown"


def _actual_fixture_summary(run_dir: Path, result: dict[str, Any]) -> dict[str, Any]:
    sidecar_written = (run_dir / "decision_work").exists()
    if not sidecar_written:
        return {
            "resolver_status": "not_applicable",
            "attachment_status": result["attachment_state"],
            "receipt_state": "not_written",
            "sidecar_written": False,
            "agent_handoff_written": False,
        }
    status = _status(run_dir)
    resolver_status = status.get("resolver_summary", {}).get(
        "resolver_status",
        "not_preserved_after_failed_closed",
    )
    return {
        "resolver_status": resolver_status,
        "attachment_status": status["attachment_state"],
        "receipt_state": _receipt_state(run_dir),
        "sidecar_written": True,
        "agent_handoff_written": (
            run_dir / "decision_work/agent_handoff_packet.json"
        ).exists(),
    }


def _assert_no_private_or_local_content(run_dir: Path, tmp_path: Path) -> None:
    rendered = _sidecar_text(run_dir)
    assert str(tmp_path) not in rendered
    for marker in PRIVACY_MARKERS:
        assert marker not in rendered


def test_review_json_shape_and_conservative_flags() -> None:
    review = _load_review()

    assert review["schema_version"] == EXPECTED_SCHEMA
    assert review["reviewed_stage"] == "PR173"
    assert set(review["fixture_modes_reviewed"]) == EXPECTED_FIXTURES
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


def test_review_covers_all_required_fixture_modes() -> None:
    review = _load_review()
    fixtures = _fixture_reviews(review)

    assert set(fixtures) == EXPECTED_FIXTURES
    for fixture in fixtures.values():
        assert fixture["model_calls"] == 0
        assert fixture["archive_completion_blocked"] is False
        assert fixture["unsafe_content_copied"] is False
        assert fixture["local_absolute_paths_exported"] is False
        assert fixture["finding"]
        assert "blocker_or_caveat" in fixture


def test_temp_hook_fixtures_match_reviewed_states(tmp_path: Path, monkeypatch) -> None:
    review_fixtures = _fixture_reviews(_load_review())

    flag_off_run = tmp_path / "flag-off/run"
    _write_completed_archive_run(flag_off_run)
    flag_off_result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=flag_off_run,
        environ={},
        created_at="2026-07-02T00:00:00Z",
    )

    no_refs_run = tmp_path / "no-safe-refs/run"
    _write_completed_archive_run(no_refs_run)
    no_refs_result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=no_refs_run,
        environ={FLAG: "1"},
        created_at="2026-07-02T00:00:00Z",
    )

    safe_refs_run = tmp_path / "safe-refs/run"
    _write_completed_archive_run(safe_refs_run)
    brief = _write_markdown(tmp_path / "safe-brief.md")
    enriched = _write_markdown(tmp_path / "safe-enriched.md")
    triage_read = _write_json(
        tmp_path / "safe-triage-read.json",
        "lolla.decision_work_automatic_triage_provisional_read.v0",
    )
    safe_refs_result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=safe_refs_run,
        environ={
            FLAG: "true",
            "LOLLA_DECISION_WORK_BRIEF_REF": str(brief),
            "LOLLA_DECISION_WORK_BRIEF_ENRICHED_REF": str(enriched),
            "LOLLA_DECISION_WORK_BRIEF_TRIAGE_READ_REF": str(triage_read),
        },
        created_at="2026-07-02T00:00:00Z",
    )

    partial_run = tmp_path / "brief-only/run"
    _write_completed_archive_run(partial_run)
    partial_brief = _write_markdown(tmp_path / "partial-brief.md")
    partial_result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=partial_run,
        environ={FLAG: "on", "LOLLA_DECISION_WORK_BRIEF_REF": str(partial_brief)},
        created_at="2026-07-02T00:00:00Z",
    )

    direct_run = tmp_path / "direct-runtime/run"
    _write_completed_archive_run(direct_run)
    direct_result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=direct_run,
        environ={
            FLAG: "yes",
            MODE_ENV: "future_direct_runtime_interpretation_not_allowed",
        },
        created_at="2026-07-02T00:00:00Z",
    )

    unsafe_run = tmp_path / "unsafe-ref/run"
    _write_completed_archive_run(unsafe_run)
    unsafe_ref = tmp_path / "unsafe.md"
    unsafe_ref.write_text("unsafe " + "raw_message" + "_content\n", encoding="utf-8")
    unsafe_result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=unsafe_run,
        environ={FLAG: "1", "LOLLA_DECISION_WORK_BRIEF_REF": str(unsafe_ref)},
        created_at="2026-07-02T00:00:00Z",
    )

    failed_run = tmp_path / "bundle-exception/run"
    _write_completed_archive_run(failed_run)

    def raise_bundle_error(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("bundle failed")

    with monkeypatch.context() as patch_context:
        patch_context.setattr(
            runtime_attachment,
            "build_decision_work_brief_runtime_bundle",
            raise_bundle_error,
        )
        failed_result = (
            runtime_attachment.run_post_archive_decision_work_brief_attachment(
                run_dir=failed_run,
                environ={FLAG: "1"},
                created_at="2026-07-02T00:00:00Z",
            )
        )

    actual_by_fixture = {
        "flag_off": _actual_fixture_summary(flag_off_run, flag_off_result),
        "flag_on_no_safe_refs": _actual_fixture_summary(no_refs_run, no_refs_result),
        "flag_on_safe_refs_available": _actual_fixture_summary(
            safe_refs_run,
            safe_refs_result,
        ),
        "flag_on_safe_brief_only_agent_or_caveated": _actual_fixture_summary(
            partial_run,
            partial_result,
        ),
        "direct_runtime_interpretation_blocked": _actual_fixture_summary(
            direct_run,
            direct_result,
        ),
        "unsafe_private_marker_blocked": _actual_fixture_summary(
            unsafe_run,
            unsafe_result,
        ),
        "bundle_exception_failed_closed": _actual_fixture_summary(
            failed_run,
            failed_result,
        ),
    }

    for fixture_name, actual in actual_by_fixture.items():
        expected = review_fixtures[fixture_name]
        assert actual["resolver_status"] == expected["resolver_status"]
        assert actual["attachment_status"] == expected["attachment_status"]
        assert actual["receipt_state"] == expected["receipt_state"]
        assert actual["sidecar_written"] is expected["sidecar_written"]
        assert actual["agent_handoff_written"] is expected["agent_handoff_written"]

    for run_dir in (
        no_refs_run,
        safe_refs_run,
        partial_run,
        direct_run,
        unsafe_run,
        failed_run,
    ):
        _assert_no_private_or_local_content(run_dir, tmp_path)


def test_review_blocks_direct_interpretation_and_privacy_marker_modes() -> None:
    fixtures = _fixture_reviews(_load_review())

    direct = fixtures["direct_runtime_interpretation_blocked"]
    unsafe = fixtures["unsafe_private_marker_blocked"]
    failed = fixtures["bundle_exception_failed_closed"]

    assert direct["resolver_status"] == "blocked_direct_runtime_interpretation"
    assert direct["attachment_status"] == "blocked"
    assert direct["model_calls"] == 0
    assert unsafe["resolver_status"] == "blocked_privacy_risk"
    assert unsafe["unsafe_content_copied"] is False
    assert failed["attachment_status"] == "failed_closed"
    assert failed["archive_completion_blocked"] is False


def test_review_decision_gate_and_non_claims() -> None:
    review = _load_review()
    rendered = json.dumps(review, sort_keys=True).lower()

    assert review["decision_gate"] in ALLOWED_DECISION_GATES
    assert review["decision_gate"] == "checked_in_safe_case_registry"
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


def test_pr174_review_artifacts_are_private_safe() -> None:
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


def test_pr174_docs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([REVIEW_DOC, REVIEW_JSON, PR173_DOC])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
