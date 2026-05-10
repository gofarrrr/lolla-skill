from __future__ import annotations

from scripts.run_v60_composer_source_arm_replay import (
    build_source_arm_profile,
    source_arm_match,
)


def test_source_arm_match_separates_strict_lane_from_enhanced() -> None:
    assert source_arm_match(["lane_preserved"], "strict_lane") is True
    assert source_arm_match(["lane_preserved", "embedding_absence_exact"], "strict_lane") is False
    assert source_arm_match(["embedding_absence_exact"], "enhanced") is True
    assert source_arm_match(["lane_preserved", "embedding_affordance_exact"], "enhanced") is True
    assert source_arm_match(["lane_preserved"], "enhanced") is False


def test_build_source_arm_profile_filters_opportunities_and_hides_embedding_profile() -> None:
    profile = {
        "case_id": "case",
        "lane_profile": {"nominated_model_ids": ["a", "b"]},
        "embedding_profile": {"top_embedding_models": [{"model_id": "b"}]},
        "private_trace_summary": {
            "packet_usefulness": "useful",
            "selected_opportunity_count": 3,
        },
        "composer_opportunities": [
            {
                "opportunity_id": "lane",
                "source_mix": ["lane_preserved"],
            },
            {
                "opportunity_id": "embed",
                "source_mix": ["embedding_affordance_exact"],
            },
            {
                "opportunity_id": "mixed",
                "source_mix": ["lane_preserved", "embedding_absence_exact"],
            },
        ],
    }

    lane_profile = build_source_arm_profile(profile=profile, arm="strict_lane")
    enhanced_profile = build_source_arm_profile(profile=profile, arm="enhanced")

    assert [item["opportunity_id"] for item in lane_profile["composer_opportunities"]] == ["lane"]
    assert lane_profile["embedding_profile"] == {}
    assert lane_profile["packet_source_counts"] == {"lane_preserved": 1}
    assert [
        item["opportunity_id"] for item in enhanced_profile["composer_opportunities"]
    ] == ["embed", "mixed"]
    assert enhanced_profile["packet_source_counts"] == {
        "embedding_absence_exact": 1,
        "embedding_affordance_exact": 1,
        "lane_preserved": 1,
    }
