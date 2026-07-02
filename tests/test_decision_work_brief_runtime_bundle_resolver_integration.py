from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_brief_agent_handoff import (
    build_decision_work_brief_agent_handoff,
)
from engine.system_b.decision_work_brief_runtime_bundle import (
    build_decision_work_brief_runtime_bundle,
)
from engine.system_b.decision_work_brief_safe_supply_resolver import (
    resolve_decision_work_brief_safe_supply,
    write_resolver_json,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/evals/build_decision_work_brief_runtime_bundle.py"
RESOLVER_CONTRACT = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-safe-supply-resolver-contract-v0.json"
)
PR172_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-bundle-resolver-integration-v0.md"
)
PR162_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-bundle-generator-v0.md"
)
PR171_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-runtime-safe-supply-resolver-v0.md"
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
REQUIRED_FALSE_FLAGS = {
    "human_validated",
    "human_review_completed",
    "product_proof",
    "runtime_invoked",
    "runtime_behavior_changed",
    "skill_invoked",
    "archive_mutated",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "raw_private_content_included",
    "provider_text_included",
    "local_absolute_paths_included",
}


def _write_completed_run(run_dir: Path) -> None:
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
        "Safe fixture revised answer placeholder.",
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


def _resolver_output(
    tmp_path: Path,
    run_dir: Path,
    *,
    mode: str = "manual_ref_supply_only",
    brief_markdown_path: Path | None = None,
    enriched_brief_path: Path | None = None,
    triage_packet_path: Path | None = None,
    triage_read_path: Path | None = None,
) -> Path:
    result = resolve_decision_work_brief_safe_supply(
        run_dir=run_dir,
        contract_path=RESOLVER_CONTRACT,
        mode=mode,
        brief_markdown_path=brief_markdown_path,
        enriched_brief_path=enriched_brief_path,
        triage_packet_path=triage_packet_path,
        triage_read_path=triage_read_path,
        created_at="2026-07-02T00:00:00Z",
    )
    out = tmp_path / f"resolver-{mode}.json"
    write_resolver_json(out, result, pretty=True)
    return out


def _build_with_resolver(
    tmp_path: Path,
    resolver_output: Path,
    *,
    run_dir: Path,
) -> dict[str, Any]:
    return build_decision_work_brief_runtime_bundle(
        run_dir=run_dir,
        output_dir=tmp_path / "bundle-output",
        resolver_output_path=resolver_output,
        created_at="2026-07-02T00:00:00Z",
    )


def _receipt(output_dir: Path) -> str:
    return (output_dir / "decision_work/user_receipt.md").read_text(encoding="utf-8")


def _rendered_bundle_text(output_dir: Path, status: dict[str, Any]) -> str:
    parts = [
        json.dumps(status, sort_keys=True),
        _receipt(output_dir),
    ]
    handoff = build_decision_work_brief_agent_handoff(
        source_run_ref=status["source_run_ref"],
        attachment_status=status,
        created_at="2026-07-02T00:00:00Z",
    )
    parts.append(json.dumps(handoff, sort_keys=True))
    return "\n".join(parts)


def test_resolved_resolver_output_feeds_available_bundle(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    output_dir = tmp_path / "bundle-output"
    _write_completed_run(run_dir)
    brief = _write_markdown(tmp_path / "brief.md")
    enriched = _write_markdown(tmp_path / "enriched.md")
    triage_packet = _write_json(
        tmp_path / "triage-packet.json",
        "lolla.decision_work_automatic_triage_packets.v0",
    )
    triage_read = _write_json(
        tmp_path / "triage-read.json",
        "lolla.decision_work_automatic_triage_provisional_read.v0",
    )
    resolver = _resolver_output(
        tmp_path,
        run_dir,
        brief_markdown_path=brief,
        enriched_brief_path=enriched,
        triage_packet_path=triage_packet,
        triage_read_path=triage_read,
    )

    status = build_decision_work_brief_runtime_bundle(
        run_dir=run_dir,
        output_dir=output_dir,
        resolver_output_path=resolver,
        created_at="2026-07-02T00:00:00Z",
    )

    assert status["attachment_state"] == "generated"
    assert status["resolver_summary"]["resolver_status"] == "resolved"
    assert status["resolver_summary"]["feeds_runtime_bundle"] is True
    assert status["generated_artifacts"]["safe_supply_resolver"] == (
        "decision_work/safe_supply_resolver.json"
    )
    assert status["generated_artifacts"]["automatic_triage_packet"] == (
        "decision_work/automatic_triage_packet.json"
    )
    assert "Decision Work Brief: available" in _receipt(output_dir)
    assert "not proof that the advice is correct" in _receipt(output_dir)


def test_partially_resolved_resolver_output_feeds_agent_only_bundle(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "runs/case/run"
    output_dir = tmp_path / "bundle-output"
    _write_completed_run(run_dir)
    resolver = _resolver_output(
        tmp_path,
        run_dir,
        brief_markdown_path=_write_markdown(tmp_path / "brief.md"),
    )

    status = build_decision_work_brief_runtime_bundle(
        run_dir=run_dir,
        output_dir=output_dir,
        resolver_output_path=resolver,
        created_at="2026-07-02T00:00:00Z",
    )

    assert status["attachment_state"] == "generated_agent_only"
    assert status["resolver_summary"]["resolver_status"] == "partially_resolved"
    assert "runtime_specific_triage_read_not_supplied" in status["deferred_reasons"]
    assert "Decision Work Brief: available for agent inspection" in _receipt(output_dir)


def test_no_safe_inputs_resolver_output_defers_without_fake_brief(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    output_dir = tmp_path / "bundle-output"
    _write_completed_run(run_dir)
    resolver = _resolver_output(tmp_path, run_dir)

    status = build_decision_work_brief_runtime_bundle(
        run_dir=run_dir,
        output_dir=output_dir,
        resolver_output_path=resolver,
        created_at="2026-07-02T00:00:00Z",
    )

    assert status["attachment_state"] == "deferred"
    assert status["resolver_summary"]["resolver_status"] == "no_safe_inputs"
    assert "decision_work_brief_markdown" not in status["generated_artifacts"]
    assert "Decision Work Brief: deferred" in _receipt(output_dir)


def test_queued_and_local_private_resolver_outputs_defer_safely(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)

    queued_status = _build_with_resolver(
        tmp_path / "queued",
        _resolver_output(
            tmp_path / "queued",
            run_dir,
            mode="offline_interpretation_queue",
        ),
        run_dir=run_dir,
    )
    local_private_status = _build_with_resolver(
        tmp_path / "local-private",
        _resolver_output(
            tmp_path / "local-private",
            run_dir,
            mode="local_private_operator_mode",
        ),
        run_dir=run_dir,
    )

    assert queued_status["attachment_state"] == "deferred"
    assert queued_status["resolver_summary"]["resolver_status"] == (
        "queued_for_offline_interpretation"
    )
    assert queued_status["resolver_summary"]["queue_handoff"]["queued"] is True
    assert local_private_status["attachment_state"] == "deferred"
    assert local_private_status["resolver_summary"]["resolver_status"] == (
        "local_private_operator_required"
    )


def test_blocked_direct_runtime_interpretation_resolver_output_blocks(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "runs/case/run"
    output_dir = tmp_path / "bundle-output"
    _write_completed_run(run_dir)
    resolver = _resolver_output(
        tmp_path,
        run_dir,
        mode="future_direct_runtime_interpretation_not_allowed",
    )

    status = build_decision_work_brief_runtime_bundle(
        run_dir=run_dir,
        output_dir=output_dir,
        resolver_output_path=resolver,
        created_at="2026-07-02T00:00:00Z",
    )

    assert status["attachment_state"] == "blocked"
    assert status["resolver_summary"]["resolver_status"] == (
        "blocked_direct_runtime_interpretation"
    )
    assert "resolver:blocked_direct_runtime_interpretation" in status["blocked_reasons"]
    assert "Decision Work Brief: blocked" in _receipt(output_dir)


def test_invalid_resolver_schema_blocks_fail_closed(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)
    resolver = tmp_path / "bad-resolver.json"
    resolver.write_text(
        json.dumps({"schema_version": "wrong.schema.v0", "resolver_status": "resolved"}),
        encoding="utf-8",
    )

    status = _build_with_resolver(tmp_path, resolver, run_dir=run_dir)

    assert status["attachment_state"] == "blocked"
    assert status["resolver_summary"]["resolver_status"] == "blocked_schema_invalid"
    assert "resolver:blocked_schema_invalid" in status["blocked_reasons"]


def test_privacy_marker_in_resolver_output_blocks_fail_closed(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)
    resolver = json.loads(_resolver_output(tmp_path, run_dir).read_text(encoding="utf-8"))
    resolver["debug_note"] = "unsafe " + "raw_message" + "_content"
    resolver_path = tmp_path / "unsafe-resolver.json"
    resolver_path.write_text(json.dumps(resolver), encoding="utf-8")

    status = _build_with_resolver(tmp_path, resolver_path, run_dir=run_dir)

    assert status["attachment_state"] == "blocked"
    assert status["resolver_summary"]["resolver_status"] == "blocked_privacy_risk"
    assert "resolver:blocked_privacy_risk" in status["blocked_reasons"]


def test_cli_accepts_resolver_output_and_preserves_manual_ref_flags(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "runs/case/run"
    output_dir = tmp_path / "bundle-output"
    _write_completed_run(run_dir)
    resolver = _resolver_output(
        tmp_path,
        run_dir,
        brief_markdown_path=_write_markdown(tmp_path / "brief.md"),
        triage_read_path=_write_json(
            tmp_path / "triage-read.json",
            "lolla.decision_work_automatic_triage_provisional_read.v0",
        ),
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--run-dir",
            str(run_dir),
            "--out",
            str(output_dir),
            "--resolver-output",
            str(resolver),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["attachment_state"] == "generated"
    assert payload["resolver_summary"]["resolver_status"] == "resolved"


def test_resolver_summary_feeds_agent_handoff_without_action_authorization(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "runs/case/run"
    output_dir = tmp_path / "bundle-output"
    _write_completed_run(run_dir)
    resolver = _resolver_output(
        tmp_path,
        run_dir,
        brief_markdown_path=_write_markdown(tmp_path / "brief.md"),
    )
    status = build_decision_work_brief_runtime_bundle(
        run_dir=run_dir,
        output_dir=output_dir,
        resolver_output_path=resolver,
        created_at="2026-07-02T00:00:00Z",
    )

    handoff = build_decision_work_brief_agent_handoff(
        source_run_ref=status["source_run_ref"],
        attachment_status=status,
        created_at="2026-07-02T00:00:00Z",
    )

    assert handoff["safe_supply_resolver"]["resolver_status"] == "partially_resolved"
    assert handoff["safe_supply_resolver"]["resolved_inputs"] == [
        "completed_run_dir_ref",
        "source_refs",
        "rendered_brief_markdown_ref",
    ]
    assert handoff["safe_supply_resolver"]["agent_action_authorized"] is False


def test_resolver_aware_bundle_outputs_are_private_safe(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    output_dir = tmp_path / "bundle-output"
    _write_completed_run(run_dir)
    resolver = _resolver_output(
        tmp_path,
        run_dir,
        brief_markdown_path=_write_markdown(tmp_path / "brief.md"),
        triage_read_path=_write_json(
            tmp_path / "triage-read.json",
            "lolla.decision_work_automatic_triage_provisional_read.v0",
        ),
    )

    status = build_decision_work_brief_runtime_bundle(
        run_dir=run_dir,
        output_dir=output_dir,
        resolver_output_path=resolver,
        created_at="2026-07-02T00:00:00Z",
    )
    rendered = _rendered_bundle_text(output_dir, status)

    for field in REQUIRED_FALSE_FLAGS:
        assert status["custody_flags"][field] is False
    assert status["custody_flags"]["model_calls"] == 0
    assert "not_agent_action_authorization" in status["non_claims"]
    assert str(tmp_path) not in rendered
    for marker in PRIVACY_MARKERS:
        assert marker not in rendered


def test_pr172_docs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([PR172_DOC, PR162_DOC, PR171_DOC])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
