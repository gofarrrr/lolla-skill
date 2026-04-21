#!/usr/bin/env python3
"""Phase 3 Commit B step 4 — programmatic fixture synthesis (option 2 under 14e).

Doctrine-safe because NO outcome is asserted by the author. The expected
result of every scenario is MEASURED from cosine math against the live
embeddings DB, not chosen. If reality disagrees with intent, the scenario
is classified by what the numbers say.

Pipeline:
  1. Build the near-tie seed pool: every seed whose top-1 and top-2
     fan-adjusted ally/compound affinities differ by < ε. This is the same
     pool that drove the ε calibration in handover §14h item 2 step 2.
  2. Quasi-random selection: seeds sorted by id, take every k-th to spread
     across the graph ("all over the place" per user). No taste calls.
  3. For each selected (seed, top1, top2):
       - probe_top1 = top1's `select_when[0]` from knowledge_graph.json
       - probe_top2 = top2's `select_when[0]`
       - probe_offtopic = `select_when[0]` of a model picked by a
         deterministic hash of the seed id, constrained to be NOT in the
         seed's neighborhood.
     `select_when` is third-party curator prose about "when to reach for
     this model" — authored for a different purpose than activation_condition,
     so using it as a probe is NOT the author eyeballing AC strings.
  4. Embed every probe once via OpenAI, cache in frozen_probes.json.
  5. Read both activation_condition embeddings from `edge_activation_conditions`.
  6. Compute cosine(probe, top1_ac) and cosine(probe, top2_ac) for each
     (seed, probe) pair. Classify the scenario by gate rules:
       - If max(cos_top1, cos_top2) < noise_floor → expect ABSTAIN
       - elif cos_top2 > cos_top1 → expect SWAP (top2 promoted)
       - else → expect NO-SWAP (top1 stays)
  7. Emit scenario JSON files under tests/fixtures/activation_tiebreaker/
     with the measured outcome embedded.

Run:
    OPENAI_API_KEY=... python3 scripts/synthesize_tiebreaker_fixtures.py

Idempotent — won't re-embed probes already in frozen_probes.json.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sqlite3
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from engine.system_b.embedding_retriever import embed_query
from engine.system_b.relation_graph import (
    _ACTIVATION_MATCH_EPSILON,
    _ACTIVATION_MATCH_NOISE_FLOOR,
)

GRAPH_PATH = REPO / "data" / "relationship_graph.json"
KG_PATH = REPO / "data" / "knowledge_graph.json"
DB_PATH = REPO / "data" / "embeddings.db"
FIXTURE_DIR = REPO / "tests" / "fixtures" / "activation_tiebreaker"
SCENARIO_DIR = FIXTURE_DIR / "scenarios"
FROZEN_PROBES_PATH = FIXTURE_DIR / "frozen_probes.json"

TARGET_SCENARIO_COUNT = 30  # pool cap; actual emitted count may be less if pool is smaller


def _fan_adjust(affinity: float, fan: int) -> float:
    if fan <= 1:
        return affinity
    return affinity / (1.0 + math.log(fan))


def _build_near_tie_pool() -> list[dict]:
    """Walk the compiled graph and emit {seed, top1, top2, delta, ac_top1, ac_top2}
    for every seed whose top-1 / top-2 ally-or-compound fan-adjusted affinities
    differ by less than ε."""
    edges = json.loads(GRAPH_PATH.read_text())
    adj: dict[str, list[dict]] = {}
    degree: dict[str, int] = {}
    for e in edges:
        src = str(e.get("source_model_id", "")).strip()
        tgt = str(e.get("target_model_id", "")).strip()
        etype = str(e.get("edge_type", "")).strip().lower()
        if not src or not tgt or not etype:
            continue
        adj.setdefault(src, []).append({
            "target": tgt,
            "edge_type": etype,
            "affinity": float(e.get("composition_affinity") or 0.0),
            "activation_condition": str(e.get("activation_condition", "") or ""),
        })
        degree[src] = degree.get(src, 0) + 1
        degree[tgt] = degree.get(tgt, 0) + 1

    pool: list[dict] = []
    for seed, neighbors in adj.items():
        allies = [n for n in neighbors if n["edge_type"] in {"ally", "compound"}]
        ranked = sorted(
            (
                {
                    "target": n["target"],
                    "edge_type": n["edge_type"],
                    "raw_affinity": n["affinity"],
                    "adj_affinity": _fan_adjust(n["affinity"], degree.get(n["target"], 1)),
                    "activation_condition": n["activation_condition"],
                }
                for n in allies if n["affinity"] >= 0.6
            ),
            key=lambda r: (-r["adj_affinity"], r["target"]),
        )
        if len(ranked) < 2:
            continue
        top1, top2 = ranked[0], ranked[1]
        delta = top1["adj_affinity"] - top2["adj_affinity"]
        if delta >= _ACTIVATION_MATCH_EPSILON:
            continue
        if not top1["activation_condition"] or not top2["activation_condition"]:
            continue
        pool.append({
            "seed": seed,
            "top1": top1,
            "top2": top2,
            "delta": delta,
        })
    pool.sort(key=lambda p: p["seed"])
    return pool


def _load_select_when() -> dict[str, str]:
    """model_id → first select_when sentence (third-party prose, not AC)."""
    kg = json.loads(KG_PATH.read_text())
    out: dict[str, str] = {}
    for model_id, record in kg.get("models", {}).items():
        sw = record.get("select_when") or []
        if isinstance(sw, list) and sw:
            first = str(sw[0]).strip()
            if first:
                out[model_id] = first
    return out


def _pick_offtopic(seed: str, adj_pool: set[str], all_models: list[str]) -> str:
    """Deterministic pick: hash(seed) → index into models sorted by id,
    stepping until we find a model NOT in the seed's neighborhood and
    not the seed itself. No taste."""
    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    sorted_models = sorted(all_models)
    n = len(sorted_models)
    for offset in range(n):
        candidate = sorted_models[(h + offset) % n]
        if candidate != seed and candidate not in adj_pool:
            return candidate
    raise RuntimeError(f"no off-topic candidate for {seed}")


def _unpack_embedding(blob: bytes) -> list[float]:
    # Matches scripts/build_edge_activation_embeddings.py storage format.
    count = len(blob) // 4
    return list(struct.unpack(f"{count}f", blob))


def _load_ac_embedding(conn: sqlite3.Connection, source: str, target: str, edge_type: str) -> list[float] | None:
    row = conn.execute(
        """SELECT embedding FROM edge_activation_conditions
           WHERE source_model_id = ? AND target_model_id = ? AND edge_type = ?""",
        (source, target, edge_type),
    ).fetchone()
    if row is None:
        return None
    return _unpack_embedding(row[0])


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def _load_frozen_probes() -> dict:
    if FROZEN_PROBES_PATH.exists():
        return json.loads(FROZEN_PROBES_PATH.read_text())
    return {}


def _classify(cos_top1: float, cos_top2: float) -> str:
    if max(cos_top1, cos_top2) < _ACTIVATION_MATCH_NOISE_FLOOR:
        return "abstain"
    if cos_top2 > cos_top1:
        return "swap"
    return "no_swap"


def main() -> int:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY missing", file=sys.stderr)
        return 1

    pool = _build_near_tie_pool()
    print(f"near-tie pool size: {len(pool)} seeds (δ < {_ACTIVATION_MATCH_EPSILON})")
    if not pool:
        print("pool empty — nothing to synthesize", file=sys.stderr)
        return 1

    # Quasi-random selection: every k-th seed by sorted id.
    step = max(1, len(pool) // TARGET_SCENARIO_COUNT)
    selected = pool[::step][:TARGET_SCENARIO_COUNT]
    print(f"selected {len(selected)} seeds (every {step}-th, sorted by seed_id)")

    select_when = _load_select_when()
    kg = json.loads(KG_PATH.read_text())
    edges = json.loads(GRAPH_PATH.read_text())

    # Build adjacency for off-topic picking.
    adj_set: dict[str, set[str]] = {}
    for e in edges:
        s = str(e.get("source_model_id", "")).strip()
        t = str(e.get("target_model_id", "")).strip()
        if s and t:
            adj_set.setdefault(s, set()).add(t)
            adj_set.setdefault(t, set()).add(s)

    frozen = _load_frozen_probes()

    def ensure_probe(key: str, text: str) -> None:
        if key in frozen and isinstance(frozen[key], dict) and frozen[key].get("text") == text and frozen[key].get("vector"):
            return
        vec = embed_query(text, api_key)
        if not vec:
            raise RuntimeError(f"embedding failed for probe {key}")
        frozen[key] = {"text": text, "vector": vec}
        print(f"  embedded {key}")

    conn = sqlite3.connect(DB_PATH)

    scenarios_written = 0
    by_class: dict[str, int] = {"swap": 0, "no_swap": 0, "abstain": 0, "skipped": 0}
    existing_scenario_ids: set[str] = set()
    SCENARIO_DIR.mkdir(parents=True, exist_ok=True)

    # Preserve pre-existing starter scenarios (01, 02, 03) — do not overwrite.
    for p in SCENARIO_DIR.glob("*.json"):
        existing_scenario_ids.add(p.stem)

    for idx, entry in enumerate(selected, start=1):
        seed = entry["seed"]
        t1 = entry["top1"]["target"]
        t2 = entry["top2"]["target"]
        e1 = entry["top1"]["edge_type"]
        e2 = entry["top2"]["edge_type"]

        sw_t1 = select_when.get(t1)
        sw_t2 = select_when.get(t2)
        if not sw_t1 or not sw_t2:
            by_class["skipped"] += 1
            continue

        offtopic_model = _pick_offtopic(seed, adj_set.get(seed, set()) | {seed}, list(kg.get("models", {}).keys()))
        sw_off = select_when.get(offtopic_model)
        if not sw_off:
            by_class["skipped"] += 1
            continue

        k_t1 = f"synth_{seed}__probe_top1_{t1}"
        k_t2 = f"synth_{seed}__probe_top2_{t2}"
        k_off = f"synth_{seed}__probe_offtopic_{offtopic_model}"

        ensure_probe(k_t1, sw_t1)
        ensure_probe(k_t2, sw_t2)
        ensure_probe(k_off, sw_off)

        ac1_vec = _load_ac_embedding(conn, seed, t1, e1)
        ac2_vec = _load_ac_embedding(conn, seed, t2, e2)
        if ac1_vec is None or ac2_vec is None:
            by_class["skipped"] += 1
            continue

        scenarios_for_seed = [
            ("probe_top1", k_t1, t1),
            ("probe_top2", k_t2, t2),
            ("probe_offtopic", k_off, offtopic_model),
        ]
        for suffix, probe_key, source_model in scenarios_for_seed:
            pvec = frozen[probe_key]["vector"]
            cos1 = _cosine(pvec, ac1_vec)
            cos2 = _cosine(pvec, ac2_vec)
            cls = _classify(cos1, cos2)
            by_class[cls] += 1

            if cls == "swap":
                expected_top = [t2, t1]
            elif cls == "no_swap":
                expected_top = [t1, t2]
            else:
                expected_top = [t1, t2]  # abstain → default order survives

            scenario_id = f"synth_{idx:02d}_{seed}_{suffix}"
            if scenario_id in existing_scenario_ids:
                continue

            payload = {
                "name": f"synth near-tie seed {seed}; probe {suffix} → {cls}",
                "description": (
                    "Programmatically synthesized via "
                    "scripts/synthesize_tiebreaker_fixtures.py. Probe text "
                    "is the top-1 select_when sentence from a third-party "
                    f"model ({source_model}) in the knowledge graph — NOT "
                    "authored in-session. Expected outcome is DERIVED from "
                    "cosine measurement against the live embeddings DB, not "
                    "asserted by the author. See §14e option 2 in the handover."
                ),
                "claim_type": "programmatic_synthesis",
                "seed_model_id": seed,
                "probe_key": probe_key,
                "top1_model_id": t1,
                "top2_model_id": t2,
                "delta_adj_affinity": round(entry["delta"], 6),
                "measured_cosines": {
                    "probe_vs_ac_top1": round(cos1, 4),
                    "probe_vs_ac_top2": round(cos2, 4),
                },
                "expected": {
                    "gate_class": cls,
                    "top_supporting_model_ids": expected_top,
                },
                "notes": (
                    "Outcome classified by gate rules: "
                    "max(cos_top1, cos_top2) < 0.45 → abstain; "
                    "cos_top2 > cos_top1 → swap; else no_swap. "
                    "If this scenario's assertion is wrong, the matcher changed "
                    "OR the DB was rebuilt with different embeddings — "
                    "re-running the synthesizer will recompute the expected class."
                ),
            }
            (SCENARIO_DIR / f"{scenario_id}.json").write_text(json.dumps(payload, indent=2) + "\n")
            scenarios_written += 1

    FROZEN_PROBES_PATH.write_text(json.dumps(frozen, indent=2) + "\n")
    print(f"scenarios written: {scenarios_written}")
    print(f"class distribution: {by_class}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
