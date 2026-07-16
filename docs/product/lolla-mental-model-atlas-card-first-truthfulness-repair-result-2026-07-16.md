# Mental Model Atlas Card-First and Guided-Reader Repair Result

Status: local founder review ready; unpublished

Date: 2026-07-16

Decision:

`guided_reader_abstraction_repair_ready_for_founder_validation`

## Executive result

The local Abstraction page is now a guided human learning page rather than a
source dump followed by technical cards. It begins with three exact
source-derived orientation cues, presents the canonical article in five focused
chapters with a persistent sense of place, continues into practical guidance,
and groups the exact graph neighborhood by the kind of intellectual relationship
it offers.

The founder's follow-up identified two separate defects in the first card-first
repair:

1. the complete source was truthful but still behaved as one very long scroll;
2. technical and curation material appeared in the same reading flow as material
   intended to teach a person.

The repair keeps the exact source, graph, and knowledge-graph custody while
changing their presentation boundary. The ordinary reader sees 55 substantive
source lines in the five-step learning sequence, the source title in the hero,
and four dated relationship-curation lines only in a collapsed source appendix.
No substantive source line is deleted or silently reclassified as irrelevant.

The truthful current statement is:

> The Abstraction source is complete and its default presentation is a reviewed
> five-step human reading projection. The broader Teacher product remains
> partial.

Provider calls: 0.

Provider cost: `$0.00`.

## Human journey now implemented

The default path is:

1. **Understand the idea** — definition, purpose, and memorable analogies.
2. **Use it in practice** — frameworks, examples, decisions, and communication.
3. **Know its limits** — strengths, weaknesses, and the risk of detaching from
   reality.
4. **See the connections** — the source's explanation of models that reinforce
   or challenge abstraction.
5. **Apply it safely** — risks, mitigations, and premortem questions.

Only one source chapter is shown at a time in guided mode. The chapter rail
stays visible, marks the current step, and supplies explicit previous/next
actions. Selecting another chapter returns the reader to a stable reading
position rather than leaving them at an unexplained page offset.

An optional **View exact source as one document** control opens all five chapters
and the source appendix in source order. That mode preserves browser search,
copy, print, and audit use without making the complete document the default
learning experience. Print CSS exposes the complete source even when the screen
is in guided mode.

## Human versus technical material

The exact 126-line, 14,518-byte source partitions into:

- one source title used by the hero;
- 55 substantive lines in the primary five-chapter learning sequence;
- four substantive lines in the collapsed source-curation appendix;
- structural blank lines, headings, table delimiters, and horizontal rules that
  remain accounted for by the exact line map.

The four appendix lines are the dated, slug-form **Structured Tension Curation**
record. They are still authoritative source bytes, but they function as a
maintenance/curation ledger rather than as the next step in a person's learning
journey. Weaknesses, risks, mitigations, relationship explanations, and
premortem questions remain primary human material; the cleaner layout does not
hide the restraints that keep the model honest.

Derived technical fields follow the same rule:

- use and avoid guidance is immediately visible;
- premortems, heuristics, and failure modes are available as an optional
  practical toolkit;
- record names, slugs, source locators, extraction labels, and evidence custody
  are behind explicit review disclosures;
- page coverage, hashes, and nonclaims remain inspectable but do not interrupt
  the lesson.

## Graph and connection meaning

All 12 exact Abstraction-incident relationship records remain available, with
parallel records preserved. The default presentation no longer asks a human to
scan 12 structurally similar cards in one run. It offers three deliberate views:

- **Works with** — seven ally records;
- **Productive tensions** — four tension records;
- **Direct conflicts** — one antagonist record.

Each visible relationship tells the reader which other model is involved, what
kind of relationship it is, whether Abstraction points to that model or that
model points to Abstraction, and the checked-in plain-language relationship
story. Source indices, confidence, and authored-direction custody are available
in a disclosure. The graph is a route to comparison and further learning, not
a ranking or proof of relevance.

## Source-bound interaction contract

The additive v2 page now includes
`lolla.atlas_human_reader_projection.v1`. It fixes, for this reviewed source:

- the five chapter IDs, labels, order, source line ranges, and orientation copy;
- the default chapter and single-open guided interaction;
- the exact source appendix range and collapsed default;
- three orientation cues copied from exact source lines;
- a lossless substantive-line partition with no unassigned or duplicated lines;
- explicit nonclaims that this projection is not a source rewrite, corpus-wide
  heading classifier, permission to delete appendix lines, or a completed
  Teacher journey.

The Python builder and TypeScript loader both reject chapter gaps, overlaps,
wrong heading boundaries, orientation-copy drift, appendix drift, or false line
accounting. The renderer does not infer this hierarchy from headings at runtime;
the reviewed projection is checked in and hash-bound.

## Frozen and additive custody

Frozen Phase 1 v1 anchors remain byte-identical:

- v1 manifest: `203999a61dbe9c2e943bbcb9f5b4dd87779d4557ea9fcfbd50b3e9d59e816c52`;
- v1 model page: `8cc07cbbf68f399dcd5787df9067bd3a3646068b59ed691ca043ffc9e9ce406f`.

Current additive v2 anchors:

- canonical source: `6d689abd7ae1f8022e2450b045b0f03ffc57700f8298ff858018d808845f5650`;
- canonical KG record: `ec28ee731944e7760dd574a401593d4dac1373ad69d3d080f9e58a4ebd19daef`;
- v2 model page: `46a666bb276c1ebdcb6ecd4045cbb440fcb0538b5a0ca7d2abc813f113f4512d`;
- v2 manifest: `41f4f19d98d94335993b28b734fae4100ad0dc5b622bd4f7bf93f037640dabdd`.

The additive package remains under
`apps/mental-model-atlas/public/data/card-first-v1/`.

## Browser review

The first card-first page was source-complete but visually blocked as a human
journey by an independent browser review: the full page occupied roughly 20
desktop viewports and 29 mobile viewports, and its flat chapter rail did not
preserve location after a jump.

The current real-browser review at 1440×900 and 390×844 found:

- default full page after the final technical-footer collapse: approximately
  7.9 desktop or 9.5 mobile viewports;
- default source-reading area: approximately 2.6 desktop or 3.3 mobile
  viewports;
- one visible source chapter in guided mode;
- one visible connection group rather than all 12 records at once;
- sticky current-step orientation on desktop and mobile;
- active chapter beginning below the sticky mobile navigation with no overlap;
- zero page-level horizontal overflow at 390 px;
- exact-source full-document mode still available.

The independent follow-up returned `ACCEPT` with no blockers at 1440×900,
390×844, or 320×780. It also verified previous/next behavior, keyboard entry,
sticky orientation during deep scrolling, full-source mode with all 60 unique
source lines, the collapsed source appendix, operational-toolkit disclosure,
connection-group switching, and controlled table overflow. It identified only
non-blocking polish: the desktop start action sits slightly below the first
viewport, later mobile chapter buttons can be outside the horizontally scrolled
button strip even though the textual current-step label remains visible, and
terminal Next briefly returns focus to the document body.

The current review packet is
`docs/product/evidence/lolla-mental-model-atlas-guided-reader-2026-07-16/`.
The earlier card-first screenshot packet remains historical evidence of the
superseded long-scroll composition; it was not deleted or relabelled as the
current experience.

## Architecture trade-off

One independent architecture audit preferred a continuous source document with
passive scroll-spy navigation because it maximizes always-visible source custody.
The founder feedback and independent visual audit instead established that the
default continuous document was not a usable learning journey. The implemented
compromise makes one chapter visible at a time for ordinary reading while
retaining an explicit full-source mode and print expansion for inspection.

This is a local product judgment for the Abstraction tracer, not a corpus-wide
rule. Founder validation must still decide whether the guided progression feels
natural and whether the full-source escape hatch is sufficient.

## Verification

The machine-readable receipt is
[`lolla-mental-model-atlas-card-first-repair-evidence-v1.json`](../evals/lolla-mental-model-atlas-card-first-repair-evidence-v1.json).
Final checks:

- card-first plus frozen Phase 1 Python tests: 31 passed;
- PRD contract and the two initially timed-out Observatory tests: 6 passed;
- Atlas Vitest in the ordinary parallel configuration: 33 passed;
- Atlas Vitest in a single-worker diagnostic configuration: 33 passed;
- TypeScript check: passed;
- production build: passed; model-page route chunk 32.75 kB raw and 9.99 kB
  gzip;
- dependency audit: zero known vulnerabilities;
- complete repository suite: 5,009 passed and 93 subtests passed;
- warning: one existing `datetime.utcnow()` deprecation;
- Stage 0 register: valid with 25 components, 24 connections, 17 Constitution
  findings, 26 Decision Trail groups, and 639 accounted implementation files;
- follow-up changed Markdown links: 32 checked, zero missing;
- four changed JSON artifacts parsed;
- changed Python compiled;
- `git diff --check`, added-material secret scan, and Git object integrity:
  passed.

The first repository-wide run exposed two stale PRD status assertions, which
were updated to the explicit guided-reader state, plus two Observatory HTTP
timeouts. Both Observatory tests passed immediately in a focused six-test run.
The final repository-wide rerun passed all 5,009 tests. A Vitest AtlasPage load
test also timed out only while the Python full suite was saturating the machine;
it passed alone, in the serial diagnostic run, and in the final ordinary
parallel run after that load ended. No product code was changed to hide either
environmental timing event.

## Nonclaims and next decision

This page does not prove teaching usefulness, comprehension, mastery, graph
relevance, relationship truth, content rights, public-deployment readiness,
Teacher journey quality, or behavior across the other 221 models. Native
VoiceOver/NVDA/JAWS review remains open. The app remains local and disconnected
from Lolla's live pressure runtime and Observatory.

The next decision is founder validation at `/models/abstraction`: does the
five-step source journey now feel understandable, navigable, and human; do the
practical and connection continuations add context without turning the page
back into a technical artifact; and is the optional full-source mode the right
custody escape hatch? A positive answer still does not authorize publication,
Phase 2, Teacher journeys, the other model pages, or runtime integration.
