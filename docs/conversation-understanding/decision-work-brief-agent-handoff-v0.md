# Decision Work Brief Agent Handoff v0

Status: PR165 agent handoff packet

Date: 2026-07-02

Contract: `lolla.decision_work_brief_agent_handoff_contract.v0`

Packet schema: `lolla.decision_work_brief_agent_handoff.v0`

## Purpose

PR165 defines and generates the checked-in-safe packet another agent can
inspect from a Decision Work Brief runtime bundle.

The handoff is for inspection, routing, and caveat preservation. It does not
authorize action. It does not contain raw/private conversation text, raw memo
text, provider text, private ledgers, local absolute paths, hidden
chain-of-thought style material, or secrets.

## Packet Contents

The packet includes:

- source run ref;
- attachment status ref;
- brief and enriched brief refs;
- triage refs;
- source status;
- privacy/redaction status;
- missingness;
- uncertainty and source-depth notes from existing triage artifacts when
  supplied;
- route outputs;
- blocked/deferred state;
- agent inspection focus;
- custody flags;
- non-claims.

Every packet sets:

- `agent_action_authorized: false`
- `automatic_action_authorized: false`
- `must_not_be_used_as_quality_label: true`

## CLI

```bash
python3 scripts/evals/build_decision_work_brief_agent_handoff.py \
  --source-run-ref launch-public-enterprise-beta/20260627T104146Z_7bfe79 \
  --attachment-status /tmp/decision_work/attachment_status.json \
  --triage-read reviews/codex-assisted/decision-work-automatic-triage-provisional-read-v0/read.json \
  --case-id launch-public-enterprise-beta \
  --out /tmp/decision_work/agent_handoff_packet.json \
  --pretty
```

## Decision Gate

Decision gate:

```text
proceed_to_flagged_post_archive_runtime_hook
```

Reason:

The handoff packet can be generated from manual bundle outputs, preserves
source refs, missingness, route outputs, and non-claims, and keeps raw/private
material out of the default agent surface. The next slice may inspect runtime
entry points and add only a default-off post-archive hook if a safe hook point
exists.

## Explicit Non-Claims

PR165 does not:

- run `$lolla`;
- invoke the Lolla skill;
- call provider or model APIs from repo code;
- mutate archives;
- change runtime behavior;
- change prompts;
- touch `SKILL.md`;
- touch `scripts/skill/*`;
- create new Lolla runs;
- create new interpretation reads;
- create new builder outputs;
- check in raw/private content;
- claim human validation;
- claim product proof;
- score answer quality;
- approve or certify advice;
- authorize agent or automatic action;
- implement runtime attachment.
