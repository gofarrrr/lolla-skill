"""Phase 3 Commit B smoke tests — real graph, real DB, frozen probe vectors.

These tests run `RelationGraph.neighborhood(reasoning_context=...)` against
the real compiled graph (`data/relationship_graph.json`) and the real
backfilled embeddings DB (`data/embeddings.db`). Probe vectors are frozen
in `tests/fixtures/activation_tiebreaker/frozen_probes.json` so the tests
stay offline and deterministic.

Scope: MECHANICAL FAITHFULNESS only. Each scenario declares an expected
output order that follows from cosine between the probe and curator ACs.
It does NOT encode "model X is the right antidote for Y" — that's a
semantic claim that needs blind-authored fixtures under the 14e protocol.

If `data/relationship_graph.json` or `data/embeddings.db` or the frozen
probe file is missing, tests are skipped rather than failed — this keeps
the suite green in environments that don't carry the artifacts.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.activation_matcher import match_activation
from engine.system_b.relation_graph import RelationGraph, RelationNeighbor
from engine.system_b.tendency_catalog import TendencyRef


_REPO = Path(__file__).resolve().parents[1]
_FIXTURE_DIR = _REPO / "tests" / "fixtures" / "activation_tiebreaker"
_GRAPH_PATH = _REPO / "data" / "relationship_graph.json"
_DB_PATH = _REPO / "data" / "embeddings.db"
_PROBES_PATH = _FIXTURE_DIR / "frozen_probes.json"


def _artifacts_available() -> bool:
    return _GRAPH_PATH.exists() and _DB_PATH.exists() and _PROBES_PATH.exists()


def _load_graph() -> RelationGraph:
    """Load the real compiled graph via the same field-mapping the production
    loader uses. We don't use RelationGraph.load() because it looks for
    `build/relationship_graph.json`; our test artifact lives in `data/`."""
    edges = json.loads(_GRAPH_PATH.read_text())
    adj: dict[str, list[RelationNeighbor]] = {}
    for e in edges:
        src = str(e.get("source_model_id", "")).strip()
        tgt = str(e.get("target_model_id", "")).strip()
        if not src or not tgt:
            continue
        adj.setdefault(src, []).append(
            RelationNeighbor(
                model_id=tgt,
                edge_type=str(e.get("edge_type", "")).strip().lower(),
                composition_affinity=float(e.get("composition_affinity") or 0.0),
                source_description=str(e.get("source_description", "") or ""),
                affinity_rationale=str(e.get("affinity_rationale", "") or ""),
                activation_condition=str(e.get("activation_condition", "") or ""),
            )
        )
    return RelationGraph({s: tuple(ns) for s, ns in adj.items()})


def _frozen_embedder_factory(probe_text: str, probe_vec: list[float]):
    """Return an embedder closure that hands back `probe_vec` when called
    with exactly `probe_text`, and returns None otherwise. The matcher
    should only ever call the embedder once per request, with the exact
    adapter-produced prose — mismatch means the adapter changed and the
    fixture needs revisiting."""
    def _embed(text: str, api_key: str) -> list[float] | None:
        if text == probe_text:
            return probe_vec
        # Unexpected text — surface as an empty embed (matcher will abstain),
        # which will fail the fixture assertion and flag the drift.
        return None
    return _embed


def _probe_as_tendency_ref(probe_text: str) -> TendencyRef:
    """Pack the probe text into a TendencyRef's description field. The
    adapter `_prose_from_tendency_ref` emits `display_name + description`,
    so keep display_name empty to make the emitted prose exactly
    `probe_text`. This keeps the frozen-vector lookup a direct match."""
    return TendencyRef(
        tendency_id="probe",
        display_name="",  # keep empty so adapter's output == probe_text
        routing_key="probe",
        antidote_model_ids=(),
        description=probe_text,
    )


@unittest.skipUnless(_artifacts_available(), "graph/DB/probes artifacts missing")
class RealDataMechanicalFaithfulnessTests(unittest.TestCase):
    """Each scenario JSON becomes one subtest here."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = _load_graph()
        cls.probes = json.loads(_PROBES_PATH.read_text())
        cls.scenarios = sorted((_FIXTURE_DIR / "scenarios").glob("*.json"))

    def test_scenarios(self) -> None:
        self.assertGreater(len(self.scenarios), 0, "no scenario files found")
        for scenario_path in self.scenarios:
            with self.subTest(scenario=scenario_path.name):
                scen = json.loads(scenario_path.read_text())
                probe = self.probes[scen["probe_key"]]
                probe_text = probe["text"]
                probe_vec = probe["vector"]

                # Build a matcher bound to the frozen embedder so no network
                # call happens. match_activation supports `embedder=` override.
                embedder = _frozen_embedder_factory(probe_text, probe_vec)

                def bound_matcher(reasoning_input, edges, *, db_path, api_key):
                    return match_activation(
                        reasoning_input,
                        edges,
                        db_path=db_path,
                        api_key=api_key,
                        embedder=embedder,
                    )

                result = self.graph.neighborhood(
                    [scen["seed_model_id"]],
                    max_supporting_models=len(
                        scen["expected"]["top_supporting_model_ids"]
                    ),
                    reasoning_context=_probe_as_tendency_ref(probe_text),
                    embeddings_db_path=str(_DB_PATH),
                    openai_api_key="unused-frozen-embedder",
                    _activation_matcher=bound_matcher,
                )

                self.assertEqual(
                    list(result.supporting_model_ids),
                    scen["expected"]["top_supporting_model_ids"],
                    msg=(
                        f"fixture {scenario_path.name}: expected "
                        f"{scen['expected']['top_supporting_model_ids']}, got "
                        f"{list(result.supporting_model_ids)}"
                    ),
                )

    def test_determinism(self) -> None:
        """Same scenario run twice → identical output. Guards against
        hidden nondeterminism in the dedup / sort / gate pipeline."""
        if not self.scenarios:
            self.skipTest("no scenarios")
        scen = json.loads(self.scenarios[0].read_text())
        probe = self.probes[scen["probe_key"]]
        embedder = _frozen_embedder_factory(probe["text"], probe["vector"])

        def bound_matcher(reasoning_input, edges, *, db_path, api_key):
            return match_activation(
                reasoning_input, edges,
                db_path=db_path, api_key=api_key, embedder=embedder,
            )

        kwargs = dict(
            seed_model_ids=[scen["seed_model_id"]],
            max_supporting_models=len(scen["expected"]["top_supporting_model_ids"]),
            reasoning_context=_probe_as_tendency_ref(probe["text"]),
            embeddings_db_path=str(_DB_PATH),
            openai_api_key="unused-frozen-embedder",
            _activation_matcher=bound_matcher,
        )
        first = self.graph.neighborhood(**kwargs)
        second = self.graph.neighborhood(**kwargs)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
