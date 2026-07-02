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

### PR180 Offline Interpretation Queue Packet Builder v0

Build the deterministic queue packet/preparation layer.

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

### PR183 Three-Case Regeneration Review v0

Use the queue/prompt/intake path against the three known cases:

- launch-public-enterprise-beta;
- deploy-assisted-intake-routing;
- ceo-remove-founding-cofounder.

Compare regenerated reads against the existing curated reads. Do not require
identical wording. Require:

- same decision frame or a documented uncertainty;
- same broad action-consequence direction or a documented disagreement;
- visible source limits;
- non-proof boundaries;
- high-risk routing for cofounder/governance.

This PR decides whether the new supply path is good enough for a one-new-run
pilot.

### PR184 Queue-To-Brief-To-Sidecar Pilot v0

Run the full path on exactly one case:

```text
queue item
-> generated interpretation read
-> Decision Work Brief
-> enriched brief
-> triage read
-> resolver-approved refs
-> runtime sidecar bundle
```

The output should still be offline/internal. No default-on hook. No customer
claim.

### PR185 First New Completed Run Supply Pilot v0

Use one completed run that was not one of the three curated registry cases.

Goal:

> Can the system pick up a new completed run and produce safe Decision Work
> artifacts without hand-building the whole interpretation path?

This PR should be allowed to conclude "not yet."

### PR186 Automatic Semantic Supply Closure Gate v0

Review PR178-PR185 and decide the next path:

- continue with more pilots;
- patch prompt packet / validator;
- patch high-risk receipt language;
- add a background queue runner;
- add first-class production registry lookup;
- stop and keep the feature internal.

Do not make runtime attachment default-on from this gate.

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
