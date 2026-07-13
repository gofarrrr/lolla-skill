import json
from pathlib import Path

from scripts.evals.build_simulated_reliability_review_packets_v1 import build_packet


ROOT = Path(__file__).resolve().parents[1]


def test_blind_packet_is_replayable_and_hides_arm_identity_and_source_target():
    result = json.loads(
        (
            ROOT
            / "research/simulated-reliability-v1-transfer-2026-07-12/t1/v1-case01-flood-infrastructure-primary/result.json"
        ).read_text()
    )
    conversation = (
        ROOT
        / "research/simulated-reliability-corpus-v1-2026-07-12/naturalized-transfer-sources/v1-case01-flood-infrastructure.txt"
    ).read_text()
    contract = json.loads(
        (ROOT / "docs/evals/simulated-reliability-v1-review-contract-v1.json").read_text()
    )
    first = build_packet(
        run_id="test", case_id=result["case_id"], conversation=conversation, result=result, contract=contract
    )
    second = build_packet(
        run_id="test", case_id=result["case_id"], conversation=conversation, result=result, contract=contract
    )
    assert first == second
    packet, mapping = first
    assert set(mapping["blind_label_to_arm_id"].values()) == {
        "transcript_only",
        "direct_pressure",
        "graph_expanded_pressure",
    }
    serialized = json.dumps(packet)
    assert "pressure_expected" not in serialized
    assert "stand_down_expected" not in serialized
    assert "blind_label_to_arm_id" not in serialized
    assert packet["boundaries"]["scalar_score_requested"] is False


def test_review_contract_forbids_scalar_winner_and_keeps_harm_separate():
    contract = json.loads(
        (ROOT / "docs/evals/simulated-reliability-v1-review-contract-v1.json").read_text()
    )
    assert contract["scalar_quality_score_forbidden"] is True
    assert contract["winner_label_forbidden"] is True
    comparative = contract["scorecard"]["comparative"]
    assert "graph_only_contribution" in comparative
    assert "graph_only_burden_or_harm" in comparative
