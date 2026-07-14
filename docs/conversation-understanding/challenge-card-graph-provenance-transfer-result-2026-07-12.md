# Challenge-card graph-provenance transfer result — 2026-07-12

## Decision

Challenge cards and fact-free recall provenance pass their deterministic boundary, but the selector remains semantically inert. The housing transfer probe failed because every arm abstained. No runtime or graph integration is authorized.

## What improved

- all 222 models have challenge-oriented cards built from curated input/output types, failure modes, and premortem questions;
- ambiguous `danger_when` metadata is no longer mislabeled as an exclusion;
- every graph candidate carries controlled `recalled_by_mechanism_ids`;
- direct candidates cannot falsely claim graph provenance;
- unknown mechanisms, invented models, malformed custody, and forced outputs fail locally;
- housing prompts stayed below 12.3 KB with five to eight candidates.

## Frozen result

- provider calls: 3/3 operational;
- estimated cost: `$0.00053781`;
- source/provider selected-ID invariance: passed trivially with empty sets;
- canonical custody and unsupported-selection gates: passed;
- protected `premortem` activation: failed;
- source, provider, and ablation selections: all empty.

## Why it failed

The selector received recall mechanism IDs but not their operational definitions. Canonical identity again substituted for semantic meaning. Its `premortem` card described a superficial premortem failure, not why a missing reversal condition makes premortem relevant.

The global envelope also made abstention much cheaper than evaluating every candidate. After two distinct selector designs produced blanket abstention, the product constitution's problem-class trigger fired. The accompanying research note maps the failure to selective classification, cognitive load, and abstention framing research.

## Next boundary

Replace generative subset selection with exhaustive per-candidate semantic assessment. Include full fact-free mechanism cards alongside model challenge cards. Deterministic code requires complete candidate coverage and routes only rows the model labels `applicable`; it never changes a semantic label. Preserve `ambiguous`, `not_applicable`, and `insufficient_evidence` per candidate.

No new provider call is authorized until that provider-free contract passes adversarial completeness, custody, polarity, false-abstention, and source-entailment review on a new case.

## Evidence

- cards and packets: `research/challenge-card-graph-provenance-transfer-corpus-2026-07-12/`
- frozen target: `docs/evals/challenge-card-graph-provenance-transfer-target-v1.json`
- calls: `research/challenge-card-graph-provenance-transfer-probe-2026-07-12/`
- problem-class review: `docs/conversation-understanding/canonical-candidate-abstention-problem-class-2026-07-12.md`

