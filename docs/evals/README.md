# Product Delta / Eval Docs Index

Status: GitHub-facing eval navigation

This directory contains the evidence and evaluation layer around Lolla. The
main thing to understand is the split between the live skill and the offline
eval lane.

```text
Lolla runtime:
  captures a serious conversation
  runs the reasoning audit
  produces a revised decision answer
  archives custody artifacts

Product Delta eval lane:
  reads existing safe artifacts later
  checks whether cases are reviewable
  prepares provisional review packets
  preserves uncertainty and disagreement
  lints against overclaiming
  prepares later human validation
```

The runtime produces the object of study. The eval lane studies that object
later. The eval lane does not run `$lolla`, invoke the skill, call providers,
mutate archives, change prompts, change runtime behavior, score answer
quality, create automatic labels, or authorize agent action.

## Big Picture

Lolla is trying to sit between fluent AI advice and real action.

The product question is not:

```text
Did the second answer sound better?
```

The product question is:

```text
Did structured audit pressure create a decision-useful delta that a reviewer
can inspect without pretending certainty?
```

That means the eval lane cares about concrete changes:

- action changed;
- threshold changed;
- sequence changed;
- evidence gate or stop rule appeared;
- scope narrowed;
- overclaim was retracted;
- a stakeholder, value, constraint, or unresolved question was preserved;
- uncertainty became visible in a way that matters.

It also cares about losses:

- useful original advice got weakened;
- ambition or momentum was buried under generic prudence;
- Lolla added process without leverage;
- the revised answer became longer but not more actionable;
- the system misunderstood the conversation;
- a clean artifact made weak evidence look stronger than it is.

## What To Look For

When reading Product Delta artifacts, look for:

- `vanilla_likely_next_action`: what the user seemed likely to do before Lolla;
- `lolla_likely_next_action`: what the revised answer seemed to make more likely;
- `material_difference`: whether the candidate delta changes a decision-relevant thing;
- `structural_delta`: action, threshold, sequence, gate, stop rule, scope, written term, or question changes;
- `useful_friction`: pressure that changes action or review burden in a useful way;
- `noisy_friction`: caution, delay, or structure that does not add decision leverage;
- `lost_value`: what the revised answer may have weakened or overwritten;
- `interpretation_adequacy`: whether Lolla and the reviewer understood the conversation well enough;
- source refs, field statuses, missingness, and uncertainty notes;
- human follow-up questions and falsification notes.

The healthiest current Product Delta signal is not a bigger win count. It is a
downgrade:

```text
accept-operations-role-startup
material_improvement_candidate -> partial_improvement_candidate
```

That downgrade matters because the specialist review preserved lost value,
value-overwrite risk, user-specific ambition, and written-gate proportionality
uncertainty instead of laundering a broad positive read into a smoother
conclusion.

## What Not To Infer

Product Delta artifacts do not prove:

- Lolla improves decisions;
- Codex-assisted reads are human labels;
- a judge is calibrated;
- clean artifacts imply good advice;
- a candidate label is ground truth;
- an agent may act on the revised answer;
- a lint-clean package is product proof.

Current Codex-assisted reads are provisional, internal, and lower-claim. Human
review later must validate, correct, or reject them.

## How We Evaluate

The current non-human phase uses four layers:

1. **Protocol and taxonomy.** Define what counts as a candidate product delta,
   useful friction, noisy friction, lost value, interpretation adequacy, and
   failure.
2. **Read-only deterministic tooling.** Build readiness reports, review shells,
   specialist packets, and boundary lint from existing safe artifacts.
3. **Context-engineered specialist reads.** Decompose broad judgment into
   narrow provisional reads, such as conversation interpretation, likely next
   actions, structural delta, friction/lost value, and overclaim risk.
4. **Conservative fan-in.** Preserve disagreement, downgrade pressure,
   missingness, and human follow-up questions without voting or scoring.

The point is not to create an LLM judge. The point is to make provisional
interpretation more inspectable.

## Safe Commands

Build a read-only Product Delta readiness report and PR72-shaped shells:

```bash
python3 scripts/evals/build_product_delta_provisional_review.py \
  --case-list docs/evals/product-delta-seed-cases-v0.json \
  --out /tmp/product_delta_readiness.md \
  --json-out /tmp/product_delta_readiness.json
```

Build checked-in-safe specialist packets from existing eval artifacts:

```bash
python3 scripts/evals/build_product_delta_specialist_packets.py \
  --case-list docs/evals/product-delta-seed-cases-v0.json \
  --provisional-review reviews/codex-assisted/product-delta-provisional-run-v0/review.json \
  --codex-batch reviews/codex-assisted/product-delta-batch-v0/review.json \
  --limit 2 \
  --out /tmp/product_delta_specialist_packets.json
```

Run deterministic boundary lint over selected Product Delta artifacts:

```bash
python3 scripts/evals/lint_product_delta_evidence.py --paths \
  docs/evals/product-delta-provisional-report-v0.md \
  reviews/codex-assisted/product-delta-batch-v0/review.json \
  reviews/codex-assisted/specialist-review-batch-v0/review.json \
  reviews/codex-assisted/fan-in-disagreement-report-v0/report.json
```

Run the focused Product Delta tests:

```bash
python3 -m pytest -q \
  tests/test_product_delta_pr71_pr84_package_gate.py \
  tests/test_product_delta_fan_in_disagreement_report.py \
  tests/test_codex_assisted_specialist_review_batch.py \
  tests/test_provisional_reviewer_trap_set.py \
  tests/test_product_delta_specialist_packets.py \
  tests/test_product_delta_specialist_contracts.py \
  tests/test_product_delta_boundary_lint.py \
  tests/test_product_delta_batch_fixture.py \
  tests/test_product_delta_readiness.py
```

These commands are read-only against the Lolla runtime. They do not run the
skill, call providers, mutate archives, or create product proof.

## Current Phase Map

Start with these:

| File | Purpose |
|---|---|
| [Product Delta Evidence Thesis](product-delta-evidence-thesis-v0.md) | The PR71 claim, baseline, lower-claim doctrine, and Product Delta vocabulary. |
| [Product Delta Evidence And Interpretation Adequacy](product-delta-evidence-and-interpretation-adequacy-v0.md) | The bridge from audit machinery to product-delta evidence and why conversation interpretation is load-bearing. |
| [Vanilla-vs-Lolla Provisional Review Protocol](vanilla-vs-lolla-provisional-review-protocol-v0.md) | The PR72 review protocol and field shape. |
| [Product Delta Provisional Report](product-delta-provisional-report-v0.md) | PR77's report over readiness and broad Codex-assisted provisional reads. |
| [Product Delta Evidence Boundary Lint](product-delta-evidence-boundary-lint-v0.md) | PR78's deterministic non-claim and privacy-boundary lint. |
| [Context-Engineered Provisional Review Architecture](context-engineered-provisional-review-architecture-v0.md) | PR79's rejection of a broad judge in favor of bounded specialist reads. |
| [Product Delta Specialist Review Contracts](product-delta-specialist-review-contracts-v0.md) | PR80's typed contracts for specialist reads and fan-in. |
| [Product Delta Specialist Packet Builder](product-delta-specialist-packet-builder-v0.md) | PR81's read-only packetization stage. |
| [Provisional Reviewer Trap Set](provisional-reviewer-trap-set-v0.md) | PR82's checked-in-safe traps for thin context, length bias, lost value, and overclaim hardening. |
| [Codex-Assisted Specialist Review Batch](codex-assisted-specialist-review-batch-v0.md) | PR83's trap discipline and two-case specialist batch. |
| [Product Delta Fan-In / Disagreement Report](product-delta-fan-in-disagreement-report-v0.md) | PR84's static comparison of broad PR76 reads and specialist PR83 reads. |
| [Product Delta PR71-PR84 Packaging Gate](product-delta-pr71-pr84-packaging-gate-v0.md) | PR85's package manifest, validation boundary, useful signal, and unresolved risk. |
| [Product Delta Evaluation Readiness PRD](product-delta-evaluation-readiness-prd-v0.md) | PR235's eval-phase PRD: summarize existing Product Delta, Human Review, and Review Corpus lanes; preserve the downgrade signal; reject live judging as the immediate move; and choose a balanced offline Product Delta evidence batch next. |
| [Balanced Offline Product Delta Evidence Batch Plan](balanced-offline-product-delta-evidence-batch-plan-v0.md) | PR236's plan-only balanced-batch slice: define buckets, source rules, privacy/custody rules, check-in policy, anti-overclaim rules, and the candidate-selector plan gate without selecting cases or running a batch. |
| [Balanced Batch Candidate Selector / Readiness Builder Plan](balanced-batch-candidate-selector-readiness-builder-plan-v0.md) | PR237's plan-only selector/readiness-builder slice: define safe source signals, bucket hypotheses, readiness criteria, output shape, refusal/defer statuses, and anti-flattery rules before any selector implementation or Product Delta batch run. |

## Runtime And Skill Opportunities

From the skill perspective, the eval lane shows which runtime artifacts matter
most for future review:

- `agent_result.json` for compact run status, caller action, artifact refs, and
  product-level summary fields;
- `evaluation.json` for deterministic artifact/schema/custody/health checks;
- `reasoning_trace.json` for local custody, path/hash references, run health,
  usage, and model-call metadata without duplicating raw transcript text;
- review-corpus exports for case selection and human-review queues;
- audit decision records for safe accountability shells;
- Product Delta packets for narrower future interpretation reads.

The opportunity is to keep improving what the runtime preserves so later
reviewers can inspect decision deltas without raw/private leakage or fake
certainty. That does not require making Product Delta eval part of the live
skill. For now, the split is intentional.

## Current Stop Line

The PR71-PR85 non-human Product Delta phase is packaged. It is coherent enough
to inspect, lint, and use as internal scaffolding. It is not broad enough or
human-reviewed enough to claim product proof.

The new Product Delta Evaluation Readiness PRD keeps that boundary and selects
a balanced offline evidence batch before any live evaluator. The next PR should
plan that batch rather than build a live judge.

The Balanced Offline Product Delta Evidence Batch Plan now defines that batch
shape. The next PR should plan the candidate selector/readiness builder rather
than run Product Delta review.

The Balanced Batch Candidate Selector / Readiness Builder Plan now defines how
a future deterministic selector should choose candidate cases from explicit
safe source scopes, existing metadata, provisional labels, specialist fan-in,
human-review taxonomy hints, run-health/capture metadata, and review-corpus
readiness metadata. It stops before selector implementation, broad archive
scans, Product Delta review runs, model/provider calls, live judging, answer
scoring, or product-proof claims.

Good next moves later include:

- human-review intake over the current packets and reports;
- local-private packet mode for deeper interpretation adequacy review;
- a larger specialist batch that includes no-change, noise, worse, and
  inconclusive real cases;
- more trap fixtures if a specific failure mode repeats.

Do not expand this lane just to create more artifacts. New work should answer a
specific evidence question.
