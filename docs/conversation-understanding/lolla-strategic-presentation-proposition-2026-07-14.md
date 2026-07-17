# Lolla Strategic Presentation Proposition

Status: founder-approved presentation direction; implemented locally for
pre-merge review; not a runtime contract or product-proof claim

Date: 2026-07-14

Scope: product positioning, README information architecture,
`HOW_IT_WORKS.md` information architecture, intellectual lineage, model
strategy, claim discipline, and documentation migration

Read this proposal under the binding
[Lolla Product Constitution v5](lolla-product-constitution-v5.md), the
[founder product vision](lolla-founder-product-vision-2026-07-14.md), the
[current-state constitutional audit](lolla-current-state-constitutional-audit-2026-07-13.md),
and the
[current roadmap](../../plans/lolla-post-v1-constitution-aligned-roadmap-2026-07-13.md).
It records the adopted presentation direction; it does not replace those
contracts or authorize stronger product claims than the evidence supports.

## Executive Recommendation

Lolla should present itself with one identity:

> **Lolla is a reasoning-pressure layer for serious AI conversations.**

Its human promise is:

> **Slow down the moment a fluent AI answer starts to feel like certainty.**

Its product contract is:

> Preserve the conversation, introduce traceable pressure from outside the
> answer's current reasoning trajectory, ask the reasoner to reconsider, and
> leave an inspectable record for the human who still owns the decision.

Its technical principle is:

```text
LLMs interpret messy conversational meaning.
Deterministic code owns identity, custody, bounds, replay, graph recall,
budgets, and ledgers.
The graph introduces pressure; it does not certify relevance.
The reasoner may apply, reject, or park that pressure.
The record proves what process occurred, not that the result is wise.
The human owns the decision and its consequences.
```

This hierarchy gives Lolla an understandable front door without flattening the
substance of the project. “Reasoning audit,” “Decision Trail,” “Decision Work,”
“Product Delta,” “Observatory,” “Mental Model Teacher,” “external System 2,”
and “knowledge-first engine” can all remain useful terms, but none should
compete with the primary identity. They are descriptors, artifacts, research
programs, interfaces, metaphors, or future surfaces.

The README should explain the user problem and the product in minutes. The
technical story should then point to `HOW_IT_WORKS.md`, which should explain
the authority boundary and the complete flow. Neither document should be a
development ledger.

## What This Proposal Reconciles

The repository contains 1,566 Markdown files. That is evidence of substantial
work, but it is not one coherent presentation surface. A repository-wide
inventory, heading and phrase review, and detailed reading of the current
entrypoints, constitution, current-state audit, roadmap, latest R4 evidence,
modular how-it-works documents, product plans, board briefs, evaluation notes,
and founder vision reveal several true but competing descriptions:

- a system for “being less wrong”;
- an external System 2 guardrail;
- a knowledge-first reasoning-about-reasoning engine;
- a reasoning-audit harness;
- a reasoning-pressure system;
- an accountable-reconsideration process;
- a Decision Trail or reasoning-work receipt;
- a Decision Work sidecar;
- an Observatory for inspecting runs;
- a future Mental Model Teacher;
- a portable Markdown memory layer for future agents.

These descriptions are not mutually exclusive. The presentation problem is
that they currently appear at the same level.

The root README is 1,456 lines and `HOW_IT_WORKS.md` is 823 lines. Both begin
with useful explanations and then accumulate implementation chronology,
evaluation programs, PR-era terminology, current experiment status, and large
documentation indexes. A cold reader cannot tell which passages define the
product, which report historical work, which describe research-only paths,
and which are future plans.

The solution is not another synonym. It is a messaging hierarchy.

## The Messaging Hierarchy

| Level | Recommended language | What it does |
|---|---|---|
| Human tension | “Fluency can feel like certainty before the reasoning has earned it.” | Names the moment the user recognizes. |
| Human promise | “Slow down that moment.” | States the desired experience without promising paralysis or doubt for its own sake. |
| Product category | “A reasoning-pressure layer for serious AI conversations.” | Names what Lolla is. |
| Product action | “Preserve, pressure, reconsider, record.” | Gives the shortest accurate mechanism. |
| User outcome | “Another inspectable angle before you decide.” | Describes value without guaranteeing a better answer. |
| Shareable artifact | “A revised position and its decision trail.” | Names what travels beyond the chat. |
| Technical principle | “Probabilistic interpretation inside deterministic custody.” | Explains the hybrid architecture. |
| Defensible asset | “A purpose-compiled mental-model substrate and provenance-bearing relationship graph.” | Explains why this is more than a critique prompt. |
| Evidence boundary | “The receipt proves the process, not the wisdom of the decision.” | Prevents trust inflation. |

This stack should remain stable even if the runtime becomes a standalone
application, the model mix changes, or the Teacher becomes a real surface.

## The Primary User And Wedge

The first presentation should not address everyone who uses AI.

The primary user is an AI power user, founder, operator, advisor, researcher,
or small team doing consequential strategic work through a multi-turn
conversation with Claude Code, Codex, or another capable agent. They already
have a plausible answer. Their problem is not blank-page generation. Their
problem is knowing when that plausible answer has become too settled.

“Serious” describes the user's level of consequence and attention. It does not
mean Lolla is approved to replace medical, legal, financial, safety, or other
qualified professional judgment. The current system is not authorized for
automatic or high-stakes reliance.

The primary use moment is:

```text
I have had a long, useful conversation with an AI.
The answer is coherent enough that I may act on it.
I know the situation is ambiguous and incomplete.
Before I commit, I want a different, traceable pressure on the reasoning—
without losing the conversation that produced it.
```

Secondary audiences can follow later:

- teams that need to share the path behind an AI-assisted recommendation;
- agent builders who need inspectable pressure and custody around decisions;
- reviewers and evaluation teams studying what changed after reconsideration;
- learners exploring how mental models interact, oppose, and constrain one
  another.

The initial market story should be written for the first audience. Trying to
sell the skill, team decision trail, audit infrastructure, evaluation harness,
Observatory, and Teacher at once recreates the current confusion.

## Why “Reasoning Pressure” Is The Best Category

Several positioning options are available. None is perfect.

| Option | Strength | Risk | Recommended role |
|---|---|---|---|
| AI reasoning audit | Familiar and serious | Can imply a verdict, certification, or proven quality test | Use as a secondary descriptor |
| External System 2 | Memorable | Treats a human-cognition metaphor as a literal claim about LLMs; suggests a complete deliberative faculty | Use only as a clearly labeled analogy |
| Mental-model engine | Makes the substrate visible | Starts with the machinery rather than the user's problem; sounds like a model-name recommender | Use in the technical explanation |
| Decision Trail | Tangible and team-friendly | Describes the artifact but not the externally supplied pressure that creates the delta | Use for the shareable record |
| AI decision review | Easy to understand | Suggests Lolla reviews the correctness of a decision and may invite high-stakes reliance | Avoid as the primary category |
| Reasoning-pressure layer | Constitutionally accurate and differentiated | Needs one sentence of explanation | Use as the primary category |

“Pressure” matters because Lolla is not supposed to agree, rank, certify, or
force. It introduces a bounded possibility from the curated graph rather than
requiring the original trajectory to generate every challenge itself. The
reasoner is allowed to reject or park it. The human can inspect what happened.

“External” here is relative to the answer's current trajectory. It does not
mean epistemically independent: the source corpus, curation, graph, and
reconsidering model can share assumptions or blind spots. Provenance makes the
pressure inspectable; it does not make it true.

The word also makes room for a quiet outcome. Sometimes the pressure changes a
decision threshold, sequence, scope, test, or stop rule. Sometimes it is
rejected because its conditions do not hold. Sometimes it is preserved for a
future state. The product should not manufacture visible disagreement merely
to prove that it ran.

## The Core Story

### The problem

Experts often sound trustworthy because they remove ambiguity. LLMs can do
this at extraordinary speed. A long conversation may contain uncertainty,
changed assumptions, constraints introduced in the middle, abandoned options,
and competing values. The final answer can smooth those tensions into one
confident narrative.

The danger is not that every fluent answer is wrong. Many are useful. The
danger is premature closure: fluency changes how settled the answer feels
before the underlying uncertainty has changed.

Asking the same model to “critique itself” is useful, but it is not a complete
answer. A fresh prompt or fresh model can still inherit the same frame, broad
training priors, and conversational trajectory. Lolla adds a deliberately
different failure surface: bounded, source-shaped pressure from a compiled
mental-model substrate, with provenance and a disposition ledger.

### The product move

Lolla does four things:

1. **Preserve** the complete available conversation as the authoritative
   source, while declaring every compact processing view and omission.
2. **Interpret** the messy meaning with bounded LLM jobs where semantic
   judgment is necessary.
3. **Pressure** the reasoning with deterministic graph recall and curated
   model material whose identity and provenance can be inspected.
4. **Reconsider and record** whether each pressure was applied, rejected, or
   parked, then leave a revised position and process record.

The best short form is:

```text
preserve → pressure → reconsider → record
```

The more technically exact form is:

```text
complete conversation
        ↓
bounded LLM interpretations of messy meaning
        ↓
deterministic identity, graph recall, bounds, and provenance
        ↓
pressure portfolio with no probabilistic silent deletion
        ↓
reasoner applies, rejects, or parks each pressure
        ↓
revised position + Markdown record + process receipt
        ↓
human decision
```

### The value

Lolla's value is not “more thoughts” or “more caution.” It is useful friction:

- an unknown made explicit;
- a hidden constraint made operational;
- a trade-off restored after it disappeared from the final answer;
- a neglected stakeholder or dependency brought back into view;
- a threshold, gate, sequence, scope, reversal condition, or stop rule made
  visible;
- a pressure rejected for a stated reason rather than silently ignored;
- a conversation converted into a record that a later human or agent can
  inspect without replaying the entire chat history.

The product should never promise that all of those occur in every run.

## What Makes Lolla More Than A Prompt

The README should make the depth visible, but only after the reader understands
the product.

One run sits on top of several distinct bodies of work:

1. **A source-shaped mental-model corpus**

   The founding program drew on roughly 200 books and related primary-source
   study to produce 222 canonical model articles. LLMs assisted the research
   and synthesis process; reviewed curation and compiled artifacts make the
   material stable enough to inspect and reuse. This should not be described
   as either spontaneous runtime generation or purely human-authored text.

2. **A relationship and intervention graph**

   The current graph contains 222 canonical model identities, 25
   Munger-inspired cognitive tendencies, 1,358 model-to-model relationship
   edges, 241 tendency-antidote bindings, and 1,742 total graph edges when
   tendency links are included. Relations distinguish allies, antagonists,
   and structured tensions. They do more than say that two model names are
   semantically similar.

3. **Purpose-compiled model affordances**

   The current V60 research artifact contains 222 model records, 306
   source-backed affordances, and 697 absence records. The absence records are
   especially important: they preserve where a tempting use is not supported.
   V60 remains `draft_review_only`; its existence is evidence of substrate
   work, not proof of runtime semantic correctness.

4. **A hybrid runtime**

   LLMs do the jobs that require interpretation. Deterministic machinery owns
   stable IDs, hashes, source custody, schema validation, graph traversal,
   processing bounds, call and cost envelopes, replay, and disposition
   ledgers. “Deterministic” describes execution and custody, not semantic
   truth.

5. **An evaluation laboratory**

   The repository contains frozen fixtures, matched controls, protected
   source-first targets, exact request and response custody, cost ledgers, and
   non-scalar review vectors. This is how the project learns where the
   architecture fails. It should be summarized as evidence discipline, not
   poured into the public README as PR chronology.

6. **Portable process artifacts**

   Current runs preserve source and audit artifacts and can render Markdown
   memos. The broader cold-reader agent-memory package is a product direction,
   not a completed claim. The principle is already stable: important reasoning
   should survive outside chat history in a readable, inspectable format.

These are the proof points behind the phrase “reasoning-pressure layer.” They
are not six separate products.

## Recommended README Architecture

### Reader contract

A cold reader should be able to answer these questions within three minutes:

1. What uncomfortable moment is Lolla built for?
2. What does it do to an AI conversation?
3. Why is this different from “critique your answer”?
4. What do I receive?
5. What is real today, and what is still experimental?
6. How do I try it?

The README should target roughly 250–400 lines, not because shortness is a
virtue by itself, but because its job is orientation and activation. Detailed
runtime and research material already has better homes.

### Recommended section order

1. **Hero: one category, one human promise**
2. **The moment Lolla is for**
3. **What happens in one run**
4. **What the user receives**
5. **Why this is not just self-critique or another prompt**
6. **The hybrid architecture in one diagram**
7. **What sits behind one run**
8. **A labeled example or short demo**
9. **Install and run**
10. **Current status and non-claims**
11. **Privacy, providers, and cost summary**
12. **Intellectual lineage and acknowledgments**
13. **Where to go deeper**
14. **Contributing and license**

Install should not come before the reader understands what the product does,
but neither should it be buried after hundreds of lines of experiment history.

### Proposed first screen

The exact copy can change, but the first screen should read approximately like
this:

> # Lolla
>
> **A reasoning-pressure layer for serious AI conversations.**
>
> Lolla slows down the moment a fluent AI answer starts to feel like
> certainty.
>
> Run it after a consequential conversation with Claude Code, Codex, or
> another capable agent. Lolla preserves the conversation, uses language
> models where its messy meaning must be interpreted, recalls traceable
> challenge pressure from a curated mental-model graph, and asks the reasoner
> to apply, reject, or park that pressure. It leaves a revised position and an
> inspectable record of what happened.
>
> Lolla does not certify that the answer is correct or the decision is wise.
> It makes another angle visible before the human decides.
>
> ```text
> conversation → external pressure → reconsideration → decision trail
> ```

This copy leads with the experience, explains the mechanism, and includes the
trust boundary before the reader can mistake “audit” for certification.

### What the README should show as output

Use plain user-facing objects rather than internal artifact names:

- **Revised position** — what the reasoner now recommends or leaves open.
- **What changed** — action, threshold, sequence, scope, gate, assumption, or
  stop rule, when a material change occurred.
- **Pressure dispositions** — what was applied, rejected, or parked and why.
- **Decision trail** — the important path through the conversation, including
  uncertainty and dropped or reopened considerations.
- **Process receipt** — what was captured, processed, omitted, called,
  preserved, or missing.
- **Portable Markdown** — a readable record that can outlive the chat and
  support later review.

The README should not imply that every current run already produces the full
future Decision Trail or cold-reader memory object. It should label the present
artifact set and the intended product direction separately.

### What the README should say about current status

Use a compact, visible status box:

> Lolla is an experimental skill and research system. The live pipeline,
> source custody, graph-survival path, pressure ledger, archives, and local
> evaluation machinery exist. The project has not established that it
> reliably improves decisions, that its graph adds unique value over strong
> fresh-model reconsideration, or that a clean receipt indicates a wise
> answer. Current work is testing semantic restraint and false positives on
> matched holdouts.

The latest R4 matched evidence supports that caution. Both arms recovered
genuine residual gaps, while the repaired residual reader still failed both
quiet controls. The correct public conclusion is that the machinery is real
and the reliability claim remains open.

### What should leave the README

- the long Product Delta execution lane and its PR chronology;
- R1–R5 implementation narratives;
- current experiment authorizations and consumed-call details;
- full artifact indexes;
- detailed environment-variable tables;
- full cost-accounting instructions;
- version-by-version curation history;
- a long unclassified list of every repository consulted;
- unsupported or orphaned research statistics;
- future Teacher and Observatory details presented as if they were the current
  core product.

Nothing needs to be deleted as evidence. It needs to be moved behind stable
links.

## Recommended `HOW_IT_WORKS.md` Architecture

### Reader contract

`HOW_IT_WORKS.md` should answer a different set of questions:

1. Which parts of the system are probabilistic, deterministic, or human-owned?
2. How does the complete conversation remain authoritative?
3. How is the mental-model substrate produced and recalled?
4. What happens from capture through reconsideration and archival?
5. What does the graph prove, and what does it not prove?
6. What happens when a stage is quiet, partial, missing, or failed?
7. How do model choice, cost, privacy, and provider policy fit the design?
8. What evidence supports the architecture, and what remains unknown?

It should be technical, but it should teach the architecture rather than
replay development history.

### Recommended section order

1. **The system contract**

   Start with the six-line authority boundary from the constitution.

2. **One end-to-end diagram**

   Show complete conversation, semantic views, four pressure lanes,
   deterministic graph survival, pressure portfolio, reconsideration,
   Markdown output, receipt, and human decision.

3. **Who owns what**

   | Question | Owner |
   |---|---|
   | What did this messy exchange mean? | Bounded LLM interpretation, with source references and uncertainty |
   | What is the stable identity of a source, model, pressure, or record? | Deterministic code |
   | Which bounded graph neighbors are recalled? | Deterministic traversal after admitted seeds |
   | Is a recalled model actually useful here? | Reconsidering reasoner, visible as apply/reject/park |
   | Did the process run as claimed? | Deterministic receipt and custody checks |
   | Is the answer wise enough to act on? | Human judgment |

4. **How the knowledge substrate was built**

   Explain the source books, 222 canonical Markdown articles, LLM-assisted
   synthesis, curation waves, relationship semantics, affordances, absence
   records, compiled graph, and optional embeddings. Separate immutable source
   material, reviewed curation, compiled artifacts, and runtime selections.

5. **How a conversation is represented**

   Explain authoritative transcript versus declared processing views,
   source-span custody, semantic interpretations, missingness states, and why
   deterministic turn-count or keyword rules cannot decide conversational
   meaning.

6. **The four pressure lanes**

   Give each lane one job, its input, its probabilistic work, its deterministic
   work, and its output. Put deep prompt and routing details in the existing
   modular lane document.

7. **Constitutional graph survival**

   Explain direct recall, graph recall, active set, reserve, provenance, token
   bounds, no silent probabilistic deletion, and apply/reject/park. State
   explicitly that deterministic recall is not certified relevance.

8. **Reconsideration**

   Explain what the reasoner receives, what it is allowed to do, how forcing
   is prevented, how a quiet result remains valid, and how same-context versus
   fresh-context reconsideration is disclosed.

9. **Artifacts and custody**

   Explain the source, processing views, result, memo, trace, usage summary,
   pressure ledger, and receipt at the level needed to inspect a run. Link to
   schemas rather than reproducing them.

10. **Model and provider strategy**

    Explain the current economical testing operator, override boundaries,
    exact routing and cost custody, embeddings provider, and future comparison
    policy.

11. **Failure and degraded states**

    Preserve `complete`, `completed_zero`, `partial`, `failed`, and `missing`
    as different states. Explain why no output, a quiet read, and a failed call
    are not interchangeable.

12. **Evidence and limitations**

    Summarize what is mechanically demonstrated, what has only simulated or
    bounded provider evidence, and what would require real-user evidence.

13. **Detailed references**

    Point to the six modular `docs/how-it-works/` files, the current
    constitution, current-state audit, roadmap, cost/telemetry guide, and eval
    index. Do not recreate a 250-link catalog.

### What should leave `HOW_IT_WORKS.md`

The “Current Notes” development chronology should move to a changelog or
historical development index. Large tables of every PR-era document should be
replaced by a small map of canonical documents. Implementation details that
are still accurate can remain in the modular how-it-works files, where readers
can opt into them.

## The Technical Story: Best Of Both Worlds

The strongest architecture story is not “deterministic versus probabilistic.”
It is correct allocation of authority.

### What LLMs are good at here

- interpreting indirect and ambiguous conversational meaning;
- recognizing a changed position across multiple turns;
- distinguishing a live concern from a historical aside;
- generating a source-grounded attempted application of a pressure;
- reconsidering a decision under several competing considerations;
- writing a readable revised position.

These are probabilistic jobs. They can disagree, fail, or return zero. Lolla
should bound them, preserve their source views, and record their identities
rather than pretend to turn them into deterministic facts.

### What deterministic machinery is good at here

- preserving the complete source and exact processing views;
- stable IDs, hashes, aliases, speaker ownership, and source spans;
- schema shape and local business-rule validation;
- graph traversal over admitted canonical identities;
- bounded fan-in and token envelopes;
- request previews, model/provider routing, call ceilings, and cost ledgers;
- distinguishing absent, quiet, partial, failed, and malformed states;
- ensuring every pressure presented to the consumer receives a disposition;
- replaying and comparing the exact process.

Deterministic code should reject malformed custody. It should not repair
meaning.

### Why this split matters

A brittle system tries to force messy human meaning through keywords,
chronology, or nested rule gates. A vague system gives an LLM the whole job and
then cannot prove what context, source, pressure, or cost shaped the answer.

Lolla's architecture is an attempt to avoid both failures. The LLM can remain
flexible where language is irreducibly messy. The system can remain exact where
identity, evidence, process, and limits must be inspectable.

This is a stronger claim than “deterministic systems are trustworthy.” It is
also a more honest one.

## How To Present The Current Model Choice

The current OpenRouter operator is `google/gemini-3.1-flash-lite`, pinned under
the current R4 contract. It is an economical experimental operator, not
Lolla's quality ceiling and not a validated production-model choice.

Recommended public language:

> Lolla currently uses an economical model configuration so the project can
> run bounded experiments, preserve exact provider and cost custody, and learn
> which failures belong to the architecture rather than to uncontrolled model
> changes. Model boundaries are replaceable. Stronger models and model mixes
> are future comparison arms, not assumed fixes.

Avoid:

- “The system uses cheap models now, so it will work better with expensive
  models.”
- “Any frontier model can be dropped in with the same behavior.”
- “The architecture is model-independent.”

Those statements are plausible hopes, not current evidence. A stronger model
may improve semantic reads and reconsideration while also changing restraint,
verbosity, context absorption, cost, or reproducibility. The right future
claim is architectural portability under an explicit evaluation contract.

If Lolla becomes a standalone product, the likely model strategy is stage
specific: use the least expensive model that passes each bounded job's
fidelity and restraint gates, and reserve stronger models for the jobs where
measured incremental value justifies them. That decision should follow model
comparison, not precede it.

## Intellectual Lineage

The giants belong in the story, but Lolla should not borrow their authority as
a substitute for evidence. Each influence should be attached to a precise
design decision.

### Charlie Munger: the root and the name

Munger is the clearest intellectual root. His latticework of mental models and
*The Psychology of Human Misjudgment* supplied two founding ideas:

- recurring failures interact rather than appearing one at a time;
- no single discipline or frame is sufficient for important judgment.

The name comes from Munger's description of the Lollapalooza tendency: “the
tendency to get extreme consequences from confluences of psychological
tendencies acting in favor of a particular outcome.” The current 25-tendency
layer is an adaptation for inspecting human–LLM reasoning transactions, not a
claim that an LLM has human psychology. The primary-source quotation is
available in Stripe Press's [*Poor Charlie's Almanack* excerpt](https://assets.stripeassets.com/fzn2n1nzq965/0RUnI35jpt78x10nvlO2Y/b66a46dba182182a2a0082213eafc634/SP_PCA-ZINE_2023_11_27.pdf).

Recommended use: a short “Why Lolla is called Lolla” subsection and the first
entry in the lineage section. Do not make the homepage a biography of Munger.

### Kahneman and Tversky: a useful metaphor with a boundary

*Thinking, Fast and Slow* gives readers familiar language for fast associative
processing and slower deliberation. It can help explain the motivation for an
external pause. The [publisher's description](https://us.macmillan.com/books/9780374533557/thinkingfastandslow/)
itself presents System 1 and System 2 as a way of describing human thought.

Recommended use: “Lolla borrows the fast/slow distinction as a design
metaphor.” Do not say Kahneman established that LLMs are System 1 machines or
that Lolla is literally System 2. That is Lolla's analogy, not Kahneman's
finding.

### *Framers*: pressure on the question, not only the answer

Kenneth Cukier, Viktor Mayer-Schönberger, and Francis de Véricourt emphasize
framing as the construction of a mental model that makes a situation
intelligible. The official [*Framers* site](https://framers-book.com/) connects
better outcomes with generating alternatives before the final choice.

Recommended use: explain why Lane 3 asks what the question makes visible or
invisible, and why a well-reasoned answer can still be trapped inside a weak
frame.

### Balaji Srinivasan: probabilistic generation plus deterministic machinery

Balaji's [“AI is Polytheistic, Not Monotheistic”](https://balajis.com/p/ai-is-polytheistic-not-monotheistic)
distinguishes probabilistic AI from deterministic computing and describes
verification as part of the emerging workflow. His concise warning—“0% AI is
slow, but 100% AI is slop”—is a useful architecture epigraph.

Recommended use: one sidebar in `HOW_IT_WORKS.md`, followed immediately by
Lolla's more precise authority split. Do not say his essay proves Lolla's
architecture or that deterministic code verifies semantic truth.

### Andrej Karpathy: persistent compiled knowledge

Karpathy's [LLM knowledge-wiki proposal](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
argues for a persistent, interlinked Markdown artifact between raw sources and
repeated retrieval. “The wiki is a persistent, compounding artifact” is a
useful description of the durable-knowledge intuition.

The chronology matters. The gist appeared immediately before Lolla's first
public repository commits and was credited in the initial README. It informed
the early implementation, but it is not the origin of the product thesis. The
Munger-inspired audit idea and the founder's adversarial legal perspective are
the roots; Karpathy is an engineering parallel for compiled knowledge and
Markdown persistence.

### The founder's legal practice: the lived perspective

The legal background is not a decorative origin story. It supplies a concrete
way of reading persuasive text:

- separate confidence from burden of proof;
- preserve the record;
- distinguish assertion from evidence;
- look for assumptions, missing authorities, adverse interpretations, and
  reversal conditions;
- make disagreement inspectable without pretending that opposition guarantees
  truth.

This founder story should remain in the README, but in a compact form centered
on why it shaped the product. The current job-seeking and proof-of-work passage
can move to a personal note or project history.

## Quote Policy

The hero should use Lolla's own sentence, not a famous person's authority.

Recommended hierarchy:

1. **No epigraph above the product definition.** The first claim should belong
   to Lolla.
2. **One Munger quotation in the name/origin section.** It explains the root.
3. **At most one architecture quotation in `HOW_IT_WORKS.md`.** Balaji's line is
   the strongest candidate because it is short and directly related to the
   hybrid design.
4. **Paraphrase Kahneman and *Framers* with clear attribution.** Their ideas are
   more useful than ornamental quotation.
5. **Use Karpathy's line only in the knowledge-compilation section.** It should
   explain a design influence, not confer authority on the entire product.

Stacking Munger, Kahneman, Balaji, *Framers*, Karpathy, and several research
papers in the first screen would make Lolla look derived and defensive. The
lineage should deepen a product the reader already understands.

## GitHub And Engineering Influences

The existing README puts all referenced projects in one list and repeatedly
says they “validated” Lolla. The more credible structure is to distinguish
three relationships.

### Adapted or materially incorporated

- [Machine Bullshit](https://github.com/synthanai/Machine-Bullshit) — a detector
  adapted into Lolla's Bullshit Index lane, with license attribution.

This category requires exact implementation and license notes.

### Architecture and implementation influences

- [qmd](https://github.com/tobi/qmd) — hybrid retrieval and reciprocal-rank
  fusion patterns;
- [Karpathy's knowledge wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
  — persistent compiled Markdown knowledge;
- [iwe](https://github.com/iwe-org/iwe) — structured Markdown knowledge and
  graph navigation patterns;
- [supermemory](https://github.com/supermemoryai/supermemory) — conversation
  extraction, relation typing, and deduplication patterns.

Use “informed,” “inspired,” or “provided a pattern,” not “validated.” Another
repository can confirm that a pattern is plausible or reusable; it cannot
validate Lolla's product claim.

### Presentation, workflow, and research references

- gstack and superpowers for showing what a substantial coding-agent skill can
  look like;
- context-engineering projects for context-packaging patterns;
- SkillsBench for empirical questions about what makes skill packages useful;
- maintained memory, graph, structured-output, and agent repositories reviewed
  during specific architecture decisions.

These belong in an acknowledgments or engineering-lineage document. They do
not all belong in the main README.

## Terminology Policy

| Term | Keep, qualify, or retire | Use |
|---|---|---|
| Lolla | Keep | Product name |
| reasoning-pressure layer | Keep | Primary category |
| serious AI conversations | Keep | Primary context |
| slow down | Keep and define | Useful pause before premature closure, not generalized indecision, runtime latency, or analysis for its own sake |
| reasoning audit | Keep, qualified | Familiar secondary descriptor; never imply certification |
| Decision Trail | Keep | Human-readable process artifact and future team surface |
| process receipt / audit receipt | Keep | Mechanical custody artifact; never a quality badge |
| portable Markdown record | Keep | Current principle and partial capability; distinguish full future cold-reader memory |
| being less wrong | Keep as philosophy | Never use as a measured outcome claim |
| external System 2 | Qualify as metaphor | Never present as literal architecture or scientific fact |
| mental-model engine | Keep below the fold | Substrate explanation, not primary user promise |
| knowledge-first | Keep below the fold | Engineering approach, not category |
| Decision Work | Move to internal/history | Research program and sidecar terminology |
| Product Delta | Move to evals | Evaluation lens, not product identity |
| Observatory | Keep as interface name | Product surface for inspecting one selected run |
| Mental Model Teacher | Keep as future direction | Deferred learning surface, not current core |
| R1–R5, SK3, V60, Gate 6/7 | Keep in technical/research docs | Never require these terms for README comprehension |
| quality noise | Rephrase externally | “Traceable external pressure” or “purposeful interruption” |
| deterministic verification | Retire for semantics | Use “deterministic custody and process verification” |
| anti-bullshit system | Keep as a component description | Too adversarial and narrow for the whole product |

## Claim And Evidence Discipline

The presentation should follow a visible claim ladder.

### Safe now

- Lolla preserves a complete available conversation and declares processing
  omissions.
- The runtime can produce structured pressure, reconsideration artifacts,
  archives, cost custody, and a process receipt.
- The repository contains the stated corpus, graph, curation, and evaluation
  artifacts.
- Deterministic code can prove which artifacts, IDs, requests, responses,
  bounds, and dispositions were recorded.
- Specific development and provider experiments produced the documented
  outputs at the documented cost.

### Safe with qualification

- Lolla can surface another angle.
- Lolla is designed to create useful friction.
- A Decision Trail can help a reviewer inspect how a recommendation formed.
- The graph can introduce pressure that a same-trajectory answer did not
  visibly contain.
- Better stage-specific models may improve bounded semantic work.

These are capability, design, or hypothesis claims—not proof of reliable user
benefit.

### Not currently safe

- Lolla improves reasoning quality.
- Lolla makes decisions better or users less wrong.
- Its graph reliably contributes unique value over a strong fresh model.
- Its deterministic substrate verifies semantic truth.
- A clean receipt means the revised answer is safe to use.
- Premium models will make the product work.
- The current system is ready for automatic or high-stakes reliance.

### Research claims

The current README and problem/thesis document contain several memorable
quantitative claims, including 30% versus 85%, 8–38×, 5×, and various sample
sizes. The July product blueprint already identified these as requiring direct,
precise citations or removal.

Recommendation:

- remove orphaned statistics from the README;
- create a small evidence page if research foundations matter to the public
  case;
- link every numerical claim directly to the primary paper;
- state what task, model, sample, and limitation the result actually covers;
- never convert one benchmark into a universal statement about LLM reasoning;
- separate external research evidence from Lolla's own experimental evidence.

The front door does not need a wall of statistics. The recognizable product
moment is strong enough.

## Documentation Migration Map

| Current content | Destination |
|---|---|
| README hero, short why, install, use | Rewritten README |
| README Product Delta and R4 chronology | `docs/evals/README.md` plus current evidence handoff |
| README detailed cost mechanics | `docs/cost-and-telemetry.md` |
| README full project-influence list | New intellectual/engineering lineage note or concise acknowledgments section |
| README long founder proof-of-work story | Compact founder note in README; full version in project history |
| README unsupported research statistics | Remove pending primary-source evidence page |
| HOW system principle and live flow | Rewritten `HOW_IT_WORKS.md` |
| HOW deep lane mechanics | `docs/how-it-works/pipeline-lanes.md` and `live-flow.md` |
| HOW substrate inventory | `docs/how-it-works/knowledge-substrate.md` |
| HOW history of architectural migrations | `docs/how-it-works/architecture-and-evolution.md` or project history |
| HOW operations and environment detail | `docs/how-it-works/operations-and-limits.md` |
| HOW “Current Notes” chronology | Changelog or historical development index |
| HOW giant document catalog | Small canonical reading map |
| Teacher and Observatory plans | `docs/product/README.md`, clearly labeled planning surfaces |
| Binding product rules | Constitution v5 and `AGENTS.md`, linked but not duplicated wholesale |

The migration should preserve historical evidence. It should not rewrite
frozen experiment files or pretend older proposals never existed.

## The Demo Story

Lolla should be demonstrated through one difficult conversation, not through a
tour of the repository.

The demo sequence should be:

1. Show the original multi-turn conversation and the answer the user was about
   to rely on.
2. Name why the answer felt compelling.
3. Show one exact passage or conversational development that the pressure
   attaches to.
4. Show the external model or tension that was introduced and its provenance.
5. Show whether the reasoner applied, rejected, or parked it.
6. Show the concrete delta: action, threshold, sequence, scope, gate,
   assumption, stop rule, or explicit non-change.
7. Show what remains unknown and what the system refuses to claim.
8. Download or open the Markdown record and show that a cold reader can follow
   the decision without replaying the chat interface.

The case must be labeled accurately as a development fixture, simulated
conversation, provider run, or real-user case. A polished simulation can prove
that the machinery is understandable. It cannot prove market usefulness.

The emotional conclusion should be:

> I can see why the final answer alone was not enough.

The technical conclusion should be:

> I can see where the pressure came from, what the reasoner did with it, and
> what the system still does not know.

## Positioning Risks And Falsifiers

The recommended story is coherent, but coherence is not market evidence. It
should be tested against these failure modes.

### “Reasoning pressure” may be too unfamiliar

The term is accurate but not self-explanatory. If cold readers repeat it
without understanding what happens in a run, it has become project jargon.

Falsifier: after reading the first screen, a reader cannot explain the product
without using the phrase itself.

Mitigation: always follow the category with “preserve, pressure, reconsider,
record” and one concrete before/after example.

### “Slow down” may sound anti-action

Founders and operators often value speed. A product that sounds like permanent
hesitation will lose the people who most need a pre-commitment check.

Falsifier: readers describe Lolla as a tool that adds caution, latency, or more
analysis to every AI interaction.

Mitigation: attach the phrase to a specific moment—when an answer is about to
be relied on—and show that the useful result can be a sharper next move, a
clear test, or an explicit decision to proceed.

### The mental-model substrate may sound like pop psychology

“222 mental models” can sound like a large flash-card library or an appeal to
famous thinkers. The product is not defensible merely because the number is
large.

Falsifier: readers remember the model count but cannot explain provenance,
relationships, misuse boundaries, or why the reasoner may reject a model.

Mitigation: lead with one pressure transaction and use counts only as evidence
of compilation depth. Show an antagonist, tension, source, and ignore boundary
rather than a carousel of model names.

### “Decision Trail” may outrun the current artifact

The phrase is concrete and valuable, but the full cold-reader, longitudinal
memory object remains a product direction.

Falsifier: a new user expects every current run to reconstruct all decision
threads, options, changes, values, and future reopen conditions without human
help.

Mitigation: label current archive and Markdown outputs separately from the
planned fuller Decision Trail.

### The story may mistake technical depth for customer value

Thousands of tests, exact hashes, protected targets, and elaborate curation
demonstrate engineering seriousness. They do not prove that a user wants the
result or will change a decision because of it.

Falsifier: the best demo still needs an architecture lecture before the user
cares about the outcome.

Mitigation: demo the decision delta first. Let technical custody answer the
reader's second question: “Why should I trust that this process actually
happened?”

### The current skill audience may not imply a standalone market

Claude Code and Codex users are a credible wedge because the product can
capture a rich working conversation. Their behavior does not by itself prove a
larger team or enterprise category.

Falsifier: people like the concept but do not return with conversations they
consider important enough to audit, or they will not wait for the current
cost and latency.

Mitigation: treat repeat use, chosen audit moments, inspected Markdown
records, and action-level deltas as product evidence before broadening the
category.

### Better models may not fix the hard problem

More capable models may read conversation state more faithfully. They may also
absorb pressure too eagerly, produce more persuasive false positives, or make
the graph's incremental contribution harder to distinguish from a strong
fresh-model control.

Falsifier: a stronger model improves prose and apparent sophistication without
improving source fidelity, quiet-case restraint, or useful unique pressure.

Mitigation: compare models on the existing vector of fidelity, restraint,
disposition quality, lost value, cost, and custody. Do not collapse the result
into preference or one score.

## Local Implementation Status

The founder accepted the hierarchy and authorized the documentation rewrite on
2026-07-14. Steps 1–7 below have been applied locally for review before any
commit, push, PR, or merge. Step 8 remains a later market-validation task:

1. Approve or revise the primary category and human promise.
2. Rewrite only the README first screen and status box.
3. Build one labeled demonstration section from an already authorized,
   non-protected artifact.
4. Reduce the rest of the README by moving—not deleting—research chronology and
   deep technical material.
5. Rewrite `HOW_IT_WORKS.md` around authority and data flow, reusing the six
   modular technical documents.
6. Create a short intellectual and engineering lineage note with exact
   attributions and license relationships.
7. Run a claim audit over the new entrypoints against Constitution v5, the
   latest evidence, provider/model status, and the current runtime.
8. Give both documents to cold readers: one product-oriented and one
   technical. Ask each to explain Lolla without using internal project terms.

No provider call was made for this documentation work.

## Adopted Presentation Stack

The founder adopted this messaging stack as the presentation source of truth:

```text
PRODUCT
Lolla — a reasoning-pressure layer for serious AI conversations.

PROMISE
Slow down the moment fluency starts to feel like certainty.

MECHANISM
Preserve → pressure → reconsider → record.

OUTCOME
Another inspectable angle, a revised position, and its decision trail.

BOUNDARY
The record proves the process, not the wisdom of the decision.
```

Everything else in the project should attach to one of those five lines.
