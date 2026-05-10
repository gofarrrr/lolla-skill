# V60 Transaction C4.3 Consideration-Router Readout

Date: 2026-05-10
Status: dormant replay evidence only
Branch: `feat/v60-transaction-local-replay-lab`

## Plain-English Summary

C4.3 corrects the C4.2 drift.

C4.2 asked whether v60 could safely add one public edge to a strong baseline.
That was useful, but too narrow. The product question is not "can v60 speak to
the user?" The sharper question is:

> Can v60 provide compact, source-backed material that is useful for Claude Code
> / Codex to consider, even when the material is rejected, deferred, kept
> private, or creates no visible answer change?

This is still dormant lab work. It does not integrate v60 into live `/lolla`.

## What Changed

The paid replay harness now supports:

```bash
--c-variant consideration_router
```

Implementation:

- `scripts/run_v60_transaction_paid_replay.py`
- `tests/test_v60_transaction_paid_replay.py`

C4.3 keeps the normal public answer fields so Arm C can still be blinded
against Arm B. It adds a private `consideration_usefulness_report` for review.

The private report asks for:

- one `chunk_assessment` per candidate card;
- `usefulness_to_consider`: `high`, `medium`, `low`, or `none`;
- `opportunity_role`: frame changer, evidence gate, diagnostic question,
  guardrail, tension maker, boundary marker, compression aid, or rejection aid;
- `route`: private reasoning, public answer delta, diagnostic question,
  evidence gate, guardrail, defer missing evidence, reject irrelevant, or reject
  duplicate;
- up to three selected opportunities;
- retrieval feedback about whether the packet was overfed, underfed, or missing
  a better signal.

The validator checks shape, trace IDs, enums, one assessment per card, selected
opportunity references, and public-output machinery leaks. It does not judge
semantic usefulness.

## Why This Matters

This aligns v60 with the existing lane doctrine. Lanes do not prove truth; they
surface opportunities for structured reconsideration. v60 should do the same at
a richer level:

- the deterministic layer decides what deserves consideration;
- v60 provides source-backed affordances and absence rails;
- the LLM decides whether to use, reject, defer, or privately absorb them;
- review artifacts let us study what happened.

This is also the right place to connect the qmd lesson. qmd's useful idea is
hybrid, context-aware retrieval: lexical search, semantic search, query
expansion, reranking, context metadata, and score traces. For Lolla, that should
eventually mean affordance-level and absence-level retrieval with explainable
selection. But embeddings must remain additive low-trust recall, not the judge.

## Verification

Commands run:

```bash
python3 -m pytest tests/test_v60_transaction_paid_replay.py -q
python3 -m py_compile scripts/run_v60_transaction_paid_replay.py
```

Result:

- focused paid-replay tests: 33 passed;
- replay script compiled.

## Dry Run

Path:

- `data/evaluations/v60_transaction_replay_lab/2026-05-10-c43-consideration-router-dry-run`

Configuration:

- Artifact: `data/compiled/model_affordances/affordances_v60.json`
- Config: `cap8_focused`
- Mode: `edge_audit`
- Cases: all 8 manifest cases
- C variant: `consideration_router`
- Paid calls: 0

Aggregate:

- Items: 8
- Cards per item: 8
- Suppressed candidates per item: 10
- Ledger validation: `{"not_run_dry_run": 8}`
- Delta validation: `{"not_applicable": 8}`
- Consideration validation: `{"not_run_dry_run": 8}`
- Arm B prompt estimate: 3,619-9,184 tokens
- Arm C packet view estimate: 6,544-7,276 tokens
- Arm C prompt estimate: 11,551-17,179 tokens

Dry-run packet pressure:

| Item | C Prompt Tokens | Packet Tokens | Cards | Absence Records | Weak Support | Medium Confidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `multi-offer__edge_audit` | 15,070 | 7,183 | 8 | 16 | 0 | 1 |
| `whistleblower__edge_audit` | 15,761 | 7,276 | 8 | 16 | 0 | 1 |
| `startup-pivot__edge_audit` | 12,381 | 6,902 | 8 | 16 | 0 | 0 |
| `real-estate__edge_audit` | 11,551 | 6,664 | 8 | 16 | 2 | 2 |
| `friendship-money__edge_audit` | 12,735 | 6,708 | 8 | 16 | 0 | 0 |
| `messy-three-problems__edge_audit` | 13,919 | 6,544 | 8 | 16 | 0 | 0 |
| `user-has-plan__edge_audit` | 12,993 | 6,887 | 8 | 16 | 0 | 0 |
| `phd-research__edge_audit` | 17,179 | 6,727 | 8 | 16 | 0 | 0 |

## Interpretation

C4.3 is not evidence that v60 is product-ready. It is evidence that the lab now
asks the right question.

The next paid run should not be scored only by Arm C public wins. It should
separate:

- private packet usefulness;
- correct rejection and deferral;
- public answer delta when deserved;
- correct no-op when the packet adds no public value;
- overfeeding or underfeeding signals;
- whether qmd-style retrieval would have selected better chunks.

## Next Test

Run a small paid C4.3 replay on the same eight cases, then review two artifacts
per item:

1. The blinded Arm B vs Arm C public outputs.
2. The private `consideration_usefulness_report`.

Promotion should require usefulness evidence from both layers. A public tie can
still be informative if the private report shows that v60 created a guardrail,
blocked an overclaim, or correctly rejected irrelevant material.
