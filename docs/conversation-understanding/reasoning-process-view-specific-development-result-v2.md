# Reasoning-process view-specific development result

Status: source custody solved; four semantic views pass development review; exploration requires a local-path redesign  
Date: 2026-07-11

## Outcome in simple terms

The new sentence-alias interface fixed the mechanical problem. Gemini no longer
had to reproduce long quotations: it selected short visible IDs, and local code
resolved them to stable source spans. Across the first redesign probe, all 61
citations were valid. After a zero-call correction to our compiler's authority
label, all five responses compiled without changing model content.

That did not make all semantic reading reliable. The first redesign still
missed the important limit attached to an earlier alternative, allowed a
trajectory claim without separate starting evidence, and admitted one final
proposal as if it were a challenge.

The v2 relationship contracts then required:

- starting state, current position, and qualification for a trajectory;
- an alternative and its specifically attached condition or limit;
- the prior claim or frame, challenge, response, and revision for a challenge.

Fifteen failure-derived fixtures across all five conversations and their
append-only compilations passed provider-free. In a new Case-02 probe, the
position, evidence, uncertainty, and challenge relationships passed source
review. The challenge reader no longer mislabeled the final proposal.

Exploration remained the exception. It again omitted the earlier named-role
recruitment test and the qualification that real volunteer energy need not
provide all required ownership. A targeted chronological call recovered the
alternative but substituted a more general volunteer-risk sentence for the
attached qualification. A final conversation-only ablation recovered neither,
so the optional ledger was not the root cause.

## What the experiments establish

| question | evidenced answer |
| --- | --- |
| Can stable aliases replace free-form quote reproduction? | Yes in this development case: 61/61 v1 and 59/59 v2 role citations resolved. |
| Can deterministic validation catch convincing custody errors? | Yes; it caught the compiler-authority mismatch, invalid parking value, unknown auxiliary IDs, and all prior quote problems without semantic rules. |
| Do explicit relationship roles help? | Yes. Position and challenge failures were corrected in the v2 model output. |
| Is one full-conversation reader reliable for all five questions? | No. Exploration repeatedly lost the same minority alternative-limit relationship. |
| Was the complete auxiliary ledger causing that exploration miss? | Not supported. Removing it did not recover the target and created new field confusion. |
| Is Phase-4 transfer ready? | No. One critical dimension remains at zero. |

## Important implementation lesson

`park_unselected_auxiliary_observations` should not be model-authored. All five
v2 payloads returned `false` despite a provider schema declaring `const: true`.
Parking the unselected complement is deterministic custody policy. Future
provider schemas should omit that field; compilation should add the mechanical
disposition unconditionally and preserve it in the receipt.

Likewise, when no auxiliary ledger is supplied, the provider schema should not
ask for auxiliary observation IDs. In the conversation-only ablation, Gemini
put sentence aliases into that empty field. Schema shape must follow the actual
context supplied.

## Current architecture decision

Keep four full-conversation readers:

- position and decision trajectory, with explicit starting/current evidence;
- evidence and assumption discipline;
- uncertainty and unresolved state;
- challenge and revision response, with an explicit prior frame.

Redesign only exploration. The next provider-free question is whether a narrow
local chronological harvester can preserve alternative-plus-attached-limit
pairs per turn or short turn window, append them directly to custody, and avoid
another global semantic synthesizer. This is not a return to the former
three-lens 88–95-event architecture: it is one failed semantic family, a fixed
pair contract, bounded local windows, and no global rewrite.

No more prompt repair, model call, transfer, graph, live-skill, or runtime work
is authorized until that exploration-only design passes provider-free fan-out,
duplicate-custody, and cold-reader representation checks.

## Accounting

- View-specific v1 probe: 5 Gemini/OpenRouter calls, $0.0114425 estimated.
- View-specific v2 probe: 5 Gemini/OpenRouter calls, $0.01207775 estimated.
- Targeted chronological exploration: 1 call, $0.00253225 estimated.
- Conversation-only ablation: 1 call, $0.001959 estimated.
- Total in this redesign sequence: 12 calls, $0.0280115 estimated.
- Automatic retries, fallbacks, evaluator, embedding, graph, pipeline, and
  runtime calls: zero.

These are activity and operability facts, not evidence of reasoning quality,
effort, trust, or final-answer correctness.

## Continuation evidence

- Provider-free v1 interface:
  `research/reasoning-process-view-specific-interface-2026-07-11/report.json`;
- v1 probe and compiler replay:
  `research/reasoning-process-view-specific-probe-2026-07-11/` and
  `research/reasoning-process-view-specific-replay-2026-07-11/`;
- provider-free v2 relationships:
  `research/reasoning-process-view-specific-v2-2026-07-11/report.json`;
- v2 source review:
  `research/reasoning-process-view-specific-v2-probe-2026-07-11/source-review.json`;
- targeted exploration and ablation reviews:
  `research/reasoning-process-exploration-v3-probe-2026-07-11/source-review.json`
  and
  `research/reasoning-process-exploration-v4-ablation-2026-07-11/source-review.json`.
