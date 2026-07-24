from __future__ import annotations

import os
import subprocess
from pathlib import Path


def _env_for(run_id: str, tmp_path: Path) -> dict[str, str]:
    state = tmp_path / f"{run_id}_env.sh"
    state.write_text(
        "\n".join(
            [
                f'export SKILL_DIR="{Path.cwd()}"',
                f'export LOLLA_RUN_ID="{run_id}"',
                f'export LOLLA_EXPECTED_RUN_ID="{run_id}"',
                'export LOLLA_TMP_DIR="/tmp"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["LOLLA_ENV_STATE"] = str(state)
    return env


def test_run_extract_step_accepts_exact_current_conversation_path_as_noop(
    tmp_path: Path,
) -> None:
    run_id = f"argtol_extract_{os.getpid()}"
    expected_conversation = Path(f"/tmp/lolla_{run_id}_conversation.txt")
    expected_conversation.unlink(missing_ok=True)

    completed = subprocess.run(
        [
            "bash",
            "scripts/skill/run_extract_step.sh",
            str(expected_conversation),
        ],
        cwd=Path.cwd(),
        env=_env_for(run_id, tmp_path),
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "conversation file missing or empty" in completed.stderr
    assert "unknown argument" not in completed.stderr


def test_run_extract_step_rejects_wrong_positional_conversation_path(
    tmp_path: Path,
) -> None:
    run_id = f"argtol_extract_wrong_{os.getpid()}"

    completed = subprocess.run(
        [
            "bash",
            "scripts/skill/run_extract_step.sh",
            "/tmp/lolla_other_conversation.txt",
        ],
        cwd=Path.cwd(),
        env=_env_for(run_id, tmp_path),
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 2
    assert "unexpected --conversation-file" in completed.stderr


def test_run_pipeline_step_accepts_exact_current_paths_as_noops(
    tmp_path: Path,
) -> None:
    run_id = f"argtol_pipeline_{os.getpid()}"
    expected_extraction = Path(f"/tmp/lolla_{run_id}_extraction.json")
    expected_conversation = Path(f"/tmp/lolla_{run_id}_conversation.txt")
    expected_result = Path(f"/tmp/lolla_{run_id}_result.json")
    for path in (expected_extraction, expected_conversation, expected_result):
        path.unlink(missing_ok=True)

    completed = subprocess.run(
        [
            "bash",
            "scripts/skill/run_pipeline_step.sh",
            str(expected_extraction),
            str(expected_conversation),
            str(expected_result),
        ],
        cwd=Path.cwd(),
        env=_env_for(run_id, tmp_path),
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "extraction JSON missing or empty" in completed.stderr
    assert "unknown argument" not in completed.stderr
