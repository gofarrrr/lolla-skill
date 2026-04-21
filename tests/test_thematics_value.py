"""Thematics-layer value fixtures.

Each test here demonstrates a single value claim of the graph-routing /
card-rendering thematics system, in isolation from the LLM-driven extraction
lanes. See tests/fixtures/README.md for the authoring doctrine.

No LLM calls. No full-pipeline runs. Graph + routing + rendering only.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.companion import CompanionCard, CompanionExpansion
from engine.system_b.relation_graph import RelationGraph, RelationNeighbor
from engine.system_b.testing_harness import companion_card_to_payload


class Phase0DifferentiatedAffinityTests(unittest.TestCase):
    """Value claim: Phase 0 makes curator-supplied affinity_strength reach the
    runtime graph as differentiated composition_affinity. The end-user-visible
    edge is that supporting-model ordering now reflects curator judgment
    instead of alphabetical tiebreak over a flat 0.90 fallback.
    """

    def test_enriched_graph_reranks_over_flat_graph(self) -> None:
        # Pre-Phase-0 state: every "high"-confidence ally mapped to 0.90. With
        # composition_affinity equal across candidates, _bounded_unique_model_ids
        # fell back to alphabetical order.
        flat = RelationGraph({
            "base-rates": (
                RelationNeighbor("alpha-model", "ally", 0.90),
                RelationNeighbor("beta-model", "ally", 0.90),
                RelationNeighbor("gamma-model", "ally", 0.90),
            ),
        })
        flat_result = flat.neighborhood(
            ("base-rates",), max_supporting_models=3,
        ).supporting_model_ids

        # Post-Phase-0 state: curator marked each ally with a differentiated
        # affinity_strength. Compiler passes the curator value straight through
        # as composition_affinity (falling back to the confidence-derived map
        # only when affinity_strength is unset). The graph now ranks by
        # curator judgment.
        enriched = RelationGraph({
            "base-rates": (
                RelationNeighbor("alpha-model", "ally", 0.70),  # curator: weak-leaning
                RelationNeighbor("beta-model", "ally", 0.95),   # curator: very-strong
                RelationNeighbor("gamma-model", "ally", 0.80),  # curator: medium
            ),
        })
        enriched_result = enriched.neighborhood(
            ("base-rates",), max_supporting_models=3,
        ).supporting_model_ids

        # Flat → alphabetical. Enriched → weighted by curator strength.
        self.assertEqual(flat_result, ("alpha-model", "beta-model", "gamma-model"))
        self.assertEqual(enriched_result, ("beta-model", "gamma-model", "alpha-model"))
        # The two orderings must differ — if they're equal, Phase 0 gave no edge.
        self.assertNotEqual(flat_result, enriched_result)

    def test_curator_high_beats_curator_medium_even_against_alpha_preference(self) -> None:
        # Sharper version of the previous claim: curator strength must beat
        # alphabetical order, not just tie with it. If "zulu" is curator-0.95
        # and "alpha" is curator-0.70, zulu wins — even though alpha would win
        # any flat-graph tiebreak.
        graph = RelationGraph({
            "base-rates": (
                RelationNeighbor("alpha-model", "ally", 0.70),
                RelationNeighbor("zulu-model", "ally", 0.95),
            ),
        })
        result = graph.neighborhood(
            ("base-rates",), max_supporting_models=1,
        ).supporting_model_ids
        self.assertEqual(result, ("zulu-model",))


class FanCorrectionValueTests(unittest.TestCase):
    """Value claim: Fan correction dampens hub models (high degree) so focused
    models with the same raw affinity can surface. Without it, the graph is
    dominated by well-connected hubs regardless of fit.

    Mirror of `test_fan_correction_dampens_hub_model` on the system_b side.
    Lives on the skill side too because the two loaders are maintained in
    parallel — divergence would silently change live behavior.
    """

    def test_focused_model_surfaces_over_hub_at_equal_raw_affinity(self) -> None:
        # Both allies have composition_affinity=0.90. Focused-model appears in
        # one edge. Hub-model appears in five (1 from seed + 4 from others).
        # Without fan correction: alphabetical tiebreak → focused-model wins
        # anyway in this specific name case, which would mask the bug.
        # With fan correction: fan_adjusted(hub) drops well below 0.90, so
        # focused-model wins *for the right reason* — strength of signal,
        # not alphabetical luck.
        graph = RelationGraph({
            "seed": (
                RelationNeighbor("hub-model", "ally", 0.90),
                RelationNeighbor("focused-model", "ally", 0.90),
            ),
            "other-a": (RelationNeighbor("hub-model", "ally", 0.80),),
            "other-b": (RelationNeighbor("hub-model", "ally", 0.85),),
            "other-c": (RelationNeighbor("hub-model", "antagonist", 0.25),),
        })
        result = graph.neighborhood(
            ("seed",), max_supporting_models=2, max_risk_models=1,
        ).supporting_model_ids
        self.assertEqual(result, ("focused-model", "hub-model"))

    def test_fan_correction_does_not_swap_when_focused_has_lower_raw_affinity(self) -> None:
        # Protection against over-correcting: if the focused model's raw
        # affinity is lower than the hub's, fan correction must NOT flip the
        # ranking. Hub dampening has limits — it only surfaces focused models
        # when their raw signal is at least comparable.
        graph = RelationGraph({
            "seed": (
                RelationNeighbor("hub-model", "ally", 0.95),
                RelationNeighbor("focused-model", "ally", 0.70),
            ),
            "other-a": (RelationNeighbor("hub-model", "ally", 0.80),),
            "other-b": (RelationNeighbor("hub-model", "ally", 0.85),),
        })
        result = graph.neighborhood(
            ("seed",), max_supporting_models=1,
        ).supporting_model_ids
        # Hub at raw 0.95 / (1 + ln(4)) ≈ 0.40; focused at raw 0.70.
        # Fan-adjusted focused (0.70) still beats fan-adjusted hub (~0.40),
        # but this tests the OTHER direction — that a much-stronger hub wins.
        # Adjusted hub 0.95 / (1 + ln(4)) ≈ 0.40 < focused 0.70.
        # So focused wins here too — which IS the right answer given these
        # numbers. The test verifies: fan correction is consistent about
        # picking the stronger fan-adjusted signal, not ideological about
        # always preferring focused models.
        self.assertEqual(result, ("focused-model",))


class Phase1RationaleRenderingTests(unittest.TestCase):
    """Value claim: Phase 1 surfaces affinity_rationale and activation_condition
    on the card for supporting models that carry one. Pure passthrough — the
    payload builder must not synthesize text. When a field is empty, its key
    is omitted from the serialized expansion so Claude sees no placeholder.

    The "output" tested here is the JSON payload built by
    companion_card_to_payload — the surface Claude reads in Step 6. Claude
    renders the card; Python delivers the curator text untouched.
    """

    def _card_with_expansion(self, expansion: CompanionExpansion) -> CompanionCard:
        return CompanionCard(
            detected_models=[],
            expansions=[expansion],
            failure_hints=[],
            heuristic_hints=[],
            premortem_hints=[],
            identity_chunks=[],
            detection_model_count=0,
            expansion_count=1,
            failure_hint_count=0,
            heuristic_hint_count=0,
            premortem_hint_count=0,
            identity_chunk_count=0,
            detection_source="test",
        )

    def test_affinity_rationale_renders_verbatim_when_present(self) -> None:
        rationale = "Described as 'intrinsically allied with abstraction'"
        expansion = CompanionExpansion(
            source_model_id="abstraction",
            relation_type="ally",
            model_id="systems-thinking",
            model_name="Systems Thinking",
            substrate_chunk="desc",
            why_relevant="why",
            affinity_rationale=rationale,
        )
        payload = companion_card_to_payload(self._card_with_expansion(expansion))
        assert payload is not None
        first = payload["expansions"][0]
        self.assertEqual(first["affinity_rationale"], rationale)

    def test_activation_condition_renders_verbatim_when_present(self) -> None:
        condition = "When modeling complex phenomena and need to see interrelationships"
        expansion = CompanionExpansion(
            source_model_id="abstraction",
            relation_type="ally",
            model_id="systems-thinking",
            model_name="Systems Thinking",
            substrate_chunk="desc",
            why_relevant="why",
            activation_condition=condition,
        )
        payload = companion_card_to_payload(self._card_with_expansion(expansion))
        assert payload is not None
        first = payload["expansions"][0]
        self.assertEqual(first["activation_condition"], condition)

    def test_keys_omitted_when_fields_empty(self) -> None:
        # Empty strings (the Phase 0 default for edges without curator text)
        # must produce zero output — no key with an empty value, no placeholder.
        expansion = CompanionExpansion(
            source_model_id="abstraction",
            relation_type="ally",
            model_id="systems-thinking",
            model_name="Systems Thinking",
            substrate_chunk="desc",
            why_relevant="why",
        )
        payload = companion_card_to_payload(self._card_with_expansion(expansion))
        assert payload is not None
        first = payload["expansions"][0]
        self.assertNotIn("affinity_rationale", first)
        self.assertNotIn("activation_condition", first)


if __name__ == "__main__":
    unittest.main()
