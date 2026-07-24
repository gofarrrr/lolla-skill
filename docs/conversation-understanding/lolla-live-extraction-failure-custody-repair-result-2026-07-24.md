# Live extraction failure-custody repair result

Date: 2026-07-24

Status: implemented and verified locally; not yet repository-published

Scope: ordinary `$lolla` source capture and the terminal boundary between
conversation extraction and graph pressure

Graph, planner, prompts, provider route, and normal answer behavior changed:
**no**

## Plain-language result

The failed Marcus run did not reach the mental-model graph. OpenRouter first
could not be reached, then a same-run manual retry reached the provider but
ended with `finish_reason: error` and only a partial response. Lolla treated
that partial response as if the model had completed and merely forgotten two
meaning fields. The second invocation also replaced the first invocation's
call sidecar.

The repaired behavior is:

1. the conversation is supplied to a private runtime helper instead of being
   shown as an `Added ...conversation.txt` editor patch;
2. a provider interruption is reported as a provider interruption before any
   semantic field check;
3. every attempted extraction call remains in one append-preserving sidecar;
4. every extraction attempt receives one terminal seal;
5. a sealed run cannot call the provider again;
6. a failed attempt records `extraction_failed`, appends one exact user
   receipt, and creates a minimal private archive;
7. the graph and later reasoning stages do not start after failed extraction.

This repairs process truthfulness. It does not prove that extraction meaning is
correct, that the graph is useful, or that the revised answer is better.

## What changed

### Private source capture

`scripts/skill/capture_conversation.py` accepts the formatted source only on
standard input. It validates the existing transcript grammar, writes the
run-scoped source with owner-only permissions, records the source hash and
`conversation_captured` event, and prints only counts. It refuses to replace
different source text inside the same run.

The skill contract now explicitly forbids Apply Patch, file editors, and
repository-writing tools for conversation capture. The host may still show a
generic runtime tool action; it no longer needs to show the transcript as a
source-code file addition.

### Provider failure before semantic validation

The provider boundary already recognized `finish_reason: error` as
`provider_finish_error`, but extraction ignored that status and continued to
required-field validation. Extraction now inspects the terminal boundary-call
record first. A non-`ok` provider status stops admission without publishing the
partial provider body as `raw_extraction`.

Current OpenRouter guidance documents both top-level error envelopes and
choice-level provider errors alongside partial non-streaming output. The
boundary now preserves the served provider name, error source, canonical error
type, public error code, provider code, `Retry-After`, and a SHA-256 digest of
the error message. It does not persist the raw provider error message in these
diagnostic fields. Source checked 2026-07-24:
[OpenRouter errors and debugging](https://openrouter.ai/docs/api_reference/errors-and-debugging).

### Attempt history and terminal seal

Extraction call persistence now merges earlier call records with the current
process instead of replacing the sidecar. Budget reservation IDs are the
primary deterministic identity; canonical record hashes provide a fallback for
older or test records.

`scripts/skill/finalize_extraction_attempt.py` writes
`lolla.extraction_terminal.v1`. It records whether extraction completed,
declined, or failed; confirms that the graph did not start; compares call
sidecar count with budget-ledger attempt count; records exact and conservative
cost custody; and sets `same_run_retry_allowed: false`.

Failed attempts are copied to:

```text
$LOLLA_ARCHIVE_DIR/_failed-extractions/<run_id>/
```

or the equivalent directory under the default local archive root. This is not
a normal completed case archive. Its manifest explicitly disclaims graph
output, reconsideration, answer quality, and usefulness evidence.

## Provider incident during repair testing

Repository-development provider authorization remained zero calls and
USD 0.00. While proving the new retry guard with a red test, the pre-repair
code made one unintended HTTP request to OpenRouter using an intentionally
invalid test key. OpenRouter returned HTTP 401. No authenticated model
generation or provider output was observed. The provider-reported cost field
was USD 0.00; the local safety ledger conservatively reserved and accounted
USD 0.0085688 because an exact charge was unavailable.

That request was a test-design error, not an authorized experiment. No retry,
replacement, or further provider request was made. The implemented guard now
stops the same test before boundary-client construction.

## Evidence

Provider-free targeted checks currently pass:

- quiet capture and immutable same-run source;
- provider failure before missing-field validation;
- cross-process extraction call preservation;
- safe choice-level provider diagnostics;
- terminal seal, one failure event, one receipt, and minimal failure archive;
- sealed-run rejection before provider loading;
- existing successful extraction, missing-field, and quote-repair behavior;
- live skill-contract checks.

The final provider-free checkpoints are:

- 135 focused and directly adjacent tests passed;
- 5,206 repository tests passed;
- all 93 subtests passed;
- one pre-existing `datetime.utcnow()` deprecation warning remained;
- the skill-authoring validator, self-contained-skill validator, Constitution
  Stage 0 register validator, repository-local-authority validator, public
  handoff validator, Python compilation, Bash syntax, JSON parsing, and
  `git diff --check` passed.

No provider call was made by final verification.

## User-visible behavior

On a provider interruption, the exact default receipt is:

> Lolla stopped before the graph because the model provider interrupted the
> conversation read. No automatic retry was made. The source and failure
> evidence were preserved privately. Start a new `$lolla` run when you want to
> try again.

The next attempt must start with a new `$lolla` invocation. Re-running the
Step 2 helper under the old run ID is intentionally blocked.

## Boundaries and nonclaims

- This repair does not change the 222 mental-model sources or 1,358 relations.
- It does not change one-hop traversal, active/reserve survival, lane
  selection, prompts, model choice, or provider routing.
- It does not add automatic retry or fallback.
- It does not make a partial extraction semantically trustworthy.
- It does not establish graph causation, answer improvement, or user
  usefulness.
- It does not make the private temp artifact invisible to the operating system
  or operator; it removes the misleading user-facing editor-diff workflow.
