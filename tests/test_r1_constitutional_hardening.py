from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import run_extract
from engine.system_b.boundary_provider import OpenAICompatibleBoundaryClient
from engine.system_b.usage_summary import build_usage_summary


class _Response:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


def _success_payload(*, cost: float = 0.000123) -> dict:
    return {
        "id": "gen-r1-exact-response",
        "model": "google/gemini-3.1-flash-lite",
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "total_tokens": 120,
            "cost": cost,
        },
        "choices": [
            {"finish_reason": "stop", "message": {"content": '{"ok": true}'}}
        ],
    }


def _client() -> OpenAICompatibleBoundaryClient:
    return OpenAICompatibleBoundaryClient(
        provider_name="openrouter",
        api_key="test-key",
        base_url="https://openrouter.ai/api/v1",
        model="google/gemini-3.1-flash-lite",
    )


def test_140_turn_authoritative_conversation_survives_bounded_processing_view(
    tmp_path: Path,
) -> None:
    turns: list[str] = ["CONVERSATION: 140 turns, 70 user messages, 70 assistant responses\n"]
    for index in range(1, 71):
        turns.append(f"[Turn {index}] USER:\nQuestion {index} " + ("u" * 600) + "\n\n")
        turns.append(
            f"[Turn {index}] ASSISTANT:\nAnswer {index} " + ("a" * 600) + "\n\n"
        )
    authoritative = "".join(turns)
    assert len(authoritative) > run_extract.MAX_CONVERSATION_CHARS
    source = tmp_path / "lolla_r1_conversation.txt"
    source.write_text(authoritative, encoding="utf-8")

    processing, truncation = run_extract._truncate_conversation(authoritative)
    metadata = run_extract._write_conversation_processing_view(
        conversation_path=source,
        authoritative_text=authoritative,
        processing_text=processing,
        truncation_info=truncation,
    )

    assert source.read_text(encoding="utf-8") == authoritative
    assert metadata["status"] == "partial"
    assert metadata["authoritative_conversation_preserved"] is True
    assert metadata["processing_view_is_authoritative"] is False
    assert metadata["omitted_turn_count"] > 0
    assert metadata["authoritative_sha256"] == hashlib.sha256(
        authoritative.encode("utf-8")
    ).hexdigest()
    assert (tmp_path / "lolla_r1_conversation_processing_view.txt").read_text(
        encoding="utf-8"
    ) == processing


def test_openrouter_request_has_frozen_output_price_routing_and_privacy_contract(
    monkeypatch, tmp_path: Path
) -> None:
    state_path = tmp_path / "provider_budget.json"
    monkeypatch.setenv("LOLLA_RUN_ID", "r1-request-contract")
    monkeypatch.setenv("LOLLA_PROVIDER_BUDGET_STATE", str(state_path))
    captured: dict[str, object] = {}

    def fake_urlopen(req, timeout):
        captured["body"] = json.loads(req.data.decode("utf-8"))
        captured["timeout"] = timeout
        return _Response(_success_payload())

    monkeypatch.setattr("engine.system_b.boundary_provider.request.urlopen", fake_urlopen)
    client = _client()
    payload, metadata = client.run_json_with_metadata(
        "system", "user", stage="extraction"
    )

    body = captured["body"]
    assert isinstance(body, dict)
    assert body["max_tokens"] == 5000
    assert body["provider"] == {
        "allow_fallbacks": False,
        "require_parameters": True,
        "data_collection": "deny",
        "max_price": {"prompt": 0.3, "completion": 1.6},
        "order": ["google-vertex/global"],
    }
    assert payload == {"ok": True}
    assert metadata.provider_attempted is True
    assert metadata.response_id == "gen-r1-exact-response"
    assert metadata.exact_cost_usd == 0.000123
    assert metadata.pricing_table_stale is False
    ledger = json.loads(state_path.read_text(encoding="utf-8"))
    assert ledger["attempted_provider_calls"] == 1
    assert ledger["provider_reported_cost_usd"] == 0.000123
    assert ledger["reservations"][0]["accounting_basis"] == "provider_reported_exact"


def test_call_and_usd_ceilings_block_before_network_and_do_not_inflate_work(
    monkeypatch, tmp_path: Path
) -> None:
    state_path = tmp_path / "provider_budget.json"
    monkeypatch.setenv("LOLLA_RUN_ID", "r1-budget-contract")
    monkeypatch.setenv("LOLLA_PROVIDER_BUDGET_STATE", str(state_path))
    monkeypatch.setenv("LOLLA_MAX_PROVIDER_CALLS", "1")
    attempted = 0

    def fake_urlopen(_req, timeout):
        nonlocal attempted
        attempted += 1
        return _Response(_success_payload())

    monkeypatch.setattr("engine.system_b.boundary_provider.request.urlopen", fake_urlopen)
    client = _client()
    client.run_json("system", "user", stage="pass2")
    blocked, metadata = client.run_json_with_metadata("system", "user", stage="pass2")

    assert attempted == 1
    assert blocked == {}
    assert metadata.status == "budget_blocked_preflight"
    assert metadata.provider_attempted is False
    summary = build_usage_summary(
        run_id="r1-budget-contract",
        pipeline_boundary_calls=client.call_log,
    )
    assert summary["vendors"]["openrouter"]["calls"] == 1
    assert summary["vendors"]["openrouter"]["preflight_non_attempt_count"] == 1

    second_state = tmp_path / "provider_budget_usd.json"
    monkeypatch.setenv("LOLLA_PROVIDER_BUDGET_STATE", str(second_state))
    monkeypatch.setenv("LOLLA_MAX_PROVIDER_CALLS", "96")
    monkeypatch.setenv("LOLLA_MAX_PROVIDER_COST_USD", "0.001")
    usd_client = _client()
    _, usd_metadata = usd_client.run_json_with_metadata(
        "system", "user", stage="extraction"
    )
    assert usd_metadata.status == "budget_blocked_preflight"
    assert attempted == 1
