"""Deterministic aggregation for the fixed core-semantic corpus."""
from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


CORE_SEMANTIC_CORPUS_COMPARISON_SCHEMA_VERSION = (
    "lolla.core_semantic_corpus_comparison.v0"
)


def build_core_semantic_corpus_comparison(
    *,
    manifest_path: Path | str,
    comparison_paths: Sequence[Path | str],
    artifact_dirs: Sequence[Path | str],
    repo_root: Path | str,
) -> dict[str, Any]:
    manifest = _load_object(Path(manifest_path))
    root = Path(repo_root)
    comparisons = [_load_object(Path(path)) for path in comparison_paths]
    by_case = {str(item.get("case_id") or ""): item for item in comparisons}
    expected_ids = {str(case["case_id"]) for case in manifest["cases"]}
    if set(by_case) != expected_ids:
        missing = sorted(expected_ids - set(by_case))
        extra = sorted(set(by_case) - expected_ids)
        raise ValueError(f"comparison set does not match corpus; missing={missing}, extra={extra}")

    gold_by_case: dict[str, dict[str, Any]] = {}
    stratum_by_case: dict[str, str] = {}
    for case in manifest["cases"]:
        case_id = str(case["case_id"])
        gold_by_case[case_id] = _load_object(root / case["gold_path"])
        stratum_by_case[case_id] = str(case["stratum"])

    per_case = []
    for case_id in sorted(by_case):
        comparison = by_case[case_id]
        compact = comparison["compact_path"]
        shadow = comparison["shadow_path"]
        per_case.append(
            {
                "case_id": case_id,
                "stratum": stratum_by_case[case_id],
                "gold_observation_count": len(gold_by_case[case_id]["required_observations"]),
                "compact": _case_path_metrics(compact),
                "shadow": _case_path_metrics(shadow),
                "delta": {
                    "mean_recall": shadow["gold_span_recall"]["mean_recall"]
                    - compact["gold_span_recall"]["mean_recall"],
                    "span_repeatability": shadow["repeatability"]["mean_span_jaccard"]
                    - compact["repeatability"]["mean_span_jaccard"],
                    "labeled_repeatability": shadow["repeatability"]["mean_labeled_jaccard"]
                    - compact["repeatability"]["mean_labeled_jaccard"],
                },
            }
        )

    return {
        "schema_version": CORE_SEMANTIC_CORPUS_COMPARISON_SCHEMA_VERSION,
        "corpus_id": manifest["corpus_id"],
        "case_count": len(per_case),
        "repeat_contract": manifest["repeat_contract"],
        "compact_path": _aggregate_path(
            path_name="compact_path",
            comparisons=by_case,
            gold_by_case=gold_by_case,
        ),
        "shadow_path": _aggregate_path(
            path_name="shadow_path",
            comparisons=by_case,
            gold_by_case=gold_by_case,
        ),
        "head_to_head": {
            "recall_wins": sum(item["delta"]["mean_recall"] > 0 for item in per_case),
            "span_repeatability_wins": sum(
                item["delta"]["span_repeatability"] > 0 for item in per_case
            ),
            "labeled_repeatability_wins": sum(
                item["delta"]["labeled_repeatability"] > 0 for item in per_case
            ),
            "case_count": len(per_case),
        },
        "per_case": per_case,
        "operational": _operational_summary([Path(path) for path in artifact_dirs]),
        "comparison_limits": [
            "gold annotations are provisional source-first research judgments",
            "exact-span recall does not credit ungrounded paraphrases",
            "three repeats are an initial stability signal, not production reliability proof",
            "token totals are a cost proxy; provider billing amounts are not persisted",
            "the short governance case has only one user and one assistant turn",
        ],
    }


def render_core_semantic_corpus_comparison_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_core_semantic_corpus_comparison_markdown(payload: Mapping[str, Any]) -> str:
    compact = payload["compact_path"]
    shadow = payload["shadow_path"]
    head = payload["head_to_head"]
    lines = [
        "# Core Semantic Corpus Comparison",
        "",
        f"Corpus: `{payload['corpus_id']}` ({payload['case_count']} cases, three repeats per path)",
        "",
        "## Corpus result",
        "",
        "| measure | compact | shadow |",
        "| --- | ---: | ---: |",
        f"| macro exact-span recall | {compact['macro_mean_recall']:.3f} | {shadow['macro_mean_recall']:.3f} |",
        f"| weighted exact-span recall | {compact['weighted_mean_recall']:.3f} | {shadow['weighted_mean_recall']:.3f} |",
        f"| stable observations | {compact['stable_observation_count']} / {compact['gold_observation_count']} | {shadow['stable_observation_count']} / {shadow['gold_observation_count']} |",
        f"| never recovered | {compact['never_observation_count']} / {compact['gold_observation_count']} | {shadow['never_observation_count']} / {shadow['gold_observation_count']} |",
        f"| macro span repeatability | {compact['macro_span_repeatability']:.3f} | {shadow['macro_span_repeatability']:.3f} |",
        f"| macro labeled repeatability | {compact['macro_labeled_repeatability']:.3f} | {shadow['macro_labeled_repeatability']:.3f} |",
        f"| lowest case recall | {compact['case_recall_floor']:.3f} | {shadow['case_recall_floor']:.3f} |",
        "",
        f"Shadow wins recall on {head['recall_wins']}/{head['case_count']} cases, span repeatability on {head['span_repeatability_wins']}/{head['case_count']}, and labeled repeatability on {head['labeled_repeatability_wins']}/{head['case_count']}.",
        "",
        "## Per case",
        "",
        "| case | stratum | gold | compact recall | shadow recall | compact span J | shadow span J |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in payload["per_case"]:
        lines.append(
            f"| `{item['case_id']}` | `{item['stratum']}` | {item['gold_observation_count']} | "
            f"{item['compact']['mean_recall']:.3f} | {item['shadow']['mean_recall']:.3f} | "
            f"{item['compact']['span_repeatability']:.3f} | {item['shadow']['span_repeatability']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Recovery by semantic dimension",
            "",
            "| dimension | compact weighted recall | shadow weighted recall | compact stable | shadow stable | gold |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    dimensions = sorted(set(compact["dimensions"]) | set(shadow["dimensions"]))
    for dimension in dimensions:
        left = compact["dimensions"].get(dimension, {})
        right = shadow["dimensions"].get(dimension, {})
        lines.append(
            f"| `{dimension}` | {left.get('weighted_recall', 0.0):.3f} | "
            f"{right.get('weighted_recall', 0.0):.3f} | "
            f"{left.get('stable_observation_count', 0)} | "
            f"{right.get('stable_observation_count', 0)} | "
            f"{right.get('gold_observation_count', left.get('gold_observation_count', 0))} |"
        )

    lines.extend(["", "## Operational readout", ""])
    for path_name in ("compact", "shadow"):
        record = payload["operational"][path_name]
        lines.append(
            f"- {path_name}: {record['artifact_count']} successful artifacts; "
            f"usage tracked for {record['usage_tracked_artifact_count']}; "
            f"{record['call_count']} recorded calls and {record['total_tokens']} tokens."
        )
    lines.append(
        f"- Preserved failed attempts: {payload['operational']['preserved_failed_attempt_count']}."
    )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in payload["comparison_limits"])
    return "\n".join(lines) + "\n"


def _case_path_metrics(path: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "mean_recall": path["gold_span_recall"]["mean_recall"],
        "stable_observation_count": len(path["gold_span_recall"]["stable_observation_ids"]),
        "never_observation_count": len(path["gold_span_recall"]["never_observation_ids"]),
        "span_repeatability": path["repeatability"]["mean_span_jaccard"],
        "labeled_repeatability": path["repeatability"]["mean_labeled_jaccard"],
    }


def _aggregate_path(
    *,
    path_name: str,
    comparisons: Mapping[str, Mapping[str, Any]],
    gold_by_case: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    recall_values = []
    span_values = []
    label_values = []
    stable_count = 0
    never_count = 0
    gold_count = 0
    recovered_total = 0
    opportunity_total = 0
    dimension_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"gold": 0, "recovered": 0, "stable": 0, "never": 0, "opportunities": 0}
    )

    for case_id, comparison in comparisons.items():
        path = comparison[path_name]
        recall = path["gold_span_recall"]
        repeatability = path["repeatability"]
        recall_values.append(float(recall["mean_recall"]))
        span_values.append(float(repeatability["mean_span_jaccard"]))
        label_values.append(float(repeatability["mean_labeled_jaccard"]))
        stable = set(recall["stable_observation_ids"])
        never = set(recall["never_observation_ids"])
        observations = gold_by_case[case_id]["required_observations"]
        gold_count += len(observations)
        stable_count += len(stable)
        never_count += len(never)
        for run in recall["per_run"]:
            recovered_total += int(run["recovered_count"])
            opportunity_total += int(run["total_count"])
        per_run_sets = [set(run["observation_ids"]) for run in recall["per_run"]]
        for observation in observations:
            observation_id = str(observation["observation_id"])
            dimension = str(observation["dimension"])
            counts = dimension_counts[dimension]
            counts["gold"] += 1
            counts["opportunities"] += len(per_run_sets)
            counts["recovered"] += sum(observation_id in run for run in per_run_sets)
            counts["stable"] += observation_id in stable
            counts["never"] += observation_id in never

    return {
        "macro_mean_recall": _mean(recall_values),
        "weighted_mean_recall": recovered_total / opportunity_total if opportunity_total else 0.0,
        "macro_span_repeatability": _mean(span_values),
        "macro_labeled_repeatability": _mean(label_values),
        "case_recall_floor": min(recall_values) if recall_values else 0.0,
        "case_recall_ceiling": max(recall_values) if recall_values else 0.0,
        "stable_observation_count": stable_count,
        "never_observation_count": never_count,
        "gold_observation_count": gold_count,
        "dimensions": {
            dimension: {
                "weighted_recall": counts["recovered"] / counts["opportunities"]
                if counts["opportunities"] else 0.0,
                "stable_observation_count": counts["stable"],
                "never_observation_count": counts["never"],
                "gold_observation_count": counts["gold"],
            }
            for dimension, counts in sorted(dimension_counts.items())
        },
    }


def _operational_summary(artifact_dirs: list[Path]) -> dict[str, Any]:
    records = {
        "compact": _empty_usage(),
        "shadow": _empty_usage(),
    }
    failed_count = 0
    for directory in artifact_dirs:
        failed_count += len(list(directory.glob("*.error.json")))
        for kind in ("compact", "shadow"):
            for path in sorted(directory.glob(f"{kind}-[0-9][0-9].json")):
                payload = _load_object(path)
                record = records[kind]
                record["artifact_count"] += 1
                calls = (payload.get("model_usage") or {}).get("calls") or []
                if calls:
                    record["usage_tracked_artifact_count"] += 1
                for call in calls:
                    record["call_count"] += 1
                    record["prompt_tokens"] += int(call.get("prompt_tokens") or 0)
                    record["completion_tokens"] += int(call.get("completion_tokens") or 0)
                    record["total_tokens"] += int(call.get("total_tokens") or 0)
    return {
        "compact": records["compact"],
        "shadow": records["shadow"],
        "preserved_failed_attempt_count": failed_count,
    }


def _empty_usage() -> dict[str, int]:
    return {
        "artifact_count": 0,
        "usage_tracked_artifact_count": 0,
        "call_count": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value

