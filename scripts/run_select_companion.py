#!/usr/bin/env python3
"""
Companion cheat-sheet selection for Lolla skill.

Takes fingerprinted companion chunks + DeltaCard model IDs and produces a
compact, bounded, de-duplicated CompanionCheatSheet with anti-echo filtering.

Usage:
    python3 scripts/run_select_companion.py \
        --chunks-json '{"models": [{"model_id": "...", "display_name": "...", "chunks": [...]}]}' \
        --delta-model-ids "base-rates,premortem"

    python3 scripts/run_select_companion.py --help

Input --chunks-json schema:
    {
      "models": [
        {
          "model_id": "systems-thinking",
          "display_name": "Systems Thinking",
          "chunks": [
            {
              "chunk_type": "identity|failure_mode|heuristic|premortem|ally|antagonist",
              "text": "chunk content",
              "source_layer": "wave1|wave2|wave3",
              "extraction_type": "explicit|normalized|unknown",
              "confidence": "high|medium|low|unknown",
              "relation_target_id": ""
            }
          ]
        }
      ]
    }

Output: JSON CompanionCheatSheet with model anchors and selected chunks.
"""

import argparse
import json
import re
import sys
from collections import Counter


# ---------------------------------------------------------------------------
# Budget defaults
# ---------------------------------------------------------------------------

DEFAULT_BUDGET_MAX = 20
DEFAULT_PER_MODEL_CAP = 5
DEFAULT_PER_TYPE_CAP = 5

# Chunk types that echo the DeltaCard when the same model appears in both.
# Heuristic hints restate "how to use this model" which the DeltaCard already
# covers via next_moves. Identity chunks are KEPT because the companion lane's
# identity ("you're already using this model — here's when it's dangerous")
# is different from the delta card's introduction ("you should start using this").
_ECHO_TYPES = frozenset({"heuristic"})

CHUNK_TYPE_PRIORITY = {
    "failure_mode": 0,
    "premortem": 1,
    "antagonist": 2,
    "heuristic": 3,
    "ally": 4,
    "identity": 5,
}

CONFIDENCE_RANK = {"high": 0, "medium": 1, "low": 2}


# ---------------------------------------------------------------------------
# Internal types (plain dicts for script simplicity)
# ---------------------------------------------------------------------------

def _chunk_sort_key(chunk: dict) -> tuple:
    return (
        CHUNK_TYPE_PRIORITY.get(chunk.get("chunk_type", ""), 9),
        CONFIDENCE_RANK.get(chunk.get("confidence", ""), 3),
        0 if chunk.get("extraction_type") == "explicit" else 1,
        chunk.get("text", "")[:40],
    )


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) >= 3}


def _texts_overlap(a: str, b: str) -> bool:
    tokens_a = _tokenize(a)
    tokens_b = _tokenize(b)
    if not tokens_a or not tokens_b:
        return False
    return len(tokens_a & tokens_b) / min(len(tokens_a), len(tokens_b)) >= 0.8


def select(
    models_data: list[dict],
    delta_model_ids: set[str],
    *,
    budget_max: int = DEFAULT_BUDGET_MAX,
    per_model_cap: int = DEFAULT_PER_MODEL_CAP,
    per_type_cap: int = DEFAULT_PER_TYPE_CAP,
) -> dict:
    """Run the full companion selection pipeline.

    Returns a JSON-serializable CompanionCheatSheet dict.
    """
    # Step 1: Flatten all chunks with source model info
    candidates = []
    display_names = {}
    for model in models_data:
        model_id = model["model_id"]
        display_names[model_id] = model.get("display_name", model_id)
        for chunk in model.get("chunks", []):
            candidates.append({
                "chunk_type": chunk.get("chunk_type", ""),
                "source_model_id": model_id,
                "text": chunk.get("text", ""),
                "source_layer": chunk.get("source_layer", "unknown"),
                "extraction_type": chunk.get("extraction_type", "unknown"),
                "confidence": chunk.get("confidence", "unknown"),
                "relation_target_id": chunk.get("relation_target_id", ""),
            })

    # Step 2: Anti-echo — drop echo types for delta-overlapping models
    if delta_model_ids:
        candidates = [
            c for c in candidates
            if not (c["source_model_id"] in delta_model_ids and c["chunk_type"] in _ECHO_TYPES)
        ]

    # Step 3: Deduplicate by text overlap
    deduped = []
    for chunk in candidates:
        if any(_texts_overlap(chunk["text"], existing["text"]) for existing in deduped):
            continue
        deduped.append(chunk)
    candidates = deduped

    # Step 4: Sort by type priority, confidence, extraction type
    candidates.sort(key=_chunk_sort_key)

    # Step 5: Group by model
    by_model: dict[str, list[dict]] = {}
    for chunk in candidates:
        by_model.setdefault(chunk["source_model_id"], []).append(chunk)

    # Step 6: Two-pass selection
    type_counts: Counter = Counter()
    model_counts: Counter = Counter()
    selected: list[dict] = []
    used: set[tuple[str, int]] = set()
    model_ids = list(by_model.keys())

    # Pass 1 — Type diversity: one chunk of each type
    all_types = ["failure_mode", "premortem", "antagonist", "heuristic", "ally", "identity"]
    for chunk_type in all_types:
        if len(selected) >= budget_max:
            break
        for model_id in model_ids:
            if model_counts[model_id] >= per_model_cap:
                continue
            for idx, chunk in enumerate(by_model[model_id]):
                key = (model_id, idx)
                if key in used:
                    continue
                if chunk["chunk_type"] != chunk_type:
                    continue
                selected.append(chunk)
                used.add(key)
                type_counts[chunk["chunk_type"]] += 1
                model_counts[model_id] += 1
                break
            else:
                continue
            break

    # Pass 2 — Round-robin breadth and depth
    if len(selected) < budget_max:
        max_rounds = max((len(v) for v in by_model.values()), default=0)
        for _ in range(max_rounds):
            for model_id in model_ids:
                if len(selected) >= budget_max:
                    break
                if model_counts[model_id] >= per_model_cap:
                    continue
                for idx, chunk in enumerate(by_model[model_id]):
                    key = (model_id, idx)
                    if key in used:
                        continue
                    if type_counts[chunk["chunk_type"]] >= per_type_cap:
                        continue
                    selected.append(chunk)
                    used.add(key)
                    type_counts[chunk["chunk_type"]] += 1
                    model_counts[model_id] += 1
                    break
            if len(selected) >= budget_max:
                break

    # Step 7: Assemble into anchors
    anchor_chunks: dict[str, list[dict]] = {}
    for chunk in selected:
        anchor_chunks.setdefault(chunk["source_model_id"], []).append(chunk)

    anchors = []
    for model_id, chunks in anchor_chunks.items():
        anchors.append({
            "model_id": model_id,
            "display_name": display_names.get(model_id, model_id),
            "chunks": [
                {
                    "chunk_type": c["chunk_type"],
                    "text": c["text"],
                    "provenance": {
                        "source_layer": c["source_layer"],
                        "extraction_type": c["extraction_type"],
                        "confidence": c["confidence"],
                        **({"relation_target_id": c["relation_target_id"]}
                           if c.get("relation_target_id") else {}),
                    },
                }
                for c in chunks
            ],
        })

    return {
        "anchors": anchors,
        "total_chunk_count": len(selected),
        "budget_max": budget_max,
        "anti_echo_model_ids": sorted(delta_model_ids),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Companion cheat-sheet selection: anti-echo, dedup, budget, two-pass diversity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Input --chunks-json: JSON with {"models": [{"model_id", "display_name", "chunks": [...]}]}
Each chunk: {"chunk_type", "text", "source_layer", "extraction_type", "confidence"}

--delta-model-ids: Comma-separated model IDs already in the DeltaCard (for anti-echo).
  Heuristic chunks for these models are dropped; all other types are kept.

Output: JSON CompanionCheatSheet with model anchors and selected chunks.
""",
    )
    parser.add_argument("--chunks-json", required=True,
                        help="JSON string with models and their chunks")
    parser.add_argument("--delta-model-ids", default="",
                        help="Comma-separated model IDs from DeltaCard (for anti-echo)")
    parser.add_argument("--budget-max", type=int, default=DEFAULT_BUDGET_MAX,
                        help=f"Maximum total chunks (default: {DEFAULT_BUDGET_MAX})")
    parser.add_argument("--per-model-cap", type=int, default=DEFAULT_PER_MODEL_CAP,
                        help=f"Maximum chunks per model (default: {DEFAULT_PER_MODEL_CAP})")
    parser.add_argument("--per-type-cap", type=int, default=DEFAULT_PER_TYPE_CAP,
                        help=f"Maximum chunks of any single type (default: {DEFAULT_PER_TYPE_CAP})")
    args = parser.parse_args()

    try:
        data = json.loads(args.chunks_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    models_data = data.get("models", [])
    delta_ids = {mid.strip() for mid in args.delta_model_ids.split(",") if mid.strip()}

    result = select(
        models_data,
        delta_ids,
        budget_max=args.budget_max,
        per_model_cap=args.per_model_cap,
        per_type_cap=args.per_type_cap,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
