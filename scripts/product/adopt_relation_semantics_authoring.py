#!/usr/bin/env python3
"""Admit or validate the repository-local Wave 3 relation-authoring set.

The one-time ``--source-dir`` path is an operator input only.  It is never
written to the repository manifest.  Once admitted, ``--validate-only`` proves
that a fresh clone has the complete source set and no longer needs the recovery
snapshot.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable


SCHEMA_VERSION = "lolla.relation_semantics_authoring_manifest.v1"
SOURCE_ANCHOR_SCHEMA_VERSION = "lolla.relation_source_anchor_register.v1"
RECOVERY_ID = "relation-semantics-reconciled-snapshot-a7796265"
EXPECTED_MODEL_COUNT = 222
EXPECTED_RELATION_COUNT = 1_358
EXPECTED_RECORD_BYTES = 1_243_714
EXPECTED_RECORD_SET_SHA256 = (
    "a779626577a3f373a6882b68f5c0621e3cc2fb62935c13b3421ca2b2ca2ca3cd"
)
RELATION_FAMILIES = {
    "allies": "ally",
    "antagonists": "antagonist",
    "structured_tensions": "tension",
}
INACTIVE_IDENTITIES = {
    "commitment-and-consistency-bias": "commitment-bias",
    "representativeness-bias": "representativeness-heuristic",
}


class RelationAuthoringError(ValueError):
    """Raised when relation authorship or its repository custody is invalid."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RelationAuthoringError(f"Cannot read valid JSON from {path}: {exc}") from exc


def _canonical_model_ids(root: Path) -> tuple[str, ...]:
    graph = _json(root / "data" / "knowledge_graph.json")
    models = graph.get("models") if isinstance(graph, dict) else None
    if not isinstance(models, dict):
        raise RelationAuthoringError("data/knowledge_graph.json has no model registry")
    model_ids = tuple(sorted(str(model_id) for model_id in models))
    if len(model_ids) != EXPECTED_MODEL_COUNT:
        raise RelationAuthoringError(
            f"Expected {EXPECTED_MODEL_COUNT} canonical models, found {len(model_ids)}"
        )
    return model_ids


def _record_files(directory: Path, model_ids: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    missing: list[str] = []
    for model_id in model_ids:
        path = directory / f"{model_id}.json"
        if not path.is_file():
            missing.append(model_id)
        else:
            files.append(path)
    if missing:
        raise RelationAuthoringError(
            "Missing canonical relation-authoring records: " + ", ".join(missing)
        )
    return files


def _record_entries(files: Iterable[Path], *, base: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted(files, key=lambda item: item.name):
        payload = path.read_bytes()
        entries.append(
            {
                "model_id": path.stem,
                "path": path.relative_to(base).as_posix(),
                "sha256": _sha256(payload),
                "bytes": len(payload),
            }
        )
    return entries


def _record_set_sha(entries: list[dict[str, Any]]) -> str:
    hash_view = [
        {"path": Path(entry["path"]).name, "sha256": entry["sha256"], "bytes": entry["bytes"]}
        for entry in entries
    ]
    canonical = json.dumps(hash_view, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256(canonical)


def _validate_recovered_identity(entries: list[dict[str, Any]]) -> None:
    byte_count = sum(int(entry["bytes"]) for entry in entries)
    record_set_sha = _record_set_sha(entries)
    failures: list[str] = []
    if len(entries) != EXPECTED_MODEL_COUNT:
        failures.append(f"record count {len(entries)} != {EXPECTED_MODEL_COUNT}")
    if byte_count != EXPECTED_RECORD_BYTES:
        failures.append(f"record bytes {byte_count} != {EXPECTED_RECORD_BYTES}")
    if record_set_sha != EXPECTED_RECORD_SET_SHA256:
        failures.append(
            f"record-set sha256 {record_set_sha} != {EXPECTED_RECORD_SET_SHA256}"
        )
    if failures:
        raise RelationAuthoringError("Recovery snapshot identity mismatch: " + "; ".join(failures))


def _validate_relation_item(
    item: Any,
    *,
    record_path: Path,
    family: str,
    valid_model_ids: set[str],
) -> None:
    if not isinstance(item, dict):
        raise RelationAuthoringError(f"{record_path}: {family} item is not an object")
    text_key = "tension_text" if family == "structured_tensions" else "rationale_text"
    required = {
        "target_model_id",
        text_key,
        "source_quote",
        "extraction_type",
        "confidence",
    }
    if family != "structured_tensions":
        required.update({"affinity_strength", "affinity_rationale", "activation_condition"})
    missing = sorted(required.difference(item))
    if missing:
        raise RelationAuthoringError(
            f"{record_path}: {family} item missing {', '.join(missing)}"
        )
    if item["target_model_id"] not in valid_model_ids:
        raise RelationAuthoringError(
            f"{record_path}: noncanonical target {item['target_model_id']!r}"
        )


def _load_and_validate_records(
    files: Iterable[Path], *, valid_model_ids: set[str]
) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for path in sorted(files, key=lambda item: item.name):
        payload = _json(path)
        if not isinstance(payload, dict):
            raise RelationAuthoringError(f"{path}: record is not an object")
        model_id = payload.get("model_id")
        if model_id != path.stem:
            raise RelationAuthoringError(
                f"{path}: model_id {model_id!r} does not match filename"
            )
        if model_id not in valid_model_ids:
            raise RelationAuthoringError(f"{path}: model_id is not canonical")
        for family in RELATION_FAMILIES:
            items = payload.get(family)
            if not isinstance(items, list):
                raise RelationAuthoringError(f"{path}: {family} is not an array")
            for item in items:
                _validate_relation_item(
                    item,
                    record_path=path,
                    family=family,
                    valid_model_ids=valid_model_ids,
                )
        records[str(model_id)] = payload
    if set(records) != valid_model_ids:
        raise RelationAuthoringError("Relation records do not exactly cover canonical models")
    return records


def _authored_relation_rows(
    records: dict[str, dict[str, Any]],
) -> dict[tuple[str, str, str], dict[str, Any]]:
    rows: dict[tuple[str, str, str], dict[str, Any]] = {}
    for model_id in sorted(records):
        record = records[model_id]
        for family, edge_type in RELATION_FAMILIES.items():
            for item in record[family]:
                key = (model_id, str(item["target_model_id"]), edge_type)
                if key in rows:
                    raise RelationAuthoringError(f"Duplicate authored relation {key}")
                rows[key] = item
    if len(rows) != EXPECTED_RELATION_COUNT:
        raise RelationAuthoringError(
            f"Expected {EXPECTED_RELATION_COUNT} authored relations, found {len(rows)}"
        )
    return rows


def _normalized_excerpt(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def _source_anchor_register(
    root: Path,
    records: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    published = _json(root / "data" / "relationship_graph.json")
    if not isinstance(published, list):
        raise RelationAuthoringError("data/relationship_graph.json is not an array")
    published_indexes = {
        (
            str(row.get("source_model_id")),
            str(row.get("target_model_id")),
            str(row.get("edge_type")),
        ): index
        for index, row in enumerate(published)
        if isinstance(row, dict)
    }

    state_counts = {
        "exact_span": 0,
        "normalized_excerpt": 0,
        "synthesized_or_multi_span": 0,
        "unresolved": 0,
        "missing": 0,
    }
    relations: list[dict[str, Any]] = []
    relation_index = 0
    for source_model_id in sorted(records):
        record = records[source_model_id]
        source_path = root / "data" / "model_sources" / str(record.get("source_file", ""))
        source_text = source_path.read_text(encoding="utf-8") if source_path.is_file() else None
        source_identity = (
            {
                "path": source_path.relative_to(root).as_posix(),
                "sha256": _sha256(source_path.read_bytes()),
                "bytes": source_path.stat().st_size,
            }
            if source_text is not None
            else {
                "path": source_path.relative_to(root).as_posix(),
                "sha256": None,
                "bytes": None,
            }
        )
        for family, edge_type in RELATION_FAMILIES.items():
            for item_index, item in enumerate(record[family]):
                target_model_id = str(item["target_model_id"])
                identity = (source_model_id, target_model_id, edge_type)
                source_quote = str(item.get("source_quote", ""))
                exact_span: dict[str, int] | None = None
                if source_text is None or not source_quote:
                    state = "missing"
                else:
                    start = source_text.find(source_quote)
                    if start >= 0:
                        state = "exact_span"
                        exact_span = {
                            "start_char": start,
                            "end_char_exclusive": start + len(source_quote),
                        }
                    elif _normalized_excerpt(source_quote) in _normalized_excerpt(source_text):
                        state = "normalized_excerpt"
                    else:
                        state = "unresolved"
                state_counts[state] += 1
                if identity not in published_indexes:
                    raise RelationAuthoringError(
                        f"Cannot resolve authored relation to published graph: {identity}"
                    )
                relations.append(
                    {
                        "relation_id": "::".join(identity),
                        "source_model_id": source_model_id,
                        "target_model_id": target_model_id,
                        "edge_type": edge_type,
                        "source_order": relation_index,
                        "authoring_pointer": {
                            "path": (
                                root
                                / "data"
                                / "curation"
                                / "relation_semantics"
                                / f"{source_model_id}.json"
                            ).relative_to(root).as_posix(),
                            "family": family,
                            "item_index": item_index,
                        },
                        "published_pointer": {
                            "path": "data/relationship_graph.json",
                            "item_index": published_indexes[identity],
                        },
                        "source": source_identity,
                        "source_anchor_state": state,
                        "exact_span": exact_span,
                    }
                )
                relation_index += 1

    if len(relations) != EXPECTED_RELATION_COUNT:
        raise RelationAuthoringError(
            f"Expected {EXPECTED_RELATION_COUNT} source anchors, found {len(relations)}"
        )
    return {
        "schema_version": SOURCE_ANCHOR_SCHEMA_VERSION,
        "created_date": "2026-07-22",
        "status": "complete",
        "classification_authority": "mechanical_only_no_semantic_repair",
        "state_definitions": {
            "exact_span": "source_quote is an exact character substring of the declared source",
            "normalized_excerpt": (
                "source_quote matches after whitespace collapse and case-folding but has no exact span"
            ),
            "synthesized_or_multi_span": (
                "reserved for an explicit future human declaration; never inferred mechanically"
            ),
            "unresolved": (
                "a nonempty quote and source exist, but the declared excerpt cannot be located mechanically"
            ),
            "missing": "the declared source or source_quote is unavailable",
        },
        "coverage": {
            "relation_count": len(relations),
            "state_counts": state_counts,
            "all_relations_classified": True,
            "provider_calls": 0,
            "semantic_repair_performed": False,
        },
        "relations": relations,
        "non_claims": [
            "exact_span_is_not_semantic_correctness",
            "normalized_excerpt_is_not_an_exact_source_locator",
            "unresolved_is_not_false",
            "synthesized_or_multi_span_requires_human_declaration",
        ],
    }


def _validate_published_relation_reconciliation(
    root: Path, authored: dict[tuple[str, str, str], dict[str, Any]]
) -> dict[str, int]:
    graph = _json(root / "data" / "relationship_graph.json")
    if not isinstance(graph, list):
        raise RelationAuthoringError("data/relationship_graph.json is not an array")
    published: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in graph:
        if not isinstance(row, dict):
            raise RelationAuthoringError("Published relation row is not an object")
        key = (
            str(row.get("source_model_id")),
            str(row.get("target_model_id")),
            str(row.get("edge_type")),
        )
        if key in published:
            raise RelationAuthoringError(f"Duplicate published relation {key}")
        published[key] = row
    if set(published) != set(authored):
        missing = sorted(set(authored).difference(published))
        extra = sorted(set(published).difference(authored))
        raise RelationAuthoringError(
            f"Published relation identities differ: missing={missing[:5]}, extra={extra[:5]}"
        )

    family_counts = {"ally": 0, "antagonist": 0, "tension": 0}
    for key, item in authored.items():
        row = published[key]
        family_counts[key[2]] += 1
        text_key = "tension_text" if key[2] == "tension" else "rationale_text"
        comparisons = {
            "source_description": item[text_key],
            "source_quote": item["source_quote"],
            "extraction_type": item["extraction_type"],
            "confidence": item["confidence"],
        }
        if key[2] != "tension":
            comparisons.update(
                {
                    "affinity_rationale": item["affinity_rationale"],
                    "activation_condition": item["activation_condition"],
                }
            )
            # Ally strength is carried directly into the published composition
            # weight. Antagonist composition weight is a compiler-derived
            # compatibility value, not the authored opposition strength.
            if key[2] == "ally":
                comparisons["composition_affinity"] = item["affinity_strength"]
        elif "tension_type" in item:
            comparisons["tension_type"] = item["tension_type"]
        for field, expected in comparisons.items():
            if row.get(field) != expected:
                raise RelationAuthoringError(
                    f"Published field drift for {key} at {field}: "
                    f"{row.get(field)!r} != {expected!r}"
                )
    return family_counts


def _inactive_records(root: Path) -> list[dict[str, Any]]:
    relation_dir = root / "data" / "curation" / "relation_semantics"
    records: list[dict[str, Any]] = []
    for old_id, canonical_id in sorted(INACTIVE_IDENTITIES.items()):
        path = relation_dir / f"{old_id}.json"
        if not path.is_file():
            raise RelationAuthoringError(f"Missing historical identity record {path}")
        payload = path.read_bytes()
        records.append(
            {
                "model_id": old_id,
                "path": path.relative_to(root).as_posix(),
                "sha256": _sha256(payload),
                "bytes": len(payload),
                "lifecycle": "historical_superseded_identity",
                "canonical_model_id": canonical_id,
                "compiler_included": False,
                "runtime_aliasing_authorized": False,
            }
        )
    return records


def _build_manifest(
    root: Path,
    *,
    entries: list[dict[str, Any]],
    family_counts: dict[str, int],
    source_anchor_register: dict[str, Any],
) -> dict[str, Any]:
    schema_path = root / "data" / "curation" / "relation_semantics" / "schema.json"
    schema_bytes = schema_path.read_bytes()
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "complete",
        "created_date": "2026-07-22",
        "authority": {
            "repository_role": "sole_active_project_authority",
            "authoring_directory": "data/curation/relation_semantics",
            "other_repository_required": False,
            "machine_specific_path_recorded": False,
        },
        "recovery": {
            "recovery_id": RECOVERY_ID,
            "source_kind": "temporary_machine_local_recovery_snapshot",
            "source_snapshot_after_admission_required": False,
            "semantic_regeneration_performed": False,
            "provider_calls": 0,
            "expected_record_count": EXPECTED_MODEL_COUNT,
            "expected_record_bytes": EXPECTED_RECORD_BYTES,
            "expected_record_set_sha256": EXPECTED_RECORD_SET_SHA256,
            "record_set_hash_algorithm": (
                "sha256(canonical-json(sorted [{path basename, sha256, bytes}]))"
            ),
        },
        "active_records": entries,
        "inactive_records": _inactive_records(root),
        "schema": {
            "path": schema_path.relative_to(root).as_posix(),
            "sha256": _sha256(schema_bytes),
            "bytes": len(schema_bytes),
        },
        "source_anchor_register": {
            "path": "data/curation/relation_source_anchor_register.json",
            "sha256": _sha256(_canonical_json_bytes(source_anchor_register)),
            "bytes": len(_canonical_json_bytes(source_anchor_register)),
            "status": source_anchor_register["status"],
            "state_counts": source_anchor_register["coverage"]["state_counts"],
        },
        "coverage": {
            "canonical_model_count": EXPECTED_MODEL_COUNT,
            "active_record_count": len(entries),
            "active_record_bytes": sum(int(entry["bytes"]) for entry in entries),
            "active_record_set_sha256": _record_set_sha(entries),
            "relation_count": sum(family_counts.values()),
            "relation_counts_by_family": family_counts,
            "published_rich_graph_reconciled": True,
        },
        "non_claims": [
            "source_custody_is_not_semantic_correctness",
            "published_reconciliation_is_not_runtime_usefulness",
            "inactive_identity_records_are_not_runtime_aliases",
            "published_antagonist_composition_affinity_is_not_authored_opposition_strength",
        ],
    }


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def adopt(root: Path, source_dir: Path) -> dict[str, Any]:
    model_ids = _canonical_model_ids(root)
    source_files = _record_files(source_dir, model_ids)
    source_entries = _record_entries(source_files, base=source_dir)
    _validate_recovered_identity(source_entries)
    source_records = _load_and_validate_records(
        source_files, valid_model_ids=set(model_ids)
    )
    authored = _authored_relation_rows(source_records)
    family_counts = _validate_published_relation_reconciliation(root, authored)

    destination = root / "data" / "curation" / "relation_semantics"
    destination.mkdir(parents=True, exist_ok=True)
    for source in source_files:
        (destination / source.name).write_bytes(source.read_bytes())
    return validate(root, write_manifest=True)


def validate(root: Path, *, write_manifest: bool) -> dict[str, Any]:
    model_ids = _canonical_model_ids(root)
    relation_dir = root / "data" / "curation" / "relation_semantics"
    files = _record_files(relation_dir, model_ids)
    entries = _record_entries(files, base=root)
    _validate_recovered_identity(entries)
    records = _load_and_validate_records(files, valid_model_ids=set(model_ids))
    authored = _authored_relation_rows(records)
    family_counts = _validate_published_relation_reconciliation(root, authored)
    source_anchor_register = _source_anchor_register(root, records)
    source_anchor_path = root / "data" / "curation" / "relation_source_anchor_register.json"
    source_anchor_bytes = _canonical_json_bytes(source_anchor_register)
    if write_manifest:
        source_anchor_path.write_bytes(source_anchor_bytes)
    else:
        if not source_anchor_path.is_file():
            raise RelationAuthoringError(f"Missing source-anchor register {source_anchor_path}")
        if source_anchor_path.read_bytes() != source_anchor_bytes:
            raise RelationAuthoringError("Relation source-anchor register is stale")
    manifest = _build_manifest(
        root,
        entries=entries,
        family_counts=family_counts,
        source_anchor_register=source_anchor_register,
    )
    manifest_path = root / "data" / "curation" / "relation_semantics_manifest.json"
    manifest_bytes = _canonical_json_bytes(manifest)
    if write_manifest:
        manifest_path.write_bytes(manifest_bytes)
    else:
        if not manifest_path.is_file():
            raise RelationAuthoringError(f"Missing manifest {manifest_path}")
        if manifest_path.read_bytes() != manifest_bytes:
            raise RelationAuthoringError("Relation-authoring manifest is stale")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--source-dir",
        type=Path,
        help="One-time recovery input. The path is never recorded in repository artifacts.",
    )
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.source_dir and args.validate_only:
        parser.error("--source-dir and --validate-only are mutually exclusive")
    manifest = (
        adopt(root, args.source_dir.resolve())
        if args.source_dir
        else validate(root, write_manifest=not args.validate_only)
    )
    print(
        json.dumps(
            {
                "status": "valid" if args.validate_only else "written",
                "active_record_count": manifest["coverage"]["active_record_count"],
                "relation_count": manifest["coverage"]["relation_count"],
                "record_set_sha256": manifest["coverage"]["active_record_set_sha256"],
                "other_repository_required": manifest["authority"]["other_repository_required"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
