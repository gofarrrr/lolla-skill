# Specialist Extractor Probe Runner v0

PR29A adds a local/offline runner harness for probing existing specialist
extractors with deterministic fake boundary payloads.

This is not a real specialist-quality probe yet. It proves the custody,
validation, comparison, and output contract before any model calls are approved.

## Purpose

PR28 found that the existing specialist extractors may help with repeated
semantic coverage gaps, but each extractor requires a boundary object with
`run_json(...)` to generate candidates:

- `extract_live_constraints(...)`
- `extract_stance_events(...)`
- `extract_dropped_threads(...)`

PR29A keeps those extractors behind an injected fake boundary. That lets the
repo verify:

- candidate validation is exercised;
- invalid candidates are dropped and counted;
- specialist outputs can be injected through `construct_conversation_ir(...)`;
- baseline and enhanced semantic coverage summaries can be compared;
- the JSON artifact does not leak raw archive text or local machine paths;
- archives are not mutated.

## What The Runner Does

The runner reads one archived run directory and:

1. Builds the baseline PR26 semantic coverage report in memory.
2. Loads `ConversationContext` from `conversation.txt` and `extraction.json`.
3. Runs selected existing specialist extractors through a fake boundary.
4. Rebuilds `ConversationIR` using the existing injection hooks.
5. Compares baseline coverage with specialist-enhanced coverage.
6. Writes a compact JSON probe result.

The schema version is:

```text
lolla.specialist_extractor_probe.v0
```

The output includes:

- run identity from `case_id`, `run_id`, and `archive_relpath`;
- local-only source scope flags;
- baseline semantic coverage summary;
- enhanced semantic coverage summary;
- attempted specialists;
- model-call counters, fixed at zero in this PR;
- per-specialist candidate, validation, grounding, and improvement counts;
- notes and non-goals.

## Fake Boundary Fixture

The CLI requires a JSON fixture with any of these keys:

```json
{
  "live_constraints": [],
  "stance_events": [],
  "dropped_threads": []
}
```

Each list is handed to the corresponding existing extractor as if it came from
`boundary.run_json(...)`. The extractor validation layer still runs, so
non-substrings, invalid turns, and invalid taxonomy values are dropped by the
same local validation code a real probe would use.

This fixture exists only to validate the harness. It is not evidence that real
model-generated specialist candidates are good, stable, cheap, or worth
integrating.

## CLI

Example:

```bash
python3 scripts/probe_specialist_extractors.py \
  /path/to/archive/run \
  --fake-boundary /path/to/fake_boundary.json \
  --out /tmp/lolla_specialist_probe.json \
  --all
```

To run a subset:

```bash
python3 scripts/probe_specialist_extractors.py \
  /path/to/archive/run \
  --fake-boundary /path/to/fake_boundary.json \
  --out /tmp/lolla_specialist_probe.json \
  --specialist live_constraints \
  --specialist stance
```

The CLI returns nonzero for missing run directories, malformed fake-boundary
JSON, invalid specialists, or output-path errors. It rejects `--out` paths
inside the archived run directory so the probe cannot write into the archive.
It does not call models.

## Privacy And Custody

The probe may read raw local archive artifacts internally because specialist
validation needs transcript context. The exported probe result must not include:

- raw transcript text;
- memo text;
- revised-answer text;
- model messages;
- provider reasoning details;
- failed quote text;
- absolute local archive paths;
- control argument values.

The runner does not mutate archive folders and does not write
`semantic_coverage_report.json` into the archive.

## What This Proves

PR29A proves the runner contract can be tested without model calls:

- fake live-constraint candidates can improve `live_constraints` grounding;
- fake stance candidates can improve assistant stance lineage grounding;
- fake dropped-thread candidates can improve dropped-thread grounding;
- invalid candidates are dropped and counted;
- output is deterministic and custody-safe.

It does not prove that real specialist extractors improve semantic coverage on
modern runs. That requires explicit model-call approval and cost/custody
reporting.

## Recommended Next Slice

Only after this harness is merged and model calls are explicitly approved, the
next slice can be:

```text
real_specialist_extractor_probe_on_four_modern_runs
```

That later probe should run the actual specialists on the four modern baseline
archives, record model-call counts and cost, measure validation drop rates, and
compare real enhanced coverage against the PR26 baseline.

## Non-Goals

- no real model calls;
- no OpenRouter calls;
- no production prompt changes;
- no `$lolla` runtime changes;
- no `SKILL.md` changes;
- no `archive_run.py` integration;
- no semantic coverage archive integration;
- no graph DB;
- no embeddings;
- no chunking;
- no `conversation_understanding_ir.v0`;
- no new user-values extractor;
- no LLM judge;
- no answer-quality scoring;
- no provider-boundary policy change.
