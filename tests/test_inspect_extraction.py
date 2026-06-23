from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "inspect_extraction.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("inspect_extraction", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_summarize_extraction_payload_unwraps_run_extract_envelope() -> None:
    module = _load_module()
    summary = module.summarize_extraction_payload(
        {
            "status": "ok",
            "capture_health": "good",
            "capture_manifest": {
                "actual_user_turns": 2,
                "actual_assistant_turns": 2,
                "char_length": 1234,
            },
            "extraction": {
                "decision_situation": "Whether to take the startup role",
                "reasoning_passages": ["If wife conversation goes well, take B."],
                "live_constraints": [{"constraint": "7-day deadline"}],
                "dropped_threads": [],
                "turns": [{"speaker": "user"}, {"speaker": "assistant"}],
            },
        }
    )

    assert summary["extraction_source_path"] == "$.extraction"
    assert summary["has_nested_extraction"] is True
    assert summary["decision_situation"] == "Whether to take the startup role"
    assert summary["reasoning_passage_count"] == 1
    assert summary["live_constraint_count"] == 1
    assert summary["turn_count"] == 2
    assert summary["capture_manifest"]["actual_user_turns"] == 2


def test_summarize_extraction_payload_accepts_legacy_top_level_shape() -> None:
    module = _load_module()
    summary = module.summarize_extraction_payload(
        {
            "decision_situation": "Legacy decision",
            "reasoning_passages": ["Only pivot after evidence."],
            "live_constraints": [],
        }
    )

    assert summary["extraction_source_path"] == "$"
    assert summary["has_nested_extraction"] is False
    assert summary["decision_situation"] == "Legacy decision"
    assert summary["reasoning_passage_count"] == 1


def test_inspect_extraction_cli_prints_nested_counts(tmp_path: Path) -> None:
    extraction_path = tmp_path / "extraction.json"
    extraction_path.write_text(
        json.dumps(
            {
                "status": "ok",
                "extraction": {
                    "decision_situation": "Nested decision",
                    "reasoning_passages": ["A"],
                    "live_constraints": ["B"],
                },
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(extraction_path)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "extraction_source_path: $.extraction" in result.stdout
    assert "decision_situation: Nested decision" in result.stdout
    assert "reasoning_passages: 1" in result.stdout
    assert "live_constraints: 1" in result.stdout
