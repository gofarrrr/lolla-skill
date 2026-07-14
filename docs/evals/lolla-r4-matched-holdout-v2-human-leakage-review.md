# R4 matched holdout v2 human semantic leakage review

Status: passed by founder/PM human review; hash-bound target gate satisfied

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

Human finding: `passed`

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

Human finding: `passed`

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

Human finding: `passed`

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

Human finding: `passed`

## Founder/PM declaration and custody

The founder supplied this exact human declaration on 2026-07-14:

> human leakage review passes

It applies to all four complete source/prior pairs and means that the assistant
does not state the expected Lolla classification, the prior does not instruct
the reader how to discount itself, the last four messages alone do not disclose
the complete target, and the source does not tell the reader what to emit or
suppress. Human semantic sufficiency is decided affirmatively for these exact
bytes, so target authorship may begin.

| Case | Source SHA-256 | Prior SHA-256 | Last four sufficient for both surfaces |
|---|---|---|---|
| `r4h2-case01-community-audio-archive` | `4af8f39ce9cc8e4b7edbb80111c2cfabac09037e176895ae380392308a4ac3c1` | `e77baaf2378d8cfc3cc29371b4dc5e472b585a09f29b29d8725ff49d99ae7095` | no |
| `r4h2-case02-serialized-essay-pilot` | `922228b8371d9536464adc402390f6e50d894927e0b9a7f9c60518d9a68bdb80` | `b5706dc359957e92fb25ee9535d3981835f7496fc4f138eae12885f18f3a3543` | no |
| `r4h2-case03-research-workspace-service` | `9c3c979fbe79e6a573f9dc316e1e03c7a1ffc29dc0b5abd7c139825ef2a652ad` | `53aff0c8c41fd7c1504718f4190a736addad67d0f150ddbaa6482cfb71c95e52` | no |
| `r4h2-case04-shared-language-course` | `ce8f1652612467e83589b9073b6a8c83273044fb4c5ab611852e1d916cdb0783` | `9e0ec28e5094b7c68560db1af1e231c6859972317a0dd2204cfa3914ad202ac5` | no |

The deterministic prohibited-language scan is supporting custody evidence, not
a substitute for this human semantic judgment. Any byte change to a reviewed
source or prior invalidates the declaration and requires another human review.

## Evaluation limitation

Cases 01 and 02 end with summaries of several adopted documents and controls.
Those summaries provide some recency assistance. They do not disclose the
expected classification and are not independently sufficient to evaluate both
surfaces. The holdout therefore must not be described as a pure test of
recovering every relevant fact exclusively from distant context.
