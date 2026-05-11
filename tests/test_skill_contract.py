from __future__ import annotations

from pathlib import Path


def test_skill_does_not_launch_pressure_checks_before_v60_ledger_gate() -> None:
    skill = Path("SKILL.md").read_text(encoding="utf-8")

    assert "--require-valid" in skill
    assert "Launch these BEFORE writing Step 6" not in skill
    assert "Before you begin writing your reconsideration, launch" not in skill
    assert "Launch Step 7 only after" in skill
    assert "before starting any pressure-check agent" in skill
    assert (
        'finalize_v60_telemetry.py --run-id "${LOLLA_RUN_ID}" --quiet --require-valid || exit $?'
        in skill
    )
