from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/evals/validate_stage0_public_handoff.py"
PACKET_PATH = ROOT / "docs/evals/lolla-stage0-public-handoff-cold-reader-answers-v1.json"


def _load_validator():
    spec = importlib.util.spec_from_file_location("stage0_public_handoff_validator", VALIDATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_public_handoff_validates_from_cli() -> None:
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    receipt = json.loads(completed.stdout)
    assert receipt["status"] == "valid"
    assert receipt["cold_reader_question_count"] == 10
    assert receipt["current_entrypoint_count"] == 6
    assert receipt["required_file_count"] == 16
    assert receipt["local_link_count"] >= 50
    assert receipt["provider_calls"] == 0
    assert receipt["provider_cost_usd"] == 0.0


def test_public_handoff_rejects_stale_root_claim() -> None:
    validator = _load_validator()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    errors, receipt = validator.validate(
        ROOT,
        text_overrides={"README.md": readme + "\nThe architecture is sound.\n"},
    )

    assert receipt["status"] == "invalid"
    assert "forbidden stale public claim: architecture is sound" in errors


def test_public_handoff_rejects_provider_activity_and_question_drift() -> None:
    validator = _load_validator()
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    candidate = copy.deepcopy(packet)
    candidate["provider_calls"] = 1
    candidate["provider_cost_usd"] = 0.01
    candidate["questions"] = candidate["questions"][:-1]

    errors, receipt = validator.validate(ROOT, packet_override=candidate)

    assert receipt["status"] == "invalid"
    assert "cold-reader provider_calls must be 0" in errors
    assert "cold-reader provider_cost_usd must be 0.00" in errors
    assert "cold-reader questions must match the ten-question orientation contract" in errors


def test_current_entrypoint_links_resolve() -> None:
    validator = _load_validator()
    errors, receipt = validator.validate(ROOT)

    assert not [error for error in errors if "link" in error], errors
    assert receipt["local_link_count"] >= 50


def test_historical_discoverability_is_not_pinned_to_root_product_docs() -> None:
    historical_tests = tuple(
        path
        for path in (ROOT / "tests").glob("test_*.py")
        if path != Path(__file__)
        if "docs/history/decision-work-product-delta-discoverability.md"
        in path.read_text(encoding="utf-8")
    )

    assert len(historical_tests) == 60
    for path in historical_tests:
        text = path.read_text(encoding="utf-8")
        assert 'README_PATH = REPO_ROOT / "README.md"' not in text
        assert 'HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"' not in text
        assert "HISTORICAL_DISCOVERY_PATH" in text
