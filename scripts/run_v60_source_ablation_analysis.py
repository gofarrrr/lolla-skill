#!/usr/bin/env python3
"""Run C4.6 source ablation over existing v60 replay artifacts.

This is a no-new-token analysis. It reuses the paid C4.5 system-bound composer
run and asks what visible value came from strict lane-preserved opportunities
versus embedding/absence/hybrid-enriched opportunities.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


SOURCE_ABLATION_VERSION = "v60_source_ablation_analysis.v1"
DEFAULT_C45_DIR = Path(
    "data/evaluations/v60_transaction_replay_lab/2026-05-10-c45-system-bound-enrichment-paid"
)
DEFAULT_C45_SUMMARY = "summary_revalidated_numeric_guard.json"
DEFAULT_C44_SUMMARY = Path(
    "data/evaluations/v60_transaction_replay_lab/"
    "2026-05-10-c44c-exact-chunk-private-replay-hardened-paid/"
    "summary_revalidated.json"
)
DEFAULT_EMBEDDING_SUMMARY = Path(
    "data/evaluations/v60_transaction_embedding_lab/"
    "2026-05-10-v60-embedding-pickup-absence-view/summary.json"
)
DEFAULT_OUTPUT_DIR = Path(
    "data/evaluations/v60_transaction_replay_lab/2026-05-10-c46-source-ablation-analysis"
)
LANE_SOURCE = "lane_preserved"
ENHANCED_SOURCES = frozenset(
    {"embedding_affordance_exact", "embedding_absence_exact", "hybrid_rrf_exact"}
)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = REPO_ROOT
    c45_dir = resolve(root, args.c45_dir)
    c45_summary_path = c45_dir / args.c45_summary
    output_dir = resolve(root, args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    c45_summary = load_json(c45_summary_path)
    c44_summary = load_optional_json(resolve(root, args.c44_summary))
    embedding_summary = load_optional_json(resolve(root, args.embedding_summary))
    analysis = analyze(
        c45_dir=c45_dir,
        c45_summary=c45_summary,
        c44_summary=c44_summary,
        embedding_summary=embedding_summary,
    )
    write_json(output_dir / "summary.json", analysis)
    (output_dir / "source_ablation_report.md").write_text(render_report(analysis), encoding="utf-8")
    print(f"wrote {output_dir / 'summary.json'}")
    print(f"wrote {output_dir / 'source_ablation_report.md'}")
    return 0


def analyze(
    *,
    c45_dir: Path,
    c45_summary: Mapping[str, Any],
    c44_summary: Mapping[str, Any],
    embedding_summary: Mapping[str, Any],
) -> dict[str, Any]:
    case_rows = []
    aggregate = {
        "case_count": 0,
        "opportunity_count": 0,
        "strict_lane_opportunity_count": 0,
        "lane_inclusive_opportunity_count": 0,
        "enhanced_opportunity_count": 0,
        "mixed_source_opportunity_count": 0,
        "safe_public_delta_count": 0,
        "unsafe_public_delta_count": 0,
        "strict_lane_safe_public_delta_count": 0,
        "lane_inclusive_safe_public_delta_count": 0,
        "enhanced_safe_public_delta_count": 0,
        "strict_lane_unsafe_public_delta_count": 0,
        "enhanced_unsafe_public_delta_count": 0,
    }
    opportunity_source_counts: Counter[str] = Counter()
    opportunity_route_by_class: dict[str, Counter[str]] = defaultdict(Counter)
    admitted_safe_by_class: Counter[str] = Counter()
    admitted_unsafe_by_class: Counter[str] = Counter()
    admitted_safe_by_source: Counter[str] = Counter()
    admitted_unsafe_by_source: Counter[str] = Counter()

    for item in (mapping(row) for row in list_of(c45_summary.get("items"))):
        profile = load_json(c45_dir / text(item.get("system_profile_path")))
        output = load_json(c45_dir / text(item.get("composer_output_path")))
        validation = mapping(item.get("composer_validation"))
        opportunities = {
            text(opp.get("opportunity_id")): mapping(opp)
            for opp in list_of(profile.get("composer_opportunities"))
            if text(mapping(opp).get("opportunity_id"))
        }
        case_opportunities = []
        for opportunity in opportunities.values():
            source_mix = sorted(strings(opportunity.get("source_mix")))
            source_class = classify_sources(source_mix)
            aggregate["opportunity_count"] += 1
            if source_class == "strict_lane":
                aggregate["strict_lane_opportunity_count"] += 1
            if LANE_SOURCE in source_mix:
                aggregate["lane_inclusive_opportunity_count"] += 1
            if any(source in ENHANCED_SOURCES for source in source_mix):
                aggregate["enhanced_opportunity_count"] += 1
            if source_class == "mixed_lane_enhanced":
                aggregate["mixed_source_opportunity_count"] += 1
            for source in source_mix:
                opportunity_source_counts[source] += 1
            opportunity_route_by_class[source_class][text(opportunity.get("route"))] += 1
            case_opportunities.append(
                {
                    "opportunity_id": text(opportunity.get("opportunity_id")),
                    "route": text(opportunity.get("route")),
                    "source_mix": source_mix,
                    "source_class": source_class,
                    "model_ids": strings(opportunity.get("model_ids")),
                    "private_value": text(opportunity.get("private_value")),
                }
            )

        admitted_items = []
        for admitted in (mapping(row) for row in list_of(output.get("admitted_items"))):
            public_delta = text(admitted.get("public_delta"))
            if not public_delta:
                continue
            source_ids = strings(admitted.get("source_opportunity_ids"))
            source_mix = sorted(
                {
                    source
                    for source_id in source_ids
                    for source in strings(opportunities.get(source_id, {}).get("source_mix"))
                }
            )
            source_class = classify_sources(source_mix)
            safe = text(validation.get("status")) == "valid"
            if safe:
                aggregate["safe_public_delta_count"] += 1
                admitted_safe_by_class[source_class] += 1
                for source in source_mix:
                    admitted_safe_by_source[source] += 1
                if source_class == "strict_lane":
                    aggregate["strict_lane_safe_public_delta_count"] += 1
                if LANE_SOURCE in source_mix:
                    aggregate["lane_inclusive_safe_public_delta_count"] += 1
                if any(source in ENHANCED_SOURCES for source in source_mix):
                    aggregate["enhanced_safe_public_delta_count"] += 1
            else:
                aggregate["unsafe_public_delta_count"] += 1
                admitted_unsafe_by_class[source_class] += 1
                for source in source_mix:
                    admitted_unsafe_by_source[source] += 1
                if source_class == "strict_lane":
                    aggregate["strict_lane_unsafe_public_delta_count"] += 1
                if any(source in ENHANCED_SOURCES for source in source_mix):
                    aggregate["enhanced_unsafe_public_delta_count"] += 1
            admitted_items.append(
                {
                    "source_opportunity_ids": source_ids,
                    "source_mix": source_mix,
                    "source_class": source_class,
                    "safe_after_validation": safe,
                    "delta_type": text(admitted.get("delta_type")),
                    "public_delta": public_delta,
                    "quality_value": text(admitted.get("quality_value")),
                    "friction_cost": text(admitted.get("friction_cost")),
                    "why_admitted": text(admitted.get("why_admitted")),
                }
            )

        case_rows.append(
            {
                "case_id": text(item.get("case_id")),
                "composer_validation_status": text(validation.get("status")),
                "composer_errors": strings(validation.get("errors")),
                "admission_decision": text(validation.get("admission_decision")),
                "opportunity_count": len(opportunities),
                "strict_lane_opportunity_count": sum(
                    1 for row in case_opportunities if row["source_class"] == "strict_lane"
                ),
                "enhanced_opportunity_count": sum(
                    1
                    for row in case_opportunities
                    if any(source in ENHANCED_SOURCES for source in row["source_mix"])
                ),
                "opportunities": case_opportunities,
                "admitted_public_items": admitted_items,
            }
        )

    aggregate["case_count"] = len(case_rows)
    aggregate["strict_lane_counterfactual_safe_public_delta_lower_bound"] = aggregate[
        "strict_lane_safe_public_delta_count"
    ]
    aggregate["enhanced_incremental_safe_public_delta_lower_bound"] = (
        aggregate["safe_public_delta_count"]
        - aggregate["strict_lane_counterfactual_safe_public_delta_lower_bound"]
    )
    aggregate["opportunity_source_counts"] = dict(sorted(opportunity_source_counts.items()))
    aggregate["opportunity_route_by_class"] = {
        key: dict(sorted(counter.items())) for key, counter in sorted(opportunity_route_by_class.items())
    }
    aggregate["admitted_safe_by_class"] = dict(sorted(admitted_safe_by_class.items()))
    aggregate["admitted_unsafe_by_class"] = dict(sorted(admitted_unsafe_by_class.items()))
    aggregate["admitted_safe_by_source"] = dict(sorted(admitted_safe_by_source.items()))
    aggregate["admitted_unsafe_by_source"] = dict(sorted(admitted_unsafe_by_source.items()))

    c45_aggregate = mapping(c45_summary.get("aggregate"))
    c44_aggregate = mapping(c44_summary.get("aggregate"))
    embedding_aggregate = mapping(embedding_summary.get("aggregate"))

    return {
        "source_ablation_version": SOURCE_ABLATION_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_mode": "no_new_token_artifact_ablation",
        "inputs": {
            "c45_summary": text(c45_summary.get("system_bound_replay_version")),
            "c44_summary_present": bool(c44_summary),
            "embedding_summary_present": bool(embedding_summary),
        },
        "cost_context": {
            "new_model_calls_for_ablation": 0,
            "new_token_cost_usd_for_ablation": 0.0,
            "c45_existing_call_count": integer(c45_aggregate.get("call_count")),
            "c45_existing_cost_usd": c45_aggregate.get("cost_usd", 0),
            "c44_existing_call_count": integer(c44_aggregate.get("call_count")),
            "c44_existing_cost_usd": c44_aggregate.get("cost_usd", 0),
            "embedding_existing_call_count": integer(
                mapping(embedding_aggregate.get("embedding_usage")).get("call_count")
            ),
            "embedding_existing_tokens": integer(
                mapping(embedding_aggregate.get("embedding_usage")).get("total_tokens")
            ),
        },
        "definitions": {
            "strict_lane": "all source_mix values are lane_preserved",
            "lane_inclusive": "source_mix includes lane_preserved, possibly with enhanced sources",
            "enhanced": "source_mix includes embedding_affordance_exact, embedding_absence_exact, or hybrid_rrf_exact",
            "safe_public_delta": "composer output row validates after numeric/private-language guards",
            "lower_bound_warning": (
                "This no-new-token ablation uses the already-run full composer output. "
                "A filtered lane-only composer run could behave differently."
            ),
        },
        "aggregate": aggregate,
        "cases": case_rows,
    }


def classify_sources(source_mix: list[str]) -> str:
    sources = set(source_mix)
    if sources == {LANE_SOURCE}:
        return "strict_lane"
    if LANE_SOURCE in sources and any(source in ENHANCED_SOURCES for source in sources):
        return "mixed_lane_enhanced"
    if "embedding_absence_exact" in sources and len(sources) == 1:
        return "embedding_absence"
    if "embedding_affordance_exact" in sources and len(sources) == 1:
        return "embedding_affordance"
    if "hybrid_rrf_exact" in sources and len(sources) == 1:
        return "hybrid_rrf"
    if any(source in ENHANCED_SOURCES for source in sources):
        return "enhanced_other"
    return "unknown"


def render_report(analysis: Mapping[str, Any]) -> str:
    aggregate = mapping(analysis.get("aggregate"))
    cost = mapping(analysis.get("cost_context"))
    lines = [
        "# V60 C4.6 Source Ablation Analysis",
        "",
        f"Date: {text(analysis.get('generated_at'))[:10]}",
        "Mode: no-new-token artifact ablation",
        "",
        "## Cost",
        "",
        f"- New model calls for this ablation: {integer(cost.get('new_model_calls_for_ablation'))}",
        f"- New token cost for this ablation: `${cost.get('new_token_cost_usd_for_ablation', 0)}`",
        f"- Existing C4.5 composer cost reused: `${cost.get('c45_existing_cost_usd', 0)}`",
        f"- Existing C4.4 private trace cost reused: `${cost.get('c44_existing_cost_usd', 0)}`",
        "",
        "## Aggregate",
        "",
        f"- Cases: {integer(aggregate.get('case_count'))}",
        f"- Composer opportunities: {integer(aggregate.get('opportunity_count'))}",
        f"- Strict lane-only opportunities: {integer(aggregate.get('strict_lane_opportunity_count'))}",
        f"- Enhanced opportunities: {integer(aggregate.get('enhanced_opportunity_count'))}",
        f"- Mixed lane+enhanced opportunities: {integer(aggregate.get('mixed_source_opportunity_count'))}",
        f"- Safe public deltas: {integer(aggregate.get('safe_public_delta_count'))}",
        f"- Strict lane safe public deltas: {integer(aggregate.get('strict_lane_safe_public_delta_count'))}",
        f"- Enhanced safe public deltas: {integer(aggregate.get('enhanced_safe_public_delta_count'))}",
        f"- Unsafe public deltas caught: {integer(aggregate.get('unsafe_public_delta_count'))}",
        f"- Lower-bound safe delta lift over strict lane-only: {integer(aggregate.get('enhanced_incremental_safe_public_delta_lower_bound'))}",
        f"- Opportunity source counts: `{json.dumps(mapping(aggregate.get('opportunity_source_counts')), sort_keys=True)}`",
        f"- Safe admitted by source: `{json.dumps(mapping(aggregate.get('admitted_safe_by_source')), sort_keys=True)}`",
        f"- Unsafe admitted by source: `{json.dumps(mapping(aggregate.get('admitted_unsafe_by_source')), sort_keys=True)}`",
        "",
        "## Items",
        "",
        "| Case | Opps | Strict Lane Opps | Enhanced Opps | Safe Public Deltas | Unsafe Deltas |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for case in (mapping(row) for row in list_of(analysis.get("cases"))):
        safe = sum(
            1
            for item in list_of(case.get("admitted_public_items"))
            if mapping(item).get("safe_after_validation")
        )
        unsafe = sum(
            1
            for item in list_of(case.get("admitted_public_items"))
            if not mapping(item).get("safe_after_validation")
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{text(case.get('case_id'))}`",
                    str(integer(case.get("opportunity_count"))),
                    str(integer(case.get("strict_lane_opportunity_count"))),
                    str(integer(case.get("enhanced_opportunity_count"))),
                    str(safe),
                    str(unsafe),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This is a counterfactual lower-bound analysis over an already-run full",
            "composer pass. It does not prove a separately prompted lane-only",
            "composer would make identical choices, but it does show where the",
            "safe public value in the paid C4.5 run actually came from.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c45-dir", type=Path, default=DEFAULT_C45_DIR)
    parser.add_argument("--c45-summary", default=DEFAULT_C45_SUMMARY)
    parser.add_argument("--c44-summary", type=Path, default=DEFAULT_C44_SUMMARY)
    parser.add_argument("--embedding-summary", type=Path, default=DEFAULT_EMBEDDING_SUMMARY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args(argv)


def resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_optional_json(path: Path) -> dict[str, Any]:
    return load_json(path) if path.exists() else {}


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def list_of(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def strings(value: Any) -> list[str]:
    return [text(item) for item in list_of(value) if text(item)]


def text(value: Any) -> str:
    return str(value or "").strip()


def integer(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
