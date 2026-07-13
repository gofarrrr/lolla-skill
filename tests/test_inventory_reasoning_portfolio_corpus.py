from __future__ import annotations

import json
from pathlib import Path

from scripts.evals.inventory_reasoning_portfolio_corpus import build_inventory


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def _complete_run(root: Path) -> Path:
    run = root / "case-a" / "run-1"
    run.mkdir(parents=True)
    _write_json(
        run / "graph_survival_report.json",
        {
            "schema_version": "graph.v0",
            "status": "ready",
            "candidate_survival": [
                {
                    "model_id": "alpha",
                    "survival_state": "answer_delta",
                    "selected_for_v60": True,
                },
                {
                    "model_id": "beta",
                    "survival_state": "suppressed_by_packet_cap",
                    "selected_for_v60": False,
                },
            ],
        },
    )
    _write_json(
        run / "pre_step6_private_table.json",
        {
            "schema_version": "table.v1",
            "status": "ready",
            "table_char_count": 1200,
            "table_section_count": 4,
            "source_items": [{"source_id": "one"}, {"source_id": "two"}],
            "cache": {"state": "cache_miss"},
        },
    )
    _write_json(
        run / "pre_step6_private_table_ledger.json",
        {
            "schema_version": "table-ledger.v1",
            "status": "completed",
            "items": [{"disposition": "used"}, {"disposition": "rejected"}],
        },
    )
    _write_json(
        run / "v60_ledger.json",
        {
            "schema_version": "v60-ledger.v1",
            "status": "completed",
            "transactions": [{"disposition": "private_guardrail"}],
        },
    )
    (run / "revised.txt").write_text("revised answer", encoding="utf-8")
    return run


def test_inventory_is_metadata_only_and_counts_complete_live_surface(
    tmp_path: Path,
) -> None:
    _complete_run(tmp_path)
    inventory = build_inventory(tmp_path)
    assert inventory["run_count"] == 1
    assert inventory["eligible_run_count"] == 1
    assert inventory["model_calls"] == 0
    run = inventory["runs"][0]
    assert run["case_id"] == "case-a"
    assert run["run_id"] == "run-1"
    assert run["raw_text_included"] is False
    assert run["absolute_paths_included"] is False
    assert run["graph"]["candidate_count"] == 2
    assert run["graph"]["selected_for_v60_count"] == 1
    assert run["private_table"]["source_item_count"] == 2
    assert run["private_table_ledger"]["disposition_counts"] == {
        "rejected": 1,
        "used": 1,
    }
    assert run["v60_ledger"]["disposition_counts"] == {
        "private_guardrail": 1
    }


def test_inventory_keeps_missing_run_visible_without_reading_content(
    tmp_path: Path,
) -> None:
    run = tmp_path / "case-b" / "run-2"
    run.mkdir(parents=True)
    (run / "revised.txt").write_text("partial", encoding="utf-8")
    inventory = build_inventory(tmp_path)
    assert inventory["eligible_run_count"] == 0
    result = inventory["runs"][0]
    assert result["eligibility"] == "ineligible_missing_artifacts"
    assert "graph_survival_report.json" in result["missing_artifacts"]
    assert "revised_answer_character_count" not in result


def test_inventory_rejects_noncompleted_ledgers(tmp_path: Path) -> None:
    run = _complete_run(tmp_path)
    ledger = json.loads(
        (run / "v60_ledger.json").read_text(encoding="utf-8")
    )
    ledger["status"] = "pending"
    _write_json(run / "v60_ledger.json", ledger)
    inventory = build_inventory(tmp_path)
    assert inventory["runs"][0]["eligibility"] == "ineligible_incomplete_custody"
