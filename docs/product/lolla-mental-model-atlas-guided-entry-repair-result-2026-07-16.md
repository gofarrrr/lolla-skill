# Mental Model Atlas Guided Entry Repair Result

Status: local founder-validation candidate; provider-free; unpublished

Date: 2026-07-16

Parent checkpoint: `5dab11434dc49d84326f05bc41f34bb7b117c157`

Decision: `breadcrumb_aligned_redundant_source_intro_removed`

## Executive result

The founder review exposed two real presentation defects on the Abstraction
page. The breadcrumb gave its link a 44-pixel interaction box without vertically
aligning the separator and current-model text to it. The guided source journey
also began with a second title page—`Original article`, `Learn Abstraction`, a
repeated source title, and a sentence instructing the visitor to read—before the
actual chapter navigator.

Both defects are repaired. `Model Library / Abstraction` now reads as one
aligned orientation line at desktop and mobile widths. The redundant source
introduction is gone, so `Understand` proceeds directly into the five-step
reader and its first source chapter.

No product reason justified keeping it. The repeated title and instruction did
not help the visitor choose, navigate, understand, or recover from failure. It
was source-custody residue promoted into the primary hierarchy.

## What remains

Complete source access remains available. The source document title is absent
from guided mode and returns only after the visitor explicitly selects `Read
the full article`. In that complete-source mode it has a legitimate job:
identifying the document whose five chapters are now visible together. Source
line 1 retains its exact custody marker.

The reader remains a labelled `Understand Abstraction` region with five
keyboard-operable chapter controls, explicit guided/full state, previous and
next actions, and the original source line mapping. No source, model,
relationship, graph, curation, or projection artifact changed.

## Browser evidence

At 1,440 pixels, all three breadcrumb text ranges resolve to vertical coordinate
`110.578125`. At 390 pixels they all resolve to `172.96875`. The mobile document
width remains exactly 390 pixels, so the repair creates no horizontal overflow.

The default guided state contains:

- zero `.source-layer-heading` elements;
- zero `.source-document-title` elements;
- five chapter controls;
- no visible repeated source title;
- a direct transition from the page path into the chapter navigator and source.

The explicit full-article state contains all five visible chapters and restores
`Comprehensive Briefing Document on Abstraction` under `data-source-line="1"`.

The four new screenshots remain achromatic at the rendered-pixel level. Their
hashes and sizes are recorded in the machine receipt and the
[evidence index](evidence/lolla-mental-model-atlas-guided-entry-repair-2026-07-16/README.md).

## Verification

- Focused ModelPage and monochrome tests: 11 passed.
- React/TypeScript check: passed.
- Complete Atlas tests: 43 passed across nine files.
- Production build: passed; `ModelPage` is 34.03 kB raw and 10.46 kB gzip.
- Complete repository: 5,012 tests and all 93 subtests passed, with the one
  existing `datetime.utcnow()` deprecation warning.
- Public-handoff and Stage 0 register validators: passed.
- Provider calls and provider cost: 0 and `$0.00`.
- Publication actions: none.

## Boundary

This repair answers the reported information-flow defects. It does not approve
the wider monochrome design, select a color system, complete other model pages,
clear source rights, certify native screen-reader behavior, prove learning
usefulness, authorize Phase 2, or publish the application.

The next founder review should judge the simplified breadcrumb and direct
guided-reader entry. Color remains deliberately outside this decision.
