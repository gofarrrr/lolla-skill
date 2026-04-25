"""Command-construction tests for measurement scripts after Phase 6 cleanup."""

from __future__ import annotations

from pathlib import Path

import pytest

import scripts.phase2a_lane3_quality_check as phase2a
import scripts.phase2b_lane4_quality_check as phase2b
import scripts.phase2c_lane1_quality_check as phase2c
import scripts.phase2d_lane2_quality_check as phase2d


def _capture_phase2_command(
    monkeypatch: pytest.MonkeyPatch,
    module,
    tmp_path: Path,
    *,
    new_contract: bool,
) -> list[str]:
    captured: list[list[str]] = []

    def _fake_run_subprocess(cmd: list[str]) -> tuple[int, str, str]:
        captured.append(cmd)
        return 0, "", ""

    monkeypatch.setattr(module, "_run_subprocess", _fake_run_subprocess)
    error = module.run_pipeline_once(
        tmp_path / "extraction.json",
        tmp_path / "conversation.txt",
        tmp_path / "result.json",
        new_contract=new_contract,
        resume=False,
    )

    assert error is None
    assert len(captured) == 1
    return captured[0]


@pytest.mark.parametrize(
    ("module", "new_contract"),
    [
        (phase2a, False),
        (phase2a, True),
        (phase2b, False),
        (phase2b, True),
        (phase2c, False),
        (phase2c, True),
        (phase2d, False),
        (phase2d, True),
    ],
)
def test_phase2_scripts_build_conversation_contract_commands(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    module,
    new_contract: bool,
) -> None:
    cmd = _capture_phase2_command(
        monkeypatch,
        module,
        tmp_path,
        new_contract=new_contract,
    )

    assert "--conversation-file" in cmd
    assert not any(part.startswith("--legacy") for part in cmd)
    assert "--new-contract" not in cmd
