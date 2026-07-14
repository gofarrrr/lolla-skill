from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.system_b.r4_complementary_readers import canonical_json_bytes
from scripts.evals.build_r4_matched_residual_holdout_contract import (
    CASE_IDS,
    CONTRACT_RELATIVE,
    build,
    build_files,
    load_frozen_case_inputs,
    load_source_first_targets,
    validate_matched_request_pair,
    validate,
)
from scripts.evals import run_r4_matched_residual_holdout_experiment as runner


def test_four_new_long_form_source_and_prior_pairs_are_frozen() -> None:
    cases = load_frozen_case_inputs()

    assert tuple(cases) == CASE_IDS
    assert len(cases) == 4
    assert {case["source"]["message_count"] for case in cases.values()} == {28}
    assert len({case["source"]["domain"] for case in cases.values()}) == 4

    for case_id, case in cases.items():
        source = case["source"]
        prior = case["prior"]
        assert source["case_id"] == prior["case_id"] == case_id
        assert source["evidence_kind"] == "simulated_reliability_not_real_user_evidence"
        assert [row["message_index"] for row in source["messages"]] == list(
            range(1, 29)
        )
        assert [row["speaker"] for row in source["messages"]] == [
            "user" if index % 2 else "assistant" for index in range(1, 29)
        ]
        assert len(prior["records"]) == 3
        assert prior["authority"] == "fallible_prior_interpretation_not_source_truth"
        assert case["source_sha256"] != case["prior_sha256"]


def test_source_first_targets_are_frozen_before_provider_outputs() -> None:
    inputs = load_frozen_case_inputs()
    target = load_source_first_targets()

    assert target["status"] == "frozen_after_source_prior_before_request_previews"
    assert target["provider_outputs_existed_when_authored"] is False
    assert target["target_visible_to_provider"] is False
    assert target["scalar_quality_score"] is None
    assert [row["case_id"] for row in target["cases"]] == list(CASE_IDS)

    expected = {
        "r4h-case01-oral-history-release": ("quiet", "quiet"),
        "r4h-case02-serialized-audio-pilot": ("quiet", "quiet"),
        "r4h-case03-research-data-stewardship": ("supported", "quiet"),
        "r4h-case04-cross-campus-language-program": ("quiet", "supported"),
    }
    for row in target["cases"]:
        case_id = row["case_id"]
        assert row["source_sha256"] == inputs[case_id]["source_sha256"]
        assert row["prior_sha256"] == inputs[case_id]["prior_sha256"]
        surfaces = row["canonical_surface_targets"]
        assert set(surfaces) == {"unresolved_matter", "reopen_condition"}
        assert (
            surfaces["unresolved_matter"]["disposition"],
            surfaces["reopen_condition"]["disposition"],
        ) == expected[case_id]
        for surface in surfaces.values():
            assert surface["strongest_source_aliases"]
            assert surface["outside_adopted_machinery_reason"]
            assert surface["expected_speaker_ownership"]
            assert surface["expected_modal_force"]
        assert row["likely_broad_inventory_false_positives"]
        assert row["explicit_limitations"]
        assert row["ontology_assumptions"]


def test_every_case_has_exact_matched_v2_and_residual_request_arms() -> None:
    files = build_files()

    for case_id in CASE_IDS:
        root = (
            "research/lolla-r4-matched-residual-holdout-contract-2026-07-14/"
            f"cases/{case_id}"
        )
        packet = json.loads(files[f"{root}/uncertainty-packet.json"])
        arm_a = json.loads(files[f"{root}/arm-a-request-preview.json"])
        arm_b = json.loads(files[f"{root}/arm-b-request-preview.json"])
        delta = json.loads(files[f"{root}/matched-request-delta.json"])

        source = canonical_json_bytes(packet["source"]).decode("utf-8")
        prior = canonical_json_bytes(packet["prior_interpretation_context"]).decode(
            "utf-8"
        )
        for preview in (arm_a, arm_b):
            body = preview["body"]
            user = body["messages"][1]["content"]
            assert user.count(source) == user.count(prior) == 1
            assert user.index(source) < user.index(prior) < user.index("<task>")
            assert user.rstrip().endswith("</task>")
            assert body["model"] == "google/gemini-3.1-flash-lite"
            assert body["max_tokens"] == 1600
            assert body["reasoning"] == {"effort": "minimal", "exclude": True}
            assert body["stream"] is False
            assert body["provider"] == {
                "allow_fallbacks": False,
                "data_collection": "deny",
                "max_price": {"completion": 1.5, "prompt": 0.25},
                "only": ["google-vertex"],
                "order": ["google-vertex"],
                "require_parameters": True,
                "zdr": True,
            }

        assert arm_a["body"]["seed"] == arm_b["body"]["seed"]
        assert delta["matched_source_and_prior"] is True
        assert delta["undeclared_differences"] == []
        assert delta["equal_body_fields"] == [
            "/max_tokens",
            "/model",
            "/provider",
            "/reasoning",
            "/seed",
            "/stream",
        ]
        assert delta["schema_difference_paths"] == [
            "/description",
            "/properties/reviews/description",
            "/properties/reviews/items/description",
            "/properties/reviews/items/properties/outcome/description",
            "/properties/reviews/items/properties/records/description",
            "/properties/reviews/items/properties/records/items/description",
            "/properties/reviews/items/properties/records/items/properties/evidence_ids/description",
            "/properties/reviews/items/properties/records/items/properties/interpretation/description",
            "/properties/reviews/items/properties/records/items/properties/limitations/description",
            "/properties/reviews/items/properties/records/items/properties/support/description",
            "/properties/reviews/items/properties/surface/description",
            "/properties/reviews/items/properties/surface/enum/0",
            "/properties/reviews/items/properties/surface/enum/1",
        ]


def test_every_arm_has_exact_full_context_custody_manifest() -> None:
    files = build_files()
    inputs = load_frozen_case_inputs()

    for case_id in CASE_IDS:
        root = (
            "research/lolla-r4-matched-residual-holdout-contract-2026-07-14/"
            f"cases/{case_id}"
        )
        manifests = [
            json.loads(files[f"{root}/arm-a-context-manifest.json"]),
            json.loads(files[f"{root}/arm-b-context-manifest.json"]),
        ]
        assert {row["arm"] for row in manifests} == {
            "A_frozen_v2_semantic_distinction",
            "B_frozen_residual_task",
        }
        for manifest in manifests:
            assert manifest["source"]["artifact_sha256"] == inputs[case_id][
                "source_sha256"
            ]
            assert manifest["prior"]["artifact_sha256"] == inputs[case_id][
                "prior_sha256"
            ]
            assert manifest["source"]["message_count"] == 28
            assert manifest["source"]["alias_count"] == 28
            assert manifest["section_order"] == [
                "system_instruction",
                "authoritative_source",
                "fallible_prior_interpretation_context",
                "task",
            ]
            assert [row["name"] for row in manifest["context_components"]] == [
                "system_instruction",
                "authoritative_source",
                "fallible_prior_interpretation_context",
                "task",
                "schema",
            ]
            assert all(row["utf8_bytes"] > 0 for row in manifest["context_components"])
            assert manifest["complete_source_inclusion"] is True
            assert manifest["task_at_end_invariant"] is True
            assert manifest["schema_labels_and_descriptions_are_model_context"] is True
            assert manifest["no_summary_chunking_filter_or_semantic_gate"] is True
            assert manifest["declared_omissions"]
            assert manifest["request_estimate"]["maximum_output_tokens"] == 1600

        assert manifests[0]["source"] == manifests[1]["source"]
        assert manifests[0]["prior"] == manifests[1]["prior"]
        assert manifests[0]["matched_equal_request_fields"] == manifests[1][
            "matched_equal_request_fields"
        ]
        assert manifests[0]["changed_provider_visible_semantic_fields"] == manifests[
            1
        ]["changed_provider_visible_semantic_fields"]


def test_execution_contract_freezes_counterbalanced_eight_call_design_only() -> None:
    files = build_files()
    contract = json.loads(files[CONTRACT_RELATIVE])
    serialized = json.dumps(contract, sort_keys=True)

    assert contract["status"] == "provider_free_matched_holdout_frozen_no_authorization"
    assert contract["decision_boundary"]["provider_calls_authorized"] is False
    assert contract["decision_boundary"]["authorization_file_present"] is False
    assert contract["provider_calls_made"] == 0
    assert contract["provider_cost_usd"] == 0.0
    assert "lolla-r4-matched-residual-holdout-target" not in serialized
    assert "source_first_target" not in serialized

    assert [
        (row["ordinal"], row["case_id"], row["arm"])
        for row in contract["call_plan"]
    ] == [
        (1, CASE_IDS[0], "A_frozen_v2_semantic_distinction"),
        (2, CASE_IDS[0], "B_frozen_residual_task"),
        (3, CASE_IDS[1], "B_frozen_residual_task"),
        (4, CASE_IDS[1], "A_frozen_v2_semantic_distinction"),
        (5, CASE_IDS[2], "B_frozen_residual_task"),
        (6, CASE_IDS[2], "A_frozen_v2_semantic_distinction"),
        (7, CASE_IDS[3], "A_frozen_v2_semantic_distinction"),
        (8, CASE_IDS[3], "B_frozen_residual_task"),
    ]
    assert contract["budget"] == {
        "automatic_retries": 0,
        "conservative_estimated_total_cost_usd": 0.0424625,
        "embedding_calls": 0,
        "evaluator_calls": 0,
        "fallback_models": 0,
        "graph_calls": 0,
        "hard_provider_reported_cost_per_case_usd": 0.015,
        "hard_provider_reported_cost_total_usd": 0.06,
        "maximum_provider_calls": 8,
        "pipeline_calls": 0,
        "relationship_calls": 0,
        "response_healing": False,
        "runtime_calls": 0,
        "semantic_retries": 0,
    }
    assert contract["operator"]["model"] == "google/gemini-3.1-flash-lite"
    assert contract["operator"]["provider_slug"] == "google-vertex"
    assert contract["operator"]["maximum_price_usd_per_million_tokens"] == {
        "completion": 1.5,
        "prompt": 0.25,
    }
    assert contract["evaluation_contract"]["scalar_quality_score"] is None
    assert len(contract["evaluation_contract"]["vector"]) == 10
    assert set(contract["decision_matrix"]) == {
        "residual_task_identity_supported",
        "holdout_non_discriminating",
        "residual_task_overcorrected",
        "residual_task_repair_insufficient",
        "residual_task_regressed",
        "semantic_result_not_evaluable",
    }
    assert contract["frozen_history"] == {
        "provider_free_corpus_replay": {
            "case_artifact_links": 543,
            "cases": 12,
            "unique_frozen_json_artifacts": 400,
        },
        "residual_module_sha256": "726d4bc649e8e488b5783906785fc3b481ba3ce295dac5155fcff8cd0a83616a",
        "residual_schema_sha256": "70e62d8faa27fcff6517ebaf54433ecd8f534690d86cfc6d219a1e8420b42087",
        "v1_module_sha256": "9253290093e62f62a9adbf8902ccf010ac4d4417c345222e4756e771496bf777",
        "v2_module_sha256": "e774b19cd2bac461e6d586dffbde48515ab23d6f73e1eb158ed87bdcdccdf3c8",
        "v2_schema_sha256": "12327510a78c24bcc1b89e874112517288e1a2054159def729da094de1404a65",
    }

    review_manifest = json.loads(
        files[
            "research/lolla-r4-matched-residual-holdout-contract-2026-07-14/"
            "review-evidence-manifest.json"
        ]
    )
    assert review_manifest["protected_target"]["path"].endswith("target-v1.json")
    assert review_manifest["runner_may_load_this_manifest"] is False


def test_provider_free_package_rebuilds_byte_exactly() -> None:
    built = build()
    validated = validate()

    assert built["status"] == validated["status"]
    assert built["provider_calls_made"] == validated["provider_calls_made"] == 0
    assert built["provider_cost_usd"] == validated["provider_cost_usd"] == 0.0


def test_future_runner_cannot_access_targets_and_requires_exact_authorization(
    tmp_path: Path,
) -> None:
    contract = runner.validate_contract()
    runner_source = Path(runner.__file__).read_text(encoding="utf-8").lower()

    assert "target" not in runner_source
    assert "review-evidence-manifest" not in runner_source
    assert contract["provider_calls_made"] == 0
    expected = runner.expected_authorization(contract=contract)
    authorization = tmp_path / "authorization.json"
    authorization.write_text(
        json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    runner.validate_authorization(authorization, contract=contract)

    expanded = dict(expected)
    expanded["maximum_provider_calls"] = 9
    authorization.write_text(
        json.dumps(expanded, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with pytest.raises(runner.R4MatchedResidualRunError, match="authorization"):
        runner.validate_authorization(authorization, contract=contract)


def test_future_runner_is_hash_frozen_and_dry_run_cannot_open_transport(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = runner.validate_contract()
    frozen_runner = contract["future_runner"]
    runner_path = Path(frozen_runner["path"])

    assert runner_path.resolve() == Path(runner.__file__).resolve()
    assert __import__("hashlib").sha256(runner_path.read_bytes()).hexdigest() == (
        frozen_runner["sha256"]
    )
    monkeypatch.setattr(
        runner,
        "_openrouter_transport",
        lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("dry run attempted to create provider transport")
        ),
    )
    assert runner.main(["--dry-run"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report == {
        "authorization_present": False,
        "conservative_estimated_total_cost_usd": 0.0424625,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "status": "frozen_matched_residual_contract_valid",
    }


class _FakeSuccessfulTransport:
    def __init__(self) -> None:
        self.request_hashes: list[str] = []

    def __call__(self, body: dict) -> bytes:
        self.request_hashes.append(
            __import__("hashlib").sha256(canonical_json_bytes(body)).hexdigest()
        )
        surfaces = body["response_format"]["json_schema"]["schema"]["properties"][
            "reviews"
        ]["items"]["properties"]["surface"]["enum"]
        candidate = {
            "reviews": [
                {
                    "surface": surface,
                    "outcome": "no_supported_record_observed",
                    "records": [],
                }
                for surface in surfaces
            ],
            "global_limitations": "fake transport structural result only",
        }
        ordinal = len(self.request_hashes)
        payload = {
            "id": f"fake-generation-{ordinal:02d}",
            "model": "google/gemini-3.1-flash-lite",
            "provider": "Google",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps(candidate, sort_keys=True)},
                }
            ],
            "usage": {
                "prompt_tokens": 1000,
                "completion_tokens": 100,
                "total_tokens": 1100,
                "completion_tokens_details": {"reasoning_tokens": 0},
                "cost": 0.001,
            },
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def _authorization_file(tmp_path: Path, contract: dict) -> Path:
    path = tmp_path / "authorization.json"
    path.write_text(
        json.dumps(
            runner.expected_authorization(contract=contract), indent=2, sort_keys=True
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def test_fake_transport_completes_exact_counterbalanced_eight_call_envelope(
    tmp_path: Path,
) -> None:
    contract = runner.validate_contract()
    authorization = _authorization_file(tmp_path, contract)
    transport = _FakeSuccessfulTransport()

    result = runner.execute(
        contract=contract,
        authorization_path=authorization,
        output=tmp_path / "run",
        transport=transport,
    )

    assert result["status"] == "matched_execution_complete"
    assert result["provider_calls"] == 8
    assert result["provider_reported_cost_usd"] == 0.008
    assert result["call_ordinals"] == list(range(1, 9))
    assert transport.request_hashes == [
        row["request_body_sha256"] for row in contract["call_plan"]
    ]
    assert result["relationship_calls"] == 0
    assert result["evaluator_calls"] == 0
    assert result["embedding_calls"] == 0
    assert result["graph_calls"] == 0
    assert result["pipeline_calls"] == 0
    assert result["runtime_calls"] == 0
    assert len(list((tmp_path / "run").glob("call-*-raw-response.bin"))) == 8
    assert all(row["operator_attribution_ok"] for row in result["calls"])
    assert all(row["reasoning_custody"]["exclusion_satisfied"] for row in result["calls"])
    assert all(row["local_admission_status"] == "passed" for row in result["calls"])


class _FailOnThirdTransport(_FakeSuccessfulTransport):
    def __call__(self, body: dict) -> bytes:
        if len(self.request_hashes) == 2:
            self.request_hashes.append(
                __import__("hashlib").sha256(canonical_json_bytes(body)).hexdigest()
            )
            raise OSError("synthetic first transport failure")
        return super().__call__(body)


def test_first_transport_failure_stops_without_retry_fallback_or_healing(
    tmp_path: Path,
) -> None:
    contract = runner.validate_contract()
    transport = _FailOnThirdTransport()

    result = runner.execute(
        contract=contract,
        authorization_path=_authorization_file(tmp_path, contract),
        output=tmp_path / "failed-run",
        transport=transport,
    )

    assert result["status"] == "stopped_on_first_failure"
    assert result["provider_calls"] == 3
    assert result["call_ordinals"] == [1, 2, 3]
    assert result["calls"][-1]["operational_status"] == "transport_failure"
    assert len(transport.request_hashes) == 3
    assert len(list((tmp_path / "failed-run").glob("call-*-raw-response.bin"))) == 2
    assert not (tmp_path / "failed-run" / "call-04-started.json").exists()
    assert result["automatic_retries"] == 0
    assert result["fallback_models"] == 0
    assert result["response_healing"] is False


def test_first_http_failure_preserves_exact_terminal_bytes_without_retry(
    tmp_path: Path,
) -> None:
    contract = runner.validate_contract()
    raw = b'{"error":{"message":"synthetic provider failure"}}'

    def transport(_body: dict) -> bytes:
        raise runner.R4ProviderTransportError(
            "synthetic HTTP 429", raw_response=raw, http_status=429
        )

    output = tmp_path / "http-failure"
    result = runner.execute(
        contract=contract,
        authorization_path=_authorization_file(tmp_path, contract),
        output=output,
        transport=transport,
    )

    assert result["status"] == "stopped_on_first_failure"
    assert result["provider_calls"] == 1
    assert result["calls"][0]["operational_status"] == "transport_failure"
    assert result["calls"][0]["http_status"] == 429
    assert (output / "call-01-raw-response.bin").read_bytes() == raw
    assert not (output / "call-02-started.json").exists()


class _MutatingFirstPayloadTransport(_FakeSuccessfulTransport):
    def __init__(self, mutation: str) -> None:
        super().__init__()
        self.mutation = mutation

    def __call__(self, body: dict) -> bytes:
        raw = super().__call__(body)
        payload = json.loads(raw)
        if self.mutation == "provider_identity":
            payload["provider"] = "Undeclared Provider"
        elif self.mutation == "reasoning_content":
            payload["choices"][0]["message"]["reasoning"] = "private reasoning text"
        elif self.mutation == "schema":
            content = json.loads(payload["choices"][0]["message"]["content"])
            content["reviews"][1]["surface"] = content["reviews"][0]["surface"]
            payload["choices"][0]["message"]["content"] = json.dumps(content)
        elif self.mutation == "missing_cost":
            payload["usage"].pop("cost")
        elif self.mutation == "excessive_cost":
            payload["usage"]["cost"] = 0.02
        else:
            raise AssertionError(self.mutation)
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


@pytest.mark.parametrize(
    ("mutation", "expected_status"),
    [
        ("provider_identity", "operator_attribution_failure"),
        ("reasoning_content", "reasoning_custody_failure"),
        ("schema", "schema_or_local_admission_failure"),
        ("missing_cost", "budget_custody_failure"),
        ("excessive_cost", "provider_reported_budget_failure"),
    ],
)
def test_identity_reasoning_schema_and_budget_failures_stop_after_first_result(
    tmp_path: Path, mutation: str, expected_status: str
) -> None:
    contract = runner.validate_contract()
    output = tmp_path / mutation
    result = runner.execute(
        contract=contract,
        authorization_path=_authorization_file(tmp_path, contract),
        output=output,
        transport=_MutatingFirstPayloadTransport(mutation),
    )

    assert result["status"] == "stopped_on_first_failure"
    assert result["provider_calls"] == 1
    assert result["calls"][0]["operational_status"] == expected_status
    assert (output / "call-01-raw-response.bin").is_file()
    assert not (output / "call-02-started.json").exists()


def test_execution_artifact_tampering_fails_before_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    contract = json.loads(Path(runner.DEFAULT_CONTRACT).read_text(encoding="utf-8"))
    preview_path = Path(contract["call_plan"][0]["request_preview_path"])
    absolute_preview = (Path.cwd() / preview_path).resolve()
    original_read_bytes = Path.read_bytes

    def tampered_read_bytes(path: Path) -> bytes:
        raw = original_read_bytes(path)
        return raw + b" " if path.resolve() == absolute_preview else raw

    monkeypatch.setattr(Path, "read_bytes", tampered_read_bytes)
    with pytest.raises(runner.R4MatchedResidualRunError, match="artifact drifted"):
        runner.validate_contract()


def test_matched_pair_validator_rejects_every_undeclared_request_delta() -> None:
    files = build_files()
    case_id = CASE_IDS[0]
    root = (
        "research/lolla-r4-matched-residual-holdout-contract-2026-07-14/"
        f"cases/{case_id}"
    )
    packet = json.loads(files[f"{root}/uncertainty-packet.json"])
    arm_a = json.loads(files[f"{root}/arm-a-request-preview.json"])
    arm_b = json.loads(files[f"{root}/arm-b-request-preview.json"])

    valid = validate_matched_request_pair(packet=packet, arm_a=arm_a, arm_b=arm_b)
    assert valid["undeclared_differences"] == []

    arm_b["body"]["seed"] += 1
    with pytest.raises(
        Exception, match="undeclared matched request delta|request does not equal"
    ):
        validate_matched_request_pair(packet=packet, arm_a=arm_a, arm_b=arm_b)


def test_current_official_practice_and_pricing_evidence_is_hash_frozen() -> None:
    files = build_files()
    contract = json.loads(files[CONTRACT_RELATIVE])
    practice = contract["current_official_practice"]
    path = Path(practice["path"])

    assert path.is_file()
    assert __import__("hashlib").sha256(path.read_bytes()).hexdigest() == practice[
        "sha256"
    ]
    text = path.read_text(encoding="utf-8")
    assert "Date checked: 2026-07-14" in text
    assert "$0.25" in text and "$1.50" in text
    assert "$0.0424625" in text and "$0.06" in text
    assert "does not authorize" in text.lower()
