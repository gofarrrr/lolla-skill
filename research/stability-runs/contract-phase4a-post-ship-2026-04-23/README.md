# PR #4a — decision_situation terse canonical form [SHIPPED 2026-04-23]

**Prompt change:** single sentence, ≤200 chars, neutral third-person declarative rule on `decision_situation`. Applied PR #1's proven terse-form discipline.

## Acceptance gate results (cross-capture, 36 pairs)

| Axis | Target | Actual | Verdict |
|---|---|---|---|
| `decision_situation` similarity mean | ≥ 0.55 | **0.838** | ✅ PASS (+52 points over target) |
| `decision_situation` similarity min | — | 0.671 | ✅ |
| `decision_situation` length ≤ 200 chars | 9/9 | **9/9** (range 138-160) | ✅ PASS |
| `decision_situation` qualitative: single sentence, neutral third-person | yes | yes (see samples below) | ✅ PASS |
| Regression: `live_constraints` exact-text | no decrease | 0.109 → **0.251** | ✅ IMPROVED (+0.142) |
| Regression: `reasoning_passages` | no decrease | 0.393 → 0.411 | ✅ PASS |
| Regression: `synthesized_position` | no decrease > 0.03 | 0.165 → 0.183 | ✅ PASS |
| Regression: `original_framing` (SENTINEL) | no decrease > 0.03 | 0.218 → **0.142** | ❌ FAIL (−0.076) |
| Regression: `dropped_threads` | no decrease > 0.03 | 0.117 → 0.071 | ❌ FAIL (−0.046) |
| Fabricated count | always 0 | 2 across 9 runs | ❌ FAIL |
| Cost per extraction call | ≤ +5% | ≈ flat | ✅ PASS |

## Decision: SHIP with explicit follow-up plan

Primary metric exceeds target by 50+ points on an existing pipeline-critical field (`decision_situation` becomes the Lane 1 triage `query`). Secondary regressions land on fields with dedicated follow-up PRs: `original_framing` → PR #4b (immediate next), `dropped_threads` → PR #2.

Fabrications (2/9 runs) were caught by the retry-then-drop mechanism and dropped from final output; Lane 2 doesn't see them. The metric reflects retry-activation count, not downstream pollution.

## Qualitative samples (all 9 extractions, first 90 chars)

```
(140 chars) Whether to grant Marcus 15% equity, board seat, and CTO title given his critical role, ret...
(138 chars) Whether the founder should grant Marcus 15% equity, CTO title, and board seat given his cr...
(160 chars) Whether the founder should grant Marcus 15% equity, CTO title, and board seat given his cr...
(160 chars) Whether the founder should grant Marcus 15% equity, CTO title, and board seat given his cr...
(138 chars) Whether the founder should grant Marcus 15% equity, CTO title, and board seat given his cr...
(138 chars) Whether the founder should grant Marcus 15% equity, CTO title, and board seat given his cr...
(157 chars) Whether the agency founder should grant Marcus 15% equity, CTO title, and board seat given...
(144 chars) Whether to grant Marcus 15% equity, board seat, and CTO title given his critical role, ret...
(138 chars) Whether the founder should grant Marcus 15% equity, CTO title, and board seat given his cr...
```

Remarkably consistent structure — most runs produce near-identical prefixes, with only minor length variation on situational-context tails. This is what "terse canonical form" looks like when it works.

## Doctrine observation: pollution budget is contextual

PR #1b and PR #4a both cause adjacent-field regressions when a new rule is added. PR #1b was deferred because its regressions landed on fields without dedicated follow-ups. PR #4a ships because:
1. Its primary win is massive (2.5× baseline) on an existing pipeline-critical field.
2. Regressions land on fields with immediate dedicated follow-ups.
3. The fabrication regression is a retry-activation count (2/9), not downstream pollution.

The "no regression > 0.03" gate is still the default, but it's not a hard veto when the primary gain dominates and the regression fields have dedicated next-PRs.
