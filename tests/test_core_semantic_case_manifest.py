from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = REPO_ROOT / "research/core-semantic-validation-2026-07-09/case-01-runs"
MANIFEST_PATH = RUN_DIR / "manifest.json"


def test_case_01_manifest_hashes_all_persisted_repeated_outputs() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert len(manifest["artifacts"]) == 6
    assert manifest["graph_runtime_modified"] is False
    for artifact in manifest["artifacts"]:
        path = RUN_DIR / artifact["path"]
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact["sha256"]


def test_case_01_manifest_links_current_comparison() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    comparison = (RUN_DIR / manifest["comparison"]["path"]).resolve()

    assert comparison.is_file()
    assert hashlib.sha256(comparison.read_bytes()).hexdigest() == manifest["comparison"]["sha256"]
