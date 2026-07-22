#!/usr/bin/env python3
"""Admit or validate the remaining repository-local graph compiler inputs.

``--source-root`` is a one-time recovery input and is never written to an
artifact. After admission, ``--validate-only`` requires no outside checkout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


EXPECTED_SETS = {
    "operational": {
        "count": 222,
        "bytes": 638_253,
        "sha256": "bcd0402010aeacb76335a403da0f45d6959ada3cc8c319db704b99cdcc639058",
    },
    "intervention": {
        "count": 222,
        "bytes": 948_813,
        "sha256": "6be8908b238ff07deb6eaaaadb3b2bf7d879904c99d5d6a281b14fceaeb3c90b",
    },
    "reframing": {
        "count": 51,
        "bytes": 137_668,
        "sha256": "21d5a2b4ecb2460a4196e6dd433660518862aeb3070013eb93d188db1760a5dd",
    },
    "prerequisite": {
        "count": 14,
        "bytes": 16_755,
        "sha256": "e656398b258457f18e4da780e4215ebc9d0f786e333dff16e73a566f8a714f65",
    },
    "structural_coverage": {
        "count": 16,
        "bytes": 52_556,
        "sha256": "282bf400346fedd872c3aa67c72379804c0169483ffdd0f3661ffa07030a2de3",
    },
}
EXPECTED_TENDENCY_FILES = {
    "munger_structural_mapping.md": {
        "bytes": 61_833,
        "sha256": "020b5ae2cef4ed553242105f34e2f72668d6133f650961bbfd8ec33aa513a8cb",
    },
    "munger_routing_table.json": {
        "bytes": 11_315,
        "sha256": "73665ebf0d72219f2226c9eae228dc7a85b0d265aa887dd0394ccce1a8b77c0a",
    },
}
INACTIVE_IDENTITIES = {
    "commitment-and-consistency-bias": "commitment-bias",
    "representativeness-bias": "representativeness-heuristic",
}


class CompilerInputError(ValueError):
    pass


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CompilerInputError(f"Cannot read valid JSON from {path}: {exc}") from exc


def _model_ids(root: Path) -> tuple[str, ...]:
    graph = _json(root / "data" / "knowledge_graph.json")
    models = graph.get("models") if isinstance(graph, dict) else None
    if not isinstance(models, dict) or len(models) != 222:
        raise CompilerInputError("Published graph must contain exactly 222 canonical models")
    return tuple(sorted(str(model_id) for model_id in models))


def _entries(paths: Iterable[Path], *, base: Path, root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(paths, key=lambda value: value.relative_to(base).as_posix()):
        payload = path.read_bytes()
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "set_path": path.relative_to(base).as_posix(),
                "sha256": _sha256(payload),
                "bytes": len(payload),
            }
        )
    return rows


def _set_sha(entries: list[dict[str, Any]]) -> str:
    view = [
        {"path": row["set_path"], "sha256": row["sha256"], "bytes": row["bytes"]}
        for row in entries
    ]
    return _sha256(json.dumps(view, sort_keys=True, separators=(",", ":")).encode())


def _assert_set(name: str, entries: list[dict[str, Any]]) -> None:
    expected = EXPECTED_SETS[name]
    observed = {
        "count": len(entries),
        "bytes": sum(int(row["bytes"]) for row in entries),
        "sha256": _set_sha(entries),
    }
    if observed != expected:
        raise CompilerInputError(f"{name} compiler-input identity drift: {observed} != {expected}")


def _preflight_recovery_source(root: Path, source_root: Path, ids: tuple[str, ...]) -> None:
    source_curation = source_root / "curation"

    operational_paths = [
        (root / "data" / "curation" / f"{model_id}.json")
        if model_id == "checklists"
        else (source_curation / f"{model_id}.json")
        for model_id in ids
    ]
    intervention_paths = [
        source_curation / "intervention_semantics" / f"{model_id}.json"
        for model_id in ids
    ]

    def rows(paths: Iterable[Path], base: Path | None = None) -> list[dict[str, Any]]:
        values: list[dict[str, Any]] = []
        for path in paths:
            if not path.is_file():
                raise CompilerInputError(f"Recovery input is missing: {path}")
            payload = path.read_bytes()
            values.append(
                {
                    "set_path": path.name if base is None else path.relative_to(base).as_posix(),
                    "sha256": _sha256(payload),
                    "bytes": len(payload),
                }
            )
        return sorted(values, key=lambda value: value["set_path"])

    _assert_set("operational", rows(operational_paths))
    _assert_set("intervention", rows(intervention_paths))
    for set_name, directory_name in (
        ("reframing", "reframing_semantics"),
        ("prerequisite", "prerequisite_semantics"),
        ("structural_coverage", "structural_coverage"),
    ):
        directory = source_curation / directory_name
        _assert_set(
            set_name,
            rows(directory.glob("*.json"), base=directory),
        )
    for name, expected in EXPECTED_TENDENCY_FILES.items():
        source = source_root / name
        if not source.is_file():
            raise CompilerInputError(f"Recovery input is missing: {source}")
        payload = source.read_bytes()
        if {"bytes": len(payload), "sha256": _sha256(payload)} != expected:
            raise CompilerInputError(f"Recovery tendency source identity drift: {name}")


def _local_sets(root: Path) -> dict[str, tuple[Path, list[Path]]]:
    ids = _model_ids(root)
    curation = root / "data" / "curation"
    return {
        "operational": (curation, [curation / f"{model_id}.json" for model_id in ids]),
        "intervention": (
            curation / "intervention_semantics",
            [curation / "intervention_semantics" / f"{model_id}.json" for model_id in ids],
        ),
        "reframing": (
            curation / "reframing_semantics",
            sorted((curation / "reframing_semantics").glob("*.json")),
        ),
        "prerequisite": (
            curation / "prerequisite_semantics",
            sorted((curation / "prerequisite_semantics").glob("*.json")),
        ),
        "structural_coverage": (
            curation / "structural_coverage",
            sorted((curation / "structural_coverage").glob("*.json")),
        ),
    }


def _validate_tendency_sources(root: Path) -> list[dict[str, Any]]:
    directory = root / "data" / "curation" / "tendency_semantics"
    entries: list[dict[str, Any]] = []
    for name, expected in EXPECTED_TENDENCY_FILES.items():
        path = directory / name
        if not path.is_file():
            raise CompilerInputError(f"Missing tendency compiler source {path}")
        payload = path.read_bytes()
        observed = {"bytes": len(payload), "sha256": _sha256(payload)}
        if observed != expected:
            raise CompilerInputError(f"Tendency compiler source drift for {name}")
        entries.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": observed["sha256"],
                "bytes": observed["bytes"],
            }
        )
    return entries


def _inactive_records(root: Path, subdirectory: str) -> list[dict[str, Any]]:
    directory = root / "data" / "curation" / subdirectory
    rows: list[dict[str, Any]] = []
    for old_id, canonical_id in sorted(INACTIVE_IDENTITIES.items()):
        path = directory / f"{old_id}.json"
        if not path.is_file():
            raise CompilerInputError(f"Missing historical identity record {path}")
        payload = path.read_bytes()
        rows.append(
            {
                "model_id": old_id,
                "canonical_model_id": canonical_id,
                "path": path.relative_to(root).as_posix(),
                "sha256": _sha256(payload),
                "bytes": len(payload),
                "lifecycle": "historical_superseded_identity",
                "compiler_included": False,
                "runtime_aliasing_authorized": False,
            }
        )
    return rows


def _schema_record(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    payload = path.read_bytes()
    return {
        "path": relative,
        "sha256": _sha256(payload),
        "bytes": len(payload),
    }


def build_manifest(root: Path) -> dict[str, Any]:
    sets: dict[str, Any] = {}
    for name, (base, paths) in _local_sets(root).items():
        if any(not path.is_file() for path in paths):
            raise CompilerInputError(f"{name} compiler-input set is incomplete")
        entries = _entries(paths, base=base, root=root)
        _assert_set(name, entries)
        sets[name] = {
            "record_count": len(entries),
            "record_bytes": sum(int(row["bytes"]) for row in entries),
            "record_set_sha256": _set_sha(entries),
            "records": entries,
        }

    return {
        "schema_version": "lolla.graph_compiler_inputs_manifest.v1",
        "status": "complete",
        "created_date": "2026-07-22",
        "authority": {
            "repository_role": "sole_active_project_authority",
            "other_repository_required": False,
            "machine_specific_path_recorded": False,
        },
        "recovery": {
            "source_kind": "temporary_machine_local_recovery_snapshot",
            "source_snapshot_after_admission_required": False,
            "semantic_regeneration_performed": False,
            "provider_calls": 0,
        },
        "source_dependencies": {
            "model_sources_manifest": "data/model_sources/manifest.json",
            "relation_authoring_manifest": "data/curation/relation_semantics_manifest.json",
        },
        "input_sets": sets,
        "tendency_sources": _validate_tendency_sources(root),
        "schemas": [
            _schema_record(root, "data/curation/schema.json"),
            _schema_record(root, "data/curation/intervention_semantics/schema.json"),
            _schema_record(root, "data/curation/relation_semantics/schema.json"),
        ],
        "inactive_records": {
            "operational": _inactive_records(root, ""),
            "intervention": _inactive_records(root, "intervention_semantics"),
        },
        "non_claims": [
            "compiler_input_custody_is_not_semantic_correctness",
            "exact_input_identity_is_not_runtime_usefulness",
            "historical_identity_records_are_not_runtime_aliases",
        ],
    }


def _write_manifest(root: Path, payload: dict[str, Any]) -> None:
    path = root / "data" / "curation" / "compiler_inputs_manifest.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def adopt(root: Path, source_root: Path) -> dict[str, Any]:
    ids = _model_ids(root)
    _preflight_recovery_source(root, source_root, ids)
    source_curation = source_root / "curation"
    destination_curation = root / "data" / "curation"

    # The repository's checklist record contains a later reviewed tightening
    # already present in the published graph. Every other active Wave 1 record
    # is admitted byte-for-byte from the reconciled recovery snapshot.
    for model_id in ids:
        if model_id != "checklists":
            source = source_curation / f"{model_id}.json"
            (destination_curation / source.name).write_bytes(source.read_bytes())
        source = source_curation / "intervention_semantics" / f"{model_id}.json"
        destination = destination_curation / "intervention_semantics" / source.name
        destination.write_bytes(source.read_bytes())

    (destination_curation / "schema.json").write_bytes(
        (source_curation / "schema.json").read_bytes()
    )
    (destination_curation / "intervention_semantics" / "schema.json").write_bytes(
        (source_curation / "intervention_semantics" / "schema.json").read_bytes()
    )

    for source_name, destination_name in (
        ("reframing_semantics", "reframing_semantics"),
        ("prerequisite_semantics", "prerequisite_semantics"),
        ("structural_coverage", "structural_coverage"),
    ):
        source_dir = source_curation / source_name
        destination_dir = destination_curation / destination_name
        destination_dir.mkdir(parents=True, exist_ok=True)
        for source in sorted(path for path in source_dir.iterdir() if path.is_file()):
            (destination_dir / source.name).write_bytes(source.read_bytes())

    tendency_dir = destination_curation / "tendency_semantics"
    tendency_dir.mkdir(parents=True, exist_ok=True)
    for name in EXPECTED_TENDENCY_FILES:
        (tendency_dir / name).write_bytes((source_root / name).read_bytes())

    payload = build_manifest(root)
    _write_manifest(root, payload)
    return payload


def validate(root: Path, *, write: bool) -> dict[str, Any]:
    payload = build_manifest(root)
    manifest_path = root / "data" / "curation" / "compiler_inputs_manifest.json"
    expected = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if write:
        manifest_path.write_text(expected, encoding="utf-8")
    elif not manifest_path.is_file() or manifest_path.read_text(encoding="utf-8") != expected:
        raise CompilerInputError("Graph compiler input manifest is missing or stale")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.source_root and args.validate_only:
        parser.error("--source-root and --validate-only are mutually exclusive")
    root = args.root.resolve()
    payload = (
        adopt(root, args.source_root.resolve())
        if args.source_root
        else validate(root, write=not args.validate_only)
    )
    print(
        json.dumps(
            {
                "status": "valid" if args.validate_only else "written",
                "input_set_count": len(payload["input_sets"]),
                "other_repository_required": payload["authority"]["other_repository_required"],
                "provider_calls": payload["recovery"]["provider_calls"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
