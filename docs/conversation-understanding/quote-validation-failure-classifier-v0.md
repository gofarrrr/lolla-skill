# Quote Validation Failure Classifier v0

PR23 classifies quote-validation failures before changing quote validation,
extraction prompts, or retry behavior.

The classifier is local-only. It reads raw archive artifacts internally because
debugging quote validation requires comparing failed passages with the archived
conversation text. Its outputs remain custody-bounded: no raw transcript text,
no raw fabricated passage text, no memo text, no revised-answer text, no raw
model messages, no provider reasoning details, and no absolute local archive
paths.

The classifier does not call models and does not use an LLM judge. It does not
change runtime quote validation. It does not loosen matcher tolerance. It does
not repair prompts.

For each affected archive record, the diagnostic reports hashes, lengths,
classification counts, nearest turn indexes/speakers, conservative token
overlap, retry metadata, and a per-record repair hint.

Classification buckets:

- `accepted_by_current_matcher`: current `find_substring_tolerant(...)` accepts
  the passage now, suggesting a stale or legacy failure.
- `linebreak_normalized_match`: linebreak-only normalization finds the passage.
- `unicode_punctuation_normalized_match`: smart quote, dash, or ellipsis
  normalization finds the passage.
- `whitespace_normalized_match`: broader whitespace collapse finds the passage.
- `high_token_overlap_near_match`: conservative token overlap is high, but this
  is diagnostic only and not evidence acceptance.
- `true_paraphrase_or_no_match`: no deterministic near match was found.
- `empty_or_invalid_passage`: the stored failed passage is missing or empty.

The aggregate report decides whether the next repair should target matcher
tolerance, retry prompting, extraction prompting, legacy-only no-op plus a new
smoke, or a split repair plan. That recommendation is data-derived from the
classified failures, not inherited automatically from PR22.

Non-goals:

- no runtime behavior change,
- no quote-validator behavior change,
- no prompt change,
- no model calls or LLM judge,
- no graph DB or embeddings,
- no `conversation_understanding_ir.v0`,
- no answer-quality scoring,
- no automatic human-review labels,
- no Observatory or control-plane work.
