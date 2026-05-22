# Lolla Step 6 Reasoning-Portfolio Layer PRD

Date: 2026-05-19

Status: draft PRD / knowledge-capture document for future implementation
planning. This document does not recommend a final architecture and does not
change `SKILL.md`, runtime behavior, default `/lolla`, product docs, workers,
bundles, handoff modes, or the canonical knowledge base.

2026-05-20 clarification: treat this document as a map of what must be
understood before implementation, not as an implementation recommendation. The
next implementation should reconsider the design from first principles using
the evidence captured here.

2026-05-20 portfolio correction: later discussion, prior run inspection, and
context-engineering research change the center of gravity. The candidate should
not be framed as a narrow `solver_control_note.v1` that selects what Step 6 is
allowed to see. The safer target is a private Step 6 reasoning portfolio:
broad availability, compact representation, delayed rejection. The layer may
classify, compress, rank, preserve, and point to expansion refs, but it must
not suppress source-backed or knowledge-base-selected edge material merely
because it looks off-frame to an intermediate model.

2026-05-20 autoresearch correction: future development should use an
autoresearch-style loop adapted to Lolla. Each iteration should name a
hypothesis, change the smallest research-only surface, evaluate against a fixed
case suite and rubric, log keep/retest/discard/boundary-case, and repeat. The
objective is not maximum compactness; it is better private context for Step 6
while preserving enrichment, breadth, depth, off-frame receipts, and Step 6's
role as the actual solver.

## Summary

Explore a private pre-Step-6 reasoning-portfolio layer for the Lolla skill.

The current skill is strong at finding structural pressure, but the default
workflow can still give the final reasoner either too much flat material or too
little interpreted pressure. The problem is not only "control." It is reasoning
transport: how to carry wide, strange, source-backed, and sometimes noisy
material into Step 6 without creating an artifact dump.

The candidate shape to evaluate:

```text
capture conversation
-> extract decision structure
-> derive problem_state.v1
-> run existing Lolla audit lanes and V60 retrieval/enrichment
-> build candidate inventory from all engineered artifacts
-> run small targeted reasoning_affordance.v1 calls
-> assemble step6_attention_map.v1
-> write Step 6 revised answer
-> persist ledger, memo, archive
```

The old working name `solver_control_note.v1` should be treated as a historical
placeholder. If a solver-control object survives, it should be a view of the
attention map, not a monolithic selector that tries to decide the answer before
Step 6.

The current working hypothesis remains that post-Step-6 sub-agent pressure
checks should move out of the default path because they add cost, latency, and
a large amount of secondary information. This remains a design choice to
validate, not a settled implementation decision.

## Product Problem

Today Lolla does several things well:

- captures the conversation;
- extracts decision structure;
- audits reasoning through four lanes;
- selects private source-backed material;
- asks Claude/Codex to reconsider the answer;
- records receipts and archives the run.

The weak point is not pressure discovery. The weak point is Step 6 preparation:

```text
Given what the system found, what should Step 6 have available, in what form,
with what boundaries, and with what preserved option to expand?
```

Without a good preparation step, the final reasoner can receive too much
material without a crisp sense of what to inspect. But the opposite failure is
also dangerous: if pre-Step-6 narrows too aggressively, Lolla loses exactly the
off-frame mental-model pressure that makes it valuable.

The system should prefer this failure mode:

```text
Step 6 saw a compact edge receipt and decided not to use it.
```

over this failure mode:

```text
The pre-Step-6 layer suppressed the edge receipt because it did not fit the
smooth narrative.
```

One candidate replacement for the late pressure check is therefore not "one
small control note." It is a compact reasoning portfolio that preserves:

- an active working set for Step 6;
- an edge/latticework reserve for Munger-style off-frame pressure;
- weak or negative-space receipts;
- parked items with reactivation conditions;
- expansion refs back to the full archive.

## First Principles

Lolla is not an answer generator.

Lolla is a conversation-aware reasoning-control system:

- LLMs interpret, judge, synthesize, reject, defer, and translate.
- Embeddings improve recall and vocabulary bridging.
- Deterministic code preserves custody, routing, validation, caps, schemas,
  hygiene, ledgers, and auditability.

The deterministic system should not become a cognitive system. Its job is
selection support, custody, diversity, caps, validation, and routing. The
cognitive layer decides how to think with the material.

Polya, Bevelin, and future sources should not become new public labels or new
default lanes. They should act as private reasoning-discipline presets:

```text
Polya: what kind of problem is this, and what move is needed next?
Bevelin: what does the evidence justify, what would be overreach, and what
         would happen if this model is forced?
Future presets: additional ways to preserve useful off-frame reasoning pressure.
```

Together they support a compact portfolio that helps Step 6 think, not a
deterministic monster that tries to reason in code.

### Autoresearch As Process, Not Product

Karpathy's `autoresearch` pattern is useful here as a research operating model:

```text
change one thing -> run a fixed evaluation -> log result -> keep, discard, or
retest -> repeat
```

For Lolla, the fixed evaluation is not a five-minute training run and not a
single scalar metric. It is a fixed case suite plus a multi-criterion judgment
rubric. Every meaningful iteration should ask:

```text
Did this improve the quality of private context Step 6 receives?
Did it preserve breadth and off-frame edge pressure?
Did it avoid answer bloat and machinery leakage?
Did it let negative controls stand down?
Did it avoid doing Step 6's job?
```

The local operating program is:

```text
research/pre-step6-autoresearch-program-2026-05-20.md
```

The first autoresearch hypothesis should be Bevelin-specific but not
Bevelin-exclusive:

```text
Bevelin lens probes improve edge-pressure preservation in founder and PhD v2
without causing consultant or mother negative controls to over-promote.
```

If Bevelin helps only by adding prompt mass, public labels, or premature
conclusions, the experiment should be discarded or retested. If it preserves
source-backed off-narrative pressure as scan/parked receipts and improves Step
6 replay quality, it can advance to the next research loop. Bevelin remains a
private lens pack, not the architecture.

2026-05-20 result: the first Bevelin v0 fixed-suite loop is promising but not
runtime evidence. It improved the founder high-clutter and PhD v2 answer cores
by preserving incentive/denominator/commitment/inversion pressure. It correctly
stood down on the consultant negative-control case, where rendered hybrid was
already cleaner. It improved the mother case's absence-of-evidence language but
not enough to promote beyond retest. This supports the lens-pack interface as a
private enrichment probe:

```text
attention map -> lens probe -> lens answer core -> comparison gate
```

The result does not support making Bevelin a public label, a deterministic
lane, or a default runtime dependency. The lesson is broader: lens packs should
increase the quality and diversity of Step 6 context while keeping a strict
stand-down gate.

2026-05-20 gate clarification: the comparison gate must be cognitive, not a
dumb deterministic selector. Deterministic code validates source custody,
schemas, render hashes, public-answer hygiene, inclusion/exclusion checks, and
promotion blocks. It does not decide quality. A cognitive reviewer, human in
the local static slice or a small targeted LLM call in a future manual slice,
judges whether the lens improved Step 6 context:

```text
Did this extra context help Step 6 think better without doing Step 6's job?
```

2026-05-20 Polya result: the same lens-pack interface was tested with
`polya_problem_solving_v0`. Polya behaved differently from Bevelin, which is
the desired signal. It was strongest on PhD v2, where problem shape and
next-move sequencing are the bottleneck. It was useful but not promotional on
mother, where reversible safety action under uncertainty matters. It stood down
on founder and consultant. This supports the idea that lens packs should be
small targeted cognitive probes, not one bloated universal prompt.

2026-05-20 live gate result: comparing lens answer cores as replacements for
rendered hybrid is the wrong product abstraction. Live blinded reviewers often
preferred rendered hybrid because it preserved concrete case nuance that the
short lens answer cores shaved off. A second experiment compared rendered
hybrid as the anchor against rendered hybrid plus protected private receipts.
That is closer to the intended architecture, but it exposed the key gate
tension: without a complexity tax, reviewers over-promote "more receipts"; with
a strong complexity tax, negative controls behave better but some positive
cases stand down. The current design conclusion is:

```text
Use rendered hybrid as the concrete anchor.
Use lens packs to propose novelty-filtered protected receipts.
Gate those receipts cognitively with a smallest-sufficient-packet rule.
Do not wire this into runtime or SKILL.md yet.
```

2026-05-20 card-deck result: a later slice tested the broader shape more
directly. Instead of asking a pre-Step-6 selector to decide what survives, the
system built a private Step 6 card deck containing:

- clean hybrid as the concrete anchor;
- Bevelin as a private edge-pressure card;
- Polya as a private problem-shape card;
- problem read and source refs;
- a deterministic-limit statement that code validates custody and rendering
  but does not decide cognitive usefulness.

Step 6 then wrote an answer core and a private card-consideration ledger. The
comparison gate was corrected so the reviewer judges blinded A/B/tie answer
quality only; deterministic code privately maps the blind winner to whether
the card deck improved or regressed. This preserves cognition in the gate while
keeping deterministic code to bookkeeping, hygiene, and consistency.

After refining the Step 6 replay prompt to say "as short as possible, but no
shorter" and "do not compress away concrete tripwires, conditions,
actor-specific steps, or irreversible-risk distinctions merely to be concise,"
the replay was refined again with a private `novelty_role` ledger and stronger
anchor-preservation rules. Step 6 now distinguishes visible backbone,
additive pressure, confirming support, and private guardrail. It is also told
not to shorten by deleting named channels/resources, communication boundaries,
dated windows, gates, actor sequence, tripwires, or evidence checks.

The current four-case live suite and a Gemini cross-model check both prefer
card-deck replay for founder, PhD v2, and consultant, while clean hybrid still
wins mother. That is a promising signal for the card-deck shape and a useful
falsifier: sensitive safety cases punish even small redundancy or phrasing
drift. Runtime and `SKILL.md` remain dormant.

2026-05-20 visibility-policy result: the mother boundary case led to a better
policy shape. If Step 6's private ledger marks all non-anchor cards as
`confirming_support` or `private_guardrail`, deterministic code may record that
the clean hybrid anchor is stand-down eligible. It still may not decide answer
quality. The visible answer policy requires cognitive confirmation from the
comparison gate:

```text
Step 6 ledger -> deterministic stand-down eligibility
cognitive comparison -> visible answer policy
```

In the current four-case suite this produces card-deck visible answers for
founder, PhD v2, and consultant, and clean-hybrid visible answer for mother.

2026-05-20 design-preamble cost/cache result: the red-team preconditions are
now being handled through an autoresearch design track, not a direct integration
draft. The first slice, `design_preamble_cost_cache_v0`, added a research-only
`pre_step6_design_preamble_cost_cache.v1` contract. It proves that
`runtime_cached_only` cache misses stand down to current Step 6, add 0 LLM
calls, disallow live card generation, add 0 normal runtime reviewer calls, and
record `card_deck_cache_miss`. The compiled key carries schema/version/source,
problem, V60, safety, and Step 6 prompt-contract material. Current fixtures mark
`ConversationIR` and V60 selected chunks as research-proxy/not-attached rather
than pretending this is a full live run. This keeps the first runtime candidate
honest: cached/compiled cards may be tested later, but cache misses do not
become hidden live card-generation calls.

2026-05-20 design-preamble card-interface result:
`design_preamble_card_interface_v0` added a research-only
`private_reasoning_card.v1` schema and
`pre_step6_private_reasoning_card_interface.v1` fixtures. Existing clean-hybrid,
Bevelin, and Polya cards now validate through one generic private-card schema,
and a synthetic future card validates without adding visibility-policy or ledger
fields. This means Bevelin and Polya are implementations of the interface, not
the interface itself. This does not prove runtime usefulness; it only clears the
next design question, V60/card overlap in the unified private-consideration
ledger.

2026-05-20 design-preamble ledger-overlap result:
`design_preamble_ledger_overlap_v0` added a research-only
`private_consideration_item.v1` schema and
`pre_step6_private_consideration_ledger_overlap.v1` fixture. The founder fixture
presents `reasoning_card:bevelin_card` once in hot context while preserving both
that card and a synthetic `v60_chunk:overcommitment_without_evidence` in ledger
custody. This proves the intended rule at schema level: dedupe hot context for
attention, preserve all source items for custody. The V60 item is synthetic, so
this is not yet live V60 integration.

2026-05-20 design-preamble payload-omission result:
`design_preamble_payload_omission_v0` added a research-only
`pre_step6_payload_omission.v1` gate. It uses exactly six protected categories:
dates/windows, actor sequence, named resources/channels, communication
boundaries, tripwires/gates, and evidence checks. The gate is anchor-activated,
diff-based, and mechanistic-first; it only flags anchor-present/deck-absent rows
as `introduced_omission` and explicitly records
`visibility_decision: not_decided_by_omission_gate`. All four fixed-suite
deck-aware answers preserved the protected categories. This means the mother
stand-down remains a sensitive-safety phrasing/tightness result, not a
protected-payload omission result.

2026-05-20 design-preamble ledger negative-shape result: the ledger overlap
contract now has two residual fixtures. A non-overlap fixture keeps both
`reasoning_card:polya_card` and `v60_chunk:absence_blocker_false_precision` in
hot context with no shared `overlap_group_id`. A V60-only/no-deck fixture
validates `v60_chunk:standalone_margin_of_safety` with no private card deck.
This proves dedupe is conditional, not universal, and the unified ledger schema
does not depend on the card deck being present.

2026-05-20 design-preamble visibility-asymmetry result:
`design_preamble_visibility_asymmetry_v0` added a research-only
`pre_step6_visibility_asymmetry.v1` policy contract. The runtime asymmetry is
now explicit: broad private deck, anchor-biased public answer when unresolved,
and no normal live reviewer loop. Research and experimental modes may retest
ties or ledger/reviewer disagreements at most once, using the same rubric, a
fresh blind shuffle, and a different model family if available. Deck-visible
after retest requires a reviewer preference for the deck; non-inferior keeps
the deck alive for research only. This preserves the principle that Step 6 can
receive broad private context while runtime public output remains conservative
when the signals are unclear.

2026-05-20 design-preamble calibration-floor result:
`design_preamble_calibration_floor_v0` added a research-only
`pre_step6_calibration_floor.v1` manifest. It records the current four-case
suite as `seed_suite_not_calibration`, not as promotion evidence. The required
floor is 12-20 cases with at least 3 high-clutter cases, 3
sequencing/problem-shape cases, 3 sensitive/safety/legal cases, 3 negative
controls, and 2 V60 on/off comparison pairs. Current coverage is 1, 1, 1, 2,
and 0 respectively, so `calibration_floor_met: false` and
`promotion_read: runtime_promotion_blocked`. Mother is only a
`true_standdown_candidate` with `seed_only` weight, not proof that the runtime
anchor bias has acceptable false-standdown recall. The manifest now pins the
V60 pair definition: the same case must be run twice under the same prompt
contract and card-deck policy, once with V60 selected items available and once
with those items withheld. Curating cases where V60 was substantive versus
minimal is useful as stratification, but it is not a substitute for same-case
toggles. It also records the payload-gate limitation surfaced in review:
category markers can be preserved while concrete anchor entities inside the
category are lost, so calibration must track
`preserved_by_marker_anchor_entities_missing`. The recommended next move is a
non-promotional `false_standdown_bridge_probe_v0` with 2-3 deliberately
dangerous cases before full calibration curation.

2026-05-21 false-standdown bridge-probe result:
`false_standdown_bridge_probe_v0` was run as a non-promotional packet-level
probe. Three dangerous-corner cases were pre-registered before reviewer calls:
high clutter plus sensitive tone, sensitive anchor missing a safety tripwire,
and sequencing pressure inside a sensitive boundary. Confirmation required two
reviewer families under the same rubric and fresh blind shuffles. All three
cases were confirmed `false_standdown` by both `openai/gpt-5.1-chat` and
`google/gemini-3.1-flash-lite`, so the aggregate result is
`design_review_required`. This does not prove full runtime behavior because the
probe used packet cases, not the production card generator. It does falsify a
universal runtime fallback of "unresolved means anchor visible and deck
private." Before any integration draft, the visibility policy needs redesign:
normal runtime should test whether Step 6's own private ledger can act as the
cognitive signal. If Step 6 records additive pressure and protected payload is
preserved, deck-aware output may be visible without adding a reviewer loop.
Anchor-visible should remain the fallback for private/confirming ledgers,
missing or unclear ledgers, cache misses, and payload omissions.

2026-05-21 visibility-policy redesign result:
`design_preamble_visibility_policy_redesign_v0` added a research-only
`pre_step6_visibility_policy_redesign.v1` contract. The redesigned policy fixes
the specific bridge-probe failure without adding a runtime reviewer loop. When
cache is hit, Step 6 records additive non-anchor pressure, and protected payload
is preserved, the deck-aware Step 6 answer may be visible. When Step 6 records
non-anchor cards as private/confirming, the anchor remains visible. When the
cache misses, the system uses current Step 6 without live deck generation. When
the ledger is missing/unclear or protected payload is lost, anchor visibility is
the guardrail. This keeps the cognitive signal inside Step 6's own ledger and
keeps deterministic code limited to cache, schema, payload, and custody checks.
The remaining gap is evidence: the bridge cases were packet-level; before
integration, a replay or calibration slice must show whether full Step 6 bridge
replays actually produce the additive ledger signals this policy relies on.

2026-05-21 bridge Step 6 ledger-replay result:
`bridge_step6_ledger_replay_v0` has now tested that missing upstream
dependency. Using the three pre-registered false-standdown bridge packets and
`openai/gpt-5.1-chat`, Step 6 produced a private ledger with
`additive_pressure_present` in all three cases. The aggregate result is
`step6_additive_signal_supported`. This supports the redesigned policy's core
claim that Step 6's own ledger can supply the cognitive signal without a
runtime reviewer loop. It still does not promote runtime behavior: the replay
used bridge packets rather than full production card compilation, cache-hit
handling, V60 overlap, and protected-payload omission checks. The honest next
state is: integration design may use the ledger-mediated rule as a plausible
research contract, but runtime promotion remains blocked until calibration or a
narrow board-approved experimental path.

2026-05-21 ledger-mediated integration design draft:
`research/pre-step6-ledger-mediated-integration-design-draft-2026-05-21.md`
now pins a proposed dormant integration shape, not an approved implementation
contract. The design is: broad private deck, Step 6 answer plus private ledger,
deterministic guards, then a visibility decision. Deck-aware output may be
visible only on cache hit, additive Step 6 ledger signal, preserved protected
payload, and valid custody. Cache miss uses current Step 6 with no live deck
generation. Private/confirming ledger, missing/unclear ledger, payload omission,
or custody failure all fall back to anchor/current-Step-6 guardrails. The draft
defines modes, prompt contract, unified ledger fields, cache contract, archive
fields, Observatory view, cost envelope, promotion gates, implementation slices,
and falsifiers. It does not edit `SKILL.md` or runtime. Before it becomes an
implementation contract, the mirror false-positive direction must be tested.

2026-05-21 false-positive visibility probe result:
`false_positive_visibility_probe_v0` tested the mirror risk: Step 6 marks deck
pressure additive, the deterministic guards pass, but the anchor is actually
better. Three cases were pre-registered: Bevelin structurally applicable but
irrelevant, Polya true but useless, and marker-preserved/entity-lost payload
loss. Live Step 6 replay with `openai/gpt-5.1-chat` emitted
`all_private_or_confirming` on all three, so no reviewer calls were needed. The
first two are clean `step6_stood_down` results. The marker/entity-loss case is
`not_observed`, not a pass, because the attempted case did not reach the
failure mode where Step 6 marks additive while dropping entities. Aggregate:
`continue_probe_with_not_observed`. This lowers false-positive concern but does
not close the omission gate's marker-vs-content-loss weakness.

2026-05-21 marker/entity-loss follow-up result:
`marker_entity_loss_followup_v0` ran three focused construction attempts:
resource generalization, tripwire compression, and actor-sequence blur. Live
Step 6 replay with `openai/gpt-5.1-chat` emitted
`all_private_or_confirming` on all three, so no reviewer calls were needed. The
result is stronger than a generic null: Step 6 preserved the concrete anchor
entities and kept the generic deck pressure private/confirming. Attempt 1 kept
RAINN, therapist/counsel, phone channel, and request-to-meet language. Attempt
2 kept concrete tripwires such as sexual images, threats, other minors, hidden
channels, and pressure/fear language. Attempt 3 kept RAINN, therapist/counsel,
co-parent sequencing, and the before-reporting order. Aggregate:
`followup_result: not_observed`. This reduces the marker/entity false-positive
concern but still does not prove the omission gate can catch the failure if
Step 6 ever emits additive marker-only output. Runtime promotion remains
blocked; a next engineering slice must be ultra-dormant and shadow-only.

2026-05-21 ultra-dormant shadow implementation result:
`ultra_dormant_shadow_portfolio_integration_v0` has now landed as an
instrumentation layer, not a promoted behavior. The runtime can be explicitly
run with `--pre-step6-portfolio shadow` or `LOLLA_PRE_STEP6_PORTFOLIO=shadow`.
Default remains off. The new module computes a compiled card-deck key, checks
only for an existing cached deck, records cache misses as stand-down to current
Step 6, derives a policy signal from Step 6's private ledger when supplied, and
writes an archiveable shadow sidecar. The sidecar always records zero runtime
reviewer calls, no live card generation, no visible-output application, and
closed runtime/skill/visibility gates. Observatory now has a
`/audit/pre-step6` panel and the case API exposes
`pre_step6_shadow_portfolio`. `SKILL.md` was not changed. This means the system
can start learning from shadow evidence without letting the deterministic layer
become the cognitive layer.

2026-05-21 first shadow evidence run:
`shadow_evidence_run_v0` ran without model calls. The prior-result cache-miss
arm processed eight existing result artifacts; all eight recorded
`cache_miss`, `current_step6_visible_no_deck`, and zero visible-output
applications. The fixed-suite cache-hit arm materialized the four existing card
decks into a local cache and normalized their Step 6 replay ledgers. It produced
three `deck_visible_shadow_only` records for founder, PhD, and consultant, and
one `anchor_visible_deck_private_shadow_only` record for mother. Again, visible
applications were zero. This is the first concrete proof that the dormant path
can preserve Step 6's cognitive distinction while keeping public behavior
locked.

2026-05-21 consultant-triggered false-positive probe:
The shadow harness usefully exposed a classification conflict. Older manifest
language treated `mid-level-consultant-report-2` as a negative-control seed, but
the card-deck comparison, visibility-policy artifact, and shadow decision all
treated it as deck-positive. The manifest was corrected before the probe:
consultant is now `sensitive_safety_legal` and `positive_seed`; mother remains
the current stand-down/negative-control seed. A live consultant-triggered
false-positive probe then ran with Step 6 `openai/gpt-5.1-chat` and two reviewer
families. Consultant produced `additive_pressure_present`; both reviewers
returned `true_visible`, with no payload/entity loss. The Bevelin temptation
case stood down and the marker/entity-loss case again remained `not_observed`.
This confirms that the shadow harness is telemetry, not adjudication, but it can
surface exactly the right cases for adversarial probe follow-up.

## Design Correction: Portfolio, Not Narrow Control

The core design rule:

```text
No artifact dump. No premature pruning.
```

The pre-Step-6 layer should reduce presentation burden, not reasoning
optionality. It should ask:

```text
What could this artifact reveal?
What boundary prevents overuse?
What cheap test should Step 6 apply before using it?
What expansion ref preserves the full source if Step 6 wants more?
```

It should not ask, too early:

```text
Is this useful enough to survive?
Does this fit the emerging narrative?
Can this be discarded because another LLM did not like it?
```

The guiding slogan is:

```text
Cap prose, not possibility.
Broad availability, compact representation, delayed rejection.
```

This matters because Lolla is not the same problem as a clinical-documentation
pipeline. Clinical documentation benefits from narrow section agents because
the desired output sections are known and the cost of off-section material is
high. Lolla is a reasoning system. Its edge often comes from a model, source,
or mental frame that looks odd until the final solver uses it to break the
smooth conversation path.

Therefore context engineering should be applied as focused context for small
intermediate calls, not as a license to narrow Step 6's intellectual world too
early.

## Handoff Knowledge To Preserve

The latest pre-Step-6 experiments produced knowledge that should travel into
any future design. This section is evidence memory, not a recommendation to
implement a specific handoff system.

### Core Lesson

A handoff is not a better answer.

A handoff is a possible pressure-preservation device. It is useful only if it
helps the final reasoner keep sight of something important that would otherwise
be easy to lose.

No handoff is a valid positive outcome.

The important cognitive judgment is not deterministic:

```text
Should anything be carried forward, and if so, what is the smallest useful
thing to carry in the active working set?
```

The updated question adds a second layer:

```text
What should remain outside the active working set but still be visible enough
that Step 6 can use it if the problem calls for it?
```

The deterministic system should be treated with suspicion whenever it tries to
decide this directly. Deterministic work can narrow possibilities, preserve
source refs, apply caps, validate schemas, enforce diversity, preserve protected
edge slots, and record receipts. It should not pretend to know what Step 6
should believe or what the final answer should be.

### What The Deterministic System May Do

The deterministic system may present a silver platter:

- source-grounded pressure candidates;
- relevant constraints;
- live tensions;
- missing or uncertain information;
- possible reactivation conditions;
- evidence boundaries;
- things that were selected, suppressed, skipped, rejected, or parked;
- validator-enforced warnings about overproduction;
- protected edge slots for off-frame reasoning material;
- expansion refs back to raw artifacts and source excerpts.

The platter can say:

```text
Here are the possibilities worth considering.
Here is why each surfaced.
Here is what would go wrong if it were forced.
Here is what kind of thinking it asks for.
Here is where to inspect more if this becomes live.
```

It should not say:

```text
This is the answer.
This is the correct pressure.
This is the only handoff Step 6 may use.
This is the conclusion the final reasoner should reach.
This off-frame item should disappear because it does not fit the current story.
```

### What The LLM/Judgment Layer Must Do

The cognitive work happens in LLM judgment:

- read the conversation as a whole;
- interpret what happened between user and assistant;
- notice the problem state, not just the topic;
- decide whether a pressure is live or merely plausible;
- decide whether an artifact belongs in active, brief, scan, or parked
  attention;
- decide whether to ask the user something before answering;
- decide what to set aside with a reason;
- preserve useful conflict, strangeness, and negative space;
- synthesize the final answer in ordinary language.

Sub-agents or OpenRouter calls, when used, should be treated as narrow judgment
probes, not as a default worker system. Small targeted calls are preferable to a
single overloaded prompt that tries to be Polya, Bevelin, selector, critic, and
Step 6 planner at the same time.

### Handoff Preparation Doctrine

Any future handoff or portfolio design should preserve these experimentally
earned rules:

1. No active handoff is success when the simple material already carries the
   important pressure.
2. Active handoff content must name concrete pressure likely to be lost without
   it.
3. Generic clarity, nuance, structure, source-looking texture, or visible
   diligence must not justify active handoff content.
4. One compact active handoff remains the maximum default active surface
   observed so far.
5. Edge receipts, weak signals, and parked refs may be broader than the active
   handoff, provided they are compact and clearly bounded.
6. Handoff content should preserve pressure, not plan the answer.
7. Naturalness debt is real: even valid preparation can make the final answer
   feel procedural or over-engineered if Step 6 over-obeys it.
8. A declined or parked item should record what would reactivate it.

### Attention Budget Doctrine

The current raw/hybrid experiments used small count caps such as a handful of
artifacts, source excerpts, and inspect-more items. Those caps were useful for
testing whether compact surfaces could beat raw dumps, but they are too crude
for the reasoning-portfolio target.

Future caps should be by attention weight, not just item count:

```text
active working set:        few items, high detail, Step 6 must consider
brief receipts:            medium items, one-line why/boundary
scan reserve:              broader edge/latticework receipts, very compact
parked index:              larger preserved list with reactivation refs
full archive:              uncrowded source of truth, not injected wholesale
```

Initial research budgets to evaluate:

```text
active_working_set:          4-7 items
edge_latticework_reserve:    6-12 compact receipts
weak_or_negative_space:      3-8 compact receipts
parked_but_preserved:        capped by render budget, not by narrow usefulness
source_excerpts_inline:      4-6, with expansion refs for the rest
```

These are research budgets, not final product limits.

### What A Compact Active Handoff May Preserve

A compact active handoff may preserve one or two of:

- a live tension the final reasoner may smooth over;
- a constraint the final reasoner may underweight;
- a key unknown the final reasoner may answer around;
- a problem-restatement warning;
- a minimal route hint;
- a source/evidence boundary;
- a reactivation condition.

### What Preparation Must Avoid

Pre-Step-6 preparation must avoid:

- final advice;
- answer outline;
- full plan;
- generic nuance;
- generic clarity;
- procedural completeness;
- source-looking texture as value;
- worker labels in the final user-facing output;
- bundle language in the final user-facing output;
- selector language that hides judgment;
- invented options;
- numeric priors unless source-grounded and necessary;
- confidence theater;
- public model-name parade.

### Polya And Bevelin As Thinking Instructions

Polya should help the judgment layer ask:

```text
What kind of problem is this?
What is known?
What is unknown?
What move would help thinking progress?
Should we simplify, reframe, ask, or proceed?
```

Bevelin should help the judgment layer ask:

```text
What source fact activates this pressure?
What does the evidence justify?
What assumption is being smuggled in?
What denominator, alternative, incentive, or missing non-event matters?
What would disprove or relax this pressure?
What happens if this model is forced?
What happens if this model is ignored?
What should Step 6 test cheaply before using it?
```

These are not product labels. They are private instructions for how to think
about material that the deterministic system has surfaced and preserved.

Bevelin is especially useful as an affordance interpreter, not a taxonomy. It
should help each small call describe what an artifact might reveal, what
evidence boundary controls it, and when forcing it would mislead. It should not
turn every case into a bias hunt or a mental-model parade.

### Helicopter View Of The Desired System

At the highest level, the envisioned skill should:

```text
read the conversation
think about what happened
figure out what kind of problem state exists
ask the user questions only when necessary
surface pressure that helps thinking move outside the smooth conversation path
preserve direct pressure plus edge/latticework pressure
present useful possibilities on a silver platter
let the final reasoner decide what to use, reject, defer, or translate
record what happened
```

The system should help the solver think outside the path created by fluent
conversation. It should not merely continue the smoothness of the existing
prompt-response flow.

## Prior Artifact Reality To Account For

The pre-Step-6 layer is not analyzing one clean object. It must reason over a
set of already engineered artifacts, including prior run shapes such as:

- `delta_card` with findings, top findings, secondary findings, compound
  groups, detected tendencies, and selected model ids;
- `companion_cheat_sheet` with anchors, chunk counts, budgets, anti-echo model
  ids, and reranker data;
- `companion_card` with detected models, expansions, and failure hints;
- `frame_pressure_card` with frame elements, reframings, anti-echo ids, overlap
  flags, and dropped elements;
- `structural_coverage_card` with question type, dimensions, gap routes, and
  gap questions;
- `audit_summary` with triage scores, calls, and routing;
- `run_health`;
- raw artifact handoffs with fields such as `why_provided`, `contribution`,
  `hard_boundary`, `risk_if_forced`, and `risk_if_ignored`.

The new layer should not treat these as clutter to summarize away. They are
candidate reasoning material. The problem is presentation and attention
allocation, not erasure.

## Knowledge Goals

1. Clarify whether a small `problem_state.v1` object after extraction is useful.
2. Clarify whether decomposed `reasoning_affordance.v1` records improve Step 6
   preparation better than a monolithic `solver_control_note.v1`.
3. Clarify whether `step6_attention_map.v1` can reduce artifact bloat without
   prematurely suppressing off-frame reasoning pressure.
4. Preserve the evidence for moving post-Step-6 sub-agent pressure checks out
   of the default path, without treating that move as already proven.
5. Preserve optional deeper review as a possible mode for high-stakes or
   manually requested runs.
6. Identify where cost and latency can be reduced without weakening cognition.
7. Keep Step 6, Claude/Codex, or another high-context reasoner as the actual
   solver unless future evidence argues otherwise.
8. Keep deterministic code as custody, diversity, validation, and attention
   budgeting, not judgment.
9. Keep user-facing output clean and free of internal machinery.
10. Establish how Bevelin can help preserve Munger-style edge without becoming
    a brittle deterministic mental-model taxonomy.

## Non-Goals

Do not build:

- a Polya lane;
- a Bevelin lane;
- a new mental-model taxonomy;
- a deterministic answer selector;
- a deterministic usefulness selector that silently discards edge pressure;
- a default sub-agent worker system;
- a hidden answer generator before Step 6;
- a public handoff mode;
- a bundle system;
- runtime wiring before local evidence exists.

Do not make the deterministic engine decide final advice.

## Current Default Workflow

Current skill flow:

```text
Step 1  Capture conversation
Step 2  Extract decision structure
Step 2.5 Readback and audit promise
Step 3  Run Lolla pipeline
Step 4  Render counterargument lead
Step 6  Claude/Codex writes updated position
Step 6b Persist revised answer and private ledger
Step 7  Run pressure-check sub-agents
Step 8  Compare Step 6 against sub-agent outputs
Step 8b Persist pressure check
Step 8c Prepare memo fields and render memo
Step 9  Observatory
Step 10 Archive
```

The candidate default to test removes Step 7 and Step 8 from the mandatory path
and adds a pre-Step-6 reasoning portfolio.

## Candidate Default Workflow To Evaluate

```text
Step 1  Capture conversation
Step 2  Extract decision structure
Step 2a Derive problem_state.v1
Step 2.5 Readback and audit promise
Step 3  Run existing Lolla pipeline
Step 4  Render counterargument lead
Step 5a Build candidate inventory from engineered artifacts
Step 5b Generate reasoning_affordance.v1 records with small targeted calls
Step 5c Assemble step6_attention_map.v1
Step 6  Claude/Codex writes updated position
Step 6b Persist revised answer, private ledger, and portfolio receipt
Step 8c Prepare memo fields and render memo
Step 9  Observatory
Step 10 Archive
```

Optional deeper-review mode:

```text
Step 7  Optional pressure-check sub-agents
Step 8  Optional pressure-check comparison
Step 8b Optional pressure-check persistence
```

When optional pressure check is not run, the run should record:

```json
{
  "gap_check": {
    "status": "not_run_default_off",
    "reason": "post_step6_pressure_check_is_optional_for_cost_control"
  }
}
```

This prevents the Observatory or archive from treating the missing pressure
check as an incomplete run.

## Artifact 1: problem_state.v1

### Purpose

`problem_state.v1` makes the conversation legible as a problem before the audit
lanes run.

It is mostly Polya-shaped:

```text
What is the user trying to solve?
What is known?
What is unknown?
What constraints are live?
What kind of problem is this?
What move may be needed next?
```

### Producer

Initial implementation options:

1. Derive it inside the existing extraction step.
2. Add a small post-extraction LLM pass that reads `extraction.json` and the
   captured conversation.

For a first local build, compare option 2 against the cost of changing the
existing extraction contract. Do not assume either placement is correct before
testing.

### Consumer

Consumers:

- readback text;
- pipeline context if later approved;
- `reasoning_affordance.v1`;
- `step6_attention_map.v1`;
- Step 6 private reasoning.

### Draft Schema

```json
{
  "schema_version": "problem_state.v1",
  "case_id": "string",
  "source_refs": ["turn:1", "turn:2"],
  "user_goal": "string",
  "problem_type": "decision_evaluation | action_planning | causal_diagnosis | critique | explanation | prediction | design | unclear",
  "knowns": ["string"],
  "unknowns": ["string"],
  "constraints": ["string"],
  "success_condition": "string",
  "missing_user_owned_info": ["string"],
  "suggested_next_move": "answer_now | ask_user | audit_first | stop_capture_or_scope_issue",
  "why": "string"
}
```

### Caps

- `knowns`: max 5
- `unknowns`: max 5
- `constraints`: max 5
- `missing_user_owned_info`: max 3
- `why`: max 80 words

### Forbidden Content

`problem_state.v1` must not contain:

- final advice;
- answer outlines;
- "correct answer";
- "best option";
- "the user should";
- mental-model labels as proof;
- handoff recommendations;
- generator or runtime-promotion language.

## Artifact 2: reasoning_affordance.v1

### Purpose

`reasoning_affordance.v1` is a small per-candidate interpretation record. It
does not decide whether an artifact is useful. It names what the artifact might
reveal, why it was selected, what boundary controls it, and how Step 6 can test
it cheaply.

This is where Bevelin-style thinking is most useful:

```text
What source fact activates this?
What must be true for it to matter?
What would go wrong if forced?
What would be lost if ignored?
```

The point is not to ask OpenRouter or a sub-agent to do too much. The point is
to run small, targeted, schema-bound calls that each see:

- a compact problem read;
- one candidate or tightly related candidate group;
- the source excerpt or artifact fields that justify the candidate;
- a small private preset such as Bevelin v0;
- the output schema.

### Producer

Research options:

1. Small parallel OpenRouter/provider calls, one per candidate or candidate
   cluster.
2. Local sub-agents used as bounded workers, one per candidate cluster.
3. A deterministic baseline that simply converts existing raw artifact fields
   into affordance records for comparison.

The first implementation should compare decomposed calls against the earlier
raw and hybrid handoff renderers. It should not assume cognition is always
worth the cost.

### Consumer

Consumers:

- `step6_attention_map.v1`;
- optional pre-Step-6 reviewers;
- Observatory operator view;
- replay/evaluation fixtures.

Step 6 should usually consume the assembled attention map, not the full list of
affordance records.

### Draft Schema

```json
{
  "schema_version": "reasoning_affordance.v1",
  "case_id": "string",
  "artifact_id": "string",
  "source_refs": ["turn:1", "result:delta_card.findings.0"],
  "selection_basis": "string",
  "affordance_class": "direct_pressure | structural_lens | contrarian_edge | weak_signal | negative_space | duplicate_support | false_friend | parked_receipt",
  "protected_slot": "inversion | denominator | incentive | disconfirmation | opportunity_cost | lollapalooza | model_forcing_risk | sequence_stop_rule | negative_space | none",
  "what_it_might_reveal": "string",
  "source_grounding": "string",
  "cheap_test_for_step6": "string",
  "hard_boundary": "string",
  "relaxation_condition": "string",
  "discard_condition": "string",
  "risk_if_forced": "string",
  "risk_if_ignored": "string",
  "attention_weight": "active | brief | scan | parked",
  "expansion_ref": "string"
}
```

### Field Intent

`selection_basis` should say why the engine or knowledge base surfaced this
candidate. This preserves non-LLM selection reasons even when a small model
would not have picked the item on its own.

`affordance_class` says what kind of reasoning use the item may have. It is not
a truth label.

`protected_slot` gives the deterministic layer a way to preserve Munger-style
latticework diversity without pretending to know final relevance.

`attention_weight` controls representation size, not intellectual permission.
Step 6 may promote, demote, or reject after considering the item.

`expansion_ref` preserves the route back to the fuller artifact. This lets the
inline portfolio stay compact without deleting possibility.

### Caps

- `selection_basis`: max 40 words
- `what_it_might_reveal`: max 60 words
- `source_grounding`: max 60 words
- `cheap_test_for_step6`: max 40 words
- `hard_boundary`: max 40 words
- `relaxation_condition`: max 40 words
- `discard_condition`: max 40 words
- `risk_if_forced`: max 40 words
- `risk_if_ignored`: max 40 words
- `expansion_ref`: max 1 stable pointer

### Forbidden Content

`reasoning_affordance.v1` must not contain:

- final advice;
- answer outline;
- "use this because it is correct";
- "drop this because it is not relevant";
- hidden chain-of-thought style reasoning;
- generic "add nuance" or "improve clarity";
- mental-model labels as proof;
- new facts without source refs;
- runtime promotion;
- worker-system language.

## Artifact 3: step6_attention_map.v1

### Purpose

`step6_attention_map.v1` is the fan-in object that Step 6 sees. It is a private
reasoning portfolio, not a verdict.

It should give Step 6:

- a compact active working set;
- a broader edge/latticework reserve;
- weak or negative-space receipts;
- parked-but-preserved items with reactivation conditions;
- source excerpts and expansion refs;
- a short instruction for how to use the portfolio without over-obeying it.

The map should preserve broad availability while making the actual prompt
smaller and less chaotic than injecting every engineered artifact.

### Producer

A deterministic assembler plus a small LLM fan-in call may be used:

1. Deterministic inventory builds the candidate universe from result artifacts,
   raw/hybrid handoffs, V60 private enrichment, and source excerpts.
2. Small targeted calls produce `reasoning_affordance.v1` records.
3. A deterministic budgeter enforces attention weights, protected slots, caps,
   source refs, and expansion refs.
4. An optional small fan-in LLM can write the natural-language
   `step6_instruction` and resolve duplicate phrasing.

The fan-in step must not become an answer generator.

### Consumer

Consumers:

- Step 6 revised answer;
- Step 6b ledger/receipt;
- memo fields;
- Observatory operator view;
- optional reviewer admission logic.

### Draft Schema

```json
{
  "schema_version": "step6_attention_map.v1",
  "case_id": "string",
  "source_refs": ["turn:1", "turn:2"],
  "problem_read": {
    "user_goal": "string",
    "problem_type": "string",
    "suggested_next_move": "answer_now | ask_user | audit_first | stop_insufficient_grounding"
  },
  "active_working_set": [
    {
      "artifact_id": "string",
      "why_available": "string",
      "step6_use": "string",
      "boundary": "string",
      "risk_if_ignored": "string",
      "expansion_ref": "string"
    }
  ],
  "edge_latticework_reserve": [
    {
      "artifact_id": "string",
      "protected_slot": "string",
      "why_available": "string",
      "cheap_test": "string",
      "risk_if_forced": "string",
      "risk_if_ignored": "string",
      "expansion_ref": "string"
    }
  ],
  "weak_or_negative_space_receipts": [
    {
      "artifact_id": "string",
      "why_preserved": "string",
      "reactivate_if": "string",
      "expansion_ref": "string"
    }
  ],
  "parked_but_preserved": [
    {
      "artifact_id": "string",
      "park_reason": "string",
      "reactivate_if": "string",
      "expansion_ref": "string"
    }
  ],
  "ask_user_if_any": [
    {
      "question": "string",
      "why_it_matters": "string"
    }
  ],
  "review_admission": "none | optional_review | manual_only | stop_insufficient_grounding",
  "full_archive_refs": ["string"],
  "step6_instruction": "string"
}
```

### Step 6 Instruction Template

The instruction should be short and private. A candidate template:

```text
Use this as an attention map, not as a verdict. Consider the active working set
first, scan the edge reserve before finalizing, and reject any item that fails
its boundary or cheap test. Do not expose internal labels. Write the best
answer in ordinary language.
```

### Historical Alias

`solver_control_note.v1` should be considered superseded by
`step6_attention_map.v1` unless future tests prove that a monolithic control
note beats decomposed affordances plus an attention map. If retained, it should
be a rendered view of `step6_attention_map.v1`, not a broad single call over all
artifacts.

### Caps

- `active_working_set`: target 4-7 items
- `edge_latticework_reserve`: target 6-12 compact receipts
- `weak_or_negative_space_receipts`: target 3-8 compact receipts
- `parked_but_preserved`: render-budget capped
- `ask_user_if_any`: max 2
- `step6_instruction`: max 90 words

### Forbidden Content

`step6_attention_map.v1` must not contain:

- final advice;
- full answer plan;
- "Step 6 should conclude";
- "correct answer";
- ungrounded new facts;
- mental-model labels as public proof;
- generic "add nuance";
- generic "be clearer";
- hidden chain-of-thought style reasoning;
- public model-name parade.

### Validation Knowledge

Validators should preserve the lessons from prior handoff research:

```text
If active_working_set is non-empty:
  each item must name concrete pressure or concrete use.
  generic clarity / nuance / structure language is invalid.

If edge_latticework_reserve is non-empty:
  each item must name a protected slot, cheap test, and risk_if_forced.
  low narrative fit is not a valid suppression reason by itself.

If parked_but_preserved is non-empty:
  each item must keep an expansion_ref and reactivation condition.

If review_admission == optional_review:
  the reason should be stakes, unresolved contradiction, excessive burden, or
  uncertainty about pruning, not generic diligence.

If suggested_next_move == ask_user:
  ask_user_if_any should name only user-owned information that would materially
  change the answer.
```

These checks are not meant to make deterministic code decide usefulness. They
are meant to stop invalid artifacts from masquerading as judgment.

## Optional Pre-Step-6 Reviewers

Pre-Step-6 reviewers, if retained, should be optional and narrow. They should
run only when `step6_attention_map.v1.review_admission == "optional_review"` or
when the operator explicitly requests deeper review.

Reviewers should audit the portfolio, not answer the user's problem.

Use the already-tested three-reviewer shape, with one added pruning reviewer:

```text
loss reviewer:
  What would Step 6 likely lose with simple material only?

burden reviewer:
  What would prepared material risk making worse?

minimal reviewer:
  What is the smallest useful active surface, if any?

pruning reviewer:
  Did the portfolio suppress or park any edge material too aggressively?
```

Allowed outcomes:

```text
no_active_handoff
active_surface_ok
promote_edge_receipt
ask_user_first
stop_insufficient_grounding
```

Reviewers may not:

- answer the user's problem;
- produce final advice;
- write a full plan;
- generate a polished answer outline;
- create new handoff modes;
- create runtime worker behavior.

## Post-Step-6 Pressure Check Optionality

The existing post-Step-6 sub-agent pressure check is a candidate to move out of
the default path.

### Rationale

It is useful but expensive:

- adds latency;
- adds token cost;
- produces a lot of information;
- often duplicates the reasoning Step 6 can already do when well guided;
- runs late, after the answer has already been written.

### New Modes

```text
pressure_check_mode = off | manual | high_stakes | always
```

Default:

```text
off
```

Initial local implementation may support only:

```text
off
manual
```

### Skill Behavior When Off

When off:

- do not spawn post-Step-6 sub-agents;
- do not wait for Step 8 comparison;
- do not block memo rendering on pressure-check output;
- persist an explicit not-run receipt;
- ensure run health treats this as intentional, not missing work.

## Stack Responsibilities

### Deterministic Stack

Owns:

- capture files;
- schemas;
- validators;
- source refs;
- candidate inventory;
- routing after candidate selection;
- attention weights and render budgets;
- protected-slot quotas;
- expansion refs;
- duplicate detection;
- result persistence;
- V60 ledger validation;
- product-output hygiene;
- memo rendering;
- archive;
- mode flags.

Does not own:

- semantic meaning;
- final advice;
- problem interpretation;
- deciding whether pressure is true;
- deciding that an off-frame item is useless merely because it is off-frame.

### LLM Stack

Owns:

- extraction;
- `problem_state.v1`;
- `reasoning_affordance.v1`;
- optional fan-in phrasing for `step6_attention_map.v1`;
- Step 6 synthesis;
- private use/reject/defer judgment;
- memo field drafting.

Does not own:

- untracked source claims;
- silently changing source refs;
- uncapped artifacts;
- pretending selected pressure is automatically true;
- suppressing engine-selected protected material without a receipt.

### Embeddings

Own:

- recall;
- vocabulary bridging;
- near-miss candidate surfacing.

Do not own:

- truth;
- final applicability;
- answer direction.

### Sub-Agents And OpenRouter Calls

Own:

- optional independent review;
- bounded per-candidate interpretation;
- optional high-stakes pressure checks;
- small schema-bound judgments where focused context helps.

Do not own:

- default solving;
- full answer generation;
- always-on double-checking;
- routine artifact bloat;
- broad prompts that try to replace Step 6.

## Skill-Level Changes

### SKILL.md Changes

After local fixtures and validators pass, update `SKILL.md`:

1. Add `problem_state.v1` after extraction.
2. Add research-only `reasoning_affordance.v1` generation before Step 6.
3. Add `step6_attention_map.v1` before Step 6.
4. Make post-Step-6 pressure check optional and default-off.
5. Update memo timing so it works when pressure check is not run.
6. Update archive/finalization so intentional skipped pressure check is valid.
7. Add optional manual deeper-review mode.

### User-Facing Product Surface

Do not expose:

- Polya;
- Bevelin;
- `problem_state`;
- `reasoning_affordance`;
- `step6_attention_map`;
- lane names;
- V60/chunk/ledger names;
- sub-agent machinery;
- OpenRouter/model routing details.

User should experience:

- clearer readback;
- stronger counterargument;
- tighter updated position;
- less latency;
- cleaner memo.

## Local Build Plan

### Slice 1: Docs-Only Contract

Add a research contract:

```text
research/pre-step6-reasoning-portfolio-contract-2026-05-20.md
```

It should define:

- `problem_state.v1`;
- `reasoning_affordance.v1`;
- `step6_attention_map.v1`;
- allowed affordance classes;
- allowed attention weights;
- protected slots;
- attention budgets;
- expansion refs;
- caps;
- forbidden language;
- sub-agent/OpenRouter optionality;
- post-Step-6 pressure-check default-off decision;
- the rule that broad preserved availability is preferred to premature
  suppression.

No runtime changes.

### Slice 2: Validators

Add:

```text
scripts/research/pre_step6_problem_states.py
scripts/research/pre_step6_reasoning_affordances.py
scripts/research/pre_step6_attention_maps.py
```

Add tests:

```text
tests/test_pre_step6_problem_states.py
tests/test_pre_step6_reasoning_affordances.py
tests/test_pre_step6_attention_maps.py
```

Validators should reject:

- missing source refs;
- missing expansion refs where required;
- over-cap fields;
- final-advice language;
- answer-plan language;
- runtime-promotion language;
- generator language;
- worker-system language;
- use/drop verdicts masquerading as truth;
- parked items without reactivation conditions;
- edge reserve items without boundaries or cheap tests;
- suppression of protected-slot material without a receipt.

### Slice 3: Fixtures

Create local fixtures:

```text
research/pre-step6-problem-states/*.problem-state.v1.json
research/pre-step6-reasoning-affordances/*.reasoning-affordance.v1.json
research/pre-step6-attention-maps/*.step6-attention-map.v1.json
```

Candidate first cases:

```text
mother-address-year
founder-grant-marcus-equity.high-clutter
third-year-phd-student
mid-level-consultant-report-2
marcus_new_path_result
```

Expected behavior:

```text
mother-address-year -> ask_user_if_needed or compact active pressure
founder-grant-marcus-equity.high-clutter -> broad edge reserve, not raw dump
third-year-phd-student -> active pressure plus protected edge receipts
mid-level-consultant-report-2 -> no active handoff or stop_insufficient_grounding
marcus_new_path_result -> attention map covers delta, companion, frame, structural, audit, and run_health artifacts
```

### Slice 4: Local Generator Scripts

Add research-only scripts:

```text
scripts/research/pre_step6_build_candidate_inventory.py
scripts/research/pre_step6_run_reasoning_affordances.py
scripts/research/pre_step6_build_attention_map.py
```

Inputs:

```text
--conversation-file
--extraction-file
--result-file
--problem-state-file
--raw-handoff-file optional
--hybrid-handoff-file optional
--output-dir
```

Outputs:

```text
candidate-inventory.v1.json
*.reasoning-affordance.v1.json
step6_attention_map.v1.json
```

These scripts may call the configured LLM provider, but they must remain
research-only until promoted.

### Slice 5: Skill Integration Draft

Update `SKILL.md` behind mode flags only after fixtures pass:

```text
LOLLA_STEP6_ATTENTION_MAP=on
LOLLA_PRESSURE_CHECK_MODE=off|manual
```

Historical compatibility flag, if needed:

```text
LOLLA_SOLVER_CONTROL=on
```

Initial default during testing:

```text
LOLLA_STEP6_ATTENTION_MAP=off
LOLLA_PRESSURE_CHECK_MODE=off
```

Promotion requires evidence.

### Slice 6: Cost and Quality Comparison

Compare at least five modes:

```text
A: current default with post-Step-6 sub-agents
B: raw artifact handoff, post-Step-6 sub-agents off
C: hybrid pressure-card handoff, post-Step-6 sub-agents off
D: monolithic solver_control_note, post-Step-6 sub-agents off
E: decomposed reasoning_affordances plus step6_attention_map, post-Step-6 sub-agents off
F: decomposed attention map plus optional reviewers
```

Measure:

- latency;
- token cost;
- revised-answer usefulness;
- grounding;
- practical force;
- overproduction;
- missed-pressure rate;
- premature-pruning rate;
- edge-pressure preservation;
- user-facing clarity;
- product-output hygiene.

## Testing Plan

Focused tests:

```text
PYTHONPATH=. pytest \
  tests/test_pre_step6_problem_states.py \
  tests/test_pre_step6_reasoning_affordances.py \
  tests/test_pre_step6_attention_maps.py
```

Regression tests:

```text
PYTHONPATH=. pytest \
  tests/test_pre_step6_raw_artifacts.py \
  tests/test_pre_step6_workpacks.py \
  tests/test_pre_step6_pressure_card_consumption.py \
  tests/test_pre_step6_hybrid_handoffs.py \
  tests/test_pre_step6_semi_blind_comparisons.py \
  tests/test_pre_step6_replay_ledger.py \
  tests/test_pre_step6_no_rendered_handoffs.py \
  tests/test_pre_step6_decline_evaluations.py
```

Static checks:

```text
git diff --check
```

## Evaluation Criteria

This candidate should only be considered implementation-ready if evidence
shows:

- `problem_state.v1` exists and validates on fixture cases;
- `reasoning_affordance.v1` exists and validates on fixture cases;
- `step6_attention_map.v1` exists and validates on fixture cases;
- the attention map stays private and advisory;
- no final advice appears in pre-Step-6 artifacts;
- Step 6 receives compact active pressure plus a broader edge reserve, not only
  a narrow selected handoff;
- protected edge slots are preserved, parked, or explicitly receipted rather
  than silently suppressed;
- `no_active_handoff`, parked receipts, and no extra pressure remain valid
  success states;
- Step 6 remains free to reject, demote, or promote portfolio items;
- post-Step-6 sub-agent pressure check is default-off;
- optional pressure-check mode can still be run manually or later restored;
- memo/archive/Observatory do not treat intentional pressure-check skip as a
  broken run;
- default run latency and token cost improve, or any cost increase is justified
  by clear answer-quality lift;
- Step 6 remains the solver;
- deterministic code remains custody, diversity, attention budgeting, and
  validation only;
- product-output hygiene remains clean.

## Open Questions

1. Should `problem_state.v1` be produced inside extraction or as a separate
   post-extraction pass?
2. Should `reasoning_affordance.v1` be produced by OpenRouter calls, local
   sub-agents, or a deterministic baseline first?
3. How broad should the edge/latticework reserve be before it becomes attention
   clutter rather than option preservation?
4. Which Bevelin v0 preset fields are load-bearing: evidence gate, denominator,
   disconfirmation, incentive, model-forcing risk, relaxation condition, or
   opportunity cost?
5. What protected slots should deterministic code preserve even when the small
   LLM rates the item as low fit?
6. When should a parked item be promoted back into the active working set?
7. How should Polya be added later without turning the layer into a generic
   problem-solving essay?
8. What is the minimum quality bar before enabling the attention map by
   default?
9. What is the manual trigger for optional pressure check in the skill surface?
10. Should high-stakes mode automatically run optional reviewers, or should
    that remain manual until more evidence exists?

## Initial Task Breakdown

### Task 1: Write Reasoning-Portfolio Contract

Create:

```text
research/pre-step6-reasoning-portfolio-contract-2026-05-20.md
```

Include schemas, enums, protected slots, attention budgets, expansion refs,
forbidden language, and default-off post-Step-6 pressure-check decision.

### Task 2: Add Validators

Create:

```text
scripts/research/pre_step6_problem_states.py
scripts/research/pre_step6_reasoning_affordances.py
scripts/research/pre_step6_attention_maps.py
```

Create tests:

```text
tests/test_pre_step6_problem_states.py
tests/test_pre_step6_reasoning_affordances.py
tests/test_pre_step6_attention_maps.py
```

### Task 3: Add Fixtures

Create fixture artifacts for:

```text
mother-address-year
founder-grant-marcus-equity.high-clutter
third-year-phd-student
mid-level-consultant-report-2
marcus_new_path_result
```

### Task 4: Add Research Builders

Create:

```text
scripts/research/pre_step6_build_candidate_inventory.py
scripts/research/pre_step6_run_reasoning_affordances.py
scripts/research/pre_step6_build_attention_map.py
```

Keep them research-only.

### Task 5: Draft Skill Integration

Update `SKILL.md` behind flags only after fixtures pass.

Required behavior:

- Step 6 reads the attention map.
- Step 6 sees active pressure plus a compact edge reserve.
- parked items keep expansion refs and reactivation conditions.
- post-Step-6 pressure check is optional.
- intentional pressure-check skip persists cleanly.

### Task 6: Compare Old vs New Defaults

Run old and new modes on selected fixtures.

Report:

- cost;
- latency;
- answer usefulness;
- grounding;
- practical force;
- missed pressure;
- premature pruning;
- edge-pressure preservation;
- output hygiene.

## 2026-05-21 Research Status

The current portfolio work remains research-only and shadow-only.

What has been learned:

- Broad private context still looks right. The system performs better when
  Step 6 can see the clean anchor plus Bevelin/Polya-style pressure and decide
  whether to use, combine, reject, or keep it private.
- Deterministic code must not become the cognitive brain. Its job is cache
  lookup, custody, payload tripwires, ledger-shape validation, and reviewer
  consistency checks.
- The first dormant runtime-adjacent implementation now exists behind shadow
  mode only. It adds no live card generation, no normal runtime reviewer calls,
  and no visible-output application.
- Shadow telemetry now records marker/entity-loss candidate flags. These are
  useful smoke alarms, not selectors.
- A shadow-triggered false-positive probe found no confirmed false positive,
  but it did find `ambiguous_visibility` on the founder case because reviewer
  labels and blind winner arms were tense.
- The answer-delta specificity slice added a structured Step 6 ledger field for
  concrete visible-answer changes. Historical additive replay ledgers without
  that field now stand down, and fresh answer-delta replay on founder, PhD, and
  consultant produced `all_private_or_confirming`.
- The original false-standdown bridge cases were rerun under the same
  answer-delta prompt. All three still produced `additive_pressure_present`
  with `concrete_delta_present`, and dual reviewers still judged hiding the
  fresh Step 6 answers behind the anchor as `false_standdown`. This means the
  answer-delta guardrail is not over-tight on the original bridge wins.
- The calibration corpus has now been curated and sampled. The corpus contains
  17 pre-registered cases, covers the required high-clutter,
  sequencing/problem-shape, sensitive/safety/legal, negative-control, and V60
  on/off buckets, and produced 51 live Step 6 samples.
- The corpus floor is met, but the Step 6 stability floor is not. Ten cases are
  stable and seven are unstable. The clean signals are useful: false-positive
  controls, mother, consultant, and two bridge wins behaved as expected. The
  noisy signals are also useful: high-clutter and synthetic V60-pair cases are
  where Step 6 flips between additive, private/confirming, concrete deltas, and
  reframe-only deltas.
- Aggregate read:
  `stability_review_required_before_reviewer_phase`. Reviewer adjudication is
  therefore blocked until the saved Step 6 samples are reviewed for stability,
  otherwise reviewer cognition would be judging sampling noise rather than a
  stable candidate.
- The stability review has now run and the seven unstable cases were repeated
  under the same prompt and model. Two resolved: the marker/entity
  generalization attempt became stable stand-down, and PhD V60-on became stable
  positive. Five remained unstable or borderline, concentrated in
  high-clutter/V60-adjacent cases where Step 6 often marks additive pressure
  but records only `reframed_emphasis` rather than concrete answer deltas.
- This is not a reason to loosen deterministic gates. It is a reason to ask a
  narrow cognitive question over saved samples: are reframe-only outputs ever
  genuinely better/non-inferior, or is the answer-delta guardrail correctly
  suppressing them?
- The reframe diagnostic has now run over saved samples. It selected 3 stable
  controls and 7 reframe-only diagnostics from the repeat pass, then used two
  reviewer families under blind shuffle. Result:
  `answer_delta_vocabulary_design_review_required`.
- Two reframe-only samples were confirmed useful/non-inferior by both reviewer
  families. No reframe-only sample was confirmed correctly suppressed. Six
  records were ambiguous and five had reviewer label/winner-arm tension. This
  is not runtime promotion evidence, but it is enough to show that the current
  answer-delta vocabulary is too narrow for some structural improvements.
- The likely missing concept is a concrete structural reasoning delta: decision
  boundary, test design, stop condition, sequencing frame, or commitment-shape
  change. These are not mere tone shifts, but they also are not always added
  entities or reordered sequences.

Current recommendation:

```text
keep_shadow_only
runtime_promotion_blocked
skill_update_blocked
```

Next safe improvement:

Do not run full reviewer calibration yet. Run
`answer_delta_structural_delta_design_v0` as a research-only vocabulary repair.
Generic `reframed_emphasis` should still not unlock, but Step 6 should have a
way to record concrete structural reasoning changes separately from entity
adds/removals and sequence changes. Do not add the entity-level payload gate
unless future cases with `concrete_delta_present` or a designed
`structural_delta` fail reviewer adjudication. Do not change `SKILL.md` until
calibration stability or a deliberately narrower dormant pilot is approved.

2026-05-21 structural-delta result:
`answer_delta_structural_delta_design_v0` has now run as a research-only
vocabulary repair. The `answer_delta` contract now includes:

```json
{
  "added_entities": [],
  "removed_entities": [],
  "reordered_sequences": [],
  "structural_delta": [],
  "reframed_emphasis": []
}
```

`structural_delta` is explicitly for specific public-answer structure changes:
stop conditions, unlock conditions, decision boundaries, test designs,
commitment boundaries, sequencing gates, or deadline/window logic. It is not a
generic escape hatch for "better framing." The deterministic specificity bar
keeps vague entries like `added structural framing` in `reframe_only`.

The live diagnostic produced 10 samples across four cases. Founder V60-on and
PhD V60-off both became stable positive triplets. A one-sample startup case was
also positive. The Bevelin irrelevant-incentives negative control stood down
3/3. Aggregate result:

```text
sample_count = 10
unlock_sample_count = 7
reframe_only_sample_count = 0
structural_delta_field_sample_count = 7
structural_delta_sample_count = 0
```

Interpretation: Step 6 used `structural_delta` naturally, but the live samples
also named added concrete payload, so the observed specificity bucket remained
`concrete_delta_present`. Pure `structural_delta_present` is implemented and
covered by tests, but remains `not_observed` in live samples. The negative
control surviving 3/3 is important: the new vocabulary did not immediately turn
generic Bevelin pressure into a public-visible answer.

This is the last pre-calibration vocabulary repair. The next move is the full
calibration corpus under the repaired prompt contract, tracking unlock
frequency, reframe-only frequency, structural-delta-only frequency,
structural-delta field usage, n=3 Step 6 stability, and reviewer label/winner
tension. If calibration exposes another missing answer-delta category, treat it
as a design-review signal rather than another quick vocabulary patch.

2026-05-21 targeted rerun addendum:
The two prior reframe-useful samples were rerun under the repaired prompt:

```text
founder-grant-marcus-equity.high-clutter.v60-on sample 0
third-year-phd-student.v2.v60-off sample 2
```

Both reruns produced `additive_pressure_present` and `concrete_delta_present`,
with `structural_delta` populated. Neither remained trapped as `reframe_only`.
This supports the interpretation that the repaired prompt made Step 6 more
specific, rather than merely adding a dormant field.

Pure `structural_delta_present` remains unobserved in live samples and must be
tracked explicitly in full calibration. The calibration Step 6 model is now
pinned to `moonshotai/kimi-k2.6` in the corpus manifest because the repaired
diagnostic and targeted rerun use that model, and the OpenRouter env default
returned `404` during the first live attempt. Do not blend Kimi, GPT-family, or
other model-family samples inside one calibration read.

2026-05-21 Kimi structural-delta calibration result:
The full repaired calibration corpus has now run with
`moonshotai/kimi-k2.6`. It produced 63 saved Step 6 samples: the 51 planned
samples plus 12 same-prompt repeats over the variable cases. The corpus floor
is met and no samples remain incomplete. The run records:

```text
case_count = 17
sample_count = 63
stable_case_count = 13
unstable_case_count = 4
unlock_sample_count = 33
reframe_only_sample_count = 0
structural_delta_field_sample_count = 38
structural_delta_sample_count = 0
```

The positive lesson is strong: the repaired prompt eliminated the earlier
`reframe_only` trap in this corpus. The original bridge wins stayed stable
positive, the mother and false-positive controls stayed stable stand-down, and
generic Bevelin/Polya pressure did not become visible just because
`structural_delta` exists. Step 6 used `structural_delta` naturally as custody
evidence, but every live unlock still had `concrete_delta_present`; pure
`structural_delta_present` remains implemented and tested but not observed in
live calibration.

The blocker also got sharper. Four cases remain variable even after
same-prompt repeat sampling:

```text
founder-grant-marcus-equity.high-clutter.v60-on: 4/6 unlock
mid-level-consultant-report-2:                  3/6 unlock
third-year-phd-student.v2.v60-off:              3/6 unlock
third-year-phd-student.v2.v60-on:               5/6 unlock
```

This is not a deterministic-gate problem and not a reason to add another
answer-delta category. It is Step 6 private-ledger variance: same model, same
prompt, same case shape, but Step 6 sometimes records concrete additive
pressure and sometimes records the deck as private/confirming.

Current recommendation:

```text
runtime_promotion_blocked
skill_update_blocked
shadow_implementation_blocked_for_global_policy
partitioned_reviewer_phase_allowed_for_stable_cases_only
```

Next safe step: run reviewer adjudication only on the 13 stable cases
(6 stable-positive candidates and 7 stable-standdown candidates). Keep the four
variable cases quarantined from promotion and use them for Step 6 ledger
stability design review. This preserves the intended philosophy: broad private
context, Step 6 cognition, deterministic custody, and no public bloat without
accountable evidence.

2026-05-21 partitioned reviewer and variable-case diagnostic result:
The partitioned reviewer phase has now run on the 13 stable cases only, using
`openai/gpt-5.1-chat` and `google/gemini-3.1-flash-lite` as blind reviewer
families. Result:

```text
stable_positive_supported_count = 6/6
stable_positive_rejected_count = 0
stable_standdown_supported_count = 6/7
stable_standdown_rejected_count = 0
ambiguous_count = 1
tension_count = 0
```

The single ambiguous case was benign: the anchor said "name the tripwires" and
the Step 6 answer said "name the specific tripwires." One reviewer called it a
tie, the other called Step 6 non-inferior; both reported no payload loss or
bloat. The strict contract leaves this as ambiguity rather than recoding it into
a clean win.

This supports the stable partition but still does not promote runtime or shadow
implementation.

The variable-case diagnostic also ran. Under Kimi, all four variable cases show
answer-level variance, not just ledger-label variance:

```text
founder V60-on: 4/6 unlock, min token Jaccard 0.549
consultant: 3/6 unlock, min token Jaccard 0.504
PhD V60-off: 3/6 unlock, min token Jaccard 0.596
PhD V60-on: 5/6 unlock, min token Jaccard 0.409
```

An alternative-model probe with `openai/gpt-5.1-chat` then showed the variable
behavior is partly model-family-sensitive:

```text
founder V60-on: still variable, 2/3 unlock
consultant: stable stand-down, 0/3 unlock
PhD V60-off: visibility-stable positive, 3/3 unlock
PhD V60-on: visibility-stable positive, 3/3 unlock
```

The GPT probe also produced five pure `structural_delta_present` samples. That
means the structural-delta path is no longer merely theoretical, even though it
did not fire under Kimi calibration.

Current recommendation:

```text
runtime_promotion_blocked
skill_update_blocked
global_shadow_implementation_blocked
stable_partition_supported_but_not_sufficient
variable_cases_require_model_family_and_answer_core_review
```

Do not add a deterministic wisdom selector. The next design question is whether
Step 6 ledger stability is model-family-sensitive and whether founder V60-on is
a genuinely borderline case shape. Answer that before any global shadow
implementation.

2026-05-21 model-family and V60 review result:
The next research slice tested the red-team concern that model-family stability
could become model-shopping if not adjudicated. Two research-only artifacts were
added:

```text
pre_step6_founder_v60_symmetry_check_v0
pre_step6_gpt_stability_correctness_review_v0
```

Founder V60 symmetry result:

```text
Kimi V60-on: 4/6 unlock, variable
Kimi V60-off: 6/6 unlock, stable positive
GPT V60-on: 2/3 unlock, variable
GPT V60-off: 0/3 unlock, stable stand-down
symmetry_read = v60_on_specific_destabilization_plausible
```

Both model families are variable on founder V60-on and not variable on founder
V60-off. They disagree about which V60-off answer is correct, so this is not a
visibility decision. It is a narrower existing-system finding: the residual
founder instability is plausibly tied to V60-on private context. Audit V60
private context before treating founder variance as a portfolio-policy problem.

The GPT-stability correctness review then ran two reviewer families over the
nine GPT-stable saved outputs. Result:

```text
GPT visible PhD cases supported: 6/6
GPT visible rejected: 0
pure structural_delta_present supported: 3/3
consultant GPT anchor stand-down: 1 rejected, 2 ambiguous, 1 tense record
reviewer_read = gpt_stability_design_review_required
```

This is the important interpretation: GPT stability aligned with reviewer
judgment on the PhD cases, including pure `structural_delta_present` samples,
so `structural_delta` should not be collapsed away. But GPT's stable consultant
stand-down was not cleanly supported; one sample was confirmed rejected and two
were ambiguous. Therefore:

```text
model_family_stability_is_evidence_not_authority
do_not_route_to_gpt_for_stability_alone
do_not_add_a_deterministic_selector_to_mask_variance
```

The Step 6 model class is now part of the calibrated contract. A model upgrade,
provider swap, OpenRouter backend change, or switch from Kimi to GPT is a
recalibration event, not an implementation detail. Calibration claims must say
which Step 6 model family they describe, and mixed-model evidence must be
labeled as diagnostic rather than promotional.

2026-05-22 founder V60 private-context audit result:
The next slice deliberately exited the pre-Step-6 portfolio perimeter and
audited V60/private-context behavior for Founder. This distinction matters:
the finding is about an existing private-context signal, not about adding a new
portfolio visibility rule.

The audited V60 context was:

```text
v60_chunk:overcommitment_without_evidence - Watch for informal promises becoming public commitments before written evidence and board process exist.
```

The mechanical relevance check found that the chunk is related to the Founder
case surface through `board`, `commitments`, and `evidence`. Therefore the
clean read is not "unrelated V60 noise." The result is narrower and more useful:

```text
audit_read = v60_context_related_but_destabilizing
v60_on_variable_family_count = 2
v60_off_variable_family_count = 0
founder_answer_correctness = not_decided
consultant_followup_status = queued_not_addressed
phd_followup_status = queued_not_addressed
```

The audit preserved four precommitted interpretations instead of forcing a
single post-hoc story:

```text
genuine_edge_pressure_structurally_borderline = plausible
selection_noise = weak
joint_overload = plausible
cross_chunk_consideration_gap = insufficient
```

Current interpretation: the V60 chunk is individually defensible edge pressure,
but it destabilizes Step 6 in the combined private packet. That points toward a
V60 packet/presentation interaction audit before any architecture choice. It
does not decide the correct Founder answer, because V60-off still leaves Kimi
and GPT stabilized in opposite directions.

Do not let the Founder V60 audit absorb the other variable-case findings. The
queued follow-ups remain separate:

```text
consultant_case_ambiguity_design_review_v0
kimi_phd_variance_diagnostic_v0
```

Runtime promotion, global shadow implementation, and `SKILL.md` changes remain
blocked. No deterministic selector should be added to hide variance.

2026-05-22 consultant deck-composition cleaning review:
After the Founder V60 audit, the Consultant follow-up was reframed as a
cleaning question rather than a visibility-policy question:

```text
Does the Consultant deck give Step 6 the right material to reach a clean answer,
or are anchor/cards/V60 packaging the case poorly?
```

This slice produced:

```text
consultant_deck_composition_review_v0
consultant_cleaning_variant_v0
```

The review found:

```text
Kimi unlock ratio = 0.5
GPT unlock ratio = 0.0
GPT anchor stand-down reviewer-supported = false
v60_status = not_active
cleaning_read = anchor_strong_deck_pressure_thin_but_useful
```

The Consultant anchor is strong. It already carries counsel-first sequencing,
no confrontation, no private investigation, no unusual system access, attorney
intake questions, the Wednesday protocol, concrete partner-encounter tripwires,
and reversibility. The deck pressure is useful but thin: independent counsel,
built-in channel-bias checking, minimal/narrow partner response, and "until
counsel guides you" as the reversibility boundary.

This explains the variance without adding a gate. The useful delta is small
enough that Step 6 can honestly flip between visible additive pressure and
private confirming support. The problem is not that the resolver lacks a
deterministic rule. The problem is that the deck makes Step 6 infer narrow
pressure atoms from broad Bevelin/Polya identities.

The cleaning variant keeps the anchor as backbone and replaces broad lens labels
with three concrete micro-cards:

```text
counsel_independence_and_channel_bias_card
wednesday_tripwire_preservation_card
reversibility_until_counsel_boundary_card
```

This is the intended direction: cleaner private material for Step 6, not more
audit hygiene after Step 6. The next safe move is
`consultant_cleaning_variant_replay_v0`, which should test whether this cleaner
table improves Step 6 consideration stability. Success is cleaner cognition and
custody, not automatic deck visibility.

2026-05-22 consultant cleaning variant replay:
`consultant_cleaning_variant_replay_v0` replayed the cleaned Consultant table
through live Step 6 sampling with `moonshotai/kimi-k2.6`. Six live samples
completed; sample `4` stalled twice at the provider/model layer and was
replaced by sample `6`.

The aggregate result:

```text
sample_count = 6
micro_card_additive_count = 4
all_private_or_confirming_count = 2
missing_or_unclear_count = 0
unlock_ratio = 0.667
old_kimi_unlock_ratio = 0.5
consideration_stability_read = mixed
cleaning_improvement_read = changed_but_still_mixed
protected_payload_all_present_count = 6
runtime_promotion = blocked
skill_update = blocked
```

The replay improved legibility more than stability. Step 6 did not treat the
cards as a generic bundle. It consistently kept the counsel/channel-bias card
and Wednesday-tripwire card private or confirming, while treating only
`reversibility_until_counsel_boundary_card` as additive in 4/6 samples. The
recurring public-useful delta is narrow:

```text
keep the first moves reversible until counsel guides the next action
```

This is the cleaning lesson. Broad private material was preserved, but the table
made the useful pressure atom visible enough for Step 6 to select it. The case
remains mixed because Step 6 can honestly read the same small boundary as either
a public addition or already sufficiently carried by the anchor.

Do not fix this with another deterministic gate. The better next Consultant
move is an anchor-cleaning probe:

```text
consultant_anchor_boundary_patch_probe_v0
```

Build a patched Consultant anchor candidate that includes the counsel-gated
reversibility boundary, then replay the same three micro-cards. Success would
mean the cards mostly stand down as private/confirming while protected payload
stays intact. That would move the learning into the base table Step 6 receives,
not into a visibility selector.

2026-05-22 consultant anchor-boundary patch probe:
`consultant_anchor_boundary_patch_probe_v0` tested that exact graduation
hypothesis. The probe made one minimal anchor change:

```text
keep the first moves reversible
```

became:

```text
keep the first moves reversible until counsel guides the next action
```

This was a hypothesis-test input, not a proposed per-case patch architecture.
The same three micro-cards remained available.

Aggregate result:

```text
sample_count = 6
micro_card_standdown_count = 5
micro_card_standdown_rate = 0.833
micro_card_additive_count = 1
missing_or_unclear_count = 0
reversibility_card_additive_count = 1
reversibility_card_additive_rate = 0.167
patched_boundary_present_count = 6
protected_payload_all_present_count = 6
protected_payload_preserved = true
upstream_pressure_carried = yes
next_investigation = synthesis
consultant_classification = graduation_candidate
runtime_promotion = blocked
skill_update = blocked
```

Interpretation: the patched anchor carried the recurring pressure. Before the
patch, the reversibility card was additive in 4/6 samples. After the patch, it
was additive in 1/6 samples, with protected payload preserved in every sample.
The one additive outlier appears to be a meta-ledger attribution lag: Step 6
credited the micro-card with adding the patched phrase even though the patched
anchor already contained it.

Consultant should stop here for this research chapter. It is now classified as
a `graduation_candidate` for the single pressure atom:

```text
keep the first moves reversible until counsel guides the next action
```

The follow-up is not a runtime patch. The follow-up is
`consultant_upstream_origin_investigation_v0`, scoped as an upstream-origin
finding: why did the original anchor synthesis compress the pressure to generic
reversibility and drop the counsel-gated terminal condition?

2026-05-22 PhD Kimi variance cleaning review:
`phd_kimi_variance_cleaning_review_v0` tested whether the Consultant cleaning
lesson generalizes. It used the PhD V60-off case to avoid mixing the result
with Founder-style V60 packet instability:

```text
third-year-phd-student.v2.v60-off
```

The visible backbone stayed the rendered hybrid PhD anchor. The private table
contained four atomic cards:

```text
bounded_probe_not_commitment_card
single_cell_collaborator_feasibility_card
fallback_reentry_readiness_card
visible_stop_date_conditions_card
```

No broad Bevelin or Polya lens labels were shown to Step 6.

The first live Kimi call hung at the provider/model layer. The research script
therefore added an opt-in OpenRouter reasoning-disable setting for this slice
only. After that, six live `moonshotai/kimi-k2.6` samples completed cleanly.
This means the evidence condition is:

```text
Kimi + OpenRouter + PhD atomic prompt + reasoning_disabled=true
```

not model family alone.

Aggregate result:

```text
sample_count = 6
micro_card_additive_count = 6
all_private_or_confirming_count = 0
missing_or_unclear_count = 0
protected_payload_all_present_count = 6
atomic_discrimination_read = discriminated
runtime_promotion = blocked
skill_update = blocked
```

Card additive counts:

```text
bounded_probe_not_commitment_card = 4
single_cell_collaborator_feasibility_card = 2
fallback_reentry_readiness_card = 1
visible_stop_date_conditions_card = 3
```

Interpretation: atomic decomposition generalized, but not in the Consultant
shape. Consultant produced one dominant graduation candidate. PhD produced a
distributed pressure pattern. Step 6 selected different subsets of the atomic
cards in different runs, while preserving protected payload in every sample.

This is not a reason to add a gate. It is not a reason to route to GPT. It is
not a reason to promote runtime. It is evidence that card granularity matters:
atoms help Step 6 discriminate when a broad bundle hides several separable
structural moves.

The product lesson is:

```text
cards are diagnostic instruments, not permanent answer engines
```

The next stop-boundary slice is `evidence_surface_v0`: a small human-readable
surface that aggregates Consultant and PhD cleaning results so operators can
see recurring pressure atoms and candidate graduations without reading raw JSON.
It must nominate evidence only. It must not automate upstream graduation.

2026-05-22 cleaning evidence surface:
`evidence_surface_v0` built that minimum surface:

```text
research/pre-step6-cleaning-evidence-surface/cleaning-evidence-surface.v1.json
research/pre-step6-cleaning-evidence-surface/cleaning-evidence-surface.md
```

The surface is research-only and runtime-dormant. Its principles are encoded in
the artifact:

```text
code_may_nominate = true
humans_decide = true
automatic_graduation_allowed = false
runtime_visibility_change_allowed = false
```

It currently covers two cleaning-lane cases:

```text
mid-level-consultant-report-2
third-year-phd-student.v2.v60-off
```

It nominates one Consultant pressure atom for human review:

```text
reversibility_until_counsel_boundary_card
keep the first moves reversible until counsel guides the next action
```

Basis:

```text
4/6 additive before anchor patch
1/6 additive after patched anchor
protected payload preserved 6/6
status = human_review_required
next_investigation = synthesis
```

It does not nominate any PhD atom for graduation. PhD is marked as
`distributed_atomic_discrimination`: useful atom-level pressure is real, but it
is spread across several cards rather than concentrated in one recurring
graduation candidate.

This is the smallest real Evidence Surface layer. It makes patterns readable to
humans. It does not decide wisdom. It does not move cards upstream. It does not
change runtime output. It exists so the human curator can interpret what Step 6
actually used.

The research queue has now reached the stop boundary. The next artifact should
be a closeout decision document, not another probe.

2026-05-22 cleaning research closeout:
The closeout document is:

```text
research/pre-step6-cleaning-research-closeout-2026-05-22.md
```

Closeout decision:

```text
research_phase = complete
runtime_promotion = blocked
skill_update = blocked
shadow_implementation = allowed_as_separate_program
next_research_probe = not_recommended
```

The closeout precommits what shadow implementation means:

```text
LOLLA_STEP6_PORTFOLIO=off|shadow|on
default = off
```

In `shadow`, the card-deck assembly, unified ledger, answer-delta checks,
payload omission records, custody validation, and evidence-surface records may
run in production-adjacent code paths and write archive/Observatory records.
The user-facing answer remains exactly the current Step 6 output. No visibility
decision changes what the user sees.

The closeout also hands off the Founder V60 finding:

```text
Founder V60-on instability is a V60 packet/selection/presentation issue,
not a pre-Step-6 portfolio-policy issue.
```

Recommended next action for Founder is a separate V60 audit, not another
portfolio gate.

This is where this research chapter stops. Continuing to produce more
probe-shaped evidence would now be a way to avoid the product decision rather
than a way to learn something materially new.

## Reconsideration Posture

This document does not recommend immediate implementation.

Before changing `SKILL.md`, the team should decide whether the knowledge in
this PRD supports a real improvement over the current flow.

The first useful evidence would be a small validated contract showing whether:

```text
problem_state.v1 can describe the problem without solving it
reasoning_affordance.v1 can label affordances without becoming a selector
step6_attention_map.v1 can guide Step 6 without becoming an answer plan
edge receipts can stay broad enough without reintroducing artifact bloat
post-Step-6 sub-agents can be removed from default without breaking the run
```

Claims to falsify early:

```text
decomposed affordance calls beat raw/hybrid handoff renderers
the attention map improves Step 6 more than it distracts Step 6
protected edge slots preserve useful reasoning rather than ornamental clutter
small targeted calls are cheaper or more reliable than one monolithic control call
```

If those claims do not hold, the design should be revised or abandoned. If they
do hold, a future implementation can still reconsider placement, schema, cost,
and skill integration before promotion.
