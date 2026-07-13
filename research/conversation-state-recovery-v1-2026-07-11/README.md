# Conversation-state candidate recovery v1

Status: provider-free replay passed; no provider call authorized  
Date: 2026-07-11

## Purpose

This package freezes the recovery foundation created after the monolithic
conversation-state probe failed semantically. It tests whether the five
source-reviewed development conversations can pass through three shallow typed
candidate families, exact source custody, a deterministic ledger, and the
existing conversation-state handoff without provenance loss or graph leakage.

It does not test whether a model can populate those candidates correctly.

## Contents

- `contract.json`: immutable artifact, case, source, fixture, and aggregate
  expectations;
- `atomic-migration.json`: source-reviewed split of two legacy mixed-strength
  constraints into four atomic candidates;
- `replay-result.json`: checked-in deterministic replay result;
- `result.md`: plain-language interpretation and stop line.

The four adversarial fixtures live in
`tests/fixtures/conversation_state_recovery/` and are hash-locked by the
contract.

## Reproduce

```bash
PYTHONPATH=. python3 scripts/evals/replay_conversation_state_candidate_recovery.py \
  --contract research/conversation-state-recovery-v1-2026-07-11/contract.json
```

The replay performs no provider or graph calls and does not change runtime.

## Boundary

Passing means the typed representation, source resolver, candidate ledger,
quarantine, and compiler work against reviewed fixtures. It does not mean:

- automatic extraction improved;
- provider structured output will accept the schemas;
- the reviewed labels are independent gold;
- mental-model selection or graph pressure improved;
- a revised answer is better;
- runtime integration is justified.

