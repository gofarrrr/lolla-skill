from __future__ import annotations

import copy
import io
import json
import os
import pty
import select
import subprocess
import sys
import time
from pathlib import Path

from engine.system_b.constitutional_graph_survival import (
    build_constitutional_graph_survival,
)
from engine.system_b.output_hygiene import finalize_live_output_hygiene
from engine.system_b.pre_step6_private_table import build_pre_step6_private_table
from engine.system_b.reasoning_trace import build_reasoning_trace
from scripts.skill import persist_private_artifact
from scripts.skill import prepare_consumer_packet


ROOT = Path(__file__).resolve().parents[1]


def _graph_portfolio() -> dict:
    knowledge = json.loads(
        (ROOT / "data" / "knowledge_graph.json").read_text(encoding="utf-8")
    )
    relations = json.loads(
        (ROOT / "data" / "relationship_graph.json").read_text(encoding="utf-8")
    )
    candidates = [
        {
            "model_id": model_id,
            "model_name": model_id,
            "recall_source": "fixture",
            "final_rank": index,
        }
        for index, model_id in enumerate(
            ["expected-value", "inversion", "opportunity-cost"],
            start=1,
        )
    ]
    return build_constitutional_graph_survival(
        candidates=candidates,
        knowledge_graph=knowledge,
        relationship_graph=relations,
    )


def _private_table(result: dict) -> dict:
    payload, _ = build_pre_step6_private_table(
        result_payload={
            **result,
            "delta_card": {
                "top_findings": [
                    {
                        "tendency_id": "loss-aversion",
                        "tendency_name": "Loss aversion",
                        "severity": "high",
                        "specific_passage": "The refusal branch was priced as collapse.",
                        "challenge_statement": "The numbers were not source-supported.",
                        "next_move": "Use ranges and evidence gates.",
                    }
                ]
            },
        }
    )
    return payload


def _v60_enrichment() -> dict:
    transaction = {
        "card_id": "v60-card-001-expected-value",
        "model_id": "expected-value",
        "selection_source": "fixture",
        "selection_reason": "The answer used unsupported arithmetic.",
        "source_file": "fixture.json",
        "disposition": "",
        "route": "",
        "strongest_plausible_application": "",
        "why": "",
        "visible_effect": "",
        "private_guardrail": "",
        "risk_if_forced": "",
        "technical_blocker": "",
        "chunk_id": "aff::expected-value.test",
        "chunk_kind": "affordance",
        "affordance_id": "test",
        "chunk_status": "active",
        "chunk_source_file": "fixture.json",
    }
    return {
        "status": "active",
        "telemetry": {"selected_chunk_ids": [transaction["chunk_id"]]},
        "consideration_ledger_skeleton": {
            "schema_version": "v60_skill_consideration_ledger.v2",
            "transactions": [transaction],
        },
    }


def _valid_decisions(result: dict) -> dict:
    graph = {}
    for item in result["constitutional_graph_survival"][
        "disposition_ledger_skeleton"
    ]["items"]:
        graph[item["pressure_id"]] = {
            "disposition": "reject",
            "strongest_plausible_application": "Test the strongest case-specific use.",
            "attempted_application_condition": "The mechanism needs source evidence.",
            "why": "The fixture does not establish the mechanism.",
            "failed_condition": "No source evidence establishes the mechanism.",
            "reopen_condition": "",
            "visible_effect": "",
            "private_guardrail": "",
            "risk_if_forced": "A hypothesis would become a fact.",
            "risk_if_ignored": "A useful edge could remain untested.",
        }

    private_table = {}
    for item in result["pre_step6_private_table"]["consideration_ledger_skeleton"][
        "items"
    ]:
        private_table[item["source_id"]] = {
            "disposition": "rejected",
            "why": "This source did not change the answer.",
            "visible_effect": "",
            "private_guardrail": "",
        }

    v60 = {
        "aff::expected-value.test": {
            "disposition": "used",
            "route": "evidence_gate",
            "strongest_plausible_application": "Block unsupported arithmetic.",
            "why": "The original answer presented invented values as analysis.",
            "visible_effect": "The revision withdraws the numerical ranking.",
            "private_guardrail": "",
            "risk_if_forced": "",
            "technical_blocker": "",
        }
    }
    return {
        "revised_answer": "## Updated position\n\nUse a dated diligence process.",
        "graph_decisions": graph,
        "private_table_decisions": private_table,
        "v60_decisions": v60,
    }


def _write_result(tmp_path: Path, run_id: str) -> tuple[Path, dict]:
    result: dict = {
        "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
        "constitutional_graph_survival": _graph_portfolio(),
        "v60_enrichment": _v60_enrichment(),
    }
    result["pre_step6_private_table"] = _private_table(result)
    path = tmp_path / f"lolla_{run_id}_result.json"
    path.write_text(json.dumps(result), encoding="utf-8")
    path.chmod(0o600)
    return path, result


def test_fresh_shell_loads_only_the_exact_requested_run_state(tmp_path: Path) -> None:
    requested = "requested_run"
    stale = "stale_run"
    requested_state = tmp_path / f"lolla_{requested}_env.sh"
    stale_state = tmp_path / f"lolla_{stale}_env.sh"
    requested_state.write_text(
        f"export LOLLA_RUN_ID={requested}\n"
        f"export LOLLA_EXPECTED_RUN_ID={requested}\n"
        f"export SKILL_DIR={ROOT}\n",
        encoding="utf-8",
    )
    stale_state.write_text(
        f"export LOLLA_RUN_ID={stale}\n"
        f"export LOLLA_EXPECTED_RUN_ID={stale}\n"
        f"export SKILL_DIR={ROOT}\n",
        encoding="utf-8",
    )
    latest = tmp_path / "lolla_latest_env.sh"
    latest.symlink_to(stale_state)

    result = subprocess.run(
        [
            "bash",
            "-c",
            (
                f'. "{ROOT / "scripts/skill/load_run_state.sh"}"; '
                f'lolla_load_run_state "{requested}"; '
                "printf '%s|%s' \"$LOLLA_RUN_ID\" \"$LOLLA_EXPECTED_RUN_ID\""
            ),
        ],
        text=True,
        capture_output=True,
        env={
            **os.environ,
            "LOLLA_TMP_DIR": str(tmp_path),
            "LOLLA_LATEST_ENV_STATE": str(latest),
            "LOLLA_RUN_ID": "",
            "LOLLA_EXPECTED_RUN_ID": "",
            "LOLLA_ENV_STATE": "",
        },
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == f"{requested}|{requested}"


def test_setup_quotes_runtime_state_for_fresh_shells(tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime $(touch SHOULD_NOT_EXIST)"
    completed = subprocess.run(
        ["bash", str(ROOT / "scripts/skill/setup.sh")],
        text=True,
        capture_output=True,
        env={
            **os.environ,
            "LOLLA_TMP_DIR": str(runtime_root),
            "OPENROUTER_API_KEY": "provider-free-fixture-key",
            "LOLLA_OPENROUTER_API_KEY": "",
            "OPENAI_API_KEY": "",
        },
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    run_line = next(
        line for line in completed.stdout.splitlines() if line.startswith("RUN_HANDLE: ")
    )
    run_id = run_line.removeprefix("RUN_HANDLE: ")
    state_path = runtime_root / f"lolla_{run_id}_env.sh"
    assert state_path.exists()
    assert state_path.stat().st_mode & 0o777 == 0o600

    loaded = subprocess.run(
        [
            "bash",
            "-c",
            '. "$1"; printf "%s|%s" "$LOLLA_RUN_ID" "$LOLLA_TMP_DIR"',
            "bash",
            str(state_path),
        ],
        text=True,
        capture_output=True,
        cwd=tmp_path,
        check=False,
    )
    assert loaded.returncode == 0, loaded.stderr
    assert loaded.stdout == f"{run_id}|{runtime_root}"
    assert not (tmp_path / "SHOULD_NOT_EXIST").exists()


def test_ordinary_private_consumer_and_pressure_wrappers_reload_exact_state(
    tmp_path: Path,
) -> None:
    run_id = "fresh_wrapper_run"
    transcript = tmp_path / f"lolla_{run_id}_live_transcript.txt"
    operator = tmp_path / f"lolla_{run_id}_operator.log"
    state = tmp_path / f"lolla_{run_id}_env.sh"
    transcript.write_text("", encoding="utf-8")
    operator.write_text("", encoding="utf-8")
    state.write_text(
        "\n".join(
            [
                "umask 077",
                f"export SKILL_DIR={ROOT}",
                f"export LOLLA_RUN_ID={run_id}",
                f"export LOLLA_EXPECTED_RUN_ID={run_id}",
                f"export LOLLA_LIVE_TRANSCRIPT={transcript}",
                f"export LOLLA_OPERATOR_LOG={operator}",
                f"export LOLLA_ENV_STATE={state}",
                f"export LOLLA_TMP_DIR={tmp_path}",
                "export LOLLA_AUDIT_MODE=standard",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for private_file in (transcript, operator, state):
        private_file.chmod(0o600)

    extraction_path = tmp_path / f"lolla_{run_id}_extraction.json"
    extraction_path.write_text(
        json.dumps(
            {
                "status": "ok",
                "extraction": {
                    "decision_situation": "Choose a bounded next step.",
                    "live_constraints": [],
                    "synthesized_position": "Proceed carefully.",
                    "reasoning_passages": [],
                    "original_framing": "",
                    "dropped_threads": [],
                },
            }
        ),
        encoding="utf-8",
    )
    extraction_path.chmod(0o600)
    _write_result(tmp_path, run_id)

    fresh_env = {
        **os.environ,
        "LOLLA_TMP_DIR": str(tmp_path),
        "LOLLA_RUN_ID": "",
        "LOLLA_EXPECTED_RUN_ID": "",
        "LOLLA_ENV_STATE": "",
    }
    consumer = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts/skill/prepare_consumer_step.sh"),
            "--run-id",
            run_id,
            "--stage",
            "readback",
        ],
        text=True,
        capture_output=True,
        env=fresh_env,
        check=False,
    )
    assert consumer.returncode == 0, consumer.stderr
    assert consumer.stdout == "CONSUMER_PACKET_STATUS: readback ready\n"

    narration_marker = "PRIVATE_FRESH_SHELL_NARRATION"
    narration = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts/skill/persist_private_step.sh"),
            "--run-id",
            run_id,
            "--kind",
            "narration",
        ],
        input=narration_marker,
        text=True,
        capture_output=True,
        env=fresh_env,
        check=False,
    )
    assert narration.returncode == 0, narration.stderr
    assert narration_marker not in narration.stdout + narration.stderr
    assert transcript.read_text(encoding="utf-8").strip() == narration_marker

    pressure = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts/skill/persist_default_pressure_step.sh"),
            "--run-id",
            run_id,
        ],
        text=True,
        capture_output=True,
        env=fresh_env,
        check=False,
    )
    assert pressure.returncode == 0, pressure.stderr
    assert pressure.stdout == "PRESSURE_CHECK_STATUS: default_off ready\n"


def test_private_step6_persistence_accepts_only_mutable_fields_and_hides_payload(
    tmp_path: Path,
) -> None:
    run_id = "private_step6"
    result_path, original = _write_result(tmp_path, run_id)
    transcript = tmp_path / f"lolla_{run_id}_live_transcript.txt"
    transcript.write_text("", encoding="utf-8")
    packet = _valid_decisions(original)
    private_marker = "PRIVATE_MARKER_DO_NOT_ECHO"
    packet["revised_answer"] += f"\n\n{private_marker}"

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/skill/persist_private_artifact.py"),
            "--run-id",
            run_id,
            "--kind",
            "step6",
            "--tmp-dir",
            str(tmp_path),
        ],
        input=json.dumps(packet),
        text=True,
        capture_output=True,
        env={
            **os.environ,
            "LOLLA_RUN_ID": run_id,
            "LOLLA_EXPECTED_RUN_ID": run_id,
            "LOLLA_LIVE_TRANSCRIPT": str(transcript),
            "PYTHONPATH": str(ROOT),
        },
        check=False,
    )

    visible = completed.stdout + completed.stderr
    assert completed.returncode == 0, visible
    assert visible == (
        "PRIVATE_INPUT_READY\n"
        "PRIVATE_PERSIST_STATUS: step6 valid; graph=valid; "
        "private_table=valid; v60=valid\n"
    )
    assert private_marker not in visible
    persisted = json.loads(result_path.read_text(encoding="utf-8"))
    assert private_marker in persisted["revised_answer"]
    assert transcript.stat().st_mode & 0o777 == 0o600
    assert result_path.stat().st_mode & 0o777 == 0o600
    assert (
        persisted["constitutional_graph_survival_ledger_validation"]["status"]
        == "valid"
    )
    assert persisted["pre_step6_private_table_ledger_validation"]["status"] == "valid"
    assert persisted["v60_consideration_validation"]["status"] == "valid"

    graph_skeleton = original["constitutional_graph_survival"][
        "disposition_ledger_skeleton"
    ]["items"]
    graph_ledger = persisted["constitutional_graph_survival_ledger"]["items"]
    assert [
        (item["pressure_id"], item["model_id"], item["consumer_locator"])
        for item in graph_ledger
    ] == [
        (item["pressure_id"], item["model_id"], item["consumer_locator"])
        for item in graph_skeleton
    ]


def test_private_persistence_true_pty_waits_for_ready_and_does_not_echo(
    tmp_path: Path,
) -> None:
    run_id = "private_persist_true_pty"
    marker = "PRIVATE_NARRATION_MUST_NOT_ECHO_18c7"
    transcript = tmp_path / f"lolla_{run_id}_live_transcript.txt"
    transcript.write_text("", encoding="utf-8")
    transcript.chmod(0o600)
    env = {
        **os.environ,
        "LOLLA_RUN_ID": run_id,
        "LOLLA_EXPECTED_RUN_ID": run_id,
        "LOLLA_LIVE_TRANSCRIPT": str(transcript),
        "PYTHONPATH": str(ROOT),
        "PYTHONUNBUFFERED": "1",
    }
    master_fd, slave_fd = pty.openpty()
    process = subprocess.Popen(
        [
            sys.executable,
            str(ROOT / "scripts/skill/persist_private_artifact.py"),
            "--run-id",
            run_id,
            "--kind",
            "narration",
            "--tmp-dir",
            str(tmp_path),
        ],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        env=env,
        close_fds=True,
    )
    os.close(slave_fd)
    output = bytearray()
    deadline = time.monotonic() + 5
    try:
        while b"PRIVATE_INPUT_READY" not in output:
            remaining = deadline - time.monotonic()
            assert remaining > 0, output.decode("utf-8", errors="replace")
            readable, _, _ = select.select([master_fd], [], [], remaining)
            assert readable
            output.extend(os.read(master_fd, 4096))
        # In canonical terminal mode EOF is recognized at the start of an
        # empty line. Terminate the private payload with a newline first so a
        # single Ctrl-D closes stdin instead of only releasing a partial line.
        os.write(master_fd, (marker + "\n").encode("utf-8"))
        os.write(master_fd, b"\x04")
        exit_deadline = time.monotonic() + 5
        while process.poll() is None:
            assert time.monotonic() < exit_deadline, output.decode(
                "utf-8", errors="replace"
            )
            readable, _, _ = select.select([master_fd], [], [], 0.1)
            if readable:
                try:
                    output.extend(os.read(master_fd, 4096))
                except OSError:
                    break
        process.wait(timeout=5)
        while True:
            readable, _, _ = select.select([master_fd], [], [], 0)
            if not readable:
                break
            try:
                chunk = os.read(master_fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            output.extend(chunk)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        os.close(master_fd)

    rendered = output.decode("utf-8", errors="replace")
    assert process.returncode == 0, rendered
    assert "PRIVATE_INPUT_READY" in rendered
    assert "PRIVATE_PERSIST_STATUS: narration ready" in rendered
    assert marker not in rendered
    assert transcript.read_text(encoding="utf-8").strip() == marker


def test_private_narration_retry_is_idempotent_and_receipt_override_is_hidden(
    tmp_path: Path,
) -> None:
    run_id = "private_text_idempotency"
    transcript = tmp_path / f"lolla_{run_id}_live_transcript.txt"
    transcript.write_text("", encoding="utf-8")
    transcript.chmod(0o600)
    env = {
        **os.environ,
        "LOLLA_RUN_ID": run_id,
        "LOLLA_EXPECTED_RUN_ID": run_id,
        "LOLLA_LIVE_TRANSCRIPT": str(transcript),
        "LOLLA_TMP_DIR": str(tmp_path),
        "PYTHONPATH": str(ROOT),
    }
    narration = "The user-facing readback appears exactly once."
    command = [
        sys.executable,
        str(ROOT / "scripts/skill/persist_private_artifact.py"),
        "--run-id",
        run_id,
        "--kind",
        "narration",
        "--tmp-dir",
        str(tmp_path),
    ]
    first = subprocess.run(
        command,
        input=narration,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    second = subprocess.run(
        command,
        input=narration,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    assert first.returncode == second.returncode == 0
    assert transcript.read_text(encoding="utf-8").count(narration) == 1

    private_receipt = "PRIVATE RECEIPT BODY MUST NOT ECHO"
    receipt = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/skill/persist_private_artifact.py"),
            "--run-id",
            run_id,
            "--kind",
            "receipt",
            "--tmp-dir",
            str(tmp_path),
        ],
        input=private_receipt,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    visible = receipt.stdout + receipt.stderr
    assert receipt.returncode == 0, visible
    assert visible == (
        "PRIVATE_INPUT_READY\n"
        "PRIVATE_PERSIST_STATUS: receipt_override ready\n"
    )
    assert private_receipt not in visible
    override = tmp_path / f"lolla_{run_id}_final_receipt_override.txt"
    assert override.read_text(encoding="utf-8").strip() == private_receipt
    assert override.stat().st_mode & 0o777 == 0o600


def test_authoritative_capture_true_pty_waits_for_ready_and_does_not_echo(
    tmp_path: Path,
) -> None:
    run_id = "capture_true_pty"
    source = (
        ROOT
        / "research/test-cases/phase2d-marcus-controlled-comparison-2026-04-24"
        / "lolla_20260422T155622Z_conversation.txt"
    ).read_text(encoding="utf-8")
    source_marker = "I run a 90-person digital agency"
    assert source_marker in source

    state = tmp_path / f"lolla_{run_id}_env.sh"
    transcript = tmp_path / f"lolla_{run_id}_live_transcript.txt"
    operator = tmp_path / f"lolla_{run_id}_operator.log"
    transcript.write_text("", encoding="utf-8")
    operator.write_text("", encoding="utf-8")
    state.write_text(
        "\n".join(
            [
                "umask 077",
                f"export SKILL_DIR={ROOT}",
                f"export LOLLA_RUN_ID={run_id}",
                f"export LOLLA_EXPECTED_RUN_ID={run_id}",
                f"export LOLLA_LIVE_TRANSCRIPT={transcript}",
                f"export LOLLA_OPERATOR_LOG={operator}",
                f"export LOLLA_ENV_STATE={state}",
                f"export LOLLA_TMP_DIR={tmp_path}",
                "export LOLLA_AUDIT_MODE=standard",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for runtime_file in (state, transcript, operator):
        runtime_file.chmod(0o600)

    master_fd, slave_fd = pty.openpty()
    process = subprocess.Popen(
        [
            "bash",
            str(ROOT / "scripts/skill/capture_step.sh"),
            "--run-id",
            run_id,
        ],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        env={
            **os.environ,
            "LOLLA_TMP_DIR": str(tmp_path),
            "LOLLA_ENV_STATE": str(state),
            "PYTHONPATH": str(ROOT),
            "PYTHONUNBUFFERED": "1",
        },
        close_fds=True,
    )
    os.close(slave_fd)
    output = bytearray()
    deadline = time.monotonic() + 5
    try:
        while b"PRIVATE_INPUT_READY" not in output:
            remaining = deadline - time.monotonic()
            assert remaining > 0, output.decode("utf-8", errors="replace")
            readable, _, _ = select.select([master_fd], [], [], remaining)
            assert readable
            output.extend(os.read(master_fd, 4096))
        os.write(master_fd, source.encode("utf-8"))
        if not source.endswith("\n"):
            os.write(master_fd, b"\n")
        os.write(master_fd, b"\x04")

        exit_deadline = time.monotonic() + 5
        while process.poll() is None:
            assert time.monotonic() < exit_deadline, output.decode(
                "utf-8", errors="replace"
            )
            readable, _, _ = select.select([master_fd], [], [], 0.1)
            if readable:
                try:
                    output.extend(os.read(master_fd, 4096))
                except OSError:
                    break
        process.wait(timeout=5)
        while True:
            readable, _, _ = select.select([master_fd], [], [], 0)
            if not readable:
                break
            try:
                chunk = os.read(master_fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            output.extend(chunk)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        os.close(master_fd)

    rendered = output.decode("utf-8", errors="replace")
    assert process.returncode == 0, rendered
    assert "PRIVATE_INPUT_READY" in rendered
    assert "CAPTURE_STATUS: ready; message_blocks=14" in rendered
    assert source_marker not in rendered
    captured = tmp_path / f"lolla_{run_id}_conversation.txt"
    assert captured.read_text(encoding="utf-8") == source
    assert captured.stat().st_mode & 0o777 == 0o600


def test_invalid_private_step6_packet_is_atomic_and_records_safe_failure(
    tmp_path: Path,
) -> None:
    run_id = "invalid_private_step6"
    result_path, original = _write_result(tmp_path, run_id)
    before = result_path.read_bytes()
    packet = _valid_decisions(original)
    first_id = next(iter(packet["graph_decisions"]))
    packet["graph_decisions"][first_id]["disposition"] = "park"
    packet["graph_decisions"][first_id]["reopen_condition"] = ""
    secret = "SECRET_PRIVATE_RATIONALE"
    packet["graph_decisions"][first_id]["why"] = secret

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/skill/persist_private_artifact.py"),
            "--run-id",
            run_id,
            "--kind",
            "step6",
            "--tmp-dir",
            str(tmp_path),
        ],
        input=json.dumps(packet),
        text=True,
        capture_output=True,
        env={
            **os.environ,
            "LOLLA_RUN_ID": run_id,
            "LOLLA_EXPECTED_RUN_ID": run_id,
            "LOLLA_OPERATOR_LOG": str(tmp_path / f"lolla_{run_id}_operator.log"),
            "PYTHONPATH": str(ROOT),
        },
        check=False,
    )

    visible = completed.stdout + completed.stderr
    assert completed.returncode != 0
    assert visible == (
        "PRIVATE_INPUT_READY\n"
        "PRIVATE_PERSIST_STATUS: step6 invalid; error_count=1; replacement=none\n"
    )
    assert secret not in visible
    assert result_path.read_bytes() == before
    events = json.loads(
        (tmp_path / f"lolla_{run_id}_run_events.json").read_text(encoding="utf-8")
    )
    failure = events["events"][-1]
    assert failure["event_type"] == "private_persistence_failed"
    assert failure["details"] == {
        "error_class": "validation_error",
        "error_count": 1,
        "kind": "step6",
        "private_payload_visible": False,
        "replacement_status": "not_written",
    }
    assert secret not in json.dumps(failure)


def test_private_persistence_event_failure_is_compact_and_has_no_traceback(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    run_id = "private_event_failure"

    def fail_event(**_kwargs) -> None:
        raise OSError("private-event-marker-must-not-be-visible")

    monkeypatch.setattr(persist_private_artifact, "append_run_event", fail_event)
    monkeypatch.setenv("LOLLA_RUN_ID", run_id)
    monkeypatch.setenv("LOLLA_EXPECTED_RUN_ID", run_id)
    monkeypatch.setenv(
        "LOLLA_LIVE_TRANSCRIPT",
        str(tmp_path / f"lolla_{run_id}_live_transcript.txt"),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "persist_private_artifact.py",
            "--run-id",
            run_id,
            "--kind",
            "narration",
            "--tmp-dir",
            str(tmp_path),
        ],
    )
    monkeypatch.setattr(sys, "stdin", io.StringIO("private narration"))

    assert persist_private_artifact.main() == 2
    captured = capsys.readouterr()
    visible = captured.out + captured.err
    assert "PRIVATE_INPUT_READY" in visible
    assert (
        "PRIVATE_PERSIST_STATUS: narration incomplete; "
        "replacement=written; event_custody=failed"
    ) in visible
    assert "Traceback" not in visible
    assert "private-event-marker-must-not-be-visible" not in visible


def test_consumer_event_failure_is_compact_and_has_no_traceback(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    run_id = "consumer_event_failure"
    (tmp_path / f"lolla_{run_id}_extraction.json").write_text(
        json.dumps({"status": "ok", "extraction": {}}),
        encoding="utf-8",
    )

    def fail_event(**_kwargs) -> None:
        raise OSError("consumer-event-marker-must-not-be-visible")

    monkeypatch.setattr(prepare_consumer_packet, "append_run_event", fail_event)
    monkeypatch.setenv("LOLLA_RUN_ID", run_id)
    monkeypatch.setenv("LOLLA_EXPECTED_RUN_ID", run_id)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prepare_consumer_packet.py",
            "--run-id",
            run_id,
            "--stage",
            "readback",
            "--tmp-dir",
            str(tmp_path),
        ],
    )

    assert prepare_consumer_packet.main() == 2
    captured = capsys.readouterr()
    visible = captured.out + captured.err
    assert (
        "CONSUMER_PACKET_STATUS: readback incomplete; "
        "packet=written; event_custody=failed"
    ) in visible
    assert "Traceback" not in visible
    assert "consumer-event-marker-must-not-be-visible" not in visible


def test_manual_live_transcript_never_claims_complete_surface_zero_leaks() -> None:
    result = finalize_live_output_hygiene(
        {
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
        },
        "The revised answer is ready.",
    )

    hygiene = result["live_output_hygiene"]
    health = result["run_health"]
    assert hygiene["observed_scope"] == ["curated_live_transcript_artifact"]
    assert hygiene["complete_visible_surface_observed"] is False
    assert hygiene["complete_visible_surface_leak_count"] is None
    assert health["live_output_observed_surface_leak_count"] == 0
    assert health["complete_visible_surface_leak_count"] is None


def test_reasoning_trace_declares_tool_stream_not_observed(tmp_path: Path) -> None:
    run_id = "trace_coverage"
    run_dir = tmp_path / "archive"
    run_dir.mkdir()
    (run_dir / "result.json").write_text(
        json.dumps(
            {
                "run_health": {"overall": "healthy"},
                "usage_summary": {},
                "audit_summary": {},
            }
        ),
        encoding="utf-8",
    )
    trace = build_reasoning_trace(
        run_dir,
        run_id=run_id,
        case_id="case",
        fingerprint="abc",
        how_matched="new",
        files_copied=["result.json"],
        files_missing=[],
        manifest={"run_count": 1},
    )

    assert trace["tool_calls"] == []
    assert trace["tool_call_coverage"] == {
        "status": "not_observed",
        "scope": "repository_run_events_only",
        "complete_host_tool_stream_captured": False,
        "non_claim": "empty_tool_calls_does_not_prove_no_host_tool_calls",
    }
    assert trace["surface_divergence"]["complete_visible_surface_compared"] is False


def test_schema_owned_consumer_packets_do_not_dump_private_content(
    tmp_path: Path,
) -> None:
    run_id = "consumer_packets"
    result_path, _ = _write_result(tmp_path, run_id)
    extraction = {
        "status": "ok",
        "extraction": {
            "decision_situation": "Whether to grant Marcus equity",
            "live_constraints": [{"constraint": "A sale may happen in three years."}],
            "synthesized_position": "Decide partner or employee.",
            "reasoning_passages": [{"text": "The decision was made binary."}],
            "original_framing": "Should I grant 15 percent?",
            "dropped_threads": [{"thread": "Leadership precedent"}],
        },
        "capture_manifest": {"actual_user_turns": 7, "actual_assistant_turns": 7},
    }
    (tmp_path / f"lolla_{run_id}_extraction.json").write_text(
        json.dumps(extraction),
        encoding="utf-8",
    )
    marker = "PRIVATE_PACKET_MARKER"
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    payload["delta_card"] = {"top_findings": [{"private": marker}]}
    result_path.write_text(json.dumps(payload), encoding="utf-8")

    outputs: list[str] = []
    for stage in ("readback", "reconsideration", "verification"):
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/skill/prepare_consumer_packet.py"),
                "--run-id",
                run_id,
                "--stage",
                stage,
                "--tmp-dir",
                str(tmp_path),
            ],
            text=True,
            capture_output=True,
            env={
                **os.environ,
                "LOLLA_RUN_ID": run_id,
                "LOLLA_EXPECTED_RUN_ID": run_id,
                "PYTHONPATH": str(ROOT),
            },
            check=False,
        )
        assert completed.returncode == 0, completed.stderr
        outputs.append(completed.stdout + completed.stderr)
        packet_path = tmp_path / f"lolla_{run_id}_consumer_{stage}.json"
        assert packet_path.exists()
        assert packet_path.stat().st_mode & 0o777 == 0o600

    visible = "".join(outputs)
    assert visible == (
        "CONSUMER_PACKET_STATUS: readback ready\n"
        "CONSUMER_PACKET_STATUS: reconsideration ready\n"
        "CONSUMER_PACKET_STATUS: verification ready\n"
    )
    assert marker not in visible
    assert "{" not in visible
    assert "/tmp" not in visible


def test_provider_free_marcus_boundary_replay_has_no_private_visible_marker(
    tmp_path: Path,
) -> None:
    """Replay the host transport boundary without calling a model provider."""

    run_id = "marcus_boundary_replay"
    source = (
        ROOT
        / "research/test-cases/phase2d-marcus-controlled-comparison-2026-04-24"
        / "lolla_20260422T155622Z_conversation.txt"
    ).read_text(encoding="utf-8")
    assert source.count("] USER:") == 7
    assert source.count("] ASSISTANT:") == 7
    source_marker = "I run a 90-person digital agency"
    assert source_marker in source

    transcript = tmp_path / f"lolla_{run_id}_live_transcript.txt"
    operator = tmp_path / f"lolla_{run_id}_operator.log"
    state = tmp_path / f"lolla_{run_id}_env.sh"
    transcript.write_text("", encoding="utf-8")
    operator.write_text("", encoding="utf-8")
    state.write_text(
        "\n".join(
            [
                "umask 077",
                f"export SKILL_DIR={ROOT}",
                f"export LOLLA_RUN_ID={run_id}",
                f"export LOLLA_EXPECTED_RUN_ID={run_id}",
                f"export LOLLA_LIVE_TRANSCRIPT={transcript}",
                f"export LOLLA_OPERATOR_LOG={operator}",
                f"export LOLLA_ENV_STATE={state}",
                f"export LOLLA_TMP_DIR={tmp_path}",
                "export LOLLA_AUDIT_MODE=standard",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for runtime_file in (transcript, operator, state):
        runtime_file.chmod(0o600)

    common_env = {
        **os.environ,
        "LOLLA_TMP_DIR": str(tmp_path),
        "LOLLA_ENV_STATE": str(state),
        "PYTHONPATH": str(ROOT),
        # Sentinels prove this replay does not need credentials. No provider
        # runner is invoked anywhere in this test.
        "OPENROUTER_API_KEY": "",
        "OPENAI_API_KEY": "",
    }
    capture = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts/skill/capture_step.sh"),
            "--run-id",
            run_id,
        ],
        input=source,
        text=True,
        capture_output=True,
        env=common_env,
        check=False,
    )
    assert capture.returncode == 0, capture.stderr

    extraction = {
        "status": "ok",
        "extraction": {
            "decision_situation": "Whether to grant Marcus partnership equity",
            "live_constraints": [],
            "reasoning_passages": [],
            "original_framing": "Should Marcus receive 15 percent?",
            "synthesized_position": "Decide partner or employee.",
            "dropped_threads": [],
            "turns": [],
        },
        "capture_manifest": {
            "actual_user_turns": 7,
            "actual_assistant_turns": 7,
        },
    }
    extraction_path = tmp_path / f"lolla_{run_id}_extraction.json"
    extraction_path.write_text(
        json.dumps(extraction),
        encoding="utf-8",
    )
    extraction_path.chmod(0o600)
    result_path, original = _write_result(tmp_path, run_id)
    seeded = json.loads(result_path.read_text(encoding="utf-8"))
    seeded.update(
        {
            "extraction": extraction["extraction"],
            "capture_manifest": extraction["capture_manifest"],
            "audit_summary": {
                "boundary_call_count": 0,
                "boundary_calls": [],
                "warnings": [],
            },
            "companion_cheat_sheet": {
                "anchors": [],
                "anti_echo_model_ids": [],
            },
            "usage_summary": {
                "run_id": run_id,
                "pricing_table_version": "provider-free-replay",
                "estimated_total_cost_usd": 0,
                "cost_estimate_state": "not_applicable",
                "vendors": {},
            },
        }
    )
    result_path.write_text(json.dumps(seeded), encoding="utf-8")
    original = seeded
    decisions = _valid_decisions(original)
    revised_marker = "PRIVATE_REVISED_MARKER"
    decisions["revised_answer"] += f"\n\n{revised_marker}"
    step6 = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts/skill/persist_private_step.sh"),
            "--run-id",
            run_id,
            "--kind",
            "step6",
        ],
        input=json.dumps(decisions),
        text=True,
        capture_output=True,
        env=common_env,
        check=False,
    )
    assert step6.returncode == 0, step6.stderr

    memo_marker = "PRIVATE_MEMO_MARKER"
    memo = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts/skill/persist_private_step.sh"),
            "--run-id",
            run_id,
            "--kind",
            "memo",
        ],
        input=json.dumps(
            {
                "memo_substantive_title": "Partnership diligence",
                "memo_orientation_note": memo_marker,
                "memo_what_changed": "Sequence changed.",
                "memo_what_still_holds": "Candor still matters.",
                "memo_take_back_or_set_aside": "The binary was withdrawn.",
                "memo_pressure_check": "",
            }
        ),
        text=True,
        capture_output=True,
        env=common_env,
        check=False,
    )
    assert memo.returncode == 0, memo.stderr

    pressure = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts/skill/persist_default_pressure_step.sh"),
            "--run-id",
            run_id,
        ],
        text=True,
        capture_output=True,
        env=common_env,
        check=False,
    )
    assert pressure.returncode == 0, pressure.stderr

    render_memo = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts/skill/render_memo_step.sh"),
            "--run-id",
            run_id,
        ],
        text=True,
        capture_output=True,
        env=common_env,
        check=False,
    )
    assert render_memo.returncode == 0, render_memo.stderr

    verification = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts/skill/prepare_consumer_step.sh"),
            "--run-id",
            run_id,
            "--stage",
            "verification",
        ],
        text=True,
        capture_output=True,
        env=common_env,
        check=False,
    )
    assert verification.returncode == 0, verification.stderr

    archive_root = tmp_path / "archive"
    finalization = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts/skill/finalize_and_archive.sh"),
            "--run-id",
            run_id,
            "--skip-observatory",
        ],
        text=True,
        capture_output=True,
        env={
            **common_env,
            "LOLLA_ARCHIVE_DIR": str(archive_root),
        },
        check=False,
    )
    assert finalization.returncode == 0, finalization.stderr

    visible = capture.stdout + capture.stderr + step6.stdout + step6.stderr
    visible += memo.stdout + memo.stderr + pressure.stdout + pressure.stderr
    visible += render_memo.stdout + render_memo.stderr
    visible += verification.stdout + verification.stderr
    visible += finalization.stdout + finalization.stderr
    assert source_marker not in visible
    assert revised_marker not in visible
    assert memo_marker not in visible
    assert "{" not in visible
    assert "/tmp/" not in visible
    assert "Added " not in visible
    assert "Edited " not in visible
    assert "PRIVATE_INPUT_READY" in visible
    assert "CAPTURE_STATUS: ready; message_blocks=14" in visible
    assert "PRIVATE_PERSIST_STATUS: step6 valid" in visible
    assert "PRIVATE_PERSIST_STATUS: memo_note ready" in visible
    assert "PRESSURE_CHECK_STATUS: default_off ready" in visible
    assert "MEMO_STATUS: ready" in visible
    assert "CONSUMER_PACKET_STATUS: verification ready" in visible
    assert "USER_RECEIPT_BEGIN" in visible
    assert "USER_RECEIPT_END" in visible

    assert source_marker in (
        tmp_path / f"lolla_{run_id}_conversation.txt"
    ).read_text(encoding="utf-8")
    assert revised_marker in json.loads(result_path.read_text(encoding="utf-8"))[
        "revised_answer"
    ]
    assert memo_marker in json.loads(
        (tmp_path / f"lolla_{run_id}_memo_note.json").read_text(encoding="utf-8")
    )["memo_orientation_note"]
    assert memo_marker == json.loads(
        result_path.read_text(encoding="utf-8")
    )["memo_orientation_note"]
    run_dirs = list(archive_root.glob(f"*/{run_id}"))
    assert len(run_dirs) == 1
    archived_trace = json.loads(
        (run_dirs[0] / "reasoning_trace.json").read_text(encoding="utf-8")
    )
    assert archived_trace["tool_call_coverage"]["status"] == "not_observed"
    assert all(
        path.stat().st_mode & 0o777 == 0o600
        for path in tmp_path.iterdir()
        if path.is_file()
    )
