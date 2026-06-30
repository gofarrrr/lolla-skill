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

2. Symlink into your skills directory.

For Claude Code:

```bash
mkdir -p ~/.claude/skills
ln -s /path/to/lolla-skill ~/.claude/skills/lolla
```

For Codex:

```bash
mkdir -p ~/.codex/skills
ln -s /path/to/lolla-skill ~/.codex/skills/lolla
```

3. Add your API keys (one of these locations):

```bash
# Option A: Global config (works across all projects)
mkdir -p ~/.config/lolla
cat > ~/.config/lolla/.env << 'EOF'
OPENROUTER_API_KEY=your-openrouter-key-here
OPENAI_API_KEY=your-openai-key-here  # optional — enables embedding swiss cheese layer
EOF

# Option B: Per-project for Claude Code
mkdir -p .claude
cat > .claude/lolla.env << 'EOF'
OPENROUTER_API_KEY=your-openrouter-key-here
OPENAI_API_KEY=your-openai-key-here  # optional
EOF

# Option C: Per-project for Codex
mkdir -p .codex
cat > .codex/lolla.env << 'EOF'
OPENROUTER_API_KEY=your-openrouter-key-here
OPENAI_API_KEY=your-openai-key-here  # optional
EOF
```

Only `OPENROUTER_API_KEY` is required. `OPENAI_API_KEY` enables the embedding swiss cheese layer — a redundancy mechanism that catches tendencies the LLM triage misses (and vice versa). Embeddings use multi-query expansion (gpt-4o-mini generates domain-vocabulary variants, fused via Reciprocal Rank Fusion) to bridge the gap between user language and curated model terminology. The system works without it, just with one fewer detection layer.

4. Restart the agent surface. In Claude Code, `/lolla` is now available. In Codex, invoke `$lolla` or ask to use the Lolla skill.

## Usage

In any Claude Code conversation where you're getting strategic advice, run:

```
/lolla
```

In Codex, run:

```
$lolla
```

The skill captures the conversation, extracts the decision structure, and runs the full audit pipeline. It works best on conversations where you're making a recommendation, weighing tradeoffs, or giving strategic advice.

At completion, each run is archived locally under `~/.local/share/lolla/runs/`.
The archive includes `agent_result.json`: a compact `lolla_agent_result.v1`
handoff for agents that says whether the run is fit for automatic use, what
changed when that is visible from product artifacts, which human questions
remain, and where to inspect the archive. It also includes `evaluation.json`: a
deterministic run-readiness receipt for artifact/schema/custody/health
consistency, including capture adequacy, not advice-quality scoring. Finally,
`reasoning_trace.json` is a local-only custody manifest that indexes the
captured conversation, result, memo, health, usage, ledger artifacts,
reasoning-lens IDs, model-call telemetry, capture adequacy, and trace-adequacy
status by path/hash and structured metadata without duplicating raw transcript
text.
`LOLLA_AUDIT_MODE` can record the run as `quick`, `standard`, `deep`,
`high_stakes`, or `stability`; the normalized value is persisted as
`risk_mode`. Today this is metadata only: it does not change prompts, cost,
Step 7 behavior, replay, or high-stakes policy.
The Observatory URL in the final receipt opens the completed run as a local
viewer. Its `Cases` tab also lists local archived runs from
`~/.local/share/lolla/runs/` (or `$LOLLA_ARCHIVE_DIR`) so recent history can be
opened without leaving the browser. Run-to-run comparison and dataset export
still live in the archive folder and the comparison/export scripts below.
To turn archived reasoning traces into a local reasoning-eval corpus, run:

```bash
python3 scripts/export_reasoning_trace_dataset.py \
  ~/.local/share/lolla/runs \
  --out /tmp/lolla_reasoning_traces.jsonl \
  --summary-out /tmp/lolla_reasoning_traces_summary.json
```

To build a broader human-review corpus from archived run envelopes, run:

```bash
python3 scripts/export_review_corpus.py \
  ~/.local/share/lolla/runs \
  --out /tmp/lolla_review_corpus.jsonl \
  --manifest-out /tmp/lolla_review_corpus_manifest.json
```

The review corpus is deterministic and local-only. It summarizes artifact
presence, run health, capture adequacy, `agent_result.json`, `evaluation.json`,
usage/model metadata, and optional control-plane references with blank
human-review fields. It does not copy raw transcript/memo text, does not score
advice quality, and does not use an LLM judge.

## Offline Product Delta Evidence Lane

The live skill and the eval lane are separate.

```text
Lolla runtime:
  current conversation -> audit pressure -> revised answer -> archived artifacts

Product Delta eval lane:
  existing safe artifacts -> readiness -> provisional review packets -> lint -> disagreement report
```

The runtime creates the object of study. The Product Delta lane studies it
later. It does not run `$lolla`, invoke the skill, call providers, mutate
archives, change prompts, judge answer quality, or approve agent action.

Use this lane when you want to understand what changed between the original
strong-model conversation and the Lolla revised answer. The review questions
are deliberately concrete:

- Did the likely next action, threshold, sequence, evidence gate, stop rule, or
  scope change?
- Did Lolla add useful friction, or only caution and process?
- Did it lose something valuable from the original answer?
- Did it understand the conversation well enough for the review to be useful?
- Are empty fields, missing artifacts, and provisional reads clearly marked as
  non-claims?

Safe local commands include:

```bash
python3 scripts/evals/build_product_delta_provisional_review.py \
  --case-list docs/evals/product-delta-seed-cases-v0.json \
  --out /tmp/product_delta_readiness.md \
  --json-out /tmp/product_delta_readiness.json
```

```bash
python3 scripts/evals/build_product_delta_specialist_packets.py \
  --case-list docs/evals/product-delta-seed-cases-v0.json \
  --provisional-review reviews/codex-assisted/product-delta-provisional-run-v0/review.json \
  --codex-batch reviews/codex-assisted/product-delta-batch-v0/review.json \
  --limit 2 \
  --out /tmp/product_delta_specialist_packets.json
```

```bash
python3 scripts/evals/lint_product_delta_evidence.py --paths \
  docs/evals/product-delta-provisional-report-v0.md \
  reviews/codex-assisted/product-delta-batch-v0/review.json \
  reviews/codex-assisted/specialist-review-batch-v0/review.json \
  reviews/codex-assisted/fan-in-disagreement-report-v0/report.json
```

The current packaged Product Delta phase is PR71-PR85. It is useful internal
evidence scaffolding, not product proof. Its healthiest signal is a downgrade:
`accept-operations-role-startup` moved from `material_improvement_candidate`
to `partial_improvement_candidate` after specialist review preserved lost
value and interpretation concerns.

The emerging customer-facing product surface is the Decision Trail: the revised
answer plus a compact process report explaining what conversation produced it,
what changed, what was challenged, what remains missing, and what should not be
overclaimed. See
[Board Product Briefs](docs/board/README.md) for a simple board/customer-facing
reading packet,
[Decision Work Receipt PRD](docs/conversation-understanding/decision-work-receipt-prd-v0.md)
for the actionable implementation plan for the missing work-trail layer, its
schema contract in
[Decision Work Receipt Schema](docs/conversation-understanding/decision-work-receipt-v0.json),
the first read-only source/context inventory exporter in
[Decision Work Receipt Source Inventory](docs/conversation-understanding/decision-work-receipt-source-inventory-v0.md),
the deterministic turn-count and one-shot/multi-turn process-shape slice in
[Decision Work Receipt Conversation Process Map](docs/conversation-understanding/decision-work-receipt-conversation-process-map-v0.md),
the challenge-surface and run-health-caveat slice in
[Decision Work Receipt Challenge Coverage Map](docs/conversation-understanding/decision-work-receipt-challenge-coverage-map-v0.md),
and the composed sparse receipt exporter in
[Decision Work Receipt Exporter](docs/conversation-understanding/decision-work-receipt-exporter-v0.md).
The first fixture review is
[Decision Work Receipt Fixture Review](docs/conversation-understanding/decision-work-receipt-fixture-review-v0.md):
the receipt is useful as a work-trail shell, but still too thin to explain the
messy semantic story without later bounded interpretation. The phase decision
is
[Decision Work Receipt Decision Gate](docs/conversation-understanding/decision-work-receipt-decision-gate-v0.md):
keep the sparse receipt as an internal/workflow artifact and do not build a
parallel Work Receipt interpretation system yet. See
[Lolla Decision Trail Web Page Draft](docs/lolla-decision-trail-web-page-v0.md)
for the simple customer explanation and
[Decision Trail Readiness Audit](docs/conversation-understanding/decision-trail-readiness-audit-v0.md)
for the current gap between that vision and the information Lolla captures
today. The staged PR86-PR89 implementation bridge is
[Decision Trail PR86-PR89 PRD](docs/conversation-understanding/decision-trail-pr86-pr89-prd-v0.md).
PR86 now defines the report contract in
[Decision Trail Report PRD](docs/conversation-understanding/decision-trail-report-prd-v0.md)
and the machine-readable
[Decision Trail Report Schema](docs/conversation-understanding/decision-trail-report-v0.json).
PR87 implements the conservative read-only exporter described in
[Decision Trail Read-Only Exporter](docs/conversation-understanding/decision-trail-readonly-exporter-v0.md).
PR88's completed review is
[Decision Trail Export Fixture Review](docs/conversation-understanding/decision-trail-export-fixture-review-v0.md):
the report is useful as a custody and missingness shell, but checked-in-safe
evidence remains too thin for the full Decision Trail product without later
bounded interpretation. PR89's
[Decision Trail Interpretation Gap Decision](docs/conversation-understanding/decision-trail-interpretation-gap-decision-v0.md)
selects narrow offline LLM specialist contracts as the next move, while keeping
runtime integration, broad IR work, judging, scoring, and automatic labels
deferred.
The PR90 implementation handoff is preserved as
[PR90 Decision Trail Goal Prompt](docs/conversation-understanding/decision-trail-pr90-goal-prompt-v0.md).
PR90's completed local contract surface is
[Decision Trail Specialist Contracts](docs/conversation-understanding/decision-trail-specialist-contracts-v0.md).
PR91 adds the local read-only packetization surface:
[Decision Trail Specialist Packet Builder](docs/conversation-understanding/decision-trail-specialist-packet-builder-v0.md).
PR92 adds the local trap-fixture checkpoint:
[Decision Trail Specialist Trap Set](docs/conversation-understanding/decision-trail-specialist-trap-set-v0.md).
PR93 adds the local discipline dry run:
[Decision Trail Specialist Dry Run](docs/conversation-understanding/decision-trail-specialist-dry-run-v0.md).
PR94 adds the local path decision:
[Decision Trail Specialist Path Decision](docs/conversation-understanding/decision-trail-specialist-path-decision-v0.md).
PR95 adds the explicit local-private packet mode:
[Decision Trail Local-Private Packet Mode](docs/conversation-understanding/decision-trail-local-private-packet-mode-v0.md).
PR96 smoke-reviews that mode:
[Decision Trail Local-Private Packet Smoke Review](docs/conversation-understanding/decision-trail-local-private-packet-smoke-review-v0.md).
PR97 runs the tiny local-private specialist-output pilot:
[Decision Trail Local-Private Specialist Output Pilot](docs/conversation-understanding/decision-trail-local-private-specialist-output-pilot-v0.md).
PR98 reviews that pilot and blocks broadening until a contract/packet patch:
[Decision Trail Specialist Output Pilot Review](docs/conversation-understanding/decision-trail-specialist-output-pilot-review-v0.md).
PR99 applies that patch:
[Decision Trail Specialist Contract And Packet Patch](docs/conversation-understanding/decision-trail-specialist-contract-and-packet-patch-v0.md).
PR100 uses the patched shape for one more one-case pilot:
[Decision Trail Second One-Case Specialist Pilot](docs/conversation-understanding/decision-trail-second-one-case-specialist-pilot-v0.md).
PR101 compares PR97 and PR100 before any broader specialist-output work:
[Decision Trail Specialist Pilot Comparison Gate](docs/conversation-understanding/decision-trail-specialist-pilot-comparison-gate-v0.md).
PR102 uses the one allowed diversity-targeted pilot:
[Decision Trail Third One-Case Diversity Pilot](docs/conversation-understanding/decision-trail-third-one-case-diversity-pilot-v0.md).
PR103 closes the one-case pilot phase:
[Decision Trail Specialist Pilot Phase Closure Gate](docs/conversation-understanding/decision-trail-specialist-pilot-phase-closure-gate-v0.md).
PR104 packages the closed pilot phase for later human correction:
[Decision Trail Human Review Intake Packet](docs/conversation-understanding/decision-trail-human-review-intake-packet-v0.md).

Current Decision Trail status: this is still offline evidence and packet
machinery, not automatic skill behavior. A normal Lolla run does not trigger
the Product Delta eval lane, the Decision Trail exporter, or specialist
interpretation. PR95 lets an operator explicitly build local-private packets
from completed run directories for later review. PR96 shows that metadata-only
packets work over real completed runs and that include-text packets work
mechanically while marking themselves unsafe for commit. PR97 shows one
operator-selected local-private include-text packet can support all four PR90
specialist-output shapes by checked-in summary only: conversation shape, likely
action, friction/lost value, and conservative fan-in.

This is still one-case, Codex-assisted, unvalidated, and not product proof. It
does not fill a first-class Decision Trail automatically, does not run inside
`$lolla`, and does not authorize agents. PR99 patches the specialist contracts
and packet metadata with source-scope, truncation, vanilla-overlap, lost-value
severity, assistant-influence source-status, fan-in downgrade-trigger, and
local-private retention-policy fields. PR100 then uses the patched shape on one
additional case and records a more conservative partial-usefulness read because
the vanilla conversation already contained much of the visible action sequence.
PR101 compares PR97 and PR100 and decides broad specialist-output batches are
still not ready. The only allowed continuation is at most one
diversity-targeted third one-case pilot in a different decision family; if no
safe diverse run exists, pause instead of forcing evidence. PR102 uses that
one diversity-targeted pilot on the `deploy-assisted-intake-routing` case and
recommends a closure gate before any fourth pilot or broad batch. PR103 closes
that phase: no fourth one-case pilot, no broad batch, and no runtime
integration. PR104 packages the three pilots into a future-human-review intake
packet with blank correction fields. The next responsible move is pause until
human review capacity returns.

Start here: **[Product Delta / Eval Docs Index](docs/evals/README.md)**.

**Trigger phrases** (the skill also activates on these):
- "audit this", "check my reasoning", "find blind spots"
- "stress test", "what am I missing", "challenge this"
- "devil's advocate", "what are we not seeing", "pre-mortem"

## Requirements

- **Python 3.10+** (uses stdlib only, no pip dependencies)
- **OpenRouter API key** (for LLM inference via calibrated prompts)
- **Optional:** OpenAI API key (enables semantic embedding search for richer companion matching)
- **Orchestrator model:** Claude Opus 4.7 recommended. Sonnet 4.6 is acceptable with mild phrasing regressions. Haiku is below the floor — it has been observed to skip critical artifact-persistence steps while generating plausible-looking output for the steps that did not run. The preamble asks the orchestrator to self-identify and refuse if it is Haiku; see [Architecture and Evolution §Model Requirements](docs/how-it-works/architecture-and-evolution.md#model-requirements) for details.

## What's Inside

```
lolla-skill/
├── SKILL.md              # Skill definition (Claude Code/Codex reads this)
├── HOW_IT_WORKS.md       # Full technical reference
├── engine/system_b/      # Bundled pipeline engine (stdlib runtime, zero pip dependencies)
├── data/                 # Knowledge graph, curation layers, embeddings
│   └── curated/          # Compiled substrate files (bundle selector, signal lexicon)
├── scripts/
│   ├── run_extract.py      # Step 2: conversation → decision structure (capture-critical gate, quote-fabrication retry, truncation transparency)
│   ├── run_pipeline.py     # Step 3: decision structure → four-lane audit (family-clustered Pass 1, run_health envelope)
│   ├── render_memo.py      # Deterministic markdown memo from result.json (no LLM)
│   ├── archive_run.py      # Local archive + agent_result.json + evaluation.json + reasoning_trace.json custody manifest
│   ├── export_reasoning_trace_dataset.py # Local JSONL corpus + summary from archived traces
│   ├── export_review_corpus.py # Local JSONL run-envelope corpus + human-review template
│   ├── evals/               # Read-only Product Delta eval helpers and boundary lint
│   └── stability_check.py  # Diagnostic harness (Mode A aggregate / Mode B pipeline-variance / Mode C extraction-drift)
├── docs/evals/            # Evaluation doctrine, Product Delta evidence docs, manifests, and review protocols
├── observatory/          # Local web UI — four cards, revised answer, reasoning graph, run health, pipeline inspector
├── references/           # Tendency catalog, calibration, guardrails (loaded on demand)
└── tests/                # Unit tests (trigger sources, frame validation, fuzzy matching, BI context, memo rendering)
```

The engine runs entirely on Python stdlib. No virtual environment, no pip install, no external packages.

## How It Works

See **[HOW_IT_WORKS.md](HOW_IT_WORKS.md)** — the full technical reference covering the problem, architecture, knowledge substrate, step-by-step pipeline flow, quality doctrine, known limitations, and cost per run.

For a plain-language shareable overview, see **[Lolla: A Reasoning Audit Layer for AI Agents](docs/lolla-pitch-and-invitation.md)**.

For the current machine-readable handoff, see **[Lolla Agent Result Contract](docs/lolla-agent-result-contract.md)**.

For the June 2026 roadmap toward an agent-callable reasoning-audit harness, see **[PRD: Lolla As A Reasoning-Audit Harness](docs/lolla-reasoning-audit-harness-prd.md)**.

For how Lolla can fit beside CrabTrap-style proxies, guardrails, approval systems, sandboxes, identity scopes, and trace stores, see **[Agent Control Layers And Lolla Integration](docs/agent-control-layers-and-lolla-integration.md)**.

For the eval doctrine behind that roadmap, see **[Lolla Evaluation Methodology](docs/lolla-evaluation-methodology.md)**.

For the offline Product Delta evidence lane, including what to run, what to
inspect, and what not to infer, see **[Product Delta / Eval Docs Index](docs/evals/README.md)**.

## Cost

A typical default audit makes ~50-85 OpenRouter calls, with optional OpenAI embedding calls when `OPENAI_API_KEY` is set:

- **OpenRouter:** ~18-25 calls for extraction and the four pipeline lanes, plus one Bullshit Index call per audited passage (often ~30-60 on long answers).
- **OpenAI:** optional embeddings + query expansion through the model retrieval layer; usually well under $0.01.
- **Anthropic:** no calls in the default flow. Step-7 pressure-check sub-agents are rested by default and only add Anthropic usage when the user/operator explicitly enables deeper-review mode.

Default-run cost is typically dominated by OpenRouter and is printed in the final receipt. Optional deeper-review mode can add a larger Anthropic line depending on which Claude model the orchestrator runs.

Every run produces a self-describing `usage_summary` block in the result JSON with per-vendor cost, per-stage call counts, prompt-cache hit rate, and the version date of the price table. Three places to read it:
- Visual: `http://localhost:8080/usage` (when the Observatory is running)
- API: `GET http://localhost:8080/api/case/<case_id>/usage`
- Raw: `jq .usage_summary /tmp/lolla_<run_id>_result.json`

Full doc: **[docs/cost-and-telemetry.md](docs/cost-and-telemetry.md)** — single source of truth for what's measured, where it lives, how to bump prices, and how to add a new vendor or stage.

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
- [supermemory](https://github.com/supermemoryai/supermemory) — Extraction pipeline patterns (relationship typing, deduplication, conversation capture) informed our conversation-to-ConversationContext extraction design.
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
- **Deeper conversation interpretation.** There's more signal in conversational dynamics — how positions shift across turns, where the human pushed back and the LLM folded, where concerns were raised and then quietly dropped. The current Decision Trail lane is approaching this carefully: deterministic code prepares custody-safe packets, while messy interpretation remains future bounded LLM specialist work rather than deterministic guessing.
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
