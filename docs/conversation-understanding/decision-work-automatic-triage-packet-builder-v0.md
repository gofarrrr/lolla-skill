# Decision Work Automatic Triage Packet Builder v0

Status: PR155 automatic triage packet builder

Date: 2026-07-02

Schema: `lolla.decision_work_automatic_triage_packets.v0`

## Purpose

PR155 adds a deterministic offline packet builder for future Decision Work
automatic triage.

The builder prepares checked-in-safe evidence packets from existing Decision
Work Brief, interpretation-read, review, human-calibration, and PR154 triage
contract artifacts. It gathers references, custody flags, missingness, field
group policy, known limits, and future triage tasks. It does not decide any
triage category or route.

The packet is input preparation only. A later provisional read may use it to
route attention to source-depth, overtrust, private-context, domain/legal,
agent-inspection, and runtime-blocker concerns.

## Inputs

The CLI accepts the PR154 contract and an explicit output path:

```bash
python3 scripts/evals/build_decision_work_automatic_triage_packets.py \
  --triage-contract docs/conversation-understanding/decision-work-automatic-triage-contract-v0.json \
  --out /tmp/decision_work_automatic_triage_packets.json \
  --pretty
```

The default packet scope is exactly the three builder-enriched Decision Work
Brief cases already present in the offline evidence package:

- `launch-public-enterprise-beta`
- `deploy-assisted-intake-routing`
- `ceo-remove-founding-cofounder`

For each case, the packet carries checked-in-safe refs to:

- builder-generated enriched brief;
- original rendered brief;
- conversation interpretation read;
- relevant source reviews;
- three-builder-case pattern review;
- human-review awaiting-response state;
- PR154 automatic triage contract.

## Packet Shape

The packet includes:

- `schema_version`
- `packet_metadata`
- `mode: checked_in_safe`
- `triage_contract_ref`
- `source_cases`
- `source_artifacts`
- `enriched_brief_refs`
- `original_brief_refs`
- `interpretation_read_refs`
- `source_review_refs`
- `human_calibration_refs`
- `custody_flags`
- `triage_field_groups`
- `future_triage_tasks`
- `known_limits`
- `non_claims`

The `triage_field_groups` entries mirror the PR154 contract policy, but every
field remains `not_evaluated`, with `semantic_triage_filled: false` and
`value: null`.

## Boundaries

PR155 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- create new Lolla runs;
- create new interpretation reads;
- create a populated triage read;
- fill semantic triage fields;
- check in raw/private content;
- include provider text;
- include local absolute paths;
- fill human-review answers;
- claim product proof;
- claim human validation;
- score answer quality;
- create approval or certification labels;
- authorize agent or automatic action;
- implement runtime attachment.

## Validation

The PR155 tests prove that:

- the packet schema version is `lolla.decision_work_automatic_triage_packets.v0`;
- exactly the three intended cases are included;
- all packet refs resolve to checked-in artifacts;
- custody flags remain conservative;
- triage field groups are present but unfilled;
- the CLI writes a packet to an explicit output path;
- unsupported triage-contract schemas are rejected;
- generated packets contain no raw/private markers or local absolute paths.

## Recommended Next Slice

Recommended next slice:

```text
PR156 Codex-Assisted Provisional Triage Read v0
```

That slice may use one PR155 packet to produce a provisional triage read. It
must still avoid runtime integration, model calls from repo code, product
proof, human validation, answer-quality scoring, and action authorization.
