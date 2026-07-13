from __future__ import annotations

import json
from pathlib import Path

from scripts.evals.run_conversation_state_microtask_probe_v4 import (
    build_repaired_micro_contract,
    validate_authorization,
    validate_contract,
)
from scripts.evals import run_conversation_state_microtask_probe as v1


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = [
    ROOT / "research/conversation-state-microtask-transfer-case01-v4-2026-07-11",
    ROOT / "research/conversation-state-microtask-transfer-case04-v4-2026-07-11",
]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_transfer_contracts_are_frozen_under_one_generic_repair_round() -> None:
    for package in PACKAGES:
        contract_path = package / "contract.json"
        contract = _load(contract_path)
        validate_contract(contract)
        assert contract["repair_round"]["round"] == 1
        assert contract["repair_round"]["maximum_rounds"] == 1
        assert contract["repair_round"]["case_specific_language"] is False
        assert contract["repair_round"]["thresholds_changed"] is False
        validate_authorization(
            _load(package / "call-authorization.json"),
            contract_path=contract_path,
            contract=contract,
        )


def test_repair_prompts_are_generic_and_keep_source_id_admission() -> None:
    contract = _load(PACKAGES[0] / "contract.json")
    catalog = v1._catalog(contract)
    constraints = build_repaired_micro_contract("constraints", catalog=catalog)
    positions = build_repaired_micro_contract("positions", catalog=catalog)
    threads = build_repaired_micro_contract("threads", catalog=catalog)
    assert "sweep every user turn" in constraints["system_prompt"]
    assert "assistant suggestion" in constraints["system_prompt"]
    assert "one composed focal current direction" in positions["system_prompt"]
    assert "final turn backward" in threads["system_prompt"]
    for micro in (constraints, positions, threads):
        span_ids = micro["schema"]["$defs"]["EvidenceRef"]["properties"][
            "span_id"
        ]["enum"]
        assert span_ids
        assert all(value.startswith("span-") for value in span_ids)
        assert "Willow" not in micro["system_prompt"]
        assert "Mara" not in micro["system_prompt"]
