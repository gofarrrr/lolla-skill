# Reasoning Pressure Handoff v0

Status: shadow contract with dependency-free structural validator
Runtime status: not integrated
Date: 2026-07-10

Governing documents:

- `docs/conversation-understanding/lolla-product-constitution-v0.md`
- `docs/conversation-understanding/hybrid-reasoning-boundary-v0.md`
- `docs/conversation-understanding/reasoning-pattern-packet-v0.md`
- `docs/conversation-understanding/lolla-evaluation-doctrine-v0.md`

## Purpose

This contract defines the smallest **active working-set slice** between
deterministic graph recall and a fresh reasoning consumer. It is not the whole
future Step 6 reasoning portfolio.

It exists because two tempting alternatives failed:

1. The obvious enterprise-beta pressure did not beat a strong transcript-only
   reconsideration. More machinery did not create a unique decision delta.
2. The full 27-event SK3 semantic overlay was worse than transcript-only
   control on Case 07. Source-valid context reinforced the assistant's prior
   frame while omitting the user's self-correction.

The answer is not to remove the raw conversation or to add deterministic
semantic gates. The answer is to keep the raw conversation authoritative,
keep the active surface small, and preserve off-frame possibilities in a
compact reserve with expansion paths and delayed rejection.

The Case 07 result blocks an undifferentiated 27-event context dump. It does
not authorize premature pruning of graph-surfaced edge material.

## Position in the system

```text
full conversation
  -> source-linked semantic inventory for audit/navigation
  -> LLM-proposed fact-free reasoning patterns
  -> deterministic validation and graph candidate recall
  -> LLM-composed small case-local pressure handoff
  -> fresh reconsideration with the full conversation
  -> revised answer plus private consideration ledger
```

The graph does not write the final pressure. It returns candidates. An LLM or
human decides whether and how a candidate applies to this conversation.

## Exact disposition custody

The companion contract
`reasoning-pressure-disposition-ledger-v0.json` closes the identity gap between
the pressure handoff and the later receipt.

- deterministic code builds one shell for every `pressure_id` in packet order;
- the consumer must copy every ID exactly once without renaming, aggregation,
  or omission;
- each item records its strongest plausible application, disposition, reason,
  claimed visible or private effect, and both forcing and ignoring risks;
- structural validation checks identity, shape, required claims, and
  disposition/effect field compatibility;
- an independent semantic review separately records whether the claimed
  visible/private effect matches the actual revised answer.

The structural validator does not read the revised prose and infer whether an
effect occurred. It records the independent review's status and reviewed
output hash when supplied. `pending` is honest and valid; it is not silently
promoted to acceptance.

## What enters the fresh reasoning context

The fresh consumer receives:

- the complete authoritative conversation;
- the original answer or position being reconsidered;
- at most four case-local pressure items;
- up to four source-linked preservation items;
- explicit known limits and unresolved evidence;
- no expected answer, gold delta, human-review label, or product verdict.

This list describes the active slice only. The broader research portfolio may
also provide a compact edge/latticework reserve, weak or negative-space
receipts, parked items with reactivation conditions, and full archive refs.
Those layers remain research-only and are not represented by this v0 schema.

The handoff does not contain:

- the full semantic event inventory;
- the full graph candidate catalog;
- a parade of mental-model names;
- raw provider output or private chain-of-thought;
- numeric quality, confidence, depth, or proof-of-work scores;
- a command to reverse the original advice.

## Pressure item

Each pressure item must name:

1. **Mechanism:** the graph-returned candidate being applied.
2. **Source events:** exact source-linked semantic IDs that make the pressure
   plausible.
3. **Challenge:** one plain-language question or tension for the fresh reasoner.
4. **Applicability condition:** what must be true for the pressure to matter.
5. **Decision effect:** which kind of reasoning change it could produce:
   question, alternative, evidence gate, condition, sequence, reversal rule,
   or risk treatment.
6. **Consequence if true:** how the advice would materially change.
7. **Set-aside condition:** why the pressure should be rejected, deferred, or
   kept private if it does not fit.
8. **Graph trace:** the deterministic route that caused the candidate to be
   considered.

This prevents a mental-model label from becoming a conclusion. A useful item
must explain both its strongest application and its failure boundary.

## Preservation item

Pressure is not the only thing the consumer needs. It must also know what
useful value is at risk of being destroyed by overcorrection.

A preservation item carries a source-linked instruction such as:

- preserve legitimate urgency;
- preserve a user-owned ambition;
- preserve a valid safety boundary;
- preserve a useful original action;
- preserve uncertainty where the evidence is incomplete.

This is how the product avoids equating “more skeptical” with “better.”

## Authority split

LLM or human responsibilities:

- decide which graph candidates have case-local relevance;
- compose challenge, applicability, consequence, and set-aside fields;
- select preservation items;
- preserve ambiguity and conflicting interpretations;
- use, reject, defer, or keep each item private during reconsideration.

Deterministic responsibilities:

- verify conversation, pattern-packet, and graph-version hashes;
- verify every source event and graph trace reference exists;
- validate the schema, controlled effect vocabulary, item caps, and IDs;
- prevent raw provider/private reasoning leakage;
- record omitted, rejected, deferred, and used items without deciding which
  disposition is wise;
- reproduce graph traversal and packet assembly.

Forbidden deterministic behavior:

- selecting pressure because a keyword appears;
- preferring a reader family as semantic truth;
- ranking relevance by event count;
- deciding a user changed their mind;
- inferring applicability from topic, domain, or case facts;
- auto-promoting an item because it recurs or has a high graph score.

## Evaluation contract

The strong-baseline comparison answers one claim: whether Lolla adds unique
visible answer improvement.

```text
control = full conversation + original answer + neutral reconsideration
treatment = identical control + pressure handoff
```

Positive-case success requires at least one unique, source-grounded,
decision-relevant delta without extra lost value. Quiet-case success requires
responsible stand-down or private guarding without public bloat. A longer,
more structured, or more cautious answer is not a win.

Equivalence blocks a unique answer-improvement claim. It does not by itself
erase consideration/process value. That separate read asks whether Lolla
exposed a structurally different lens, preserved it through the portfolio, and
received a serious disposition without forced public absorption.

A future portfolio comparison should distinguish three arms when the call
budget justifies it:

```text
A = full conversation + strong neutral reconsideration
B = A + active pressure slice
C = A + active slice + compact edge/weak/parked portfolio
```

The B/C comparison measures whether protected breadth creates novel pressure
or false stand-down without recreating context dumping.

Before runtime integration, evidence must include:

- one non-obvious positive case;
- one quiet case;
- one known semantic-omission case;
- blinded comparison against the strong baseline;
- exact-run human review;
- no custody red lines;
- no deterministic semantic rules;
- an explicit rollback path.

## Current decision

This is a validated active-slice boundary, not a complete consumer and not
runtime authorization. No paid call, graph input, Step 6 prompt, skill
behavior, or runtime path changes because this contract exists.

The illustrative enterprise-beta packet contains three pressure items and two
preservation items: five consumer items versus 27 events in the blocked full
overlay. This is about 81% fewer top-level items, but it is only a compactness
observation, not a quality or token-efficiency score.

`engine/system_b/reasoning_pressure_handoff.py` now validates the mechanical
contract without a JSON Schema dependency. It checks shape, item caps, hashes,
custodied source and graph reference membership, boundary flags, and required
non-claims. It returns `valid_for_shadow_evaluation_only` and explicitly does
not validate semantic relevance or answer quality.

The same module now builds and validates the research-only exact disposition
ledger. This hardens packet-to-receipt custody after the protected-edge batch
returned a plausible but renamed pressure ID. The new ledger remains runtime
dormant and does not authorize the active handoff, pattern routing, or fresh
consumer.

The same packet has now been sealed in shadow mode against saved run
`20260709T201634Z_7a7930`. It links the authoritative conversation, SK3 semantic
shadow, reasoning-pattern packet, fact-free routing projection, and graph
survival report by real hashes. Its eight unique source-event references and
three graph references validate against 21 known semantic events and 73 graph
candidate rows.

That proves mechanical lineage, not semantic relevance. The pressure selection
is Codex-assisted and provisional, and the live runtime did not produce it. The
next no-call task is to compose this active slice with the existing dormant
`step6_attention_map.v1` portfolio shape so edge, weak, and parked material is
preserved without recreating the 27-event dump. Exact human review follows
that portfolio reconciliation. Only after that review should a new non-obvious
downstream call be considered.
