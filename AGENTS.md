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
2. `docs/conversation-understanding/lolla-current-state-constitutional-audit-2026-07-13.md`
   — ground-up product and architecture assessment, including the defects R1
   and R2 repaired.
3. `plans/lolla-post-v1-constitution-aligned-roadmap-2026-07-13.md` — current
   ordered development sequence and decision gates.
4. `docs/conversation-understanding/lolla-r4-residual-false-positive-causal-diagnosis-2026-07-14.md`
   and `plans/lolla-r4-residual-false-positive-causal-diagnosis-plan-2026-07-14.md`
   — latest completed work, the five-record causal map, evidence against a
   general paired-completion explanation, competing falsifiers, and the one
   bounded diagnostic experiment earned without implementing or designing it.
5. `docs/conversation-understanding/lolla-r4-matched-holdout-v2-execution-result-2026-07-14.md`
   and `plans/lolla-r4-matched-holdout-v2-execution-a1-plan-2026-07-14.md`
   — exact eight-call execution custody, record-level
   source-first review, frozen decision, and next provider-free causal gate.
6. `docs/conversation-understanding/lolla-r4-matched-holdout-v2-leakage-correction-result-2026-07-14.md`
   and `plans/lolla-r4-matched-holdout-v2-leakage-correction-plan-2026-07-14.md`
   — frozen design evidence, the rejected v1 evidence, leakage-corrected v2
   sources and priors, hash-bound human review, protected target, matched
   requests, and the now-consumed non-authorizing contract.
7. `docs/conversation-understanding/lolla-r4-residual-task-identity-repair-result-2026-07-14.md`
   and `plans/lolla-r4-residual-task-identity-repair-plan-2026-07-14.md` — the
   published additive residual-discovery contract and frozen boundaries.
8. `docs/conversation-understanding/lolla-r4-semantic-distinction-causal-diagnosis-2026-07-14.md`
   — the record-level Case 01/04 map, competing causal explanations,
   falsifiers, and the single repair class that earned the latest work.
9. `docs/conversation-understanding/lolla-r4-semantic-distinction-execution-result-2026-07-14.md`
   — consumed holdout evidence, exact provider cost, and the semantic failure
   that the causal diagnosis explains.
10. `docs/conversation-understanding/lolla-r4-semantic-distinction-preparation-result-2026-07-14.md`,
   `plans/lolla-r4-semantic-distinction-plan-2026-07-14.md`, and
   `docs/conversation-understanding/lolla-r4-semantic-distinction-current-practice-2026-07-14.md`
   — the consumed frozen contract, completed R4 causal plan, and official-
   practice check behind it.
11. `README.md`, `HOW_IT_WORKS.md`, `SKILL.md`, and `docs/skill/STEPS.md` when
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
PYTHONPATH=. python3 scripts/evals/build_r4_matched_residual_holdout_contract.py --validate-only
PYTHONPATH=. python3 scripts/evals/run_r4_matched_residual_holdout_experiment.py --dry-run
PYTHONPATH=. python3 scripts/evals/build_r4_semantic_distinction_contract.py --validate-only
PYTHONPATH=. python3 scripts/evals/run_r4_semantic_distinction_experiment.py --dry-run
PYTHONPATH=. python3 scripts/evals/finalize_r4_semantic_distinction_execution.py --validate-only
PYTHONPATH=. pytest -q tests/test_r4_matched_holdout_v2_execution_a1.py tests/test_r4_matched_residual_holdout.py tests/test_r4_matched_residual_holdout_v2.py tests/test_r4_residual_task.py tests/test_r4_residual_task_contract.py tests/test_r4_semantic_distinction.py tests/test_r4_semantic_distinction_contract.py tests/test_r4_semantic_distinction_execution.py tests/test_r4_provider_free_corpus_replay.py
PYTHONPATH=. pytest -q
```

Also run `git diff --check` on the current change and validate changed JSON.
Do not rewrite frozen historical evidence merely to clean legacy whitespace.
At the 2026-07-14 execution closeout, the focused R4 slice passes 111 tests.
The complete suite passes 4,939 tests and all 93 subtests, with one existing
`datetime.utcnow()` deprecation warning. A changed count is not automatically
a regression; unexplained failures or historical hash drift are.

## Current handoff — 2026-07-14

- R1 trust/capture/cost/privacy/custody hardening: complete provider-free.
- R2 constitutional graph survival: complete provider-free.
- R3 fresh-consumer work: honestly closed/deferred without meeting its semantic
  exit condition; do not reopen it casually.
- R4 inventory, fan-in, first complementary-reader attempt, token correction,
  corrected diagnostic, provider-free semantic-distinction repair, exact
  holdout execution, provider-free causal diagnosis, and provider-free
  residual-task identity repair, rejected v1 matched holdout, leakage-corrected
  v2 matched holdout, its one-use exact execution, and the provider-free
  five-record false-positive causal diagnosis: complete and documented.
  The residual contract makes residual discovery the complete provider-visible
  job,
  deterministically maps its two enum values to the existing canonical roles,
  and preserves source/prior order, paired shape, relationship behavior,
  model, provider route, runtime, and graph. Case 04 locally expects two quiet
  surfaces; Case 01 preserves only the recurring operating-capability
  funding/ownership residual. The v1 matched design at `b464642` is permanently
  rejected because its evidence leaked classifications. The additive v2
  package freezes four new 28-message sources and priors, a human leakage pass
  bound to exact hashes, a protected source-first target, and eight exact
  v2/residual requests. All eight calls completed once. Both arms recovered
  the genuine post-June service gap and Board-designation dependency; the
  residual arm still failed both quiet controls. Its frozen decision is
  `residual_task_repair_insufficient`. The follow-on diagnosis rejects paired
  completion as a general cause because Cases 01 and 02 failed without a
  genuine companion finding. It preserves a narrower, falsifiable companion
  mechanism for Cases 03 and 04 and ends with
  `r4_separated_surface_experiment_earned`; that means a provider-free design
  goal may be considered separately, not that a split is a repair or that an
  experiment is authorized.
- Canonical integration target: `main`. The provider-free v2 package was
  published through GitHub PR #365 in canonical merge
  `b7d1d62c05bdf05f91401c25ceb0a2cc73ffe307`. The completed A1 execution was
  published through PR #366 in canonical merge
  `9c5e9301640592d3ab5d0a95489a6960da60e1f4`; both raw checkpoint
  `e2f83561686172538c8ac8876a53da2a804dc503` and reviewed closeout
  `284c0cb28de868185364fc4bf61996310e006210` remain ancestors. Earlier PR #364
  contains the residual-task contract;
  PR #362 remains the consumed semantic-distinction execution handoff and
  PR #363 the completed causal diagnosis.
- PR #347 was recognized as merged through the consolidation. PRs #348-#359
  are closed as superseded after verifying every exact head commit is reachable
  from `main`; their historical branches and discussions remain intact.
- Provider calls currently authorized: zero. The one-use A3 authorization was
  consumed by exactly four calls at an exact provider-reported `$0.01107025`.
  The one-use matched-holdout A1 authorization was consumed by exactly eight
  calls at an exact provider-reported `$0.01408165`; no second execution is
  permitted.
- The residual-task goal made zero provider calls at `$0.00`, prepared no new
  holdout, and did not request authorization. Its exact decision is
  `residual_contract_ready_for_new_holdout_design`.
- Raw A1 execution and mechanical custody were committed before protected
  review in `e2f83561686172538c8ac8876a53da2a804dc503`. The complete local
  evidence is under
  `research/lolla-r4-matched-holdout-v2-execution-2026-07-14-a1/`. The
  temporary authorization is not committed. The source-first review covers all
  16 records without a scalar score.
- Runtime/graph integration, wider-corpus execution, model comparison,
  production-model selection, receipt claims, and scalar scoring: unauthorized.

The next eligible unit, if separately authorized, is provider-free design of a
single separated-versus-paired surface experiment. It may test only whether
separation suppresses the Case 03/04 opposite-surface companion records while
preserving genuine findings and must retain Case 01/02 quiet controls to expose
independent governed-machinery errors. Do not treat separation as an earned
repair, start design automatically, retry A1 or A3,
execute rejected v1, create another authorization, or make an unapproved
provider call. Do not reveal protected targets to a runner or modify frozen
sources, priors, requests, operators, or outputs. R5, runtime/graph integration,
relationship work, wider-corpus execution, model comparison, production-model
selection, and product-usefulness claims remain gated and unauthorized.

## Resume the local diagnosis branch

The execution evidence is canonical. The completed provider-free causal
diagnosis is intentionally local and unpublished on this machine:

```bash
cd /Users/marcin/Desktop/lolla-skill-main
git switch agent/r4-residual-false-positive-causal-diagnosis
git status -sb
python3 -m json.tool research/lolla-r4-residual-false-positive-causal-diagnosis-2026-07-14/causal-diagnosis.json >/dev/null
PYTHONPATH=. pytest -q tests/test_r4_provider_free_corpus_replay.py
```

Do not infer publication or provider authorization from this local branch,
the diagnosis, historical authorizations, or the completed evidence. Publishing
this branch, designing the ablation, and executing it each require their own
founder decision.
