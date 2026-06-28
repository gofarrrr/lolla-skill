# Risk Mode Implementation Plan v0

Status: docs/design-only implementation plan
Date: 2026-06-28
Review slice: `risk_mode_implementation_plan_v0`

PR39 turns PR36 policy, PR37 fixtures, and PR38 fixture review into a concrete
future implementation path. It does not implement that path.

PR39 itself is not runtime enforcement. It does not run `$lolla`, call models,
change runtime code, change prompts, change `SKILL.md`, mutate archives, add
tests, change `evaluation.py`, change `agent_result.py`, change
`archive_run.py`, change `caller_action`, change provider-boundary policy, add
answer-quality scoring, populate labels automatically, add crisis/domain
runtime protocols, add model-based risk classification, add
`conversation_understanding_ir.v0`, or add graph DB, embeddings, chunking,
memory, or specialist runtime integration.

## Source Decisions

This plan depends on:

- [Risk Mode Behavior Plan v0](risk-mode-behavior-plan-v0.md);
- [Risk Mode Fixture Matrix v0](risk-mode-fixture-matrix-v0.md);
- [Risk Mode Fixture Review v0](risk-mode-fixture-review-v0.md);
- [Live Output Hygiene Decision v0](live-output-hygiene-decision-v0.md);
- [Agent Result Contract](../lolla-agent-result-contract.md).

PR36 decided that risk mode is a custody, review, and reliance layer. It is not
answer-quality scoring, domain authority, or action approval.

PR37 created 12 fixture cases covering `quick`, `standard`, `deep`,
`high_stakes`, `stability`, and excluded/domain-review routing.

PR38 reviewed those fixtures. All 12 now pass as useful implementation gates.
PR38 also added the missing high-stakes user-values / stakeholder-obligation
conflict fixture.

## Smallest Future Behavior Change

The smallest useful future behavior change is:

```text
high_stakes reliance/readiness tightening
```

The first implementation should be test-first and should preserve the existing
contract before adding new behavior.

Plain-language target:

- if `risk_mode` is `high_stakes`, Lolla should remain conservative even when
  required saved artifacts are present and clean;
- clean product/custody artifacts should not become unrestricted agent
  readiness;
- otherwise clean `high_stakes` runs should preserve the current
  `caller_action: ask_user_first` contract behavior unless a later separate
  caller-action PR explicitly changes it;
- high-stakes reliance copy should explain that the answer may be reviewable
  while action still requires human or domain review;
- `high_stakes` must not become automatic failure, domain approval, or generic
  caution theater.

The first code-bearing PR after PR39 should therefore be a contract-lock slice,
not broad enforcement.

## Why Not Broader Enforcement

Do not start by making every risk mode change behavior.

Broad enforcement would create too many simultaneous failure modes:

- `quick` could become an excuse for thin custody or overclaiming;
- `deep` could be mistaken for proof that optional reviewers ran;
- `stability` could be confused with answer correctness;
- `high_stakes` could drift into domain authority or blanket refusal;
- `caller_action` could change without contract tests;
- clean artifacts could be treated as action approval.

The safest first behavior is narrower: lock and clarify high-stakes reliance
semantics that the contract already describes.

## Current State

Today:

- `LOLLA_AUDIT_MODE` accepts `quick`, `standard`, `deep`, `high_stakes`, and
  `stability`;
- invalid explicit values fail before model calls;
- normalized `risk_mode` persists into `result.json`, `agent_result.json`,
  `reasoning_trace.json`, and archive metadata;
- risk mode does not change prompts, cost, Step 7, capture strictness,
  evaluation scoring, live-output finalization, Observatory behavior, or
  `SKILL.md`;
- the agent-result contract already keeps otherwise clean `high_stakes` runs
  conservative with `caller_action: ask_user_first`;
- `evaluation.json` remains deterministic run-readiness, not answer wisdom;
- `safe_for_agent_use` remains human-owned in review artifacts.

PR39 does not change this state.

## Phased Implementation Path

### Phase 0: Current State

Status: already true.

- Risk-mode metadata exists.
- PR36 policy exists.
- PR37 fixtures exist.
- PR38 fixture review exists.
- `high_stakes` contract language already says otherwise clean runs stay
  conservative through `ask_user_first`.
- No new enforcement exists.

### Phase 1: Test-Only Contract Lock

Status: completed by PR40.

```text
tests/test_risk_mode_contract.py
```

Purpose:

Add tests that prove current high-stakes reliance behavior remains
conservative before any behavior change.

Completed work:

- contract tests proving otherwise clean `high_stakes` maps to
  `caller_action: ask_user_first`;
- regression tests proving clean `standard` behavior does not accidentally
  change;
- fixture-mapped tests for the PR37/PR38 high-stakes cases;
- tests proving degraded artifacts still block reliance regardless of live
  output;
- tests proving `live_output_health: not_checked` remains a caveat, not
  answer-level failure by default;
- tests proving review-corpus export preserves `risk_mode`, `caller_action`,
  and `caller_readiness`;
- tests proving contract wording remains approval-neutral;
- no behavior change;
- no `SKILL.md` change;
- no broad caller-action rewrite.

PR40 observed and locked the current reliance contract: a degraded high-stakes
run produces `caller_action: do_not_use_run_degraded` and evaluation
`caller_readiness: do_not_use`. PR40 does not introduce a new rule that every
contract-consistent degraded run must make `evaluation.overall` fail; future
artifact-clarity work may revisit that explicitly.

### Phase 2: Evaluation Artifact Clarity

Status: completed by PR41.

Purpose:

Make the conservative high-stakes reliance caveat clearer in artifacts, only
after Phase 1 tests lock current behavior.

Completed changes:

- `evaluation.json` now includes `risk_mode_reliance_policy` for
  `risk_mode: high_stakes`;
- otherwise clean high-stakes runs record the reliance caveat while preserving
  `caller_action: ask_user_first` and `caller_readiness: inspect_first`;
- degraded high-stakes runs record that risk mode does not override degraded
  run state, preserving `caller_action: do_not_use_run_degraded` and
  `caller_readiness: do_not_use`;
- standard clean runs do not receive the high-stakes caveat and retain current
  `use_revised_answer` / `ready` behavior;
- deterministic tests ensure high-stakes clean artifacts do not silently imply
  automatic agent use;
- no domain approval;
- no answer-quality scoring.

PR41 does not change `agent_result.json`, `caller_action`, prompts,
`SKILL.md`, runtime enforcement, or archive behavior.

### Phase 3: Review-Surface Integration

Status: completed by PR42.

Purpose:

Expose high-stakes reliance caveats in review and corpus surfaces without
enforcing runtime action.

Completed changes:

- review corpus records now include compact `risk_mode_reliance` metadata;
- high-stakes records expose PR41's `risk_mode_reliance_policy` status,
  `caller_action`, `caller_readiness`, human/domain review requirements, and
  `automatic_safe_for_agent_use: false`;
- standard records without the high-stakes caveat record `present: false`;
- human-review workflow tells reviewers that the caveat is not answer-quality
  failure, domain approval, or automatic agent-use approval;
- `safe_for_agent_use` remains human-owned.

### Phase 4: Later Runtime Behavior, Explicitly Approved

Only after Phases 1-3 are complete should runtime behavior be considered.

Any runtime PR must:

- cite PR36, PR37, PR38, and this PR39 plan;
- name exactly which fixture behavior changes and which remains unchanged;
- prove `standard` mode remains stable;
- preserve conservative high-stakes reliance;
- define rollback conditions;
- avoid domain authority;
- avoid automatic action approval;
- update contract docs;
- include tests before behavior changes merge.

## Future Test Plan

Future implementation PRs should include these tests before changing behavior:

| area | required checks |
|---|---|
| Risk-mode parsing | Missing/empty mode defaults to `standard`; explicit invalid mode fails before model calls; accepted values remain `quick`, `standard`, `deep`, `high_stakes`, `stability`. |
| Preservation | `risk_mode` persists consistently through `result.json`, `agent_result.json`, `reasoning_trace.json`, archive metadata, and any relevant evaluation record. |
| Agent result | Otherwise clean `high_stakes` returns `ask_user_first`; degraded runs return `do_not_use_run_degraded`; `standard` clean runs keep existing behavior. |
| Evaluation artifact | High-stakes reliance caveat is present if implemented; `evaluation.json` remains deterministic run-readiness, not answer-quality scoring. |
| Fixture mapping | PR37/PR38 fixtures preserve expected `safe_for_agent_use`, `caller_action`, answer-level, run-envelope, and live-output separations. |
| Regression | `quick`, `standard`, `deep`, and `stability` do not change accidentally while high-stakes tests are added. |
| Privacy | No raw transcript, memo, revised-answer, model/provider content, private reasoning, local absolute paths, secrets, or credentials leak into shareable docs or test fixtures. |
| Archive custody | Tests do not mutate archived runs; fixture data remains synthetic or paraphrase-only unless explicitly local-only. |
| `SKILL.md` boundary | No conductor-contract changes unless a separate `SKILL.md` PR is explicitly approved. |

## Fixture Coverage Required

Phase 1 should map at least these fixtures:

- `risk_high_stakes_clean_not_checked_v0`;
- `risk_high_stakes_clean_trusted_live_v0`;
- `risk_high_stakes_artifact_degraded_v0`;
- `risk_high_stakes_unsupported_claim_v0`;
- `risk_high_stakes_values_conflict_unresolved_v0`;
- `risk_standard_clean_not_checked_v0`;
- `risk_standard_clean_trusted_live_v0`;
- `risk_standard_saved_clean_live_leak_v0`;
- `risk_stability_archive_consistency_v0`;
- `risk_quick_thin_scope_declared_v0`;
- `risk_deep_intent_not_automatic_v0`.

The excluded/crisis fixture should remain a policy guard unless a separate
external crisis/domain protocol project exists. Lolla should not become that
handler.

## Contract Impact Analysis

`agent_result.json`:

- Phase 1 should assert current `caller_action` behavior.
- Phase 2 may clarify `status_reason` or `notes`.
- Any new enum, changed enum meaning, or automatic `yes` pathway requires a
  separate contract PR.

`evaluation.json`:

- Phase 1 should not change it.
- Phase 2 may add an explicit high-stakes reliance caveat while preserving
  deterministic run-readiness semantics.
- It must not score answer quality or domain correctness.

Review corpus records:

- Phase 3 may expose risk-mode reliance caveats for human reviewers.
- It must not populate human labels automatically.

Human review workflow:

- May gain reviewer guidance for high-stakes reliance caveats.
- `safe_for_agent_use` remains human-owned.

Observatory:

- Not needed for Phase 1.
- Later UI copy should only surface the stable policy; it should not imply
  action approval.

`SKILL.md`:

- Not touched in PR39.
- Not touched in Phase 1 unless a separate conductor-contract PR is approved.

## Caller-Action Drift

Treat these as caller-action drift:

- returning `use_revised_answer` for otherwise clean `high_stakes` without a
  separate contract PR and tests;
- using clean artifacts to bypass `ask_user_first`;
- changing `ask_user_first` semantics from "ask the human before relying" into
  "the human is optional";
- treating trusted live-output cleanliness as action approval;
- mapping unsupported high-stakes domain claims to an automatic proceed path;
- changing control-plane mappings without updating contract docs and tests.

## Domain-Authority Drift

Treat these as Lolla pretending to be a domain authority:

- saying Lolla cleared, approved, certified, or validated a legal, medical,
  clinical, financial, security, crisis, employment, or safety action;
- resolving user-values or stakeholder-obligation conflicts automatically;
- treating `high_stakes` as a domain-specific protocol;
- adding unsupported domain facts because risk is high;
- using risk mode to infer stable personality traits, legal obligations,
  medical suitability, investment safety, or crisis disposition;
- turning `safe_for_agent_use` into automatic approval.

## What Should Remain Unchanged

Until a later explicit PR:

- prompts;
- model calls;
- Step 7 behavior;
- capture strategy;
- live-output finalization;
- archive mutation behavior;
- provider-boundary policy;
- `caller_action` enum and broad policy;
- `SKILL.md`;
- domain/crisis protocols;
- answer-quality scoring;
- LLM judges;
- automatic human-review labels.

## Rollout Order

1. Land this PR39 plan.
2. Add Phase 1 contract-lock tests for current high-stakes behavior.
3. Only after tests pass, consider Phase 2 artifact clarity.
4. Only after artifact clarity is stable, expose risk caveats in review/corpus
   surfaces.
5. Only after those gates, consider runtime enforcement in a separate PR.
6. Keep judge work deferred until human labels and fixture evidence justify it.

## Go / No-Go Criteria

Go for Phase 1 when:

- PR36, PR37, PR38, and PR39 are landed;
- the test fixtures can be represented without raw private content;
- expected `caller_action` and `safe_for_agent_use` behavior is explicit;
- maintainers agree Phase 1 is test-only or refactor-only.

No-go for implementation when:

- the proposal changes `caller_action` without a contract PR;
- the proposal treats risk mode as answer quality;
- the proposal adds domain/crisis behavior;
- the proposal relies on model-based risk classification;
- the proposal changes prompts or `SKILL.md`;
- the proposal cannot map to PR37/PR38 fixtures;
- the proposal cannot prove `standard` mode remains stable.

## What This Does And Does Not Justify

This does justify:

- treating high-stakes reliance/readiness tightening as the next implementation
  direction;
- starting with contract-lock tests before behavior changes;
- requiring future risk-mode work to cite PR36, PR37, PR38, and PR39;
- preserving `ask_user_first` as the current high-stakes reference behavior;
- keeping high-stakes reliance conservative.

This does not justify:

- runtime enforcement in PR39;
- caller-action changes;
- prompt changes;
- `SKILL.md` changes;
- evaluation, agent-result, or archive code changes;
- new tests in PR39;
- domain or crisis runtime protocols;
- model-based risk classification;
- answer-quality scoring;
- an LLM judge;
- automatic `safe_for_agent_use`;
- automatic human labels.

## Recommended Next Slice

PR43 should be:

```text
Risk Mode Reliance Review Batch v0
```

Purpose:

Use the PR42 review-corpus surface in a small local review batch to verify that
reviewers can separate high-stakes reliance caveats from answer-level quality
and human-owned `safe_for_agent_use`. That slice should remain local
human-review work, not answer-quality scoring, runtime enforcement,
caller-action redesign, automatic labeling, or domain approval.

## Review Receipt

- PR39 is docs/design-only.
- Smallest future behavior change named:
  `high_stakes` reliance/readiness tightening.
- PR40 now completes the first code-bearing slice: test-only contract lock.
- PR41 now completes deterministic evaluation artifact clarity by adding
  `risk_mode_reliance_policy` to high-stakes evaluation checks.
- PR42 now completes review-surface integration by exposing
  `risk_mode_reliance` in review-corpus records and human-review workflow docs.
- PR36, PR37, and PR38 are cited as prerequisites.
- Contract impacts are named for `agent_result.json`, `evaluation.json`,
  review corpus records, human review workflow, Observatory, and `SKILL.md`.
- No `$lolla` run.
- No model calls.
- PR41 changes only deterministic evaluation artifact code and tests.
- PR42 changes only review-corpus export code, tests, and docs.
- No prompts changed.
- No `SKILL.md` changes.
- No risk-mode enforcement.
- PR40 adds contract-lock tests only; no production code changed.
- No caller-action change.
- No judge, answer-quality score, automatic labels, or domain protocol.
