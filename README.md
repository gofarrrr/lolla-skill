# Lolla

**A reasoning-pressure layer for serious AI conversations.**

Lolla slows down the moment a fluent AI answer starts to feel like certainty.

Run it after a consequential conversation with Claude Code or Codex. Lolla
preserves the conversation, uses language models where
its messy meaning must be interpreted, recalls traceable challenge pressure
from a curated mental-model graph, and asks the reasoner to apply, reject, or
park that pressure. It leaves a revised position and an inspectable record of
what happened.

Lolla does not certify that an answer is correct or a decision is wise. It
makes another angle visible before the human decides.

```text
conversation → external pressure → reconsideration → decision trail
```

> **Experimental status — 2026-07-14:** The live skill, four pressure lanes,
> graph-survival path, archives, ledgers, Observatory, and process receipts
> exist. The project has not established that Lolla reliably improves
> decisions, that its graph adds unique value over a strong fresh-model read,
> or that a clean receipt indicates a sound answer. Current evaluation is
> focused on semantic restraint and false positives.

## The Moment Lolla Is For

You have spent forty minutes working through a hiring decision, vendor
contract, product bet, research plan, or organizational change with an AI. The
conversation was useful. The final answer is coherent enough to act on.

That is precisely when a second problem appears.

The conversation may contain an assumption introduced in turn two, a
constraint weakened in turn nine, an option quietly abandoned in turn
fourteen, and a trade-off polished away in the final memo. The prose feels
settled. The underlying uncertainty may not be.

Lolla is a deliberate pause at that point. Not permanent hesitation. Not a
generic risk list. Not another answer produced from a blank prompt.

It asks whether the reasoning needs another frame, a reversal condition, a
missing test, a neglected dependency, or a challenge that the current
trajectory did not select for itself. Sometimes the pressure changes the
position. Sometimes it is rejected. Sometimes it is worth preserving for
later.

“External” means external to the answer's current trajectory. It does not mean
independent truth. The source corpus, curation, graph, and models can still
share assumptions and blind spots. Provenance makes pressure inspectable; it
does not make it correct.

## What A Run Does

Lolla follows four product moves:

1. **Preserve.** The complete available prose conversation remains the
   authoritative source. Any compact processing view is stored separately
   with explicit omission metadata.
2. **Interpret.** Bounded LLM jobs read the parts that require semantic
   judgment: the current position, constraints, dropped threads, reasoning
   passages, frames, and gaps.
3. **Pressure.** Four audit lanes and a curated relationship graph introduce
   source-shaped structural challenges. Deterministic code preserves their
   identities, provenance, bounds, and custody.
4. **Reconsider and record.** The reasoner must apply, reject, or park each
   active graph pressure. The updated position, Markdown memo, run artifacts,
   usage, and process receipt are archived locally.

Short version:

```text
preserve → pressure → reconsider → record
```

### The four pressure lanes

| Lane | The question it asks | Main output |
|---|---|---|
| **Structural Pressure** | Which recurring cognitive tendencies may be shaping this reasoning? | Specific findings, corrective models, challenges, and reversal triggers |
| **Model Companion** | Which mental models are already doing work, and where might they fail? | Verified model anchors, failure modes, premortem questions, and opposing models |
| **Frame Pressure** | What does the question make visible, fixed, or unthinkable? | Embedded assumptions, mutable constraints, counterfactuals, and alternative questions |
| **Structural Coverage** | Which decision territory did the answer never enter? | Missing dimensions and questions only the decision-maker can answer |

These lanes produce candidate pressure, not verdicts. The graph introduces
possibilities; it does not certify relevance. A strange lens may survive long
enough to be inspected and still be rejected without appearing in the public
answer.

## What You Get

A completed run produces several views of the same reasoning episode:

- **Updated position** — what survived, what changed, and what remains open.
- **Pressure dispositions** — which active graph pressures were applied,
  rejected, or parked and why.
- **Markdown memo** — a readable local record of the run.
- **Observatory** — a local interface for the four cards, revised answer,
  graph, run health, usage, and archived cases.
- **Process receipt** — capture, artifact, schema, provider, cost, and custody
  evidence. It is not an answer-quality score.
- **Local archive** — the authoritative conversation, declared processing
  views, extraction, result, revised answer, memo, ledgers, evaluation receipt,
  and reasoning trace under `~/.local/share/lolla/runs/` by default.

The fuller **Decision Trail** is the product direction: a portable account of
how the position formed, which options and constraints mattered, what changed,
and what a later human or agent should reopen. Current artifacts contain much
of that process evidence, but they do not yet guarantee a complete cold-reader
reconstruction or longitudinal memory.

## A Development Example

This example is provider-backed development evidence, not independent product
validation or runtime authorization.

In a simulated museum licensing conversation, a fresh transcript-only
reasoner made no material change. The pressure arm received six graph lenses.
It applied two and rejected four:

- **Commitment bias** exposed the missing early-termination condition: what
  evidence would end the pilot?
- **Premortem** turned an acknowledged worst case into a threshold question:
  is persistent social and technical learning bad enough to reject the pilot,
  and are the safeguards sufficient?
- Active listening, confirmation bias, intellectual humility, and sunk cost
  were rejected as already handled or unsupported.

The result preserved the strong original analysis while adding a reversal rule
and severity test that were absent from the control. The source review also
recorded an artifact defect and explicitly refused to claim independent
usefulness. See the
[fresh reasoning-pressure museum pair result](docs/conversation-understanding/fresh-reasoning-pressure-museum-pair-result-2026-07-12.md).

This is the behavior Lolla is trying to make possible: not six model names in
the answer, but two useful pressures, four grounded rejections, and a visible
record of the difference.

## Why This Is More Than A Critique Prompt

The product is not the instruction “think harder.” One run sits on top of a
compiled reasoning substrate and a custody system.

### The substrate

The founding research program drew on roughly 200 books and related source
study. LLMs assisted the research and synthesis; reviewed curation and
compilation made the material stable enough to inspect and reuse.

The current repository contains:

- 222 canonical mental-model identities and source articles;
- 25 cognitive tendencies adapted from Charlie Munger's framework;
- 1,358 model-to-model relationship edges across allies, antagonists, and
  structured tensions;
- 241 tendency-to-antidote bindings;
- 1,742 total graph edges when tendency links are included;
- 222 V60 model records, 306 source-backed affordances, and 697 absence
  records in the current `draft_review_only` transaction layer;
- precomputed embeddings for source chunks, model signals, tendency guidance,
  and relationship activation conditions.

The absence records matter. They preserve what a source does *not* support, so
a tempting model application can be blocked rather than stretched.

### The authority split

Lolla uses the best tool for each kind of work:

| Work | Owner |
|---|---|
| Interpret messy conversational meaning | Bounded LLM jobs |
| Preserve source identity, hashes, speaker ownership, and exact artifacts | Deterministic code |
| Traverse the admitted graph and enforce context, call, and cost bounds | Deterministic code |
| Decide whether a recalled pressure applies | Reconsidering reasoner, recorded as apply/reject/park |
| Verify that the recorded process occurred | Deterministic receipt and custody checks |
| Decide whether the answer is wise enough to act on | Human judgment |

Deterministic code can prove shape, identity, custody, and process. It cannot
repair meaning or prove that a pressure is relevant.

## Install

### Requirements

- Python 3.10 or newer; the runtime uses the standard library and needs no
  `pip` installation.
- An OpenRouter API key for LLM interpretation.
- Optionally, a direct OpenAI API key for the embedding redundancy layer.
- Claude Code or Codex as the current skill surface.

Claude Opus 4.7 is the currently documented Claude Code recommendation.
Codex is supported, but an equivalent Codex orchestrator-floor study has not
yet been completed. See
[Model Requirements](docs/how-it-works/architecture-and-evolution.md#model-requirements).

### 1. Clone the repository

```bash
git clone https://github.com/gofarrrr/lolla-skill.git
cd lolla-skill
```

### 2. Link the skill

For Claude Code:

```bash
mkdir -p ~/.claude/skills
ln -s "$PWD" ~/.claude/skills/lolla
```

For Codex:

```bash
mkdir -p ~/.codex/skills
ln -s "$PWD" ~/.codex/skills/lolla
```

### 3. Configure provider keys

Global configuration:

```bash
mkdir -p ~/.config/lolla
cat > ~/.config/lolla/.env <<'EOF'
OPENROUTER_API_KEY=your-openrouter-key
OPENAI_API_KEY=your-openai-key  # optional
EOF
```

You can instead use `.claude/lolla.env` or `.codex/lolla.env` inside a
project. Only the OpenRouter key is required. If the OpenAI key is absent,
Lolla records that embeddings are off and continues through the documented
embedding-off path; it does not redirect embeddings to another provider.

### 4. Restart the agent surface

Claude Code exposes `/lolla`. In Codex, invoke `$lolla` or ask Codex to use the
Lolla skill.

## Use It

After a strategic conversation, run:

```text
/lolla
```

or in Codex:

```text
$lolla
```

The skill also recognizes requests such as:

- “audit this”;
- “check my reasoning”;
- “find blind spots”;
- “stress test this”;
- “what am I missing?”;
- “challenge this”;
- “what are we not seeing?”;
- “run a pre-mortem.”

It works best after a substantial conversation involving a recommendation,
trade-off, uncertain commitment, or strategic choice. It is not intended for
ordinary coding questions or simple factual lookup.

A normal completion gives you the revised position in chat and a functional
receipt with the Observatory URL, memo path, cost, and archive location.

## Current Evidence And Limits

Mechanically, Lolla can:

- preserve the complete available conversation and declare bounded views;
- run the four pressure lanes;
- preserve a bounded graph portfolio before probabilistic verification;
- require apply/reject/park custody for every active pressure;
- persist the updated position, memo, local archive, provider identity, usage,
  and process receipts;
- distinguish quiet, partial, failed, missing, and malformed states;
- replay and compare frozen development evidence.

It has not established:

- reliable improvement in reasoning or decisions;
- real-user usefulness across a representative population;
- unique graph value over strong fresh-model reconsideration;
- semantic reliability of the current R4 reader architecture;
- safe automatic, medical, legal, financial, or other high-stakes reliance;
- that a more expensive model will solve the remaining failures.

The latest leakage-corrected R4 matched holdout ran once under its exact frozen
contract. Both arms recovered genuine residual gaps. The repaired residual arm
still produced false positives on both quiet controls, so the frozen decision
is `residual_task_repair_insufficient`. That reader is not integrated into the
runtime. See the
[matched-holdout execution result](docs/conversation-understanding/lolla-r4-matched-holdout-v2-execution-result-2026-07-14.md)
and the
[current roadmap](plans/lolla-post-v1-constitution-aligned-roadmap-2026-07-13.md).

## Models, Providers, Privacy, And Cost

The current default LLM operator is `google/gemini-3.1-flash-lite` through
OpenRouter. It is an economical experimental choice, not a validated
production model or Lolla's quality ceiling. `LOLLA_OPENROUTER_MODEL` can
override it, but model changes should be evaluated rather than assumed
equivalent.

A typical core run makes roughly 18–25 OpenRouter calls. The Bullshit Index can
add up to 12 bounded delivery-audit calls on longer answers. The ordinary live
receipt records per-stage calls, tokens, the served model, provider response
identity, exact provider-reported cost when available, and the local estimate.
The documented user-facing expectation is usually five to eight minutes, but
length, provider behavior, and triggered lanes can change that.

Conversation content is sent to the configured LLM provider. If embeddings are
enabled, query-expansion and embedding material are sent directly to OpenAI.
Run artifacts are archived locally by default. The request and receipt record
routing, fallback, data-collection policy, and ZDR request state; a requested
privacy property is not presented as proof that a provider endpoint supplied
it. Review provider policies before using sensitive material.

See [Cost and Telemetry](docs/cost-and-telemetry.md) for the exact accounting
contract.

## What Lolla Is Not

- Not a fact checker or domain expert.
- Not a second answer from a blank prompt.
- Not a generic “consider the risks” generator.
- Not a deterministic solver of human meaning.
- Not a score for reasoning quality.
- Not an approval badge for a person, agent, or decision.
- Not a substitute for qualified professional review.
- Not a requirement to use every mental model it recalls.

The desired pressure may be strange, weak, already handled, or rejected. A
quiet or unchanged result can be honest. Public disagreement is not proof that
the system helped.

## Why The Name Is Lolla

Charlie Munger used “Lollapalooza tendency” for the extreme effects that can
arise when several psychological tendencies reinforce one another. That idea
is the root of the project: important failures rarely arrive as one clean bias,
and no single model is sufficient for important judgment.

Munger's latticework shaped the tendency and mental-model substrate. Daniel
Kahneman and Amos Tversky's fast/slow distinction provides a design metaphor,
not a literal claim that LLMs are System 1 or that Lolla is System 2. Kenneth
Cukier, Viktor Mayer-Schönberger, and Francis de Véricourt's *Framers* shaped
the pressure on the question itself. Balaji Srinivasan's probabilistic-versus-
deterministic framing informed the authority split. Andrej Karpathy's
[knowledge-wiki proposal](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
informed the compiled Markdown knowledge approach.

The founder's legal background supplies the lived reading method: preserve the
record, separate assertion from evidence, test the burden of proof, find the
adverse interpretation, and distinguish a persuasive brief from a sound one.

For the full origin, product boundary, and future Markdown-memory and Teacher
direction, read the
[Founder Product Vision](docs/conversation-understanding/lolla-founder-product-vision-2026-07-14.md).

## Engineering Influences

- [Machine Bullshit](https://github.com/synthanai/Machine-Bullshit) supplied a
  detector adapted into Lolla's Bullshit Index, with its license attribution.
- [qmd](https://github.com/tobi/qmd) informed hybrid retrieval and reciprocal
  rank fusion patterns.
- [iwe](https://github.com/iwe-org/iwe) informed structured Markdown knowledge
  and graph-navigation patterns.
- [supermemory](https://github.com/supermemoryai/supermemory) informed parts of
  conversation extraction, relationship typing, and deduplication.
- Karpathy's knowledge wiki informed the distinction between raw sources and a
  persistent compiled knowledge artifact.

These projects informed particular decisions. They do not validate Lolla's
product claims.

## Read Deeper

- [How Lolla Works](HOW_IT_WORKS.md) — authority, knowledge compilation,
  runtime flow, artifacts, providers, failures, and limits.
- [Product Constitution v5](docs/conversation-understanding/lolla-product-constitution-v5.md)
  — binding rules and product evils.
- [Founder Product Vision](docs/conversation-understanding/lolla-founder-product-vision-2026-07-14.md)
  — the human purpose and future product boundary.
- [Current Constitutional Audit](docs/conversation-understanding/lolla-current-state-constitutional-audit-2026-07-13.md)
  — ground-up state assessment.
- [Current Roadmap](plans/lolla-post-v1-constitution-aligned-roadmap-2026-07-13.md)
  — ordered development and evidence gates.
- [Evaluation Index](docs/evals/README.md) — Product Delta, frozen experiments,
  review contracts, and non-claims.
- [Board and Product History](docs/board/README.md) — earlier Decision Work
  briefs, sidecar experiments, and other historical product evidence.
- [Product Planning Index](docs/product/README.md) — future Observatory work,
  portable-memory, and Mental Model Teacher surfaces.

## Repository Map

```text
lolla-skill/
├── SKILL.md                 # Claude Code and Codex orchestration contract
├── HOW_IT_WORKS.md          # Technical product explanation
├── engine/system_b/         # Standard-library runtime engine
├── data/                    # Graph, curation, compiled substrate, embeddings
├── scripts/                 # Capture, pipeline, memo, archive, eval helpers
├── observatory/             # Local run-inspection interface
├── references/              # Runtime guidance loaded by the skill
├── docs/                    # Current contracts, product notes, and evidence
├── research/                # Frozen development evidence and artifacts
└── tests/                   # Runtime, custody, and evaluation verification
```

Historical research remains in the repository because it records what was
tried, rejected, repaired, or frozen. Treat the newest explicit status as
current behavior; an older proposal is not a live feature.

## Contributing

This is an experimental project. Issues, critique, test cases, and careful
counterexamples are welcome. Please do not open a change that silently rewrites
frozen experiment evidence or turns a process receipt into a quality claim.

## License

MIT. See [LICENSE](LICENSE).
