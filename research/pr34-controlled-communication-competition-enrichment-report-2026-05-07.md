# PR34 Controlled Communication And Competition Enrichment Report

**Status:** controlled reviewed enrichment quality loop, dormant/review-only

**Decision label:** `controlled_communication_competition_enrichment_ready`

**Branch:** `feature/reasoning-substrate-pr34-controlled-communication-competition-enrichment`

## Purpose

PR34 follows PR33's packet-usefulness review. PR33 showed that controlled
reviewed depth can improve the same packet handoff without increasing
candidate count or letting Python choose the answer. PR34 therefore takes one
more small, gap-driven enrichment step, focused on families that remained
useful and thin after v6:

- competitive interdependence: `nash-equilibrium`, `prisoners-dilemma`;
- communication and feedback: `active-listening`,
  `constructive-feedback-models`, `feedback-models-sbi`;
- analogical/adaptive reasoning: `analogies-and-metaphors`,
  `natural-selection-analogy`.

This is not broad Batch 3b, runtime promotion, a live lane adapter, prompt
work, receiver-side answer generation, or user-facing Decision Pressure. The
point is to read seven repo-custodied graph-only sources, extract only
source-supported operational depth, and preserve absence records where tempting
uses are unsupported.

## Batch Shape

- Target runtime graph models: `7`
- Source-custodied source files used: `7`
- Models already present in v6: `0`
- New batch directory: `data/model_affordances/batch_6/`
- Batch records added: `7`
- Batch affordances added: `7`
- Batch absence records added: `14`
- Compiled artifact: `data/compiled/model_affordances/affordances_v7.json`
- Compiled artifact status: `draft_review_only`
- v7 compiled model records: `88`
- v7 compiled affordances: `124`
- v7 compiled absence records: `161`
- Runtime graph models still graph-only after v7: `134`
- Source-evidence references in v7 records: `1542`
- Treatment requirements in v7 affordances: `231`
- Diagnostic questions in v7 affordances: `466`
- Misuse guards in v7 affordances: `441`

## Target Selection

| model_id | why selected | source file | outcome | affordances | absences |
| --- | --- | --- | --- | ---: | ---: |
| `nash-equilibrium` | PR33 remaining competitive dynamics gap | `Nash_Equilibrium_rag.md` | `strong_affordance_record` | 1 | 2 |
| `prisoners-dilemma` | PR33 remaining competitive/cooperation dynamics gap | `Prisoners_Dilemma_rag.md` | `strong_affordance_record` | 1 | 2 |
| `active-listening` | PR33 communication and feedback gap | `Active Listening_rag.md` | `strong_affordance_record` | 1 | 2 |
| `constructive-feedback-models` | PR33 communication and feedback gap | `Constructive_Feedback_Models_rag.md` | `strong_affordance_record` | 1 | 2 |
| `feedback-models-sbi` | PR33 communication and feedback gap | `Feedback_Models_Sbi_rag.md` | `strong_affordance_record` | 1 | 2 |
| `analogies-and-metaphors` | PR33 analogical reasoning gap | `Analogies_And_Metaphors_rag.md` | `strong_affordance_record` | 1 | 2 |
| `natural-selection-analogy` | PR33 analogical/adaptive reasoning gap | `Natural_Selection_Analogy_rag.md` | `strong_affordance_record` | 1 | 2 |

## Extraction Outcomes

`nash-equilibrium` produced a stable best-response map. Strong fields:
players, credible moves, payoff drivers, beliefs, reachability, and stability
versus desirability. Missing or weak fields: stable-outcome-as-good and pure
computable-equilibrium prediction were recorded as absences.

`prisoners-dilemma` produced a defection incentive reframe test. Strong fields:
individually sensible defection, collectively better cooperation, trust,
enforcement, repeated interaction, and game redesign. Missing or weak fields:
every-coordination-problem-is-betrayal and hostile-frame-default were rejected.

`active-listening` produced a hidden disagreement diagnostic loop. Strong
fields: visible versus real disagreement, factual/emotional content, local
knowledge, how-they-think questions, and confirmation before advice. Missing
or weak fields: performative listening and sweeping interpretation were
rejected.

`constructive-feedback-models` produced a specific standard correction card.
Strong fields: objective standard, specific deviation, accurate criticism,
cause/effect context, supportive timing, and actionable adjustment. Missing or
weak fields: rank-backed feedback and confirming-performance narratives were
rejected.

`feedback-models-sbi` produced a situation-impact-invitation structure. Strong
fields: concrete incident, observable behavior, impact, collaboration request,
and implications. Missing or weak fields: scripted judgment feedback and
selective situation framing were rejected.

`analogies-and-metaphors` produced a structural fit transfer test. Strong
fields: source analogy, target domain, shared mechanism, reference-class
assumptions, and analogy boundary. Missing or weak fields: analogy-as-proof and
map-substituting-for-territory were rejected.

`natural-selection-analogy` produced a variation-selection-retention loop.
Strong fields: variants, selection environment, fitness criteria, real feedback,
retention rules, and failure inspection. Missing or weak fields:
survival-proves-optimal-design and simplistic competition metaphor were
rejected.

## Corpus Lessons

The batch supports the next controlled enrichment step without expanding by
count momentum. All seven sources produced compact reviewed depth with exact
source custody and absence records. The strongest product value is in how the
records create useful tensions:

- `nash-equilibrium` and `prisoners-dilemma` help distinguish stable patterns,
  bad collective outcomes, and games that need redesign.
- `active-listening` and `prisoners-dilemma` create a useful packet tension:
  sometimes the answer should listen harder, and sometimes the incentive
  structure rewards concealment so listening alone is not enough.
- `constructive-feedback-models` and `feedback-models-sbi` split feedback depth
  into two levels: standard/process correction and concrete incident structure.
- `analogies-and-metaphors` and `natural-selection-analogy` add generation and
  adaptive reasoning while explicitly blocking analogy-as-proof and emergence
  theater.

The important lesson is still not "v7 is closer to complete." The lesson is
that targeted reviewed records can make specific packet families richer while
preserving overclaim boundaries.

## Non-Promotion Boundary

PR34 does not:

- run live `/lolla`;
- change prompts;
- rewrite lanes;
- build a live lane adapter;
- add runtime packet production;
- promote v7 into runtime;
- create user-facing Decision Pressure;
- wire Observatory, memo, Step 8, Step 6, or Lane 4 runtime;
- call models;
- run judges;
- broaden beyond the 7 target models;
- create Batch 3b;
- make Python choose final pressure.

## Recommendation For PR35

PR35 should probably be another packet-usefulness review, not another
extraction batch by default.

Recommended slice:

1. Create one review-only packet fixture that nominates PR34-upgraded models in
   a realistic communication/competition case.
2. Compare a v6-style packet against a v7 packet using the same nominations.
3. Render both with the PR30 reviewer-only renderer.
4. Judge whether `nash-equilibrium`, `prisoners-dilemma`, `active-listening`,
   `constructive-feedback-models`, `feedback-models-sbi`, and the analogy
   cards help a receiver decide what to use, merge, ignore, or set aside.

Only if PR35 finds that v7 improves handoff usefulness without creating
procedural or strategic clutter should another small controlled enrichment
batch begin. The next extraction batch should remain capability-gap driven,
not broad 222-model completion.
