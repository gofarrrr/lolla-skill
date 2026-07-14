# Lolla Product Constitution v2

Status: binding development house rules  
Date: 2026-07-11

This amendment incorporates
`docs/conversation-understanding/lolla-product-constitution-v1.md` in full. V0
and v1 remain immutable because completed evidence packages hash-lock them. If
this amendment conflicts with an earlier version, v2 governs future work;
historical runs remain governed by the constitution hash frozen in their
contracts.

## House rule 14 — Semantic responsibility must match visible context

A probabilistic task may only be evaluated against judgments its supplied
context can support. A local turn window can surface possible moves, claims,
questions, and evidence. It cannot reliably decide conversation-wide origin,
ownership, acceptance, first introduction, or final trajectory. Those judgments
belong to fresh cross-turn synthesis. Source strength, by contrast, should be
classified where attribution and modality remain visible and must not be
silently strengthened later.

Extraction families are complementary lenses, not deterministic routing silos.
Evidence found by one lens may support another synthesis task. Code may validate
identity and references across those families, but it may not decide semantic
relevance.

Decomposition is incomplete until fan-in is bounded. Small calls that create a
large overlapping ledger have merely moved overload downstream. Every frozen
design must measure both fan-out reliability and the candidate/token burden at
fan-in.

## Product evil — Context-invisible labels and hidden fan-in overload

The system asks a local reader for a global label, treats overlapping lenses as
exclusive gates, or celebrates narrow calls while their combined output
recreates one oversized synthesis task. The resulting pipeline can be tidy and
fully typed while remaining semantically brittle.

## Additional “what good looks like” questions

- Could this task know the label from the exact context it receives?
- Are complementary observations allowed to cross family boundaries without a
  deterministic relevance judgment?
- Is fan-in candidate and token load measured and bounded, not merely shifted?
