from __future__ import annotations

import logging
from dataclasses import dataclass

from .tendency_catalog import TendencyCatalog

_LOGGER = logging.getLogger("system_b.triage")


@dataclass(frozen=True)
class TriageScore:
    tendency_id: str
    score: int
    evidence: str


def parse_pass1_scores(payload: dict[str, object], catalog: TendencyCatalog) -> list[TriageScore]:
    scores = payload.get("scores", [])
    if not isinstance(scores, list):
        return []

    results: list[TriageScore] = []
    for entry in scores:
        if not isinstance(entry, dict):
            continue
        key = str(entry.get("tendency_id", "")).strip()
        if not key:
            continue
        try:
            tendency = catalog.lookup(key)
        except KeyError:
            _LOGGER.debug("Triage: skipping unknown tendency_id %r", key)
            continue
        results.append(
            TriageScore(
                tendency_id=tendency.tendency_id,
                score=_coerce_int(entry.get("score")),
                evidence=str(entry.get("evidence", "")),
            )
        )
    return results


def _coerce_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
