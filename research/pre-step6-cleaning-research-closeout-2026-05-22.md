# Pre-Step-6 Cleaning Research Closeout

Date: 2026-05-22

Status: research phase closed for this chapter.

Runtime remains dormant. `SKILL.md` remains unchanged.

## The Big Picture

We started with a bloat problem.

The system could produce many engineered artifacts, but Step 6 was at risk of
receiving either too much undifferentiated material or material that had already
been narrowed too early by deterministic code. The goal was never to make code
think for Step 6. The goal was to make Step 6's thinking table better:

```text
wide enough to preserve edge
clean enough to reduce bloat
structured enough to be considered
auditable enough that humans can learn from it
```

The program now has a clean architecture statement:

```text
Deterministic system: selects, validates, records, preserves custody.
Cognitive system: Step 6 and human review decide what matters.
Cleaning system: uses evidence to improve the context Step 6 receives.
```

The product is not a permanent card deck. The product is evidence-guided
context engineering.

## What We Built

The research track produced four kinds of artifacts:

1. Custody and safety contracts

These include cached-card contracts, private-card interface, unified ledger
shape, payload-omission tripwires, visibility-policy prototypes, answer-delta
specificity, and model-commitment notes.

Their purpose is not cognition. Their purpose is to keep evidence legible and
prevent silent promotion.

2. Probe and calibration evidence

The program tested both failure directions:

```text
false stand-down: useful deck pressure hidden by anchor bias
false positive: deck pressure surfaced when anchor should have stayed visible
```

It also tested Step 6 stability, model-family stability, structural-delta
vocabulary, V60 interaction, Consultant ambiguity, and PhD variance.

3. Cleaning-lane slices

The final research turn moved attention from accounting to cleaning:

```text
consultant_cleaning_variant_replay_v0
consultant_anchor_boundary_patch_probe_v0
phd_kimi_variance_cleaning_review_v0
evidence_surface_v0
```

These slices tested whether a cleaner private table improves Step 6's cognition
without adding gates.

4. Evidence surface

The minimum evidence surface now exists:

```text
research/pre-step6-cleaning-evidence-surface/cleaning-evidence-surface.v1.json
research/pre-step6-cleaning-evidence-surface/cleaning-evidence-surface.md
```

It aggregates pressure-atom recurrence for humans. It does not graduate cards.
It does not change runtime. It encodes:

```text
code_may_nominate = true
humans_decide = true
automatic_graduation_allowed = false
runtime_visibility_change_allowed = false
```

## What We Learned

### 1. Atomic cards can clean the table

Consultant and PhD both improved in legibility when broad lens pressure was
decomposed into concrete pressure atoms.

This does not mean every card should be atomic. Bundles can preserve coherence
when their elements reinforce each other. Atoms help when a broad bundle hides
several separable structural moves and Step 6 needs to discriminate.

### 2. Consultant produced a graduation candidate

Consultant's recurring useful atom was:

```text
keep the first moves reversible until counsel guides the next action
```

Evidence:

```text
4/6 additive before anchor patch
1/6 additive after patched anchor
protected payload preserved 6/6
```

Interpretation:

```text
graduation_candidate, human_review_required
```

This does not authorize a per-case patch layer. It authorizes a human upstream
origin investigation:

```text
Why did original anchor synthesis compress this into generic reversibility
instead of preserving the counsel-gated terminal condition?
```

### 3. PhD generalized the atomic-card idea differently

PhD V60-off used four atomic cards:

```text
bounded_probe_not_commitment_card = 4/6 additive
single_cell_collaborator_feasibility_card = 2/6 additive
fallback_reentry_readiness_card = 1/6 additive
visible_stop_date_conditions_card = 3/6 additive
```

Protected payload was preserved in 6/6 samples.

Interpretation:

```text
distributed_atomic_discrimination
watch_not_graduate
```

PhD did not produce a single graduation candidate. The useful pressure is real,
but distributed. That means the deck is still diagnostic for PhD rather than
ready to migrate upstream as one clean atom.

### 4. V60 produced a separate finding

Founder V60-on instability is a V60/private-context issue, not a pre-Step-6
portfolio issue.

Recorded finding:

```text
research/pre-step6-founder-v60-private-context-audit-readout-2026-05-22.md
```

Read:

```text
v60_context_related_but_destabilizing
```

Recommended handoff:

```text
Run a separate V60 selection / packet-presentation audit for Founder-shaped
cases. Do not absorb that work into pre-Step-6 portfolio policy.
```

### 5. Model commitment includes call configuration

The PhD cleaning slice initially hung under Kimi through OpenRouter. The slice
completed after adding an opt-in research-script setting:

```text
LOLLA_OPENROUTER_DISABLE_REASONING=1
```

This reinforces an earlier lesson:

```text
model commitment = model family + provider + backend behavior + prompt contract + call configuration
```

Any model/provider/backend/call-config change is a recalibration event.

## What Must Not Be Automated

Do not automate these decisions:

```text
card graduation
upstream migration
lens relevance
model selection as a proxy for correctness
visibility based only on recurrence
borderline-case suppression as a wisdom answer
```

Allowed:

```text
Code records.
Code validates custody.
Code aggregates evidence.
Code nominates candidates.
Humans interpret.
Humans decide curation.
Code implements decided curation.
```

This is the line that keeps the deterministic system from becoming the
cognitive brain.

## Shadow Implementation Definition

If the board chooses to start a separate shadow implementation phase, the scope
should mean exactly this:

```text
The visibility resolver and card-deck assembly run in production-adjacent code
paths behind a dormant flag. The unified ledger, answer_delta checks, payload
omission records, custody validation, and evidence-surface records are written
to result/archive artifacts. Observatory gains read-only views. The user-facing
answer remains exactly the current Step 6 output. No visibility decision changes
what the user sees.
```

Flag shape:

```text
LOLLA_STEP6_PORTFOLIO=off|shadow|on
default = off
```

This closeout does not recommend turning `on`.

## Precommitted Decision Criteria

Shadow implementation is justified only if all four conditions hold:

```text
1. Consultant produced an interpretable result.
2. PhD produced an interpretable result.
3. Evidence surface exists in a form humans can read.
4. The closeout can honestly say the system is understood well enough to run
   dormant in production-adjacent paths without changing visible output.
```

Read:

```text
1. yes
2. yes
3. yes
4. yes, for dormant shadow only
```

Decision:

```text
The research chapter can stop.
Dormant shadow implementation is allowed as a separate next program.
Runtime-on promotion is not allowed.
SKILL.md behavior change is not allowed.
More probe-shaped research is not needed before closeout.
```

## What "Call It A Day" Means

We can call this research chapter done now.

Done does not mean the system is ready to visibly change user answers. It means
we understand the design well enough to stop refining it in research loops.

The next move is a product/engineering choice, not another proof:

```text
Option A: start a separate dormant-shadow implementation program.
Option B: park the research, keep runtime unchanged, and use the closeout as the
         handoff for a later implementation window.
```

Both are valid. What we should not do is continue generating one more clever
probe to avoid making that choice.

## Final Principles

These are the load-bearing principles that survived the research phase:

```text
1. The system learns by making the thinking table better.
2. Code may nominate; humans decide.
3. Cards are diagnostic instruments, not permanent answer engines.
4. Pressure atoms graduate upstream only through human curation.
5. Runtime waits.
```

Closeout read:

```text
research_phase = complete
runtime_promotion = blocked
skill_update = blocked
shadow_implementation = allowed_as_separate_program
next_research_probe = not_recommended
```

