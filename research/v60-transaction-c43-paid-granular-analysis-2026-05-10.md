# V60 Transaction C4.3 Paid Granular Analysis

Date: 2026-05-10
Status: dormant replay evidence only
Branch: `feat/v60-transaction-local-replay-lab`

## Scope

This note analyzes the paid C4.3 consideration-router run at the v60 packet
level. It is not a product-readiness report and it does not promote v60 into
live `/lolla`.

Primary artifacts:

- Run summary:
  `data/evaluations/v60_transaction_replay_lab/2026-05-10-c43-consideration-router-paid-edge-all/summary.json`
- Run report:
  `data/evaluations/v60_transaction_replay_lab/2026-05-10-c43-consideration-router-paid-edge-all/paid_replay_report.md`
- Packets:
  `data/evaluations/v60_transaction_replay_lab/2026-05-10-c43-consideration-router-paid-edge-all/packets/`
- Outputs:
  `data/evaluations/v60_transaction_replay_lab/2026-05-10-c43-consideration-router-paid-edge-all/outputs/`
- Case manifest:
  `research/v60-transaction-replay-case-manifest-2026-05-09.json`

## Plain-English Read

The public result is negative: Arm B beat Arm C in all 8 judged edge-audit
items. That does not mean v60 was useless. It means the C4.3 public surface was
not good enough, and the model often failed the private/public separation.

The private result is more interesting. Across 64 candidate cards, the model
often did the right internal move: reject irrelevant cards, identify duplicates,
defer missing-evidence cards, or keep a useful guardrail private. The problem
is that C4.3 asked one model to do too many things at once:

1. reconsider the answer;
2. produce public prose;
3. maintain a strict card ledger;
4. create a usefulness report;
5. avoid leaking any private mechanism language.

It repeatedly failed parts 3 and 5. That is an architecture finding, not only a
model-quality finding.

The deterministic system is doing useful recall, but it is not yet doing
sufficiently smart packet selection. The cap favors earlier lanes and active
baseline anchors. That often feeds the model cards that confirm what the
vanilla answer already did, while suppressing later gap candidates that might
have produced a less obvious edge.

## How The Deterministic Pickup Actually Works

The paid replay does not run live `/lolla`. It reads archived case artifacts
and turns existing lane outputs into review-only nominations.

The chain is:

1. Load a case from
   `research/v60-transaction-replay-case-manifest-2026-05-09.json`.
2. Load the archived result, extraction, conversation, query, and vanilla answer.
3. Add any explicit manifest nominations as lane `0`.
4. Extract nominations from archived lane outputs:
   - Lane 1: `delta_card.selected_model_ids` and `delta_card.findings[*].selected_model_ids`.
   - Lane 2: `companion_cheat_sheet.anchors[*].model_id`.
   - Lane 3: `frame_pressure_card.reframings[*].grounding_model`.
   - Lane 4: `structural_coverage_card.gap_routes[*].candidate_model_ids`.
5. Merge duplicate model nominations while preserving every `pulled_by` source
   and every `why_pulled` reason.
6. Sort by earliest lane order, then by original discovery order.
7. Keep at most 18 merged nominations for this replay config.
8. Build a v60 reasoning-substrate packet from explicit
   `data/compiled/model_affordances/affordances_v60.json`.
9. Keep 8 candidate cards for `cap8_focused`; suppress the rest.
10. Give the decoder a compact packet view with:
    - card identity;
    - pulled-by lane provenance;
    - source custody;
    - grouped reviewed affordance cards;
    - absence records;
    - do-not-overclaim warnings;
    - suppressed candidate visibility.

Important: the deterministic layer still does not semantically decide what is
true or what must be used. It packages candidates for consideration. The LLM
owns use, rejection, deferral, merging, and public wording.

## Run Configuration

- Variant: `consideration_router`
- Config: `cap8_focused`
- Cases: 8
- Modes: `edge_audit`
- Generator: `x-ai/grok-4.1-fast`
- Judge: `moonshotai/kimi-k2.6`
- Paid calls: 24
- Reported cost: `$0.275665`
- Total tokens: `253,305`
- Input tokens: `178,947`
- Output tokens: `74,358`

Every item had 8 candidate cards and 10 suppressed candidates.

## Aggregate Results

Public judge:

- Arm B wins: 8
- Arm C wins: 0

Validation:

- Ledger valid: 2
- Ledger invalid: 6
- Consideration report valid: 2
- Consideration report invalid: 6
- Delta validation: not applicable for all 8, because C4.3 is not a composed
  public-delta variant.

Raw private usefulness, including invalid reports:

- `useful`: 6
- `mixed`: 1
- `not_useful`: 1

The run summary currently reports consideration usefulness only for valid
reports, so it shows only `{"useful": 1, "not_useful": 1}`. That is technically
accurate for validator-clean outputs, but it hides the raw signal in invalid
reports. Future summaries should report both validator-clean usefulness and raw
declared usefulness.

Across all 64 card assessments:

- Usefulness: 20 high, 21 medium, 23 low.
- Routes: 30 private reasoning, 20 reject duplicate, 9 reject irrelevant,
  5 defer missing evidence, 0 public answer delta.
- Opportunity roles: 18 rejection aid, 14 guardrail, 8 compression aid,
  6 boundary marker, 6 frame changer, 6 evidence gate, 4 tension maker,
  2 diagnostic question.
- Evidence status: 44 quoted exact, 9 inferred from turn, 10 missing,
  1 not needed.
- Ledger dispositions: 20 used, 37 rejected, 7 deferred.

The strongest behavioral fact is this: C4.3 did not treat v60 as a public edge
generator. It treated v60 mostly as private audit material. That matches the
product philosophy, but the public answer path was not composed well enough to
benefit from it.

## Major Failure Modes

### 1. Public Mechanism Leaks

Six consideration reports failed because public fields leaked private mechanism
language. Examples included language like `substrate`, card references,
model-name mentions, and process scaffolding such as `FULL ASSISTANT REASONING`.

This is the clearest architecture lesson. If v60 is private enrichment for
Claude Code or Codex, then the public surface should be composed or sanitized
deterministically. The same model should not be trusted to both reason with the
packet and hide the packet perfectly.

### 2. Ledger Enum Drift

Several invalid ledgers came from the model putting `silent_application` in
`effect_type`. In the schema, `silent_application` is a
`final_answer_visibility`, not an `effect_type`.

Other failures:

- `used` with `effect_type=no_effect`;
- `used` without `final_answer_delta`;
- `deferred` with evidence status that was not missing, conflicting, or inferred;
- rejected cards without `strongest_plausible_application`;
- summary counts not matching transaction rows.

The model's intuition is understandable: it wanted a way to say "this was used
silently." The schema splits that into `effect_type=guardrail` or similar plus
`final_answer_visibility=silent_application`. That split is too easy to violate
in a live generation. A future router should either build ledgers
deterministically from a simpler trace or accept and normalize the model's
natural terms before validation.

### 3. Selected Opportunity Schema Mismatch

Invalid selected opportunities included:

- more than 3 opportunities;
- shortened card IDs such as `card-004` instead of `card-004-premortem`;
- selected route `defer_missing_evidence`, which is allowed for card assessment
  routes but not selected opportunity routes;
- missing public surface for a non-private selected route.

This suggests the C4.3 selected-opportunity schema is slightly out of sync with
the behavior we actually want. If an opportunity is useful because it should be
deferred, the schema should either allow that directly or keep deferred items
outside selected opportunities.

### 4. C4.3 Public Surface Was Weak

Arm C often preserved or repackaged the vanilla answer while Arm B used generic
edge-audit reasoning to find raw case-specific misses. The public judge rewarded
Arm B because it produced visible user value:

- unresolved leadership-review risk in `multi_offer`;
- documentation/evidence preservation in `whistleblower`;
- engineer burn, prospect-bias, and flat-growth cause in `startup_pivot`;
- debt-cost cascade and funding-source question in `real_estate`;
- affordability/resource verification in `friendship_money`;
- boyfriend withdrawal, mother-care logistics, and extension realism in
  `messy_three_problems`;
- employer IP/non-compete risk in `user_has_plan`;
- public single-cell-data path in `phd_research`.

Most of those edges came from raw case facts, not from the selected v60 packet.
That matters. V60 is not a replacement for case-level edge mining. It should
enrich the model's reasoning after the conversation has already been searched
for concrete pressure.

## What Looks Good

### Traceable Candidate Selection

Every card carries provenance:

- which lane pulled it;
- why it was pulled;
- an evidence quote when available;
- coverage status;
- affordance IDs;
- absence records;
- source custody.

This gives us a real audit trail. We can disagree with a selected card without
guessing how it got there.

### Correct Rejection Is Visible

The model correctly rejected several tempting but wrong cards:

- `price-discrimination` in `real_estate`, which was an explicit weak-support
  stress probe, not a natural match;
- `systems-thinking` in `whistleblower`, because the case did not show a
  recurring system pattern beyond the immediate incident;
- `power-dynamics` and `lock-in` in `friendship_money`, because business-style
  leverage frames risked distorting a personal friendship case;
- several tail-risk or antifragility cards in `user_has_plan`, because they did
  not add real evidence beyond the baseline.

This is exactly the behavior we want from private enrichment. The LLM did not
blindly use every card.

### Correct No-Op Exists

`user-has-plan__edge_audit` is the cleanest useful no-op. The ledger and
consideration report both validated. The packet was marked `not_useful`, all 8
cards were rejected, and no public v60 delta was created.

That is not a failure of v60. It is evidence that the router can say "nothing
worth adding here" when the packet duplicates or weakly matches the case.

### Private Reports Are Diagnostically Valuable

Even invalid reports often explain what happened:

- "duplicate of existing pressure";
- "missing case evidence";
- "wrong object";
- "private guardrail only";
- "risks defensiveness if made explicit";
- "would over-structure a personal case."

This is much better than judging only final prose. It gives us an observability
layer over the reasoning transaction.

## What Looks Fishy

### Early Lanes Dominate The Cap

The cap is 8 cards. The nomination list is sorted by lane order. That means
Lane 1 and Lane 2 often consume the packet before Lane 4 coverage candidates
can enter.

This creates a subtle bias: Lane 2 companion anchors often describe mental
models already active in the vanilla answer. Enriching them confirms or
compresses the baseline, but it does not necessarily produce the missing edge.

The system is good at explaining why the current answer works. It is less good
at forcing a genuinely different lens into the packet when the cap is tight.

### Family Redundancy Consumes Slots

The commitment/reversibility family repeatedly consumed multiple slots:

- `sunk-cost-fallacy`;
- `lock-in`;
- `commitment-bias`;
- `switching-costs`;
- `path-dependence`.

These are not identical, but in a capped packet they can become redundant. A
family cap or diversity rule would preserve more room for unrelated lenses.

### Explicit Probe Cards Contaminate Product Read

Two manifest probes were intentionally artificial:

- `batna` in `multi_offer` as a medium-confidence probe;
- `price-discrimination` in `real_estate` as a weak-support probe.

They are valuable for stress testing warning visibility and rejection behavior,
but they should not be counted as evidence of natural product selection quality.
Future product-readiness runs need a no-probe configuration.

### Suppressed Candidates Sometimes Look More Edge-Like

Some suppressed candidates look plausibly useful:

- `survivorship-bias` and `brainstorming` in `phd_research`;
- relationship and psychological-safety cards in `messy_three_problems`;
- uncertainty and calibration cards in `multi_offer`;
- optionality and path-dependence cards in `whistleblower`.

This does not prove they would have helped. It proves we need a selection test
that compares cap strategies, not only decoder variants.

### One Concrete Data Normalization Bug

`phd_research` suppressed `commitment-and-consistency-bias` because the model ID
was not found in the runtime graph. That looks like an alias or naming mismatch
and should be fixed before any merge that depends on clean nomination coverage.

## Per-Run Findings

### `multi-offer__edge_audit`

Selected cards:

- `batna` from explicit lane 0 probe and Lane 4.
- `power-dynamics`, `sunk-cost-fallacy`, `status-quo-bias`,
  `meta-cognitive-reflection`, `information-asymmetry` from Lane 2.
- `optionality` from Lane 3.
- `opportunity-cost` from Lane 4.

Suppressed highlights:

- resource-allocation cards such as `comparative-advantage`, `trade-offs`,
  `prioritization`;
- uncertainty cards such as `true-uncertainty-navigation`,
  `probabilistic-thinking`, `confidence-calibration`;
- `experimentation`.

Private v60 behavior:

- marked packet `useful`;
- selected 0 opportunities;
- mostly routed cards to private reasoning or duplicate/reject paths;
- correctly saw that the cards confirmed existing structure more than they
  changed the public answer.

Public result:

- Arm B won by surfacing the dropped "meets expectations" leadership-review
  thread.
- Arm C produced no public edge and leaked process scaffold.

Assessment:

The selected cards were reasonable, but they were mostly already active in the
baseline. The missing public edge came from conversation memory, not from v60.
This case argues for pairing v60 with raw conversation edge retrieval.

### `whistleblower__edge_audit`

Selected cards:

- `systems-thinking` from Lane 1.
- `information-asymmetry`, `game-theory-payoffs`, `power-dynamics`,
  `principal-agent-problem`, `intellectual-humility` from Lane 2.
- `decision-trees` from Lane 3.
- `sunk-cost-fallacy` from Lane 4.

Suppressed highlights:

- `lock-in`, `commitment-bias`, `switching-costs`, `optionality`,
  `path-dependence`;
- more competitive dynamics cards like `nash-equilibrium`, `prisoners-dilemma`,
  `batna`, `red-queen-effect`, `moral-hazard`.

Private v60 behavior:

- correctly rejected `systems-thinking` as over-structuralization;
- treated game/power/principal-agent cards as private guardrails;
- deferred `decision-trees` because jurisdiction and legal-protection evidence
  were missing.

Public result:

- Arm B won by making documentation and evidence preservation the immediate
  first move.
- Arm C had useful instincts, but leaked "substrate" style language and did not
  translate the private evidence gate into a clean public step.

Assessment:

The deterministic selection was coherent. The problem was translation. V60
confirmed institutional incentive risk, but the best user move was practical
evidence handling. We need either evidence-procedure cards or a composer that
turns private evidence gates into user-safe actions.

### `startup-pivot__edge_audit`

Selected cards:

- `base-rates`, `statistics-concepts`,
  `scientific-method-evidence-testing` from Lane 1.
- `boundaries`, `theory-of-constraints`, `experimentation` from Lane 2.
- `decision-trees`, `falsifiability` from Lane 3.

Suppressed highlights:

- competitive dynamics cards;
- resource-allocation cards such as `opportunity-cost`, `trade-offs`,
  `prioritization`.

Private v60 behavior:

- ledger valid;
- identified `decision-trees` as a high-usefulness frame changer;
- deferred `base-rates` because no reference class evidence was present;
- rejected many cards as baseline duplicates.

Public result:

- Arm B won by surfacing engineer burn, prospect-bias in the signal mix, and
  unknown cause of flat growth.
- Arm C named a hybrid-strategy edge, but public text leaked framework language
  and was weaker than B.

Assessment:

This was one of the better deterministic packets. `decision-trees` found a real
binary-frame issue. But C4.3 routed it privately, and the public edge audit
needed a clearer user-facing delta.

### `real-estate__edge_audit`

Selected cards:

- `price-discrimination` explicit lane 0 weak-support probe.
- `margin-of-safety`, `nash-equilibrium` from Lane 2.
- `premortem`, `optionality` from Lane 3.
- `sunk-cost-fallacy`, `lock-in`, `commitment-bias` from Lane 4.

Suppressed highlights:

- more commitment/reversibility cards;
- more competitive dynamics cards;
- resource-allocation cards.

Private v60 behavior:

- packet marked `mixed`;
- correctly rejected `price-discrimination` as irrelevant;
- treated `premortem` as useful private caution;
- deferred optionality around deadline fixity.

Public result:

- Arm B won by surfacing debt-cost cascade, funding-source proof, post-inspection
  discovery risk, and auction-term realism.
- Arm C produced no public edge and leaked model names.

Assessment:

The packet had good financial-caution lenses, but also artificial and redundant
cards. The strongest edge required concrete financing mechanics, not abstract
mental-model enrichment. Product runs should exclude explicit probes and add
domain-specific evidence-gate retrieval where available.

### `friendship-money__edge_audit`

Selected cards:

- `power-dynamics` from Lane 1.
- `opportunity-cost`, `boundaries` from Lane 2.
- `optionality`, `peer-review-your-perspectives` from Lane 3.
- `sunk-cost-fallacy`, `lock-in`, `commitment-bias` from Lane 4.

Suppressed highlights:

- `empathy`, `psychological-safety`, `six-thinking-hats`, `social-proof`;
- risk-response cards.

Private v60 behavior:

- packet marked `useful`;
- high usefulness for opportunity cost, boundaries, optionality, and sunk cost;
- rejected power/lock-in style business frames as scope mismatch;
- selected 4 private opportunities, violating the max-3 schema.

Public result:

- Arm B won by adding affordability and local-resource verification.
- Arm C mostly preserved the baseline and surfaced only a sunk-cost note.

Assessment:

This is a good example of v60 being useful privately but not visibly additive.
The deterministic packet matched the case well, but the baseline already had
most of the structure. The best public improvements were execution/evidence
checks.

### `messy-three-problems__edge_audit`

Selected cards:

- `delays`, `checklists`, `self-control` from Lane 1.
- `sunk-cost-fallacy`, `wysiati`,
  `scientific-method-evidence-testing` from Lane 2.
- `optionality`, `creative-destruction` from Lane 3.

Suppressed highlights:

- commitment/reversibility cards;
- `power-dynamics`, `empathy`, `psychological-safety`, `six-thinking-hats`,
  `social-proof`.

Private v60 behavior:

- packet marked `useful`;
- five high-usefulness private reasoning routes;
- several used cards had invalid `effect_type=silent_application`.

Public result:

- Arm B won by surfacing boyfriend withdrawal as a stronger signal, mother-care
  logistics, extension rejection risk, and DC inertia.
- Arm C preserved a generic sequencing answer.

Assessment:

The selected cards supported existing sequencing logic. Suppressed relationship
and interpersonal cards may have been more likely to challenge the boyfriend
and mother-care assumptions. This is a cap/diversity warning.

### `user-has-plan__edge_audit`

Selected cards:

- `optimism-bias-and-planning-fallacy`, `optionality`, `feedback-loops` from
  Lane 2.
- `base-rates` from Lane 3.
- `risk-assessment`, `black-swan-events`, `antifragility`,
  `margin-of-safety` from Lane 4.

Suppressed highlights:

- more risk-response and resource-allocation cards;
- `principal-agent-problem`, `moral-hazard`.

Private v60 behavior:

- ledger valid;
- consideration report valid;
- packet marked `not_useful`;
- all 8 cards rejected or privately noted as duplicate/weak.

Public result:

- Arm B won by finding employer IP/non-compete risk, but also invented a
  quantitative founder-survey claim.
- Judge marked promotion as `retest`.

Assessment:

This is the best no-op signal. C4.3 behaved responsibly. The fact that B still
won shows that v60 no-op can be correct while raw edge-audit still finds a
separate case-specific risk. Evaluation must score these separately.

### `phd-research__edge_audit`

Selected cards:

- `step-back`, `falsifiability`, `metacognitive-questioning`,
  `first-principles-thinking` from Lane 1.
- `regret-theory`, `base-rates`, `problem-framing-and-reframing`,
  `risk-assessment` from Lane 2.

Suppressed highlights:

- `commitment-and-consistency-bias` was suppressed as
  `model_id_not_in_runtime_graph`;
- `survivorship-bias`;
- `brainstorming`;
- competitive dynamics cards.

Private v60 behavior:

- packet marked `useful`;
- high usefulness for regret theory, base rates, reframing, and risk assessment;
- selected 4 private opportunities, violating the max-3 schema;
- several used transactions had `effect_type=no_effect`, invalid for used cards.

Public result:

- Arm B won by surfacing public single-cell-data validation and conditional
  prerequisites.
- Arm C mostly restated the baseline.

Assessment:

The selected cards heavily overlapped the baseline's existing reasoning.
Suppressed `survivorship-bias` and `brainstorming` may have been more
edge-generating. The naming mismatch needs a cleanup.

## Deterministic Selection Lessons

### The Current System Recalls Before It Ranks

The deterministic packet builder is reliable at carrying lane provenance into a
v60 card packet. It is not yet ranking for marginal cognitive value. It mostly
answers:

> What models did prior lanes already nominate?

It does not yet answer:

> Which v60 affordance or absence chunk is most likely to add a useful new
> consideration beyond the vanilla answer?

That is the central next step.

### Lane 2 Is High Precision But Often Low Marginal Delta

Lane 2 companion anchors are strong because they are anchored in the existing
answer. But that is also why they often duplicate the baseline. They are useful
for guardrails and confirmation, less reliable for non-obvious edge discovery.

### Lane 4 Is Under-Exercised Under Cap Pressure

Lane 4 gap candidates often arrive after the cap. They need either reserved
slots or a diversity rule. Otherwise the packet can become a mirror of the
answer's current reasoning instead of an invitation to think sideways.

### Absence Is Present But Not Yet Central Enough

Every selected card had absence records. The model used missing-evidence logic,
but it did not visibly reason from specific absence records as first-class
blockers. In a v60 world with hundreds of absence records, absence should have
its own route, maybe `absence_blocker`, not only a background caution.

### Embeddings/QMD-Style Retrieval Should Be Additive, Not Sovereign

The qmd lesson is relevant: smarter pickup probably needs hybrid retrieval,
including lexical match, semantic embeddings, query expansion, metadata, and
reranking. But embeddings should be low-trust recall. They can help find
candidate affordance chunks and absence blockers; they should not decide what
is true or what the answer must say.

## Product Interpretation

V60 should not be a user-facing module. It should be private enrichment for the
reasoning agent or skill.

The product shape should be:

1. Existing conversation and lane machinery identifies candidate model IDs and
   pressure surfaces.
2. A v60 enrichment adapter expands those model IDs into grouped affordance and
   absence cards.
3. The reasoning model privately considers the packet.
4. The model returns a trace of use, rejection, deferral, and private value.
5. Deterministic code validates IDs, caps, leaks, evidence statuses, and public
   admission rules.
6. A public composer admits only clean, useful, user-safe deltas.
7. The human user never sees v60 internals unless we build a separate debug or
   professional review surface.

This keeps the deterministic system in the right role: courier, guardrail,
validator, and observability layer. It does not become the judge of the user's
whole situation.

## Recommended Next Moves Before Any Product Merge

1. Keep C4.3 as lab-only evidence. Do not connect it to live `/lolla`.
2. Add a product-mode replay with no explicit manifest probes.
3. Split the C4.3 task:
   - the LLM produces only private consideration trace and usefulness report;
   - deterministic code builds or normalizes the ledger;
   - deterministic composer controls any public delta.
4. Add raw usefulness aggregation even when the report is validator-invalid.
5. Fix or alias `commitment-and-consistency-bias`.
6. Add family caps and lane-diversity caps:
   - reserve some slots for active baseline anchors;
   - reserve some slots for gap/novel lenses;
   - reserve at least one slot for absence/evidence blockers when available;
   - keep weak-support probes only in stress-test mode.
7. Add an absence-specific route and validator checks.
8. Run a cap-strategy comparison:
   - lane-order cap8;
   - family-diverse cap8;
   - lane-reserved cap8;
   - affordance-level semantic rerank cap8;
   - cap12 pressure test.
9. Evaluate separately:
   - public answer quality;
   - private usefulness;
   - correct rejection;
   - correct deferral;
   - no-op correctness;
   - retrieval quality;
   - leak and ledger compliance.

## Bottom Line

C4.3 proves that v60 can create useful private consideration traces, including
correct rejection and correct no-op. It also proves that the current all-in-one
public/private C4.3 decoder is not product-safe.

The bottleneck is no longer only corpus quality. It is packet selection and
epistemic transport:

> Can we choose the right v60 chunks, show them privately to the reasoning
> model, preserve freedom of conclusion, and still force honest consideration
> without leaking theater into the answer?

This run says: partly yes on private consideration, no on direct public
generation, and not yet on deterministic selection quality under tight caps.
