from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from engine.system_b.agent_result import build_agent_result
from engine.system_b.control_plane import (
    CONTROL_INPUT_SCHEMA_VERSION,
    CONTROL_RESULT_SCHEMA_VERSION,
    build_control_result,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_RUN_PATH = REPO_ROOT / "scripts" / "archive_run.py"


def _load_archive_run_module():
    spec = importlib.util.spec_from_file_location("archive_run", ARCHIVE_RUN_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _seed_archived_run(run_dir: Path, *, control_input: dict | None = None) -> None:
    run_dir.mkdir(parents=True)
    _write_json(
        run_dir / "extraction.json",
        {
            "status": "ok",
            "capture_adequacy": {
                "schema_version": "lolla.capture_adequacy.v0",
                "status": "good",
                "capture_strategy": "full",
                "declared_turn_count": 2,
                "captured_turn_count": 2,
                "omitted_turn_count": 0,
                "captured_windows": [],
                "omitted_windows": [],
                "risk_flags": [],
                "notes": [],
            },
            "extraction": {"decision_situation": "Whether to send an email"},
        },
    )
    _write_json(
        run_dir / "result.json",
        {
            "run_health": {
                "overall": "healthy",
                "product_output_health": "clean",
                "live_output_health": "clean",
                "issues": [],
                "issue_details": [],
            },
            "revised_answer": "Send only after confirming the recipient.",
            "delta_card": {
                "findings": [
                    {
                        "severity": "medium",
                        "challenge_statement": "The answer did not name the external-send reversal condition.",
                    }
                ]
            },
        },
    )
    (run_dir / "revised.txt").write_text(
        "Send only after confirming the recipient.",
        encoding="utf-8",
    )
    (run_dir / "memo.md").write_text("# Memo\n", encoding="utf-8")
    if control_input is not None:
        _write_json(run_dir / "control_input.json", control_input)


def _seed_tmp_run(tmp_dir: Path, run_id: str, *, control_input: dict | None = None) -> None:
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / f"lolla_{run_id}_conversation.txt").write_text(
        "[Turn 1] USER:\nShould the agent send the email?\n",
        encoding="utf-8",
    )
    _write_json(
        tmp_dir / f"lolla_{run_id}_extraction.json",
        {"status": "ok", "extraction": {"decision_situation": "Whether to send an email"}},
    )
    _write_json(
        tmp_dir / f"lolla_{run_id}_result.json",
        {
            "run_health": {
                "overall": "healthy",
                "product_output_health": "clean",
                "live_output_health": "clean",
                "issues": [],
                "issue_details": [],
            },
            "v60_enrichment": {"status": "disabled"},
            "revised_answer": "Send only after confirming the recipient.",
        },
    )
    (tmp_dir / f"lolla_{run_id}_revised.txt").write_text(
        "Send only after confirming the recipient.",
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_memo.md").write_text("# Memo\n", encoding="utf-8")
    _write_json(
        tmp_dir / f"lolla_{run_id}_run_events.json",
        {"schema_version": "lolla.run_events.v0.1", "run_id": run_id, "events": []},
    )
    if control_input is not None:
        _write_json(tmp_dir / f"lolla_{run_id}_control_input.json", control_input)


def _control_input() -> dict:
    return {
        "schema_version": CONTROL_INPUT_SCHEMA_VERSION,
        "mode": "pre_action_reasoning_gate",
        "conversation": {
            "trace_id": "trace_123",
            "span_ids": ["span_a", "span_b"],
            "session_id": "session_456",
        },
        "agent": {
            "framework": "openai_agents_sdk",
            "run_id": "agent_run_789",
        },
        "proposed_action": {
            "tool_name": "send_email",
            "arguments": {
                "to": "customer@example.com",
                "subject": "Account closure",
            },
            "risk_class": "external_side_effect",
        },
        "control_context": {
            "approval_id": "approval_001",
            "policy_engine": "crabtrap",
            "policy_decision": "needs_review",
            "sandbox_id": "sandbox_abc",
            "credential_scope": "gmail.send",
            "tool_call_ids": ["tool_call_1"],
        },
    }


def test_agent_result_summarizes_control_input_without_argument_values(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "run"
    _seed_archived_run(run_dir, control_input=_control_input())

    payload = build_agent_result(run_dir, run_id="run-control", case_id="case-control")

    control = payload["control_context"]
    assert control["schema_version"] == CONTROL_INPUT_SCHEMA_VERSION
    assert control["status"] == "valid"
    assert control["control_mode"] == "pre_action_reasoning_gate"
    assert control["external_trace_id"] == "trace_123"
    assert control["external_span_ids"] == ["span_a", "span_b"]
    assert control["agent_run_id"] == "agent_run_789"
    assert control["agent_framework"] == "openai_agents_sdk"
    assert control["tool_call_ids"] == ["tool_call_1"]
    assert control["approval_id"] == "approval_001"
    assert control["policy_engine"] == "crabtrap"
    assert control["policy_decision"] == "needs_review"
    assert control["sandbox_id"] == "sandbox_abc"
    assert control["credential_scope"] == "gmail.send"
    assert control["proposed_action"] == {
        "tool_name": "send_email",
        "risk_class": "external_side_effect",
        "has_arguments": True,
        "argument_keys": ["subject", "to"],
    }
    serialized = json.dumps(payload)
    assert "customer@example.com" not in serialized
    assert "Account closure" not in serialized


def test_control_result_wraps_agent_result_without_approving_action(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    _seed_archived_run(run_dir, control_input=_control_input())
    from engine.system_b.agent_result import write_agent_result

    write_agent_result(run_dir, run_id="run-control", case_id="case-control")

    payload = build_control_result(run_dir, run_id="run-control", case_id="case-control")

    assert payload["schema_version"] == CONTROL_RESULT_SCHEMA_VERSION
    assert payload["control_mode"] == "pre_action_reasoning_gate"
    assert payload["caller_action"] == "use_revised_answer"
    assert payload["approval_outcome"] == "proceed_with_external_policy"
    assert payload["boundary"] == {
        "lolla_approves_actions": False,
        "lolla_replaces_policy_engine": False,
        "lolla_replaces_sandbox": False,
        "lolla_replaces_identity_scope": False,
    }


def test_archive_run_preserves_control_input_and_generates_control_result(
    tmp_path: Path,
) -> None:
    archive_run = _load_archive_run_module()
    run_id = "controlrun"
    tmp_dir = tmp_path / "tmp"
    archive_root = tmp_path / "archive"
    _seed_tmp_run(tmp_dir, run_id, control_input=_control_input())

    archived = archive_run.archive_run(run_id, archive_root=archive_root, tmp_dir=tmp_dir)
    run_dir = Path(archived["run_dir"])

    assert (run_dir / "control_input.json").is_file()
    assert (run_dir / "control_result.json").is_file()
    assert (tmp_dir / f"lolla_{run_id}_control_result.json").is_file()

    agent_result = json.loads((run_dir / "agent_result.json").read_text(encoding="utf-8"))
    control_result = json.loads((run_dir / "control_result.json").read_text(encoding="utf-8"))
    trace = json.loads((run_dir / "reasoning_trace.json").read_text(encoding="utf-8"))

    assert agent_result["control_context"]["external_trace_id"] == "trace_123"
    assert control_result["schema_version"] == CONTROL_RESULT_SCHEMA_VERSION
    assert control_result["control_input"]["approval_id"] == "approval_001"
    artifact_roles = {item["path"]: item["role"] for item in trace["artifacts"]}
    assert artifact_roles["control_input.json"] == "control_plane_input"
    assert artifact_roles["control_result.json"] == "control_plane_result"
    assert trace["process"]["control_plane"]["external_trace_id"] == "trace_123"


def test_archive_run_ordinary_flow_does_not_generate_control_result(
    tmp_path: Path,
) -> None:
    archive_run = _load_archive_run_module()
    run_id = "ordinaryrun"
    tmp_dir = tmp_path / "tmp"
    archive_root = tmp_path / "archive"
    _seed_tmp_run(tmp_dir, run_id)

    archived = archive_run.archive_run(run_id, archive_root=archive_root, tmp_dir=tmp_dir)
    run_dir = Path(archived["run_dir"])

    agent_result = json.loads((run_dir / "agent_result.json").read_text(encoding="utf-8"))
    trace = json.loads((run_dir / "reasoning_trace.json").read_text(encoding="utf-8"))

    assert "control_context" not in agent_result
    assert "control_plane" not in trace["process"]
    assert not (run_dir / "control_result.json").exists()
    assert not (tmp_dir / f"lolla_{run_id}_control_result.json").exists()
