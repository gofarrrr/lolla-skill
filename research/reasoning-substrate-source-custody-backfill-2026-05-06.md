# Reasoning Substrate Source Custody Backfill

**Date:** 2026-05-06
**PR slice:** PR26 - source custody backfill
**Status:** deterministic custody-only infrastructure
**Decision label:** `source_custody_backfill_complete`

## Verdict

PR26 completes repo-local source custody for the full 222-model runtime
substrate without extracting new affordance records or changing runtime
behavior.

This changes the source layer only:

- Runtime graph models: `222`.
- Repo-local source custody entries: `222`.
- Runtime model IDs missing source custody: `0`.
- v4 reviewed affordance records: still `55`.
- Graph-only runtime models after v4: still `167`.

The important distinction remains:

> 222 source files in custody does not mean 222 reviewed v4 affordance records.

PR26 makes the source truth reviewable, hashable, quotable, and available for
future controlled extraction. It does not add source-backed v4 depth for the
remaining graph-only models.

## What Changed

PR26 copied the remaining `167` canonical markdown files from:

`/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216`

into:

`data/model_sources/`

The existing `55` files already in source custody were byte-identical to the
canonical files and were left unchanged. The manifest was regenerated from the
runtime graph's `source_file` references.

The manifest now records, for every runtime model:

- `model_id`
- `filename`
- repo-local `path`
- `sha256`
- byte count

## Validation Added

PR26 adds `engine/system_b/source_custody.py`, a deterministic report helper
that checks:

- runtime graph model count;
- manifest model count;
- duplicate manifest model IDs;
- manifest IDs outside the runtime graph;
- runtime model IDs missing from the manifest;
- local source file existence;
- local SHA-256 match against manifest;
- local byte-count match against manifest;
- canonical source file existence;
- local/canonical SHA-256 match.

Focused tests in `tests/test_reasoning_substrate_source_custody.py` prove the
full custody state:

- manifest covers all `222` runtime models;
- all local files exist and match manifest hashes/byte counts;
- all local files match canonical markdown bytes.

The PR25 coverage audit module also now exposes clearer post-PR26 fields:

- `source_custody_model_count`
- `runtime_model_ids_missing_source_custody_count`
- `runtime_model_ids_missing_source_custody`

## What Did Not Change

PR26 did not:

- create or modify affordance records;
- modify `data/compiled/model_affordances/affordances_v4.json`;
- extract the remaining `167` v4 records;
- run model calls or judges;
- change prompts;
- rewrite lanes;
- run live lanes to build packets;
- wire `/lolla`, Observatory, memo, Step 8, Step 6, or Lane 4 runtime;
- choose final pressure;
- create user-facing Decision Pressure output.

## Product Meaning

PR25 made the packet road executable. PR26 makes the source road dependable.

The next bottleneck is no longer "can future extraction quote repo-local source
truth?" It can. The next bottleneck is whether packet fixtures show that
compact enriched cards are useful to the next LLM/reviewer before extraction
expands.

Recommended next slice:

1. Build one tiny reviewed packet fixture from explicit nominations.
2. Include a mix of v4-reviewed, graph-only, and newly custodied-but-not-yet-v4
   models.
3. Inspect whether the packet is compact, source-aware, and useful for LLM
   judgment.
4. Only then start a first extraction batch of 20-30.

Decision label for that next slice should be something like
`static_packet_fixture_review_complete`, not runtime promotion.
