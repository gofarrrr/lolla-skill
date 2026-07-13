from __future__ import annotations

import json
import signal
from dataclasses import dataclass
from pathlib import Path

import pytest

from scripts.evals import run_core_semantic_corpus as runner


@dataclass
class _Call:
    stage: str
    status: str = "ok"
    raw_message_content: str = "must not persist"

    def to_dict(self) -> dict[str, object]:
        return {
            "stage": self.stage,
            "status": self.status,
            "raw_message_content": self.raw_message_content,
        }


class _Provider:
    def __init__(self) -> None:
        self.call_log: list[_Call] = []


def test_stage_mapping_covers_each_focused_reader() -> None:
    assert runner._stage_for_prompt("LIVE CONSTRAINTS") == (
        "core_semantic_shadow.live_constraints"
    )
    assert runner._stage_for_prompt("STANCE EVENT") == (
        "core_semantic_shadow.assistant_stances"
    )
    assert runner._stage_for_prompt("DROPPED THREADS") == (
        "core_semantic_shadow.dropped_threads"
    )
    assert runner._stage_for_prompt("QUESTION TRAJECTORY SEMANTICS") == (
        "core_semantic_shadow.question_trajectory"
    )
    assert runner._stage_for_prompt("USER PRESSURE SEMANTICS") == (
        "core_semantic_shadow.user_pressure"
    )
    assert runner._stage_for_prompt("USER COUNTER-PRESSURE SEMANTICS") == (
        "core_semantic_shadow.user_pressure"
    )
    assert runner._stage_for_prompt(
        "USER COUNTER-PRESSURE TEMPORAL SEMANTICS"
    ) == "core_semantic_shadow.user_pressure"
    assert runner._stage_for_prompt("OPTION AND EVIDENCE SEMANTICS") == (
        "core_semantic_shadow.option_evidence"
    )


@pytest.mark.skipif(
    not hasattr(signal, "raise_signal") or not hasattr(signal, "setitimer"),
    reason="POSIX wall-clock signal is unavailable",
)
def test_wall_clock_guard_interrupts_and_names_the_in_flight_stage() -> None:
    with pytest.raises(runner.EvaluationCallWallTimeout) as caught:
        with runner._wall_clock_guard(seconds=30, stage="reader.stage"):
            signal.raise_signal(signal.SIGALRM)

    assert caught.value.stage == "reader.stage"
    assert caught.value.timeout_seconds == 30


def test_stage_boundary_fails_closed_on_recorded_provider_failure() -> None:
    class FailedProvider(_Provider):
        def run_json(
            self,
            system_prompt: str,
            user_prompt: str,
            *,
            stage: str,
        ) -> dict[str, object]:
            del system_prompt, user_prompt
            self.call_log.append(_Call(stage=stage, status="timeout"))
            return {}

    boundary = runner._StageBoundary(FailedProvider(), wall_timeout=0)

    with pytest.raises(runner.EvaluationBoundaryCallFailure) as caught:
        boundary.run_json("QUESTION TRAJECTORY SEMANTICS", "source")

    assert caught.value.stage == "core_semantic_shadow.question_trajectory"
    assert caught.value.provider_status == "timeout"


def test_stage_boundary_retries_ok_response_missing_required_output_keys() -> None:
    class MalformedProvider(_Provider):
        def run_json(
            self,
            system_prompt: str,
            user_prompt: str,
            *,
            stage: str,
        ) -> dict[str, object]:
            del system_prompt, user_prompt
            self.call_log.append(_Call(stage=stage, status="ok"))
            return {}

    boundary = runner._StageBoundary(MalformedProvider(), wall_timeout=0)

    with pytest.raises(runner.EvaluationBoundaryCallFailure) as caught:
        boundary.run_json("OPTION AND EVIDENCE SEMANTICS", "source")

    assert caught.value.stage == "core_semantic_shadow.option_evidence"
    assert caught.value.provider_status == (
        "invalid_output_contract_missing_keys:"
        "evidence_boundary_events,option_events"
    )


def test_shadow_retry_preserves_failure_custody_and_only_missing_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _Provider()
    boundary = runner._StageBoundary(provider, wall_timeout=90)
    output = tmp_path / "shadow-01.json"
    invocation_count = 0

    def fake_run_shadow(**kwargs: object) -> None:
        nonlocal invocation_count
        invocation_count += 1
        if invocation_count == 1:
            provider.call_log.append(_Call(stage="completed.reader"))
            raise runner.EvaluationCallWallTimeout(
                stage="stuck.reader",
                timeout_seconds=90,
            )
        Path(str(kwargs["output_path"])).write_text(
            json.dumps(
                {
                    "schema_version": "lolla.core_semantic_shadow.v0",
                    "semantic_candidate_ledger": {
                        "reader_calls": [
                            {
                                "reader_role": role,
                                "raw_candidate_counts": {
                                    key: 0
                                    for key in runner.REQUIRED_RAW_COUNT_KEYS_BY_ROLE[
                                        role
                                    ]
                                },
                            }
                            for role in runner.EXPECTED_SHADOW_READER_ROLES
                        ]
                    },
                }
            ),
            encoding="utf-8",
        )

    monkeypatch.setattr(runner, "_run_shadow", fake_run_shadow)

    runner._run_shadow_with_retries(
        case_id="case-test",
        repeat=1,
        conversation_path=tmp_path / "conversation.txt",
        context_extraction_path=tmp_path / "compact.json",
        output_path=output,
        boundary=boundary,
    )

    error_path = tmp_path / "shadow-01-attempt-01.error.json"
    error = json.loads(error_path.read_text(encoding="utf-8"))
    artifact = json.loads(output.read_text(encoding="utf-8"))

    assert invocation_count == 2
    assert error["status"] == "wall_clock_timeout"
    assert error["failed_stage"] == "stuck.reader"
    assert error["in_flight_call_recorded"] is False
    assert error["completed_calls_before_failure"] == [
        {"stage": "completed.reader", "status": "ok"}
    ]
    assert "must not persist" not in error_path.read_text(encoding="utf-8")
    assert artifact["evaluation_execution"] == {
        "failed_attempts_before_success": 1,
        "bounded_retry_limit": 3,
        "per_call_wall_timeout_seconds": 90,
    }
