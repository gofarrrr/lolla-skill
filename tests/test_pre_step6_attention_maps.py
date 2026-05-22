from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_attention_maps import (  # noqa: E402
    MAX_RENDER_CHARS,
    Step6AttentionMapValidationError,
    render_step6_attention_map,
    validate_step6_attention_map_payload,
)
from pre_step6_build_attention_map import build_step6_attention_map  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "research/pre-step6-attention-maps"
PROBLEM_STATE_DIR = REPO_ROOT / "research/pre-step6-problem-states"
AFFORDANCE_DIR = REPO_ROOT / "research/pre-step6-reasoning-affordances"


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_valid_step6_attention_map_fixture_validates() -> None:
    payload = _load_fixture("mother-address-year.step6-attention-map.v1.json")

    validate_step6_attention_map_payload(payload)


def test_attention_map_rejects_edge_items_without_boundaries() -> None:
    payload = _load_fixture("mother-address-year.step6-attention-map.v1.json")
    edge = payload["edge_latticework_reserve"][0]
    edge["cheap_test"] = ""
    edge["risk_if_forced"] = ""
    edge["risk_if_ignored"] = ""
    edge["expansion_ref"] = ""

    with pytest.raises(Step6AttentionMapValidationError) as exc:
        validate_step6_attention_map_payload(payload)

    message = str(exc.value)
    assert "cheap_test" in message
    assert "risk_if_forced" in message
    assert "risk_if_ignored" in message
    assert "expansion_ref" in message


def test_attention_map_rejects_parked_items_without_reactivation_refs() -> None:
    payload = _load_fixture("mother-address-year.step6-attention-map.v1.json")
    parked = payload["parked_but_preserved"][0]
    parked["park_reason"] = ""
    parked["reactivate_if"] = ""
    parked["expansion_ref"] = ""

    with pytest.raises(Step6AttentionMapValidationError) as exc:
        validate_step6_attention_map_payload(payload)

    message = str(exc.value)
    assert "park_reason" in message
    assert "reactivate_if" in message
    assert "expansion_ref" in message


def test_attention_map_rejects_non_advisory_instruction_language() -> None:
    payload = _load_fixture("mother-address-year.step6-attention-map.v1.json")
    payload["step6_instruction"] = "Step 6 should conclude with the final recommendation."

    with pytest.raises(Step6AttentionMapValidationError, match="forbidden language"):
        validate_step6_attention_map_payload(payload)


def test_builder_preserves_active_and_protected_edge_affordances() -> None:
    problem_state = json.loads(
        (PROBLEM_STATE_DIR / "mother-address-year.problem-state.v1.json").read_text(
            encoding="utf-8"
        )
    )
    affordances = [
        json.loads(
            (AFFORDANCE_DIR / "mother-silence.active.reasoning-affordance.v1.json").read_text(
                encoding="utf-8"
            )
        ),
        json.loads(
            (
                AFFORDANCE_DIR
                / "founder-valuation-denominator.scan.reasoning-affordance.v1.json"
            ).read_text(encoding="utf-8")
        ),
    ]

    payload = build_step6_attention_map(
        case_id="mixed-preservation-test",
        problem_state=problem_state,
        affordances=affordances,
        full_archive_refs=["archive:mixed"],
    )

    validate_step6_attention_map_payload(payload)
    assert any(
        item["artifact_id"] == "mother_surveillance_instrument_trust_gate"
        for item in payload["active_working_set"]
    )
    assert any(
        item["artifact_id"] == "founder_duplicate_valuation_base_rate_gate"
        and item["protected_slot"] == "denominator"
        for item in payload["edge_latticework_reserve"]
    )


def test_builder_preserves_low_fit_protected_items_in_parked_section() -> None:
    problem_state = json.loads(
        (PROBLEM_STATE_DIR / "mother-address-year.problem-state.v1.json").read_text(
            encoding="utf-8"
        )
    )
    affordance = json.loads(
        (
            AFFORDANCE_DIR / "founder-architecture-false-friend.reasoning-affordance.v1.json"
        ).read_text(encoding="utf-8")
    )

    payload = build_step6_attention_map(
        case_id="mixed-parked-test",
        problem_state=problem_state,
        affordances=[affordance],
        full_archive_refs=["archive:mixed"],
    )

    validate_step6_attention_map_payload(payload)
    assert any(
        item["artifact_id"] == "founder_misfit_architecture_note_hybrid_quiet"
        for item in payload["parked_but_preserved"]
    )


def test_consultant_attention_map_keeps_negative_control_bounded() -> None:
    payload = _load_fixture("mid-level-consultant-report-2.step6-attention-map.v1.json")

    validate_step6_attention_map_payload(payload)
    active_ids = {item["artifact_id"] for item in payload["active_working_set"]}
    edge_ids = {item["artifact_id"] for item in payload["edge_latticework_reserve"]}
    parked_ids = {item["artifact_id"] for item in payload["parked_but_preserved"]}

    assert "consultant_counsel_incentive_gate" in active_ids
    assert "consultant_wednesday_protocol_boundary" in active_ids
    assert "consultant_internal_channel_distinction" in edge_ids
    assert "consultant_power_dynamics_misfit_discard" in parked_ids


def test_phd_v2_attention_map_activates_silva_and_preserves_fallback_stop_rule() -> None:
    payload = _load_fixture("third-year-phd-student.v2.step6-attention-map.v1.json")

    validate_step6_attention_map_payload(payload)
    active_ids = {item["artifact_id"] for item in payload["active_working_set"]}
    parked_ids = {item["artifact_id"] for item in payload["parked_but_preserved"]}

    assert "phd_silva_constraint_retest" in active_ids
    assert "phd_fallback_viability_boundary_parked" in parked_ids


def test_rendered_attention_map_stays_capped_and_keeps_archive_refs() -> None:
    payload = _load_fixture("mother-address-year.step6-attention-map.v1.json")

    rendered = render_step6_attention_map(payload)

    assert len(rendered) <= MAX_RENDER_CHARS
    assert "FULL ARCHIVE REFS" in rendered
    assert "research/pre-step6-raw-artifact-fixtures/mother-address-year.raw-artifact-handoff.v1.json" in rendered


def test_static_attention_map_fixtures_validate() -> None:
    paths = sorted(FIXTURE_DIR.glob("*.step6-attention-map.v1.json"))

    assert {path.name for path in paths} == {
        "founder-grant-marcus-equity.high-clutter.step6-attention-map.v1.json",
        "mid-level-consultant-report-2.step6-attention-map.v1.json",
        "mother-address-year.step6-attention-map.v1.json",
        "third-year-phd-student.step6-attention-map.v1.json",
        "third-year-phd-student.v2.step6-attention-map.v1.json",
    }
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_step6_attention_map_payload(payload, path=path)
        assert len(render_step6_attention_map(payload)) <= MAX_RENDER_CHARS
