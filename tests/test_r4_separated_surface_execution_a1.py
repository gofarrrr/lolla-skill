from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/lolla-r4-separated-surface-experiment-v1-execution-2026-07-14-a1"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_raw_execution_a1_is_terminal_first_failure_custody() -> None:
    result = _load(OUTPUT / "result.json")
    manifest = _load(OUTPUT / "raw-evidence-manifest.json")
    consumption = _load(OUTPUT / "authorization-consumption.json")

    assert result["status"] == "stopped_on_first_failure"
    assert result["provider_calls"] == 7
    assert result["call_ordinals"] == list(range(1, 8))
    assert [row["operational_status"] for row in result["call_results"][:6]] == ["completed"] * 6
    assert result["call_results"][6]["operational_status"] == "terminal_validation_failure"
    assert result["call_results"][6]["finish_reason"] == "error"
    assert result["first_failure_stopped_further_transport"] is True
    assert not any(OUTPUT.glob("call-08-*"))
    assert result["automatic_retries"] == 0
    assert result["semantic_retries"] == 0
    assert result["fallback_models"] == 0
    assert result["model_substitutions"] == 0
    assert result["response_healing"] is False

    assert consumption["status"] == "consumed_terminal_first_failure"
    assert consumption["authorization_sha256"] == "e41321fec40af572ae643af73cb6a04a7624756d84c723b0c09bcb2829450edf"
    assert consumption["provider_calls"] == 7
    assert consumption["second_execution_authorized"] is False

    for row in manifest["files"]:
        artifact = OUTPUT / row["path"]
        assert artifact.is_file()
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == row["sha256"]
        assert len(artifact.read_bytes()) == row["bytes"]
    assert manifest["provider_calls"] == 7
    assert manifest["completed_calls"] == 6
    assert manifest["failed_ordinal"] == 7
