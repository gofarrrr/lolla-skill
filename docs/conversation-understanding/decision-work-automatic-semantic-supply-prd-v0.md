# Decision Work Automatic Semantic Supply PRD v0

Status: product / implementation roadmap
Date: 2026-07-03

## Purpose

Decision Work Brief Offline v1 and Runtime-Attached Internal v1 are now
functional in a narrow, honest way:

- completed Lolla artifacts can be turned into readable Decision Work Briefs;
- existing interpretation reads can enrich those briefs;
- existing triage reads can route attention and caveats;
- the default-off runtime hook can attach safe Decision Work artifacts after
  archive completion;
- missing or unsafe inputs defer or block instead of producing fake certainty.

The remaining product gap is not another sidecar or manifest. It is automatic
semantic supply:

> Given a newly completed Lolla run, create the safe interpreted artifacts that
> a Decision Work Brief needs, validate them, render them, triage them, and make
> them available to the runtime sidecar without letting the runtime guess from
> messy conversation text.

This PRD defines that next development path so the work does not drift into
more packaging loops, direct runtime interpretation, or theater around curated
fixtures.

## Finished Product Target

The finished product should feel like this:

1. A user has a serious AI-assisted conversation.
2. Lolla audits the conversation and produces its revised answer and archive.
3. After the archive is complete, a safe offline interpretation job prepares a
   Decision Work Brief.
4. The user sees a short receipt:
   - what decision was being worked on;
   - what action consequence became clearer;
   - what still might be wrong;
   - whether the full brief is available, caveated, agent-only, blocked, or
     deferred.
5. The full brief explains the path to the answer in plain language.
6. An agent handoff packet receives source refs, missingness, privacy status,
   uncertainty, blockers, and inspection focus without raw private content or
   action authorization.
7. If the system lacks safe inputs, it says so. If the case is high-risk, it
   routes the brief to caveated or agent-inspection-only surfaces. If the
   interpretation fails validation, it blocks or defers.

The finished product is not:

- a correctness certificate;
- a quality score;
- proof Lolla improved the decision;
- human validation;
- default-on runtime model calls;
- direct runtime interpretation from raw conversation;
- agent action authorization.

## Current System Boundary

### What Works Now

The merged system can already do the following:

- build source/status packets over completed artifacts;
- create checked-in-safe, Codex-assisted interpretation reads for curated cases;
- render Decision Work Briefs;
- enrich those briefs through deterministic rules;
- create provisional automatic triage reads;
- validate non-claims and privacy boundaries;
- build runtime sidecar bundles from resolver-approved safe refs;
- write a default-off post-archive sidecar when
  `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE` is enabled;
- produce short receipts and agent handoff packets;
- defer, block, or fail closed when safe inputs are missing or unsafe.

The three current known cases are useful regression fixtures:

- `launch-public-enterprise-beta`;
- `deploy-assisted-intake-routing`;
- `ceo-remove-founding-cofounder`.

They prove the evidence chain and runtime sidecar path can work when safe
semantic artifacts already exist.

### What Does Not Work Yet

The system does not yet automatically create useful Decision Work material for
arbitrary new Lolla runs.

For a new completed run, Runtime-Attached Internal v1 can attach safe refs if
they already exist. Without those refs, the correct behavior is to defer. That
is safe, but it is not the full product.

Missing today:

- a durable offline interpretation queue;
- a queue item contract for completed runs that need semantic supply;
- a bounded interpreter handoff packet or prompt packet;
- generated interpretation read validation against the PR133 schema;
- generated triage read validation against the automatic triage contract;
- a queue-to-brief-to-enriched-brief-to-triage-to-sidecar flow;
- comparison against the three existing curated cases as regression fixtures;
- a decision on when generated output is user-surface, agent-only, blocked, or
  deferred.

## Product Principle

Automatic semantic supply must be offline and bounded.

Do not make this shape:

```text
runtime hook -> raw conversation -> model call -> user-facing claim
```

Use this shape:

```text
completed archive
-> deterministic packet
-> offline interpretation queue
-> bounded LLM/Codex interpretation read
-> deterministic validation
-> Decision Work Brief render
-> deterministic enrichment
-> bounded triage read
-> deterministic resolver approval
-> runtime sidecar update or deferred/blocked state
```

The runtime hook should remain a sidecar writer and status carrier. It should
not become the semantic interpreter.

## Deterministic Ownership

Deterministic code may own:

- locating completed run artifacts;
- checking run completeness and hygiene;
- building metadata/status packets;
- preserving source refs and missingness;
- preserving redacted/private availability;
- checking schema validity;
- rejecting unsafe paths and privacy markers;
- rendering Markdown from already-filled fields;
- copying resolver-approved safe refs;
- writing sidecar status, receipt, and handoff artifacts;
- routing obvious missing/blocker states;
- preserving non-claims.

Deterministic code must not infer:

- what the user really meant;
- which option was live or abandoned;
- whether Lolla improved the decision;
- whether the advice is good;
- whether friction was useful or noisy;
- whether lost value occurred;
- whether the user changed their mind;
- whether stakeholder obligations or values were satisfied.

## LLM / Codex Interpretation Ownership

The LLM/Codex layer may fill bounded interpretation fields when supplied with a
safe packet and an explicit output schema.

Candidate fields already proven useful in PR131-PR134:

- `decision_question`;
- `likely_starting_direction`, with visible uncertainty;
- `revised_direction_or_action_consequence`;
- `decision_thresholds`;
- `evidence_gates`;
- `useful_friction`, as descriptive process pressure, not a quality label;
- `what_the_final_answer_does_not_prove`.

Fields that should remain evidence-only or extra-cautious until more evidence
exists:

- `live_options`;
- `abandoned_or_rejected_options`;
- `noisy_friction`;
- `lost_value`;
- user values;
- stakeholder obligations;
- assistant influence on user framing;
- legal, compliance, medical, employment, governance, or relationship
  conclusions.

Every interpreted field must carry:

- source refs;
- source status;
- uncertainty;
- privacy limits;
- whether human or domain review is required;
- whether it may feed the brief;
- whether it may feed agent inspection;
- `must_not_be_used_as_quality_label: true`.

## Existing Artifacts To Reuse

The automatic supply path should reuse existing work instead of inventing a
parallel system:

- [Decision Work Brief Schema](decision-work-brief-v0.json)
- [Decision Work Brief Packet Builder](decision-work-brief-packet-builder-v0.md)
- [Decision Work Conversation Interpretation Contract](decision-work-conversation-interpretation-contract-v0.md)
- [Decision Work Conversation Interpretation Offline Packet](decision-work-conversation-interpretation-offline-packet-v0.md)
- [Decision Work Conversation Interpretation Read Schema](decision-work-conversation-interpretation-read-schema-v0.md)
- [Decision Work Brief Enrichment Rules Contract](decision-work-brief-enrichment-rules-contract-v0.md)
- [Decision Work Brief Offline Enriched Builder](decision-work-brief-offline-enriched-builder-v0.md)
- [Decision Work Automatic Triage Contract](decision-work-automatic-triage-contract-v0.md)
- [Decision Work Automatic Triage Packet Builder](decision-work-automatic-triage-packet-builder-v0.md)
- [Decision Work Automatic Triage Provisional Read](decision-work-automatic-triage-provisional-read-v0.md)
- [Decision Work Brief Runtime Safe Supply Resolver](decision-work-brief-runtime-safe-supply-resolver-v0.md)
- [Decision Work Brief Runtime Bundle Resolver Integration](decision-work-brief-runtime-bundle-resolver-integration-v0.md)
- [Decision Work Brief Runtime Hook Resolver Wiring](decision-work-brief-runtime-hook-resolver-wiring-v0.md)
- [Decision Work Brief Runtime Checked-In Safe Case Registry](decision-work-brief-runtime-checked-in-safe-case-registry-v0.md)
- [Decision Work Brief Runtime-Attached Internal v1 Package Refresh](decision-work-brief-runtime-attached-internal-v1-package-refresh-v0.md)

## User Surfaces

The first automatic supply product should support three surfaces.

### User Receipt

Short and caveated. It should answer:

- is a Decision Work Brief available?
- what changed for action?
- what is the main caveat?
- is the full brief user-visible, agent-only, blocked, or deferred?

High-risk cases must not receive the same generic "available" language as low
risk cases. Governance, legal, medical, compliance, employment, safety, or
relationship-sensitive cases need stronger caveat text.

### Full Brief

Plain-language explanation of:

- the decision;
- what changed;
- what this means for action;
- what still might be wrong;
- what this does not prove;
- evidence and limits;
- what the interpretation adds, when available.

### Agent Handoff

Structured, source-linked packet for inspection. It may route attention and
name blockers. It must not authorize action.

## Development Sequence

### PR178 Decision Work Automatic Semantic Supply PRD v0

Create this PRD, update the existing Decision Work Brief and runtime-attachment
PRDs, and add a focused doc test proving that the next stage is offline,
bounded, validation-first, and not direct runtime interpretation.

Done when:

- the finished product target is explicit;
- the current "prepared cases only" limitation is named without euphemism;
- the next PR sequence is anchored to existing code/docs;
- non-claims are preserved.

### PR179 Offline Interpretation Queue Contract v0

Define the queue item and queue result contracts.

Likely fields:

- run ref;
- source packet ref;
- allowed source refs;
- requested interpretation fields;
- privacy mode;
- queue status;
- blocked/deferred reasons;
- output destination refs;
- validation requirements;
- custody flags;
- non-claims.

Statuses should include:

- `queued`;
- `running`;
- `completed`;
- `blocked_missing_packet`;
- `blocked_privacy_risk`;
- `blocked_schema_invalid`;
- `failed_validation`;
- `requires_local_private_operator`;
- `unsafe_to_export`;
- `cancelled`.

No interpreter, model calls, runtime hook changes, or sidecar updates in PR179.

PR179 is now implemented as the
[Decision Work Offline Interpretation Queue Contract](decision-work-offline-interpretation-queue-contract-v0.md).
It defines the queue item/result vocabulary and selects
`proceed_to_queue_packet_builder` for PR180.

### PR180 Offline Interpretation Queue Packet Builder v0

Build the deterministic queue packet/preparation layer.

PR180 is implemented as
[Decision Work Offline Interpretation Queue Builder](decision-work-offline-interpretation-queue-builder-v0.md).

It should:

- read a completed run;
- build or reference a PR130-style interpretation packet;
- create a queue item;
- preserve source refs and privacy status;
- write no raw/private content to checked-in artifacts;
- leave semantic fields empty.

No model calls yet.

### PR181 Operator/Codex Interpretation Prompt Packet v0

Prepare a bounded prompt/input packet for an operator or Codex session to fill
the PR133 interpretation read schema.

PR181 is implemented as
[Decision Work Operator/Codex Interpretation Prompt Packet](decision-work-operator-codex-interpretation-prompt-packet-v0.md).

This is the first bridge from deterministic queue to probabilistic
interpretation, but it should still not call providers from repo code.

The packet should include:

- allowed source summaries or refs;
- fields to fill;
- forbidden claims;
- output schema;
- privacy constraints;
- examples from the three existing cases;
- validation command.

### PR182 Generated Interpretation Read Intake And Validator v0

Accept an externally supplied interpretation read JSON and validate it before
it can feed the brief.

PR182 is implemented as
[Decision Work Generated Interpretation Read Intake](decision-work-generated-interpretation-read-intake-v0.md).

It should reject:

- missing source refs;
- missing uncertainty;
- product-proof claims;
- human-validation claims;
- quality labels;
- action authorization;
- raw/private markers;
- local absolute paths;
- unsupported schema versions.

PR182 does not generate reads, modify reads, render briefs, enrich briefs,
create triage, update resolver refs, update runtime sidecars, call providers,
or authorize action.

### PR183 Three-Case Generated Interpretation Read Intake Review v0

Review the generated-read intake path against the three known checked-in reads
and synthetic rejected reads:

PR183 is implemented as
[Decision Work Generated Interpretation Read Intake Review](decision-work-generated-interpretation-read-intake-review-v0.md).

- launch-public-enterprise-beta;
- deploy-assisted-intake-routing;
- ceo-remove-founding-cofounder.

Do not require regeneration in this slice. PR182 validates generated reads but
does not generate them, so the immediate review should inspect accepted and
rejected intake behavior before a true regeneration/operator-read pilot.

Require:

- same decision frame or a documented uncertainty;
- same broad action-consequence direction or a documented disagreement;
- visible source limits;
- non-proof boundaries;
- high-risk routing for cofounder/governance.

This PR decides whether the new supply path is good enough for a one-case
operator/Codex generated-read pilot.

### PR184 Operator/Codex Generated Read Pilot v0

PR184 is implemented as
[Decision Work Operator/Codex Generated Read Pilot](decision-work-operator-codex-generated-read-pilot-v0.md).

Run exactly one checked-in-safe generated-read candidate through the PR182
intake validator:

```text
operator/Codex generated read candidate
-> generated-read intake validator
-> accepted / rejected / repair-required intake result
-> next supply-planning gate
```

This slice still does not render a Decision Work Brief, enrich a brief,
generate triage, mark resolver refs usable, update runtime sidecars, create a
queue worker, call providers, or claim semantic correctness. It selects a generated
read-to-brief supply plan next.

### PR185 Generated Read To Brief Supply Plan v0

PR185 is implemented as
[Decision Work Generated Read To Brief Supply Plan](decision-work-generated-read-to-brief-supply-plan-v0.md).

Define how an accepted generated read may safely become Decision Work Brief,
enrichment, triage, resolver, and sidecar supply without bypassing privacy,
source-depth, and non-claim boundaries.

This should be a plan/gate before a builder consumes the new read.

### PR186 Decision Work Generated Read Brief Supply Adapter v0

PR186 is implemented as
[Decision Work Generated Read Brief Supply Adapter](decision-work-generated-read-brief-supply-adapter-v0.md).

Build the deterministic adapter that takes an accepted generated read and PR182
intake result and emits a safe brief-supply packet for later offline rendering.

This adapter may validate, normalize, copy allowed fields, preserve source refs,
preserve uncertainty, and block/defer unsafe supply. It must not add semantic
interpretation, render a brief, enrich a brief, generate triage, mark resolver
refs usable, update runtime sidecars, or call providers.

### PR187 Decision Work Generated Read Brief Rendering Pilot v0

PR187 is implemented as
[Decision Work Generated Read Brief Rendering Pilot](decision-work-generated-read-brief-rendering-pilot-v0.md).

Use the PR186 supply packet to render exactly one offline generated-read brief
for the launch-beta checked-in-safe generated read.

This should still be offline/internal, should not update runtime sidecars, and
should preserve the distinction between structural supply readiness and semantic
truth.

### PR188 Decision Work Generated Read Brief vs Existing Brief Review v0

PR188 is implemented as
[Decision Work Generated Read Brief vs Existing Brief Review](decision-work-generated-read-brief-vs-existing-brief-review-v0.md).

Compare the launch-beta generated-read-rendered brief against the existing
rendered and enriched launch-beta brief surfaces before trying a second
generated-read case.

The review should answer whether the generated-read brief preserves the same
core decision/action consequence, uncertainty, source limits, privacy limits,
and non-claims, and whether fluency creates overtrust risk.

This PR still must not generate a read, render a second case, enrich, generate
triage, mark resolver refs usable, update sidecars, call providers, or claim
semantic correctness.

### PR189 Decision Work Generated Read Second Brief Rendering Pilot v0

PR189 is implemented as
[Decision Work Generated Read Second Brief Rendering Pilot](decision-work-generated-read-second-brief-rendering-pilot-v0.md).

Run the generated-read-to-brief path on one second checked-in-safe case:
`deploy-assisted-intake-routing`. This tests compliance/workflow caveats and a
different decision family than launch timing.

PR189 should remain offline, Codex/operator-assisted, and deterministic after
the checked-in read exists. It must not use raw/private content, create a new
run, call models, generate triage, mark resolver refs usable, or update runtime
sidecars.

### PR190 Decision Work Generated Read Brief Two-Case Pattern Review v0

PR190 is implemented as
[Decision Work Generated Read Brief Two-Case Pattern Review](decision-work-generated-read-brief-two-case-pattern-review-v0.md).

Review the launch-beta and deploy-intake generated-read-rendered briefs
together and decide whether the path is stable enough to plan generated-read
triage supply, needs a renderer/supply patch, needs a third case, or should
stop for source-depth or product-surface review.

### PR191 Decision Work Generated Read Triage Supply Plan v0

PR191 is implemented as
[Decision Work Generated Read Triage Supply Plan](decision-work-generated-read-triage-supply-plan-v0.md).

Define the safe plan for turning generated-read brief supply and rendered brief
findings into future triage supply. This is a plan before implementation, and
does not generate automatic triage, mark resolver refs usable, update runtime
sidecars, call models, claim proof, score quality, or authorize action.

### PR192 Decision Work Generated Read Triage Supply Adapter v0

PR192 is implemented as
[Decision Work Generated Read Triage Supply Adapter](decision-work-generated-read-triage-supply-adapter-v0.md).

It builds the deterministic adapter that prepares a triage-supply packet from
generated-read artifacts. The adapter validates, normalizes, copies allowed
routing inputs, preserves evidence-only fields, and records blockers. It still
does not generate triage, create a triage read, mark resolver refs usable,
update runtime sidecars, change runtime behavior, call models, claim proof,
score quality, or authorize action.

### PR193 Decision Work Generated Read Triage Generation Pilot v0

PR193 is implemented as
[Decision Work Generated Read Triage Generation Pilot](decision-work-generated-read-triage-generation-pilot-v0.md).

It creates the first generated-read triage pilot over the launch-beta
triage-supply packet. The provisional triage read routes attention only and
still does not mark resolver refs usable, update sidecars, wire runtime
behavior, call models/providers from repo code, score answer quality, claim
proof, or authorize action.

### PR194 Decision Work Generated Read Triage Pilot Review v0

PR194 is implemented as
[Decision Work Generated Read Triage Pilot Review](decision-work-generated-read-triage-pilot-review-v0.md).

It reviews whether the first generated triage read is safe and useful enough to
attempt a second case. The review stays docs/review/tests only and selects
deploy-intake next while preserving the no-resolver, no-sidecar, no-runtime,
no-model-call, no-scoring, no-proof, and no-action boundary.

### PR195 Second Generated Read Triage Pilot v0

PR195 is implemented as
[Decision Work Generated Read Second Triage Pilot](decision-work-generated-read-second-triage-pilot-v0.md).

It runs the generated-read triage pilot on `deploy-assisted-intake-routing`.
The second triage read preserves healthcare operations and compliance caveats,
avoids broad clinical/legal advice, and stops before resolver approval, runtime
sidecar updates, runtime wiring, model calls, product proof, human validation,
scoring, or action authorization.

### PR196 Two-Case Generated Read Triage Pattern Review v0

PR196 is implemented as
[Decision Work Generated Read Triage Two-Case Pattern Review](decision-work-generated-read-triage-two-case-pattern-review-v0.md).

It compares the launch-beta and deploy-intake generated triage reads together.
The review finds the route vocabulary stable enough to plan generated-read
resolver supply while preserving that triage routes are attention-routing
states, not answer-quality scores, ref approval, runtime sidecar permission, or
action authorization.

### PR197 Decision Work Generated Read Resolver Supply Plan v0

Implemented as
[Decision Work Generated Read Resolver Supply Plan](decision-work-generated-read-resolver-supply-plan-v0.md).

Define the safe plan for turning generated-read artifacts and generated triage
reads into resolver-supply candidates. The plan separates resolver supply from
resolver approval, lets candidate packets preserve runtime/user-surface
blocking, and still stops before resolver approval, runtime sidecar updates,
runtime wiring, model calls, product proof, human validation, scoring, advice
correctness claims, or action authorization.

### PR198 Decision Work Generated Read Resolver Supply Adapter v0

Implemented as
[Decision Work Generated Read Resolver Supply Adapter](decision-work-generated-read-resolver-supply-adapter-v0.md).

Implement the deterministic adapter that prepares resolver-candidate packets
from generated-read artifacts and generated triage reads. The adapter preserves
refs, route summaries, runtime/user-surface blocking, source status,
uncertainty, privacy limits, custody flags, and non-claims without approving
resolver refs, updating sidecars, wiring runtime, calling models, scoring,
proving value, validating advice correctness, or authorizing action.

### PR199 Decision Work Generated Read Resolver Supply Review v0

Implemented as
[Decision Work Generated Read Resolver Supply Review](decision-work-generated-read-resolver-supply-review-v0.md).

Review the launch-beta and deploy-intake resolver-supply candidate packets
before any resolver approval, runtime sidecar update, runtime wiring, model
calls, scoring, proof claims, or action authorization. The review confirms
candidate packets remain candidate summaries, not approved refs, runtime
permission, user-surface readiness, quality labels, proof, or action
authorization.

### PR200 Decision Work Automatic Semantic Supply Pre-Runtime v1 Package Gate v0

Implemented as
[Decision Work Automatic Semantic Supply Pre-Runtime v1 Package Gate](decision-work-automatic-semantic-supply-pre-runtime-v1-package-gate-v0.md).

Package PR178 through PR199 as a pre-runtime v1 capability. The package claims
only an offline, checked-in-safe, pre-runtime chain from generated
interpretation reads to resolver-supply candidate packets, with validation,
rendering, triage, and resolver-boundary safeguards. It does not claim runtime
attachment, resolver approval, sidecar updates, default-on behavior,
arbitrary-run production automation, human validation, product proof, advice
correctness, scoring, or action authorization.

### PR201 Resolver Candidate To Runtime Sidecar Update Plan v0

Implemented as
[Decision Work Resolver Candidate Sidecar Update Plan](decision-work-resolver-candidate-sidecar-update-plan-v0.md).

Plan how a future layer could consider resolver-supply candidates for runtime
sidecar update packets without treating candidates as approval. The plan keeps
sidecar update packets offline and proposed only: not actual `decision_work/`
sidecar writes, not archive mutation, not resolver approval, not runtime
wiring, not user-surface readiness, not quality labels, and not action
authorization.

### PR202 Resolver Candidate Sidecar Update Packet Adapter v0

Implemented as
[Decision Work Resolver Candidate Sidecar Update Packet Adapter](decision-work-resolver-candidate-sidecar-update-packet-adapter-v0.md).

Implement a deterministic adapter that turns a PR198 resolver-supply candidate
packet into an offline sidecar update packet artifact. The adapter does not
write sidecars, mutate archives, approve resolver refs, wire runtime, call
models, score answer quality, claim proof, or authorize action.

### PR203 Decision Work Sidecar Update Packet Review v0

Implemented as
[Decision Work Sidecar Update Packet Review](decision-work-sidecar-update-packet-review-v0.md).

Review launch/deploy sidecar update packets before any actual sidecar write,
archive mutation, resolver approval, runtime wiring, model calls, scoring,
proof claims, or action authorization. The review confirms proposed packets
remain offline artifacts and selects a pre-write package gate next.

### PR204 Decision Work Sidecar Update Packet Pre-Write Package Gate v0

Implemented as
[Decision Work Sidecar Update Packet Pre-Write Package Gate](decision-work-sidecar-update-packet-prewrite-package-gate-v0.md).

Package PR201 through PR203 as a narrow pre-write capability. The package keeps
sidecar update packets offline, deterministic, inspectable, and separate from
actual sidecar writes, archive mutation, resolver approval, runtime wiring,
default-on behavior, proof claims, scoring, and action authorization.

### PR205 Runtime Sidecar Write Plan v0

Implemented as
[Decision Work Runtime Sidecar Write Plan](decision-work-runtime-sidecar-write-plan-v0.md).

Plan the first actual sidecar-write implementation. This remains
docs/review/tests only: no sidecar write code, no archive mutation, no runtime
wiring, no resolver approval, no default-on behavior, no model calls, no
scoring, no proof claims, and no action authorization. The plan selects a
future default-off dry-run adapter next.

### PR206 Default-Off Sidecar Write Dry-Run Adapter v0

Implemented as
[Decision Work Sidecar Write Dry-Run Adapter](decision-work-sidecar-write-dry-run-adapter-v0.md).

Build a deterministic dry-run adapter that consumes PR202 sidecar update
packets and emits `lolla.decision_work_sidecar_write_dry_run.v0` results.
Launch-beta produces `dry_run_ready`; deploy-intake produces
`dry_run_packet_with_runtime_block`. Optional preview files are written only
under an explicit safe output directory. The adapter still does not perform
actual sidecar writes, write `decision_work/`, mutate archives, wire runtime,
approve resolver refs, make runtime default-on, call models, score answer
quality, claim proof, or authorize action.

Selected gate:

```text
proceed_to_sidecar_write_dry_run_review
```

Do not make runtime attachment default-on from this gate.

### PR207 Sidecar Write Dry-Run Review v0

Implemented as
[Decision Work Sidecar Write Dry-Run Review](decision-work-sidecar-write-dry-run-review-v0.md).

Review the launch-beta and deploy-intake dry-run outputs before any actual
sidecar-write implementation. The review confirms launch produces
`dry_run_ready`, deploy-intake preserves `dry_run_packet_with_runtime_block`,
preview files stay inside explicit safe output directories, and
`actual_sidecar_write_performed`, `archive_mutated`, `runtime_wiring_changed`,
and `resolver_refs_approved` remain false.

Selected gate:

```text
proceed_to_sidecar_write_dry_run_package_gate
```

Recommended next PR:

```text
PR208 Sidecar Write Dry-Run Package Gate v0
```

Do not implement PR208 from this review.

### PR208 Sidecar Write Dry-Run Package Gate v0

Implemented as
[Decision Work Sidecar Write Dry-Run Package Gate](decision-work-sidecar-write-dry-run-package-gate-v0.md).

Package PR206 through PR207 as a narrow dry-run capability. The package claim
is that Decision Work Sidecar Write Dry-Run v1 is functional as an offline,
deterministic preview layer that can show what would be written from a sidecar
update packet while preserving actual-write, archive-mutation,
resolver-approval, runtime-wiring, proof, scoring, and action-authorization
prohibitions.

Selected gate:

```text
sidecar_write_dry_run_v1_packaged
```

Recommended next PR:

```text
PR209 Runtime Sidecar Write Contract v0
```

Do not implement sidecar writes from this package gate.

### PR209 Runtime Sidecar Write Contract v0

Implemented as
[Decision Work Runtime Sidecar Write Contract](decision-work-runtime-sidecar-write-contract-v0.md).

Define the contract for a future explicit operator sidecar write adapter
without implementing writes. The contract accepts PR202 sidecar update packets
and PR206 dry-run results as inputs, requires a matching dry run, explicit
archive path, explicit mode, path safety checks, privacy checks, authority
claim checks, and default-off runtime posture, and records write modes,
statuses, allowed files, forbidden content, audit receipt requirements, and
fail-closed rules.

Selected gate:

```text
proceed_to_explicit_operator_sidecar_write_adapter
```

Recommended next PR:

```text
PR210 Explicit Operator Sidecar Write Adapter v0
```

Do not implement PR210 from this contract. PR209 still does not write
sidecars, write `decision_work/`, mutate archives, wire runtime, approve
resolver refs, make runtime default-on, call models, score answer quality,
claim proof, or authorize action.

### PR210 Explicit Operator Sidecar Write Adapter v0

Implemented as
[Decision Work Explicit Operator Sidecar Write Adapter](decision-work-explicit-operator-sidecar-write-adapter-v0.md).

Build the first write adapter, but constrain it to explicit operator
fixture/output directories only. The adapter consumes a PR202 sidecar update
packet and a matching PR206 dry-run result, writes sidecar-shaped files only
under a safe caller-supplied temp/output `decision_work` directory, and emits
`lolla.decision_work_explicit_operator_sidecar_write_receipt.v0`.

Launch-beta produces:

```text
write_completed_fixture_only
```

Deploy-intake produces:

```text
write_completed_blocked_state_fixture_only
```

Selected gate:

```text
proceed_to_explicit_operator_sidecar_write_review
```

Recommended next PR:

```text
PR211 Explicit Operator Sidecar Write Review v0
```

Do not implement PR211 review findings as runtime behavior. PR210 still does
not write real archives, mutate historical archive folders, wire runtime,
update the post-archive hook, approve resolver refs, call models, score answer
quality, claim proof, or authorize action.

### PR211 Explicit Operator Sidecar Write Review v0

Implemented as
[Decision Work Explicit Operator Sidecar Write Review](decision-work-explicit-operator-sidecar-write-review-v0.md).

Review the launch-beta and deploy-intake fixture-only sidecar writes before
packaging the explicit operator write layer. The review checks that launch
produces `write_completed_fixture_only`, deploy produces
`write_completed_blocked_state_fixture_only`, generated fixture files stay
inside explicit safe temp/output targets, real/historical archive mutation is
false, runtime wiring is false, resolver refs remain unapproved, and all proof,
scoring, validation, and action-authority claims remain closed.

Selected gate:

```text
proceed_to_explicit_operator_sidecar_write_package_gate
```

Recommended next PR:

```text
PR212 Explicit Operator Sidecar Write Package Gate v0
```

Do not implement PR212 from this review. PR211 still does not write real
archives, mutate historical archive folders, wire runtime, update the
post-archive hook, approve resolver refs, call models, score answer quality,
claim proof, or authorize action.

### PR212 Explicit Operator Sidecar Write Package Gate v0

Implemented as
[Decision Work Explicit Operator Sidecar Write Package Gate](decision-work-explicit-operator-sidecar-write-package-gate-v0.md)
with the machine-readable
[explicit operator sidecar write package manifest](decision-work-explicit-operator-sidecar-write-package-manifest-v0.json).

Package PR210 through PR211 as Decision Work Explicit Operator Sidecar Write v1.
The narrow claim is that a controlled explicit operator write layer can write
sidecar-shaped files into safe fixture/operator `decision_work` target
directories from validated PR202 sidecar update packets and matching PR206
dry-run results.

Selected gate:

```text
explicit_operator_sidecar_write_v1_packaged
```

Recommended next PR:

```text
PR213 Controlled Archive Sidecar Write Fixture Plan v0
```

Do not implement PR213 from this package. PR212 still does not write real
archives, mutate historical archive folders as normal behavior, wire runtime,
update the post-archive hook, approve resolver refs, call models, score answer
quality, claim proof, or authorize action.

## Readiness Gates

Automatic semantic supply is not ready for normal use until:

- generated interpretation reads pass schema and boundary validation;
- generated reads reproduce the core action-consequence pattern on the three
  curated cases;
- at least one non-curated completed run produces a useful, caveated, source-
  linked brief;
- high-risk receipt language is visibly different from ordinary available
  receipt language;
- missing/private source limits remain clear;
- agent handoff remains inspection-only;
- no runtime model calls are needed;
- raw/private content remains out of checked-in artifacts;
- the sidecar can still defer or block without looking broken.

## Stop Lines

Do not:

- run `$lolla` as part of implementation;
- invoke the Lolla skill;
- call provider/model APIs from repo code in this phase;
- make runtime attachment default-on;
- perform direct runtime interpretation;
- copy raw/private conversation text into checked-in artifacts;
- expose provider text or private ledgers;
- mutate historical archives;
- score answer quality;
- create approval labels;
- claim human validation;
- claim product proof;
- claim advice correctness;
- authorize agent or automatic action.

## Product Language

Use this language:

> Automatic semantic supply prepares the missing interpreted Decision Work
> artifacts after a run is complete, validates them, and makes them available
> to the sidecar only when they are safe enough to carry.

Avoid this language:

> The runtime understands every new conversation.

Use this language:

> The system can defer when safe semantic inputs do not exist.

Avoid this language:

> The brief proves Lolla improved the decision.

## Expected Outcome

At the end of this phase, maintainers should know whether Lolla can move from:

```text
prepared cases can be attached
```

to:

```text
new completed runs can enter an offline interpretation queue and produce
validated, caveated Decision Work artifacts that the sidecar can attach
```

The target is not confidence theater. The target is a bounded, inspectable,
repeatable supply path for the semantic artifacts that make the Decision Work
Brief useful.
