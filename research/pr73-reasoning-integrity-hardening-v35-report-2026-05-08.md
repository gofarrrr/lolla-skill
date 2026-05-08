# PR73 v35 Reasoning-Integrity Hardening Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr73-reasoning-integrity-v35`

## Verdict

PASS as dormant reviewed substrate.

PR73 is not a runtime pickup change. It does not touch `/lolla`, prompts, packet rendering, lane adapters, or product behavior.

This pass is intentionally not a split/enrichment batch. It hardens reasoning-integrity records without adding new positive affordance IDs.

## Why This PR Exists

PR72 proved that positive splits can be added safely when the downstream transaction changes. PR73 tested the same question on reasoning-integrity records:

> Do Chain of Thought, Chain of Verification, Critical Thinking, and Falsifiability need more affordance identity, or better misuse/routing precision?

The answer was mostly better precision.

Adding new positive cards here would have created a near-duplicate reasoning-integrity pile: name assumptions, test evidence, avoid theater. That would make the corpus louder without making packets sharper.

## Source Files Re-Read

Canonical source files were read directly:

- `MM_CANONICAL_216/Chain_Of_Thought_rag.md`
- `MM_CANONICAL_216/Chain_Of_Verification_rag.md`
- `MM_CANONICAL_216/Falsifiability_rag.md`
- `MM_CANONICAL_216/Critical_Thinking_rag.md`

Adjacent ownership was also checked before adding anything:

- `conjunction-fallacy.sequence-probability-stress-test`
- `decomposition.mece-key-driver-action-map`
- `decomposition.test-cuts-and-assumptions`
- `emotional-intelligence.emotion-evidence-landing-check`
- `empathy.ground-reframing-in-stakeholder-evidence`

## Changes Made

### Chain of Thought

No new positive affordance.

Existing affordance hardened:

- `chain-of-thought.audit-stepwise-reasoning`

Added treatment requirement:

- `prune-chain-to-governing-answer`

Purpose:

Chain of Thought should not become a displayed reasoning dump. The source supports pruning branches, finding the one-day answer, and reconnecting stepwise reasoning to a governing answer or solution path.

The added requirement makes the card better at saying:

- use stepwise reasoning only when it exposes weak links;
- prune branches that do not change the answer;
- state the governing answer after the chain is audited.

### Chain of Verification

No new positive affordance.

Added absence/routing guard:

- `sequence-probability-stress-test-as-chain-of-verification`

Purpose:

The source mentions conjunctive success, but cumulative probability stress testing is better owned by `conjunction-fallacy` unless the case also needs an auditable evidence trail for each link before proceeding.

Routing rule:

- Chain of Verification owns evidence-backed link verification and auditable trails.
- Conjunction Fallacy owns cumulative success-probability fragility.
- Base Rates owns reference-class priors.
- Survivorship Bias owns hidden failure distributions.

### Critical Thinking

No new positive affordance.

Existing affordance hardened:

- `critical-thinking.claim-evidence-assumption-check`

Added treatment requirements:

- `preserve-personal-data-and-action-threshold`
- `test-active-framework-fit`

Added absence/routing guards:

- `emotion-filtered-rationality-as-critical-thinking`
- `standalone-problem-disaggregation-as-critical-thinking`

Purpose:

Critical Thinking should not become detached rationality theater. The source explicitly warns that ignoring emotional content in high-stakes human problems can miss crucial personal data. It also includes problem disaggregation, MECE, WHTB, and framework-fit material, but generic decomposition work is better owned by `decomposition`.

The hardening makes the card better at saying:

- do not filter out personal/emotional data before checking whether it changes the judgment;
- validate personal data rather than treating emotion as proof;
- if a named framework carries the claim, test the assumptions and context fit;
- route generic decomposition/framework work to decomposition unless the live transaction is claim/evidence/assumption scrutiny.

### Falsifiability

No change.

The existing record is already transaction-clean:

- `falsifiability.disconfirming-reversal-gate`

It already owns user-verifiable disconfirming observations, thresholds, reversal conditions, and anti-theater guards. Splitting red-team, dialectic, sensitivity analysis, or AI validation into new positive cards would weaken the record rather than improve it.

## v35 Artifact Summary

Compiled artifact:

- `data/compiled/model_affordances/affordances_v35.json`
- `data/compiled/model_affordances/quality_report_v35.md`

Metadata:

- Artifact: `model_affordances_v35`
- Status: `draft_review_only`
- Records: 222
- Affordances: 271
- Absence records: 501
- Schema failures: 0
- Source hash failures: 0
- Source quote rejections: 0

Delta from v34:

- Affordances: 271 -> 271
- Absences: 498 -> 501

Target record shapes:

- `chain-of-thought`: 1 affordance, 4 absences, 2 treatment requirements
- `chain-of-verification`: 1 affordance, 4 absences, 2 treatment requirements
- `critical-thinking`: 1 affordance, 4 absences, 3 treatment requirements
- `falsifiability`: 1 affordance, 2 absences, 3 treatment requirements

## Why This Is Not Bloat

PR73 adds no positive affordance IDs.

It blocks the tempting expansion path:

- Chain of Verification does not become a second Conjunction Fallacy card.
- Critical Thinking does not become generic Decomposition.
- Critical Thinking does not swallow Emotional Intelligence or Empathy.
- Chain of Thought does not become transcript theater.
- Falsifiability remains one clear reversal-gate record.

The useful work is precision: better requirements and better “do not promote” rails.

## Runtime Safety

This PR remains dormant substrate only.

No live runtime path imports v35. The PR73 test scans:

- `engine/system_b/__init__.py`
- `engine/system_b/pipeline.py`
- `engine/system_b/reasoning_substrate_packet.py`
- `engine/system_b/reasoning_substrate_packet_review.py`
- `scripts/run_pipeline.py`

Expected result: `affordances_v35` and `model_affordances_v35` appear only in tests and compiled artifact files, not live runtime paths.

## Verification

```bash
pytest tests/test_pr73_v35_reasoning_integrity_hardening.py \
  tests/test_pr72_v34_split_candidate_enrichment.py \
  tests/test_pr71_v33_low_absence_guard_enrichment.py \
  tests/test_pr70_v32_medium_supported_guard_enrichment.py \
  tests/test_pr69_v31_weak_support_guard_enrichment.py \
  tests/test_model_affordance_compiler.py

rg -n "affordances_v35|model_affordances_v35" engine scripts tests -g '*.py'

git diff --check
```

## Next Corpus Frontier

The next pass should continue this pattern:

1. Read full canonical source.
2. Check adjacent ownership before adding positives.
3. Add positive affordance identity only when the receiver transaction changes.
4. Otherwise prefer treatment hardening, absence rails, and routing guards.

Good next targets are one-affordance records where the source likely has multiple operational modes but adjacent ownership may already be strong:

- `chain-of-thought` style reasoning cards are probably mostly hardening candidates.
- broad communication cards need especially strict routing.
- decision/risk cards should be checked against base-rates, expected-value, probabilistic-thinking, conjunction-fallacy, and survivorship-bias before splitting.

The corpus is getting sharper when it learns when not to expand.
