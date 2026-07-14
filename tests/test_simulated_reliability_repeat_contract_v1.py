from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

from scripts.evals.run_simulated_reliability_case_v1 import load_contract


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/evals/simulated-reliability-v1-repeat-contract-v1.json"


def test_repeat_contract_inherits_exact_v1_runtime_and_authorizes_no_call_yet() -> None:
    raw = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    merged = load_contract(CONTRACT_PATH)
    assert raw["activation_prerequisites"]["provider_calls_currently_authorized"] == 0
    assert raw["activation_prerequisites"]["explicit_founder_cost_decision_required"] is True
    assert merged["provider_request"]["model"] == "google/gemini-3.5-flash-20260519"
    assert merged["transfer"]["repeat_ids"] == ["repeat_2"]
    assert merged["seeds"]["repeat_2"] == 202
    assert merged["transfer"]["automatic_retries"] == 0
    assert merged["transfer"]["maximum_provider_calls"] == 18
    assert raw["stability_comparison"]["scalar_stability_score"] is None


def test_repeat_selection_is_hash_minimum_per_prospective_stratum() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / contract["selection"]["source"]).read_text(encoding="utf-8"))
    source_review = json.loads(
        (ROOT / contract["selection"]["strata_source"]).read_text(encoding="utf-8")
    )
    assert hashlib.sha256((ROOT / contract["selection"]["source"]).read_bytes()).hexdigest() == contract["selection"]["source_sha256"]
    assert hashlib.sha256((ROOT / contract["selection"]["strata_source"]).read_bytes()).hexdigest() == contract["selection"]["strata_source_sha256"]

    behavior = {row["case_id"]: row["expected_public_behavior"] for row in source_review["cases"]}
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in manifest["transfer_cases"]:
        groups[behavior[row["case_id"]]].append(row)
    expected = {
        stratum: min(rows, key=lambda row: row["sha256"])["case_id"]
        for stratum, rows in groups.items()
    }
    observed = {
        row["expected_public_behavior"]: row["case_id"]
        for row in contract["selection"]["selected"]
    }
    assert observed == expected
