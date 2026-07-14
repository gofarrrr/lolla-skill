from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/lolla-r4-separated-surface-experiment-v1-execution-2026-07-14-a2"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_raw_execution_a2_is_complete_final_run_custody() -> None:
    result = _load(OUTPUT / "result.json")
    manifest = _load(OUTPUT / "raw-evidence-manifest.json")
    consumption = _load(OUTPUT / "authorization-consumption.json")

    assert result["status"] == "complete"
    assert result["provider_calls"] == 12
    assert result["call_ordinals"] == list(range(1, 13))
    assert [row["operational_status"] for row in result["call_results"]] == ["completed"] * 12
    assert [row["finish_reason"] for row in result["call_results"]] == ["stop"] * 12
    assert result["first_failure_stopped_further_transport"] is False
    assert result["automatic_retries"] == 0
    assert result["semantic_retries"] == 0
    assert result["fallback_models"] == 0
    assert result["model_substitutions"] == 0
    assert result["response_healing"] is False

    assert consumption["status"] == "consumed_complete_final_execution"
    assert consumption["authorization_instance"] == "lolla-r4-separated-surface-experiment-v1-a2"
    assert consumption["founder_authorization_type"] == "new final full-execution authorization"
    assert consumption["authorization_sha256"] == "e41321fec40af572ae643af73cb6a04a7624756d84c723b0c09bcb2829450edf"
    assert consumption["previous_a1_authorization"] == "consumed_and_not_reusable"
    assert consumption["a2_authorization"] == "separately_issued_one_use_final_permitted_execution"
    assert consumption["third_execution_authorized"] is False

    assert manifest["provider_calls"] == 12
    assert manifest["completed_calls"] == 12
    assert manifest["failed_ordinal"] is None
    assert manifest["unattempted_ordinals"] == []
    for row in manifest["files"]:
        artifact = OUTPUT / row["path"]
        assert artifact.is_file()
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == row["sha256"]
        assert len(artifact.read_bytes()) == row["bytes"]
