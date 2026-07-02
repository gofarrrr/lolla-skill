# Decision Work Brief PR114-PR144 Packaging Gate v0

Status: PR145 offline evidence package gate.

Manifest:
[Decision Work Brief PR114-PR144 package manifest](decision-work-brief-pr114-pr144-package-manifest-v0.json)

## Why PR145 Exists

PR144 selected `package_pr114_pr144`. PR145 packages the offline Decision Work
Brief evidence surface so a maintainer can review, stage, or pause the work
deliberately.

The question is:

> Can a fresh reviewer understand exactly what PR114 through PR144 added, what
> is deterministic, what is provisional interpretation, what remains unproven,
> what files belong to the phase, and what must not be staged with it?

PR145 answers that with a versioned package manifest, an explicit staging list,
do-not-stage warnings, and tests for reference resolution, boundary metadata,
privacy hygiene, and lower-claim language.

## Package Scope

The package contains only the Decision Work Brief and Decision Work Conversation
Interpretation offline surface from PR114 through PR144:

- brief schema, packet builder, renderer, and rendered examples;
- conversation interpretation contract, packet builder, read schema, tiny
  reads, and comparison reviews;
- enrichment rules, deterministic enriched-brief builder, enriched examples,
  builder reviews, PR142 patch, PR143 review, and PR144 closure gate;
- focused tests, CLI wrappers, and code modules for those offline pieces.

It does not include unrelated notes, plans, synthetic reviews, archive paths,
runtime temp state, `SKILL.md`, or `scripts/skill/*`.

## Strongest Useful Signal

The strongest useful signal is the end-to-end offline chain:

completed-run artifacts can be represented as checked-in-safe source/status
packets, rendered into a readable Decision Work Brief, enriched with a small
set of already-created provisional interpretation fields, and checked by tests
that preserve source limits and non-claims.

The launch-beta and deploy-intake enriched examples show the intended user
value: the brief makes the action consequence easier to understand without
saying Lolla proved the advice better.

## Strongest Unresolved Risk

The strongest unresolved risk is source depth. Checked-in-safe artifacts are
compressed, raw/private conversation text is not checked in, and the
interpretation reads are Codex-assisted rather than human validated. Private
nuance could change starting-direction, lost-value, stakeholder, or user-intent
reads.

Packaging does not solve that risk. It makes the current risk easier to inspect.

## Boundary

PR145 is a package gate for an offline/downstream Decision Work Brief surface.
It is not runtime integration.

PR145 does not run `$lolla`, invoke the Lolla skill, call providers, mutate
archives, change prompts, touch `SKILL.md`, change runtime behavior, change
`scripts/skill/*`, create a new Lolla run, create a new interpretation read,
add a judge, score answer quality, create automatic labels, authorize agent
action, or claim product proof.

## Validation Policy

The manifest records a focused validation policy for:

- pytest over the Decision Work Brief and Decision Work Conversation
  Interpretation tests;
- `jq` parsing over all listed JSON/schema/review artifacts;
- Product Delta boundary lint over package docs, JSON, reviews, and examples;
- `git diff --check`;
- local Markdown link checks;
- trailing-whitespace scans;
- privacy/content marker scans;
- checks that `SKILL.md` and `scripts/skill/*` remain untouched.

## Suggested Stop Point

Stop after PR145 and decide whether to stage/package PR114-PR145 explicitly.

If maintainers continue later, the next PR should be chosen deliberately from
the packaged evidence: a third builder case, more local-private adequacy
checks, human review intake, or a future runtime-attachment plan. Runtime
integration should not be implemented from this package gate alone.
