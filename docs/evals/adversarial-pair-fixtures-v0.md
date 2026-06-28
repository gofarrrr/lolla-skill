# Adversarial Pair Fixtures v0

Status: seed fixture set
Date: 2026-06-27
Review slice: `adversarial_pair_fixtures_v0`

This note turns PR30's six human-reviewed complex runs and PR31's actionable
delta rubric into the first adversarial pair fixture set.

The purpose is narrow. PR32 does not implement a judge, run a judge, score
answers, call models, run `$lolla`, change runtime behavior, change prompts,
change `SKILL.md`, mutate archived runs, or automatically label corpus
records. It creates fixture definitions that a future human reviewer or
calibrated judge can be tested against later.

The fixture question:

```text
Can the evaluator prefer the answer pattern with the stronger actionable delta,
even when the competing answer pattern is smoother, longer, warmer, more
balanced, or more familiar?
```

## Sources

This fixture set is grounded in:

- [Complex Baseline Human Review v0](complex-baseline-human-review-v0.md)
- [Actionable Delta Rubric v0](actionable-delta-rubric-v0.md)
- `reviews/human/complex-baseline-v0/review.json`

The fixtures use only compact paraphrased answer patterns. They do not include
raw transcript text, raw memo text, raw revised-answer text, raw model/provider
messages, private reasoning details, secrets, credentials, local absolute
paths, or archive contents.

## Fixture Set

| fixture id | source case | judge trap | PR31 labels | expected winner |
|---|---|---|---|---|
| `apf_v0_001_cofounder_authority_transfer` | `ceo-remove-founding-cofounder` | founder loyalty / cooperation reset versus authority transfer | `action_changed`, `sequence_changed`, `stop_rule_added` | `revised_answer` |
| `apf_v0_002_career_written_terms` | `accept-operations-role-startup` | emotional identity clarity versus written operating terms | `written_term_added`, `evidence_gate_added`, `user_question_added` | `revised_answer` |
| `apf_v0_003_enterprise_buyer_proof` | `launch-public-enterprise-beta` | marquee customer aura versus buyer-behavior proof | `evidence_gate_added`, `scope_narrowed`, `threshold_changed` | `revised_answer` |
| `apf_v0_004_consulting_scoped_pilot` | `pre-sell-undefined-consulting` | polish/status interpretation versus client-ready scoped pilot | `overclaim_retracted`, `scope_narrowed`, `action_changed` | `revised_answer` |
| `apf_v0_005_pivot_capacity_gate` | `pivot-company-product-strategy` | market excitement versus capacity and current-obligation gate | `sequence_changed`, `evidence_gate_added`, `threshold_changed` | `revised_answer` |
| `apf_v0_006_clinic_operable_controls` | `deploy-assisted-intake-routing` | long checklist safety theater versus operable controls | `scope_narrowed`, `stop_rule_added`, `action_changed` | `revised_answer` |

These are seed fixtures, not benchmark claims. Six fixtures are enough to test
whether the fixture format is useful; they are not enough to calibrate a judge.

## Fixture Details

### `apf_v0_001_cofounder_authority_transfer`

Source:

- case: `ceo-remove-founding-cofounder`
- run: `20260627T093131Z_59d153`

Fixture type: `founder_loyalty_vs_authority_transfer`

Rubric labels:

- `action_changed`
- `sequence_changed`
- `stop_rule_added`

Original answer pattern summary: a smoother cooperation-reset pattern that
prioritizes loyalty, trust repair, and a staged conversation while leaving real
authority movement ambiguous.

Revised answer pattern summary: an authority-transfer pattern that moves
decision rights first, permits only a bounded transition role, and adds
stop-loss rules.

Why the revised answer should win: the revised pattern changes the operating
decision. It prevents a loyalty-preserving conversation from becoming a way to
avoid moving authority.

Judge trap: smoothness bias plus authority/loyalty ambiguity bias.

Evidence required:

- artifact-supported authority ambiguity in the original decision shape;
- revised action that moves authority before testing cooperation;
- explicit condition or stop rule for the transition.

Invalid preference reason: preferring the smoother reset pattern is wrong if it
rewards relational polish while leaving the decision-rights problem unresolved.

### `apf_v0_002_career_written_terms`

Source:

- case: `accept-operations-role-startup`
- run: `20260627T132700Z_bae7f3`

Fixture type: `identity_clarity_vs_written_terms`

Rubric labels:

- `written_term_added`
- `evidence_gate_added`
- `user_question_added`

Original answer pattern summary: an emotionally resonant career-choice pattern
that weighs identity, aliveness, safety, and status without forcing either
option to prove operating authority.

Revised answer pattern summary: a terms-first pattern that requires both paths
to produce written operating terms under deadlines and treats household consent
as capacity evidence.

Why the revised answer should win: the revised pattern changes the decision
from "which story feels truer" to "which option can produce usable operating
conditions."

Judge trap: confidence/warmth bias plus generic balance bias.

Evidence required:

- artifact-supported ambiguity about both career options;
- written terms required from both options;
- stakeholder or household-capacity question that can change the choice.

Invalid preference reason: preferring the warmer identity pattern is wrong if
it lets either employer win through story, title, or emotional resonance rather
than operating proof.

### `apf_v0_003_enterprise_buyer_proof`

Source:

- case: `launch-public-enterprise-beta`
- run: `20260627T104146Z_7bfe79`

Fixture type: `marquee_aura_vs_buyer_proof`

Rubric labels:

- `evidence_gate_added`
- `scope_narrowed`
- `threshold_changed`

Original answer pattern summary: a polished enterprise-growth pattern that
lets the larger or more impressive prospect pull the launch narrative.

Revised answer pattern summary: a buyer-proof pattern that gives both
prospects the same paid pilot shape and assigns priority by payment,
procurement clarity, scope tolerance, and proof value.

Why the revised answer should win: the revised pattern blocks aura from acting
as evidence. It makes the bigger logo earn priority through buyer behavior.

Judge trap: status/aura bias plus market-excitement bias.

Evidence required:

- two candidate buyers or paths with different aura/proof profiles;
- same written paid pilot shape applied to both;
- thresholds for payment, procurement, support load, or scope tolerance.

Invalid preference reason: preferring the marquee-customer pattern is wrong if
it rewards perceived status while ignoring the proof needed to make the pilot
operable.

### `apf_v0_004_consulting_scoped_pilot`

Source:

- case: `pre-sell-undefined-consulting`
- run: `20260627T133637Z_cad396`

Fixture type: `status_read_vs_scoped_pilot`

Rubric labels:

- `overclaim_retracted`
- `scope_narrowed`
- `action_changed`

Original answer pattern summary: a skeptical anti-polish pattern that treats
professional presentation mainly as status avoidance or premature brand work.

Revised answer pattern summary: a scoped-pilot pattern that keeps one paid
pilot, allows only tiny presentation polish, and requires a client-ready offer
brief without letting polish define the offer.

Why the revised answer should win: the revised pattern retracts an overclean
status read while preserving the cash and scope discipline of the original
advice.

Judge trap: generic skepticism bias plus polish/status confusion.

Evidence required:

- trace-supported need for credibility with a real client;
- revised distinction between legitimate client readiness and scope inflation;
- preserved one-pilot constraint.

Invalid preference reason: preferring the anti-polish pattern is wrong if it
mistakes useful commercial credibility for status spending and weakens the
actual sale.

### `apf_v0_005_pivot_capacity_gate`

Source:

- case: `pivot-company-product-strategy`
- run: `20260627T110450Z_5d2da7`

Fixture type: `market_excitement_vs_capacity_gate`

Rubric labels:

- `sequence_changed`
- `evidence_gate_added`
- `threshold_changed`

Original answer pattern summary: a market-upside pattern that gives the
higher-ACV opportunity pride of place and treats market validation as the first
serious test.

Revised answer pattern summary: a capacity-first pattern that requires a
short capacity and current-obligation gate before market validation can consume
engineering capacity.

Why the revised answer should win: the revised pattern protects existing
obligations and team capacity before letting market excitement pull the company
into a larger pivot.

Judge trap: market-excitement bias plus higher-ACV bias.

Evidence required:

- existing customer or delivery obligation that would be harmed by the pivot;
- explicit capacity/obligation gate;
- sequencing that puts that gate before market validation.

Invalid preference reason: preferring the market-upside pattern is wrong if it
treats higher ACV as proof before checking whether the company can honor
current obligations.

### `apf_v0_006_clinic_operable_controls`

Source:

- case: `deploy-assisted-intake-routing`
- run: `20260627T130339Z_4cd3cb`

Fixture type: `checklist_theater_vs_operable_controls`

Rubric labels:

- `scope_narrowed`
- `stop_rule_added`
- `action_changed`

Original answer pattern summary: a long, safety-forward checklist pattern that
looks responsible but risks being too heavy for the operating team to use.

Revised answer pattern summary: an operable-controls pattern that narrows the
pilot, requires a backlog diagnosis, and defines must-pass controls plus
pause/rollback triggers.

Why the revised answer should win: the revised pattern makes safety usable
under pressure instead of rewarding the appearance of comprehensive governance.

Judge trap: length/comprehensiveness bias plus checklist theater bias.

Evidence required:

- operational burden or exhausted-admin context;
- revised controls that are fewer, concrete, and must-pass;
- diagnosis and rollback conditions tied to the launch decision.

Invalid preference reason: preferring the longer checklist is wrong if it
rewards apparent caution while making the controls less likely to be operated.

## Cross-Fixture Judge Traps

The fixture set is designed to expose these traps:

- smoothness bias;
- length/comprehensiveness bias;
- status/aura bias;
- checklist theater bias;
- generic balance bias;
- confidence/warmth bias;
- market-excitement bias;
- authority/loyalty ambiguity bias.

## How These Fixtures Should Be Used Later

Future PRs may turn these fixtures into pairwise review prompts or evaluation
records. A reviewer or future calibrated judge should be asked which answer
pattern should win and why. The expected winner is always `revised_answer`
because the revised pattern carries the stronger PR31 actionable delta.

Do not use these fixtures as an automated release gate yet. They are seed
fixtures for error analysis and future calibration. A future judge must first
prove it can prefer actionable deltas over smooth no-op prose on held-out,
human-reviewed examples.

PR33 now adds a broader human-review corpus batch:

`docs/evals/human-review-corpus-batch-v0.md`

That batch provides more human-owned examples for future fixtures, but it still
does not create calibration, benchmark claims, automatic scoring, or a judge.

## What This Does And Does Not Justify

This does justify:

- using the six PR30 cases as the first adversarial fixture seed set;
- testing future evaluators against smoothness/status/checklist/generic-balance
  traps;
- building later pairwise review prompts from this fixture schema;
- using PR31 labels as the reason the revised pattern should win.

This does not justify:

- a generic LLM judge;
- a calibrated judge yet;
- answer-quality scoring;
- automatic labels;
- runtime integration;
- prompt rewrite;
- `conversation_understanding_ir.v0`;
- graph DB, embeddings, chunking, or memory;
- agent approval.

## Review Receipt

- Six fixtures created, one per PR30 complex case.
- Each fixture cites PR31 rubric labels.
- Each fixture names the judge trap and expected winner.
- Fixture content is paraphrase-only.
- No raw transcript, memo, revised answer, model/provider content, private
  reasoning, secrets, credentials, or local absolute paths are included.
- No `$lolla` run.
- No model calls.
- No runtime files changed.
- No prompts changed.
- No `SKILL.md` changes.
- No judge implementation.
- No automatic labels.
- PR33 Human Review Corpus Batch v0 now broadens the human-reviewed seed.
- PR34 User Values / Priorities Signal v0 now designs the missing review
  surface.
- PR35 Live Output Hygiene Decision v0 now documents the live-output hygiene
  policy.
- PR36 Risk Mode Behavior Plan v0 now documents risk-mode review and reliance
  policy.
- PR37 Risk Mode Fixture Matrix v0 now documents risk-mode fixture examples.
- PR38 Risk Mode Fixture Review v0 now reviews those risk-mode fixtures and
  adds the missing high-stakes values/priorities conflict fixture.
- PR39 Risk Mode Implementation Plan v0 now plans high-stakes
  reliance/readiness tightening without implementation.
- PR40 Risk Mode Contract Lock Tests v0 now locks the current conservative
  risk-mode contract in tests.
- PR41 Risk Mode Evaluation Artifact Clarity v0 is the next evaluation slice.
