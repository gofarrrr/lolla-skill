from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.system_b.conversation_state_candidates import build_source_catalog
from engine.system_b.reasoning_process_views import (
    COVERAGE_CANDIDATES_SCHEMA,
    PHASE2_REPORT_SCHEMA,
    ReasoningProcessViewError,
    build_coverage_candidates,
    build_fan_in_stress_fixture,
    build_phase2_artifacts,
    build_probe_input_packet,
    canonical_json_bytes,
    resolve_target_evidence,
    sha256_bytes,
    sha256_file,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/evals/reasoning-process-phase2-coverage-contract-v1.json"
REVIEW_PATH = ROOT / "docs/evals/reasoning-process-phase2-coverage-review-v1.json"
OUTPUT = ROOT / "research/reasoning-process-phase2-views-2026-07-11"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def phase2_inputs() -> tuple[dict, dict, dict]:
    contract = _load(CONTRACT_PATH)
    candidates = build_coverage_candidates(contract=contract, repo_root=ROOT)
    review = _load(REVIEW_PATH)
    return contract, candidates, review


def test_exact_quote_resolution_prefers_unique_sentence() -> None:
    text = "[Turn 1] USER:\nFirst sentence. Exact target sentence."
    catalog = build_source_catalog(source_text=text, source_path="fixture.txt")
    span = resolve_target_evidence(
        catalog=catalog,
        speaker="user",
        turn_index=1,
        quote="Exact target sentence.",
    )
    assert span.kind == "sentence"
    assert span.text == "Exact target sentence."


def test_exact_quote_resolution_fails_closed() -> None:
    catalog = build_source_catalog(
        source_text="[Turn 1] USER:\nOnly source sentence.",
        source_path="fixture.txt",
    )
    with pytest.raises(ReasoningProcessViewError, match="target quote not found"):
        resolve_target_evidence(
            catalog=catalog,
            speaker="assistant",
            turn_index=1,
            quote="Invented text.",
        )


def test_coverage_candidates_lock_sources_and_do_not_decide_semantics(
    phase2_inputs: tuple[dict, dict, dict],
) -> None:
    contract, candidates, _ = phase2_inputs
    assert candidates["schema_version"] == COVERAGE_CANDIDATES_SCHEMA
    assert candidates["case_count"] == 5
    assert candidates["target_count"] == 25
    assert candidates["coverage_contract_sha256"] == sha256_bytes(
        canonical_json_bytes(contract)
    )
    assert candidates["boundary"] == {
        "exact_source_resolution_deterministic": True,
        "overlap_is_semantic_coverage": False,
        "semantic_coverage_decided_by_code": False,
        "provider_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "runtime_calls": 0,
    }
    assert sum(
        target["mechanical_overlap_count"] > 0
        for case in candidates["cases"]
        for target in case["targets"]
    ) == 11
    assert all(
        target["semantic_coverage_decided_by_code"] is False
        for case in candidates["cases"]
        for target in case["targets"]
    )


def test_review_discloses_strict_source_review_and_full_decision_accounting(
    phase2_inputs: tuple[dict, dict, dict],
) -> None:
    _, _, review = phase2_inputs
    decisions = [
        target for case in review["cases"] for target in case["targets"]
    ]
    assert len(decisions) == 25
    assert sum(item["decision"] == "covered_by_phase1" for item in decisions) == 1
    assert sum(item["decision"] == "addendum_required" for item in decisions) == 24
    assert review["reviewer_independence"] == "same_project_session_not_blind"
    assert review["boundary"]["exact_overlap_treated_as_semantic_coverage"] is False
    assert review["boundary"]["source_review_treated_as_independent_gold"] is False


def test_phase2_builds_append_only_views_with_complete_accounting(
    phase2_inputs: tuple[dict, dict, dict],
) -> None:
    contract, candidates, review = phase2_inputs
    before_hashes = {
        case["case_id"]: sha256_file(ROOT / case["phase1_ledger_path"])
        for case in contract["cases"]
    }
    result = build_phase2_artifacts(
        contract=contract,
        candidates=candidates,
        review=review,
        repo_root=ROOT,
    )
    assert result["schema_version"] == PHASE2_REPORT_SCHEMA
    assert result["status"] == "provider_free_pass"
    assert result["case_count"] == 5
    assert result["view_count"] == 25
    assert result["addendum_observation_count"] == 24
    assert set(result["calls"].values()) == {0}
    assert all(case["coverage_state"] == "ready" for case in result["cases"])

    views = [view for case in result["cases"] for view in case["views"]]
    probe_inputs = [probe for case in result["cases"] for probe in case["probe_inputs"]]
    assert len(views) == 25
    assert all(view["budget"]["budget_exceeded"] is False for view in views)
    assert max(view["budget"]["observed_input_observations"] for view in views) == 29
    assert max(view["budget"]["observed_input_utf8_bytes"] for view in views) < 9000
    assert all(
        len(view["dispositions"])
        == view["budget"]["observed_input_observations"]
        for view in views
    )
    assert len(probe_inputs) == 25
    assert max(
        probe["metrics"]["observed_input_utf8_bytes"] for probe in probe_inputs
    ) < 17000
    assert all(
        probe["metrics"]["auxiliary_ledger_omitted_whole"] is False
        and probe["packet"]["boundary"]["protected_target_included"] is False
        and probe["packet"]["boundary"]["source_review_addendum_included"] is False
        and "phase2-source-review-" not in json.dumps(probe["packet"])
        for probe in probe_inputs
    )
    assert all(
        view["boundary"]["semantic_selection_performed_by_code"] is False
        and view["boundary"]["direct_graph_routing_allowed"] is False
        for view in views
    )

    for case in result["cases"]:
        assert case["addendum"]["boundary"]["phase1_ledger_modified"] is False
        assert all(
            observation["graph_routing_eligible"] is False
            for observation in case["addendum"]["observations"]
        )
    after_hashes = {
        case["case_id"]: sha256_file(ROOT / case["phase1_ledger_path"])
        for case in contract["cases"]
    }
    assert after_hashes == before_hashes


def test_challenge_views_use_prospective_addenda_not_silent_phase1_relabeling(
    phase2_inputs: tuple[dict, dict, dict],
) -> None:
    contract, candidates, review = phase2_inputs
    result = build_phase2_artifacts(
        contract=contract,
        candidates=candidates,
        review=review,
        repo_root=ROOT,
    )
    challenge_views = [
        view
        for case in result["cases"]
        for view in case["views"]
        if view["view_kind"] == "challenge_and_revision_response"
    ]
    assert len(challenge_views) == 5
    assert all(
        view["items"][0]["source_observation_ids"][0].startswith(
            "phase2-source-review-"
        )
        for view in challenge_views
    )
    case05 = next(
        case for case in result["cases"] if case["case_id"] == "amb1-case05-family-archive"
    )
    position_view = next(
        view
        for view in case05["views"]
        if view["view_kind"] == "position_and_decision_trajectory"
    )
    assert position_view["items"][0]["source_observation_ids"] == [
        "csynth-positions-001-ff8697a3ba3b"
    ]


def test_review_cannot_claim_phase1_coverage_without_overlap(
    phase2_inputs: tuple[dict, dict, dict],
) -> None:
    contract, candidates, review = phase2_inputs
    corrupted = json.loads(json.dumps(review))
    target = corrupted["cases"][0]["targets"][1]
    target["decision"] = "covered_by_phase1"
    target["phase1_observation_ids"] = ["invented-observation"]
    with pytest.raises(ReasoningProcessViewError, match="non-overlapping"):
        build_phase2_artifacts(
            contract=contract,
            candidates=candidates,
            review=corrupted,
            repo_root=ROOT,
        )


def test_long_conversation_fan_in_stress_hits_observation_ceiling_without_overflow() -> None:
    source_path = ROOT / "research/test-cases/case_parenting_teen_conversation.txt"
    fixture = build_fan_in_stress_fixture(
        source_text=source_path.read_text(encoding="utf-8"),
        source_path="research/test-cases/case_parenting_teen_conversation.txt",
        source_sha256="c8a8cfa4280cd2d359cdf89736c4c54e415c6a23ed24ac4ab01442b41edae3b4",
    )
    assert fixture["status"] == "provider_free_representation_pass"
    assert fixture["source_manifest"]["message_count"] == 24
    assert fixture["view"]["budget"]["observed_input_observations"] == 32
    assert fixture["view"]["budget"]["observed_input_utf8_bytes"] < 24000
    assert fixture["view"]["budget"]["budget_exceeded"] is False
    assert fixture["probe_input"]["metrics"]["observed_input_utf8_bytes"] == 21307
    assert fixture["probe_input"]["metrics"]["auxiliary_ledger_omitted_whole"] is True
    assert fixture["probe_input"]["metrics"]["auxiliary_observation_count_available"] == 32
    assert fixture["probe_input"]["metrics"]["auxiliary_observation_count_included"] == 0
    assert fixture["boundary"]["semantic_quality_evaluated"] is False


def test_probe_input_omits_auxiliary_ledger_whole_instead_of_semantic_truncation() -> None:
    source_path = ROOT / "research/test-cases/case_parenting_teen_conversation.txt"
    source_text = source_path.read_text(encoding="utf-8")
    observations = [
        {
            "observation_id": f"stress-{index:03d}",
            "family": "exploration_and_alternatives",
            "interpretation": "A deliberately large auxiliary record. " * 20,
            "semantic_status": "unclear",
            "source_span_ids": ["span-placeholder"],
        }
        for index in range(32)
    ]
    result = build_probe_input_packet(
        case_id="stress-case",
        source_path="research/test-cases/case_parenting_teen_conversation.txt",
        source_sha256="c8a8cfa4280cd2d359cdf89736c4c54e415c6a23ed24ac4ab01442b41edae3b4",
        source_text=source_text,
        base_observations=observations,
        view_kind="exploration_and_alternatives",
    )
    assert result["metrics"]["auxiliary_ledger_omitted_whole"] is True
    assert result["metrics"]["auxiliary_observation_count_available"] == 32
    assert result["metrics"]["auxiliary_observation_count_included"] == 0
    assert result["packet"]["auxiliary_phase1_ledger"]["observations"] == []
    assert result["packet"]["boundary"]["semantic_prefilter_performed"] is False


def test_checked_in_phase2_artifacts_match_frozen_counts() -> None:
    report = _load(OUTPUT / "report.json")
    assert report["status"] == "provider_free_pass"
    assert report["view_count"] == 25
    assert report["addendum_observation_count"] == 24
    assert report["fan_in_stress"] == {
        "artifact_path": "research/reasoning-process-phase2-views-2026-07-11/fan-in-stress-fixture.json",
        "budget_exceeded": False,
        "input_observation_count": 32,
        "input_utf8_bytes": 7851,
        "probe_auxiliary_ledger_omitted_whole": True,
        "probe_input_utf8_bytes": 21307,
        "semantic_quality_evaluated": False,
        "source_message_count": 24,
        "status": "provider_free_representation_pass",
    }
    checked_views = list((OUTPUT / "cases").glob("*/views/*.json"))
    assert len(checked_views) == 25
    assert all(_load(path)["budget"]["budget_exceeded"] is False for path in checked_views)
