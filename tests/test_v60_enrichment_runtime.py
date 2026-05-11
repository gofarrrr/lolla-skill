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
    _selection_tokens,
    build_v60_consideration_ledger_skeleton,
    build_v60_enrichment,
    extract_v60_candidates,
    finalize_v60_consideration,
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
            {
                "model_id": "optionality",
                "affordance_id": "optionality.expand-before-evaluating",
                "status": "supported",
                "confidence": "high",
                "mechanism": "Expand the option set before evaluating a binary decision.",
                "activation_shape": {
                    "use_when": ["The case is framed as a binary choice."],
                    "case_evidence_needed": ["The excluded third path."],
                    "do_not_use_when": ["The option set is already exhaustive."],
                },
                "treatment_requirements": [],
                "diagnostic_questions": ["What option is missing from the binary?"],
                "misuse_guards": [],
                "source_evidence": [{"source_file": "Optionality.md", "source_quote": "Expand before evaluating."}],
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
            {
                "model_id": "optionality",
                "source_file": "Optionality.md",
                "status": "supported",
                "affordances": [
                    {
                        "model_id": "optionality",
                        "affordance_id": "optionality.expand-before-evaluating",
                        "status": "supported",
                        "confidence": "high",
                        "mechanism": "Expand the option set before evaluating a binary decision.",
                        "activation_shape": {
                            "use_when": ["The case is framed as a binary choice."],
                            "case_evidence_needed": ["The excluded third path."],
                            "do_not_use_when": ["The option set is already exhaustive."],
                        },
                        "treatment_requirements": [],
                        "diagnostic_questions": ["What option is missing from the binary?"],
                        "misuse_guards": [],
                        "source_evidence": [{"source_file": "Optionality.md", "source_quote": "Expand before evaluating."}],
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


def test_v60_affordance_selection_prefers_case_relevant_sibling(tmp_path: Path) -> None:
    artifact = _artifact()
    record = artifact["model_records"][0]
    relevant = record["affordances"][0]
    irrelevant = {
        **relevant,
        "affordance_id": "opportunity-cost.accounting-budget-label",
        "mechanism": "Label accounting budget categories after the decision is made.",
        "activation_shape": {
            "use_when": ["The work is a bookkeeping cleanup."],
            "case_evidence_needed": ["Existing accounting categories."],
            "do_not_use_when": ["The choice displaces a real alternative."],
        },
        "diagnostic_questions": ["Which budget category should this cost sit in?"],
        "source_evidence": [
            {"source_file": "Opportunity_Cost.md", "source_quote": "Accounting labels are not the decision."}
        ],
    }
    record["affordances"] = [irrelevant, relevant]
    artifact["affordances"] = [irrelevant, relevant]
    artifact_path = tmp_path / "affordances_v60.json"
    _write_json(artifact_path, artifact)

    enrichment = build_v60_enrichment(
        root=tmp_path,
        result_payload={
            "delta_card": {
                "findings": [
                    {
                        "selected_model_ids": ["opportunity-cost"],
                        "challenge_statement": "The answer never names the displaced alternative.",
                        "next_move": "Ask what option disappears if we accept the offer.",
                    }
                ]
            }
        },
        conversation_context=_context(),
        affordances_path=artifact_path,
        enable_embeddings=False,
        max_cards=1,
    )

    selected = enrichment["selected_cards"][0]["selected_affordance_cards"][0]
    assert selected["affordance_id"] == "opportunity-cost.displaced-alternative-commitment-gate"
    assert selected["selection_method"] == "local_relevance"
    assert selected["selection_effect_type"] == "missing_option"
    assert selected["sibling_alternatives_considered"] == 1
    assert enrichment["telemetry"]["selected_chunk_effect_types"]["missing_option"] == 1


def test_v60_absence_selection_prefers_specific_overclaim_blocker(tmp_path: Path) -> None:
    artifact = _artifact()
    record = artifact["model_records"][0]
    generic = record["absence_records"][0]
    specific = {
        "attempted_field": "fallback-without-evidence",
        "status": "not_supported_by_source",
        "runtime_policy": "do_not_promote",
        "reason": "Block treating a named fallback as a real option when the conversation has no evidence that the fallback is available.",
        "source_evidence": [
            {"source_file": "Opportunity_Cost.md", "source_quote": "Alternatives must be real displaced options."}
        ],
    }
    record["absence_records"] = [generic, specific]
    artifact["absence_records"] = [generic, specific]
    artifact_path = tmp_path / "affordances_v60.json"
    _write_json(artifact_path, artifact)

    enrichment = build_v60_enrichment(
        root=tmp_path,
        result_payload={
            "delta_card": {
                "findings": [
                    {
                        "selected_model_ids": ["opportunity-cost"],
                        "challenge_statement": "The answer leans on a fallback without evidence.",
                        "next_move": "Do not overclaim a fallback unless the option is actually available.",
                    }
                ]
            }
        },
        conversation_context=_context(),
        affordances_path=artifact_path,
        enable_embeddings=False,
        max_cards=1,
    )

    selected = enrichment["selected_cards"][0]["selected_absence_records"][0]
    assert selected["attempted_field"] == "fallback-without-evidence"
    assert selected["selection_method"] == "local_relevance"
    assert selected["selection_effect_type"] == "overclaim_blocker"
    assert selected["absence_blocker_reason"]


def test_v60_selection_tokens_drop_explanatory_stopwords() -> None:
    tokens = _selection_tokens(
        "After all, before being useful, the founder should test reversibility "
        "and integration risk."
    )

    assert {"after", "all", "before", "being", "should"} - tokens == {
        "after",
        "all",
        "before",
        "being",
        "should",
    }
    assert {"founder", "test", "reversibility", "integration", "risk"}.issubset(tokens)


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


def test_v60_selection_reserves_frame_opportunity_before_packet_cap(tmp_path: Path) -> None:
    artifact_path = tmp_path / "affordances_v60.json"
    _write_json(artifact_path, _artifact())

    enrichment = build_v60_enrichment(
        root=tmp_path,
        result_payload={
            "delta_card": {"selected_model_ids": ["opportunity-cost"]},
            "frame_pressure_card": {
                "routes": [
                    {
                        "frame_pattern": "binary_collapse",
                        "candidate_model_ids": ["premortem", "optionality"],
                    }
                ]
            },
        },
        conversation_context=_context(),
        affordances_path=artifact_path,
        enable_embeddings=False,
        max_cards=2,
        lane_slots=1,
        frame_opportunity_slots=1,
        embedding_affordance_slots=0,
        embedding_absence_slots=0,
        hybrid_slots=0,
    )

    assert enrichment["telemetry"]["selected_model_ids"] == [
        "opportunity-cost",
        "optionality",
    ]
    assert enrichment["selected_cards"][1]["selection_source"] == "frame_opportunity_reserved"
    assert "aff::optionality.expand-before-evaluating" in enrichment["telemetry"]["selected_chunk_ids"]


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
                "chunk_kind": "affordance",
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
                "chunk_kind": "absence",
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


def test_v60_enrichment_includes_deterministic_ledger_skeleton(tmp_path: Path) -> None:
    artifact_path = tmp_path / "affordances_v60.json"
    _write_json(artifact_path, _artifact())
    enrichment = build_v60_enrichment(
        root=tmp_path,
        result_payload={"delta_card": {"selected_model_ids": ["opportunity-cost"]}},
        conversation_context=_context(),
        affordances_path=artifact_path,
        enable_embeddings=False,
    )

    skeleton = enrichment["consideration_ledger_skeleton"]

    assert skeleton == build_v60_consideration_ledger_skeleton(enrichment)
    assert skeleton["schema_version"] == LEDGER_SCHEMA_VERSION
    assert [row["chunk_id"] for row in skeleton["transactions"]] == (
        enrichment["telemetry"]["selected_chunk_ids"]
    )
    assert {row["chunk_kind"] for row in skeleton["transactions"]} == {
        "affordance",
        "absence",
    }
    assert all(row["card_id"] == "v60-card-001-opportunity-cost" for row in skeleton["transactions"])
    assert all(row["model_id"] == "opportunity-cost" for row in skeleton["transactions"])
    assert "visible_effect" in skeleton["transactions"][0]
    absence_row = next(row for row in skeleton["transactions"] if row["chunk_kind"] == "absence")
    assert "blocked_or_guarded_claim" in absence_row
    assert "uncertainty_boundary" in absence_row


def test_v60_ledger_validation_rejects_identity_mismatches(tmp_path: Path) -> None:
    artifact_path = tmp_path / "affordances_v60.json"
    _write_json(artifact_path, _artifact())
    enrichment = build_v60_enrichment(
        root=tmp_path,
        result_payload={"delta_card": {"selected_model_ids": ["opportunity-cost"]}},
        conversation_context=_context(),
        affordances_path=artifact_path,
        enable_embeddings=False,
    )
    chunk_id = enrichment["telemetry"]["selected_chunk_ids"][0]
    ledger = {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "transactions": [
            {
                "chunk_id": chunk_id,
                "card_id": "v60-card-999-wrong",
                "model_id": "wrong-model",
                "chunk_kind": "absence",
                "disposition": "used",
                "route": "updated_position",
                "strongest_plausible_application": "Use it.",
                "why": "It applies.",
                "visible_effect": "Changed the answer.",
            },
            {
                "chunk_id": enrichment["telemetry"]["selected_chunk_ids"][1],
                "card_id": "v60-card-001-opportunity-cost",
                "model_id": "opportunity-cost",
                "chunk_kind": "absence",
                "disposition": "rejected",
                "route": "irrelevant",
                "strongest_plausible_application": "Block generic pro/con usage.",
                "risk_if_forced": "Would force a generic list.",
                "why": "Not present.",
            },
        ],
    }

    validation = validate_v60_consideration_ledger(ledger, enrichment=enrichment)

    assert validation["status"] == "invalid"
    assert any("card_id does not match selected chunk" in err for err in validation["errors"])
    assert any("model_id does not match selected chunk" in err for err in validation["errors"])
    assert any("chunk_kind does not match selected chunk" in err for err in validation["errors"])


def test_v60_ledger_validation_rejects_route_disposition_contradictions(tmp_path: Path) -> None:
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
                "chunk_kind": "affordance",
                "disposition": "used",
                "route": "irrelevant",
                "strongest_plausible_application": "Use it.",
                "why": "It applies.",
                "visible_effect": "Changed the answer.",
            },
            {
                "chunk_id": chunk_ids[1],
                "card_id": "v60-card-001-opportunity-cost",
                "model_id": "opportunity-cost",
                "chunk_kind": "absence",
                "disposition": "rejected",
                "route": "updated_position",
                "strongest_plausible_application": "Use it.",
                "risk_if_forced": "Would force a wrong update.",
                "why": "It should not update the answer.",
            },
        ],
    }

    validation = validate_v60_consideration_ledger(ledger, enrichment=enrichment)

    assert validation["status"] == "invalid"
    assert any("route is incompatible with disposition" in err for err in validation["errors"])


def test_v60_ledger_validation_rejects_used_affordance_without_effect_or_guardrail(tmp_path: Path) -> None:
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
                "chunk_kind": "affordance",
                "disposition": "used",
                "route": "updated_position",
                "strongest_plausible_application": "Use it.",
                "why": "It applies.",
                "visible_effect": "",
                "private_guardrail": "",
            },
            {
                "chunk_id": chunk_ids[1],
                "card_id": "v60-card-001-opportunity-cost",
                "model_id": "opportunity-cost",
                "chunk_kind": "absence",
                "disposition": "rejected",
                "route": "irrelevant",
                "strongest_plausible_application": "Block generic pro/con usage.",
                "risk_if_forced": "Would force a generic list.",
                "why": "Not present.",
            },
        ],
    }

    validation = validate_v60_consideration_ledger(ledger, enrichment=enrichment)

    assert validation["status"] == "invalid"
    assert any("visible_effect or private_guardrail" in err for err in validation["errors"])


def test_v60_ledger_validation_rejects_used_absence_without_blocker_or_boundary(tmp_path: Path) -> None:
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
                "chunk_kind": "affordance",
                "disposition": "rejected",
                "route": "irrelevant",
                "strongest_plausible_application": "Name the displaced alternative.",
                "risk_if_forced": "Would force an irrelevant trade-off.",
                "why": "Not needed.",
            },
            {
                "chunk_id": chunk_ids[1],
                "card_id": "v60-card-001-opportunity-cost",
                "model_id": "opportunity-cost",
                "chunk_kind": "absence",
                "disposition": "used",
                "route": "private_guardrail",
                "strongest_plausible_application": "Block generic pro/con usage.",
                "why": "It kept the answer from overclaiming.",
                "private_guardrail": "Avoided generic pro/con framing.",
                "blocked_or_guarded_claim": "",
                "uncertainty_boundary": "",
            },
        ],
    }

    validation = validate_v60_consideration_ledger(ledger, enrichment=enrichment)

    assert validation["status"] == "invalid"
    assert any("blocked_or_guarded_claim or uncertainty_boundary" in err for err in validation["errors"])


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
                "chunk_kind": "absence",
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


def test_finalize_v60_consideration_marks_missing_ledger_degraded(tmp_path: Path) -> None:
    artifact_path = tmp_path / "affordances_v60.json"
    _write_json(artifact_path, _artifact())
    enrichment = build_v60_enrichment(
        root=tmp_path,
        result_payload={"delta_card": {"selected_model_ids": ["opportunity-cost"]}},
        conversation_context=_context(),
        affordances_path=artifact_path,
        enable_embeddings=False,
    )

    result = finalize_v60_consideration(
        {
            "run_health": {"overall": "healthy", "issues": []},
            "v60_enrichment": enrichment,
        }
    )

    assert result["run_health"]["overall"] == "degraded"
    assert result["run_health"]["v60_consideration_ledger"] == "missing"
    assert result["run_health"]["v60_unaccounted_chunk_count"] == 2
    assert "v60_consideration_ledger_missing" in result["run_health"]["issues"]
    missing_detail = next(
        detail
        for detail in result["run_health"]["issue_details"]
        if detail["code"] == "v60_consideration_ledger_missing"
    )
    assert missing_detail["severity"] == "degraded"
    assert missing_detail["axis"] == "v60"
    assert result["v60_consideration_validation"]["status"] == "missing"


def test_finalize_v60_consideration_marks_invalid_ledger_degraded_with_issue_detail(
    tmp_path: Path,
) -> None:
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
                "chunk_kind": "affordance",
                "disposition": "used",
                "route": "irrelevant",
                "strongest_plausible_application": "Use it to name the displaced alternative.",
                "risk_if_forced": "",
                "why": "It changed the threshold.",
                "visible_effect": "Named the displaced alternative.",
            },
            {
                "chunk_id": chunk_ids[1],
                "card_id": "v60-card-001-opportunity-cost",
                "model_id": "opportunity-cost",
                "chunk_kind": "absence",
                "disposition": "rejected",
                "route": "irrelevant",
                "strongest_plausible_application": "Block generic pro/con usage.",
                "risk_if_forced": "Would claim the answer used generic pro/con reasoning.",
                "why": "That was not present.",
            },
        ],
    }

    result = finalize_v60_consideration(
        {
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
            "v60_enrichment": enrichment,
        },
        ledger=ledger,
    )

    assert result["run_health"]["overall"] == "degraded"
    assert result["run_health"]["v60_consideration_ledger"] == "invalid"
    assert "v60_consideration_ledger_invalid" in result["run_health"]["issues"]
    invalid_detail = next(
        detail
        for detail in result["run_health"]["issue_details"]
        if detail["code"] == "v60_consideration_ledger_invalid"
    )
    assert invalid_detail["severity"] == "degraded"
    assert invalid_detail["axis"] == "v60"
    assert invalid_detail["validation_error_count"] >= 1


def test_finalize_v60_consideration_merges_valid_ledger_counts(tmp_path: Path) -> None:
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
                "chunk_kind": "affordance",
                "disposition": "used",
                "route": "updated_position",
                "strongest_plausible_application": "Use it to name the displaced alternative.",
                "risk_if_forced": "",
                "why": "It changed the threshold.",
                "visible_effect": "Named the displaced alternative.",
            },
            {
                "chunk_id": chunk_ids[1],
                "card_id": "v60-card-001-opportunity-cost",
                "model_id": "opportunity-cost",
                "chunk_kind": "absence",
                "disposition": "rejected",
                "route": "irrelevant",
                "strongest_plausible_application": "Block generic pro/con usage.",
                "risk_if_forced": "Would claim the answer used generic pro/con reasoning.",
                "why": "That was not present.",
                "visible_effect": "",
            },
        ],
    }

    result = finalize_v60_consideration(
        {
            "run_health": {"overall": "healthy", "issues": []},
            "v60_enrichment": enrichment,
        },
        ledger=ledger,
    )

    assert result["run_health"]["overall"] == "healthy"
    assert result["run_health"]["v60_consideration_ledger"] == "valid"
    assert result["run_health"]["v60_used_chunk_count"] == 1
    assert result["run_health"]["v60_presented_but_not_used_chunk_count"] == 1
    assert result["run_health"]["v60_unaccounted_chunk_count"] == 0


def test_finalize_v60_consideration_clears_stale_invalid_issue_after_valid_rerun(
    tmp_path: Path,
) -> None:
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
    invalid_ledger = {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "transactions": [
            {
                "chunk_id": chunk_ids[0],
                "card_id": "v60-card-001-opportunity-cost",
                "model_id": "opportunity-cost",
                "chunk_kind": "affordance",
                "disposition": "used",
                "route": "irrelevant",
                "strongest_plausible_application": "Use it to name the displaced alternative.",
                "risk_if_forced": "",
                "why": "It changed the threshold.",
                "visible_effect": "Named the displaced alternative.",
            },
            {
                "chunk_id": chunk_ids[1],
                "card_id": "v60-card-001-opportunity-cost",
                "model_id": "opportunity-cost",
                "chunk_kind": "absence",
                "disposition": "rejected",
                "route": "irrelevant",
                "strongest_plausible_application": "Block generic pro/con usage.",
                "risk_if_forced": "Would claim the answer used generic pro/con reasoning.",
                "why": "That was not present.",
            },
        ],
    }
    invalid_result = finalize_v60_consideration(
        {
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
            "v60_enrichment": enrichment,
        },
        ledger=invalid_ledger,
    )
    assert invalid_result["run_health"]["overall"] == "degraded"
    assert "v60_consideration_ledger_invalid" in invalid_result["run_health"]["issues"]

    valid_ledger = {
        **invalid_ledger,
        "transactions": [
            {
                **invalid_ledger["transactions"][0],
                "route": "updated_position",
            },
            invalid_ledger["transactions"][1],
        ],
    }
    fixed_result = finalize_v60_consideration(invalid_result, ledger=valid_ledger)

    assert fixed_result["run_health"]["overall"] == "healthy"
    assert fixed_result["run_health"]["v60_consideration_ledger"] == "valid"
    assert "v60_consideration_ledger_invalid" not in fixed_result["run_health"]["issues"]
    assert "v60_consideration_ledger_missing" not in fixed_result["run_health"]["issues"]
    assert all(
        item["code"]
        not in {"v60_consideration_ledger_invalid", "v60_consideration_ledger_missing"}
        for item in fixed_result["run_health"]["issue_details"]
    )
