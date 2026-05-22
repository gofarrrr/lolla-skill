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


def test_archive_run_copies_pre_step6_shadow_portfolio_sidecar(tmp_path: Path) -> None:
    run_id = "shadowcopy"
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
                "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
                "v60_enrichment": {"status": "disabled"},
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_pre_step6_shadow_portfolio.json").write_text(
        json.dumps(
            {
                "schema_version": "pre_step6_shadow_portfolio.v1",
                "status": "shadow_cache_miss",
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_pre_step6_private_table.json").write_text(
        json.dumps(
            {
                "schema_version": "pre_step6_private_table.v1",
                "status": "ready",
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_pre_step6_private_table.md").write_text(
        "# Pre-Step-6 Private Thinking Table\n",
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_pre_step6_private_table_ledger.json").write_text(
        json.dumps(
            {
                "schema_version": "pre_step6_private_table_ledger.v1",
                "status": "completed",
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

    run_dir = Path(archived["run_dir"])
    assert "pre_step6_shadow_portfolio.json" in archived["files_copied"]
    assert "pre_step6_private_table.json" in archived["files_copied"]
    assert "pre_step6_private_table.md" in archived["files_copied"]
    assert "pre_step6_private_table_ledger.json" in archived["files_copied"]
    assert (run_dir / "pre_step6_shadow_portfolio.json").exists()
    assert (run_dir / "pre_step6_private_table.json").exists()
    assert (run_dir / "pre_step6_private_table.md").exists()
    assert (run_dir / "pre_step6_private_table_ledger.json").exists()


def test_archive_run_records_product_output_hygiene_before_copy(tmp_path: Path) -> None:
    run_id = "hygiene"
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
                "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
                "v60_enrichment": {"status": "disabled"},
                "revised_answer": "Ask for a sharper evidence gate.",
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_revised.txt").write_text(
        "This V60 chunk should change the answer.",
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_memo.md").write_text(
        "# Decision note\n\nThis point survived independent review.",
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
    assert archived_result["run_health"]["product_output_health"] == "unsafe"
    assert archived_result["run_health"]["product_output_leak_count"] >= 3
    assert "product_output_leak" in archived_result["run_health"]["issues"]
    leak_surfaces = {
        leak["surface"]
        for leak in archived_result["run_health"]["product_output_leaks"]
    }
    assert {"revised_txt", "memo_markdown"}.issubset(leak_surfaces)


def test_archive_run_records_unsafe_live_transcript_before_copy(tmp_path: Path) -> None:
    run_id = "liveunsafe"
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
                "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
                "v60_enrichment": {"status": "disabled"},
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_live_transcript.txt").write_text(
        "Beat 2 is done. Now launching pressure-check agents.",
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
    assert archived_result["run_health"]["live_output_health"] == "unsafe"
    assert archived_result["run_health"]["live_output_leak_count"] >= 2
    assert "live_output_leak" in archived_result["run_health"]["issues"]
    leak_surfaces = {
        leak["surface"]
        for leak in archived_result["run_health"]["live_output_leaks"]
    }
    assert leak_surfaces == {"live_narration"}


def test_archive_run_records_manual_clean_live_transcript_as_not_checked_before_copy(tmp_path: Path) -> None:
    run_id = "liveunchecked"
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
                "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
                "v60_enrichment": {"status": "disabled"},
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_live_transcript.txt").write_text(
        "I have the counterargument; I am folding it into the revised answer now.",
        encoding="utf-8",
    )

    archive_run = _load_archive_run_module()
    archived = archive_run.archive_run(
        run_id,
        archive_root=archive_root,
        tmp_dir=tmp_dir,
    )

    archived_result = json.loads((Path(archived["run_dir"]) / "result.json").read_text())
    assert archived_result["run_health"]["overall"] == "healthy"
    assert archived_result["run_health"]["live_output_health"] == "not_checked"
    assert archived_result["run_health"]["live_output_leak_count"] == 0
    assert archived_result["run_health"]["live_output_leaks"] == []
    assert archived_result["live_output_hygiene"]["status"] == "not_checked"
    assert archived_result["live_output_hygiene"]["transcript_status"] == "clean"
    assert archived_result["live_output_hygiene"]["capture_mode"] == "manual_unverified"


def test_archive_run_preserves_trusted_clean_live_transcript_before_copy(tmp_path: Path) -> None:
    from engine.system_b.output_hygiene import finalize_live_output_hygiene

    run_id = "livetrusted"
    tmp_dir = tmp_path / "tmp"
    archive_root = tmp_path / "archive"
    tmp_dir.mkdir()
    transcript = "I have the counterargument; I am folding it into the revised answer now."

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
    finalized_result = finalize_live_output_hygiene(
        {
            "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
            "v60_enrichment": {"status": "disabled"},
        },
        transcript,
        trusted_capture=True,
        require_live_output_clean=True,
    )
    (tmp_dir / f"lolla_{run_id}_result.json").write_text(
        json.dumps(finalized_result),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_live_transcript.txt").write_text(
        transcript,
        encoding="utf-8",
    )

    archive_run = _load_archive_run_module()
    archived = archive_run.archive_run(
        run_id,
        archive_root=archive_root,
        tmp_dir=tmp_dir,
    )

    archived_result = json.loads((Path(archived["run_dir"]) / "result.json").read_text())
    assert archived_result["run_health"]["overall"] == "healthy"
    assert archived_result["run_health"]["live_output_health"] == "clean"
    assert archived_result["live_output_hygiene"]["status"] == "clean"
    assert archived_result["live_output_hygiene"]["capture_mode"] == "trusted"


def test_archive_run_flags_orchestrator_notice_in_live_transcript_before_copy(tmp_path: Path) -> None:
    run_id = "liveorchestrator"
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
                "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
                "v60_enrichment": {"status": "disabled"},
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_live_transcript.txt").write_text(
        "Orchestrator: Sonnet — phrasing quality may be mildly degraded vs Opus "
        "(see Model Requirements).",
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
    assert archived_result["run_health"]["live_output_health"] == "unsafe"
    leaked_terms = {
        leak["term"]
        for leak in archived_result["run_health"]["live_output_leaks"]
    }
    assert {"orchestrator", "Model Requirements"}.issubset(leaked_terms)


def test_archive_run_records_missing_live_transcript_without_degrading(tmp_path: Path) -> None:
    run_id = "livemissing"
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
                "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
                "v60_enrichment": {"status": "disabled"},
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
    assert archived_result["run_health"]["overall"] == "healthy"
    assert archived_result["run_health"]["live_output_health"] == "missing"
    assert archived_result["run_health"]["live_output_leak_count"] == 0
    assert archived_result["run_health"]["live_output_leaks"] == []
    assert "live_output_missing" not in archived_result["run_health"]["issues"]
    assert archived_result["live_output_hygiene"]["status"] == "missing"
