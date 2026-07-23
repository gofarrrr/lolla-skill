from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_graph_increment_rehearsal_result import (
    BLIND_REVIEW_PACKET_RELPATH,
    CONSOLIDATION_RELPATH,
    CONSOLIDATION_SCHEMA_VERSION,
    EXECUTION_SEALED_MANIFEST_RELPATH,
    PAIR_REVIEW_RELPATHS,
    REVIEW_RESPONSE_SCHEMA_VERSION,
    _validate_fresh_pair_review,
    build_blind_review_inputs,
    build_review_consolidation,
    render_json,
    validate_checked_in_blind_review_inputs,
    validate_checked_in_review_consolidation,
)
from engine.system_b.product_delta_paired_screen import (
    DEFAULT_BLIND_PACKETS_RELPATH as CONTROL_BLIND_PACKETS_RELPATH,
    validate_checked_in_screen,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REVIEW_HASHES = {
    "primary": "6fe5453e96c53a1dc4e493fb66c95886d04b4244d553e7f5f79c52237e412033",
    "skeptical": "9e9b7ae54b4453769db0603af1365b48c3a5e2249a99741e41376dabb1d43693",
}


def _read_json(relpath: str) -> dict[str, Any]:
    payload = json.loads((REPO_ROOT / relpath).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_blind_packet_reuses_existing_controls_exactly() -> None:
    blind, _ = build_blind_review_inputs(repo_root=REPO_ROOT)
    control = _read_json(CONTROL_BLIND_PACKETS_RELPATH)
    duplicate = next(
        item
        for item in control["paired_cases"]
        if item["evidence_class"] == "exact_duplicate_null"
    )

    assert blind["qualification_cases"] == control["qualification_cases"]
    assert blind["paired_cases"][0] == duplicate
    assert blind["standdown_cases"] == control["standdown_cases"]


def test_blind_packet_excludes_lineage_and_source_proxy_material() -> None:
    blind, sealed = build_blind_review_inputs(repo_root=REPO_ROOT)
    rendered = render_json(blind)

    for marker in (
        "condition-A",
        "condition-B",
        "f2_fresh_human_controlled_fact_free_direct_only",
        "f3_fresh_human_controlled_fact_free_plus_current_graph",
        "rehearsal_direct_plus_current_one_hop",
        "source-read-primary.json",
        "reference-observation-primary.json",
        "confirmation-bias",
        "incentives",
        "abstraction",
    ):
        assert marker not in rendered
    assert sealed["handling"][
        "unblind_only_after_both_substantive_reviews_are_frozen"
    ]
    assert sealed["blind_review_packet"]["sha256"] == hashlib.sha256(
        rendered.encode("utf-8")
    ).hexdigest()


def test_first_terminal_review_outputs_have_frozen_hashes_and_boundaries() -> None:
    for lane, relpath in PAIR_REVIEW_RELPATHS.items():
        raw = (REPO_ROOT / relpath).read_bytes()
        payload = json.loads(raw)
        assert hashlib.sha256(raw).hexdigest() == EXPECTED_REVIEW_HASHES[lane]
        assert payload["schema_version"] == REVIEW_RESPONSE_SCHEMA_VERSION
        assert payload["fresh_context"] is True
        assert payload["saw_lineage_before_freeze"] is False
        assert payload["saw_source_proxy_reads_before_freeze"] is False
        assert payload["saw_sibling_review_before_freeze"] is False
        assert payload["boundary"] == {
            "answer_quality_scored": False,
            "ground_truth": False,
            "human_validated": False,
            "provider_calls": 0,
            "winner_selected": False,
        }


def test_consolidation_preserves_controls_lineage_and_nonclaims() -> None:
    consolidation, errors = build_review_consolidation(repo_root=REPO_ROOT)

    assert errors == []
    assert consolidation["schema_version"] == CONSOLIDATION_SCHEMA_VERSION
    assert consolidation["status"] == "valid_frozen_agent_diagnostic"
    observations = consolidation["bounded_observations"]
    assert observations["duplicate_null_material_reads"] == [
        "absent",
        "absent",
    ]
    assert observations["new_pair_material_reads"] == ["present", "present"]
    assert observations["standdown_support_reads"] == [
        "supported",
        "supported",
    ]
    assert observations["direct_only_review_arm"] == "A"
    assert observations["current_one_hop_graph_review_arm"] == "B"
    assert (
        observations[
            "both_reviewers_declared_new_pair_lineage_indistinguishable"
        ]
        is True
    )
    boundary = consolidation["boundary"]
    assert boundary["repository_provider_api_calls"] == 0
    assert boundary["codex_agent_contexts_used_total"] == 6
    assert boundary["scalar_summary_created"] is False
    assert boundary["graph_causation_established"] is False
    assert boundary["graph_relevance_established"] is False
    assert boundary["human_usefulness_established"] is False
    assert boundary["permission_to_expand_graph_created"] is False


def test_consolidation_preserves_each_reviewer_atomic_read_side_by_side() -> None:
    consolidation, _ = build_review_consolidation(repo_root=REPO_ROOT)
    new_pair = next(
        item
        for item in consolidation["paired_reviews"]
        if item["case_id"] == "retailer-graph-increment-rehearsal-blind"
    )

    assert len(new_pair["reviewer_reads"]) == 2
    assert all(item["atomic_moves"] for item in new_pair["reviewer_reads"])
    assert {
        item["review_id"] for item in new_pair["reviewer_reads"]
    } == {
        "agent-graph-increment-pair-primary-v1",
        "agent-graph-increment-pair-skeptical-v1",
    }
    assert {
        item["identity_guess_relation_to_graph_lineage"]
        for item in new_pair["reviewer_reads"]
    } == {"declared_indistinguishable"}
    assert "score" not in render_json(new_pair)
    assert "winner" not in render_json(new_pair)


def test_review_validator_fails_closed_on_duplicate_case_or_authority_key() -> None:
    payload = _read_json(PAIR_REVIEW_RELPATHS["primary"])
    qualification_ids = [
        item["case_id"] for item in payload["qualification_reviews"]
    ]
    pair_ids = [item["case_id"] for item in payload["paired_reviews"]]
    standdown_ids = [item["case_id"] for item in payload["standdown_reviews"]]

    duplicated = copy.deepcopy(payload)
    duplicated["qualification_reviews"][1]["case_id"] = qualification_ids[0]
    duplicate_errors = _validate_fresh_pair_review(
        duplicated,
        lane="primary",
        expected_qualification_ids=qualification_ids,
        expected_pair_ids=pair_ids,
        expected_standdown_ids=standdown_ids,
    )
    assert any("case ids or order mismatch" in item for item in duplicate_errors)

    authority_drift = copy.deepcopy(payload)
    authority_drift["winner"] = "B"
    authority_errors = _validate_fresh_pair_review(
        authority_drift,
        lane="primary",
        expected_qualification_ids=qualification_ids,
        expected_pair_ids=pair_ids,
        expected_standdown_ids=standdown_ids,
    )
    assert any("forbidden keys:winner" in item for item in authority_errors)


def test_checked_in_result_artifacts_are_exact_builder_output() -> None:
    blind, sealed = build_blind_review_inputs(repo_root=REPO_ROOT)
    consolidation, errors = build_review_consolidation(repo_root=REPO_ROOT)
    assert errors == []

    for relpath, payload in (
        (BLIND_REVIEW_PACKET_RELPATH, blind),
        (EXECUTION_SEALED_MANIFEST_RELPATH, sealed),
        (CONSOLIDATION_RELPATH, consolidation),
    ):
        assert (REPO_ROOT / relpath).read_text(
            encoding="utf-8"
        ) == render_json(payload)
    assert validate_checked_in_blind_review_inputs(repo_root=REPO_ROOT) == []
    assert validate_checked_in_review_consolidation(repo_root=REPO_ROOT) == []


def test_complete_result_cli_and_existing_paired_screen_are_current() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_product_delta_graph_increment_rehearsal_result.py",
            "--validate-complete",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "rehearsal result is current" in result.stdout
    assert validate_checked_in_screen(repo_root=REPO_ROOT) == []
