#!/usr/bin/env python3
"""Add a deterministic Lolla capture envelope to frozen development sources.

The source conversations remain byte-for-byte unchanged.  Each derived file is
the exact source preceded by a count header that ``run_extract.py`` can verify.
No semantic field, turn, or message is inferred or rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "lolla.capture_ready_development_corpus.v1"
_MARKER = re.compile(r"^\[Turn (\d+)\] (USER|ASSISTANT):\s*$", re.MULTILINE)


class CaptureReadyCorpusError(ValueError):
    """Raised when the frozen source cannot be wrapped mechanically."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CaptureReadyCorpusError("source manifest must be a JSON object")
    return value


def _validate_markers(text: str, *, expected_pairs: int, expected_messages: int) -> None:
    markers = _MARKER.findall(text)
    if len(markers) != expected_messages:
        raise CaptureReadyCorpusError("source marker count differs from frozen manifest")
    expected: list[tuple[str, str]] = []
    for turn in range(1, expected_pairs + 1):
        expected.extend([(str(turn), "USER"), (str(turn), "ASSISTANT")])
    if markers != expected:
        raise CaptureReadyCorpusError("source markers do not alternate in exact turn order")


def build_capture_ready_corpus(
    *,
    repo_root: Path,
    source_manifest_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    source_manifest = _load_object(source_manifest_path)
    if source_manifest.get("status") != "frozen_complete":
        raise CaptureReadyCorpusError("source manifest is not frozen complete")
    cases = source_manifest.get("cases")
    if not isinstance(cases, list) or not cases:
        raise CaptureReadyCorpusError("source manifest has no cases")

    output_dir.mkdir(parents=True, exist_ok=False)
    derived_cases: list[dict[str, Any]] = []
    for item in cases:
        if not isinstance(item, Mapping):
            raise CaptureReadyCorpusError("case entry must be an object")
        source_path = repo_root / str(item.get("path", ""))
        if not source_path.is_file():
            raise CaptureReadyCorpusError(f"source file missing: {source_path}")
        source_bytes = source_path.read_bytes()
        if _sha256_bytes(source_bytes) != item.get("sha256"):
            raise CaptureReadyCorpusError(f"source hash mismatch: {source_path}")
        source_text = source_bytes.decode("utf-8")
        if source_text.lstrip().startswith("CONVERSATION:"):
            raise CaptureReadyCorpusError("source already contains a capture header")

        pairs = int(item.get("turn_pairs", 0) or 0)
        messages = int(item.get("message_count", 0) or 0)
        if pairs <= 0 or messages != pairs * 2:
            raise CaptureReadyCorpusError("frozen pair/message counts are inconsistent")
        _validate_markers(source_text, expected_pairs=pairs, expected_messages=messages)

        header = (
            f"CONVERSATION: {messages} turns, {pairs} user messages, "
            f"{pairs} assistant responses\n\n"
        )
        derived_bytes = header.encode("utf-8") + source_bytes
        destination = output_dir / source_path.name
        destination.write_bytes(derived_bytes)
        derived_cases.append(
            {
                "case_id": item.get("case_id"),
                "title": item.get("title"),
                "source_path": str(source_path.relative_to(repo_root)),
                "source_sha256": item.get("sha256"),
                "derived_path": str(destination.relative_to(repo_root)),
                "derived_sha256": _sha256_bytes(derived_bytes),
                "message_count": messages,
                "turn_pairs": pairs,
                "header": header.strip(),
                "semantic_source_bytes_unchanged": derived_bytes.endswith(source_bytes),
            }
        )

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "status": "frozen_complete",
        "source_manifest_path": str(source_manifest_path.relative_to(repo_root)),
        "source_manifest_sha256": _sha256_file(source_manifest_path),
        "transform": {
            "kind": "prepend_declared_capture_counts_only",
            "semantic_rewrite": False,
            "model_call": False,
            "selection_or_scoring": False,
        },
        "cases": derived_cases,
        "non_claims": [
            "not a new conversation corpus",
            "not a clean holdout",
            "not semantic enrichment",
            "not evidence of Lolla usefulness",
        ],
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    source_manifest = (
        args.source_manifest
        if args.source_manifest.is_absolute()
        else repo_root / args.source_manifest
    )
    output_dir = args.output_dir if args.output_dir.is_absolute() else repo_root / args.output_dir
    manifest = build_capture_ready_corpus(
        repo_root=repo_root,
        source_manifest_path=source_manifest,
        output_dir=output_dir,
    )
    print(json.dumps({"status": manifest["status"], "case_count": len(manifest["cases"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
