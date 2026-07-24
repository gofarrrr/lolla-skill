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

## New human or AI coder

This GitHub repository is the complete current project authority. A fresh clone
does not need chat history, the founder's machine, another checkout, or provider
credentials to understand and validate the current graph and skill package.
Start with [AGENTS.md](AGENTS.md), which gives a short universal cold start and
then routes graph, skill, Atlas, Decision Work, and research tasks to their own
evidence. Do not infer current work from `PROGRESS.md`, `TODOS.md`, an old PRD,
or a dated result's “next step”; those files preserve historical reasoning.

The foundational graph and Atlas checkpoint is
[PR #379](https://github.com/gofarrrr/lolla-skill/pull/379). The current public
handoff and live-skill contract is [PR #380](https://github.com/gofarrrr/lolla-skill/pull/380).

## Current status

| Area | Lifecycle | What that means |
|---|---|---|
| Four-lane pressure skill | **LIVE / EXPERIMENTAL** | Implemented ordinary path; semantic and human value remain under evaluation. |
| Conversation and live-host custody | **LIVE / BOUNDED** | One exact run handle survives fresh shells. Conversation, narration, revised prose, disposition judgments, memo fields, and exceptional receipt overrides use private runtime standard input only after an explicit no-echo readiness signal. Schema-owned packets replace ordinary ad hoc artifact dumps. Complete available user/assistant prose is authoritative; above 80,000 characters, initial extraction uses a declared partial view. |
| Deterministic custody and graph survival | **LIVE** | Owns identity, bounds, provenance, replay, budgets, ledgers, and pressure survival—not semantic truth. |
| Graph authoring and publication custody | **LIVE SOURCE / PROVIDER-FREE VALIDATION** | All 222 Markdown sources, reviewed curation, 1,358 rich authored directed relations, compiler inputs, one published read boundary, and the declared current pressure policy are repository-local and reproducible. Complete multi-path custody remains candidate-only. |
| Observatory | **BOUNDED / READ-ONLY** | Displays artifacts it can locate; it does not create meaning or authorize action. |
| Decision Trail and Product Delta | **BOUNDED / OFFLINE** | Read completed artifacts later; they do not influence the live answer. |
| Decision Work | **BOUNDED / OPERATOR-DIRECTED** | Validates and packages supplied interpretations; no trustworthy arbitrary-run semantic supplier exists. |
| Mental Model Atlas | **PARKED / CHECKED-IN PHASE 1 REVIEW** | A source-bound, undeployed interface candidate exists; founder visual, native screen-reader, rights, and real-user gates remain open. |
| Mental Model Teacher | **PARKED** | The wider lesson and learning-product journey is preserved but has not earned active product development. |
| R3/R4 conversation readers | **RESEARCH ONLY / RETIRED** | Evidence is preserved; the incremental R4 architecture must not supply live or Decision Work state. |
| Real-user usefulness | **UNKNOWN** | Mechanical tests and simulations do not establish customer value or better decisions. |

No repository-development provider experiment is currently authorized. Running the installed skill is a separate user-operated action that uses the user's own provider credentials and can incur cost.

## What happens in a live run

```text
available user/assistant prose
  -> private stdin capture + authoritative conversation.txt
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

In Codex, repository code can keep private payloads out of ordinary shell commands, patch previews, and raw diagnostic output. It cannot hide the host's own tool cards, so a clean curated narration remains `not_checked` unless a complete trusted host-visible capture is supplied. See the [Codex live-run boundary](docs/skill/CODEX_LIVE_RUN_BOUNDARY.md) and its [2026-07-24 provider-free repair evidence](docs/conversation-understanding/lolla-codex-live-run-boundary-repair-result-2026-07-24.md).

The optional passage-quality profile receives all available user-turn prose so it can distinguish user-stated facts from unsupported additions. That source context is repeated across up to twelve provider calls and may increase input tokens and cost. A missing passage judgment remains explicitly partial; it does not erase an otherwise complete core audit or make the result decision-ready.

See [HOW_IT_WORKS.md](HOW_IT_WORKS.md) for implementation boundaries and
[docs/README.md](docs/README.md) for lifecycle-organized documentation. In this
repository, “repository-published” means merged to the canonical GitHub branch;
it does not mean deployed, production-ready, rights-cleared, or proven useful.

## Install

Requirements:

- Python 3.13 or later for the documented and hosted verification path;
- a POSIX shell on macOS, Linux, or WSL (native Windows is not currently a
  documented path);
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

Before adding provider credentials, validate the entire packaged skill and
graph chain from the clone:

```bash
PYTHONPATH=. python3 scripts/evals/validate_self_contained_skill.py --validate-only
```

This check makes no provider or embedding calls. It validates the skill's
named files, 222 source documents, reviewed graph inputs, byte-equivalent
candidate compilation, published snapshot, all 163 frozen policy windows, and a bundled live
pipeline from an unrelated working directory with ambient Python paths disabled.

GitHub also runs this provider-free public-handoff gate on pull requests and
`main`. Contributors can reproduce its Python environment with
`requirements-dev.txt`; see [CONTRIBUTING.md](CONTRIBUTING.md).

Store credentials outside the repository, for example in
`~/.config/lolla/.env`:

```text
OPENROUTER_API_KEY=your-key
OPENAI_API_KEY=your-optional-embedding-key
```

Never commit that file. Current provider routes, model behavior, prices, and
privacy policies can change; verify the live operating docs before a
provider-facing run.

## Data, providers, and local archives

Before running Lolla on sensitive material, understand the data boundary:

- live semantic stages send captured conversation content or derived prompts
  to OpenRouter under the operator's credentials;
- optional embedding work sends its declared inputs directly to OpenAI and is
  not silently rerouted through OpenRouter;
- local archives may retain conversation prose, provider outputs, and custody metadata under `~/.local/share/lolla/runs/`; runtime setup and archive finalization keep directories `0700` and files `0600`;
- the provider-free readiness and public-handoff validators send nothing to a
  model or embedding provider;
- provider retention, routing, price, and privacy terms can change, so review
  the current [live-flow boundary](docs/how-it-works/live-flow.md) and
  [cost and telemetry contract](docs/cost-and-telemetry.md) before use.

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

The detailed live contract is [SKILL.md](SKILL.md), the step procedure is [docs/skill/STEPS.md](docs/skill/STEPS.md), and Codex operators should also follow the
[live-run transport boundary](docs/skill/CODEX_LIVE_RUN_BOUNDARY.md). Maintainers should use the
[knowledge-substrate operations reference](references/knowledge-substrate-operations.md)
for graph ownership, validation, and prospective/live boundaries.

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
claim. Missing, completed-zero, partial, failed, and complete states remain different. An attempted provider-backed call without usable output makes the run partial; the final receipt names the affected stage/check and preserves the no-retry boundary. `tool_calls: []` means no host tool stream was supplied to the trace builder, not that no tools ran. Owner-only local archives say nothing about provider egress or what the Codex interface displayed.

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

Stage 0.6 is complete. Nothing starts automatically. July's provider-free,
checked-in-safe Stage 1 truthfulness review is eligible but unstarted; it may
not inspect private archives, generate semantics, call providers, automate
Decision Work, reopen R4/R5, or change runtime behavior.
The separate June specialist program stopped after three Codex-assisted reads;
its PR104 principal-human packet remains blank and paused. Stage 1 tests interface honesty, not conversation meaning; see the [stage lineage](docs/conversation-understanding/lolla-decision-trail-stage-lineage-2026-07-22.md).

Separately, the provider-free Mental Model Atlas is consolidated around one
canonical identity path. A 16-model orientation view opens exact,
40-record-paged neighborhoods from all 222 canonical models and 1,358 authored
relations; model and relation identities survive route changes, while reviewed
teaching-page availability remains a separate card-first contract. The
Abstraction source is complete and presented through five source-bound human
chapters; the wider Teacher product remains partial and parked. The visual
system is deliberately achromatic precise editorial cartography. Frozen
fixtures and Canvas are explicit review-only paths, not competing ordinary
routes. See the current [Atlas custody V2 result](docs/product/lolla-mental-model-atlas-custody-v2-result-2026-07-22.md)
and the frozen [V1 publication checkpoint](docs/product/lolla-mental-model-atlas-baseline-publication-result-2026-07-17.md).
Its checked-in, undeployed first-viewport repair now awaits provider-free founder re-review,
not deployment, Phase 2, Teacher journeys, runtime links, provider use, or a
product-usefulness claim.

The graph-authoring recovery did not rewrite the frozen Atlas V1 packages. The
active Atlas now reads the V2 projection with current repository-local
custody. A recursive proof classifies all 2,182 V1/V2 differences as custody
fields and finds zero unexpected semantic, identity, layout, paging, or
interface changes. See the [custody V2 result](docs/product/lolla-mental-model-atlas-custody-v2-result-2026-07-22.md).

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
