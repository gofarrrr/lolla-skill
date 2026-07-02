# Decision Work Brief Offline v1 Package Gate v0

Status: PR158 offline v1 package gate

Date: 2026-07-02

Schema: `lolla.decision_work_brief_offline_v1_package_manifest.v0`

## Purpose

PR158 packages the Decision Work Brief Offline v1 evidence system after PR157
selected `package_offline_v1`.

The package is a narrow offline-v1 claim:

```text
The Decision Work Brief system can preserve source/custody status, render a
readable brief, enrich it with bounded provisional interpretation, prepare
automatic triage packets, and create a provisional triage read that routes
attention to source-depth, overtrust, private-context, domain/legal,
agent-inspection, and runtime-blocker concerns.
```

This is not runtime integration, customer readiness, human validation, product
proof, answer-quality scoring, approval, certification, or agent action
authorization.

The package manifest is:

- [Decision Work Brief Offline v1 Package Manifest](decision-work-brief-offline-v1-package-manifest-v0.json)

## Package Scope

The v1 package includes:

- the PR114-PR144 base package by reference to the PR145 manifest;
- PR145 packaging-gate files;
- PR146-PR157 additions for local-private adequacy, the third builder case,
  human-review scaffolding, the automatic triage contract, the automatic triage
  packet builder, the provisional triage read, and the offline-v1 closure gate;
- PR158 package-gate files;
- discoverability docs touched by the offline-v1 sequence.

The package intentionally excludes unrelated notes, `plans/*`,
`reviews/synthetic/*`, archive paths, runtime temp state, `SKILL.md`, and
`scripts/skill/*`.

## Strongest Useful Signal

The strongest useful signal is that the offline system now forms a coherent
chain:

```text
completed artifacts
-> checked-in-safe brief
-> bounded interpretation read
-> deterministic enriched brief
-> automatic triage packet
-> provisional triage read
-> closure/package gate
```

Across three decision families, the system can make the action consequence
easier to inspect while preserving uncertainty, source limits, and non-claims.

## Strongest Unresolved Risk

The strongest unresolved risk is still source depth and calibration. The
checked-in artifacts are compressed, private context is not copied, the triage
read is Codex-assisted and provisional, and no real human reviewer has filled
the PR151 response template.

Cleaner offline output must not be treated as proof of good advice.

## Boundary

PR158 does not:

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
- include provider text;
- include local absolute paths;
- fill human-review answers;
- claim human validation;
- claim product proof;
- score answer quality;
- approve or certify advice;
- authorize agent or automatic action;
- implement runtime attachment.

## Validation Checklist

Before staging this package, run the focused checks for:

- PR158 package gate tests;
- PR157 closure gate tests;
- PR156 provisional triage read tests;
- PR155 automatic triage packet builder tests;
- PR154 automatic triage contract tests;
- Product Delta boundary lint;
- JSON parsing over the manifest and manifest-listed JSON artifacts;
- Markdown local-link checks over manifest-listed Markdown;
- trailing-whitespace and privacy-marker scans;
- `git diff --check`;
- `git status --short -- SKILL.md scripts/skill`.

## Recommended Next Step

Recommended next step:

```text
Stage and commit PR155-PR158 only after validation, then push/update the PR if
the maintainer wants the Offline v1 package on GitHub.
```

After packaging, the next product evidence step is still a real human response
to the PR151 template. Codex must not fill that response.
