# Decision Work Offline Interpretation Queue Builder v0

Status: PR180 deterministic queue packet builder
Date: 2026-07-03
Output schema: `lolla.decision_work_offline_interpretation_queue_item.v0`

## Purpose

PR180 implements the deterministic packet/preparation layer for the
[Decision Work Offline Interpretation Queue Contract](decision-work-offline-interpretation-queue-contract-v0.md).

The builder prepares a checked-in-safe queue item for a completed run and an
optional PR130-compatible source packet. It records refs, status, missingness,
requested fields, privacy policy, validation requirements, downstream expected
outputs, custody flags, and non-claims.

It does not fill semantic interpretation fields. It does not call a model,
invoke the Lolla skill, create a new Lolla run, mutate archives, update the
runtime hook, generate a Decision Work Brief, generate enrichment, create a
triage read, score advice, or authorize action.

## CLI

```bash
python3 scripts/evals/build_decision_work_offline_interpretation_queue.py \
  --run-dir <completed-run-dir> \
  --contract docs/conversation-understanding/decision-work-offline-interpretation-queue-contract-v0.json \
  --source-packet <optional-pr130-packet-json> \
  --out /tmp/decision_work_offline_interpretation_queue_item.json \
  --pretty
```

Supported modes:

- `checked_in_safe_metadata_only`, the default;
- `local_private_operator`, metadata/status only;
- `disabled`.

## Output

The builder emits:

- `schema_version`;
- `queue_metadata`;
- `queue_mode`;
- `source_run_ref`;
- `source_packet_ref`;
- `allowed_source_refs`;
- `requested_interpretation_fields`;
- `privacy_mode`;
- `custody_flags`;
- `queue_status`;
- `blocked_or_deferred_reasons`;
- `output_destinations`;
- `validation_requirements`;
- `downstream_refs`;
- `known_limits`;
- `semantic_fields_filled: false`;
- `non_claims`.

## Status Logic

The default `checked_in_safe_metadata_only` mode emits:

- `queued` when the supplied source packet exists, parses, uses
  `lolla.decision_work_conversation_interpretation_packets.v0`, and contains no
  unsafe markers;
- `blocked_missing_packet` when no source packet is supplied or the completed
  run ref is unavailable;
- `blocked_schema_invalid` when the packet is malformed or uses an unsupported
  schema;
- `blocked_privacy_risk` when the supplied packet contains privacy, secret, or
  local-path markers.

`local_private_operator` emits `requires_local_private_operator`. It records
that private context may be needed outside checked-in artifacts, but it still
does not export private content.

`disabled` emits `not_requested`.

## Safety Policy

Checked-in-safe output may include sanitized refs, basenames, relative repo refs,
statuses, missingness, and non-claims. It must not include raw conversation
text, raw revised answers, raw memo text, provider text, private ledgers,
secrets, or local absolute paths.

The builder refuses to write output inside the input run directory. That keeps
PR180 from mutating the completed archive.

## Relationship To Interpretation

The queue item is not interpretation. It is the queueable envelope for a later
bounded operator/Codex interpretation step. Every requested field remains
`semantic_field_filled: false` with `interpretation_status:
requested_not_filled`.

Future work may use the queue item to create an operator/Codex prompt packet and
then validate a generated interpretation read against the PR133 schema. PR180
stops before both steps.

## Decision Gate

Selected next step:

```text
proceed_to_operator_codex_prompt_packet
```

Recommended next PR:

```text
PR181 Operator/Codex Interpretation Prompt Packet v0
```

Reason:

The builder can now prepare a safe, non-interpretive queue item. The next safe
slice is a prompt/input packet contract for an operator or Codex session to fill
a bounded interpretation read later, without introducing repo-side provider
calls or generated-read intake.

PR181 is tracked in
[Decision Work Operator/Codex Interpretation Prompt Packet](decision-work-operator-codex-interpretation-prompt-packet-v0.md).
