from __future__ import annotations

import hashlib
import json
from pathlib import Path

from engine.system_b.core_semantic_shadow import (
    USER_COUNTERPRESSURE_KINDS,
    USER_COUNTERPRESSURE_SYSTEM_PROMPT,
    USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    REPO_ROOT
    / "research/core-semantic-sk4-counterpressure-v21-temporal-preflight-2026-07-10/preflight-contract.json"
)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_temporal_preflight_contract_is_frozen_to_local_prompt_and_sources() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    prompt = contract["prompt_contract"]

    assert contract["contract_status"] == "prepared_no_calls_executed"
    assert contract["case_id"] == "case-08-oncologist-career-family"
    assert contract["successful_call_budget"] == 3
    assert prompt["change_type"] == "temporal_addendum_only"
    assert prompt["frozen_v2_prompt_sha256"] == _sha256_text(
        USER_COUNTERPRESSURE_SYSTEM_PROMPT
    )
    assert prompt["v21_temporal_prompt_sha256"] == _sha256_text(
        USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT
    )
    assert prompt["v21_temporal_prompt_character_count"] == len(
        USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT
    )
    assert prompt["allowed_kinds"] == sorted(USER_COUNTERPRESSURE_KINDS)
    assert prompt["new_output_fields"] == []

    source = REPO_ROOT / contract["source"]["conversation_path"]
    assert contract["source"]["conversation_sha256"] == _sha256_path(source)
    scoring = contract["temporal_scoring_contract"]
    assert scoring["sha256"] == _sha256_path(REPO_ROOT / scoring["path"])
    assert scoring["frozen_before_future_calls"] is True
    assert scoring["semantic_runtime_judge_allowed"] is False
    assert contract["deterministic_contract"]["changed_from_v2"] is False
    assert contract["control"]["rerun_other_readers"] is False
    assert contract["control"]["modify_baseline_artifacts"] is False
