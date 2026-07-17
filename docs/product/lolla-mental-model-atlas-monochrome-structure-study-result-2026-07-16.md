# Mental Model Atlas Monochrome Structure Study Result

Status: local founder validation ready; unpublished

Date: 2026-07-16

Decision:

`monochrome_structure_study_ready_for_founder_validation`

## Executive result

The rejected color treatment has been removed rather than cosmetically toned
down. Atlas, Library, and the Abstraction model page now use no chromatic color.
The system is deliberately limited to white, gray, black, typography, spacing,
rule weight, line form, direction, and structural movement.

This is a study of the visual skeleton, not a final brand proposal. Its purpose
is to establish whether the product can feel coherent before color is allowed
back into the system.

The earlier user-journey corrections remain:

- a first model viewport contains what the model does, when it helps, what to
  watch for, and the entry into the learning journey;
- the model title no longer consumes most of the screen;
- source reading remains one chapter at a time with an explicit full-article
  mode;
- the four page destinations use the human labels **Understand**, **Use it**,
  **Connections**, and **Perspective**;
- internal fixture and renderer controls are absent by default and available
  only through `/atlas?review=1`;
- Library and Atlas use visitor language rather than projection, phase, frozen-
  slice, confidence, or canonical-ID vocabulary;
- the unfinished Learn route is not advertised as an active primary
  destination.

Provider calls: 0.

Provider cost: `$0.00`.

## What the line system means

The previous pass used color on narrow borders. Those borders were still
arbitrary decoration. This pass gives every line an explicit job:

- a light hairline separates related information;
- a dark rule marks a major product boundary;
- a solid line means ally;
- a dotted line means tension;
- a dashed line with a cross means antagonist;
- an arrow preserves authored source-to-target direction;
- a heavier rule or monochrome fill means selected, focused, or current;
- an animated underline reveals navigation state;
- graph motion changes camera or selection state rather than decorating the
  page.

Relationship type is therefore readable without hue. The selected Abstraction
Atlas slice displays three solid ally edges, one dotted tension edge, and one
dashed antagonist edge. The complete model page still exposes all 12 exact
incident records: seven ally, four tension, and one antagonist, with five
authored from Abstraction and seven authored toward it.

No model, relationship, type, direction, parallel record, source line, or
generated source artifact changed.

## First-time visitor review

The pages were exercised in a real browser as a visitor rather than reviewed
only from components.

At 1,440 by 900, the Abstraction orientation panel begins at approximately 229
pixels and ends at 438 pixels. The next learning section begins at 571 pixels,
so useful orientation and the next step both appear in the first viewport.
The desktop document has no horizontal overflow.

At 320 pixels wide, the document remains exactly 320 pixels wide and every
visible link, button, input, select, and disclosure target is at least 44 by 44
pixels. The 390-pixel model and Atlas entries preserve their hierarchy without
horizontal overflow.

The full-article control exposes all five reviewed source chapters. Atlas model
selection exposes one selected node and the five exact in-slice relationships.
The model relationship tabs preserve all three written and geometric line
forms. Reduced-motion preference disables the motion control, reduces the
camera transition to the clean near-zero fallback, and leaves no active
animation.

Browser computed-style inspection found zero visible chromatic values across
the reviewed Atlas, Library, model, selected, disabled, and relationship
states. Pixel inspection of all eight evidence screenshots also found zero
pixels whose red, green, and blue channels differ.

## Human and technical content boundary

The primary model journey now contains material that helps a person understand
and use the model. It does not foreground source-file locators, record names,
normalization state, confidence, compiled-curation labels, or evaluation
terminology.

That is a presentation change, not evidence deletion. Exact source and
relationship custody remain in the underlying projection, artifacts, tests,
and bounded review disclosures. The current page remains partial because only
Abstraction has a reviewed complete article and the broader Teacher journey is
not implemented.

## Failure, loading, and accessibility states

Unavailable pages, loading, source failure, completed-zero search, disabled
controls, keyboard focus, selected graph nodes, and reduced motion remain
explicit states. The graph no longer leaks the browser's default blue focus
ring: focus is represented through the same black node and line grammar while
remaining visible.

Relationship meaning remains redundant through text and geometry. Model
relationship tabs retain roving keyboard focus. The mobile Atlas keeps a
list-first entry because a graph canvas is not the best first interaction on a
narrow touch surface.

Native VoiceOver, NVDA, and JAWS review remains open. Browser structure and
target measurements are not a claim of native screen-reader certification.

## Verification

- Atlas frontend tests: 43 passed across 9 files.
- Monochrome guard: all color literals in the new visual layer are achromatic.
- Production TypeScript and Vite build: passed.
- `ModelPage` chunk: 34.32 kB raw and 10.52 kB gzip.
- Browser desktop, mobile, narrow-width, graph-selection, relationship-tab,
  full-article, focus, and reduced-motion checks: passed.
- Rendered screenshot chromatic-pixel count: zero across all eight captures.
- Provider calls and cost: 0 and `$0.00`.

The complete repository suite passed 5,011 tests and all 93 subtests, with the
one existing `datetime.utcnow()` deprecation warning. Its first run exposed one
historical-test coupling:
the frozen vibrant-editorial evidence test required its old navigation labels
to remain in the current `ModelPage.tsx`. The repair keeps the old evidence
immutable, verifies those labels in its historical result document, and lets
current-interface assertions follow the current visitor language.

## Evidence

The browser packet is
[`lolla-mental-model-atlas-monochrome-structure-study-2026-07-16`](evidence/lolla-mental-model-atlas-monochrome-structure-study-2026-07-16/README.md).
The machine-readable receipt is
[`lolla-mental-model-atlas-monochrome-structure-study-evidence-v1.json`](../evals/lolla-mental-model-atlas-monochrome-structure-study-evidence-v1.json).
The implementation plan is
[`lolla-mental-model-atlas-monochrome-structure-study-plan-2026-07-16.md`](../../plans/lolla-mental-model-atlas-monochrome-structure-study-plan-2026-07-16.md).

The former vibrant-editorial packet remains historical evidence of the
superseded direction. It is not relabeled as the current design.

## Product boundary

This is still a local Phase 1 product tracer. It does not create 221 additional
complete model pages, create Teacher journeys, connect Atlas to Lolla runtime
or Observatory, clear source rights, prove comprehension, or prove real-user
usefulness.

It also does not decide the future palette. If the founder accepts the
structure, color should return only in a separate study with a named semantic
job and a much smaller visual budget. No color decision is implied by this
checkpoint.

## Exact founder decision

Review `/models/abstraction`, `/atlas`, and `/models` and decide whether this
monochrome hierarchy and line grammar are a credible base. Acceptance means
the structure may proceed to a separate color study. It does not authorize
publication, deployment, Phase 2, Teacher journeys, runtime links, provider
use, or product-usefulness claims.
