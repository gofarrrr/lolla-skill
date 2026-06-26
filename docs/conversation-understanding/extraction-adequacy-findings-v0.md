# Extraction Adequacy Findings v0

This note summarizes a local PR22 drilldown over the PR21 extraction-adequacy
corpus export. It is a snapshot of one local archive corpus, not a universal
benchmark for Lolla or for the extraction chain.

The analyzer used only the PR21 JSONL corpus records and aggregate manifest. It
did not read raw transcript text, memo text, revised answers, model messages,
provider reasoning details, or control-plane argument values.

## Local Corpus Snapshot

Input corpus:

- `record_count`: 63
- `valid_record_count`: 63
- `invalid_record_count`: 0
- `adequacy_status_counts`: `good`: 51, `warn`: 11, `critical`: 1
- `capture_adequacy_status_counts`: `unknown`: 62, `good`: 1
- `report_available_count`: 0
- `report_missing_count`: 63
- `report_built_in_memory_count`: 63
- `invalid_turn_ref_total`: 6
- `missing_turn_ref_total`: 0
- `speaker_mismatch_total`: 0
- `quote_fabrication_total`: 22
- `omitted_turn_total`: 0
- `conversation_context_available_count`: 62
- `conversation_ir_available_count`: 62
- `specialist_opportunity_counts`: `live_constraints_extraction`: 63,
  `stance_extraction`: 63, `dropped_threads_extraction`: 49

The corpus mostly predates capture-adequacy and extraction-adequacy archive
artifacts. `report_built_in_memory_count: 63` is therefore expected: PR21 had to
reconstruct the deterministic reports in memory from older archived artifacts
instead of reading checked-in `extraction_adequacy_report.json` files from each
run folder. That is a legacy metadata limit, not evidence that archives were
mutated.

## Drilldown Findings

The single critical record was:

- `mid-level-consultant-report-1/20260428T110004Z`

Its compact PR21 corpus record showed:

- `conversation_context_available`: false
- `conversation_ir_available`: false
- `invalid_turn_ref_count`: 6
- `quote_fabrication_count`: 1

This critical case is best read as a historical/archive-completeness problem
plus invalid turn references, not as proof that a new semantic extraction layer
is needed.

The 11 warning records were:

- `agency-owner-grant-marcus-1/20260525T204111Z`
- `consultant-report-senior-partner/20260623T130424Z_127d92`
- `grant-equity-partnership-status/20260422T100308Z`
- `grant-head-engineering-equity-1/20260527T144148Z`
- `grant-head-engineering-equity-2/20260528T091614Z`
- `grant-head-engineering-equity-4/20260609T151134Z`
- `mid-level-consultant-report/20260424T124651Z`
- `prioritize-control-plane-contract/20260625T125625Z_aae54e`
- `solo-founder-deciding-pivot/20260510T203614Z`
- `solo-founder-deciding-pivot/20260510T212232Z`
- `third-year-phd-student/20260425T122400Z`

All 11 warning records had `quote_fabrication` as their status cause. None of
the warning records had invalid turn refs, missing turn refs, speaker mismatch,
omitted turns, missing ConversationContext, or missing ConversationIR.

Quote fabrication was spread across 12 non-good records when the critical record
is included. Two `solo-founder-deciding-pivot` records each had a count of 6;
the remaining affected records had a count of 1 each. So the issue is not a
single isolated record, but it is also not uniformly distributed.

## Legacy Metadata Limits

The local corpus is heavily legacy-shaped:

- 63 of 63 records had no archived `extraction_adequacy_report.json`.
- 63 of 63 reports were built in memory by the read-only exporter.
- 62 of 63 records had unknown capture-adequacy status and unknown capture
  strategy in the compact corpus record.

These limits mean the findings should guide the next narrow diagnostic slice,
not broad claims about extraction quality. In particular, `good` here means the
deterministic adequacy envelope did not find the measured failure modes. It does
not prove semantic understanding, answer quality, or domain safety.

## Specialist Opportunities

The PR21 manifest reported diagnostic specialist opportunities:

- `live_constraints_extraction`: 63
- `stance_extraction`: 63
- `dropped_threads_extraction`: 49

These are coverage signals. They show where specialist extractors might improve
grounding or assistant-recommendation coverage in a later experiment. They do
not prove that a specialist should run in production, and they are not the
strongest immediate explanation of the 11 warning records.

The broadest specialist-shaped opportunity is
`live_constraints_span_grounding`, because `live_constraints_extraction` appears
across all 63 records. It should remain a later candidate unless quote
validation repair stops being the clearer measured failure.

## Recommended Next Slice

Recommended next implementation slice:

`quote_validation_repair`

Reason: quote fabrication appears in all 11 warning records and in the single
critical record, for 22 total quote-fabrication findings. Invalid turn refs are
important but concentrated in one historical critical record where
ConversationContext and ConversationIR were unavailable. A narrow deterministic
quote-validation repair or repair-reporting slice is therefore better justified
than a broad specialist-extractor implementation.

Non-goals for the next slice remain:

- no runtime behavior change without a separate decision,
- no model calls or new extraction prompt,
- no graph DB or embeddings,
- no `conversation_understanding_ir.v0`,
- no LLM judge or answer-quality scoring,
- no automatic human-review labels,
- no Observatory or control-plane work.
