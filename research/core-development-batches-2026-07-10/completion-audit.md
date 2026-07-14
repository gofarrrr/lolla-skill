# Core development batches — completion audit

Date: 2026-07-10  
Status: **complete**

## Program result

All four planned batches were executed under frozen contracts and recorded
without retroactive repair:

1. paired downstream discrimination — directional treatment value, clean
   integration gate failed;
2. protected-edge/false-stand-down — correct stand-down, exact accountability
   gate failed;
3. fact/reasoning invariance shadow — deterministic custody passed, semantic
   invariance failed;
4. integration decision — retain the experimental live core, keep new
   semantic/portfolio/pattern integration research-only, and continue with a
   narrower accountability-first development program.

No completed empirical case was rerun, retuned, or reclassified as a pass.

## Bounded provider use

Across Batches 1–3:

- 65 OpenRouter calls;
- 14 direct OpenAI embedding/query-expansion calls;
- zero evaluator calls;
- no experiment-level automatic retries;
- estimated total cost `$0.11107375`.

Batch 2's extractor used its one prospectively allowed quote-repair call. That
is part of its frozen extraction contract, not an experiment rerun.

Embedding credential separation is explicit: direct OpenAI calls require
`OPENAI_API_KEY`; an empty key disables embeddings/query expansion and does
not fall back to the OpenRouter credential.

## Verification

- focused decision/contract suite: 42 passed;
- full non-network suite: 3,940 passed, 1 skipped, 93 subtests passed;
- Batch 3 runner and engine modules compile;
- all JSON under the batch package and active conversation/eval contracts
  parses;
- all Batch 3 frozen source, routing, corpus, engine, and runner hashes match;
- all Batch 4 review references match their recorded hashes;
- credential-shaped and personal-absolute-path scan is clean on the new
  package and governing documents;
- `git diff --check` passes.

The pre-existing working tree contains extensive development changes and new
research artifacts. They were preserved; nothing was reset, staged, committed,
or deleted during this completion audit.

## Canonical handoff

- Product rules:
  `docs/conversation-understanding/lolla-product-constitution-v0.md`
- Evaluation rules:
  `docs/conversation-understanding/lolla-evaluation-doctrine-v0.md`
- Current measurement state:
  `docs/evals/lolla-product-measurement-map-v0.md`
- Founder-facing roadmap:
  `plans/lolla-product-blueprint-and-repository-gardening-2026-07-09.md`
- Integration decision:
  `research/core-development-batches-2026-07-10/batch4-decision.md`
- Continuous execution record:
  `research/core-development-batches-2026-07-10/notes.md`

## Next fixed milestone

Demonstrate one clean run in which Lolla contributes a source-backed pressure
that a strong fresh reasoner would otherwise miss or insufficiently consider,
does not force it, and records its exact identity and effect without an
unsupported claim.

Before that paid run:

1. harden exact pressure ID/reference custody;
2. keep effect-consistency review semantic rather than implementing Python
   meaning rules;
3. define the future routing target as unresolved joint-process reasoning;
4. freeze both downstream arms on a new case before either call.

The later fact-boundary retest uses new fixtures and the clarified target. It
does not tune Batch 3.
