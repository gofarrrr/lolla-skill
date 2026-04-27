# Lane 2 next-track decision memo

Date: 2026-04-27
Status: decision memo after PR #43 producer audit merge
Input artifact: `research/stability-runs/lane2-producer-audit-2026-04-26/synthesis.md`

## 1. Decision

The next Lane 2 track should start with **quote-validation repair before demotion**.

This is a narrow producer-side fix. It does not loosen the trust gate. It keeps the rule that every surfaced anchor must be backed by a literal substring from the answer. The change is that when the verifier accepts a model but returns a non-literal or slightly paraphrased evidence quote, the system gets one chance to repair that quote to a real substring before demoting the model.

Recommended implementation track:

1. Quote-validation repair before demotion.
2. Re-run the PR #43 audit corpus against the change.
3. If trust stays clean and friction yield improves, keep it.
4. Then decide whether recall for interpretive models is still the next bottleneck.

Do **not** start with candidate-cap tuning, verifier decomposition, or full producer decomposition. Those may become justified later, but they are not the first move the audit calls for.

## 2. Why this is first

PR #43 found that Lane 2 is **high-trust but uneven-friction**:

- Trust axis: 0 false positives across 26 observed anchor judgments.
- Friction axis: useful anchors often fail to reach Step 6.
- Stability axis: the same source can yield different friction across runs.

The optimization target is:

> More useful mental-model pressure, same or near-same trust, better repeatability.

Quote-validation repair is the best first move because it directly targets a known friction leak without weakening the trust layer.

The audit found quote-validation demotion rates of:

- Case 1: 50%
- Marcus: 67%
- Case 7: 57%
- Other cases: 0%

This is not the only Lane 2 problem, but it is the cleanest one to attack first. The verifier has already said "this model is present"; the downstream code then drops the model because the quote is not a literal substring. A repair step can preserve the trust doctrine by accepting only a repaired quote that is literally present in the source.

## 3. What this should not become

This track must not become "trust paraphrased quotes."

The literal-substring gate exists for a good reason: it prevents hallucinated evidence. The repair step is allowed to replace a bad quote with a real quote. It is not allowed to accept the verifier's paraphrase as evidence.

This track also must not become "surface more anchors by being less strict."

The audit's strongest result is the clean trust axis. The system's most valuable property is that surfaced anchors are defensible. We should spend that trust carefully.

## 4. Proposed behavior

Current behavior:

1. Verifier returns an accepted model with `evidence_quote`.
2. `parse_verification_response` checks whether `evidence_quote in answer_text`.
3. If not literal, the accepted model is demoted with `execution_quote_not_literal_substring`.

Proposed behavior:

1. Verifier returns an accepted model with `evidence_quote`.
2. Exact literal check runs.
3. If exact check fails, normalized literal check runs.
4. If normalized check fails, quote-repair tries to find a high-overlap literal substring from `answer_text`.
5. If repair finds a literal substring, accept the model with the repaired quote and record that repair happened.
6. If repair fails, demote exactly as today.

The repaired quote must be a literal substring. No exception.

## 5. Implementation sketch

Likely code area:

- `engine/system_b/companion_routing.py`
- `parse_verification_response`

There are already helper functions near the top of the file:

- `_quote_in_answer`
- `_normalize_quotes`
- `_tokenize`

One immediate issue: `parse_verification_response` currently uses raw `evidence_quote in answer_text`, not `_quote_in_answer`. So the first safe improvement is to use the existing normalized quote helper.

Do not use `_fuzzy_quote_in_answer` at the verification parsing site. It is useful for fingerprint validation, but here it would trust token-overlap evidence that may only be a paraphrase. Verification repair must end in a literal substring from `answer_text`.

The next improvement is a small quote-repair helper, for example:

```text
repair_evidence_quote(evidence_quote, answer_text) -> repaired_literal_quote | None
```

It should:

- split `answer_text` into candidate sentence or paragraph spans,
- score candidate spans by token overlap with the verifier quote,
- require a high threshold,
- reject very short or generic spans,
- return only a substring copied from `answer_text`,
- return `None` if no safe repair exists.

This should be deterministic if possible. If deterministic repair is too weak, a later version can test an LLM quote-repair call, but the first implementation should avoid adding another probabilistic stage.

## 6. Audit and observability requirements

The repair must be visible in audit output.

At minimum, we need to know:

- how many accepted verifier entries were exact-literal,
- how many were repaired,
- how many still demoted,
- original verifier quote for repaired/demoted rows,
- repaired literal quote when repair succeeds.

The current audit structures may need a small field addition. If adding a first-class field is too much for the first PR, the fallback is to record repair/demotion counts in rejected metadata or audit summary. But the preferred version is first-class observability, because this track exists to measure the quote gate.

Suggested field names:

- `companion_verification_quote_repairs`
- `original_evidence_quote`
- `repaired_evidence_quote`
- `repair_method`
- `repair_score`

## 7. Acceptance gates

The first implementation should be judged on the existing PR #43 audit corpus.

Hard gates:

- False positives remain 0 on the audited observed-anchor rows, or any new possible false positive triggers manual review and blocks merge.
- Every surfaced anchor still has a literal evidence quote.
- No repaired quote is accepted unless it is an exact substring of the source answer.

Product gates:

- `post_verifier_validation_failure_rate` drops on at least two of the affected cases (case 1, Marcus, case 7).
- Repair rescues a non-trivial number of anchors across the audit corpus, with a working floor of at least 5 repaired accepted entries. A technically correct repair that rescues zero or near-zero anchors is not product-successful.
- `friction_yield_strict` or `friction_yield_any_honest` improves on at least one affected case.
- Cases that previously had 0% post-verifier demotion do not regress: no new false positives, no new quote-validation demotions, and no lower friction yield caused by the parser change.
- Same-source case 3 vs case 7 is not allowed to get worse.

Interpretive gate:

- If quote repair mostly preserves anchors that the human audit classifies as honest, this track succeeds.
- If quote repair mostly preserves anchors with quote drift or weak evidence, stop and tighten repair.

## 8. Why not recall first

Recall is a real problem. Marcus's 13/60 candidate slate and repeated absences for interpretive models show that.

But recall is a broader change. It may require substrate aliases, reasoning-shape recall, embedding policy, or a new decomposition step. It can also increase the verifier's burden by sending more borderline candidates downstream.

Quote repair is smaller and more trust-preserving. It only rescues candidates that the existing verifier already accepted. That makes it the better first test.

Recall should be the second track if quote repair improves quote-gate losses but leaves friction yield too low.

## 9. Why not verifier decomposition first

Earlier Lane 2 notes considered verifier cleanup, candidate-cap changes, and reasoning-type partitioned verification. The producer audit changes the priority.

The audit did not show a generic false-positive problem. It also did not show that "more verifier architecture" is the next obvious fix. It showed several separate leaks:

- quote validation,
- recall vocabulary,
- verifier interpretive rejection,
- run-to-run variance,
- honest anchor ambiguity.

Verifier decomposition might help some of these, but it is too broad for the first post-audit move. It also risks adding another probabilistic layer before we have tried the simpler deterministic repair.

Candidate-cap reduction is especially not first. The audit found missed useful anchors and one thin candidate slate. Lowering the candidate cap could make recall starvation worse.

## 10. Why not full Sully-style decomposition first

The Sully lesson still matters: overloaded prompts often create downstream correction loops.

But the audit's discipline says not to jump straight to an elegant architecture. The leak map should choose the next move.

Full producer decomposition may be right later if:

- quote repair does not improve affected cases,
- recall work does not improve interpretive-model yield,
- same-source stability remains too low,
- and the remaining failures clearly come from overloaded LLM judgment rather than deterministic glue.

Until then, decomposition is held.

## 11. Second track if quote repair passes

If quote repair improves friction without weakening trust, the likely next track is **recall for interpretive models**.

Target families:

- Problem Framing And Reframing
- Optionality
- Premortem
- Opportunity Cost

Likely recall work:

- richer model aliases and trigger phrases,
- reasoning-shape tags,
- shape-scoped recall,
- embedding recall policy review,
- deterministic expansion of source phrases into model-family candidates.

This track should have its own design memo. It should not be smuggled into quote repair.

## 12. What "better" means

Lane 2 is better only if it improves all three product axes:

1. **Trust:** surfaced anchors are still defensible.
2. **Friction:** more anchor-worthy clusters produce useful mental-model pressure.
3. **Repeatability:** rerunning the same conversation produces less product-level variation.

The quote-repair track mostly targets trust-preserving friction. It may not solve repeatability. That is acceptable for a first move, as long as the remaining repeatability problem is measured clearly after the change.

## 13. Next artifact

Next artifact should be an implementation plan or PR for quote-validation repair.

Proposed branch:

`feat/lane2-quote-validation-repair-2026-04-27`

Proposed PR scope:

- implement normalized quote matching in `parse_verification_response`,
- add deterministic quote repair before demotion,
- persist repair observability,
- add unit tests for exact, normalized, repaired, and unrepaired quote cases,
- re-run the PR #43 audit corpus or a bounded subset that includes case 1, Marcus, and case 7.

Stop condition:

- If repaired anchors introduce any false-positive or weak-evidence pattern, stop and tighten or abandon the repair path.

The goal is not more anchors at any cost. The goal is **more useful mental-model pressure, same trust, better measured behavior**.
