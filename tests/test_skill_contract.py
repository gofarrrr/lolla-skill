from __future__ import annotations

import re
from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_skill_rests_post_step6_pressure_checks_by_default() -> None:
    skill = _read("SKILL.md")
    steps = _read("docs/skill/STEPS.md")
    setup = _read("scripts/skill/setup.sh")
    run_extract_helper = _read("scripts/skill/run_extract_step.sh")
    run_pipeline_helper = _read("scripts/skill/run_pipeline_step.sh")
    capture_validator = _read("scripts/skill/validate_conversation_capture.py")
    pressure_helper = _read("scripts/skill/persist_default_off_pressure_check.py")
    memo_helper = _read("scripts/skill/render_memo_step.sh")
    finalizer_helper = _read("scripts/skill/finalize_and_archive.sh")
    contract = "\n".join(
        [
            skill,
            steps,
            setup,
            run_extract_helper,
            run_pipeline_helper,
            capture_validator,
            pressure_helper,
            memo_helper,
            finalizer_helper,
        ]
    )

    assert "--pre-step6-portfolio step6_private" in contract
    assert "--pre-step6-portfolio-cache-dir" in contract
    assert "--pre-step6-portfolio-cache-ref" in contract
    assert "LOLLA_PRE_STEP6_PORTFOLIO_CACHE_DIR" in contract
    assert "LOLLA_PRE_STEP6_PORTFOLIO_CACHE_REF" in contract
    assert "LOLLA_PRE_STEP6_REQUIRE_CACHE_HIT" in contract
    assert "Pre-Step-6 private table receipt:" in contract
    assert "operator cache ref:" in contract
    assert "expected cache file:" in contract
    assert "/tmp/lolla_${LOLLA_RUN_ID}_pre_step6_private_table.md" in contract
    assert "pre_step6_private_table_ledger" in contract
    assert '"schema_version": "pre_step6_private_table_ledger.v1"' in contract

    assert "Post-Step-6 pressure-check sub-agents are rested by default" in contract
    assert "LOLLA_STEP7_PRESSURE_CHECK=on" in contract
    assert '"status": "not_run_default_off"' in contract
    assert '"reason": "post_step6_pressure_check_default_off"' in contract
    assert "Default-off runs do not write" in contract
    assert "only AFTER Step 6b finalization succeeds" in contract

    assert "Copy the provided `source_id` values exactly" in contract
    assert "--require-valid" in contract
    assert "finalize_pre_step6_private_table_ledger.py" in contract
    assert '"source_id": "<copy exact source_id from the skeleton>"' in contract
    assert '"source_id": "lane1_structural_challenge"' not in contract
    assert "Launch these BEFORE writing Step 6" not in contract
    assert "Before you begin writing your reconsideration, launch" not in contract


def test_run_state_is_pinned_to_env_state_not_latest_symlink_docs() -> None:
    skill = _read("SKILL.md")
    steps = _read("docs/skill/STEPS.md")
    setup = _read("scripts/skill/setup.sh")
    helper_paths = [
        "scripts/skill/run_extract_step.sh",
        "scripts/skill/run_pipeline_step.sh",
        "scripts/skill/finalize_step6_ledgers.sh",
        "scripts/skill/render_memo_step.sh",
        "scripts/skill/finalize_and_archive.sh",
    ]
    helpers = {path: _read(path) for path in helper_paths}

    assert "scripts/skill/setup.sh" in skill
    assert "$HOME/.codex/skills/lolla" in skill
    assert ".codex/skills/lolla" in setup
    assert ".codex/lolla.env" in setup
    assert "make_run_id" in setup
    assert "LOLLA_EXPECTED_RUN_ID" in setup
    assert "LOLLA_ENV_STATE" in setup
    assert 'ln -sf "$LOLLA_ENV_STATE" /tmp/lolla_latest_env.sh' in setup
    assert "record_run_event.py" in setup

    docs = "\n".join([skill, steps])
    assert ". \"$LOLLA_ENV_STATE\"" in docs
    assert "source /tmp/lolla_latest_env.sh" not in docs
    assert ". /tmp/lolla_latest_env.sh" not in docs
    assert "discoverability fallback" in skill

    for path, text in helpers.items():
        assert "LOLLA_ENV_STATE" in text, path
        assert "LOLLA_EXPECTED_RUN_ID" in text, path
        assert "run state mismatch" in text, path

    assert "assert_expected_run_state" in _read("scripts/skill/persist_revised_answer.py")
    assert "assert_expected_run_state" in _read(
        "scripts/skill/persist_default_off_pressure_check.py"
    )


def test_skill_requires_live_transcript_artifact_and_gate_before_archive() -> None:
    skill = _read("SKILL.md")
    steps = _read("docs/skill/STEPS.md")
    contract = "\n".join([skill, steps])

    assert "/tmp/lolla_${LOLLA_RUN_ID}_live_transcript.txt" in contract
    assert "append every user-visible" in contract
    assert "finalize_live_output_hygiene.py" in contract
    assert "--require-live-output-clean" in contract
    assert "--trusted-transcript" in contract
    assert "manual transcript" in contract
    assert "live_output_health: not_checked" in contract
    assert "before archive" in contract.lower()


def test_reasoning_trace_archive_contract_is_preserved() -> None:
    skill = _read("SKILL.md")
    steps = _read("docs/skill/STEPS.md")
    archive = _read("scripts/archive_run.py")
    contract = "\n".join([skill, steps, archive])

    assert "18 core/optional" in contract
    assert "run_events.json" in contract
    assert "user_usefulness_review.json" in contract
    assert "outcome_review.json" in contract
    assert "graph_survival_report.json" in contract
    assert "graph_survival_report.md" in contract
    assert "reasoning_trace.json" in contract
    assert "exact captured-conversation hash first" in contract
    assert "conversation_hashes" in contract
    assert "exact fingerprint first, then token-set Jaccard" not in contract


def test_load_bearing_helpers_record_lifecycle_events() -> None:
    setup = _read("scripts/skill/setup.sh")
    run_extract_helper = _read("scripts/skill/run_extract_step.sh")
    run_pipeline_helper = _read("scripts/skill/run_pipeline_step.sh")
    revised_helper = _read("scripts/skill/persist_revised_answer.py")
    ledger_helper = _read("scripts/skill/finalize_step6_ledgers.sh")
    pressure_helper = _read("scripts/skill/persist_default_off_pressure_check.py")
    memo_helper = _read("scripts/skill/render_memo_step.sh")
    finalizer_helper = _read("scripts/skill/finalize_and_archive.sh")

    helper_contract = "\n".join(
        [
            setup,
            run_extract_helper,
            run_pipeline_helper,
            revised_helper,
            ledger_helper,
            pressure_helper,
            memo_helper,
            finalizer_helper,
        ]
    )

    assert "run_initialized" in setup
    assert "record_run_event_quiet" in helper_contract
    assert "extraction_completed" in run_extract_helper
    assert "pipeline_completed" in run_pipeline_helper
    assert "revised_answer_persisted" in revised_helper
    assert "step6_ledgers_finalized" in ledger_helper
    assert "pressure_check_state_persisted" in pressure_helper
    assert "memo_rendered" in memo_helper
    assert "observatory_launch_attempted" in finalizer_helper
    assert "observatory_launch_skipped" in finalizer_helper
    assert "observatory_$OBSERVATORY_STATUS" in finalizer_helper
    assert "archive_completed" in finalizer_helper
    assert "final_receipt_written" in finalizer_helper

    for helper in [
        run_extract_helper,
        run_pipeline_helper,
        ledger_helper,
        memo_helper,
        finalizer_helper,
    ]:
        assert "scripts/record_run_event.py" in helper
        assert "--quiet || true" in helper


def test_skill_externalized_step_anchors_resolve() -> None:
    skill = _read("SKILL.md")
    steps = _read("docs/skill/STEPS.md")
    explicit_anchors = set(re.findall(r'<a id="([^"]+)"></a>', steps))
    heading_anchors = {
        re.sub(r"[^a-z0-9 -]", "", match.group(1).strip().lower()).replace(" ", "-")
        for match in re.finditer(r"^##+ (.+)$", steps, flags=re.MULTILINE)
    }
    anchors = explicit_anchors | heading_anchors

    linked = re.findall(r"\]\(docs/skill/STEPS\.md#([^)]+)\)", skill)
    assert linked
    missing = sorted(anchor for anchor in linked if anchor not in anchors)
    assert missing == []


def test_skill_stays_compact_but_not_overcompressed() -> None:
    line_count = len(_read("SKILL.md").splitlines())
    assert line_count < 500
    assert line_count >= 220


def test_load_bearing_steps_use_helpers() -> None:
    skill = _read("SKILL.md")
    steps = _read("docs/skill/STEPS.md")
    run_extract_helper = _read("scripts/skill/run_extract_step.sh")
    run_pipeline_helper = _read("scripts/skill/run_pipeline_step.sh")
    capture_validator = _read("scripts/skill/validate_conversation_capture.py")
    revised_helper = _read("scripts/skill/persist_revised_answer.py")
    ledger_helper = _read("scripts/skill/finalize_step6_ledgers.sh")
    finalizer_helper = _read("scripts/skill/finalize_and_archive.sh")
    memo_helper = _read("scripts/skill/render_memo_step.sh")
    pressure_helper = _read("scripts/skill/persist_default_off_pressure_check.py")

    assert 'bash "$SKILL_DIR/scripts/skill/run_extract_step.sh"' in steps
    assert 'bash "$SKILL_DIR/scripts/skill/run_pipeline_step.sh"' in steps
    assert 'python3 "$SKILL_DIR/scripts/skill/persist_revised_answer.py"' in steps
    assert 'bash "$SKILL_DIR/scripts/skill/finalize_step6_ledgers.sh" --pre-step6-only' in steps
    assert 'bash "$SKILL_DIR/scripts/skill/finalize_step6_ledgers.sh" --v60-only' in steps
    assert 'python3 "$SKILL_DIR/scripts/skill/persist_default_off_pressure_check.py"' in steps
    assert 'bash "$SKILL_DIR/scripts/skill/render_memo_step.sh"' in steps
    assert 'bash "$SKILL_DIR/scripts/skill/finalize_and_archive.sh"' in steps
    assert "--receipt-file" in steps
    assert "--skip-observatory" in steps
    assert "invoke the helper" in skill
    assert "Every new Bash tool call starts in a fresh shell" in skill

    assert "run_extract.py" in run_extract_helper
    assert "validate_conversation_capture.py" in run_extract_helper
    assert "validate_conversation_capture.py" in run_pipeline_helper
    assert "no [Turn N] ASSISTANT markers found" in capture_validator
    assert "--pre-step6-portfolio step6_private" in run_pipeline_helper
    assert "LOLLA_PRE_STEP6_REQUIRE_CACHE_HIT" in run_pipeline_helper
    assert 'cache.get("state") != "cache_hit"' in run_pipeline_helper
    assert "revised_answer_written_at" in revised_helper
    assert '"--file"' in revised_helper
    assert "LOLLA_LIVE_TRANSCRIPT" in revised_helper
    assert "finalize_v60_telemetry.py" in ledger_helper
    assert "finalize_pre_step6_private_table_ledger.py" in ledger_helper
    assert "gap_check_summary" in pressure_helper
    assert "pressure_check_mode" in pressure_helper
    assert "render_memo.py" in memo_helper
    assert "--result" in memo_helper
    assert "--memo-note-file" in memo_helper
    assert "archive_run.py" in finalizer_helper
    assert "USER_RECEIPT_BEGIN" in finalizer_helper
    assert "RECEIPT_FILE" in finalizer_helper
    assert "receipt not in transcript" in finalizer_helper
    assert finalizer_helper.count("USER_RECEIPT_BEGIN") == 1
    assert finalizer_helper.rfind("USER_RECEIPT_BEGIN") > finalizer_helper.rfind(
        "archive_run.py"
    )
    assert (
        finalizer_helper.rfind("append_receipt_to_transcript")
        < finalizer_helper.rfind("archive_run.py")
        < finalizer_helper.rfind("USER_RECEIPT_BEGIN")
    )
    assert "for _ in {1..15}" in finalizer_helper


def test_skill_docs_do_not_expose_direct_load_bearing_commands() -> None:
    docs = "\n".join([_read("SKILL.md"), _read("docs/skill/STEPS.md")])

    forbidden_direct_commands = [
        "python3 $SKILL_DIR/scripts/run_extract.py",
        "python3 $SKILL_DIR/scripts/run_pipeline.py",
        "python3 $SKILL_DIR/scripts/render_memo.py",
        "python3 scripts/render_memo.py",
        "python3 scripts/finalize_v60_consideration_ledger.py",
        "python3 scripts/archive_run.py",
        "source /tmp/lolla_latest_env.sh",
    ]
    for command in forbidden_direct_commands:
        assert command not in docs


def test_research_cache_vars_are_not_loaded_by_default_env() -> None:
    setup = _read("scripts/skill/setup.sh")
    gitignore = _read(".gitignore")
    forbidden = [
        "LOLLA_PRE_STEP6_PORTFOLIO_CACHE_DIR",
        "LOLLA_PRE_STEP6_PORTFOLIO_CACHE_REF",
        "LOLLA_PRE_STEP6_REQUIRE_CACHE_HIT",
    ]

    assert ".env.research" in setup
    assert "LOLLA_RESEARCH_MODE" in setup
    assert ".env.research" in gitignore

    env_path = Path(".env")
    if env_path.exists():
        env_text = env_path.read_text(encoding="utf-8")
        for key in forbidden:
            assert key not in env_text
