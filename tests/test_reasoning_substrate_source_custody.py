from __future__ import annotations

from pathlib import Path

import pytest

from engine.system_b.source_custody import (
    DEFAULT_CANONICAL_SOURCE_DIR,
    build_source_custody_report,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_source_custody_manifest_covers_all_runtime_models() -> None:
    report = build_source_custody_report(REPO_ROOT)

    assert report["runtime_model_count"] == 222
    assert report["manifest_model_count"] == 222
    assert report["manifest_file_count"] == 222
    assert report["missing_manifest_model_ids"] == []
    assert report["manifest_model_ids_outside_runtime_graph"] == []
    assert report["source_file_mismatch_model_ids"] == []


def test_source_custody_files_exist_and_match_manifest_hashes() -> None:
    report = build_source_custody_report(REPO_ROOT)

    assert report["missing_local_source_model_ids"] == []
    assert report["local_sha256_mismatch_model_ids"] == []
    assert report["local_byte_mismatch_model_ids"] == []


def test_source_custody_matches_canonical_markdown_bytes() -> None:
    if not DEFAULT_CANONICAL_SOURCE_DIR.exists():
        pytest.skip("canonical source directory is not available in this environment")

    report = build_source_custody_report(REPO_ROOT)

    assert report["canonical_source_dir_exists"] is True
    assert report["missing_canonical_source_model_ids"] == []
    assert report["canonical_sha256_mismatch_model_ids"] == []
