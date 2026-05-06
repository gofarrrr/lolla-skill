from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


DEFAULT_CANONICAL_SOURCE_DIR = Path(
    "/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216"
)


def build_source_custody_report(
    root: Path,
    *,
    knowledge_graph_path: Path | None = None,
    source_manifest_path: Path | None = None,
    canonical_source_dir: Path | None = DEFAULT_CANONICAL_SOURCE_DIR,
) -> dict[str, Any]:
    """Validate repo-local source custody against the runtime graph.

    This report is deterministic custody bookkeeping only. It does not extract
    affordances, alter runtime matching, or judge source usefulness.
    """

    root = Path(root)
    graph = _load_json(knowledge_graph_path or root / "data" / "knowledge_graph.json")
    manifest_path = source_manifest_path or root / "data" / "model_sources" / "manifest.json"
    manifest = _load_json(manifest_path)

    models = _mapping(graph.get("models"))
    runtime_model_ids = set(str(model_id) for model_id in models)
    source_root = root / str(manifest.get("source_root", "data/model_sources"))
    manifest_entries = [_mapping(entry) for entry in _list(manifest.get("files"))]
    manifest_by_model = {
        str(entry.get("model_id")): entry
        for entry in manifest_entries
        if str(entry.get("model_id", "")).strip()
    }
    canonical_dir = Path(canonical_source_dir) if canonical_source_dir is not None else None
    canonical_exists = bool(canonical_dir and canonical_dir.exists())

    missing_manifest = sorted(runtime_model_ids - set(manifest_by_model))
    outside_runtime = sorted(set(manifest_by_model) - runtime_model_ids)
    missing_local: list[str] = []
    local_hash_mismatch: list[str] = []
    local_byte_mismatch: list[str] = []
    source_file_mismatch: list[str] = []
    missing_canonical: list[str] = []
    canonical_hash_mismatch: list[str] = []
    duplicate_manifest_model_ids = _duplicates(
        str(entry.get("model_id"))
        for entry in manifest_entries
        if str(entry.get("model_id", "")).strip()
    )

    for model_id in sorted(runtime_model_ids):
        model = _mapping(models.get(model_id))
        expected_filename = str(model.get("source_file", "")).strip()
        entry = manifest_by_model.get(model_id)
        if entry is None:
            continue

        filename = str(entry.get("filename") or Path(str(entry.get("path", ""))).name)
        local_path = source_root / filename
        if not local_path.exists():
            missing_local.append(model_id)
            continue

        local_data = local_path.read_bytes()
        local_hash = hashlib.sha256(local_data).hexdigest()
        if local_hash != str(entry.get("sha256", "")):
            local_hash_mismatch.append(model_id)
        if len(local_data) != int(entry.get("bytes", -1)):
            local_byte_mismatch.append(model_id)

        if expected_filename and filename != expected_filename:
            source_file_mismatch.append(model_id)

        if canonical_dir is None:
            continue
        canonical_path = canonical_dir / expected_filename
        if not canonical_exists or not canonical_path.exists():
            missing_canonical.append(model_id)
            continue
        canonical_hash = hashlib.sha256(canonical_path.read_bytes()).hexdigest()
        if canonical_hash != local_hash:
            canonical_hash_mismatch.append(model_id)

    return {
        "report_version": "source_custody.v1",
        "runtime_model_count": len(runtime_model_ids),
        "manifest_model_count": len(manifest_by_model),
        "manifest_file_count": len(manifest_entries),
        "missing_manifest_model_ids": missing_manifest,
        "manifest_model_ids_outside_runtime_graph": outside_runtime,
        "duplicate_manifest_model_ids": duplicate_manifest_model_ids,
        "missing_local_source_model_ids": sorted(missing_local),
        "source_file_mismatch_model_ids": sorted(source_file_mismatch),
        "local_sha256_mismatch_model_ids": sorted(set(local_hash_mismatch)),
        "local_byte_mismatch_model_ids": sorted(local_byte_mismatch),
        "canonical_source_dir": str(canonical_dir or ""),
        "canonical_source_dir_exists": canonical_exists,
        "missing_canonical_source_model_ids": sorted(missing_canonical),
        "canonical_sha256_mismatch_model_ids": sorted(canonical_hash_mismatch),
    }


def _duplicates(values: Any) -> list[str]:
    seen: set[str] = set()
    duplicated: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text:
            continue
        if text in seen:
            duplicated.add(text)
        seen.add(text)
    return sorted(duplicated)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
