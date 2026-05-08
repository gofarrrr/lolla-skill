# PR28 Controlled Graph-Only Extraction Report

**Status:** controlled reviewed extraction quality loop, dormant/review-only

**Decision label:** `controlled_graph_only_extraction_batch_ready`

**Branch:** `feature/reasoning-substrate-pr28-controlled-graph-only-extraction`

## Purpose

PR28 is the first controlled extraction batch after PR27 proved that mixed
reasoning-substrate packets are useful but graph-only cards are thin.

This is not Batch 3b, not runtime promotion, not a live lane adapter, not prompt
work, and not user-facing Decision Pressure. The point is to read ten
repo-custodied graph-only sources, extract only source-supported operational
affordances, and preserve absences where the source does not support a tempting
field.

## Batch Shape

- Target runtime graph models: `10`
- Source-custodied source files used: `10`
- Models already present in v4: `0`
- New batch directory: `data/model_affordances/batch_4/`
- Batch records added: `10`
- Batch affordances added: `10`
- Batch absence records added: `20`
- Compiled artifact: `data/compiled/model_affordances/affordances_v5.json`
- Compiled artifact status: `draft_review_only`
- v5 compiled model records: `65`
- v5 compiled affordances: `101`
- v5 compiled absence records: `115`

## Target Selection

| model_id | why selected | source file | outcome | affordances | absences |
| --- | --- | --- | --- | ---: | ---: |
| `chain-of-verification` | PR27 graph-only useful-but-thin card | `Chain_Of_Verification_rag.md` | `strong_affordance_record` | 1 | 2 |
| `constraints` | PR27 graph-only useful-but-thin card | `Constraints_rag.md` | `strong_affordance_record` | 1 | 2 |
| `confirmation-bias` | PR27 graph-only useful-but-thin card | `Confirmation_Bias_rag.md` | `strong_affordance_record` | 1 | 2 |
| `step-back` | PR27 graph-only useful-but-thin card | `Step_Back_rag.md` | `strong_affordance_record` | 1 | 2 |
| `scientific-method-evidence-testing` | PR25/PR27 reasoning-gap adjacency | `Scientific_Method_Evidence_Testing_rag.md` | `strong_affordance_record` | 1 | 2 |
| `five-whys-method` | PR25 static lane priority and root-cause adjacency | `Five_Whys_Method_rag.md` | `strong_affordance_record` | 1 | 2 |
| `root-cause-analysis` | PR25 static lane priority and recurrence diagnosis adjacency | `Root_Cause_Analysis_rag.md` | `strong_affordance_record` | 1 | 2 |
| `first-principles-thinking` | PR25 static lane priority and reasoning-gap adjacency | `First_Principles_Thinking_rag.md` | `strong_affordance_record` | 1 | 2 |
| `intellectual-humility` | PR25 static lane priority and correction-gate adjacency | `Intellectual_Humility_rag.md` | `strong_affordance_record` | 1 | 2 |
| `authority-bias` | PR25 static lane priority and evidence-vs-status adjacency | `Authority_Bias_rag.md` | `strong_affordance_record` | 1 | 2 |

## Extraction Outcomes

`chain-of-verification` produced a make-or-break premise audit. Strong fields:
linked premises, auditable trail, evidence per link, verification theater guard.
Missing or weak fields: exhaustive sign-off and pure linear implementation were
recorded as absences.

`constraints` produced a scope-boundary decision filter. Strong fields: explicit
scope, exclusions, trade-offs, old-constraint checks, too-loose and too-tight
guards. Missing or weak fields: permanent rule compliance and elaborate control
systems were rejected.

`confirmation-bias` produced a disconfirming-evidence equality check. Strong
fields: missing denominator, sponsor-backed recommendation defense, first
falsifier, exception-trap guard. Missing or weak fields: blaming others for bias
and adding more favorable evidence were rejected.

`step-back` produced a reorientation-before-execution gate. Strong fields:
governing structure, one-day answer, problem-owner frame, bounded return to
action. Missing or weak fields: indefinite reflection and comprehensive research
before action were rejected.

`scientific-method-evidence-testing` produced a falsifiable hypothesis threshold
test. Strong fields: testable hypothesis, disconfirming evidence, analytical
thresholds, proxy validation, political hypothesis guard. Missing or weak fields:
politically protected hypotheses and convenient proxy shortcuts were rejected.

`five-whys-method` produced an evidence-bound causal chain drilldown. Strong
fields: observable causal chain, logs/process evidence, falsifiable fact,
actionable what/how. Missing or weak fields: emotional why-loops and single
linear causes for complex systems were rejected.

`root-cause-analysis` produced a machine-level recurrence diagnosis. Strong
fields: proximate/root distinction, case-at-hand vs machine-level change,
controllable levers, causal stack guard. Missing or weak fields: single tidy root
cause and diagnosis without machine change were rejected.

`first-principles-thinking` produced an elemental truth rebuild gate. Strong
fields: facts and desired outcome, convention stripping, "what would need to be
true", concrete action requirement. Missing or weak fields: ignoring constraints
and abstract truth without action were rejected.

`intellectual-humility` produced a corrigible confidence review. Strong fields:
confidence outrunning evidence, external critique, update condition, teacher vs
student vs peer. Missing or weak fields: performative self-minimization and
authority deference through humility were rejected.

`authority-bias` produced a domain-bound deference audit. Strong fields:
expertise, trustworthiness, domain fit, reasoning chain, override evidence,
status/idea separation. Missing or weak fields: blind credential deference and
assumed cross-domain expertise transfer were rejected.

## Corpus Signal

The ten source files were not too thin for reviewed extraction. Each supported
one compact operational affordance with exact source custody. The quality signal
is not "ten files filled"; it is that each file also produced absences that keep
the card honest.

The batch suggests the 167 source-custodied graph-only models are likely a mixed
set:

- Some will support one narrow reviewed affordance immediately.
- Some may be useful only as graph-only shelf hints until better source material
  exists.
- Some will overlap existing v4 records and should generate duplicate or
  do-not-promote absences rather than new cards.
- Some will be broad enough that packet usefulness should be tested before
  expanding extraction volume.

## Quality Gates Preserved

- Every semantic field is backed by exact source evidence.
- Every target model references a repo-custodied source file.
- No target model was already present in v4.
- Absence records are first-class and counted.
- v5 remains `draft_review_only`.
- v5 is not imported by live runtime paths.
- No prompts, lanes, live `/lolla`, Observatory, memo, Step 8, Step 6, Lane 4
  runtime, judges, model calls, or user-facing Decision Pressure surfaces were
  changed.

## Recommendation For PR29

PR29 should regenerate a tiny mixed reasoning-substrate packet fixture using v5
and compare it against PR27's mixed packet:

1. Keep the same explicit nominations where possible.
2. Confirm the four PR27 graph-only cards now show reviewed depth:
   `chain-of-verification`, `constraints`, `confirmation-bias`, `step-back`.
3. Add a few PR28-only cards to test adjacent reasoning usefulness:
   `scientific-method-evidence-testing`, `root-cause-analysis`,
   `authority-bias`, or `intellectual-humility`.
4. Review whether the packet is still compact, more useful, and still honest.
5. Do not start broad extraction until packet comparison shows which new depth
   actually improves the LLM handoff.

The next slice should be packet regeneration/comparison, not automatic scale-up.
