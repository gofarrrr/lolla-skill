#!/usr/bin/env python3
"""Build a dormant Step 6 portfolio around an existing active handoff.

Semantic selection lives in the authored research spec. This builder only
checks coverage, source/graph membership, hashes, shape, render budget, and
runtime dormancy. It does not call models or decide relevance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
RESEARCH_SCRIPTS = REPO_ROOT / "scripts/research"
if str(RESEARCH_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(RESEARCH_SCRIPTS))

from pre_step6_attention_maps import (  # noqa: E402
    MAX_RENDER_CHARS,
    STEP6_ATTENTION_MAP_SCHEMA_VERSION,
    render_step6_attention_map,
    validate_step6_attention_map_payload,
)


SPEC_SCHEMA_VERSION = "lolla.reasoning_portfolio_shadow_spec.v0"
VALIDATION_SCHEMA_VERSION = "lolla.reasoning_portfolio_shadow_validation.v0"
GRAPH_INDEX_SCHEMA_VERSION = "lolla.review_safe_graph_candidate_index.v0"
_SPEC_FIELDS = {
    "schema_version",
    "status",
    "runtime_policy",
    "case_id",
    "problem_read",
    "active_items",
    "edge_items",
    "weak_items",
    "parked_items",
    "ask_user_if_any",
    "review_admission",
    "full_archive_refs",
    "step6_instruction",
}


class ReasoningPortfolioShadowError(ValueError):
    """Raised when a portfolio cannot be sealed mechanically."""


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReasoningPortfolioShadowError(f"expected JSON object: {path}")
    return value


def _hash_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _require_fields(value: Mapping[str, Any], fields: set[str], label: str) -> None:
    missing = sorted(fields - set(value))
    unknown = sorted(set(value) - fields)
    if missing:
        raise ReasoningPortfolioShadowError(f"{label} missing fields: {missing}")
    if unknown:
        raise ReasoningPortfolioShadowError(f"{label} unknown fields: {unknown}")


def _known_handoff_ids(handoff: Mapping[str, Any]) -> set[str]:
    return {
        str(item["pressure_id"])
        for item in handoff.get("pressure_items", [])
        if isinstance(item, Mapping) and item.get("pressure_id")
    } | {
        str(item["preservation_id"])
        for item in handoff.get("preservation_items", [])
        if isinstance(item, Mapping) and item.get("preservation_id")
    }


def _known_source_event_ids(handoff: Mapping[str, Any]) -> set[str]:
    values: set[str] = set()
    for group in ("pressure_items", "preservation_items"):
        for item in handoff.get(group, []):
            if not isinstance(item, Mapping):
                continue
            values.update(str(ref) for ref in item.get("source_event_ids", []))
    return values


def build_graph_candidate_index(
    graph_report: Mapping[str, Any], *, graph_report_sha256: str
) -> dict[str, Any]:
    rows = graph_report.get("candidate_survival")
    if not isinstance(rows, list):
        raise ReasoningPortfolioShadowError(
            "graph report is missing candidate_survival"
        )
    candidates: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        model_id = str(row.get("model_id") or "")
        if not model_id:
            continue
        candidates.append(
            {
                "graph_trace_ref": f"graph_survival.model.{model_id}",
                "model_id": model_id,
                "survival_state": str(row.get("survival_state") or ""),
                "selected_for_v60": row.get("selected_for_v60") is True,
                "sources": sorted(
                    str(source) for source in row.get("sources", []) if source
                ),
            }
        )
    candidates.sort(key=lambda item: item["graph_trace_ref"])
    return {
        "schema_version": GRAPH_INDEX_SCHEMA_VERSION,
        "status": "review_safe_metadata_only",
        "graph_report_sha256": graph_report_sha256,
        "candidate_count": len(candidates),
        "raw_graph_text_included": False,
        "local_absolute_paths_included": False,
        "candidates": candidates,
        "non_claims": [
            "candidate_presence_is_not_relevance",
            "selection_is_not_causal_attribution",
            "suppression_is_not_noise",
            "not_runtime_integration_authority",
        ],
    }


def build_reasoning_portfolio_shadow(
    *,
    spec_path: Path,
    active_handoff_path: Path,
    graph_report_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    spec = _load_object(spec_path)
    handoff = _load_object(active_handoff_path)
    graph_report = _load_object(graph_report_path)

    _require_fields(spec, _SPEC_FIELDS, "portfolio spec")
    if spec.get("schema_version") != SPEC_SCHEMA_VERSION:
        raise ReasoningPortfolioShadowError("unexpected portfolio spec schema")
    if spec.get("status") != "research_only":
        raise ReasoningPortfolioShadowError("portfolio spec must be research_only")
    if spec.get("runtime_policy") != "runtime_dormant":
        raise ReasoningPortfolioShadowError(
            "portfolio spec must remain runtime_dormant"
        )

    graph_hash = _hash_file(graph_report_path)
    graph_index = build_graph_candidate_index(
        graph_report, graph_report_sha256=graph_hash
    )
    known_graph_refs = {
        item["graph_trace_ref"] for item in graph_index["candidates"]
    }
    known_handoff_ids = _known_handoff_ids(handoff)
    known_source_ids = _known_source_event_ids(handoff)

    active_items = spec.get("active_items")
    if not isinstance(active_items, list):
        raise ReasoningPortfolioShadowError("active_items must be a list")
    active_source_ids = [
        str(item.get("source_item_id") or "")
        for item in active_items
        if isinstance(item, Mapping)
    ]
    if len(active_source_ids) != len(set(active_source_ids)):
        raise ReasoningPortfolioShadowError("active source_item_id is duplicated")
    if set(active_source_ids) != known_handoff_ids:
        missing = sorted(known_handoff_ids - set(active_source_ids))
        unknown = sorted(set(active_source_ids) - known_handoff_ids)
        raise ReasoningPortfolioShadowError(
            f"active handoff coverage mismatch; missing={missing}; unknown={unknown}"
        )

    for group_name in ("edge_items", "parked_items"):
        for index, item in enumerate(spec.get(group_name, [])):
            graph_ref = str(item.get("graph_trace_ref") or "")
            if graph_ref not in known_graph_refs:
                raise ReasoningPortfolioShadowError(
                    f"{group_name}[{index}] references unknown graph candidate"
                )
    for index, item in enumerate(spec.get("weak_items", [])):
        evidence_refs = set(map(str, item.get("evidence_refs", [])))
        if not evidence_refs:
            raise ReasoningPortfolioShadowError(
                f"weak_items[{index}] has no evidence refs"
            )
        unknown = evidence_refs - known_source_ids - known_graph_refs
        if unknown:
            raise ReasoningPortfolioShadowError(
                f"weak_items[{index}] has unknown evidence refs: {sorted(unknown)}"
            )

    portfolio = {
        "schema_version": STEP6_ATTENTION_MAP_SCHEMA_VERSION,
        "status": "research_only",
        "runtime_policy": "runtime_dormant",
        "case_id": str(spec["case_id"]),
        "source_refs": [
            f"active-handoff@{_hash_file(active_handoff_path)}",
            f"graph-survival-report@{graph_hash}",
        ],
        "problem_read": spec["problem_read"],
        "active_working_set": [
            {
                key: value
                for key, value in item.items()
                if key != "source_item_id"
            }
            for item in active_items
        ],
        "edge_latticework_reserve": [
            {key: value for key, value in item.items() if key != "graph_trace_ref"}
            for item in spec["edge_items"]
        ],
        "weak_or_negative_space_receipts": [
            {key: value for key, value in item.items() if key != "evidence_refs"}
            for item in spec["weak_items"]
        ],
        "parked_but_preserved": [
            {key: value for key, value in item.items() if key != "graph_trace_ref"}
            for item in spec["parked_items"]
        ],
        "ask_user_if_any": spec["ask_user_if_any"],
        "review_admission": spec["review_admission"],
        "full_archive_refs": spec["full_archive_refs"],
        "step6_instruction": spec["step6_instruction"],
    }
    validate_step6_attention_map_payload(portfolio)
    rendered = render_step6_attention_map(portfolio)

    active_graph_refs = {
        ref
        for item in handoff.get("pressure_items", [])
        for ref in item.get("graph_trace_refs", [])
    }
    portfolio_graph_refs = {
        str(item["graph_trace_ref"])
        for group in (spec["edge_items"], spec["parked_items"])
        for item in group
    }
    validation = {
        "schema_version": VALIDATION_SCHEMA_VERSION,
        "status": "valid_for_shadow_review_only",
        "case_id": spec["case_id"],
        "input_hashes": {
            "spec_sha256": _hash_file(spec_path),
            "active_handoff_sha256": _hash_file(active_handoff_path),
            "graph_report_sha256": graph_hash,
        },
        "active_handoff_item_count": len(known_handoff_ids),
        "active_item_count": len(portfolio["active_working_set"]),
        "active_handoff_coverage_complete": set(active_source_ids)
        == known_handoff_ids,
        "edge_item_count": len(portfolio["edge_latticework_reserve"]),
        "weak_item_count": len(portfolio["weak_or_negative_space_receipts"]),
        "parked_item_count": len(portfolio["parked_but_preserved"]),
        "known_graph_candidate_count": len(known_graph_refs),
        "active_graph_ref_count": len(active_graph_refs),
        "additional_preserved_graph_ref_count": len(
            portfolio_graph_refs - active_graph_refs
        ),
        "rendered_character_count": len(rendered),
        "rendered_character_limit": MAX_RENDER_CHARS,
        "rendered_character_headroom": MAX_RENDER_CHARS - len(rendered),
        "rendered_budget_utilization": round(len(rendered) / MAX_RENDER_CHARS, 4),
        "rendered_budget_warning": (
            "near_limit" if len(rendered) / MAX_RENDER_CHARS >= 0.9 else "none"
        ),
        "builder_model_calls": 0,
        "semantic_relevance_validated": False,
        "answer_quality_validated": False,
        "runtime_integration_authorized": False,
        "non_claims": [
            "compactness_is_not_quality",
            "preservation_is_not_relevance",
            "graph_recall_is_not_causal_attribution",
            "codex_authored_spec_requires_human_review",
        ],
    }
    return portfolio, graph_index, validation


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--active-handoff", type=Path, required=True)
    parser.add_argument("--graph-report", type=Path, required=True)
    parser.add_argument("--portfolio-output", type=Path, required=True)
    parser.add_argument("--graph-index-output", type=Path, required=True)
    parser.add_argument("--validation-output", type=Path, required=True)
    args = parser.parse_args(argv)
    portfolio, graph_index, validation = build_reasoning_portfolio_shadow(
        spec_path=args.spec,
        active_handoff_path=args.active_handoff,
        graph_report_path=args.graph_report,
    )
    _write_json(args.portfolio_output, portfolio)
    _write_json(args.graph_index_output, graph_index)
    _write_json(args.validation_output, validation)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
