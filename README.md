# Lolla

*Named after the Lollapalooza effect — Charlie Munger's term for what happens when multiple cognitive tendencies compound together to produce extreme misjudgment. That compounding is what makes reasoning failures dangerous, and what makes them detectable.*

**A reasoning audit for AI conversations.**

Lolla detects structural weaknesses in LLM-generated strategic advice — not by generating opinions, but by routing through a curated substrate of 222 mental models, 25 cognitive tendencies, and 1,358 relationship edges compiled from primary sources.

When you ask an LLM whether to hire a VP of Sales, sign a vendor contract, or restructure your engineering org, the answer sounds confident. Lolla tells you *where that confidence is structurally fragile* — and what specific mental models challenge it.

Lolla is not in the business of finding better answers. It is in the business of **being less wrong** — reintroducing the friction that LLM fluency removes, so that inconvenient tensions, missing reversal conditions, and embedded assumptions don't get smoothed out of the narrative.

Four independent audit lanes:

| Lane | What it asks | Output |
|------|-------------|--------|
| **Structural Pressure** | Which cognitive tendencies are distorting this reasoning? | DeltaCard — tendency detections with corrective models, challenge statements, reversal triggers |
| **Model Companion** | Which mental models are already active in this reasoning? | CompanionCheatSheet — verified model presence with failure modes, premortem questions, antagonists |
| **Frame Pressure** | What assumptions are embedded in the question itself? | FramePressureCard — suppressed counterfactuals, mutable constraints, reframed alternative questions |
| **Structural Coverage** | What structural territory did the answer never enter? | CoverageCard — gap dimensions with discovery questions only the decision-maker can answer |

Each lane produces independent, traceable findings grounded in curated knowledge — not LLM-generated commentary.

## Why This Exists

LLMs will keep getting better. They'll get more accurate, more nuanced, more capable of complex reasoning. So why build a deterministic system to challenge them?

Because fluency and correctness are different problems. An LLM can produce a perfectly coherent recommendation that is structurally fragile — built on an unexamined assumption, missing a reversal condition, or anchored to whichever framing the question happened to use. The better the prose, the harder this is to see. Getting better at generating doesn't mean getting better at knowing where the generation is weak.

This is not a temporary gap waiting for the next model release to close. It's architectural:

- **Probabilistic systems cannot self-verify.** An LLM auditing its own reasoning is sampling from the same distribution that produced the flaw. Anthropic's sycophancy research, Princeton's user studies (N=557), and MIT's Bayesian modeling all converge on the same finding: LLMs systematically agree with users and defend their own outputs, even when wrong. A different model helps — but it shares training biases. A deterministic substrate with curated failure modes doesn't share anything.

- **Structure beats context.** Giving a model all the right facts produces 30% accuracy on reasoning tasks. Giving it a structured reasoning framework produces 85% (Car Wash Study, 120 trials, p=0.001). CMU's research shows surface cues dominate implicit constraints by 8-38x across 14 frontier models. The knowledge exists inside the model — it doesn't activate without structural intervention.

- **Reasoning quality is not factual accuracy.** Almost all existing LLM guardrails check whether the output is *true* or *safe*. Almost nobody checks whether the *reasoning structure* is sound — whether the argument would survive adversarial challenge, whether the confidence is earned, whether the frame suppresses alternatives. This is the gap Lolla occupies.

The broader landscape is converging on the same insight. Microsoft's GraphRAG, Stanford's DSPy, NVIDIA's NeMo Guardrails, Karpathy's knowledge compilation architecture — all are building hybrid systems where LLMs handle the probabilistic edges and deterministic structures handle the reliable middle. Neurosymbolic AI saw 236 publications in 2023 alone. The question is no longer *whether* to combine LLMs with structured knowledge, but *how* — and for *which problems*.

Most of these systems target factual grounding (is the output true?) or compliance (is the output safe?). Lolla targets a different problem: **is the reasoning structurally sound?** Not "did the LLM hallucinate a fact" but "did the LLM close on a recommendation without testing the frame, dismiss a risk without evidence, or let one scenario do all the argumentative work?"

That problem doesn't go away as models improve. It gets harder to see.

## Install

1. Clone this repo:

```bash
git clone https://github.com/gofarrrr/lolla-skill.git
```

2. Symlink into your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills
ln -s /path/to/lolla-skill ~/.claude/skills/lolla
```

3. Add your API keys (one of these locations):

```bash
# Option A: Global config (works across all projects)
mkdir -p ~/.config/lolla
cat > ~/.config/lolla/.env << 'EOF'
OPENROUTER_API_KEY=your-openrouter-key-here
OPENAI_API_KEY=your-openai-key-here  # optional — enables embedding swiss cheese layer
EOF

# Option B: Per-project (create in any project's .claude/ directory)
cat > .claude/lolla.env << 'EOF'
OPENROUTER_API_KEY=your-openrouter-key-here
OPENAI_API_KEY=your-openai-key-here  # optional
EOF
```

Only `OPENROUTER_API_KEY` is required. `OPENAI_API_KEY` enables the embedding swiss cheese layer — a redundancy mechanism that catches tendencies the LLM triage misses (and vice versa). Embeddings use multi-query expansion (gpt-4o-mini generates domain-vocabulary variants, fused via Reciprocal Rank Fusion) to bridge the gap between user language and curated model terminology. The system works without it, just with one fewer detection layer.

4. Restart Claude Code. The `/lolla` command is now available.

## Usage

In any Claude Code conversation where you're getting strategic advice, run:

```
/lolla
```

The skill captures the conversation, extracts the decision structure, and runs the full audit pipeline. It works best on conversations where you're making a recommendation, weighing tradeoffs, or giving strategic advice.

**Trigger phrases** (the skill also activates on these):
- "audit this", "check my reasoning", "find blind spots"
- "stress test", "what am I missing", "challenge this"
- "devil's advocate", "what are we not seeing", "pre-mortem"

## Requirements

- **Python 3.10+** (uses stdlib only, no pip dependencies)
- **OpenRouter API key** (for LLM inference via calibrated prompts)
- **Optional:** OpenAI API key (enables semantic embedding search for richer companion matching)

## What's Inside

```
lolla-skill/
├── SKILL.md              # Skill definition (Claude Code reads this)
├── HOW_IT_WORKS.md       # Full technical reference
├── engine/system_b/      # Bundled pipeline engine (67 files, zero dependencies)
├── data/                 # Knowledge graph, curation layers, embeddings
│   └── curated/          # Compiled substrate files (bundle selector, signal lexicon)
├── scripts/
│   ├── run_extract.py    # Step 2: conversation → decision structure (with capture validation)
│   ├── run_pipeline.py   # Step 3: decision structure → four-lane audit (with run health)
│   └── render_memo.py    # Deterministic markdown memo from result.json (no LLM)
├── observatory/          # Local web UI — four cards, revised answer, reasoning graph, run health, pipeline inspector
├── references/           # Tendency catalog, calibration, guardrails (loaded on demand)
└── tests/                # Unit tests (trigger sources, frame validation, fuzzy matching, BI context, memo rendering)
```

The engine runs entirely on Python stdlib. No virtual environment, no pip install, no external packages.

## How It Works

See **[HOW_IT_WORKS.md](HOW_IT_WORKS.md)** — the full technical reference covering the problem, architecture, knowledge substrate, step-by-step pipeline flow, quality doctrine, known limitations, and cost per run.

## Cost

A typical audit makes 10-13 OpenRouter calls against the configured model (default: `x-ai/grok-4.1-fast`). Total: ~30-40K tokens, approximately $0.03-0.06 per run. Embeddings (if enabled) add one gpt-4o-mini expansion call (~$0.001) plus batch embedding for 3 query variants (~$0.0002).

## Inspiration and Credits

Lolla exists because of foundational work by others:

- **Charlie Munger** — [*The Psychology of Human Misjudgment*](https://fs.blog/great-talks/psychology-human-misjudgment/) is the intellectual root. The 25 cognitive tendencies are Munger's framework, adapted for LLM-generated reasoning.
- **Daniel Kahneman** — *Thinking, Fast and Slow* established the System 1 / System 2 framework. LLMs are extraordinary System 1 machines — fast, fluent, pattern-matching — but structurally weak at System 2: slow, deliberate, logically disciplined reasoning. Lolla is an external System 2 guardrail.
- **Balaji Srinivasan** — His framing of AI as probabilistic (good at "middle-to-middle" generation) but needing a deterministic verification layer directly influenced our architecture: LLMs at the probabilistic edges, curated knowledge in the deterministic middle. "0% AI is slow, but 100% AI is slop" — Lolla occupies the space between, where human-curated structure disciplines LLM flexibility.
- **Farnam Street / The Knowledge Project** — Shane Parrish's interviews and writing on mental models shaped how the 222-model substrate was selected and organized.
- **Kenneth Cukier, Viktor Mayer-Schönberger & Francis de Véricourt** — *Framers: Human Advantage in an Age of Technology and Turmoil* directly informed Lane 3 (Frame Pressure). The thesis that framing is humanity's core cognitive advantage — and that the frame constrains the solution space before reasoning even begins — is why Lolla audits the question, not just the answer.
- **Research foundations** — Perez et al. (2022) on sycophancy, Kadavath et al. (2022) on calibration, Turpin et al. (2023) on unfaithful reasoning, Sharma et al. (2023) on sycophancy taxonomy.

### Projects That Informed Our Approach

- [qmd](https://github.com/tobi/qmd) (Tobi Lutke) — Hybrid search architecture: embeddings as one layer alongside BM25 and LLM re-ranking, fused via reciprocal rank fusion. Validated our swiss cheese approach where embeddings complement LLM triage rather than replacing it.
- [Karpathy's knowledge wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (Andrej Karpathy) — Compilation-based knowledge management: raw sources → persistent wiki artifacts with cross-references, not retrieval-based rediscovery. Directly mirrors our curation → compilation pipeline.
- [autoresearch](https://github.com/karpathy/autoresearch) (Andrej Karpathy) — Clean separation of stable substrate from experimental layer, with documentation as a first-class programming interface.
- [iwe](https://github.com/iwe-org/iwe) — Structured knowledge graphs from Markdown with hierarchy, polyhierarchy, and context inheritance. "Messy knowledge yields poor results." Validated our curated-Markdown-first doctrine.
- [Machine Bullshit](https://github.com/synthanai/Machine-Bullshit) (Hannigan et al., 2025) — Four-subtype LLM-as-judge bullshit detector operationalizing Frankfurt's (2005) definition. Adapted for strategic advice domain as Lolla's Bullshit Index layer. MIT license.
- [Mathematical methods and human thought in the age of AI](https://arxiv.org/abs/2603.26524) (Klowden & Tao, 2026) — "Odorless proof" concept (technically correct output lacking insight), "smell test" as informal quality assessment before formal verification, blue/red team framing for AI-assisted reasoning. Directly informs our anti-bullshit doctrine and Lolla's architectural role as a red team system.
- [gstack](https://github.com/AshMartian/gstack) — Demonstrated that Claude Code skills can be comprehensive workflow systems, not just prompt snippets.
- [superpowers](https://github.com/NickHeap2/claude-code-superpowers) — Showed how to present a skill with confidence and clear value proposition.
- [context-engineering](https://github.com/coleam00/context-engineering) — Validated the academic-rigor approach to skill presentation and that curated knowledge substrates outperform generated content.
- [supermemory](https://github.com/supermemoryai/supermemory) — Extraction pipeline patterns (relationship typing, deduplication, conversation capture) informed our conversation-to-CritiqueRequest extraction design.
- [SkillsBench](https://github.com/benchflow-ai/skillsbench) — Research findings on skill effectiveness (+18.6pp for 2-3 focused modules, +16.2pp for curated knowledge, worked examples as effectiveness separator) validated our architecture choices.

## Origin

Lolla was built by a lawyer, not a software engineer. I'm a trained legal professional who learned agentic coding about ten months ago. I had no prior software engineering background. Everything in this project — the RAG pipeline that built the canonical articles, the curation methodology, the deterministic routing, the knowledge graph compilation, the evaluation system — I learned by needing it and building it.

That background is not incidental to the design. Lawyers think about reasoning structure professionally: burden of proof, adversarial challenge, the difference between a persuasive argument and a sound one, why a confident brief can be structurally weak. Lolla audits reasoning the way a good opposing counsel reads a brief — not to disagree, but to find where the structure doesn't hold.

Building this project taught me how RAG works (and where it fails), how curation differs from generation, how LLMs actually behave under structured constraints, what knowledge engineering looks like in practice, why the distinction between deterministic and probabilistic matters for trust, and what context engineering means when you're trying to make an LLM focus rather than wander.

What I discovered along the way is that I genuinely love building things. The problem-solving, the architecture decisions, the moment when a system starts working — that's what gets me up in the morning. This project is my proof of work: not a portfolio of tutorials, but a working system built from scratch by someone who did the research and figured out how to make it real in an agentic-first world.

If you're building something where structured reasoning, knowledge engineering, or AI audit systems matter — and you're looking for someone who thinks about these problems obsessively — I'd love to talk.

## What's Next

The system works — but more data from real runs will let us tune the deterministic routing, understand detection patterns better, and calibrate where the system is strong and where it's still rough.

- **More mental models.** Domain-specific model packs — legal reasoning, medical decision-making, engineering tradeoffs — each following the same curation methodology, would make the system sharper in specialized contexts.
- **New lanes.** The four-lane architecture is extensible. Temporal reasoning, stakeholder mapping, assumption dependency chains — each would follow the same pattern: probabilistic detection at the edges, deterministic routing in the middle.
- **Better detection calibration.** More runs against more cases means better understanding of where each tendency's detection boundary should sit.
- **Deeper conversation extraction.** There's more signal in conversational dynamics — how positions shift across turns, where the human pushed back and the LLM folded, where concerns were raised and then quietly dropped.
- **Beyond the skill.** The curated knowledge substrate and the audit architecture are not limited to a Claude Code skill. The same engine could power API-level reasoning checks, editorial review workflows, decision journaling tools, or structured training environments where people practice spotting reasoning weaknesses. We see directions we haven't built yet — and probably directions we haven't thought of.

If you see an application we're missing or have ideas about where this kind of system would be valuable, open an issue. The most interesting next steps often come from people with different problems than ours.

## Contributing

The most valuable contributions don't require deep knowledge of the codebase:

- **Run the system and share findings.** Every real-world audit helps us understand detection patterns and calibration gaps.
- **Add mental models.** Write a canonical article from primary sources, curate its activation and intervention semantics, and it enters the substrate.
- **Write eval cases.** Professional-grade strategic scenarios with known reasoning weaknesses help us measure whether the system catches what it should.
- **Challenge the architecture.** Read [HOW_IT_WORKS.md](HOW_IT_WORKS.md) and tell us where the design doesn't hold.

This is an early-stage project built by someone who learned as he went. The architecture is sound, the knowledge substrate is real, and the system produces genuine structural pressure. But there are rough edges, unexplored directions, and decisions that deserve scrutiny from people with different expertise. That's the point of making it public.

## License

MIT
