# Thematics-layer value fixtures

**What lives here:** test fixtures that exercise the deterministic **thematics layer** (graph routing, model selection, card rendering) in isolation from the LLM-driven extraction lanes upstream. Each fixture takes authored typed inputs (constructed `RelationGraph` / `RelationNeighbor` / `FingerprintPayload` / `TriggeredTendency` / `FrameRoute` / `DimensionRoute`) and asserts the thematics system produces the expected edge.

**What does NOT live here:** fixtures that run the full skill pipeline against raw conversation text. Those conflate extraction-lane quality (nondeterministic LLM output) with thematics-layer behavior, so a thematics regression can hide behind an extraction improvement and vice versa. Conversation-level eyeballing uses `tests/conv_*.txt` and `scripts/run_pipeline.py` — not this directory.

## Authoring doctrine

Each fixture states a **single value claim** and demonstrates it. The claim answers: "why did we build this piece of the thematics system, and how do we know it's giving us an edge?"

Anti-pattern: "assert the routing returns the same thing it returned last Tuesday." That measures stasis, not value.

Pattern: construct a graph / input where a *specific* feature is load-bearing, and assert the output changes in the expected direction. Include a before/after contrast in the test where it sharpens the claim.

## Test-first fixtures

When a value claim refers to a phase not yet implemented (e.g., Phase 1 card rendering at the time this doc was written), author the fixture anyway and mark it `pytest.mark.skip` or `xfail` with a `reason=` that names the phase. The fixture then documents the value claim and flips to `passing` when the implementation lands. This is faster than retrofitting fixtures after-the-fact, and it keeps the value-claim doctrine honest — we don't ship a feature without a fixture that demonstrates why.

## Closed-vocabulary constraint

Per the "closed vocabulary" principle, model IDs in fixtures MUST be one of the 222 real canonical model IDs, unless the fixture is constructing an obviously synthetic graph (`"hub-model"`, `"seed"`, etc. — as in `test_fan_correction_dampens_hub_model` on the system_b side). Mixing real and synthetic IDs in the same fixture is a smell.
