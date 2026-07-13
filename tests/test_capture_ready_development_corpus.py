from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.evals.build_capture_ready_development_corpus import (
    CaptureReadyCorpusError,
    build_capture_ready_corpus,
)
from scripts.run_extract import _validate_conversation_capture


REPO_ROOT = Path(__file__).resolve().parents[1]
REAL_MANIFEST = (
    REPO_ROOT
    / "research/designed-ambiguous-pool-v1-2026-07-10/capture-ready-cases/manifest.json"
)


def _write_source(root: Path, *, header: bool = False) -> tuple[Path, Path]:
    source = root / "sources" / "case.txt"
    source.parent.mkdir(parents=True)
    prefix = "CONVERSATION: 2 turns, 1 user message, 1 assistant response\n\n" if header else ""
    source.write_text(
        prefix + "[Turn 1] USER:\nA?\n\n[Turn 1] ASSISTANT:\nB.\n",
        encoding="utf-8",
    )
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest = root / "source-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "status": "frozen_complete",
                "cases": [
                    {
                        "case_id": "case-1",
                        "title": "One",
                        "path": str(source.relative_to(root)),
                        "sha256": digest,
                        "message_count": 2,
                        "turn_pairs": 1,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return source, manifest


def test_builder_only_prepends_capture_header_and_preserves_source_bytes(tmp_path: Path) -> None:
    source, manifest_path = _write_source(tmp_path)
    output_dir = tmp_path / "derived"
    manifest = build_capture_ready_corpus(
        repo_root=tmp_path,
        source_manifest_path=manifest_path,
        output_dir=output_dir,
    )

    derived = output_dir / source.name
    value = derived.read_bytes()
    assert value.startswith(
        b"CONVERSATION: 2 turns, 1 user messages, 1 assistant responses\n\n"
    )
    assert value.endswith(source.read_bytes())
    assert manifest["transform"]["semantic_rewrite"] is False
    assert manifest["cases"][0]["semantic_source_bytes_unchanged"] is True


def test_builder_rejects_source_that_already_has_capture_header(tmp_path: Path) -> None:
    _source, manifest_path = _write_source(tmp_path, header=True)
    with pytest.raises(CaptureReadyCorpusError, match="already contains"):
        build_capture_ready_corpus(
            repo_root=tmp_path,
            source_manifest_path=manifest_path,
            output_dir=tmp_path / "derived",
        )


def test_real_capture_ready_corpus_preserves_all_sources_and_passes_preflight() -> None:
    manifest = json.loads(REAL_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["status"] == "frozen_complete"
    assert len(manifest["cases"]) == 5
    for item in manifest["cases"]:
        source = REPO_ROOT / item["source_path"]
        derived = REPO_ROOT / item["derived_path"]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == item["source_sha256"]
        assert hashlib.sha256(derived.read_bytes()).hexdigest() == item["derived_sha256"]
        assert derived.read_bytes().endswith(source.read_bytes())
        capture = _validate_conversation_capture(derived.read_text(encoding="utf-8"))
        assert capture["capture_health"] == "good"
        assert capture["capture_manifest"]["actual_user_turns"] == item["turn_pairs"]
        assert capture["capture_manifest"]["actual_assistant_turns"] == item["turn_pairs"]
