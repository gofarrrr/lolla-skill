# Decision Work Brief Runtime Attachment Contract v0

Status: PR160 runtime attachment contract

Date: 2026-07-02

Schema: `lolla.decision_work_brief_runtime_attachment_contract.v0`

## Purpose

PR160 defines the contract for attaching Decision Work Brief artifacts to a
completed Lolla run. It does not implement generation, sidecar writing, runtime
hooks, model calls, archive mutation, scoring, product proof, human validation,
or agent action authorization.

The contract follows the PR159 runtime attachment PRD:

```text
Lolla run completes
-> archive is finalized
-> deterministic hygiene passes
-> optional flagged post-archive Decision Work Brief generation
-> automatic triage routes the output
-> user sees a short receipt plus link, or a clear blocked/deferred note
```

## Attachment Modes

The contract allows four modes:

- `disabled`: no runtime attachment is requested.
- `manual_post_archive`: an operator runs a post-archive bundle command.
- `flagged_post_archive`: a future default-off runtime hook may run after
  archive finalization when an explicit local flag is set.
- `future_default_not_implemented`: reserved only to make default-on behavior
  explicitly out of scope.

`disabled` is the default.

## Attachment States

The contract recognizes these states:

- `not_requested`
- `not_eligible`
- `blocked`
- `deferred`
- `generated`
- `generated_agent_only`
- `failed_closed`

Blocked and failed states are first-class outputs. They are not advice-quality
judgments.

## Run Eligibility

The first runtime-safe path may only consider a completed, archived Lolla run
with structured artifacts and conservative custody. The contract requires:

- archive finalized;
- revised answer present;
- required structured artifacts present and parseable;
- hygiene status clean enough for checked-in-safe post-processing;
- source refs resolvable;
- output path safe;
- no raw/private export in default mode;
- no product-proof, human-validation, scoring, approval, or action-authority
  claims.

## User Receipt Shape

The user-facing surface is a short receipt, not the full brief:

```text
Decision Work Brief: available

What changed: <one short action-consequence line or "See brief">

Main caveat: this is an audit summary, not proof that the advice is correct.

Open full brief: <artifact ref>
```

When the brief is blocked or deferred, the receipt names the state and reason.
It must always include a caveat/non-claim line.

## Agent Handoff Shape

Another agent should receive structured refs and custody information, not raw
private material by default. The contract requires handoff refs for:

- attachment status;
- brief JSON/Markdown when present;
- enriched brief when present;
- automatic triage packet/read when present;
- source refs and source status;
- privacy/redaction status;
- missingness and uncertainty;
- route outputs;
- blocked/deferred state;
- explicit `agent_action_authorized: false`.

## Blocker Vocabulary

Hard blockers stop user-visible generation. Soft triage blockers may still
permit an internal or agent-only bundle.

Hard blockers include incomplete artifacts, archive not finalized, missing
revised answer, malformed JSON, failed hygiene, unsafe output path, unresolved
source refs, privacy-marker risk, schema failure, attempted model/provider or
runtime invocation, attempted scoring, and attempted action authorization.

Soft triage blockers include source-depth thinness, high overtrust risk,
private-context dependency, domain/legal/compliance/medical/financial/
governance/employment/safety escalation, relationship or political sensitivity,
lost-value risk, and agent-inspection-only routing.

## Privacy And Export Policy

Default runtime attachment must be checked-in-safe metadata and rendered brief
refs only. It must not export raw conversation text, raw revised answer text,
raw memo text, provider text, private ledgers, local absolute paths, secrets, or
hidden chain-of-thought style material.

Private/local material may be recorded as available, missing, or withheld. It
must not be copied into the runtime attachment bundle by default.

## Decision Gate

Decision gate:

```text
proceed_to_runtime_sidecar_contract
```

Reason:

The contract is coherent enough to define artifact locations next. It preserves
the PR159 boundaries: post-archive, default-off, non-blocking, fail-closed,
source-limited, and unable to authorize action.

## Explicit Non-Claims

PR160 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs from repo code;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- create new Lolla runs;
- create new interpretation reads;
- create new builder outputs;
- check in raw/private content;
- claim human validation;
- claim product proof;
- score answer quality;
- approve or certify advice;
- authorize agent or automatic action;
- implement runtime attachment.
