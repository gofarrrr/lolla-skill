from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping


def load_route_quality_review_status(root: Path) -> dict[str, dict[str, str]]:
    path = Path(root) / "route_quality_review_status.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {}

    registry: dict[str, dict[str, str]] = {}
    for tendency_id, entry in payload.items():
        if not isinstance(entry, Mapping):
            continue
        normalized_entry: dict[str, str] = {}
        for key, value in entry.items():
            normalized_key = str(key).strip()
            normalized_value = str(value).strip()
            if normalized_key and normalized_value:
                normalized_entry[normalized_key] = normalized_value
        if normalized_entry:
            registry[str(tendency_id).strip()] = normalized_entry
    return registry
