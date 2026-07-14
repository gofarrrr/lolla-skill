# Lolla Product Constitution v1

Status: binding development house rules  
Date: 2026-07-11

This amendment incorporates
`docs/conversation-understanding/lolla-product-constitution-v0.md` in full. The
v0 file remains immutable because completed evidence packages hash-lock it. V1
adds the following binding house rule, product evil, and evaluation question.
If this amendment conflicts with v0, v1 governs future work; historical runs
remain governed by the constitution hash frozen in their contracts.

## House rule 13 — Current practice must be checked, dated, and explicit

The model's remembered knowledge is not sufficient authority for a design that
depends on changing external technology. Before building, upgrading, freezing,
or authorizing work involving LLMs, model capabilities, provider APIs, prompts,
structured outputs, schemas, SDKs, agent frameworks, evaluation methods,
embeddings, retrieval, or security boundaries, the development agent must check
the current state of practice.

The check is proportional to risk and temporal volatility, but it is mandatory.
It includes:

- current primary documentation and capability metadata from the selected
  provider or model lab;
- current changelogs, schema subsets, limitations, and deprecations relevant to
  the exact version or endpoint;
- at least one maintained practitioner implementation, reference repository, or
  SDK pattern when the problem is implementation-facing;
- a dated record of sources checked, practices adopted, practices rejected, and
  deliberate departures;
- exact provider, model, SDK, prompt, schema, and projection identities in the
  frozen contract when they affect reproducibility.

For provider-backed experiments, this review happens before calls are
authorized—not after an avoidable failure. For longer development sequences, it
is refreshed when the relevant technology, dependency, model, endpoint, or
assumption may have changed. If current practice cannot be verified, the gap is
recorded as an explicit uncertainty or blocker rather than silently filled from
model memory.

Current practice informs implementation; it does not override the rest of the
constitution. Popular frameworks, automatic retries, larger agent graphs, or
new provider features are adopted only when they strengthen Lolla's product
boundary and earn their complexity. The standing structured-extraction example
is `structured-extraction-practices-july-2026.md`.

## Product evil — Stale-practice certainty

A development agent implements a remembered API pattern, schema feature, model
capability, evaluation convention, or framework recommendation without checking
whether it remains current. The resulting design may be internally polished but
already obsolete, unsupported, or needlessly brittle. Training memory is a
starting hypothesis, not a current technical source.

## Additional “what good looks like” question

Were temporally unstable technical assumptions checked against dated current
primary sources and maintained practice before implementation or calls?
