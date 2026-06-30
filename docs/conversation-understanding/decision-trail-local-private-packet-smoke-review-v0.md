# Decision Trail Local-Private Packet Smoke Review v0

Status: local smoke/review gate
Date: 2026-06-30
Slice: PR96 Decision Trail Local-Private Packet Smoke Review v0

## Purpose

PR96 reviews whether PR95's `local_private_mode` packet builder is usable
enough to justify a later bounded specialist-output pilot.

PR96 is not that pilot. It does not fill likely actions, live options,
stakeholders, values/priorities, assistant influence, useful/noisy friction,
lost value, or fan-in. It checks whether the packet surface can safely prepare
source context for those future reads.

## Runtime Boundary

PR96 is offline and downstream from the Lolla runtime.

It does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or models;
- mutate archives;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- change runtime behavior;
- create specialist outputs;
- execute fan-in;
- score answer quality;
- create automatic labels;
- authorize agent action;
- claim product proof.

## Smoke Runs

PR96 used the PR95 CLI to generate local outputs under a temporary directory.
Those outputs are not checked in.

### Real Metadata-Only Smoke

The metadata-only smoke used two existing completed local run directories:

- `ceo-remove-founding-cofounder/20260627T093131Z_59d153`
- `accept-founding-engineer-role/20260627T073034Z_a7c221`

The generated packet output reported:

- schema version: `lolla.decision_trail_specialist_packets.v0`;
- mode: `local_private_mode`;
- report count: 2;
- four packet roles per run;
- 16 local artifact records per run;
- `raw_private_content_included: false`;
- `content_inclusion_mode: metadata_only`;
- `specialist_reads_filled: false`;
- `fan_in_executed: false`;
- `runtime_invoked: false`;
- `skill_invoked: false`;
- `model_calls: 0`;
- `archive_mutated: false`.

This is a useful signal: local-private metadata mode can see the real artifact
surface without copying raw/private content into the packet.

It is also limited: metadata-only mode proves source availability, not
interpretation adequacy.

### Real Include-Text Smoke

One real completed run was also used for a local-only `include_text` smoke with
a small per-artifact cap:

- `ceo-remove-founding-cofounder/20260627T093131Z_59d153`

The private output was generated locally, summarized structurally, and then
deleted. The checked-in review does not include raw conversation, memo, revised
answer, private ledger, provider text, or local absolute paths.

The structural summary showed:

- report count: 1;
- artifact records read: 16;
- artifact records with included content: 16;
- truncated artifact records: 16;
- four packet roles present;
- `raw_private_content_included: true`;
- `raw_transcripts_included: true`;
- `raw_revised_answers_included: true`;
- `raw_memos_included: true`;
- `commit_safety: unsafe_for_commit_by_default`;
- `requires_operator_review_before_share: true`;
- `specialist_reads_filled: false`;
- `fan_in_executed: false`.

This confirms the real private path works mechanically and marks itself as
unsafe. It does not prove that the copied text is sufficient for good
specialist interpretation.

### Synthetic Include-Text Smoke

PR96 also generated a synthetic local-private include-text packet under the
temporary smoke directory. This synthetic output is safe test material and
confirms the include-text booleans and guardrails without exposing real private
content.

## Guardrail Checks

PR96 checked that local-private output is rejected when written:

- inside the repository;
- inside the selected local run directory.

Both rejected with sanitized errors.

## Review Read

What PR96 made easier to see:

- Real completed runs have the artifact families future specialists need to
  inspect.
- Metadata-only packets are useful for source availability, custody, and
  planning.
- Include-text packets can carry private source context locally and mark the
  output unsafe for commit.
- The packet builder preserves the correct boundary: packets are input
  scaffolds only.

What PR96 did not prove:

- that future specialists will interpret the conversation correctly;
- that include-text packets are safe to share;
- that a specialist-output batch should be broad;
- that Lolla improved either decision;
- that human review happened;
- that an agent may act.

## Main Product Read

The packet lane was ready for one tiny local-private specialist-output pilot,
not a broad batch. PR97 has now run that pilot:

- [Decision Trail Local-Private Specialist Output Pilot v0](decision-trail-local-private-specialist-output-pilot-v0.md)

PR97 used one operator-selected completed run and produced bounded,
non-human-validated specialist outputs from a local-private include-text packet.
The checked-in review preserves only summary-level output, uncertainty, source
refs, limitations, and non-claims. It did not check in private packet content.

## Recommended Next Slice

PR98 has now reviewed the PR97 pilot:

- [Decision Trail Specialist Output Pilot Review v0](decision-trail-specialist-output-pilot-review-v0.md)

PR99 has now applied the requested patch:

```text
Decision Trail Specialist Contract And Packet Patch v0
```

See:

- [Decision Trail Specialist Contract And Packet Patch v0](decision-trail-specialist-contract-and-packet-patch-v0.md)

It patches the PR90 contracts and PR95 packet metadata surfaced by PR98,
preserves the one-case limitation as a first-class result, and avoids broad
product claims, fan-in-as-verdict, runtime integration, and another
specialist-output pilot.

PR100 has now used the patched shape on one more operator-selected one-case
pilot:

- [Decision Trail Second One-Case Specialist Pilot v0](decision-trail-second-one-case-specialist-pilot-v0.md)

PR101 has now compared PR97 and PR100:

- [Decision Trail Specialist Pilot Comparison Gate v0](decision-trail-specialist-pilot-comparison-gate-v0.md)

It decided broad specialist-output batches were not ready and allowed at most
one diversity-targeted third one-case pilot. PR102 has now used that one
diversity pilot:

- [Decision Trail Third One-Case Diversity Pilot v0](decision-trail-third-one-case-diversity-pilot-v0.md)

Any future closure or intake slice must not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider APIs outside the current agent session;
- mutate archives;
- change runtime behavior;
- add scoring, judging, automatic labels, or agent authorization;
- treat clean packets as proof of good advice.

## Files

The durable checked-in review artifact is:

- [`review.json`](../../reviews/codex-assisted/decision-trail-local-private-packet-smoke-review-v0/review.json)

The temporary smoke outputs were intentionally not checked in.
