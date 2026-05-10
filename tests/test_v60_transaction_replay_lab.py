from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.card_transaction_ledger import validate_card_transaction_ledger_payload
from scripts.run_v60_transaction_replay_lab import (
    LAB_VERSION,
    main as run_v60_replay_lab_main,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_v60_replay_lab_dry_run_builds_grouped_packets_and_ledgers(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    manifest_path = tmp_path / "cases.json"
    output_dir = tmp_path / "out"
    _write_json(
        result_path,
        {
            "query": "Should the founder grant equity now?",
            "vanilla_answer": "Grant equity if retention risk is high.",
            "delta_card": {
                "selected_model_ids": ["opportunity-cost"],
                "findings": [
                    {
                        "tendency_id": "availability-misweighing-tendency",
                        "specific_passage": "retention risk is high",
                        "selected_model_ids": ["base-rates", "opportunity-cost"],
                    }
                ],
            },
            "companion_cheat_sheet": {
                "anchors": [
                    {
                        "model_id": "optionalty-typo",
                        "presence_explanation": "Deliberate missing model control.",
                        "evidence_quote": "retention risk",
                    }
                ]
            },
            "frame_pressure_card": {
                "reframings": [
                    {
                        "grounding_model": "inversion",
                        "reframed_question": "What would make this grant fail?",
                        "what_opens": "Failure-mode review.",
                    }
                ]
            },
            "structural_coverage_card": {
                "gap_routes": [
                    {
                        "dimension_id": "resource-allocation",
                        "dimension_name": "Resource Allocation",
                        "candidate_model_ids": ["batna", "base-rates"],
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
                    "case_id": "founder-equity-test",
                    "result_path": str(result_path),
                    "include_reason": "Synthetic test case for dry-run packet assembly.",
                    "risk_notes": ["Do not infer product-readiness from this fixture."],
                    "tags": ["decision-under-uncertainty", "negotiation"],
                }
            ],
        },
    )

    assert (
        run_v60_replay_lab_main(
            [
                "--case-manifest",
                str(manifest_path),
                "--output-dir",
                str(output_dir),
                "--affordances-path",
                str(REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v60.json"),
                "--dry-run",
            ]
        )
        == 0
    )

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["dry_run"] is True
    assert summary["case_count"] == 1
    assert summary["provider_plan"]["generator_model"] == "x-ai/grok-4.1-fast"
    assert summary["provider_plan"]["judge_model"] == "moonshotai/kimi-k2.6"
    assert summary["provider_plan"]["paid_calls_made"] is False

    packet = json.loads(
        (output_dir / "packets" / "founder-equity-test.json").read_text(encoding="utf-8")
    )
    assert packet["status"] == "draft_review_only"
    assert packet["runtime_policy"] == "runtime_dormant"
    assert "affordances_v60.json" in packet["source_artifacts"][1]
    reviewed_cards = [
        card for card in packet["candidate_cards"] if card["reviewed_affordance_cards"]
    ]
    assert reviewed_cards
    assert reviewed_cards[0]["reviewed_affordance_cards"][0]["affordance_id"]

    ledger = json.loads(
        (output_dir / "ledger_templates" / "founder-equity-test.json").read_text(
            encoding="utf-8"
        )
    )
    assert ledger["dry_run_placeholder"] is True
    validate_card_transaction_ledger_payload(ledger, packet=packet)

    arm_c = json.loads(
        (output_dir / "arms" / "arm_c" / "founder-equity-test.json").read_text(
            encoding="utf-8"
        )
    )
    assert arm_c["arm"] == "C"
    arm_c_packet = arm_c["user_packet"]["reasoning_substrate_packet"]
    assert arm_c_packet["packet_id"] == packet["packet_id"]
    assert arm_c_packet["view"] == "decoder_compact_v1"
    assert "runtime_graph_fields" not in arm_c_packet["candidate_cards"][0]
    assert "reviewed_affordance_fields" not in arm_c_packet["candidate_cards"][0]
    assert summary["cases"][0]["token_estimates"]["arm_c_packet_view"] < (
        summary["cases"][0]["token_estimates"]["packet"]
    )
    report = (output_dir / "preflight_report.md").read_text(encoding="utf-8")
    assert "Architecture Read" in report
    assert "User Read" in report
    assert "Product Read" in report
    assert "Monetization Read" in report


def test_v60_replay_lab_requires_explicit_v60_artifact(tmp_path: Path) -> None:
    manifest_path = tmp_path / "cases.json"
    _write_json(
        manifest_path,
        {
            "lab_version": LAB_VERSION,
            "cases": [{"case_id": "case", "query": "Q", "vanilla_answer": "A"}],
        },
    )

    try:
        run_v60_replay_lab_main(
            [
                "--case-manifest",
                str(manifest_path),
                "--affordances-path",
                str(REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v59.json"),
                "--dry-run",
            ]
        )
    except Exception as exc:
        assert "affordances_v60.json" in str(exc)
    else:
        raise AssertionError("expected explicit v60 artifact failure")
