# Live-run interface and passage truthfulness repair

Date: 2026-07-24

Status: repository-published through
[PR #403](https://github.com/gofarrrr/lolla-skill/pull/403)

Source incident: user-operated run `20260724T165556Z_76a156`

Evidence class: **retrospective real skill execution over the simulated
14-message Marcus conversation, followed by provider-free reproduction and
contract tests**. The private run source and archive are not checked into this
repository.

Provider or embedding calls made for this repair: **0**

Repository provider/API cost: **USD 0.00**

Graph sources, relations, direct selection, one-hop traversal, active/reserve
bounds, graph prompts, and apply/reject/park custody changed: **no**

## Question

Can the ordinary skill stop replaying source text in an interactive terminal,
give the optional passage checker every available user-stated fact, and report
an incomplete passage profile consistently to the user and machine callers
without weakening any other partial/failure boundary?

## Plain-language result

The inspected run showed that the core audit and graph path worked, but four
supporting interfaces were not telling the same complete story:

1. the capture helper disabled terminal echo only after startup, while the host
   had no signal telling it when that protection was active;
2. the passage checker received a short model-extracted fact list instead of
   all user turns, so it falsely treated several stated facts as invented;
3. one dropped-thread interpretation was copied into every passage check and
   dominated the profile;
4. the chat said the critique was usable but incomplete, while the receipt was
   generic and `agent_result.json` told callers not to use any part of the run.

The repair makes those boundaries explicit:

- the capture helper emits `PRIVATE_INPUT_READY` only when its input channel is
  safe to use; the skill must wait for it before sending source;
- an interactive capture that cannot disable echo fails before reading source;
- the passage checker receives the complete available user-turn prose plus a
  clearly provisional extraction scaffold;
- the exact passage-check context has character counts and SHA-256 custody;
- global dropped-thread interpretations no longer repeat inside every passage
  check;
- run health records both attempted passage checks and failures;
- the final receipt names the exact missing-check count and no-retry state;
- an otherwise complete standard-mode run with only this optional passage
  profile incomplete remains `status: partial` but becomes available for human
  review;
- any second health issue, unsafe output, missing core artifact, or high-stakes
  mode still produces `do_not_use_run_degraded`;
- a manually maintained live transcript remains `not_checked`, and the receipt
  now says plainly that it does not prove everything shown in the terminal was
  clean.

## What the terminal defect actually was

The earlier helper correctly cleared the terminal's `ECHO` flag while it was
reading. That unit was real, but the host could send the conversation before
the helper reached it:

```text
process starts
  -> Python imports and run-state checks
  -> host sends source too early
  -> terminal may still echo source
  -> helper finally disables echo and reads
```

The new sequence is:

```text
process starts
  -> Python imports and run-state checks
  -> helper disables terminal echo
  -> helper prints PRIVATE_INPUT_READY
  -> host sends source
  -> helper reads, validates, and privately writes source
  -> helper restores terminal state
```

For non-interactive standard input, the helper emits the same readiness line
before reading. Pipes do not have terminal echo, but one protocol is easier for
hosts to follow correctly. A true pseudo-terminal regression test waits for
the readiness line, sends a unique source marker, closes input, and proves that
the marker is in the owner-only source artifact but absent from terminal
output. A separate test proves that failure to disable echo cannot fall back to
an unsafe read.

This prevents the observed race only when the host follows the readiness
protocol. It does not make a manually curated narration a trusted capture of
the whole host console.

## What changed in the passage checker

Before the repair, each passage-level evaluation received:

```text
model-extracted decision summary
+ selected extracted constraints
+ the same global dropped-thread list
```

The extraction for the inspected run omitted several facts that were present
in the conversation, including the executive's tenure, team size, internal
systems, and a prior revenue loss. The checker therefore lacked the evidence
needed to distinguish a user-stated fact from an unsupported assistant claim.
The repeated dropped-thread line also invited the same omission finding in
nearly every passage.

After the repair, each passage-level evaluation receives:

```text
complete available user-turn prose, marked authoritative for user-stated facts
+ provisional extracted decision scaffold, marked potentially incomplete
- global dropped-thread interpretation
```

The persisted `bullshit_profile.context_custody` records:

- whether all available user turns were supplied;
- user-turn count;
- user-context character count and SHA-256;
- complete passage-context character count and SHA-256;
- that dropped threads were not injected into each passage context.

The main four-lane audit still owns dropped-thread and structural-coverage
pressure. Removing the repeated passage-level hint does not delete it from the
audit.

This is a source-supply correction, not proof that the passage judge will now
interpret every fact correctly. No provider-backed rerun was authorized or
performed.

## Health and caller semantics

The optional passage profile can be incomplete while the source capture,
four-lane audit, graph pressure, reconsideration, revised answer, and memo all
exist. Treating that case as fully healthy would hide missing work. Treating it
like a failed core audit would contradict what the user can actually inspect.

The narrow policy is therefore:

| Condition | Status | Caller action |
|---|---|---|
| standard mode; only passage profile partial; core artifacts present; product output clean; live output not unsafe | `partial` | `review_revised_answer` |
| same condition plus untrusted manual live narration | `partial` | `review_revised_answer`; deterministic evaluation is `inspect_first` |
| passage profile partial plus any other material issue | `partial` or worse | `do_not_use_run_degraded` |
| high-stakes mode with passage profile partial | `partial` | `do_not_use_run_degraded` |
| product or live output unsafe | `degraded` | `do_not_use_run_degraded` |

`review_revised_answer` means a human may inspect the revised answer together
with its caveats. It is not permission to act, an answer-quality score, or a
claim that the passage profile is complete.

## Cost and privacy consequence

The optional passage checker now sends all available user-turn prose in each
of at most twelve passage calls. This corrects evidence starvation, but it may
increase provider input tokens and cost, especially for long conversations.
The exact effect is unknown until a separately authorized live run records its
actual usage. Lolla does not silently truncate this context back to the
incomplete extracted fact list to save cost.

This repair does not introduce a new provider or a new category of source data:
the live pressure system already sends conversation-derived material under the
operator's credentials. It does increase repetition of user prose across the
optional checker calls, which operators should understand before using the
skill on sensitive material.

## Provider-free verification

The repair is covered by:

- a true PTY readiness/no-echo test;
- a fail-closed terminal-setup test;
- non-interactive capture and source-replacement guards;
- a complete-user-context and exact-hash custody test;
- a no-global-dropped-thread passage-context test;
- exact partial-receipt and untrusted-live-narration tests;
- standard, multiple-issue, unsafe, and high-stakes caller-policy tests;
- deterministic evaluation-readiness tests;
- existing graph, risk-mode, archive, skill-contract, and passage-budget
  regressions.

Final provider-free verification passed 5,221 repository tests and all 93
subtests. The Constitution Stage 0 register, public handoff validator, packaged
skill validator, Python compilation, Bash syntax, and `git diff --check` also
passed. One existing `datetime.utcnow()` deprecation warning remained.

No live Lolla run, provider call, embedding call, automatic retry, semantic
healing, archive rewrite, or graph execution was used to validate the repair.

## Remaining limits and nonclaims

- The completed `20260724T165556Z_76a156` archive remains immutable; this
  prospective repair does not rewrite its receipt or profile.
- The saved narration from that run remains `not_checked`; it is not upgraded
  to a trusted full-console capture.
- The passage checker may still make semantic mistakes even with complete
  source context.
- The larger passage prompts may cost more; no cost reduction is claimed.
- The graph still uses six direct-active candidates plus bounded one-hop
  antagonist/tension/ally expansion and explicit reserve.
- No incoming, two-hop, multi-hop, community, or global graph behavior is
  added or authorized.
- This repair does not isolate graph contribution, establish answer
  improvement, or prove real-user usefulness.
- The same host reasoner still performs reconsideration; it is not independent
  validation.
