#!/usr/bin/env python3
"""Compare two pipeline result.json files for meaningful equivalence.

Used as the acceptance gate for Phase 1 (old-path vs new-path shim
equivalence) and as a regression tool for future lane migrations.

Meaningful fields (compared):
- detected_tendencies                           (list[str])
- delta_card.findings                           (list[dict])
- companion_cheat_sheet.anchors                 (list[dict])
- frame_pressure_card.reframings                (list[dict])
- structural_coverage_card.gap_questions        (list[dict])
- audit_summary.triggered_tendencies            (list[str])

Skipped (noise):
- Timing fields (*_seconds, etc.)
- boundary_calls metadata (tokens, timestamps, provider info)
- run_health timings

Usage:
    python3 scripts/compare_outputs.py path/to/old.json path/to/new.json
    # exit code 0 = all meaningful fields match; 1 = one or more mismatches

Programmatic use:
    from scripts.compare_outputs import compare_results, Comparison
    report = compare_results(old_payload, new_payload)
    if not report.all_match:
        ...
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


# A (name, extractor) pair. Extractor pulls the value from a result payload;
# missing paths become empty list / None so absence vs. absence still matches.
_FIELD_EXTRACTORS: tuple[tuple[str, Callable[[dict], Any]], ...] = (
    ("detected_tendencies",
     lambda r: r.get("detected_tendencies", [])),
    ("delta_card.findings",
     lambda r: (r.get("delta_card") or {}).get("findings", [])),
    ("companion_cheat_sheet.anchors",
     lambda r: (r.get("companion_cheat_sheet") or {}).get("anchors", [])),
    ("frame_pressure_card.reframings",
     lambda r: (r.get("frame_pressure_card") or {}).get("reframings", [])),
    ("structural_coverage_card.gap_questions",
     lambda r: (r.get("structural_coverage_card") or {}).get("gap_questions", [])),
    ("audit_summary.triggered_tendencies",
     lambda r: (r.get("audit_summary") or {}).get("triggered_tendencies", [])),
)


@dataclass(frozen=True)
class FieldComparison:
    field_name: str
    match: bool
    left: Any = None
    right: Any = None


@dataclass(frozen=True)
class Comparison:
    fields: tuple[FieldComparison, ...]

    @property
    def all_match(self) -> bool:
        return all(f.match for f in self.fields)

    @property
    def mismatches(self) -> tuple[FieldComparison, ...]:
        return tuple(f for f in self.fields if not f.match)


def compare_results(left: dict, right: dict) -> Comparison:
    results: list[FieldComparison] = []
    for name, extractor in _FIELD_EXTRACTORS:
        l_val = extractor(left)
        r_val = extractor(right)
        match = l_val == r_val
        results.append(
            FieldComparison(
                field_name=name,
                match=match,
                left=l_val if not match else None,
                right=r_val if not match else None,
            )
        )
    return Comparison(fields=tuple(results))


def render_report(comparison: Comparison, *, left_label: str = "left", right_label: str = "right") -> str:
    lines: list[str] = []
    lines.append(f"comparing {left_label}  vs  {right_label}")
    lines.append("")
    width = max(len(f.field_name) for f in comparison.fields)
    for f in comparison.fields:
        status = "MATCH " if f.match else "DIFFER"
        lines.append(f"  [{status}] {f.field_name.ljust(width)}")
    lines.append("")
    if comparison.all_match:
        lines.append("result: all 6 meaningful fields match.")
    else:
        lines.append(f"result: {len(comparison.mismatches)} of {len(comparison.fields)} fields diverge.")
        lines.append("")
        for f in comparison.mismatches:
            lines.append(f"--- {f.field_name} ---")
            lines.append(f"  {left_label}: {json.dumps(f.left, indent=2, ensure_ascii=False)}")
            lines.append(f"  {right_label}: {json.dumps(f.right, indent=2, ensure_ascii=False)}")
            lines.append("")
    return "\n".join(lines)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare two pipeline result.json files on meaningful fields",
    )
    parser.add_argument("left", type=Path, help="First result.json path (e.g. old-path)")
    parser.add_argument("right", type=Path, help="Second result.json path (e.g. new-path)")
    parser.add_argument(
        "--left-label",
        default=None,
        help="Label for the first file in the report (default: filename)",
    )
    parser.add_argument(
        "--right-label",
        default=None,
        help="Label for the second file in the report (default: filename)",
    )
    args = parser.parse_args()

    left_payload = _load(args.left)
    right_payload = _load(args.right)

    report = compare_results(left_payload, right_payload)
    print(render_report(
        report,
        left_label=args.left_label or args.left.name,
        right_label=args.right_label or args.right.name,
    ))

    return 0 if report.all_match else 1


if __name__ == "__main__":
    sys.exit(main())
