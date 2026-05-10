from __future__ import annotations

import json
from pathlib import Path

from scripts.run_v60_transaction_replay_lab import LAB_VERSION
from scripts.run_v60_transaction_replay_matrix import main as run_matrix_main


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_v60_transaction_matrix_compares_configurations_without_model_calls(
    tmp_path: Path,
) -> None:
    result_path = tmp_path / "result.json"
    manifest_path = tmp_path / "cases.json"
    output_dir = tmp_path / "matrix"
    _write_json(
        result_path,
        {
            "query": "Which strategic option should we choose?",
            "vanilla_answer": "Choose the option with the clearest upside.",
            "delta_card": {
                "selected_model_ids": [
                    "opportunity-cost",
                    "base-rates",
                    "inversion",
                    "batna",
                    "systems-thinking",
                    "principal-agent-problem",
                ],
            },
        },
    )
    _write_json(
        manifest_path,
        {
            "lab_version": LAB_VERSION,
            "cases": [
                {
                    "case_id": "matrix-test",
                    "result_path": str(result_path),
                    "include_reason": "Matrix test case.",
                    "risk_notes": ["Synthetic test only."],
                    "tags": ["decision-under-uncertainty"],
                }
            ],
        },
    )

    assert (
        run_matrix_main(
            [
                "--case-manifest",
                str(manifest_path),
                "--output-dir",
                str(output_dir),
                "--affordances-path",
                str(REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v60.json"),
                "--config-id",
                "cap4_tiny",
                "--dry-run",
            ]
        )
        == 0
    )

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["dry_run"] is True
    assert summary["config_count"] == 1
    assert summary["configs"][0]["config_id"] == "cap4_tiny"
    assert summary["configs"][0]["aggregate"]["cases_with_suppression"] == 1
    assert summary["configs"][0]["cases"][0]["token_estimates"]["arm_c_modes"]
    assert summary["configs"][0]["cases"][0]["requirements_flags"]

    report = (output_dir / "matrix_report.md").read_text(encoding="utf-8")
    assert "Configuration Summary" in report
    assert "Requirement Signals" in report
    assert "Case Pressure" in report
