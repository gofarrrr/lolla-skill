# R4 matched holdout v2 human semantic leakage review

Status: awaiting founder/PM human review before target authorship

Date prepared: 2026-07-14

Provider calls: 0

Provider cost: `$0.00`

## Why this gate exists

The rejected v1 evidence allowed a reader to copy parts of the expected Lolla
classification from source or prior wording. V2 may proceed to target
authorship only after a human confirms that the expected result must instead be
inferred from operational facts distributed across the conversation.

Deterministic vocabulary lint has passed with zero prohibited matches. That
check cannot decide whether ordinary prose still gives away the answer. The
human reviewer owns that judgment.

## Review standard

For each source and prior, confirm all five statements:

1. No experiment-specific ontology appears in the source or prior.
2. No assistant turn states the expected Lolla category or structured result.
3. The broad-anchor prior in Case 01 does not criticize or discount its own
   framing.
4. The final four messages alone are insufficient to determine both expected
   surfaces.
5. The source does not tell a future reader what to emit, suppress, or keep
   quiet.

If any statement is false, identify the case and passage. The source must be
revised and rehashed before a target exists.

## Case 01 — community audio archive

Experimental role: governed-pending restraint control with a broad ordinary-
language unresolved anchor in the prior.

- [Source](../../research/lolla-r4-matched-holdout-v2-source-freeze-2026-07-14/sources/r4h2-case01-community-audio-archive.json)
- [Prior](../../research/lolla-r4-matched-holdout-v2-source-freeze-2026-07-14/priors/r4h2-case01-community-audio-archive.json)

Preliminary CTO review:

- The prior says that several kinds of file work remain unresolved, but it
  neither criticizes that framing nor instructs a later reader to discount it.
- Owners, legal procedures, community review, access states, complaint review,
  embargo alerts, capacity thresholds, and calendars are distributed from
  messages 3 through 24.
- Messages 25–28 confirm signed policy, staffing, ledger ownership, and audit
  dates, but do not independently supply the earlier permission rules,
  complaint trigger, decision criteria, or case-specific responses needed to
  determine both surfaces.
- No assistant turn names the expected Lolla result.

Human finding: `pending`

## Case 02 — serialized essay audio pilot

Experimental role: governed-pending restraint control without a matching prior
anchor.

- [Source](../../research/lolla-r4-matched-holdout-v2-source-freeze-2026-07-14/sources/r4h2-case02-serialized-essay-pilot.json)
- [Prior](../../research/lolla-r4-matched-holdout-v2-source-freeze-2026-07-14/priors/r4h2-case02-serialized-essay-pilot.json)

Preliminary CTO review:

- Production authority, accessibility checks, bank and budget thresholds,
  narrator response, version control, privacy limits, channel handling,
  checkpoints, and the dated board choice are distributed across messages
  3–24.
- Messages 25–28 confirm the signed charter, budget, role authority, and board
  agenda, but do not independently supply the earlier release, narrator,
  version, accessibility, measurement, and distribution facts needed to
  determine both surfaces.
- The prior describes the bounded pilot and evidence limits without naming a
  missing category.
- No assistant turn names the expected Lolla result.

Human finding: `pending`

## Case 03 — research workspace service

Experimental role: genuine recurring ownership, funding, and capacity issue.

- [Source](../../research/lolla-r4-matched-holdout-v2-source-freeze-2026-07-14/sources/r4h2-case03-research-workspace-service.json)
- [Prior](../../research/lolla-r4-matched-holdout-v2-source-freeze-2026-07-14/priors/r4h2-case03-research-workspace-service.json)

Preliminary CTO review:

- The current two-semester position and authority boundary are established in
  messages 3–8.
- The recurring workload is established in messages 15–17 through concrete
  task volume and unit responses.
- Messages 19, 25, and 27 establish the later proposal route, signed launch
  boundary, and lack of present appropriation or assignment.
- Messages 25–28 alone mention a later service and signature requirements, but
  omit the earlier workload, task volume, specialist estimate, and exact unit
  refusals. They therefore cannot independently establish the complete
  supported record or determine both surfaces.
- The prior discusses launch scope, data tiers, compatibility, and incident
  controls without naming the recurring service issue.
- No assistant turn names the expected Lolla category.

Human finding: `pending`

## Case 04 — shared language course

Experimental role: genuine later premise-breaking external dependency.

- [Source](../../research/lolla-r4-matched-holdout-v2-source-freeze-2026-07-14/sources/r4h2-case04-shared-language-course.json)
- [Prior](../../research/lolla-r4-matched-holdout-v2-source-freeze-2026-07-14/priors/r4h2-case04-shared-language-course.json)

Preliminary CTO review:

- Messages 5–7 establish that recognized cross-campus credit depends on a
  current State Academic Board designation and identify the issuing authority.
- Message 17 establishes that local deans cannot supply that authority and
  that no second designated instructor is listed.
- Message 23 supplies the board's immediate-effect withdrawal rule; messages
  25 and 27 supply the signed continuity appendix and current program endpoint.
- Messages 25–28 alone do not say that shared credit depends on the
  designation or that the board can withdraw it without a grace period. They
  therefore cannot independently establish the complete supported record or
  determine both surfaces.
- The prior focuses on the approved course and ordinary operating controls; it
  does not name the external dependency.
- No assistant turn names the expected Lolla category.

Human finding: `pending`

## Founder/PM declaration

To pass this gate, the human reviewer should confirm:

> I reviewed the v2 source/prior leakage packet. For all four cases, the
> assistant does not state the expected Lolla classification, the prior does
> not instruct the reader how to discount itself, the last four messages alone
> do not disclose the complete target, and the source does not tell the reader
> what to emit or suppress. Target authorship may begin.

No target, request preview, execution contract, authorization shape, or v2
runner may be authored while this declaration remains pending.
