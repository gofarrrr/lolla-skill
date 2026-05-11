# Private Enrichment Treatment (Step 6)

## What this file is

The doctrine for privately handling lane material and `v60_enrichment` before
writing the Step 6 updated position. The user should see better reasoning, not
the machinery that caused it.

The central rule:

> The model has freedom of conclusion, but not freedom from consideration.

Lane outputs and V60 chunks are not commands. They are also not disposable
suggestions. They are curated material the system already selected from a
source-backed substrate. You may use, reject, defer, or keep them private as a
guardrail, but you owe them a serious hearing.

## The Consideration Standard

For every lane pressure you set aside, and for every selected V60 chunk, be able
to answer four private questions:

1. What is the strongest plausible application of this material to the current
   conversation?
2. What case evidence would be needed for that application to be valid?
3. If I use it, what changes in the advice, threshold, question, sequence, risk
   treatment, or evidence gate?
4. If I reject or defer it, what is the concrete failed condition or risk if it
   is forced?

This is not a request to mention everything. It is a request to metabolize the
material before deciding what belongs in the public answer.

## Rejection Standard

Bad rejection:

- "not relevant"
- "already covered"
- "too generic"
- "no change"

Good rejection:

- names the attempted application;
- names the condition that failed;
- names what would go wrong if the material were forced into the answer;
- preserves any useful residue as a private guardrail, evidence gate, or
  diagnostic question when possible.

`already_covered` is valid only when you can name where the public answer already
contains the same reasoning pressure. `irrelevant` is valid only when you can
name the strongest plausible application and why it fails.

## Absence Records

Absence records are not weak affordances. They are blockers.

Use them to prevent overclaim, duplicate splits, source-thin model use, and
tempting but unsupported public claims. An absence record can be the most useful
part of a card even when no visible sentence names it.

When an absence record is marked `used`, the private ledger must name what it
blocked or bounded. Fill at least one of:

- `blocked_or_guarded_claim`: the overclaim, unsupported interpretation, or
  positive use that the absence prevented;
- `uncertainty_boundary`: the confidence or evidence boundary preserved by the
  absence.

Do not mark an absence record `used` merely because it was read. If it did not
block, bound, or guard anything, reject or defer it with a concrete
`risk_if_forced`.

## Ledger Skeleton

The runtime provides a deterministic `consideration_ledger_skeleton` and may
also write `/tmp/lolla_${LOLLA_RUN_ID}_v60_ledger_skeleton.json`. Start from
that skeleton. Do not invent transaction identity fields.

Runtime chunk selection is local-relevance scored against the conversation and
lane evidence. Each selected chunk may include `selection_method`,
`selection_score`, `selection_reason`, `selection_effect_type`, and
`sibling_alternatives_considered`. Treat those fields as custody/recall
telemetry, not as proof that the chunk is useful. A `record_order_first`
selection method means the deterministic layer found no local lexical match and
fell back explicitly; give it a hearing, but be especially willing to reject or
defer it with a concrete reason.

Do not edit:

- `chunk_id`
- `card_id`
- `model_id`
- `chunk_kind`

Fill:

- `disposition`
- `route`
- `strongest_plausible_application`
- `why`
- `visible_effect`
- `private_guardrail`
- `risk_if_forced`
- absence-only blocker/boundary fields when applicable

After writing the ledger, run V60 finalization in require-valid mode before
continuing to pressure checks, memo rendering, Observatory, or archive. If
validation fails, repair the ledger against the skeleton and rerun finalization.
Do not let an invalid ledger become the first archived version of the run.

Route compatibility:

- `used`: `updated_position`, `pressure_check`, `private_guardrail`,
  `evidence_gate`, `diagnostic_question`
- `rejected`: `set_aside`, `already_covered`, `irrelevant`,
  `missing_evidence`, `duplicate`
- `deferred`: `set_aside`, `missing_evidence`, `evidence_gate`,
  `diagnostic_question`
- `not_considered`: `already_covered`, `duplicate`, `irrelevant`

## Public / Private Split

The public answer should not prove that you considered the packet. Do not leak
V60, affordance, chunk, packet, ledger, lane, card, or internal ID language.

The right behavior is:

- privately test the material hard;
- publicly show only the decision-relevant improvement;
- leave a ledger so reviewers can see what happened under the hood.

If the packet produces no public delta, that can still be a good result if the
ledger shows responsible rejection, deferral, no-op correctness, or private
guardrail use.
