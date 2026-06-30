# Decision Trail Specialist Path Decision v0

Status: PR94 docs-only decision gate
Date: 2026-06-29

## Decision

Selected outcome: **Outcome A: implement local-private Decision Trail packet
mode next**.

Recommended future slice:

```text
PR95 Decision Trail Local-Private Packet Mode v0
```

PR94 does not implement PR95. It decides the path after PR90 through PR93.
Completion note: PR95 is now implemented by
[`Decision Trail Local-Private Packet Mode v0`](decision-trail-local-private-packet-mode-v0.md),
the local-private packet-builder extension, and focused tests.
The implemented mode keeps PR88 fixture review as lineage-only in
local-private packets, derives raw-content inclusion flags from actual included
artifacts, requires repo-local fixture/schema inputs, and keeps all
local-private outputs unsafe for commit by default.

The decision is narrow:

> The specialist lane should not run a broader checked-in-safe specialist
> batch yet. The evidence says checked-in-safe packets are useful for custody
> and gap preservation, but too thin for the interpretation fields users care
> about. The next useful step is a local-private packet mode that can inspect
> local private artifacts without checking raw/private content into the repo.

## Evidence Considered

PR94 considers the landed Decision Trail sequence:

| Slice | Evidence | Read |
|---|---|---|
| [PR87 read-only exporter](decision-trail-readonly-exporter-v0.md) | Builds `lolla.decision_trail_report.v0` from structured artifacts only. | Useful custody and missingness shell; messy fields remain unfilled. |
| [PR88 fixture review](decision-trail-export-fixture-review-v0.md) | Reviews generated report behavior in safe-fixture mode. | Shell is readable and useful, but safe fixtures are too sparse for full product interpretation. |
| [PR89 interpretation-gap decision](decision-trail-interpretation-gap-decision-v0.md) | Chooses narrow offline specialist enrichment. | Correctly rejects deterministic interpretation, broad IR, runtime integration, judging, and graph/memory work. |
| [PR90 specialist contracts](decision-trail-specialist-contracts-v0.md) | Defines four typed specialist contracts. | Good boundary: roles are narrow and preserve source refs, uncertainty, and non-claims. |
| [PR91 packet builder](decision-trail-specialist-packet-builder-v0.md) | Builds checked-in-safe packets from PR88 review artifacts. | Packet scaffolding works, but it preserves `source_report_not_checked_in` and `safe_fixture_only` thinness. |
| [PR92 trap set](decision-trail-specialist-trap-set-v0.md) | Creates ten trap families. | Good discipline surface before specialist reads. |
| [PR93 dry run](decision-trail-specialist-dry-run-v0.md) | Dry-runs traps and packet surfaces without specialist outputs. | The setup mostly resists over-inference, but cannot prove real interpretation adequacy from checked-in-safe fixtures. |

## Contradicting Evidence First

There is a good argument for pausing now:

- PR93 still uses checked-in-safe fixture surfaces.
- No human review capacity is available.
- No local-private shadow review has been run.
- No contract-conforming specialist outputs exist yet.
- The current packet fixture has only two report targets.

Those are serious limits.

There is also a good argument for running a tiny specialist batch over the
current PR91 packets:

- The contracts exist.
- The packet builder exists.
- The trap surface exists.
- PR93 showed the setup can preserve gaps.

But that batch would mostly produce blocked/thin reads. It would prove that the
current safe packets are sparse, which PR88, PR91, and PR93 already showed.

So the next useful move is not "more checked-in-safe review." It is to create
the local-private packet mode needed for a meaningful offline specialist pass.

## What PR93 Proved

PR93 proved only discipline, not product value.

Useful PR93 signals:

- all ten PR92 trap families were inspected;
- seven traps met expected behavior;
- three traps partly met expected behavior;
- zero traps missed expected behavior;
- the dry run did not create contract-conforming specialist outputs;
- the dry run did not execute fan-in;
- the dry run preserved `safe_fixture_only`;
- the dry run preserved `source_report_not_checked_in`;
- the dry run preserved `local_private_shadow_review:not_run`;
- the dry run preserved eight interpretation-needed sections;
- the dry run preserved overtrust risk around `structural_delta`.

This is enough to keep going.

It is not enough to claim that Decision Trail understands messy conversations.

## What PR93 Did Not Prove

PR93 did not prove:

- future specialists will read real conversations correctly;
- checked-in-safe packets are enough for likely action or lost-value reads;
- the Decision Trail report is product-ready;
- Lolla improved any decision;
- the specialist method is calibrated;
- trap expectations are human labels;
- an agent may act.

The main bottleneck is now source access, not contract shape.

## Selected Outcome A: Local-Private Packet Mode

PR95 should implement a local-private packet mode for the Decision Trail
specialist packet builder.

PR95 now implements that mode explicitly. It keeps checked-in-safe mode as the
default, requires `--mode local_private_mode`, requires an explicit output path,
rejects local-private output inside the repo or selected run directory, records
a local read manifest, and marks local-private outputs unsafe for commit by
default. It still creates no specialist outputs and does not execute fan-in.

The mode should remain offline and explicit. It may inspect local private run
artifacts only when the operator asks for that mode.

It should produce local output only. Checked-in fixtures must remain
checked-in-safe and must not include raw/private content.

The goal is to create packets that future specialist reads can actually use,
while deterministic code still preserves custody:

- what was read;
- what was not read;
- whether raw/private content was included;
- which artifacts were available but redacted in checked-in mode;
- which source refs support each packet field;
- which fields remain unavailable;
- what must not be claimed.

## PR95 Must Do

PR95 should:

- extend `decision_trail_specialist_packets.py` to support
  `local_private_mode`;
- require explicit `--mode local_private_mode`;
- require explicit operator-chosen output path;
- refuse output inside the archive run directory;
- record `raw_private_content_included` truthfully;
- distinguish `checked_in_safe_mode` from `local_private_mode`;
- record a read manifest of local private artifacts inspected;
- preserve artifact status for raw conversation, revised answer, memo, and
  private/operator artifacts;
- keep checked-in fixtures raw/private-free;
- test local-private behavior only with synthetic temp run directories;
- keep generated local-private smoke output in `/tmp` or another non-repo path;
- document that local-private packets are not safe for commit by default.

## PR95 May Do

PR95 may include local-private packet fields such as:

- `private_context_policy`;
- `local_private_artifacts_read`;
- `local_private_artifacts_not_read`;
- `raw_private_content_included`;
- `content_inclusion_mode`;
- `source_text_refs`;
- `content_excerpt_policy`;
- `privacy_warning`;
- `commit_safety`;
- `requires_operator_review_before_share`.

If it includes text excerpts, they must be local-only outputs and never
checked-in fixtures.

## PR95 Must Not Do

PR95 must not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or models;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- create specialist outputs;
- execute fan-in;
- add a broad judge;
- score answer quality;
- create automatic labels;
- authorize agent action;
- add graph DB, memory, embeddings, chunking, or GraphRAG;
- check in raw transcripts, raw revised answers, raw memos, provider text,
  private ledgers, or local absolute paths;
- claim product proof;
- treat local-private access as human validation.

## Rejected Outcome B: Tiny Specialist Batch Over Current Packets

Rejected for now.

The current PR91 packets are intentionally thin. PR93 already showed the likely
result: mostly blocked checked-in-safe reads, private-needed status, and
gap-preserving fan-in.

A tiny batch over those packets would add artifacts but little new evidence. It
would also increase the risk that provisional blocked reads start to look like
semantic product evidence.

This option may become useful after PR95 creates local-private packets.

## Rejected Outcome C: Simplify Or Stop The Specialist Lane

Rejected for now.

The lane has not shown the failure pattern that would justify simplification:

- PR90 contracts are narrow;
- PR91 packets preserve thinness;
- PR92 traps target the right risks;
- PR93 resisted the trap surface without missed expected behavior;
- PR78 lint stayed clean.

The lane is not product proof, but it is still behaving like a useful
investigation scaffold.

## Rejected Outcome D: Pause Until Human Review

Rejected for now, with caveat.

Human review is still necessary before any product proof or calibrated eval
claim. But current human review capacity is unavailable, and there is a useful
offline engineering slice that can be completed without pretending to replace
humans: local-private packet mode.

Pause becomes the right choice after PR95 if local-private packets still cannot
produce enough usable context without unsafe content handling or excessive
complexity.

## Rejected Outcome E: Runtime Integration

Rejected.

The Decision Trail specialist lane is not ready for runtime integration. It is
still an offline evidence and interpretation scaffold. It must not alter the
Lolla skill, default audit run, prompts, archive behavior, or user-facing
runtime output.

## Rejected Outcome F: Broad Conversation Understanding IR

Rejected for now.

A durable `conversation_understanding_ir.v0` may become justified later, but
PR93 does not prove that broad IR is the next bottleneck. The immediate
bottleneck is that checked-in-safe packet surfaces lack enough source context
for likely action, option status, assistant influence, useful/noisy friction,
and lost value.

Local-private packet mode is a narrower way to test that bottleneck.

## What Would Falsify The Selected Path

Stop or simplify after PR95 if:

- local-private packets require copying too much raw/private content to be
  usable;
- local-private packet outputs are hard to keep out of commits;
- source refs become confusing or unsafe;
- likely action and lost-value fields still cannot be read without a broader
  conversation-understanding artifact;
- local-private packets make the report feel more authoritative without making
  interpretation more inspectable;
- tests cannot enforce privacy and commit-safety boundaries;
- the implementation starts to look like runtime integration by another name.

Current read after PR95: do not jump straight to specialist outputs. First run
a local-private packet smoke/review that checks usability, source-ref clarity,
privacy handling, overclaim risk, and whether the PR90 contracts need changes.

Completion note: PR96 has now run that smoke/review:

[`Decision Trail Local-Private Packet Smoke Review v0`](decision-trail-local-private-packet-smoke-review-v0.md)

The review found the packet path mechanically usable and recommended only a
tiny local-private specialist-output pilot next, not a broad batch.

## Recommended PR95 Validation

PR95 should validate:

- checked-in-safe behavior remains unchanged;
- local-private mode is explicit;
- local-private mode refuses unsafe output paths;
- local-private mode records truthful custody flags;
- local-private mode can read synthetic raw/private artifacts in temp fixtures;
- local-private output is generated outside the repo in tests/smoke;
- checked-in fixtures contain no raw/private content;
- PR78 lint remains clean over checked-in artifacts;
- privacy marker scans pass over checked-in files;
- `SKILL.md`, `scripts/skill/*`, and runtime files remain untouched.

## Non-Claims

PR94 does not claim:

- Lolla improves decisions;
- Decision Trail is product-ready;
- local-private mode will solve interpretation;
- Codex dry-run reads are calibrated;
- human validation exists;
- clean artifacts imply good advice;
- an agent may act.

## Final Read

PR90 through PR93 show that the specialist lane is disciplined enough to keep
investigating, but too thin in checked-in-safe mode to fill the decision-story
fields users care about.

The next question is:

> Can a local-private packet mode provide enough real conversation context for
> bounded offline specialists while deterministic custody keeps the output
> explicit, private, non-claiming, and hard to accidentally commit?
