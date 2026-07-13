from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from scripts.evals import run_designed_ambiguous_pool as runner


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/designed-ambiguous-pool-v1-2026-07-10"


def _contract() -> dict:
    return json.loads((PACKAGE / "generation-contract.json").read_text(encoding="utf-8"))


def _contract_for_current_tree() -> dict:
    """Return a synthetic runnable copy without rewriting the closed contract.

    The checked-in contract preserves the pre-call hashes. Canonical protocol
    docs are allowed to record post-run findings, so unit tests that exercise a
    fake new call must refresh hash locks only in memory.
    """
    contract = _contract()
    for lock in contract["hash_locks"]:
        path = runner.shared._repo_path(lock["path"], label=lock["role"])
        lock["sha256"] = runner.shared._hash_file(path)
    return contract


def _payload(contract: dict) -> dict:
    cases = []
    for spec in contract["case_specs"]:
        messages = []
        for index in range(1, 15):
            role = "user" if index % 2 else "assistant"
            content = (
                f"This is a fictional {role} turn {index} in {spec['title']}. "
                "The speaker adds a concrete consideration while leaving more than one "
                "reasonable interpretation available. The wording is conversational, "
                "acknowledges uncertainty, and does not contain an evaluation label, "
                "hidden answer, external statistic, or predetermined reasoning lens. "
                "Later context may qualify what seemed important earlier."
            )
            messages.append({"role": role, "content": content})
        cases.append(
            {
                "case_id": spec["case_id"],
                "title": spec["title"],
                "stratum": spec["stratum"],
                "messages": messages,
            }
        )
    return {"schema_version": runner.PAYLOAD_SCHEMA, "cases": cases}


def test_contract_shape_freezes_independent_model_and_hidden_rank() -> None:
    contract = _contract_for_current_tree()
    runner.validate_contract(contract)
    prompts = runner.build_prompts(contract)
    assert contract["call_configuration"]["model"] == "moonshotai/kimi-k2.6"
    assert contract["call_configuration"]["downstream_model"] == (
        "openai/gpt-5.1-chat"
    )
    assert contract["call_configuration"]["reasoning_parameter_sent"] is False
    assert contract["selection_contract"]["public_seed"] not in prompts["user_prompt"]
    assert json.dumps(contract["selection_contract"]["ranked_case_ids"]) not in (
        prompts["user_prompt"]
    )
    assert contract["selection_contract"]["ranked_case_ids"][0] == (
        "amb1-case02-nonprofit-scale"
    )


def test_response_schema_requires_five_cases_and_fourteen_role_content_messages() -> None:
    schema = runner._response_schema(_contract())["schema"]
    cases = schema["properties"]["cases"]
    messages = cases["items"]["properties"]["messages"]
    message = messages["items"]
    assert cases["minItems"] == cases["maxItems"] == 5
    assert messages["minItems"] == messages["maxItems"] == 14
    assert set(message["required"]) == {"role", "content"}
    assert "message_id" not in message["properties"]


def test_payload_validator_enforces_alternation_but_not_semantic_keywords() -> None:
    contract = _contract()
    payload = _payload(contract)
    assert runner._validate_payload(payload, contract) == []
    broken = deepcopy(payload)
    broken["cases"][1]["messages"][4]["role"] = "assistant"
    assert "case[1].messages[4] role invalid" in runner._validate_payload(
        broken, contract
    )


def test_fake_call_builds_canonical_ids_without_changing_dialogue() -> None:
    contract = _contract_for_current_tree()
    payload = _payload(contract)

    def fake_call(_: object) -> dict:
        return {
            "call_attempted": True,
            "requested_model": "moonshotai/kimi-k2.6",
            "status": "ok",
            "response": payload,
            "validation_errors": [],
            "served_model": "moonshotai/kimi-k2.6-20260420",
            "model_attribution_status": "served_version_alias",
            "finish_reason": "stop",
            "prompt_tokens": 1500,
            "completion_tokens": 8000,
            "total_tokens": 9500,
            "reasoning_tokens": 0,
            "usage_evidence_state": "complete",
            "duration_seconds": 1.0,
        }

    pool, custody, summary = runner.run_generation(contract, call_fn=fake_call)
    assert pool["status"] == "frozen_unreviewed"
    assert pool["selected_case_id"] is None
    assert pool["cases"][0]["messages"][0]["message_id"] == (
        "amb1-case01-product-scope-m01"
    )
    assert pool["cases"][0]["messages"][0]["content"] == (
        payload["cases"][0]["messages"][0]["content"]
    )
    assert custody["recorded_call_count"] == 1
    assert summary["status"] == "passed"
    assert summary["estimated_cost_usd"] is not None
    assert summary["semantic_or_graph_selection_performed"] is False


def test_http_request_uses_strict_schema_and_omits_reasoning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = _contract()
    payload = _payload(contract)
    captured: dict = {}

    class FakeResponse:
        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def read(self) -> bytes:
            provider_payload = {
                "model": "moonshotai/kimi-k2.6-20260420",
                "choices": [
                    {
                        "message": {"content": json.dumps(payload)},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 1500,
                    "completion_tokens": 8000,
                    "total_tokens": 9500,
                },
            }
            return json.dumps(provider_payload).encode("utf-8")

    def fake_urlopen(req: object, timeout: float) -> FakeResponse:
        captured["body"] = json.loads(req.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(runner.request, "urlopen", fake_urlopen)
    call = runner._call_openrouter(contract)
    body = captured["body"]
    assert call["status"] == "ok"
    assert "reasoning" not in body
    assert body["response_format"]["type"] == "json_schema"
    assert body["response_format"]["json_schema"]["strict"] is True
    assert body["provider"]["require_parameters"] is True
