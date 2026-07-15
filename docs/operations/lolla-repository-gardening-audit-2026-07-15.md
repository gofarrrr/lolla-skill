# Lolla repository gardening audit

Date: 2026-07-15

Status: provider-free operational snapshot and disposition; no deletion,
closure, migration, or history rewrite performed

Canonical base: `fc30bd944bfb91fbff0cc09190487997f3fe3185`

## Executive result

The repository is mechanically healthy but visually dense. Current product
truth was difficult to recover because a small live system, several bounded
artifact workflows, substantial prototypes, and a large research history were
presented on similar documentation planes.

This pass fixes the entrypoint problem. It does not pretend that every old file,
branch, pull request, generated generation, or local worktree should be removed.
The correct gardening order is classify, establish precedence, validate a fresh
clone, then authorize any destructive or storage-changing cleanup separately.

## Snapshot

Measured from the maintainer checkout on 2026-07-15:

| Measure | Count or size | Interpretation |
|---|---:|---|
| Tracked files | 9,260 | Large enough that root navigation must carry lifecycle status. |
| Markdown files | 1,579 | Historical product/research prose can overwhelm current truth. |
| JSON files | 6,216 | Mostly evidence, generated artifacts, contracts, manifests, and fixtures; existence is not integration. |
| Python files | 1,288 | Includes live code, bounded tools, research runners, and tests. |
| Research files | 5,282 | Scientific and development history dominates file count. |
| Eval-document files | 281 | Extensive evaluation estate; mostly offline or research-only. |
| Fixture files | 157 | Bounded contract inputs, not real-user evidence. |
| Compiled-data files | 122 | Multiple generations are retained; current-use identity must come from live contracts. |
| Approximate tracked working-tree size | 450.1 MiB | Public clone/storage friction deserves a separate data-custody review. |
| Git packed-object size | 61.52 MiB | Git transport is smaller than the expanded working tree but not trivial. |
| Remote refs under `origin` | 241 | Large historical branch estate; no bulk deletion is justified without ancestry/PR custody review. |
| Open pull requests | 14 | Mostly old research/feature work; current lifecycle is unclear from GitHub alone. |
| Registered local worktrees | 7 | Maintainer-machine state, not repository product truth. |

The largest tracked file observed was `data/embeddings.db` at roughly 41.4 MiB.
Large compiled affordance generations and frozen probe artifacts account for
many other multi-megabyte files. This audit does not decide whether any of them
belong in Git LFS, release assets, generated caches, or the repository.

## Open pull-request estate

The following PRs were open at the snapshot:

- #191 `docs/first-principles-system-story`;
- #174 `feature/html-case-learning-artifact`;
- #173 `feature/bevelin-safe-local-substrate-experiment`;
- #172 `feature/bevelin-lane1-treatment-audit`;
- #86, #85, #84, #83, #82, #81, #80, #78, and #77 from the early
  knowledge-substrate sequence;
- #63 `research/cross-lane-design-intent-2026-04-27`.

These are operationally stale relative to the Stage 0 map, but “stale” does not
mean safe to close. A later GitHub-custody goal should inspect exact ancestry,
review discussions, superseding commits, and any unique evidence before
closing or labeling them.

## What this gardening pass changes

- root README is a current public orientation rather than a 1,500-line
  development chronology;
- `PROJECT_STATUS.md` becomes the short current-state contract;
- `HOW_IT_WORKS.md` describes reachable architecture and bounded seams;
- `docs/README.md` organizes documentation by lifecycle;
- historical-reading guidance explains status precedence and immutable evidence;
- contribution rules make provider, privacy, integration, and claim boundaries
  explicit;
- current board/product/eval indexes lead with lifecycle status;
- the old Decision Work and Product Delta milestone-name contract lives in a
  lifecycle-labeled historical registry instead of requiring those names in
  both public root documents;
- a deterministic validator prevents selected stale claims from returning to
  the current entrypoints;
- a cold-reader record makes the ten essential orientation questions explicit.

Git history at the Stage 0 merge preserves the exact former root README and
HOW_IT_WORKS chronology. The underlying historical documents remain in place.

The first repository-wide test run after shortening the root documents exposed
60 historical discoverability test modules that still treated both root files
as an append-only milestone registry. Their expected titles and exact locators
were preserved in
[`docs/history/decision-work-product-delta-discoverability.md`](../history/decision-work-product-delta-discoverability.md),
and those tests now read that explicit historical surface. This changes where
historical names are discovered, not the frozen evidence, historical artifact
content, or live behavior.

## Dispositions

### Keep current

- `README.md`, `PROJECT_STATUS.md`, `HOW_IT_WORKS.md`, `AGENTS.md`,
  `CONTRIBUTING.md`, and `docs/README.md` as the public/cold-start layer;
- the Decision Work and Product Delta registry as the compatibility surface
  for historical discoverability tests;
- Constitution v5, Stage 0 addendum, machine register, and restart roadmap as
  controlling development/evidence boundaries;
- `SKILL.md` and `docs/skill/STEPS.md` as live behavior contracts.

### Preserve without broad editing

- frozen experiment evidence;
- historical plans and results;
- research and review artifacts;
- test fixtures and fake transports;
- current compiled substrate generations until a separate source-of-truth and
  reproducibility audit decides their storage.

### Park operational cleanup

- branch deletion or archival;
- closure/labeling of the 14 historical PRs;
- removal of stale local worktrees or movement of local `main` pointers;
- Git LFS, release-asset, generated-cache, or artifact-store migration;
- file-by-file rewriting of 1,500+ historical Markdown documents;
- pruning of compiled-data generations.

### Retire from product interpretation

- treating file count, imports, tests, PR titles, or polished fixtures as proof
  of one integrated product;
- treating old “next step” language as authorization;
- treating R4 readers as live or Decision Work semantic supply.

## Maintainer worktree custody

The founder-owned shared worktree had 64 pre-existing dirty entries when this
pass began. It was not switched, staged, stashed, reset, cleaned, committed, or
used for publication. Work occurred in isolated worktrees from canonical
remote `main`.

Absolute local paths are operational details and are intentionally not part of
the product contract.

## Remaining risks

1. Historical documents still contain old status and proposal language. The
   lifecycle entrypoints now control, but search results can still land on an
   old file directly.
2. The repository is large for a public skill. Clone and checkout friction may
   reduce adoption even if Git transport remains manageable.
3. Many open PRs and remote branches make repository governance look unfinished
   until separately classified.
4. The live skill contract itself contains calibrated model/provider claims
   that can age; provider-facing work needs freshness checks.
5. A mechanical cold-reader validator cannot substitute for an independent
   human reviewer.

## Recommended later operations goals

These are separate decisions, not automatic continuation:

1. **Historical PR and branch custody audit:** classify every open PR and remote
   branch as merged/reachable, unique evidence, active, or safely closable.
2. **Large-artifact source-of-truth audit:** identify which data are source,
   reproducible build output, cache, fixture, or immutable evidence before any
   migration.
3. **Historical-search landing review:** add lightweight status banners only to
   the highest-traffic stale entrypoints, without rewriting frozen evidence.

None is required to start the separately authorized Stage 1 truthfulness gate,
but the first two matter before calling the repository operationally tidy at
scale.
