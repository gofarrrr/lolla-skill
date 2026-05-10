# V60 C4.4 Exact-Chunk Private Replay Readout

Date: 2026-05-10

Status: dormant lab evidence only. This does not attach v60 to `/lolla` runtime.

## Question

Can exact v60 affordance and absence chunks survive retrieval and private model
consideration without being flattened into generic model names or forced into
public-answer theater?

## Runs

### C4.4 Card-Level Exact Chunks

Path:
`data/evaluations/v60_transaction_replay_lab/2026-05-10-c44-exact-chunk-private-replay-paid/`

- Generator: `x-ai/grok-4.1-fast`
- Items: 8
- Cost: `$0.030204`
- Raw validation: 6 valid, 2 invalid
- Packet usefulness: 6 useful, 2 mixed

The two invalid traces were informative. The model assessed each card's
affordance chunk and absence chunk separately, duplicating every card ID. That
means the model naturally treated the exact v60 affordance and absence records
as different cognitive objects. One verdict per model-card is too compressed for
exact-chunk use.

### C4.4b Strict Chunk-Level

Path:
`data/evaluations/v60_transaction_replay_lab/2026-05-10-c44b-exact-chunk-private-replay-chunk-paid/`

- Generator: `x-ai/grok-4.1-fast`
- Items: 8
- Cost: `$0.032552`
- Raw validation: 4 valid, 4 invalid
- Packet usefulness: 7 useful, 1 mixed

This confirmed the right granularity but exposed contract brittleness. Failures
were mostly missing low-salience absence rows, enum drift (`opportunity_role:
none` for rejected chunks), and one validator bug around public candidate
detection.

### C4.4c Hardened Chunk-Level

Path:
`data/evaluations/v60_transaction_replay_lab/2026-05-10-c44c-exact-chunk-private-replay-hardened-paid/`

Revalidated aggregate:
`data/evaluations/v60_transaction_replay_lab/2026-05-10-c44c-exact-chunk-private-replay-hardened-paid/summary_revalidated.json`

- Generator: `x-ai/grok-4.1-fast`
- Items: 8
- Cost: `$0.032632`
- Raw validation before final validator relaxation: 7 valid, 1 invalid
- Post-hoc validation after fixing the evidence-gate field rule: 8 valid
- Packet usefulness: 7 useful, 1 mixed
- Total chunks assessed: 128

Aggregate routes:

- `private_reasoning`: 43
- `guardrail`: 33
- `reject_irrelevant`: 32
- `evidence_gate`: 7
- `diagnostic_question_candidate`: 4
- `public_delta_candidate`: 4
- `reject_duplicate`: 4
- `defer_missing_evidence`: 1

Aggregate usefulness:

- high: 53
- medium: 42
- low: 29
- none: 4

## Source-Slot Read

The 4/2/1/1 pickup policy was: 4 lane-preserved cards, 2 embedding-affordance
novel cards, 1 embedding-absence card, and 1 hybrid/RRF card.

Lane-preserved cards still carried the backbone: 64 chunk assessments, with 25
high and 22 medium usefulness marks. That says the deterministic lane system is
not obsolete; it remains the provenance spine.

Embedding-affordance slots earned their place: 32 chunk assessments, with 16
high and 8 medium marks. They produced real selected opportunities, including
optionality on `startup_pivot` and private/evidence/guardrail effects elsewhere.
The point is not "embeddings replace lanes." The point is "embeddings recover
contextual candidates the lanes sometimes suppress."

Embedding-absence slots were especially important: 16 chunk assessments, with 9
high and 5 medium marks. These were not just footnotes. They produced guardrails,
evidence gates, diagnostic opportunities, private reasoning effects, and one
public-delta candidate. This supports the product thesis that absence records
must be first-class blockers, not a footer.

Hybrid/RRF was mixed but not useless: 16 chunk assessments, with 3 high and 7
medium marks. It is probably a secondary slot, not the main novelty channel.

## Case-Level Signals

`startup_pivot` is the cleanest positive example. Exact chunks surfaced:

- optionality as a public candidate: test a hybrid/partial pivot rather than
  treating the choice as binary;
- premortem as a diagnostic question: ask what failure modes the pivot plan has;
- lean-startup absence as a blocker: do not treat flat growth symptoms alone as
  validated learning.

`real_estate` showed a different value shape. Price-discrimination and Nash were
rejected as irrelevant, while margin-of-safety, premortem, and opportunity cost
were useful. That is the desired behavior: the model did not force every
selected chunk to matter.

`friendship_money` showed absence/guardrail value. Prospect-theory and
opportunity-cost blockers protected against loss-frame pressure and costless
enabling, while empathy stayed private rather than becoming sentimental public
copy.

`whistleblower` was the only mixed packet. Even there, critical-thinking and
incentives were useful, while systems-thinking/power-dynamics were overfit. This
is a good negative signal: exact chunk routing can identify overfed cards.

## Kimi / Provider Findings

An attempted `moonshotai/kimi-k2.6` generator sweep produced one valid
`multi_offer` trace in the aborted run directory, but then hit provider-envelope
JSON failure and later hung on a subset run. After hardening, a 60-second Kimi
timeout smoke recorded an error row successfully:

`data/evaluations/v60_transaction_replay_lab/2026-05-10-c44c-exact-chunk-private-replay-kimi-timeout-smoke/`

Practical read: Kimi can remain a judge or occasional cross-check, but it should
not be the default generator for routine local exact-chunk replay until the
harness has stricter process timeout defaults and/or a smaller prompt profile.

## What This Proves

Exact v60 chunks can be delivered as private cognitive opportunities. The model
can distinguish:

- useful private reasoning from public deltas;
- affordances from absence blockers;
- strong opportunities from irrelevant or duplicate cards;
- lane-backed candidates from embedding-novel candidates;
- evidence gates and diagnostic questions from answer prose.

Most importantly, "useful" does not mean "the final answer changes." Useful can
mean:

- the model rejects a tempting but unsupported mental-model move;
- a missing evidence gate becomes visible;
- a vague answer becomes a testable threshold;
- a hidden bias/pressure gets guarded privately;
- an option-space expansion becomes available to the composer.

That matches the product philosophy: freedom of conclusion, not freedom from
consideration.

## What This Does Not Prove

This does not prove live `/lolla` readiness.

This does not prove user-facing improvement, because C4.4 intentionally avoided
final-answer generation and judging.

This does not prove the 4/2/1/1 policy is optimal. It only proves it is a sane
candidate policy worth testing further.

This does not prove cross-model stability. Grok is usable for this generator
path; Kimi was operationally unstable under the same prompt size.

## Architecture Implication

The future packet should be grouped by model-card for human/debug readability,
but the private consideration ledger should be chunk-level. A card-level ledger
collapses the exact affordance and absence rows too early.

Recommended shape:

1. Deterministic lanes nominate model IDs with provenance.
2. Embedding retrieval adds low-trust recall over exact v60 affordance and
   absence chunks.
3. Selection policy reserves explicit slots for lane, embedding-affordance,
   embedding-absence, and hybrid candidates.
4. Packet groups by model but preserves exact chunk IDs.
5. Private consideration returns one assessment per exact chunk.
6. Composer receives only selected opportunities, gates, and guardrails.
7. Public answer never sees v60/card/mental-model language directly.

## Next Test

Run C4.5 as a composer-boundary test:

- Input: vanilla answer, exact-chunk private trace, and selected opportunities.
- Output: a candidate answer delta or empty delta.
- Validator: no private-language leaks, no unsupported model naming, no forced
  chunk usage, and explicit reason when no delta is admitted.
- Compare against vanilla only after the private transport is stable.

Do not merge this into live product behavior yet. It is reasonable to merge the
dormant lab harness and docs after review, because they improve our ability to
measure the future runtime design without promoting v60 automatically.
