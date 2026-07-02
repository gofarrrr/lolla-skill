# Decision Work Brief Runtime Attachment Review v0

Status: PR167 runtime attachment review

Date: 2026-07-02

Review schema: `lolla.decision_work_brief_runtime_attachment_review.v0`

Review JSON:
[PR167 review](../../reviews/codex-assisted/decision-work-brief-runtime-attachment-review-v0/review.json)

## Purpose

PR167 reviews the PR160-PR166 runtime-attachment sequence and decides whether
the system is coherent enough to package as Decision Work Brief
runtime-attached internal v1.

This is a runtime packaging review, not product validation. It does not claim
customer readiness, human validation, product proof, advice correctness,
answer-quality scoring, or action authorization.

## What Was Reviewed

The review covers:

- PR160 runtime attachment contract;
- PR161 sidecar/artifact-location contract;
- PR162 manual post-archive bundle generator;
- PR163 eligibility and blocker gate;
- PR164 short receipt renderer;
- PR165 agent handoff packet;
- PR166 default-off post-archive hook in `scripts/archive_run.py`.

## Findings

The sequence supports the intended internal v1 shape:

- attachment is default off behind `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE`;
- the hook runs after archive completion;
- default-off archive behavior is unchanged;
- enabled attachment writes only a `decision_work/` sidecar;
- bundle generation is non-blocking and fail-closed;
- blocked and deferred states are explicit;
- receipts stay short and caveated;
- agent handoff packets carry refs, route outputs, missingness, privacy status,
  and non-claims;
- no full brief is rendered into chat by default;
- no model/provider calls, scoring, approval, validation, or action
  authorization are added.

## Remaining Limits

Runtime-attached internal v1 is still limited:

- deterministic runtime code does not invent a brief from raw conversation
  content;
- a clean runtime sidecar may be `deferred` until a safe brief artifact is
  supplied;
- provisional triage remains Codex-assisted/offline and human-calibration
  deferred;
- customer-facing wording and live user experience need separate product work;
- the hook is not default-on.

## Decision Gate

Decision gate:

```text
package_runtime_attached_internal_v1
```

Reason:

The contracts, manual generation, eligibility, receipt, handoff, and
default-off post-archive hook are coherent enough to package as internal v1
with explicit limitations.

## Explicit Non-Claims

PR167 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs from repo code;
- mutate historical archives;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- create new Lolla runs;
- create new interpretation reads;
- check in raw/private content;
- claim human validation;
- claim product proof;
- score answer quality;
- approve or certify advice;
- authorize agent or automatic action;
- make runtime attachment default-on;
- claim customer readiness.
