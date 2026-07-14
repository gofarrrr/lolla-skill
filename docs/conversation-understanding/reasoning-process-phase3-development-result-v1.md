# Reasoning-process Phase 3 development result

Status: complete — material redesign required  
Date: 2026-07-11

## Outcome

Phase 3 did not pass its frozen gate, and Phase 4 transfer is not authorized.

The target-blind five-reader design was tested on the mechanically selected
Case 02 using Gemini 3.1 Flash Lite through OpenRouter. The model received the
authoritative conversation, one narrow process question, and the complete
Phase-1 auxiliary ledger. It never received protected targets or Phase-2
source-review addenda.

The baseline stopped after an OpenRouter rate-limit error on request three. Its
two reviewable calls recovered one protected target and missed one earlier
alternative. That semantic miss—not the rate limit—justified the single allowed
generic repair.

The repair required a chronological scan and up to four materially distinct
items. All five calls completed. Four were admitted and recovered their
protected targets. The exploration call was quarantined because it joined
non-contiguous source text with an ellipsis; its recovered alternative also
omitted the protected limiting condition. One admitted position item
strengthened its cited evidence into advice that the cited sentence did not
state.

Repair evidence vector:

| dimension | result |
| --- | ---: |
| operational success | 5/5 |
| typed admission | 4/5 |
| protected target visibility | 4/5 |
| exact source references | 28/29 |
| invalid admitted items | 1 |
| source-strength inflations | 1 |
| context-invisible labels | 1 |
| critical dimensions at zero | 1 |

Partial improvement cannot be promoted into a pass because the frozen contract
requires every dimension to be admitted, source-valid, protected-target
visible, and free of source-strength or context-invisible errors.

## Architectural interpretation

The result supports the main hybrid thesis:

- Gemini was useful at the narrow semantic jobs;
- deterministic source validation correctly caught a convincing but invalid
  ellipsis quotation;
- the full-conversation scan recovered earlier minority material that the
  baseline dropped;
- the canonical ledger, append-only overlays, complete dispositions, budgets,
  and call custody all worked without semantic rules.

The failure is at the semantic interface, not a reason to add deterministic
conversation gates or another global synthesizer. One universal item schema
does not force the relationships each process question actually needs.

## Next bounded redesign

Provider-free work should next test:

1. five view-specific response contracts rather than one universal item shape;
2. explicit semantic roles such as alternative plus limit, challenge plus
   response, evidence claim plus boundary, and current position plus remaining
   qualification;
3. a lossless sentence-span table with visible stable IDs, so the reader selects
   evidence instead of reproducing long quotations;
4. the same authoritative-conversation, target-blind, no-score, no-graph, and
   deterministic-custody boundaries.

This is a small interface redesign, not an architectural expansion. No second
prompt repair, transfer case, graph test, live-skill change, or runtime
integration is authorized.

## Accounting and evidence

- Total OpenRouter requests: 8.
- Estimated total cost: $0.018682.
- Automatic retries, fallback models, evaluator calls, embedding calls, graph
  calls, pipeline calls, and runtime calls: zero.
- Terminal record:
  `research/reasoning-process-phase3-development-2026-07-11/decision.json`.
- Human-readable evidence:
  `research/reasoning-process-phase3-development-2026-07-11/result.md`.
