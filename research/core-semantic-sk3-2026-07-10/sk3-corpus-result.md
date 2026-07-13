# SK3 Locked-Corpus Evaluation Result

Date: 2026-07-10  
Corpus: `core-semantic-corpus-v0`  
Cases: 12  
Shadow repeats: 3 per case  
Recorded shadow calls: 144  
Requested model: `google/gemini-3.1-flash-lite`  
Served model: `google/gemini-3.1-flash-lite-20260507`

## Decision

SK3 is a **partial result and does not pass its promotion gate**.

The revised shadow reader found five observations that the prior reader never
found and raised weighted exact-span recall from 0.542 to 0.552. It also raised
the worst-case recall floor from 0.208 to 0.333. Those are useful signals.

The same reader reduced stable observations from 49 to 46, macro span
repeatability from 0.642 to 0.595, and macro labeled repeatability from 0.628
to 0.566. It remains well below every locked v0.1 promotion target. SK4 should
not begin as though SK3 were solved, and graph integration remains blocked.

The authoritative deterministic result is in `corpus-comparison.json` and
`corpus-comparison.md` in this directory.

## Experiment integrity

- All 12 source hashes, gold files, scoring rules, and three-repeat contracts
  remained unchanged.
- The compact path did not change in SK1-SK3, so its 36 locked July 9 artifacts
  were reused rather than paid for again.
- The revised shadow path was run afresh three times on every case.
- All 36 persisted shadow artifacts report four successful provider calls.
- All 895 raw candidates have a terminal ledger record; candidate custody is
  complete in all 36 artifacts.
- No graph input, graph traversal, live routing, receipt, or runtime behavior
  changed.

One operational incident occurred outside the persisted artifacts. During the
first Case 09 attempt, the provider returned headers and then left the joint
response body open. The configured socket timeout did not stop the slow
chunked body. The process was manually interrupted after the delay and resumed
from the missing artifact. Three specialist calls had completed and one joint
call was in flight in that abandoned process. The retry completed all three
Case 09 repeats normally. Therefore 144 successful calls and 693,478 tokens
are recorded, while actual submitted calls and billing may be higher by those
four abandoned-attempt calls.

## Headline comparison

| Measure | July 9 shadow | SK3 shadow | Change |
| --- | ---: | ---: | ---: |
| Weighted exact-span recall | 0.542 | 0.552 | +0.010 |
| Macro exact-span recall | 0.528 | 0.541 | +0.013 |
| Stable observations | 49 / 102 | 46 / 102 | -3 |
| Never recovered | 41 / 102 | 36 / 102 | -5 |
| Macro span repeatability | 0.642 | 0.595 | -0.047 |
| Macro labeled repeatability | 0.628 | 0.566 | -0.062 |
| Lowest case recall | 0.208 | 0.333 | +0.125 |
| Highest case recall | 0.778 | 0.733 | -0.044 |

This is broader but less stable recovery. It is not a quality win merely
because mean recall moved upward.

## Result by semantic dimension

| Dimension | July 9 | SK3 | Stable change | Never-recovered change |
| --- | ---: | ---: | ---: | ---: |
| Assistant positions and revisions | 0.545 | 0.576 | 12 to 10 | 10 to 6 |
| Constraints and options | 0.614 | 0.684 | 11 to 11 | 7 to 4 |
| Dropped or under-carried threads | 0.273 | 0.242 | 2 to 2 | 7 to 8 |
| Operative questions | 0.697 | 0.682 | 13 to 14 | 5 to 6 |
| Uncertainty and evidence boundaries | 0.472 | 0.389 | 4 to 3 | 4 to 6 |
| User corrections and pressure | 0.479 | 0.521 | 7 to 6 | 8 to 6 |

The intended SK3 families did not move together:

- Question-family repeatability stayed almost flat (0.824 to 0.819), while
  validated current-view question events increased from 64 to 132. The reader
  preserved much more of the question trajectory, but gold operative-question
  recall fell slightly. The evaluation currently has no precision measure for
  the extra events, so their usefulness requires source-first review.
- Stance recall rose from 0.545 to 0.576 and four formerly never-recovered
  stances appeared at least once. However, stable stance observations fell
  from 12 to 10, stance span repeatability fell from 0.685 to 0.607, and stance
  label repeatability fell from 0.606 to 0.567.

Some improvement and regression examples are concrete:

- the later due-diligence question in Case 02, middle-path question in Case
  10, and big-picture-plan question in Case 12 became newly recoverable;
- the previously stable current-plan-completeness question in Case 07 became
  never recovered;
- Case 08 alternated between `Am I missing anything` and the later direct-call
  question, showing that exhaustive reading alone did not make current-question
  selection stable;
- Case 11 produced a coherent three-question trajectory in all repeats, while
  instability elsewhere in that case sharply reduced its overall repeatability.

## What the candidate ledger taught us

The structural ledger works. Across 895 candidates it preserved:

- 857 selected candidates;
- 29 candidates not supported by their claimed source;
- 2 mechanically invalid candidates;
- 3 reader-set-aside candidates;
- 4 ambiguous candidates.

However, the semantic disposition contract did not work reliably. The model
omitted `candidate_disposition` on 516 of 895 proposals. Deterministic backward
compatibility then selected 487 validated proposals by default. The ledger is
therefore reliable as a custody and rejection record, but this run does not
validate it as a complete record of hypotheses the model considered and set
aside.

Question relation references worked materially better than stance references:

| Family | Resolved | Unresolved | Not declared |
| --- | ---: | ---: | ---: |
| Question events | 80 | 15 | 37 |
| Assistant stance events | 1 | 23 | 162 |

Many unresolved stance references pointed to real source text that the same
reader did not emit as a stance candidate. This exposes a contract mismatch:
an exact source quote can exist without an event to which the deterministic
resolver can attach it. Python correctly reported the mismatch and did not
guess a target.

No question or stance trajectory event declared relation ambiguity. This does
not prove that the conversations were unambiguous; it shows that the current
prompt did not elicit the uncertainty representation we intended.

## What we can and cannot conclude

We can conclude that:

- exhaustive question reading preserves more stages of a conversation;
- exact evidence validation, terminal candidate custody, and current-view
  reconstruction work across the corpus;
- broader recovery is possible without deterministic semantic rules;
- the stance-linking and semantic-disposition prompt contracts are not being
  followed reliably;
- the current version is too unstable for graph or live-path promotion.

We cannot conclude that:

- the extra question events are all useful or correct;
- higher candidate volume means better reasoning;
- the ledger contains hypotheses the model considered but never returned;
- agreement between three runs proves semantic truth;
- this pre-audit representation improves the final Lolla challenge;
- the result isolates SK3 causally, because SK1-SK3 and their prompt changes
  were evaluated together against the July 9 baseline.

## Unknown unknowns made visible

1. The provisional gold set measures required recall but not precision. A
   reader can emit more valid source spans without representing the decision
   more accurately.
2. One model repeated three times may share the same blind spots. Stability can
   be consistent error.
3. Exact-span scoring intentionally under-credits faithful synthesis. The
   provenance repair helps inspect synthesis but does not solve its evaluation.
4. Adding required metadata can change which semantic spans the model selects;
   metadata is not behaviorally free.
5. The current joint prompt asks one model response to cover four semantic
   families. Cross-family prompt interference is plausible but not yet proven.
6. The response-body hang is not represented automatically in the run ledger,
   so the operational receipt still has a failure-observability gap.
7. Better pre-audit conversation understanding may still fail to improve the
   graph-selected mental models or the final reconsideration.

## Next bounded step

Do not add SK4 fields yet. Run one small ablation/repair experiment focused on
the observed SK3 failures:

1. retain exhaustive question extraction and exact relation evidence;
2. simplify stance linking so a later stance references an earlier candidate
   from the same returned list rather than independently quoting an event the
   reader may not emit;
3. stop presenting a missing disposition as if semantic selection were fully
   observed; measure disposition-contract compliance explicitly;
4. add an evaluation-only wall-clock guard and abandoned-attempt record;
5. test the change on the three most diagnostic cases (02, 08, and 11) with
   the same three-repeat contract;
6. promote the repair to the full locked corpus only if stance stability
   improves without losing operative-question coverage.

This is a bounded prompt-and-harness experiment. It does not authorize a new
agent architecture, deterministic semantic gates, graph integration, or live
runtime changes.

## Bounded repair implementation status — 2026-07-10

The local repair described above is complete; no additional paid call has been
made yet.

The supplied essay *Your LLM Pipeline Is Slow Because Your Agents Do Too Much*
made one missing design problem explicit: the SK3 joint reader was still a
monolithic semantic call. It had to extract four families, follow four label
contracts, preserve exact evidence, express ambiguity, and add ledger
dispositions in one response. The corpus showed the same failure pattern as
the essay's general claim: more output did not produce more stable first-pass
semantics.

The repair therefore:

- moves question trajectory into one focused one-array call;
- leaves the related pressure/option/evidence fields in a narrower
  decision-context call for this ablation;
- simplifies stance references to earlier array indices;
- treats explicit disposition as optional observability rather than pretending
  the ledger sees unreturned alternatives;
- records and retries wall-clock/provider failures in the evaluation harness.

This adds one focused model call to the experimental path, taking it from four
to five calls per shadow run. The calls remain sequential for the ablation.
The article's parallel-execution recommendation is deliberately deferred until
semantic quality is established.

Local verification completed with 3,860 non-network tests passing and one
pre-existing skip. The next paid action is limited to three repeats of Cases
02, 08, and 11.

## Repair preflight update

The repair experiment began with Case 02 and stopped there because the stance
gate failed. Question repeatability improved to 1.000, but stance
repeatability fell and exact-span recall dropped to 0.208. Cases 08 and 11 were
not run.

The complete result, paid-call accounting, preserved invalid preflight, and
post-stop schema repair are documented in
`research/core-semantic-sk3-repair-2026-07-10/case-02-preflight-result.md`.

The current local suite contains 3,862 passing non-network tests and one
pre-existing skip. One further Case 02-only run would test the explicit item
schemas; it requires a new paid-call approval.

The approved explicit-schema Case 02 rerun is now complete. Recall improved to
0.583 and stance span repeatability to 0.602, with complete stance, option, and
evidence source adherence. Question-family repeatability fell to 0.208 because
the model selected different sets of genuine intermediate questions and did
not consistently assign the same current stage. Cases 08 and 11 remain paused.
See `research/core-semantic-sk3-repair-2026-07-10/case-02-preflight-result.md`.

The repair was then run unchanged on Cases 08 and 11. Across the three
diagnostic cases, weighted recall improved from 0.413 to 0.547 and macro span
repeatability from 0.450 to 0.628. Operative-question recall improved to 0.889.
User-pressure recovery remained 0.111 and dropped-thread recovery remained
zero, so the remaining nine cases were not run. The full decision is in
`research/core-semantic-sk3-repair-2026-07-10/three-case-repair-result.md`.
