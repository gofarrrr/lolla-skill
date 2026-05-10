# V60 C4.5 System-Bound Enrichment Readout

Date: 2026-05-10

Status: dormant integration replay evidence only. This does not attach v60 to
live `/lolla`.

## Question

Can v60 operate as part of the larger Lolla pipeline, rather than as a separate
feature, by enriching existing lane and embedding nominations and then handing a
small, safe composer input back to the system?

The target architecture is:

1. Real Lolla run artifact.
2. Existing lane nominations and provenance.
3. Embedding-assisted v60 exact chunk recall.
4. Private exact-chunk consideration trace.
5. Composer-safe opportunity summary.
6. Deterministic validation of leaks, caps, and unsupported public claims.
7. No live runtime effect.

## Implementation

New harness:

`scripts/run_v60_system_bound_enrichment_replay.py`

The harness uses:

- real replay case manifest:
  `research/v60-transaction-replay-case-manifest-2026-05-09.json`;
- explicit v60 artifact:
  `data/compiled/model_affordances/affordances_v60.json`;
- embedding retrieval summary:
  `data/evaluations/v60_transaction_embedding_lab/2026-05-10-v60-embedding-pickup-absence-view/summary.json`;
- validated C4.4c private traces:
  `data/evaluations/v60_transaction_replay_lab/2026-05-10-c44c-exact-chunk-private-replay-hardened-paid/`.

It builds a system profile per case that includes lane nomination profile,
embedding profile, packet source mix, private trace summary, and distilled
composer opportunities. The composer never receives raw v60 chunk text as a
public-writing instruction.

## Dry Run

Path:

`data/evaluations/v60_transaction_replay_lab/2026-05-10-c45-system-bound-enrichment-dry-run/`

- Items: 8
- Private traces revalidated: 8/8
- Composer prompts: about 5k-6k estimated tokens each
- Total estimated composer prompt tokens: 45,668

Compared with C4.4c private consideration, this is a lower-friction second
stage. The expensive part is private chunk consideration; the composer boundary
gets a compact opportunity summary.

## Paid Run

Raw paid path:

`data/evaluations/v60_transaction_replay_lab/2026-05-10-c45-system-bound-enrichment-paid/summary.json`

Safety-revalidated path:

`data/evaluations/v60_transaction_replay_lab/2026-05-10-c45-system-bound-enrichment-paid/summary_revalidated_numeric_guard.json`

Paid run:

- Generator: `x-ai/grok-4.1-fast`
- Items: 8
- Paid calls: 8
- Cost: `$0.009722`
- Input tokens: 45,419
- Output tokens: 2,016
- Total tokens: 47,435

Schema validation after accepting `public_delta_candidate` as an admission
decision synonym: 8/8 valid.

Safety validation after adding a numeric novelty guard: 7/8 valid.

The one invalid was `real_estate`. The composer admitted a directionally useful
margin-of-safety delta but invented fresh quantitative ranges (`10`, `12`, and
`24`) not present in the prompt. The deterministic numeric novelty guard caught
it.

This is a good failure. It proves why the system needs deterministic
post-composition checks even after private enrichment improves the reasoning
surface.

## Outcomes

Across the 8 cases, the private trace produced 22 composer opportunities. The
composer admitted 5 public deltas before numeric safety filtering. After the
safety guard, 4 safe public deltas remained.

Valid admitted public deltas came from:

- embedding absence: 2
- embedding affordance: 1
- hybrid/RRF: 1
- lane preserved: 0 after numeric safety filtering

This is important. In this run, the valid public additions came from recall
outside the plain lane-preserved backbone. The lanes still provided the
provenance spine and many private guardrails, but embeddings and absence chunks
created the visible incremental value.

Three cases correctly admitted no public delta:

- `whistleblower`: private evidence and power-risk guardrails mattered, but
  public additions risked legal-advice/friction/redundancy.
- `friendship_money`: opportunities were useful privately, but the existing
  answer was already emotionally calibrated; public additions risked judging the
  friend or repeating the point.
- `user_has_plan`: v60 reinforced optimism/base-rate/opportunity-cost guards,
  but no low-friction visible improvement was worth adding.

That is exactly the desired behavior. Useful does not mean public.

## Case Read

### Multi Offer

Admitted one diagnostic delta:

> Before committing to B, pressure-test the downside: Is the worst-case
> survivable, and what are the exit thresholds?

Source: embedding absence exact. This is a strong example of absence/guardrail
pickup turning into an executable decision test.

### Startup Pivot

Admitted one option-space delta:

> Consider a hybrid: run the pre-buy test and pivot conversations while
> minimally maintaining the current product.

Source: embedding affordance exact. This is the clearest example of v60 adding
a missing option without replacing the answer.

### Messy Three Problems

Admitted one option-space delta:

> Treat the short-term rental as a reversible step that buys time to test
> boyfriend commitment and mom-care plans.

Source: hybrid/RRF exact. This shows the system can add useful optionality even
in a messy multi-thread case without dumping every model.

### PhD Research

Admitted one concrete next move:

> Emphasize the 18-month checkpoint with explicit learning objective, success
> threshold, and reset rule.

Source: embedding absence exact. This is a good example of absence as a plan
hardener.

### Real Estate

The composer tried to admit a margin-of-safety delta but invented new numbers.
The numeric novelty guard rejected it. Directionally, the opportunity was good;
composition was unsafe.

Lesson: C4.5 needs deterministic claim-safety checks before any answer delta
can be considered product-safe.

## What This Proves

v60 can be baked into the system as a private enrichment layer:

- lanes preserve provenance and existing system structure;
- embeddings recover flexible contextual opportunities;
- v60 exact chunks add affordance and absence specificity;
- private consideration filters usefulness, rejections, and guardrails;
- composer boundary can admit small deltas or correctly admit none;
- deterministic validation catches leaks and unsupported quantitative claims.

This is more promising than treating v60 as a separate feature. The useful unit
is not "show the user a mental model." The useful unit is "improve the internal
reasoning conditions before answer composition."

## What This Does Not Prove

This does not prove live `/lolla` readiness.

This does not prove the 4/2/1/1 pickup policy is optimal.

This does not prove all public deltas are safe; the real-estate numeric failure
shows that composer output needs deterministic claim checks.

This does not yet measure latency in the full live pipeline. The composer stage
is cheap, but private exact-chunk consideration is still the expensive piece.

## Product Read

The most valuable shape is not "make every answer longer." It is:

- admit a small visible delta when it is clearly high-value and low-friction;
- otherwise preserve private guardrails;
- reject redundant opportunities;
- block unsupported or overfit additions;
- keep the user experience clean.

That is how v60 can make the system smarter without making the product feel
heavier.

## Architecture Recommendation

Keep moving toward baked-in integration, but in dormant/shadow mode:

1. Add v60 exact chunk retrieval as an internal enrichment layer after lane
   nomination.
2. Keep lane provenance as the backbone.
3. Use embeddings as low-trust recall, with reserved absence retrieval.
4. Produce private chunk-level consideration traces.
5. Feed only distilled opportunities to the composer.
6. Enforce deterministic validation:
   - private-language leak guard;
   - admitted-delta cap;
   - no unsupported numeric claims;
   - no raw v60/chunk/card IDs in public fields;
   - no automatic promotion from useful-private to public-visible.
7. Stay out of live `/lolla` until shadow runs show stable value, latency, and
   safety.

## Next Checks

The next work should verify integration choices, not just answer deltas:

- Run a source ablation: lane-only composer opportunities vs lane+embedding
  opportunities, using the same cases.
- Test a cheaper private-consideration profile, because C4.4 is the cost-heavy
  stage.
- Add a stronger claim-safety validator beyond numeric novelty, especially for
  legal/financial/medical-style assertions.
- Evaluate whether the 4/2/1/1 policy should reserve two absence slots in
  high-stakes or sparse-evidence cases.
- Run shadow-style replay over more real Lolla artifacts before any merge into
  runtime behavior.

Merge recommendation: mergeable as dormant lab/testing infrastructure after
review. Not mergeable as live product behavior yet.
