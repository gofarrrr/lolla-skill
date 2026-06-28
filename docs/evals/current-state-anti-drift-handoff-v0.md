# Current State Anti-Drift Handoff v0

Status: current-state handoff
Date: 2026-06-28
Slice: PR45, updated by PR56

This note is the compact first-read handoff for a fresh Lolla eval session. It
summarizes what the harness is, what PR30-PR56 built, what evidence exists now,
and what must not be built until the next explicit approval gates.

PR45 is docs-only. It does not run Lolla, call models, mutate archives, change
runtime behavior, change prompts, or change `SKILL.md`.

## One-Sentence State

Lolla uses probabilistic reasoning where semantic judgment is needed, but wraps
that judgment in deterministic custody: capture, artifacts, health checks,
schemas, review-corpus exports, evaluation receipts, and human-owned review
before any judge or enforcement is allowed.

## How To Think About Lolla Now

Lolla is a reasoning-audit harness, not a broad safety system. Its native
question is whether the reasoning behind an answer, plan, or proposed action
deserves trust before the user or an agent relies on it.

The product boundary is still sharp:

- deterministic code checks artifact custody, schema validity, capture
  adequacy, run health, provider-boundary state, caller-action consistency, and
  review-corpus visibility;
- model judgment is used by the normal Lolla pipeline for interpretation,
  audit pressure, and answer revision;
- human reviewers decide answer-level quality, useful friction,
  `safe_for_agent_use`, taxonomy changes, and any future judge calibration;
- `caller_action` is machine-readable caller guidance, not human approval;
- `risk_mode` is reliance and review context, not answer-quality scoring,
  domain approval, or automatic safety.

## PR30-PR56 Chain

- PR30 created the six-run human/product review seed over the clean complex
  conversation baseline.
- PR31 defined the human-owned actionable-delta rubric.
- PR32 added paraphrase-only adversarial pair fixtures to test smoothness and
  comfort traps.
- PR33 broadened local human review to a 14-record corpus batch.
- PR34 designed the first-class user-values/priorities signal without
  extraction or runtime integration.
- PR35 documented the live-output hygiene policy and kept `not_checked` honest
  by default.
- PR36 documented the risk-mode behavior policy: risk raises reliance and review
  burden before runtime behavior changes.
- PR37 added paraphrase-only risk-mode fixture expectations.
- PR38 reviewed those fixtures and added the high-stakes values/priorities
  conflict fixture.
- PR39 planned high-stakes reliance/readiness tightening as a contract-first
  path.
- PR40 locked current risk-mode behavior in tests.
- PR41 added explicit high-stakes reliance caveats to `evaluation.json`.
- PR42 exposed those caveats per review-corpus record as
  `risk_mode_reliance`.
- PR43 used PR37/PR38 fixtures to confirm reviewers can interpret the PR42
  surface without confusing a reliance caveat for approval.
- PR44 added additive manifest-level counts so the corpus-level absence or
  presence of reliance-present high-stakes evidence is visible at a glance.
- PR45 recorded this anti-drift handoff.
- PR46 planned the future approved high-stakes evidence seed.
- PR47 added paraphrase-only high-stakes evidence fixtures.
- PR48 added a read-only manifest analyzer that reports whether high-stakes
  reliance-present archive evidence actually exists.
- PR49 planned the human-owned user-values/priorities worksheet.
- PR50 added paraphrase-only worksheet fixtures.
- PR51 reviewed those fixtures and found all six pass as understandable
  human-review examples.
- PR52 added deterministic blank worksheet export structure without extraction
  or runtime behavior.
- PR53 piloted four human-filled values/priorities worksheets from existing
  reviewed summaries without raw content, extraction, or runtime behavior.
- PR54 reviewed that pilot, marked all four worksheets pass, and closed the v0
  worksheet lane as complete for human-owned review before any extraction,
  memory, runtime integration, automatic labels, or judging.
- PR55 lands the Semantica-inspired accountability PRD as a docs-only planning
  artifact. It borrows accountability primitives such as decision records,
  provenance maps, conflict registers, preflight diagnostics, and run-local case
  graph views while explicitly rejecting graph databases, embeddings, memory,
  policy engines, compliance-platform drift, LLM judges, answer-quality scoring,
  automatic labels, and runtime behavior changes.
- PR56 lands the Lolla Doctor / Preflight plan as a docs-only planning
  artifact. It defines a future read-only doctor report for runtime discovery,
  archive-root discovery, helper script availability, provider/cost readiness,
  review-corpus manifest visibility, high-stakes evidence absence/presence,
  output-path safety, repo/runtime boundary checks, and privacy-safe output. It
  does not add the CLI.

## Current Corpus Evidence

The current local review-corpus export shows:

```json
{
  "record_count": 80,
  "risk_mode_counts": {
    "standard": 80
  },
  "risk_mode_reliance_present_counts": {
    "false": 80,
    "true": 0
  },
  "risk_mode_reliance_by_risk_mode_counts": {
    "standard|false": 80
  },
  "risk_mode_reliance_check_status_counts": {
    "unavailable": 80
  }
}
```

This means the real local archive corpus currently has no high-stakes
`risk_mode_reliance.present: true` evidence. Future docs must not claim real
high-stakes archive evidence until approved high-stakes runs actually exist.

The generated review-corpus manifest still carries an existing local-only
`archive_root` absolute path field. That is a local manifest custody field, not
a PR44 reliance-count leak. The PR44 reliance-count fields themselves contain
only aggregate keys and counts.

## What Is Still Missing

- no real high-stakes reliance-present archive evidence;
- no approved high-stakes run batch;
- no calibrated LLM judge;
- no answer-quality scoring;
- no automatic human-review labels;
- no runtime risk-mode enforcement beyond the existing conservative
  `high_stakes` caller-action contract;
- no implemented user-values/priorities extraction or report; PR49 only plans
  the human worksheet, PR50 only adds paraphrase-only fixtures, PR51 only
  reviews those fixtures, PR52 only creates blank worksheet structure, PR53
  only pilots human-filled worksheets from reviewed summaries, and PR54 only
  reviews the pilot and pauses the lane at human-owned v0;
- no trusted live-output transcript implementation;
- no implemented Semantica-inspired accountability primitive yet: no
  `lolla.audit_decision_record.v0`, `lolla.provenance_map.v0`,
  `lolla.review_conflict_register.v0`, `lolla.case_graph.v0`, or `lolla doctor`
  CLI exists from PR55 or PR56;
- no domain, crisis, legal, medical, financial, or safety protocol.

## Explicit Non-Goals

Do not build any of these from this handoff alone:

- `$lolla` runs;
- model calls;
- archive mutation;
- `SKILL.md` changes;
- prompt or reference changes;
- runtime behavior changes;
- `caller_action` relaxation;
- provider-boundary policy changes;
- LLM judges;
- answer-quality scoring;
- automatic human-review labels;
- model-based risk classification;
- crisis or domain runtime protocols;
- `conversation_understanding_ir.v0`;
- graph databases, embeddings, chunking, memory layers, or specialist runtime
  integration.
- Semantica-style policy engines, compliance platforms, global context graphs,
  LLM judges, answer-quality scoring, or automatic labels.

## Current Stop Point

The PR46 -> PR47 -> PR48 readiness queue is now complete:

1. PR46 designed the evidence seed plan without running cases.
2. PR47 created paraphrase-only fixtures for reviewer expectation checks before
   real runs.
3. PR48 added the read-only analyzer for review-corpus manifests.

Stop here. Creating real high-stakes archive evidence requires explicit product
approval.

The later safe lanes are separate:

1. PR49 defines a human values/priorities worksheet plan. PR50 adds
   paraphrase-only worksheet fixtures. PR51 reviews those fixtures and
   recommends blank worksheet/export structure. PR52 adds that blank structure.
   PR53 pilots four human-filled worksheets. PR54 reviews the pilot and closes
   the worksheet lane at v0 for human-owned review. Do not continue into
   extraction, runtime integration, memory, automatic labels, or judging without
   a new explicit gate.
2. PR55 records a Semantica-inspired accountability plan. PR56 records the
   doctor/preflight plan. The next possible slice from that lane is PR57 Lolla
   Doctor Read-Only CLI v0, and it still needs a separate implementation gate.
   Do not implement decision records, provenance maps, conflict registers, case
   graph exports, platform work, or runtime behavior from PR55 or PR56 alone.
3. A later live-output hygiene lane can plan and lock current behavior, then
   stop for an implementation decision.

For a plain-language map of what the current system can do and which recorded
cases demonstrate it, read:

```text
docs/evals/current-system-capabilities-v0.md
```

For the Semantica-inspired accountability boundary and proposed PR55-PR65 queue,
read:

```text
docs/conversation-understanding/semantica-inspired-accountability-prd-v0.md
```

For the PR56 doctor/preflight design, read:

```text
docs/evals/lolla-doctor-preflight-plan-v0.md
```

## Decision Gates

- Now: decide whether to create approved real high-stakes evidence.
- Values lane: PR54 has decided the v0 worksheet lane is complete enough to
  pause for human-owned review; reopen only by explicit approval.
- Accountability lane: PR55 approves only the Semantica-inspired roadmap and
  PR56 approves only the doctor/preflight design. PR57 may implement the
  smallest read-only doctor CLI next, but only with a separate gate and without
  model calls, `$lolla` runs, archive mutation, prompt changes, `SKILL.md`
  changes, provider-boundary policy changes, or high-stakes approval behavior.
- After a live-output hygiene planning/review lane: decide whether to implement
  trusted live-output transcript hygiene.

Until those gates are explicitly approved, the machine should keep the evidence
lane honest: deterministic counts and fixtures may describe readiness, but they
must not pretend to be real high-stakes outcomes, human approvals, or automated
judgment.
