# Pre-Step-6 Replay Ledger Aggregate Readout

Date: 2026-05-18

Status: research-only aggregate. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, public output, workers, bundles, or handoff modes.

Related:

```text
research/pre-step6-replay-records/third-year-phd-student.conflict.off-default-replay.v1.json
research/pre-step6-replay-records/mother-address-year.quiet.off-default-replay.v1.json
research/pre-step6-replay-records/founder-grant-marcus-equity.high-clutter.off-default-replay.v1.json
research/pre-step6-source-overclaim-audits/third-year-phd-student.conflict.rendered-hybrid.source-overclaim-audit.v1.json
research/pre-step6-source-overclaim-audits/mother-address-year.quiet.rendered-hybrid.source-overclaim-audit.v1.json
research/pre-step6-source-overclaim-audits/founder-grant-marcus-equity.high-clutter.rendered-hybrid.source-overclaim-audit.v1.json
research/pre-step6-semi-blind-comparisons/third-year-phd-student.conflict.semi-blind-comparison.v1.json
research/pre-step6-semi-blind-comparisons/mother-address-year.quiet.semi-blind-comparison.v1.json
research/pre-step6-semi-blind-comparisons/founder-grant-marcus-equity.high-clutter.semi-blind-comparison.v1.json
scripts/research/pre_step6_replay_ledger.py
tests/test_pre_step6_replay_ledger.py
tests/test_pre_step6_semi_blind_comparisons.py
```

## Question

After five static replay ledger records, including one rendered-hybrid loss,
what has actually been earned?

This aggregate is intentionally hostile to hype. It asks whether the current
evidence justifies:

```text
product promotion
runtime wiring
new handoff modes
replay generator design
more static replay
native or less-author-biased rejudging
```

The answer is not "four wins plus one healthy loss means promote." The answer is:

```text
the research surface is credible enough to challenge with less-author-biased
replay, but not ready for generator work or product integration
```

## Evidence Table

| Case | Mode | Comparison Kind | Winner | Source/Overclaim Audit | Naturalness Debt | Watch/Present Failure Modes | What Rendered Improved | What Control/Raw Still Did Better | Promotion Read |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PhD conflict | `card_first`, one card, one `inspect_more` | native semi-blind judge | rendered hybrid | pass, counts as replay win | medium | 1 | Preserved Silva-vs-fallback tension, gates, duplicate demotion | Raw won overclaim risk, machinery hygiene, unforcedness; control won lightness | pass to replay only |
| Mother quiet | `no_extra_pressure`, no card, no `inspect_more`, quiet guidance | local semi-blind rubric | rendered hybrid | pass, counts as replay win | low | 0 | Preserved monitored-channel caution while declining extra pressure | Control won length and unforcedness | pass to replay only |
| Founder high-clutter | `card_first`, one card, one `inspect_more`, two quiet receipts | local semi-blind rubric | rendered hybrid | pass, counts as replay win | medium | 2 | Preserved dependency pressure, false-precision caution, and quiet receipt demotion | Control won length and unforcedness; raw/control were less visibly structured | pass to replay only |
| Founder high-clutter native rejudge | `card_first`, one card, one `inspect_more`, two quiet receipts | native semi-blind judge | rendered hybrid aggregate, control tie by count | pass, counts as replay win | medium | 4 | Preserved the high-clutter decision tension under a less-author-biased judge | Control won source grounding, overclaim risk, lightness, and unforcedness | pass to replay only, with stronger brake |
| Consultant negative control | `card_first`, one card, two `inspect_more` items | local semi-blind rubric | control | pass, does not count | medium | 3 | Rendered preserved action/overreaction tension, but not enough to win | Control was shorter, safer, more grounded, and more natural | stop |

Aggregate facts:

```text
replay records: 5
rendered_hybrid replay wins: 4
control/raw/tie replay stops: 1
source/overclaim audit failures: 0
naturalness debt low: 1
naturalness debt medium: 4
naturalness debt high: 0
failed or losing replay records: 1
native/semi-blind judge records: 2
local-rubric records: 3
runtime/product promotion records: 0
```

## Risk Table

| Risk | Current Evidence | PM Read |
| --- | --- | --- |
| Naturalness debt recurrence | Four of five audited rendered answers carry medium naturalness debt. | This is now a pattern watch, not a decorative caveat. |
| Bloat recurrence | Founder high-clutter is 1,499 chars and has `answer_bloat: watch`. | High-clutter may become private notebook drift if unchecked. |
| Local-rubric bias | Three of five records are local semi-blind rubric records, including the first negative/control stop. | Treat local records as evidence-shape signals, not broad preference proof. |
| Pass-only archive bias | The ledger now has one rendered loss/control stop. | Trophy-shelf risk is reduced, not gone. One loss proves practice can record contrary evidence; it does not solve generator selection. |
| Source/overclaim durability | All five audits pass; no high-debt or failed audit record exists. | Good so far, but the first rendered loser shows a pass can still `does_not_count`. |
| Private machinery leakage | No current replay record reports leakage. | Keep watching, especially in high-clutter and quiet receipts cases. |
| Runtime temptation | Every replay record explicitly blocks product promotion and runtime wiring. | The docs must keep saying no, because "four wins plus one healthy loss" is still easy to misuse. |

## What The Passes Mean

The current records support a narrow architecture claim:

```text
The rendered hybrid handoff can transport selected private pressure into a
Step-6-style answer core while preserving source/overclaim custody.
```

The useful behaviors now observed are:

```text
card_first can preserve important pressure
no_extra_pressure can decline extra cognition
quiet_receipts can demote clutter without deleting custody
the ledger can record a rendered loss without schema bending
```

This is meaningful because the same small surface handled conflict, quiet
restraint, high-clutter demotion, and a negative/control stop without adding:

```text
new modes
bundle indexing
workers
subagent orchestration
live generation
runtime wiring
```

## What The Passes Do Not Mean

The current evidence still does not prove:

```text
rendered hybrid generally beats raw/control
humans would prefer the rendered answers
the local rubric decisions are robust
the builder/selector problem is solved
the system can reliably choose when not to generate a rendered handoff
medium naturalness debt is harmless
high-clutter answers will stay small in live use
runtime integration is justified
product docs should change
```

The most important limitation is not schema coverage. It is evidence shape:

```text
Four of five replay records are rendered wins.
Three of five records are local-rubric records.
Four of five audited rendered answers carry medium naturalness debt.
One negative/control stop exists, but it is local-rubric.
```

That combination argues for challenge, not promotion.

## Naturalness Debt

Current naturalness debt looks like an occasional tax in the mother case and a
recurring risk in the PhD, founder, and consultant rendered answers.

The worrying pattern is:

```text
rendered hybrid wins decision structure
control/raw win lightness, unforcedness, or overclaim caution
```

That tradeoff may be acceptable only when the decision pressure is genuinely
worth the added structure. If the pattern repeats in lower-pressure or
negative-control cases, rendered hybrid becomes worse than raw/control even if
it passes inclusion checks.

The PM rule should stay:

```text
medium naturalness debt is a watch
repeated medium debt blocks generator discussion until rejudged
high naturalness debt blocks replay win
```

Do not turn this into a fussy deterministic score. Use it as a promotion brake.

## Stop Conditions

Stop or narrow the rendered-hybrid path if any of these happen:

```text
native or less-author-biased judge prefers raw/control on the same case
rendered wins structure but loses usability in a lower-pressure case
source/overclaim audit fails after a comparison win
naturalness debt reaches high
medium naturalness debt repeats without a clear decision-quality gain
quiet receipts become a private mini-index
quiet mode starts adding pressure instead of withholding it
rendered answers leak private machinery or procedural terms
control/raw ties rendered while staying shorter and more natural
```

The last condition matters. A tie against a simpler arm is not neutral. Under the
current doctrine, a simpler tie should push away from generator work.

## Decision

Current aggregate decision after the negative/control replay:

```text
product_promotion: no
runtime_wiring: no
new_handoff_modes: no
bundle: no
workers: no
replay_generator_proposal: not_yet
more_static_replay: yes, but only if it tests selector failure
native_or_less_author_biased_rejudge: useful for any future promotion claim
```

The May 19 founder native rejudge satisfied the first brake:

```text
challenge the least comfortable local-rubric pass
```

The May 19 consultant negative/control replay satisfied the second brake:

```text
record at least one rendered-hybrid tie/loss/stop
```

But this still does not authorize option C:

```text
C. Draft a small off-default replay-generator proposal.
```

Generator work is still blocked because the live unsolved problem has changed:

```text
when should the system decline to generate/use a rendered handoff at all?
```

The negative/control replay shows such a case exists. It does not yet design the
selector or prove the selector can find it.

## Next Slice

Next recommended slice after the first rendered loss:

```text
post_negative_selector_boundary_decision
```

Purpose:

```text
decide what evidence would justify a tiny off-default generator proposal without
turning the generator into a deterministic reasoner
```

Pass criteria:

```text
explicit decline conditions for rendered handoff generation
medium naturalness debt treated as a design constraint
the consultant stop included as first-class evidence
no attempt to make the generator choose final truth
product promotion remains blocked
runtime wiring remains false
```

Do not use that slice to implement a generator. Its job is to decide whether
generator design is even worth specifying.

## PM Verdict

The replay ledger is doing useful research work. It is preserving custody,
comparison records, source/overclaim audits, naturalness debt, and promotion
blocks without pretending to be the reasoner.

The archive is no longer pass-only:

```text
five records
four rendered wins
one control win / rendered stop
zero failed audits
four medium-debt rendered audits
```

That is healthier than the previous state, but it points to the next product
boundary: any future generator must know when to withhold the rendered surface.

The next move should define that selector boundary before any implementation.

2026-05-19 follow-up: the founder high-clutter native rejudge has been
recorded:

```text
research/pre-step6-founder-high-clutter-native-rejudge-readout-2026-05-19.md
```

The rejudge kept rendered hybrid as aggregate winner, but made the evidence less
comfortable: control tied rendered on simple criterion count, while rendered won
only through aggregate weighting of decision usefulness, conflict preservation,
machinery hygiene, and duplicate demotion. Naturalness debt remains medium,
source grounding is now a watch, and answer bloat remains a watch.

This confirms the aggregate's caution rather than relaxing it. The next slice
should be a true negative/control replay where rendered hybrid can honestly tie
or lose. Replay-generator work remains not earned.

2026-05-19 follow-up: the first negative/control replay has been recorded:

```text
research/pre-step6-negative-control-replay-readout-2026-05-19.md
```

The consultant negative-control slice records a rendered-hybrid loss without
schema bending. Control wins aggregate, rendered passes source/overclaim audit
but `does_not_count`, and replay decision is `stop`.

This reduces trophy-shelf risk. It does not authorize generator work. The next
question is now selector-boundary design: what evidence would let a future
off-default generator decline rendered handoff generation when the control path
is already enough?

2026-05-19 selector-boundary follow-up:

```text
research/pre-step6-selector-boundary-decision-memo-2026-05-19.md
```

The selector-boundary memo keeps generator implementation blocked. It records
that the core question has moved from "can rendered transport pressure?" to
"can we know when not to transport it?" The recommended next gate is a native or
less-author-biased rejudge of the consultant negative/control stop.
