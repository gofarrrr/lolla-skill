from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/lolla-r4-matched-holdout-v2-execution-2026-07-14-a1"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_raw_execution_a1_is_sealed_provider_free() -> None:
    from scripts.evals import seal_r4_matched_holdout_v2_execution_a1 as seal

    summary = seal.validate_raw()

    assert summary == {
        "status": "raw_execution_sealed_before_semantic_review",
        "provider_calls": 8,
        "provider_reported_cost_usd": 0.01408165,
        "authorization_consumed": True,
    }


def test_authorization_is_consumed_and_cannot_authorize_a_second_run() -> None:
    value = _load(OUTPUT / "authorization-consumption.json")

    assert value["authorization_sha256"] == (
        "3cfe4f0fa5d4be3b8941ca54e9f0fcc4f25c17f354788ff9db8c995366ddd49d"
    )
    assert value["status"] == "consumed_terminal_run_complete"
    assert value["provider_transport_constructed"] is True
    assert value["provider_calls_attempted"] == 8
    assert value["provider_calls_completed"] == 8
    assert value["second_execution_authorized"] is False
    assert value["retry_or_replacement_call_authorized"] is False


def test_raw_manifest_locks_every_runner_file_and_terminal_call() -> None:
    manifest = _load(OUTPUT / "raw-evidence-manifest.json")

    assert manifest["status"] == "raw_execution_sealed_before_semantic_review"
    assert manifest["file_count"] == len(manifest["files"]) == 25
    assert manifest["provider_calls"] == 8
    assert manifest["provider_reported_cost_usd"] == 0.01408165
    assert [row["ordinal"] for row in manifest["calls"]] == list(range(1, 9))
    assert all(row["operator_attribution_ok"] for row in manifest["calls"])
    assert all(row["local_admission_status"] == "passed" for row in manifest["calls"])
    assert all(row["reasoning_tokens"] == 0 for row in manifest["calls"])
    assert all(row["raw_response_preserved_exactly"] for row in manifest["calls"])
    assert all((ROOT / row["path"]).is_file() for row in manifest["files"])


def test_sealer_has_no_network_or_semantic_review_dependency() -> None:
    from scripts.evals import seal_r4_matched_holdout_v2_execution_a1 as seal

    source = Path(seal.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported.isdisjoint(
        {"anthropic", "google", "httpx", "openai", "requests", "urllib"}
    )
    assert "target" not in source.lower()
    assert "source-first" not in source.lower()


def test_sealer_rejects_raw_response_tampering(tmp_path: Path) -> None:
    from scripts.evals import seal_r4_matched_holdout_v2_execution_a1 as seal

    copied = tmp_path / "execution"
    copied.mkdir()
    for path in OUTPUT.glob("call-*"):
        (copied / path.name).write_bytes(path.read_bytes())
    (copied / "result.json").write_bytes((OUTPUT / "result.json").read_bytes())
    raw = copied / "call-01-raw-response.bin"
    raw.write_bytes(raw.read_bytes() + b"tamper")

    with pytest.raises(seal.R4MatchedExecutionA1SealError, match="raw response"):
        seal._build_raw_values(output=copied)
