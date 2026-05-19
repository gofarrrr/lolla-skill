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

After three static replay ledger records, what has actually been earned?

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

The answer is not "three wins means promote." The answer is:

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

Aggregate facts:

```text
replay records: 3
rendered_hybrid replay wins: 3
source/overclaim audit failures: 0
naturalness debt low: 1
naturalness debt medium: 2
naturalness debt high: 0
failed or losing replay records: 0
native/semi-blind judge records: 1
local-rubric records: 2
runtime/product promotion records: 0
```

## Risk Table

| Risk | Current Evidence | PM Read |
| --- | --- | --- |
| Naturalness debt recurrence | Two of three replay wins carry medium naturalness debt. | This is now a pattern watch, not a decorative caveat. |
| Bloat recurrence | Founder high-clutter is 1,499 chars and has `answer_bloat: watch`. | High-clutter may become private notebook drift if unchecked. |
| Local-rubric bias | Mother and founder wins are local semi-blind rubric records, not native judge runs. | Treat them as restraint/clutter signals, not broad preference proof. |
| Pass-only archive bias | The ledger can record failure, but the archive has no failed replay record yet. | Failure-capable schema is not the same as failure-tolerant research practice. |
| Source/overclaim durability | All three audits pass; no high-debt or failed audit record exists. | Good so far, but the audit has not been tested against a rendered loser. |
| Private machinery leakage | No current replay record reports leakage. | Keep watching, especially in high-clutter and quiet receipts cases. |
| Runtime temptation | Every replay record explicitly blocks product promotion and runtime wiring. | The docs must keep saying no, because "three wins" is an easy story to misuse. |

## What The Passes Mean

The three records support a narrow architecture claim:

```text
The rendered hybrid handoff can transport selected private pressure into a
Step-6-style answer core while preserving source/overclaim custody.
```

The three useful behaviors now observed are:

```text
card_first can preserve important pressure
no_extra_pressure can decline extra cognition
quiet_receipts can demote clutter without deleting custody
```

This is meaningful because the same small surface handled conflict, quiet
restraint, and high-clutter demotion without adding:

```text
new modes
bundle indexing
workers
subagent orchestration
live generation
runtime wiring
```

## What The Passes Do Not Mean

The current evidence does not prove:

```text
rendered hybrid generally beats raw/control
humans would prefer the rendered answers
the local rubric decisions are robust
the builder/selector problem is solved
the system can record and learn from losing evidence in practice
medium naturalness debt is harmless
high-clutter answers will stay small in live use
runtime integration is justified
product docs should change
```

The most important limitation is not schema coverage. It is evidence shape:

```text
All replay records are passes.
Two of three passes are local-rubric records.
Two of three passes carry medium naturalness debt.
```

That combination argues for challenge, not promotion.

## Naturalness Debt

Current naturalness debt looks like an occasional tax in the mother case and a
recurring risk in the PhD/founder cases.

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

Current aggregate decision:

```text
product_promotion: no
runtime_wiring: no
new_handoff_modes: no
bundle: no
workers: no
replay_generator_proposal: not_yet
more_static_replay: yes, but only if falsification-oriented
native_or_less_author_biased_rejudge: yes
```

Choose option B before C:

```text
B. Run a native or less-author-biased judge replay on the riskiest local-rubric
   pass before drafting any replay-generator proposal.
```

The riskiest current pass is founder high-clutter because it has both:

```text
medium naturalness debt
answer bloat watch
```

If a less-author-biased judge downgrades founder to raw/control/tie, record that
honestly as `retest` or `stop`. That would be valuable evidence, not a setback.

If founder survives less-author-biased rejudging, the next blocker is option A:

```text
A. Add one true negative/control replay where rendered hybrid should tie or lose.
```

Only after B and A should option C be discussed:

```text
C. Draft a small off-default replay-generator proposal.
```

Generator work is not earned by the current aggregate alone.

## Next Slice

Next recommended slice:

```text
native_or_less_author_biased_founder_high_clutter_rejudge
```

Purpose:

```text
test whether the least comfortable replay win survives a judge that did not
author the local rubric
```

Pass criteria:

```text
dependency-system pressure still matters
quiet receipts stay quiet
control/raw lightness remains visible in the record
medium naturalness debt is not minimized
rendered does not win merely by being more complete
raw/control/tie can be recorded honestly as retest or stop
product promotion remains blocked
runtime wiring remains false
```

Do not use that slice to add fields, modes, workers, or a generator. Its job is
to make the current evidence less comfortable.

## PM Verdict

The replay ledger is doing useful research work. It is preserving custody,
comparison records, source/overclaim audits, naturalness debt, and promotion
blocks without pretending to be the reasoner.

But the archive is currently too clean:

```text
three records
three passes
zero losses
zero failed audits
zero high-debt examples
```

That is exactly when research can start looking rigorous while quietly becoming
a trophy shelf.

The next move should challenge the least comfortable win, not build on it.

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
