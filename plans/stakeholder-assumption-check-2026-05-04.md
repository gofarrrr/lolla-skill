# Plan: Stakeholder Assumption Check

> Source: ToM spike discussion, `/Users/marcin/Downloads/tom_llm_memo (1).md`, and local spike `research/spikes/tom-evidence-study-2026-04-29/`.
> Status: implementation plan, not production doctrine.
> Product name: internal only. Do not expose "Theory of Mind" to users.

## Product Thesis

Lolla should not try to read people's minds. It should catch when the advice already does.

The useful feature is not a broad empathy lane, a visible "perspectives brief", or a psychological profile of every person in the story. The useful feature is a narrow assumption check:

1. The advice depends on another actor.
2. The advice assumes that actor knows, wants, believes, interprets, permits, blocks, retaliates, cooperates, or exits in a particular way.
3. That assumption may be grounded, plausible, or speculative.
4. If the assumption is wrong, the plan changes.

Only item 4 earns user-facing space.

## Research Takeaways To Preserve

- SimToM: split perspective filtering from reasoning. First ask what the actor knows; only then ask what the advice assumes about that actor.
- FANToM: information-asymmetric conversations are the real target. Multi-framing consistency matters when the same stakeholder assumption drives advice.
- Ullman / SCALPEL: bridging facts must be explicit. If the model relies on "they saw it", "they were told", "they have access", or "they can infer it", that bridge must be named.
- Shapira: ToM behavior is not robust enough for confident psychological narration.
- ToMBench: emotion, desire, intention, knowledge, belief, and non-literal communication are useful taxonomy, not fields to fill every run.

## Non-Goals

- Do not create a visible "Theory of Mind" section.
- Do not create stakeholder emotion cards.
- Do not predict reactions unless a predicted reaction changes a concrete action.
- Do not add a fifth major product lane in the first implementation.
- Do not trigger merely because the conversation names another person.
- Do not surface speculative mental-state claims in chat or memo.
- Do not use numeric confidence like `0.85`. Use qualitative grounding tiers.

## Durable Architectural Decisions

- **Runtime location**: optional check after audit cards exist and before final pressure-check synthesis.
- **Initial integration**: feed plan-changing stakeholder assumptions into the existing pressure-check path, not a new visible chat beat.
- **Result field**: persist under `stakeholder_assumption_check` in `result.json`.
- **Surface rule**: user-facing chat only receives stakeholder material when it changes the recommendation.
- **Memo rule**: stakeholder material appears only inside the existing decision-note or pressure-check section when surfaced in chat or Step 8.
- **Observatory rule**: Observatory may show the full inspectable ledger because it is the detail surface.
- **Failure rule**: if the checker triggers and fails, record the failure in `run_health`; do not silently disappear it.
- **Grounding tiers**:
  - `grounded`: directly stated, quoted, or strongly established by the transcript.
  - `plausible`: reasonable inference, but not safe enough to carry advice alone.
  - `speculative`: possible, but must not be used as the basis for advice unless framed as an open question.

## Trigger Contract

The checker should run only when at least one trigger is present and the possible output could change a plan.

### Trigger Signals

Run when any of these are true:

- The advice recommends communicating with a specific person or group.
- The advice depends on another actor's cooperation, consent, silence, interpretation, approval, retaliation, exit, funding, access, or enforcement.
- A stakeholder has veto, blocking, custody, governance, legal, financial, social, or operational power.
- The user explicitly worries about someone's reaction.
- The answer uses phrases equivalent to: "they will", "they won't", "they care about", "they are likely to", "they will understand", "they will accept", "they will react", "they probably want".
- There is material information asymmetry between the user and another actor.
- Structural Coverage flags material gaps in `stakeholder-alignment`, `incentive-alignment`, `competitive-dynamics`, `information-quality`, or `risk-response`.
- The pressure-check stage surfaces an alternative stakeholder forum, channel, sequence, or commitment structure.

### Skip Conditions

Skip when any of these are true:

- No concrete third-party actor materially affects the recommendation.
- The third party is merely background context.
- The only possible output would be generic: "consider how they might feel".
- The check cannot change an action, threshold, sequence, question, risk treatment, or communication content.
- The conversation is too thin to ground actor-specific claims and no communication/action depends on the actor.

## Data Contract

Persist a compact object. Do not persist a broad mental profile.

```json
{
  "status": "skipped | completed | skipped_error",
  "triggered": true,
  "trigger_reason": "recommendation depends on ex-husband cooperation and interpretation",
  "surface": true,
  "summary": "Share general grooming-pattern evidence, not screenshots or exact phrases.",
  "critical_actors": [
    {
      "actor_id": "ex_husband",
      "display_name": "ex-husband",
      "role": "co-parent with 50% custody",
      "power_or_dependency": ["custody", "counter-messaging", "therapy buy-in"],
      "advice_assumption": "He can be moved by evidence without using it against the trust-rebuild.",
      "grounding": "plausible",
      "known_to_actor": [
        "He has been told the mother thinks the Instagram contact is serious."
      ],
      "unknown_to_actor": [
        "Exact surveillance details unless the mother discloses them."
      ],
      "bridging_facts": [
        "He has 50% custody, so his interpretation can shape the daughter's weekends."
      ],
      "unsafe_inferences": [
        "That he will use evidence constructively after receiving it."
      ],
      "risk_if_wrong": "He reframes the evidence to the daughter as proof the mother is overreacting.",
      "plan_change": "Share general legal and grooming-pattern facts; do not forward screenshots or exact phrases.",
      "open_question": "What evidence can move him without giving him material to weaponize?"
    }
  ]
}
```

Required invariant: every surfaced item must include `plan_change`.

## Prompt Contract

### Stage A: Evidence Ledger

Purpose: identify what the actor actually knows and what the advice must not assume.

Rules:

- Use only transcript-grounded facts.
- If a fact is inferred from role, closeness, or likely access, mark it `plausible`, not `grounded`.
- If the actor might know a fact but the transcript does not establish it, place it in `unknown_or_unproven`.
- List bridging facts explicitly.
- Do not infer emotions, desires, or intentions in this stage.

Output:

```json
{
  "actors": [
    {
      "actor_id": "string",
      "display_name": "string",
      "role": "string",
      "power_or_dependency": ["string"],
      "known_grounded": ["string"],
      "known_plausible": ["string"],
      "unknown_or_unproven": ["string"],
      "bridging_facts": ["string"],
      "unsupported_bridges": ["string"]
    }
  ]
}
```

### Stage B: Assumption Audit

Purpose: audit the recommendation, not the actor's soul.

Rules:

- Look for assumptions the advice makes about each actor.
- Classify each assumption as `grounded`, `plausible`, or `speculative`.
- Name the risk if the assumption is wrong.
- Name the smallest plan change.
- Do not list emotions by default.
- Do not output general relationship advice.
- Do not surface anything without a plan change.

Output:

```json
{
  "status": "completed",
  "surface": true,
  "summary": "string",
  "critical_actors": [
    {
      "actor_id": "string",
      "advice_assumption": "string",
      "grounding": "grounded | plausible | speculative",
      "risk_if_wrong": "string",
      "plan_change": "string",
      "open_question": "string"
    }
  ]
}
```

## User-Facing Rendering Contract

Chat receives no new section.

If stakeholder material is material, it appears inside `### Pressure Check` as one concrete correction:

```md
### Pressure Check

One stakeholder assumption changes the plan. I treated the ex conversation as evidence-backed persuasion, but evidence can also become ammunition if forwarded. Share the legal threshold and grooming-pattern summary; do not send screenshots or exact phrases. He gets enough to update, not enough to reframe the situation to your daughter as "your mother is overreacting."
```

Bad:

```md
### Stakeholder Perspective Brief

The ex-husband likely feels defensive and wants control. Your daughter probably feels betrayed. The therapist may want...
```

Why bad: speculative psychology, new visible section, no bounded plan change.

## Validation Metrics

Track these before graduation:

- `trigger_rate`: share of runs where the checker runs. Target: below 35-40% during validation.
- `surface_rate`: share of all runs where output reaches chat or memo. Target: much lower than trigger rate.
- `material_change_rate`: share of triggered runs with a concrete plan change.
- `grounded_or_plausible_surface_rate`: surfaced outputs classified as grounded or plausible. Target: near 100%.
- `speculative_surface_rate`: surfaced outputs classified as speculative. Target: 0.
- `duplicate_rate`: outputs that merely repeat Structural Coverage or existing pressure-check content. Target: low.
- `word_cost`: extra user-facing words. Target: 80-140 words when surfaced.
- `silent_failure_rate`: triggered checks that fail without run-health visibility. Target: 0.

Kill or demote the feature if:

- It mostly says "consider their perspective".
- It frequently invents emotions, desires, or intentions.
- It duplicates existing pressure-check output without changing the plan.
- It triggers on most interpersonal cases.
- It creates more visible prose than useful correction.

## Phase 0: Close The Research Spike

**Goal**: make the current spike inspectable before anyone treats it as doctrine.

### What to build

Add a `STATUS.md` to `research/spikes/tom-evidence-study-2026-04-29/` that records:

- what the spike tested
- what the prototype does and does not do
- known failure: role/closeness can over-infer what a stakeholder knows
- recommendation: graduate only as a Stakeholder Assumption Check, not as a full ToM lane
- current evidence status: insufficient for production

Also add a short note to the prototype README that the missing `STATUS.md` was resolved and the prototype output should not be used as a prompt contract.

### Acceptance criteria

- [ ] `STATUS.md` exists and marks the spike experimental.
- [ ] It names the over-inference risk from the Marcus/Jake/Lina prototype output.
- [ ] It explicitly rejects visible stakeholder emotion cards.
- [ ] No production docs cite the spike as doctrine.

## Phase 1: Build The Offline Annotation Pack

**Goal**: establish whether the lens catches real misses before writing runtime code.

### What to build

Create `research/spikes/tom-evidence-study-2026-04-29/02-annotations/` fixtures for 8-12 archived cases.

Each fixture should label:

- case id and archived run path
- critical actors
- actor power or dependency
- advice assumption
- what the actor knows, might know, and does not know
- whether the assumption was grounded, plausible, or speculative
- what changes if the assumption is wrong
- whether current Lolla already caught it
- whether the stakeholder check would add a non-duplicative correction

Use positive and negative controls:

- positive: Mother/ex, whistleblower/wife, PhD/advisor/Silva PI, Marcus/Marcus/Jake/Lina
- negative: cases with third parties that do not materially affect the recommendation
- edge: short/thin case where the checker should skip rather than speculate

### Acceptance criteria

- [ ] At least 8 cases annotated.
- [ ] At least 2 negative controls included.
- [ ] Every positive annotation names a concrete `plan_change`.
- [ ] Every speculative item is marked and prohibited from surface output.
- [ ] Annotation format can be parsed by a simple test harness.

## Phase 2: Implement The Trigger Harness Offline

**Goal**: tune trigger discipline without touching `/lolla` runtime behavior.

### What to build

Create an offline harness that reads archived `conversation.txt`, `extraction.json`, and `result.json`, then emits:

- `triggered`
- `trigger_reason`
- `skip_reason`
- `candidate_actors`
- `candidate_assumptions`

The first trigger implementation can be a conservative rules-plus-LLM hybrid:

- deterministic prefilter from structural coverage dimensions, dropped threads, live constraints, and recommendation language
- LLM classifier only when the deterministic prefilter finds a stakeholder-shaped dependency

### Acceptance criteria

- [ ] Harness skips negative controls.
- [ ] Harness triggers on known positive controls.
- [ ] Trigger rate on archived validation set stays below 40%.
- [ ] Every trigger includes a reason tied to a plan dependency, not merely "third party exists".
- [ ] Test output is saved under the spike folder, not wired into production.

## Phase 3: Implement The Offline Checker Prototype

**Goal**: replace the broad ToM prototype with the narrow assumption-audit shape.

### What to build

Create an offline checker that runs Stage A and Stage B using the contracts above.

Differences from `scripts/spikes/tom_perspective_probe.py`:

- no `emotions` list
- no `desires` list by default
- no numeric confidence
- no broad `predicted_reaction_to_advice`
- no assumption may surface without a `plan_change`
- role/closeness inferences are `plausible`, never `grounded`

### Acceptance criteria

- [ ] Outputs match the new compact schema.
- [ ] Marcus/Jake/Lina style closeness inferences are not marked grounded.
- [ ] Negative controls produce `surface: false`.
- [ ] Positive controls produce at most 1-2 surfaced assumptions per run.
- [ ] The checker can run on archived cases without modifying result JSON.

## Phase 4: Score The Checker Against Annotations

**Goal**: decide whether runtime integration is justified.

### What to build

Add a scoring script that compares checker outputs with the Phase 1 annotation pack.

Track:

- trigger precision and recall
- actor match
- assumption match
- plan-change match
- duplicate vs new correction
- speculative surface violations
- word-cost estimate

### Acceptance criteria

- [ ] Speculative surface violations are zero on the annotation set.
- [ ] Negative controls remain silent.
- [ ] At least 60% of positive cases produce a useful non-duplicative correction, or the plan is revised before runtime integration.
- [ ] Duplicate rate is low enough that this is not just Structural Coverage repeated in softer language.

## Phase 5: Add Runtime Field Behind A Flag

**Goal**: make `/lolla` able to compute the check without changing chat or memo output.

### What to build

Add an opt-in runtime flag such as `LOLLA_STAKEHOLDER_CHECK=1`.

When enabled:

- run the trigger after audit cards exist
- run the checker only when triggered
- persist output under `stakeholder_assumption_check`
- add usage telemetry for any model calls
- add run-health issue if the checker was triggered and failed

When disabled:

- result JSON shape remains backward compatible
- no extra model call occurs
- no chat, memo, or Observatory behavior changes

### Acceptance criteria

- [ ] Default `/lolla` behavior is unchanged.
- [ ] Flagged runs persist `stakeholder_assumption_check`.
- [ ] Triggered failures appear in `run_health.issues`.
- [ ] Usage summary includes checker calls.
- [ ] Unit tests cover disabled, skipped, completed, and error states.

## Phase 6: Add Observatory Inspection

**Goal**: expose the ledger for debugging without changing the live user surface.

### What to build

Add an Observatory panel that appears only when `stakeholder_assumption_check.status` is `completed` or `skipped_error`.

Show:

- trigger reason
- actor
- power/dependency
- advice assumption
- grounding tier
- known/unknown split
- bridging facts
- risk if wrong
- plan change
- open question

Do not show emotion, desire, or intention sections.

### Acceptance criteria

- [ ] Panel is absent when checker is skipped.
- [ ] Panel appears for completed checks.
- [ ] Error state is visible when triggered checker fails.
- [ ] No internal prompt text appears in Observatory.
- [ ] Existing Observatory tests still pass.

## Phase 7: Feed The Check Into Pressure-Check Synthesis

**Goal**: let the user benefit from the check only when it changes advice.

### What to build

Update Step 8 pressure-check instructions so the orchestrator asks:

1. Did the stakeholder check identify an assumption Step 6 relied on?
2. Is the assumption grounded, plausible, or speculative?
3. Does the risk-if-wrong require a different action, sequence, threshold, question, or communication boundary?

Surface only if the answer to 3 is yes and the assumption is not speculative.

### Acceptance criteria

- [ ] No new chat heading is introduced.
- [ ] Surfaced text appears only inside `### Pressure Check`.
- [ ] Surfaced text names the plan change, not the checker.
- [ ] Rendered chat does not include "Theory of Mind", "stakeholder assumption check", "checker", "lane", or other machinery.
- [ ] If no material plan change exists, chat remains unchanged.

## Phase 8: Memo Integration

**Goal**: preserve useful stakeholder corrections in the portable memo without adding a new memo category.

### What to build

Update memo guidance so stakeholder-check material may be included only when it was surfaced in Step 8 or materially changes the decision note.

Preferred placement:

- `memo_pressure_check` when it is a late divergence
- `memo_what_changed` when it changes the core revised advice

Do not add a new `Stakeholder Perspective` memo section in the first release.

### Acceptance criteria

- [ ] Memo first screen still answers what changed in the advice.
- [ ] No process language appears in the memo note layer.
- [ ] Stakeholder material is compressed to the plan change.
- [ ] Renderer tests cover presence and absence.

## Phase 9: Validation Runs

**Goal**: prove the feature is useful and quiet on real `/lolla` runs.

### What to run

Run at least 6 validation cases with the flag enabled:

- Mother case
- Whistleblower case
- PhD case
- Marcus case
- one short/thin case
- one third-party-present negative control

For each run, inspect:

- chat output
- memo
- Observatory panel
- result JSON
- run health
- usage summary
- archive artifacts

### Acceptance criteria

- [ ] No scaffolding leak in chat.
- [ ] No speculative stakeholder psychology in chat or memo.
- [ ] At least 2 cases produce a materially useful plan change.
- [ ] At least 1 case correctly skips despite named third parties.
- [ ] Run-health captures checker errors if any occur.
- [ ] Cost increase is acceptable for triggered-only behavior.

## Phase 10: Graduation Decision

**Goal**: decide whether to merge, revise, or abandon.

### PASS

Merge if:

- validation shows plan-changing corrections in multiple cases
- surface output remains rare and compact
- speculative surface rate is zero
- negative controls skip
- no major chat or memo quality regression appears

### REVISE

Revise if:

- trigger rate is too high
- output duplicates existing pressure-check behavior
- Observatory is useful but chat output is noisy
- the checker needs a narrower actor selector

### BLOCK

Do not merge if:

- the feature invents mental states
- speculative claims reach user-facing output
- the checker mostly produces generic "consider their perspective" advice
- it adds visible ceremony without changing recommendations

## Likely File Touch Points

Research and planning:

- `research/spikes/tom-evidence-study-2026-04-29/STATUS.md`
- `research/spikes/tom-evidence-study-2026-04-29/02-annotations/*.json`
- `plans/stakeholder-assumption-check-2026-05-04.md`

Reference docs:

- `references/stakeholder-assumption-check.md` (new)
- `references/sub-agent-prompts.md`
- `references/chat-output-format.md`
- `references/memo-output-format.md`
- `SKILL.md`

Runtime:

- `scripts/run_pipeline.py`
- possible new module under `engine/system_b/` for trigger/checker logic
- `scripts/render_memo.py`
- `observatory/render_schema.json`
- `observatory/serve_result.py`

Tests:

- trigger/checker unit tests
- run-pipeline contract tests
- render-memo tests
- Observatory panel tests
- regression tests for no chat/memo machinery leak

## First Implementation Slice

The first real PR should not touch runtime behavior.

Build only:

1. `STATUS.md`
2. annotation schema
3. 4 annotated cases
4. offline trigger harness
5. scoring skeleton

That slice answers the only question that matters before code integration:

Does this lens find plan-changing stakeholder assumptions that Lolla does not already catch, while staying quiet on cases where it should stay quiet?
