# PR #3 — Minimal Attempt (terse + final-turn-anchor on synthesized_position)

**Date:** 2026-04-23
**Outcome:** REVERTED. Target field REGRESSED on both character-level and semantic metrics.

## What was tried

Replaced the `synthesized_position` prompt from "The AI's final or most developed recommendation/analysis..." (~330 chars, ambiguous on "most developed") to "the stance expressed in the FINAL assistant turn (mechanical anchor), single declarative statement, ≤300 chars, neutral third-person" (~250 chars, mechanical anchor).

Chose minimal-change approach (kept synthesized_position as string, no Position object) based on the PR #1b + PR #2 saturation learnings — full Position object would be even more prompt content than what failed in those PRs.

## Cross-capture result (vs PR #4b baseline)

| Field | PR #4b | PR #3 minimal | Δ |
|---|---|---|---|
| **`synthesized_position` (TARGET) — SequenceMatcher** | 0.216 | **0.147** | **−0.069** |
| **`synthesized_position` (TARGET) — embedding cosine** | 0.835 | **0.735** | **−0.100** |
| `decision_situation` | 0.869 | 0.902 | +0.033 |
| `original_framing` | 0.340 | 0.506 | +0.166 |
| `reasoning_passages` | 0.657 | 0.527 | −0.130 |
| `live_constraints` exact-text | 0.345 | 0.296 | −0.049 |
| `dropped_threads` | 0.222 | 0.252 | +0.030 |
| Fabricated count | 0 | 0 | ✓ |

**Both metrics agree: target field genuinely regressed.** Not a measurement artifact.

## Why it failed

The mechanical-anchor rule made the LLM pick different sentences from the final turn each run, producing more paraphrase drift than the "most developed" prose instruction. The previous free-form synthesis had lots of shared prose across runs (even if conceptually drifting); the new terse rule produced short, differently-worded restatements.

This is the OPPOSITE of the effect on decision_situation (PR #4a) and original_framing (PR #4b), where terse-rule forced STRUCTURED identical prefixes. Those fields benefited from length reduction because their prior baselines were very verbose (~400+ chars). synthesized_position's baseline was already moderately terse (~700-900 chars of substantive content); further tightening just amplified variance.

## Doctrine refinement: terse-rule is not universally applicable

After PR #4a + #4b, we had hoped terse-form discipline was a compound pattern that worked on all free-text fields. PR #3 minimal disproves that. Terse-form works when:
1. Baseline prompt produces verbose output (>300 chars of content-heavy prose)
2. The canonical form can be captured in a single sentence
3. The concept being captured is structural (decision, framing) not recommendation-heavy

synthesized_position fails criterion 3 — it captures a recommendation or position which is inherently multi-clause and content-heavy. Can't be compressed to a sentence without losing information.

## Pattern summary across PR #1b, PR #2, PR #3

Three PRs attempted to improve specific fields via prompt additions/changes. All three failed their acceptance gates:
- **PR #1b** (canonical_key): primary metric passed but adjacent fields polluted; deferred.
- **PR #2** (dropped_threads): either target gained at cost to others (tie-break) or target regressed (slim); deferred.
- **PR #3 minimal** (synthesized_position): target regressed on both char-level and semantic metrics; reverted.

The common thread: **the monolithic extraction prompt has saturated**. Adding rules or changing rules in-place either pollutes other fields or makes the target field worse (because paraphrase drift exceeds baseline shared-substring density).

The 3 PRs that DID ship (#1, #4a, #4b) all applied the same narrow mechanism: **terse-form rule on existing free-text with verbose baseline**. That mechanism is exhausted after #4b — remaining free-text fields either don't have verbose baselines (synthesized_position) or depend on schema changes (Position, move_type) that bring the pollution problem back.

## Next architectural step

**Track A decomposition** (separate LLM call per field) is the structural unblock. Each field gets its own dedicated prompt with only the context it needs; attention competition within a monolithic prompt is eliminated by construction. PR #1b, PR #2, PR #3 full, PR #5 all rationally resume after Track A lands.

Until Track A: extraction contract is at its plateau. Further improvements require architectural work, not prompt work.
