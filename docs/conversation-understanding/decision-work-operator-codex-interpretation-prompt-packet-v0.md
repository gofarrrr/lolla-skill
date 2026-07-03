# Decision Work Operator/Codex Interpretation Prompt Packet v0

Status: PR181 prompt/input packet contract
Date: 2026-07-03
Schema: `lolla.decision_work_operator_codex_interpretation_prompt_packet.v0`

## Purpose

PR181 defines the bounded prompt/input packet that a future operator or Codex
session can use to fill a PR133 Decision Work conversation interpretation read
from an offline queue item.

This is not a generated interpretation read. It is not generated-read intake. It
does not call providers from repo code, run Lolla, invoke the Lolla skill,
create a new Lolla run, mutate archives, change runtime behavior, update
sidecars, score advice, validate product value, or authorize action.

## Source And Target

Source queue item:

```text
lolla.decision_work_offline_interpretation_queue_item.v0
```

Target output schema:

```text
lolla.decision_work_conversation_interpretation_read.v0
```

The target schema is described in
[Decision Work Conversation Interpretation Read Schema](decision-work-conversation-interpretation-read-schema-v0.md).

The machine-readable PR181 prompt packet contract is:

- [Decision Work Operator/Codex Interpretation Prompt Packet JSON](decision-work-operator-codex-interpretation-prompt-packet-v0.json)

## What The Future Operator/Codex Session May Do

A later operator or Codex session may use this packet to produce a separate
candidate interpretation read. That future read must preserve source refs,
uncertainty, missingness, privacy limits, and non-claims.

The future session may fill only the bounded fields requested by the queue
contract:

- `decision_question`;
- `likely_starting_direction`;
- `revised_direction_or_action_consequence`;
- `decision_thresholds`;
- `evidence_gates`;
- `useful_friction`;
- `what_the_final_answer_does_not_prove`.

Every filled field must keep source refs and uncertainty. Missing context must
stay visible.

## What The Packet Refuses

The packet refuses:

- direct runtime interpretation;
- repo-side provider/model calls;
- generated read creation in PR181;
- generated-read intake in PR181;
- raw/private conversation export;
- raw revised-answer export;
- raw memo export;
- provider text export;
- private ledger export;
- local absolute path export;
- answer-quality scoring;
- approval labels;
- advice-correctness claims;
- product-proof claims;
- human-validation claims;
- agent or automatic action authorization.

## Example Refs

The packet points to the three checked-in-safe examples as references only:

- `launch-public-enterprise-beta`;
- `deploy-assisted-intake-routing`;
- `ceo-remove-founding-cofounder`.

The cofounder case remains relationship, governance, and legal sensitive. A
future interpretation read must keep that caveat visible and must not turn the
read into operational approval.

## Validation Checklist

Before a future generated interpretation read can feed the rest of automatic
semantic supply, a later intake validator must confirm:

- source queue item schema is valid;
- source queue item status is queueable;
- allowed source refs are preserved;
- requested fields are present;
- source refs and uncertainty are present;
- missingness is visible;
- privacy rules are preserved;
- forbidden claims are absent;
- answer-quality scoring is absent;
- action authorization is absent;
- product-proof and human-validation claims are absent.

## Decision Gate

Selected next step:

```text
proceed_to_generated_read_intake_validator
```

Recommended next PR:

```text
PR182 Generated Interpretation Read Intake And Validator v0
```

Reason:

The queue item and prompt packet are now defined. The next safe slice is an
intake/validator for a separately produced candidate interpretation read. That
future PR should validate schema, source refs, uncertainty, privacy, and
non-claims before any brief rendering, enrichment, triage, resolver approval, or
runtime sidecar update.
