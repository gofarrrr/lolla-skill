# PR61 Targeted v23 Guard Enrichment Report

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr61-targeted-v23-guard-enrichment`

Status: dormant reviewed substrate only; no runtime pickup

## Purpose

PR61 continues the post-v18 enrichment pass after v22. This round adds no positive affordances. It adds source-backed absence rails where current cards could otherwise be promoted too eagerly by a future receiver.

The question is not whether the source is rich. Most sources are rich. The stricter question is:

> Would this extra rail change a future use, reject, or defer decision?

These seven did. Agile-methodologies was reviewed and rejected for this round because its fixed-dependency warning is already first-class inside the existing affordance.

## Artifact

- Previous artifact: `model_affordances_v22`
- New artifact: `model_affordances_v23`
- Path: `data/compiled/model_affordances/affordances_v23.json`
- Status: `draft_review_only`
- Records: `222`
- Affordances: `268`
- Absence records: `441`
- Schema validation failures: `0`
- Source quote rejections: `0`

Delta from v22:

- `+0` affordances
- `+7` absence records
- `+0` records
- no live runtime import

## Added Absence Rails

### `problem-framing-and-reframing`: `technical-frame-without-organizational-context`

Blocks a technically correct or content-only frame when organizational attitudes, politics, management style, fear, or social-system effects visibly shape the problem.

Why absence, not positive affordance:

- The existing alternative-frame affordance already covers frame comparison.
- This is a reject/defer rail for a frame that omits the management/social context, not a fourth positive framing move.

### `elasticity`: `elastic-snippet-without-relevance-quality-check`

Blocks elastic context compression when retrieved snippets are irrelevant, low quality, or likely to skew the answer.

Why absence, not positive affordance:

- The existing elasticity card already mentions dynamic context triage.
- The missing runtime behavior is a quality gate before trusting elastic snippets.

### `constructive-feedback-models`: `case-at-hand-correction-without-process-diagnosis`

Blocks person-focused or incident-only correction when the machine/process that produced the outcome is visible but unexamined.

Why absence, not positive affordance:

- A machine-level positive split would overlap with systems-thinking, root-cause-analysis, and feedback-loops.
- The transaction-distinct behavior is a blocker: do not stop at personal correction when process evidence matters.

### `internal-locus-of-control`: `agency-as-dismissal-of-opposing-feedback`

Blocks agency language when felt control becomes arrogance, dismissive impatience, or selective perception against opposing evidence.

Why absence, not positive affordance:

- The existing card already maps controllable levers and constraints.
- This rail prevents agency from becoming an excuse to ignore corrective signals.

### `meta-cognitive-reflection`: `rationalization-as-reflection`

Blocks post-hoc rationalization presented as genuine self-audit.

Why absence, not positive affordance:

- The existing card already handles bounded reflection and action loops.
- This rail distinguishes real reflection from the conscious mind defending decisions already made.

### `active-listening`: `vulnerability-probing-without-containment`

Blocks listening moves that invite vulnerability and then abandon the emotional content without containment or responsible follow-through.

Why absence, not positive affordance:

- The existing card already covers diagnose-before-advice and anti-performative listening.
- This rail protects trust after disclosure rather than adding another listening technique.

### `chaos-theory`: `imposed-will-without-system-listening`

Blocks chaos language used to force a preferred intervention while ignoring observed system behavior.

Why absence, not positive affordance:

- The existing card already covers resilience-over-precision bet sizing.
- This is the opposite-side guard from fatalism and exact optimization: do not impose will while pretending to respect nonlinearity.

## Rejected This Round

### `agile-methodologies`

Rejected for PR61. The source supports a warning that Agile can deny fixed external commitments, interfaces, or regulatory constraints, but the current affordance already carries that warning in `do_not_use_when`, `case_evidence_needed`, diagnostic questions, and source evidence.

Adding another absence now would mostly duplicate current behavior. If packet review later shows receivers still over-promote Agile under fixed dependencies, this can be revisited with packet evidence.

## Runtime Safety

No runtime, prompt, packet, lane, Observatory, or product path was changed.

The v23 artifact remains dormant and review-only. Future live pickup still needs explicit artifact selection; PR61 adds no latest-file behavior and no receiver instruction changes.

## Validation

Target validation:

```bash
python3 -c "from pathlib import Path; import sys; sys.path.insert(0, str(Path('engine').resolve())); from system_b.model_affordance_validation import validate_model_affordance_file; files=[Path('data/model_affordances/pilot/problem-framing-and-reframing.json'), Path('data/model_affordances/batch_16/elasticity.json'), Path('data/model_affordances/batch_6/constructive-feedback-models.json'), Path('data/model_affordances/batch_14/internal-locus-of-control.json'), Path('data/model_affordances/batch_17/meta-cognitive-reflection.json'), Path('data/model_affordances/batch_6/active-listening.json'), Path('data/model_affordances/batch_9/chaos-theory.json')]; [validate_model_affordance_file(f, source_roots=(Path('data/model_sources'),)) for f in files]; print('validation_ok', len(files))"
```

Compile:

```bash
python3 scripts/compile_model_affordances.py --record-dir data/model_affordances/pilot --record-dir data/model_affordances/batch_1 --record-dir data/model_affordances/batch_2 --record-dir data/model_affordances/batch_3a --record-dir data/model_affordances/batch_4 --record-dir data/model_affordances/batch_5 --record-dir data/model_affordances/batch_6 --record-dir data/model_affordances/batch_7 --record-dir data/model_affordances/batch_8 --record-dir data/model_affordances/batch_9 --record-dir data/model_affordances/batch_10 --record-dir data/model_affordances/batch_11 --record-dir data/model_affordances/batch_12 --record-dir data/model_affordances/batch_13 --record-dir data/model_affordances/batch_14 --record-dir data/model_affordances/batch_15 --record-dir data/model_affordances/batch_16 --record-dir data/model_affordances/batch_17 --compiled-filename affordances_v23.json --quality-report-filename quality_report_v23.md --artifact-id model_affordances_v23 --report-title "Model Affordance Quality Report v23"
```

Expected focused test set:

```bash
pytest tests/test_pr61_v23_guard_enrichment.py tests/test_pr60_v22_guard_enrichment.py tests/test_model_affordance_pilot.py tests/test_model_affordance_compiler.py tests/test_pr34_batch6_records.py tests/test_pr42_batch9_records.py tests/test_pr51_batch14_records.py tests/test_pr53_batch16_records.py tests/test_pr54_batch17_records.py
```

## Bottom Line

PR61 strengthens absence-first treatment. It keeps positive affordance count fixed and adds seven precise blockers for bad promotion:

- technical framing that hides organizational context;
- elastic snippets without relevance quality;
- feedback that stops at the person/case and misses process diagnosis;
- agency that dismisses opposing feedback;
- reflection that is really rationalization;
- listening that invites vulnerability without containment;
- chaos language that imposes will instead of listening to the system.

This is a less-wrong improvement, not a broader dump.
