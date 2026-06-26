from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.system_b.boundary_provider import BoundaryCallRecord
from engine.system_b.specialist_extractor_probe import (
    SPECIALIST_EXTRACTOR_PROBE_SCHEMA_VERSION,
    build_real_specialist_extractor_probe,
    build_specialist_extractor_probe,
    render_specialist_extractor_probe_json,
    write_real_specialist_extractor_probe,
    write_specialist_extractor_probe,
)
from scripts import probe_real_specialist_extractors as real_cli
from scripts.probe_specialist_extractors import main as cli_main


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _seed_run(tmp_path: Path) -> Path:
    run_dir = (
        tmp_path
        / "Users"
        / "marcin"
        / "SECRET_HOME"
        / "runs"
        / "case-a"
        / "run-a"
    )
    run_dir.mkdir(parents=True)
    (run_dir / "conversation.txt").write_text(
        "CONVERSATION: 4 turns, 2 user messages, 2 assistant responses\n\n"
        "[Turn 1] USER:\n"
        "SECRET TRANSCRIPT. We have six users ready and only two engineers.\n\n"
        "[Turn 1] ASSISTANT:\n"
        "Do not launch broadly; use a gated beta instead.\n\n"
        "[Turn 2] USER:\n"
        "SECRET PUSHBACK. Sales needs a proof point this week.\n\n"
        "[Turn 2] ASSISTANT:\n"
        "The proof point can be a narrower customer-success story.\n",
        encoding="utf-8",
    )
    _write_json(
        run_dir / "extraction.json",
        {
            "status": "ok",
            "capture_health": "good",
            "capture_adequacy": {
                "schema_version": "lolla.capture_adequacy.v0",
                "status": "good",
                "capture_strategy": "full",
                "declared_turn_count": 4,
                "captured_turn_count": 4,
                "omitted_turn_count": 0,
                "captured_windows": [],
                "omitted_windows": [],
                "risk_flags": [],
                "notes": [],
            },
            "extraction": {
                "decision_situation": "Whether to launch the beta",
                "live_constraints": [
                    {
                        "constraint": "six users ready",
                        "introduced_turn": 1,
                        "status": "active",
                        "weight": "structural",
                    }
                ],
                "synthesized_position": "Use a gated beta.",
                "reasoning_passages": [
                    "Do not launch broadly; use a gated beta instead."
                ],
                "original_framing": "Launch broadly?",
                "dropped_threads": [
                    {
                        "thread": "customer success story",
                        "raised_by": "assistant",
                        "raised_turn": 2,
                        "status": "acknowledged_then_dropped",
                    }
                ],
                "_quote_validation": {
                    "total": 1,
                    "verified": 1,
                    "fabricated": 0,
                    "fabricated_passages": ["SECRET FABRICATED PASSAGE"],
                },
            },
        },
    )
    _write_json(
        run_dir / "extraction_adequacy_report.json",
        {
            "schema_version": "lolla.extraction_adequacy_report.v0",
            "adequacy_status": "good",
            "extraction_field_summary": {
                "decision_situation_present": True,
                "live_constraints_count": 1,
                "dropped_threads_count": 1,
                "reasoning_passages_count": 1,
                "quote_validation": {
                    "present": True,
                    "total": 1,
                    "verified": 1,
                    "fabricated": 0,
                },
            },
            "provenance_gap_findings": {
                "missing_turn_ref_count": 0,
                "invalid_turn_ref_count": 0,
                "speaker_mismatch_count": 0,
            },
        },
    )
    _write_json(
        run_dir / "result.json",
        {
            "audit_summary": "SECRET AUDIT SUMMARY",
            "delta_card": {"present": True},
            "frame_pressure_card": {"present": True},
            "structural_coverage_card": {"present": True},
            "revised_answer_present": True,
            "memo_what_changed": "SECRET CHANGE REASON",
        },
    )
    (run_dir / "revised.txt").write_text("SECRET REVISED ANSWER", encoding="utf-8")
    (run_dir / "memo.md").write_text("SECRET MEMO TEXT", encoding="utf-8")
    _write_json(run_dir / "reasoning_trace.json", {"artifacts": []})
    _write_json(run_dir / "evaluation.json", {"overall": "partial", "checks": []})
    _write_json(
        run_dir / "agent_result.json",
        {
            "case_id": "case-a",
            "run_id": "run-a",
            "created_at": "2026-06-26T12:00:00Z",
            "status": "partial",
            "caller_action": "do_not_use_run_degraded",
            "changed_advice_summary": "SECRET CHANGED ADVICE",
            "do_not_act_before": ["SECRET GATE"],
            "human_questions": ["SECRET QUESTION"],
        },
    )
    return run_dir


def _fake_boundary_payload() -> dict:
    return {
        "live_constraints": [
            {
                "mode": "span",
                "text": "six users ready",
                "turn_index": 1,
                "kind": "constraint",
                "kind_ambiguity": False,
            }
        ],
        "stance_events": [
            {
                "text": "use a gated beta instead",
                "turn_index": 1,
                "relation": "commitment",
                "relation_ambiguity": False,
            }
        ],
        "dropped_threads": [
            {
                "text": "narrower customer-success story",
                "turn_index": 2,
                "speaker": "assistant",
                "kind": "open_loop",
                "kind_ambiguity": False,
                "superseded_by": "SECRET SUPERSEDED LABEL",
            }
        ],
    }


class _RecordingBoundary:
    def __init__(self) -> None:
        self.call_log: list[BoundaryCallRecord] = []
        self.last_call_metadata = None

    def run_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        stage: str = "unlabeled",
        tendency_id: str = "",
    ) -> dict[str, object]:
        del user_prompt
        record = BoundaryCallRecord(
            stage=stage,
            tendency_id=tendency_id,
            provider_name="openrouter",
            requested_model="google/gemini-3.1-flash-lite",
            served_model="google/gemini-3.1-flash-lite",
            model="google/gemini-3.1-flash-lite",
            model_attribution_status="matched",
            status="ok",
            finish_reason="stop",
            raw_message_content="SECRET RAW MODEL MESSAGE",
            temperature=0.2,
            prompt_tokens=100,
            completion_tokens=20,
            total_tokens=120,
            reasoning_disabled=True,
            reasoning_details_present=False,
        )
        self.call_log.append(record)
        self.last_call_metadata = record
        if "LIVE CONSTRAINTS" in system_prompt:
            return {"live_constraints": _fake_boundary_payload()["live_constraints"]}
        if "STANCE EVENT" in system_prompt:
            return {"stance_events": _fake_boundary_payload()["stance_events"]}
        if "DROPPED THREADS" in system_prompt:
            return {"dropped_threads": _fake_boundary_payload()["dropped_threads"]}
        return {}


def test_fake_boundary_live_constraints_improve_grounding(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)

    probe = build_specialist_extractor_probe(
        run_dir,
        fake_boundary_payload=_fake_boundary_payload(),
        specialists=["live_constraints"],
    )

    assert probe["schema_version"] == SPECIALIST_EXTRACTOR_PROBE_SCHEMA_VERSION
    assert probe["model_calls_made"] is False
    assert probe["model_call_count"] == 0
    assert probe["boundary_mode"] == "fake"
    live = probe["specialists"]["live_constraints"]
    assert live["attempted"] is True
    assert live["raw_candidate_count"] == 1
    assert live["validated_event_count"] == 1
    assert live["grounding_counts"]["span"] == 1
    assert live["did_improve_coverage"] is True
    assert live["improved_elements"] == ["live_constraints"]
    assert probe["baseline_semantic_coverage"]["semantic_elements"]["live_constraints"][
        "grounding"
    ] == "turn_ref"
    assert probe["enhanced_semantic_coverage"]["semantic_elements"]["live_constraints"][
        "grounding"
    ] == "span"


def test_fake_boundary_stance_events_improve_stance_lineage(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)

    probe = build_specialist_extractor_probe(
        run_dir,
        fake_boundary_payload=_fake_boundary_payload(),
        specialists=["stance"],
    )

    stance = probe["specialists"]["stance"]
    assert stance["attempted"] is True
    assert stance["validated_event_count"] == 1
    assert stance["grounding_counts"]["span"] == 1
    assert stance["did_improve_coverage"] is True
    element = "assistant_stance_or_recommendation_lineage"
    assert probe["baseline_semantic_coverage"]["semantic_elements"][element][
        "grounding"
    ] == "artifact_present_only"
    assert probe["enhanced_semantic_coverage"]["semantic_elements"][element][
        "grounding"
    ] == "span"


def test_fake_boundary_dropped_threads_produce_span_grounded_event(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(tmp_path)

    probe = build_specialist_extractor_probe(
        run_dir,
        fake_boundary_payload=_fake_boundary_payload(),
        specialists=["dropped_threads"],
    )

    dropped = probe["specialists"]["dropped_threads"]
    assert dropped["attempted"] is True
    assert dropped["validated_event_count"] == 1
    assert dropped["grounding_counts"]["span"] == 1
    assert dropped["did_improve_coverage"] is True
    assert dropped["improved_elements"] == ["dropped_or_under_carried_threads"]


def test_invalid_fake_boundary_candidate_is_dropped_and_reported(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(tmp_path)
    payload = {
        "live_constraints": [
            {
                "mode": "span",
                "text": "not a real substring",
                "turn_index": 1,
                "kind": "constraint",
            }
        ]
    }

    probe = build_specialist_extractor_probe(
        run_dir,
        fake_boundary_payload=payload,
        specialists=["live_constraints"],
    )

    live = probe["specialists"]["live_constraints"]
    assert live["raw_candidate_count"] == 1
    assert live["validated_event_count"] == 0
    assert live["validation_failures"]["dropped_not_substring"] == 1
    assert live["did_improve_coverage"] is False


def test_probe_output_does_not_leak_raw_text_or_absolute_paths(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(tmp_path)

    rendered = render_specialist_extractor_probe_json(
        build_specialist_extractor_probe(
            run_dir,
            fake_boundary_payload=_fake_boundary_payload(),
            specialists=["live_constraints", "stance", "dropped_threads"],
        )
    )

    assert "SECRET" not in rendered
    assert "SECRET_HOME" not in rendered
    assert "/Users/" not in rendered
    assert "six users ready" not in rendered
    assert "use a gated beta instead" not in rendered
    assert "narrower customer-success story" not in rendered
    assert "case-a/run-a" in rendered


def test_archive_folder_is_not_mutated(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)
    before = sorted(path.relative_to(run_dir) for path in run_dir.rglob("*") if path.is_file())

    build_specialist_extractor_probe(
        run_dir,
        fake_boundary_payload=_fake_boundary_payload(),
        specialists=["live_constraints", "stance", "dropped_threads"],
    )
    after = sorted(path.relative_to(run_dir) for path in run_dir.rglob("*") if path.is_file())

    assert before == after
    assert not (run_dir / "semantic_coverage_report.json").exists()


def test_output_is_deterministic(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)

    first = render_specialist_extractor_probe_json(
        build_specialist_extractor_probe(
            run_dir,
            fake_boundary_payload=_fake_boundary_payload(),
        )
    )
    second = render_specialist_extractor_probe_json(
        build_specialist_extractor_probe(
            run_dir,
            fake_boundary_payload=_fake_boundary_payload(),
        )
    )

    assert first == second


def test_cli_writes_json_and_exits_zero(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)
    fixture = tmp_path / "fake_boundary.json"
    fixture.write_text(json.dumps(_fake_boundary_payload()), encoding="utf-8")
    out = tmp_path / "probe.json"

    exit_code = cli_main(
        [
            str(run_dir),
            "--fake-boundary",
            str(fixture),
            "--out",
            str(out),
            "--all",
        ]
    )
    payload = json.loads(out.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert payload["schema_version"] == SPECIALIST_EXTRACTOR_PROBE_SCHEMA_VERSION
    assert payload["fake_boundary_call_count"] == 3
    assert out.exists()


def test_cli_rejects_output_inside_run_dir_without_mutating_archive(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = _seed_run(tmp_path)
    fixture = tmp_path / "fake_boundary.json"
    fixture.write_text(json.dumps(_fake_boundary_payload()), encoding="utf-8")
    out = run_dir / "probe.json"

    exit_code = cli_main(
        [
            str(run_dir),
            "--fake-boundary",
            str(fixture),
            "--out",
            str(out),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "out path must not be inside run_dir" in captured.err
    assert str(run_dir) not in captured.err
    assert not out.exists()


def test_library_rejects_output_inside_run_dir(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)
    out = run_dir / "probe.json"

    with pytest.raises(ValueError, match="out path must not be inside run_dir"):
        write_specialist_extractor_probe(
            run_dir,
            out,
            fake_boundary_payload=_fake_boundary_payload(),
        )

    assert not out.exists()


def test_real_boundary_probe_records_sanitized_model_calls_and_cost(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(tmp_path)

    probe = build_real_specialist_extractor_probe(
        run_dir,
        boundary=_RecordingBoundary(),
        specialists=["live_constraints", "stance", "dropped_threads"],
    )
    rendered = render_specialist_extractor_probe_json(probe)

    assert probe["boundary_mode"] == "real"
    assert probe["model_calls_made"] is True
    assert probe["model_call_count"] == 3
    assert probe["model_usage"]["estimated_total_cost_usd"] > 0
    assert [call["stage"] for call in probe["boundary_calls"]] == [
        "specialist_probe.live_constraints",
        "specialist_probe.stance",
        "specialist_probe.dropped_threads",
    ]
    assert probe["specialists"]["live_constraints"]["did_improve_coverage"] is True
    assert probe["specialists"]["stance"]["did_improve_coverage"] is True
    assert probe["specialists"]["dropped_threads"]["did_improve_coverage"] is True
    assert "SECRET RAW MODEL MESSAGE" not in rendered
    assert "raw_message_content" not in rendered
    assert "SECRET" not in rendered
    assert "/Users/" not in rendered
    assert "six users ready" not in rendered


def test_real_library_rejects_output_inside_run_dir(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)
    out = run_dir / "real-probe.json"

    with pytest.raises(ValueError, match="out path must not be inside run_dir"):
        write_real_specialist_extractor_probe(
            run_dir,
            out,
            boundary=_RecordingBoundary(),
        )

    assert not out.exists()


def test_real_probe_cli_requires_explicit_approval(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)
    archive_root = run_dir.parents[1]

    exit_code = real_cli.main(
        [
            str(archive_root),
            "--run",
            "case-a/run-a",
            "--out-dir",
            str(tmp_path / "probe-runs"),
            "--json-out",
            str(tmp_path / "probe.json"),
            "--md-out",
            str(tmp_path / "probe.md"),
        ]
    )

    assert exit_code == 2


def test_real_probe_cli_writes_reports_without_archive_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_dir = _seed_run(tmp_path)
    archive_root = run_dir.parents[1]
    before = sorted(path.relative_to(archive_root) for path in archive_root.rglob("*") if path.is_file())
    out_dir = tmp_path / "probe-runs"
    json_out = tmp_path / "probe.json"
    md_out = tmp_path / "probe.md"

    from engine.system_b import boundary_provider

    monkeypatch.setattr(
        boundary_provider,
        "load_boundary_client_from_env",
        lambda _provider: _RecordingBoundary(),
    )

    exit_code = real_cli.main(
        [
            str(archive_root),
            "--run",
            "case-a/run-a",
            "--out-dir",
            str(out_dir),
            "--json-out",
            str(json_out),
            "--md-out",
            str(md_out),
            "--real-boundary-approved",
            "--all",
        ]
    )
    after = sorted(path.relative_to(archive_root) for path in archive_root.rglob("*") if path.is_file())
    rendered = json_out.read_text(encoding="utf-8") + md_out.read_text(encoding="utf-8")

    assert exit_code == 0
    assert json_out.exists()
    assert md_out.exists()
    assert (out_dir / "case-a__run-a.json").exists()
    assert before == after
    assert "SECRET" not in rendered
    assert "/Users/" not in rendered
    assert "raw_message_content" not in rendered
    assert "case-a/run-a" in rendered


def test_real_probe_cli_rejects_outputs_inside_archive_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_dir = _seed_run(tmp_path)
    archive_root = run_dir.parents[1]
    from engine.system_b import boundary_provider

    monkeypatch.setattr(
        boundary_provider,
        "load_boundary_client_from_env",
        lambda _provider: _RecordingBoundary(),
    )

    exit_code = real_cli.main(
        [
            str(archive_root),
            "--run",
            "case-a/run-a",
            "--out-dir",
            str(archive_root / "probe-runs"),
            "--json-out",
            str(tmp_path / "probe.json"),
            "--md-out",
            str(tmp_path / "probe.md"),
            "--real-boundary-approved",
        ]
    )

    assert exit_code == 2
    assert not (archive_root / "probe-runs").exists()


def test_real_probe_cli_rejects_non_openrouter_provider_without_outputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_dir = _seed_run(tmp_path)
    archive_root = run_dir.parents[1]
    out_dir = tmp_path / "probe-runs"
    json_out = tmp_path / "probe.json"
    md_out = tmp_path / "probe.md"
    from engine.system_b import boundary_provider

    def fail_if_called(_provider: str) -> _RecordingBoundary:
        raise AssertionError("boundary client should not be loaded")

    monkeypatch.setattr(
        boundary_provider,
        "load_boundary_client_from_env",
        fail_if_called,
    )

    exit_code = real_cli.main(
        [
            str(archive_root),
            "--run",
            "case-a/run-a",
            "--out-dir",
            str(out_dir),
            "--json-out",
            str(json_out),
            "--md-out",
            str(md_out),
            "--provider",
            "openai",
            "--real-boundary-approved",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "real specialist probe currently supports openrouter cost telemetry only" in captured.err
    assert not out_dir.exists()
    assert not json_out.exists()
    assert not md_out.exists()


def test_cli_fails_cleanly_for_missing_run_dir(tmp_path: Path) -> None:
    fixture = tmp_path / "fake_boundary.json"
    fixture.write_text(json.dumps(_fake_boundary_payload()), encoding="utf-8")

    exit_code = cli_main(
        [
            str(tmp_path / "missing"),
            "--fake-boundary",
            str(fixture),
            "--out",
            str(tmp_path / "probe.json"),
        ]
    )

    assert exit_code == 2


def test_cli_fails_cleanly_for_malformed_fake_boundary(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)
    fixture = tmp_path / "fake_boundary.json"
    fixture.write_text("{not-json", encoding="utf-8")

    exit_code = cli_main(
        [
            str(run_dir),
            "--fake-boundary",
            str(fixture),
            "--out",
            str(tmp_path / "probe.json"),
        ]
    )

    assert exit_code == 2
