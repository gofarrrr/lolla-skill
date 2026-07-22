# Lolla self-contained graph substrate and skill result

Date: 2026-07-22
Status: provider-free implementation complete; live semantic policy unchanged;
separate Atlas custody boundary resolved prospectively in V2
Repository authority: this repository only
Provider calls authorized or made: 0
Embedding calls or rebuilds: 0

## Result in plain language

The graph was not failing because it needed a graph database, global community
search, two-hop traversal, or more LLM calls. The main problem was ownership:
the published graph looked healthy, but a fresh contributor could not trace and
reproduce the complete path from the 222 Markdown sources through reviewed
curation and compilation into the exact pressure portfolio.

That ownership chain is now local and explicit:

```text
222 canonical Markdown files
  -> reviewed model and relationship curation
  -> source-anchor and compiler-input manifests
  -> deterministic candidate compiler
  -> exact published graph release
  -> one immutable published-substrate reader
  -> one versioned constitutional pressure planner
  -> active pressure + reserve
  -> apply / reject / park by the reconsidering reasoner
```

A GitHub user can clone this repository and validate that chain without the
founder's machine, another checkout, provider credentials, or a semantic
regeneration step. The root `SKILL.md` remains the one Lolla skill. Its setup
script now identifies the package that contains it instead of searching for a
different installed project.

## What was completed

### 1. Baseline and authority boundary

The provider-free baseline freezes:

- 222 canonical model identities;
- 1,358 rich authored relations: 523 ally, 344 antagonist, and 491 tension;
- 1,742 compact graph edges;
- 163 contiguous 60-model pressure-policy windows;
- 489 graph-active admissions;
- 265 graph-active admissions with multiple exact paths;
- 808 additional convergent exact paths not carried on the current outer active
  item.

Current setup, source, curation, compiler, manifest, test, and documentation
surfaces are scanned as repository-local authority. No current surface depends
on the retired recovery location.

### 2. Source and compiler reconstruction

All 222 active relationship-authoring records are under
`data/curation/relation_semantics/`. Their aggregate identity is:

```text
record_count: 222
total_bytes: 1,243,714
aggregate_sha256: a779626577a3f373a6882b68f5c0621e3cc2fb62935c13b3421ca2b2ca2ca3cd
```

All 1,358 published rich relations resolve to one active authoring record.
Source anchors preserve exact, normalized-only, unresolved, missing, and the
human-only synthesized/multi-span state separately. The present mechanical
classification is 605 exact spans, 14 normalization-only matches, 739
unresolved excerpts, and 0 missing sources. Unresolved does not mean false; it
means the declared excerpt was not mechanically locatable and was not silently
repaired.

The operational, intervention, reframing, prerequisite, structural-coverage,
and tendency inputs are also local and hash-locked. The existing compiler was
deepened rather than replaced. It requires an explicit candidate directory,
refuses the published directory, refuses compile-from-output fallback, performs
no provider call, and recreates both publication artifacts exactly:

| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `data/knowledge_graph.json` | `5689b79868339ce9221b799eac88870a6053b69a67ba3aaef3f2ba5cd62efdae` | 2,129,575 |
| `data/relationship_graph.json` | `89808c4585498f3880b4d7fa0110d64cd46f7acff312c0870fc6cb9a97e752cf` | 1,263,715 |

All 867 expected activation-condition embedding records are current. The check
opened the existing database read-only; it did not generate embeddings.

### 3. One published read boundary

`PublishedKnowledgeSubstrate` is the single current publication loader. It
provides immutable exact model and relation records, stable IDs, source order,
compiled pointers, available source custody, and directional outgoing,
incoming-reference, and incident indexes. Incoming-reference lookup preserves
the authored direction; it does not manufacture a reciprocal edge.

The reader distinguishes `complete`, `completed_zero`, `partial`, `failed`, and
`missing`. It does not compile, generate, repair aliases, rank candidates,
allocate pressure, rebuild embeddings, or call a provider. Live graph consumers
were migrated to the shared snapshot with exact adapter equivalence.

### 4. One current pressure planner

The existing constitutional policy now has one named owner:

```text
policy_id: lolla.constitutional_pressure_planner
version: 1.0.0
identity: sha256:829bd0c086610dafabb09b5c941580efcc511396a3ed8c5d3ea3673e17031b10
direct active cap: 6
expansion seeds: direct active only
direction: authored outgoing
hop depth: 1
slots: antagonist, tension, ally
```

The extraction did not change active or reserve identities, order, admission
edges, bounds, or portfolio hashes in any of the 163 frozen windows. It still
runs before probabilistic verification, so bounded graph pressure cannot be
silently domesticated before reconsideration.

### 5. Prospective complete path custody

A candidate-only projection now records expansion scope, expanded direct
seeds, unexpanded direct reserve, every bounded target, active/reserve
disposition, the winning admission path, and all exact provenance paths. Across
the frozen corpus it serializes 6,025 exact paths over 3,723 target records and
accounts for all 808 previously omitted convergent active-target paths. There
are no unaccounted paths.

This projection is intentionally not imported by the live pipeline, reasoner,
receipt, Decision Trail, Atlas, or Observatory. It is evidence that complete
custody is feasible without changing the current selection; it is not a silent
runtime promotion.

### 6. One self-contained skill package

The existing skill now has:

- one trigger description and one canonical ten-step runtime workflow;
- one repository-contained setup helper that resolves its own package root;
- consistent `/lolla` Claude Code and `$lolla` Codex installation surfaces;
- generated Codex-facing metadata at `agents/openai.yaml`;
- a directly linked, one-level graph operations reference;
- a provider-free readiness register and validator;
- an isolated package-copy test with provider keys removed.

The readiness command is:

```bash
PYTHONPATH=. python3 scripts/evals/validate_self_contained_skill.py --validate-only
```

It validates source custody, relation and compiler manifests, candidate
byte-equivalence, strict publication loading, all 163 pressure-policy windows,
skill structure, invoked helper presence, and current path authority. It does
not run Lolla and cannot spend provider tokens.

## Historical metadata boundary

One old absolute source-residency string remains inside the hash-locked
`affordances_v60.json` historical/live artifact. Rewriting that byte would
rewrite frozen evidence and change the artifact identity. It is therefore
declared as one exact SHA-locked exception with `active_dependency: false`.
Nothing resolves, opens, imports, validates, or runs from that path; current
setup, manifests, documentation, compiler inputs, and readiness checks all use
repository-local files.

This is a deliberately honest boundary: the repository has no active external
worktree dependency, but it does not falsify immutable provenance to make the
old artifact appear newly authored. Replacing that inert field requires a
prospective V60 artifact version and an explicit runtime-promotion review, not
an in-place cleanup.

## What this result does not establish

- A graph path is not relevance, truth, causation, or importance.
- A byte-identical compile does not prove that the authored semantics are wise.
- A schema-valid or complete receipt does not prove answer quality.
- One-hop outgoing policy is not proven better than incoming, multi-hop, or a
  no-graph control.
- The 808 recovered paths are custody evidence, not 808 useful insights.
- No accuracy, cost, real-user usefulness, market, or production claim follows
  from this work.
- No graph database, MCP connection, community detection, global graph search,
  continuous mutation, or automatic relation extraction was added.

## Frozen Atlas boundary found during full verification and later resolved

The graph repair deliberately changed repository-local custody metadata and
recovered the complete relation-authoring files. Those changes alter file
hashes that the older Atlas Phase 1, card-first, and navigation packages embed
as exact provenance. A field-by-field dry rebuild found 520 changed leaves
across the Phase 1 package: all 520 are SHA-256 custody fields; model meaning,
relation meaning, membership, ordering, layout, paging, and interface fields do
not differ.

The existing Atlas packages and their evidence receipts are explicitly frozen
checkpoints. They were therefore not rewritten to make the full suite green.
Seventeen Atlas exact-replay checks correctly expose the resulting boundary:
the old package is internally frozen, while the current source manifest and
relation-authoring files now have repository-local identities.

The graph/skill audit did not resolve that separate product boundary. In the
subsequently authorized Atlas custody V2 work, the safe prospective option was
implemented: six V1 artifacts remain hash-locked and byte-exact, three V2
packages carry current repository-local custody, and only the three active data
URLs moved. A recursive all-package comparison classified 2,182 custody-only
differences and zero unexpected differences. Model/relation meaning, identity,
order, layout, paging, and interface fields remain equal. The controlling
follow-up is
`docs/product/lolla-mental-model-atlas-custody-v2-result-2026-07-22.md`.

## Remaining graph opportunities, in decision order

1. Decide whether complete multi-path custody should become a live receipt
   field without changing which pressure is active. This is a transparency
   decision, not a recall expansion.
2. Build a source-first semantic evaluation before expanding traversal. Compare
   the exact current outgoing one-hop policy against named controls and measure
   distinct useful pressure, forced associations, cognitive load, provenance,
   and dispositions separately.
3. Only if that evaluation reveals a specific miss, test one alternative at a
   time: incoming references, direct-reserve expansion, or bounded two-edge
   paths. Never combine them into a “global graph” bundle.
4. Test the graph-to-V60 handoff offline if graph-only active models are being
   judged without enough source-backed transaction material.
5. Keep Atlas and other human-facing exploration outside this substrate task
   until the knowledge and policy question has an evidence-backed answer.

## Verification record

The provider-free verification record is:

- self-contained skill readiness: complete for 222 models, 1,358 relations,
  163 pressure windows, and byte-equivalent candidate publication;
- repository authority scan after custody V2: 2,288 current files, zero active retired-worktree
  references, and one exact inert frozen-artifact exception;
- Stage 0 register and public handoff after custody V2: valid, including 653 implementation
  files, 25 components, 24 connections, 10 cold-reader questions, and 110
  local documentation links;
- focused Phase 4–6 checks: 31 passed;
- frozen R3 and current wrapper regressions: 51 passed;
- broad repository suite before the Atlas V2 follow-up, with 17 frozen-Atlas
  checks and 20 commit-state-only skill guards separated: 5,020 passed, 93 subtests passed,
  and one existing `datetime.utcnow()` deprecation warning;
- the 20 historical Decision Work guards passed in a temporary Git metadata
  snapshot whose `HEAD` includes the authorized skill edits; they fail only in
  the real dirty worktree because their stated assertion is that `SKILL.md` and
  `scripts/skill/` have no uncommitted change;
- the later custody V2 proof restores all 17 Atlas exact-replay checks against
  current repository-local authority while preserving V1 exactly.

JSON validation, `git diff --check`, shell syntax validation, and the skill
creator's structural validator pass. Provider calls and embedding calls remain
zero.
