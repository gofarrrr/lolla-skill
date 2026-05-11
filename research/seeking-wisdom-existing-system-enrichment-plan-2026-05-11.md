# Seeking Wisdom Existing-System Enrichment Plan

Date: 2026-05-11

## Correction

The first Bevelin/Lane 1 PR direction was wrong in an important way.

I treated `Seeking Wisdom` as something that could be judged with a new
deterministic audit surface. That conflicts with how Lolla actually works.
`HOW_IT_WORKS.md` is explicit:

- LLMs do the cognitively heavy semantic work: Pass 1 tendency triage, Pass 2
  deep checks, Lane 2 fingerprint/verification, Lane 3 frame extraction and
  reframing, Lane 4 classification/coverage/question generation, and Step 6
  private consideration.
- Embeddings are probabilistic support: Swiss-cheese tendency recall,
  activation-condition tiebreakers, companion recall, and V60 candidate recall.
- The deterministic middle owns custody, routing, traceability, caps, graph
  traversal, explicit artifact lookup, ledger validation, and product-output
  hygiene.
- The knowledge substrate is where durable deterministic value lives: canonical
  markdown articles, curated wave JSON, V60 affordance/absence records,
  compiled graphs, and precomputed embeddings.

So Bevelin should not become a new lane, a new review layer, or a lexical
scoring system. The right question is:

> Does `Seeking Wisdom` improve the source-backed knowledge that the existing
> LLM and embedding stages already use?

If it helps, it should improve the current substrate, prompts, and compiled
artifacts. It should not multiply architecture.

## Source Lineage

`Lolla-system-b` remains the source lineage for Lane 1:

- `munger_structural_mapping.md`
- `The_Psychology_of_Human_Misjudgment.md`
- canonical mental-model markdown files
- Munger tendency to model bindings
- the original structural-pressure engine

`lolla-skill` is the live system:

- conversation-native `ConversationContext`;
- provenance-bearing `ConversationIR`;
- lane packets;
- four independent lanes;
- V60 private enrichment;
- Step 6 consideration ledger;
- product-output hygiene;
- archived run comparison and Observatory traces.

`Peter Bevelin - Seeking Wisdom.md` should be treated as another source in the
same curation tradition, not as a replacement ontology.

## What Bevelin Can Add

Munger names the failure mode. The model corpus supplies corrective repertoire.
Bevelin can sharpen the operational tests that make a detected tendency
material.

Useful Bevelin-shaped questions are mostly of this kind:

- What evidence would prove this wrong?
- What reference class or denominator should govern the claim?
- Who benefits, who pays, and who bears the consequence?
- What threshold would change the decision?
- What is the downside if wrong, and how reversible is the move?
- What alternatives remain live?
- What state of mind is driving closure?
- Would the proposed system look fair if roles were reversed?
- What should be recorded now so the decision can teach us later?

Those are not a new lane. They are better activation contexts, treatment
requirements, diagnostic questions, absence blockers, and materiality tests for
the existing substrate.

## Correct Architectural Placement

### Lane 1

Lane 1 already uses LLMs for the hard work:

- Pass 1 family-clustered triage reads the conversation transaction.
- Embeddings add candidate tendencies without gating the LLM.
- Pass 2 deep checks one tendency in isolation.
- Subpattern menus guide the LLM toward the best route hint.
- Routing and DeltaCard assembly stay deterministic.

Bevelin belongs here only as sharper source-backed guidance inside existing
Munger tendencies and subpatterns, for example:

- `overoptimism-tendency / missing-denominator`: representative evidence,
  denominator, base-rate, failure distribution.
- `reason-respecting-tendency`: fake explanations vs causal evidence and
  disconfirmation.
- `inconsistency-avoidance-tendency`: reversal conditions, written
  falsification checks, predecision commitments.
- `contrast-misreaction-tendency`: absolute yardstick after removing the
  comparison frame.
- `kantian-fairness-tendency`: role reversal and system-level fairness.
- `reward-and-punishment-superresponse-tendency`: actor incentives and who
  bears consequences.
- `use-it-or-lose-it-tendency`: postmortem trace, feedback, and learning loop.

The test is not "does a lexical audit find those words?" The test is whether
the Pass 1/Pass 2 LLMs make better semantic judgments after the source-backed
guidance is incorporated.

### V60 Private Enrichment

V60 is probably the best first runtime target because it is already a
source-backed transaction layer:

- explicit `affordances_v60.json`;
- affordance and absence chunks;
- optional embedding recall;
- deterministic custody and caps;
- Step 6 private consideration by Claude/Codex;
- ledger validation of every selected chunk.

Bevelin can enrich V60 records as:

- new treatment requirements;
- sharper diagnostic questions;
- absence blockers that prevent tempting overclaims;
- source evidence for existing affordances;
- candidate chunks for models such as `falsifiability`, `premortem`,
  `base-rates`, `incentives`, `opportunity-cost`, `feedback-loops`,
  `principal-agent-problem`, `decision-trees`, and `false-precision-avoidance`.

This keeps the architecture intact: the deterministic layer selects and
preserves custody; the LLM decides whether the chunk matters in Step 6; the
ledger records use/reject/defer/private guardrail.

### Embeddings

Bevelin should not create a separate retrieval path.

If Bevelin records enter the substrate, the existing embedding mechanisms pick
them up through the normal compiled artifacts:

- tendency guidance vectors;
- activation-condition embeddings for near-tie tiebreaking;
- companion/V60 embedding recall;
- source-backed chunks in the affordance substrate.

The invariant remains: embeddings add candidates; they do not remove LLM or
lane-selected candidates.

### Product Surface

Bevelin should not appear as a product label.

The user should see better pressure:

- a clearer evidence gate;
- a sharper disconfirmation question;
- a real threshold;
- a preserved alternative;
- a role-reversal fairness check;
- a learning/postmortem trace.

The Observatory can show the source-backed substrate lineage. The chat and memo
should remain product-clean.

## What Not To Build

Do not build:

- a Bevelin lane;
- a Bevelin card;
- a lexical Bevelin score;
- a separate Bevelin review layer;
- a prompt bulk-insert of checklist language into every Pass 1/Pass 2 call;
- product prose that says "Bevelin says..." or exposes the new source as a
  user-facing taxonomy.

Those moves multiply architecture and risk checklist bloat.

## Correct Test

The right local test is an A/B substrate test through the existing pipeline.

### Baseline

Use archived conversations and current `origin/main` behavior:

- existing Pass 1/Pass 2 prompts;
- existing `subpattern_catalog.json`;
- existing `affordances_v60.json`;
- current embeddings and V60 behavior.

### Candidate Enrichment

Create a Bevelin-enriched candidate artifact set:

- source-backed additions to existing subpatterns;
- source-backed additions to existing V60 affordance/absence records;
- possibly a small number of new V60 affordance/absence records when no current
  record owns the Bevelin pressure cleanly;
- no new runtime layer.

The candidate set should be explicit and reviewable, not discovered by globbing
or "latest" selection.

### Replay

Run the same archived cases through baseline and candidate artifacts, then
compare with existing system tools:

- detection funnel: Pass 1 triggered, Pass 2 detected, routed, DeltaCard count;
- V60 telemetry: selected chunk count, selected model IDs, effect types;
- Step 6 ledger: used/rejected/deferred/private guardrail;
- product output: what changed, what stayed, product hygiene;
- archived-run comparison: eligibility before answer diff;
- stability harness where repeated runs are needed.

### What Counts As A Win

A Bevelin enrichment is useful if it improves the current system in one of
these ways:

1. **Better LLM detection:** Pass 1/Pass 2 catches a material tendency-shaped
   omission, missed challenge, or uncritical acceptance that the baseline
   missed, without broad overfire.
2. **Better route hint:** Pass 2 selects a more precise subpattern or model
   route because the source-backed activation context is sharper.
3. **Better private reasoning transport:** V60 selects a Bevelin-enriched
   affordance/absence chunk, Step 6 uses it or keeps it as a private guardrail,
   and the ledger explains the disposition.
4. **Better product delta:** the final answer adds a materially useful
   threshold, evidence gate, disconfirmation test, role-reversal check, or
   learning trace that baseline omitted.
5. **No product/system damage:** no extra findings for their own sake, no
   checklist theater, no internal source leakage, no memo bloat, no degraded
   run health.

### What Does Not Count

Not a win:

- a deterministic text match says the concept was "present";
- the candidate chunk was selected but rejected as irrelevant;
- the final answer mentions a broad checklist item without changing the
  decision pressure;
- Lane 1 fires more often but with lower precision;
- the output gets longer without adding a real action delta.

## Candidate Enrichment Targets

These are hypotheses for curation, not approved records.

### Highest-Priority Targets

1. **Disconfirmation / Falsification**
   - Existing homes: `falsifiability`, `premortem`, `inversion`,
     `scientific-method-evidence-testing`, `critical-thinking`.
   - Likely tendencies: `overoptimism-tendency`,
     `reason-respecting-tendency`, `inconsistency-avoidance-tendency`,
     `simple-pain-avoiding-psychological-denial-tendency`.
   - Desired pressure: "what evidence would make this conclusion false?"

2. **Role Reversal / System Fairness**
   - Existing homes: `principal-agent-problem`, `power-dynamics`,
     `boundaries`, `obligations-controls-mapping`,
     `psychological-safety`, `systems-thinking`.
   - Likely tendencies: `kantian-fairness-tendency`,
     `reciprocation-tendency`, `reward-and-punishment-superresponse-tendency`,
     `authority-misinfluence-tendency`.
   - Desired pressure: "would this rule still be fair and controllable if roles
     were reversed?"

3. **Postmortem / Learning Trace**
   - Existing homes: `feedback-loops`, `auditability-traceability`,
     `hindsight-bias`, `iteration`, `lean-startup-methodology`,
     `adaptation`.
   - Likely tendencies: `use-it-or-lose-it-tendency`,
     `inconsistency-avoidance-tendency`, `overoptimism-tendency`.
   - Desired pressure: "what should be recorded before the decision so later
     feedback can improve the model?"

4. **Absolute Yardstick**
   - Existing homes: `metrics`, `goal-setting`,
     `baseline-establishment`, `false-precision-avoidance`,
     `multi-criteria-decision-analysis`.
   - Likely tendencies: `contrast-misreaction-tendency`,
     `overoptimism-tendency`, `reason-respecting-tendency`.
   - Desired pressure: "what threshold governs the choice when the comparison
     frame is removed?"

### Lower-Priority Targets

These are already strongly represented in the current system and should only
be touched if review shows quality problems rather than presence problems:

- downside/reversibility;
- alternatives/opportunity cost;
- representative evidence/base rates;
- actor incentives.

## First Practical PR Shape

The next implementation PR should not add a new runtime layer.

It should do one narrow substrate experiment:

1. Choose 2-3 high-priority Bevelin targets.
2. Add source-backed candidate records to the existing V60 affordance/absence
   substrate or subpattern catalog.
3. Compile or point the pipeline to the candidate artifact explicitly.
4. Replay a small archived case set against baseline and candidate artifacts.
5. Compare with existing run-health, V60 ledger, product-output, and
   downstream-influence surfaces.

Only after that should we decide whether Bevelin is:

- redundant in a given region;
- useful only as V60 private enrichment;
- useful as sharper Lane 1 subpattern materiality;
- useful as embedding-recall source material;
- too broad/checklist-like to promote.

## Current Conclusion

Bevelin is probably useful, but not as a system.

It is potentially useful as source material that sharpens the existing
knowledge substrate. The test must run through Lolla's actual cognitive paths:
LLM detection, embedding recall, deterministic custody, V60 private
consideration, and product-clean Step 6 revision.

The central question is not:

> Can we detect Bevelin concepts in past outputs?

The central question is:

> When Bevelin is incorporated into the existing substrate, do the existing
> LLM/embedding stages select, reason with, and account for that knowledge in a
> way that creates better structural pressure without adding noise?
