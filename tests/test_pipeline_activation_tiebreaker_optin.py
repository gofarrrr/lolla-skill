"""Pipeline-level opt-in tests for the Phase 3 Commit B activation tiebreaker.

Covers the `PipelineConfig.activation_tiebreaker_enabled` flag:

  - OFF (default): `route_deep_check_results` path is used; `RelationGraph.neighborhood()`
    receives no `reasoning_context` / `embeddings_db_path` / `openai_api_key`.
  - ON: per-tendency `TendencyRef` is threaded as `reasoning_context`; `embeddings_db_path`
    and `openai_api_key` (when present in env) are forwarded.

The downstream gate behavior itself is covered by
`test_relation_graph_activation_tiebreaker.py`. These tests isolate the
pipeline wire-up.
"""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.deep_checks import DeepCheckResult
from engine.system_b.pipeline import PipelineConfig, SystemBPipeline
from engine.system_b.relation_graph import RelationGraph, RouteNeighborhood
from engine.system_b.tendency_catalog import ModelBinding, TendencyCatalog, TendencyRef


class _SpyRelationGraph(RelationGraph):
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
        description="Overthinking blocks a decision that evidence already supports.",
        antidote_model_ids=("first-principles-thinking",),
        antidote_bindings=(binding,),
    )
    return TendencyCatalog(
        tendencies={"analysis-paralysis": tendency},
        alias_index={"analysis-paralysis": "analysis-paralysis"},
    )


def _deep_result() -> DeepCheckResult:
    return DeepCheckResult(
        tendency_id="analysis-paralysis",
        tendency_name="Analysis Paralysis",
        tendency_number=0,
        detected=True,
        confidence=0.95,
        evidence=(),
        sub_pattern="",
        specific_passage="",
        severity="high",
        reason="unit test",
    )


def _pipeline(config: PipelineConfig, spy: _SpyRelationGraph, *, db_path: Path | None) -> SystemBPipeline:
    # Bypass load() — construct with only what the helper path touches.
    pipe = SystemBPipeline.__new__(SystemBPipeline)
    pipe._catalog = _catalog()
    pipe._relation_graph = spy
    pipe._config = config
    pipe._embeddings_db_path = db_path
    pipe._embedding_api_key = os.environ.get("OPENAI_API_KEY", "")
    return pipe


class PipelineActivationOptInTests(unittest.TestCase):
    def test_flag_off_omits_activation_kwargs(self) -> None:
        spy = _SpyRelationGraph()
        pipe = _pipeline(
            PipelineConfig(activation_tiebreaker_enabled=False),
            spy,
            db_path=Path("/tmp/fake.db"),
        )

        pipe._route_deep_check_results_with_optional_tiebreaker(
            [_deep_result()], relevance_scores=None,
        )

        self.assertEqual(len(spy.calls), 1)
        call = spy.calls[0]
        # Default `route_deep_check_results` path leaves these at the underlying
        # default (None) because the pipeline-level helper did not pass them.
        self.assertNotIn("reasoning_context", [k for k, v in call.items() if v is not None and k == "reasoning_context"])
        # Be explicit:
        self.assertTrue(
            call.get("reasoning_context") is None,
            f"flag OFF must not forward reasoning_context; got {call.get('reasoning_context')!r}",
        )
        self.assertTrue(call.get("embeddings_db_path") is None)
        self.assertTrue(call.get("openai_api_key") is None)

    def test_flag_on_forwards_per_tendency_ref(self) -> None:
        spy = _SpyRelationGraph()
        db = Path("/tmp/fake.db")
        config = PipelineConfig(activation_tiebreaker_enabled=True)
        pipe = _pipeline(config, spy, db_path=db)
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=False):
            pipe._embedding_api_key = "sk-test"
            pipe._route_deep_check_results_with_optional_tiebreaker(
                [_deep_result()], relevance_scores=None,
            )

        self.assertEqual(len(spy.calls), 1)
        call = spy.calls[0]
        ctx = call.get("reasoning_context")
        self.assertIsInstance(ctx, TendencyRef)
        self.assertEqual(ctx.tendency_id, "analysis-paralysis")
        self.assertEqual(call.get("embeddings_db_path"), db)
        self.assertEqual(call.get("openai_api_key"), "sk-test")

    def test_flag_on_skips_undetected(self) -> None:
        spy = _SpyRelationGraph()
        pipe = _pipeline(
            PipelineConfig(activation_tiebreaker_enabled=True), spy, db_path=None,
        )
        undetected = DeepCheckResult(
            tendency_id="analysis-paralysis",
            tendency_name="Analysis Paralysis",
            tendency_number=0,
            detected=False,
            confidence=0.0,
            evidence=(),
            sub_pattern="",
            specific_passage="",
            severity="",
            reason="",
        )
        routes = pipe._route_deep_check_results_with_optional_tiebreaker(
            [undetected], relevance_scores=None,
        )
        self.assertEqual(routes, ())
        self.assertEqual(spy.calls, [])


if __name__ == "__main__":
    unittest.main()
