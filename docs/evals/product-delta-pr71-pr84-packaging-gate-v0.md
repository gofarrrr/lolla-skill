# Product Delta PR71-PR84 Packaging Gate v0

Status: packaging/closure gate

Slice: PR85 Product Delta PR71-PR84 Packaging Gate v0

Manifest:
[Product Delta PR71-PR84 package manifest](product-delta-pr71-pr84-package-manifest-v0.json)

## Why PR85 Exists

PR85 closes the current Product Delta Evidence phase as a packageable working
tree surface. It is not an evidence-expansion PR and not a new review method.

The question is:

> Can a fresh reviewer understand exactly what PR71-PR84 added, what is
> provisional, what is not proof, what files belong to this phase, and what
> validation shows the package is internally coherent?

PR85 answers that by creating a versioned package manifest, documenting the
phase architecture, and adding tests that check source references, boundary
metadata, PR78 lint coverage, non-claims, and thinness limits across the
Product Delta lane.

## Boundary

PR85 is a packaging gate for the Product Delta eval lane. It is not runtime
integration.

The runtime/eval split remains:

- Lolla runtime captures conversations, runs provider-backed audit lanes,
  produces revised answers, and persists custody artifacts.
- Product Delta eval reads existing safe artifacts later, packetizes cases,
  supports provisional specialist review outside runtime, validates schemas
  and non-claims, preserves uncertainty and disagreement, and prepares later
  human validation.

PR85 does not run `$lolla`, invoke the Lolla skill, call providers, mutate
archives, change prompts, touch `SKILL.md`, change runtime behavior, change
`scripts/skill/*`, create runtime temp state, launch Observatory, persist
revised answers, add an LLM judge, add answer-quality scoring, create
automatic labels, or authorize agent action.

## What PR71-PR84 Added

PR71 through PR84 form one lower-claim Product Delta Evidence phase:

1. **PR71 thesis/protocol framing**
   Product Delta Evidence is framed as a downstream eval question, not product
   proof. It asks whether revised answers change likely decisions in
   decision-useful ways, while keeping Codex-assisted review provisional.

2. **PR72 provisional review protocol**
   The vanilla-vs-Lolla protocol defines the case-review shape: likely next
   actions, material difference, structural delta, decision leverage, friction,
   lost value, interpretation adequacy, uncertainty, and non-claims.

3. **PR73 paired-review dry run**
   A small safe-context dry run checks whether the PR72 shape can carry
   provisional reads and human follow-up questions without becoming human
   validation.

4. **PR74 failure taxonomy**
   The provisional taxonomy names product-delta, interpretation, and
   review-process failure families without converting them into automatic
   labels.

5. **PR75 readiness**
   A read-only analyzer checks 14 existing cases for Product Delta
   reviewability and emits PR72-shaped shells. Twelve cases are ready for
   Codex-assisted provisional review, one is partial/private-content-only, and
   one is blocked by degraded-run status.

6. **PR76 broad Codex batch**
   Codex-assisted provisional review fills the 12 ready shells. This is the
   broad semantic fill that later specialist work compares against; it is not
   human review, judge calibration, or product proof.

7. **PR77 provisional report**
   The state-of-evidence report summarizes PR75 and PR76, including candidate
   distribution, lost-value risks, interpretation concerns, and the absence of
   noise/worse candidates.

8. **PR78 boundary lint**
   Deterministic local lint checks Product Delta docs/JSON/review artifacts
   for lower-claim metadata, forbidden authority fields, privacy/content
   markers, and targeted overclaim drift. It is boundary hygiene, not semantic
   validation.

9. **PR79 architecture**
   The specialist-review architecture rejects a broad LLM judge and instead
   decomposes Product Delta review into bounded specialist reads plus
   disagreement-preserving fan-in.

10. **PR80 contracts**
    Typed contracts define eight specialist reads with source status, source
    refs, uncertainty, what-would-make-this-wrong material, and non-claims.

11. **PR81 packets**
    A read-only packet builder creates checked-in-safe per-specialist input
    packets for two fixture cases. Packets are not specialist answers.

12. **PR82 traps**
    Ten checked-in-safe trap families test whether future specialist review
    resists thin context, length bias, caution theater, repeated vanilla gates,
    lost live options, ambition burial, assistant-influence blindness,
    disagreement smoothing, clean-artifact authority leakage, and hardened
    provisional language.

13. **PR83 specialist batch**
    The first Codex-assisted specialist batch runs trap discipline and fills
    all eight PR80 specialist reads for the two PR81 packet-fixture cases.

14. **PR84 fan-in/disagreement report**
    A static report compares existing PR76 broad reads with existing PR83
    specialist fan-in reads. PR84 creates no new specialist reads.

## Strongest Useful Signal

The strongest useful signal from PR71-PR84 is not a bigger positive result. It
is the preserved downgrade:

`accept-operations-role-startup`

`material_improvement_candidate -> partial_improvement_candidate`

PR76 read this case as a material improvement candidate. PR83 decomposed the
case into specialist reads and downgraded the net candidate to partial because
lost value, value-overwrite risk, user-specific ambition, and written-gate
proportion remained unresolved. PR84 then preserved that downgrade as the main
fan-in/disagreement report finding.

That is useful because it shows the review harness can make the evidence less
impressive when uncertainty and lost value demand it.

## Strongest Unresolved Risk

The strongest unresolved risk is thinness:

- PR83/PR84 compare only two real cases;
- both cases came from PR81's compact packet fixture;
- both had prior positive PR76 context;
- no real-case no-change, added-noise, worse, or inconclusive outcome appears
  in PR83/PR84;
- no human validation is available;
- checked-in safe mode uses compressed context;
- no raw transcript, raw revised answer, raw memo, or private archive content
  was read;
- PR33 is used only as historical review-safe context, not fresh validation.

This is enough to package the scaffold. It is not enough to characterize
product behavior.

## Source Reference Gate

PR85 records and tests the source-reference policy:

- PR84 references to PR76 and PR83 artifacts should resolve.
- PR83 references to PR81 packets, PR76 broad reads, and PR33 historical
  review context should resolve where they name checked-in files.
- PR81 packet references to PR75 shells, PR76 broad reads, seed cases, and
  PR80 schemas should resolve.
- PR75 and PR76 source artifact paths should resolve where present.

Archive-relative identifiers remain case identity only. They are not permission
to read local private archive content.

## Validation Coverage

The PR85 package gate records a validation policy for:

- focused pytest over the Product Delta tests from PR75 through PR85;
- `jq` parsing over the manifest and all package JSON artifacts;
- PR78 lint over Product Delta docs/JSON/review artifacts;
- `git diff --check`;
- local Markdown link checks;
- trailing-whitespace scans;
- privacy/content marker scans;
- source-reference path and JSON-pointer resolution.

The new PR85 tests verify the manifest schema, conservative boundary metadata,
PR71-PR84 coverage, included-file existence, unrelated-file exclusion, key
downgrade preservation, thinness limits, PR84 static-report constraints, PR83
shape references, PR78 lint, privacy hygiene, and source-reference resolution.

## What A Clean Gate Means

A clean PR85 gate means:

- the package manifest names the Product Delta PR71-PR84 surface coherently;
- required phase files exist;
- key PR83 and PR84 source refs still resolve;
- lower-claim boundary metadata remains conservative;
- PR78 lint finds no boundary drift over the checked Product Delta surface;
- a fresh reviewer can see the useful signal and the unresolved risk quickly.

## What PR85 Does Not Mean

PR85 does not prove:

- Lolla improves decisions;
- Codex-assisted reads are human labels;
- specialist decomposition is calibrated;
- PR83 or PR84 is product proof;
- clean artifacts imply good advice;
- agents may act on outputs;
- PR76 or PR83 is right;
- the eval lane is part of runtime.

PR85 packages the scaffold. It does not make the scaffold stronger than the
evidence inside it.

## Recommended Stop Point

Stop and decide whether to stage/package PR71-PR85 explicitly, or pause until
human review capacity returns.

If maintainers continue later, the next phase should be chosen deliberately:
human-review intake, local-private packet mode for interpretation adequacy,
expanded traps, or a larger specialist batch only after deciding how to handle
positive-selection risk.
