from __future__ import annotations

import logging
from dataclasses import dataclass

from .boundary_validation import coerce_int, coerce_str, require_list_of_dicts
from .tendency_catalog import TendencyCatalog

_LOGGER = logging.getLogger("system_b.triage")

_BOUNDARY = "pass1_triage"


@dataclass(frozen=True)
class TriageScore:
    tendency_id: str
    score: int
    evidence: str


def parse_pass1_scores(payload: dict[str, object], catalog: TendencyCatalog) -> list[TriageScore]:
    entries = require_list_of_dicts(payload, "scores", _BOUNDARY)

    results: list[TriageScore] = []
    for entry in entries:
        key = coerce_str(entry.get("tendency_id")).strip()
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
                score=coerce_int(entry.get("score")),
                evidence=coerce_str(entry.get("evidence")),
            )
        )
    return results
