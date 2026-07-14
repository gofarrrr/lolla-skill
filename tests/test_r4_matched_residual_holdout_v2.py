from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from scripts.evals.build_r4_matched_holdout_v2_contract import (
    CASE_IDS,
    FORBIDDEN_ANSWER_LANGUAGE,
    HUMAN_LEAKAGE_DECLARATION,
    R4MatchedHoldoutV2Error,
    build_human_review_freeze_files,
    build_human_review_record,
    build_pre_target_audit,
    lint_v2_source_prior,
    load_v2_source_prior,
    validate_human_review_freeze,
    validate_human_review_record,
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


def test_pre_target_audit_records_custody_and_keeps_semantic_gate_human() -> None:
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
    assert audit["status"] == "awaiting_founder_pm_human_semantic_review"
    assert audit["deterministic_vocabulary_lint"]["exact_match_count"] == 0
    assert audit["human_review_required_before_target"] is True
    assert audit["deterministic_semantic_sufficiency_decided"] is False
    assert audit["target_authored"] is False
    assert audit["request_preview_authored"] is False
    assert audit["provider_calls"] == 0
    assert audit["provider_cost_usd"] == 0.0

    assert [row["case_id"] for row in audit["cases"]] == list(CASE_IDS)
    for row in audit["cases"]:
        case = cases[row["case_id"]]
        assert row["source_sha256"] == case["source_sha256"]
        assert row["prior_sha256"] == case["prior_sha256"]
        assert row["last_four_message_indices"] == [25, 26, 27, 28]
        assert len(row["last_four_canonical_sha256"]) == 64
        assert row["human_semantic_leakage_review"] == "pending"
        assert row["last_four_sufficient_for_both_surfaces"] is None
        assert row["assistant_states_expected_category"] is None
        assert row["prior_self_discounting"] is None
        assert row["source_instructs_emit_or_suppress"] is None

    assert not (
        ROOT / "docs/evals/lolla-r4-matched-holdout-v2-target.json"
    ).exists()
    assert not (
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
    assert not (
        ROOT / "docs/evals/lolla-r4-matched-holdout-v2-target.json"
    ).exists()
    assert not (
        ROOT / "docs/evals/lolla-r4-matched-holdout-v2-contract.json"
    ).exists()
