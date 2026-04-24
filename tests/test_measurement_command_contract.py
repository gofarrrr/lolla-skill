"""Command-construction tests for old/new runtime measurement scripts."""

from __future__ import annotations

from pathlib import Path

import pytest

import scripts.phase2a_lane3_quality_check as phase2a
import scripts.phase2b_lane4_quality_check as phase2b
import scripts.phase2c_lane1_quality_check as phase2c
import scripts.phase2d_lane2_quality_check as phase2d


def _capture_phase2_command(monkeypatch: pytest.MonkeyPatch, module, tmp_path: Path, *, new_contract: bool) -> list[str]:
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


def test_phase2a_old_path_uses_explicit_legacy_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cmd = _capture_phase2_command(monkeypatch, phase2a, tmp_path, new_contract=False)

    assert "--legacy-contract" in cmd
    assert "--new-contract" not in cmd


def test_phase2a_new_path_uses_default_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cmd = _capture_phase2_command(monkeypatch, phase2a, tmp_path, new_contract=True)

    assert "--legacy-contract" not in cmd
    assert "--new-contract" not in cmd


def test_phase2b_old_path_uses_explicit_legacy_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cmd = _capture_phase2_command(monkeypatch, phase2b, tmp_path, new_contract=False)

    assert "--legacy-contract" in cmd
    assert "--new-contract" not in cmd


def test_phase2b_new_path_uses_default_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cmd = _capture_phase2_command(monkeypatch, phase2b, tmp_path, new_contract=True)

    assert "--legacy-contract" not in cmd
    assert "--new-contract" not in cmd


def test_phase2c_old_path_uses_explicit_legacy_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cmd = _capture_phase2_command(monkeypatch, phase2c, tmp_path, new_contract=False)

    assert "--legacy-contract" in cmd
    assert "--new-contract" not in cmd


def test_phase2c_new_path_uses_default_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cmd = _capture_phase2_command(monkeypatch, phase2c, tmp_path, new_contract=True)

    assert "--legacy-contract" not in cmd
    assert "--new-contract" not in cmd


def test_phase2d_old_path_uses_explicit_legacy_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cmd = _capture_phase2_command(monkeypatch, phase2d, tmp_path, new_contract=False)

    assert "--legacy-contract" in cmd
    assert "--new-contract" not in cmd


def test_phase2d_new_path_uses_default_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cmd = _capture_phase2_command(monkeypatch, phase2d, tmp_path, new_contract=True)

    assert "--legacy-contract" not in cmd
    assert "--new-contract" not in cmd
