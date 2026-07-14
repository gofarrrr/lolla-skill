from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-contract.json"
TARGET_TERMS = (
    "lolla-r4-separated-surface-experiment-v1-target",
    "target-review",
    "human-leakage-review-custody",
    "intended_role_contradicted",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_builder_freezes_twelve_matched_requests_and_only_task_shape_deltas() -> None:
    from scripts.evals import build_r4_separated_surface_experiment as builder

    summary = builder.validate()
    contract = _load(CONTRACT)

    assert summary == {
        "status": "provider_free_separated_surface_experiment_valid",
        "case_count": 4,
        "request_count": 12,
        "paired_calls": 4,
        "separated_calls": 8,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }
    assert contract["status"] == "provider_free_design_frozen_no_authorization"
    assert contract["current_provider_authorization"] == {
        "maximum_calls": 0,
        "maximum_cost_usd": 0.0,
        "authorization_artifact_exists": False,
    }
    assert len(contract["call_plan"]) == 12
    assert [row["ordinal"] for row in contract["call_plan"]] == list(range(1, 13))
    assert sum(row["arm"] == "paired_residual" for row in contract["call_plan"]) == 4
    assert sum(row["arm"].startswith("separated_") for row in contract["call_plan"]) == 8

    for case in contract["cases"]:
        requests = [_load(ROOT / path) for path in case["request_preview_paths"]]
        paired = next(row for row in requests if row["arm"] == "paired_residual")
        separated = [row for row in requests if row["arm"].startswith("separated_")]
        assert paired["body"]["max_tokens"] == 1600
        assert [row["body"]["max_tokens"] for row in separated] == [800, 800]
        assert sum(row["body"]["max_tokens"] for row in separated) == 1600
        assert {row["body"]["seed"] for row in requests} == {case["seed"]}
        assert all(row["source_sha256"] == case["source_sha256"] for row in requests)
        assert all(row["prior_sha256"] == case["prior_sha256"] for row in requests)
        assert all(row["complete_source_included_once"] for row in requests)
        assert all(row["complete_prior_included_once"] for row in requests)
        assert all(row["task_at_end"] for row in requests)

        delta = _load(ROOT / case["matched_delta_manifest_path"])
        assert delta["undeclared_provider_visible_deltas"] == []
        assert delta["semantic_wording_change"] is False
        assert delta["source_or_prior_change"] is False
        assert all(path.startswith(tuple(delta["allowed_path_prefixes"])) for path in delta["all_exact_delta_paths"])


def test_execution_visible_package_and_runner_are_target_blind() -> None:
    contract = _load(CONTRACT)
    manifest = _load(ROOT / contract["execution_manifest"]["path"])
    runner_path = ROOT / contract["future_runner"]["path"]
    visible_paths = [ROOT / row["path"] for row in manifest["files"]] + [runner_path]

    assert manifest["protected_target_reference_present"] is False
    assert manifest["human_review_reference_present"] is False
    for path in visible_paths:
        text = path.read_text(encoding="utf-8").lower()
        assert not any(term in text for term in TARGET_TERMS)


def test_contract_operator_budget_cost_and_nonscalar_decision_matrix() -> None:
    contract = _load(CONTRACT)

    assert contract["operator"] == {
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "model": "google/gemini-3.1-flash-lite",
        "allowed_served_model_ids": [
            "google/gemini-3.1-flash-lite",
            "google/gemini-3.1-flash-lite-20260507",
        ],
        "provider_slug": "google-vertex",
        "allowed_served_provider_names": ["Google"],
        "provider_order": ["google-vertex"],
        "provider_only": ["google-vertex"],
        "allow_fallbacks": False,
        "require_parameters": True,
        "data_collection": "deny",
        "zdr": True,
        "maximum_price_usd_per_million_tokens": {"prompt": 0.25, "completion": 1.5},
        "reasoning": {"effort": "minimal", "exclude": True},
        "stream": False,
        "strict_json_schema": True,
    }
    assert contract["budget"]["maximum_provider_calls"] == 12
    assert contract["budget"]["proposed_hard_provider_reported_cost_total_usd"] <= 0.50
    assert contract["budget"]["automatic_retries"] == 0
    assert contract["budget"]["semantic_retries"] == 0
    assert contract["budget"]["fallback_models"] == 0
    assert contract["budget"]["response_healing"] is False
    assert contract["budget"]["model_substitutions"] == 0
    assert contract["deterministic_surface_to_canonical_role_mapping"] == {
        "residual_decision_gap": "unresolved_matter",
        "residual_reconsideration_dependency": "reopen_condition",
    }
    assert contract["evaluation"]["scalar_score"] is None
    assert set(contract["evaluation"]["decision_matrix"]) == {
        "task_shape_companion_pressure_supported",
        "separated_tasks_ineffective_companions_persist",
        "separated_tasks_overcorrected",
        "paired_arm_non_discriminating",
        "mixed_or_insufficient_evidence",
        "semantic_result_not_evaluable",
    }


def _fake_response(body: dict, ordinal: int) -> bytes:
    schema = body["response_format"]["json_schema"]["schema"]
    surfaces = schema["properties"]["reviews"]["items"]["properties"]["surface"]["enum"]
    content = {
        "reviews": [
            {"surface": surface, "outcome": "no_supported_record_observed", "records": []}
            for surface in surfaces
        ],
        "global_limitations": "",
    }
    raw = {
        "id": f"gen-fake-{ordinal:02d}",
        "model": "google/gemini-3.1-flash-lite-20260507",
        "provider": "Google",
        "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(content)}}],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "total_tokens": 120,
            "completion_tokens_details": {"reasoning_tokens": 0},
            "cost": 0.000055,
        },
    }
    return json.dumps(raw, sort_keys=True).encode("utf-8")


def test_runner_dry_run_exact_authorization_and_fake_twelve_call_success(tmp_path: Path) -> None:
    from scripts.evals import run_r4_separated_surface_experiment as runner

    contract = runner.validate_contract()
    assert runner.dry_run() == {"status": "valid_no_transport", "provider_calls": 0, "provider_cost_usd": 0.0}
    authorization = runner.expected_authorization(contract=contract)
    auth_path = tmp_path / "authorization.json"
    auth_path.write_text(json.dumps(authorization), encoding="utf-8")
    runner.validate_authorization(auth_path, contract=contract)

    calls = 0

    def transport(body: dict) -> bytes:
        nonlocal calls
        calls += 1
        return _fake_response(body, calls)

    result = runner.execute(
        contract=contract,
        authorization_path=auth_path,
        output=tmp_path / "execution",
        transport=transport,
    )
    assert calls == 12
    assert result["status"] == "complete"
    assert result["provider_calls"] == 12
    assert result["provider_reported_cost_usd"] == pytest.approx(0.00066)


def test_runner_stops_on_first_failure_without_retry(tmp_path: Path) -> None:
    from scripts.evals import run_r4_separated_surface_experiment as runner

    contract = runner.validate_contract()
    auth_path = tmp_path / "authorization.json"
    auth_path.write_text(json.dumps(runner.expected_authorization(contract=contract)), encoding="utf-8")
    calls = 0

    def transport(body: dict) -> bytes:
        nonlocal calls
        calls += 1
        if calls == 3:
            raise runner.R4ProviderTransportError("terminal", raw_response=b"failure", http_status=503)
        return _fake_response(body, calls)

    result = runner.execute(
        contract=contract,
        authorization_path=auth_path,
        output=tmp_path / "failed-execution",
        transport=transport,
    )
    assert calls == 3
    assert result["status"] == "stopped_on_first_failure"
    assert result["provider_calls"] == 3
    assert len(result["call_results"]) == 3
    assert result["call_results"][-1]["raw_response_sha256"] == hashlib.sha256(b"failure").hexdigest()


def test_authorization_tamper_is_rejected(tmp_path: Path) -> None:
    from scripts.evals import run_r4_separated_surface_experiment as runner

    contract = runner.validate_contract()
    authorization = runner.expected_authorization(contract=contract)
    authorization["maximum_provider_calls"] = 13
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(authorization), encoding="utf-8")
    with pytest.raises(runner.R4SeparatedSurfaceRunError, match="authorization drifted"):
        runner.validate_authorization(path, contract=contract)


@pytest.mark.parametrize(
    ("mutation", "expected_detail"),
    [
        (lambda payload: payload.update(model="other/model"), "operator attribution failure"),
        (lambda payload: payload.update(provider="Other"), "operator attribution failure"),
        (lambda payload: payload.update(id=""), "operator attribution failure"),
        (lambda payload: payload["choices"][0].update(finish_reason="length"), "terminal status failure"),
        (lambda payload: payload["usage"].pop("prompt_tokens"), "usage custody failure"),
        (lambda payload: payload["usage"].pop("cost"), "cost custody failure"),
        (lambda payload: payload["choices"][0]["message"].update(reasoning="not allowed"), "reasoning custody failure"),
        (lambda payload: payload["choices"][0]["message"].update(content='{"reviews": []}'), "candidate object shape invalid"),
    ],
)
def test_runner_stops_after_first_terminal_validation_failure(
    tmp_path: Path,
    mutation,
    expected_detail: str,
) -> None:
    from scripts.evals import run_r4_separated_surface_experiment as runner

    contract = runner.validate_contract()
    auth_path = tmp_path / "authorization.json"
    auth_path.write_text(json.dumps(runner.expected_authorization(contract=contract)), encoding="utf-8")
    calls = 0

    def transport(body: dict) -> bytes:
        nonlocal calls
        calls += 1
        payload = json.loads(_fake_response(body, calls))
        mutation(payload)
        return json.dumps(payload, sort_keys=True).encode("utf-8")

    result = runner.execute(
        contract=contract,
        authorization_path=auth_path,
        output=tmp_path / "failed-validation",
        transport=transport,
    )
    assert calls == 1
    assert result["status"] == "stopped_on_first_failure"
    assert result["provider_calls"] == 1
    assert result["call_ordinals"] == [1]
    assert expected_detail in result["call_results"][0]["failure_detail"]
    assert result["call_results"][0]["first_terminal_provider_result_preserved_exactly"] is True


def test_runner_enforces_provider_reported_budget_on_first_call(tmp_path: Path) -> None:
    from scripts.evals import run_r4_separated_surface_experiment as runner

    contract = runner.validate_contract()
    auth_path = tmp_path / "authorization.json"
    auth_path.write_text(json.dumps(runner.expected_authorization(contract=contract)), encoding="utf-8")
    calls = 0

    def transport(body: dict) -> bytes:
        nonlocal calls
        calls += 1
        payload = json.loads(_fake_response(body, calls))
        payload["usage"]["cost"] = 0.31
        return json.dumps(payload, sort_keys=True).encode("utf-8")

    result = runner.execute(
        contract=contract,
        authorization_path=auth_path,
        output=tmp_path / "budget-failure",
        transport=transport,
    )
    assert calls == 1
    assert result["status"] == "stopped_on_first_failure"
    assert result["provider_calls"] == 1
    assert result["call_results"][0]["operational_status"] == "provider_reported_budget_failure"


def test_undeclared_request_delta_is_rejected_by_delta_inventory() -> None:
    from scripts.evals import build_r4_separated_surface_experiment as builder

    contract = _load(CONTRACT)
    case = contract["cases"][0]
    requests = [_load(ROOT / path) for path in case["request_preview_paths"]]
    paired = next(row for row in requests if row["arm"] == "paired_residual")
    separated = next(row for row in requests if row["arm"] == "separated_decision_gap")
    tampered = json.loads(json.dumps(separated))
    tampered["body"]["temperature"] = 0
    delta = builder._delta_manifest(case["case_id"], paired, [tampered])
    assert "/temperature" in delta["undeclared_provider_visible_deltas"]
