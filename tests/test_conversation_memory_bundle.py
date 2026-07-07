from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from engine.system_b.conversation_memory_packet import (
    CONVERSATION_MEMORY_PACKET_SCHEMA_VERSION,
    ConversationMemoryInputError,
    build_conversation_memory_bundle,
    build_conversation_memory_packet,
    render_conversation_memory_packet_json,
    validate_output_dir,
)
from engine.system_b.conversation_memory_renderer import (
    render_conversation_memory_markdown,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/evals/build_conversation_memory_bundle.py"
RAW_MARKER = "RAW CONVERSATION MARKER DO NOT COPY IN PUBLIC SAFE"
PRIVATE_MARKER = "PRIVATE LEDGER MARKER DO NOT COPY"


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _fixture_run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "runs" / "sample-case" / "20260706T120000Z_test"
    run_dir.mkdir(parents=True)
    _write_json(
        run_dir / "reasoning_trace.json",
        {
            "schema_version": "lolla.reasoning_trace.v0.2",
            "case": {
                "case_id": "sample-case",
                "run_id": "20260706T120000Z_test",
                "decision_situation": "Whether to launch the beta after a mixed review.",
            },
            "capture": {
                "capture_adequacy": {
                    "status": "good",
                    "capture_strategy": "full_conversation",
                },
                "decision_structure": {
                    "live_constraint_count": 1,
                    "reasoning_passage_count": 2,
                    "dropped_thread_count": 1,
                },
            },
            "process": {
                "run_health": {
                    "overall": "healthy",
                    "product_output_health": "clean",
                }
            },
            "trace_adequacy": {
                "status": "adequate",
                "future_review_ready": True,
            },
            "reasoning_lenses": [
                {
                    "model_id": "inversion",
                    "lane": "lane3",
                    "role": "frame_pressure",
                    "selected": True,
                    "surfaced": True,
                    "disposition": "selected",
                    "source_ref": "result.json#/audit_summary/route_trace",
                },
                {
                    "model_id": "premortem",
                    "lane": "lane4",
                    "role": "gap_question",
                    "selected": False,
                    "surfaced": True,
                    "disposition": "surfaced",
                    "source_ref": "result.json#/structural_coverage_card",
                },
            ],
            "budget_suppressed_lenses": [
                {
                    "model_id": "base-rates",
                    "reason": "budget_suppressed",
                    "source": "reasoning_trace",
                }
            ],
        },
    )
    _write_json(
        run_dir / "agent_result.json",
        {
            "schema_version": "lolla_agent_result.v1",
            "case_id": "sample-case",
            "run_id": "20260706T120000Z_test",
            "status": "ok",
            "caller_action": "use_revised_answer",
            "run_health_overall": "healthy",
            "product_output_health": "clean",
            "position_changed": True,
            "main_counter_pressure": "The launch gate was under-specified.",
            "changed_advice_summary": [
                "Add a launch gate before relying on the enterprise signal."
            ],
            "take_backs": [
                "Do not treat the review as full market proof."
            ],
            "human_questions": [
                "Who owns the launch gate?"
            ],
        },
    )
    _write_json(
        run_dir / "evaluation.json",
        {
            "schema_version": "lolla.evaluation.v0",
            "case_id": "sample-case",
            "run_id": "20260706T120000Z_test",
            "overall": "pass",
            "caller_readiness": "usable_after_inspection",
        },
    )
    _write_json(
        run_dir / "extraction.json",
        {
            "status": "ok",
            "extraction": {
                "decision_situation": "Whether to launch the beta after a mixed review.",
                "original_framing": "The beta looked ready because the signal was credible.",
                "synthesized_position": "Launch only if a narrow gate passes.",
                "live_constraints": [{"text": "Do not overfit one enterprise review."}],
                "dropped_threads": [{"text": "Pricing risk was mentioned but not resolved."}],
                "assumptions": [{"text": "The team can still delay public launch."}],
            },
        },
    )
    _write_json(
        run_dir / "result.json",
        {
            "run_health": {
                "overall": "healthy",
                "product_output_health": "clean",
            },
            "memo_substantive_title": "Beta Launch Gate",
            "memo_orientation_note": "The recommendation became more conditional.",
            "memo_what_changed": "Add a gate before launch.",
            "memo_what_still_holds": "The enterprise signal still matters.",
            "memo_take_back_or_set_aside": "Do not treat one signal as proof.",
            "memo_pressure_check": "Name the disconfirming evidence.",
            "structural_coverage_card": {
                "gap_questions": [
                    {
                        "questions": [
                            "What evidence would stop the launch?"
                        ]
                    }
                ]
            },
            "revised_answer": "Launch only if the gate passes.",
        },
    )
    _write_json(
        run_dir / "memo_note.json",
        {
            "memo_substantive_title": "Beta Launch Gate",
            "memo_what_still_holds": "The enterprise signal still matters.",
        },
    )
    _write_json(
        run_dir / "graph_survival_report.json",
        {
            "schema_version": "lolla.graph_survival_report.v0.1",
            "status": "ready",
            "noise_policy": {
                "unselected_does_not_mean_noise": True,
                "unknown_noise_status": True,
            },
            "summary": {
                "lane_candidate_count": 3,
                "embedding_hit_count": 2,
                "selected_card_count": 1,
                "suppressed_signal_count": 1,
            },
            "candidate_survival": [
                {
                    "model_id": "inversion",
                    "survival_state": "selected_for_v60",
                    "sources": ["lane3"],
                    "visible_effects": ["Changed launch gate language."],
                    "private_guardrails": [],
                },
                {
                    "model_id": "base-rates",
                    "survival_state": "suppressed",
                    "sources": ["embedding"],
                    "visible_effects": [],
                    "private_guardrails": [],
                },
            ],
            "suppressed_signals": [
                {
                    "model_id": "base-rates",
                    "reason": "budget",
                    "source": "embedding",
                    "research_status": "unknown_not_noise",
                }
            ],
        },
    )
    _write_json(
        run_dir / "run_events.json",
        {
            "schema_version": "lolla.run_events.v0.1",
            "events": [
                {"event_type": "archive_started"},
                {"event_type": "archive_completed"},
            ],
        },
    )
    (run_dir / "conversation.txt").write_text(
        f"User: Should we launch?\nAssistant: Maybe.\n{RAW_MARKER}",
        encoding="utf-8",
    )
    (run_dir / "memo.md").write_text(
        "# Beta Launch Gate\n\nUse a launch gate before treating the signal as proof.",
        encoding="utf-8",
    )
    (run_dir / "revised.txt").write_text(
        "Launch only if the gate passes.",
        encoding="utf-8",
    )
    (run_dir / "pre_step6_private_table.md").write_text(
        PRIVATE_MARKER,
        encoding="utf-8",
    )
    return run_dir


def test_packet_is_self_describing_and_source_mapped(tmp_path: Path) -> None:
    packet = build_conversation_memory_packet(
        run_dir=_fixture_run_dir(tmp_path),
        created_at="2026-07-06T12:00:00Z",
    )

    assert packet["schema_version"] == CONVERSATION_MEMORY_PACKET_SCHEMA_VERSION
    assert packet["self_description"]["what_this_file_is"]
    assert packet["upflow"]["stages"]
    assert packet["interpretation_legend"]
    assert packet["reading_protocol"]
    assert packet["update_policy"]["preserve_source_refs"] is True
    assert packet["case"]["decision_situation"] == (
        "Whether to launch the beta after a mixed review."
    )
    source_artifacts = {ref["artifact"] for ref in packet["source_refs"]}
    assert {
        "reasoning_trace.json",
        "agent_result.json",
        "evaluation.json",
        "memo.md",
        "conversation.txt",
    }.issubset(source_artifacts)
    assert packet["source_conversation"]["included"] is False
    assert packet["suppressed_or_unadjudicated"]["items"][0]["model_id"] == "base-rates"


def test_public_safe_rejects_raw_conversation_and_omits_raw_text(tmp_path: Path) -> None:
    run_dir = _fixture_run_dir(tmp_path)

    with pytest.raises(ConversationMemoryInputError, match="public_safe"):
        build_conversation_memory_packet(
            run_dir=run_dir,
            privacy_mode="public_safe",
            include_raw_conversation=True,
        )

    packet = build_conversation_memory_packet(
        run_dir=run_dir,
        privacy_mode="public_safe",
    )
    rendered = (
        render_conversation_memory_packet_json(packet, pretty=True)
        + render_conversation_memory_markdown(packet)
    )

    assert packet["privacy"]["raw_conversation_included"] is False
    assert RAW_MARKER not in rendered
    assert PRIVATE_MARKER not in rendered


def test_user_private_can_include_raw_conversation_explicitly(tmp_path: Path) -> None:
    packet = build_conversation_memory_packet(
        run_dir=_fixture_run_dir(tmp_path),
        privacy_mode="user_private",
        include_raw_conversation=True,
    )
    markdown = render_conversation_memory_markdown(packet)

    assert packet["privacy"]["raw_conversation_included"] is True
    assert packet["source_conversation"]["included"] is True
    assert "### Full 1:1 Conversation Transcript" in markdown
    assert "full archived `conversation.txt` transcript" in markdown
    assert RAW_MARKER in markdown
    assert "Evidence label: private" in markdown


def test_markdown_renderer_includes_required_context_blocks(tmp_path: Path) -> None:
    packet = build_conversation_memory_packet(run_dir=_fixture_run_dir(tmp_path))
    markdown = render_conversation_memory_markdown(packet)

    for heading in (
        "## Cold Reader Orientation",
        "## Claim Verification Checklist",
        "## What This File Is",
        "## What This File Is Not",
        "## How This File Was Produced",
        "## Source Artifact Map",
        "## Interpretation Legend",
        "## Agent Instructions For Future Use",
        "## Update Rules",
    ):
        assert heading in markdown
    assert markdown.count("Evidence label:") >= 20
    assert "Source refs:" in markdown
    assert "runtime_source_of_truth: false" in markdown
    assert "selected_lenses_are_not_proof" in markdown
    assert "suppressed_lenses_are_not_noise" in markdown


def test_cold_reader_orientation_is_anti_anchoring(tmp_path: Path) -> None:
    packet = build_conversation_memory_packet(run_dir=_fixture_run_dir(tmp_path))
    markdown = render_conversation_memory_markdown(packet)

    assert markdown.index("## Cold Reader Orientation") < markdown.index(
        "## What This File Is"
    )
    assert "Evidence label: `synthesis_to_verify`" in markdown
    assert "Orientation, not conclusion." in markdown
    assert "System Synthesis To Verify" in markdown
    assert "Generated synthesis appears later" in markdown
    assert "hypotheses to verify, not ground truth" in markdown
    assert "Do not treat this orientation as the answer." in markdown
    assert "Inspect the full transcript when it is included." in markdown
    assert "memo and revised answer against the transcript" in markdown
    assert "selected and suppressed lenses as system behavior, not proof" in markdown
    assert "Empty structured rows do not mean the decision has no remaining uncertainty." in markdown
    assert "Key Checks Before Trusting Any Interpretation" in markdown
    assert "Does the transcript support the generated synthesis?" in markdown
    assert "Could current business facts have changed since the run?" in markdown
    assert "- Generated synthesis:" not in markdown
    assert "The correct interpretation is" not in markdown
    assert "The proven recommendation is" not in markdown


def test_claim_verification_checklist_points_to_sources_without_proof_claims(
    tmp_path: Path,
) -> None:
    packet = build_conversation_memory_packet(run_dir=_fixture_run_dir(tmp_path))
    markdown = render_conversation_memory_markdown(packet)

    assert markdown.index("## Cold Reader Orientation") < markdown.index(
        "## Claim Verification Checklist"
    )
    assert markdown.index("## Claim Verification Checklist") < markdown.index(
        "## What This File Is"
    )
    assert "Evidence label: `synthesis_to_verify`" in markdown
    assert "Use this as a checking index, not as a conclusion." in markdown
    assert "It does not prove any claim, certify advice, or replace source inspection." in markdown
    assert "| Claim / item to verify | Best evidence in this file | Source locator | Still verify before relying |" in markdown
    assert "Decision situation: Whether to launch the beta after a mixed review." in markdown
    assert "Generated synthesized position: Launch only if a narrow gate passes." in markdown
    assert "Changed advice summary: Add a launch gate before relying on the enterprise signal." in markdown
    assert "Main counter-pressure: The launch gate was under-specified." in markdown
    assert "Open question: Who owns the launch gate?" in markdown
    assert "Run readiness: evaluation=pass, trace=adequate, future_review_ready=true" in markdown
    assert "conversation.txt, extraction.json, reasoning_trace.json" in markdown
    assert '<a id="cm-section-claim-verification-checklist"></a>' in markdown
    assert '<a id="cm-section-conversation-interpretation"></a>' in markdown
    assert '<a id="cm-section-run-health-and-readiness"></a>' in markdown
    assert "Transcript (artifact not embedded)" in markdown
    assert "[Transcript](#cm-source-full-transcript)" not in markdown
    assert "[Conversation Interpretation](#cm-section-conversation-interpretation)" in markdown
    assert "[Run Health And Readiness](#cm-section-run-health-and-readiness)" in markdown
    assert "Treat as generated synthesis; verify against source conversation and current context." in markdown
    assert "do not infer advice correctness" in markdown
    assert "The correct interpretation is" not in markdown
    assert "The proven recommendation is" not in markdown


def test_source_excerpt_anchors_are_rendered_when_sources_are_included(
    tmp_path: Path,
) -> None:
    packet = build_conversation_memory_packet(
        run_dir=_fixture_run_dir(tmp_path),
        include_raw_conversation=True,
    )
    markdown = render_conversation_memory_markdown(packet)

    assert '<a id="cm-source-full-transcript"></a>' in markdown
    assert '<a id="cm-source-memo"></a>' in markdown
    assert '<a id="cm-source-revised-answer"></a>' in markdown
    assert markdown.index('<a id="cm-source-full-transcript"></a>') < markdown.index(
        "### Full 1:1 Conversation Transcript"
    )
    assert markdown.index('<a id="cm-source-memo"></a>') < markdown.index("### Memo")
    assert markdown.index('<a id="cm-source-revised-answer"></a>') < markdown.index(
        "### Revised Answer"
    )


def test_bundle_writes_outputs_outside_archive(tmp_path: Path) -> None:
    run_dir = _fixture_run_dir(tmp_path)
    output_dir = tmp_path / "conversation-memory-output"

    result = build_conversation_memory_bundle(
        run_dir=run_dir,
        output_dir=output_dir,
        created_at="2026-07-06T12:00:00Z",
    )

    assert result["status"] == "generated"
    assert result["input_archive_mutated"] is False
    assert result["generated_artifacts"] == {
        "packet": "conversation_memory_packet.json",
        "markdown": "conversation_memory.md",
    }
    assert (output_dir / "conversation_memory_packet.json").is_file()
    assert (output_dir / "conversation_memory.md").is_file()
    assert not (run_dir / "conversation_memory.md").exists()


def test_output_inside_archive_is_rejected(tmp_path: Path) -> None:
    run_dir = _fixture_run_dir(tmp_path)

    with pytest.raises(ConversationMemoryInputError, match="outside run directory"):
        validate_output_dir(output_dir=run_dir / "conversation_memory", run_dir=run_dir)


def test_missing_required_artifacts_fail_clearly(tmp_path: Path) -> None:
    run_dir = _fixture_run_dir(tmp_path)
    (run_dir / "reasoning_trace.json").unlink()

    with pytest.raises(ConversationMemoryInputError, match="missing required artifact"):
        build_conversation_memory_packet(run_dir=run_dir)


def test_cli_generates_bundle_and_prints_status(tmp_path: Path) -> None:
    run_dir = _fixture_run_dir(tmp_path)
    output_dir = tmp_path / "cli-output"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--run-dir",
            str(run_dir),
            "--out",
            str(output_dir),
            "--privacy-mode",
            "user_private",
            "--created-at",
            "2026-07-06T12:00:00Z",
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "lolla.conversation_memory_bundle_write.v0"
    assert payload["status"] == "generated"
    assert (output_dir / "conversation_memory_packet.json").exists()
    assert (output_dir / "conversation_memory.md").exists()
