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
    audit_mode_validator = _read("scripts/skill/validate_audit_mode.py")
    capture_validator = _read("scripts/skill/validate_conversation_capture.py")
    private_persist_helper = _read("scripts/skill/persist_private_artifact.py")
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
            audit_mode_validator,
            capture_validator,
            private_persist_helper,
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
    assert "LOLLA_AUDIT_MODE" in contract
    assert "risk_mode" in contract
    assert "validate_audit_mode.py" in contract
    assert "Pre-Step-6 private table receipt:" in contract
    assert "operator cache ref:" in contract
    assert "expected cache file:" in contract
    assert "pre_step6_private_table" in contract
    assert "pre_step6_private_table_ledger" in contract
    assert "finalize_pre_step6_private_table_ledger" in contract

    assert "Post-Step-6 pressure-check sub-agents are rested by default" in contract
    assert "LOLLA_STEP7_PRESSURE_CHECK=on" in contract
    assert '"status": "not_run_default_off"' in contract
    assert '"reason": "post_step6_pressure_check_default_off"' in contract
    assert "Default-off runs do not create" in contract
    assert "only AFTER Step 6b finalization succeeds" in contract

    assert "requires exact item" in contract
    assert "copies all immutable" in contract
    assert "--require-valid" in contract
    assert "finalize_pre_step6_private_table_ledger.py" in contract
    assert '"source_id": "<copy exact source_id from the skeleton>"' not in contract
    assert '"source_id": "lane1_structural_challenge"' not in contract
    assert "Launch these BEFORE writing Step 6" not in contract
    assert "Before you begin writing your reconsideration, launch" not in contract


def test_run_state_is_pinned_to_exact_run_handle_not_latest_symlink_docs() -> None:
    skill = _read("SKILL.md")
    steps = _read("docs/skill/STEPS.md")
    setup = _read("scripts/skill/setup.sh")
    helper_paths = [
        "scripts/skill/run_extract_step.sh",
        "scripts/skill/run_pipeline_step.sh",
        "scripts/skill/persist_private_step.sh",
        "scripts/skill/prepare_consumer_step.sh",
        "scripts/skill/persist_default_pressure_step.sh",
        "scripts/skill/finalize_step6_ledgers.sh",
        "scripts/skill/render_memo_step.sh",
        "scripts/skill/finalize_and_archive.sh",
    ]
    helpers = {path: _read(path) for path in helper_paths}

    assert "scripts/skill/setup.sh" in skill
    assert "$HOME/.codex/skills/lolla" in skill
    assert "${BASH_SOURCE[0]}" in setup
    assert "_LOLLA_SCRIPT_DIR/../.." in setup
    assert 'SKILL_DIR="$HOME/.codex/skills/lolla"' not in setup
    assert 'SKILL_DIR="$HOME/.claude/skills/lolla"' not in setup
    assert ".codex/lolla.env" not in setup
    assert ".claude/lolla.env" not in setup
    assert "optional embedding retrieval and query expansion" in setup
    assert "full accuracy" not in setup
    assert "make_run_id" in setup
    assert "LOLLA_EXPECTED_RUN_ID" in setup
    assert "LOLLA_ENV_STATE" in setup
    assert "LOLLA_OPERATOR_LOG" in setup
    assert "$LOLLA_TMP_DIR/lolla_${LOLLA_RUN_ID}_operator.log" in setup
    assert 'LOLLA_TMP_DIR="${LOLLA_TMP_DIR:-/tmp}"' in setup
    assert "export LOLLA_AUDIT_MODE" in setup
    assert "risk_mode=\"$LOLLA_AUDIT_MODE\"" in setup
    assert (
        'ln -sf "$LOLLA_ENV_STATE" "$LOLLA_TMP_DIR/lolla_latest_env.sh"'
        in setup
    )
    assert setup.count("umask 077") >= 2
    assert "record_run_event.py" in setup

    docs = "\n".join([skill, steps])
    assert "RUN_HANDLE:" in docs
    assert "--run-id RUN_HANDLE" in docs
    assert "Do not copy or source an environment" in skill
    assert "source /tmp/lolla_latest_env.sh" not in docs
    assert ". /tmp/lolla_latest_env.sh" not in docs
    assert "compatibility/discoverability artifact only" in skill

    for path, text in helpers.items():
        assert "load_run_state.sh" in text, path
        assert "lolla_load_run_state" in text, path

    for path in [
        "scripts/skill/run_extract_step.sh",
        "scripts/skill/run_pipeline_step.sh",
        "scripts/skill/finalize_step6_ledgers.sh",
        "scripts/skill/render_memo_step.sh",
        "scripts/skill/finalize_and_archive.sh",
    ]:
        assert "LOLLA_EXPECTED_RUN_ID" in helpers[path], path
        assert "run state mismatch" in helpers[path], path

    private_persist = _read("scripts/skill/persist_private_artifact.py")
    assert "assert_expected_run_state" in private_persist
    assert "read_private_stdin" in private_persist
    assert "GRAPH_MUTABLE_FIELDS" in private_persist
    assert "assert_expected_run_state" in _read(
        "scripts/skill/persist_default_off_pressure_check.py"
    )


def test_skill_requires_live_transcript_artifact_and_gate_before_archive() -> None:
    skill = _read("SKILL.md")
    steps = _read("docs/skill/STEPS.md")
    finalizer = _read("scripts/skill/finalize_and_archive.sh")
    contract = "\n".join([skill, steps])

    assert "/tmp/lolla_${LOLLA_RUN_ID}_live_transcript.txt" in contract
    assert "Persist every user-visible" in contract
    assert "persist_private_step.sh --kind narration" in contract
    assert "finalize_live_output_hygiene.py" in contract
    assert "--require-live-output-clean" in contract
    assert "--trusted-transcript" in contract
    assert "manual transcript" in contract
    assert "live_output_health: not_checked" in contract
    assert "before archive" in contract.lower()
    assert "/tmp/lolla_${LOLLA_RUN_ID}_operator.log" in contract
    assert "operator.log" in contract
    assert "--trusted-transcript" in contract
    assert "--require-live-output-clean" in contract
    assert "--trusted-transcript" in finalizer
    assert "--require-live-output-clean" in finalizer
    assert "sync_trusted_transcript_to_default" in finalizer


def test_reasoning_trace_archive_contract_is_preserved() -> None:
    skill = _read("SKILL.md")
    steps = _read("docs/skill/STEPS.md")
    archive = _read("scripts/archive_run.py")
    contract = "\n".join([skill, steps, archive])

    assert "24 core/optional" in contract
    assert "operator.log" in contract
    assert "run_events.json" in contract
    assert "user_usefulness_review.json" in contract
    assert "outcome_review.json" in contract
    assert "agent_result.json" in contract
    assert "lolla_agent_result.v2" in contract
    assert "control_input.json" in contract
    assert "control_result.json" in contract
    assert "lolla_control_result.v1" in contract
    assert "does not approve actions" in contract
    assert "risk_mode" in contract
    assert "LOLLA_AUDIT_MODE" in contract
    assert "graph_survival_report.json" in contract
    assert "graph_survival_report.md" in contract
    assert "reasoning_trace.json" in contract
    assert "exact captured-conversation hash first" in contract
    assert "conversation_hashes" in contract
    assert "exact fingerprint first, then token-set Jaccard" not in contract


def test_load_bearing_helpers_record_lifecycle_events() -> None:
    setup = _read("scripts/skill/setup.sh")
    capture_helper = _read("scripts/skill/capture_conversation.py")
    run_extract_helper = _read("scripts/skill/run_extract_step.sh")
    extraction_finalizer = _read(
        "scripts/skill/finalize_extraction_attempt.py"
    )
    run_pipeline_helper = _read("scripts/skill/run_pipeline_step.sh")
    revised_helper = _read("scripts/skill/persist_revised_answer.py")
    ledger_helper = _read("scripts/skill/finalize_step6_ledgers.sh")
    pressure_helper = _read("scripts/skill/persist_default_off_pressure_check.py")
    memo_helper = _read("scripts/skill/render_memo_step.sh")
    finalizer_helper = _read("scripts/skill/finalize_and_archive.sh")
    observatory_launcher = _read("scripts/skill/launch_observatory.py")

    helper_contract = "\n".join(
        [
            setup,
            capture_helper,
            run_extract_helper,
            extraction_finalizer,
            run_pipeline_helper,
            revised_helper,
            ledger_helper,
            pressure_helper,
            memo_helper,
            finalizer_helper,
        ]
    )

    assert "run_initialized" in setup
    assert "conversation_captured" in capture_helper
    assert "record_run_event_quiet" in helper_contract
    assert "extraction_completed" in run_extract_helper
    assert "extraction_failed" in extraction_finalizer
    assert "extraction_declined" in extraction_finalizer
    assert "append_run_event" in extraction_finalizer
    assert "pipeline_completed" in run_pipeline_helper
    assert "revised_answer_persisted" in revised_helper
    assert "step6_ledgers_finalized" in ledger_helper
    assert "pressure_check_state_persisted" in pressure_helper
    assert "memo_rendered" in memo_helper
    assert "observatory_launch_attempted" in finalizer_helper
    assert "observatory_launch_skipped" in finalizer_helper
    assert "observatory_$OBSERVATORY_STATUS" in finalizer_helper
    assert "launch_observatory.py" in finalizer_helper
    assert "start_new_session=True" in observatory_launcher
    assert "archive_completed" in finalizer_helper
    assert "final_receipt_written" in finalizer_helper

    for helper in [
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


def test_skill_exposes_one_level_substrate_operations_reference() -> None:
    skill = _read("SKILL.md")
    reference = _read("references/knowledge-substrate-operations.md")

    assert "references/knowledge-substrate-operations.md" in skill
    assert "validate_self_contained_skill.py --validate-only" in reference
    assert "direct-active seeds" in reference
    assert "authored outgoing relations" in reference
    assert "candidate-only" in reference
    assert "not proof" in reference


def test_load_bearing_steps_use_helpers() -> None:
    skill = _read("SKILL.md")
    steps = _read("docs/skill/STEPS.md")
    run_extract_helper = _read("scripts/skill/run_extract_step.sh")
    run_pipeline_helper = _read("scripts/skill/run_pipeline_step.sh")
    capture_helper = _read("scripts/skill/capture_step.sh")
    capture_validator = _read("scripts/skill/validate_conversation_capture.py")
    private_persist_helper = _read("scripts/skill/persist_private_artifact.py")
    consumer_helper = _read("scripts/skill/prepare_consumer_packet.py")
    ledger_helper = _read("scripts/skill/finalize_step6_ledgers.sh")
    finalizer_helper = _read("scripts/skill/finalize_and_archive.sh")
    memo_helper = _read("scripts/skill/render_memo_step.sh")
    pressure_helper = _read("scripts/skill/persist_default_off_pressure_check.py")

    assert "bash scripts/skill/capture_step.sh --run-id RUN_HANDLE" in steps
    assert "bash scripts/skill/run_extract_step.sh --run-id RUN_HANDLE" in steps
    assert "bash scripts/skill/run_pipeline_step.sh --run-id RUN_HANDLE" in steps
    assert "persist_private_step.sh" in steps
    assert "prepare_consumer_step.sh" in steps
    assert "--kind step6" in steps
    assert "--kind receipt" in steps
    assert (
        'bash "$SKILL_DIR/scripts/skill/finalize_step6_ledgers.sh" --pre-step6-only'
        not in steps
    )
    assert (
        'bash "$SKILL_DIR/scripts/skill/finalize_step6_ledgers.sh" --v60-only'
        not in steps
    )
    assert "persist_default_pressure_step.sh --run-id RUN_HANDLE" in steps
    assert "bash scripts/skill/render_memo_step.sh --run-id RUN_HANDLE" in steps
    assert "bash scripts/skill/finalize_and_archive.sh --run-id RUN_HANDLE" in steps
    assert "--receipt-file" not in steps
    assert "--receipt-file" in finalizer_helper
    assert "--skip-observatory" in skill
    assert "--skip-observatory" in finalizer_helper
    assert "--private-receipt-override" in finalizer_helper
    assert "lolla_${LOLLA_RUN_ID}_final_receipt_override.txt" in finalizer_helper
    assert "invoke the helper" in skill
    assert "Every new shell tool call may start without prior exports" in skill

    assert "load_run_state.sh" in capture_helper
    assert "capture_conversation.py" in capture_helper
    assert "run_extract.py" in run_extract_helper
    assert "finalize_extraction_attempt.py" in run_extract_helper
    assert "extraction_terminal.json" in run_extract_helper
    assert "validate_conversation_capture.py" in run_extract_helper
    assert "validate_conversation_capture.py" in run_pipeline_helper
    assert "no [Turn N] ASSISTANT markers found" in capture_validator
    assert "--pre-step6-portfolio step6_private" in run_pipeline_helper
    assert "LOLLA_PRE_STEP6_REQUIRE_CACHE_HIT" in run_pipeline_helper
    assert 'cache.get("state") != "cache_hit"' in run_pipeline_helper
    assert "revised_answer_written_at" in private_persist_helper
    assert "read_private_stdin" in private_persist_helper
    assert "atomic_private_write_json" in private_persist_helper
    assert "memo_note_written_at" in private_persist_helper
    assert "graph_decisions" in private_persist_helper
    assert "finalize_constitutional_graph_survival_ledger" in private_persist_helper
    assert "finalize_pre_step6_private_table_ledger" in private_persist_helper
    assert "finalize_v60_consideration" in private_persist_helper
    assert "reconsideration" in consumer_helper
    assert "verification" in consumer_helper
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
    assert "launch_observatory.py" in finalizer_helper
    assert "nohup python3" not in finalizer_helper


def test_conversation_capture_is_a_private_runtime_operation_not_a_file_edit() -> None:
    skill = _read("SKILL.md")
    steps = _read("docs/skill/STEPS.md")
    contract = "\n".join([skill, steps])

    assert "capture_step.sh" in contract
    assert "PRIVATE_INPUT_READY" in contract
    assert "wait for" in contract.lower()
    assert "standard input" in contract
    assert "Apply Patch" in contract
    assert "file editor" in contract
    assert "cat > /tmp/lolla_${LOLLA_RUN_ID}_conversation.txt" not in contract


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
