from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_false_positive_visibility_probe import (  # noqa: E402
    validate_false_positive_probe_contract,
)
from pre_step6_shadow_triggered_false_positive_probe import (  # noqa: E402
    build_shadow_triggered_false_positive_probe_contract,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _seed_candidate(root: Path, case_id: str, categories: list[str]) -> None:
    _write_json(
        root
        / "research"
        / "pre-step6-rendered-hybrid-answer-cores"
        / f"{case_id}.native.rendered-hybrid-answer-core.v1.json",
        {
            "schema_version": "pre_step6_rendered_hybrid_answer_core.v1",
            "case_id": case_id,
            "answer_core": f"Anchor answer for {case_id}.",
        },
    )
    _write_json(
        root
        / "research"
        / "pre-step6-card-deck-replays"
        / f"{case_id}.card-deck-replay.v1.json",
        {
            "schema_version": "pre_step6_card_deck_replay.v1",
            "case_id": case_id,
            "step6_output": {"answer_core": f"Deck-aware answer for {case_id}."},
        },
    )
    _write_json(
        root / "research" / "pre-step6-problem-states" / f"{case_id}.problem-state.v1.json",
        {
            "schema_version": "problem_state.v1",
            "case_id": case_id,
            "user_goal": f"Resolve {case_id}.",
            "success_condition": "Choose the answer that preserves concrete payload.",
        },
    )


def test_shadow_triggered_contract_uses_deck_visible_marker_entity_candidates(
    tmp_path: Path,
) -> None:
    case_ids = ["candidate-one", "candidate-two", "candidate-three"]
    for case_id in case_ids:
        _seed_candidate(tmp_path, case_id, ["actor_sequence"])

    evidence_dir = tmp_path / "research" / "pre-step6-shadow-portfolio-evidence"
    _write_json(
        evidence_dir / "fixed-suite-cache-hit.shadow-evidence-result.v1.json",
        {
            "schema_version": "pre_step6_shadow_portfolio_evidence.v1",
            "arm": "fixed-suite-cache-hit",
            "case_records": [
                {
                    "case_id": case_id,
                    "decision": "deck_visible_shadow_only",
                    "candidate_flags": {"deck_visible_with_marker_entity_loss": True},
                    "marker_entity_loss_categories": ["actor_sequence"],
                }
                for case_id in case_ids
            ],
        },
    )

    contract = build_shadow_triggered_false_positive_probe_contract(
        root=tmp_path,
        evidence_path=evidence_dir / "fixed-suite-cache-hit.shadow-evidence-result.v1.json",
    )

    validate_false_positive_probe_contract(contract)

    assert [case["case_id"] for case in contract["probe_cases"]] == case_ids
    for case in contract["probe_cases"]:
        assert case["selection_timing"] == "pre_run"
        assert case["expected_step6_signal"] == "additive_pressure_present"
        assert "Shadow harness flagged" in case["false_positive_risk"][0]
        assert case["answer_candidates"]["anchor_visible"].startswith("Anchor answer")
        assert case["answer_candidates"]["deck_pressure"].startswith("Deck-aware answer")
