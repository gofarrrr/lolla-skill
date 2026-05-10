# Handover: V60 Local Transaction Lab

> Date: 2026-05-09
> Audience: future implementation session with no prior chat context
> Status: handover plus local dry-run preflight update
> Runtime posture: dormant, offline, review-only
> Supersedes as starting point: `plans/reasoning-substrate-affordance-transaction-handover-2026-05-08.md`

## Core Question

The old handover asked whether the v18 affordance substrate could survive
pickup. The current question is sharper:

> Can v60's richer affordance and absence substrate become useful internal
> consideration material for Claude Code / Codex without becoming overfeeding,
> over-authorization, or mental-model theater?

The target is not card usage or visible public uptake. The target is responsible
handling of curated cognition: useful chunks may be used, rejected, deferred,
kept private, or absorbed as guardrails. The human receives the downstream
reasoning product, not the v60 machinery.

## Current Ground Truth

The active reviewed affordance substrate is:

- artifact: `model_affordances_v60`
- path: `data/compiled/model_affordances/affordances_v60.json`
- status: `draft_review_only`
- model records: 222
- affordances: 306
- absence records: 697
- schema validation failures: 0
- source quote rejections: 0
- runtime references: none

Affordance distribution by model:

- 157 models with 1 affordance
- 52 models with 2 affordances
- 10 models with 3 affordances
- 1 model each with 4, 5, and 6 affordances

Absence coverage:

- every model has at least 2 absence records;
- no zero-absence model remains;
- absence records are central to safe use, not a footer.

Weak and medium support to keep visible:

- weak-support model records:
  - `devops-and-continuous-integration`
  - `price-discrimination`
- medium-confidence model set:
  - `adverse-selection`
  - `batna`
  - `devops-and-continuous-integration`
  - `markov-chains`
  - `price-discrimination`
  - `principal-agent-problem`
  - `six-thinking-hats`

## Canonical Source Doctrine

The canonical Markdown is the gold source. It must not be squeezed, softened,
or extended to satisfy runtime convenience.

Project doctrine treats these files as book-derived applied knowledge gathered
through a fixed question process, not as generic LLM world knowledge. The system
may normalize that knowledge into reviewed affordances, but it may not pretend
to possess material that the source set does not support.

Active local custody:

- source manifest: `data/model_sources/manifest.json`
- copied source files: `data/model_sources/*.md`
- copied from: `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216`
- manifest count: 222 files
- hash algorithm: SHA-256

Authority order:

1. Raw canonical Markdown source.
2. Reviewed curation JSON.
3. Compiled artifacts derived from reviewed curation.
4. Runtime interpretation.

If a compiled affordance or reviewed curation layer disagrees materially with
the canonical Markdown, the Markdown wins. The disagreement should become
visible in review notes. Do not smooth it away.

Python may validate shape, enum values, IDs, caps, exact source quotes, hashes,
and trace references. Python must not infer semantics from headings, keywords,
or model names. It must not decide what good thinking is.

## Product Doctrine

Lolla is not trying to become a fact checker or a deterministic answer oracle.
It is a reasoning-about-reasoning layer.

The current product risk is that a strong LLM plus a strong prompt can produce
high-quality generic output that feels persuasive while still:

- accepting the user's frame too cheaply;
- missing the edge that matters;
- rationalizing after the fact;
- smoothing over trade-offs;
- treating fluency as truth;
- using model names decoratively;
- ignoring absence of evidence.

The deterministic system exists to transport curated cognition with custody and
limits. It should say, in effect:

> These candidate reasoning transactions were selected by structured lanes,
> graph context, reviewed affordances, and source custody. Use, reject, or defer
> them freely, but account for them seriously.

The central doctrine still holds:

> The LLM has freedom of conclusion, but not freedom from consideration.

This does not mean the lab can know exactly what every future user will find
valuable. It also does not mean visible final-answer change is the only win. The
product bet is subtler: source-backed lenses, selected for reasoning rigor
rather than surface circumstance, can give the skill-using LLM extra cognitive
leverage that the immediate case framing would not naturally provide. The lab
should therefore measure useful-to-consider material, responsible rejection,
deferral, private guardrails, public deltas, and failure modes. It must not
pretend to measure final user value exhaustively.

## 2026-05-09 Local Preflight Update

The first dry-run transaction lab slice now exists on branch
`feat/v60-transaction-local-replay-lab`. It remains dormant and offline.

What now exists:

- grouped v60 affordance cards in the packet shape;
- grouped-card review Markdown rendering;
- a review-only transaction ledger validator;
- an eight-case replay manifest;
- Arm A/B/C prompt-packet generation;
- compact decoder-facing Arm C packet projection;
- preflight artifact generation;
- expanded dry-run configuration matrix across caps, snippet density, and
  solution modes;
- explicit Grok/Kimi provider plan metadata, with no paid calls made.

The preflight did not justify live `/lolla` pickup. It found two concrete
blockers and resolved one locally:

- cap pressure: all eight cases produced 12 cards and six suppressed
  candidates;
- compression pressure: the first Arm C prompt packets were roughly 42k-50k
  estimated tokens, then the compact projection reduced them to roughly
  12.8k-18.8k.

The matrix suggests `cap8_focused` as the first product-shaped paid pilot
configuration and `cap12_default_compact` as a research comparison. It also
separates three product modes that should not be collapsed: answer revision,
edge audit, and question gate. Therefore the next slice should choose the pilot
mode explicitly, followed by a small four-case paid pilot if approved.

## 2026-05-10 C4.3 Consideration-Router Update

After C4.2, the next iteration was reframed away from "admit one public edge."
That framing was too narrow for Lolla. The v60 substrate is internal enrichment
for Claude Code / Codex, not a human-facing worksheet.

The replay harness now has:

```bash
--c-variant consideration_router
```

C4.3 asks the model to produce the normal public answer surface plus a private
`consideration_usefulness_report`. The report has one assessment per candidate
card and separates:

- whether the card was useful to consider;
- what role it played: frame changer, evidence gate, diagnostic question,
  guardrail, tension maker, boundary marker, compression aid, or rejection aid;
- where it routed: public delta, question, evidence gate, guardrail,
  private-only reasoning, defer for missing evidence, reject irrelevant, or
  reject duplicate;
- what the packet was missing or over-supplying.

This is the same doctrine as the lanes: the deterministic system does not know
truth. It narrows the field to material worth consideration. The LLM interprets
that material inside the messy conversation.

The qmd-inspired retrieval lesson should be pursued as a follow-on: v60 probably
needs affordance-level and absence-level retrieval with lexical matching,
semantic embeddings, context metadata, reranking, and score traces. But this
must stay inside Lolla's trust hierarchy. Embeddings are additive low-trust
recall; they must never become the judge of semantic usefulness.

## What Good Looks Like

Good does not mean every card is used. Good also does not always mean the public
answer visibly changes. Good means the model handled the packet in a
decision-relevant and source-disciplined way.

Examples of good outcomes:

- A card is used because it changes the evidence threshold.
- A card is rejected because its strongest plausible application would require
  missing case evidence.
- A card is deferred into a useful question instead of forced into a claim.
- An absence record blocks a tempting but unsupported split.
- The final answer becomes less confident because the source-backed affordance
  revealed a missing condition.
- The final answer names a hidden trade-off the vanilla answer missed.
- The final answer silently applies a model without naming it.
- All cards are rejected or deferred, but the final answer improves by avoiding
  overreach.
- A card is useful because it gives the model a private guardrail, even though
  the user never sees that guardrail.
- A card is useful because it helps reject a tempting but unsupported model.

Examples of failure:

- Model-name decoration.
- Generic mental-model explanation.
- Longer answer with no better decision pressure.
- Cheap "not relevant" rejection.
- Card use with no concrete delta.
- Invented case facts to make a card fit.
- Hidden "latest artifact" selection.
- Treating v60 as runtime-promoted because it is more complete.

## Required Next Posture

**2026-05-10 update:** this section is now historical. The local lab proved
enough transport/ledger value for an explicitly approved private runtime
attachment. The product integration intentionally keeps V60 after the four
lanes, hidden from public prose, reversible by kill switch, and observable by
ledger. It still does not make V60 a final-answer oracle.

The next move is a dormant local replay lab, not `/lolla` integration.

The lab should test whether grouped v60 cards and ledgers change thought under
controlled local conditions. It should not change:

- live `/lolla`;
- `scripts/run_pipeline.py`;
- `engine/system_b/pipeline.py`;
- lane prompts;
- user-facing chat;
- memo output;
- Observatory UI;
- runtime model selection.

## Packet Doctrine

The existing dormant packet builder flattens affordance fields into
`reviewed_affordance_fields`. That is too lossy for v60. The next packet shape
must add grouped `reviewed_affordance_cards` while preserving the old field for
compatibility.

Each grouped affordance card should preserve:

- `affordance_id`
- `status`
- `confidence`
- `activation_shape`
- `treatment_requirements`
- `diagnostic_questions`
- `misuse_guards`
- `source_evidence`

Absence records must become first-class:

- possible blockers;
- do-not-overclaim rails;
- owner-boundary markers;
- reasons to defer rather than use.

Weak support and medium confidence must be visible in packet review and decoder
instructions. They must not be hidden behind a normal-looking card.

## Ledger Doctrine

The ledger should use exactly three dispositions:

- `used`
- `rejected`
- `deferred`

Do not add `merged` as a disposition. Represent merge through metadata:

- `merged_with_card_ids`
- `effect_type`
- `final_answer_delta`
- `visibility`

Every card should receive one transaction. A transaction must include:

- strongest plausible application;
- disposition;
- evidence status;
- decision reason;
- risk if forced;
- final-answer delta or reason for no delta;
- visibility;
- considered affordance IDs when available.

The validator should be shape-and-trace only. It can reject unknown card IDs,
unknown affordance IDs, invalid enums, missing required fields, or impossible
summary counts. It must not decide whether the semantic reason is wise.

## Evaluation Doctrine

Do not score the lab by card usage.

Score it by paired output comparison:

- Did grouped cards reveal a non-obvious edge?
- Did they reduce overclaiming?
- Did they create a useful question, caveat, threshold, option, sequence, or
  confidence change?
- Did they avoid invented case facts?
- Did they avoid generic model exposition?
- Did they preserve the user's actual situation?
- Did the ledger make rejection and deferral inspectable?
- Did the output improve against a strong baseline, not against a weak prompt?

Single-run evidence is insufficient. Prior Lane 2 audits showed that a producer
chain can look clean on one archive and become noisy on rerun. The lab must use
multi-run characterization where model calls are involved and must separate:

- local transaction usefulness;
- whole-run producer stability;
- honest hypothesis diversity;
- noisy adjacent model drift.

## Anti-Overfitting Doctrine

The test set should not become the product.

Use archived cases to learn, but do not encode case-specific fixes. A rule is
acceptable only if it improves general reasoning transport:

- source custody;
- cap discipline;
- absence visibility;
- provenance merge;
- ledger traceability;
- cheap-rejection blocking;
- forced-use detection;
- no hidden promotion.

A rule is suspect if it depends on:

- a case slug;
- a domain label;
- a known desired answer;
- a phrase that only appears in one archived conversation;
- a post-hoc explanation of why the run looked good.

## Read Before Implementing

Required context:

- `plans/v60-transaction-packet-local-replay-plan-2026-05-09.md`
- `plans/reasoning-substrate-affordance-transaction-handover-2026-05-08.md`
- `research/pr55-runtime-readiness-blockers-2026-05-08.md`
- `research/pr55-lane-to-nomination-provenance-contract-2026-05-08.md`
- `references/model-affordance-extraction.md`
- `plans/knowledge-use-schema-2026-05-04.md`
- `plans/knowledge-substrate-roadmap-2026-05-04.md`
- `engine/system_b/reasoning_substrate_packet.py`
- `engine/system_b/reasoning_substrate_packet_review.py`
- `scripts/run_gate4_edge_probe_experiment.py`
- `scripts/run_model_treatment_audit.py`
- `research/stability-runs/lane2-producer-audit-2026-04-26/synthesis.md`

## One-Sentence Handoff

Build a local, dormant v60 replay lab that treats canonical Markdown as the
semantic root, turns lane or explicit nominations into grouped source-backed
affordance transactions, forces a decoder to use/reject/defer them with an
inspectable ledger, and evaluates whether the resulting answer improves
decision reasoning beyond a strong generic baseline without overfitting or
mental-model theater.
