# Lolla

A reasoning audit skill for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Captures your conversation, detects structural reasoning weaknesses, and returns counter-pressure from a curated substrate of 224 mental models.

Three independent audit lanes:

- **Structural Pressure** — detects cognitive tendencies distorting the reasoning
- **Model Companion** — recognizes mental models active in the reasoning
- **Frame Pressure** — audits how the question was framed

## Install

1. Clone this repo:

```bash
git clone https://github.com/your-org/lolla-skill.git
```

2. Symlink into your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills
ln -s /path/to/lolla-skill ~/.claude/skills/lolla
```

3. Add your OpenRouter API key (one of these options):

```bash
# Option A: Global config (works across all projects)
mkdir -p ~/.config/lolla
echo 'OPENROUTER_API_KEY=your-key-here' > ~/.config/lolla/.env

# Option B: Per-project (create in any project's .claude/ directory)
echo 'OPENROUTER_API_KEY=your-key-here' > .claude/lolla.env
```

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
├── engine/system_b/      # Bundled pipeline engine (58 files, zero dependencies)
├── data/                 # Knowledge graph, curation layers, embeddings
├── scripts/              # Pipeline scripts called by the skill
├── observatory/          # Local web UI for exploring results
├── references/           # Technical reference docs (loaded on demand)
└── tests/                # Test conversations
```

The engine runs entirely on Python stdlib. No virtual environment, no pip install, no external packages.

## How It Works

The skill is a pure orchestrator. Claude captures the conversation and calls the pipeline scripts. All semantic judgment (triage, scoring, fingerprinting, deep checks) runs through OpenRouter via calibrated prompts against the curated knowledge substrate.

The knowledge substrate is built from 224 canonical articles on mental models, each curated across five waves: activation semantics, failure modes, relationship edges, reframing patterns, and prerequisite orderings.

For the full technical reference, see `references/how-it-works.md`.

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key for LLM inference |
| `OPENAI_API_KEY` | No | Enables semantic embedding search |
| `LOLLA_OPENROUTER_MODEL` | No | Override model (default: `x-ai/grok-4.1-fast`) |

## License

MIT
