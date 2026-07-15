# Lolla

**An experimental reasoning-pressure and audit skill for serious AI
conversations.**

Lolla preserves the available user/assistant exchange, introduces traceable
challenges through four reasoning-pressure lanes and a curated mental-model
graph, asks the reasoner to reconsider, and records what happened. Its purpose
is to make another angle and its disposition inspectable. It does not guarantee
a better answer, certify reasoning quality, or remove human decision authority.

The strongest demonstrated part of Lolla is its process custody: exact source
preservation within the declared prose boundary, provenance-bearing pressure,
graph-survival controls, apply/reject/park records, archive manifests, health,
cost, privacy, and read-only inspection. Real-user usefulness, market value,
and the claim that Lolla improves decisions remain unproven.

Read [PROJECT_STATUS.md](PROJECT_STATUS.md) before interpreting the rest of the
repository. It is the short canonical status. The full architecture and
evidence audit is the
[Constitution Stage 0 addendum](docs/conversation-understanding/lolla-constitution-stage0-addendum-audit-2026-07-15.md).

## Current status

| Area | Lifecycle | What that means |
|---|---|---|
| Four-lane pressure skill | **LIVE / EXPERIMENTAL** | Implemented ordinary path; semantic and human value remain under evaluation. |
| Conversation source custody | **LIVE / BOUNDED** | Preserves complete available user/assistant prose. Above 80,000 characters, initial extraction uses a declared partial view; later conversation-native pressure still loads the full source. |
| Deterministic custody and graph survival | **LIVE** | Owns identity, bounds, provenance, replay, budgets, ledgers, and pressure survival—not semantic truth. |
| Observatory | **BOUNDED / READ-ONLY** | Displays artifacts it can locate; it does not create meaning or authorize action. |
| Decision Trail and Product Delta | **BOUNDED / OFFLINE** | Read completed artifacts later; they do not influence the live answer. |
| Decision Work | **BOUNDED / OPERATOR-DIRECTED** | Validates and packages supplied interpretations; no trustworthy arbitrary-run semantic supplier exists. |
| Mental Model Atlas / Teacher | **PARKED / LOCAL PHASE 1 REVIEW** | The founder-selected Atlas job has a source-bound local tracer bullet; visual, native screen-reader, rights, and real-user gates remain open. |
| R3/R4 conversation readers | **RESEARCH ONLY / RETIRED** | Evidence is preserved; the incremental R4 architecture must not supply live or Decision Work state. |
| Real-user usefulness | **UNKNOWN** | Mechanical tests and simulations do not establish customer value or better decisions. |

No repository-development provider experiment is currently authorized. Running
the installed skill is a separate user-operated action that uses the user's own
provider credentials and can incur cost.

## What happens in a live run

```text
available user/assistant prose
  -> authoritative conversation.txt
  -> bounded initial-extraction view when needed (exact omissions recorded)
  -> provisional ConversationContext / ConversationIR
  -> four pressure lanes
       tendency pressure
       mental-model companion
       frame pressure
       structural coverage
  -> constitutional graph pressure survives probabilistic filtering
  -> reasoner applies, rejects, or parks active pressure
  -> revised answer + memo
  -> archive, manifests, health, usage/cost/privacy custody, receipt
  -> read-only Observatory projection
```

Graph recall is a hypothesis, not relevance proof. A strict schema proves
shape, not semantic correctness. A receipt proves that a process occurred, not
that the result is wise or safe.

See [HOW_IT_WORKS.md](HOW_IT_WORKS.md) for implementation boundaries and
[docs/README.md](docs/README.md) for lifecycle-organized documentation.

## Install

Requirements:

- Python 3;
- an OpenRouter key for the live LLM jobs;
- optionally, a direct OpenAI key for the documented embedding layer.

Clone and link the repository into the skill directory used by your agent:

```bash
git clone https://github.com/gofarrrr/lolla-skill.git
cd lolla-skill

# Claude Code
mkdir -p ~/.claude/skills
ln -s "$PWD" ~/.claude/skills/lolla

# Codex
mkdir -p ~/.codex/skills
ln -s "$PWD" ~/.codex/skills/lolla
```

Store credentials outside the repository, for example in
`~/.config/lolla/.env`:

```text
OPENROUTER_API_KEY=your-key
OPENAI_API_KEY=your-optional-embedding-key
```

Never commit that file. Current provider routes, model behavior, prices, and
privacy policies can change; verify the live operating docs before a
provider-facing run.

## Use

In Claude Code:

```text
/lolla
```

In Codex:

```text
$lolla
```

The skill is intended for conversations involving a material recommendation,
tradeoff, or strategic decision. It is not intended for coding tasks, simple
questions, or as the sole basis for medical, legal, financial, safety-critical,
or otherwise consequential action.

The detailed live contract is [SKILL.md](SKILL.md) and the step procedure is
[docs/skill/STEPS.md](docs/skill/STEPS.md).

## Outputs and boundaries

A completed run is archived locally under `~/.local/share/lolla/runs/` unless
the operator configures another archive directory. Typical outputs include:

- the captured conversation and declared capture boundary;
- provisional extraction and pressure artifacts;
- graph-survival and disposition records;
- revised answer and memo;
- run health, usage, cost, provider, and privacy custody;
- `agent_result.json`, `evaluation.json`, and `reasoning_trace.json`;
- a local read-only Observatory view.

`evaluation.json` is a deterministic artifact/readiness receipt, not an answer
score. `reasoning_trace.json` is custody metadata, not a hidden chain-of-thought
claim. Missing, completed-zero, partial, failed, and complete states remain
different.

For long runs, `conversation.txt` remains authoritative. A partial initial
extraction view is reported as degraded source coverage rather than being
misdescribed as truncation of the conversation itself. See the
[Stage 0.6 result](docs/conversation-understanding/lolla-stage0-6-long-conversation-truthfulness-result-2026-07-15.md).

## What the evidence established

Implemented and extensively mechanically tested:

- the live four-lane pressure path;
- deterministic mental-model identity and relationship graph traversal;
- constitutional survival of bounded graph pressure;
- apply/reject/park custody;
- archives, manifests, health, privacy, usage, and cost records;
- read-only and offline artifact projections;
- frozen experiment replay and evaluation custody.

Not established:

- that pressure is uniquely useful to real users;
- that a revised answer is better;
- that the system understands a full longitudinal conversation reliably;
- that Decision Work can automatically generate trustworthy semantic state;
- that the local Atlas tracer, parked Teacher, or retired R4 reader should be
  productized;
- production readiness or market demand.

The final R4 experiment recovered genuine findings but repeated unsafe false
positives even when the two semantic surfaces were requested separately. That
incremental reader architecture is retired, not hidden or renamed. Read the
[R4 closeout](docs/conversation-understanding/lolla-r4-product-architecture-closeout-2026-07-14.md)
for the decision and the [Stage 0 audit](docs/conversation-understanding/lolla-constitution-stage0-addendum-audit-2026-07-15.md)
for its place in the wider system.

## Current development gate

The provider-free Stage 0.6 source-coverage prerequisite is complete. The next
eligible product decision is whether to authorize Stage 1: a provider-free
truthfulness review of checked-in-safe Decision Trail material.
Stage 1 is not started by this README or by cloning the repository. It must not
inspect private archives, create a new semantic reader, call a provider,
automate Decision Work, reopen R4/R5, or change runtime behavior.

Separately, the Mental Model Atlas Phase 1 tracer bullet is implemented locally.
Its next decision is founder review of the checked-in visual truth packet. It
does not authorize public deployment, Phase 2, Teacher journeys, runtime links,
or provider use. See the
[Phase 1 result](docs/product/lolla-mental-model-atlas-phase1-visual-truth-tracer-bullet-result-2026-07-15.md).

See the
[post-Stage-0 restart roadmap](plans/lolla-post-stage0-addendum-restart-roadmap-2026-07-15.md).

## Contributing and reviewing

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Useful review at this stage
focuses on:

- whether current claims match reachable code and evidence;
- whether lifecycle labels are understandable;
- whether receipts distinguish process from quality;
- whether a completed record exposes missingness and authority honestly;
- which real user problem, if any, merits a consent-bound evidence gate.

Do not infer authorization for provider calls, historical branch cleanup,
automatic semantic generation, or product integration from an issue or pull
request.

## License

MIT
