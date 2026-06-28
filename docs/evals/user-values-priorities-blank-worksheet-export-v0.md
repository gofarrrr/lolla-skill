# User Values / Priorities Blank Worksheet Export v0

Status: narrow deterministic helper
Date: 2026-06-28
Slice: PR52

PR52 adds a deterministic blank worksheet artifact for human-owned
user-values/priorities review.

This slice does not run `$lolla`, call models, read archives, inspect raw
conversation content, mutate archives, change runtime behavior, change prompts,
change `SKILL.md`, implement extraction, populate labels automatically, score
answer quality, add a judge, change risk-mode behavior, change
`safe_for_agent_use`, or create high-stakes archive evidence.

## Tooling

The helper lives in:

- [user_values_priorities_worksheet.py](../../engine/system_b/user_values_priorities_worksheet.py)
- [build_user_values_priorities_worksheet.py](../../scripts/build_user_values_priorities_worksheet.py)
- [test_user_values_priorities_worksheet.py](../../tests/test_user_values_priorities_worksheet.py)

The CLI creates a blank worksheet JSON file:

```bash
python3 scripts/build_user_values_priorities_worksheet.py \
  --case-id example-case \
  --run-id example-run \
  --archive-relpath example-case/example-run \
  --out /tmp/lolla_user_values_priorities_worksheet.json
```

`--out` is required. `--case-id`, `--run-id`, and `--archive-relpath` are
optional compact metadata fields. The command does not accept a run directory,
does not read archive files, and does not infer values from any artifact.

## Why This Exists

PR34 defined the missing `user_values_or_priorities_signal` surface. PR49 made
that surface reviewable as a human worksheet plan. PR50 tested the worksheet
through paraphrase-only fixtures. PR51 reviewed those fixtures and found all
six clear and useful enough for human review.

PR52 is the next small step: create a consistent local blank artifact shape so
reviewers can fill worksheets later. The helper makes structure boring and
repeatable without pretending to understand values.

## Output Contract

The blank worksheet schema is:

```text
lolla.user_values_priorities_worksheet.v0
```

The generated JSON contains:

- optional `case_id`;
- optional `run_id`;
- optional `archive_relpath`;
- `review_scope: human_review_only`;
- custody flags proving the artifact is local-only, blank, human-owned, and not
  auto-extracted;
- `source_artifacts_reviewed` flags initialized to `false`;
- empty `values_items`;
- empty `conflicts`;
- empty answer-treatment lists;
- `reviewer_summary` fields initialized to `unfilled`;
- empty `reviewer_notes`.

The blank artifact is intentionally not a human-review label and not a runtime
artifact. It is a local review worksheet shell.

## Input And Validation Rules

The builder accepts only compact metadata:

- `case_id` and `run_id` must be compact identifiers, not paths;
- `archive_relpath` must be a relative forward-slash path if supplied;
- absolute paths, home-directory shorthand, parent-directory traversal, and
  private/raw-content marker strings are rejected;
- generated worksheets keep all raw/private inclusion flags false;
- `values_items` and `conflicts` must remain empty in a blank worksheet;
- all answer-treatment arrays must remain empty;
- all reviewer-summary fields must remain `unfilled`.

The module exposes deterministic validation through:

```text
validate_blank_worksheet(payload)
```

The validator checks the schema, review scope, custody flags, empty semantic
sections, unfilled reviewer summary, and absence of local absolute paths or
private/raw-content marker strings.

## What The Helper Does Not Do

The helper does not:

- read transcripts;
- read memos;
- read revised answers;
- read review-corpus records;
- inspect archive folders;
- infer explicit values;
- infer priorities;
- map stakeholder obligations;
- populate `values_items`;
- populate conflicts;
- populate answer-treatment fields;
- populate human-review labels;
- change `safe_for_agent_use`;
- change `caller_action`;
- approve high-stakes use;
- call models;
- add a judge.

## Relationship To Human Review

The worksheet is meant for later human pilots. A reviewer can create a blank
worksheet, inspect already-approved local artifacts, and fill the worksheet by
hand. Any semantic judgment remains human-owned.

Deterministic code can make sure the blank artifact is well-formed. It cannot
decide what the user values, whether the revised answer handled those values
well, or whether an agent should rely on the answer.

## PR53 Follow-Up

Recommended follow-up:

```text
PR53 User Values / Priorities Worksheet Human Pilot v0
```

PR53 now uses the blank worksheet shape against four already-reviewed records:

```text
user-values-priorities-worksheet-human-pilot-v0.md
../../reviews/human/user-values-priorities-worksheet-pilot-v0/worksheets.json
```

It stores filled worksheets under `reviews/human/...` with paraphrase-only
reviewer notes. It does not add extraction, runtime behavior, automatic labels,
model calls, high-stakes archive evidence, or a judge.

The next recommended slice is PR54 User Values / Priorities Pilot Review / V0
Decision v0. If that review finds the human pilot confusing or too burdensome,
the right follow-up is a worksheet-shape patch before any automation.

PR54 now adds that pilot review:

```text
user-values-priorities-pilot-review-v0.md
../../reviews/human/user-values-priorities-pilot-review-v0/review.json
```

It marks the v0 worksheet lane complete for human-owned review and paused
before extraction, runtime integration, memory, automatic labels,
`safe_for_agent_use` automation, or judging.

## Review Receipt

- PR52 is a narrow deterministic helper.
- Blank worksheet only.
- No `$lolla` run.
- No model calls.
- No archive reads or archive mutation.
- No raw transcript, memo, revised-answer, model/provider, private-reasoning,
  local absolute path, secret, or credential content included in generated
  worksheets.
- No runtime behavior changed.
- No prompts changed.
- No `SKILL.md` changes.
- No extraction implemented.
- No judge or answer-quality score added.
- No automatic labels added.
- No high-stakes archive evidence created.
- PR53 pilots human-filled worksheets but does not add extraction or runtime
  behavior.
- PR54 reviews the pilot and pauses the worksheet lane at human-owned v0.
