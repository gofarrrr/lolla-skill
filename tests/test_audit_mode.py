from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from engine.system_b.audit_mode import (
    AuditModeError,
    apply_risk_mode_metadata,
    audit_mode_from_env,
    normalize_audit_mode,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_RUN_SCRIPT = REPO_ROOT / "scripts" / "archive_run.py"
RUN_EXTRACT_SCRIPT = REPO_ROOT / "scripts" / "run_extract.py"
RUN_PIPELINE_SCRIPT = REPO_ROOT / "scripts" / "run_pipeline.py"
VALIDATE_SCRIPT = REPO_ROOT / "scripts" / "skill" / "validate_audit_mode.py"


def test_audit_mode_defaults_and_normalizes_env_values() -> None:
    assert normalize_audit_mode(None) == "standard"
    assert normalize_audit_mode("") == "standard"
    assert normalize_audit_mode("  HIGH_STAKES  ") == "high_stakes"
    assert audit_mode_from_env({}) == "standard"
    assert audit_mode_from_env({"LOLLA_AUDIT_MODE": "deep"}) == "deep"


def test_invalid_audit_mode_fails_with_clear_contract_message() -> None:
    with pytest.raises(AuditModeError) as excinfo:
        normalize_audit_mode("highstake")

    assert str(excinfo.value) == (
        "FATAL: invalid LOLLA_AUDIT_MODE 'highstake'. "
        "Expected one of: quick, standard, deep, high_stakes, stability."
    )


def test_validate_audit_mode_cli_fails_for_invalid_explicit_mode() -> None:
    env = dict(os.environ)
    env["LOLLA_AUDIT_MODE"] = "highstake"
    completed = subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT)],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    assert (
        "FATAL: invalid LOLLA_AUDIT_MODE 'highstake'. Expected one of: "
        "quick, standard, deep, high_stakes, stability."
    ) in completed.stderr
    assert completed.stdout == ""


def test_invalid_mode_stops_extract_before_model_client_initialization(tmp_path: Path) -> None:
    conversation_path = tmp_path / "conversation.txt"
    output_path = tmp_path / "extraction.json"
    conversation_path.write_text(
        "CONVERSATION: 1 turn, 1 user message, 1 assistant response\n\n"
        "[Turn 1] USER:\nShould we pivot?\n\n"
        "[Turn 1] ASSISTANT:\nPivot only after customer evidence.\n",
        encoding="utf-8",
    )
    env = dict(os.environ)
    env["LOLLA_AUDIT_MODE"] = "highstake"
    env.pop("OPENROUTER_API_KEY", None)
    env.pop("LOLLA_OPENROUTER_API_KEY", None)

    completed = subprocess.run(
        [
            sys.executable,
            str(RUN_EXTRACT_SCRIPT),
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
        ],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload == {
        "status": "error",
        "error": (
            "FATAL: invalid LOLLA_AUDIT_MODE 'highstake'. Expected one of: "
            "quick, standard, deep, high_stakes, stability."
        ),
    }
    assert "Failed to initialize OpenRouter client" not in completed.stdout


def test_invalid_mode_stops_pipeline_before_model_calls(tmp_path: Path) -> None:
    extraction_path = tmp_path / "extraction.json"
    conversation_path = tmp_path / "conversation.txt"
    result_path = tmp_path / "result.json"
    extraction_path.write_text("{}", encoding="utf-8")
    conversation_path.write_text("conversation", encoding="utf-8")
    env = dict(os.environ)
    env["LOLLA_AUDIT_MODE"] = "highstake"

    completed = subprocess.run(
        [
            sys.executable,
            str(RUN_PIPELINE_SCRIPT),
            "--extraction-file",
            str(extraction_path),
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(result_path),
        ],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["status"] == "error"
    assert payload["error"] == (
        "FATAL: invalid LOLLA_AUDIT_MODE 'highstake'. Expected one of: "
        "quick, standard, deep, high_stakes, stability."
    )
    assert not result_path.exists()


def test_audit_modes_are_metadata_only_at_result_layer() -> None:
    for mode in ("quick", "deep", "high_stakes", "stability"):
        payload: dict[str, object] = {"run_health": {"overall": "healthy"}}
        apply_risk_mode_metadata(payload, mode)

        assert payload == {
            "run_health": {"overall": "healthy"},
            "risk_mode": mode,
        }


def test_archive_propagates_high_stakes_risk_mode_to_artifacts(tmp_path: Path) -> None:
    run_id = "riskmode_123"
    tmp_dir = tmp_path / "tmp"
    archive_root = tmp_path / "archive"
    tmp_dir.mkdir()

    (tmp_dir / f"lolla_{run_id}_conversation.txt").write_text(
        "CONVERSATION: 1 turn, 1 user message, 1 assistant response\n\n"
        "[Turn 1] USER:\nShould we sign this enterprise contract?\n\n"
        "[Turn 1] ASSISTANT:\nSign only after legal review.\n",
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_extraction.json").write_text(
        json.dumps(
            {
                "status": "ok",
                "capture_health": "good",
                "extraction": {
                    "decision_situation": "Whether to sign an enterprise contract",
                    "turns": [
                        {"turn_index": 1, "speaker": "user", "text": "Should we sign?"},
                        {
                            "turn_index": 1,
                            "speaker": "assistant",
                            "text": "Sign only after legal review.",
                        },
                    ],
                    "reasoning_passages": ["Sign only after legal review."],
                },
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_result.json").write_text(
        json.dumps(
            {
                "status": "ok",
                "risk_mode": "high_stakes",
                "run_health": {
                    "overall": "healthy",
                    "product_output_health": "clean",
                    "live_output_health": "not_checked",
                    "issues": [],
                    "issue_details": [],
                },
                "v60_enrichment": {"status": "disabled"},
                "revised_answer": "Sign only after legal review.",
                "usage_summary": {"estimated_total_cost_usd": 0.01},
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_revised.txt").write_text(
        "Sign only after legal review.",
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_memo.md").write_text("# Memo\n", encoding="utf-8")

    spec = importlib.util.spec_from_file_location("archive_run", ARCHIVE_RUN_SCRIPT)
    assert spec and spec.loader
    archive_run = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(archive_run)

    archived = archive_run.archive_run(
        run_id,
        archive_root=archive_root,
        tmp_dir=tmp_dir,
    )

    run_dir = Path(archived["run_dir"])
    result = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
    agent_result = json.loads((run_dir / "agent_result.json").read_text(encoding="utf-8"))
    trace = json.loads((run_dir / "reasoning_trace.json").read_text(encoding="utf-8"))
    manifest = json.loads((Path(archived["case_dir"]) / ".case-manifest.json").read_text())

    assert archived["risk_mode"] == "high_stakes"
    assert result["risk_mode"] == "high_stakes"
    assert agent_result["risk_mode"] == "high_stakes"
    assert agent_result["caller_action"] == "ask_user_first"
    assert trace["process"]["risk_mode"] == "high_stakes"
    assert manifest["risk_modes_by_run"][run_id] == "high_stakes"
    assert (tmp_dir / f"lolla_{run_id}_agent_result.json").exists()
