from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/evals/validate_constitution_stage0_addendum_register.py"
REGISTER = ROOT / "docs/evals/lolla-constitution-stage0-addendum-register-v1.json"


def test_canonical_stage0_register_validates() -> None:
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR), "--register", str(REGISTER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    receipt = json.loads(completed.stdout)
    assert receipt == {
        "component_count": 25,
        "connection_count": 24,
        "constitution_rule_count": 17,
        "decision_trail_field_group_count": 26,
        "implementation_file_count": 674,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "schema_version": "lolla.constitution_stage0_addendum_validation.v1",
        "status": "valid",
    }


def test_register_rejects_active_r4_and_nonzero_provider_boundary(tmp_path: Path) -> None:
    payload = json.loads(REGISTER.read_text(encoding="utf-8"))
    r4 = next(component for component in payload["components"] if component["id"] == "r4_incremental_readers")
    r4["disposition"] = "keep_active"
    payload["provider_calls"] = 1
    candidate = tmp_path / "invalid.json"
    candidate.write_text(json.dumps(payload), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(VALIDATOR), "--register", str(candidate)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "R4 readers cannot be active" in completed.stderr
    assert "provider_calls must be 0" in completed.stderr
