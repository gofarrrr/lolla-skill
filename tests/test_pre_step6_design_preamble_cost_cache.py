from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_design_preamble_cost_cache import (  # noqa: E402
    REQUIRED_KEY_MATERIAL_FIELDS,
    build_cost_cache_contract,
    load_cost_cache_contract_payload,
    validate_cost_cache_contract_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_runtime_cached_only_miss_stands_down_without_live_generation() -> None:
    payload = build_cost_cache_contract(
        case_id="founder-grant-marcus-equity.high-clutter",
        repo_root=REPO_ROOT,
        cache_mode="runtime_cached_only",
        cache_hit=False,
    )

    validate_cost_cache_contract_payload(payload)

    assert set(payload["key_material"]) == REQUIRED_KEY_MATERIAL_FIELDS
    assert payload["compiled_card_deck_key"].startswith("sha256:")
    assert payload["cache_read"]["cache_mode"] == "runtime_cached_only"
    assert payload["cache_read"]["cache_hit"] is False
    assert payload["cache_read"]["miss_behavior"] == "stand_down_to_current_step6"
    assert payload["cost_envelope"]["net_new_llm_calls"] == 0
    assert payload["cost_envelope"]["live_card_generation_allowed"] is False
    assert payload["runtime_effect"]["step6_card_deck_presented"] is False
    assert payload["runtime_effect"]["records_issue"] == "card_deck_cache_miss"
    assert payload["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }


def test_v60_selected_item_hashes_change_the_compiled_card_deck_key() -> None:
    without_v60 = build_cost_cache_contract(
        case_id="third-year-phd-student.v2",
        repo_root=REPO_ROOT,
        cache_mode="runtime_cached_only",
        cache_hit=True,
    )
    with_v60 = build_cost_cache_contract(
        case_id="third-year-phd-student.v2",
        repo_root=REPO_ROOT,
        cache_mode="runtime_cached_only",
        cache_hit=True,
        v60_selected_item_hashes=(
            "sha256:2222222222222222222222222222222222222222222222222222222222222222",
            "sha256:1111111111111111111111111111111111111111111111111111111111111111",
        ),
    )

    validate_cost_cache_contract_payload(without_v60)
    validate_cost_cache_contract_payload(with_v60)

    assert without_v60["compiled_card_deck_key"] != with_v60["compiled_card_deck_key"]
    assert with_v60["key_material"]["v60_selected_item_hashes"] == {
        "state": "provided",
        "hashes": [
            "sha256:1111111111111111111111111111111111111111111111111111111111111111",
            "sha256:2222222222222222222222222222222222222222222222222222222222222222",
        ],
    }


def test_research_miss_may_cold_fill_but_never_adds_normal_runtime_reviewer_calls() -> None:
    payload = build_cost_cache_contract(
        case_id="mother-address-year",
        repo_root=REPO_ROOT,
        cache_mode="research",
        cache_hit=False,
    )

    validate_cost_cache_contract_payload(payload)

    assert payload["cache_read"]["miss_behavior"] == "live_card_generation_allowed"
    assert payload["cost_envelope"]["net_new_llm_calls"] == 2
    assert payload["cost_envelope"]["live_card_generation_allowed"] is True
    assert payload["cost_envelope"]["normal_runtime_reviewer_calls"] == 0
    assert payload["runtime_effect"]["step6_card_deck_presented"] is True
    assert payload["runtime_effect"]["records_issue"] == "cold_fill_used"


def test_runtime_cached_only_fixed_suite_fixtures_validate() -> None:
    fixture_dir = REPO_ROOT / "research" / "pre-step6-design-preamble-cost-cache"
    paths = sorted(fixture_dir.glob("*.runtime_cached_only.miss.cost-cache.v1.json"))

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.high-clutter.runtime_cached_only.miss.cost-cache.v1.json",
        "mid-level-consultant-report-2.runtime_cached_only.miss.cost-cache.v1.json",
        "mother-address-year.runtime_cached_only.miss.cost-cache.v1.json",
        "third-year-phd-student.v2.runtime_cached_only.miss.cost-cache.v1.json",
    ]
    for path in paths:
        payload = load_cost_cache_contract_payload(path)
        validate_cost_cache_contract_payload(payload, path=path)
        assert payload["cache_read"]["miss_behavior"] == "stand_down_to_current_step6"
        assert payload["cost_envelope"]["net_new_llm_calls"] == 0
        assert payload["runtime_effect"]["records_issue"] == "card_deck_cache_miss"
