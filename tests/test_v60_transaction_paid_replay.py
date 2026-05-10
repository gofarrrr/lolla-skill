from __future__ import annotations

import json
from pathlib import Path

from scripts.run_v60_transaction_paid_replay import (
    compose_delta_audit_output,
    compose_one_edge_output,
    deterministic_identical_judge_output,
    judge_packet_outputs_are_identical,
    main as run_paid_replay_main,
    render_report,
    sanitize_output_for_judge,
    validate_consideration_usefulness_output,
    validate_delta_candidate_report_output,
    validate_one_edge_report_output,
    validate_arm_c_ledger_output,
)
from scripts.run_v60_transaction_replay_matrix import SOLUTION_MODES
from scripts.run_v60_transaction_replay_lab import LAB_VERSION


REPO_ROOT = Path(__file__).resolve().parents[1]
AFFORDANCES_V60 = REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v60.json"
EDGE_AUDIT_MODE = next(mode for mode in SOLUTION_MODES if mode.mode_id == "edge_audit")


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_paid_replay_dry_run_builds_blindable_prompt_packets(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    manifest_path = tmp_path / "cases.json"
    output_dir = tmp_path / "paid"
    _write_json(
        result_path,
        {
            "query": "Should we raise the offer or walk?",
            "vanilla_answer": "Walk if the buffer disappears.",
            "companion_cheat_sheet": {
                "anchors": [
                    {
                        "model_id": "margin-of-safety",
                        "presence_explanation": "The answer depends on liquid buffer.",
                        "evidence_quote": "buffer disappears",
                    },
                    {
                        "model_id": "premortem",
                        "presence_explanation": "The answer names failure scenarios.",
                        "evidence_quote": "old house surprise",
                    },
                ]
            },
            "structural_coverage_card": {
                "gap_routes": [
                    {
                        "dimension_id": "risk-response",
                        "dimension_name": "Risk Response",
                        "candidate_model_ids": ["optionality", "sunk-cost-fallacy"],
                    }
                ]
            },
        },
    )
    _write_json(
        manifest_path,
        {
            "lab_version": LAB_VERSION,
            "cases": [
                {
                    "case_id": "paid-test",
                    "result_path": str(result_path),
                    "query": "Should we raise the offer or walk?",
                    "vanilla_answer": "Walk if the buffer disappears.",
                    "include_reason": "Synthetic paid replay test.",
                    "risk_notes": ["No model calls in dry run."],
                    "tags": ["personal-financial"],
                }
            ],
        },
    )

    assert (
        run_paid_replay_main(
            [
                "--case-manifest",
                str(manifest_path),
                "--affordances-path",
                str(AFFORDANCES_V60),
                "--output-dir",
                str(output_dir),
                "--cases",
                "paid-test",
                "--modes",
                "edge_audit",
                "--dry-run",
            ]
        )
        == 0
    )

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["dry_run"] is True
    assert summary["paid_calls_made"] is False
    assert summary["item_count"] == 1
    assert summary["config"]["config_id"] == "cap8_focused"
    assert summary["items"][0]["candidate_model_ids"][:2] == [
        "margin-of-safety",
        "premortem",
    ]

    arm_c_prompt = json.loads(
        (output_dir / "prompt_packets" / "paid-test__edge_audit" / "arm_c.json").read_text(
            encoding="utf-8"
        )
    )
    contract = arm_c_prompt["user_packet"]["output_contract"]
    assert "card_transaction_ledger_schema" in contract
    assert contract["card_transaction_ledger_schema"]["packet_id"].startswith("paid-cap8")
    assert arm_c_prompt["user_packet"]["reasoning_substrate_packet"]["view"] == "decoder_compact_v1"

    report = (output_dir / "paid_replay_report.md").read_text(encoding="utf-8")
    assert "V60 Transaction Paid Replay Report" in report
    assert "Ledger validation" in report


def test_paid_replay_hidden_variant_builds_private_ledger_contract(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    manifest_path = tmp_path / "cases.json"
    output_dir = tmp_path / "paid-hidden"
    _write_json(
        result_path,
        {
            "query": "Should we renegotiate or walk?",
            "vanilla_answer": "Renegotiate only if the fallback is credible.",
            "companion_cheat_sheet": {
                "anchors": [
                    {
                        "model_id": "batna",
                        "presence_explanation": "Fallback quality governs the negotiation.",
                        "evidence_quote": "fallback is credible",
                    },
                    {
                        "model_id": "principal-agent-problem",
                        "presence_explanation": "The broker's incentives may diverge.",
                        "evidence_quote": "broker pushes urgency",
                    },
                ]
            },
        },
    )
    _write_json(
        manifest_path,
        {
            "lab_version": LAB_VERSION,
            "cases": [
                {
                    "case_id": "paid-hidden-test",
                    "result_path": str(result_path),
                    "query": "Should we renegotiate or walk?",
                    "vanilla_answer": "Renegotiate only if the fallback is credible.",
                    "include_reason": "Synthetic hidden-ledger replay test.",
                    "risk_notes": ["No model calls in dry run."],
                    "tags": ["negotiation"],
                }
            ],
        },
    )

    assert (
        run_paid_replay_main(
            [
                "--case-manifest",
                str(manifest_path),
                "--affordances-path",
                str(AFFORDANCES_V60),
                "--output-dir",
                str(output_dir),
                "--cases",
                "paid-hidden-test",
                "--modes",
                "edge_audit",
                "--c-variant",
                "hidden",
                "--dry-run",
            ]
        )
        == 0
    )

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["c_variant"] == "hidden"
    assert summary["items"][0]["c_variant"] == "hidden"

    arm_c_prompt = json.loads(
        (output_dir / "prompt_packets" / "paid-hidden-test__edge_audit" / "arm_c.json").read_text(
            encoding="utf-8"
        )
    )
    assert "Hidden-ledger discipline" in arm_c_prompt["system_prompt"]
    contract = arm_c_prompt["user_packet"]["output_contract"]
    assert contract["final_answer"] == "same public prose as user_visible_answer"
    assert contract["edge_findings"] == "same public list as user_visible_edges"
    assert "private_transaction_ledger" in contract
    assert "private_delta_notes" in contract
    assert "user_visible_answer" in contract
    assert "user_visible_edges" in contract
    assert "card_transaction_ledger_schema" in contract

    report = (output_dir / "paid_replay_report.md").read_text(encoding="utf-8")
    assert "C variant: `hidden`" in report


def test_paid_replay_delta_variant_builds_delta_only_contract(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    manifest_path = tmp_path / "cases.json"
    output_dir = tmp_path / "paid-delta"
    _write_json(
        result_path,
        {
            "query": "Should we launch now or wait?",
            "vanilla_answer": "Launch only if the sales signal appears within four weeks.",
            "companion_cheat_sheet": {
                "anchors": [
                    {
                        "model_id": "optionality",
                        "presence_explanation": "The answer preserves a wait option.",
                        "evidence_quote": "wait",
                    },
                    {
                        "model_id": "base-rates",
                        "presence_explanation": "The plan depends on conversion evidence.",
                        "evidence_quote": "sales signal",
                    },
                ]
            },
        },
    )
    _write_json(
        manifest_path,
        {
            "lab_version": LAB_VERSION,
            "cases": [
                {
                    "case_id": "paid-delta-test",
                    "result_path": str(result_path),
                    "query": "Should we launch now or wait?",
                    "vanilla_answer": "Launch only if the sales signal appears within four weeks.",
                    "include_reason": "Synthetic C3 delta-only replay test.",
                    "risk_notes": ["No model calls in dry run."],
                    "tags": ["startup"],
                }
            ],
        },
    )

    assert (
        run_paid_replay_main(
            [
                "--case-manifest",
                str(manifest_path),
                "--affordances-path",
                str(AFFORDANCES_V60),
                "--output-dir",
                str(output_dir),
                "--cases",
                "paid-delta-test",
                "--modes",
                "edge_audit",
                "--c-variant",
                "delta",
                "--dry-run",
            ]
        )
        == 0
    )

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["c_variant"] == "delta"
    assert summary["aggregate"]["delta_validation_counts"] == {"not_run_dry_run": 1}

    arm_c_prompt = json.loads(
        (output_dir / "prompt_packets" / "paid-delta-test__edge_audit" / "arm_c.json").read_text(
            encoding="utf-8"
        )
    )
    assert "C3 delta-only discipline" in arm_c_prompt["system_prompt"]
    contract = arm_c_prompt["user_packet"]["output_contract"]
    assert "private_transaction_ledger" in contract
    assert "delta_candidate_report" in contract
    assert "card_transaction_ledger_schema" in contract
    assert "final_answer" not in contract
    assert "user_visible_answer" not in contract

    report = (output_dir / "paid_replay_report.md").read_text(encoding="utf-8")
    assert "C variant: `delta`" in report
    assert "Delta validation" in report


def test_paid_replay_delta_gated_variant_builds_quality_gate_contract(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    manifest_path = tmp_path / "cases.json"
    output_dir = tmp_path / "paid-delta-gated"
    _write_json(
        result_path,
        {
            "query": "Should we report internally or externally?",
            "vanilla_answer": "Get counsel before reporting.",
            "companion_cheat_sheet": {
                "anchors": [
                    {
                        "model_id": "information-asymmetry",
                        "presence_explanation": "The answer depends on who knows what.",
                        "evidence_quote": "before reporting",
                    }
                ]
            },
        },
    )
    _write_json(
        manifest_path,
        {
            "lab_version": LAB_VERSION,
            "cases": [
                {
                    "case_id": "paid-delta-gated-test",
                    "result_path": str(result_path),
                    "query": "Should we report internally or externally?",
                    "vanilla_answer": "Get counsel before reporting.",
                    "include_reason": "Synthetic C3.5 gated replay test.",
                    "risk_notes": ["No model calls in dry run."],
                    "tags": ["ethics"],
                }
            ],
        },
    )

    assert (
        run_paid_replay_main(
            [
                "--case-manifest",
                str(manifest_path),
                "--affordances-path",
                str(AFFORDANCES_V60),
                "--output-dir",
                str(output_dir),
                "--cases",
                "paid-delta-gated-test",
                "--modes",
                "edge_audit",
                "--c-variant",
                "delta_gated",
                "--dry-run",
            ]
        )
        == 0
    )

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["c_variant"] == "delta_gated"
    assert summary["aggregate"]["delta_validation_counts"] == {"not_run_dry_run": 1}

    arm_c_prompt = json.loads(
        (
            output_dir
            / "prompt_packets"
            / "paid-delta-gated-test__edge_audit"
            / "arm_c.json"
        ).read_text(encoding="utf-8")
    )
    assert "C3 delta-only discipline" in arm_c_prompt["system_prompt"]
    assert "C3.5 public-delta gate discipline" in arm_c_prompt["system_prompt"]
    accepted_delta = arm_c_prompt["user_packet"]["output_contract"][
        "delta_candidate_report"
    ]["accepted_deltas"][0]
    assert "delta_type" in accepted_delta


def test_paid_replay_delta_compact_variant_builds_c36_contract(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    manifest_path = tmp_path / "cases.json"
    output_dir = tmp_path / "paid-delta-compact"
    _write_json(
        result_path,
        {
            "query": "Should we report internally or externally?",
            "vanilla_answer": "Get counsel before reporting.",
            "companion_cheat_sheet": {
                "anchors": [
                    {
                        "model_id": "information-asymmetry",
                        "presence_explanation": "The answer depends on who knows what.",
                        "evidence_quote": "before reporting",
                    }
                ]
            },
        },
    )
    _write_json(
        manifest_path,
        {
            "lab_version": LAB_VERSION,
            "cases": [
                {
                    "case_id": "paid-delta-compact-test",
                    "result_path": str(result_path),
                    "query": "Should we report internally or externally?",
                    "vanilla_answer": "Get counsel before reporting.",
                    "include_reason": "Synthetic C3.6 compact replay test.",
                    "risk_notes": ["No model calls in dry run."],
                    "tags": ["ethics"],
                }
            ],
        },
    )

    assert (
        run_paid_replay_main(
            [
                "--case-manifest",
                str(manifest_path),
                "--affordances-path",
                str(AFFORDANCES_V60),
                "--output-dir",
                str(output_dir),
                "--cases",
                "paid-delta-compact-test",
                "--modes",
                "edge_audit",
                "--c-variant",
                "delta_compact",
                "--dry-run",
            ]
        )
        == 0
    )

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["c_variant"] == "delta_compact"
    assert summary["aggregate"]["delta_validation_counts"] == {"not_run_dry_run": 1}

    arm_c_prompt = json.loads(
        (
            output_dir
            / "prompt_packets"
            / "paid-delta-compact-test__edge_audit"
            / "arm_c.json"
        ).read_text(encoding="utf-8")
    )
    assert "C3 delta-only discipline" in arm_c_prompt["system_prompt"]
    assert "C3.6 compact public-delta gate discipline" in arm_c_prompt["system_prompt"]
    assert "Return at most one public addition" in arm_c_prompt["system_prompt"]


def test_paid_replay_one_edge_variant_builds_c4_contract(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    manifest_path = tmp_path / "cases.json"
    output_dir = tmp_path / "paid-one-edge"
    _write_json(
        result_path,
        {
            "query": "Should we raise the offer or walk?",
            "vanilla_answer": "Walk if the buffer disappears.",
            "companion_cheat_sheet": {
                "anchors": [
                    {
                        "model_id": "premortem",
                        "presence_explanation": "The answer names failure scenarios.",
                        "evidence_quote": "old house surprise",
                    }
                ]
            },
        },
    )
    _write_json(
        manifest_path,
        {
            "lab_version": LAB_VERSION,
            "cases": [
                {
                    "case_id": "paid-one-edge-test",
                    "result_path": str(result_path),
                    "query": "Should we raise the offer or walk?",
                    "vanilla_answer": "Walk if the buffer disappears.",
                    "include_reason": "Synthetic C4 one-edge replay test.",
                    "risk_notes": ["No model calls in dry run."],
                    "tags": ["personal-financial"],
                }
            ],
        },
    )

    assert (
        run_paid_replay_main(
            [
                "--case-manifest",
                str(manifest_path),
                "--affordances-path",
                str(AFFORDANCES_V60),
                "--output-dir",
                str(output_dir),
                "--cases",
                "paid-one-edge-test",
                "--modes",
                "edge_audit",
                "--c-variant",
                "one_edge",
                "--dry-run",
            ]
        )
        == 0
    )

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["c_variant"] == "one_edge"
    assert summary["aggregate"]["delta_validation_counts"] == {"not_run_dry_run": 1}

    arm_c_prompt = json.loads(
        (
            output_dir
            / "prompt_packets"
            / "paid-one-edge-test__edge_audit"
            / "arm_c.json"
        ).read_text(encoding="utf-8")
    )
    contract = arm_c_prompt["user_packet"]["output_contract"]
    assert "C4 one-edge transaction discipline" in arm_c_prompt["system_prompt"]
    assert "private_consideration_trace" in contract
    assert "one_edge_report" in contract
    assert "private_transaction_ledger" not in contract
    assert "card_transaction_ledger_schema" not in contract

    candidate_output_dir = tmp_path / "paid-candidate-edge"
    assert (
        run_paid_replay_main(
            [
                "--case-manifest",
                str(manifest_path),
                "--affordances-path",
                str(AFFORDANCES_V60),
                "--output-dir",
                str(candidate_output_dir),
                "--cases",
                "paid-one-edge-test",
                "--modes",
                "edge_audit",
                "--c-variant",
                "candidate_edge",
                "--dry-run",
            ]
        )
        == 0
    )

    candidate_summary = json.loads(
        (candidate_output_dir / "summary.json").read_text(encoding="utf-8")
    )
    assert candidate_summary["c_variant"] == "candidate_edge"

    candidate_prompt = json.loads(
        (
            candidate_output_dir
            / "prompt_packets"
            / "paid-one-edge-test__edge_audit"
            / "arm_c.json"
        ).read_text(encoding="utf-8")
    )
    candidate_contract = candidate_prompt["user_packet"]["output_contract"]
    assert "C4.1 candidate-edge transaction discipline" in candidate_prompt["system_prompt"]
    assert "private_consideration_trace" in candidate_contract
    assert "one_edge_report" in candidate_contract
    assert "best_candidate_edge" in candidate_contract["one_edge_report"]
    assert "private_transaction_ledger" not in candidate_contract
    assert "card_transaction_ledger_schema" not in candidate_contract

    hardened_output_dir = tmp_path / "paid-candidate-edge-hardened"
    assert (
        run_paid_replay_main(
            [
                "--case-manifest",
                str(manifest_path),
                "--affordances-path",
                str(AFFORDANCES_V60),
                "--output-dir",
                str(hardened_output_dir),
                "--cases",
                "paid-one-edge-test",
                "--modes",
                "edge_audit",
                "--c-variant",
                "candidate_edge_hardened",
                "--dry-run",
            ]
        )
        == 0
    )

    hardened_summary = json.loads(
        (hardened_output_dir / "summary.json").read_text(encoding="utf-8")
    )
    assert hardened_summary["c_variant"] == "candidate_edge_hardened"

    hardened_prompt = json.loads(
        (
            hardened_output_dir
            / "prompt_packets"
            / "paid-one-edge-test__edge_audit"
            / "arm_c.json"
        ).read_text(encoding="utf-8")
    )
    hardened_contract = hardened_prompt["user_packet"]["output_contract"]
    assert "C4.2 hardened candidate-edge discipline" in hardened_prompt["system_prompt"]
    assert "best_candidate_edge" in hardened_contract["one_edge_report"]
    assert "evidence_status" in hardened_contract["one_edge_report"]["best_candidate_edge"]
    assert "private_transaction_ledger" not in hardened_contract
    assert "card_transaction_ledger_schema" not in hardened_contract


def test_paid_replay_consideration_router_builds_c43_contract(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    manifest_path = tmp_path / "cases.json"
    output_dir = tmp_path / "paid-consideration-router"
    _write_json(
        result_path,
        {
            "query": "Should we pivot the startup now or preserve current revenue?",
            "vanilla_answer": "Preserve current revenue unless the new workflow tool has evidence.",
            "companion_cheat_sheet": {
                "anchors": [
                    {
                        "model_id": "optionality",
                        "presence_explanation": "The answer preserves a reversible path.",
                        "evidence_quote": "preserve current revenue",
                    },
                    {
                        "model_id": "premortem",
                        "presence_explanation": "The answer asks what would fail.",
                        "evidence_quote": "has evidence",
                    },
                ]
            },
        },
    )
    _write_json(
        manifest_path,
        {
            "lab_version": LAB_VERSION,
            "cases": [
                {
                    "case_id": "paid-consideration-router-test",
                    "result_path": str(result_path),
                    "query": "Should we pivot the startup now or preserve current revenue?",
                    "vanilla_answer": (
                        "Preserve current revenue unless the new workflow tool has evidence."
                    ),
                    "include_reason": "Synthetic C4.3 consideration-router replay test.",
                    "risk_notes": ["No model calls in dry run."],
                    "tags": ["startup"],
                }
            ],
        },
    )

    assert (
        run_paid_replay_main(
            [
                "--case-manifest",
                str(manifest_path),
                "--affordances-path",
                str(AFFORDANCES_V60),
                "--output-dir",
                str(output_dir),
                "--cases",
                "paid-consideration-router-test",
                "--modes",
                "edge_audit",
                "--c-variant",
                "consideration_router",
                "--dry-run",
            ]
        )
        == 0
    )

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["c_variant"] == "consideration_router"
    assert summary["aggregate"]["consideration_validation_counts"] == {
        "not_run_dry_run": 1
    }

    arm_c_prompt = json.loads(
        (
            output_dir
            / "prompt_packets"
            / "paid-consideration-router-test__edge_audit"
            / "arm_c.json"
        ).read_text(encoding="utf-8")
    )
    contract = arm_c_prompt["user_packet"]["output_contract"]
    assert "C4.3 consideration-router discipline" in arm_c_prompt["system_prompt"]
    assert "private_transaction_ledger" in contract
    assert "consideration_usefulness_report" in contract
    assert "chunk_assessments" in contract["consideration_usefulness_report"]
    assert "selected_opportunities" in contract["consideration_usefulness_report"]
    assert "card_transaction_ledger_schema" in contract
    assert "useful to consider" in arm_c_prompt["system_prompt"]

    report = (output_dir / "paid_replay_report.md").read_text(encoding="utf-8")
    assert "Consideration validation" in report


def test_judge_sanitization_removes_ledger_trace() -> None:
    sanitized = sanitize_output_for_judge(
        {
            "final_answer": "Use the buffer.",
            "card_transaction_ledger": {"secret": "trace"},
            "card_transactions": [{"card_id": "card-001"}],
            "packet_id": "packet",
            "ledger_version": "card_transaction_ledger.v1",
        }
    )

    assert sanitized == {"final_answer": "Use the buffer."}


def test_judge_sanitization_maps_hidden_public_fields_and_removes_private_trace() -> None:
    sanitized = sanitize_output_for_judge(
        {
            "user_visible_answer": "Use the buffer, but only after verifying the fallback.",
            "user_visible_edges": [
                "The fallback must be executable, not merely preferred.",
            ],
            "private_transaction_ledger": {"secret": "trace"},
            "private_delta_notes": {"changed": ["added fallback evidence gate"]},
            "packet_id": "packet",
            "ledger_version": "card_transaction_ledger.v1",
        }
    )

    assert sanitized == {
        "final_answer": "Use the buffer, but only after verifying the fallback.",
        "edge_findings": [
            "The fallback must be executable, not merely preferred.",
        ],
    }


def test_judge_sanitization_removes_c3_delta_trace() -> None:
    sanitized = sanitize_output_for_judge(
        {
            "final_answer": "Keep the baseline answer.",
            "edge_findings": ["Verify the fallback before treating it as leverage."],
            "private_transaction_ledger": {"secret": "trace"},
            "delta_candidate_report": {"accepted_deltas": []},
            "one_edge_report": {"should_add_public_delta": True},
            "private_consideration_trace": [{"card_id": "card-001"}],
            "c3_composition": {"accepted_delta_count": 0},
        }
    )

    assert sanitized == {
        "final_answer": "Keep the baseline answer.",
        "edge_findings": ["Verify the fallback before treating it as leverage."],
    }


def test_identical_judge_guard_forces_deterministic_tie() -> None:
    packet = {
        "output_labels": [
            {"label": "A", "output": {"final_answer": "Same answer."}},
            {"label": "B", "output": {"final_answer": "Same answer."}},
        ]
    }

    assert judge_packet_outputs_are_identical(packet) is True
    judge = deterministic_identical_judge_output(blind_map={"A": "C", "B": "B"})

    assert judge["status"] == "deterministic_identical_output_tie"
    assert judge["unblinded"]["winner"] == "tie"
    assert judge["unblinded"]["constructive_edge"] == "tie"


def test_c3_composer_preserves_baseline_and_adds_public_deltas() -> None:
    composed = compose_delta_audit_output(
        arm_b_output={
            "final_answer": "Keep the launch plan conditional on real demand.",
            "edge_findings": ["Do not treat verbal interest as revenue."],
            "rewrite_required": "only small caveat",
        },
        delta_output={
            "private_transaction_ledger": {"ledger_version": "card_transaction_ledger.v1"},
            "delta_candidate_report": {
                "accepted_deltas": [
                    {
                        "source_card_ids": ["card-001-optionality"],
                        "public_edge_text": "Preserve the wait option until one buyer makes a dated commitment.",
                    }
                ],
                "deferred_questions": [
                    {
                        "source_card_ids": ["card-002-base-rates"],
                        "public_question_text": "What conversion rate has this channel produced before?",
                        "missing_evidence": ["historical conversion rate"],
                    }
                ],
                "risk_warnings": [
                    {
                        "source_card_ids": ["card-003-planning-fallacy"],
                        "public_warning_text": "The six-week timeline may be optimism rather than evidence.",
                    }
                ],
            },
        },
        mode=EDGE_AUDIT_MODE,
    )

    assert composed["final_answer"] == "Keep the launch plan conditional on real demand."
    assert composed["edge_findings"] == [
        "Do not treat verbal interest as revenue.",
        "Preserve the wait option until one buyer makes a dated commitment.",
        [
            "What conversion rate has this channel produced before?",
            "Missing evidence: historical conversion rate",
        ],
        "The six-week timeline may be optimism rather than evidence.",
    ]
    assert composed["c3_composition"]["accepted_delta_count"] == 1
    assert composed["c3_composition"]["no_delta_collapse_to_b"] is False


def test_c3_composer_collapses_to_baseline_when_no_public_delta() -> None:
    composed = compose_delta_audit_output(
        arm_b_output={
            "final_answer": "Use the existing answer.",
            "edge_findings": ["Existing edge."],
        },
        delta_output={
            "private_transaction_ledger": {"ledger_version": "card_transaction_ledger.v1"},
            "delta_candidate_report": {
                "accepted_deltas": [],
                "deferred_questions": [],
                "risk_warnings": [],
                "no_delta_reason": "Cards duplicate the baseline pressure.",
            },
        },
        mode=EDGE_AUDIT_MODE,
    )

    assert composed["final_answer"] == "Use the existing answer."
    assert composed["edge_findings"] == ["Existing edge."]
    assert composed["c3_composition"]["no_delta_collapse_to_b"] is True


def test_c3_composer_preserves_structured_baseline_edges() -> None:
    composed = compose_delta_audit_output(
        arm_b_output={
            "final_answer": "Use the existing answer.",
            "edge_findings": [
                [
                    "Existing edge",
                    "Why it matters",
                    "Action",
                ]
            ],
        },
        delta_output={
            "private_transaction_ledger": {"ledger_version": "card_transaction_ledger.v1"},
            "delta_candidate_report": {
                "accepted_deltas": [
                    {
                        "source_card_ids": ["card-001-optionality"],
                        "public_edge_text": "Additional public edge.",
                    }
                ],
                "deferred_questions": [],
                "risk_warnings": [],
            },
        },
        mode=EDGE_AUDIT_MODE,
    )

    assert composed["edge_findings"] == [
        [
            "Existing edge",
            "Why it matters",
            "Action",
        ],
        "Additional public edge.",
    ]


def test_c35_public_delta_gate_caps_and_drops_framework_language() -> None:
    composed = compose_delta_audit_output(
        arm_b_output={
            "final_answer": "Get counsel before reporting.",
            "edge_findings": [],
        },
        delta_output={
            "private_transaction_ledger": {"ledger_version": "card_transaction_ledger.v1"},
            "delta_candidate_report": {
                "accepted_deltas": [
                    {
                        "delta_id": "framework",
                        "delta_type": "concrete_next_move",
                        "source_card_ids": ["card-001"],
                        "public_edge_text": "Payoff map names the decisive branches.",
                        "public_delta_text": "Add a game tree before choosing.",
                        "why_user_should_care": "It clarifies principal-agent incentives.",
                    },
                    {
                        "delta_id": "gate",
                        "delta_type": "evidence_gate",
                        "source_card_ids": ["card-002"],
                        "public_edge_text": "Document before reporting.",
                        "public_delta_text": "Before any report, write a timestamped factual note off work systems.",
                        "why_user_should_care": "It turns memory into usable evidence.",
                    },
                    {
                        "delta_id": "move",
                        "delta_type": "concrete_next_move",
                        "source_card_ids": ["card-003"],
                        "public_edge_text": "Call counsel before internal escalation.",
                        "public_delta_text": "Schedule two whistleblower-attorney intake calls tomorrow.",
                        "why_user_should_care": "It prevents procedural mistakes.",
                    },
                    {
                        "delta_id": "over-cap",
                        "delta_type": "risk_caveat",
                        "source_card_ids": ["card-004"],
                        "public_edge_text": "Internal report may leak early.",
                        "public_delta_text": "Do not tell colleagues before counsel reviews the facts.",
                        "why_user_should_care": "It prevents avoidable retaliation risk.",
                    },
                ],
                "deferred_questions": [],
                "risk_warnings": [],
            },
        },
        mode=EDGE_AUDIT_MODE,
        public_delta_gate=True,
    )

    assert composed["edge_findings"] == [
        [
            "Document before reporting.",
            "It turns memory into usable evidence.",
            "Before any report, write a timestamped factual note off work systems.",
        ],
        [
            "Call counsel before internal escalation.",
            "It prevents procedural mistakes.",
            "Schedule two whistleblower-attorney intake calls tomorrow.",
        ],
    ]
    assert composed["c3_composition"]["accepted_delta_count"] == 2
    assert composed["c3_composition"]["dropped_public_delta_count"] == 2
    reasons = {
        item["reason"]
        for item in composed["c3_composition"]["dropped_public_deltas"]
    }
    assert "analytical_framework_language" in reasons
    assert "public_delta_cap_exceeded" in reasons


def test_c35_public_delta_gate_collapses_when_only_weak_deltas_survive() -> None:
    composed = compose_delta_audit_output(
        arm_b_output={
            "final_answer": "Use the existing answer.",
            "edge_findings": ["Existing edge."],
        },
        delta_output={
            "private_transaction_ledger": {"ledger_version": "card_transaction_ledger.v1"},
            "delta_candidate_report": {
                "accepted_deltas": [
                    {
                        "delta_id": "bad-type",
                        "delta_type": "analysis_note",
                        "source_card_ids": ["card-001"],
                        "public_edge_text": "Better analysis.",
                        "public_delta_text": "Think harder about the incentives.",
                    }
                ],
                "deferred_questions": [],
                "risk_warnings": [],
            },
        },
        mode=EDGE_AUDIT_MODE,
        public_delta_gate=True,
    )

    assert composed["final_answer"] == "Use the existing answer."
    assert composed["edge_findings"] == ["Existing edge."]
    assert composed["c3_composition"]["no_delta_collapse_to_b"] is True
    assert composed["c3_composition"]["dropped_public_deltas"][0]["reason"] == (
        "invalid_or_missing_delta_type"
    )


def test_c36_compact_gate_prefers_evidence_gate_over_lower_priority_delta() -> None:
    composed = compose_delta_audit_output(
        arm_b_output={
            "final_answer": "Get counsel before reporting.",
            "edge_findings": [],
        },
        delta_output={
            "private_transaction_ledger": {"ledger_version": "card_transaction_ledger.v1"},
            "delta_candidate_report": {
                "accepted_deltas": [
                    {
                        "delta_id": "risk-first",
                        "delta_type": "risk_caveat",
                        "source_card_ids": ["card-001"],
                        "case_quote": "I have two kids and a mortgage.",
                        "evidence_status": "quoted_exact",
                        "public_edge_text": "Family risk can distort the timing.",
                        "public_delta_text": "Before reporting, check whether your emergency fund covers six months.",
                        "why_user_should_care": "It sizes career-risk exposure.",
                    },
                    {
                        "delta_id": "evidence-second",
                        "delta_type": "evidence_gate",
                        "source_card_ids": ["card-002"],
                        "case_quote": "I have no documentation yet.",
                        "evidence_status": "quoted_exact",
                        "public_edge_text": "No documentation is the blocker.",
                        "public_delta_text": "Before any report, write a timestamped factual note off work systems.",
                        "why_user_should_care": "It turns memory into usable evidence.",
                    },
                    {
                        "delta_id": "move-third",
                        "delta_type": "concrete_next_move",
                        "source_card_ids": ["card-003"],
                        "case_quote": "I have no documentation yet.",
                        "evidence_status": "quoted_exact",
                        "public_edge_text": "Counsel sequencing matters.",
                        "public_delta_text": "Schedule one whistleblower-attorney intake call tomorrow.",
                        "why_user_should_care": "It prevents procedural mistakes.",
                    },
                ],
                "deferred_questions": [],
                "risk_warnings": [],
            },
        },
        mode=EDGE_AUDIT_MODE,
        public_delta_gate=True,
        public_delta_gate_policy="c3_6_compact",
    )

    assert composed["edge_findings"] == [
        [
            "No documentation is the blocker.",
            "It turns memory into usable evidence.",
            "Before any report, write a timestamped factual note off work systems.",
        ],
    ]
    assert composed["c3_composition"]["accepted_delta_count"] == 1
    assert composed["c3_composition"]["public_delta_gate_version"] == (
        "c3_6_compact_public_delta_gate.v1"
    )
    reasons = [
        item["reason"]
        for item in composed["c3_composition"]["dropped_public_deltas"]
    ]
    assert reasons.count("public_delta_cap_exceeded") == 2


def test_c36_compact_gate_drops_missing_case_quote_and_duplicate_baseline() -> None:
    composed = compose_delta_audit_output(
        arm_b_output={
            "final_answer": "Before any report, write a timestamped factual note off work systems.",
            "edge_findings": [],
        },
        delta_output={
            "private_transaction_ledger": {"ledger_version": "card_transaction_ledger.v1"},
            "delta_candidate_report": {
                "accepted_deltas": [
                    {
                        "delta_id": "missing-quote",
                        "delta_type": "evidence_gate",
                        "source_card_ids": ["card-001"],
                        "case_quote": "",
                        "evidence_status": "inferred_from_turn",
                        "public_edge_text": "Missing proof blocks stronger advice.",
                        "public_delta_text": "Before any report, document exactly what you saw.",
                        "why_user_should_care": "It prevents a memory-only report.",
                    },
                    {
                        "delta_id": "duplicate",
                        "delta_type": "concrete_next_move",
                        "source_card_ids": ["card-002"],
                        "case_quote": "I have no documentation yet.",
                        "evidence_status": "quoted_exact",
                        "public_edge_text": "Document facts before reporting.",
                        "public_delta_text": "Before any report, write a timestamped factual note off work systems.",
                        "why_user_should_care": "It turns memory into usable evidence.",
                    },
                ],
                "deferred_questions": [],
                "risk_warnings": [],
            },
        },
        mode=EDGE_AUDIT_MODE,
        public_delta_gate=True,
        public_delta_gate_policy="c3_6_compact",
    )

    assert composed["edge_findings"] == []
    assert composed["c3_composition"]["no_delta_collapse_to_b"] is True
    reasons = {
        item["reason"]
        for item in composed["c3_composition"]["dropped_public_deltas"]
    }
    assert "missing_case_quote" in reasons
    assert "duplicate_of_baseline_public_output" in reasons


def test_c4_one_edge_composer_adds_one_edge_and_builds_valid_ledger() -> None:
    packet = {
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "candidate_cards": [
            {
                "card_id": "card-001-wysiati",
                "model_id": "wysiati",
                "reviewed_affordance_cards": [
                    {"affordance_id": "wysiati.missing-evidence-denominator-audit"}
                ],
            },
            {
                "card_id": "card-002-premortem",
                "model_id": "premortem",
                "reviewed_affordance_cards": [
                    {"affordance_id": "premortem.simulated-failure-to-plan-change"}
                ],
            },
        ],
    }
    composed = compose_one_edge_output(
        arm_b_output={
            "final_answer": "Do not move until the care plan is clearer.",
            "edge_findings": [],
        },
        one_edge_output={
            "private_consideration_trace": [
                {
                    "card_id": "card-001-wysiati",
                    "disposition": "used",
                    "affordance_ids_considered": [
                        "wysiati.missing-evidence-denominator-audit"
                    ],
                    "reason": "The move depends on unverified care coverage.",
                    "case_quote": "Has she seen a neurologist?",
                    "evidence_status": "quoted_exact",
                },
                {
                    "card_id": "card-002-premortem",
                    "disposition": "rejected",
                    "affordance_ids_considered": [
                        "premortem.simulated-failure-to-plan-change"
                    ],
                    "reason": "The baseline already stress-tests the move.",
                    "risk_if_forced": "Would add duplicate downside language.",
                },
            ],
            "one_edge_report": {
                "should_add_public_delta": True,
                "delta_type": "evidence_gate",
                "source_card_ids": ["card-001-wysiati"],
                "affordance_ids": ["wysiati.missing-evidence-denominator-audit"],
                "case_quote": "Has she seen a neurologist?",
                "public_delta_text": "Before finalizing the move, confirm the care plan and schedule the cognitive evaluation.",
                "why_this_changes_the_decision": "It decides whether remote support is viable.",
                "confidence": "high",
            },
        },
        packet=packet,
        mode=EDGE_AUDIT_MODE,
    )

    assert composed["edge_findings"] == [
        [
            "Before finalizing the move, confirm the care plan and schedule the cognitive evaluation.",
            "It decides whether remote support is viable.",
        ]
    ]
    assert composed["c3_composition"]["accepted_delta_count"] == 1
    assert composed["c3_composition"]["composition_version"] == "c4_one_edge_composer.v1"
    assert validate_arm_c_ledger_output(composed, packet=packet)["status"] == "valid"
    assert validate_one_edge_report_output(composed, packet=packet)["status"] == "valid"
    summary = composed["private_transaction_ledger"]["summary"]
    assert summary["used_count"] == 1
    assert summary["rejected_count"] == 1
    assert summary["visible_delta_count"] == 1


def test_c4_one_edge_composer_collapses_and_still_builds_valid_ledger() -> None:
    packet = {
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "candidate_cards": [
            {
                "card_id": "card-001-premortem",
                "model_id": "premortem",
                "reviewed_affordance_cards": [
                    {"affordance_id": "premortem.simulated-failure-to-plan-change"}
                ],
            }
        ],
    }
    composed = compose_one_edge_output(
        arm_b_output={
            "final_answer": "Keep the baseline answer.",
            "edge_findings": ["Existing edge."],
        },
        one_edge_output={
            "private_consideration_trace": [
                {
                    "card_id": "card-001-premortem",
                    "disposition": "rejected",
                    "reason": "The baseline already contains the useful stress test.",
                    "risk_if_forced": "Would duplicate the existing edge.",
                }
            ],
            "one_edge_report": {
                "should_add_public_delta": False,
                "no_delta_reason": "The baseline already contains the useful stress test.",
            },
        },
        packet=packet,
        mode=EDGE_AUDIT_MODE,
    )

    assert composed["final_answer"] == "Keep the baseline answer."
    assert composed["edge_findings"] == ["Existing edge."]
    assert composed["c3_composition"]["no_delta_collapse_to_b"] is True
    assert validate_arm_c_ledger_output(composed, packet=packet)["status"] == "valid"
    assert validate_one_edge_report_output(composed, packet=packet)["status"] == "valid"
    assert composed["private_transaction_ledger"]["summary"]["no_effect_count"] == 1


def test_c41_candidate_edge_composer_uses_best_candidate_despite_advisory_recommendation() -> None:
    packet = {
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "candidate_cards": [
            {
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "reviewed_affordance_cards": [
                    {"affordance_id": "optionality.keep-choice-alive"}
                ],
            }
        ],
    }
    composed = compose_one_edge_output(
        arm_b_output={
            "final_answer": "Keep the current plan unless demand changes.",
            "edge_findings": [],
        },
        one_edge_output={
            "private_consideration_trace": [
                {
                    "card_id": "card-001-optionality",
                    "disposition": "used",
                    "affordance_ids_considered": ["optionality.keep-choice-alive"],
                    "reason": "The baseline underweights making demand real before choosing.",
                    "case_quote": "three interested buyers",
                    "evidence_status": "quoted_exact",
                }
            ],
            "one_edge_report": {
                "best_candidate_edge": {
                    "delta_type": "concrete_next_move",
                    "source_card_ids": ["card-001-optionality"],
                    "affordance_ids": ["optionality.keep-choice-alive"],
                    "case_quote": "three interested buyers",
                    "public_delta_text": "Before choosing, call one interested buyer and ask for a dated purchase commitment.",
                    "why_this_changes_the_decision": "It converts vague interest into a real option test.",
                    "confidence": "high",
                    "admission_risk": "It may duplicate the baseline if the answer already asks for commitments.",
                },
                "recommend_public_admission": False,
                "admission_rationale": "The edge may be redundant, so the deterministic gate should decide.",
            },
        },
        packet=packet,
        mode=EDGE_AUDIT_MODE,
        public_delta_gate_policy="c4_1_candidate_edge",
    )

    assert composed["edge_findings"] == [
        [
            "Before choosing, call one interested buyer and ask for a dated purchase commitment.",
            "It converts vague interest into a real option test.",
        ]
    ]
    assert composed["c3_composition"]["composition_version"] == (
        "c4_1_candidate_edge_composer.v1"
    )
    assert composed["c3_composition"]["model_recommend_public_admission"] is False
    assert composed["c3_composition"]["accepted_delta_count"] == 1
    assert validate_arm_c_ledger_output(composed, packet=packet)["status"] == "valid"
    assert validate_one_edge_report_output(composed, packet=packet)["status"] == "valid"


def test_c42_hardened_candidate_edge_admits_option_preserving_action() -> None:
    packet = {
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "candidate_cards": [
            {
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "reviewed_affordance_cards": [
                    {"affordance_id": "optionality.expand-before-evaluating"}
                ],
            }
        ],
    }
    composed = compose_one_edge_output(
        arm_b_output={
            "final_answer": "Choose B only after diligence.",
            "edge_findings": [],
        },
        one_edge_output={
            "private_consideration_trace": [
                {
                    "card_id": "card-001-optionality",
                    "disposition": "used",
                    "affordance_ids_considered": ["optionality.expand-before-evaluating"],
                    "reason": "The deadline compresses diligence.",
                    "case_quote": "7-day decision deadline",
                    "evidence_status": "quoted_exact",
                }
            ],
            "one_edge_report": {
                "best_candidate_edge": {
                    "delta_type": "option_space_expansion",
                    "source_card_ids": ["card-001-optionality"],
                    "affordance_ids": ["optionality.expand-before-evaluating"],
                    "case_quote": "7-day decision deadline",
                    "evidence_status": "quoted_exact",
                    "public_delta_text": "Ask all three companies to extend the 7-day decision deadline to 14 days before choosing.",
                    "why_this_changes_the_decision": "It preserves time to finish diligence without rushing into B.",
                    "confidence": "high",
                    "admission_risk": "The extension may be unavailable.",
                },
                "recommend_public_admission": True,
                "admission_rationale": "Concrete option-preserving action.",
            },
        },
        packet=packet,
        mode=EDGE_AUDIT_MODE,
        public_delta_gate_policy="c4_2_hardened_edge",
        case_evidence_text="The user has a 7-day decision deadline.",
    )

    assert composed["c3_composition"]["composition_version"] == (
        "c4_2_hardened_edge_composer.v1"
    )
    assert composed["c3_composition"]["accepted_delta_count"] == 1
    assert validate_arm_c_ledger_output(composed, packet=packet)["status"] == "valid"
    assert (
        validate_one_edge_report_output(
            composed,
            packet=packet,
            case_evidence_text="The user has a 7-day decision deadline.",
            require_exact_case_quote=True,
            public_delta_gate_policy="c4_2_hardened_edge",
        )["status"]
        == "valid"
    )


def test_c42_hardened_candidate_edge_rejects_non_exact_quote() -> None:
    packet = {
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "candidate_cards": [
            {
                "card_id": "card-001-evidence",
                "model_id": "evidence",
                "reviewed_affordance_cards": [
                    {"affordance_id": "evidence.require-case-support"}
                ],
            }
        ],
    }
    payload = {
        "private_consideration_trace": [
            {
                "card_id": "card-001-evidence",
                "disposition": "used",
                "affordance_ids_considered": ["evidence.require-case-support"],
                "reason": "A move is possible only if the quoted fact is real.",
                "case_quote": "invented fact",
                "evidence_status": "quoted_exact",
            }
        ],
        "one_edge_report": {
            "best_candidate_edge": {
                "delta_type": "concrete_next_move",
                "source_card_ids": ["card-001-evidence"],
                "affordance_ids": ["evidence.require-case-support"],
                "case_quote": "invented fact",
                "evidence_status": "quoted_exact",
                "public_delta_text": "Ask counsel to verify the timestamped record before reporting.",
                "why_this_changes_the_decision": "It prevents acting on unsupported evidence.",
                "confidence": "medium",
                "admission_risk": "Quote may not be in the case.",
            },
            "recommend_public_admission": True,
            "admission_rationale": "Would be useful if grounded.",
        },
    }
    composed = compose_one_edge_output(
        arm_b_output={"final_answer": "Keep the baseline.", "edge_findings": []},
        one_edge_output=payload,
        packet=packet,
        mode=EDGE_AUDIT_MODE,
        public_delta_gate_policy="c4_2_hardened_edge",
        case_evidence_text="The case text contains no matching evidence.",
    )

    assert composed["c3_composition"]["accepted_delta_count"] == 0
    assert composed["c3_composition"]["dropped_public_deltas"][0]["reason"] == (
        "case_quote_not_exact"
    )
    validation = validate_one_edge_report_output(
        composed,
        packet=packet,
        case_evidence_text="The case text contains no matching evidence.",
        require_exact_case_quote=True,
        public_delta_gate_policy="c4_2_hardened_edge",
    )
    assert validation["status"] == "invalid"
    assert any("case_quote is not an exact case substring" in error for error in validation["errors"])


def test_c4_one_edge_validation_catches_bad_public_edge() -> None:
    packet = {
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "candidate_cards": [
            {
                "card_id": "card-001-premortem",
                "model_id": "premortem",
                "reviewed_affordance_cards": [
                    {"affordance_id": "premortem.simulated-failure-to-plan-change"}
                ],
            }
        ],
    }
    result = validate_one_edge_report_output(
        {
            "private_consideration_trace": [
                {"card_id": "card-999", "disposition": "used", "reason": "Bad trace."}
            ],
            "one_edge_report": {
                "should_add_public_delta": True,
                "delta_type": "analysis_note",
                "source_card_ids": ["card-999"],
                "affordance_ids": ["premortem.simulated-failure-to-plan-change"],
                "case_quote": "",
                "public_delta_text": "Add a payoff map for this decision.",
                "why_this_changes_the_decision": "It sounds smart.",
            },
        },
        packet=packet,
    )

    assert result["status"] == "invalid"
    assert any("source_card_ids contains unknown cards" in error for error in result["errors"])
    assert any("delta_type is invalid" in error for error in result["errors"])
    assert any("case_quote is required" in error for error in result["errors"])
    assert any("analytical-framework shaped" in error for error in result["errors"])


def test_arm_c_ledger_validation_reports_missing_ledger() -> None:
    assert validate_arm_c_ledger_output({}, packet={"candidate_cards": []}) == {
        "status": "missing_ledger"
    }


def test_arm_c_ledger_validation_repairs_summary_only_mismatch() -> None:
    packet = {
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "candidate_cards": [
            {
                "card_id": "card-001-margin-of-safety",
                "model_id": "margin-of-safety",
                "reviewed_affordance_cards": [
                    {"affordance_id": "margin-of-safety.evidence-sized-operating-buffer"}
                ],
            }
        ],
    }
    ledger = {
        "ledger_version": "card_transaction_ledger.v1",
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "card_transactions": [
            {
                "card_id": "card-001-margin-of-safety",
                "model_id": "margin-of-safety",
                "disposition": "rejected",
                "effect_type": "no_effect",
                "affordance_ids_considered": [],
                "merged_with_card_ids": [],
                "strongest_plausible_application": "The card could reinforce buffer discipline.",
                "grounding_check": {
                    "case_quote": "",
                    "evidence_status": "not_needed",
                    "missing_evidence": [],
                },
                "decision_reason": "Already covered.",
                "rejection_ground": "duplicate_of_existing_pressure",
                "risk_if_forced": "Would add no new delta.",
                "residue": "",
                "final_answer_delta": "",
                "final_answer_visibility": "not_visible",
            }
        ],
        "summary": {
            "used_count": 99,
            "rejected_count": 0,
            "deferred_count": 0,
            "visible_delta_count": 0,
            "silent_delta_count": 0,
            "no_effect_count": 0,
        },
    }

    result = validate_arm_c_ledger_output({"card_transaction_ledger": ledger}, packet=packet)

    assert result["status"] == "valid_after_summary_repair"
    assert result["summary"]["rejected_count"] == 1
    assert result["summary"]["no_effect_count"] == 1


def test_arm_c_ledger_validation_accepts_hidden_private_ledger() -> None:
    packet = {
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "candidate_cards": [
            {
                "card_id": "card-001-margin-of-safety",
                "model_id": "margin-of-safety",
                "reviewed_affordance_cards": [
                    {"affordance_id": "margin-of-safety.evidence-sized-operating-buffer"}
                ],
            }
        ],
    }
    ledger = {
        "ledger_version": "card_transaction_ledger.v1",
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "card_transactions": [
            {
                "card_id": "card-001-margin-of-safety",
                "model_id": "margin-of-safety",
                "disposition": "used",
                "effect_type": "guardrail",
                "affordance_ids_considered": [
                    "margin-of-safety.evidence-sized-operating-buffer"
                ],
                "merged_with_card_ids": [],
                "strongest_plausible_application": "The decision depends on an operating buffer.",
                "grounding_check": {
                    "case_quote": "buffer",
                    "evidence_status": "inferred_from_turn",
                    "missing_evidence": [],
                },
                "decision_reason": "The user-facing answer should gate action on buffer evidence.",
                "rejection_ground": "",
                "risk_if_forced": "",
                "residue": "",
                "final_answer_delta": "Add a buffer evidence gate.",
                "final_answer_visibility": "visible_caveat",
            }
        ],
        "summary": {
            "used_count": 1,
            "rejected_count": 0,
            "deferred_count": 0,
            "visible_delta_count": 1,
            "silent_delta_count": 0,
            "no_effect_count": 0,
        },
    }

    result = validate_arm_c_ledger_output(
        {"private_transaction_ledger": ledger},
        packet=packet,
    )

    assert result["status"] == "valid"
    assert result["transaction_count"] == 1


def test_delta_candidate_report_validation_accepts_trace_consistent_delta() -> None:
    packet = {
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "candidate_cards": [
            {
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "reviewed_affordance_cards": [
                    {"affordance_id": "optionality.sequence-preserving-choice"}
                ],
            }
        ],
    }
    ledger = {
        "ledger_version": "card_transaction_ledger.v1",
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "card_transactions": [
            {
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "disposition": "used",
                "effect_type": "counterframe",
                "affordance_ids_considered": [
                    "optionality.sequence-preserving-choice"
                ],
                "merged_with_card_ids": [],
                "strongest_plausible_application": "The user can sequence the choice.",
                "grounding_check": {
                    "case_quote": "wait",
                    "evidence_status": "inferred_from_turn",
                    "missing_evidence": [],
                },
                "decision_reason": "The public delta preserves a reversible option.",
                "rejection_ground": "",
                "risk_if_forced": "",
                "residue": "",
                "final_answer_delta": "Preserve the wait option until one buyer commits.",
                "final_answer_visibility": "visible_reframe",
            }
        ],
        "summary": {
            "used_count": 1,
            "rejected_count": 0,
            "deferred_count": 0,
            "visible_delta_count": 1,
            "silent_delta_count": 0,
            "no_effect_count": 0,
        },
    }
    payload = {
        "private_transaction_ledger": ledger,
        "delta_candidate_report": {
            "accepted_deltas": [
                {
                    "source_card_ids": ["card-001-optionality"],
                    "affordance_ids": ["optionality.sequence-preserving-choice"],
                    "public_delta_text": "Preserve the wait option until one buyer commits.",
                    "evidence_status": "inferred_from_turn",
                    "case_quote": "wait",
                    "why_user_should_care": "It avoids irreversible commitment.",
                    "confidence": "medium",
                }
            ],
            "deferred_questions": [],
            "risk_warnings": [],
            "rejected_cards": [],
            "no_delta_reason": "",
        },
    }

    result = validate_delta_candidate_report_output(payload, packet=packet)

    assert result == {
        "status": "valid",
        "accepted_delta_count": 1,
        "deferred_question_count": 0,
        "risk_warning_count": 0,
    }


def test_delta_candidate_report_validation_catches_private_language_and_trace_mismatch() -> None:
    packet = {
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "candidate_cards": [
            {
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "reviewed_affordance_cards": [
                    {"affordance_id": "optionality.sequence-preserving-choice"}
                ],
            }
        ],
    }
    ledger = {
        "ledger_version": "card_transaction_ledger.v1",
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "card_transactions": [
            {
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "disposition": "rejected",
                "effect_type": "no_effect",
                "affordance_ids_considered": [],
                "merged_with_card_ids": [],
                "strongest_plausible_application": "The user can sequence the choice.",
                "grounding_check": {
                    "case_quote": "",
                    "evidence_status": "not_needed",
                    "missing_evidence": [],
                },
                "decision_reason": "Already covered.",
                "rejection_ground": "duplicate_of_existing_pressure",
                "risk_if_forced": "Would add ceremony.",
                "residue": "",
                "final_answer_delta": "",
                "final_answer_visibility": "not_visible",
            }
        ],
        "summary": {
            "used_count": 0,
            "rejected_count": 1,
            "deferred_count": 0,
            "visible_delta_count": 0,
            "silent_delta_count": 0,
            "no_effect_count": 1,
        },
    }
    payload = {
        "private_transaction_ledger": ledger,
        "delta_candidate_report": {
            "accepted_deltas": [
                {
                    "source_card_ids": ["card-001-optionality"],
                    "affordance_ids": ["optionality.sequence-preserving-choice"],
                    "public_delta_text": "This affordance should change the answer.",
                    "evidence_status": "inferred_from_turn",
                }
            ],
            "deferred_questions": [],
            "risk_warnings": [],
            "rejected_cards": [],
            "no_delta_reason": "",
        },
    }

    result = validate_delta_candidate_report_output(payload, packet=packet)

    assert result["status"] == "invalid"
    assert any("private mechanism language" in error for error in result["errors"])
    assert any("non-used card transactions" in error for error in result["errors"])


def test_consideration_usefulness_validation_tracks_private_value_without_public_uptake() -> None:
    packet = {
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "candidate_cards": [
            {
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "reviewed_affordance_cards": [
                    {"affordance_id": "optionality.sequence-preserving-choice"}
                ],
            },
            {
                "card_id": "card-002-premortem",
                "model_id": "premortem",
                "reviewed_affordance_cards": [
                    {"affordance_id": "premortem.failure-first-stress-test"}
                ],
            },
        ],
    }
    payload = {
        "final_answer": "Keep the current revenue path while testing the new workflow demand.",
        "edge_findings": [],
        "consideration_usefulness_report": {
            "packet_usefulness": "mixed",
            "chunk_assessments": [
                {
                    "card_id": "card-001-optionality",
                    "model_id": "optionality",
                    "usefulness_to_consider": "high",
                    "opportunity_role": "frame_changer",
                    "route": "public_answer_delta",
                    "affordance_ids_considered": [
                        "optionality.sequence-preserving-choice"
                    ],
                    "what_it_helped_notice": "The choice can be sequenced.",
                    "why_not_used_publicly": "",
                    "evidence_status": "inferred_from_turn",
                },
                {
                    "card_id": "card-002-premortem",
                    "model_id": "premortem",
                    "usefulness_to_consider": "medium",
                    "opportunity_role": "guardrail",
                    "route": "private_reasoning",
                    "affordance_ids_considered": [
                        "premortem.failure-first-stress-test"
                    ],
                    "what_it_helped_notice": "Do not overstate demand evidence.",
                    "why_not_used_publicly": "The public answer already contains the test.",
                    "evidence_status": "not_needed",
                },
            ],
            "selected_opportunities": [
                {
                    "opportunity_id": "opp-1",
                    "route": "public_answer_delta",
                    "source_card_ids": ["card-001-optionality"],
                    "public_surface": "Test demand without abandoning current revenue.",
                    "private_value": "This changed the frame from pivot/no-pivot to sequencing.",
                }
            ],
            "retrieval_feedback": [],
            "no_public_delta_reason": "",
        },
    }

    result = validate_consideration_usefulness_output(payload, packet=packet)

    assert result == {
        "status": "valid",
        "assessment_count": 2,
        "selected_opportunity_count": 1,
        "packet_usefulness": "mixed",
    }


def test_consideration_usefulness_validation_catches_missing_assessments_and_leaks() -> None:
    packet = {
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "candidate_cards": [
            {
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "reviewed_affordance_cards": [
                    {"affordance_id": "optionality.sequence-preserving-choice"}
                ],
            }
        ],
    }
    payload = {
        "final_answer": "The affordance card says to use this model.",
        "consideration_usefulness_report": {
            "packet_usefulness": "good",
            "chunk_assessments": [
                {
                    "card_id": "card-999-missing",
                    "model_id": "premortem",
                    "usefulness_to_consider": "very",
                    "opportunity_role": "interesting",
                    "route": "private_reasoning",
                    "affordance_ids_considered": ["unknown"],
                    "what_it_helped_notice": "",
                    "why_not_used_publicly": "",
                    "evidence_status": "maybe",
                }
            ],
            "selected_opportunities": [
                {
                    "opportunity_id": "opp-1",
                    "route": "reject_duplicate",
                    "source_card_ids": ["card-999-missing"],
                    "public_surface": "Use the packet.",
                    "private_value": "",
                }
            ],
            "retrieval_feedback": [],
            "no_public_delta_reason": "",
        },
    }

    result = validate_consideration_usefulness_output(payload, packet=packet)

    assert result["status"] == "invalid"
    assert any("packet_usefulness is invalid" in error for error in result["errors"])
    assert any("chunk_assessments missing card IDs" in error for error in result["errors"])
    assert any("chunk_assessments contains unknown card IDs" in error for error in result["errors"])
    assert any("public output leaks private mechanism language" in error for error in result["errors"])


def test_delta_candidate_report_validation_can_enforce_c35_gate_rules() -> None:
    packet = {
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "candidate_cards": [
            {
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "reviewed_affordance_cards": [
                    {"affordance_id": "optionality.sequence-preserving-choice"}
                ],
            }
        ],
    }
    ledger = {
        "ledger_version": "card_transaction_ledger.v1",
        "packet_id": "packet",
        "status": "draft_review_only",
        "runtime_policy": "runtime_dormant",
        "card_transactions": [
            {
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "disposition": "used",
                "effect_type": "counterframe",
                "affordance_ids_considered": [
                    "optionality.sequence-preserving-choice"
                ],
                "merged_with_card_ids": [],
                "strongest_plausible_application": "The user can sequence the choice.",
                "grounding_check": {
                    "case_quote": "wait",
                    "evidence_status": "inferred_from_turn",
                    "missing_evidence": [],
                },
                "decision_reason": "The public delta preserves a reversible option.",
                "rejection_ground": "",
                "risk_if_forced": "",
                "residue": "",
                "final_answer_delta": "Preserve the wait option until one buyer commits.",
                "final_answer_visibility": "visible_reframe",
            }
        ],
        "summary": {
            "used_count": 1,
            "rejected_count": 0,
            "deferred_count": 0,
            "visible_delta_count": 1,
            "silent_delta_count": 0,
            "no_effect_count": 0,
        },
    }
    payload = {
        "private_transaction_ledger": ledger,
        "delta_candidate_report": {
            "accepted_deltas": [
                {
                    "delta_type": "analysis_note",
                    "source_card_ids": ["card-001-optionality"],
                    "affordance_ids": ["optionality.sequence-preserving-choice"],
                    "public_delta_text": "Add a payoff map for this decision.",
                    "evidence_status": "inferred_from_turn",
                    "case_quote": "",
                }
            ],
            "deferred_questions": [],
            "risk_warnings": [],
            "rejected_cards": [],
            "no_delta_reason": "",
        },
    }

    result = validate_delta_candidate_report_output(
        payload,
        packet=packet,
        require_public_delta_gate=True,
    )

    assert result["status"] == "invalid"
    assert any("delta_type is invalid" in error for error in result["errors"])
    assert any("analytical-framework shaped" in error for error in result["errors"])
    assert any("case_quote is required" in error for error in result["errors"])


def test_paid_replay_report_surfaces_public_delta_gate_counts() -> None:
    report = render_report(
        {
            "dry_run": False,
            "config": {"config_id": "cap8_focused"},
            "generator_model": "generator",
            "judge_model": "judge",
            "c_variant": "delta_gated",
            "aggregate": {
                "call_count": 3,
                "cost_usd": 0.01,
                "judge_winner_counts": {"B": 1},
                "ledger_validation_counts": {"valid": 1},
                "delta_validation_counts": {"invalid": 1},
                "public_delta_gate_counts": {
                    "accepted_delta_count": 1,
                    "collapse_to_b_count": 1,
                    "dropped_public_delta_count": 2,
                    "gate_enabled_items": 1,
                    "raw_accepted_delta_count": 3,
                },
                "public_delta_gate_drop_reasons": {
                    "analytical_framework_language": 1,
                    "not_directly_user_actionable": 1,
                },
            },
            "items": [
                {
                    "item_id": "case__edge_audit",
                    "candidate_model_ids": ["premortem"],
                    "suppressed_candidate_count": 10,
                    "ledger_validation": {"status": "valid"},
                    "judge": {"unblinded": {"winner": "B"}, "promotion_read": "retest"},
                }
            ],
        }
    )

    assert "Public delta gate" in report
    assert '"dropped_public_delta_count": 2' in report
    assert "analytical_framework_language" in report
