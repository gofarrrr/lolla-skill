"""Deterministic comparison of compact and shadow semantic reads."""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


CORE_SEMANTIC_COMPARISON_SCHEMA_VERSION = "lolla.core_semantic_comparison.v0"


_FAMILY_DIMENSIONS = {
    "question_events": {"operative_question"},
    "user_pressure_events": {"user_corrections_and_pressure"},
    "option_events": {"constraints_and_options"},
    "evidence_boundary_events": {"uncertainty_and_evidence_boundaries"},
    "live_constraint_events": {"constraints_and_options"},
    "assistant_stance_events": {"assistant_positions_and_revisions"},
    "dropped_thread_events": {"dropped_or_under_carried_threads"},
    "reasoning_passages": {"assistant_positions_and_revisions"},
}


def build_core_semantic_comparison(
    *,
    compact_paths: Sequence[Path | str],
    shadow_paths: Sequence[Path | str],
    conversation_path: Path | str,
    gold_path: Path | str,
) -> dict[str, Any]:
    conversation_file = Path(conversation_path)
    gold_file = Path(gold_path)
    conversation_text = conversation_file.read_text(encoding="utf-8")
    gold = json.loads(gold_file.read_text(encoding="utf-8"))
    source_sha256 = hashlib.sha256(conversation_text.encode("utf-8")).hexdigest()
    expected_sha256 = str(gold.get("source_file_sha256") or "")
    if expected_sha256 and source_sha256 != expected_sha256:
        raise ValueError("gold source hash does not match conversation fixture")

    turns = _parse_turns(conversation_text)
    compact_runs = [
        _compact_run(Path(path), turns=turns) for path in compact_paths
    ]
    shadow_runs = [
        _shadow_run(Path(path), turns=turns) for path in shadow_paths
    ]

    return {
        "schema_version": CORE_SEMANTIC_COMPARISON_SCHEMA_VERSION,
        "case_id": str(gold.get("case_id") or ""),
        "source": {
            "conversation_sha256": source_sha256,
            "gold_sha256": hashlib.sha256(gold_file.read_bytes()).hexdigest(),
            "compact_run_count": len(compact_runs),
            "shadow_run_count": len(shadow_runs),
        },
        "compact_path": _path_summary(compact_runs, gold=gold),
        "shadow_path": _path_summary(shadow_runs, gold=gold),
        "comparison_limits": [
            "exact_span_recall measures source-grounded recovery, not total semantic correctness",
            "compact paraphrases may be semantically useful while remaining unverified as source spans",
            "three repeats are an initial stability signal, not a production reliability estimate",
            "gold annotations are provisional source-first research judgments",
        ],
    }


def render_core_semantic_comparison_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_core_semantic_comparison_markdown(payload: Mapping[str, Any]) -> str:
    compact = payload["compact_path"]
    shadow = payload["shadow_path"]
    lines = [
        "# Core Semantic Two-Path Comparison",
        "",
        f"Case: `{payload.get('case_id', '')}`",
        "",
        "## Initial result",
        "",
        "| measure | compact path | shadow path |",
        "| --- | ---: | ---: |",
        f"| repeated runs | {compact['run_count']} | {shadow['run_count']} |",
        f"| exact-span gold recall | {compact['gold_span_recall']['mean_recall']:.3f} | {shadow['gold_span_recall']['mean_recall']:.3f} |",
        f"| mean span repeatability | {compact['repeatability']['mean_span_jaccard']:.3f} | {shadow['repeatability']['mean_span_jaccard']:.3f} |",
        f"| mean label repeatability | {compact['repeatability']['mean_labeled_jaccard']:.3f} | {shadow['repeatability']['mean_labeled_jaccard']:.3f} |",
        "",
        "Exact-span recall is deliberately strict. Compact summaries without literal source spans do not receive source-grounding credit even when their paraphrase is directionally correct.",
        "",
        "## Repeatability by family",
        "",
        "| path | family | counts by run | span Jaccard | labeled Jaccard |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for path_name, summary in (("compact", compact), ("shadow", shadow)):
        for family, record in summary["repeatability"]["families"].items():
            lines.append(
                f"| {path_name} | `{family}` | {record['counts']} | "
                f"{record['span_jaccard']:.3f} | {record['labeled_jaccard']:.3f} |"
            )
    lines.extend(
        [
            "",
            "## Gold observations recovered by exact source span",
            "",
        ]
    )
    for path_name, summary in (("Compact", compact), ("Shadow", shadow)):
        recall = summary["gold_span_recall"]
        lines.extend(
            [
                f"### {path_name}",
                "",
                f"Mean recall: {recall['mean_recall']:.3f}",
                "",
                f"Stable across all repeats: {', '.join(recall['stable_observation_ids']) or 'none'}",
                "",
                f"Never source-grounded: {', '.join(recall['never_observation_ids']) or 'none'}",
                "",
            ]
        )
    lines.extend(["## Limits", ""])
    lines.extend(f"- {item}" for item in payload.get("comparison_limits", []))
    return "\n".join(lines) + "\n"


def _compact_run(path: Path, *, turns: Mapping[tuple[int, str], str]) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    extraction = payload.get("extraction") if isinstance(payload.get("extraction"), dict) else payload
    evidence: dict[str, list[dict[str, Any]]] = {"reasoning_passages": []}
    for passage in extraction.get("reasoning_passages") or []:
        located = _locate_quote(str(passage), turns, preferred_speaker="assistant")
        if located:
            evidence["reasoning_passages"].append(
                {
                    "kind": "reasoning_passage",
                    "turn_index": located[0],
                    "speaker": located[1],
                    "quote": located[2],
                    "grounding": "span",
                    "provenance_status": "exact_span",
                }
            )
    evidence["live_constraints"] = [
        {
            "kind": "constraint",
            "turn_index": int(item.get("introduced_turn") or 0),
            "speaker": "user",
            "quote": "",
            "summary": str(item.get("constraint") or ""),
            "grounding": "turn_ref",
            "provenance_status": "legacy_turn_ref_only",
        }
        for item in extraction.get("live_constraints") or []
        if isinstance(item, dict)
    ]
    evidence["dropped_threads"] = [
        {
            "kind": str(item.get("status") or "dropped_thread"),
            "turn_index": int(item.get("raised_turn") or 0),
            "speaker": str(item.get("raised_by") or "user"),
            "quote": "",
            "summary": str(item.get("thread") or ""),
            "grounding": "turn_ref",
            "provenance_status": "legacy_turn_ref_only",
        }
        for item in extraction.get("dropped_threads") or []
        if isinstance(item, dict)
    ]
    return {
        "path": path.name,
        "decision_text": str(extraction.get("decision_situation") or ""),
        "families": evidence,
    }


def _shadow_run(
    path: Path,
    *,
    turns: Mapping[tuple[int, str], str],
) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_families = payload.get("semantic_events") or {}
    families: dict[str, list[dict[str, Any]]] = {}
    for family, items in raw_families.items():
        normalized: list[dict[str, Any]] = []
        for item in items or []:
            source = item.get("source") if isinstance(item.get("source"), dict) else None
            if source is not None:
                normalized.append(
                    _normalized_item(
                        item,
                        source=source,
                        provenance_status="exact_span",
                    )
                )
                continue

            provenance = item.get("provenance") or {}
            span = provenance.get("span_ref") if isinstance(provenance, dict) else None
            if isinstance(span, dict):
                normalized.append(
                    _normalized_item(
                        item,
                        source={
                            "turn_index": span.get("turn_index")
                            or item.get("turn_index")
                            or item.get("introduced_at_turn"),
                            "speaker": span.get("speaker")
                            or item.get("speaker")
                            or "user",
                            "quote": item.get("text") or "",
                        },
                        provenance_status="exact_span",
                    )
                )
                continue

            components = (
                provenance.get("components")
                if isinstance(provenance, dict)
                else None
            )
            if isinstance(components, list) and components:
                declared_status = str(
                    provenance.get("provenance_status")
                    or item.get("provenance_status")
                    or "component_evidence_complete"
                )
                for component in components:
                    component_payload = (
                        component if isinstance(component, Mapping) else {}
                    )
                    source, component_status = _component_source(
                        component_payload,
                        turns=turns,
                        declared_status=declared_status,
                    )
                    normalized.append(
                        _normalized_item(
                            item,
                            source=source,
                            provenance_status=component_status,
                            component_id=str(
                                component_payload.get("component_id") or ""
                            ),
                            derivation_id=str(
                                provenance.get("derivation_id")
                                or item.get("issue_id")
                                or ""
                            ),
                        )
                    )
                continue

            turn_refs = (
                provenance.get("turn_refs")
                if isinstance(provenance, dict)
                else None
            )
            refs = turn_refs if isinstance(turn_refs, list) and turn_refs else [{}]
            for turn_ref in refs:
                normalized.append(
                    _normalized_item(
                        item,
                        source={
                            "turn_index": turn_ref.get("turn_index")
                            or item.get("turn_index")
                            or item.get("introduced_at_turn"),
                            "speaker": turn_ref.get("speaker")
                            or item.get("speaker")
                            or "user",
                            "quote": "",
                        },
                        provenance_status="legacy_incomplete_provenance",
                    )
                )
        families[family] = normalized
    return {"path": path.name, "decision_text": "", "families": families}


def _normalized_item(
    item: Mapping[str, Any],
    *,
    source: Mapping[str, Any],
    provenance_status: str,
    component_id: str = "",
    derivation_id: str = "",
) -> dict[str, Any]:
    return {
        "kind": str(item.get("kind") or item.get("stance") or ""),
        "turn_index": int(source.get("turn_index") or 0),
        "speaker": str(source.get("speaker") or ""),
        "quote": str(source.get("quote") or ""),
        "summary": str(item.get("text") or ""),
        "grounding": "span" if source.get("quote") else "turn_ref",
        "provenance_status": provenance_status,
        "component_id": component_id,
        "derivation_id": derivation_id,
    }


def _component_source(
    component: Mapping[str, Any],
    *,
    turns: Mapping[tuple[int, str], str],
    declared_status: str,
) -> tuple[dict[str, Any], str]:
    span_ref = (
        component.get("span_ref")
        if isinstance(component.get("span_ref"), dict)
        else {}
    )
    try:
        turn_index = int(span_ref.get("turn_index") or 0)
    except (TypeError, ValueError):
        turn_index = 0
    speaker = str(span_ref.get("speaker") or "")
    quote = str(component.get("quote") or "")
    try:
        start_char = int(span_ref.get("start_char"))
        end_char = int(span_ref.get("end_char"))
    except (TypeError, ValueError):
        start_char = -1
        end_char = -1
    turn_text = turns.get((turn_index, speaker))
    valid = (
        turn_text is not None
        and start_char >= 0
        and end_char >= start_char
        and turn_text[start_char:end_char] == quote
    )
    return (
        {
            "turn_index": turn_index,
            "speaker": speaker,
            "quote": quote if valid else "",
        },
        declared_status if valid else "component_evidence_invalid",
    )


def _path_summary(runs: list[dict[str, Any]], *, gold: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "run_count": len(runs),
        "run_paths": [run["path"] for run in runs],
        "repeatability": _repeatability(runs),
        "gold_span_recall": _gold_span_recall(runs, gold=gold),
        "provenance_status": _provenance_status_summary(runs),
        "decision_text_exact_agreement": len({run["decision_text"] for run in runs}) <= 1,
    }


def _provenance_status_summary(runs: list[dict[str, Any]]) -> dict[str, Any]:
    counts_by_run: list[dict[str, int]] = []
    for run in runs:
        counts: dict[str, int] = {}
        for items in run["families"].values():
            for item in items:
                status = str(item.get("provenance_status") or "unknown")
                counts[status] = counts.get(status, 0) + 1
        counts_by_run.append(dict(sorted(counts.items())))
    return {
        "counts_by_run": counts_by_run,
        "legacy_incomplete_count": sum(
            counts.get("legacy_incomplete_provenance", 0)
            for counts in counts_by_run
        ),
        "invalid_component_count": sum(
            counts.get("component_evidence_invalid", 0)
            for counts in counts_by_run
        ),
    }


def _repeatability(runs: list[dict[str, Any]]) -> dict[str, Any]:
    families = sorted({family for run in runs for family in run["families"]})
    records: dict[str, dict[str, Any]] = {}
    span_scores: list[float] = []
    label_scores: list[float] = []
    for family in families:
        span_sets = [_signature_set(run, family, labeled=False) for run in runs]
        label_sets = [_signature_set(run, family, labeled=True) for run in runs]
        span_score = _mean_pairwise_jaccard(span_sets)
        label_score = _mean_pairwise_jaccard(label_sets)
        records[family] = {
            "counts": [len(run["families"].get(family, [])) for run in runs],
            "span_jaccard": span_score,
            "labeled_jaccard": label_score,
        }
        span_scores.append(span_score)
        label_scores.append(label_score)
    return {
        "mean_span_jaccard": sum(span_scores) / len(span_scores) if span_scores else 0.0,
        "mean_labeled_jaccard": sum(label_scores) / len(label_scores) if label_scores else 0.0,
        "families": records,
    }


def _gold_span_recall(runs: list[dict[str, Any]], *, gold: Mapping[str, Any]) -> dict[str, Any]:
    observations = gold.get("required_observations") or []
    per_run: list[dict[str, Any]] = []
    recovered_sets: list[set[str]] = []
    for run in runs:
        recovered: set[str] = set()
        for observation in observations:
            if _observation_recovered(run, observation):
                recovered.add(str(observation.get("observation_id") or ""))
        recovered_sets.append(recovered)
        total = len(observations)
        per_run.append(
            {
                "recovered_count": len(recovered),
                "total_count": total,
                "recall": len(recovered) / total if total else 0.0,
                "observation_ids": sorted(recovered),
            }
        )
    all_ids = {str(item.get("observation_id") or "") for item in observations}
    stable = set.intersection(*recovered_sets) if recovered_sets else set()
    ever = set.union(*recovered_sets) if recovered_sets else set()
    return {
        "mean_recall": sum(item["recall"] for item in per_run) / len(per_run) if per_run else 0.0,
        "per_run": per_run,
        "stable_observation_ids": sorted(stable),
        "never_observation_ids": sorted(all_ids - ever),
    }


def _observation_recovered(run: Mapping[str, Any], observation: Mapping[str, Any]) -> bool:
    dimension = str(observation.get("dimension") or "")
    for family, items in run["families"].items():
        if dimension not in _FAMILY_DIMENSIONS.get(family, set()):
            continue
        for item in items:
            if item.get("grounding") != "span":
                continue
            for evidence in observation.get("evidence") or []:
                if (
                    int(item.get("turn_index") or 0) == int(evidence.get("turn_index") or -1)
                    and str(item.get("speaker") or "") == str(evidence.get("speaker") or "")
                    and _quotes_overlap(str(item.get("quote") or ""), str(evidence.get("quote") or ""))
                ):
                    return True
    return False


def _signature_set(run: Mapping[str, Any], family: str, *, labeled: bool) -> set[str]:
    signatures = set()
    for item in run["families"].get(family, []):
        quote = _normalize_quote(str(item.get("quote") or item.get("summary") or ""))
        base = f"{int(item.get('turn_index') or 0)}|{item.get('speaker') or ''}|{quote}"
        signatures.add(f"{item.get('kind') or ''}|{base}" if labeled else base)
    return signatures


def _mean_pairwise_jaccard(sets: list[set[str]]) -> float:
    if len(sets) < 2:
        return 1.0 if sets else 0.0
    scores = []
    for left_index in range(len(sets)):
        for right_index in range(left_index + 1, len(sets)):
            left = sets[left_index]
            right = sets[right_index]
            union = left | right
            scores.append(len(left & right) / len(union) if union else 1.0)
    return sum(scores) / len(scores)


def _parse_turns(text: str) -> dict[tuple[int, str], str]:
    pattern = re.compile(r"\[Turn (\d+)\] (USER|ASSISTANT):\n")
    matches = list(pattern.finditer(text))
    turns: dict[tuple[int, str], str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        turns[(int(match.group(1)), match.group(2).lower())] = text[start:end].strip()
    return turns


def _locate_quote(quote: str, turns: Mapping[tuple[int, str], str], *, preferred_speaker: str) -> tuple[int, str, str] | None:
    for (turn, speaker), text in turns.items():
        if speaker != preferred_speaker:
            continue
        if quote and quote in text:
            return turn, speaker, quote
    return None


def _quotes_overlap(left: str, right: str) -> bool:
    a = _normalize_quote(left)
    b = _normalize_quote(right)
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    a_tokens = set(a.split())
    b_tokens = set(b.split())
    union = a_tokens | b_tokens
    return bool(union) and len(a_tokens & b_tokens) / len(union) >= 0.6


def _normalize_quote(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))
