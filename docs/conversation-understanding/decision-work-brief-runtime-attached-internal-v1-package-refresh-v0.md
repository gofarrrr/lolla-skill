# Decision Work Brief Runtime-Attached Internal v1 Package Refresh v0

Status: PR177 package refresh gate

Date: 2026-07-02

Manifest:
[runtime-attached internal v1 package refresh manifest](decision-work-brief-runtime-attached-internal-v1-package-manifest-v0.json)

## Purpose

PR177 packages the current Decision Work Brief runtime-attachment tranche for
maintainer review. It refreshes the earlier PR167 package gate so the package
now includes PR168 through PR176: safe supply planning, resolver contract,
resolver implementation, resolver-aware bundle integration, runtime hook
resolver wiring, resolver fixture review, checked-in-safe case registry, and
registry-backed fixture review.

This is a package, review, and manifest slice only. It does not add runtime
behavior, resolver behavior, queue behavior, model calls, prompt changes, or
default-on attachment.

## Narrow Internal v1 Claim

Decision Work Brief Runtime-Attached Internal v1 is functional as an internal,
default-off, post-archive sidecar path for completed runs when safe refs are
supplied manually or through checked-in-safe registry fixtures.

That means the package can claim:

- default-off post-archive attachment behind
  `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE`;
- resolver-aware bundle generation;
- manual safe-ref supply;
- checked-in-safe registry fixture supply for three known examples;
- available, deferred, blocked, agent-only, and failed-closed sidecar states;
- short receipt generation;
- agent handoff packet generation;
- custody, status, missingness, and non-claim preservation.

It does not mean customer readiness or arbitrary-run semantic coverage.

## Flag Behavior

The runtime flag is:

```text
LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE
```

Enabled values are:

```text
1
true
on
yes
```

When the flag is off:

- no Decision Work Brief resolver runs;
- no runtime bundle runs;
- no `decision_work/` sidecar is written;
- archive behavior is unchanged.

When the flag is on:

- the hook runs only after archive completion;
- it builds safe supply resolver output;
- it passes resolver output into the resolver-aware runtime bundle;
- it writes a `decision_work/` sidecar when possible;
- it records deferred, blocked, generated, agent-only, or failed-closed status;
- it remains non-blocking for archive completion;
- it fails closed if bundle generation raises.

The hook still does not interpret messy conversation meaning.

## Sidecar Surface

Depending on resolver state and available safe refs, the sidecar may include:

- `decision_work/attachment_status.json`;
- `decision_work/safe_supply_resolver.json`;
- `decision_work/decision_work_brief.json`;
- `decision_work/decision_work_brief.md`;
- `decision_work/decision_work_brief_enriched.md`;
- `decision_work/automatic_triage_packet.json`;
- `decision_work/automatic_triage_read.json`;
- `decision_work/agent_handoff_packet.json`;
- `decision_work/user_receipt.md`.

The bundle copies only resolver-approved safe refs. It does not copy raw
conversation text, raw revised-answer text, raw memo text, provider text,
private ledgers, local paths, or credential material.

## Safe Supply

The runtime-attached path can consume safe inputs in two reviewed ways.

Manual supply:

- an operator provides explicit safe brief, enriched brief, interpretation
  read, triage packet, or triage read refs;
- the resolver validates refs, schemas, privacy markers, and feedability;
- the bundle uses only resolver-approved refs.

Checked-in-safe registry supply:

- PR175 defines a deterministic registry for three known examples:
  `launch-public-enterprise-beta`,
  `deploy-assisted-intake-routing`, and
  `ceo-remove-founding-cofounder`;
- PR176 verifies those registry refs can drive generated temporary hook
  sidecars through the resolver-aware hook seam;
- this is curated demo/test supply only, not a general live-run solution.

No-safe-input behavior:

- the resolver records `no_safe_inputs` or a deferred reason;
- the bundle writes a deferred sidecar and receipt;
- no fake brief is created.

Unsafe-input behavior:

- unsafe refs, private-marker content, unsupported schemas, and forbidden
  direct runtime interpretation are blocked;
- the sidecar records the blocker;
- unsafe content is not copied into the sidecar.

Failure behavior:

- if bundle generation fails, the hook writes `failed_closed` when possible;
- archive completion remains non-blocking.

## User Receipt

The receipt is intentionally short. It communicates one of these states:

- available;
- available for agent inspection;
- deferred;
- blocked;
- failed closed;
- not requested.

Every receipt keeps the caveat visible: the brief is an audit summary, not proof
that the advice is correct.

The receipt is still a product-surface weakness. The cofounder/governance case
can generate an available receipt while the full brief carries legal,
governance, equity, board, and relationship caveats. PR177 packages that
limitation rather than hiding it.

## Agent Handoff

The agent handoff packet communicates:

- source run ref;
- attachment status ref;
- brief and enriched brief refs;
- triage refs;
- resolver summary;
- source status;
- privacy/redaction status;
- missingness;
- uncertainty and route outputs when available;
- explicit non-claims;
- `agent_action_authorized: false`.

The handoff is for inspection. It is not action authorization.

## What Remains Unresolved

Runtime-Attached Internal v1 still does not solve:

- arbitrary-run semantic brief supply;
- first-class production hook registry lookup by case key;
- offline interpretation queue behavior;
- customer-facing product copy;
- cofounder/governance sensitivity in the short receipt;
- human validation;
- product proof;
- advice correctness;
- default-on readiness.

The normal arbitrary-run outcome remains deferred unless safe run-specific
brief, enriched brief, interpretation, and triage refs already exist.

## Why Default-On Is Still Not Recommended

Default-on attachment would make many runs produce deferred notes or
source-limited sidecars before the product surface and semantic supply path are
ready. It could also make curated registry fixtures look like general product
coverage. The current default-off flag is the right internal boundary until
safe run-specific interpretation supply and user-facing receipt language are
settled.

## Package Conclusion

Runtime-Attached Internal v1 is packageable for maintainer review.

The recommended next step is:

```text
Audit/stage/commit the PR160-PR177 runtime-attached internal v1 package using a
narrow manifest-derived pathspec.
```

Do not use broad staging. The package manifest exists to keep the next staging
step tight and to avoid unrelated docs, plans, synthetic reviews, skill files,
archive paths, or private material.

## Explicit Non-Claims

PR177 does not claim:

- customer readiness;
- default-on runtime behavior;
- arbitrary-run semantic coverage;
- direct runtime interpretation;
- runtime model calls;
- human validation;
- product proof;
- answer-quality scoring;
- advice correctness;
- proof that Lolla improved decisions;
- approval or certification;
- agent or automatic action authorization;
- a general arbitrary-run solution.
