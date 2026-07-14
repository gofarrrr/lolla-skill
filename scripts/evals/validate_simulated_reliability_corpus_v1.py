#!/usr/bin/env python3
"""Provider-free custody validator for the frozen V1 simulated corpus."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evals.run_simulated_reliability_naturalization_v1 import _proposal_review


DEFAULT_MANIFEST = Path(
    "research/simulated-reliability-corpus-v1-2026-07-12/manifest.json"
)
HEADER_RE = re.compile(
    r"^CONVERSATION:\s*(\d+)\s+turns,\s*(\d+)\s+user messages,\s*"
    r"(\d+)\s+assistant responses$"
)
MARKER_RE = re.compile(r"^\[Turn (\d+)\] (USER|ASSISTANT):$", re.MULTILINE)
CASE_ID_RE = re.compile(r"^Case ID:\s*(\S+)\s*$", re.MULTILINE)
FORBIDDEN_SOURCE_PATTERNS = {
    "lolla": re.compile(r"\blolla\b", re.IGNORECASE),
    "mental_model": re.compile(r"\bmental[ -]models?\b", re.IGNORECASE),
    "graph_language": re.compile(r"\bgraph(?:-based)?\s+(?:system|pressure|selection)\b", re.IGNORECASE),
    "expected_pressure": re.compile(r"\bexpected[ -]pressure\b", re.IGNORECASE),
    "gold_answer": re.compile(r"\bgold[ -]answer\b", re.IGNORECASE),
    "stand_down_label": re.compile(r"\bstand[ -]down(?:_expected)?\b", re.IGNORECASE),
}


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve(root: Path, record: dict[str, Any], label: str) -> Path:
    path = root / str(record["path"])
    if not path.is_file():
        raise AssertionError(f"missing {label}: {path}")
    actual = _sha256(path)
    if actual != record["sha256"]:
        raise AssertionError(
            f"{label} hash mismatch for {path}: {actual} != {record['sha256']}"
        )
    return path


def validate(manifest_path: Path = DEFAULT_MANIFEST, *, root: Path | None = None) -> dict[str, Any]:
    root = (root or Path.cwd()).resolve()
    path = manifest_path if manifest_path.is_absolute() else root / manifest_path
    manifest = _load_json(path)

    if manifest["status"] != "frozen_complete_provider_free":
        raise AssertionError("V1 manifest is not frozen")
    if manifest["case_count"] != 20:
        raise AssertionError("V1 must contain exactly 20 cases")
    if manifest["calibration_count"] != 8 or manifest["transfer_count"] != 12:
        raise AssertionError("V1 must contain 8 calibration and 12 transfer cases")

    contract_path = _resolve(root, manifest["authoring_contract"], "authoring contract")
    inventory_path = _resolve(root, manifest["inventory"], "inventory")
    review_path = _resolve(root, manifest["source_review"], "source review")
    naturalized_review_path = _resolve(
        root, manifest["naturalized_source_review"], "naturalized source review"
    )
    draft_path = _resolve(root, manifest["pre_call_draft_record"], "pre-call draft record")
    contract = _load_json(contract_path)
    _load_json(inventory_path)
    review = _load_json(review_path)
    naturalized_review = _load_json(naturalized_review_path)
    draft = _load_json(draft_path)

    if contract["status"] != "frozen_complete_after_naturalism_correction":
        raise AssertionError("authoring contract has not reached its final freeze")
    if contract["turn_pairs_per_case"] != 12:
        raise AssertionError("authoring contract must require 12 turn pairs")
    if any(draft["custody_at_invalidation"].values()):
        raise AssertionError("short draft was used before invalidation")

    calibration = manifest["calibration_cases"]
    transfer = manifest["transfer_cases"]
    if len(calibration) != 8 or len(transfer) != 12:
        raise AssertionError("manifest arrays contradict declared counts")

    case_ids: list[str] = []
    hashes: list[str] = []
    for record in calibration:
        _resolve(root, record, f"calibration case {record['case_id']}")
        case_ids.append(record["case_id"])
        hashes.append(record["sha256"])

    for record in transfer:
        source_path = _resolve(root, record, f"transfer case {record['case_id']}")
        text = source_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        header = HEADER_RE.fullmatch(lines[0] if lines else "")
        if not header or tuple(map(int, header.groups())) != (24, 12, 12):
            raise AssertionError(f"invalid capture header: {source_path}")

        markers = [(int(turn), role) for turn, role in MARKER_RE.findall(text)]
        expected = [
            (turn, role)
            for turn in range(1, 13)
            for role in ("USER", "ASSISTANT")
        ]
        if markers != expected:
            raise AssertionError(f"turn sequence mismatch: {source_path}")
        if record["message_count"] != len(markers):
            raise AssertionError(f"message count mismatch: {source_path}")

        ids = CASE_ID_RE.findall(text)
        if ids != [record["case_id"]]:
            raise AssertionError(f"case ID mismatch: {source_path}")
        words = len(text.split())
        if words != record["word_count"]:
            raise AssertionError(f"word count mismatch: {source_path}")
        if words < 1500:
            raise AssertionError(f"transfer source remains too compressed: {source_path}")

        split = re.split(
            r"(?m)^\[Turn \d+\] (USER|ASSISTANT):\n",
            text,
        )[1:]
        shape_review = _proposal_review(
            {
                "messages": [
                    {"role": role, "text": body.strip()}
                    for role, body in zip(split[0::2], split[1::2])
                ]
            }
        )
        if shape_review["status"] != "provider_free_shape_pass_semantic_review_required":
            raise AssertionError(
                f"naturalism shape review failed for {source_path}: {shape_review['issues']}"
            )

        for name, pattern in FORBIDDEN_SOURCE_PATTERNS.items():
            if pattern.search(text):
                raise AssertionError(f"{name} leakage in {source_path}")
        case_ids.append(record["case_id"])
        hashes.append(record["sha256"])

    if len(case_ids) != len(set(case_ids)):
        raise AssertionError("duplicate case IDs")
    if len(hashes) != len(set(hashes)):
        raise AssertionError("duplicate source hashes")

    review_cases = review["cases"]
    review_ids = [record["case_id"] for record in review_cases]
    transfer_ids = [record["case_id"] for record in transfer]
    if review_ids != transfer_ids:
        raise AssertionError("source-review order or identity differs from transfer manifest")
    behavior_counts = Counter(record["expected_public_behavior"] for record in review_cases)
    expected_counts = Counter(contract["public_behavior_mix"])
    if behavior_counts != expected_counts:
        raise AssertionError(
            f"public behavior mix mismatch: {dict(behavior_counts)} != {dict(expected_counts)}"
        )
    if manifest["source_review"]["supplied_to_pipeline_or_reasoners"]:
        raise AssertionError("source review must remain hidden from pipeline and reasoners")
    naturalized_review_ids = [row["case_id"] for row in naturalized_review["cases"]]
    if naturalized_review_ids != transfer_ids:
        raise AssertionError("naturalized source-review identities differ from transfer manifest")
    if naturalized_review["status"] != "all_twelve_provider_free_naturalized_variants_admitted_for_final_corpus_freeze":
        raise AssertionError("naturalized source review has not admitted all cases")
    if manifest["naturalized_source_review"]["supplied_to_pipeline_or_reasoners"]:
        raise AssertionError("naturalized source review must remain hidden from pipeline and reasoners")

    return {
        "status": "pass",
        "calibration_cases": len(calibration),
        "transfer_cases": len(transfer),
        "transfer_messages": sum(record["message_count"] for record in transfer),
        "transfer_words": sum(record["word_count"] for record in transfer),
        "behavior_mix": dict(behavior_counts),
        "lolla_pipeline_provider_calls": 0,
        "rejected_source_editor_provider_calls": manifest["freeze_boundary"][
            "rejected_source_editor_provider_calls"
        ],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, sort_keys=True))
