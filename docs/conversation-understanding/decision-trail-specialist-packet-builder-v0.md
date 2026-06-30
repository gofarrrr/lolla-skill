# Decision Trail Specialist Packet Builder v0

Status: read-only deterministic packet builder
Date: 2026-06-29
Slice: PR91 Decision Trail Specialist Packet Builder v0

## Purpose

PR91 implements the deterministic packetization stage for future Decision Trail
specialist reads.

PR90 defined contracts for four narrow offline interpretation specialists:

- `conversation_shape_reader`
- `likely_action_reader`
- `friction_lost_value_reader`
- `conservative_fan_in_reader`

PR91 prepares input packets for those roles. It does not run the roles.

The packet builder turns the PR88 fixture-review surface into source-aware,
checked-in-safe input scaffolds. Those scaffolds say what a future specialist
may inspect, which contract it must satisfy, what is missing, and what must not
be claimed.

## Runtime Boundary

PR91 is offline and downstream from the Lolla runtime.

It does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or models;
- mutate archives;
- read raw transcripts;
- read raw revised answers;
- read raw memos;
- read provider text;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- change runtime behavior;
- fill specialist reads;
- execute fan-in;
- score answer quality;
- create automatic labels;
- authorize agent action;
- claim product proof.

## What It Reads

In `checked_in_safe_mode`, the builder reads:

- `reviews/codex-assisted/decision-trail-fixture-review-v0/review.json`
- `docs/conversation-understanding/decision-trail-specialist-contracts-v0.json`

The fixture review is the PR88 durable review record. PR88 did not check in the
generated Decision Trail report JSON; it checked in the review findings instead.

PR91 preserves that fact in every packet. It records `source_report_not_checked_in`
as a known limit rather than pretending the full generated report is present.

PR95 extends the same builder with explicit `local_private_mode`:

- [Decision Trail Local-Private Packet Mode v0](decision-trail-local-private-packet-mode-v0.md)

That mode may inspect operator-selected completed run directories and produce
local-only packet outputs. It is not safe for commit by default. In
local-private mode, the PR88 fixture-review input is retained as lineage only;
packet content comes from the selected run artifacts and the PR90 contract
schema. The CLI requires the fixture-review and contract-schema inputs to be
repo-local so local absolute paths do not leak into packet references.

Current standing after PR95: the builder can prepare checked-in-safe packets
and explicit local-private packets, but it still does not run specialists,
fill specialist output fields, execute fan-in, or decide whether a revised
answer improved a decision. PR96 has now smoke-reviewed the local-private
packet path and found it mechanically usable for source access, while still
not proving interpretation adequacy.

## What It Outputs

The generated JSON uses:

```text
lolla.decision_trail_specialist_packets.v0
```

Top-level fields include:

- `schema_version`
- `generated_by`
- `mode`
- `input_refs`
- `boundary`
- `packet_policy`
- `report_count`
- `reports`
- `non_claims`

Each report bundle includes:

- `report_id`
- `report_ref`
- `source_run_ref`
- `report_mode`
- `source_refs`
- `available_context`
- `missing_or_thin_context`
- `packets`

Each report bundle contains one packet for each PR90 specialist role.

Each packet records:

- specialist role;
- PR90 contract reference;
- input mode;
- allowed inputs;
- forbidden output categories;
- review questions;
- source refs;
- safe context;
- known limits;
- required non-claims;
- expected output contract.

The packet's `expected_output_contract` names the future output shape. It is
not a filled specialist read.

## Checked-In Fixture

The compact checked-in fixture is:

```text
reviews/codex-assisted/decision-trail-specialist-packets-v0/packets.json
```

It contains the two PR88 report-review targets:

- `structured_fixture_report`
- `sparse_missing_fixture_report`

The fixture is intentionally small because PR91 is about packet shape, not
evidence expansion.

## What Packets Are Not

Packets are not:

- specialist reviews;
- human validation;
- ground truth;
- judge calibration data;
- product proof;
- answer-quality measurement;
- automatic labels;
- agent permission;
- runtime integration.

PR91 may ask:

```text
Can a future specialist identify likely next actions from allowed inputs?
```

PR91 must not answer:

```text
The likely next action changed.
```

That answer belongs to a later bounded specialist-review slice, and even then
it remains non-human-validated until a human reviewer corrects or confirms it.

## How To Run

Build the checked-in fixture shape:

```bash
python3 scripts/evals/build_decision_trail_specialist_packets.py \
  --fixture-review reviews/codex-assisted/decision-trail-fixture-review-v0/review.json \
  --contract-schema docs/conversation-understanding/decision-trail-specialist-contracts-v0.json \
  --out reviews/codex-assisted/decision-trail-specialist-packets-v0/packets.json
```

Build a temporary sanity-check output:

```bash
python3 scripts/evals/build_decision_trail_specialist_packets.py \
  --fixture-review reviews/codex-assisted/decision-trail-fixture-review-v0/review.json \
  --contract-schema docs/conversation-understanding/decision-trail-specialist-contracts-v0.json \
  --out /tmp/decision_trail_specialist_packets_check.json
```

Filter to one report target:

```bash
python3 scripts/evals/build_decision_trail_specialist_packets.py \
  --fixture-review reviews/codex-assisted/decision-trail-fixture-review-v0/review.json \
  --contract-schema docs/conversation-understanding/decision-trail-specialist-contracts-v0.json \
  --report-id structured_fixture_report \
  --out /tmp/decision_trail_specialist_packets_structured.json
```

Build a metadata-only local-private packet:

```bash
python3 scripts/evals/build_decision_trail_specialist_packets.py \
  --fixture-review reviews/codex-assisted/decision-trail-fixture-review-v0/review.json \
  --contract-schema docs/conversation-understanding/decision-trail-specialist-contracts-v0.json \
  --mode local_private_mode \
  --local-run-dir <archive-run-dir> \
  --content-inclusion metadata_only \
  --out /tmp/decision_trail_local_private_packets.json
```

Build a local-private packet that includes private text:

```bash
python3 scripts/evals/build_decision_trail_specialist_packets.py \
  --fixture-review reviews/codex-assisted/decision-trail-fixture-review-v0/review.json \
  --contract-schema docs/conversation-understanding/decision-trail-specialist-contracts-v0.json \
  --mode local_private_mode \
  --local-run-dir <archive-run-dir> \
  --content-inclusion include_text \
  --out /tmp/decision_trail_local_private_packets_with_text.json
```

The CLI rejects local-private output inside the selected run directory and
inside the repository. Raw-content family booleans in local-private output are
derived from actual included artifacts, not merely from choosing
`include_text`.

## Validation Meaning

Validation can show:

- the CLI can deterministically construct packets from checked-in-safe inputs;
- every PR88 report target gets all four PR90 specialist packets;
- lower-claim metadata remains conservative;
- source refs and known limits are preserved;
- checked-in outputs avoid raw/private content;
- PR78 lint accepts the packet artifacts.

Validation cannot show:

- future specialist reads will be correct;
- Lolla improved a decision;
- a human validated the report;
- checked-in safe context is enough for product use;
- an agent may act.

## Relationship To PR92

PR92 implements the first checked-in-safe trap layer against these packets:

[`Decision Trail Specialist Trap Set v0`](decision-trail-specialist-trap-set-v0.md)

The trap set tests whether future specialist passes resist over-inference,
overtrust, lost-value blindness, and fan-in smoothing before any specialist
review batch is run.

## Relationship To PR93

PR93 runs a Codex-assisted provisional dry run over the PR92 traps and this
packet surface:

[`Decision Trail Specialist Dry Run v0`](decision-trail-specialist-dry-run-v0.md)

It preserves the packet surface as input scaffolding only. It does not create
contract-conforming specialist outputs or execute fan-in.

## Relationship To PR95

PR95 implements the local-private path selected by PR94:

[`Decision Trail Local-Private Packet Mode v0`](decision-trail-local-private-packet-mode-v0.md)

It keeps checked-in-safe mode as the default while allowing local-only packets
to carry private source context for a future specialist pass. PR95 does not
prove that the context is sufficient; that is what the next local-private
packet smoke/review needed to test.

## Relationship To PR96

PR96 reviews the local-private packet path:

[`Decision Trail Local-Private Packet Smoke Review v0`](decision-trail-local-private-packet-smoke-review-v0.md)

It confirms metadata-only packets work over two real completed runs, confirms
the include-text path mechanically with unsafe-for-commit marking, and still
does not create specialist outputs or execute fan-in.

## Next Step

The next recommended slice after PR96 was a tiny local-private
specialist-output pilot over one or two operator-selected completed runs. PR97
has now completed that one-case pilot:

[`Decision Trail Local-Private Specialist Output Pilot v0`](decision-trail-local-private-specialist-output-pilot-v0.md)

The pilot used PR95 local-private packet output and filled all four PR90
specialist roles by checked-in summary only. It still avoids runtime
integration, archive mutation, provider/API calls, scoring, automatic labels,
and product-proof claims.

The next recommended slice was PR98: review whether the PR97 output reveals
contract or packet-shape revisions before any broader specialist-output batch.
PR98 is now complete:

[`Decision Trail Specialist Output Pilot Review v0`](decision-trail-specialist-output-pilot-review-v0.md)

PR99 has now applied that patch:

[`Decision Trail Specialist Contract And Packet Patch v0`](decision-trail-specialist-contract-and-packet-patch-v0.md)

The packet builder now exposes role-readable source-scope metadata, truncation
impact metadata, local-private retention policy metadata, and per-role
`pr99_patch_fields` while preserving the existing output-path guards and
non-claim boundary.

PR100 has now used those patched packets on a second one-case pilot:

[`Decision Trail Second One-Case Specialist Pilot v0`](decision-trail-second-one-case-specialist-pilot-v0.md)

PR101 has now compared PR97 and PR100:

[`Decision Trail Specialist Pilot Comparison Gate v0`](decision-trail-specialist-pilot-comparison-gate-v0.md)

It decides broad specialist-output batches are not ready and allows at most one
diversity-targeted third one-case pilot before stopping or simplifying.
