# Decision Work Automatic Triage Provisional Read v0

Status: PR156 Codex-assisted provisional triage read

Date: 2026-07-02

Schema: `lolla.decision_work_automatic_triage_provisional_read.v0`

## Purpose

PR156 uses one PR155 automatic-triage packet shape to run a bounded
Codex-assisted provisional triage read over the three existing Decision Work
Brief builder outputs.

The read asks which cases look like normal brief candidates, which should stay
agent-inspection-only, which need domain/legal/human calibration, where source
depth is thin, and where cleaner prose could create false confidence.

This is not a model call from repo code. It is not human validation, product
proof, answer-quality scoring, runtime integration, approval, certification, or
agent action authorization.

The checked-in read is:

- [PR156 triage read JSON](../../reviews/codex-assisted/decision-work-automatic-triage-provisional-read-v0/read.json)

## Source Packet

PR155 can generate the packet locally:

```bash
python3 scripts/evals/build_decision_work_automatic_triage_packets.py \
  --triage-contract docs/conversation-understanding/decision-work-automatic-triage-contract-v0.json \
  --out /tmp/decision_work_automatic_triage_packets.json \
  --pretty
```

PR156 does not check in that generated packet. The read records a safe source
packet summary instead: packet schema, case count, source artifact refs, and
the fact that the packet was generated locally from checked-in-safe metadata.

## Cases

The provisional read covers exactly:

- `launch-public-enterprise-beta`
- `deploy-assisted-intake-routing`
- `ceo-remove-founding-cofounder`

It uses only existing builder outputs, original rendered briefs,
interpretation reads, review artifacts, PR153 human-review pause status, and
the PR154 triage contract.

## Provisional Pattern

The read finds a usable routing distinction:

- launch-beta is the closest normal brief candidate, with source-depth and
  buyer-context caveats;
- deploy-intake is useful but should route through domain/compliance caution
  before any user-facing confidence;
- the cofounder/governance case is the strongest overtrust risk and should be
  treated as agent-inspection-only or human/domain-calibration-required before
  user-facing use.

This pattern is useful because triage can route attention without pretending
to decide correctness.

## Boundaries

PR156 does not:

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
- include provider text;
- include local absolute paths;
- fill human-review answers;
- claim human validation;
- claim product proof;
- score answer quality;
- approve or certify the advice;
- authorize agent or automatic action;
- implement runtime attachment.

## Decision Gate

Decision gate:

```text
proceed_to_offline_v1_closure_gate
```

Recommended next slice:

```text
PR157 Decision Work Brief Offline v1 Closure Gate v0
```

PR157 should decide whether the Decision Work Brief, enrichment, and automatic
triage system is coherent enough to call functional offline v1 with explicit
limitations.
