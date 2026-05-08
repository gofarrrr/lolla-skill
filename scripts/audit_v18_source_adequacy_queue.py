from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AFFORDANCES_PATH = Path("data/compiled/model_affordances/affordances_v18.json")

BROAD_META_MODELS = {
    "systems-thinking",
    "latticework-of-mental-models",
    "chain-of-thought",
    "meta-cognitive-reflection",
    "mental-models-of-reality",
    "reasoning-mode-router",
    "system-1",
    "system-2",
    "complexity-bias-resistance",
    "logical-fallacies",
    "circle-of-competence",
    "intellectual-humility",
    "cognitive-biases",
    "critical-thinking",
    "metacognitive-questioning",
}

LATE_CONTROLLED_BATCHES = {
    "batch_10",
    "batch_11",
    "batch_12",
    "batch_13",
    "batch_14",
    "batch_15",
    "batch_16",
    "batch_17",
}


@dataclass(frozen=True)
class ModelRiskRow:
    model_id: str
    score: int
    priority: str
    flags: tuple[str, ...]
    affordance_count: int
    absence_count: int
    max_source_refs: int
    total_source_refs: int
    dominant_confidence: str
    record_status: str
    record_path: str
    source_path: str
    source_bytes: int


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a deterministic PR56 source-adequacy risk queue."
    )
    parser.add_argument(
        "--affordances-path",
        default=DEFAULT_AFFORDANCES_PATH,
        type=Path,
        help="Compiled affordance artifact to inspect.",
    )
    parser.add_argument(
        "--top",
        default=80,
        type=int,
        help="Number of queue rows to print.",
    )
    args = parser.parse_args()

    artifact_path = _resolve(args.affordances_path)
    payload = _load_json(artifact_path)
    rows = build_risk_rows(payload)
    print(render_markdown(payload, rows, top=args.top, artifact_path=artifact_path))


def build_risk_rows(payload: dict[str, Any]) -> list[ModelRiskRow]:
    metadata = _dict(payload.get("compile_metadata"))
    record_paths = _dict(metadata.get("record_paths"))
    source_files = {
        str(item.get("model_id")): item
        for item in _list(metadata.get("source_files"))
        if isinstance(item, dict) and item.get("model_id")
    }
    do_not_promote = {
        str(item.get("affordance_id"))
        for item in _list(payload.get("do_not_runtime_promote_without_rewrite_review"))
        if isinstance(item, dict) and item.get("affordance_id")
    }

    rows: list[ModelRiskRow] = []
    for record in _list(payload.get("model_records")):
        if not isinstance(record, dict):
            continue
        model_id = str(record.get("model_id") or "")
        if not model_id:
            continue
        affordances = [item for item in _list(record.get("affordances")) if isinstance(item, dict)]
        absences = [item for item in _list(record.get("absence_records")) if isinstance(item, dict)]
        confidences = Counter(str(item.get("confidence") or "unknown") for item in affordances)
        dominant_confidence = _dominant_confidence(confidences)
        source_ref_counts = [
            len([ev for ev in _list(item.get("source_evidence")) if isinstance(ev, dict)])
            for item in affordances
        ]
        record_path = str(record_paths.get(model_id) or "")
        source_info = _dict(source_files.get(model_id))
        source_path = str(source_info.get("path") or "")
        source_bytes = int(source_info.get("bytes") or 0)
        flags = risk_flags(
            model_id=model_id,
            record=record,
            affordances=affordances,
            absences=absences,
            dominant_confidence=dominant_confidence,
            source_ref_counts=source_ref_counts,
            record_path=record_path,
            source_bytes=source_bytes,
            do_not_promote=do_not_promote,
        )
        score = risk_score(flags)
        rows.append(
            ModelRiskRow(
                model_id=model_id,
                score=score,
                priority=priority_for_score(score),
                flags=tuple(flags),
                affordance_count=len(affordances),
                absence_count=len(absences),
                max_source_refs=max(source_ref_counts, default=0),
                total_source_refs=sum(source_ref_counts),
                dominant_confidence=dominant_confidence,
                record_status=str(record.get("status") or "unknown"),
                record_path=record_path,
                source_path=source_path,
                source_bytes=source_bytes,
            )
        )
    return sorted(rows, key=lambda row: (-row.score, row.model_id))


def risk_flags(
    *,
    model_id: str,
    record: dict[str, Any],
    affordances: list[dict[str, Any]],
    absences: list[dict[str, Any]],
    dominant_confidence: str,
    source_ref_counts: list[int],
    record_path: str,
    source_bytes: int,
    do_not_promote: set[str],
) -> list[str]:
    flags: list[str] = []
    affordance_count = len(affordances)
    absence_count = len(absences)
    affordance_ids = {str(item.get("affordance_id") or "") for item in affordances}
    record_status = str(record.get("status") or "")

    if record_status == "weak_support" or any(
        str(item.get("status") or "") == "weak_support" for item in affordances
    ):
        flags.append("weak_support")
    if dominant_confidence in {"medium", "weak"}:
        flags.append(f"{dominant_confidence}_confidence")
    if affordance_ids.intersection(do_not_promote):
        flags.append("do_not_promote_without_rewrite_review")
    if absence_count == 0:
        flags.append("zero_absence_records")
    if model_id in BROAD_META_MODELS:
        flags.append("broad_meta_model")
    if affordance_count >= 2:
        flags.append("multi_affordance_grouping_needed")
    if affordance_count == 1 and max(source_ref_counts, default=0) >= 12:
        flags.append("one_affordance_high_source_refs")
    if source_bytes >= 18_000:
        flags.append("large_source_file")
    if affordance_count == 1 and any(batch in record_path for batch in LATE_CONTROLLED_BATCHES):
        flags.append("late_controlled_one_affordance")
    if absence_count >= 3:
        flags.append("absence_heavy")
    return flags


def risk_score(flags: list[str]) -> int:
    weights = {
        "do_not_promote_without_rewrite_review": 9,
        "weak_support": 8,
        "medium_confidence": 5,
        "weak_confidence": 7,
        "zero_absence_records": 5,
        "broad_meta_model": 4,
        "one_affordance_high_source_refs": 4,
        "multi_affordance_grouping_needed": 3,
        "late_controlled_one_affordance": 3,
        "large_source_file": 2,
        "absence_heavy": 2,
    }
    return sum(weights.get(flag, 0) for flag in flags)


def priority_for_score(score: int) -> str:
    if score >= 14:
        return "P0"
    if score >= 9:
        return "P1"
    if score >= 5:
        return "P2"
    return "P3"


def render_markdown(
    payload: dict[str, Any], rows: list[ModelRiskRow], *, top: int, artifact_path: Path
) -> str:
    counter = Counter(flag for row in rows for flag in row.flags)
    priorities = Counter(row.priority for row in rows)
    lines = [
        "# PR56 v18 Source Adequacy Risk Queue",
        "",
        "Generated by `scripts/audit_v18_source_adequacy_queue.py`.",
        "",
        "This queue is deterministic prioritization for human source review. It does not grade final quality, infer missing affordances, or promote runtime use.",
        "",
        "## Artifact",
        "",
        f"- Path: `{_rel(artifact_path)}`",
        f"- Artifact: `{payload.get('artifact')}`",
        f"- Status: `{payload.get('status')}`",
        f"- Records: `{len(_list(payload.get('model_records')))}`",
        f"- Affordances: `{len(_list(payload.get('affordances')))}`",
        f"- Absence records: `{len(_list(payload.get('absence_records')))}`",
        "",
        "## Priority Distribution",
        "",
        "| Priority | Count |",
        "| --- | ---: |",
    ]
    for priority in ("P0", "P1", "P2", "P3"):
        lines.append(f"| `{priority}` | {priorities.get(priority, 0)} |")

    lines.extend(
        [
            "",
            "## Flag Distribution",
            "",
            "| Flag | Count |",
            "| --- | ---: |",
        ]
    )
    for flag, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{flag}` | {count} |")

    lines.extend(
        [
            "",
            f"## Top {top} Review Queue",
            "",
            "| priority | score | model_id | aff | abs | max refs | confidence | flags | source |",
            "| --- | ---: | --- | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in rows[:top]:
        flags = ", ".join(f"`{flag}`" for flag in row.flags) or "none"
        lines.append(
            "| "
            f"`{row.priority}` | {row.score} | `{row.model_id}` | "
            f"{row.affordance_count} | {row.absence_count} | {row.max_source_refs} | "
            f"`{row.dominant_confidence}` | {flags} | `{row.source_path}` |"
        )

    lines.extend(
        [
            "",
            "## Review Rule",
            "",
            "Reviewers should not rewrite records from this queue directly. For each model, first decide whether the current record is:",
            "",
            "- `complete_as_compressed`",
            "- `split_candidate`",
            "- `needs_absence_enrichment`",
            "- `needs_affordance_rewrite`",
            "- `source_too_thin`",
            "- `too_broad_for_runtime`",
            "- `packet_shape_blocker_only`",
            "",
            "A split candidate requires evidence that a source-supported cluster would change downstream use/reject/defer/merge/block behavior.",
        ]
    )
    return "\n".join(lines)


def _dominant_confidence(counter: Counter[str]) -> str:
    if not counter:
        return "unknown"
    order = {"weak": 0, "medium": 1, "high": 2, "not_applicable": 3}
    return sorted(counter.items(), key=lambda item: (-item[1], order.get(item[0], 9), item[0]))[0][0]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    main()
