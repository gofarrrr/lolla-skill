# System-Level Semantic Evaluation Result

Date: 2026-07-10  
New paid calls for this analysis: 0  
Decision: retain SK3 repair; stop pressure prompt tuning; repair evaluation ontology

## Why this analysis was necessary

The pressure experiments scored only `user_pressure_events` against pressure
gold. Source review showed that some missing concepts were present in evidence,
option, constraint, or question events. The evaluation was correctly measuring
reader placement but incorrectly being read as total product coverage.

The new deterministic scorer reports both:

- **family-aligned coverage:** the exact source span appeared in a reader mapped
  to the observation's intended dimension;
- **system-level coverage:** the exact source span appeared anywhere in the
  semantic packet.

No semantic inference occurs during scoring.

## Full 12-case SK3 result

| measure | family-aligned | system-level | delta |
| --- | ---: | ---: | ---: |
| weighted exact-span recall | 0.552 | 0.716 | +0.163 |
| stable observations | 46 / 102 | 63 / 102 | +17 |

There were 50 observation/run cross-family rescues among 306 opportunities.
Pressure source material rose from 0.521 to 0.813 at the system level; dropped-
thread source material rose from 0.242 to 0.697.

Those gains mean the material was present, not that it carried the correct
semantic role. A dropped-thread quote preserved as a constraint cannot support
a dropped-thread audit without additional interpretation.

## Diagnostic three-case comparison

| arm | family recall | system recall | family stable | system stable |
| --- | ---: | ---: | ---: | ---: |
| SK3 repair | 0.547 | 0.760 | 13 / 25 | 19 / 25 |
| broad SK4 | 0.493 | 0.747 | 11 / 25 | 17 / 25 |

Broad SK4 remains worse than SK3 even when evaluated as a complete packet. Its
apparently improved Case 08 concept coverage does not justify the overall
regressions.

## Pressure ontology finding

The three diagnostic pressure observations are heterogeneous:

- Case 02 is primarily a frame correction, though later represented as an
  option condition.
- Case 08 is primarily an evidence/assumption boundary before becoming a later
  explicit reasoning qualification.
- Case 11 is initially an evidence boundary and later a self-correction of the
  pipeline premise.

A single family-specific recall number therefore mixes concept coverage,
semantic placement, and chronology. Further pressure prompt tuning would
optimize the wrong unit.

## Consequence

The retained system is more useful than the family-only score suggested, but
less organized and temporally complete than a system-level recall number would
suggest. The next task is to define what each observation must provide to each
consumer, then evaluate current artifacts before changing extraction again.

Canonical evaluation doctrine:
`docs/conversation-understanding/lolla-evaluation-doctrine-v0.md`.
