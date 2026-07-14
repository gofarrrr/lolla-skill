# Designed ambiguous conversation pool v0

Status: active synthetic-source protocol; not real-world product evidence  
Date: 2026-07-10

## Purpose

Create realistic multi-turn development and holdout fixtures when no untouched,
review-safe source conversation exists. The target is not a puzzle with a
hidden correct answer. It is a conversation in which several interpretations,
values, and actions remain defensible as context changes.

## What realistic ambiguity means

Each conversation must contain:

- at least seven user/assistant turn pairs;
- material facts introduced after the assistant has already formed a view;
- at least two moments where the user corrects, resists, or narrows the
  assistant's frame;
- at least one tension between two legitimate values, not a good option and an
  obviously foolish one;
- an assistant that is useful but naturally uneven—capable of clarification,
  overconfidence, repair, and incomplete synthesis without becoming a
  caricature;
- a final state that may be a provisional plan, a conditional plan, or a
  clearly unresolved choice;
- uncertainty that cannot be removed merely by writing a longer answer.

Conversation style should vary. Some messages may be short, emotional, or
fragmentary. The assistant should not turn every reply into a numbered memo.
Characters may contradict earlier emphasis without the fixture explaining the
contradiction for the evaluator.

## What must not be planted

The authoring prompt and generated text must not contain:

- mental-model names, Lolla, graph language, evaluation labels, expected
  pressure, or a gold answer;
- an instruction to make the assistant wrong in a particular way;
- deliberate factual misinformation, invented expert statistics, or an
  obvious trap designed for a later critic;
- a predeclared expected action delta;
- high-stakes medical, legal, child-safety, self-harm, violence, housing-
  emergency, employment-retaliation, political-persuasion, or major personal-
  finance advice.

## Division of labor

The independent source model writes dialogue content from frozen scenario
briefs. It does not select the evaluation case.

Deterministic code owns:

- schema and exact case count;
- role alternation and message count;
- canonical message IDs;
- hashes, ordering, call count, usage, cost, and provider error custody;
- the precomputed candidate ranking.

It also owns the capture envelope. Every runnable derivative must begin with a
machine-checkable `CONVERSATION:` header whose declared user, assistant, and
total marker counts match the frozen source. A missing or inconsistent header
must fail dry-run validation before provider I/O. The original authored source
remains immutable; adding the envelope creates a separately hashed derivative,
not a semantic rewrite.

Codex or a human reviews candidates in frozen order for only:

- declared-domain safety;
- realistic dialogue rather than memo theater;
- actual ambiguity rather than a disguised obvious answer;
- absence of Lolla, graph, model-name, or expected-finding leakage;
- internal intelligibility sufficient to run the pipeline.

The reviewer may reject a case only with a named defect from that list. It may
not choose the case most likely to activate Lolla, produce a mental-model hit,
create an answer delta, or make the graph look useful.

## Evidence boundary

A passing designed pool is still synthetic evidence. It can support plumbing,
failure discovery, comparative evaluation, and a provisional generalization
probe. It cannot establish real-world usefulness, human decision improvement,
population representativeness, or graph value by itself.

## Current development result

Five founder-directed, seven-pair conversations now exist under
`research/designed-ambiguous-pool-v1-2026-07-10/`. They are same-session
development fixtures, not independent holdouts. Deterministic capture-ready
derivatives preserve each semantic source byte-for-byte and add only declared
message counts.

The first two ranked cases were permanently consumed by evaluation-envelope
failures: a missing capture header and a Python 3.9 pipeline import. Both defects
now fail preflight before provider calls. The third case completed the full
pipeline under Python 3.12 but formally failed an inherited core-call subbudget
that was not derived from the pipeline's activation surface.

That completed observation found both signal and noise. Raw V60 artifacts held
plausible hypothesis-threshold and resource-allocation pressure, while several
lane findings repeated the conversation, diagnosed motives, requested
unsupported base rates, or invented responsibilities. Companion verification
also returned malformed truncated JSON. Most importantly, the as-run Step-6
table selected eight V60 cards but presented five names and zero affordance
mechanisms because the renderer did not read the current `mechanism` and
`reason` fields. The zero-call transport repair is complete and tested. No
downstream answer comparison or graph claim is authorized from this corpus.
