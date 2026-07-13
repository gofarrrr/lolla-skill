from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts.evals import run_user_counterpressure_preflight as preflight


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_preflight_contract_locks_one_reader_and_unchanged_sk3_control(
    tmp_path: Path,
) -> None:
    contract = preflight.build_contract(
        manifest_path=preflight.DEFAULT_MANIFEST,
        output_dir=tmp_path,
    )

    assert contract["case_id"] == "case-08-oncologist-career-family"
    assert contract["contract_status"] == "prepared_no_calls_executed"
    assert contract["repeat_count"] == 3
    assert contract["successful_call_budget"] == 3
    assert contract["probabilistic_job"]["reader_calls_per_repeat"] == 1
    assert contract["probabilistic_job"]["allowed_kinds"] == [
        "material_qualification",
        "premise_correction",
        "reasoning_objection",
    ]
    assert contract["control"]["rerun_other_readers"] is False
    assert contract["control"]["modify_baseline_artifacts"] is False
    assert len(contract["control"]["baseline_artifacts"]) == 3
    assert contract["deterministic_job"]["must_not_infer_semantic_role"] is True
    assert contract["gate"]["pass_authorizes"] == (
        "three-case pressure-only ablation"
    )
    assert "SK4 promotion" in contract["gate"]["pass_does_not_authorize"]
    assert len(contract["locked_gold_pressure_observations"]) == 1


def test_default_command_writes_contract_without_loading_a_provider(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_user_counterpressure_preflight.py",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert preflight.main() == 0

    contract_path = tmp_path / "preflight-contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    assert contract["contract_status"] == "prepared_no_calls_executed"
    assert not list(tmp_path.glob("counterpressure-*.json"))
    assert not (tmp_path / "preflight-result.json").exists()
