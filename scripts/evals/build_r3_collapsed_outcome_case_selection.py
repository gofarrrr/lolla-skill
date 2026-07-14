#!/usr/bin/env python3
"""Freeze provider-free direct and graph pressure for the next R3 case."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.constitutional_graph_survival import (  # noqa: E402
    build_constitutional_graph_survival,
)
from engine.system_b.r3_fresh_consumer import (  # noqa: E402
    build_pressure_bundle,
    text_sha256,
    value_sha256,
)
from engine.system_b.r3_task_shape_counterfactual import (  # noqa: E402
    collapsed_one_pass_request_body,
    request_metrics,
)


CASE_ID = "v2-case01-anchor-contract"
SOURCE = ROOT / (
    "research/lolla-r3-collapsed-outcome-case-2026-07-13/source/"
    "v2-case01-anchor-contract.txt"
)
SOURCE_FREEZE = ROOT / (
    "research/lolla-r3-collapsed-outcome-case-2026-07-13/source/"
    "source-freeze.json"
)
SELECTION = ROOT / (
    "research/lolla-r3-collapsed-outcome-case-2026-07-13/selection/"
    "direct-pattern-selection.json"
)
KNOWLEDGE = ROOT / "data/knowledge_graph.json"
RELATIONSHIPS = ROOT / "data/relationship_graph.json"
BUILDER = ROOT / "scripts/evals/build_r3_collapsed_outcome_case_selection.py"
SOURCE_FREEZE_COMMIT = "dff7b48f5e1ab94e91fd0e42cdf6ba12fb02feb6"

RESULT_NAME = "result.json"
BUNDLE_NAME = "collapsed-pressure-contract.json"
SUMMARY_NAME = "selection-summary.json"
ARTIFACT_NAMES = (RESULT_NAME, BUNDLE_NAME, SUMMARY_NAME)


class R3CollapsedSelectionError(RuntimeError):
    """Raised when the prospective selection loses source or graph custody."""


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_bytes(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_json_bytes(value))


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _turn_map(source: str) -> dict[tuple[int, str], str]:
    pattern = re.compile(
        r"(?ms)^\[Turn (\d+)\] (USER|ASSISTANT):\n"
        r"(.*?)(?=^\[Turn \d+\] (?:USER|ASSISTANT):\n|\Z)"
    )
    result = {
        (int(match.group(1)), match.group(2).lower()): match.group(3).strip()
        for match in pattern.finditer(source)
    }
    expected = {
        (turn, speaker)
        for turn in range(1, 15)
        for speaker in ("user", "assistant")
    }
    if set(result) != expected or any(not value for value in result.values()):
        raise R3CollapsedSelectionError("source turn custody is invalid")
    return result


def _validate_source() -> tuple[str, dict[str, Any]]:
    source = SOURCE.read_text(encoding="utf-8")
    freeze = _load(SOURCE_FREEZE)
    if not isinstance(freeze, dict):
        raise R3CollapsedSelectionError("source freeze must be an object")
    if (
        freeze.get("case_id") != CASE_ID
        or freeze.get("status")
        != "source_frozen_provider_free_before_targets_or_pressure_selection"
        or freeze.get("source", {}).get("sha256") != text_sha256(source)
        or freeze.get("source", {}).get("message_count") != 28
        or freeze.get("freeze_boundary", {}).get(
            "expected_pressure_outcomes_authored_before_freeze"
        )
        is not False
        or freeze.get("freeze_boundary", {}).get(
            "canonical_pressure_ids_selected_before_freeze"
        )
        is not False
    ):
        raise R3CollapsedSelectionError("prospective source freeze drifted")
    _turn_map(source)
    return source, freeze


def _validate_selection(
    *, source: str, knowledge: Mapping[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    selection = _load(SELECTION)
    models = knowledge.get("models")
    if not isinstance(selection, dict):
        raise R3CollapsedSelectionError("direct selection must be an object")
    if not isinstance(models, Mapping) or len(models) != 222:
        raise R3CollapsedSelectionError("canonical registry drifted")
    if (
        selection.get("case_id") != CASE_ID
        or selection.get("status")
        != "direct_patterns_frozen_before_expected_dispositions"
        or selection.get("source_sha256") != text_sha256(source)
        or selection.get("semantic_owner", {}).get(
            "deterministic_code_inferred_meaning"
        )
        is not False
        or selection.get("freeze_boundary", {}).get(
            "expected_candidate_dispositions_authored"
        )
        is not False
        or selection.get("freeze_boundary", {}).get(
            "source_review_target_authored"
        )
        is not False
    ):
        raise R3CollapsedSelectionError("direct pattern selection boundary drifted")
    patterns = selection.get("patterns")
    if not isinstance(patterns, list) or len(patterns) != 6:
        raise R3CollapsedSelectionError("exactly six direct patterns are required")
    turn_map = _turn_map(source)
    normalized: list[dict[str, Any]] = []
    seen_patterns: set[str] = set()
    seen_models: set[str] = set()
    ordering: list[tuple[int, str]] = []
    for pattern in patterns:
        if not isinstance(pattern, Mapping):
            raise R3CollapsedSelectionError("direct pattern must be an object")
        pattern_id = str(pattern.get("pattern_id", ""))
        model_id = str(pattern.get("canonical_model_id", ""))
        fact_stripped = str(pattern.get("fact_stripped_pattern", "")).strip()
        evidence = pattern.get("source_evidence")
        if (
            not pattern_id
            or pattern_id in seen_patterns
            or not fact_stripped
            or model_id not in models
            or model_id in seen_models
            or not isinstance(evidence, list)
            or not evidence
        ):
            raise R3CollapsedSelectionError("direct pattern identity is invalid")
        turns: list[int] = []
        for item in evidence:
            if not isinstance(item, Mapping):
                raise R3CollapsedSelectionError("source evidence must be an object")
            turn = item.get("turn_number")
            speaker = item.get("speaker")
            quote = item.get("quote")
            if (
                not isinstance(turn, int)
                or speaker not in {"user", "assistant"}
                or not isinstance(quote, str)
                or not quote.strip()
                or quote not in turn_map.get((turn, speaker), "")
            ):
                raise R3CollapsedSelectionError(
                    f"source evidence drifted for {pattern_id}"
                )
            turns.append(turn)
        seen_patterns.add(pattern_id)
        seen_models.add(model_id)
        ordering.append((min(turns), pattern_id))
        normalized.append(dict(pattern))
    if ordering != sorted(ordering):
        raise R3CollapsedSelectionError("direct pattern ordering rule drifted")
    return selection, normalized


def construct(*, include_runtime: bool = False) -> dict[str, dict[str, Any]]:
    source, source_freeze = _validate_source()
    knowledge = _load(KNOWLEDGE)
    relationships = _load(RELATIONSHIPS)
    if not isinstance(knowledge, dict) or not isinstance(
        relationships, (dict, list)
    ):
        raise R3CollapsedSelectionError("knowledge or relationship graph drifted")
    selection, patterns = _validate_selection(
        source=source,
        knowledge=knowledge,
    )
    candidates = [
        {
            "model_id": pattern["canonical_model_id"],
            "recall_source": "provider_free_fact_stripped_pattern_projection",
            "source_mechanism_ids": [pattern["pattern_id"]],
        }
        for pattern in patterns
    ]
    portfolio = build_constitutional_graph_survival(
        candidates=candidates,
        knowledge_graph=knowledge,
        relationship_graph=relationships,
    )
    active = portfolio["active_pressure_items"]
    if (
        portfolio["path_counts"]["direct_active"] != 6
        or portfolio["path_counts"]["graph_active"] != 3
        or len(active) != 9
    ):
        raise R3CollapsedSelectionError("nine-item direct/graph portfolio drifted")
    direct_ids = [pattern["canonical_model_id"] for pattern in patterns]
    if [item["model_id"] for item in active[:6]] != direct_ids:
        raise R3CollapsedSelectionError("direct canonical order drifted")

    companion_candidates = [
        {
            "selection_rank": index,
            "pattern_id": pattern["pattern_id"],
            "model_id": pattern["canonical_model_id"],
            "fact_stripped_pattern": pattern["fact_stripped_pattern"],
            "source_evidence": pattern["source_evidence"],
            "selection_claim": pattern["selection_claim"],
        }
        for index, pattern in enumerate(patterns)
    ]
    result: dict[str, Any] = {
        "schema_version": "lolla.r3_collapsed_outcome_selection_result.v1",
        "status": "provider_free_direct_and_graph_portfolio_frozen",
        "case_id": CASE_ID,
        "audit_summary": {"companion_candidates": companion_candidates},
        "constitutional_graph_survival": portfolio,
        "boundary": {
            "source_frozen_before_selection": True,
            "selection_frozen_before_target_review": True,
            "direct_semantics_same_project_codex_authored": True,
            "graph_expansion_deterministic": True,
            "graph_recall_is_relevance_proof": False,
            "candidate_deletion": False,
            "provider_calls": 0,
            "runtime_effect": "none",
        },
    }
    result["result_sha256"] = value_sha256(result)
    result_file_sha = hashlib.sha256(_json_bytes(result)).hexdigest()

    output_root = SELECTION.parent
    refs = [
        {
            "path": _relative(SOURCE),
            "role": "authoritative_conversation",
            "sha256": _file_sha(SOURCE),
        },
        {
            "path": _relative(SOURCE_FREEZE),
            "role": "prospective_source_freeze",
            "sha256": _file_sha(SOURCE_FREEZE),
        },
        {
            "path": _relative(SELECTION),
            "role": "fact_stripped_direct_selection",
            "sha256": _file_sha(SELECTION),
        },
        {
            "path": _relative(output_root / RESULT_NAME),
            "role": "direct_and_graph_portfolio",
            "sha256": result_file_sha,
        },
        {
            "path": _relative(KNOWLEDGE),
            "role": "canonical_mental_model_registry",
            "sha256": _file_sha(KNOWLEDGE),
        },
        {
            "path": _relative(RELATIONSHIPS),
            "role": "deterministic_relationship_graph",
            "sha256": _file_sha(RELATIONSHIPS),
        },
    ]
    base_bundle = build_pressure_bundle(
        case_id=CASE_ID,
        conversation=source,
        constitutional_graph_survival=portfolio,
        source_refs=refs,
    )
    collapsed_body = collapsed_one_pass_request_body(
        base_body=base_bundle["request_body"],
        packet=base_bundle["packet"],
    )
    metrics = request_metrics(collapsed_body)
    maximum_cost = metrics["maximum_estimated_cost_usd"]
    if maximum_cost > 0.01:
        raise R3CollapsedSelectionError("collapsed request exceeds one-cent envelope")
    request_contract = dict(base_bundle["request_contract"])
    request_contract.update(
        {
            "wire_contract": "collapsed_outcome_one_pass",
            "maximum_estimated_call_cost_usd": maximum_cost,
            "current_provider_calls_authorized": 0,
        }
    )
    schema = collapsed_body["response_format"]["json_schema"]["schema"]
    system_prompt = collapsed_body["messages"][0]["content"]
    user_prompt = collapsed_body["messages"][1]["content"]
    bundle: dict[str, Any] = {
        "schema_version": "lolla.r3_collapsed_outcome_pressure_contract.v1",
        "status": "provider_free_selection_frozen_target_review_not_authored",
        "case_id": CASE_ID,
        "packet_sha256": base_bundle["packet"]["packet_sha256"],
        "packet_source_refs": base_bundle["packet"]["source_refs"],
        "request_contract": request_contract,
        "request_metrics": metrics,
        "reconstruction": {
            "selection_builder": _relative(BUILDER),
            "provider_material_function": "construct(include_runtime=True)",
            "packet_function": "engine.system_b.r3_fresh_consumer.build_pressure_packet",
            "request_function": (
                "engine.system_b.r3_task_shape_counterfactual."
                "collapsed_one_pass_request_body"
            ),
        },
        "hashes": {
            "system_prompt_sha256": text_sha256(system_prompt),
            "user_prompt_sha256": text_sha256(user_prompt),
            "response_schema_sha256": value_sha256(schema),
            "request_body_sha256": value_sha256(collapsed_body),
            "constitutional_graph_portfolio_sha256": portfolio["portfolio_sha256"],
        },
        "provider_calls_made": 0,
        "next_call_authorized": False,
        "runtime_effect": "none",
    }
    bundle["bundle_sha256"] = value_sha256(bundle)

    summary: dict[str, Any] = {
        "schema_version": "lolla.r3_collapsed_outcome_selection_summary.v1",
        "status": "source_and_nine_item_portfolio_frozen_before_target_review",
        "case_id": CASE_ID,
        "source_freeze_commit": SOURCE_FREEZE_COMMIT,
        "source_sha256": source_freeze["source"]["sha256"],
        "direct_model_ids": direct_ids,
        "graph_model_ids": [item["model_id"] for item in active[6:]],
        "active_pressure_ids": [item["pressure_id"] for item in active],
        "path_counts": portfolio["path_counts"],
        "fan_in_measurement": portfolio["fan_in_measurement"],
        "maximum_estimated_call_cost_usd": maximum_cost,
        "maximum_provider_reported_cost_usd": 0.01,
        "provider_calls": 0,
        "next_call_authorized": False,
        "expected_dispositions_authored": False,
        "source_review_authored": False,
        "runtime_effect": "none",
        "frozen_inputs": [
            {"path": _relative(path), "sha256": _file_sha(path)}
            for path in (
                SOURCE,
                SOURCE_FREEZE,
                SELECTION,
                KNOWLEDGE,
                RELATIONSHIPS,
                BUILDER,
            )
        ],
        "artifacts": [
            {"path": _relative(output_root / RESULT_NAME), "sha256": result_file_sha},
            {
                "path": _relative(output_root / BUNDLE_NAME),
                "sha256": hashlib.sha256(_json_bytes(bundle)).hexdigest(),
            },
        ],
    }
    summary["summary_sha256"] = value_sha256(summary)
    artifacts = {
        RESULT_NAME: result,
        BUNDLE_NAME: bundle,
        SUMMARY_NAME: summary,
    }
    if include_runtime:
        artifacts["_runtime_material"] = {
            "packet": base_bundle["packet"],
            "response_schema": schema,
            "request_body": collapsed_body,
            "request_contract": request_contract,
            "request_metrics": metrics,
        }
    return artifacts


def build(output: Path) -> dict[str, Any]:
    artifacts = construct()
    for name in ARTIFACT_NAMES:
        value = artifacts[name]
        _write(output / name, value)
    return artifacts[SUMMARY_NAME]


def validate(output: Path) -> dict[str, Any]:
    expected = construct()
    for name in ARTIFACT_NAMES:
        value = expected[name]
        path = output / name
        if not path.is_file() or _load(path) != value:
            raise R3CollapsedSelectionError(f"checked-in artifact drifted: {name}")
    return expected[SUMMARY_NAME]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    summary = validate(output) if args.validate_only else build(output)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "active_pressure_count": len(summary["active_pressure_ids"]),
                "maximum_estimated_call_cost_usd": summary[
                    "maximum_estimated_call_cost_usd"
                ],
                "provider_calls": summary["provider_calls"],
                "next_call_authorized": summary["next_call_authorized"],
                "summary_sha256": summary["summary_sha256"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
