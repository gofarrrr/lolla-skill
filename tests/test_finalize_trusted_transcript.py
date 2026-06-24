from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess
from pathlib import Path


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_finalize_and_archive_accepts_trusted_live_transcript(tmp_path: Path) -> None:
    run_id = f"trustedlive_{os.getpid()}"
    repo = Path.cwd()
    archive_root = tmp_path / "archive"
    trusted_transcript = tmp_path / "complete-live-session.txt"
    env_state = tmp_path / "env.sh"
    tmp = Path("/tmp")

    (tmp / f"lolla_{run_id}_conversation.txt").write_text(
        "CONVERSATION: 1 turn, 1 user message, 1 assistant response\n\n"
        "[Turn 1] USER:\nShould we preserve a trusted live transcript?\n\n"
        "[Turn 1] ASSISTANT:\nYes, preserve the clean visible transcript.\n",
        encoding="utf-8",
    )
    _write_json(
        tmp / f"lolla_{run_id}_extraction.json",
        {
            "status": "ok",
            "extraction": {
                "decision_situation": "Whether trusted live transcripts archive cleanly",
                "live_constraints": [],
                "reasoning_passages": ["preserve the clean visible transcript"],
                "original_framing": "Should we preserve a trusted live transcript?",
                "synthesized_position": "Preserve the trusted transcript.",
                "dropped_threads": [],
                "turns": [],
            },
        },
    )
    _write_json(
        tmp / f"lolla_{run_id}_result.json",
        {
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
            "pre_step6_private_table": {"status": "not_run"},
            "v60_enrichment": {"status": "disabled"},
            "audit_summary": {"boundary_call_count": 0, "boundary_calls": [], "warnings": []},
            "companion_cheat_sheet": {"anchors": [], "anti_echo_model_ids": []},
            "usage_summary": {
                "run_id": run_id,
                "pricing_table_version": "synthetic",
                "estimated_total_cost_usd": 0,
                "cost_estimate_state": "complete",
                "vendors": {},
            },
        },
    )
    _write_json(
        tmp / f"lolla_{run_id}_run_events.json",
        {
            "schema_version": "lolla.run_events.v0.1",
            "run_id": run_id,
            "events": [],
        },
    )
    (tmp / f"lolla_{run_id}_operator.log").write_text(
        "[synthetic] operator log initialized\n",
        encoding="utf-8",
    )
    trusted_transcript.write_text(
        "I have the counterargument; I am folding it into the revised answer now.\n",
        encoding="utf-8",
    )
    (tmp / f"lolla_{run_id}_live_transcript.txt").write_text(
        "manual placeholder that should be replaced by the trusted transcript\n",
        encoding="utf-8",
    )
    env_state.write_text(
        "\n".join(
            [
                f"export SKILL_DIR={shlex.quote(str(repo))}",
                f"export LOLLA_RUN_ID={shlex.quote(run_id)}",
                f"export LOLLA_EXPECTED_RUN_ID={shlex.quote(run_id)}",
                f"export LOLLA_LIVE_TRANSCRIPT={shlex.quote(str(tmp / f'lolla_{run_id}_live_transcript.txt'))}",
                f"export LOLLA_OPERATOR_LOG={shlex.quote(str(tmp / f'lolla_{run_id}_operator.log'))}",
                f"export LOLLA_ENV_STATE={shlex.quote(str(env_state))}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["LOLLA_ENV_STATE"] = str(env_state)
    env["LOLLA_ARCHIVE_DIR"] = str(archive_root)
    completed = subprocess.run(
        [
            "bash",
            "scripts/skill/finalize_and_archive.sh",
            "--run-id",
            run_id,
            "--skip-observatory",
            "--trusted-transcript",
            str(trusted_transcript),
            "--require-live-output-clean",
        ],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "USER_RECEIPT_BEGIN" in completed.stdout
    assert "USER_RECEIPT_END" in completed.stdout
    assert "Archived run " not in completed.stdout

    run_dirs = sorted(archive_root.glob(f"*/{run_id}"))
    assert len(run_dirs) == 1
    run_dir = run_dirs[0]
    archived_result = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
    archived_transcript = (run_dir / "live_transcript.txt").read_text(encoding="utf-8")
    trace = json.loads((run_dir / "reasoning_trace.json").read_text(encoding="utf-8"))
    trace_by_path = {item["path"]: item for item in trace["artifacts"]}

    assert archived_result["run_health"]["live_output_health"] == "clean"
    assert archived_result["live_output_hygiene"]["capture_mode"] == "trusted"
    assert "I have the counterargument" in archived_transcript
    assert "Observatory was not launched." in archived_transcript
    assert "manual placeholder" not in archived_transcript
    assert trace_by_path["live_transcript.txt"]["sha256"] == (
        "sha256:" + hashlib.sha256(archived_transcript.encode("utf-8")).hexdigest()
    )
