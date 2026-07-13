# Conversation-event architecture A–E conclusion

Status: **material redesign required**  
Date: 2026-07-11

## Plain conclusion

The experiment made Lolla safer and clarified the problem, but this version is
not ready for the live skill.

Breaking the conversation into turn-pair jobs solved the mechanical problems:
all calls returned valid typed data, source IDs resolved exactly, every proposal
was preserved, invalid synthesis failed closed, and no factual state entered the
graph. The failure moved to the semantic fan-in. Three overlapping lenses
created 88–95 events for each fourteen-message conversation. Fresh synthesis
then had too much noisy, repetitive material and repeated the failures we were
trying to remove: fragmented positions, broad threads that missed the specific
unresolved concern, and incorrect source-strength labels.

One generic synthesis repair did not solve this reliably. Under current custody,
only one of three cases compiles; that case still fails the constraint-quality
requirements. Phase D therefore fails and Phase E graph work is deliberately not
run.

## What we learned

- “Small jobs” worked at the edges but do not help if fan-in recreates one large
  overloaded job.
- The three harvesters are complementary lenses, not exclusive routes. Evidence
  missed by one was often found by another.
- Deterministic code should validate identity, shape, references, terminal
  custody, and stop rules. It should not decide which messy candidate matters.
- Global labels such as ownership, accepted versus conditional, thread
  trajectory, and relevance still belong to probabilistic synthesis.
- Source strength is better classified near the original local wording; global
  synthesis repeatedly inflated direct, attributed, possible, and preferred
  claims even after definitions were added.
- A reviewed handoff is a useful target but not exhaustive gold. Exact quote
  recall must be paired with trajectory-level source review.

## Evidence by phase

| phase | result | decisive evidence |
| --- | --- | --- |
| A | pass | 5/5 reviewed cases round-tripped; 45 atomic constraints; zero violations or graph seeds |
| B | narrow fail | 84 calls; 100% operational and typed; transfer cross-lens coverage 30/32 versus frozen 95% gate; 88–95 events per case |
| C | fail after one repair | 18 calls; two thread outputs quarantined; only 1/3 cases compiles under current custody; strict constraint precision 0.308 and recall 0.286 |
| D | fail | zero semantically passing end-to-end cases; no integration authority |
| E | not run | D did not pass; zero graph calls and zero graph seeds |

Total: 102 provider calls, zero automatic retries, approximately $0.13235,
zero graph calls, and no runtime modification.

## Next architecture to test

Do not add another prompt layer to the current fan-in. The next provider-free
design should introduce a bounded semantic consolidation boundary per turn
pair. It may probabilistically merge overlapping observations from the three
lenses, but it must preserve every input and its disposition so deterministic
code never becomes a relevance judge. Claim strength should be classified in
that local context. Global position and thread synthesis should then receive a
small ordered set of normalized turn records rather than 88–95 raw events.

Only reopen provider calls after that representation, its event budget, source
custody, fail-closed compiler, and evaluation contract pass without providers.

## Unknowns kept open

- whether one consolidated per-window reader is better than three lenses plus a
  local semantic consolidator;
- whether a stronger or different model changes the fan-in result;
- whether repeated runs are stable;
- how the approach scales beyond fourteen-message conversations;
- whether a state packet that clears these gates improves the later reasoning
  pressure in a way users value.

The hybrid product thesis remains intact. This experiment rejects one
implementation, not the idea that probabilistic interpretation and deterministic
custody can reinforce each other.
