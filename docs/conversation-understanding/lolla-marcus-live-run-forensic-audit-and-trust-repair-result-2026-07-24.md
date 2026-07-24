# Marcus live-run forensic audit and trust repair

Date: 2026-07-24

Status: implemented and verified locally; not yet repository-published

Scope: retrospective inspection of completed run
`20260724T150313Z_defca7`, followed by provider-free runtime truthfulness and
privacy repairs

Evidence class: **real skill execution over a simulated 14-message strategic
conversation**. The run is useful operating evidence. It is not genuine
real-user usefulness evidence.

Provider or embedding calls made for this audit and repair: **0**

Graph sources, relations, traversal policy, prompts, model route, and answer
selection changed: **no**

## Plain-language result

Most of the intended Lolla path worked:

- all 14 user/assistant messages were preserved;
- the initial decision read used the complete conversation;
- the four pressure lanes ran;
- the mental-model graph supplied both directly selected models and connected
  models;
- the same host reasoner received a combined pressure table before rewriting
  its answer;
- apply, reject, and park records were completed;
- the revised answer, memo, Observatory, archive, usage, and cost artifacts
  were produced.

But the run was not as healthy as its receipt claimed.

One provider-backed pressure check ended in an HTTP 429 provider error and
returned no usable result. The raw call record preserved that fact, but run
health still said `healthy`, emitted no warning, and the final receipt presented
the run as complete. This was a process-truthfulness defect: the evidence
existed, but the product summary hid its consequence.

Two local privacy defects were also confirmed. The interactive terminal echoed
the supplied conversation while it was being captured, and the durable archive
used ordinary `0755` directory and `0644` file modes. The curated live
transcript did not claim that the visible console was clean—it correctly
reported `not_checked`—but it also did not represent everything the user
actually saw.

The repairs make those limitations visible and private:

1. an attempted provider call without a usable result now makes the run
   `partial`, names the affected stage/check, and appears in the final receipt;
2. interactive conversation capture disables terminal echo while reading;
3. fresh run artifacts and successful or failed archives are owner-only;
4. the already completed Marcus run was remediated in place to owner-only
   permissions without changing any artifact content or hash.

## Direct answers to the forensic questions

| Question | Finding |
|---|---|
| Did anything work? | Yes. Source custody, full-view extraction, the main pressure pipeline, graph selection, same-context reconsideration, disposition ledgers, memo, archive, and Observatory all completed. |
| Was there a silent failure? | Yes. One recorded `pass2` call for `availability-misweighing-tendency` ended as `provider_finish_error` with provider code `429`. It was not retried, which was correct, but it was not promoted into run health or the final receipt. |
| Was the conversation passed properly? | Mechanically, yes for this run. The authoritative and processing-view hashes were identical, both lengths were 26,182 characters, all 7 user and 7 assistant messages were counted, and zero turns were omitted. This proves custody and complete initial-view coverage, not semantic understanding. |
| Did the graph run? | Yes. The graph-survival artifact was `active`: 6 direct models survived the direct cap and 3 connected models survived one-hop expansion. The remaining candidates stayed in reserve rather than disappearing. |
| Did graph pressure reach the agent? | Yes, through the private Step 6 pressure table read by the same host reasoner before it wrote the revised answer. The completed ledgers prove that each required item received a disposition. They do not prove deep cognitive engagement or graph causation. |
| Was the reconsideration independent? | No. It stayed in the original host conversation. Optional clean-context pressure checks were default-off. This is inspectable self-reconsideration, not external validation. |
| Did the graph improve the answer? | The final answer materially corrected unsupported certainty and opened a reversible third option. The run cannot establish that the graph uniquely caused that change because lanes, graph pressure, private enrichments, and same-context reflection arrived together without a control. |

## What happened under the hood

### 1. Source custody was complete

The capture event recorded:

- 14 message blocks;
- 7 user messages and 7 assistant responses;
- 26,304 source bytes;
- one authoritative SHA-256 identity.

Extraction then parsed 26,182 characters of conversation prose. Its declared
and actual counts matched. The separately named processing view reported:

- `status: full`;
- `processing_strategy: full`;
- the same SHA-256 as the authoritative conversation;
- 26,182 authoritative and processing characters;
- zero omitted turns.

The byte count and character count differ because they measure encoded bytes
and Unicode characters, respectively. They are not evidence of truncation.

This run therefore did not encounter Lolla's above-80,000-character partial
initial-extraction policy.

### 2. Provider-backed interpretation mostly completed

The archived audit summary preserved 18 named boundary calls associated with
the pressure audit:

- 17 ended `ok`;
- 1 `pass2` call ended `provider_finish_error`;
- the affected tendency was `availability-misweighing-tendency`;
- the served provider reported a rate-limit error with public code `429`.

The broader usage ledger recorded additional calls used by extraction,
query-expansion/embedding, and other audit components. It estimated total run
cost at USD 0.053321; the final user receipt rounded this to USD 0.05.

No automatic retry occurred. That behavior was correct. The defect was that
the missing result was treated as if it had no health consequence.

### 3. The graph was actually active

The relevant graph-survival counts were:

```text
222-model curated source corpus
        |
        +-- direct recall: 60 candidates
        |       +-- 6 active
        |       `-- 54 retained in reserve
        |
        `-- one-hop relationship expansion: 20 candidate paths
                +-- 3 active
                `-- 17 retained in reserve

9 active graph-pressure items reached the Step 6 custody boundary
```

The six direct active models were:

- representativeness heuristic;
- inversion;
- empathy;
- psychological safety;
- user-centered design;
- aleatory/epistemic uncertainty recognition.

The three connected one-hop models were:

- confirmation bias;
- commitment bias;
- base rates.

The selection contract explicitly recorded:

- direct cap: 6;
- graph slots: antagonist, tension, and ally;
- one exact connected identity per slot;
- no probabilistic applicability gate;
- no candidate deletion.

This answers the recurring “only six models” confusion. Six is the per-run
direct context cap, not the size of the knowledge base and not the total number
of models the graph can expose. This run started from 60 direct candidates,
retained 54 in reserve, added 20 one-hop candidates, and actively delivered 9
graph items.

It also shows the current limit. Lolla did **not** perform arbitrary multi-hop
or global graph search, community detection, or GraphRAG-style synthesis over
the 222 files. It used a deliberately bounded one-hop pressure graph.

### 4. Graph and lane material reached the same host reasoner

The combined pre-Step-6 table reported:

- `status: ready`;
- 18 source items;
- private-context delivery enabled;
- no live card-generation call;
- no code-owned answer selection;
- every ledger item visible or resolvable.

The execution transcript shows the host reading this table after the pipeline
completed and before writing the revised answer. The resulting ledgers
recorded:

- combined private table: 16 `used`, 1 `rejected`, 1
  `private_guardrail`;
- graph-survival portfolio: 6 `apply`, 2 `park`, 1 `reject`.

These records are useful custody. They prove that the host did not silently
omit required items from the disposition record. They do not prove that the
host understood each item correctly, assigned the right disposition, or would
have revised the answer differently without the graph.

### 5. The answer changed in a defensible direction

The original answer forced the decision into “partner or employee,” used an
invented USD 11M-versus-USD 5M comparison, predicted departure and team loss
too confidently, treated vesting as a near-complete answer to permanent-equity
risk, and inferred Marcus's motives without direct evidence.

The reconsidered answer:

- withdrew the forced binary;
- withdrew unsupported numeric precision and behavioral certainty;
- separated agency economics, governance, and platform ownership;
- changed Friday's dinner from a closing event into discovery plus explicit
  intent;
- introduced a time-bounded diligence period;
- used ranges, evidence gates, legal/IP review, and staged commitments;
- preserved succession and concentration-risk work even if Marcus stays.

That is a meaningful output delta. The correct claim is “the completed Lolla
process produced a more qualified and reversible answer,” not “the graph made
the answer better.”

## Defects and repairs

### A. Hidden provider-call loss

Before the repair:

```text
attempted pass2 call -> provider error 429 -> raw call record retained
                                           -> run_health: healthy
                                           -> final receipt: no warning
```

After the repair:

```text
attempted non-ok provider call
  -> provider_call_terminal_loss
  -> run_health: partial
  -> failed-call count, stage, tendency, status, provider, model, and safe
     error-type/code custody
  -> explicit audit warning
  -> final receipt names the missing check and says it was not retried
```

Provider-boundary privacy health remains a separate axis. A provider can obey
the no-reasoning-details boundary while a call still fails to produce a usable
semantic result; “privacy boundary clean” must not mean “execution complete.”

### B. Conversation echo in an interactive terminal

The capture helper already avoided printing source text and used private
standard input. The real execution nevertheless supplied the source through an
interactive terminal whose echo flag was still enabled, so the terminal
replayed the entire conversation in its tool output.

The helper now temporarily clears the terminal's `ECHO` flag while reading and
restores the original terminal state afterward. Non-interactive standard input
is unchanged. The user may still see that a runtime tool was invoked, but the
source should not be replayed by the terminal.

### C. Local archive permissions

The completed run originally had:

- archive, case, and run directories: `0755`;
- archived files, including conversation prose: `0644`.

On a multi-user machine, those modes permit other local users to traverse the
directories and read the files.

Fresh setup now establishes `umask 077` and persists it in the run environment.
Extraction and pipeline outputs use private atomic writes. Successful archives
recursively enforce `0700` directories and `0600` files. Failed-extraction
archive roots, directories, and files use the same policy.

The exact completed Marcus archive and matching `/tmp` files were remediated
after inspection:

- archive root: `0700`;
- case directory: `0700`;
- run directory: `0700`;
- case manifest and every run file: `0600`.

Only permissions changed. File content and SHA-256 identity did not.

## Verification

The changes were developed against failures that reproduced:

- a provider error hidden beneath `healthy`;
- a generic final receipt that did not name the missing provider-backed check;
- `0644` processing and result artifacts;
- `0755`/`0644` completed archive custody;
- permissive failed-extraction archive parents;
- interactive capture without a terminal no-echo guard.

Final provider-free verification passed:

- 148 focused runtime, receipt, capture, permission, archive, and skill-contract
  tests;
- the 94-test Stage 0/critical-path set;
- 5,212 repository tests and all 93 subtests;
- the Constitution Stage 0 register and public-handoff validators;
- Python compilation, Bash syntax, and `git diff --check`.

One pre-existing `datetime.utcnow()` deprecation warning remained.

No provider call, embedding call, model retry, graph run, or semantic
experiment was performed for these repairs.

## What remains unknown

- Whether the extraction represented the conversation's meaning correctly.
- Whether the nine active graph models were the most useful pressure for this
  case.
- Whether a two-hop, multi-hop, or global view would add useful novelty or only
  more noise.
- Whether the host's apply/reject/park judgments were sound.
- Whether the final answer would be judged better by the principal human.
- How much of the output delta came from direct lanes, graph connections,
  private enrichment, or ordinary same-context reconsideration.
- Whether the revised answer improves a real decision or outcome.

The next semantic question is therefore not “should we add more graph hops?”
It is “can we isolate what the current one-hop graph contributes, beyond
ordinary run-to-run variation and the other pressure lanes?” Existing Product
Delta experiments remain `not_evaluable`, so this repair does not authorize or
answer that question.

## Boundaries and nonclaims

- This work repairs process truthfulness and local privacy.
- It does not change the 222 Markdown mental models or 1,358 authored
  relations.
- It does not change direct selection, one-hop traversal, active/reserve caps,
  prompts, model choice, routing, or no-retry policy.
- It does not turn the mental-model graph into a factual knowledge graph or
  Microsoft-style GraphRAG system.
- It does not establish graph causation, answer accuracy, cost advantage,
  human usefulness, or production readiness.
- It does not make the same-context host an independent reviewer.
