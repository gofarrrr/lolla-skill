# Modern Extraction Baseline v0

This note records a local modern current-main baseline after the PR23
quote-validation classifier. It is a small findings note, not a runtime change
or universal benchmark.

The purpose was narrow: check whether the historical quote-fabrication warnings
from the legacy-heavy corpus still reproduce on modern archives created by the
current artifact chain.

No runtime behavior, quote validation, extraction prompts, retry prompts,
provider-boundary policy, `SKILL.md`, graph memory, embeddings,
`conversation_understanding_ir.v0`, or LLM judging changed for this baseline.

## Runs Included

The baseline includes four modern clean runs:

- `launch-limited-beta-workflow / 20260626T125112Z_b861fd`
- `initiate-pre-sale-coffee / 20260626T131939Z_368960`
- `implement-price-increase-three / 20260626T132915Z_49172d`
- `five-person-saas-team / 20260626T133147Z_99712f`

These are local archive runs. They are useful as current-main evidence, but
they are not a broad benchmark of every conversation shape Lolla may see.

## Summary

| case | run_id | quote fabricated | quote total / verified | extraction adequacy | capture adequacy | turn-ref issues invalid / missing / speaker | run health | degradation cause |
|---|---|---:|---:|---|---|---:|---|---|
| `launch-limited-beta-workflow` | `20260626T125112Z_b861fd` | 0 | 5 / 5 | good | good / full | 0 / 0 / 0 | partial | `vendor_boundary_reasoning_leak` |
| `initiate-pre-sale-coffee` | `20260626T131939Z_368960` | 0 | 5 / 5 | good | good / full | 0 / 0 / 0 | partial | `vendor_boundary_reasoning_leak` |
| `implement-price-increase-three` | `20260626T132915Z_49172d` | 0 | 5 / 5 | good | good / full | 0 / 0 / 0 | partial | `vendor_boundary_reasoning_leak` |
| `five-person-saas-team` | `20260626T133147Z_99712f` | 0 | 3 / 3 | good | good / full | 0 / 0 / 0 | partial | `vendor_boundary_reasoning_leak` |

The important separation is that the runs are partial because of contained
provider-boundary warnings, not because of extraction adequacy or quote
validation.

## Corpus Delta

After adding the four modern baseline samples to the local archive corpus, the
PR21/PR22-style corpus export reported:

- `record_count`: 67
- `valid_record_count`: 67
- `invalid_record_count`: 0
- `adequacy_status_counts`: `good`: 55, `warn`: 11, `critical`: 1
- `capture_adequacy_status_counts`: `good`: 5, `unknown`: 62
- `report_available_count`: 4
- `report_built_in_memory_count`: 63
- `quote_fabrication_total`: 22
- `invalid_turn_ref_total`: 6
- `missing_turn_ref_total`: 0
- `speaker_mismatch_total`: 0
- `clean_baseline_sample`: 4

The historical quote-fabrication total did not increase. The new modern records
all landed as `clean_baseline_sample`.

## Quote-Validation Conclusion

Modern current-main evidence does not justify quote-validation runtime repair
right now.

The PR22 historical corpus signal was worth investigating:

- 11 warning records had quote-validation causes.
- 12 non-good historical records had quote-fabrication findings when the
  critical record is included.
- The total historical quote-fabrication count was 22.

PR23 then classified those historical failures and found that many were stale
relative to the current matcher. The modern baseline adds the current-runtime
check: four modern runs produced verifiable reasoning passages with zero quote
fabrication.

Therefore, do not do the following unless a fresh modern run reproduces a
specific failure class:

- matcher tolerance repair,
- retry prompt repair,
- extraction prompt repair,
- quote-validation loosening.

This is not a claim that quote validation is solved forever. It is a claim that
the current evidence does not support changing the runtime quote-validation
contract.

## Decision Rule

If a future modern run produces `quote_fabrication`, classify the fresh failure
with the PR23 tooling before changing runtime behavior.

Use the classification to choose the narrowest next slice:

- If the fresh failure is formatting-only, consider a narrow deterministic
  matcher fix for that exact formatting class.
- If the fresh failure is true paraphrase or no deterministic match, consider
  retry prompt or extraction prompt repair depending on retry metadata.
- If the run is partial only because of provider-boundary warnings, keep that on
  the provider-boundary policy track.
- If current matcher replay accepts the fresh failure, investigate artifact
  generation versus replay consistency before changing the matcher.

## Boundary

This baseline clears the current quote-validation repair suspicion. It does not
prove full conversation understanding.

It does show that, on these modern samples, the measured mechanical extraction
layer is healthy:

- quote validation is clean,
- capture adequacy is good/full,
- turn references are clean,
- extraction adequacy is good,
- reasoning-trace custody indexes the modern artifacts,
- agent and evaluation artifacts are present.

It does not prove that extraction preserves the deeper semantic work of the
conversation, such as changed constraints, load-bearing user values, dropped
threads, assistant overconfidence, counter-pressure, or why the revised answer
changed. That remains future semantic extraction review work.

Provider-boundary degradation is also separate. The modern runs remained
agent-degraded because of `vendor_boundary_reasoning_leak`, but that is not
evidence of quote-validation or extraction failure.

## Non-Goals

- no runtime behavior change,
- no quote-validator behavior change,
- no prompt change,
- no provider-boundary policy change,
- no graph DB or embeddings,
- no chunking work,
- no `conversation_understanding_ir.v0`,
- no LLM judge,
- no answer-quality scoring,
- no automatic human-review labels,
- no `SKILL.md` change.
