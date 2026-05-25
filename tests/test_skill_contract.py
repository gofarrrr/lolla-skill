from __future__ import annotations

from pathlib import Path


def test_skill_rests_post_step6_pressure_checks_by_default() -> None:
    skill = Path("SKILL.md").read_text(encoding="utf-8")

    assert "--pre-step6-portfolio step6_private" in skill
    assert "--pre-step6-portfolio-cache-dir" in skill
    assert "--pre-step6-portfolio-cache-ref" in skill
    assert "LOLLA_PRE_STEP6_PORTFOLIO_CACHE_DIR" in skill
    assert "LOLLA_PRE_STEP6_PORTFOLIO_CACHE_REF" in skill
    assert "LOLLA_PRE_STEP6_REQUIRE_CACHE_HIT" in skill
    assert "Pre-Step-6 private table receipt:" in skill
    assert "operator cache ref:" in skill
    assert "expected cache file:" in skill
    assert "/tmp/lolla_${LOLLA_RUN_ID}_pre_step6_private_table.md" in skill
    assert "pre_step6_private_table_ledger" in skill
    assert '"schema_version": "pre_step6_private_table_ledger.v1"' in skill
    assert "LOLLA_ENV_STATE" in skill
    assert ". /tmp/lolla_latest_env.sh" in skill
    assert "exit 1" in skill
    assert "Copy the provided `source_id` values exactly" in skill
    assert "--require-valid" in skill
    assert "finalize_pre_step6_private_table_ledger.py" in skill
    assert '"source_id": "<copy exact source_id from the skeleton>"' in skill
    assert '"source_id": "lane1_structural_challenge"' not in skill
    assert "Launch these BEFORE writing Step 6" not in skill
    assert "Before you begin writing your reconsideration, launch" not in skill
    assert "Post-Step-6 pressure-check sub-agents are rested by default" in skill
    assert "LOLLA_STEP7_PRESSURE_CHECK=on" in skill
    assert '"status": "not_run_default_off"' in skill
    assert '"reason": "post_step6_pressure_check_default_off"' in skill
    assert "Default-off runs do not write" in skill
    assert "only AFTER Step 6b finalization succeeds" in skill
    assert (
        'finalize_v60_telemetry.py --run-id "${LOLLA_RUN_ID}" --quiet --require-valid || exit $?'
        in skill
    )
    assert (
        'finalize_pre_step6_private_table_ledger.py --run-id "${LOLLA_RUN_ID}" --quiet --require-valid || exit $?'
        in skill
    )


def test_skill_requires_live_transcript_artifact_and_gate_before_archive() -> None:
    skill = Path("SKILL.md").read_text(encoding="utf-8")

    assert "/tmp/lolla_${LOLLA_RUN_ID}_live_transcript.txt" in skill
    assert "append every user-visible" in skill
    assert "finalize_live_output_hygiene.py" in skill
    assert "--require-live-output-clean" in skill
    assert "--trusted-transcript" in skill
    assert "manual transcript" in skill
    assert "live_output_health: not_checked" in skill
    assert "before archive" in skill.lower()
