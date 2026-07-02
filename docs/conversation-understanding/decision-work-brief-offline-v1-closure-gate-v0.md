# Decision Work Brief Offline v1 Closure Gate v0

Status: PR157 offline v1 closure gate

Date: 2026-07-02

Schema: `lolla.decision_work_brief_offline_v1_closure_gate.v0`

## Purpose

PR157 decides whether the Decision Work Brief, interpretation-enrichment, and
automatic-triage evidence chain is coherent enough to call functional offline
v1 with explicit limitations.

This is a closure/readiness review, not product validation. It asks whether
the offline chain can preserve custody, render a readable brief, enrich the
brief with bounded interpretation, prepare automatic triage packets, run a
Codex-assisted provisional triage read, and keep limitations visible.

The checked-in closure review is:

- [PR157 closure review JSON](../../reviews/codex-assisted/decision-work-brief-offline-v1-closure-gate-v0/review.json)

## End-To-End Chain

The offline chain now has:

- a Decision Work Brief schema and deterministic packet/renderer path;
- checked-in-safe rendered briefs for three decision families;
- provisional conversation interpretation reads with source refs and
  uncertainty;
- deterministic enrichment rules and an offline enriched-brief builder;
- builder-generated enriched briefs for all three cases;
- additional local-private adequacy checks that record safe conclusions only;
- human-review intake and pilot scaffolding that remains unfilled;
- a human-review awaiting-response pause gate;
- an automatic triage contract;
- a deterministic automatic triage packet builder;
- one Codex-assisted provisional automatic triage read over the three cases.

## Functional Offline v1 Claim

PR157 supports a narrow functional offline v1 claim:

```text
Given completed Lolla run artifacts and existing offline evidence artifacts,
the system can preserve custody/source status, render a readable Decision Work
Brief, enrich it with bounded provisional interpretation, prepare automatic
triage packets, and create a provisional triage read that routes attention to
source-depth, overtrust, private-context, domain/legal, agent-inspection, and
runtime-blocker concerns.
```

That is an offline evidence-system claim. It is not a customer-readiness claim.

## What Remains Blocked

Runtime integration remains blocked because:

- no runtime attachment contract has been implemented;
- no prompt or live extraction path has been changed;
- the triage read is Codex-assisted and provisional;
- no real human review response exists;
- private/source-depth questions remain unresolved;
- domain/legal/compliance/governance calibration has not occurred.

Customer-facing claims remain blocked because:

- the artifacts are checked-in-safe compressed summaries;
- raw/private conversation details are not checked in;
- human validation is absent;
- the system has not proven answer correctness or product value;
- the cofounder and healthcare cases can create false confidence if caveats
  are separated from the main brief.

## Decision Gate

Decision gate:

```text
package_offline_v1
```

Reason:

PR155 and PR156 work, the limitations are explicit, runtime/customer-facing
claims remain blocked, and the system can honestly be packaged as functional
offline v1 with human calibration deferred.

Recommended next slice:

```text
PR158 Decision Work Brief Offline v1 Package Gate v0
```

## Explicit Non-Claims

PR157 does not:

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
- fill human-review answers;
- claim human validation;
- claim product proof;
- score answer quality;
- approve or certify advice;
- authorize agent or automatic action;
- implement runtime attachment.
