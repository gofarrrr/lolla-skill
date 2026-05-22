# Operations and Limits

Operational doctrine, runtime requirements, edge cases, and cost notes for Lolla runs.

## Contents

- Quality doctrine and non-goals
- Known limitations
- Environment variables
- Edge cases
- Cost per run and telemetry pointer

## Quality Doctrine

- **Specificity over generality** — "Consider the risks" is not a finding. "The reasoning closes on a recommendation without naming what evidence would reverse it — Inconsistency-Avoidance operating on this passage" is a finding. Specificity means naming the reasoning pattern and where it appears, not domain facts.
- **Reversal triggers must be observable** — "If things go wrong" is not a trigger. "If Q2 pipeline coverage drops below 3x while integration is consuming >20% of engineering hours" is a trigger.
- **Curated knowledge is the substrate; useful reasoning is the product** — Claude does not invent new detector findings, challenge statements, or V60 affordances. It must account for the curated material, but public chat and memo prose should show the decision-relevant mechanism in natural language. Exact model names, chunk IDs, affordance text, absence records, and ledger decisions belong in Observatory/audit unless they genuinely help the user understand the answer.
- **Intellectual honesty** — Flag genuine uncertainty. If a detection is borderline, say so. Better to surface 3 strong findings than 8 padded ones.
- **False confidence is worse than honest uncertainty** — The whole system exists to fight borrowed certainty. It must not create more of it.
- **The process is part of the product** — Every finding is traceable: which tendency was detected, why, which models competed, which won. The system is a reasoning observability layer, not a magic answer box.


## What Lolla Is Not

- **Not a second answer.** Lolla does not compete with the vanilla model at being a domain expert.
- **Not a generic "think harder" prompt.** It routes through specific curated knowledge, not broad instructions.
- **Not a fact-checking engine.** It audits reasoning structure, not factual claims.
- **Not a domain classifier.** The query identifies live constraints and omissions, not a retrieval topic.
- **Not a consultant simulator.** It does not rewrite the memo. It surfaces compact structural pressure.
- **Not a deterministic case-solver.** The downstream model or human still decides what to do with the pressure.

Lolla succeeds when it makes better reconsideration possible, not when it dictates the outcome.


## Known Limitations

- **Pass 1 can miss tendencies.** The old 25-in-one prompt is gone; six family-clustered specialists reduce load and improve stability, but each cluster is still probabilistic semantic triage. Adjacent tendencies can still be confused. Embedding swiss cheese partially addresses this.
- **Pass 2 is single-shot.** No iterative refinement. If the deep check misses a sub-pattern, it stays missed.
- **Routing is lookup-only.** 1-hop graph expansion with optional embedding reranking, no multi-hop reasoning or dynamic traversal.
- **Embedding threshold is fixed.** 0.30 for tendency signal, not tuned per tendency.
- **Quote validation has intentionally narrow tolerance.** Extraction-level `reasoning_passages` accept exact transcript spans, case drift, or a symmetric wrapper quote around the whole span; paraphrase is still rejected and dropped. Lane 2 verification has a separate quote-repair path for accepted anchors, but repairs are tracked as `quote_repairs` so evidence cleanup is visible rather than silent.
- **V60 selection is an opportunity layer, not a truth oracle.** It can surface source-backed affordances and absence blockers that the lanes did not fully express, especially through embedding recall, but Claude/Codex can still reject or defer them. Usefulness is measured through the ledger and final-answer delta, not by forcing every selected chunk into public prose.
- **No feedback loop.** Pipeline output doesn't feed back into itself. No learning from past runs — improvements come from reviewed curation at the correct layer.

---


## Environment Requirements

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENROUTER_API_KEY` or `LOLLA_OPENROUTER_API_KEY` | Yes | All LLM judgment (extraction, triage, deep checks, fingerprint, verify, frame extraction, reframing) |
| `OPENAI_API_KEY` | No | Enables embedding swiss cheese (tendency signal, companion recall, chunk reranking). System works without it via deterministic routing only. |
| `LOLLA_OPENROUTER_MODEL` | No | Override model (default: `x-ai/grok-4.1-fast`) |
| `LOLLA_LLM_TIMEOUT` | No | Timeout per boundary call in seconds (default: 45, max: 120) |
| `LOLLA_V60_ENRICHMENT` | No | Set to `off` or `0` to disable private V60 enrichment for a run; default is on/auto when `affordances_v60.json` exists |
| `LOLLA_ACTIVATION_TIEBREAKER` | No | Set to `off`/`0` to disable the near-tie activation-condition tiebreaker in graph routing; default is on. |
| `LOLLA_STAKEHOLDER_CHECK` | No | Experimental optional stakeholder assumption check. If enabled and it fails, `run_health` records `stakeholder_check_failed`; user-facing surfacing remains disabled. |
| `LOLLA_PRE_STEP6_PORTFOLIO` | No | Set to `shadow` to enable the dormant pre-Step-6 shadow portfolio recorder. Default is `off`; shadow mode never changes visible output. |
| `LOLLA_PRE_STEP6_PORTFOLIO_CACHE_DIR` | No | Cache directory for precomputed pre-Step-6 card decks used by shadow mode. Cache misses stand down. |
| `LOLLA_CASE_ID` | No | Force a specific archive case folder name, skipping fingerprint matching. |
| `LOLLA_ARCHIVE_DIR` | No | Override the archive root; default is `~/.local/share/lolla/runs/`. |
| `LOLLA_REPO_ROOT` | No | Override engine location (not needed for standard installs) |

---


## Edge Cases

| Situation | What Happens |
|-----------|-------------|
| Conversation is about code debugging | Extraction returns `not_strategic`, Claude presents polite decline |
| Conversation is 1-2 turns | Extraction still works. Less material for Lane 2 fingerprinting. Lane 3 (frame pressure) is most useful on short conversations. |
| Conversation is very long | Claude/`run_extract.py` truncate to first 3 + last 15 turns when the long-conversation or 80K-character cap fires. `capture_manifest.truncation_applied` records what was omitted, and `run_health.issues[]` includes `capture_truncated`. |
| Pipeline finds zero tendencies | Valid outcome. "No structural pressures detected." |
| OpenRouter times out | Boundary client returns empty payload + a degraded `BoundaryCallMetadata` (status `timeout` / `http_error_*` / `url_error` / `response_json_error`). No internal retry loop. The pipeline degrades — affected lanes return empty/partial results, the run continues, and the failure is visible in `audit_summary.boundary_calls[]`. The only application-level retry is extraction's single quote-fabrication retry (see *Capture validation* in Step 2). |
| `OPENAI_API_KEY` not set | Embeddings disabled. Pipeline runs purely on LLM triage + deterministic routing. Works fine, just without the swiss cheese redundancy layer. |
| V60 artifact missing or disabled | The four lanes still run. `v60_enrichment` becomes `disabled` or `skipped_error`; if enabled but unavailable, `run_health.issues[]` includes `v60_enrichment_failed`. |
| V60 active but ledger missing | `finalize_v60_telemetry.py` marks `run_health.v60_consideration_ledger: missing`, adds `v60_consideration_ledger_missing`, and records every selected chunk as unaccounted. The run archives, but it is visibly incomplete. |
| Pre-Step-6 shadow portfolio disabled | Normal behavior. The live run does not record `pre_step6_shadow_portfolio`, and visible output is unchanged. |
| Pre-Step-6 shadow cache miss | Shadow mode records a stand-down result and still leaves visible Step 6 unchanged. |
| Multiple strategic threads in one conversation | Extraction captures the most developed/recent thread. |

---


## Cost Per Run

A typical run makes 18-25 OpenRouter calls against `x-ai/grok-4.1-fast`:
- 1 extraction call (~3K tokens in, ~1K out); +1 retry on quote fabrication (~14% of runs observed) adds ~2-3K tokens
- 6 Pass 1 cluster triage calls in parallel (~5-6K tokens each; ~5,600 prompt + 150-300 completion per cluster)
- 2-7 deep check calls (~2K tokens each; count depends on how many tendencies triggered)
- 2 companion calls — fingerprint + verification (~3K tokens each)
- 2 frame pressure calls — extraction + reframing (~2K tokens each)
- 2-3 structural coverage calls (~2K tokens each): question classification, dimension detection + coverage, gap question generation (conditional, only when gaps exist)

Total: roughly 60-110K tokens per run. At Grok 4.1 Fast pricing, approximately $0.04-0.10 per audit. Embeddings (if enabled) add one gpt-4o-mini expansion call (~$0.001) plus a batch embedding call for the original query + 2 domain variants (~$0.0002). The revision step is available for headless/eval runs but skipped in the skill flow — Claude produces the updated position directly.

The Bullshit Index runs one OpenRouter call per passage of the audited answer (typically 30-60 calls in parallel). On a long answer this can dominate the OpenRouter call count. It runs in `_run_bullshit_index` after the lanes complete and is recorded under `stage="bullshit_index"` in the per-run telemetry.

V60 private enrichment adds no extra OpenRouter chat call. It does deterministic artifact lookup plus optional reuse of the embedding retriever when embeddings are enabled; that can add the same small OpenAI query-expansion/embedding cost profile described above. The dominant V60 cost is context and orchestration attention in Step 6, which is why the default cap is 8 private cards and the ledger records presented-but-not-used chunks.

The Step-7 pressure-check sub-agents are rested by default. If the user/operator explicitly enables deeper-review mode, they fire from inside the SKILL via Claude Code's Agent tool, *not* through the OpenRouter boundary client. They run on whatever Claude model the orchestrator inherits (typically Opus). On optional runs this can be the dominant cost line. Their `total_tokens` (no prompt/completion split available) is recorded into the same `usage_summary` block by Step 8b.

The cost bump compared to earlier versions is load-reduction working as designed. Pass 1 was previously a single monolithic call scoring all 25 tendencies under ~11 confusion guardrails; it is now six family-clustered specialists (3-5 tendencies each, family-relevant guardrails only). The trade-off is more calls for narrower per-call load — and measured Pass 1 stability moved from 0.50 → 0.70 Jaccard on a fixed Marcus extraction as a result.

**Per-run telemetry** lives in the `usage_summary` block of the result JSON. See **[cost-and-telemetry.md](../cost-and-telemetry.md)** for the canonical reference: what's measured, where it's stored, how to verify it, how to bump prices, and how to add a new vendor or stage. The Observatory's `/usage` page renders the same data visually.

**Per-call raw responses** live in `audit_summary.boundary_calls[N]` alongside the token counts. Each record carries `raw_message_content` (the full LLM response string), `finish_reason`, and `temperature` so any LLM decision is investigable from `result.json` alone without re-running the pipeline (PR 1 of the 2026-04-28 granular-visibility roadmap). Adds ~10–50 KB to a typical `result.json` depending on call count.
