# Mental Model Teacher Observatory Ownership and Portability Boundary v0

Status: source-owner verification slice
Date: 2026-07-06
Decision gate: `keep_teacher_learn_server_rendered_until_source_owner_verified`

## Purpose

This slice answers a narrow architecture question before more Teacher UX work:

```text
Does Teacher Learn belong in a separate app source path, or in the portable
Observatory surface that ships with the skill runtime?
```

The finding is conservative: do not port Teacher Learn into a compiled
Observatory app by default. The current Observatory owner is the portable local
Python server, while the compiled frontend bundle is an optional app-era
artifact whose source is not present in this repository.

This does not run Lolla.
It does not invoke the Lolla skill.
It does not call providers or model APIs.
It does not create new runs, mutate archives, judge answer quality, authorize
action, or wire Lolla runtime behavior.

## Evidence

The current local repository contains:

- `observatory/serve_result.py`
- `observatory/render_schema.json`
- `observatory/build/index.html`
- `observatory/build/assets/*.js`
- `observatory/build/assets/*.css`

It does not contain a local frontend source app:

- no root `package.json`;
- no `observatory/package.json`;
- no `observatory/svelte-app/`;
- no local `vite.config.*`;
- no local `svelte.config.*`.

`observatory/serve_result.py` records that the bundle under
`observatory/build/` is optional app-era distribution material whose former
source workspace is retired and is not a dependency. That same header says the
repository-owned surfaces are rendered from Python and stay portable when the
bundle is absent.

`docs/how-it-works/live-flow.md` describes the current launch path as:

```text
finalize_and_archive.sh -> scripts/skill/launch_observatory.py -> observatory/serve_result.py
```

The same doc names the design intent: a stdlib Python server plus a prebuilt
frontend bundle, with server-rendered audit panels that work without a Node
toolchain.

## Ownership Map

| Asset | Current role | Ownership decision |
| --- | --- | --- |
| `observatory/serve_result.py` | Portable local Observatory server, read-only APIs, `/audit/*`, `/usage`, and `/teacher-learning` | Current owner for Teacher Learn until a source app owner is verified |
| `observatory/build/*` | Compiled frontend bundle for the existing `/` case surface | Optional compiled artifact; do not hand-edit; not the local source of truth |
| Legacy bundle authoring source | Not present in the active project | Do not depend on another workspace; require repository-local source before replacement |
| `scripts/skill/launch_observatory.py` | Skill launcher for the local post-run viewer | Runtime launcher boundary; not changed by Teacher UX planning |
| `docs/how-it-works/live-flow.md` | Current live-flow doctrine | Evidence that portability is an intentional design constraint |
| `docs/product/mental-model-teacher-observatory-*.md` | Teacher Observatory product planning trail | Product design owner for the learning surface, not runtime authorization |

## Product Boundary

Observatory should remain the single post-run shell.

Teacher Learn should not become:

- a second app beside Observatory;
- a duplicate of raw Teacher notes;
- a duplicate of telemetry panels;
- a second advice engine;
- a source of product proof;
- a source of answer or advice correctness labels;
- an action authorization surface.

Teacher Learn should become a first-class learning mode inside Observatory:

```text
case context -> reasoning move -> mental models -> relations -> practice rep
```

Telemetry should remain a separate explanation mode:

```text
run custody -> extraction -> routing -> sidecars -> traces -> health
```

These two modes may read from the same artifacts, but they must not present the
same information with two competing meanings.

## First-Class and Second-Class Data

In the Teacher Learn surface, first-class information is:

- the case anchor;
- the reasoning move;
- canonical mental model identity;
- relation story;
- practice rep;
- do-not-overlearn boundary;
- product-safe model detail;
- product-safe relation detail;
- visible missingness and non-claims.

Secondary information is:

- source refs;
- source custody;
- packet status;
- review status;
- artifact availability;
- links into telemetry.

Internal-only information is:

- raw `audit_summary`;
- raw `usage_summary`;
- raw artifact paths;
- raw routing internals;
- raw embedding similarity;
- raw graph ranking or affinity;
- Product Delta and eval internals.

This means Teacher Learn can sit inside Observatory without becoming the
Observatory telemetry UI.

## Source-Port Policy

The previous candidate gate, `proceed_to_compiled_observatory_learn_source_port`,
is now treated as a question, not an instruction.

Before any compiled frontend port, a future PR must establish:

1. repository-local frontend source and a reproducible build contract;
2. whether that source is intended to own the long-term Observatory UI;
3. whether the portable skill should keep server-rendered product surfaces
   even if the compiled bundle exists;
4. how source builds are generated into `observatory/build/` without hand-editing
   compiled assets;
5. how to prevent Teacher Learn from diverging between Python-rendered and
   compiled app surfaces.

Until that verification exists, continue treating the server-rendered
`/teacher-learning` route as the authoritative local implementation path for
Teacher Learn.

## What Changes Now

This PR does not change runtime behavior.

It changes the product plan:

- Teacher Learn remains inside Observatory.
- The portable Python Observatory server remains the current owner.
- The compiled bundle remains optional and non-authoritative for new Teacher
  work until repository-local source and ownership are approved.
- The next UX work should improve information flow inside the current portable
  Observatory path rather than start by porting to a missing source tree.

## Stop Line

This PR stops before:

- compiled SPA source work;
- bundle rebuilds;
- runtime integration;
- launcher changes;
- live Lolla runs;
- provider or model calls;
- archive mutation;
- product proof claims;
- human validation claims;
- answer or advice correctness scoring;
- action authorization.

Recommended next gate:

```text
proceed_to_teacher_learn_information_architecture_revision
```
