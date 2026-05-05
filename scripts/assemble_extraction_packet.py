from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CURATED_ROOT = Path("data/curation")
DEFAULT_SOURCE_DIR = Path("data/model_sources")
DEFAULT_SOURCE_MANIFEST_PATH = Path("data/model_sources/manifest.json")
DEFAULT_SCHEMA_PATH = Path("data/schemas/model_affordance.schema.json")
DEFAULT_CONTRACT_PATH = Path("references/model-affordance-extraction.md")
DEFAULT_RECORD_DIR = Path("data/model_affordances/batch_1")
DEFAULT_OUTPUT_DIR = Path("data/model_affordances/batch_1/packets")
PACKET_SCHEMA_VERSION = "model_affordance_extraction_packet.v1"


class ExtractionPacketError(RuntimeError):
    pass


@dataclass(frozen=True)
class SourceResidency:
    model_id: str
    source_file: str
    local_path: Path
    canonical_path: Path
    sha256: str
    byte_count: int


def assemble_extraction_packet(
    model_id: str,
    *,
    root: Path = REPO_ROOT,
    curation_root: Path = DEFAULT_CURATED_ROOT,
    source_dir: Path = DEFAULT_SOURCE_DIR,
    source_manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    contract_path: Path = DEFAULT_CONTRACT_PATH,
    record_dir: Path = DEFAULT_RECORD_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    copy_source: bool = True,
    write: bool = True,
) -> dict[str, Any]:
    root = Path(root)
    curation_root = _resolve(root, curation_root)
    source_dir = _resolve(root, source_dir)
    source_manifest_path = _resolve(root, source_manifest_path)
    schema_path = _resolve(root, schema_path)
    contract_path = _resolve(root, contract_path)
    record_dir = _resolve(root, record_dir)
    output_dir = _resolve(root, output_dir)

    activation_curation = _load_json(curation_root / f"{model_id}.json")
    source_residency = ensure_source_residency(
        model_id,
        activation_curation=activation_curation,
        root=root,
        source_dir=source_dir,
        source_manifest_path=source_manifest_path,
        copy_source=copy_source,
    )

    packet = {
        "packet_schema_version": PACKET_SCHEMA_VERSION,
        "model_id": model_id,
        "source": {
            "source_file": source_residency.source_file,
            "source_path": _display_path(source_residency.local_path, root),
            "canonical_source_path": str(source_residency.canonical_path),
            "sha256": source_residency.sha256,
            "bytes": source_residency.byte_count,
            "markdown": source_residency.local_path.read_text(encoding="utf-8"),
        },
        "curation": {
            "activation": _curation_block(curation_root / f"{model_id}.json"),
            "intervention_semantics": _curation_block(
                curation_root / "intervention_semantics" / f"{model_id}.json"
            ),
            "relation_semantics": _curation_block(
                curation_root / "relation_semantics" / f"{model_id}.json"
            ),
        },
        "schema": {
            "path": _display_path(schema_path, root),
            "payload": _load_json(schema_path),
        },
        "contract": {
            "path": _display_path(contract_path, root),
            "markdown": contract_path.read_text(encoding="utf-8"),
        },
        "extraction_protocol": [
            "Read the full source markdown before drafting any record.",
            "Use curation as reviewed context, not as a substitute for source reading.",
            "Prefer fewer, sharper affordances over broad schema completion.",
            "Emit absence records when the source is too thin or does not support a field.",
            "Every source_quote must be an exact substring of the named source file.",
            "Do not call external services from packet assembly.",
        ],
        "expected_output": {
            "record_path": f"{_display_path(record_dir, root)}/{model_id}.json",
            "validator": (
                "engine.system_b.model_affordance_validation."
                "validate_model_affordance_file"
            ),
            "validator_source_roots": ["data/model_sources"],
            "review_required_before_commit": True,
        },
    }

    if write:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{model_id}.json"
        output_path.write_text(
            json.dumps(packet, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return packet


def ensure_source_residency(
    model_id: str,
    *,
    activation_curation: dict[str, Any],
    root: Path = REPO_ROOT,
    source_dir: Path,
    source_manifest_path: Path,
    copy_source: bool,
) -> SourceResidency:
    source_file = str(activation_curation.get("source_file") or "")
    if not source_file.endswith(".md"):
        raise ExtractionPacketError(f"{model_id}: activation curation lacks source_file")

    manifest = _load_json(source_manifest_path)
    copied_from = Path(str(manifest.get("copied_from") or ""))
    if not copied_from.is_absolute():
        copied_from = _resolve(root, copied_from)
    canonical_path = copied_from / source_file
    local_path = source_dir / source_file

    if not local_path.exists():
        if not copy_source:
            raise ExtractionPacketError(f"{model_id}: local source is missing: {local_path}")
        if not canonical_path.exists():
            raise ExtractionPacketError(
                f"{model_id}: canonical source is missing: {canonical_path}"
            )
        source_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(canonical_path, local_path)

    if canonical_path.exists() and local_path.read_bytes() != canonical_path.read_bytes():
        raise ExtractionPacketError(
            f"{model_id}: local source differs from canonical source"
        )

    data = local_path.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    entry = {
        "model_id": model_id,
        "filename": source_file,
        "path": _display_path(local_path, root),
        "sha256": sha256,
        "bytes": len(data),
    }
    _upsert_source_manifest_entry(source_manifest_path, manifest, entry)
    return SourceResidency(
        model_id=model_id,
        source_file=source_file,
        local_path=local_path,
        canonical_path=canonical_path,
        sha256=sha256,
        byte_count=len(data),
    )


def _upsert_source_manifest_entry(
    manifest_path: Path,
    manifest: dict[str, Any],
    entry: dict[str, Any],
) -> None:
    if manifest.get("hash_algorithm") != "sha256":
        raise ExtractionPacketError("source manifest must use sha256")
    files = manifest.get("files")
    if not isinstance(files, list):
        raise ExtractionPacketError("source manifest files must be a list")

    model_id = str(entry["model_id"])
    filename = str(entry["filename"])
    replaced = False
    for index, existing in enumerate(files):
        if not isinstance(existing, dict):
            raise ExtractionPacketError("source manifest entries must be objects")
        existing_model_id = str(existing.get("model_id") or "")
        existing_filename = str(existing.get("filename") or "")
        if existing_filename == filename and existing_model_id != model_id:
            raise ExtractionPacketError(
                f"{filename}: already belongs to {existing_model_id}"
            )
        if existing_model_id == model_id:
            files[index] = entry
            replaced = True
            break
    if not replaced:
        files.append(entry)

    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def _curation_block(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "present": False,
            "path": _display_path(path, REPO_ROOT),
            "payload": None,
        }
    return {
        "present": True,
        "path": _display_path(path, REPO_ROOT),
        "payload": _load_json(path),
    }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ExtractionPacketError(f"required file is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ExtractionPacketError(f"{path}: JSON payload must be an object")
    return payload


def _resolve(root: Path, path: Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else root / path


def _display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Assemble one model-affordance extraction packet."
    )
    parser.add_argument("model_id")
    parser.add_argument("--curation-root", type=Path, default=DEFAULT_CURATED_ROOT)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument(
        "--source-manifest",
        type=Path,
        default=DEFAULT_SOURCE_MANIFEST_PATH,
    )
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    parser.add_argument("--record-dir", type=Path, default=DEFAULT_RECORD_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--no-copy-source",
        action="store_true",
        help="Fail instead of copying a missing source file from the canonical root.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Assemble and validate inputs without writing a packet.",
    )
    args = parser.parse_args(argv)

    try:
        assemble_extraction_packet(
            args.model_id,
            curation_root=args.curation_root,
            source_dir=args.source_dir,
            source_manifest_path=args.source_manifest,
            schema_path=args.schema,
            contract_path=args.contract,
            record_dir=args.record_dir,
            output_dir=args.output_dir,
            copy_source=not args.no_copy_source,
            write=not args.no_write,
        )
    except ExtractionPacketError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
