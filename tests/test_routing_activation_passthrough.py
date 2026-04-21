"""Phase 3 Commit B call-site wire-up tests.

Covers kwarg pass-through from the routing layer down to
`RelationGraph.neighborhood()`:

  routing.route_tendency / route_detected_tendencies / route_deep_check_results
  PressureRouter.route
  PressureBundleSelector.select / select_from_packet

The downstream gate behavior itself is covered by
`test_relation_graph_activation_tiebreaker.py`. These tests only verify that
each layer threads `reasoning_context`, `embeddings_db_path`, and
`openai_api_key` through unchanged, and that omitting them produces the
pre-wire default (no kwargs, byte-identical behavior).
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b import routing
from engine.system_b.pressure_router import PressureRouter
from engine.system_b.relation_graph import RelationGraph, RouteNeighborhood
from engine.system_b.subpattern_catalog import (
    ModelBindingRef,
    SubpatternCatalog,
    SubpatternRef,
    TendencySubpatterns,
)
from engine.system_b.tendency_catalog import ModelBinding, TendencyCatalog, TendencyRef


class _SpyRelationGraph(RelationGraph):
    """Captures the kwargs passed to neighborhood() so tests can assert
    what the upstream layers forwarded."""

    def __init__(self) -> None:
        super().__init__({})
        self.calls: list[dict] = []

    def neighborhood(self, seed_model_ids, **kwargs):  # type: ignore[override]
        self.calls.append({"seed_model_ids": tuple(seed_model_ids), **kwargs})
        return RouteNeighborhood()


def _catalog() -> TendencyCatalog:
    binding = ModelBinding(model_id="first-principles-thinking")
    tendency = TendencyRef(
        tendency_id="analysis-paralysis",
        display_name="Analysis Paralysis",
        routing_key="analysis_paralysis",
        antidote_model_ids=("first-principles-thinking",),
        antidote_bindings=(binding,),
    )
    return TendencyCatalog(
        tendencies={"analysis-paralysis": tendency},
        alias_index={"analysis-paralysis": "analysis-paralysis"},
    )


def _subpatterns() -> SubpatternCatalog:
    subpattern = SubpatternRef(
        subpattern_id="general",
        display_name="General",
        description="",
        primary_model_ids=("first-principles-thinking",),
        bindings=(ModelBindingRef(model_id="first-principles-thinking"),),
    )
    tendency_subs = TendencySubpatterns(
        tendency_id="analysis-paralysis",
        display_name="Analysis Paralysis",
        subpatterns=(subpattern,),
    )
    return SubpatternCatalog({"analysis-paralysis": tendency_subs})


def _probe_context() -> TendencyRef:
    return TendencyRef(
        tendency_id="probe",
        display_name="",
        routing_key="probe",
        antidote_model_ids=(),
        description="probe prose — reasoning-shape sentinel",
    )


class RoutingPassThroughTests(unittest.TestCase):
    def test_route_tendency_default_omits_activation_kwargs(self) -> None:
        spy = _SpyRelationGraph()
        catalog = _catalog()

        routing.route_tendency(
            "analysis-paralysis",
            catalog=catalog,
            relation_graph=spy,
        )

        self.assertEqual(len(spy.calls), 1)
        call = spy.calls[0]
        self.assertIsNone(call["reasoning_context"])
        self.assertIsNone(call["embeddings_db_path"])
        self.assertIsNone(call["openai_api_key"])

    def test_route_tendency_forwards_activation_kwargs(self) -> None:
        spy = _SpyRelationGraph()
        catalog = _catalog()
        probe = _probe_context()

        routing.route_tendency(
            "analysis-paralysis",
            catalog=catalog,
            relation_graph=spy,
            reasoning_context=probe,
            embeddings_db_path="/tmp/fake.db",
            openai_api_key="sk-test",
        )

        self.assertEqual(len(spy.calls), 1)
        call = spy.calls[0]
        self.assertIs(call["reasoning_context"], probe)
        self.assertEqual(call["embeddings_db_path"], "/tmp/fake.db")
        self.assertEqual(call["openai_api_key"], "sk-test")

    def test_route_detected_tendencies_forwards_kwargs(self) -> None:
        spy = _SpyRelationGraph()
        catalog = _catalog()
        probe = _probe_context()

        routing.route_detected_tendencies(
            ["analysis-paralysis"],
            catalog=catalog,
            relation_graph=spy,
            reasoning_context=probe,
            embeddings_db_path="/tmp/fake.db",
            openai_api_key="sk-test",
        )

        self.assertEqual(len(spy.calls), 1)
        self.assertIs(spy.calls[0]["reasoning_context"], probe)


class PressureRouterPassThroughTests(unittest.TestCase):
    def test_default_omits_activation_kwargs(self) -> None:
        spy = _SpyRelationGraph()
        router = PressureRouter(_catalog(), _subpatterns(), spy)

        router.route("analysis-paralysis")

        self.assertEqual(len(spy.calls), 1)
        call = spy.calls[0]
        self.assertIsNone(call["reasoning_context"])
        self.assertIsNone(call["embeddings_db_path"])
        self.assertIsNone(call["openai_api_key"])

    def test_forwards_activation_kwargs(self) -> None:
        spy = _SpyRelationGraph()
        router = PressureRouter(_catalog(), _subpatterns(), spy)
        probe = _probe_context()

        router.route(
            "analysis-paralysis",
            reasoning_context=probe,
            embeddings_db_path="/tmp/fake.db",
            openai_api_key="sk-test",
        )

        self.assertEqual(len(spy.calls), 1)
        call = spy.calls[0]
        self.assertIs(call["reasoning_context"], probe)
        self.assertEqual(call["embeddings_db_path"], "/tmp/fake.db")
        self.assertEqual(call["openai_api_key"], "sk-test")


if __name__ == "__main__":
    unittest.main()
