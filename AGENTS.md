# Lolla repository guidance

This file applies to the entire repository. It is the cold-start handoff for
agents and developers. Keep it current when a development goal changes the
project boundary or the next decision.

## Product in one paragraph

Lolla is an experimental reasoning-pressure and audit system for consequential,
open situations where facts, frames, values, and trade-offs are incomplete and
there may be no known correct answer or best lens. It preserves a rich
conversation, uses LLMs to interpret its messy meaning, and uses deterministic
machinery plus a curated mental-model graph to introduce provenance-bearing
external pressure. The reasoner reconsiders; the system records the process.
Lolla makes additional ways of seeing inspectable. It does not select an oracle
answer, certify reasoning quality, or remove human decision authority.

## Universal cold start

Before changing architecture, claims, or the next experiment, read only this
universal set in order:

1. `PROJECT_STATUS.md` — the single current-state and authorization contract.
2. `docs/conversation-understanding/lolla-product-constitution-v5.md` — binding
   development rules.
3. `HOW_IT_WORKS.md` — reachable architecture and explicit absent edges.
4. `docs/README.md` — lifecycle navigation and task-specific routes.
5. `plans/lolla-post-stage0-addendum-restart-roadmap-2026-07-15.md` — the gated
   sequence; an eligible stage is not an authorized stage.

Then read only the lane you will touch:

- **Live skill:** `SKILL.md` and `docs/skill/STEPS.md`.
- **Graph, compiler, or planner:** read `docs/conversation-understanding/lolla-self-contained-graph-substrate-and-skill-result-2026-07-22.md`, `references/knowledge-substrate-operations.md`, and `docs/evals/lolla-self-contained-skill-readiness-v1.json`.
  For new graph or semantic-supply opportunities also read the pressure/understanding/graph PRD, consumer-context contract v1, its 2026-07-22 correction, `docs/conversation-understanding/lolla-consumer-context-role-attribution-case-candidate-result-2026-07-23.md`, `docs/conversation-understanding/lolla-agent-only-paired-delta-screen-result-2026-07-23.md`, `docs/conversation-understanding/lolla-agent-only-graph-variance-calibration-result-2026-07-23.md`, the completed agent-only graph replication contract/plan/result, the 2026-07-24 reviewer-envelope repair contract/plan/result, `docs/conversation-understanding/lolla-agent-only-graph-review-envelope-v2-result-2026-07-24.md`, and `docs/conversation-understanding/lolla-agent-only-graph-review-nonclaim-custody-v3-repair-result-2026-07-24.md`, then use `.codex/skills/audit-lolla-boundaries/SKILL.md`.
- **Decision Trail or Decision Work:** the Stage 0 addendum/register, Stage 0.6
  result, sidecar current state, and interpretation contract linked by
  `docs/README.md`. Also read
  `docs/conversation-understanding/lolla-decision-trail-stage-lineage-2026-07-22.md`:
  June's specialist-output program remains paused at an unfilled PR104 human-
  review packet, while July's Stage 1 is a separate, narrower, unauthorized
  interface-truthfulness option that does not supersede the pause.
- **Atlas:** the custody V2 result/evidence, canonical baseline publication,
  `apps/mental-model-atlas/README.md`, and its `DESIGN_SYSTEM.md`.
- **R1–R4 research history:** the current-state audit, R4 closeout, and frozen
  A1/A2 results/plans. Read them to understand a named decision, never as a
  current implementation sequence.
- **Provider-facing work:** reread the provider, key, cost, and privacy rules
  below and freeze a new exact authorization contract before transport.

`PROGRESS.md`, `TODOS.md`, older PRDs, and dated result files preserve why the
project made earlier choices. They are not the current backlog or authority.
The current seventeen-question repository handoff review is
`docs/evals/lolla-public-handoff-cold-reader-review-2026-07-22.md`; it is
maintainer/agent evidence, not independent human acceptance.

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

- Do not define “good” as agreement with a reference answer, maximum pressure
  application, or selection of the lenses most similar to the conversation.
  A source-first human target protects meaning and exposes effects; it is not
  an oracle for the correct decision or the best mental model.
- Treat the conversation as both authoritative evidence and a conditioning
  field. A fluent model may continue its framing, omissions, sycophancy, and
  coherence. Probabilistic familiarity is not the boundary of thinkability.
- A “digital twin” is a metaphor for an inspectable second reasoning surface,
  not a claim to reproduce the user, the agent, or their mind. It preserves the
  exchange and introduces reasoning operations the prompt may never summon.
- A mental model contributes a reasoning operation, question, counterframe,
  failure mode, or test—not a case fact or conclusion. Inversion, for example,
  tells the reasoner how to look again; it does not supply the answer.
- Fact-free pressure is not fact-free judgment. Case facts may be withheld from
  controlled graph recall so routing does not collapse into semantic matching;
  reattach the authoritative conversation before application or disposition.
- Use Lolla as a camera, not an engine: increase inspectable information and
  resolution before action outruns understanding. More applied lenses, words,
  certainty, or activity are not success when they add only analysis theater.
- Bound volume and preserve stopping rules without using predicted relevance to
  domesticate pressure. The aim is not exhaustive use of all 222 lenses; it is
  a tractable opportunity for a non-obvious lens to create an `aha`, a useful
  question, a grounded rejection, or an honest unresolved path.
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
- The frozen provider-boundary receipt retains its 2026-07-13 active-route
  date. New usage summaries qualify it as `active_openrouter_route_only` and
  separately report the 2026-05-25 whole-table check. Optional Step 7
  Anthropic rates are historical and must not be used for current budgeting
  without a prospective price-table version and exact official recheck.

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
PYTHONPATH=. python3 scripts/evals/validate_self_contained_skill.py --validate-only
PYTHONPATH=. pytest -q tests/test_run_extract.py tests/test_run_pipeline_contract_default.py tests/test_agent_result.py tests/test_constitution_stage0_addendum_register.py tests/test_stage0_public_handoff.py tests/test_r4_separated_surface_execution_a2.py
PYTHONPATH=. pytest -q
```

Also run `git diff --check` on the current change and validate changed JSON.
Do not rewrite frozen historical evidence merely to clean legacy whitespace.
The Stage 0 addendum publication passed 4,968 tests and all 93 subtests with one
existing `datetime.utcnow()` deprecation warning. A changed count is not
automatically a regression; unexplained failures or historical hash drift are.

For Mental Model Atlas work, also run:

```bash
PYTHONPATH=. python3 scripts/product/build_mental_model_atlas_custody_v2.py --validate-only
PYTHONPATH=. pytest -q tests/test_mental_model_atlas_custody_v2.py
PYTHONPATH=. pytest -q tests/test_mental_model_atlas_phase1_projection.py
PYTHONPATH=. pytest -q tests/test_mental_model_atlas_card_first_repair.py
PYTHONPATH=. pytest -q tests/test_mental_model_atlas_navigation_index.py
cd apps/mental-model-atlas
npm ci
npm run check
npm test
npm run build
npm audit --audit-level=moderate
```

Do not regenerate source meaning in the browser, normalize exact relations, infer missing pages, or treat the local visual gate as deployment clearance.

## Current handoff — 2026-07-24

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
- The live four-lane pressure path, graph recall, graph-survival portfolio, and
  apply/reject/park custody are the experimental core; unique usefulness is
  unproven. Private stdin capture, provider-status-first admission,
  append-preserved attempts, and terminal failure seals now guard entry to the
  unchanged graph. Its bundled engine now resolves independently of caller
  cwd. This repository owns all 222 sources, 1,358 relations, and the root
  skill; compilation is byte-exact and all 163 windows replay.
  Candidate-only path custody is not live; optional Step 7 remains default-off.
- The provider-free Marcus run repair is published through PR #401. It promotes a preserved `pass2` 429 hidden beneath `healthy` into partial health and the receipt, suppresses capture echo, and enforces `umask 077`, `0700` archive directories, and `0600` files. The inspected run's modes were remediated without content or graph changes; usefulness remains unproven.
- A later live run exposed a startup race that PR #401's in-read no-echo guard could not prevent on its own. The provider-free follow-up adds the exact `PRIVATE_INPUT_READY` handshake, true-PTY regression coverage, fail-closed echo setup, source-complete passage-check context with exact custody, no globally repeated dropped-thread hint, exact partial receipts, and a narrow review-only caller state when that optional profile is the sole partial cause. The graph is unchanged. See `docs/conversation-understanding/lolla-live-run-interface-and-passage-truthfulness-repair-result-2026-07-24.md`.
- Decision Work is an optional operator-directed sidecar; it and Observatory can package/read artifacts but cannot generate trustworthy arbitrary meaning.
- Product Delta's agent-only paired screen preserves mixed moves, harms,
  disagreement, nulls, and stand-down; it validates no graph or usefulness.
- The graph-increment result and variance calibration are frozen. Three of four generations completed; one direct draw failed without a recoverable payload and was not replaced.
  Both blind reviews completed. The within-graph pair was materially different in both reviews; a historical cross pair drew `present / uncertain`; the missing draw removed the within-direct and one cross pair.
  The result is `not_evaluable`; it authorizes no graph attribution or expansion.
- The graph replication is consumed: all eight generations completed, but one blind review failed 29 enum checks. It was preserved without repair; no post-reveal work ran. Result: `not_evaluable`; no retry is authorized.
- The reviewer-envelope v2 authorization is consumed. Both blind reviews passed, so both post-reveal contexts ran; each then failed one exact `nonclaims_acknowledged` equality check because the schema fixed type and length but not the frozen wording.
  All four first-terminal payloads are preserved without retry, repair, or semantic salvage. The result remains `not_evaluable`; it creates no graph or traversal evidence.
- The provider-free V3 nonclaim-custody repair is complete. Exact nonclaims now belong to deterministic input packets under stable IDs, order, count, and hash; the prospective response schema has no echo or forced acknowledgment.
  Two valid fixtures pass and two legacy echo fixtures fail exactly. This proves packet mechanics, not model compliance or graph value. Zero semantic contexts ran.
- Atlas opens exact neighborhoods from the 222-model / 1,358-relation index.
  V1 is immutable; V2 has 2,182 custody-only and zero unexpected differences.
  Teacher and review surfaces remain parked. Design/viewport mechanics are not
  founder, screen-reader, rights, deployment, or usefulness acceptance.
- Preserve the exact founder-supplied `lolla` RGB wordmark and SHA-256 note in
  `apps/mental-model-atlas/public/brand/`; CSS must not redraw its letterforms.
- The Stage 0 addendum was canonically published through PR #372 at merge
  `fc30bd944bfb91fbff0cc09190487997f3fe3185`. Its
  machine register assigns every canonical implementation file to an explicit
  lifecycle disposition and distinguishes live calls from artifact handoffs,
  optional hooks, offline paths, read-only projections, and absent links.
- Provider calls authorized for repository development: zero. One unintended invalid-key repair-test request reached OpenRouter HTTP 401 before the new guard; no authenticated generation/output, provider-reported cost $0.00, conservative ledger $0.0085688, no retry/replacement. A1 and A2 authorizations are consumed; A1 remains separate `semantic_result_not_evaluable` evidence. A2
  completed twelve calls for `$0.02148425`. No A3, retry, replacement, prompt
  tweak, model comparison, or integration is authorized.
- Path-custody promotion, incoming/two-hop pressure, reserve expansion, new ranking, wider semantic execution, model comparison, receipt claims, scalar scoring, and graph-evaluation continuation are unauthorized.
  The V3 provider-free custody decision is complete. Its prospective two-context post-reveal run remains unauthorized without the exact new authorization in the V3 machine contract.

Stage 0.5 made the map clone-legible; Stage 0.6 corrected source custody.
PRs #379–#395 carry graph/Atlas custody, public handoffs, Decision Trail lineage, A/B/C planning, case freeze, paired-delta work, rehearsal, variance, replication, and the provider-free reviewer-envelope repair. The separate V2 execution result is tracked through PR #396 and the provider-free V3 nonclaim-custody repair through PR #397.
The founder declines human review; that v1 experiment stays unfilled and paused.
The graph rehearsal proves no graph value. Calibration lost a generation baseline; replication lost one review to an ambiguous enum envelope; V2 fixed the blind shape, but both post-reveal contexts drifted the frozen nonclaim wording and were rejected without salvage. V3 repairs that response boundary provider-free by assigning exact nonclaim presentation to deterministic input custody.
The semantic follow-ups remain `not_evaluable`; the V3 fixture result creates no graph, usefulness, Atlas, or Stage 1 authority.
Stage 1 is separate from June's paused PR104 program. A/B/C authorizes no
review, provider, graph/runtime, sidecar, or interface work.
