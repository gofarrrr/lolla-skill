# Decision Trail Specialist Contract And Packet Patch v0

Status: contract and packet metadata patch
Date: 2026-06-30
Slice: PR99 Decision Trail Specialist Contract And Packet Patch v0

## Purpose

PR99 applies the patch required by PR98 before any second specialist-output
pilot.

PR98 found that PR97's one-case local-private specialist-output pilot was
useful enough to continue, but too loose to broaden. The weak points were
vanilla overlap, lost-value severity, assistant-influence source status,
source-scope and truncation impact, fan-in downgrade triggers, and
local-private retention/deletion status.

PR99 patches those surfaces without running another specialist pass.

## What Changed

PR99 keeps the schema family stable:

```text
lolla.decision_trail_specialist_contracts.v0
lolla.decision_trail_specialist_packets.v0
```

The patch is additive and conservative.

### Contract Fields

The PR90 contract catalog now expects these additional fields:

- `assistant_influence_source_status` for `conversation_shape_reader`;
- `vanilla_overlap_read` for `likely_action_reader`;
- `lost_value_severity_read` and `severity_source_status` for
  `friction_lost_value_reader`;
- `downgrade_triggers` and `not_ready_reason` for
  `conservative_fan_in_reader`;
- `source_scope_and_truncation_impact` for every specialist role.

These are not semantic findings. They are required future output slots so a
specialist must explicitly say what it knows, what it does not know, and what
source-scope limits affect the read.

### Packet Metadata

The packet builder now adds deterministic custody metadata for future
specialists:

- `source_scope_summary`;
- `truncation_summary`;
- `local_private_retention_policy`;
- per-role `pr99_patch_fields` in `expected_output_contract`.

For local-private packets, the source-scope summary distinguishes:

- `absent`;
- `malformed`;
- `present_not_read`;
- `read_metadata`;
- `read_text_truncated`;
- `read_text_complete`.

The truncation summary records the maximum text cap, count of truncated
artifacts, truncated artifact refs, and whether specialists must cite
truncation impact.

The retention policy makes one thing explicit: the packet builder does not
delete local-private output. Future checked-in pilot reviews must state whether
include-text output was deleted after review, retained locally, or never
created.

## Runtime Boundary

PR99 is offline and downstream from the Lolla runtime.

It does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or external model APIs;
- mutate archives;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- change runtime behavior;
- run another specialist pilot;
- execute fan-in as a verdict;
- measure answer quality;
- create automatic labels;
- authorize agent action;
- claim product proof.

## Validation Meaning

Validation can show:

- future specialist packets name the PR99-required output fields;
- packet contexts expose source-scope and truncation metadata;
- local-private packet retention status is explicitly review-owned;
- checked-in-safe packets remain private-content-free;
- boundary lint still accepts the artifacts.

Validation cannot show:

- future specialists will interpret conversations correctly;
- Lolla improved a decision;
- the PR97 pilot was semantically right;
- a second pilot will be useful;
- human validation happened;
- an agent may act.

## Next Slice

PR100 has now used the patched shape on one additional case:

```text
PR100 Decision Trail Second One-Case Specialist Pilot v0
```

See:

- [Decision Trail Second One-Case Specialist Pilot v0](decision-trail-second-one-case-specialist-pilot-v0.md)

That pilot used the patched contracts and packet metadata on one
operator-selected completed run only. It did not broaden the batch.

The PR100 result is useful but conservative: the patched fields made material
vanilla overlap visible and downgraded the net read to partial usefulness.

The next conservative slice should be:

```text
PR101 Decision Trail Specialist Pilot Comparison Gate v0
```

PR101 should compare PR97 and PR100 before deciding whether to run a third
one-case pilot, pause, simplify, or prepare any small multi-case review.
