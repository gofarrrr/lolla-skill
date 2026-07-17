# Mental Model Atlas baseline consolidation result — 2026-07-17

Status: complete locally, provider-free, unpublished.

Decision: `adopt_single_canonical_identity_path_preserve_review_and_historical_assets`

## Executive result

The Atlas now has one explicit ordinary ownership path:

```text
16-model orientation view
  -> select an exact canonical model
  -> navigation-v1 owns model and relation identity across all 222 models
  -> exact incident-neighborhood page from 1,358 checked-in relations
  -> model/relation route keeps that canonical identity
  -> complete teaching page only when a reviewed page artifact exists
```

The 16-model landing view remains an intentional orientation presentation. A
deterministic regression test now proves that every model and relation record
it shows is byte-equivalent to the canonical navigation package. It no longer
acts as a competing identity source after navigation.

This closeout fixes the harmful overlaps found by a cold-start architecture
audit. It does not delete historical evidence, claim product usefulness,
authorize publication, or connect Atlas to the live Lolla runtime.

## What was repaired

1. **Canonical identity survives route changes.** A canonical model outside the
   16-model orientation slice now opens as a real summary-only model instead of
   “not found.” An exact canonical relation likewise remains navigable and
   returns to a neighborhood that can actually load it.
2. **Projection loading is route-scoped.** Atlas and Library load presentation
   projections. Learn, complete model pages, and relation pages no longer load
   the old Phase 1 projection merely to fabricate a fallback lookup.
3. **Page availability has one owner.** The card-first page registry now decides
   whether a complete model page exists. The unused legacy model-page loader and
   its duplicate availability helper were removed from the active code.
4. **Review paths are isolated.** Frozen fixtures and Canvas comparison remain
   available only with explicit `review=1`. Ordinary URLs ignore and remove
   `fixture` and `renderer` parameters.
5. **Relationship language has one owner.** Ally, antagonist, and tension
   labels and line names now come from `src/relationPresentation.ts`: solid,
   dashed, and double. Direction remains a separate source-to-target property.
6. **Cross-route CSS ownership is scoped.** Relation-page fact rules no longer
   override the Atlas selection panel through a shared global class name.
7. **Unsupported state was removed.** The unused runtime `family` state and
   unused hovered-relation state are no longer presented as implemented
   behavior. The future family route in the PRD remains a proposal, not a live
   contract.
8. **The full-stack whitespace defect was repaired prospectively.** Frozen
   commits were not rewritten.

Code checkpoint: `0d85d39fdcef181bd657d6849013c3a1aa978a5f`.

## Lifecycle map

### Active local product candidate

- one modular stylesheet entrypoint: `src/design-system/index.css`;
- one binding visual contract: `apps/mental-model-atlas/DESIGN_SYSTEM.md`;
- SVG editorial graph for ordinary visitors;
- 16-model canonical orientation presentation;
- 222-model / 1,358-relation canonical navigation identity package;
- exact 40-record incident-neighborhood paging;
- card-first Abstraction page as the only complete model teaching page;
- one complete exact relation teaching page;
- truthful summary-only fallbacks for every other canonical identity;
- Library, accessible text view, loading, zero, missing, and failure states.

### Explicit review-only

- Canvas comparison renderer;
- parallel, bidirectional, medium-confidence, and historical Confirmation Bias
  fixture routes;
- fixture and renderer selectors;
- screenshot packets and browser-review receipts.

Review-only paths require `review=1`. They are not competing ordinary product
routes and do not determine canonical identity.

### Immutable or superseded evidence

- Phase 1 projection package and manifests;
- six historical Confirmation Bias fixture pages;
- earlier card-first, vibrant, monochrome, guided-entry, design-system, and
  graph-repair checkpoints;
- screenshots and exact evidence receipts.

Old “current” or “next decision” language inside those dated checkpoint notes
describes the state at that checkpoint. This baseline document and the current
repository indexes control present behavior. Preservation is deliberate; it is
not active compatibility code.

### Parked or forbidden

- Mental Model Teacher journeys;
- Atlas deployment or public publication;
- Atlas integration with the live pressure pipeline or Observatory;
- provider calls, generated relationship meaning, model ranking, or relevance
  inference;
- Phase 2 and real-user usefulness claims.

## Remaining boundaries

This is a clean implementation baseline, not a finished product claim.

- Only Abstraction has a reviewed complete model article.
- Only one relation has a reviewed complete relation page.
- Native screen-reader review, source-rights review, deployment review, and
  real-user usefulness evidence remain open.
- The initial 16-model view and canonical navigation index are two presentation
  packages by design, but a deterministic test now enforces one shared identity
  and relation meaning.
- Historical artifacts remain in the repository because custody rules prohibit
  deleting or rewriting evidence merely to make the tree look smaller.

## Verification at the code checkpoint

- navigation builder: 222 models and 1,358 relations validated;
- navigation tests: 4 passed, including orientation/canonical equivalence;
- Atlas application: 13 test files and 58 tests passed;
- TypeScript check: passed;
- production build: passed;
- dependency audit at moderate severity: zero vulnerabilities;
- complete repository suite: 5,016 passed and 93 subtests passed;
- one existing `datetime.utcnow()` deprecation warning;
- provider calls: 0;
- provider cost: `$0.00`.

Fresh-clone verification remains required before publication of the complete
branch.

## Cold-start rule

For Atlas work, read in this order:

1. this baseline result;
2. `apps/mental-model-atlas/DESIGN_SYSTEM.md`;
3. `apps/mental-model-atlas/README.md`;
4. the neighborhood-navigation result and machine evidence;
5. older dated result files only when investigating their specific frozen
   checkpoint.

Do not infer a new implementation goal from an older result's next-step prose.
The only present founder gate is whether this consolidated local branch should
be published and adopted canonically. Until that occurs, a deleted chat is
recoverable on this machine from the branch, but not from a fresh clone.
