from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from engine.system_b.r4_complementary_readers import canonical_json_bytes
from scripts.evals import run_r4_matched_holdout_v2_experiment as runner
from scripts.evals.build_r4_matched_holdout_v2_contract import (
    CASE_IDS,
    FORBIDDEN_ANSWER_LANGUAGE,
    HUMAN_LEAKAGE_DECLARATION,
    R4MatchedHoldoutV2Error,
    REQUEST_OUTPUT_ROOT,
    CONTRACT_PATH,
    build_contract_files,
    build_matched_delta_files,
    build_request_preview_files,
    build_human_review_freeze_files,
    build_human_review_record,
    build_pre_target_audit,
    lint_v2_source_prior,
    load_source_first_target,
    load_v2_source_prior,
    validate_human_review_freeze,
    validate_human_review_record,
    validate_request_preview_files,
    validate_matched_request_pair,
    validate_matched_delta_files,
    validate_contract_package,
    validate_source_first_target_freeze,
)


ROOT = Path(__file__).resolve().parents[1]
V1_COMMIT = "b46464278e86f4c5d6c53e154bc272d93f09b116"
V1_REJECTION = (
    ROOT / "docs/evals/lolla-r4-matched-residual-holdout-v1-rejection.json"
)
V1_IMMUTABLE_PATHS = (
    "docs/evals/lolla-r4-matched-residual-holdout-contract-v1.json",
    "docs/evals/lolla-r4-matched-residual-holdout-target-v1.json",
    "research/lolla-r4-matched-residual-holdout-contract-2026-07-14",
    "research/lolla-r4-matched-residual-holdout-source-freeze-2026-07-14",
    "scripts/evals/build_r4_matched_residual_holdout_contract.py",
    "scripts/evals/run_r4_matched_residual_holdout_experiment.py",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str, text: bool = False) -> bytes | str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=text,
    ).stdout


def test_v1_checkpoint_is_byte_frozen_and_rejected_before_authorization() -> None:
    assert _git("rev-parse", V1_COMMIT, text=True).strip() == V1_COMMIT
    frozen_paths = set(
        _git(
            "ls-tree",
            "-r",
            "--name-only",
            V1_COMMIT,
            "--",
            *V1_IMMUTABLE_PATHS,
            text=True,
        ).splitlines()
    )
    current_paths = {
        str(path.relative_to(ROOT))
        for scope in V1_IMMUTABLE_PATHS
        for path in (
            [ROOT / scope]
            if (ROOT / scope).is_file()
            else (ROOT / scope).rglob("*")
        )
        if path.is_file()
    }
    assert current_paths == frozen_paths
    for relative in sorted(frozen_paths):
        assert (ROOT / relative).read_bytes() == _git(
            "show", f"{V1_COMMIT}:{relative}"
        )

    rejection = json.loads(V1_REJECTION.read_text(encoding="utf-8"))
    assert rejection == {
        "schema_version": "lolla.r4_matched_residual_holdout_rejection.v1",
        "status": "rejected_before_authorization_for_source_target_semantic_leakage",
        "date": "2026-07-14",
        "checkpoint_commit": V1_COMMIT,
        "contract": {
            "path": "docs/evals/lolla-r4-matched-residual-holdout-contract-v1.json",
            "sha256": "508153a3a3f32121c17783797946dfe484d2bf901d29e0cea51090b453946044",
        },
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "authorization_existed": False,
        "provider_output_existed": False,
        "runner_and_custody_mechanics_passed": True,
        "execution_authorization_eligible": False,
        "founder_execution_authorization_must_never_be_granted": True,
        "blocking_defect": "source_and_prior_text_leak_expected_semantic_classifications",
        "defect_classification": {
            "evidentiary_design": True,
            "transport": False,
            "schema": False,
            "budget": False,
            "target_isolation": False,
        },
        "exact_leakage_findings": [
            {
                "artifact": "research/lolla-r4-matched-residual-holdout-source-freeze-2026-07-14/priors/r4h-case01-oral-history-release.json",
                "location": "records[2].limitations",
                "finding": "The prior critiques its own broad framing and tells the reader it may overstate what remains outside adopted machinery.",
            },
            {
                "artifact": "research/lolla-r4-matched-residual-holdout-source-freeze-2026-07-14/sources/r4h-case01-oral-history-release.json",
                "location": "message 28",
                "finding": "The assistant tells a future source-first review not to relabel governed pending work as newly discovered gaps.",
            },
            {
                "artifact": "research/lolla-r4-matched-residual-holdout-source-freeze-2026-07-14/sources/r4h-case02-serialized-audio-pilot.json",
                "location": "message 28",
                "finding": "The assistant states that continuation creates no separate gap and that pause execution does not independently reopen the decision.",
            },
            {
                "artifact": "research/lolla-r4-matched-residual-holdout-source-freeze-2026-07-14/sources/r4h-case03-research-data-stewardship.json",
                "location": "messages 22, 24, and 28",
                "finding": "The assistant names the material residual, says which facts must not be emitted, and states the complete expected decision-gap result.",
            },
            {
                "artifact": "research/lolla-r4-matched-residual-holdout-source-freeze-2026-07-14/sources/r4h-case04-cross-campus-language-program.json",
                "location": "message 28",
                "finding": "The assistant names the expected reconsideration surface, the quiet matters, and the premise-breaking dependency.",
            },
        ],
        "supersession": {
            "v1_evidence_may_be_executed": False,
            "v1_mechanical_harness_may_inform_v2": True,
            "v2_requires_new_case_ids_sources_priors_targets_hashes_and_requests": True,
        },
    }
    assert _sha(ROOT / rejection["contract"]["path"]) == rejection["contract"][
        "sha256"
    ]


def test_v2_sources_and_priors_are_new_long_form_and_pass_vocabulary_lint() -> None:
    cases = load_v2_source_prior()
    report = lint_v2_source_prior(cases)

    assert tuple(cases) == CASE_IDS
    assert len(cases) == 4
    assert len({case["source"]["domain"] for case in cases.values()}) == 4
    assert report["status"] == "deterministic_vocabulary_lint_passed"
    assert report["exact_match_count"] == 0
    assert report["matches"] == []
    assert report["terms"] == list(FORBIDDEN_ANSWER_LANGUAGE)

    for case_id, case in cases.items():
        source = case["source"]
        prior = case["prior"]
        assert case_id.startswith("r4h2-")
        assert source["case_id"] == prior["case_id"] == case_id
        assert source["message_count"] == 28
        assert [row["message_index"] for row in source["messages"]] == list(
            range(1, 29)
        )
        assert [row["speaker"] for row in source["messages"]] == [
            "user" if index % 2 else "assistant" for index in range(1, 29)
        ]
        assert source["evidence_kind"] == (
            "simulated_reliability_not_real_user_evidence"
        )
        assert prior["authority"] == (
            "fallible_prior_interpretation_not_source_truth"
        )
        assert len(prior["records"]) == 3
        assert case["source_sha256"] != case["prior_sha256"]

    broad_prior = json.dumps(
        cases[CASE_IDS[0]]["prior"], ensure_ascii=False
    ).lower()
    assert "unresolved" in broad_prior
    assert "may overstate" not in broad_prior
    assert "discount" not in broad_prior


def test_human_gate_audit_records_pass_without_automating_semantic_judgment() -> None:
    cases = load_v2_source_prior()
    audit = build_pre_target_audit(cases)

    assert {
        "unresolved_matter",
        "reopen_condition",
        "emit",
        "emitted",
        "suppress",
        "suppressed",
        "keep quiet",
        "expected result",
        "structured answer",
        "reopen the decision",
    }.issubset(FORBIDDEN_ANSWER_LANGUAGE)
    assert audit["status"] == "human_review_passed_target_authorship_unlocked"
    assert audit["deterministic_vocabulary_lint"]["exact_match_count"] == 0
    assert audit["human_review_required_before_target"] == "satisfied"
    assert audit["deterministic_semantic_sufficiency_decided"] is False
    assert audit["human_semantic_sufficiency_decided"] is True
    assert audit["human_declaration"] == HUMAN_LEAKAGE_DECLARATION
    assert audit["target_authored"] is True
    assert audit["request_preview_authored"] is True
    assert audit["provider_calls"] == 0
    assert audit["provider_cost_usd"] == 0.0

    assert [row["case_id"] for row in audit["cases"]] == list(CASE_IDS)
    for row in audit["cases"]:
        case = cases[row["case_id"]]
        assert row["source_sha256"] == case["source_sha256"]
        assert row["prior_sha256"] == case["prior_sha256"]
        assert row["last_four_message_indices"] == [25, 26, 27, 28]
        assert len(row["last_four_canonical_sha256"]) == 64
        assert row["human_semantic_leakage_review"] == "passed"
        assert row["last_four_sufficient_for_both_surfaces"] is False
        assert row["assistant_states_expected_category"] is False
        assert row["prior_self_discounting"] is False
        assert row["source_instructs_emit_or_suppress"] is False

    assert (
        ROOT / "docs/evals/lolla-r4-matched-holdout-v2-target.json"
    ).exists()
    assert (
        ROOT / "docs/evals/lolla-r4-matched-holdout-v2-contract.json"
    ).exists()


def test_exact_human_declaration_unlocks_only_the_reviewed_source_prior_hashes() -> None:
    cases = load_v2_source_prior()
    review = build_human_review_record(
        cases,
        declaration=HUMAN_LEAKAGE_DECLARATION,
    )

    assert HUMAN_LEAKAGE_DECLARATION == "human leakage review passes"
    assert review["status"] == "human_semantic_leakage_review_passed"
    assert review["human_declaration"] == HUMAN_LEAKAGE_DECLARATION
    assert review["human_review_required_before_target"] == "satisfied"
    assert review["target_authorship_may_begin"] is True
    assert review["human_semantic_sufficiency_decided"] is True
    assert review["deterministic_semantic_sufficiency_decided"] is False
    assert review["byte_change_invalidates_review"] is True
    assert review["provider_calls"] == 0
    assert review["provider_cost_usd"] == 0.0
    assert validate_human_review_record(review, cases=cases) == review

    assert [row["case_id"] for row in review["cases"]] == list(CASE_IDS)
    for row in review["cases"]:
        assert row["human_semantic_leakage_review"] == "passed"
        assert row["last_four_sufficient_for_both_surfaces"] is False
        assert row["assistant_states_expected_category"] is False
        assert row["prior_self_discounting"] is False
        assert row["source_instructs_emit_or_suppress"] is False
        assert row["source_sha256"] == cases[row["case_id"]]["source_sha256"]
        assert row["prior_sha256"] == cases[row["case_id"]]["prior_sha256"]

    changed = {case_id: dict(case) for case_id, case in cases.items()}
    changed[CASE_IDS[0]]["source_sha256"] = "0" * 64
    with pytest.raises(R4MatchedHoldoutV2Error, match="reviewed source/prior hash"):
        validate_human_review_record(review, cases=changed)

    with pytest.raises(R4MatchedHoldoutV2Error, match="exact human declaration"):
        build_human_review_record(cases, declaration="review passes")


def test_human_review_and_source_prior_freeze_are_exact_before_target() -> None:
    expected = build_human_review_freeze_files()
    review = validate_human_review_freeze()

    assert set(expected) == {
        "research/lolla-r4-matched-holdout-v2-source-freeze-2026-07-14/leakage-audit.json",
        "research/lolla-r4-matched-holdout-v2-source-freeze-2026-07-14/freeze-manifest.json",
    }
    for relative, raw in expected.items():
        assert (ROOT / relative).read_bytes() == raw

    assert review["status"] == "human_semantic_leakage_review_passed"
    freeze = json.loads(
        expected[
            "research/lolla-r4-matched-holdout-v2-source-freeze-2026-07-14/freeze-manifest.json"
        ]
    )
    assert freeze["status"] == "source_prior_and_human_review_frozen_before_target"
    assert freeze["source_prior_checkpoint_commit"] == (
        "1d02d2abc1f416178fbd00a9f0b93aad353c24b2"
    )
    assert freeze["target_existed_when_frozen"] is False
    assert freeze["request_preview_existed_when_frozen"] is False
    assert freeze["provider_output_existed_when_frozen"] is False
    assert len(freeze["cases"]) == 4
    assert (
        ROOT / "docs/evals/lolla-r4-matched-holdout-v2-target.json"
    ).exists()
    assert (
        ROOT / "docs/evals/lolla-r4-matched-holdout-v2-contract.json"
    ).exists()


def test_protected_source_first_target_is_hash_bound_and_predates_requests() -> None:
    target = load_source_first_target()
    cases = {row["case_id"]: row for row in target["cases"]}

    assert target["status"] == "frozen_after_human_review_before_request_previews"
    assert target["review_method"] == (
        "human_source_first_product_ontology_before_any_provider_output"
    )
    assert target["provider_outputs_existed_when_authored"] is False
    assert target["target_visible_to_provider"] is False
    assert target["runner_may_load_target"] is False
    assert target["provider_calls"] == 0
    assert target["provider_cost_usd"] == 0.0
    assert target["valid_reader_states"] == [
        "supported",
        "quiet",
        "ambiguous",
        "partial",
        "failed",
        "missing",
    ]
    assert set(cases) == set(CASE_IDS)

    expected = {
        CASE_IDS[0]: {"unresolved_matter": "quiet", "reopen_condition": "quiet"},
        CASE_IDS[1]: {"unresolved_matter": "quiet", "reopen_condition": "quiet"},
        CASE_IDS[2]: {
            "unresolved_matter": "supported",
            "reopen_condition": "quiet",
        },
        CASE_IDS[3]: {
            "unresolved_matter": "quiet",
            "reopen_condition": "supported",
        },
    }
    source_inputs = load_v2_source_prior()
    for case_id, surfaces in expected.items():
        row = cases[case_id]
        assert row["source_sha256"] == source_inputs[case_id]["source_sha256"]
        assert row["prior_sha256"] == source_inputs[case_id]["prior_sha256"]
        assert {
            surface: value["disposition"]
            for surface, value in row["canonical_surface_targets"].items()
        } == surfaces
        for surface, disposition in surfaces.items():
            review = row["canonical_surface_targets"][surface]
            assert len(review["strongest_source_aliases"]) >= 3
            assert review["expected_speaker_ownership"]
            assert review["expected_modal_force"]
            assert review["outside_adopted_machinery_reason"]
            if disposition == "supported":
                assert review["expected_result"]["outcome"] == "records_present"
                assert len(review["expected_result"]["records"]) == 1
            else:
                assert review["expected_result"] == {
                    "outcome": "no_supported_record_observed",
                    "records": [],
                }

    assert target["evaluation_limitations"][0]["kind"] == (
        "recent_summary_assistance"
    )
    assert (
        ROOT / "research/lolla-r4-matched-holdout-v2-contract-2026-07-14"
    ).exists()
    assert (
        ROOT / "docs/evals/lolla-r4-matched-holdout-v2-contract.json"
    ).exists()


def test_target_review_metadata_freezes_target_before_request_generation() -> None:
    review = validate_source_first_target_freeze()

    assert review["status"] == "protected_target_frozen_before_requests"
    assert review["target"]["path"] == (
        "docs/evals/lolla-r4-matched-holdout-v2-target.json"
    )
    assert review["target"]["sha256"] == _sha(
        ROOT / review["target"]["path"]
    )
    assert review["human_review_checkpoint_commit"] == (
        "04706f67620b2548754454178a594d30228925ac"
    )
    assert review["request_previews_existed_when_target_frozen"] is False
    assert review["provider_outputs_existed_when_target_frozen"] is False
    assert review["runner_may_load_review_metadata"] is False
    assert review["provider_calls"] == 0
    assert review["provider_cost_usd"] == 0.0


def test_exact_matched_provider_blind_request_previews_preserve_full_context() -> None:
    expected = build_request_preview_files()
    result = validate_request_preview_files()
    inputs = load_v2_source_prior()

    assert len(expected) == 32
    assert result == {
        "status": "provider_blind_request_previews_valid",
        "case_count": 4,
        "request_count": 8,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }
    protected_terms = (
        "lolla-r4-matched-holdout-v2-target",
        "target-review",
        "leakage-audit",
        "human leakage review passes",
        "target_role",
    )
    for relative, raw in expected.items():
        assert (ROOT / relative).read_bytes() == raw
        lowered = raw.decode("utf-8").lower()
        assert not any(term in lowered for term in protected_terms)

    for case_id in CASE_IDS:
        case_root = REQUEST_OUTPUT_ROOT / "cases" / case_id
        packet = json.loads((case_root / "uncertainty-packet.json").read_text())
        arm_a = json.loads((case_root / "arm-a-request-preview.json").read_text())
        arm_b = json.loads((case_root / "arm-b-request-preview.json").read_text())
        manifest_a = json.loads((case_root / "arm-a-context-manifest.json").read_text())
        manifest_b = json.loads((case_root / "arm-b-context-manifest.json").read_text())
        source_text = json.dumps(
            packet["source"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        prior_text = json.dumps(
            packet["prior_interpretation_context"],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        for preview, manifest in ((arm_a, manifest_a), (arm_b, manifest_b)):
            user = preview["body"]["messages"][1]["content"]
            assert user.count(source_text) == 1
            assert user.count(prior_text) == 1
            assert user.index(source_text) < user.index(prior_text) < user.index("<task>")
            assert user.rstrip().endswith("</task>")
            assert manifest["complete_source_inclusion"] is True
            assert manifest["source"]["artifact_sha256"] == inputs[case_id][
                "source_sha256"
            ]
            assert manifest["prior"]["artifact_sha256"] == inputs[case_id][
                "prior_sha256"
            ]
            assert manifest["no_summary_chunking_filter_or_semantic_gate"] is True
        for field in ("max_tokens", "model", "provider", "reasoning", "seed", "stream"):
            assert arm_a["body"][field] == arm_b["body"][field]
        assert arm_a["body"]["max_tokens"] == 1600
        assert arm_a["body"]["model"] == "google/gemini-3.1-flash-lite"
        assert arm_a["body"]["provider"]["only"] == ["google-vertex"]
        assert arm_a["body"]["provider"]["allow_fallbacks"] is False


def test_exact_declared_request_deltas_reject_every_undeclared_change() -> None:
    expected = build_matched_delta_files()
    result = validate_matched_delta_files()

    assert len(expected) == 4
    assert result == {
        "status": "exact_matched_request_deltas_valid",
        "case_count": 4,
        "undeclared_difference_count": 0,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }
    for case_id in CASE_IDS:
        case_root = REQUEST_OUTPUT_ROOT / "cases" / case_id
        relative = str(
            (case_root / "matched-request-delta.json").relative_to(ROOT)
        )
        assert (ROOT / relative).read_bytes() == expected[relative]
        delta = json.loads(expected[relative])
        assert delta["matched_source_and_prior"] is True
        assert delta["paired_task_shape_unchanged"] is True
        assert delta["undeclared_differences"] == []
        assert len(delta["schema_difference_paths"]) == 13

        packet = json.loads((case_root / "uncertainty-packet.json").read_text())
        arm_a = json.loads((case_root / "arm-a-request-preview.json").read_text())
        arm_b = json.loads((case_root / "arm-b-request-preview.json").read_text())
        changed = json.loads(json.dumps(arm_b))
        changed["body"]["seed"] += 1
        with pytest.raises(R4MatchedHoldoutV2Error, match="exact frozen residual"):
            validate_matched_request_pair(
                packet=packet,
                arm_a=arm_a,
                arm_b=changed,
            )


def test_non_authorizing_contract_freezes_counterbalanced_eight_call_envelope() -> None:
    expected = build_contract_files()
    contract = validate_contract_package()

    assert set(expected) == {
        "docs/evals/lolla-r4-matched-holdout-v2-contract.json",
        "research/lolla-r4-matched-holdout-v2-contract-2026-07-14/execution-manifest.json",
        "research/lolla-r4-matched-holdout-v2-contract-2026-07-14/manifest.json",
    }
    for relative, raw in expected.items():
        assert (ROOT / relative).read_bytes() == raw
    assert contract["status"] == (
        "provider_free_matched_holdout_v2_frozen_no_authorization"
    )
    assert contract["provider_calls_made"] == 0
    assert contract["provider_cost_usd"] == 0.0
    assert contract["decision_boundary"]["provider_calls_authorized"] is False
    assert contract["decision_boundary"]["authorization_file_present"] is False
    assert contract["decision_boundary"]["package_requests_authorization"] is False
    assert contract["budget"]["maximum_provider_calls"] == 8
    assert contract["budget"]["conservative_estimated_total_cost_usd"] == 0.040521
    assert contract["budget"]["hard_provider_reported_cost_per_case_usd"] == 0.03
    assert contract["budget"]["hard_provider_reported_cost_total_usd"] == 0.12
    assert [(row["case_id"], row["arm"][0]) for row in contract["call_plan"]] == [
        (CASE_IDS[0], "A"),
        (CASE_IDS[0], "B"),
        (CASE_IDS[1], "B"),
        (CASE_IDS[1], "A"),
        (CASE_IDS[2], "B"),
        (CASE_IDS[2], "A"),
        (CASE_IDS[3], "A"),
        (CASE_IDS[3], "B"),
    ]
    assert contract["operator"]["model"] == "google/gemini-3.1-flash-lite"
    assert contract["operator"]["provider_only"] == ["google-vertex"]
    assert contract["operator"]["allow_fallbacks"] is False
    assert contract["operator"]["maximum_output_tokens"] == 1600
    assert contract["operator"]["reasoning"] == {
        "effort": "minimal",
        "exclude": True,
    }
    assert contract["evaluation_contract"]["scalar_quality_score"] is None
    assert len(contract["evaluation_contract"]["vector"]) == 10
    assert contract["frozen_history"]["provider_free_corpus_replay"] == {
        "cases": 12,
        "case_artifact_links": 543,
        "unique_frozen_json_artifacts": 400,
    }
    serialized = json.dumps(contract, sort_keys=True).lower()
    assert "lolla-r4-matched-holdout-v2-target" not in serialized
    assert "target-review" not in serialized
    assert HUMAN_LEAKAGE_DECLARATION not in serialized
    assert not list(ROOT.glob("**/*matched-holdout-v2*authorization*.json"))


def test_future_runner_is_target_blind_and_requires_exact_separate_authorization(
    tmp_path: Path,
) -> None:
    contract = runner.validate_contract()
    source = Path(runner.__file__).read_text(encoding="utf-8").lower()
    execution_manifest = json.loads(
        (
            ROOT
            / "research/lolla-r4-matched-holdout-v2-contract-2026-07-14/execution-manifest.json"
        ).read_text(encoding="utf-8")
    )

    assert "target" not in source
    assert "leakage" not in source
    assert HUMAN_LEAKAGE_DECLARATION not in source
    assert "target" not in json.dumps(execution_manifest).lower()
    assert execution_manifest["protected_review_reference_present"] is False
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
    with pytest.raises(runner.R4MatchedHoldoutV2RunError, match="authorization"):
        runner.validate_authorization(authorization, contract=contract)


def test_dry_run_cannot_construct_transport(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = runner.validate_contract()
    frozen_runner = contract["future_runner"]
    runner_path = ROOT / frozen_runner["path"]

    assert runner_path.resolve() == Path(runner.__file__).resolve()
    assert _sha(runner_path) == frozen_runner["sha256"]
    monkeypatch.setattr(
        runner,
        "_openrouter_transport",
        lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("dry run attempted to construct network transport")
        ),
    )
    assert runner.main(["--dry-run"]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "authorization_present": False,
        "conservative_estimated_total_cost_usd": 0.040521,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "status": "frozen_matched_residual_v2_contract_valid",
    }


class _FakeSuccessfulTransport:
    def __init__(self) -> None:
        self.request_hashes: list[str] = []

    def __call__(self, body: dict) -> bytes:
        self.request_hashes.append(hashlib.sha256(canonical_json_bytes(body)).hexdigest())
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
    transport = _FakeSuccessfulTransport()
    result = runner.execute(
        contract=contract,
        authorization_path=_authorization_file(tmp_path, contract),
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
    assert all(row["operator_attribution_ok"] for row in result["calls"])
    assert all(row["reasoning_custody"]["exclusion_satisfied"] for row in result["calls"])
    assert all(row["local_admission_status"] == "passed" for row in result["calls"])
    assert len(list((tmp_path / "run").glob("call-*-raw-response.bin"))) == 8
    assert {
        "relationship_calls": result["relationship_calls"],
        "evaluator_calls": result["evaluator_calls"],
        "embedding_calls": result["embedding_calls"],
        "graph_calls": result["graph_calls"],
        "pipeline_calls": result["pipeline_calls"],
        "runtime_calls": result["runtime_calls"],
    } == {
        "relationship_calls": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }


class _FailOnThirdTransport(_FakeSuccessfulTransport):
    def __call__(self, body: dict) -> bytes:
        if len(self.request_hashes) == 2:
            self.request_hashes.append(
                hashlib.sha256(canonical_json_bytes(body)).hexdigest()
            )
            raise OSError("synthetic first transport failure")
        return super().__call__(body)


def test_first_transport_failure_stops_without_retry_fallback_or_healing(
    tmp_path: Path,
) -> None:
    contract = runner.validate_contract()
    transport = _FailOnThirdTransport()
    output = tmp_path / "failed-run"
    result = runner.execute(
        contract=contract,
        authorization_path=_authorization_file(tmp_path, contract),
        output=output,
        transport=transport,
    )

    assert result["status"] == "stopped_on_first_failure"
    assert result["provider_calls"] == 3
    assert result["call_ordinals"] == [1, 2, 3]
    assert result["calls"][-1]["operational_status"] == "transport_failure"
    assert not (output / "call-04-started.json").exists()
    assert result["automatic_retries"] == 0
    assert result["semantic_retries"] == 0
    assert result["fallback_models"] == 0
    assert result["response_healing"] is False


def test_first_http_failure_preserves_exact_terminal_bytes(tmp_path: Path) -> None:
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
        payload = json.loads(super().__call__(body))
        if self.mutation == "model_identity":
            payload["model"] = "undeclared/model"
        elif self.mutation == "provider_identity":
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
            payload["usage"]["cost"] = 0.04
        else:
            raise AssertionError(self.mutation)
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


@pytest.mark.parametrize(
    ("mutation", "expected_status"),
    [
        ("model_identity", "operator_attribution_failure"),
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


def test_execution_artifact_tampering_fails_before_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = json.loads(Path(runner.DEFAULT_CONTRACT).read_text(encoding="utf-8"))
    preview_path = ROOT / contract["call_plan"][0]["request_preview_path"]
    original_read_bytes = Path.read_bytes

    def tampered_read_bytes(path: Path) -> bytes:
        raw = original_read_bytes(path)
        return raw + b" " if path.resolve() == preview_path.resolve() else raw

    monkeypatch.setattr(Path, "read_bytes", tampered_read_bytes)
    with pytest.raises(runner.R4MatchedHoldoutV2RunError, match="artifact drifted"):
        runner.validate_contract()
