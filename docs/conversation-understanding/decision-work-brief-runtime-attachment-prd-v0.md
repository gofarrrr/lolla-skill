# Decision Work Brief Runtime Attachment PRD v0

Status: runtime-attached internal v1 merged; automatic supply remains future work
Date: 2026-07-03

## Purpose

Decision Work Brief Offline v1 is now functional as an offline evidence system.
It can take completed Lolla artifacts, render readable briefs, enrich those
briefs with bounded provisional interpretation, and create automatic-triage
reads that route attention toward source-depth, overtrust, private-context,
domain, agent-inspection, and runtime-blocker concerns.

This PRD answers the next product question:

> If the Decision Work Brief eventually attaches to Lolla, when should it run,
> what should a user see, what should another agent see, and what must block it?

This document does not implement runtime attachment. It defines the first safe
plan for attaching the offline system without pretending it is customer-ready,
human-validated, product proof, answer-quality scoring, or action
authorization.

## First Principles

The runtime should produce the decision-audit run. The Decision Work Brief
should explain that run after the fact.

That separation matters. If the brief becomes part of the same live answer too
early, it can make provisional interpretation look like authority. The product
value is not "Lolla says the decision is right." The product value is:

> The final answer travels with a compact receipt for how it was made, what was
> challenged, what changed, what is still uncertain, and what should not be
> overclaimed.

The system should therefore optimize for:

- inspectability over persuasion;
- source refs over raw-content exposure;
- routing over scoring;
- caveated summaries over polished certainty;
- agent-readable structure without agent action authorization;
- deterministic custody plus LLM interpretation, not deterministic claims about
  messy human meaning.

## Current State

Offline v1 can already do the following over completed artifacts:

- preserve source and custody status;
- render a readable Decision Work Brief;
- enrich the brief with a bounded interpretation section;
- prepare automatic triage packets;
- create Codex-assisted provisional triage reads;
- route attention toward source-depth, overtrust, private-context, domain/legal,
  agent-inspection, and runtime-blocker concerns;
- preserve explicit non-claims.

Offline v1 still cannot claim:

- runtime integration;
- customer readiness;
- human validation;
- product proof;
- advice correctness;
- proof that Lolla improved the decision;
- answer-quality scoring;
- agent or automatic action authorization;
- deterministic understanding of the messy conversation.

## Product Goal

The eventual user experience should be:

1. The user runs Lolla on a serious AI-assisted decision.
2. Lolla produces the revised answer as it does now.
3. After the run is complete and archived, the system may create a Decision
   Work Brief artifact.
4. The user sees a short, plain-language receipt and can open the full brief if
   needed.
5. Another agent can inspect a structured evidence packet without receiving raw
   private content by default.
6. If the artifacts are too thin, high-risk, or unsafe to summarize, the system
   says so instead of producing a confident-looking brief.

## Non-Goals

This PRD does not propose:

- changing `$lolla` prompts;
- changing `SKILL.md`;
- changing `scripts/skill/*`;
- changing live Lolla reasoning behavior;
- calling provider/model APIs from repo code;
- mutating historical archives;
- scoring answer quality;
- creating approval labels;
- authorizing an agent to act;
- treating clean artifacts as proof of good advice;
- exposing raw conversation, provider text, private ledgers, or local paths to
  another agent by default.

## Decision 1: When Should The Brief Run?

### Option A: Automatically After Every Lolla Run

Pros:

- Every run gets the same evidence surface.
- Users do not need to remember a separate command.
- It makes the product promise visible immediately.

Cons:

- It may generate confident-looking briefs for degraded or incomplete runs.
- It increases runtime complexity before the attachment contract is proven.
- It can make provisional interpretation feel like part of the answer itself.
- It may waste work on simple runs where a Decision Work Brief is not useful.

Verdict:

Do not start here.

### Option B: Only On Explicit User Request

Pros:

- Safest from an overtrust and cost perspective.
- Easy to explain: "generate a Decision Work Brief for this run."
- Keeps the first runtime-adjacent slice closer to the current offline workflow.

Cons:

- Users may miss the main product value.
- Evidence generation becomes inconsistent.
- It may feel bolted on rather than native.

Verdict:

Use this as the first manual fallback and debugging path.

### Option C: Only For Completed Clean Runs

Pros:

- Matches the current Offline v1 evidence boundary.
- Reduces false confidence from partial or failed artifacts.
- Lets deterministic hygiene decide whether the system has enough custody to
  build a report.

Cons:

- Some degraded runs might still be worth summarizing as "do not trust this."
- Users may wonder why the brief sometimes does not appear.

Verdict:

This should be the first automatic eligibility rule.

### Option D: Only When Triage Says It Is Useful

Pros:

- Better product experience: generate the brief when it adds value.
- Avoids clutter for low-stakes or source-thin runs.
- Lets the system route high-risk outputs toward agent-only or blocked states.

Cons:

- Triage itself needs a packet and often a brief-like source surface.
- If triage becomes a gate too early, it can become a hidden score.
- It still needs calibration.

Verdict:

Use triage to decide presentation and routing, not first-generation eligibility.

### Recommended Timing

First runtime-safe path:

```text
Lolla run completes
-> archive is finalized
-> deterministic hygiene passes
-> optional flagged post-archive Decision Work Brief generation
-> automatic triage routes the output
-> user sees a short receipt plus link, or a clear blocked/deferred note
```

The brief should be generated post-archive, not during answer generation. It
should not block the revised answer. If brief generation fails, the run should
remain complete and the archive should record that the brief is unavailable.

## Decision 2: What Should The User See?

The user should not see the entire machinery by default. The main surface should
be short and practical.

### Surface A: Short Receipt

Recommended default.

The user sees a compact summary after the revised answer:

```text
Decision Work Brief: available

What changed: the audit sharpened the action from a broad launch choice into a
scoped private pilot decision with buyer-behavior gates.

Main caveat: this is a source-limited audit summary, not proof that the advice
is correct.

Open full brief: <local artifact link>
```

Pros:

- Gives value in seconds.
- Keeps the answer usable.
- Makes the caveat visible.

Cons:

- Hides detail unless the user opens the brief.
- Needs careful wording to avoid sounding like approval.

Verdict:

Use as default when a brief is generated and not blocked from user surface.

### Surface B: Full Brief

The user can open the full Decision Work Brief from a link or archive view.

Pros:

- Shows the decision, action consequence, interpretation, uncertainty, and
  evidence limits.
- Useful when the decision is high-stakes or needs review.

Cons:

- Too much for the default chat flow.
- Can still look overly authoritative if presented without caveats.

Verdict:

Make it available, but not the default full display.

### Surface C: Triage Summary

The triage summary should say where attention is needed. It must not be a
rating.

Example:

```text
Triage: domain review recommended. The brief is useful for inspection, but the
decision touches compliance and operational-risk constraints that the audit did
not validate.
```

Pros:

- Helps the user know what to do next.
- Separates "useful evidence" from "safe to act."

Cons:

- If worded badly, it becomes a score or approval label.

Verdict:

Show one triage sentence in the short receipt. Put detailed triage in the full
brief or agent packet.

### Surface D: Evidence Bundle Link

The user should be able to open the artifact bundle when needed.

Pros:

- Makes the work inspectable.
- Supports later verification.
- Lets another agent read structured evidence.

Cons:

- Most users will not read it.
- Must avoid exposing private or raw content accidentally.

Verdict:

Always link when artifacts are generated. Do not dump the bundle into chat.

### Surface E: Warning/Caveat Line

Always required.

The user-facing receipt should always include one of these:

- "This is an audit summary, not proof the advice is correct."
- "This brief is source-limited and should not be treated as approval to act."
- "This run is not ready for user-facing brief output; see evidence limits."

Verdict:

Required for every user-visible Decision Work Brief surface.

## Decision 3: What Should Another Agent See?

Another agent should receive structured evidence, not a private transcript by
default.

Recommended agent handoff:

- brief artifact ref;
- enriched brief artifact ref;
- automatic triage read ref;
- source refs and source status;
- privacy/redaction status;
- missingness;
- uncertainty fields;
- non-claims;
- route outputs such as `user_surface_caveated`, `agent_inspection_only`, or
  `runtime_attachment_blocked`;
- explicit "not authorized to act" flag.

Default agent handoff must not include:

- raw conversation text;
- raw revised answer text beyond the user-approved final answer surface;
- raw memo text;
- provider text;
- private ledgers;
- local absolute paths;
- secrets;
- hidden chain-of-thought style material;
- action authorization.

Private/local modes may record that richer material exists, but they should pass
availability and source refs, not the material itself, unless an operator
explicitly chooses a local-private review mode.

## Decision 4: What Blocks Generation?

### Hard Deterministic Blockers

The system should not generate a user-visible Decision Work Brief when:

- the Lolla run is incomplete;
- the archive is not finalized;
- required structured artifacts are missing or malformed;
- the revised answer artifact is missing;
- hygiene or boundary lint fails;
- output would be written inside an unsafe location;
- the artifact set contains raw/private content that the target mode must not
  export;
- schema validation fails;
- source refs cannot be resolved;
- custody flags would need to claim model calls, runtime invocation, archive
  mutation, scoring, approval, or agent action authorization.

Expected behavior:

- do not generate the brief;
- write or show a compact blocked reason;
- preserve that this is a custody failure, not an advice-quality judgment.

### Soft Triage Blockers

The system may generate an internal or agent-only artifact, but should avoid
ordinary user-surface display when:

- source depth is too thin;
- private context is required to understand the decision;
- overtrust risk is high;
- domain, legal, compliance, medical, financial, governance, employment, or
  safety review is recommended;
- lost-value risk is unresolved;
- the decision appears relationship-sensitive or politically sensitive;
- the interpretation is too provisional to be summarized safely.

Expected behavior:

- generate an agent-inspection or maintainer artifact if safe;
- show a user-visible note that the brief is blocked or caveated;
- do not present the brief as approval, proof, or advice correctness.

## Decision 5: What Is The First Runtime-Safe Slice?

The first runtime-safe slice should not be full automation. It should be a
post-archive, flagged attachment path.

Recommended first slice:

```text
PR159: Runtime attachment PRD
PR160: Runtime attachment contract and artifact-location plan
PR161: Manual post-archive generation command over one completed run
PR162: Flagged post-archive runtime hook that only runs on completed clean runs
PR163: Runtime attachment fixture review over blocked, caveated, and available cases
PR164: Runtime attachment package gate
```

The first actual behavior change should be:

> Behind an explicit local flag, after a Lolla run is complete and archived, run
> the existing offline Decision Work Brief pipeline, write the brief artifacts as
> post-run sidecars, and show only a short receipt plus link if deterministic
> hygiene and triage allow it.

The flag should default off until review says otherwise.

The runtime hook must be:

- post-archive;
- non-blocking for the revised answer;
- safe to fail closed;
- limited to completed clean runs;
- explicit about blocked reasons;
- unable to authorize action;
- unable to convert triage into a score;
- unable to expose raw/private material by default.

## How This Helps The System

Runtime attachment is useful only if it preserves the value of Offline v1:

- The user gets a practical receipt for the decision process.
- The full brief is available without crowding the final answer.
- Another agent can inspect structured evidence instead of guessing from the
  final memo alone.
- The system can say "we cannot safely summarize this" when source depth,
  privacy, or domain risk is too high.
- Maintainers can see whether the evidence surface survives real use.

The key product move is not more prose. The key product move is that the final
answer becomes accompanied by inspectable context:

- what decision was being made;
- what the audit pressed on;
- what changed for action;
- what remains uncertain;
- what evidence exists;
- what evidence is missing;
- what nobody should claim.

## Tradeoffs

### Speed Versus Evidence

A default brief after every run is attractive, but it risks making Lolla feel
slower and more complicated. A flagged post-archive path is slower to productize
but safer to learn from.

### User Simplicity Versus Inspectability

Most users need a short receipt, not the full artifact graph. Agents and
maintainers need the graph. The product should separate these surfaces instead
of forcing everyone to read the same material.

### Automation Versus Calibration

The future normal path should be automatic LLM-assisted triage, not human review
of every run. Human review is still useful as calibration. It should help catch
overtrust, missing source depth, and confusing presentation, but it should not
become a hidden quality label.

### Privacy Versus Usefulness

The richest interpretation often depends on private context. The runtime path
must preserve the fact that private context exists without exporting it by
default. This will make some user-visible briefs thinner, but it keeps the
system safe.

## Acceptance Criteria For The First Runtime Attachment PRs

A first implementation sequence should be considered healthy only if:

- it can generate no user-visible brief when blockers exist;
- it can produce a short receipt plus link for a clean completed run;
- it writes artifacts after archive completion, not during answer generation;
- it preserves source refs, uncertainty, triage, and non-claims;
- it passes privacy scans;
- it does not touch prompts, `SKILL.md`, or `scripts/skill/*`;
- it does not call provider/model APIs from repo code;
- it does not score answer quality;
- it does not authorize agent action;
- it does not claim product proof;
- it records blocked/deferred states as first-class outcomes.

## Recommended Next Work

PR160-PR167 have now implemented the first runtime-attached internal v1 slice:
contract, sidecar shape, manual bundle generator, eligibility gate, short
receipt, agent handoff, default-off post-archive hook, and package gate.

PR168 reviews that package and selects `safe_brief_supply_planning`. PR169
classifies the required inputs and selects PR170. PR170 defines the safe supply
resolver contract. PR171 implements the deterministic resolver. PR172 wires
resolver output into the manual bundle path. PR173 wires the default-off
post-archive hook to call that resolver-aware bundle chain and selects:

> PR174 Runtime Hook Resolver Fixture Review v0

The reason was narrow: the runtime hook became mechanically attached,
default-off, post-archive, and fail-closed, but concrete sidecar outputs needed
review before adding more machinery. PR174 now reviews those fixture states and
selects:

> PR175 Decision Work Brief Runtime Checked-In Safe Case Registry v0

The next supply step should provide stable checked-in-safe refs for known
examples. That improves demos and regression tests without claiming arbitrary
live runs can be semantically interpreted by deterministic runtime code.

PR175 implements that checked-in-safe registry and selects:

> PR176 Decision Work Brief Runtime Hook Registry Fixture Review v0

The next review should exercise concrete hook sidecars using registry-supplied
refs, still behind the existing default-off flag.

PR176 reviews those registry-backed fixtures using temporary sidecars. The
launch-beta, deploy-intake, and cofounder registry entries can generate
sidecars through the existing resolver-aware hook seam, while registry misses
and unsafe registry entries remain blocked before fake brief supply. PR176
selects:

> PR177 Decision Work Brief Runtime-Attached Internal v1 Package Refresh v0

The package refresh should preserve the narrow claim: internal runtime
attachment is functional behind a flag for completed clean runs when safe refs
exist, but arbitrary-run semantic supply, customer readiness, human validation,
product proof, answer-quality scoring, advice correctness, and action
authorization remain unclaimed.

PR177 performs that package refresh with a manifest covering PR160-PR176 plus
the PR177 package files. It selects the next operational step:

> Audit/stage/commit the PR160-PR177 runtime-attached internal v1 package using
> a narrow manifest-derived pathspec.

The package remains internal and default-off. It still does not add an
interpretation queue, model calls, customer presentation, product proof, human
validation, answer-quality scoring, advice correctness, or action
authorization.

PR216 merged the PR160-PR177 runtime-attached internal v1 package into `main`.
That closes the first runtime attachment phase. The current runtime path is
real but input-supply-limited:

- prepared safe refs can be attached;
- curated registry examples can exercise repeatable sidecar states;
- new arbitrary completed runs normally defer until safe semantic refs exist.

The next product phase is therefore not more sidecar plumbing. It is:

> PR178 Decision Work Automatic Semantic Supply PRD v0

See [Decision Work Automatic Semantic Supply PRD](decision-work-automatic-semantic-supply-prd-v0.md).
That PRD should own the follow-on path from completed archive to offline
interpretation queue, generated interpretation read, validation, brief
rendering, triage, resolver-approved refs, and sidecar update.

The first contract slice in that follow-on path is
[Decision Work Offline Interpretation Queue Contract](decision-work-offline-interpretation-queue-contract-v0.md).
It defines queue item/result vocabulary only; it does not add runtime
interpretation or hook behavior.

PR179-PR182 now define the first automatic semantic supply scaffold:

- [Decision Work Offline Interpretation Queue Contract](decision-work-offline-interpretation-queue-contract-v0.md);
- [Decision Work Offline Interpretation Queue Builder](decision-work-offline-interpretation-queue-builder-v0.md);
- [Decision Work Operator/Codex Interpretation Prompt Packet](decision-work-operator-codex-interpretation-prompt-packet-v0.md);
- [Decision Work Generated Interpretation Read Intake](decision-work-generated-interpretation-read-intake-v0.md).

Those slices let completed runs become queueable and let externally supplied
interpretation reads be validated, but they still do not generate reads, call
models, render new briefs, create triage, update resolver refs, or update
runtime sidecars.

The runtime hook should remain default-off, post-archive, sidecar-only, and
fail-closed while that automatic supply path is proven.

## Stop Line

Do not make runtime attachment default-on.

Do not make the brief automatic for every run until blocked, caveated,
agent-only, and ordinary available cases have been reviewed.

Do not treat automatic triage as scoring.

Do not show raw/private material to another agent by default.

Do not let a clean Decision Work Brief imply good advice.
