from __future__ import annotations

import argparse
import copy
import hashlib
import json
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "engine"))

from system_b.model_affordance_validation import (  # noqa: E402
    iter_model_affordance_errors,
)


DEFAULT_RECORD_DIR = Path("data/model_affordances/pilot")
DEFAULT_PILOT_MANIFEST_PATH = Path("data/model_affordances/pilot_manifest.json")
DEFAULT_SOURCE_DIR = Path("data/model_sources")
DEFAULT_SOURCE_MANIFEST_PATH = Path("data/model_sources/manifest.json")
DEFAULT_SCHEMA_PATH = Path("data/schemas/model_affordance.schema.json")
DEFAULT_OUTPUT_DIR = Path("data/compiled/model_affordances")
COMPILED_FILENAME = "affordances_v1.json"
QUALITY_REPORT_FILENAME = "quality_report_v1.md"
CONFIDENCE_ORDER = ("high", "medium", "weak", "not_applicable")
AFFORDANCE_STATUS_ORDER = (
    "supported",
    "weak_support",
    "duplicate_of_existing_field",
    "deferred_for_review",
)

DO_NOT_PROMOTE_FLAGS = (
    {
        "affordance_id": "systems-thinking.structure-over-events",
        "reason": (
            "Broad-overlay risk; reviewers disagreed on whether it should remain "
            "separate from feedback-loop-mapping."
        ),
        "future_trigger_condition": (
            "Merge or rewrite only if archived-case evaluation shows 80%+ "
            "coactivation with systems-thinking.feedback-loop-mapping."
        ),
    },
    {
        "affordance_id": "confidence-calibration.method-first-self-interrogation",
        "reason": (
            "Broad scope; reviewers disagreed on whether breadth-from-source is "
            "acceptable as-is."
        ),
        "future_trigger_condition": (
            "Split only if future runtime cases show learning/mastery calibration "
            "and business-claim confidence require different treatment."
        ),
    },
    {
        "affordance_id": "inversion.obstacle-removal-before-added-force",
        "reason": (
            "Likely sub-affordance rather than peer affordance; reviewers broadly "
            "agree this needs rewrite review before runtime promotion."
        ),
        "future_trigger_condition": (
            "Introduce parent_affordance_id or granularity only if a second "
            "sub-affordance case appears."
        ),
    },
)


class ModelAffordanceCompilationError(RuntimeError):
    pass


@dataclass(frozen=True)
class CompilationResult:
    compiled_path: Path
    quality_report_path: Path
    compiled: dict[str, object]
    quality_report: str


def compile_model_affordances(
    *,
    root: Path = REPO_ROOT,
    record_dir: Path = DEFAULT_RECORD_DIR,
    pilot_manifest_path: Path = DEFAULT_PILOT_MANIFEST_PATH,
    source_dir: Path = DEFAULT_SOURCE_DIR,
    source_manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> CompilationResult:
    root = Path(root)
    record_dir = _resolve(root, record_dir)
    pilot_manifest_path = _resolve(root, pilot_manifest_path)
    source_dir = _resolve(root, source_dir)
    source_manifest_path = _resolve(root, source_manifest_path)
    schema_path = _resolve(root, schema_path)
    output_dir = _resolve(root, output_dir)

    pilot_manifest = _load_object(pilot_manifest_path)
    source_manifest = _load_object(source_manifest_path)
    schema = _load_object(schema_path)

    hash_failures = _source_hash_failures(
        source_dir=source_dir,
        source_manifest=source_manifest,
    )
    if hash_failures:
        raise ModelAffordanceCompilationError(
            "source hash verification failed: " + "; ".join(hash_failures)
        )

    records, record_paths = _load_records_from_manifest(
        root=root,
        record_dir=record_dir,
        pilot_manifest=pilot_manifest,
    )
    validation_summary = _validate_records(
        records=records,
        record_paths=record_paths,
        source_dir=source_dir,
    )
    if validation_summary["schema_validation_failure_count"] or validation_summary[
        "source_quote_rejection_count"
    ]:
        raise ModelAffordanceCompilationError(
            "model affordance validation failed: "
            f"schema_validation_failure_count={validation_summary['schema_validation_failure_count']}; "
            f"source_quote_rejection_count={validation_summary['source_quote_rejection_count']}; "
            + "; ".join(validation_summary["errors"])
        )

    compiled = _build_compiled_artifact(
        records=records,
        record_paths=record_paths,
        pilot_manifest=pilot_manifest,
        source_manifest=source_manifest,
        schema=schema,
        validation_summary=validation_summary,
    )
    quality_report = render_quality_report(compiled)

    compiled_path = output_dir / COMPILED_FILENAME
    quality_report_path = output_dir / QUALITY_REPORT_FILENAME
    if write:
        output_dir.mkdir(parents=True, exist_ok=True)
        compiled_path.write_text(
            json.dumps(compiled, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        quality_report_path.write_text(quality_report, encoding="utf-8")

    return CompilationResult(
        compiled_path=compiled_path,
        quality_report_path=quality_report_path,
        compiled=compiled,
        quality_report=quality_report,
    )


def render_quality_report(compiled: dict[str, object]) -> str:
    quality = _quality_signals(compiled)
    records = _records(compiled)
    metadata = _dict(compiled["compile_metadata"])
    lines: list[str] = [
        "# Model Affordance Quality Report v1",
        "",
        "This report surfaces honesty signals for human reviewers. It does not grade quality, infer missing knowledge, or promote any affordance into runtime use.",
        "",
        "## Honesty Signals",
        "",
        f"- Contributing records: `{metadata['contributing_record_count']}`",
        f"- Compiled affordances: `{metadata['affordance_count']}`",
        f"- Compiled absence records: `{metadata['absence_record_count']}`",
        "- Affordance count distribution per model:",
    ]
    for count, model_ids in quality["affordance_count_distribution"].items():
        lines.append(f"  - `{count}` affordance(s): {', '.join(model_ids)}")
    lines.extend(
        [
            "- Absence record status counts:",
            *[
                f"  - `{status}`: `{count}`"
                for status, count in quality["absence_status_counts"].items()
            ],
            "- Affordance confidence counts:",
            *[
                f"  - `{confidence}`: `{count}`"
                for confidence, count in quality["affordance_confidence_counts"].items()
            ],
            "- Affordance status counts:",
            *[
                f"  - `{status}`: `{count}`"
                for status, count in quality["affordance_status_counts"].items()
            ],
            f"- Source-quote rejection count from compile run: `{quality['source_quote_rejection_count']}`",
            f"- Schema-validation failure count from compile run: `{quality['schema_validation_failure_count']}`",
            "",
            "## Do Not Runtime Promote Without Rewrite Review",
            "",
            "| affordance_id | reason | future trigger condition |",
            "| --- | --- | --- |",
        ]
    )
    for flag in quality["do_not_promote_flags"]:
        lines.append(
            "| "
            f"`{flag['affordance_id']}` | "
            f"{flag['reason']} | "
            f"{flag['future_trigger_condition']} |"
        )

    lines.extend(
        [
            "",
            "## Per-Model Summary",
            "",
            "| model_id | affordance count | absence count | dominant confidence | flags |",
            "| --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in quality["per_model_summary"]:
        flags = ", ".join(f"`{flag}`" for flag in row["flags"]) or "none"
        lines.append(
            "| "
            f"`{row['model_id']}` | "
            f"{row['affordance_count']} | "
            f"{row['absence_count']} | "
            f"`{row['dominant_confidence']}` | "
            f"{flags} |"
        )

    lines.extend(
        [
            "",
            "## Cross-Model Deterministic Observations",
            "",
            "### Identical Extraction-Type Distributions",
            "",
        ]
    )
    if quality["identical_extraction_type_distributions"]:
        for item in quality["identical_extraction_type_distributions"]:
            lines.append(
                f"- {', '.join(item['model_ids'])}: `{item['distribution']}`"
            )
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "### Affordances With Short Source Quotes",
            "",
            f"Median affordance-level source quote length: `{quality['source_quote_length_median']}` characters.",
            "",
        ]
    )
    if quality["affordances_with_short_source_quotes"]:
        for item in quality["affordances_with_short_source_quotes"]:
            lines.append(
                "- "
                f"`{item['affordance_id']}`: shortest quote `{item['shortest_quote_length']}` chars "
                f"across `{item['quote_count']}` quote(s)"
            )
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "### Review Notes With Empty Dropped Material",
            "",
        ]
    )
    if quality["empty_dropped_material_notes"]:
        for item in quality["empty_dropped_material_notes"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## What This Report Deliberately Omits",
            "",
            "- No completeness ratios.",
            "- No coverage-style scoring.",
            "- No quality grade.",
            "- No automated drop or rewrite recommendations.",
            "- No semantic genericity scoring beyond PR 1 validation.",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_compiled_artifact(
    *,
    records: list[dict[str, object]],
    record_paths: dict[str, Path],
    pilot_manifest: dict[str, object],
    source_manifest: dict[str, object],
    schema: dict[str, object],
    validation_summary: dict[str, object],
) -> dict[str, object]:
    records = sorted(records, key=lambda record: str(record["model_id"]))
    affordances = []
    absence_records = []
    for record in records:
        model_id = str(record["model_id"])
        for affordance in _list(record["affordances"]):
            item = copy.deepcopy(_dict(affordance))
            item["model_id"] = model_id
            affordances.append(item)
        for absence in _list(record["absence_records"]):
            item = copy.deepcopy(_dict(absence))
            item["model_id"] = model_id
            absence_records.append(item)

    source_files = sorted(
        copy.deepcopy(_list(source_manifest["files"])),
        key=lambda item: str(_dict(item)["model_id"]),
    )
    compile_date = str(pilot_manifest.get("created_date") or "unknown")
    compiled_at = f"{compile_date}T00:00:00Z" if compile_date != "unknown" else "unknown"
    compiled = {
        "artifact": "model_affordances_v1",
        "status": "draft_review_only",
        "compile_metadata": {
            "compiled_at": compiled_at,
            "compiler": "scripts/compile_model_affordances.py",
            "contributing_record_count": len(records),
            "affordance_count": len(affordances),
            "absence_record_count": len(absence_records),
            "schema_id": schema.get("$id", ""),
            "schema_version": "model_affordance.schema.json",
            "source_hash_algorithm": source_manifest["hash_algorithm"],
            "source_files": source_files,
            "record_paths": {
                model_id: str(path.relative_to(REPO_ROOT))
                if path.is_relative_to(REPO_ROOT)
                else str(path)
                for model_id, path in sorted(record_paths.items())
            },
            "validation": {
                "schema_validation_failure_count": validation_summary[
                    "schema_validation_failure_count"
                ],
                "source_quote_rejection_count": validation_summary[
                    "source_quote_rejection_count"
                ],
                "source_hash_failure_count": 0,
            },
        },
        "source_residency": copy.deepcopy(_dict(pilot_manifest["source_residency"])),
        "do_not_runtime_promote_without_rewrite_review": list(DO_NOT_PROMOTE_FLAGS),
        "model_records": copy.deepcopy(records),
        "affordances": sorted(affordances, key=lambda item: str(item["affordance_id"])),
        "absence_records": sorted(
            absence_records,
            key=lambda item: (str(item["model_id"]), str(item["attempted_field"])),
        ),
    }
    compiled["quality_signals"] = _quality_signals(compiled)
    return compiled


def _quality_signals(compiled: dict[str, object]) -> dict[str, object]:
    records = _records(compiled)
    flags_by_id = {
        str(flag["affordance_id"]): flag
        for flag in _list(compiled["do_not_runtime_promote_without_rewrite_review"])
    }
    affordance_count_distribution: dict[str, list[str]] = defaultdict(list)
    absence_status_counts: Counter[str] = Counter()
    affordance_confidence_counts: Counter[str] = Counter()
    affordance_status_counts: Counter[str] = Counter()
    per_model_summary = []
    extraction_groups: dict[tuple[tuple[str, int], ...], list[str]] = defaultdict(list)
    empty_dropped_material_notes: list[str] = []
    affordance_quote_lengths: list[int] = []
    affordance_shortest_quotes: list[dict[str, object]] = []

    for record in records:
        model_id = str(record["model_id"])
        affordances = [_dict(item) for item in _list(record["affordances"])]
        absences = [_dict(item) for item in _list(record["absence_records"])]
        affordance_count_distribution[str(len(affordances))].append(model_id)
        for absence in absences:
            absence_status_counts[str(absence["status"])] += 1
        for affordance in affordances:
            affordance_confidence_counts[str(affordance["confidence"])] += 1
            affordance_status_counts[str(affordance["status"])] += 1

        confidence_counts = Counter(str(item["confidence"]) for item in affordances)
        dominant_confidence = _dominant_counter_key(confidence_counts)
        model_flags = [
            str(affordance["affordance_id"])
            for affordance in affordances
            if str(affordance["affordance_id"]) in flags_by_id
        ]
        per_model_summary.append(
            {
                "model_id": model_id,
                "affordance_count": len(affordances),
                "absence_count": len(absences),
                "dominant_confidence": dominant_confidence,
                "flags": model_flags,
            }
        )

        extraction_counter = Counter(
            str(evidence["extraction_type"]) for evidence in _iter_all_evidence(record)
        )
        extraction_groups[tuple(sorted(extraction_counter.items()))].append(model_id)

        review_notes = _dict(record["review_notes"])
        if not _list(review_notes.get("dropped_material", [])):
            empty_dropped_material_notes.append(f"{model_id}.review_notes")
        for affordance in affordances:
            if "review_notes" in affordance and not _list(
                _dict(affordance["review_notes"]).get("dropped_material", [])
            ):
                empty_dropped_material_notes.append(
                    f"{affordance['affordance_id']}.review_notes"
                )
            lengths = [
                len(str(evidence["source_quote"]))
                for evidence in _list(affordance["source_evidence"])
            ]
            affordance_quote_lengths.extend(lengths)
            if lengths:
                affordance_shortest_quotes.append(
                    {
                        "affordance_id": affordance["affordance_id"],
                        "shortest_quote_length": min(lengths),
                        "quote_count": len(lengths),
                    }
                )

    median_quote_length = (
        int(statistics.median(affordance_quote_lengths))
        if affordance_quote_lengths
        else 0
    )
    affordances_with_short_source_quotes = sorted(
        [
            item
            for item in affordance_shortest_quotes
            if int(item["shortest_quote_length"]) < median_quote_length
        ],
        key=lambda item: (int(item["shortest_quote_length"]), str(item["affordance_id"])),
    )
    identical_extraction_type_distributions = []
    for distribution, model_ids in sorted(
        extraction_groups.items(), key=lambda item: (-len(item[1]), str(item[0]))
    ):
        if len(model_ids) < 2:
            continue
        identical_extraction_type_distributions.append(
            {
                "distribution": dict(distribution),
                "model_ids": sorted(model_ids),
            }
        )

    validation = _dict(_dict(compiled["compile_metadata"])["validation"])
    return {
        "affordance_count_distribution": {
            count: sorted(model_ids)
            for count, model_ids in sorted(
                affordance_count_distribution.items(), key=lambda item: int(item[0])
            )
        },
        "absence_status_counts": _ordered_counts(absence_status_counts),
        "affordance_confidence_counts": _ordered_counts(
            affordance_confidence_counts,
            order=CONFIDENCE_ORDER,
            include_zero=True,
        ),
        "affordance_status_counts": _ordered_counts(
            affordance_status_counts,
            order=AFFORDANCE_STATUS_ORDER,
            include_zero=True,
        ),
        "source_quote_rejection_count": validation["source_quote_rejection_count"],
        "schema_validation_failure_count": validation["schema_validation_failure_count"],
        "do_not_promote_flags": list(DO_NOT_PROMOTE_FLAGS),
        "per_model_summary": sorted(per_model_summary, key=lambda item: item["model_id"]),
        "identical_extraction_type_distributions": identical_extraction_type_distributions,
        "source_quote_length_median": median_quote_length,
        "affordances_with_short_source_quotes": affordances_with_short_source_quotes,
        "empty_dropped_material_notes": sorted(empty_dropped_material_notes),
    }


def _validate_records(
    *,
    records: list[dict[str, object]],
    record_paths: dict[str, Path],
    source_dir: Path,
) -> dict[str, object]:
    errors: list[str] = []
    schema_failure_count = 0
    source_quote_rejection_count = 0
    for record in records:
        model_id = str(record.get("model_id", "<record>"))
        record_errors = list(
            iter_model_affordance_errors(
                record,
                path=record_paths.get(model_id, Path(model_id)),
                source_roots=(source_dir,),
            )
        )
        for error in record_errors:
            if "source_quote is not an exact substring" in error:
                source_quote_rejection_count += 1
            else:
                schema_failure_count += 1
            errors.append(error)
    return {
        "schema_validation_failure_count": schema_failure_count,
        "source_quote_rejection_count": source_quote_rejection_count,
        "errors": errors,
    }


def _source_hash_failures(
    *,
    source_dir: Path,
    source_manifest: dict[str, object],
) -> list[str]:
    failures: list[str] = []
    if source_manifest.get("hash_algorithm") != "sha256":
        failures.append("unsupported source hash algorithm")
        return failures
    for entry in _list(source_manifest.get("files", [])):
        item = _dict(entry)
        filename = str(item.get("filename") or Path(str(item["path"])).name)
        path = source_dir / filename
        if not path.exists():
            failures.append(f"{path}: missing source file")
            continue
        data = path.read_bytes()
        actual_hash = hashlib.sha256(data).hexdigest()
        if actual_hash != item["sha256"]:
            failures.append(f"{path}: sha256 mismatch")
        if len(data) != item["bytes"]:
            failures.append(f"{path}: byte count mismatch")
    return failures


def _load_records_from_manifest(
    *,
    root: Path,
    record_dir: Path,
    pilot_manifest: dict[str, object],
) -> tuple[list[dict[str, object]], dict[str, Path]]:
    records = []
    record_paths: dict[str, Path] = {}
    seen_paths = set()
    for manifest_record in _list(pilot_manifest["records"]):
        manifest_item = _dict(manifest_record)
        manifest_path = Path(str(manifest_item["record_path"]))
        path = record_dir / manifest_path.name
        if not path.exists():
            path = _resolve(root, manifest_path)
        if path in seen_paths:
            raise ModelAffordanceCompilationError(f"duplicate record path: {path}")
        seen_paths.add(path)
        if path.parent != record_dir:
            raise ModelAffordanceCompilationError(f"record path outside record_dir: {path}")
        record = _load_object(path)
        if record["model_id"] != manifest_item["model_id"]:
            raise ModelAffordanceCompilationError(f"{path}: model_id does not match pilot manifest")
        record_paths[str(record["model_id"])] = path
        records.append(record)
    return records, record_paths


def _iter_all_evidence(record: dict[str, object]) -> Iterable[dict[str, object]]:
    for evidence in _list(record.get("source_evidence", [])):
        yield _dict(evidence)
    for affordance in _list(record.get("affordances", [])):
        for evidence in _list(_dict(affordance).get("source_evidence", [])):
            yield _dict(evidence)
    for absence in _list(record.get("absence_records", [])):
        for evidence in _list(_dict(absence).get("source_evidence", [])):
            yield _dict(evidence)


def _ordered_counts(
    counter: Counter[str],
    *,
    order: Iterable[str] = (),
    include_zero: bool = False,
) -> dict[str, int]:
    ordered = {}
    ordered_keys = tuple(order)
    for key in ordered_keys:
        if include_zero or counter[key]:
            ordered[key] = counter[key]
    for key in sorted(set(counter).difference(ordered_keys)):
        ordered[key] = counter[key]
    return ordered


def _dominant_counter_key(counter: Counter[str]) -> str:
    if not counter:
        return "not_applicable"
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _records(compiled: dict[str, object]) -> list[dict[str, object]]:
    return [_dict(item) for item in _list(compiled["model_records"])]


def _load_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ModelAffordanceCompilationError(f"{path}: expected JSON object")
    return payload


def _resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def _dict(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ModelAffordanceCompilationError(f"expected object, got {type(value).__name__}")
    return value


def _list(value: object) -> list[object]:
    if not isinstance(value, list):
        raise ModelAffordanceCompilationError(f"expected list, got {type(value).__name__}")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compile draft model affordance records and quality report."
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--record-dir", type=Path, default=DEFAULT_RECORD_DIR)
    parser.add_argument("--pilot-manifest", type=Path, default=DEFAULT_PILOT_MANIFEST_PATH)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST_PATH)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    try:
        result = compile_model_affordances(
            root=args.root,
            record_dir=args.record_dir,
            pilot_manifest_path=args.pilot_manifest,
            source_dir=args.source_dir,
            source_manifest_path=args.source_manifest,
            schema_path=args.schema,
            output_dir=args.output_dir,
        )
    except ModelAffordanceCompilationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {result.compiled_path}")
    print(f"Wrote {result.quality_report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
