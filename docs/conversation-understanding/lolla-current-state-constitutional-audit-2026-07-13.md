# Lolla current-state constitutional audit

Status: audit complete; R1 and R2 repairs integrated provider-free

Date: 2026-07-13

Baseline: `173e2fb` on `codex/reasoning-audit-v1-handoff`

Provider calls made: none

## Post-audit implementation note

R1 and R2 are now complete provider-free. The live runtime preserves the full available
conversation separately from any bounded extraction view, emits neutral
`review_revised_answer` custody, freezes provider output/price/call/privacy
contracts before the network, preserves exact provider response and charged
cost identity, and guarantees every private-table ledger atom is visible or
exactly resolvable. It now also constructs a bounded constitutional graph
portfolio before probabilistic verification, preserves overflow and malformed
paths separately, and requires apply/reject/park custody over every active
pressure item. The defect documented below is the historical finding that R2
repairs; it remains useful as the causal explanation for the change.

## Bottom line

Lolla is not a hollow prototype. It has a real end-to-end skill, a substantial
curated substrate, four pressure lanes, deterministic validation, strong local
artifact custody, run-health reporting, ledgers, a memo, an Observatory, and a
reproducible V1 evaluation program.

At the audited baseline, the live product was not constitutionally coherent
enough for another paid reliability campaign or a claim that clean runs were
fit for automatic reliance. R1 and R2 have now repaired those mechanical
blockers without changing the evidence boundary: automatic reliance remains
unproven.

The most important baseline defect was architectural: the live Model Companion path
recalls up to 60 candidates, asks an LLM verifier which are present, and only
expands the 2–4 accepted candidates through the graph. In four recent local
runs, 53–57 candidates per run were silently omitted before Step 6. The audit
trail remembers their disappearance, but the reconsidering reasoner never sees
them. This is the exact “probabilistic re-domestication of deterministic
pressure” prohibited by Constitution v5.

The other baseline defects were more tractable:

- a skill-level long-conversation instruction can silently pre-truncate the
  authoritative transcript;
- clean artifact custody becomes `caller_action: use_revised_answer`, although
  usefulness and reconstruction are not established;
- the provider boundary has no hard per-call output ceiling, price ceiling,
  cumulative run budget, exact charged-cost custody, or explicit data-retention
  posture.

The completed R1/R2 response was a small staged repair, not a rewrite or model
comparison. The next move is the separately frozen R3 fresh-consumer proof.

## What we now understand from the ground up

The intended product loop is:

```text
authoritative conversation
  -> probabilistic interpretation of messy meaning
  -> deterministic identity, custody, bounds, and graph recall
  -> bounded active pressure plus compact edge reserve
  -> probabilistic apply / reject / park reconsideration
  -> disciplined public answer
  -> process receipt, not a quality badge
  -> human decision authority
```

At the audit baseline, the live loop was closer to:

```text
captured prose conversation
  -> one latest-position extraction
  -> deterministic and embedding recall
  -> probabilistic verifier deletes most recalled candidates
  -> graph expansion of verifier survivors only
  -> same-context reconsideration
  -> strong custody receipt
  -> clean custody may say use_revised_answer
```

That difference explains the feeling that the system was being “dumbed down.”
Compaction itself is not the problem. The problem is that compactness is
achieved by letting another probabilistic pass decide which external pressure
is allowed to exist. Lolla becomes cleaner precisely where it was designed to
remain usefully strange.

## What genuinely works

### Custody and failure honesty

The strongest part of Lolla is its deterministic harness:

- ordinary runs archive the conversation, extraction, lane results, revised
  answer, memo, ledgers, health, usage, and trace references;
- exact evidence and source references are validated;
- malformed provider and schema outcomes can be preserved rather than silently
  healed;
- V60 and private-table material receive structured disposition ledgers;
- `evaluation.json` explicitly evaluates the run envelope rather than advice
  wisdom;
- V1 preserved one semantic join failure and four HTTP 402 failures instead of
  manufacturing a complete batch.

This is important because a future system can be improved only when its misses,
omissions, costs, and transformations survive inspection.

### The probabilistic/deterministic principle

The constitution is technically sound:

- LLMs should interpret ambiguity, language, applicability, and role;
- deterministic code should own exact identity, hashes, source references,
  bounds, graph traversal, replay, budgets, and ledger completeness;
- graph recall is pressure, not relevance proof;
- the final reasoner may reject pressure, but an intermediate relevance pass
  may not erase it silently.

The research branch has working examples of this boundary: controlled IDs,
source-first role records, direct and graph portfolios, and fresh-consumer
apply/reject/park ledgers. Those are research assets, not current live behavior.

### Evaluation discipline

V1 is useful precisely because it did not produce a flattering scalar.

- 12 transfer cases were attempted;
- 7 completed;
- 1 failed the semantic join;
- 4 preserved funding-envelope failures;
- 5 complete cases stood down correctly;
- 2 stood down falsely;
- no untouched transfer case activated the direct or graph pressure arms;
- receipt integrity was supported;
- usefulness, stability, real-user transfer, and receipt reconstruction were
  not established.

This means we are smarter about the system even though we are not yet able to
claim it works reliably. We know which foundations are strong and which part of
the causal chain has not earned promotion.

## Blocking drift found at baseline (repaired by R1/R2)

### 1. Graph pressure was filtered before reconsideration (R2 repaired)

`Pipeline._run_companion()` passes recalled candidates to
`run_verification_call_with_diagnostics()`, then calls
`build_companion_card()` only with `verification.detected_models`. Graph
expansion therefore starts after the probabilistic verifier, not before it.
`pre_step6_private_table.py` and `v60_enrichment.py` consume the surviving
cheat-sheet anchors; they do not restore rejected or silent candidates.

Four recent local archives provide direct structural evidence:

| run | candidates | detected | rejected | silently omitted |
| --- | ---: | ---: | ---: | ---: |
| adopt architectural product | 60 | 2 | 2 | 56 |
| approve proposed project | 60 | 3 | 0 | 57 |
| five-person SaaS | 60 | 4 | 3 | 53 |
| split conversation processing | 60 | 2 | 3 | 55 |

This table does not claim that all 60 candidates were useful. Most probably
were not. It proves the narrower constitutional failure: the final reasoner was
not allowed to inspect and disposition the bounded deterministic pressure.

### 2. Full-conversation custody could fail before the machinery saw it (R1 repaired)

`docs/skill/STEPS.md` tells the orchestrator to include only the first three and
last fifteen turns when a conversation exceeds 100 turns. If the orchestrator
writes a header describing only those retained turns, downstream capture
adequacy can honestly validate the file it received while missing the larger
source omission.

`run_extract.py` has a separate 80,000-character processing cap. That cap is
better designed: it records what was omitted and retains the captured source
artifact. The repair is therefore not “never compact.” It is to keep the full
available prose transcript authoritative and make every processing view a
separate, declared derivative.

### 3. The machine-facing receipt inflated reliance (R1 repaired)

`agent_result.py` correctly distinguishes healthy, partial, degraded, and
incomplete run envelopes. But for an ordinary healthy run it returns
`use_revised_answer`. Three of the four inspected archives do so solely because
required product artifacts are present.

That crosses a boundary the rest of the project states correctly:

```text
artifact completeness != semantic usefulness
receipt integrity != proof of reasoning quality
revised answer exists != advice is ready for autonomous use
```

The label should become neutral until blinded usefulness and fresh-reader
reconstruction are demonstrated.

### 4. Paid-call and privacy controls were below the current bar (R1 repaired)

The live OpenRouter request uses `response_format: {"type": "json_object"}`
and a temperature, but no stage-specific output cap, `provider.max_price`,
run-level call or USD envelope, `provider.require_parameters`, explicit data
policy, or ZDR preference. The runtime estimates cost from a local table and
does not persist OpenRouter's exact `usage.cost` or response ID.

Current primary guidance supports stronger controls:

- [OpenRouter Structured Outputs](https://openrouter.ai/docs/guides/features/structured-outputs)
  recommends strict JSON Schema for supported models and
  `require_parameters: true`;
- [OpenRouter Provider Routing](https://openrouter.ai/docs/guides/routing/provider-selection)
  documents `max_price`, parameter enforcement, fallback control,
  `data_collection`, and ZDR routing;
- [OpenRouter Usage Accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting)
  documents exact cost and generation identifiers in response usage;
- [OpenRouter Models](https://openrouter.ai/docs/guides/overview/models) exposes
  current supported parameters and prices;
- [Gemini 3.1 Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite)
  and [Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output)
  confirm that the current affordable model supports structured output, subject
  to its schema subset.

The implementation-facing check also reviewed the maintained
[OpenRouter AI SDK provider](https://github.com/OpenRouterTeam/ai-sdk-provider),
which exposes exact OpenRouter cost metadata, and Google's maintained
[Python Gen AI SDK](https://github.com/googleapis/python-genai), whose examples
keep the JSON schema in the request contract and warn against duplicating it in
the prompt. Lolla can preserve its stdlib client; the useful practice is the
request and custody pattern, not adopting another dependency.

This does not authorize a blanket schema rewrite. Earlier probes showed that
complex schemas can fail while small decomposed jobs succeed. The adoption rule
is stage-specific strict contracts, locally validated first.

## Important but non-blocking gaps

### Multi-thread conversation understanding

The live extractor emits one decision situation, one latest synthesized
position, and a small set of passages. This is useful as a lane input, but not a
complete representation of a long ambiguous conversation with parallel topics,
starting positions, revisions, qualifications, unresolved matters, and reopen
conditions.

The role-first research is relevant here, but integrating it before the graph
survival and custody blockers are fixed would mix two causal changes. Semantic
representation is Stage R4, not the immediate patch.

### Same-context reconsideration

The skill currently asks the same orchestrator that participated in the
conversation to write Step 6. The repository acknowledges this trajectory and
self-justification risk, and optional subagents remain off by default. This is
an accepted current limitation, not a surprise rewrite request.

What is missing is per-run disclosure. Every receipt should say whether the
consumer was same-context or fresh-context. Fresh-consumer testing comes only
after the provider-free portfolio contract passes.

### Private-table cap versus ledger

Two inspected private tables hit the 9,000-character cap. The builder collects
ledger source items before hard-capping the rendered markdown. Current examples
retained their core selected cards, but no regression test proves the necessary
invariant:

> Every ledger-required item is either fully visible to the consumer or has an
> exact source pointer the consumer can resolve.

This is a provider-free custody test, not a reason for another model call.

### Product and marketing language

“Reasoning-quality gate,” “fit for automatic use,” and categorical claims that
Lolla detects fragility exceed the V1 evidence. The accurate current
description is:

> Lolla is an experimental reasoning-pressure and audit system that preserves
> a conversation, introduces curated structural pressure, asks for accountable
> reconsideration, and records what happened. It does not certify that the
> revised answer is better or safe to act on.

The README and shareable pitch are corrected with this audit. Historical PRDs
remain historical and should not be treated as the live product contract.

## Cost and model decision

The current OpenRouter model API lists these approximate input/output prices per
million tokens on 2026-07-13:

| model | input | output | local evidence |
| --- | ---: | ---: | --- |
| Qwen 3.5 Flash | $0.065 | $0.26 | not yet tested on the decisive microtask |
| DeepSeek V4 Flash | $0.077 | $0.154 | cheap, but failed the exact evidence interface and was slow in the frozen probe |
| Gemini 3.1 Flash-Lite | $0.25 | $1.50 | passed the exact small starting-position task quickly |
| GLM 5.2 | $0.93 | $3.00 | no evidence justifying its higher price here |
| Gemini 3.5 Flash | $1.50 | $9.00 | premium benchmark only; routine testing prohibited |

Therefore:

- keep Gemini 3.1 Flash-Lite as the provisional live default;
- do not infer that it is a production-quality operator;
- do not switch to DeepSeek merely because it is cheaper;
- do not use Gemini 3.5 Flash for routine development;
- spend nothing until the provider-free R1 and R2 contracts pass;
- when a call is finally authorized, cap the complete attempt at $0.01 with no
  retry, fallback, or healing.

## Unknowns we should preserve, not answer by assertion

- Can an active set plus compact edge reserve preserve strange pressure without
  overwhelming the final reasoner?
- Does graph-expanded pressure add anything beyond a strong fresh second pass?
- Can a fresh consumer reject most candidates honestly without absorbing them
  or bloating the answer?
- Will real users find the revised answer or the receipt useful?
- Can a cold future agent reconstruct the process from the receipt without
  mistaking it for certification?
- Which parts of a tool-use trajectory, if any, belong in reasoning custody?
- Does an explicit no-retention provider posture materially change availability,
  latency, or cost for the selected model?

These are future experiments. None should be converted into a deterministic
meaning rule or a marketing claim.

## Decision and current handoff

The system has a strong enough custody foundation and graph-survival path to
continue to one tightly frozen fresh-consumer proof. This does not establish
that the pressure is useful, that the selected active set is semantically
optimal, or that a revised answer is better.

Follow
`plans/lolla-post-v1-constitution-aligned-roadmap-2026-07-13.md` in order. R1
completed provider-free trust, capture, cost, privacy, and ledger hardening. R2
completed the smallest graph-survival correction. R3 is now the boundary: one
fresh Gemini 3.1 Flash-Lite pressure attempt may be authorized only after its
entire contract passes locally, with a $0.01 cap, no retry, no fallback, and no
healing. See the R1/R2 result note for the exact implementation and evidence.

The machine-readable finding register is
`docs/evals/lolla-current-state-constitutional-drift-register-v1.json`.
