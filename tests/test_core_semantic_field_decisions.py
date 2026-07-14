from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = REPO_ROOT / "docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json"
DECISIONS = REPO_ROOT / "research/core-semantic-validation-2026-07-09/field-decisions.json"


def test_every_decision_work_contract_field_has_exactly_one_decision() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    decisions = json.loads(DECISIONS.read_text(encoding="utf-8"))["fields"]

    contract_fields = {
        (group, item["field_name"])
        for group, items in contract["field_groups"].items()
        for item in items
    }
    decided_fields = {
        (item["field_group"], item["field_name"])
        for item in decisions
    }

    assert len(contract_fields) == 46
    assert len(decisions) == 46
    assert len(decided_fields) == 46
    assert decided_fields == contract_fields


def test_field_decisions_have_operational_destinations_and_reasons() -> None:
    fields = json.loads(DECISIONS.read_text(encoding="utf-8"))["fields"]
    allowed = {"keep", "merge", "defer", "remove"}

    for field in fields:
        assert field["decision"] in allowed
        assert field["timing"]
        assert field["job"]
        assert field["target"]
        assert len(field["reason"]) >= 30


def test_pre_audit_field_decisions_do_not_promote_post_audit_outcomes() -> None:
    fields = json.loads(DECISIONS.read_text(encoding="utf-8"))["fields"]
    by_name = {item["field_name"]: item for item in fields}

    for field_name in (
        "revised_direction_or_action_consequence",
        "what_lolla_pressed_on",
        "what_changed",
        "useful_friction",
        "noisy_friction",
        "lost_value",
        "overcorrection_risk",
        "false_precision_risk",
        "generic_caution_risk",
    ):
        assert by_name[field_name]["decision"] == "defer"
        assert by_name[field_name]["timing"] == "post"
