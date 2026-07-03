# Decision Work Automatic Semantic Supply Pre-Runtime v1 Package Gate v0

Status: PR200 package gate
Date: 2026-07-03

Manifest:
[automatic semantic supply pre-runtime v1 package manifest](decision-work-automatic-semantic-supply-pre-runtime-v1-package-manifest-v0.json)

## Purpose

PR200 packages the Automatic Semantic Supply chain from PR178 through PR199 as
a pre-runtime v1 capability.

This is a package gate. It does not approve resolver refs, update sidecars,
wire runtime, make runtime attachment default-on, call providers/models,
create workers, score answer quality, claim product proof, claim human
validation, validate advice correctness, or authorize action.

## Narrow Pre-Runtime v1 Claim

Decision Work Automatic Semantic Supply Pre-Runtime v1 is functional as an
offline, checked-in-safe, pre-runtime chain from generated interpretation reads
to resolver-supply candidate packets, with validation, rendering, triage, and
resolver-boundary safeguards.

That means the package can claim:

- offline interpretation queue scaffolding exists;
- generated interpretation reads can be intake-validated;
- one launch-beta generated read and one deploy-intake generated read can be
  checked in as safe pilot artifacts;
- accepted reads can produce brief-supply packets;
- generated-read briefs can be rendered for launch-beta and deploy-intake;
- generated-read triage-supply packets can be prepared;
- checked-in-safe generated triage reads exist for launch-beta and deploy-
  intake;
- resolver-supply candidate packets can be prepared for launch-beta and
  deploy-intake;
- deploy-intake preserves runtime and user-surface blocking;
- source refs, uncertainty, privacy limits, custody flags, and non-claims
  travel forward.

It does not mean runtime attachment, resolver approval, sidecar updates,
default-on behavior, arbitrary-run production automation, human validation,
product proof, advice correctness, scoring, or action authorization.

## Functional Chain

The packaged pre-runtime chain is:

```text
automatic semantic supply PRD
-> offline queue contract
-> queue item builder
-> operator/Codex prompt packet contract
-> generated interpretation read intake validator
-> generated-read intake review
-> operator/Codex generated read pilot
-> generated-read to brief supply plan
-> generated-read brief supply adapter
-> generated-read brief rendering pilot
-> generated-read brief comparison review
-> second generated-read brief rendering pilot
-> two-case generated-read brief pattern review
-> generated-read triage supply plan
-> generated-read triage supply adapter
-> generated-read triage generation pilot
-> generated-read triage pilot review
-> second generated-read triage pilot
-> two-case generated-read triage pattern review
-> generated-read resolver supply plan
-> generated-read resolver supply adapter
-> generated-read resolver supply review
```

The final artifact in the functional chain is a resolver-supply candidate
packet. That packet is still not resolver approval.

## What Is Functional

Pre-runtime v1 can:

- represent a completed run as a queueable semantic-supply item;
- define an operator/Codex prompt packet shape;
- validate an externally supplied generated interpretation read;
- reject unsafe schema, privacy, source-ref, uncertainty, proof, quality, or
  action-authority states;
- prepare brief supply from accepted generated reads;
- render checked-in-safe generated-read briefs for two cases;
- prepare triage supply;
- review checked-in-safe generated triage reads for two cases;
- prepare resolver-supply candidate packets;
- preserve a runtime/user-surface block for deploy-intake;
- keep candidate supply separate from resolver approval.

## What Remains Missing

Pre-runtime v1 still does not provide:

- runtime sidecar updates;
- resolver approval;
- runtime wiring;
- default-on behavior;
- arbitrary-run production automation;
- queue workers or daemons;
- provider/model calls from repo code;
- generated interpretation read creation by repo code;
- generated triage creation by repo code;
- human validation;
- product proof;
- answer-quality scoring;
- advice-correctness validation;
- action authorization.

## Boundary And Non-Claims

The package preserves these boundaries:

- deterministic code may validate, normalize, copy safe refs, preserve
  missingness, and route blocked/deferred states;
- deterministic code must not infer new messy conversation meaning;
- generated-read artifacts remain provisional and source-limited;
- triage routes are attention-routing states, not quality labels;
- resolver supply candidates are not resolver approval;
- runtime sidecar update is still unavailable;
- agent and automatic action authorization stay false.

## Validation Strategy

The package gate should be validated by:

- checking the package manifest schema;
- verifying every manifest-listed file exists;
- confirming forbidden paths are absent;
- running focused tests across PR178 through PR200;
- regenerating launch/deploy brief-supply, triage-supply, and resolver-supply
  temp artifacts;
- parsing all checked-in JSON artifacts with `jq`;
- running Product Delta evidence boundary lint over touched docs/review JSON;
- checking local Markdown links;
- scanning for trailing whitespace;
- scanning for local-path, secret, raw/private-content, provider-text, and
  hidden-reasoning markers;
- confirming `SKILL.md` and `scripts/skill/*` remain untouched.

## Suggested Staging Pathspec

When this package is audited for a PR, use the manifest as the staging source
of truth. Do not stage broad directories.

Suggested shape:

```bash
git add -- $(python3 - <<'PY'
import json
from pathlib import Path

manifest_path = Path(
    "docs/conversation-understanding/"
    "decision-work-automatic-semantic-supply-pre-runtime-v1-package-manifest-v0.json"
)
manifest = json.loads(manifest_path.read_text())
paths = []
for group in manifest["included_files"].values():
    paths.extend(group)
paths.append(str(manifest_path))
seen = set()
for path in paths:
    if path not in seen:
        seen.add(path)
        print(path)
PY
)
```

Then compare the staged set against the manifest-derived set before committing.

## Decision Gate

Selected gate:

```text
automatic_semantic_supply_pre_runtime_v1_packaged
```

Recommended next step:

```text
Audit, stage, commit, push, and review the PR178-PR200 pre-runtime package.
```

Recommended next implementation PR after package review:

```text
PR201 Resolver Candidate To Runtime Sidecar Update Plan v0
```

Do not implement PR201 from this package gate. The next phase is the runtime
boundary, and it needs its own plan before anything can update sidecars.

## Explicit Non-Claims

PR200 does not claim:

- runtime attachment;
- resolver approval;
- approved resolver refs;
- runtime sidecar updates;
- runtime wiring;
- default-on behavior;
- arbitrary-run production automation;
- provider/model calls;
- queue workers or daemons;
- product proof;
- human validation;
- answer-quality scoring;
- advice correctness;
- proof that Lolla improved decisions;
- agent action authorization;
- automatic action authorization.
