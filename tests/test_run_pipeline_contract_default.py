"""CLI/runtime contract tests for scripts/run_pipeline.py.

These tests exercise the public CLI entry point while patching live pipeline
loading and post-processing calls, so they never call OpenRouter.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.run_pipeline as run_pipeline


def _write_extraction_and_conversation(
    tmp_path: Path,
    *,
    include_legacy_fields: bool = True,
) -> tuple[Path, Path]:
    extraction_path = tmp_path / "extraction.json"
    conversation_path = tmp_path / "conversation.txt"
    payload = {
        "status": "ok",
        "extraction": {
            "is_strategic": True,
            "decision_situation": "Should we accept the offer?",
            "live_constraints": [
                {
                    "constraint": "Budget is capped.",
                    "introduced_turn": 1,
                    "status": "active",
                    "weight": "structural",
                }
            ],
            "synthesized_position": "Accept it with safeguards.",
            "reasoning_passages": ["Accept it with safeguards."],
            "original_framing": "Is this too risky?",
            "dropped_threads": [],
            "_quote_validation": {"fabricated": 0},
        },
        "capture_health": "good",
        "capture_warnings": [],
        "capture_manifest": {
            "declared_turns": 1,
            "actual_user_turns": 1,
            "actual_assistant_turns": 1,
        },
    }
    if include_legacy_fields:
        payload.update(
            {
                "query": "Should we accept the offer?",
                "vanilla_answer": "Accept it with safeguards.",
            }
        )
    extraction_path.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    conversation_path.write_text(
        "CONVERSATION: 1 turn, 1 user message, 1 assistant response\n\n"
        "[Turn 1] USER:\n"
        "Should we accept the offer?\n\n"
        "[Turn 1] ASSISTANT:\n"
        "Accept it with safeguards.\n",
        encoding="utf-8",
    )
    return extraction_path, conversation_path


def _install_live_pipeline_fakes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    bundle_chunks: tuple[object, ...] | None = None,
    companion_fingerprints: tuple[object, ...] = (),
    audit_warnings: tuple[str, ...] = (),
    embedding_retriever: object | None = None,
) -> list[object]:
    import system_b.boundary_provider as boundary_provider
    import system_b.bullshit_index as bullshit_index
    import system_b.pipeline as pipeline_mod

    captured_inputs: list[object] = []

    class _FakeSubstrate:
        def all_chunks(self) -> tuple[object, ...]:
            return bundle_chunks or ()

    class _FakeBundleSelector:
        _substrate = _FakeSubstrate()

    class _FakePipeline:
        _embedding_retriever = embedding_retriever
        _bundle_selector = _FakeBundleSelector() if bundle_chunks is not None else None

        def run(self, pipeline_input: object) -> object:
            captured_inputs.append(pipeline_input)
            return SimpleNamespace(
                delta_card=SimpleNamespace(findings=[]),
                frame_pressure_card=None,
                audit=SimpleNamespace(
                    warnings=list(audit_warnings),
                    companion_fingerprint_validated=list(companion_fingerprints),
                ),
                prompt_versions={},
            )

    class _FakeBullshitProfile:
        def to_payload(self) -> dict:
            return {"status": "skipped-test-double"}

    def _load_live(cls, *, root, provider_name, config):  # noqa: ANN001, ARG001
        return _FakePipeline()

    monkeypatch.setattr(run_pipeline, "_resolve_data_root", lambda: tmp_path)
    monkeypatch.setattr(run_pipeline, "_serialize_result", lambda result, **kwargs: {})
    monkeypatch.setattr(pipeline_mod.SystemBPipeline, "load_live", classmethod(_load_live))
    monkeypatch.setattr(boundary_provider, "load_boundary_client_from_env", lambda provider_name: object())
    monkeypatch.setattr(
        bullshit_index,
        "evaluate_text",
        lambda text, client, *, context_summary: _FakeBullshitProfile(),
    )
    return captured_inputs


def _install_clean_health_pipeline_fakes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    embedding_retriever: object | None = None,
) -> list[object]:
    return _install_live_pipeline_fakes(
        monkeypatch,
        tmp_path,
        bundle_chunks=(object(),),
        companion_fingerprints=(object(),),
        embedding_retriever=embedding_retriever,
    )


def test_file_inputs_with_conversation_use_conversation_context_by_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import system_b.conversation_context as context_mod

    extraction_path, conversation_path = _write_extraction_and_conversation(tmp_path)
    output_path = tmp_path / "result.json"
    captured_inputs = _install_live_pipeline_fakes(monkeypatch, tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_pipeline.py",
            "--extraction-file",
            str(extraction_path),
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
            "--skip-revision",
        ],
    )

    assert run_pipeline.main() == 0
    assert len(captured_inputs) == 1
    assert isinstance(captured_inputs[0], context_mod.ConversationContext)


def test_file_inputs_do_not_require_legacy_query_answer_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import system_b.conversation_context as context_mod

    extraction_path, conversation_path = _write_extraction_and_conversation(
        tmp_path,
        include_legacy_fields=False,
    )
    output_path = tmp_path / "result.json"
    captured_inputs = _install_live_pipeline_fakes(monkeypatch, tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_pipeline.py",
            "--extraction-file",
            str(extraction_path),
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
            "--skip-revision",
        ],
    )

    assert run_pipeline.main() == 0
    assert len(captured_inputs) == 1
    assert isinstance(captured_inputs[0], context_mod.ConversationContext)


def test_postprocessing_uses_conversation_context_before_stale_legacy_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import system_b.bullshit_index as bullshit_index

    extraction_path, conversation_path = _write_extraction_and_conversation(tmp_path)
    payload = json.loads(extraction_path.read_text(encoding="utf-8"))
    payload["query"] = "STALE LEGACY QUERY"
    payload["vanilla_answer"] = "STALE LEGACY ANSWER"
    extraction_path.write_text(json.dumps(payload), encoding="utf-8")

    output_path = tmp_path / "result.json"
    _install_live_pipeline_fakes(monkeypatch, tmp_path)
    captured_bi: dict[str, str] = {}

    class _FakeBullshitProfile:
        def to_payload(self) -> dict:
            return {"status": "skipped-test-double"}

    def _capture_bi(text, client, *, context_summary):  # noqa: ANN001, ARG001
        captured_bi["text"] = text
        captured_bi["context_summary"] = context_summary
        return _FakeBullshitProfile()

    monkeypatch.setattr(bullshit_index, "evaluate_text", _capture_bi)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_pipeline.py",
            "--extraction-file",
            str(extraction_path),
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
            "--skip-revision",
        ],
    )

    assert run_pipeline.main() == 0
    assert captured_bi["text"] == "Accept it with safeguards."
    assert "STALE LEGACY" not in captured_bi["text"]
    assert "Decision: Should we accept the offer?" in captured_bi["context_summary"]


def test_new_contract_flag_with_file_inputs_still_uses_conversation_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import system_b.conversation_context as context_mod

    extraction_path, conversation_path = _write_extraction_and_conversation(tmp_path)
    output_path = tmp_path / "result.json"
    captured_inputs = _install_live_pipeline_fakes(monkeypatch, tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_pipeline.py",
            "--extraction-file",
            str(extraction_path),
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
            "--skip-revision",
            "--new-contract",
        ],
    )

    assert run_pipeline.main() == 0
    assert len(captured_inputs) == 1
    assert isinstance(captured_inputs[0], context_mod.ConversationContext)


def test_stakeholder_check_disabled_by_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import system_b.stakeholder_assumption_check as stakeholder_check

    extraction_path, conversation_path = _write_extraction_and_conversation(tmp_path)
    output_path = tmp_path / "result.json"
    _install_live_pipeline_fakes(monkeypatch, tmp_path)

    def _fail_if_called(**kwargs):  # noqa: ANN003
        raise AssertionError("stakeholder check should be disabled by default")

    monkeypatch.delenv("LOLLA_STAKEHOLDER_CHECK", raising=False)
    monkeypatch.setattr(stakeholder_check, "run_stakeholder_assumption_check", _fail_if_called)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_pipeline.py",
            "--extraction-file",
            str(extraction_path),
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
            "--skip-revision",
        ],
    )

    assert run_pipeline.main() == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert "stakeholder_assumption_check" not in payload


def test_v60_enrichment_can_be_disabled_by_cli(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    extraction_path, conversation_path = _write_extraction_and_conversation(tmp_path)
    output_path = tmp_path / "result.json"
    _install_live_pipeline_fakes(monkeypatch, tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_pipeline.py",
            "--extraction-file",
            str(extraction_path),
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
            "--skip-revision",
            "--v60-enrichment",
            "off",
        ],
    )

    assert run_pipeline.main() == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["v60_enrichment"]["status"] == "disabled"
    assert payload["run_health"]["v60_enrichment"] == "disabled"
    assert "v60_enrichment_failed" not in payload["run_health"]["issues"]


def test_stakeholder_check_flag_persists_payload_and_usage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import system_b.stakeholder_assumption_check as stakeholder_check

    extraction_path, conversation_path = _write_extraction_and_conversation(tmp_path)
    output_path = tmp_path / "result.json"
    _install_live_pipeline_fakes(monkeypatch, tmp_path)

    class _FakeBoundary:
        call_log = []

    def _fake_load_boundary(provider_name: str):  # noqa: ARG001
        return _FakeBoundary()

    call_record = {
        "stage": "stakeholder_assumption_check",
        "provider_name": "openrouter",
        "model": "fake-model",
        "status": "ok",
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
    }

    def _fake_check(**kwargs):  # noqa: ANN003
        assert isinstance(kwargs["boundary"], _FakeBoundary)
        return (
            {
                "status": "completed",
                "triggered": True,
                "surface": True,
                "critical_actors": [{"display_name": "advisor", "plan_change": "Ask first."}],
            },
            [call_record],
        )

    monkeypatch.setenv("LOLLA_STAKEHOLDER_CHECK", "1")
    monkeypatch.setattr(stakeholder_check, "run_stakeholder_assumption_check", _fake_check)
    monkeypatch.setattr("system_b.boundary_provider.load_boundary_client_from_env", _fake_load_boundary)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_pipeline.py",
            "--extraction-file",
            str(extraction_path),
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
            "--skip-revision",
        ],
    )

    assert run_pipeline.main() == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["stakeholder_assumption_check"]["status"] == "completed"
    stages = payload["usage_summary"]["vendors"]["openrouter"]["stages"]
    assert "stakeholder_assumption_check" in stages
    assert stages["stakeholder_assumption_check"]["calls"] == 1


def test_triggered_stakeholder_check_failure_degrades_run_health(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import system_b.stakeholder_assumption_check as stakeholder_check

    extraction_path, conversation_path = _write_extraction_and_conversation(tmp_path)
    output_path = tmp_path / "result.json"
    _install_live_pipeline_fakes(monkeypatch, tmp_path)

    def _fake_check(**kwargs):  # noqa: ANN003
        return (
            {
                "status": "skipped_error",
                "triggered": True,
                "surface": False,
                "error": "test failure",
                "critical_actors": [],
            },
            [],
        )

    monkeypatch.setenv("LOLLA_STAKEHOLDER_CHECK", "1")
    monkeypatch.setattr(stakeholder_check, "run_stakeholder_assumption_check", _fake_check)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_pipeline.py",
            "--extraction-file",
            str(extraction_path),
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
            "--skip-revision",
        ],
    )

    assert run_pipeline.main() == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["stakeholder_assumption_check"]["status"] == "skipped_error"
    assert "stakeholder_check_failed" in payload["run_health"]["issues"]
    assert payload["run_health"]["overall"] == "degraded"


def test_optional_embeddings_off_is_visible_without_degrading_run_health(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    extraction_path, conversation_path = _write_extraction_and_conversation(tmp_path)
    output_path = tmp_path / "result.json"
    _install_clean_health_pipeline_fakes(monkeypatch, tmp_path)

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_pipeline.py",
            "--env-file",
            str(tmp_path / "no-env"),
            "--extraction-file",
            str(extraction_path),
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
            "--skip-revision",
            "--v60-enrichment",
            "off",
        ],
    )

    assert run_pipeline.main() == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload["run_health"]["overall"] == "healthy"
    assert "embeddings_off" in payload["run_health"]["issues"]
    assert {
        "code": "embeddings_off",
        "severity": "optional_off",
        "axis": "retrieval",
    } in [
        {
            "code": detail["code"],
            "severity": detail["severity"],
            "axis": detail["axis"],
        }
        for detail in payload["run_health"]["issue_details"]
    ]


def test_capture_critical_remains_critical_with_health_issue_details(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    extraction_path, conversation_path = _write_extraction_and_conversation(tmp_path)
    payload = json.loads(extraction_path.read_text(encoding="utf-8"))
    payload["capture_health"] = "critical"
    extraction_path.write_text(json.dumps(payload), encoding="utf-8")
    output_path = tmp_path / "result.json"
    _install_clean_health_pipeline_fakes(monkeypatch, tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_pipeline.py",
            "--extraction-file",
            str(extraction_path),
            "--conversation-file",
            str(conversation_path),
            "--output-file",
            str(output_path),
            "--skip-revision",
            "--v60-enrichment",
            "off",
        ],
    )

    assert run_pipeline.main() == 0
    result = json.loads(output_path.read_text(encoding="utf-8"))

    assert result["run_health"]["overall"] == "critical"
    capture_detail = next(
        detail
        for detail in result["run_health"]["issue_details"]
        if detail["code"] == "capture_critical"
    )
    assert capture_detail["severity"] == "critical"
    assert capture_detail["axis"] == "capture"


def test_extraction_file_without_conversation_file_requires_conversation_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    extraction_path, _conversation_path = _write_extraction_and_conversation(tmp_path)
    output_path = tmp_path / "result.json"
    captured_inputs = _install_live_pipeline_fakes(monkeypatch, tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_pipeline.py",
            "--extraction-file",
            str(extraction_path),
            "--output-file",
            str(output_path),
            "--skip-revision",
        ],
    )

    assert run_pipeline.main() == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "error"
    assert "--extraction-file requires --conversation-file" in payload["error"]
    assert captured_inputs == []


def test_extraction_json_returns_structured_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_path = tmp_path / "result.json"
    captured_inputs = _install_live_pipeline_fakes(monkeypatch, tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_pipeline.py",
            "--extraction-json",
            json.dumps(
                {
                    "query": "Should we accept the offer?",
                    "vanilla_answer": "Accept it with safeguards.",
                }
            ),
            "--output-file",
            str(output_path),
            "--skip-revision",
        ],
    )

    assert run_pipeline.main() == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "error"
    assert "--extraction-json is no longer supported" in payload["error"]
    assert captured_inputs == []


def test_extraction_file_and_extraction_json_remain_argparse_mutually_exclusive(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    extraction_path, _conversation_path = _write_extraction_and_conversation(tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_pipeline.py",
            "--extraction-file",
            str(extraction_path),
            "--extraction-json",
            json.dumps({"query": "q", "vanilla_answer": "a"}),
            "--skip-revision",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        run_pipeline.main()

    assert exc_info.value.code == 2
    assert "not allowed with argument" in capsys.readouterr().err
