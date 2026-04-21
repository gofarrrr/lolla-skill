"""Phase 3 Commit B invariant tests for `RelationGraph.neighborhood()`'s
activation-match near-tie tiebreaker.

These tests check ENGINEERING INVARIANTS of the gate (when it fires, when it
doesn't, what it does when it fires). They do NOT encode claims of the form
"for reasoning-shape X, the correct model is Y" — those claims belong in
fixture-authored tests under the 14e blind-authoring protocol, which must be
written by someone other than the matcher author (or with second-reader
review). See research/deep-graph-enrichment-handover.md §14e.

Invariants covered:
  1. Default path (no `reasoning_context`) is byte-identical to pre-wire.
  2. Gate does NOT fire when top-1/top-2 delta ≥ ε.
  3. Gate does NOT fire when matcher's top similarity < noise floor.
  4. Gate DOES fire when delta < ε AND top sim ≥ noise floor AND matcher
     picks top-2 as the higher-cosine candidate.
  5. Gate does NOT fire when `relevance_scores` are supplied (that path
     has its own ordering logic; activation-match doesn't overrule it).
  6. Gate does NOT fire when matcher returns empty (graceful degradation).
  7. TypeError from the matcher propagates (programmer-error contract).
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.activation_matcher import ActivationMatchResult
from engine.system_b.relation_graph import (
    RelationGraph,
    RelationNeighbor,
    _ACTIVATION_MATCH_EPSILON,
    _ACTIVATION_MATCH_NOISE_FLOOR,
)
from engine.system_b.tendency_catalog import TendencyRef


def _make_graph(edges: list[tuple[str, str, str, float]]) -> RelationGraph:
    """Build a RelationGraph from (source, target, edge_type, affinity) tuples."""
    adj: dict[str, list[RelationNeighbor]] = {}
    for src, tgt, etype, aff in edges:
        adj.setdefault(src, []).append(
            RelationNeighbor(
                model_id=tgt,
                edge_type=etype,
                composition_affinity=aff,
            )
        )
    return RelationGraph({s: tuple(ns) for s, ns in adj.items()})


def _probe() -> TendencyRef:
    """A facts-free reasoning-shape input usable as `reasoning_context`.
    Content is irrelevant — the stub matcher ignores it."""
    return TendencyRef(
        tendency_id="probe",
        display_name="Probe",
        routing_key="probe",
        antidote_model_ids=(),
        description="stand-in for a real reasoning-shape input",
    )


class DefaultPathInvariantTests(unittest.TestCase):
    """Invariant 1: omitting `reasoning_context` leaves behavior untouched."""

    def test_no_reasoning_context_same_as_before_wire(self) -> None:
        graph = _make_graph([
            ("seed", "alpha", "ally", 0.90),
            ("seed", "beta", "ally", 0.895),  # near-tie with alpha
        ])
        # No reasoning_context; expect affinity-based ordering (alpha first,
        # beta second tied by lexicographic tiebreak within _bounded_...).
        result = graph.neighborhood(["seed"], max_supporting_models=2)
        self.assertEqual(result.supporting_model_ids, ("alpha", "beta"))

    def test_reasoning_context_without_db_path_is_noop(self) -> None:
        """Gate requires both `reasoning_context` AND `embeddings_db_path`.
        Missing either → no activation-match call, default behavior."""
        graph = _make_graph([
            ("seed", "alpha", "ally", 0.90),
            ("seed", "beta", "ally", 0.895),
        ])

        called: list = []

        def tracking_matcher(*args, **kwargs):
            called.append(1)
            return ()

        result = graph.neighborhood(
            ["seed"],
            max_supporting_models=2,
            reasoning_context=_probe(),
            # embeddings_db_path omitted intentionally
            _activation_matcher=tracking_matcher,
        )
        self.assertEqual(result.supporting_model_ids, ("alpha", "beta"))
        self.assertEqual(called, [])  # matcher must not have been called


class EpsilonGateTests(unittest.TestCase):
    """Invariant 2: gate does not fire outside the ε window."""

    def test_non_tie_does_not_consult_matcher(self) -> None:
        # delta = 0.05, well above ε (0.01)
        graph = _make_graph([
            ("seed", "alpha", "ally", 0.90),
            ("seed", "beta", "ally", 0.85),
        ])

        called: list = []

        def tracking_matcher(*args, **kwargs):
            called.append(1)
            return ()

        result = graph.neighborhood(
            ["seed"],
            max_supporting_models=2,
            reasoning_context=_probe(),
            embeddings_db_path="/tmp/unused.db",
            _activation_matcher=tracking_matcher,
        )
        self.assertEqual(result.supporting_model_ids, ("alpha", "beta"))
        self.assertEqual(called, [])  # matcher never consulted outside ε

    def test_exactly_at_epsilon_boundary_does_not_fire(self) -> None:
        # delta exactly ε → not "< ε" → gate does not fire
        graph = _make_graph([
            ("seed", "alpha", "ally", 0.90),
            ("seed", "beta", "ally", 0.90 - _ACTIVATION_MATCH_EPSILON),
        ])

        called: list = []

        def tracking_matcher(*args, **kwargs):
            called.append(1)
            return ()

        result = graph.neighborhood(
            ["seed"],
            max_supporting_models=2,
            reasoning_context=_probe(),
            embeddings_db_path="/tmp/unused.db",
            _activation_matcher=tracking_matcher,
        )
        self.assertEqual(result.supporting_model_ids, ("alpha", "beta"))
        self.assertEqual(called, [])


class NoiseFloorGateTests(unittest.TestCase):
    """Invariant 3: gate does not fire below the noise floor."""

    def test_top_sim_below_floor_does_not_swap(self) -> None:
        graph = _make_graph([
            ("seed", "alpha", "ally", 0.90),
            ("seed", "beta", "ally", 0.895),
        ])

        def weak_matcher(_ctx, edges, *, db_path, api_key):
            # Both below floor; even though beta scores higher, signal is noise
            return tuple(
                ActivationMatchResult(
                    source_model_id=s, target_model_id=t, edge_type=e,
                    similarity=0.40 if t == "beta" else 0.30,
                )
                for (s, t, e) in edges
            )

        result = graph.neighborhood(
            ["seed"],
            max_supporting_models=2,
            reasoning_context=_probe(),
            embeddings_db_path="/tmp/unused.db",
            _activation_matcher=weak_matcher,
        )
        # Both below 0.45 floor → no swap
        self.assertEqual(result.supporting_model_ids, ("alpha", "beta"))

    def test_top2_above_floor_top1_below_still_swaps(self) -> None:
        """`max(sim_top1, sim_top2) ≥ floor` is the guard; not both."""
        graph = _make_graph([
            ("seed", "alpha", "ally", 0.90),
            ("seed", "beta", "ally", 0.895),
        ])

        def matcher(_ctx, edges, *, db_path, api_key):
            return tuple(
                ActivationMatchResult(
                    source_model_id=s, target_model_id=t, edge_type=e,
                    similarity=0.80 if t == "beta" else 0.20,
                )
                for (s, t, e) in edges
            )

        result = graph.neighborhood(
            ["seed"],
            max_supporting_models=2,
            reasoning_context=_probe(),
            embeddings_db_path="/tmp/unused.db",
            _activation_matcher=matcher,
        )
        # beta's 0.80 is well above floor; swap happens
        self.assertEqual(result.supporting_model_ids, ("beta", "alpha"))


class SwapBehaviorTests(unittest.TestCase):
    """Invariant 4: when all gates open, top-2 replaces top-1 if it scores
    higher. Top-3 and beyond are preserved in their affinity-sorted order."""

    def test_swap_when_top2_wins(self) -> None:
        graph = _make_graph([
            ("seed", "alpha", "ally", 0.90),
            ("seed", "beta", "ally", 0.895),
            ("seed", "gamma", "ally", 0.80),  # well outside ε
        ])

        def matcher(_ctx, edges, *, db_path, api_key):
            return tuple(
                ActivationMatchResult(
                    source_model_id=s, target_model_id=t, edge_type=e,
                    similarity=0.70 if t == "beta" else 0.50,
                )
                for (s, t, e) in edges
            )

        result = graph.neighborhood(
            ["seed"],
            max_supporting_models=3,
            reasoning_context=_probe(),
            embeddings_db_path="/tmp/unused.db",
            _activation_matcher=matcher,
        )
        # beta surfaced past alpha; gamma unchanged
        self.assertEqual(result.supporting_model_ids, ("beta", "alpha", "gamma"))

    def test_no_swap_when_top1_wins(self) -> None:
        graph = _make_graph([
            ("seed", "alpha", "ally", 0.90),
            ("seed", "beta", "ally", 0.895),
        ])

        def matcher(_ctx, edges, *, db_path, api_key):
            return tuple(
                ActivationMatchResult(
                    source_model_id=s, target_model_id=t, edge_type=e,
                    similarity=0.70 if t == "alpha" else 0.50,
                )
                for (s, t, e) in edges
            )

        result = graph.neighborhood(
            ["seed"],
            max_supporting_models=2,
            reasoning_context=_probe(),
            embeddings_db_path="/tmp/unused.db",
            _activation_matcher=matcher,
        )
        # alpha's sim higher → no swap
        self.assertEqual(result.supporting_model_ids, ("alpha", "beta"))

    def test_risk_candidates_also_retied(self) -> None:
        """Antagonist/tension path uses the same tiebreaker."""
        graph = _make_graph([
            ("seed", "alpha-risk", "antagonist", 0.90),
            ("seed", "beta-risk", "antagonist", 0.895),
        ])

        def matcher(_ctx, edges, *, db_path, api_key):
            return tuple(
                ActivationMatchResult(
                    source_model_id=s, target_model_id=t, edge_type=e,
                    similarity=0.70 if t == "beta-risk" else 0.50,
                )
                for (s, t, e) in edges
            )

        result = graph.neighborhood(
            ["seed"],
            max_risk_models=2,
            reasoning_context=_probe(),
            embeddings_db_path="/tmp/unused.db",
            _activation_matcher=matcher,
        )
        self.assertEqual(result.risk_model_ids, ("beta-risk", "alpha-risk"))


class RelevanceScoresOverrideTests(unittest.TestCase):
    """Invariant 5: when `relevance_scores` are supplied, they are the
    authoritative ordering signal; activation-match is not consulted."""

    def test_relevance_scores_skip_activation_matcher(self) -> None:
        graph = _make_graph([
            ("seed", "alpha", "ally", 0.90),
            ("seed", "beta", "ally", 0.895),
        ])

        called: list = []

        def tracking_matcher(*args, **kwargs):
            called.append(1)
            return ()

        result = graph.neighborhood(
            ["seed"],
            max_supporting_models=2,
            reasoning_context=_probe(),
            embeddings_db_path="/tmp/unused.db",
            relevance_scores={"alpha": 0.1, "beta": 0.9},  # beta has higher relevance
            _activation_matcher=tracking_matcher,
        )
        # relevance_scores should order beta above alpha
        self.assertEqual(result.supporting_model_ids, ("beta", "alpha"))
        self.assertEqual(called, [])  # activation matcher not consulted


class GracefulDegradationTests(unittest.TestCase):
    """Invariant 6: gate degrades gracefully on empty/missing matcher output."""

    def test_empty_matcher_output_is_noop(self) -> None:
        graph = _make_graph([
            ("seed", "alpha", "ally", 0.90),
            ("seed", "beta", "ally", 0.895),
        ])

        def empty_matcher(*args, **kwargs):
            return ()  # e.g., DB missing rows for these edges

        result = graph.neighborhood(
            ["seed"],
            max_supporting_models=2,
            reasoning_context=_probe(),
            embeddings_db_path="/tmp/unused.db",
            _activation_matcher=empty_matcher,
        )
        self.assertEqual(result.supporting_model_ids, ("alpha", "beta"))

    def test_matcher_exception_other_than_typeerror_is_noop(self) -> None:
        """Any non-TypeError exception from the matcher is treated as a
        runtime degradation — gate abstains."""
        graph = _make_graph([
            ("seed", "alpha", "ally", 0.90),
            ("seed", "beta", "ally", 0.895),
        ])

        def raising_matcher(*args, **kwargs):
            raise RuntimeError("network flaked")

        result = graph.neighborhood(
            ["seed"],
            max_supporting_models=2,
            reasoning_context=_probe(),
            embeddings_db_path="/tmp/unused.db",
            _activation_matcher=raising_matcher,
        )
        self.assertEqual(result.supporting_model_ids, ("alpha", "beta"))


class TypeErrorPropagationTests(unittest.TestCase):
    """Invariant 7: TypeError from the matcher is a programmer-error contract
    violation (caller passed something outside `ReasoningShapeInput`). It
    propagates — never masked as a runtime degradation."""

    def test_typeerror_propagates(self) -> None:
        graph = _make_graph([
            ("seed", "alpha", "ally", 0.90),
            ("seed", "beta", "ally", 0.895),
        ])

        def strict_matcher(*args, **kwargs):
            raise TypeError("match_activation: reasoning_input must be one of ...")

        with self.assertRaises(TypeError):
            graph.neighborhood(
                ["seed"],
                max_supporting_models=2,
                reasoning_context=_probe(),
                embeddings_db_path="/tmp/unused.db",
                _activation_matcher=strict_matcher,
            )


class CalibrationConstantsTests(unittest.TestCase):
    """Sanity-check the data-grounded constants against the measurement
    recorded in commit 43d39e4. If these change, update the handover doc
    §14h item 2 and re-justify from fresh measurement — not by taste."""

    def test_epsilon_matches_measurement(self) -> None:
        self.assertEqual(_ACTIVATION_MATCH_EPSILON, 0.01)

    def test_noise_floor_matches_measurement(self) -> None:
        self.assertEqual(_ACTIVATION_MATCH_NOISE_FLOOR, 0.45)


if __name__ == "__main__":
    unittest.main()
