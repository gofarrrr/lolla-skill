# Lolla R4 provider-free corpus and replay plan

Status: next major stage prepared; execution not started

Date: 2026-07-13

Provider calls authorized: zero

Runtime integration authorized: no

## Goal

Determine exactly what the current conversation-understanding system preserves,
misplaces, fragments, or loses across realistic multi-thread conversations
before changing prompts, schemas, models, or architecture.

R4 begins with inventory and replay, not invention.

## Constitutional boundary

```text
LLMs interpret messy conversation meaning.
Deterministic code preserves identity, source custody, bounds, replay, and joins.
Deterministic code must not infer semantic roles from keywords or chronology.
Different semantic readers may overlap.
Fan-in must preserve disagreement and missing coverage.
The graph receives controlled reasoning abstractions, not a lossy factual summary.
No metric becomes a quality badge.
```

R4 must not turn the extraction layer into a brittle multi-stage semantic gate.
It may make missing information and contradictions visible. It may not decide
what the conversation means through hand-written rules.

## Existing evidence to reuse

The starting corpus is already present:

- twelve naturalized transfer conversations;
- 24 messages and twelve user/assistant pairs per case;
- exact source hashes under the V1 manifest;
- six pressure-expected, four stand-down-expected, and two park-expected
  source-review strata;
- a provider-free role-input preflight covering all twelve transfer cases;
- sealed V1 outputs and receipts where transfer execution completed;
- preserved failure artifacts where it did not;
- later role-first, role-first v2.1, qualification, mechanism, coverage, and
  fresh-consumer research artifacts.

Primary source paths:

- `research/simulated-reliability-corpus-v1-2026-07-12/manifest.json`
  (`93fabb750960e9c3c2b683f8ae576ca61ca2c50204039718cde0aff7c9ffbb27`)
- `research/simulated-reliability-corpus-v1-2026-07-12/naturalized-transfer-sources/`
- `research/simulated-reliability-corpus-v1-2026-07-12/naturalized-source-review.json`
- `research/simulated-reliability-corpus-v1-2026-07-12/provider-free-role-input-preflight/report.json`
- `research/simulated-reliability-v1-evaluation-2026-07-13/evidence-matrix.json`

These are simulated reliability inputs, not real-user usefulness evidence.
Several were used during prior research, so R4 must label calibration,
transfer, exposed, and review-only evidence rather than pretending everything
is a fresh holdout.

## First bounded R4 goal

### 1. Freeze a replay inventory

For every one of the twelve cases, record exact paths and hashes for:

- authoritative conversation;
- source-first review or protected target;
- position/role artifacts;
- qualification and unresolved-matter artifacts;
- mechanism and coverage artifacts;
- direct and graph pressure inputs;
- final consumer output, if present;
- receipt and custody result;
- preserved failure boundary;
- whether the artifact was used for tuning, review, or transfer evidence.

Missing artifacts must be explicit. A missing file cannot become an empty
semantic result.

### 2. Freeze a vector measurement contract

Measure separately, never as one score:

- **system-level coverage:** which material conversation threads appear
  anywhere across complementary readers;
- **role placement:** starting position, current position, qualification,
  unresolved matter, and reopen condition remain distinct where supported;
- **temporal fidelity:** later repair does not erase the earlier position, and
  an earlier concern is not presented as current;
- **speaker ownership:** user beliefs, assistant suggestions, and joint
  decisions are not collapsed;
- **source precision:** every semantic record resolves to exact turns and
  speaker evidence;
- **cross-thread integrity:** separate strategic threads stay separate while
  their relationships remain visible;
- **fan-in load:** counts and byte/token estimates at every reader-to-synthesis
  boundary;
- **false stand-down:** material unresolved pressure does not disappear merely
  because one reader missed it;
- **over-fragmentation:** one coherent trajectory is not split into artificial
  records;
- **custody and replay:** identity, hashes, missingness, and deterministic joins
  reproduce exactly.

Coverage is a diagnostic, not a relevance gate. A reader may overlap with
another reader. Deterministic code may count and join explicit records but may
not infer a role from turn position or vocabulary.

### 3. Replay before repair

Use existing sealed outputs and provider-free projections first. Do not call a
model to fill a missing artifact. Do not change prompts or validators while
building the inventory.

The replay should answer:

- Which questions can existing artifacts answer exactly?
- Which failures are representational rather than transport or custody?
- Which cases expose the same causal defect?
- Which gaps require a new probabilistic read rather than better deterministic
  assembly?
- Is the existing multi-reader output already sufficient when evaluated at the
  system level, even if one reader is incomplete?

### 4. Choose one causal next change

Only after the gap matrix is frozen should R4 select a repair. The repair must
name one observed failure and one expected changed measurement. Examples may
include a clearer semantic role contract, a bounded fan-in representation, or
an explicit missingness state. The inventory must decide which, not intuition.

## Required outputs

- `r4-corpus-replay-manifest.json` with exact source and artifact custody;
- `r4-measurement-contract.json` with vector definitions and non-claims;
- `r4-replay-gap-matrix.json` with per-case availability and first causal gap;
- a plain-language result explaining what is already measurable;
- one recommended bounded repair or a documented finding that no repair is
  yet earned.

## Stop rules

Stop and report before implementation if:

- the twelve source hashes do not reproduce;
- source-first review is missing for a metric that requires it;
- a replay would require reading private raw payloads into Git;
- a missing semantic artifact is being treated as an empty result;
- two artifacts use incompatible identity or source-reference contracts;
- a proposed deterministic rule interprets meaning from keywords, chronology,
  or array order;
- the work starts optimizing one reader while system-level coverage is still
  unknown;
- a new model call appears necessary.

A need for a model call is not automatic authorization. It must become a new
falsifiable proposal after provider-free evidence is exhausted.

## Acceptance criteria

- all twelve naturalized source bytes and hashes reproduce;
- every available sealed artifact has an exact role and provenance label;
- absent, failed, partial, exposed, and review-only states are distinct;
- the measurement vector has no composite quality score;
- at least starting/current/qualification/unresolved/reopen interpretations are
  separately inspectable where source review supports them;
- multiple threads and cross-thread relationships are represented without
  deterministic semantic inference;
- fan-in load is measured rather than guessed;
- current false-stand-down and fragmentation evidence is locatable by case;
- no provider call, prompt tuning, model shopping, runtime integration, or
  architecture redesign occurs;
- the next repair, if any, follows from one repeated observable gap.

## What this goal will not establish

R4's first provider-free replay will not prove product usefulness, model
reliability, graph value, real-user transfer, decision quality, or production
readiness. It will make the next development choice evidence-based and cheap.
