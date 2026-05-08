# PR79 Complexity Guard Hardening v41 Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr79-complexity-guards-v41`

## Verdict

PASS as dormant reviewed substrate hardening.

Do not treat this PR as runtime pickup, prompt injection, lane wiring, packet
shape change, or product behavior. PR79 stays inside the reviewed affordance
substrate and compiled artifact path only.

## What Changed

PR79 hardens complexity-family guardrails without adding new positive
affordances. The goal is to preserve the corpus' useful complexity language
while preventing vague "complex systems" rhetoric from becoming an
accountability escape in a future receiver packet.

Changed records:

- `butterfly-effect`: hardened `cascade-mysticism` with exact source evidence
  requiring a plausible transmission path before butterfly-effect language is
  promoted.
- `chaos-theory`: hardened `chaos-as-accountability-escape` with exact source
  evidence that chaos language must still preserve prioritization, bounded
  bets, accountability, adaptation, and monitoring.
- `emergence`: added `let-it-emerge-without-minimal-structure` as an absence
  record blocking emergence/no-design use when the case lacks minimal
  structure, constraints, and feedback.
- `self-organization-and-emergent-order`: hardened
  `emergent-order-as-no-design-needed` with exact source evidence about goals,
  feedback, guardrails, and drift.

Compiled artifact:

- Artifact: `model_affordances_v41`
- Status: `draft_review_only`
- Records: `222`
- Affordances: `276`
- Absence records: `515`
- Schema failures: `0`
- Source hash failures: `0`
- Source quote rejections: `0`

## Why This Is Not a Split PR

The full-source pass did not support adding new positive runtime identities in
this ring without creating bloat. The complexity family already has distinct
positive affordances for:

- cascade-path tracing;
- resilience-over-precision bet sizing;
- interaction-produced behavior mapping;
- condition and feedback design;
- local-interaction condition shaping;
- feedback-loop, delay, systems, and nonlinear-dynamics reasoning elsewhere in
  the corpus.

The main risk was not missing vocabulary. The main risk was over-authorizing
complexity language after pickup. PR79 therefore strengthens absence rails
rather than inflating the positive surface.

## Read-Through Judgment

Compression remains acceptable for this ring. Butterfly effect, chaos theory,
emergence, and self-organization already expose transaction-relevant positive
moves. Splitting them further right now would mostly restate nearby models,
especially `systems-thinking`, `feedback-loops`, `non-linear-dynamics`,
`delays`, and `complex-adaptive-systems`.

The needed runtime distinction is instead negative:

- Do not turn cascade reasoning into mysticism.
- Do not turn chaos into helplessness or accountability avoidance.
- Do not turn emergence into "just let it happen."
- Do not turn self-organization into no-governance ideology.

These are high-value rails for a future receiver because they tell the LLM what
not to promote when a nominated card sounds attractive but the case evidence is
thin.

## Deliberate Non-Changes

No changes were made to:

- live `/lolla` runtime paths;
- prompts;
- lane adapters;
- packet producer defaults;
- packet renderer;
- Observatory or final-answer surfaces.

No automatic "latest artifact" behavior was introduced. v41 remains a dormant
compiled substrate artifact.

## PASS / No-Change Notes

The following nearby records were reviewed as context but not changed in this
ring:

- `non-linear-dynamics`: already requires concrete nonlinear interaction and
  warns against generic complexity theater.
- `systems-thinking`: already contains explicit structure, feedback, boundary,
  and over-broadness controls.
- `feedback-loops`: already has loop-specific evidence requirements and misuse
  guards.
- `delays`: already separates lag-aware reasoning from vague timing excuses.
- `complex-adaptive-systems`: already owns adaptive-agent and condition-design
  territory more directly than the narrower guard records changed here.

## Verification

Focused verification should run:

```bash
pytest tests/test_pr79_v41_complexity_guard_hardening.py tests/test_pr78_v40_systems_leverage_splits.py tests/test_model_affordance_compiler.py
rg -n "affordances_v41|model_affordances_v41" engine scripts tests -g '*.py'
git diff --check
jq '.compile_metadata.validation' data/compiled/model_affordances/affordances_v41.json
```

Expected result:

- PR79 target records validate against schemas and source quotes.
- v41 preserves all v40 model IDs.
- v41 preserves all v40 affordance IDs.
- v41 adds exactly one absence field:
  `let-it-emerge-without-minimal-structure`.
- v41 is not imported by live runtime paths.

## Next Ring

The next useful ring should continue full-corpus enrichment cautiously by
family. Good candidates are communication, persuasion, narrative, and cultural
reasoning records, because those are likely to contain multiple
transaction-distinct uses and equally important misuse guards.

The operating rule should remain strict:

Add or split only when the source supports a downstream use/reject/defer
decision that would change a future receiver transaction. Otherwise harden
treatment requirements or absence rails.
