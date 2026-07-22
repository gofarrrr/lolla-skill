# Lolla Pressure, Understanding, and Graph Evidence PRD v0

Date: 2026-07-22
Status: decision-ready PRD; provider-free planning complete; execution gates remain separate
Depends on: Constitution v5, PR #381 Decision Trail lineage, the self-contained graph/skill result, the graph audit workbook, PR104, and the minimum viable loop result
Provider calls and cost authorized by this PRD: 0 and `$0.00`
Runtime, graph-policy, private-archive, sidecar-automation, Atlas, and interface changes authorized by this PRD: none

## Product decision in simple terms

Lolla currently has one strong machine capability and two open human questions.

The strong capability is **proof of process**: it can preserve the available
conversation, introduce bounded graph pressure, ask a reasoner to reconsider,
record apply/reject/park dispositions, and leave a detailed receipt.

The first open question is **understanding**: can the system reliably preserve
the semantic table of contents of a long conversation—what changed, what was
adopted, what remained unresolved, what the assistant influenced, and what
value was lost?

The second open question is **graph value**: when the semantic input is fair,
does the current 222-model graph add useful pressure beyond direct recall or a
strong transcript-only reconsideration?

Those are different questions. More graph hops cannot repair a bad semantic
read. A truthful receipt cannot prove that pressure was useful. A good answer
on one synthetic case cannot validate arbitrary conversations.

This PRD therefore makes three compatible decisions:

### A. Pressure now

Keep the current live experimental product centered on:

```text
preserve -> pressure -> reconsider -> disposition -> process receipt
```

Describe it as an inspectable second angle, not a conversation-understanding
engine or quality certificate. Keep Decision Trail, Decision Work, and
Observatory bounded unless their missing semantic supplier is separately
earned.

### B. Understand later

Keep the richer longitudinal-understanding job alive, but resume at the exact
PR104 human-review stop point. A principal human must correct, reject,
simplify, or mark unavailable the three candidate reads. Another AI read, R4,
or a new sidecar does not substitute for that evidence.

### C. Test the conversation-to-graph bridge

Before incoming references, two hops, global search, or new ranking, compare
the current graph under a source-first human-controlled semantic input with the
current live input and named controls. This separates a semantic-supplier miss
from a graph-policy miss.

## Falsifiable product questions

This program keeps three outcomes separate.

### A — current product honesty

> Can a cold maintainer explain the live product as reasoning pressure plus a
> process receipt without inferring reliable longitudinal understanding,
> answer improvement, or action authority?

This is a documentation and boundary result, not a usefulness result.

### B — semantic fidelity

> Can a principal human, reading source first, fairly correct or reject the
> three PR104 candidate reads and identify which semantic fields are useful,
> misleading, too expensive, or unavailable?

If the source is unavailable, the correct result is `unavailable`, not a guess.

### C — graph contribution

> Holding the conversation, human-controlled semantic target, graph release,
> one-hop policy, reasoner contract, and review rubric fixed, does graph-backed
> pressure expose a material source-reviewable angle that direct-only and
> transcript-only controls miss without unacceptable forced association,
> cognitive load, invented facts, or lost value?

If the answer is no, the graph must be allowed to stand down. If the answer is
unclear, do not expand traversal.

## Why this PRD comes after the graph reconstruction

The graph's ownership problem is fixed. A fresh clone now owns:

- all 222 Markdown models;
- reviewed relation curation and 1,358 directed relations;
- source-anchor and compiler-input manifests;
- a deterministic candidate compiler that recreates published bytes;
- one immutable published-substrate reader;
- one named outgoing-one-hop pressure planner;
- exact active/reserve custody;
- a candidate-only complete bounded-path projection.

That work answers “what graph did we run?” It does not answer “did we give the
graph the right semantic problem?” or “did its pressure help a person?” Those
are now the highest-value uncertainties.

## Current inside-out system map

```text
1. Available user/assistant prose
   Authority: source custody
   Strength: exact preservation and disclosed bounded views
   Limit: not system prompts, tool payloads, files, or all host context

2. ConversationContext / ConversationIR
   Authority: provisional semantic interpretation
   Strength: supplies live lanes with shared context
   Limit: above 80,000 characters the initial extraction view is partial;
          longitudinal semantic adequacy is unproven

3. Four pressure jobs
   Authority: provider-authored hypotheses
   Strength: distinct tendency, companion, frame, and structural products
   Limit: separation does not prove independent errors

4. Lane 2 semantic-to-graph bridge
   Current live shape:
     ConversationIR -> lane packet -> LLM fingerprint
     + assistant-turn recall text -> candidate model recall
   Authority: provisional model selection
   Limit: not validated against a stable human semantic target

5. Published knowledge substrate
   Authority: deterministic identity, direction, release, and source custody
   Strength: 222 models, 1,358 relations, exact local publication
   Limit: curated relation is a hypothesis, not relevance or causation

6. Constitutional pressure planner
   Authority: deterministic bounded policy
   Current policy: direct-active only seeds, outgoing authored edges, one hop,
                   antagonist/tension/ally slots, active/reserve custody
   Limit: current policy is not proven better than named controls

7. Reconsidering host reasoner
   Authority: apply / reject / park
   Strength: graph pressure cannot be silently deleted before inspection
   Limit: ordinary live reconsideration is same-context, not independent

8. Revised answer and memo
   Authority: reasoner output
   Limit: change is not proof of improvement

9. Archive, receipt, Decision Trail, Decision Work, Observatory
   Authority: process custody and bounded projections
   Strength: inspectable evidence, health, privacy, cost, missingness
   Limit: no trustworthy arbitrary-run semantic supplier or action authority
```

## Evidence already available

### Strong mechanical evidence

- source, hash, request, response, path, disposition, health, privacy, cost,
  archive, and replay custody;
- exact graph publication and bounded one-hop planner replay;
- graph pressure survival before probabilistic verification;
- complete active apply/reject/park ledgers;
- repository-only open-source setup and validation.

### Narrow positive semantic evidence

The July 12 minimum viable loop preserved two realistic synthetic cases. One
retailer case produced a source-reviewed non-obvious pressure addition. One
library case produced a correct quiet stand-down. The receipt was
reconstructable by a cold reader.

The same evidence also preserved failures: unsupported numerical precision,
modal-force understatement, a failed generic typed-output gate, and no human
usefulness or runtime proof. The controlled mechanism bridge was useful in
that bounded path, but automatic role-record-to-pattern interpretation had
previously failed invariance and protected-mechanism gates.

### Unresolved human evidence

The June Decision Trail specialist program contains three Codex-assisted
candidate reads. PR103 closed the one-case program. PR104 leaves every
principal-human correction field blank and recommends pausing until human
review capacity returns.

The July checked-in-safe Stage 1 is a separate interface-truthfulness option.
It can test labels but cannot fill this semantic gap.

## Required evaluation architecture

Do not replace the live path. Build an offline evidence case around existing
owners and keep all arms source-identical.

```text
complete bounded source case
        |
        +-> source-first principal-human semantic target
        |      changes / adoptions / qualifications / unresolved matters
        |      values / influence / lost value / unavailable fields
        |
        +-> Arm 0: transcript-only strong reconsideration
        |
        +-> Arm 1: current live semantic bridge
        |          -> current direct recall
        |          -> current outgoing-one-hop planner
        |
        +-> Arm 2: human-controlled fact-free mechanism packet
        |          -> current direct recall only
        |
        +-> Arm 3: same human-controlled packet
                   -> current outgoing-one-hop planner
        |
        v
source-first, non-scalar human comparison
```

The arms isolate different causes:

| Comparison | Question isolated |
|---|---|
| Arm 1 vs Arm 3 | Did the current semantic bridge distort or omit the graph problem? |
| Arm 2 vs Arm 3 | Did relationship expansion add anything beyond direct recalled models? |
| Arm 0 vs Arm 3 | Did graph-backed pressure add value beyond strong transcript-only reconsideration? |
| Every arm vs source | Did any output invent facts, erase value, or misrepresent the conversation? |

The human-controlled mechanism packet is an evaluation oracle, not a proposed
runtime truth service. Reuse the existing `ReasoningPatternPacket` fact-free
boundary and reasoning-mechanism ontology where they fit. Version
prospectively rather than rewriting frozen research artifacts. Do not pass raw
role prose, case facts, desired outcomes, topic labels, graph model names, or
source embeddings into controlled routing.

## Evidence vector

Record each dimension independently:

1. **Source fidelity:** were decision state, qualification, adoption,
   influence, values, and unresolved matters represented fairly?
2. **Semantic invariance/sensitivity:** did harmless factual variation preserve
   the same mechanism, and did a material mechanism ablation change it?
3. **Graph custody:** were model IDs, exact paths, direction, policy identity,
   active/reserve state, and omissions preserved?
4. **Distinct useful pressure:** did an arm expose a material angle missing
   from its named control?
5. **Forced association:** did a candidate follow mechanically but lack a fair
   relationship to the case?
6. **Cognitive load:** did pressure add review burden or friction theater?
7. **Disposition quality:** could the reasoner accountably apply, reject, or
   park every active pressure item?
8. **Answer integrity:** were facts, uncertainty, and causation preserved?
9. **Preserved/lost value:** did revision bury momentum, ambition, simplicity,
   stakeholder detail, or useful original advice?
10. **Human correction burden:** how much source-first work was required to
    make the semantic packet fair?
11. **Privacy and cost:** what left the machine, what remained local, and what
    did each arm cost?

No scalar score, winner label, or majority vote may replace this vector.

## Decision logic

| Result | Meaning | Next move |
|---|---|---|
| Arm 3 works, Arm 1 fails | Semantic bridge is the primary defect | Redesign or retain human-supplied bridge; do not expand traversal |
| Arms 2 and 3 are equivalent | One-hop relations add no observed value | Preserve direct-only/no-graph possibility; do not force graph use |
| Arm 3 adds a useful angle without material harm | Current graph can contribute under fair input | Repeat on one diverse case, then test human usefulness |
| Arm 3 misses one named source-supported lens | A graph-policy/content miss may exist | Freeze one alternative experiment only |
| Every graph arm creates forced association or burden | Graph contribution is not earned | Stand down or materially redesign; more hops are contraindicated |
| Human source target cannot be produced fairly | Semantic evidence unavailable | Preserve pause; do not substitute AI agreement |
| Any arm invents high-stakes facts or causation | Answer-integrity failure | Stop the case; preserve first result; no retry under same authorization |

## Graph-opportunity ladder

Only move downward when the previous gate produces evidence.

1. **Complete path custody:** decide whether the existing candidate-only
   complete bounded paths improve receipt transparency without changing active
   pressure.
2. **Fair-input current-policy evaluation:** run the four-arm comparison above.
3. **One alternative traversal:** if a specific miss is established, choose
   exactly one of incoming-reference traversal, direct-reserve expansion, or
   bounded two-edge paths.
4. **Graph-to-V60 handoff:** test offline only if graph-only active models lack
   enough source-backed transaction material.
5. **Live promotion:** separately review runtime, receipt, replay, privacy,
   cost, rollback, and user evidence.

Global community search, a graph database, MCP transport, continuous graph
mutation, and automatic relation extraction do not enter this ladder until a
matching user job and falsifiable failure exist.

## PR104 human-review protocol

The principal reviewer must inspect source before candidate interpretation.
For each of the three existing cases:

1. confirm whether sufficient source is available;
2. if not, mark the semantic question unavailable and identify the missing
   source—do not infer it from the checked-in summary;
3. correct or reject the decision question and vanilla-overlap read;
4. correct or reject the claimed action delta;
5. record preserved and lost value;
6. identify what the candidate read got wrong and preserved well;
7. identify fields to remove or simplify;
8. state a non-scalar human net read;
9. sign/date the review boundary and source set.

The existing PR104 packet remains immutable evidence. A completed review must
be a new prospective artifact that references PR104; it must not overwrite the
blank historical fields.

## User stories

### Person using Lolla now

“Give me another inspectable angle, let the reasoner reject it, and show me
what happened. Do not tell me the process proves the answer is wise.”

### Person returning later

“Help me recover the decision story, but show which meaning was human-corrected,
which was provisional, and which is unavailable.”

### Graph evaluator

“Give the current graph a fair source-first semantic input, compare it with
direct-only and transcript-only controls, and let no-use or stand-down win.”

### Maintainer or AI coder

“Show me the existing owner and required evidence gate before I add a reader,
hop, database, sidecar, queue, or interface.”

## Non-goals

This PRD does not authorize:

- filling PR104 fields without a principal human and source access;
- another Codex specialist pilot or R4/R5 reader;
- provider or embedding calls;
- a new live semantic supplier;
- graph-byte, direction, hop, active/reserve, ranking, or prompt changes;
- runtime receipt or Decision Work automation;
- Atlas, Teacher, Observatory, or frontend work;
- accuracy, cost-saving, usefulness, market, or production claims;
- agent action based on any graph, receipt, sidecar, or review artifact.

## Acceptance criteria for this PRD package

- [x] June and July Decision Trail lineage is explicit and repository-published.
- [x] Pressure-now, understand-later, and graph-bridge work are separate but
      compatible.
- [x] Current live owners and absent connections are named.
- [x] Existing `ReasoningPatternPacket`, ontology, graph reader, and planner are
      reused rather than replaced in the proposed evaluation.
- [x] Controls isolate semantic supply, direct recall, graph expansion, and
      transcript-only reconsideration.
- [x] PR104 remains blank immutable evidence.
- [x] Provider, private-source, graph-policy, runtime, and interface work remain
      unauthorized.
- [x] The implementation sequence is captured in a separate tracer-bullet plan.

## Next authorization

Publishing this PRD authorizes no experiment. The next valid founder/human
action is one of:

1. provide principal-human capacity and appropriate source access for a new
   PR104 completion artifact;
2. authorize provider-free packet/fixture preparation for one exact existing
   checked-in-safe bridge case, without semantic generation;
3. keep both lanes paused and retain pressure-now plus mechanical receipts as
   the working product boundary.

Any provider-backed execution must later freeze exact cases, source and target
hashes, prompts, schemas, models/routes, seeds, call maximum, token caps, USD
ceiling, privacy treatment, retry/fallback prohibition, and stop rules.
