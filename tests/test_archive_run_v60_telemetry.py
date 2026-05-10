from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_RUN_PATH = REPO_ROOT / "scripts" / "archive_run.py"


def _load_archive_run_module():
    spec = importlib.util.spec_from_file_location("archive_run", ARCHIVE_RUN_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_archive_run_marks_active_v60_missing_ledger_before_copy(tmp_path: Path) -> None:
    run_id = "testrun"
    tmp_dir = tmp_path / "tmp"
    archive_root = tmp_path / "archive"
    tmp_dir.mkdir()

    (tmp_dir / f"lolla_{run_id}_extraction.json").write_text(
        json.dumps(
            {
                "extraction": {
                    "decision_situation": "Founder deciding whether to pivot",
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_result.json").write_text(
        json.dumps(
            {
                "run_health": {"overall": "healthy", "issues": []},
                "v60_enrichment": {
                    "status": "active",
                    "telemetry": {
                        "selected_chunk_ids": [
                            "aff::optionality.expand-before-evaluating",
                            "abs::optionality::option-name-as-real-option",
                        ]
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    archive_run = _load_archive_run_module()
    archived = archive_run.archive_run(
        run_id,
        archive_root=archive_root,
        tmp_dir=tmp_dir,
    )

    archived_result = json.loads((Path(archived["run_dir"]) / "result.json").read_text())
    assert archived_result["run_health"]["overall"] == "degraded"
    assert archived_result["run_health"]["v60_consideration_ledger"] == "missing"
    assert archived_result["run_health"]["v60_unaccounted_chunk_count"] == 2
    assert "v60_consideration_ledger_missing" in archived_result["run_health"]["issues"]
    assert archived_result["v60_consideration_validation"]["status"] == "missing"
