# Decision Trail Specialist Output Pilot Review v0

Status: review and contract-revision gate
Date: 2026-06-30
Slice: PR98 Decision Trail Specialist Output Pilot Review / Contract Revision v0

## Purpose

PR98 reviews the PR97 local-private specialist-output pilot before any broader
specialist batch.

It asks:

> Did the one-case pilot expose enough value to continue, and what must change
> before the next specialist-output run?

The answer is: continue, but patch the contracts and packet shape first. PR97
showed the specialist lane can make the Decision Trail more concrete, but it
also showed that the current contracts are too permissive around vanilla
overlap, lost-value severity, assistant-influence source status, truncation
impact, and fan-in downgrade rules.

## Inputs Reviewed

PR98 reviews only checked-in PR97 summaries:

- [Decision Trail Local-Private Specialist Output Pilot v0](decision-trail-local-private-specialist-output-pilot-v0.md)
- [`review.json`](../../reviews/codex-assisted/decision-trail-local-private-specialist-output-pilot-v0/review.json)

PR98 does not read or retain the local-private include-text packet. The PR97
private packet was a temporary local source surface and is not checked in.

## Boundary

PR98 is offline and downstream from the Lolla runtime.

It does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or external model APIs;
- mutate archives;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- change runtime behavior;
- fill a new specialist batch;
- execute fan-in as a verdict;
- measure answer quality;
- create automatic labels;
- authorize agent action;
- claim product proof.

## Review Verdict

PR97 is useful enough to keep the specialist lane alive, but not stable enough
to broaden.

Decision:

```text
Do not run a broad specialist-output batch yet.
Patch the specialist contracts and packet metadata first.
Then run at most a second one-case pilot.
```

## What PR97 Made Easier To See

PR97 made four things more legible than the sparse Decision Trail shell:

- the conversation shape: authority transfer versus continued reset testing;
- the likely-action delta: move authority first, narrow transition role, add
  stop conditions;
- the lost-value tension: clarity may cost relationship simplicity, trust, or
  momentum;
- the fan-in tension: the structural delta looks strong, but assistant
  influence, vanilla overlap, and stakeholder/value risks remain unresolved.

That is the useful signal. Local-private source access can make the Decision
Trail more decision-shaped.

## What PR97 Exposed As Weak

PR97 also exposed five gaps that should be patched before more cases:

1. The likely-action reader needs a first-class vanilla-overlap field.
   Otherwise the system may credit Lolla for an action sequence the vanilla
   answer already contained.
2. The friction/lost-value reader needs to separate lost-value presence from
   lost-value severity. Otherwise every visible cost looks similarly important.
3. The conversation-shape reader needs clearer assistant-influence source
   status. Otherwise "partly visible" can harden into implied influence.
4. Every role needs truncation/source-scope impact. Otherwise missing context
   can be mistaken for absent context.
5. Conservative fan-in needs downgrade triggers. Otherwise fan-in can sound
   confident even when key fields remain unresolved.

## Contract Revision Queue

PR98 recommended a small PR99 contract and packet patch before any second pilot:

- add `vanilla_overlap_read` to the likely-action reader;
- add `lost_value_severity_read` to the friction/lost-value reader;
- add `assistant_influence_source_status` to the conversation-shape reader;
- add `source_scope_and_truncation_impact` to every specialist output;
- add `downgrade_triggers` and `not_ready_reason` to conservative fan-in;
- add explicit local-private packet retention/deletion status to the checked-in
  review summary.

PR99 has now applied this patch additively while keeping the schema family
stable:

- [Decision Trail Specialist Contract And Packet Patch v0](decision-trail-specialist-contract-and-packet-patch-v0.md)

## Packet Revision Queue

The packet path should also get tighter before broader use:

- include a per-run truncation summary that future specialists must cite;
- expose a short source-scope summary per role without copying raw text into
  checked-in artifacts;
- preserve whether each artifact was absent, present-not-read, read-metadata,
  read-text-truncated, or read-text-complete;
- require checked-in pilot summaries to state whether local include-text output
  was deleted, retained locally, or never created;
- keep output-path guards unchanged.

## Next Slice

PR99 is now complete:

```text
Decision Trail Specialist Contract And Packet Patch v0
```

It patched contracts, packet metadata, tests, and docs only. It did not run
another specialist pilot.

After PR99, the conservative path is a second one-case pilot, not a broad
batch. That future slice would be PR100.

## Non-Claims

PR98 is not:

- human review;
- ground truth;
- judge calibration data;
- product proof;
- answer-quality measurement;
- automatic labeling;
- runtime integration;
- evidence that clean specialist outputs mean good advice;
- agent action authorization.
