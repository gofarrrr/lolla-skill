# Lolla repository guidance

This file applies to the entire repository. It is the cold-start handoff for
agents and developers. Keep it current when a development goal changes the
project boundary or the next decision.

## Product in one paragraph

Lolla is an experimental reasoning-pressure and audit system. It preserves a
rich conversation, uses LLMs to interpret its messy meaning, uses deterministic
machinery and a curated mental-model graph to introduce provenance-bearing
external pressure, asks a reasoner to reconsider that pressure, and records the
process. Lolla is designed to make another angle inspectable—not to guarantee a
better answer, certify reasoning quality, or remove human decision authority.

## Read first

Read these in order before proposing architecture or the next experiment:

1. `PROJECT_STATUS.md` and `docs/README.md` — the concise current product,
   lifecycle, authorization, and documentation map.
2. `docs/conversation-understanding/lolla-constitution-stage0-addendum-audit-2026-07-15.md`
   and `docs/evals/lolla-constitution-stage0-addendum-register-v1.json` — the
   current reachability, evidence, disposition, and Decision Trail coverage
   map. This is the controlling cold-start status.
3. `plans/lolla-post-stage0-addendum-restart-roadmap-2026-07-15.md` — the
   current gated sequence. Stage 1 begins with checked-in-safe truthfulness;
   later real-run, live-pressure, and architecture decisions require separate
   founder authorization.
4. `docs/conversation-understanding/lolla-stage0-6-long-conversation-truthfulness-result-2026-07-15.md`
   — the current source-coverage correction: complete source custody is
   distinct from the partial initial extraction view above 80,000 characters.
5. `docs/product/lolla-mental-model-atlas-and-teacher-prd-v1.md` and
   `plans/lolla-mental-model-atlas-tracer-bullet-plan-2026-07-15.md` — the
   prospective founder-selected public Atlas/Teacher job and its provider-free
   gated implementation plan. This does not unpark Teacher or authorize the
   first tracer bullet.
6. `docs/conversation-understanding/lolla-product-constitution-v5.md` — binding
   future-development rules. Earlier constitutions are immutable historical
   evidence, not the current contract.
7. `README.md`, `HOW_IT_WORKS.md`, `SKILL.md`, and `docs/skill/STEPS.md` — the
   public orientation and ordinary live-skill behavior.
8. `docs/conversation-understanding/lolla-current-state-constitutional-audit-2026-07-13.md`
   — ground-up product and architecture assessment, including the defects R1
   and R2 repaired.
9. `docs/conversation-understanding/lolla-r4-product-architecture-closeout-2026-07-14.md`
   and `plans/lolla-r4-product-architecture-closeout-plan-2026-07-14.md` — the
   decision that stopped the incremental R4 reader while preserving the live
   pressure path, bounded sidecars, and research evidence.
10. `docs/conversation-understanding/lolla-r4-separated-surface-execution-a2-result-2026-07-14.md`
   and `plans/lolla-r4-separated-surface-execution-a2-plan-2026-07-14.md`
   — immutable final R4 evidence and the frozen
   `separated_tasks_ineffective_companions_persist` decision.
11. `docs/conversation-understanding/lolla-r4-separated-surface-execution-result-2026-07-14.md`
   and `plans/lolla-r4-separated-surface-execution-a1-plan-2026-07-14.md`
   — immutable A1 first-failure evidence and frozen
   `semantic_result_not_evaluable` decision. Do not combine A1 calls with A2.
12. `docs/board/decision-work-sidecar-internal-v1-current-state.md` and
   `docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.md`
   — the implemented sidecar boundary and the richer, still-provisional
   interpretation target.

Older PRDs, research branches, and historical result files remain valuable,
but do not treat their proposals as current runtime behavior. Follow the newest
explicit status and preserve frozen historical evidence.

## Binding way to think about the system

Keep this boundary visible in every design:

```text
LLMs interpret messy conversational meaning.
Deterministic code owns identity, custody, exact evidence, bounds, replay,
budgets, graph traversal, and ledgers.
The graph introduces pressure; it does not certify relevance.
The reconsidering reasoner may apply, reject, or park pressure.
The receipt proves what process occurred, not that the result is wise.
The human owns the decision and its consequences.
```

Consequences:

- Do not build keyword, turn-count, chronology, or nested deterministic gates
  to decide semantic role, relevance, materiality, relationship meaning, or
  answer quality.
- Do not let a probabilistic applicability pass silently delete bounded graph
  candidates before the reconsidering reasoner can inspect them. That is the
  Constitution-v5 product evil: probabilistic re-domestication of independent
  pressure.
- Bounded context is necessary, but compactness must not erase custody. Keep
  the complete available conversation authoritative and declare every
  processing view and omission separately.
- Preserve `complete`, `completed_zero`, `partial`, `failed`, and `missing` as
  different states. Absence of a reader result is not semantic stand-down.
- Preserve overlap and disagreement. Do not merge, rank, or vote away distinct
  provider-authored interpretations merely to make the output cleaner.
- A strict schema proves shape, not semantic correctness. A clean receipt is
  not a quality badge. Never collapse the evaluation vector into one score.
- The desired pressure may be strange, weak, or rejected. Success is not
  forcing the LLM to use it; success is making it inspectable and preserving
  the disposition.

## Working method

- Start every goal from the constitution, the current roadmap stage, and one
  falsifiable question. Prefer one causal change over an architectural bundle.
- Take initiative on provider-free implementation, fixtures, validation,
  documentation, and gardening. Do not ask the founder to approve every small
  step. Stop when a product judgment, new provider spend, or material scope
  expansion genuinely requires the founder.
- Explain progress in plain language: what we changed, why, what it showed,
  what remains unknown, cost, and the next decision. Ask one founder question
  at a time.
- Label evidence honestly: development fixture, simulated conversation,
  provider output, human source-first target, local structural result, or real-
  user evidence. Polished simulations test reliability mechanics; they do not
  prove genuine user usefulness.
- Simulated conversations should resemble difficult, ambiguous, multi-turn
  human/LLM work to the greatest practical degree. Do not use tiny polished
  dialogues as a proxy for long-conversation performance unless the tested
  claim is explicitly narrow.
- When prompt, model, schema, provider, context-window, or reasoning-envelope
  work becomes nontrivial or produces dubious results, check current official
  primary guidance and relevant maintained implementations before changing the
  architecture. Record the date, sources, adopted practices, rejected changes,
  and why. Search for known versions of persistent failures rather than
  repeatedly improvising locally.
- Prefer small, clearly delimited probabilistic jobs with explicit authority,
  source order, zero/ambiguous behavior, and local admission. Do not make the
  task small by stripping the context needed to interpret its meaning.
- Update the plan, result note, README/index, and this file when the handoff
  changes. A new machine or agent should not need chat history to resume.

## Provider, key, cost, and privacy rules

- Provider calls are never implied by “continue,” “go,” a green local test, or
  the existence of a runner. Require an explicit founder authorization tied to
  an exact frozen contract, cases, call maximum, and USD ceiling.
- Before authorization, freeze source and role hashes, a hidden source-first
  target, prompts, schemas, request previews, model/provider routing, seeds,
  output caps, cost estimate, stop rules, and the exact authorization shape.
- After authorization, make no automatic retry, semantic retry, fallback,
  response healing, premium-model substitution, evaluator call, or scope
  expansion unless the same exact authorization permits it. Preserve the first
  terminal result honestly.
- The retired R4 evidence preserves its historical Gemini/OpenRouter operator
  exactly. It is not a current experiment default or authorization. Any future
  provider-facing goal must recheck official model, route, price, privacy, and
  structured-output guidance and freeze a new exact operator contract.
- Embeddings use the direct OpenAI key (`OPENAI_API_KEY` or the explicitly
  supported Lolla alias), not the OpenRouter key. If the OpenAI key is absent,
  follow the documented provider-free/degraded path; do not silently redirect
  embeddings to another provider.
- Never print, commit, or copy `.env` values or secrets into artifacts. Store
  only declared routing policy, response/generation identity, usage custody,
  exact provider-reported cost when available, and safe hashes/redactions.
- Current prices, model behavior, schemas, and provider policies are unstable.
  Recheck official sources at the time of any future provider-facing change.

## Frozen evidence and repository discipline

- Do not rewrite historical experiment prompts, runners, source targets,
  authorizations, outputs, or closeouts. Add a prospective version and hash-lock
  the boundary instead.
- New downstream R4 artifacts that contain old case IDs must be explicitly
  excluded from the frozen corpus replay discovery, with a regression test, so
  later work cannot rewrite the historical 400-artifact inventory.
- Preserve user changes in dirty worktrees. Keep commits and stacked PRs
  narrow, explain their parent branch, and push restart-safe checkpoints.
- Use exact hashes, stable IDs, source aliases, speaker/turn provenance, and
  deterministic manifests for custody. Code may reject malformed custody; it
  may not repair meaning.
- Do not garden or archive historical files merely because they look old. First
  classify them as current entrypoint, immutable evidence, superseded proposal,
  generated artifact, or genuinely redundant material. Gardening is outside
  the current critical path unless confusion blocks development.

## Verification discipline

Run the smallest relevant checks while iterating, then the full suite before a
handoff or PR update. For the current Stage 0 public handoff:

```bash
PYTHONPATH=. python3 scripts/evals/validate_constitution_stage0_addendum_register.py --register docs/evals/lolla-constitution-stage0-addendum-register-v1.json
PYTHONPATH=. python3 scripts/evals/validate_stage0_public_handoff.py
PYTHONPATH=. pytest -q tests/test_run_extract.py tests/test_run_pipeline_contract_default.py tests/test_agent_result.py tests/test_constitution_stage0_addendum_register.py tests/test_stage0_public_handoff.py tests/test_r4_separated_surface_execution_a2.py
PYTHONPATH=. pytest -q
```

Also run `git diff --check` on the current change and validate changed JSON.
Do not rewrite frozen historical evidence merely to clean legacy whitespace.
The Stage 0 addendum publication passed 4,968 tests and all 93 subtests with one
existing `datetime.utcnow()` deprecation warning. A changed count is not
automatically a regression; unexplained failures or historical hash drift are.

## Current handoff — 2026-07-15

- R1 trust/capture/cost/privacy/custody hardening: complete provider-free.
- R2 constitutional graph survival: complete provider-free.
- R3 fresh-consumer work: honestly closed/deferred without meeting its semantic
  exit condition; do not reopen it casually.
- R4's incremental conversation-reader program is complete and stopped. The
  final A2 run preserved both genuine findings but separation did not suppress
  either opposite-surface companion; separated dependency calls also repeated
  governed-machinery false positives. The canonical scientific decision is
  `separated_tasks_ineffective_companions_persist`.
- The provider-free product decision is
  `stop_current_r4_reader_preserve_core_pressure_and_decision_trail`. Preserve
  R4 as immutable research evidence; do not import its residual or separated
  readers into the live skill, graph path, Decision Work semantic supply, or
  Observatory.
- Complete available user/assistant prose remains authoritative in
  `conversation.txt`. Processing views and semantic reads are derivative and
  must disclose omissions. Stage 0.6 repaired exact message accounting and
  propagation: above 80,000 characters, the initial extraction view is marked
  partial, health degrades as `extraction_processing_view_partial`, and
  `agent_result.source_coverage` preserves the exact window. The threshold and
  first-3-plus-last-15 policy remain unchanged; semantic adequacy is unproven.
- The live four-lane pressure engine, mental-model graph recall,
  constitutional graph-survival portfolio, and apply/reject/park custody remain
  the experimental core. They operate mechanically but have not established
  unique real-user usefulness.
- Decision Work remains an optional, post-run, operator-directed sidecar. Its
  packaging and read-only Observatory surfaces exist; trustworthy automatic
  semantic generation for arbitrary runs does not. Do not use R4 as that
  generator.
- The prospective Mental Model Atlas and Teacher v1 PRD now defines the
  previously missing founder-selected user job and a real-user evidence plan:
  a public 222-model Atlas, full model and exact directed relation pages, and
  curated learning journeys at the founder's visual-quality bar. Teacher
  remains `park` at this baseline. The PRD does not authorize its first local
  tracer bullet, full-corpus build, public deployment, provider call, runtime
  connection, or product-usefulness claim.
- The Stage 0 addendum was canonically published through PR #372 at merge
  `fc30bd944bfb91fbff0cc09190487997f3fe3185`. Its
  machine register assigns every canonical implementation file to an explicit
  lifecycle disposition and distinguishes live calls from artifact handoffs,
  optional hooks, offline paths, read-only projections, and absent links.
- Provider calls authorized for repository development: zero. A1 and A2 authorizations are
  consumed; A1 remains separate `semantic_result_not_evaluable` evidence. A2
  completed twelve calls for `$0.02148425`. No A3, retry, replacement, prompt
  tweak, model comparison, or integration is authorized.
- Runtime/graph integration, wider-corpus execution, model comparison,
  production-model selection, receipt claims, and scalar scoring: unauthorized.

The Stage 0.5 public-handoff gardening pass made the canonical map legible from
a fresh clone. Stage 0.6 then corrected deterministic long-conversation
source-coverage custody without changing prompts, providers, graph behavior,
or the semantic architecture. The next eligible product goal remains Stage 1:
a provider-free, checked-in-safe Decision Trail truthfulness review. Stage 1
is not authorized by these prerequisites. It may not inspect private archives,
generate a new semantic read, call a provider, automate the sidecar, change
runtime, reopen R4/R5, or claim product usefulness. Real-run review and
live-pressure usefulness remain later, separately authorized stages.
