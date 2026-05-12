# Bevelin Safe Local Baseline

Date: 2026-05-12

## Branch And Base

- Branch: `feature/bevelin-safe-local-substrate-experiment`
- Base branch at experiment start: `feature/bevelin-lane1-treatment-audit`
- Base commit: `043d15c`
- Working tree note: unrelated untracked planning/research files existed before this experiment and were not staged or edited for this work.

## Default Runtime Artifacts

These paths are baseline/read-only for this experiment:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `data/compiled/model_affordances/affordances_v60.json` | 6029605 | `4dea740ecf71894a8b56146502983c4d3e448f24a6628a8430a445b3c47bedc8` |
| `data/curated/subpattern_catalog.json` | 282645 | `9bc69584261374195f1fd754ec058e42a7c9ff556ad86f6417b0a8c784e2efce` |
| `data/embeddings.db` | 43368448 | `cc9b81315060b32cd62fa69db7d025fdb83559c6e53496d9b5504153a84e5b8d` |
| `research/v60-embedding-balanced-4211-case-manifest-2026-05-10.json` | 26622 | `23b1d2e141d02298bd5ddb34750d48cdfea30d7ed6f7fe8d84e0d08e9945a4e7` |

## Safety Contract

- Do not overwrite `data/compiled/model_affordances/affordances_v60.json`.
- Do not edit live `/lolla` runtime defaults.
- Do not create a Bevelin lane, Bevelin card, Bevelin score, or public Bevelin product label.
- Keep candidate substrate behind an explicit path:
  `data/compiled/model_affordances/bevelin_candidate/affordances_v60.json`.
- Preserve the V60 contract that replay/runtime paths require a file named
  `affordances_v60.json` and artifact id `model_affordances_v60`.
- Use source-backed records and the existing V60 selector/ledger machinery.
- Stop before paid or live LLM calls if dry replay shows candidate chunks do not
  naturally enter packets.

## First-Wave Candidate Scope

| Unit | Decision |
| --- | --- |
| BVL-04 absolute yardstick | Candidate overlay on `baseline-establishment`. |
| BVL-06 role-reversal system fairness | Candidate overlay on `obligations-controls-mapping`. |
| BVL-08 postmortem / learning trace | Control/duplicate check against `hindsight-bias` and feedback records. |
| BVL-01 disconfirmation / prosecutor test | Control/duplicate check against `falsifiability` and adjacent records. |

## Stop/Go Gates

- Stop if candidate records fail source validation.
- Stop if candidate compile mutates the default V60 artifact.
- Stop if candidate chunks only work under explicit forced nominations and do
  not enter normal 8-case replay packets.
- Stop if outputs would need broad prompt stuffing or a new architectural layer.
- Continue only if candidate substrate reaches relevant packets and creates a
  credible private reasoning opportunity without bloat or machinery leakage.
