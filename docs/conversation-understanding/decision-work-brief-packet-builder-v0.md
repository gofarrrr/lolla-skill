# Decision Work Brief Packet Builder v0

Status: PR115 read-only local packet builder
Date: 2026-07-01
Schema: `lolla.decision_work_brief_packets.v0`

## Purpose

PR115 implements the deterministic packet-preparation layer for the future
Decision Work Brief.

PR114 defined the user-facing brief contract:

```text
lolla.decision_work_brief.v0
```

PR115 does not fill that contract. It prepares source-aware input packets that
a later bounded LLM or human reviewer can use to fill the brief sections.

The packet builder answers a narrower question:

> Which completed-run artifacts, receipts, reports, and private/redacted source
> surfaces are available for a future Decision Work Brief interpretation pass?

It does not answer what the decision really meant, what action should be taken,
or whether the advice was good.

## Relationship To The Brief And Receipt

The layers are:

```text
Completed Lolla run artifacts
  -> Decision Work Receipt / Decision Trail / Product Delta refs
  -> Decision Work Brief packet
  -> future provisional or human interpretation
  -> future rendered Decision Work Brief
```

The Decision Work Brief is the future user-facing layer. The Evidence Receipt
and related reports are backing layers. The packet sits between them: it
collects bounded inputs and makes source availability, missingness, redaction,
private-local availability, custody flags, and non-claims explicit.

## What It Builds

The packet JSON uses:

```text
lolla.decision_work_brief_packets.v0
```

Top-level fields include:

- `schema_version`
- `packet_metadata`
- `mode`
- `source_run`
- `input_refs`
- `custody_flags`
- `packet_sections`
- `required_future_output`
- `non_claims`

The required future output points back to:

```text
docs/conversation-understanding/decision-work-brief-v0.json
lolla.decision_work_brief.v0
```

Each packet includes all eight target brief sections:

- `decision`
- `starting_direction`
- `what_lolla_pressed_on`
- `what_changed`
- `what_this_means_for_action`
- `what_still_might_be_wrong`
- `what_was_not_proven`
- `evidence_receipt`

Each packet section records:

- the future question a reviewer must answer;
- allowed source categories;
- available source refs;
- unavailable or redacted source refs;
- known limits;
- that interpretation is still required;
- the required output contract reference in the PR114 schema.

## Modes

### `metadata_only`

This is the default and the checked-in-safe mode.

It reads safe structured JSON metadata and records raw/private artifact
availability without copying raw text into the output. It may be used for
checked-in fixtures only if the output passes the normal privacy and boundary
scans.

In this mode:

- `checked_in_safe: true`
- `raw_private_content_included: false`
- `provider_text_included: false`
- `brief_generated: false`
- `semantic_interpretation_performed: false`
- `model_calls: 0`
- `archive_mutated: false`

### `local_private`

This mode is explicitly operator-selected.

Without `--include-private-text`, it still records metadata only, but the output
is treated as a local/private packet because it was built from an
operator-selected run directory.

With `--include-private-text`, the builder may copy capped local text excerpts
from private run artifacts into the packet. That output is unsafe for commit and
requires operator review before sharing.

In include-text local-private mode:

- `checked_in_safe: false`
- `unsafe_for_commit: true`
- `raw_private_content_included: true`
- source refs and truncation flags are preserved;
- local absolute paths are omitted;
- no brief is generated.

## Usage

Build a metadata-only packet:

```bash
python3 scripts/evals/build_decision_work_brief_packets.py \
  --run-dir <completed-run-dir> \
  --out /tmp/decision_work_brief_packets.json \
  --pretty
```

Link existing offline reports by metadata only:

```bash
python3 scripts/evals/build_decision_work_brief_packets.py \
  --run-dir <completed-run-dir> \
  --decision-work-receipt /tmp/decision_work_receipt.json \
  --decision-trail-report /tmp/decision_trail_report.json \
  --product-delta-report /tmp/product_delta_report.json \
  --out /tmp/decision_work_brief_packets.json \
  --pretty
```

Build a local-private include-text packet:

```bash
python3 scripts/evals/build_decision_work_brief_packets.py \
  --run-dir <completed-run-dir> \
  --mode local_private \
  --include-private-text \
  --max-text-chars 12000 \
  --out /tmp/decision_work_brief_packets_private.json \
  --pretty
```

The CLI rejects output paths inside the run directory. For local-private
include-text mode, it also rejects repo-local output paths.

## What It Reads

The builder prefers structured artifacts and metadata:

- `agent_result.json`
- `evaluation.json`
- `reasoning_trace.json`
- `extraction.json`
- `result.json`
- `memo_note.json`
- `graph_survival_report.json`
- optional Decision Work Receipt JSON supplied by path
- optional Decision Trail report JSON supplied by path
- optional Product Delta report JSON supplied by path

Raw/private artifacts such as `conversation.txt`, `revised.txt`, `memo.md`,
`live_transcript.txt`, `operator.log`, private tables, and private ledgers are
not copied in `metadata_only` mode. The packet may record that they exist, are
missing, are malformed, are redacted, or are available only locally.

External report paths are sanitized to artifact names. The packet records hash,
byte count, schema version when available, status, and source kind. It does not
copy report bodies or local absolute paths.

## What It Does Not Do

PR115 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call providers or models;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- generate a populated Decision Work Brief;
- fill semantic brief sections;
- infer likely action, live options, values, stakeholders, useful friction,
  noisy friction, lost value, or answer quality from prose;
- add a broad judge;
- add scoring;
- create automatic labels;
- authorize agent action;
- add graph DB, memory, embeddings, chunking, or GraphRAG;
- claim product proof.

## Non-Claims

Every packet carries explicit non-claims:

- `packet_is_not_a_brief`
- `packet_is_not_product_proof`
- `packet_does_not_score_answer_quality`
- `packet_does_not_authorize_agent_action`
- `packet_does_not_validate_decision_correctness`
- `missingness_is_not_negative_semantic_evidence`
- `clean_artifacts_do_not_imply_good_advice`
- `future_interpretation_required`

These are part of the contract. A clean packet means the packet stayed inside
the custody boundary. It does not mean the future brief will be useful or that
the underlying advice should be trusted.

## Validation Meaning

Validation can show:

- the packet schema version is stable;
- default mode is metadata-only;
- custody flags remain conservative;
- raw/private text is not copied into metadata-only output;
- external reports are linked by safe metadata only;
- optional missing reports become source status, not semantic findings;
- all eight brief section packets are present;
- output path guardrails work;
- local-private include-text output is marked unsafe for commit;
- PR116, PR117, and PR118 implementation files are absent.

Validation cannot show:

- the future interpretation will be correct;
- the future brief will be useful;
- a human validated the packet;
- clean artifacts imply good advice;
- an agent may act.

## Next Slice

The recommended next slice is:

```text
PR116 Codex-Assisted Brief Draft Pilot v0
```

PR116 may use PR115 packets as local input for a tiny provisional draft pilot.
It should still avoid runtime integration, archive mutation, provider/model
calls from repo code, product-proof claims, scoring, automatic labels, and
agent action authorization.
