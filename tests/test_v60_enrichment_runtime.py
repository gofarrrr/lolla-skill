from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.conversation_context import (
    ConversationContext,
    ExtractionPayload,
    Turn,
)
from engine.system_b.v60_enrichment import (
    LEDGER_SCHEMA_VERSION,
    build_v60_enrichment,
    extract_v60_candidates,
    validate_v60_consideration_ledger,
)


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _context() -> ConversationContext:
    return ConversationContext(
        turns=(
            Turn(1, "user", "Should we accept the offer or keep negotiating?"),
            Turn(1, "assistant", "Accept it with safeguards and a fallback."),
        ),
        extraction=ExtractionPayload(
            decision_situation="Should we accept the offer?",
            live_constraints=(),
            synthesized_position="Accept it with safeguards.",
            reasoning_passages=("Accept it with safeguards.",),
            original_framing="Is the offer too risky?",
            dropped_threads=(),
        ),
    )


def _artifact() -> dict:
    return {
        "artifact": "model_affordances_v60",
        "status": "draft_review_only",
        "affordances": [
            {
                "model_id": "opportunity-cost",
                "affordance_id": "opportunity-cost.displaced-alternative-commitment-gate",
                "status": "supported",
                "confidence": "high",
                "mechanism": "Ask what the commitment displaces.",
                "activation_shape": {
                    "use_when": ["A choice commits scarce resources."],
                    "case_evidence_needed": ["The forgone option."],
                    "do_not_use_when": ["Nothing material is displaced."],
                },
                "treatment_requirements": [
                    {
                        "requirement_id": "name-displaced-alternative",
                        "description": "Name the displaced alternative.",
                        "evidence_required": ["Current option set."],
                        "good_output_shape": ["A trade-off statement."],
                    }
                ],
                "diagnostic_questions": ["What option disappears if we say yes?"],
                "misuse_guards": ["Do not invent fake alternatives."],
                "source_evidence": [{"source_file": "Opportunity_Cost.md", "source_quote": "Every choice has a cost."}],
            },
            {
                "model_id": "premortem",
                "affordance_id": "premortem.simulated-failure-to-plan-change",
                "status": "supported",
                "confidence": "high",
                "mechanism": "Imagine failure before commitment.",
                "activation_shape": {
                    "use_when": ["A plan sounds settled."],
                    "case_evidence_needed": ["The failure mode."],
                    "do_not_use_when": [],
                },
                "treatment_requirements": [],
                "diagnostic_questions": ["What would make this fail?"],
                "misuse_guards": [],
                "source_evidence": [{"source_file": "Premortem.md", "source_quote": "Imagine the plan failed."}],
            },
        ],
        "absence_records": [
            {
                "model_id": "opportunity-cost",
                "attempted_field": "generic-pro-con-list",
                "status": "not_supported_by_source",
                "runtime_policy": "do_not_promote",
                "reason": "The source supports displaced alternatives, not generic lists.",
                "source_evidence": [{"source_file": "Opportunity_Cost.md", "source_quote": "Cost is the next best alternative."}],
            }
        ],
        "model_records": [
            {
                "model_id": "opportunity-cost",
                "source_file": "Opportunity_Cost.md",
                "status": "supported",
                "affordances": [
                    {
                        "model_id": "opportunity-cost",
                        "affordance_id": "opportunity-cost.displaced-alternative-commitment-gate",
                        "status": "supported",
                        "confidence": "high",
                        "mechanism": "Ask what the commitment displaces.",
                        "activation_shape": {
                            "use_when": ["A choice commits scarce resources."],
                            "case_evidence_needed": ["The forgone option."],
                            "do_not_use_when": ["Nothing material is displaced."],
                        },
                        "treatment_requirements": [
                            {
                                "requirement_id": "name-displaced-alternative",
                                "description": "Name the displaced alternative.",
                                "evidence_required": ["Current option set."],
                                "good_output_shape": ["A trade-off statement."],
                            }
                        ],
                        "diagnostic_questions": ["What option disappears if we say yes?"],
                        "misuse_guards": ["Do not invent fake alternatives."],
                        "source_evidence": [{"source_file": "Opportunity_Cost.md", "source_quote": "Every choice has a cost."}],
                    }
                ],
                "absence_records": [
                    {
                        "attempted_field": "generic-pro-con-list",
                        "status": "not_supported_by_source",
                        "runtime_policy": "do_not_promote",
                        "reason": "The source supports displaced alternatives, not generic lists.",
                        "source_evidence": [{"source_file": "Opportunity_Cost.md", "source_quote": "Cost is the next best alternative."}],
                    }
                ],
            },
            {
                "model_id": "premortem",
                "source_file": "Premortem.md",
                "status": "supported",
                "affordances": [
                    {
                        "model_id": "premortem",
                        "affordance_id": "premortem.simulated-failure-to-plan-change",
                        "status": "supported",
                        "confidence": "high",
                        "mechanism": "Imagine failure before commitment.",
                        "activation_shape": {
                            "use_when": ["A plan sounds settled."],
                            "case_evidence_needed": ["The failure mode."],
                            "do_not_use_when": [],
                        },
                        "treatment_requirements": [],
                        "diagnostic_questions": ["What would make this fail?"],
                        "misuse_guards": [],
                        "source_evidence": [{"source_file": "Premortem.md", "source_quote": "Imagine the plan failed."}],
                    }
                ],
                "absence_records": [],
            },
        ],
    }


class _FakeRetriever:
    def rank_models_expanded(self, query_text: str, api_key: str, top_k: int = 24):  # noqa: ANN001
        assert "Retrieval goal" in query_text
        assert api_key == "test-key"
        return [
            {"model_id": "premortem", "score": 0.91, "signal_type": "select_when"},
            {"model_id": "opportunity-cost", "score": 0.82, "signal_type": "danger_when"},
        ][:top_k]


def test_v60_enrichment_builds_private_cards_and_skip_telemetry(tmp_path: Path) -> None:
    artifact_path = tmp_path / "affordances_v60.json"
    _write_json(artifact_path, _artifact())
    result = {
        "delta_card": {
            "selected_model_ids": ["opportunity-cost"],
            "findings": [
                {
                    "tendency_id": "doubt-avoidance",
                    "selected_model_ids": ["opportunity-cost"],
                    "specific_passage": "Accept it with safeguards.",
                }
            ],
        }
    }

    enrichment = build_v60_enrichment(
        root=tmp_path,
        result_payload=result,
        conversation_context=_context(),
        affordances_path=artifact_path,
        embedding_retriever=_FakeRetriever(),
        embedding_api_key="test-key",
        enable_embeddings=True,
        max_cards=1,
    )

    assert enrichment["status"] == "active"
    assert enrichment["runtime_policy"] == "private_skill_enrichment"
    assert enrichment["candidate_pool"]["embedding_mode"] == "on"
    assert enrichment["selected_cards"][0]["model_id"] == "opportunity-cost"
    assert enrichment["selected_cards"][0]["selected_affordance_cards"][0]["chunk_id"] == (
        "aff::opportunity-cost.displaced-alternative-commitment-gate"
    )
    assert enrichment["selected_cards"][0]["selected_absence_records"][0]["chunk_id"] == (
        "abs::opportunity-cost::generic-pro-con-list"
    )
    assert enrichment["telemetry"]["selected_chunk_count"] == 2
    assert "premortem" in enrichment["telemetry"]["not_presented_model_ids"]


def test_extract_v60_candidates_reads_all_four_lane_surfaces() -> None:
    candidates = extract_v60_candidates(
        {
            "delta_card": {"selected_model_ids": ["opportunity-cost"]},
            "companion_cheat_sheet": {
                "anchors": [{"model_id": "optionality", "presence_explanation": "Option set is narrow."}]
            },
            "frame_pressure_card": {
                "reframings": [{"grounding_model": "inversion", "what_opens": "Failure view."}]
            },
            "structural_coverage_card": {
                "gap_routes": [{"candidate_model_ids": ["base-rates"], "dimension_name": "Evidence"}]
            },
        }
    )

    assert [candidate.model_id for candidate in candidates] == [
        "opportunity-cost",
        "optionality",
        "inversion",
        "base-rates",
    ]


def test_missing_v60_records_do_not_consume_hot_context_slots(tmp_path: Path) -> None:
    artifact_path = tmp_path / "affordances_v60.json"
    _write_json(artifact_path, _artifact())

    enrichment = build_v60_enrichment(
        root=tmp_path,
        result_payload={"delta_card": {"selected_model_ids": ["not-in-v60"]}},
        conversation_context=_context(),
        affordances_path=artifact_path,
        embedding_retriever=_FakeRetriever(),
        embedding_api_key="test-key",
        enable_embeddings=True,
        max_cards=1,
    )

    assert enrichment["selected_cards"][0]["model_id"] == "premortem"
    assert {
        (item["model_id"], item["reason"], item["stage"])
        for item in enrichment["telemetry"]["skipped_candidates"]
    } >= {("not-in-v60", "missing_v60_record", "selection")}


def test_v60_consideration_ledger_validation_accounts_for_unused_chunks(tmp_path: Path) -> None:
    artifact_path = tmp_path / "affordances_v60.json"
    _write_json(artifact_path, _artifact())
    enrichment = build_v60_enrichment(
        root=tmp_path,
        result_payload={"delta_card": {"selected_model_ids": ["opportunity-cost"]}},
        conversation_context=_context(),
        affordances_path=artifact_path,
        enable_embeddings=False,
    )

    chunk_ids = enrichment["telemetry"]["selected_chunk_ids"]
    ledger = {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "transactions": [
            {
                "chunk_id": chunk_ids[0],
                "card_id": "v60-card-001-opportunity-cost",
                "model_id": "opportunity-cost",
                "disposition": "used",
                "route": "updated_position",
                "strongest_plausible_application": "Use the affordance to name the displaced alternative.",
                "risk_if_forced": "",
                "why": "It changed the trade-off threshold.",
                "visible_effect": "Named the displaced alternative.",
            },
            {
                "chunk_id": chunk_ids[1],
                "card_id": "v60-card-001-opportunity-cost",
                "model_id": "opportunity-cost",
                "disposition": "rejected",
                "route": "irrelevant",
                "strongest_plausible_application": "Use the absence as a warning against generic pro/con framing.",
                "risk_if_forced": "It would pretend the answer relied on a generic pro/con list.",
                "why": "The answer did not rely on a generic pro/con list.",
                "visible_effect": "",
            },
        ],
    }

    validation = validate_v60_consideration_ledger(ledger, enrichment=enrichment)

    assert validation["status"] == "valid"
    assert validation["used_chunk_ids"] == [chunk_ids[0]]
    assert validation["presented_but_not_used_chunk_ids"] == [chunk_ids[1]]


def test_v60_ledger_validation_rejects_cheap_non_used_transactions(tmp_path: Path) -> None:
    artifact_path = tmp_path / "affordances_v60.json"
    _write_json(artifact_path, _artifact())
    enrichment = build_v60_enrichment(
        root=tmp_path,
        result_payload={"delta_card": {"selected_model_ids": ["opportunity-cost"]}},
        conversation_context=_context(),
        affordances_path=artifact_path,
        enable_embeddings=False,
    )

    chunk_id = enrichment["telemetry"]["selected_chunk_ids"][1]
    ledger = {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "transactions": [
            {
                "chunk_id": chunk_id,
                "card_id": "v60-card-001-opportunity-cost",
                "model_id": "opportunity-cost",
                "disposition": "rejected",
                "route": "irrelevant",
                "why": "Not relevant.",
                "visible_effect": "",
            }
        ],
    }

    validation = validate_v60_consideration_ledger(ledger, enrichment=enrichment)

    assert validation["status"] == "invalid"
    assert any("strongest_plausible_application" in err for err in validation["errors"])
    assert any("risk_if_forced" in err for err in validation["errors"])
