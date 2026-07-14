# Counter-Pressure Temporal and Concept Coverage Review

Date: 2026-07-10  
Calls made for this review: 0  
Status: diagnostic rescore complete; prior preflight failure unchanged

## Product distinction

The review separates two useful but different properties:

1. **Concept coverage for the reasoning substrate:** Did the system preserve
   the material issue somewhere, so downstream reasoning can use it?
2. **First-introduction coverage for the audit trail:** Did the system preserve
   where that issue first entered the conversation, so the reasoning process
   can be reconstructed accurately?

A later statement may satisfy concept coverage but cannot replace the first
statement in the audit measure. Later strengthening is measured separately.

## Frozen deterministic contract

The source spans are recorded in
`counterpressure-temporal-coverage-contract.json`. For each of Cases 02, 08,
and 11 it declares:

- the original first-introduction span already used by the locked gold set;
- one later source span that strengthens or makes the same concept explicit;
- the conversation source path and hash.

The contract was created after the Case 08 v2 output was observed. Therefore,
rescoring existing artifacts is explicitly diagnostic and cannot promote the
reader or change the failed preflight. The contract is now frozen for any
future run.

No LLM judge, embeddings, keyword classifier, or semantic Python rule is used
by the scorer. Python validates source hashes and exact spans, then performs
deterministic overlap against the predeclared evidence.

## Diagnostic Case 08 rescore

| arm | selected events | first-introduction recall | concept recall | later-strengthening recall | stable concept | exact source |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| five-reader SK3 base | 24 | 0.000 | 0.000 | 0.000 | 0 / 1 | 1.000 |
| broad SK4 pressure | 24 | 0.000 | 0.000 | 0.000 | 0 / 1 | 1.000 |
| counter-pressure v2 | 11 | 0.000 | 0.667 | 0.667 | 0 / 1 | 1.000 |

The v2 reader recovered the later husband-alignment span in runs 1 and 3, but
not run 2. That produces concept and later-strengthening recall of 2/3. It
never recovered the first turn-2 introduction.

## What this resolves

The exact-span gate did hide a real partial improvement: v2 captured the
husband-alignment concept twice through a later, stronger source statement,
where SK3 and broad SK4 captured it zero times under the frozen alternative-
span contract.

However, the measurement limitation was not the whole failure:

- concept recovery was not stable;
- first-introduction recovery remained absent;
- only `material_qualification` was used, so the three-label taxonomy has not
  yet demonstrated useful discrimination.

The formal preflight failure therefore stands. Retrofitting the later quote
into the original gold file would hide the audit failure and still would not
meet the stability requirement.

## Product read

For Lolla's challenge lanes, concept coverage is the more direct adequacy
measure: a later exact span can still provide useful reasoning material. For
the receipt and proof-of-work trail, chronology matters independently: the
future agent should know that household alignment was uncertain in turn 2,
not learn only that it became explicit in turn 4.

These measures should remain side by side. Neither should be collapsed into a
single quality score, and neither proves that the final reasoning was good.

## Recommended next change

Do not add a reader, label, gate, or graph rule. Make one prompt-only temporal
revision to the existing v2 reader:

- preserve the first source span where each material counter-pressure thread
  enters the reasoning;
- also preserve a later span only when it materially strengthens, corrects, or
  changes that thread;
- do not replace the first introduction with a later, cleaner formulation;
- keep the same three semantic labels, one-array schema, exact-source rules,
  eight-item cap, and deterministic validator.

Test that revision locally with fixtures first. If the local contract remains
clean, rerun only the same three-call Case 08 preflight. The prospective gate
should report concept and first-introduction coverage separately. A reasoning-
substrate pass requires stable concept coverage; an audit-trail pass requires
stable first-introduction coverage. Neither pass alone promotes SK4.
