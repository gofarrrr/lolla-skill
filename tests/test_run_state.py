from __future__ import annotations

import datetime as dt

import pytest

from engine.system_b.run_state import (
    assert_expected_run_state,
    infer_run_id_from_lolla_path,
    make_run_id,
    validate_expected_run_state,
)


def test_make_run_id_adds_random_suffix_to_timestamp() -> None:
    run_id = make_run_id(
        now=dt.datetime(2026, 6, 23, 11, 32, 3, tzinfo=dt.timezone.utc),
        suffix_bytes=3,
    )

    assert run_id.startswith("20260623T113203Z_")
    assert len(run_id.split("_", 1)[1]) == 6


def test_infer_run_id_from_lolla_path_preserves_underscore_suffixes() -> None:
    assert (
        infer_run_id_from_lolla_path(
            "/tmp/lolla_20260623T113203Z_c4df83_result.json"
        )
        == "20260623T113203Z_c4df83"
    )
    assert (
        infer_run_id_from_lolla_path(
            "/tmp/lolla_20260623T113203Z_c4df83_live_transcript.txt"
        )
        == "20260623T113203Z_c4df83"
    )
    assert (
        infer_run_id_from_lolla_path(
            "/tmp/lolla_20260623T113203Z_c4df83_operator.log"
        )
        == "20260623T113203Z_c4df83"
    )
    assert (
        infer_run_id_from_lolla_path(
            "/tmp/lolla_20260623T113203Z_c4df83_pre_step6_private_table_ledger.json"
        )
        == "20260623T113203Z_c4df83"
    )


def test_expected_run_state_rejects_stale_active_run() -> None:
    errors = validate_expected_run_state(
        expected_run_id="20260623T113203Z_c4df83",
        actual_run_id="20260623T112550Z",
        artifact_paths=["/tmp/lolla_20260623T113203Z_c4df83_result.json"],
        phase="pipeline",
    )

    assert any("run state mismatch" in error for error in errors)


def test_expected_run_state_rejects_cross_run_artifact_path() -> None:
    errors = validate_expected_run_state(
        expected_run_id="20260623T113203Z_c4df83",
        actual_run_id="20260623T113203Z_c4df83",
        artifact_paths=["/tmp/lolla_20260623T112550Z_result.json"],
        phase="archive",
    )

    assert any("belongs to run '20260623T112550Z'" in error for error in errors)


def test_assert_expected_run_state_raises_system_exit_on_mismatch() -> None:
    with pytest.raises(SystemExit):
        assert_expected_run_state(
            expected_run_id="expected",
            actual_run_id="actual",
            phase="test",
        )
