# Plan: Mental Model Atlas custody V2 migration

Date: 2026-07-22
Status: complete locally, provider-free
Founder authorization: explicit in the 2026-07-22 graph/skill handoff
Provider and embedding calls authorized: zero

## Falsifiable question

Can the active Atlas data routes adopt the repository-local source manifest and
recovered relation-authoring hashes without rewriting V1 evidence and without
changing any model meaning, relation meaning, identity, layout, paging, or
interface field?

## Scope

1. Freeze the exact V1 Phase 1, card-first, and navigation package identities.
2. Build three prospective V2 custody packages from current repository-local
   sources and curation.
3. Compare every V1/V2 field and admit only source-custody, custody-release, and
   exact SHA-256 reference differences.
4. Keep layout hashes and complete model/relation identity vectors equal.
5. Change only the three active static-data URLs in the browser.
6. Preserve V1 artifacts and evidence byte-for-byte.
7. Update current tests, documentation, and restart commands.
8. Run the full provider-free repository and Atlas verification stack.

## Acceptance criteria

- [x] Six frozen V1 identities are unchanged.
- [x] Phase 1 V2 contains the same 12 artifacts.
- [x] Card-first V2 contains the same reviewed Abstraction page.
- [x] Navigation V2 contains all 222 models and 1,358 relations in the same
      order.
- [x] Every non-custody field is equal.
- [x] Every layout coordinate hash is equal.
- [x] All custody differences are explicitly classified.
- [x] The app loads `phase1-v2`, `card-first-v2`, and `navigation-v2` directly.
- [x] No extra fetch, fallback, semantic generation, or browser inference is
      introduced.
- [x] Provider calls and embedding calls remain zero.

## Boundaries

This migration is data custody maintenance. It does not authorize publication,
deployment, Atlas Phase 2, Teacher journeys, generated pages, relation
inference, styling changes, source-rights clearance, accessibility acceptance,
or a usefulness claim.
