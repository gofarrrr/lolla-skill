#!/usr/bin/env python3
"""Run C4.7 composer-only source-arm replay.

This is the cheap cross-check after C4.6. It does not run /lolla, does not
rerun embeddings, and does not rerun private exact-chunk consideration. It loads
the paid C4.5 system profiles, filters composer opportunities to a source arm,
and calls only the composer boundary.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_v60_chunk_exact_private_replay import (  # noqa: E402
    call_json_with_timeout,
    load_dotenv,
)
from scripts.run_v60_system_bound_enrichment_replay import (  # noqa: E402
    COMPOSER_SYSTEM_PROMPT,
    DEFAULT_MAX_ADMITTED,
    build_composer_prompt,
    load_json,
    validate_composer_output,
    write_json,
)
from scripts.run_v60_transaction_paid_replay import (  # noqa: E402
    DEFAULT_GENERATOR_MODEL,
    ReplayCallError,
    estimate_tokens,
)


SOURCE_ARM_REPLAY_VERSION = "v60_composer_source_arm_replay.v1"
DEFAULT_C45_DIR = Path(
    "data/evaluations/v60_transaction_replay_lab/2026-05-10-c45-system-bound-enrichment-paid"
)
DEFAULT_C45_SUMMARY = "summary_revalidated_numeric_guard.json"
DEFAULT_OUTPUT_DIR = Path(
    "data/evaluations/v60_transaction_replay_lab/2026-05-10-c47-composer-source-arm-lane-only"
)
STRICT_LANE_SOURCE = "lane_preserved"
ARM_CHOICES = frozenset({"strict_lane", "enhanced"})
ENHANCED_SOURCES = frozenset(
    {"embedding_affordance_exact", "embedding_absence_exact", "hybrid_rrf_exact"}
)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = REPO_ROOT
    c45_dir = resolve(root, args.c45_dir)
    output_dir = resolve(root, args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.dry_run:
        load_dotenv(resolve(root, args.env_file) if args.env_file else root / ".env")
        api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is required unless --dry-run is set")
    else:
        api_key = ""

    c45_summary = load_json(c45_dir / args.c45_summary)
    rows: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    for item in (mapping(row) for row in list_of(c45_summary.get("items"))):
        case_id = text(item.get("case_id"))
        if args.cases and case_id not in set(args.cases):
            continue
        profile = load_json(c45_dir / text(item.get("system_profile_path")))
        original_prompt = load_json(c45_dir / text(item.get("composer_prompt_path")))
        filtered_profile = build_source_arm_profile(
            profile=profile,
            arm=args.arm,
        )
        opportunities = list_of(filtered_profile.get("composer_opportunities"))
        if not opportunities and not args.include_empty_cases:
            continue

        prompt = build_source_arm_prompt(
            original_prompt=original_prompt,
            filtered_profile=filtered_profile,
            max_admitted=args.max_admitted,
        )
        item_id = f"{case_id}__composer_{args.arm}"
        print(f"running {item_id}", flush=True)
        if args.dry_run:
            output = {
                "dry_run_placeholder": True,
                "item_id": item_id,
                "estimated_prompt_tokens": estimate_tokens(prompt),
            }
            validation = {"status": "not_run_dry_run"}
        elif not opportunities:
            output = {
                "admission_decision": "no_delta",
                "admitted_items": [],
                "rejected_items": [],
                "private_guardrails_preserved": [],
                "user_visible_delta": "",
                "no_delta_reason": f"No {args.arm} opportunities were available.",
                "integration_feedback": ["Skipped model call for empty source arm."],
            }
            validation = validate_composer_output(
                output,
                system_profile=filtered_profile,
                max_admitted=args.max_admitted,
                allowed_numeric_text=json.dumps(prompt, ensure_ascii=False),
            )
        else:
            try:
                output, meta = call_json_with_timeout(
                    api_key=api_key,
                    model=args.generator_model,
                    system_prompt=COMPOSER_SYSTEM_PROMPT,
                    user_packet=prompt,
                    stage=f"{item_id}:composer_source_arm",
                    timeout_seconds=args.call_timeout_seconds,
                )
            except ReplayCallError as exc:
                output = {
                    "status": "error",
                    "stage": exc.stage,
                    "error": str(exc),
                    "raw_content": exc.raw_content,
                }
                validation = {"status": "error", "error": str(exc)}
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                output = {
                    "status": "error",
                    "stage": f"{item_id}:composer_source_arm",
                    "error": error,
                    "raw_content": "",
                }
                validation = {"status": "error", "error": error}
            else:
                calls.append({"item_id": item_id, **meta})
                validation = validate_composer_output(
                    output,
                    system_profile=filtered_profile,
                    max_admitted=args.max_admitted,
                    allowed_numeric_text=json.dumps(prompt, ensure_ascii=False),
                )
        print(f"finished {item_id}: {validation.get('status')}", flush=True)

        write_json(output_dir / "system_profiles" / f"{case_id}.json", filtered_profile)
        write_json(output_dir / "composer_prompts" / f"{case_id}.json", prompt)
        write_json(output_dir / "composer_outputs" / f"{case_id}.json", output)
        rows.append(
            {
                "item_id": item_id,
                "case_id": case_id,
                "source_arm": args.arm,
                "status": "ok" if validation.get("status") != "error" else "error",
                "opportunity_count": len(opportunities),
                "composer_validation": validation,
                "system_profile_path": f"system_profiles/{case_id}.json",
                "composer_prompt_path": f"composer_prompts/{case_id}.json",
                "composer_output_path": f"composer_outputs/{case_id}.json",
                "prompt_tokens_estimate": estimate_tokens(prompt),
                "full_c45_validation": mapping(item.get("composer_validation")),
            }
        )

    summary = {
        "source_arm_replay_version": SOURCE_ARM_REPLAY_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_arm": args.arm,
        "dry_run": bool(args.dry_run),
        "input_c45_dir": str(c45_dir),
        "input_c45_summary": args.c45_summary,
        "generator_model": "" if args.dry_run else args.generator_model,
        "item_count": len(rows),
        "items": rows,
        "aggregate": aggregate(rows, calls),
        "call_records": calls,
    }
    write_json(output_dir / "summary.json", summary)
    (output_dir / "source_arm_report.md").write_text(render_report(summary), encoding="utf-8")
    print(f"wrote {output_dir / 'summary.json'}")
    print(f"wrote {output_dir / 'source_arm_report.md'}")
    return 0


def build_source_arm_profile(*, profile: Mapping[str, Any], arm: str) -> dict[str, Any]:
    opportunities = [
        mapping(item)
        for item in list_of(profile.get("composer_opportunities"))
        if source_arm_match(strings(mapping(item).get("source_mix")), arm)
    ]
    lane_profile = mapping(profile.get("lane_profile"))
    source_counts = Counter(
        source
        for opportunity in opportunities
        for source in strings(opportunity.get("source_mix"))
    )
    return {
        "profile_version": "c47_source_arm_profile.v1",
        "source_arm": arm,
        "case_id": text(profile.get("case_id")),
        "system_role": f"composer_source_arm_{arm}",
        "lane_profile": lane_profile,
        "embedding_profile": {} if arm == "strict_lane" else mapping(profile.get("embedding_profile")),
        "packet_source_counts": dict(sorted(source_counts.items())),
        "private_trace_summary": {
            "filtered_from_packet_usefulness": text(
                mapping(profile.get("private_trace_summary")).get("packet_usefulness")
            ),
            "original_selected_opportunity_count": integer(
                mapping(profile.get("private_trace_summary")).get("selected_opportunity_count")
            ),
            "filtered_selected_opportunity_count": len(opportunities),
            "source_arm": arm,
        },
        "composer_opportunities": opportunities,
        "integration_policy": {
            "quality_first": True,
            "max_public_deltas": DEFAULT_MAX_ADMITTED,
            "allow_no_delta": True,
            "public_language_must_hide_private_machinery": True,
            "v60_role": "source_arm_ablation_not_runtime_behavior",
        },
    }


def build_source_arm_prompt(
    *,
    original_prompt: Mapping[str, Any],
    filtered_profile: Mapping[str, Any],
    max_admitted: int,
) -> dict[str, Any]:
    return build_composer_prompt(
        case_artifact={
            "case_id": text(original_prompt.get("case_id")),
            "query": text(original_prompt.get("query")),
            "conversation_excerpt": text(original_prompt.get("conversation_excerpt")),
            "vanilla_answer": text(original_prompt.get("existing_lolla_answer")),
        },
        system_profile=filtered_profile,
        max_admitted=max_admitted,
        conversation_chars=10**9,
        vanilla_chars=10**9,
    )


def source_arm_match(source_mix: list[str], arm: str) -> bool:
    sources = set(source_mix)
    if arm == "strict_lane":
        return sources == {STRICT_LANE_SOURCE}
    if arm == "enhanced":
        return any(source in ENHANCED_SOURCES for source in sources)
    raise ValueError(f"unknown arm: {arm}")


def aggregate(rows: list[Mapping[str, Any]], calls: list[Mapping[str, Any]]) -> dict[str, Any]:
    validation_counts = Counter(text(mapping(row.get("composer_validation")).get("status")) for row in rows)
    decision_counts = Counter(
        text(mapping(row.get("composer_validation")).get("admission_decision")) for row in rows
    )
    public_delta_count = sum(
        integer(mapping(row.get("composer_validation")).get("public_delta_count")) for row in rows
    )
    safe_public_delta_count = sum(
        integer(mapping(row.get("composer_validation")).get("public_delta_count"))
        for row in rows
        if text(mapping(row.get("composer_validation")).get("status")) == "valid"
    )
    return {
        "composer_validation_counts": dict(sorted((key, value) for key, value in validation_counts.items() if key)),
        "admission_decision_counts": dict(sorted((key, value) for key, value in decision_counts.items() if key)),
        "opportunity_count": sum(integer(row.get("opportunity_count")) for row in rows),
        "public_delta_count": public_delta_count,
        "safe_public_delta_count": safe_public_delta_count,
        "call_count": len(calls),
        "input_tokens": sum(integer(record.get("input_tokens")) for record in calls),
        "output_tokens": sum(integer(record.get("output_tokens")) for record in calls),
        "total_tokens": sum(integer(record.get("total_tokens")) for record in calls),
        "cost_usd": round(sum(float(record.get("cost_usd") or 0.0) for record in calls), 6),
    }


def render_report(summary: Mapping[str, Any]) -> str:
    aggregate_payload = mapping(summary.get("aggregate"))
    lines = [
        "# V60 C4.7 Composer Source-Arm Replay",
        "",
        f"Date: {text(summary.get('generated_at'))[:10]}",
        f"Source arm: `{text(summary.get('source_arm'))}`",
        "",
        "## Aggregate",
        "",
        f"- Items: {integer(summary.get('item_count'))}",
        f"- Paid calls: {integer(aggregate_payload.get('call_count'))}",
        f"- Cost: `${aggregate_payload.get('cost_usd', 0)}`",
        f"- Validation: `{json.dumps(mapping(aggregate_payload.get('composer_validation_counts')), sort_keys=True)}`",
        f"- Decisions: `{json.dumps(mapping(aggregate_payload.get('admission_decision_counts')), sort_keys=True)}`",
        f"- Opportunities: {integer(aggregate_payload.get('opportunity_count'))}",
        f"- Safe public deltas: {integer(aggregate_payload.get('safe_public_delta_count'))}",
        "",
        "## Items",
        "",
        "| Case | Opps | Validation | Decision | Safe Public Deltas |",
        "| --- | ---: | --- | --- | ---: |",
    ]
    for row in (mapping(item) for item in list_of(summary.get("items"))):
        validation = mapping(row.get("composer_validation"))
        safe_count = (
            integer(validation.get("public_delta_count"))
            if text(validation.get("status")) == "valid"
            else 0
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{text(row.get('case_id'))}`",
                    str(integer(row.get("opportunity_count"))),
                    f"`{text(validation.get('status'))}`",
                    f"`{text(validation.get('admission_decision'))}`",
                    str(safe_count),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c45-dir", type=Path, default=DEFAULT_C45_DIR)
    parser.add_argument("--c45-summary", default="summary_revalidated_numeric_guard.json")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--generator-model", default=DEFAULT_GENERATOR_MODEL)
    parser.add_argument("--arm", choices=sorted(ARM_CHOICES), default="strict_lane")
    parser.add_argument("--max-admitted", type=int, default=DEFAULT_MAX_ADMITTED)
    parser.add_argument("--call-timeout-seconds", type=int, default=300)
    parser.add_argument("--cases", nargs="*", default=[])
    parser.add_argument("--include-empty-cases", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


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
