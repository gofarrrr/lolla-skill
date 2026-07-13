from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import pytest

from scripts.evals import run_fixed_safe_holdout_pool as pool_runner
from scripts.evals import run_fixed_safe_holdout_pool_v2 as pool_runner_v2
from scripts.evals import run_fixed_safe_holdout_pool_v3 as pool_runner_v3


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/safe-holdout-pool-v1-2026-07-10"


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return _hash(path)


def _specs() -> list[dict[str, object]]:
    return [
        {
            "case_id": f"pool-case-{index}",
            "title": f"Case {index}",
            "stratum": f"stratum-{index}",
            "scenario_brief": f"A bounded fictional decision scenario {index}.",
            "required_message_count": 12,
        }
        for index in range(1, 6)
    ]


def _contract(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    monkeypatch.setattr(pool_runner, "REPO_ROOT", tmp_path)
    locks = []
    for role in (
        "pool_runner",
        "pricing",
        "evaluation_doctrine",
        "holdout_protocol",
    ):
        path = tmp_path / "locks" / f"{role}.txt"
        locks.append(
            {
                "role": role,
                "path": str(path.relative_to(tmp_path)),
                "sha256": _write(path, role),
            }
        )
    specs = _specs()
    seed = "fixed-public-seed"
    ranked = pool_runner._selection_order(
        seed, [str(item["case_id"]) for item in specs]
    )
    contract = {
        "schema_version": pool_runner.CONTRACT_SCHEMA,
        "status": "frozen_before_call",
        "run_id": "pool_test_a1",
        "pool_id": "pool-test",
        "system_prompt": "Author fictional conversations and return JSON.",
        "authoring_instruction": "Write exactly the specified safe fictional cases.",
        "case_specs": specs,
        "selection_contract": {
            "algorithm": "sha256_seed_colon_case_id_ascending",
            "public_seed": seed,
            "ranked_case_ids": ranked,
            "generator_receives_selection_order": False,
            "selection_rule_after_call": "first safety-passing case",
        },
        "call_configuration": {
            "provider": "openrouter",
            "model": "google/gemini-3.1-flash-lite",
            "temperature": 0.5,
            "max_output_tokens": 10000,
            "reasoning_effort": "none",
            "generation_calls": 1,
            "evaluator_calls": 0,
            "automatic_retries": 0,
            "provider_timeout_seconds": 30,
            "wall_clock_timeout_seconds": 60,
        },
        "call_budget": {
            "estimated_cost_ceiling_usd": 0.06,
            "pricing_table_version": pool_runner.PRICES_LAST_VERIFIED,
        },
        "hash_locks": locks,
        "artifacts": {
            "output_dir": "run",
            "pool_path": "run/pool.json",
            "call_custody_path": "run/call-custody.json",
            "run_summary_path": "run/run-summary.json",
            "case_dir": "run/cases",
        },
        "post_call_review": {
            "selection_review_scope": (
                "safety_and_contract_only_not_likely_lolla_or_graph_value"
            )
        },
        "non_claims": ["not product proof"],
    }
    contract["prompt_hashes"] = pool_runner._prompt_hashes(contract)
    return contract


def _payload(contract: dict) -> dict:
    cases = []
    for spec in contract["case_specs"]:
        messages = []
        for index in range(1, 13):
            role = "user" if index % 2 else "assistant"
            content = (
                f"This is fictional {role} message {index} for {spec['title']}. "
                "It adds concrete but bounded context, preserves uncertainty, and "
                "keeps multiple legitimate considerations in view without supplying "
                "a hidden answer key or external factual authority. The conversation "
                "remains substantive enough for a later reasoning-system fixture."
            )
            messages.append(
                {
                    "message_id": f"{spec['case_id']}-m{index:02d}",
                    "role": role,
                    "content": content,
                }
            )
        cases.append(
            {
                "case_id": spec["case_id"],
                "title": spec["title"],
                "stratum": spec["stratum"],
                "messages": messages,
            }
        )
    return {"schema_version": pool_runner.PAYLOAD_SCHEMA, "cases": cases}


def test_selection_order_is_deterministic_and_hidden_from_prompt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = _contract(tmp_path, monkeypatch)
    pool_runner.validate_contract(contract)
    prompts = pool_runner.build_prompts(contract)
    assert contract["selection_contract"]["public_seed"] not in prompts["user_prompt"]
    assert json.dumps(contract["selection_contract"]["ranked_case_ids"]) not in (
        prompts["user_prompt"]
    )
    assert contract["selection_contract"]["ranked_case_ids"] == (
        pool_runner._selection_order(
            contract["selection_contract"]["public_seed"],
            [item["case_id"] for item in contract["case_specs"]],
        )
    )


def test_payload_requires_exact_cases_messages_roles_and_ids(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = _contract(tmp_path, monkeypatch)
    payload = _payload(contract)
    assert pool_runner._validate_payload(payload, contract) == []
    broken = deepcopy(payload)
    broken["cases"][0]["messages"][3]["role"] = "user"
    assert "case[0].messages[3] role invalid" in pool_runner._validate_payload(
        broken, contract
    )


def test_one_fake_call_builds_five_hashed_cases_and_cost_custody(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = _contract(tmp_path, monkeypatch)
    payload = _payload(contract)

    def fake_call(_: object) -> dict:
        return {
            "call_attempted": True,
            "requested_model": "google/gemini-3.1-flash-lite",
            "system_prompt_sha256": contract["prompt_hashes"][
                "system_prompt_sha256"
            ],
            "user_prompt_sha256": contract["prompt_hashes"]["user_prompt_sha256"],
            "status": "ok",
            "response": payload,
            "validation_errors": [],
            "served_model": "google/gemini-3.1-flash-lite-20260507",
            "model_attribution_status": "served_version_alias",
            "finish_reason": "stop",
            "prompt_tokens": 1000,
            "completion_tokens": 5000,
            "total_tokens": 6000,
            "reasoning_tokens": 0,
            "usage_evidence_state": "complete",
            "duration_seconds": 1.0,
        }

    pool, custody, summary = pool_runner.run_pool_generation(
        contract, call_fn=fake_call
    )
    assert pool["status"] == "frozen_unreviewed"
    assert pool["selected_case_id"] is None
    assert len(pool["cases"]) == 5
    assert all(len(item["conversation_sha256"]) == 64 for item in pool["cases"])
    assert custody["recorded_call_count"] == 1
    assert summary["status"] == "passed"
    assert summary["estimated_cost_usd"] is not None
    assert summary["semantic_or_graph_selection_performed"] is False


def test_checked_in_pool_contract_is_frozen_and_dry_run_valid() -> None:
    contract_path = PACKAGE / "generation-contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    pool_runner.validate_contract(contract)
    assert contract["prompt_hashes"] == pool_runner._prompt_hashes(contract)
    assert contract["selection_contract"]["ranked_case_ids"][0] == (
        "pool1-case03-nonprofit-program-scale"
    )
    assert contract["call_configuration"]["generation_calls"] == 1
    assert contract["call_configuration"]["automatic_retries"] == 0
    assert contract["call_configuration"]["evaluator_calls"] == 0


def test_v2_contract_repairs_only_operability_and_preserves_prompts() -> None:
    v1_contract = json.loads(
        (PACKAGE / "generation-contract.json").read_text(encoding="utf-8")
    )
    v2_contract = json.loads(
        (PACKAGE / "generation-contract-v2.json").read_text(encoding="utf-8")
    )
    pool_runner_v2.validate_contract(v2_contract)
    assert v2_contract["system_prompt"] == v1_contract["system_prompt"]
    assert v2_contract["authoring_instruction"] == v1_contract[
        "authoring_instruction"
    ]
    assert v2_contract["case_specs"] == v1_contract["case_specs"]
    assert v2_contract["selection_contract"] == v1_contract["selection_contract"]
    assert v2_contract["prompt_hashes"] == v1_contract["prompt_hashes"]
    assert v1_contract["call_configuration"]["reasoning_effort"] == "none"
    assert v2_contract["call_configuration"]["reasoning_effort"] == "minimal"
    assert v2_contract["operational_repair"]["semantic_prompt_changed"] is False
    assert v2_contract["operational_repair"]["automatic_retry_of_v1"] is False


def test_v2_preserves_bounded_provider_error_diagnostics() -> None:
    diagnostic = pool_runner_v2._provider_diagnostic(
        {
            "error": {
                "code": 400,
                "message": "unsupported setting",
                "metadata": {"provider_name": "example", "secret": ["not kept"]},
            }
        },
        [],
    )
    assert diagnostic == {
        "code": 400,
        "message": "unsupported setting",
        "metadata": {"provider_name": "example"},
    }


def test_v1_failure_is_frozen_without_selection_or_false_zero() -> None:
    failure = json.loads((PACKAGE / "v1-failure.json").read_text(encoding="utf-8"))
    assert failure["status"] == (
        "failed_unsupported_reasoning_effort_and_incomplete_error_custody"
    )
    assert failure["observed"]["recorded_call_count"] == 1
    assert failure["observed"]["automatic_retries"] == 0
    assert failure["observed"]["selected_case_id"] is None
    assert failure["observed"]["total_tokens"] is None
    assert failure["observed"]["estimated_cost_usd"] is None
    assert failure["authorizations"]["retry_v1"] is False


def test_v3_contract_keeps_prompts_and_moves_canonical_ids_to_code() -> None:
    v2_contract = json.loads(
        (PACKAGE / "generation-contract-v2.json").read_text(encoding="utf-8")
    )
    v3_overlay = json.loads(
        (PACKAGE / "generation-contract-v3.json").read_text(encoding="utf-8")
    )
    v3_contract = pool_runner_v3._expand_contract(v3_overlay)
    pool_runner_v3.validate_contract(v3_overlay)
    assert v3_contract["system_prompt"] == v2_contract["system_prompt"]
    assert v3_contract["authoring_instruction"] == v2_contract[
        "authoring_instruction"
    ]
    assert v3_contract["case_specs"] == v2_contract["case_specs"]
    assert v3_contract["selection_contract"] == v2_contract["selection_contract"]
    assert v3_contract["prompt_hashes"] == v2_contract["prompt_hashes"]
    assert v3_contract["deterministic_id_repair"][
        "model_message_ids_authoritative"
    ] is False
    assert v3_contract["deterministic_id_repair"][
        "canonical_ids_assigned_by_deterministic_code"
    ] is True


def test_v3_canonicalizes_unique_numeric_ids_without_changing_content() -> None:
    raw = json.loads(
        (PACKAGE / "generation-contract-v3.json").read_text(encoding="utf-8")
    )
    contract = pool_runner_v3._expand_contract(raw)
    payload = _payload(contract)
    original_contents = []
    for case in payload["cases"]:
        for index, message in enumerate(case["messages"], start=1):
            original_contents.append(message["content"])
            message["message_id"] = index
    canonical, errors, normalization = pool_runner_v3._canonicalize_payload(
        payload, contract
    )
    assert errors == []
    assert normalization["normalized_message_count"] == 60
    assert canonical["cases"][0]["messages"][0]["message_id"] == (
        "pool1-case01-product-scope-m01"
    )
    assert [
        message["content"]
        for case in canonical["cases"]
        for message in case["messages"]
    ] == original_contents


def test_v2_failure_stays_failed_as_scorer_mismatch() -> None:
    failure = json.loads((PACKAGE / "v2-failure.json").read_text(encoding="utf-8"))
    assert failure["status"] == "failed_scorer_contract_mismatch"
    assert failure["failed_gate"]["only_error_type"] == (
        "message_id_exact_format"
    )
    assert failure["diagnosis"]["semantic_generation_failure"] is False
    assert failure["authorizations"]["declare_v2_passed"] is False
    assert failure["authorizations"]["repair_or_rewrite_v2_output"] is False


def test_v3_rate_limit_is_terminal_and_preserves_diagnostic() -> None:
    failure = json.loads((PACKAGE / "v3-failure.json").read_text(encoding="utf-8"))
    custody = json.loads(
        (
            PACKAGE
            / "run/lolla_holdout_pool_v1_20260710_a3/call-custody.json"
        ).read_text(encoding="utf-8")
    )
    decision = json.loads((PACKAGE / "decision.json").read_text(encoding="utf-8"))
    call = custody["call"]
    assert failure["status"] == (
        "failed_rate_limit_terminal_pool_generation_stopped"
    )
    assert call["provider_diagnostic"]["code"] == 429
    assert call["provider_diagnostic"]["metadata"]["error_type"] == (
        "rate_limit_exceeded"
    )
    assert call["usage_evidence_state"] == "unknown"
    assert failure["observed"]["total_tokens"] is None
    assert failure["terminal_decision"][
        "additional_pool_generation_calls_authorized"
    ] is False
    assert decision["selection"]["selected_case_id"] is None
    assert decision["authorizations"]["stage_a"] is False
    assert decision["authorizations"]["use_v2_output_as_holdout"] is False


def test_frozen_pool_failure_artifact_hashes_are_stable() -> None:
    expected = {
        "run/lolla_holdout_pool_v1_20260710_a2/pool.json": (
            "ef9b7757294b70f2d5d93bb44ad626b703f20ec00aef7953569f440421c18c5d"
        ),
        "run/lolla_holdout_pool_v1_20260710_a2/call-custody.json": (
            "6195df284b3ada96fcf62c0576cf5e52d8e0c7826bac9236e0d77f019ebf3925"
        ),
        "run/lolla_holdout_pool_v1_20260710_a2/run-summary.json": (
            "fe0d8d0429f5dc60add7d1488fa11a2f56fb91d415642651b19769ae521ff91b"
        ),
        "run/lolla_holdout_pool_v1_20260710_a3/pool.json": (
            "141d745276c017a13eb66230177102cbf12546b4b5322d373278a5447309c33d"
        ),
        "run/lolla_holdout_pool_v1_20260710_a3/call-custody.json": (
            "0c180636191f17051d0274035bd59a5929a61f403db8f5abc3830c1c47979fa2"
        ),
        "run/lolla_holdout_pool_v1_20260710_a3/run-summary.json": (
            "99e8169a12add6fd76039b4acad9d9918e89463134860a0cc67838a280801488"
        ),
    }
    for relative, digest in expected.items():
        assert _hash(PACKAGE / relative) == digest
