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

1. `docs/conversation-understanding/lolla-product-constitution-v5.md` — binding
   future-development rules. Earlier constitutions are immutable historical
   evidence, not the current contract.
2. `docs/conversation-understanding/lolla-r4-product-architecture-closeout-2026-07-14.md`
   and `plans/lolla-r4-product-architecture-closeout-plan-2026-07-14.md` — the
   current product boundary. The incremental R4 reader is stopped; complete
   conversation custody, live mental-model pressure, the optional Decision Work
   sidecar, and Observatory remain distinct preserved layers. The next product
   question is a provider-free artifact-to-Decision-Trail coverage audit.
3. `docs/conversation-understanding/lolla-current-state-constitutional-audit-2026-07-13.md`
   — ground-up product and architecture assessment, including the defects R1
   and R2 repaired.
4. `plans/lolla-post-v1-constitution-aligned-roadmap-2026-07-13.md` — current
   ordered development sequence and decision gates.
5. `docs/conversation-understanding/lolla-r4-separated-surface-execution-a2-result-2026-07-14.md`
   and `plans/lolla-r4-separated-surface-execution-a2-plan-2026-07-14.md`
   — canonical final R4 evidence: the complete twelve-call run, raw-before-target
   checkpoint, record-level source-first review, consumed authorization, and
   frozen `separated_tasks_ineffective_companions_persist` decision.
6. `docs/conversation-understanding/lolla-r4-separated-surface-execution-result-2026-07-14.md`
   and `plans/lolla-r4-separated-surface-execution-a1-plan-2026-07-14.md`
   — immutable A1 first-failure evidence and frozen
   `semantic_result_not_evaluable` decision. Do not combine A1 calls with A2.
7. `docs/conversation-understanding/lolla-r4-separated-surface-experiment-design-result-2026-07-14.md`
   and `plans/lolla-r4-separated-surface-experiment-design-plan-2026-07-14.md`
   — canonical provider-free design: hash-bound human review, protected target,
   twelve exact paired/separated requests, target-blind runner, categorical
   decision matrix, and cost custody.
8. `docs/board/decision-work-sidecar-internal-v1-current-state.md` and
   `docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.md`
   — the implemented sidecar boundary and the richer, still-provisional
   interpretation target.
9. `README.md`, `HOW_IT_WORKS.md`, `SKILL.md`, and `docs/skill/STEPS.md` when
   changing the live skill or explaining current user-facing behavior.

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
- LLM judgment calls use Gemini through OpenRouter for the current R4 contract.
  The pinned operator is `google/gemini-3.1-flash-lite` through
  `google-vertex`, with fallbacks off, required parameters, data collection
  denied, and ZDR requested. Do not use Gemini 3.5 Flash for routine testing.
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
handoff or PR update. For the current R4 package:

```bash
PYTHONPATH=. python3 scripts/evals/build_r4_residual_task_contract.py --validate-only
PYTHONPATH=. python3 scripts/evals/build_r4_matched_holdout_v2_contract.py --validate-only
PYTHONPATH=. python3 scripts/evals/run_r4_matched_holdout_v2_experiment.py --dry-run
PYTHONPATH=. python3 scripts/evals/seal_r4_matched_holdout_v2_execution_a1.py --validate-only
PYTHONPATH=. python3 scripts/evals/finalize_r4_matched_holdout_v2_execution_a1.py --validate-only
PYTHONPATH=. python3 scripts/evals/seal_r4_separated_surface_execution_a1.py --validate-only
PYTHONPATH=. python3 scripts/evals/finalize_r4_separated_surface_execution_a1.py --validate-only
PYTHONPATH=. python3 scripts/evals/seal_r4_separated_surface_execution_a2.py --validate-only
PYTHONPATH=. python3 scripts/evals/finalize_r4_separated_surface_execution_a2.py --validate-only
PYTHONPATH=. python3 scripts/evals/build_r4_matched_residual_holdout_contract.py --validate-only
PYTHONPATH=. python3 scripts/evals/run_r4_matched_residual_holdout_experiment.py --dry-run
PYTHONPATH=. python3 scripts/evals/build_r4_semantic_distinction_contract.py --validate-only
PYTHONPATH=. python3 scripts/evals/run_r4_semantic_distinction_experiment.py --dry-run
PYTHONPATH=. python3 scripts/evals/finalize_r4_semantic_distinction_execution.py --validate-only
PYTHONPATH=. pytest -q tests/test_r4_separated_surface_execution_a2.py tests/test_r4_separated_surface_execution_a1.py tests/test_r4_separated_surface_experiment.py tests/test_r4_separated_surface_target.py tests/test_r4_separated_surface_source_freeze.py tests/test_r4_matched_holdout_v2_execution_a1.py tests/test_r4_matched_residual_holdout.py tests/test_r4_matched_residual_holdout_v2.py tests/test_r4_residual_task.py tests/test_r4_residual_task_contract.py tests/test_r4_semantic_distinction.py tests/test_r4_semantic_distinction_contract.py tests/test_r4_semantic_distinction_execution.py tests/test_r4_provider_free_corpus_replay.py
PYTHONPATH=. pytest -q
```

Also run `git diff --check` on the current change and validate changed JSON.
Do not rewrite frozen historical evidence merely to clean legacy whitespace.
At the 2026-07-14 separated-surface execution A2 publication, the focused
canonical verification passes 42 tests. The complete suite passes 4,966 tests
and all 93 subtests,
with one existing `datetime.utcnow()` deprecation warning. A changed count is
not automatically a regression; unexplained failures or historical hash drift
are.

## Current handoff — 2026-07-14

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
  must disclose omissions. The current live extraction is useful but is not a
  complete long-conversation representation.
- The live four-lane pressure engine, mental-model graph recall,
  constitutional graph-survival portfolio, and apply/reject/park custody remain
  the experimental core. They operate mechanically but have not established
  unique real-user usefulness.
- Decision Work remains an optional, post-run, operator-directed sidecar. Its
  packaging and read-only Observatory surfaces exist; trustworthy automatic
  semantic generation for arbitrary runs does not. Do not use R4 as that
  generator.
- Canonical `main` is `34d0e1a8f6e80d72622deb59b10a81262344fc85`, the
  merge of PR #370. A2's exact reviewed head is
  `a525e375f7c8b5076de5fd5fafac5f9e4d8da001`; raw evidence precedes protected
  review at `407109cd64be31c92efa31a76362091b2c5943a9`.
- Provider calls currently authorized: zero. A1 and A2 authorizations are
  consumed; A1 remains separate `semantic_result_not_evaluable` evidence. A2
  completed twelve calls for `$0.02148425`. No A3, retry, replacement, prompt
  tweak, model comparison, or integration is authorized.
- Runtime/graph integration, wider-corpus execution, model comparison,
  production-model selection, receipt claims, and scalar scoring: unauthorized.

The immediate operational decision is publication of the provider-free
architecture closeout without altering its decision. After canonical
publication, the next eligible product goal is a provider-free completed-run
artifact-to-Decision-Trail coverage audit. That audit may map existing
artifacts, sidecar fields, missingness, privacy, and human-review needs; it may
not generate a new semantic read, inspect private archives without explicit
scope, write a real sidecar, call a provider, change runtime, or claim product
usefulness. R5 and any materially different reader remain separate founder
decisions.

## Constitution Stage 0 addendum cold start — 2026-07-15

The current ground-up system map is
`docs/conversation-understanding/lolla-constitution-stage0-addendum-audit-2026-07-15.md`;
its machine register is
`docs/evals/lolla-constitution-stage0-addendum-register-v1.json`. The audit base
is canonical commit `f4493e20634544addd6633d8e92a836c6488f61e`. This section
supersedes older commit and next-goal statements above without rewriting their
historical custody.

The live system is a four-lane reasoning-pressure path with constitutional
graph survival, reconsideration/disposition custody, archive, receipts, and
read-only Observatory. Decision Trail, Product Delta, portable views, and
Decision Work are bounded offline, operator, or default-off paths. Teacher and
general Decision Work semantic generation are parked. R3/R4 are research-only;
the incremental R4 reader is retired and has no live or automatic Decision Work
supply path. Real-user usefulness remains unknown.

The only next founder decision is whether to publish the addendum and
separately authorize its provider-free checked-in-safe Decision Trail
truthfulness gate. Provider calls, private-archive inspection, a new reader,
runtime change, R4/R5, model comparison, automation, and integration remain
unauthorized.
