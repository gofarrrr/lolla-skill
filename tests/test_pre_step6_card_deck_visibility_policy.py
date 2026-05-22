from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_card_deck_visibility_policy import (  # noqa: E402
    build_visibility_policy,
    validate_visibility_policy_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_visibility_policy_marks_mother_anchor_standdown_without_quality_decision() -> None:
    payload = build_visibility_policy(
        case_id="mother-address-year",
        repo_root=REPO_ROOT,
    )

    validate_visibility_policy_payload(payload)

    assert payload["deterministic_read"]["anchor_standdown_eligible"] is True
    assert payload["deterministic_read"]["deterministic_quality_decision"] is False
    assert payload["deterministic_read"]["non_anchor_additive_count"] == 0
    assert payload["deterministic_read"]["non_anchor_private_or_confirming_count"] == 2
    assert payload["cognitive_confirmation"]["status"] == "anchor_confirmed_by_reviewer"
    assert payload["cognitive_confirmation"]["reviewer_winner"] == "clean_hybrid"
    assert payload["visible_policy"]["result"] == "anchor_visible_after_cognitive_confirmation"
    assert payload["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }


def test_visibility_policy_keeps_deck_visible_when_step6_finds_additive_pressure() -> None:
    payload = build_visibility_policy(
        case_id="founder-grant-marcus-equity.high-clutter",
        repo_root=REPO_ROOT,
    )

    validate_visibility_policy_payload(payload)

    assert payload["deterministic_read"]["anchor_standdown_eligible"] is False
    assert payload["deterministic_read"]["non_anchor_additive_count"] == 2
    assert payload["cognitive_confirmation"]["reviewer_winner"] == "card_deck_replay"
    assert payload["visible_policy"]["result"] == "card_deck_visible_after_cognitive_confirmation"
