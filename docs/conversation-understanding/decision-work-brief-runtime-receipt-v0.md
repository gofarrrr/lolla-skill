# Decision Work Brief Runtime Receipt v0

Status: PR164 short receipt renderer

Date: 2026-07-02

## Purpose

PR164 defines the tiny user-facing receipt for a runtime-attached Decision Work
Brief. The receipt is intentionally short: it says whether the brief is
available, caveated, agent-inspection-only, blocked, deferred, failed closed,
or not requested.

The receipt never renders the full brief into the chat by default. It points to
the safe bundle refs when available.

## Supported States

The renderer supports:

- available;
- caveated available;
- agent-inspection-only;
- blocked;
- deferred;
- failed closed;
- disabled or not requested.

Every receipt includes a caveat line:

```text
Main caveat: this is an audit summary, not proof that the advice is correct.
```

## Examples

Available:

```text
Decision Work Brief: available

What changed: See the Decision Work Brief.

Main caveat: this is an audit summary, not proof that the advice is correct.

Open full brief: `decision_work/decision_work_brief_enriched.md`

Open evidence bundle: `decision_work/attachment_status.json`
```

Blocked:

```text
Decision Work Brief: blocked

Reason: missing_revised_answer.

Main caveat: this is an audit summary, not proof that the advice is correct.

Open evidence status: `decision_work/attachment_status.json`
```

Caveated:

```text
Decision Work Brief: available with caveats

What changed: See the Decision Work Brief.

Main caveat: this is an audit summary, not proof that the advice is correct.
```

## CLI

```bash
python3 scripts/evals/render_decision_work_brief_runtime_receipt.py \
  --status-json /tmp/decision_work/attachment_status.json \
  --out /tmp/decision_work/user_receipt.md
```

Or render directly:

```bash
python3 scripts/evals/render_decision_work_brief_runtime_receipt.py \
  --state blocked \
  --reason missing_revised_answer
```

## Decision Gate

Decision gate:

```text
proceed_to_agent_handoff_packet
```

Reason:

The receipt renderer covers available, caveated, agent-only, blocked, deferred,
failed-closed, and disabled states while preserving explicit non-claims. The
next slice should define what another agent can inspect from the attachment
bundle.

## Explicit Non-Claims

PR164 does not:

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
