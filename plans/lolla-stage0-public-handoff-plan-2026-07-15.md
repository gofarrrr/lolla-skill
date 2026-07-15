# Lolla Stage 0 public-handoff plan

Date: 2026-07-15

Status: completed provider-free; canonical publication is established by Git
ancestry, not inferred from this plan

Canonical parent: `fc30bd944bfb91fbff0cc09190487997f3fe3185`

## Goal

Make the canonical Stage 0 system map understandable from a fresh clone without
rewriting or deleting the research history.

## Falsifiable question

Can a new technical reader, using only the root entrypoints, correctly identify
what Lolla does, what is live, what is bounded, what is parked or retired, what
is unproven, and what work is currently authorized?

The handoff fails if any root entrypoint presents R4 as live, Decision Work as
automatic meaning generation, Teacher as a current product, Observatory as a
semantic engine, test density as usefulness proof, or Stage 1/provider work as
already authorized.

## Allowed work

- shorten and align root documentation;
- add a current project-status page and lifecycle documentation map;
- classify repository gardening debt without deletion;
- add provider-free validation and focused tests;
- run a maintainer cold-start review and a clean-clone smoke test;
- update current indexes and the Stage 0 register for the new handoff validator;
- publish through a narrow normal-merge pull request after verification.

## Forbidden work

- provider calls or provider authorization;
- private archive inspection;
- semantic reader, prompt, schema, model, route, runtime, graph, sidecar, or
  Observatory behavior changes;
- R4/R5 or Teacher continuation;
- closing historical PRs, deleting branches, removing artifacts, or migrating
  large files without a separate custody review;
- product-usefulness or production-readiness claims.

## Deliverables

- `README.md` — concise public orientation;
- `PROJECT_STATUS.md` — canonical current status and lifecycle map;
- `HOW_IT_WORKS.md` — reachable architecture and evidence boundaries;
- `CONTRIBUTING.md` — contribution and authorization rules;
- `docs/README.md` — lifecycle-organized documentation entrypoint;
- `docs/history/README.md` — historical reading and precedence guidance;
- `docs/history/decision-work-product-delta-discoverability.md` — explicit
  compatibility registry for historical milestone discovery;
- repository gardening audit;
- maintainer cold-reader review packet and machine record;
- provider-free validator and focused tests;
- updated current handoffs, roadmap status, and machine register.

## Verification gates

1. Current root documents are bounded in size and contain the required
   lifecycle/nonclaim language.
2. Stale public claims and superseded next-step language are absent from current
   entrypoints.
3. Historical milestone discovery is preserved outside the root product story,
   and all current-entrypoint and registry local links resolve.
4. The cold-reader machine record contains exactly ten questions, zero provider
   calls, and evidence paths for every answer.
5. The Stage 0 register validates with R4 retired and provider activity zero.
6. Focused tests and the full repository suite pass.
7. Changed JSON parses, changed Python compiles, diff check and secret scan pass.
8. A clean local clone of the exact reviewed commit passes the public-handoff
   validator and focused tests.
9. The pull request contains only the authorized handoff/gardening scope and
   merges with a normal two-parent merge commit.

## Stop conditions

Stop and return to the founder if public truthfulness requires changing live
behavior, inspecting private content, deleting historical custody, making a
provider call, or deciding Stage 1's human evidence result.

## Next decision after completion

Only whether to authorize Stage 1, the provider-free checked-in-safe Decision
Trail truthfulness review. Completion of this plan does not start Stage 1.
