# Reasoning-process stance-object v4.1 result

Status: semantic representation and shallow wire pass locally; provider rejects inherited schema keyword before inference  
Date: 2026-07-12

## Simple result

V4.1 preserved stance objects while reducing the provider schema to 3,654
bytes at depth 9. Because even a one-alias component object remained depth 11,
the provider wire uses five index-aligned string arrays. The deterministic
compiler verifies equal lengths and evidence-role membership, then reconstructs
normal component objects for inspection. Semantic column alignment remains an
LLM and source-review responsibility.

We also created three new ambiguous 14-message conversations before model use:
career transition, community-space commitment, and agency acquisition. Each
contains reported positions, an evolving stance, action-versus-acceptance
separation, and a qualification that can still change the plan. Career
transition was selected mechanically by SHA-256; protected targets and fixtures
were not present in the packet.

Provider-free gates passed:

- 60 legacy prompts and three fresh prompts built;
- all 20 legacy and three fresh reviewed fixtures compiled;
- 12 adversarial outcomes passed, including a deliberately permuted semantic
  column that remains structurally admitted for source review;
- non-position interfaces remained byte-identical;
- 200 reasoning-process tests passed before execution;
- the historical shared runner remained at its frozen hash.

## Provider and compatibility result

The single frozen career-transition request again returned HTTP 400
`INVALID_ARGUMENT` from Google before inference. There was no candidate,
compiled record, usage, cost, or semantic result. No retry or second case was
used.

The shallower failure rules out depth as a sufficient explanation. A local
audit with current `google-genai` 2.11.0 found a concrete problem: its native
`Schema` model rejects `uniqueItems` in the three inherited v2 evidence arrays.
Removing only those keywords makes the entire v4.1 schema validate. V3 also
fails the current SDK check for the same inherited keyword even though its
earlier routed call succeeded, so historical provider acceptance is not a safe
current compatibility contract.

Google's HTTP response does not name the field. `uniqueItems` is therefore the
high-confidence probable cause, not a provider-confirmed root cause.

## What we learned

The semantic stance-object redesign and provider compatibility are separate
problems. V4.1 improved the former and revealed the latter. Deterministic code
already rejects duplicate evidence IDs, so removing `uniqueItems` from the wire
schema would not weaken custody.

The parallel-column wire also has a known semantic risk: equal lengths do not
prove that the expression, object, and alias at one index belong together. The
adversarial suite preserves that as a source-review responsibility rather than
adding a compatibility matrix.

## Decision and next work

V4.1 is not ready for integration, graph, runtime, stability, full-case, or
receipt work. The career-transition case is closed. The two other new cases
remain reserved and cannot be called under the v4.1 contract.

The next bounded goal is v4.2, a wire-only compatibility correction:

1. preserve v4.1 prompts, semantics, column reconstruction, and validators;
2. remove `uniqueItems` from the position response schema while deterministic
   duplicate checks remain authoritative;
3. add a frozen current Google SDK schema preflight;
4. replay all 23 reviewed fixtures and adversarial cases;
5. select the next reserved case under a new prospective contract;
6. make at most one call with no retry, fallback, healing, judge, graph, or
   runtime behavior.

Primary evidence:

- `research/reasoning-process-stance-object-v41-2026-07-12/report.json`;
- `research/reasoning-process-stance-object-v41-2026-07-12/adversarial-review.json`;
- `research/reasoning-process-stance-object-v41-fresh-corpus-2026-07-12/report.json`;
- `docs/evals/reasoning-process-stance-object-v41-cold-reader-review.json`;
- `research/reasoning-process-stance-object-v41-probe-2026-07-12/result.json`;
- `research/reasoning-process-stance-object-v41-probe-2026-07-12/compatibility-diagnosis.json`.
