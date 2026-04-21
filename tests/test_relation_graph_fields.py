"""Section 14 Phase 0: verify affinity_rationale + activation_condition
flow from relationship_graph.json into the skill-side RelationNeighbor.

Mirrors Lolla-system-b/tests/test_relation_graph.py's Phase0FieldPlumbingTests.
Both sides keep the same guard because the two relation_graph.py files are
maintained in parallel — this test catches accidental divergence.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.relation_graph import RelationGraph, RelationNeighbor


class Phase0FieldPlumbingTests(unittest.TestCase):
    def test_relation_neighbor_accepts_new_fields(self) -> None:
        neighbor = RelationNeighbor(
            model_id="m",
            edge_type="ally",
            composition_affinity=0.9,
            affinity_rationale="because x composes with y",
            activation_condition="when reasoning settles on a single cause",
        )
        self.assertEqual(neighbor.affinity_rationale, "because x composes with y")
        self.assertEqual(neighbor.activation_condition, "when reasoning settles on a single cause")

    def test_relation_neighbor_defaults_new_fields_to_empty(self) -> None:
        neighbor = RelationNeighbor("m", "ally", 0.9)
        self.assertEqual(neighbor.affinity_rationale, "")
        self.assertEqual(neighbor.activation_condition, "")

    def test_load_populates_new_fields_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            build = root / "build"
            build.mkdir()
            (build / "relationship_graph.json").write_text(
                json.dumps([
                    {
                        "source_model_id": "a",
                        "target_model_id": "b",
                        "edge_type": "ally",
                        "composition_affinity": 0.9,
                        "affinity_rationale": "rationale-text",
                        "activation_condition": "condition-text",
                    },
                ]),
                encoding="utf-8",
            )
            graph = RelationGraph.load(root)
            neighbors = graph._graph["a"]
            self.assertEqual(len(neighbors), 1)
            self.assertEqual(neighbors[0].affinity_rationale, "rationale-text")
            self.assertEqual(neighbors[0].activation_condition, "condition-text")

    def test_load_defaults_new_fields_when_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            build = root / "build"
            build.mkdir()
            (build / "relationship_graph.json").write_text(
                json.dumps([
                    {
                        "source_model_id": "a",
                        "target_model_id": "b",
                        "edge_type": "ally",
                        "composition_affinity": 0.9,
                    },
                ]),
                encoding="utf-8",
            )
            graph = RelationGraph.load(root)
            neighbors = graph._graph["a"]
            self.assertEqual(neighbors[0].affinity_rationale, "")
            self.assertEqual(neighbors[0].activation_condition, "")


if __name__ == "__main__":
    unittest.main()
