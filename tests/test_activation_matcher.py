"""Phase 3 Commit A — unit tests for the activation matcher.

These tests cover the three invariants that keep the matcher aligned with
the reasoning-about-reasoning doctrine:

1. Typed-input enforcement at the API boundary. Raw strings, dicts, or
   anything outside the five supported types must raise TypeError before
   any embedding or DB work happens.
2. Facts/Reasoning Break inside each adapter. Every adapter drops the
   facts-carrying fields on its input type (evidence_quotes, etc.) and
   emits only reasoning-shape prose.
3. Graceful degradation on missing embedder / missing DB / missing
   backfill rows. The matcher returns an empty tuple; it never raises at
   runtime.

Tests run offline. The embedder is dependency-injected with canned vectors
so no network calls happen — that lets the tests also pin the cosine
arithmetic and the per-edge lookup flow.
"""
from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.activation_matcher import (
    ActivationMatchResult,
    _prose_from_dimension_route,
    _prose_from_fingerprint,
    _prose_from_frame_route,
    _prose_from_tendency_ref,
    _prose_from_triggered_tendency,
    match_activation,
)
from engine.system_b.companion import FingerprintMove, FingerprintPayload
from engine.system_b.edge_activation_store import (
    ensure_schema,
    upsert_edge_embedding,
)
from engine.system_b.frame_pressure import FrameRoute
from engine.system_b.pipeline import TriggeredTendency
from engine.system_b.structural_coverage import DimensionRoute
from engine.system_b.tendency_catalog import TendencyRef


def _unit_vec(*components: float) -> list[float]:
    """Return a unit-length vector. Makes cosine similarity easy to predict
    (two unit vectors along the same axis → similarity 1.0; orthogonal → 0.0)."""
    norm = math.sqrt(sum(c * c for c in components))
    return [c / norm for c in components] if norm else list(components)


class TypedInputEnforcementTests(unittest.TestCase):
    """Invariant 1: the API rejects anything outside the five supported types
    before running any embedder or DB work. This is the structural defense
    against a caller sliding a raw query string or extracted fact into the
    matcher."""

    def test_raw_string_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            match_activation(
                "the user asked about Q3 pricing",  # type: ignore[arg-type]
                [],
                db_path="/tmp/nonexistent.db",
            )

    def test_dict_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            match_activation(
                {"reasoning_move": "x"},  # type: ignore[arg-type]
                [],
                db_path="/tmp/nonexistent.db",
            )

    def test_none_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            match_activation(
                None,  # type: ignore[arg-type]
                [],
                db_path="/tmp/nonexistent.db",
            )


class FactsBreakAdapterTests(unittest.TestCase):
    """Invariant 2: adapters drop facts-bearing fields and emit only
    reasoning-shape prose. If any of these regress, facts are reaching the
    matcher and the Facts/Reasoning Break has broken."""

    def test_fingerprint_adapter_drops_evidence_quotes(self) -> None:
        fp = FingerprintPayload(
            raw=[],
            validated=[
                FingerprintMove(
                    move_id="m1",
                    reasoning_move="inverting the failure mode",
                    evidence_quotes=[
                        "the customer said 'we will never adopt this'",
                        "Q3 revenue was $42M",
                    ],
                    evidence_rationale="the answer pivots by restating the loss",
                    confidence="high",
                ),
            ],
            dropped=[],
        )
        prose = _prose_from_fingerprint(fp)
        self.assertIn("inverting the failure mode", prose)
        self.assertIn("restating the loss", prose)
        self.assertNotIn("Q3 revenue was $42M", prose)
        self.assertNotIn("customer said", prose)

    def test_fingerprint_adapter_ignores_non_validated_moves(self) -> None:
        fp = FingerprintPayload(
            raw=[
                FingerprintMove(
                    move_id="m_raw",
                    reasoning_move="raw-only noise",
                    evidence_quotes=[],
                    evidence_rationale="",
                    confidence="low",
                ),
            ],
            validated=[],
            dropped=[],
        )
        self.assertEqual(_prose_from_fingerprint(fp), "")

    def test_triggered_tendency_adapter_returns_only_id_prose(self) -> None:
        t = TriggeredTendency(
            tendency_id="social-proof-tendency",
            source="triage",
            score=7,
        )
        self.assertEqual(
            _prose_from_triggered_tendency(t),
            "social proof tendency",
        )

    def test_tendency_ref_adapter_joins_name_and_description(self) -> None:
        ref = TendencyRef(
            tendency_id="social-proof",
            display_name="Social Proof",
            routing_key="social_proof",
            antidote_model_ids=("circle-of-competence",),
            description="Defer to the crowd when direction is unclear.",
        )
        prose = _prose_from_tendency_ref(ref)
        self.assertIn("Social Proof", prose)
        self.assertIn("Defer to the crowd", prose)

    def test_frame_route_adapter_returns_pattern_only(self) -> None:
        r = FrameRoute(
            element_index=0,
            frame_pattern="false_binary",
            candidate_model_ids=("dialectical-reasoning",),
            excluded_model_ids=(),
        )
        # FrameRoute has no evidence_quote field by design — facts live on
        # ExtractedFrameElement. This test documents the structural
        # separation so a future refactor that adds quotes to FrameRoute
        # gets caught.
        self.assertEqual(_prose_from_frame_route(r), "false binary")

    def test_dimension_route_adapter_returns_dimension_name_only(self) -> None:
        r = DimensionRoute(
            dimension_id="time-horizon",
            dimension_name="Time Horizon",
            candidate_model_ids=(),
            excluded_model_ids=(),
        )
        # DetectedDimension carries coverage_evidence (quoted answer text);
        # DimensionRoute does not — this is the structural separation.
        self.assertEqual(_prose_from_dimension_route(r), "Time Horizon")


class MatcherEndToEndTests(unittest.TestCase):
    """End-to-end flow with a stub embedder and a real (temp) sqlite DB.
    Pins the cosine arithmetic + per-edge lookup, so a regression on either
    side surfaces here."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmp.name) / "embeddings.db"
        ensure_schema(self.db_path)

        # Two candidate edges. One has an activation_condition aligned with
        # the 'x' axis; the other with the 'y' axis. We'll give the matcher
        # an 'x'-aligned reasoning prose and expect edge-1 to win.
        upsert_edge_embedding(
            self.db_path,
            source_model_id="base-rates",
            target_model_id="probabilistic-thinking",
            edge_type="ally",
            activation_condition_text="when assessing rare events under calibration",
            embedding=_unit_vec(1.0, 0.0),
        )
        upsert_edge_embedding(
            self.db_path,
            source_model_id="base-rates",
            target_model_id="regression-to-the-mean",
            edge_type="ally",
            activation_condition_text="when a result looks exceptional relative to a noisy baseline",
            embedding=_unit_vec(0.0, 1.0),
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _stub_embedder_x_axis(self, text: str, api_key: str) -> list[float]:
        # Canned: any reasoning prose → x-axis vector. In a real run the
        # embedder would produce different vectors per text; the stub's
        # job is to make the DB-lookup and cosine paths deterministic.
        return _unit_vec(1.0, 0.0)

    def _stub_embedder_zero(self, text: str, api_key: str) -> None:
        return None

    def test_winner_has_highest_cosine_similarity(self) -> None:
        ref = TendencyRef(
            tendency_id="overoptimism",
            display_name="Overoptimism Tendency",
            routing_key="overoptimism",
            antidote_model_ids=("probabilistic-thinking",),
            description="Systematic underweighting of failure paths.",
        )
        results = match_activation(
            ref,
            [
                ("base-rates", "probabilistic-thinking", "ally"),
                ("base-rates", "regression-to-the-mean", "ally"),
            ],
            db_path=self.db_path,
            api_key="stub",
            embedder=self._stub_embedder_x_axis,
        )
        self.assertEqual(len(results), 2)
        by_target = {r.target_model_id: r.similarity for r in results}
        # X-axis stub vs. x-axis edge → 1.0; vs. y-axis edge → 0.0.
        self.assertAlmostEqual(by_target["probabilistic-thinking"], 1.0, places=4)
        self.assertAlmostEqual(by_target["regression-to-the-mean"], 0.0, places=4)

    def test_missing_backfill_row_is_silently_dropped(self) -> None:
        ref = TendencyRef(
            tendency_id="x",
            display_name="X",
            routing_key="x",
            antidote_model_ids=(),
            description="x",
        )
        results = match_activation(
            ref,
            [
                ("base-rates", "probabilistic-thinking", "ally"),  # present
                ("base-rates", "never-backfilled", "ally"),         # absent
            ],
            db_path=self.db_path,
            api_key="stub",
            embedder=self._stub_embedder_x_axis,
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].target_model_id, "probabilistic-thinking")

    def test_empty_prose_returns_empty_result(self) -> None:
        # TriggeredTendency with empty id → empty prose → empty result,
        # no embedder ever called.
        calls: list[str] = []

        def tracking_embedder(text: str, api_key: str) -> list[float]:
            calls.append(text)
            return _unit_vec(1.0, 0.0)

        t = TriggeredTendency(tendency_id="", source="triage", score=0)
        results = match_activation(
            t,
            [("a", "b", "ally")],
            db_path=self.db_path,
            api_key="stub",
            embedder=tracking_embedder,
        )
        self.assertEqual(results, ())
        self.assertEqual(calls, [])  # embedder must not have been called

    def test_embedder_failure_returns_empty_result(self) -> None:
        ref = TendencyRef(
            tendency_id="x",
            display_name="X",
            routing_key="x",
            antidote_model_ids=(),
            description="some prose",
        )
        results = match_activation(
            ref,
            [("base-rates", "probabilistic-thinking", "ally")],
            db_path=self.db_path,
            api_key="stub",
            embedder=self._stub_embedder_zero,  # returns None
        )
        self.assertEqual(results, ())

    def test_missing_db_returns_empty_result(self) -> None:
        ref = TendencyRef(
            tendency_id="x",
            display_name="X",
            routing_key="x",
            antidote_model_ids=(),
            description="some prose",
        )
        results = match_activation(
            ref,
            [("a", "b", "ally")],
            db_path=Path(self._tmp.name) / "does-not-exist.db",
            api_key="stub",
            embedder=self._stub_embedder_x_axis,
        )
        self.assertEqual(results, ())


class ResultShapeTests(unittest.TestCase):
    """Result dataclass is frozen and preserves the edge identity triple so
    callers can rank without re-resolving edges."""

    def test_result_is_frozen(self) -> None:
        r = ActivationMatchResult(
            source_model_id="s",
            target_model_id="t",
            edge_type="ally",
            similarity=0.7,
        )
        with self.assertRaises(Exception):
            r.similarity = 0.1  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
