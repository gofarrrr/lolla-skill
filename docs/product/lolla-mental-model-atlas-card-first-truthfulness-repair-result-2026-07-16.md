# Mental Model Atlas Card-First Truthfulness Repair Result

Status: local founder review ready; unpublished

Date: 2026-07-16

Decision:

`card_first_abstraction_truthfulness_repair_ready_for_founder_validation`

## Executive result

The local Abstraction page now behaves the way the product description implies:
the complete canonical Markdown card is the primary learning document. The
compiled knowledge-graph record and the exact relationship neighborhood remain
useful, but they appear afterward as separately named layers rather than being
presented as if they were the source card.

The previous Phase 1 page had strong hash custody but directly projected only
one of the card's 60 substantive lines. Its blanket “complete model page” label
therefore described artifact availability, not full source-card coverage. This
repair corrects that claim prospectively with an additive v2 artifact. It does
not change the frozen v1 page, manifest, result, source, graph, or relation
evidence.

The truthful current statement is:

> The Abstraction source card is complete; the broader learning page is
> partial.

Provider calls: 0.

Provider cost: `$0.00`.

## What the page contains

### Layer 1 — authoritative source card

The exact `abstraction_rag.md` bytes are embedded once in the v2 artifact. An
explicit reviewed line map accounts for all 126 physical lines and renders:

- all 60 substantive lines;
- the source title as the page H1;
- five H2 and nine H3 headings;
- paragraphs, ordered lists, unordered lists, five rules, and the complete
  five-row source table;
- zero omitted substantive or title/heading lines.

The browser derives the document from `source_text + line_map`; it does not keep
a second copied prose tree that could drift.

### Layer 2 — compiled operational curation

The complete 12-field canonical Abstraction record from
`data/knowledge_graph.json` remains available. The page labels this material
“compiled knowledge graph,” identifies it as not the source card, and exposes
its source pointer and record hash. It includes selection and danger guidance,
reasoning profile, failure modes, premortems, heuristics, source quotes, and
curation metadata.

### Layer 3 — exact relationship neighborhood

All 12 Abstraction-incident source records survive in source order:

- five outgoing and seven incoming;
- seven ally, one antagonist, and four tension records;
- both parallel Abstraction → First Principles Thinking ally and tension
  records remain distinct;
- each record keeps exact direction, relation identity, source index, and
  source-authored text;
- affinity, rank, score, and weight are not used to imply importance.

The page explicitly says these connections support navigation and comparison;
they do not certify relevance or truth.

## Coverage and remaining loss

Three component claims are complete: the authoritative source card, the full
Abstraction knowledge-graph record, and membership of the incident relationship
set. The aggregate page remains `partial` because:

- the product-safe relation records omit raw source fields such as
  `composition_affinity` and record that omission;
- reviewed runtime-affordance cards exist but are not projected by this repair;
- distinct reviewed practice prompts have not been authored;
- curated Teacher journeys have not been authored.

That boundary matters. The repair prevents the graph from replacing the card,
but it does not claim that one complete card plus compiled metadata equals a
complete teaching product.

## Frozen and additive custody

Frozen Phase 1 v1 anchors remain byte-identical:

- v1 manifest: `203999a61dbe9c2e943bbcb9f5b4dd87779d4557ea9fcfbd50b3e9d59e816c52`;
- v1 model page: `8cc07cbbf68f399dcd5787df9067bd3a3646068b59ed691ca043ffc9e9ce406f`.

Additive v2 anchors:

- canonical source: `6d689abd7ae1f8022e2450b045b0f03ffc57700f8298ff858018d808845f5650`;
- canonical KG record: `ec28ee731944e7760dd574a401593d4dac1373ad69d3d080f9e58a4ebd19daef`;
- v2 model page: `6cd0ea5990fe9a871597f1d1c14e1d119e254b183be9d7ff0dd95fd38d309eea`;
- v2 manifest: `36223e0056c40e535470235b869b887fa3ac64584aa0338c670c78290cdf68a4`.

The additive package is under
`apps/mental-model-atlas/public/data/card-first-v1/`.

## Implementation and failure behavior

The provider-free builder rejects source-hash drift, line gaps, duplication,
reordering, incorrect heading roles, false coverage counts, KG-record drift,
connection drift, and any aggregate completeness claim that hides partial or
missing components. The TypeScript loader repeats the structural checks and
verifies exact source and KG-record hashes with Web Crypto before rendering.

The page preserves failure as `failed`. A corrupt or unavailable v2 artifact is
not rendered as a complete card, `missing`, `partial`, or `completed_zero`.
Other model slugs retain their honest unavailable-page boundary; the repair
does not synthesize 221 missing articles from graph fields.

The complete card payload is fetched only on the model route, and the browser
does not load the roughly 6 MB full V60 affordance registry. The current app
shell still loads its ordinary local Phase 1 navigation projection on a direct
model-page visit because `ProjectionProvider` remains global. Removing that
redundant local fetch is a later performance cleanup, not part of the source-
loss repair and not evidence of a missing model-card field.

## Browser review packet

The local review packet at
`docs/product/evidence/lolla-mental-model-atlas-card-first-repair-2026-07-16/`
contains desktop and mobile views of:

- the card-first hero;
- the long-form source reading view;
- the source table;
- compiled operational guidance;
- all exact relationship records;
- the component-level coverage boundary;
- the fail-closed corrupt-artifact state.

The reviewed page contains 60 rendered substantive source nodes and 12
relationship cards. At 320, 340, and 390 px widths it produces no page-level or
card-layer horizontal overflow. The wide source table remains in its own
horizontally scrollable region and shows a visible small-screen scroll cue.

## Verification

The machine-readable receipt is
[`lolla-mental-model-atlas-card-first-repair-evidence-v1.json`](../evals/lolla-mental-model-atlas-card-first-repair-evidence-v1.json).
Final checks:

- card-first plus frozen Phase 1 Python tests: 26 passed;
- focused handoff tests: 37 passed;
- Atlas Vitest: 28 passed;
- TypeScript check: passed;
- production build: passed; card-first model route chunk 26.38 kB raw and
  7.98 kB gzip;
- dependency audit: zero known vulnerabilities;
- complete repository suite: 5,004 passed and 93 subtests passed;
- warning: one existing `datetime.utcnow()` deprecation;
- Stage 0 register: valid with 25 components, 24 connections, 17 Constitution
  findings, 26 Decision Trail groups, and 639 accounted Python files;
- changed Markdown links: 260 checked, zero missing;
- changed JSON, Python compilation, `git diff --check`, added-material secret
  scan, and Git object integrity: passed.

An independent, source-blind browser sub-agent initially blocked the page for
real mobile clipping in the lower layers and then found a narrower hero crop.
Both defects were repaired. Its final verdict is `accept for founder visual
validation`, with zero remaining blockers at 320, 340, and 390 px. Native
VoiceOver/NVDA/JAWS behavior remains untested and is not inferred from the
semantic HTML or accessibility-tree inspection.

## Nonclaims and next decision

This is not proof of teaching usefulness, mastery, graph relevance, relation
truth, content rights, deployment readiness, runtime behavior, or Teacher
journey quality. The full V60 registry is not shipped to the browser and no
later Atlas phase has started.

The next founder decision is visual and product-facing: does this card-first
page correctly express the intended relationship between the full mental-model
article, Lolla's operational curation, and the graph? If yes, the composition
may become the accepted local pattern after a separate publication decision.
It still cannot be made public until source rights and the remaining human gates
are cleared.
