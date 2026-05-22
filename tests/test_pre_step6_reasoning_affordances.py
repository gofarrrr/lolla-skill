from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_reasoning_affordances import (  # noqa: E402
    ReasoningAffordanceValidationError,
    affordance_from_raw_artifact,
    parked_affordance_from_candidate,
    validate_reasoning_affordance_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "research/pre-step6-reasoning-affordances"
RAW_DIR = REPO_ROOT / "research/pre-step6-raw-artifact-fixtures"


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_valid_active_reasoning_affordance_fixture_validates() -> None:
    payload = _load_fixture("mother-silence.active.reasoning-affordance.v1.json")

    validate_reasoning_affordance_payload(payload)


def test_affordance_rejects_unknown_enum_values() -> None:
    payload = _load_fixture("mother-silence.active.reasoning-affordance.v1.json")
    payload["affordance_class"] = "interesting"
    payload["protected_slot"] = "pet_theory"
    payload["attention_weight"] = "mandatory"

    with pytest.raises(ReasoningAffordanceValidationError) as exc:
        validate_reasoning_affordance_payload(payload)

    message = str(exc.value)
    assert "affordance_class" in message
    assert "protected_slot" in message
    assert "attention_weight" in message


def test_affordance_rejects_final_advice_and_generic_nuance() -> None:
    payload = _load_fixture("mother-silence.active.reasoning-affordance.v1.json")
    payload["what_it_might_reveal"] = "Use this because it is correct and add nuance."

    with pytest.raises(ReasoningAffordanceValidationError, match="forbidden language"):
        validate_reasoning_affordance_payload(payload)


def test_edge_or_scan_affordance_requires_step6_test_risks_and_expansion_ref() -> None:
    payload = _load_fixture("mother-silence.active.reasoning-affordance.v1.json")
    payload["attention_weight"] = "scan"
    payload["cheap_test_for_step6"] = ""
    payload["risk_if_forced"] = ""
    payload["risk_if_ignored"] = ""
    payload["expansion_ref"] = ""

    with pytest.raises(ReasoningAffordanceValidationError) as exc:
        validate_reasoning_affordance_payload(payload)

    message = str(exc.value)
    assert "cheap_test_for_step6" in message
    assert "risk_if_forced" in message
    assert "risk_if_ignored" in message
    assert "expansion_ref" in message


def test_raw_artifact_converts_to_reasoning_affordance_baseline() -> None:
    raw_payload = json.loads(
        (RAW_DIR / "third-year-phd-student.raw-artifact-handoff.v1.json").read_text(
            encoding="utf-8"
        )
    )
    artifact = raw_payload["artifacts"][0]

    affordance = affordance_from_raw_artifact(
        artifact,
        case_id="third-year-phd-student",
        source_ref="research/pre-step6-raw-artifact-fixtures/third-year-phd-student.raw-artifact-handoff.v1.json:artifacts[0]",
        protected_slot="sequence_stop_rule",
    )

    validate_reasoning_affordance_payload(affordance)
    assert affordance["artifact_id"] == "phd_fallback_viability_boundary"
    assert affordance["source_grounding"] == artifact["source_grounding"]
    assert affordance["risk_if_ignored"] == artifact["risk_if_ignored"]
    assert affordance["attention_weight"] == "active"


def test_low_fit_protected_candidate_parks_with_receipt() -> None:
    candidate = {
        "candidate_id": "founder_duplicate_valuation_base_rate_gate",
        "selection_basis": "Engine surfaced denominator pressure from raw handoff.",
        "summary": "Valuation uncertainty should support but not carry the equity recommendation.",
        "source_refs": ["raw:artifact"],
        "expansion_ref": "raw:artifact",
    }

    affordance = parked_affordance_from_candidate(
        candidate,
        case_id="founder-grant-marcus-equity.high-clutter",
        protected_slot="denominator",
        discard_condition="Discard only if the answer makes no valuation or equity tradeoff claim.",
    )

    validate_reasoning_affordance_payload(affordance)
    assert affordance["attention_weight"] == "parked"
    assert affordance["affordance_class"] == "parked_receipt"
    assert affordance["protected_slot"] == "denominator"
    assert affordance["selection_basis"] == candidate["selection_basis"]
    assert affordance["expansion_ref"] == candidate["expansion_ref"]


def test_static_reasoning_affordance_fixtures_cover_core_classes() -> None:
    paths = sorted(FIXTURE_DIR.glob("*.reasoning-affordance.v1.json"))

    assert {path.name for path in paths} == {
        "consultant-counsel-incentive.active.reasoning-affordance.v1.json",
        "consultant-internal-channel.scan.reasoning-affordance.v1.json",
        "consultant-power-dynamics-false-friend.parked.reasoning-affordance.v1.json",
        "consultant-wednesday-protocol.active.reasoning-affordance.v1.json",
        "founder-architecture-false-friend.reasoning-affordance.v1.json",
        "founder-middle-instruments.duplicate-support.reasoning-affordance.v1.json",
        "founder-valuation-denominator.scan.reasoning-affordance.v1.json",
        "mother-missing-professional-guidance.negative-space.reasoning-affordance.v1.json",
        "mother-silence.active.reasoning-affordance.v1.json",
        "phd-base-rate-fit.scan.reasoning-affordance.v1.json",
        "phd-fallback-parked.reasoning-affordance.v1.json",
        "phd-silva-constraint.active.reasoning-affordance.v1.json",
    }
    classes = set()
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_reasoning_affordance_payload(payload, path=path)
        classes.add(payload["affordance_class"])

    assert {
        "direct_pressure",
        "contrarian_edge",
        "negative_space",
        "duplicate_support",
        "false_friend",
        "parked_receipt",
    }.issubset(classes)
