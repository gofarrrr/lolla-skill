# Observatory Agent Memory Markdown Download v0

Status: implemented explicit export slice.

Date: 2026-07-07

Decision gate: `proceed_to_presentation_visibility_revision`

## Purpose

Observatory needs one simple way to give the user a complete, portable run
memory for a future agent.

The UX is intentionally small:

```text
Download MD for your agent
```

The button is visible in the main workspace action row because this is a core
user action, not something hidden behind technical receipts. Receipts repeats
the action with custody context so the user can understand what the export
contains and what it does not claim.

## User Flow

1. Open a selected run in Observatory.
2. Click `Download MD for your agent` from the main workspace.
3. Optionally open Receipts to inspect custody, missingness, and non-claims.
4. Observatory builds a private Markdown export from the completed run archive.
5. The browser downloads the generated `.md` file.

The route is:

```text
/api/case/<id>/conversation-memory.md
```

The Receipts button requests:

```text
/api/case/<id>/conversation-memory.md?include_raw_conversation=1
```

That query makes the action an explicit private local export. It is not the default product UI and it is not intended as a public-safe artifact.

## What The Markdown Includes

The generated Markdown is self-explaining. It includes:

- what the file is;
- what it is not;
- how to use it;
- how it was produced;
- source artifact map;
- interpretation legend;
- run summary;
- privacy and non-claims;
- conversation interpretation;
- decision situation;
- what changed;
- what still holds;
- what to revisit;
- selected lenses;
- deterministic selection trace;
- selected models;
- suppressed or unadjudicated signals;
- future useful lenses;
- open questions;
- artifact custody;
- run health and readiness;
- agent instructions for future use;
- update rules;
- source excerpts.

When the private export button is used, the Markdown includes a clearly named
`Full 1:1 Conversation Transcript` section if the archive contains
`conversation.txt`. That transcript is the primary source object a future agent
needs in a new session. Private/operator artifacts are inventoried but their
bodies are not copied into the Markdown.

## What This Is Not

This is not:

- the default product UI;
- a replacement for the archive;
- a proof that the advice is correct;
- answer correctness validation;
- advice correctness validation;
- human validation;
- product proof;
- action authorization.

## Implementation

The slice ports the offline conversation memory bundle capability into the main
repo:

- `engine/system_b/conversation_memory_packet.py`;
- `engine/system_b/conversation_memory_renderer.py`;
- `scripts/evals/build_conversation_memory_bundle.py`;
- `tests/test_conversation_memory_bundle.py`.

Observatory adds:

- a main workspace download button;
- a Receipts button;
- a Markdown download route;
- safe temp output under the OS temp directory;
- `Content-Disposition: attachment`;
- no archive mutation.

## Boundary

This slice:

- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create a new run;
- does not wire skill runtime behavior;
- does not mutate archives;
- does not edit `observatory/build`;
- does not touch `SKILL.md`;
- does not touch `scripts/skill/*`;
- does not touch `scripts/archive_run.py`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize automatic action;
- does not treat graph edges as proof;
- does not treat embedding similarity as validated relation semantics.

## Next Gate

Recommended next gate:

`proceed_to_presentation_visibility_revision`

Reason: agent-memory export is now a concrete download action. The next work
should refine what Observatory shows by default, what it summarizes, and what
it keeps behind expansion or technical inspection.
