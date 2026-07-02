# Decision Work Brief Runtime Eligibility Gate v0

Status: PR163 eligibility and blocker gate

Date: 2026-07-02

## Purpose

PR163 factors the runtime-attachment decision into a deterministic eligibility
and blocker layer.

The gate answers whether a post-archive Decision Work Brief attachment should
be treated as generated, blocked, deferred, or agent-inspection-only. It uses
only run-artifact presence, JSON parseability, output-path safety, custody
flags, attachment status, and explicit triage route fields. It does not infer
new conversation meaning.

## Inputs

The gate can inspect:

- a completed run directory;
- the intended output directory;
- a PR162 `attachment_status.json` object;
- an existing provisional triage read;
- an explicit case id.

It does not read raw conversation content for export and does not generate a
new brief.

## Hard Blockers

Hard blockers include:

- incomplete run artifacts;
- archive not finalized;
- missing revised answer;
- missing required structured artifacts;
- malformed JSON;
- failed hygiene or boundary lint status when provided;
- unsafe output path;
- unresolved source refs;
- privacy marker or raw-private export risk;
- schema validation failure;
- attempted model/provider/runtime invocation;
- attempted archive mutation;
- attempted answer-quality scoring;
- attempted action authorization.

Any hard blocker produces `blocked`.

## Soft Triage Blockers

Soft triage blockers are routing signals, not correctness judgments. They
include:

- source depth too thin;
- high overtrust risk;
- private context required;
- legal, domain, compliance, medical, financial, governance, employment, or
  safety escalation;
- relationship or political sensitivity;
- unresolved lost-value risk;
- agent-inspection-only;
- runtime attachment blocked.

Soft blockers can route an otherwise generated attachment to
`generated_agent_only`, but they do not become a score, approval, certification,
or action authorization.

## States

The gate emits only the PR160 attachment states:

- `not_requested`
- `blocked`
- `deferred`
- `generated`
- `generated_agent_only`
- `failed_closed`

## Decision Gate

Decision gate:

```text
proceed_to_runtime_receipt_renderer
```

Reason:

The eligibility gate can produce generated, blocked, deferred, and agent-only
states from fixtures without raw/private content. The next slice should render
the short user receipt for those states.

## Explicit Non-Claims

PR163 does not:

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
