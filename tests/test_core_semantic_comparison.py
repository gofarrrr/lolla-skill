from __future__ import annotations

import json
import hashlib
from pathlib import Path

from engine.system_b.core_semantic_comparison import build_core_semantic_comparison


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests/fixtures/core_semantic_validation/case_01_enterprise_logo_beta"


def _write_compact(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "extraction": {
                    "decision_situation": "Whether to launch publicly.",
                    "live_constraints": [{"constraint": "No signed contract", "introduced_turn": 3}],
                    "dropped_threads": [],
                    "reasoning_passages": [
                        "I would announce a limited public beta and make this prospect the flagship design partner."
                    ]
                }
            }
        ),
        encoding="utf-8"
    )


def _write_shadow(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "semantic_events": {
                    "question_events": [
                        {"kind": "initial", "source": {"turn_index": 1, "speaker": "user", "quote": "Should we launch publicly and use its logo to attract other customers?"}},
                        {"kind": "current", "source": {"turn_index": 5, "speaker": "user", "quote": "What evidence should we require before announcing?"}}
                    ],
                    "assistant_stance_events": [
                        {"stance": "commitment", "turn_index": 2, "speaker": "assistant", "text": "I would announce a limited public beta and make this prospect the flagship design partner.", "provenance": {"span_ref": {"turn_index": 2, "speaker": "assistant"}}}
                    ]
                }
            }
        ),
        encoding="utf-8"
    )


def test_comparison_distinguishes_span_recall_from_paraphrase(tmp_path: Path) -> None:
    compact_paths = [tmp_path / f"compact_{i}.json" for i in range(3)]
    shadow_paths = [tmp_path / f"shadow_{i}.json" for i in range(3)]
    for path in compact_paths:
        _write_compact(path)
    for path in shadow_paths:
        _write_shadow(path)

    result = build_core_semantic_comparison(
        compact_paths=compact_paths,
        shadow_paths=shadow_paths,
        conversation_path=FIXTURE_DIR / "conversation.txt",
        gold_path=FIXTURE_DIR / "gold.json",
    )

    assert result["compact_path"]["run_count"] == 3
    assert result["shadow_path"]["run_count"] == 3
    assert result["shadow_path"]["gold_span_recall"]["mean_recall"] > result["compact_path"]["gold_span_recall"]["mean_recall"]
    assert result["shadow_path"]["repeatability"]["mean_span_jaccard"] == 1.0


def test_derivation_label_is_not_scored_as_a_literal_source_span(tmp_path: Path) -> None:
    compact_paths = [tmp_path / f"compact_{i}.json" for i in range(3)]
    shadow_paths = [tmp_path / f"shadow_{i}.json" for i in range(3)]
    for path in compact_paths:
        _write_compact(path)
    for path in shadow_paths:
        path.write_text(
            json.dumps(
                {
                    "semantic_events": {
                        "live_constraint_events": [
                            {
                                "kind": "constraint",
                                "text": "No signed commitment",
                                "introduced_at_turn": 3,
                                "provenance": {
                                    "kind": "derivation",
                                    "turn_refs": [
                                        {"turn_index": 1, "speaker": "user"},
                                        {"turn_index": 3, "speaker": "user"},
                                    ],
                                },
                            }
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )

    conversation = FIXTURE_DIR / "conversation.txt"
    gold = tmp_path / "gold.json"
    gold.write_text(
        json.dumps(
            {
                "case_id": "derivation-grounding-control",
                "source_file_sha256": hashlib.sha256(conversation.read_bytes()).hexdigest(),
                "required_observations": [
                    {
                        "observation_id": "constraint.synthetic_derivation_label",
                        "dimension": "constraints_and_options",
                        "evidence": [
                            {
                                "turn_index": 1,
                                "speaker": "user",
                                "quote": "No signed commitment",
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = build_core_semantic_comparison(
        compact_paths=compact_paths,
        shadow_paths=shadow_paths,
        conversation_path=conversation,
        gold_path=gold,
    )

    assert result["shadow_path"]["gold_span_recall"]["mean_recall"] == 0.0
    assert result["shadow_path"]["provenance_status"][
        "legacy_incomplete_count"
    ] == 6


def test_exact_derivation_components_receive_span_credit(tmp_path: Path) -> None:
    compact_paths = [tmp_path / f"compact_{i}.json" for i in range(3)]
    shadow_paths = [tmp_path / f"shadow_{i}.json" for i in range(3)]
    for path in compact_paths:
        _write_compact(path)

    conversation = FIXTURE_DIR / "conversation.txt"
    conversation_text = conversation.read_text(encoding="utf-8")
    turn_three = (
        "They have not signed anything. We only have two friendly emails from "
        "their innovation lead, our only senior engineer is already supporting "
        "existing customers, and the board is excited mainly because of the "
        "company's name."
    )
    turn_five = (
        "What evidence should we require before announcing? I am worried we are "
        "treating their interest as a purchase commitment, but I am also worried "
        "that waiting will make us lose the opportunity."
    )
    first_quote = "our only senior engineer is already supporting existing customers"
    second_quote = "I am worried we are treating their interest as a purchase commitment"
    for path in shadow_paths:
        path.write_text(
            json.dumps(
                {
                    "semantic_events": {
                        "live_constraint_events": [
                            {
                                "issue_id": "derivation_001",
                                "kind": "constraint",
                                "text": "Capacity and commitment remain constrained",
                                "introduced_at_turn": 3,
                                "provenance": {
                                    "kind": "derivation",
                                    "derivation_id": "derivation_001",
                                    "turn_refs": [
                                        {"turn_index": 3, "speaker": "user"},
                                        {"turn_index": 5, "speaker": "user"},
                                    ],
                                    "source_object_ids": [],
                                    "provenance_status": "component_evidence_complete",
                                    "components": [
                                        {
                                            "component_id": "component_001",
                                            "quote": first_quote,
                                            "span_ref": {
                                                "turn_index": 3,
                                                "speaker": "user",
                                                "start_char": turn_three.index(first_quote),
                                                "end_char": turn_three.index(first_quote)
                                                + len(first_quote),
                                            },
                                        },
                                        {
                                            "component_id": "component_002",
                                            "quote": second_quote,
                                            "span_ref": {
                                                "turn_index": 5,
                                                "speaker": "user",
                                                "start_char": turn_five.index(second_quote),
                                                "end_char": turn_five.index(second_quote)
                                                + len(second_quote),
                                            },
                                        },
                                    ],
                                },
                            }
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )

    gold = tmp_path / "gold.json"
    gold.write_text(
        json.dumps(
            {
                "case_id": "derivation-component-control",
                "source_file_sha256": hashlib.sha256(
                    conversation_text.encode("utf-8")
                ).hexdigest(),
                "required_observations": [
                    {
                        "observation_id": "constraint.engineering_capacity",
                        "dimension": "constraints_and_options",
                        "evidence": [
                            {
                                "turn_index": 3,
                                "speaker": "user",
                                "quote": first_quote,
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = build_core_semantic_comparison(
        compact_paths=compact_paths,
        shadow_paths=shadow_paths,
        conversation_path=conversation,
        gold_path=gold,
    )

    assert result["shadow_path"]["gold_span_recall"]["mean_recall"] == 1.0
    assert result["shadow_path"]["provenance_status"][
        "legacy_incomplete_count"
    ] == 0
    assert result["shadow_path"]["provenance_status"][
        "invalid_component_count"
    ] == 0
