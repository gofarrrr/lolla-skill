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
parallel Work Receipt interpretation system yet. The follow-up
[Decision Work Receipt External Report Attachments](docs/conversation-understanding/decision-work-receipt-external-report-attachments-v0.md)
slice keeps that boundary while letting the receipt CLI link externally
generated Decision Trail/Product Delta reports by safe metadata only, without
copying report content or local paths. The
[Decision Work Receipt Debug Summary](docs/conversation-understanding/decision-work-receipt-debug-summary-v0.md)
renderer turns that JSON package into internal maintainer Markdown; the
checked-in
[launch-public-enterprise-beta receipt debug example](docs/conversation-understanding/decision-work-receipt-debug-summary-launch-public-enterprise-beta-v0.md)
shows the current status/missingness shape. That is not the customer-facing
story. The intended user-facing target is the
[Decision Work Brief PRD](docs/conversation-understanding/decision-work-brief-prd-v0.md):
a plain-language artifact explaining the decision, what Lolla pressed on, what
changed, what remains unresolved, and what the audit must not claim. That PRD
now includes the concrete PR113-PR158 delivery sequence for schema, local
packets, provisional brief drafts, rendering, usefulness review, second tiny
case pilot, small pattern review, third diversity case pilot, and three-case
pattern review, plain-language renderer patch, rereview, local-private
adequacy check, expansion/runtime decision gate, conversation interpretation
gap mapping, the future target contract, packet/artifact support review, and
the offline interpretation packet builder, two tiny offline interpretation
reads, the shared read schema, the first comparison gate over those reads, and
the first two checked-in-safe enrichment tests plus their pattern review, rules
contract, deterministic enriched-brief builder, builder patch, closure gate,
and package manifest.
The
[Decision Work Brief Schema](docs/conversation-understanding/decision-work-brief-v0.json)
and
[Decision Work Brief Schema Guide](docs/conversation-understanding/decision-work-brief-schema-v0.md)
define the PR114 contract. The
[Decision Work Brief Packet Builder](docs/conversation-understanding/decision-work-brief-packet-builder-v0.md)
adds the PR115 offline packet-preparation layer:
`lolla.decision_work_brief_packets.v0` can be built from completed runs with
metadata-only as the safe default and explicit local-private include-text
marking when needed. The
[Decision Work Brief Draft Pilot](docs/conversation-understanding/decision-work-brief-draft-pilot-v0.md)
adds the PR116 one-case Codex-assisted provisional draft review:
`lolla.decision_work_brief_draft_pilot.v0` embeds one checked-in-safe
`lolla.decision_work_brief.v0` draft from a locally generated metadata-only
packet, with uncertainty, follow-up questions, custody flags, and non-claims.
The
[Decision Work Brief Renderer](docs/conversation-understanding/decision-work-brief-renderer-v0.md)
adds the PR117 deterministic Markdown layer, now patched by PR123 for
plain-language headings, and the
[rendered cofounder example](docs/conversation-understanding/decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md).
The
[Decision Work Brief Usefulness Review](docs/conversation-understanding/decision-work-brief-usefulness-review-v0.md)
adds the PR118 delivery gate: proceed to one tiny second case, not product
readiness. The
[Decision Work Brief Second Tiny Case Pilot](docs/conversation-understanding/decision-work-brief-second-tiny-case-pilot-v0.md)
adds the PR119 second checked-in-safe case on `launch-public-enterprise-beta`,
with a
[rendered launch-beta example](docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md)
and a gate to `proceed_to_small_pattern_review`, not runtime integration. There
is now also a
[Decision Work Brief Small Pattern Review](docs/conversation-understanding/decision-work-brief-small-pattern-review-v0.md)
that chooses `proceed_to_third_diversity_case`, followed by the
[Decision Work Brief Third Diversity Case Pilot](docs/conversation-understanding/decision-work-brief-third-diversity-case-pilot-v0.md)
on `deploy-assisted-intake-routing` and its
[rendered intake-routing example](docs/conversation-understanding/decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md).
The
[Decision Work Brief Three-Case Pattern Review](docs/conversation-understanding/decision-work-brief-three-case-pattern-review-v0.md)
then reviews all three rendered briefs, finds a consistent action-consequence
signal, and gates to `proceed_to_plain_language_renderer_patch` because the
current Markdown still sounds too internal for a board/customer reader. The
[Decision Work Brief Plain-Language Renderer Patch](docs/conversation-understanding/decision-work-brief-plain-language-renderer-patch-v0.md)
implements that gate by regenerating all three examples with a plain-language
main body and compact Evidence and limits section. The
[Decision Work Brief Plain-Language Re-Review](docs/conversation-understanding/decision-work-brief-plain-language-rereview-v0.md)
then finds the surface readable enough for source-depth comparison and gates to
local-private adequacy. The
[Decision Work Brief Local-Private Adequacy Check](docs/conversation-understanding/decision-work-brief-local-private-adequacy-check-v0.md)
checks the launch-beta case in read-only local-private shadow mode and records
`adequate_but_missing_private_nuance` without checking in private text. The
[Decision Work Brief Expansion / Runtime Attachment Decision Gate](docs/conversation-understanding/decision-work-brief-expansion-runtime-decision-gate-v0.md)
selects `run_more_local_private_adequacy_checks`, not runtime integration.
The
[Decision Work Brief Conversation Interpretation Gap Map](docs/conversation-understanding/decision-work-brief-conversation-interpretation-gap-map-v0.md)
then maps the richer conversation fields that are clear, partial,
local-private-only, LLM-interpretable, human-review-dependent, or not currently
captured across the three cases. It gates to a target contract, not a new
extractor. The
[Decision Work Conversation Interpretation Contract](docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.md)
and
[contract JSON](docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json)
define `lolla.decision_work_conversation_interpretation_contract.v0`, a
future-facing contract for field ownership, source status, privacy handling,
missingness, custody, non-claims, and handoff shape.
The
[Decision Work Conversation Interpretation Contract Packet Review](docs/conversation-understanding/decision-work-conversation-interpretation-contract-packet-review-v0.md)
then compares that contract against the current completed-run artifact and
Decision Work Brief packet surface. It finds current packets can carry
source/status metadata, but the next needed layer is a field-grouped offline
interpretation packet, not runtime extraction.
The
[Decision Work Conversation Interpretation Offline Packet](docs/conversation-understanding/decision-work-conversation-interpretation-offline-packet-v0.md)
adds that PR130 packet layer:
`lolla.decision_work_conversation_interpretation_packets.v0` prepares a
source/status dossier over completed-run artifacts and PR128 field groups for a
future LLM or human interpretation read. It fills no semantic contract fields,
copies no raw/private content, and still does not change runtime behavior.
The
[Decision Work Conversation Interpretation Tiny Offline Read](docs/conversation-understanding/decision-work-conversation-interpretation-tiny-offline-read-v0.md)
adds PR131's first one-case provisional read over a generated PR130 packet for
`launch-public-enterprise-beta`. It fills only a small PR128 field subset,
keeps starting direction, abandoned options, and lost value uncertain, checks
in no source packet or private text, and recommends a second tiny offline read
before any schema formalization or runtime plan.
The
[Decision Work Conversation Interpretation Second Tiny Offline Read](docs/conversation-understanding/decision-work-conversation-interpretation-second-tiny-offline-read-v0.md)
adds PR132's matching read on `deploy-assisted-intake-routing`, showing the
same field set can carry a healthcare operations/deployment action consequence
while keeping starting direction, abandoned options, and lost value
source-limited. It gates to a reusable schema.
The
[Decision Work Conversation Interpretation Read Schema](docs/conversation-understanding/decision-work-conversation-interpretation-read-schema-v0.md)
and
[read JSON](docs/conversation-understanding/decision-work-conversation-interpretation-read-v0.json)
define PR133's `lolla.decision_work_conversation_interpretation_read.v0`
contract for future offline reads. It requires source refs, uncertainty,
privacy limits, human-review flags, non-claims, and no quality-label use, and
adds no interpreter or runtime extraction.
The
[Decision Work Conversation Interpretation Read Comparison](docs/conversation-understanding/decision-work-conversation-interpretation-read-comparison-v0.md)
adds PR134's comparison gate over the PR131 and PR132 reads. It finds stable
useful fields for decision question, action consequence, thresholds, evidence
gates, useful friction, and non-proof boundaries, keeps lost value and source
depth uncertain, and recommends one narrow brief-enrichment test next.
The
[Decision Work Brief Interpretation Enrichment Test](docs/conversation-understanding/decision-work-brief-interpretation-enrichment-test-v0.md)
adds PR135's separate enriched launch-beta brief:
[Decision Work Brief Enriched Launch Beta](docs/conversation-understanding/decision-work-brief-enriched-launch-public-enterprise-beta-v0.md).
It uses only the PR134 feed-now fields and gates to an original-vs-enriched
review. The
[Decision Work Brief Original vs Enriched Review](docs/conversation-understanding/decision-work-brief-original-vs-enriched-review-v0.md)
adds PR136's comparison gate and selects one second enrichment test. The
[Decision Work Brief Second Enrichment Test](docs/conversation-understanding/decision-work-brief-second-enrichment-test-v0.md)
adds PR137's separate enriched intake-routing brief:
[Decision Work Brief Enriched Intake Routing](docs/conversation-understanding/decision-work-brief-enriched-deploy-assisted-intake-routing-v0.md).
The
[Decision Work Brief Enriched Pattern Review](docs/conversation-understanding/decision-work-brief-enriched-pattern-review-v0.md)
adds PR138's two-enriched-brief pattern review. It recommends a future
enrichment-rules contract but does not implement PR139, add runtime behavior,
create new reads, or claim product proof.
The
[Decision Work Brief Enrichment Rules Contract](docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.md)
and
[contract JSON](docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.json)
add PR139's conservative field rules: only a small stable interpretation field
set may enter the user-facing brief, evidence-only fields stay out of the main
body, forbidden score/approval/proof concepts are blocked, and any builder must
preserve uncertainty, source refs, privacy limits, and non-claims.
The
[Decision Work Brief Offline Enriched Builder](docs/conversation-understanding/decision-work-brief-offline-enriched-builder-v0.md)
adds PR140's deterministic CLI for creating separate enriched Markdown from an
existing rendered brief, an interpretation read, and the PR139 rules contract.
It generates the checked-in-safe
[builder launch-beta output](docs/conversation-understanding/decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md)
and
[builder intake-routing output](docs/conversation-understanding/decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md)
without overwriting the original or hand-built enriched briefs. The
[Decision Work Brief Enriched Builder Output Review](docs/conversation-understanding/decision-work-brief-enriched-builder-output-review-v0.md)
adds PR141's comparison against the hand-built examples and selects
`proceed_to_builder_rule_patch` because the generated output is safe and useful
but still too templated for the next case.
The
[Decision Work Brief Enrichment Builder Rule Patch](docs/conversation-understanding/decision-work-brief-enrichment-builder-rule-patch-v0.md)
adds PR142's deterministic wording patch and regenerates both builder-enriched
examples with less repetitive prose while preserving uncertainty and
non-claims. The
[Decision Work Brief Builder Patch Review](docs/conversation-understanding/decision-work-brief-enrichment-builder-rule-patch-review-v0.md)
adds PR143's review of those patched outputs and gates to offline-system
closure. The
[Decision Work Brief Offline System Closure Gate](docs/conversation-understanding/decision-work-brief-offline-system-closure-gate-v0.md)
adds PR144's decision that the offline PR114-PR143 surface is coherent enough
to package, not integrate. The
[Decision Work Brief PR114-PR144 Packaging Gate](docs/conversation-understanding/decision-work-brief-pr114-pr144-packaging-gate-v0.md)
and
[package manifest](docs/conversation-understanding/decision-work-brief-pr114-pr144-package-manifest-v0.json)
add PR145's bounded package surface, staging list, do-not-stage warnings,
validation checklist, useful signal, unresolved risk, and suggested package PR
description. The
[Decision Work Brief Additional Local-Private Adequacy Checks](docs/conversation-understanding/decision-work-brief-additional-local-private-adequacy-checks-v0.md)
adds PR146's safe-conclusions-only source-depth check for the cofounder and
intake-routing cases. It finds the checked-in-safe briefs still adequate with
private nuance, and recommends a third builder case rather than runtime
integration. The
[Decision Work Brief Third Builder Case](docs/conversation-understanding/decision-work-brief-third-builder-case-v0.md)
adds PR147's feasibility gate for the cofounder builder case: the rendered
brief and PR146 support exist, but no builder-compatible interpretation read
exists yet, so it recommends creating that read before any third builder output.
The
[Decision Work Conversation Interpretation Third Tiny Offline Read](docs/conversation-understanding/decision-work-conversation-interpretation-third-tiny-offline-read-v0.md)
adds PR147A's formal-schema cofounder read, filling the same small field subset
used by the prior two reads while keeping lost value and starting direction
source-limited.
The
[Decision Work Brief Third Builder Case Output](docs/conversation-understanding/decision-work-brief-third-builder-case-output-v0.md)
adds PR148's deterministic cofounder builder output:
[builder cofounder output](docs/conversation-understanding/decision-work-brief-builder-enriched-ceo-remove-founding-cofounder-v0.md).
It finds the third builder-generated enriched brief readable enough for a
three-case pattern review, while noting source-depth sensitivity and a mild
template weakness.
The
[Decision Work Brief Three Builder Case Pattern Review](docs/conversation-understanding/decision-work-brief-three-builder-case-pattern-review-v0.md)
adds PR149's comparison across the launch-beta, intake-routing, and cofounder
builder outputs. It finds the builder stable enough to preserve action
consequence, uncertainty, field exclusions, and non-claims across three
decision families, and recommends a human-review intake plan rather than
runtime integration or another deterministic builder case.
The
[Decision Work Brief Human Review Intake Plan](docs/conversation-understanding/decision-work-brief-human-review-intake-plan-v0.md)
adds PR150's plan for that next gate. It defines what future human reviewers
should check across the three builder-generated enriched briefs, including
usefulness, action consequence, uncertainty, source depth, private-context
questions, overtrust risk, runtime blockers, stop conditions, and allowed
outcomes. It is not completed human validation and does not claim product
proof, score answer quality, authorize agent action, or attach the brief to
runtime.
The
[Decision Work Brief Human Review Pilot Scaffold](docs/conversation-understanding/decision-work-brief-human-review-pilot-scaffold-v0.md)
and
[blank response template](docs/conversation-understanding/decision-work-brief-human-review-response-template-v0.json)
add PR151's runnable human-review pilot materials. They give a future human
reviewer the three enriched briefs, instructions, stop conditions, allowed
answers, and blank fields to fill, while keeping `human_review_completed` false
until a real reviewer responds.
The
[Decision Work Brief Human Review Pilot Readiness Gate](docs/conversation-understanding/decision-work-brief-human-review-pilot-readiness-gate-v0.md)
adds PR152's explicit readiness boundary: the pilot packet and blank template
are ready, but no human response has been collected, no human validation has
happened, and runtime or customer-facing use remains blocked.
The
[Decision Work Brief Human Review Awaiting Response Gate](docs/conversation-understanding/decision-work-brief-human-review-awaiting-response-gate-v0.md)
adds PR153's pause boundary: no real human response exists yet, so the next
unblocked evidence step is a real reviewer filling the PR151 response
template, not Codex-filled review.
The
[Decision Work Automatic Triage Contract](docs/conversation-understanding/decision-work-automatic-triage-contract-v0.md)
and
[contract JSON](docs/conversation-understanding/decision-work-automatic-triage-contract-v0.json)
add PR154's future automatic routing contract. The triage layer should route
attention and escalation across user-surface, agent-inspection, source-depth,
private-context, overtrust, domain-review, human-calibration, and runtime
blocking states without becoming a score, approval, product proof, human
validation claim, or action authorization.
The
[Decision Work Automatic Triage Packet Builder](docs/conversation-understanding/decision-work-automatic-triage-packet-builder-v0.md)
adds PR155's deterministic checked-in-safe packet builder over the three
builder-enriched Decision Work Brief cases. It gathers refs, custody flags,
triage field policy, future tasks, and known limits without filling semantic
triage fields.
The
[Decision Work Automatic Triage Provisional Read](docs/conversation-understanding/decision-work-automatic-triage-provisional-read-v0.md)
adds PR156's Codex-assisted provisional triage read over that packet shape,
routing the launch, healthcare, and cofounder cases toward different
source-depth, overtrust, domain, agent-inspection, and runtime-blocker
concerns without scoring or approving advice.
The
[Decision Work Brief Offline v1 Closure Gate](docs/conversation-understanding/decision-work-brief-offline-v1-closure-gate-v0.md)
records PR157's narrow `package_offline_v1` decision: functional offline v1
means the system can preserve custody, render/enrich briefs, prepare triage
packets, and run provisional triage reads with limitations visible.
The
[Decision Work Brief Offline v1 Package Gate](docs/conversation-understanding/decision-work-brief-offline-v1-package-gate-v0.md)
adds PR158's package manifest for Offline v1, referencing the PR114-PR144 base
package and explicitly adding PR145-PR157.
The
[Decision Work Brief Runtime Attachment PRD](docs/conversation-understanding/decision-work-brief-runtime-attachment-prd-v0.md)
adds the next planning bridge after Offline v1: when a future brief should run,
what the user should see, what another agent should see, what blocks
generation, and why the first runtime-safe slice should be a flagged
post-archive attachment path rather than full automation.
The
[Decision Work Brief Runtime Attachment Contract](docs/conversation-understanding/decision-work-brief-runtime-attachment-contract-v0.md)
and
[sidecar contract](docs/conversation-understanding/decision-work-brief-runtime-sidecar-v0.md)
define PR160-PR161's default-off, post-archive-only attachment surface.
The
[manual runtime bundle generator](docs/conversation-understanding/decision-work-brief-runtime-bundle-generator-v0.md),
[eligibility gate](docs/conversation-understanding/decision-work-brief-runtime-eligibility-gate-v0.md),
[short receipt renderer](docs/conversation-understanding/decision-work-brief-runtime-receipt-v0.md),
and
[agent handoff packet](docs/conversation-understanding/decision-work-brief-agent-handoff-v0.md)
implement PR162-PR165's deterministic sidecar path: bundle status, blockers,
caveated receipt, and agent-inspection refs without model calls or raw/private
export.
The
[flagged post-archive runtime hook](docs/conversation-understanding/decision-work-brief-flagged-post-archive-runtime-hook-v0.md)
adds PR166's first runtime attachment behavior in `scripts/archive_run.py`,
behind `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE`, default off and fail-closed.
The
[runtime attachment review](docs/conversation-understanding/decision-work-brief-runtime-attachment-review-v0.md)
and
[runtime-attached internal v1 package gate](docs/conversation-understanding/decision-work-brief-runtime-attached-v1-package-gate-v0.md)
record PR167's narrow package decision: functional internal v1 behind a flag,
not customer readiness, product proof, human validation, answer-quality
scoring, advice correctness, or action authorization.
The
[runtime-attached internal v1 follow-up plan](docs/conversation-understanding/decision-work-brief-runtime-attached-v1-followup-plan-v0.md)
records PR168's next-choice gate: the hook is mechanically attached and
fail-closed, but still input-supply-limited until a safe run-specific brief,
enriched brief, and triage supply path is planned.
The
[runtime safe brief supply plan](docs/conversation-understanding/decision-work-brief-runtime-safe-brief-supply-plan-v0.md)
records PR169's input classification and selects a safe supply resolver
contract as the next step before adding more runtime behavior.
The
[runtime safe supply resolver contract](docs/conversation-understanding/decision-work-brief-runtime-safe-supply-resolver-contract-v0.md)
records PR170's contract for that resolver: allowed modes, statuses,
input types, unsafe exclusions, bundle feedability, custody flags, and the
PR171 implementation boundary. It still does not implement the resolver or
change the runtime hook.
The
[runtime safe supply resolver](docs/conversation-understanding/decision-work-brief-runtime-safe-supply-resolver-v0.md)
implements PR171's deterministic resolver and CLI. It can validate explicit
safe refs, redact local paths in output, exclude unsafe inputs, and report
whether refs can feed the manual runtime bundle. It still does not create
brief meaning or change the runtime hook.
The
[runtime bundle resolver integration](docs/conversation-understanding/decision-work-brief-runtime-bundle-resolver-integration-v0.md)
implements PR172's manual bundle bridge: `--resolver-output` is now the
preferred safe input to the manual runtime bundle, and resolver states flow into
attachment status, receipt, and agent handoff without changing the runtime hook.
The
[runtime hook resolver wiring](docs/conversation-understanding/decision-work-brief-runtime-hook-resolver-wiring-v0.md)
implements PR173's default-off hook bridge: when
`LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE` is explicitly enabled, the hook now
builds resolver output, passes it to the resolver-aware bundle, and writes a
real sidecar state while remaining non-blocking and fail-closed.
The
[runtime hook resolver fixture review](docs/conversation-understanding/decision-work-brief-runtime-hook-resolver-fixture-review-v0.md)
adds PR174's review-only pass over those sidecar states: flag-off, deferred,
available, agent-inspection-only, blocked, privacy-blocked, and failed-closed.
It selects a checked-in-safe case registry as the next narrow supply step
because useful generated states still depend on explicit safe refs.
The
[runtime checked-in-safe case registry](docs/conversation-understanding/decision-work-brief-runtime-checked-in-safe-case-registry-v0.md)
adds PR175's deterministic safe-ref registry for the three known examples, and
lets resolver mode `checked_in_safe_case_registry` feed the manual bundle
without manual env refs. It is for repeatable demos/tests only, not arbitrary
live-run interpretation.
The
[runtime hook registry fixture review](docs/conversation-understanding/decision-work-brief-runtime-hook-registry-fixture-review-v0.md)
adds PR176's review-only pass over registry-backed hook fixtures. It confirms
that launch-beta, deploy-intake, and cofounder registry refs can produce
generated temp sidecars through the resolver-aware hook seam, while still
recording that arbitrary completed runs need future safe semantic supply.
The
[runtime-attached internal v1 package refresh](docs/conversation-understanding/decision-work-brief-runtime-attached-internal-v1-package-refresh-v0.md)
adds PR177's package manifest for PR160-PR176. It packages the internal,
default-off, post-archive sidecar path for maintainer review when safe refs are
supplied manually or through registry fixtures, while explicitly withholding
customer-readiness, validation, proof, scoring, advice-correctness, arbitrary
run coverage, and action-authorization claims.
The
[automatic semantic supply PRD](docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md)
records the next product bridge after PR216 merged runtime-attached internal v1:
turn the current prepared-case workflow into an offline, bounded, validated
pipeline that can create safe Decision Work artifacts for new completed runs.
The
[offline interpretation queue contract](docs/conversation-understanding/decision-work-offline-interpretation-queue-contract-v0.md)
defines the first queue item/result schema for that bridge without adding a
queue runner, model calls, runtime hook changes, generated reads, or sidecar
updates.
The
[offline interpretation queue builder](docs/conversation-understanding/decision-work-offline-interpretation-queue-builder-v0.md)
adds the deterministic queue-item preparation layer: refs, status, missingness,
requested fields, validation requirements, custody flags, and non-claims only.
The
[operator/Codex interpretation prompt packet](docs/conversation-understanding/decision-work-operator-codex-interpretation-prompt-packet-v0.md)
defines the next bounded handoff to a future operator or Codex session, while
stopping before generated-read intake or any repo-side provider call.
The
[generated interpretation read intake validator](docs/conversation-understanding/decision-work-generated-interpretation-read-intake-v0.md)
adds PR182's strict validation gate for externally supplied Decision Work
interpretation reads. It can accept the three existing checked-in reads and
reject unsafe, under-sourced, overclaiming, or action-authorizing candidates
before any later brief, enrichment, triage, resolver, or sidecar path consumes
them.
The
[generated interpretation read intake review](docs/conversation-understanding/decision-work-generated-interpretation-read-intake-review-v0.md)
adds PR183's review-only pass over the three existing reads and temporary
synthetic rejection cases. It confirms the PR182 validator boundary and selects
one bounded operator/Codex generated-read pilot next, still without brief
rendering, triage, resolver updates, sidecar updates, model calls, proof, or
action authorization.
The
[operator/Codex generated read pilot](docs/conversation-understanding/decision-work-operator-codex-generated-read-pilot-v0.md)
adds PR184's one-case launch-beta generated-read candidate and checked-in intake
result. The intake is accepted for later offline planning only; it does not
render a brief, enrich a brief, generate triage, update resolver refs, update
runtime sidecars, judge semantic truth, score answer quality, or authorize
action. PR184 selects a generated-read-to-brief supply plan next.
The
[generated read to brief supply plan](docs/conversation-understanding/decision-work-generated-read-to-brief-supply-plan-v0.md)
adds PR185's field policy for the next deterministic adapter. It defines which
accepted generated-read fields may feed future offline brief supply, which stay
evidence-only, what source/uncertainty/privacy/non-claim data must travel
forward, and what must block, while still generating no brief, enrichment,
triage, resolver ref use, sidecar update, proof claim, score, or action
authorization.
The
[Decision Work Generated Read Brief Supply Adapter](docs/conversation-understanding/decision-work-generated-read-brief-supply-adapter-v0.md)
adds PR186's deterministic packet builder. It accepts a PR182-accepted read and
intake result, copies only allowed fields with refs and uncertainty, emits ready
or blocked supply status, and keeps sidecar updates, action authorization,
quality labels, product proof, and human validation closed.
The
[Decision Work Generated Read Brief Rendering Pilot](docs/conversation-understanding/decision-work-generated-read-brief-rendering-pilot-v0.md)
adds PR187's one-case reader-facing Markdown render for launch beta. It consumes
a ready PR186 supply packet and preserves source refs, uncertainty, privacy
limits, custody flags, and non-claims, while still not enriching, generating
triage, marking resolver refs usable, updating sidecars, proving correctness,
scoring, or authorizing action.
The
[Decision Work Generated Read Brief vs Existing Brief Review](docs/conversation-understanding/decision-work-generated-read-brief-vs-existing-brief-review-v0.md)
adds PR188's docs/review/tests-only comparison between the generated-read
launch-beta brief and the existing rendered and enriched launch-beta briefs. It
finds the generated-read brief preserves the core decision/action consequence
and boundaries, but is thinner than the enriched brief; it gates to a second
generated-read rendering pilot without enrichment, triage, resolver ref use,
sidecar update, model calls, proof claims, scoring, or action authorization.
The
[Decision Work Generated Read Second Brief Rendering Pilot](docs/conversation-understanding/decision-work-generated-read-second-brief-rendering-pilot-v0.md)
adds PR189's deploy-intake second-case generated-read rendering pilot. It uses a
checked-in-safe generated read, PR182 intake, PR186 supply, and the existing
PR187 renderer to produce a second reader-facing Markdown brief while keeping
compliance/workflow caveats, source refs, uncertainty, privacy limits, custody
flags, and non-claims visible. It still does not enrich, generate triage, mark
resolver refs usable, update sidecars, call models, prove correctness, score, or
authorize action.
The
[Decision Work Generated Read Brief Two-Case Pattern Review](docs/conversation-understanding/decision-work-generated-read-brief-two-case-pattern-review-v0.md)
adds PR190's docs/review/tests-only comparison of the launch-beta and
deploy-intake generated-read-rendered briefs. It finds the path preserves action
consequence, source refs, uncertainty, privacy limits, evidence-only exclusions,
and non-claims across two decision families, while remaining too thin for
triage generation or sidecar use. It gates to a generated-read triage supply
plan, not triage implementation.
The
[Decision Work Generated Read Triage Supply Plan](docs/conversation-understanding/decision-work-generated-read-triage-supply-plan-v0.md)
adds PR191's docs/review/tests-only plan for turning generated-read artifacts
into future triage supply. It defines allowed inputs, routing fields,
evidence-only fields, blocked fields, statuses, route categories, custody
requirements, and forbidden quality/authority route concepts while still
generating no triage, marking no resolver refs usable, updating no sidecars,
calling no models, proving nothing, scoring nothing, and authorizing no action.
The
[Decision Work Generated Read Triage Supply Adapter](docs/conversation-understanding/decision-work-generated-read-triage-supply-adapter-v0.md)
adds PR192's deterministic adapter and CLI. It consumes generated-read, PR182
intake, PR186 brief-supply, and rendered-brief refs and emits
`lolla.decision_work_generated_read_triage_supply.v0` packets for future
offline triage generation only. It supports ready, deferred, and blocked states
while still generating no triage, creating no triage read, marking no resolver
refs usable, updating no sidecars, calling no models, proving nothing, scoring
nothing, and authorizing no action.
The
[Decision Work Generated Read Triage Generation Pilot](docs/conversation-understanding/decision-work-generated-read-triage-generation-pilot-v0.md)
adds PR193's first checked-in-safe generated triage read for launch beta. It
routes attention to caveated offline brief candidacy, source-depth limits,
private-context need, overtrust risk, and runtime attachment blocking while
still not grading answer quality, proving correctness, marking resolver refs
usable, updating sidecars, calling models, or authorizing action.
The
[Decision Work Generated Read Triage Pilot Review](docs/conversation-understanding/decision-work-generated-read-triage-pilot-review-v0.md)
adds PR194's review-only pass over that first triage read. It confirms the
route vocabulary remains attention routing rather than grading or action
permission, and gates to a deploy-intake second triage pilot without creating
that second case yet.
The
[Decision Work Generated Read Second Triage Pilot](docs/conversation-understanding/decision-work-generated-read-second-triage-pilot-v0.md)
adds PR195's deploy-intake generated triage read. It routes the healthcare
workflow case to source-depth limits, private-context need, high overtrust risk,
domain review, legal/compliance review, agent inspection only, not-ready-for-
user-surface, and runtime attachment blocking while still not grading answer
quality, clearing deployment, marking resolver refs usable, updating sidecars,
calling models, or authorizing action.
The
[Decision Work Generated Read Triage Two-Case Pattern Review](docs/conversation-understanding/decision-work-generated-read-triage-two-case-pattern-review-v0.md)
adds PR196's two-case triage pattern review. It confirms the route vocabulary
works across launch-beta and deploy-intake, keeps deploy-intake escalated for
domain/compliance review, and selects generated-read resolver supply planning
next without approving resolver refs, updating sidecars, wiring runtime,
calling models, scoring advice, proving value, or authorizing action.
The
[Decision Work Generated Read Resolver Supply Plan](docs/conversation-understanding/decision-work-generated-read-resolver-supply-plan-v0.md)
adds PR197's docs/review/tests-only plan for turning generated-read artifacts
and generated triage reads into future resolver-supply candidates. It separates
resolver supply from resolver approval, allows candidate packets to preserve
runtime/user-surface blocking, and gates to a deterministic adapter without
approving refs, updating sidecars, wiring runtime, scoring, proving, or
authorizing action.
The
[Decision Work Generated Read Resolver Supply Adapter](docs/conversation-understanding/decision-work-generated-read-resolver-supply-adapter-v0.md)
adds PR198's deterministic adapter and CLI. It emits
`lolla.decision_work_generated_read_resolver_supply.v0` candidate packets from
generated-read, intake, brief-supply, rendered-brief, triage-supply, and
generated-triage refs. Launch-beta can produce a candidate packet; deploy-
intake preserves runtime/user-surface blocking. Neither status approves refs,
updates sidecars, wires runtime, scores advice, proves value, or authorizes
action.
The
[Decision Work Generated Read Resolver Supply Review](docs/conversation-understanding/decision-work-generated-read-resolver-supply-review-v0.md)
adds PR199's review-only pass over the launch-beta and deploy-intake resolver-
supply candidate packets. It confirms candidate packets remain candidate
summaries, not resolver approval, runtime sidecar permission, user-surface
readiness, quality labels, proof, or action authorization, and gates to a
pre-runtime package manifest.
The
[Decision Work Automatic Semantic Supply Pre-Runtime v1 Package Gate](docs/conversation-understanding/decision-work-automatic-semantic-supply-pre-runtime-v1-package-gate-v0.md)
adds PR200's package gate and manifest for PR178-PR199. It packages the offline
pre-runtime chain from generated interpretation reads to resolver-supply
candidate packets, while explicitly excluding runtime attachment, resolver
approval, sidecar updates, runtime wiring, default-on behavior, production
automation, scoring, proof, human validation, advice correctness, and action
authorization.
The
[Decision Work Resolver Candidate Sidecar Update Plan](docs/conversation-understanding/decision-work-resolver-candidate-sidecar-update-plan-v0.md)
adds PR201's docs/review/tests-only plan for a future offline sidecar update
packet. The plan defines proposed packet fields and statuses while making clear
that a sidecar update packet is not a real `decision_work/` sidecar write, not
archive mutation, not resolver approval, not runtime wiring, not user-surface
readiness, and not action authorization.
The
[Decision Work Resolver Candidate Sidecar Update Packet Adapter](docs/conversation-understanding/decision-work-resolver-candidate-sidecar-update-packet-adapter-v0.md)
adds PR202's deterministic offline adapter and CLI for proposed sidecar update
packets. It can turn launch/deploy resolver-supply candidates into packet
artifacts while still refusing actual `decision_work/` sidecar writes, archive
mutation, resolver approval, runtime wiring, quality labels, proof claims, and
action authorization.
The
[Decision Work Sidecar Update Packet Review](docs/conversation-understanding/decision-work-sidecar-update-packet-review-v0.md)
adds PR203's docs/review/tests-only review of launch/deploy sidecar update
packets. It confirms proposed packets remain offline artifacts rather than
real sidecar writes, archive mutation, resolver approval, runtime wiring,
user-surface readiness, quality labels, proof claims, or action authorization,
and gates to a pre-write package.
The
[Decision Work Sidecar Update Packet Pre-Write Package Gate](docs/conversation-understanding/decision-work-sidecar-update-packet-prewrite-package-gate-v0.md)
adds PR204's package gate and manifest for PR201-PR203. It packages the
offline proposed sidecar update packet layer while still excluding actual
sidecar writes, archive mutation, runtime wiring, resolver approval, default-on
behavior, proof claims, scoring, and action authorization.
The
[Decision Work Runtime Sidecar Write Plan](docs/conversation-understanding/decision-work-runtime-sidecar-write-plan-v0.md)
adds PR205's docs/review/tests-only plan for the first actual sidecar-write
implementation. It keeps implementation out of scope and selects a future
default-off dry-run adapter, not a live write.
The
[Decision Work Sidecar Write Dry-Run Adapter](docs/conversation-understanding/decision-work-sidecar-write-dry-run-adapter-v0.md)
adds PR206's deterministic dry-run adapter and CLI. It consumes PR202 sidecar
update packets, emits `lolla.decision_work_sidecar_write_dry_run.v0`, and can
write preview files only under an explicit safe output directory while still
not writing `decision_work/`, mutating archives, approving resolver refs,
wiring runtime, scoring, proving, or authorizing action.
The
[Decision Work Sidecar Write Dry-Run Review](docs/conversation-understanding/decision-work-sidecar-write-dry-run-review-v0.md)
adds PR207's docs/review/tests-only review of launch/deploy dry-run outputs.
It confirms preview files remain temp/output-only, deploy preserves runtime
blocking, and actual sidecar writes, archive mutation, resolver approval,
runtime wiring, quality labels, proof claims, and action authorization remain
closed.
The
[Decision Work Sidecar Write Dry-Run Package Gate](docs/conversation-understanding/decision-work-sidecar-write-dry-run-package-gate-v0.md)
adds PR208's package gate and manifest for PR206-PR207. It packages the
offline dry-run preview layer while still excluding actual sidecar writes,
archive mutation, runtime wiring, resolver approval, default-on behavior,
proof claims, scoring, and action authorization.
The
[Decision Work Runtime Sidecar Write Contract](docs/conversation-understanding/decision-work-runtime-sidecar-write-contract-v0.md)
adds PR209's contract/docs/schema/tests-only gate for a future explicit
operator sidecar write adapter. It defines eligible input packets, dry-run
preconditions, write modes, statuses, allowed files, forbidden content, and
audit receipt requirements while still not writing sidecars, mutating archives,
wiring runtime, approving resolver refs, scoring, proving, or authorizing
action.
The
[Decision Work Explicit Operator Sidecar Write Adapter](docs/conversation-understanding/decision-work-explicit-operator-sidecar-write-adapter-v0.md)
adds PR210's deterministic fixture-only write adapter and CLI. It can write
sidecar-shaped files from a PR202 packet and matching PR206 dry-run result into
an explicit safe temp/output `decision_work` directory, emit
`lolla.decision_work_explicit_operator_sidecar_write_receipt.v0`, and preserve
that real archives, runtime wiring, resolver approval, quality labels, proof
claims, and action authorization remain closed.
The
[Decision Work Explicit Operator Sidecar Write Review](docs/conversation-understanding/decision-work-explicit-operator-sidecar-write-review-v0.md)
adds PR211's docs/review/tests-only check over launch/deploy fixture writes. It
confirms launch writes fixture-only, deploy preserves runtime-blocked fixture
state, path safety blocks repo/archive/runtime targets, and real archive
mutation, runtime wiring, resolver approval, proof claims, scoring, and action
authorization remain closed before any package gate.
The
[Decision Work Explicit Operator Sidecar Write Package Gate](docs/conversation-understanding/decision-work-explicit-operator-sidecar-write-package-gate-v0.md)
packages PR210-PR211 as a controlled explicit operator write v1 capability,
with a
[package manifest](docs/conversation-understanding/decision-work-explicit-operator-sidecar-write-package-manifest-v0.json).
It claims only safe fixture/operator target writes from validated packets and
matching dry-runs, while excluding runtime integration, default-on behavior,
real historical archive mutation as normal behavior, resolver approval,
customer readiness, proof, scoring, advice correctness, certification, and
action authorization.
The
[Decision Work Controlled Archive Sidecar Write Fixture Plan](docs/conversation-understanding/decision-work-controlled-archive-sidecar-write-fixture-plan-v0.md)
adds PR213's docs/review/tests-only plan for the next boundary: writing the
same allowed sidecar files into synthetic archive-shaped fixture directories.
Those fixtures may resemble completed-run archives for test/operator review,
but real archives, existing historical archive paths, runtime wiring, archive
hook edits, resolver approval, proof claims, scoring, and action authorization
remain forbidden.
The
[Decision Work Controlled Archive Sidecar Write Fixture Adapter](docs/conversation-understanding/decision-work-controlled-archive-sidecar-write-fixture-adapter-v0.md)
adds PR214's deterministic adapter and CLI for synthetic archive-shaped fixture
writes. It can write launch/deploy sidecar-shaped fixture directories under
explicit safe temp/operator archive-like roots, with launch
`fixture_write_completed` and deploy `fixture_write_completed_blocked_state`,
while still refusing real archives, existing historical archive paths, repo
paths, runtime paths, resolver approval, proof claims, scoring, and action
authorization.
The
[Decision Work Controlled Archive Sidecar Write Fixture Review](docs/conversation-understanding/decision-work-controlled-archive-sidecar-write-fixture-review-v0.md)
adds PR215's docs/review/tests-only check over those launch/deploy synthetic
archive-shaped fixture writes. It confirms deploy remains runtime/user-surface
blocked, unsafe path and source mismatch cases are rejected, and real archive
mutation, archive-hook edits, runtime wiring, resolver approval, proof claims,
scoring, and action authorization remain closed before a package gate.
The
[Decision Work Controlled Archive Sidecar Write Fixture Package Gate](docs/conversation-understanding/decision-work-controlled-archive-sidecar-write-fixture-package-gate-v0.md)
packages PR213-PR215 as controlled archive sidecar write fixture v1, with a
[package manifest](docs/conversation-understanding/decision-work-controlled-archive-sidecar-write-fixture-package-manifest-v0.json).
It claims only synthetic archive-shaped fixture writes under safe temp/operator
roots, while still excluding real archive mutation, archive-hook integration,
runtime wiring, resolver approval, default-on behavior, proof claims, scoring,
advice correctness, certification, and action authorization.
The
[Decision Work Sidecar Internal v1 Completion PRD](docs/conversation-understanding/decision-work-sidecar-internal-v1-completion-prd-v0.md)
adds PR217's current-state and finish-line anchor before real archive writes.
It defines Internal v1 as complete only when an operator can validate safe
generated Decision Work artifacts, dry-run the sidecar, and explicitly write a
`decision_work/` sidecar into a real completed-run archive through a controlled
command with receipts and hard non-claims. It records a six-PR ballpark path
from PR218 through PR223 and recommends PR218 Real Archive Sidecar Write Plan
v0 next, without implementing that plan.
The
[Decision Work Real Archive Sidecar Write Plan](docs/conversation-understanding/decision-work-real-archive-sidecar-write-plan-v0.md)
adds PR218's docs/review/tests-only plan for the first controlled real archive
write boundary. It defines explicit operator confirmation, completed-run
archive markers, no-overwrite policy, receipt semantics, launch/deploy behavior,
and fail-closed refusal rules before any adapter writes real archive sidecars.
The
[Decision Work Real Archive Sidecar Write Adapter](docs/conversation-understanding/decision-work-real-archive-sidecar-write-adapter-v0.md)
adds PR219's command-only adapter and CLI. It can write the allowed
`decision_work/` sidecar file set into an explicitly supplied archive-markered
completed-run directory only with operator confirmation, preserves deploy's
blocked state, refuses existing sidecars and unsafe inputs, and still does not
wire runtime, edit archive hooks, approve resolver refs, score, prove, or
authorize action.
The
[Decision Work Real Archive Sidecar Write Review](docs/conversation-understanding/decision-work-real-archive-sidecar-write-review-v0.md)
adds PR220's docs/review/tests-only check over fresh launch/deploy synthetic
completed-run archive writes. It confirms the allowed file set, no-overwrite
and unsafe-input refusals, deploy blocked-state preservation, and no runtime
wiring, archive-hook edit, resolver approval, default-on behavior, proof
claims, scoring, or action authorization before a package gate.
The
[Decision Work Real Archive Sidecar Write Package Gate](docs/conversation-understanding/decision-work-real-archive-sidecar-write-package-gate-v0.md)
packages PR218-PR220 as real archive sidecar write v1, with a
[package manifest](docs/conversation-understanding/decision-work-real-archive-sidecar-write-package-manifest-v0.json).
It claims only a command-only, explicit-operator, no-overwrite write layer
validated against synthetic completed-run archive dirs, while still excluding
runtime wiring, archive-hook integration, default-on behavior, resolver
approval, proof claims, scoring, advice correctness, certification, and action
authorization.
The
[Decision Work Sidecar Internal v1 Operator Runbook](docs/conversation-understanding/decision-work-sidecar-internal-v1-operator-runbook-v0.md)
adds PR222's docs/tests-only internal operator flow from generated read intake
through brief supply, rendered brief, triage supply, generated triage,
resolver-supply candidate, sidecar update packet, dry-run, command-only archive
sidecar write, and receipt inspection. It uses placeholder paths only and does
not add runtime wiring, archive-hook integration, resolver approval, default-on
behavior, proof claims, scoring, advice correctness, certification, or action
authorization.
The
[Decision Work Sidecar Internal v1 Current State](docs/board/decision-work-sidecar-internal-v1-current-state.md)
adds PR223's board/product-readable closeout narrative. It states that Sidecar
Internal v1 is functional as a command-only, explicit-operator, no-overwrite
sidecar pipeline for validated Decision Work artifacts, while still not being
customer-ready automation, default-on runtime behavior, product proof, human
validation, advice correctness, scoring, approval, or action authorization.
The
[Decision Work Sidecar Automation Readiness PRD](docs/conversation-understanding/decision-work-sidecar-automation-readiness-prd-v0.md)
adds PR224's phase anchor after Internal v1. It defines automation readiness
as a conservative offline/operator phase for newly completed runs, records
sidecar-ready, blocked, deferred, and rejected statuses, and recommends a
9-12 PR roadmap beginning with an offline operator runner plan while still not
implementing a runner, queue worker, runtime hook, resolver approval,
provider/model call, default-on behavior, proof claims, scoring, or action
authorization.
The
[Decision Work Offline Operator Runner Plan](docs/conversation-understanding/decision-work-offline-operator-runner-plan-v0.md)
adds PR225's plan-only first slice for that phase. It chooses a one-shot,
command-only offline runner that will orchestrate existing deterministic CLIs
from explicit generated-read, generated-triage, completed-archive, case, and
safe-output paths, produce `runner_summary.json`, and stop at each boundary
without adding semantic interpretation, queue workers, runtime wiring,
resolver approval, overwrites, proof claims, scoring, or action authorization.
The
[Decision Work Offline Operator Runner Adapter](docs/conversation-understanding/decision-work-offline-operator-runner-adapter-v0.md)
adds PR226's command-only runner and CLI. It orchestrates the existing
deterministic chain from generated-read intake through sidecar write dry-run,
emits `lolla.decision_work_offline_operator_runner.v0`, preserves launch/deploy
blocked-state differences, and never calls the real archive write adapter.
Write flags stop before explicit write, so there is still no sidecar write,
archive mutation, runtime wiring, resolver approval, scoring, proof claim, or
action authorization.
The
[Decision Work Offline Operator Runner Fixture Review](docs/conversation-understanding/decision-work-offline-operator-runner-fixture-review-v0.md)
adds PR227's review of the runner over controlled launch/deploy fixtures and
blocker fixtures. It confirms launch reaches dry-run readiness, deploy
preserves blocked-state readiness, missing inputs defer, unsafe inputs block,
write requests stop before explicit write, and no checked-in sidecar outputs,
real archive mutation, runtime wiring, resolver approval, scoring, proof
claim, or action authorization occur.
There is still no default-on runtime integration, model call in repo code,
historical archive mutation, product proof, human validation, broad batch,
customer marketing copy, or agent action authorization. See
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
