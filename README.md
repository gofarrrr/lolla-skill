# Lolla

**A reasoning audit for AI advice.**

Lolla is the layer you run after an AI answer sounds good enough to trust.
It captures the conversation, pressure-tests the reasoning, asks what the
answer skipped, forces a revised position, and preserves the whole run as a
local artifact you can inspect later.

The name comes from Charlie Munger's "Lollapalooza effect": bad judgment often
does not come from one bias. It comes from several forces compounding until a
confident answer feels inevitable. Lolla looks for those compounds in AI
reasoning.

## The Simple Idea

AI makes polished answers cheap. That is useful, but it creates a new problem:
the answer can sound finished before the thinking is finished.

Lolla adds a second pass with a different job:

- The first model gives advice.
- Lolla asks where that advice is structurally fragile.
- The assistant must then say what survived, what it would take back, and what
  actually changed.

It is not a fact checker, a second consultant, or a longer prompt. It is a
reasoning audit: a system for finding missing reversal conditions, inherited
assumptions, weak frames, untested constraints, and gaps that only become
visible when you challenge the structure of the answer.

## When To Use It

Run Lolla when the conversation contains strategic advice you might act on:

- career decisions
- startup pivots
- legal or compliance reporting sequences
- hiring and org design
- product strategy
- investment or vendor decisions
- architectural tradeoffs
- any advice where "this sounds right" is not enough

Do not use it for simple coding help, factual lookup, creative drafting, or
cases where there is no material decision being shaped by the answer.

## What Happens In A Run

At a high level, every run does four things:

1. **Capture the conversation.** Lolla saves the relevant user and assistant
   turns into a run-specific scratch file.
2. **Extract the decision shape.** It identifies the decision, constraints,
   open threads, original framing, and assistant position.
3. **Run four independent audit lanes.** The system checks cognitive pressure,
   active mental models, hidden framing, and missing structural territory.
4. **Force reconsideration and preserve evidence.** The assistant writes a
   revised position, a memo is rendered, Observatory opens locally, and the run
   is archived with traces, health, cost, and custody metadata.

The user-facing output is deliberately small:

- a short readback of what was captured
- the strongest case against the original answer
- an updated position with what survived, what changed, and what was taken back
- a memo path
- an Observatory URL for the full breakdown
- a local archive path

The deeper machinery stays in the archive and Observatory.

## The Four Lanes

| Lane | Plain question | What it contributes |
| --- | --- | --- |
| Structural Pressure | What cognitive tendency may be distorting the reasoning? | Challenge statements, reversal triggers, corrective pressure |
| Model Companion | What mental models are already active or being violated? | Failure modes, premortem questions, useful lenses |
| Frame Pressure | What did the user's framing make too easy to accept? | Alternative questions and suppressed counterfactuals |
| Structural Coverage | What important decision territory did the answer never enter? | Gap dimensions and user-answerable discovery questions |

Each lane is independent. That separation matters: one lane can challenge the
answer, another can deepen it, another can challenge the question, and another
can show what was never addressed.

## What Makes It Different

Lolla is built around one architectural split:

**LLMs read language at the edges. Curated structure governs the middle.**

The probabilistic parts detect reasoning shape, extract frames, verify mental
model use, and generate situation-specific questions. The deterministic middle
routes those detections through a curated substrate of:

- 222 mental models
- 25 cognitive tendencies
- 241 tendency-to-model antidote bindings
- 1,358 relationship edges between models
- source-backed V60 affordance and absence records

That lets the system be flexible where language is messy and strict where
traceability matters.

## Newer Run-Capture Machinery

Recent runs preserve more than the final answer. Each run now has:

- collision-resistant run IDs such as `20260623T113203Z_c4df83`
- run-specific env files so stale `/tmp/lolla_latest_env.sh` pointers cannot
  silently mix runs
- expected-run guards before major model calls and artifact writes
- live-output hygiene checks that catch public transcript contamination
- run-event ledgers for restarts, pins, aborts, and recovery actions
- graph survival reports that preserve selected, suppressed, and
  budget-suppressed reasoning lenses
- `reasoning_trace.json`, a local custody manifest for eval-style review
- optional `user_usefulness_review.json` and `outcome_review.json` slots for
  later feedback

The goal is not just "get a better answer." The goal is to make the reasoning
process inspectable after the moment has passed.

## Install

1. Clone this repo:

```bash
git clone https://github.com/gofarrrr/lolla-skill.git
```

2. Symlink it into your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills
ln -s /path/to/lolla-skill ~/.claude/skills/lolla
```

3. Add your API keys:

```bash
mkdir -p ~/.config/lolla
cat > ~/.config/lolla/.env << 'EOF'
OPENROUTER_API_KEY=your-openrouter-key-here
OPENAI_API_KEY=your-openai-key-here  # optional
EOF
```

Only `OPENROUTER_API_KEY` is required. `OPENAI_API_KEY` enables embedding-based
retrieval redundancy; the system still works without it.

4. Restart Claude Code. The `/lolla` command is now available.

## Usage

In a Claude Code conversation where you want to audit strategic advice, run:

```text
/lolla
```

You can also trigger it with phrases such as:

- `audit this`
- `check my reasoning`
- `find blind spots`
- `stress test this`
- `what am I missing?`
- `devil's advocate`
- `pre-mortem`

Completed runs are archived locally under:

```text
~/.local/share/lolla/runs/
```

To export archived `reasoning_trace.json` manifests into a local JSONL corpus:

```bash
python3 scripts/export_reasoning_trace_dataset.py \
  ~/.local/share/lolla/runs \
  --out /tmp/lolla_reasoning_traces.jsonl \
  --summary-out /tmp/lolla_reasoning_traces_summary.json
```

## Requirements

- Python 3.10+
- OpenRouter API key
- Optional OpenAI API key for embedding retrieval
- Claude Opus 4.7 recommended as orchestrator
- Claude Sonnet 4.6 acceptable with slightly noisier prose and higher need to
  inspect run health
- Haiku is below the floor because it has been observed to skip artifact steps
  while producing plausible-looking output

## Cost

A normal default run usually costs a few cents. Recent real runs have landed
around `$0.04-$0.07`, depending on transcript size, the number of deep checks,
and the Bullshit Index passage count.

Default runs use OpenRouter for extraction and audit calls. OpenAI embedding
costs are tiny when enabled. The post-Step-6 pressure-check sub-agents are
default-off; if explicitly enabled, they run through Claude Code and can become
the dominant cost line.

Every run writes a `usage_summary` block into:

```text
/tmp/lolla_<run_id>_result.json
```

Read it through:

- Observatory: `http://localhost:8080/usage`
- API: `GET http://localhost:8080/api/case/<case_id>/usage`
- Raw JSON: `jq .usage_summary /tmp/lolla_<run_id>_result.json`

See [docs/cost-and-telemetry.md](docs/cost-and-telemetry.md) for the canonical
cost reference.

## Documentation Map

Start here:

- [HOW_IT_WORKS.md](HOW_IT_WORKS.md) - the readable system story
- [docs/how-it-works/problem-and-thesis.md](docs/how-it-works/problem-and-thesis.md) - why Lolla exists
- [docs/how-it-works/live-flow.md](docs/how-it-works/live-flow.md) - exact `/lolla` runtime flow
- [docs/how-it-works/pipeline-lanes.md](docs/how-it-works/pipeline-lanes.md) - lane internals
- [docs/how-it-works/knowledge-substrate.md](docs/how-it-works/knowledge-substrate.md) - curated model substrate
- [docs/how-it-works/operations-and-limits.md](docs/how-it-works/operations-and-limits.md) - operational doctrine and failure modes
- [docs/how-it-works/architecture-and-evolution.md](docs/how-it-works/architecture-and-evolution.md) - architecture and migration history
- [docs/cost-and-telemetry.md](docs/cost-and-telemetry.md) - cost and telemetry

## Repository Layout

```text
lolla-skill/
├── SKILL.md              # Claude Code skill instructions
├── HOW_IT_WORKS.md       # Public system overview
├── engine/system_b/      # Pipeline engine
├── data/                 # Knowledge graph, curated substrate, embeddings
├── scripts/              # Capture, pipeline, memo, archive, export tools
├── observatory/          # Local breakdown UI
├── docs/                 # Public explanatory docs
├── references/           # Operator and prompt-surface contracts
└── tests/                # Unit and regression tests
```

The engine uses Python stdlib only. No virtual environment is required for the
core skill path.

## Contributing

The most useful contributions are practical:

- Run the system on real strategic advice and report where the audit helped or
  missed.
- Add high-quality eval cases.
- Improve the curated model substrate from primary sources.
- Tighten docs where the public story and the code drift apart.
- Challenge the architecture when the trust boundary is unclear.

Lolla is a working system, but it is still early. The right posture is the one
the tool itself tries to teach: use it, inspect it, pressure-test it, and make
the reasoning better.

## License

MIT
