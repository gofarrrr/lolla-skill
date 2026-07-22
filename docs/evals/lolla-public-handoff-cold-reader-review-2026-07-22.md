# Public handoff cold-reader review — 2026-07-22

Status: provider-free repository handoff review complete

Evidence class: maintainer review plus three repository-only AI cold reads

Independent human evidence: no

Provider calls: 0

Provider cost: $0.00

Publication: [PR #380](https://github.com/gofarrrr/lolla-skill/pull/380)

## Question

Can a new human or AI coder start from the GitHub repository and correctly
distinguish what Lolla is, what is live, what remains bounded or parked, what
research is retired, how the graph actually works, and what may happen next?

## Method

The review began from `AGENTS.md` and the then-current mandatory read path. The
maintainer traced public claims into the live skill contract, graph reader and
planner code, setup behavior, Atlas V2 custody, current roadmap, frozen R4
closeout, and GitHub merge state. Three cold readers inspected, separately:

1. public-document orientation and stale-current language;
2. graph caller, planner, and fallback boundaries;
3. minimal human/AI handoff sufficiency and live-skill contradictions.

The review did not inspect private archives, run a provider, generate new
semantic evidence, or evaluate usefulness. The machine-readable expected
answers are in
[`lolla-public-handoff-cold-reader-answers-v2.json`](lolla-public-handoff-cold-reader-answers-v2.json).

## What the review found

The repository contained the necessary evidence, but its entry path was too
wide and several current-looking documents blurred different checkpoints.
Material defects were:

- thirteen mandatory document groups before task routing;
- root `PROGRESS.md` and `TODOS.md` appearing to be active queues;
- a roadmap asking whether to publish work already merged;
- Atlas V1 sometimes presented before active custody V2;
- Atlas interface evidence and the wider Teacher hypothesis conflated;
- “published” used for repository merge, runtime graph projection, and product
  availability without qualification;
- a “one planner owner” claim that hid the frozen compatibility serializer and
  degraded raw-payload fallback;
- a live-skill claim that the host was a pure orchestrator even though Step 6
  makes the host the reconsidering reasoner and disposition owner;
- four different lane jobs described as independent;
- dated Claude model calibration phrased as a current model recommendation;
- optional Claude Code Agent-tool behavior described as generally compatible
  with Codex;
- a project-local credential path that setup could see but later fresh shells
  could not rediscover;
- a fixed latency promise and an unsupported “full accuracy” embedding claim;
- a table-wide price receipt date advanced by a check of only one active route;
- no checked-in contributor dependency file or hosted cold-start gate.

## Corrections made

The handoff now has one five-document universal route and task-specific lanes
for the live skill, graph substrate, Atlas/Teacher, constitutional custody,
Decision Work/Observatory, and retired readers. Current documents classify
historical next-step language explicitly; root snapshots carry historical
banners; Atlas V2 is current custody and V1 is frozen evidence; Atlas and
Teacher are separate parked claims; and repository-published, graph-published,
deployed, rights-cleared, and useful are no longer synonyms.

The graph description now matches reachable code: one declared policy wrapper
and snapshot, a frozen executable serializer used for compatibility, and an
explicit raw-payload fallback. It still traverses exactly one authored outgoing
hop from direct-active seeds and still makes no relevance or causal claim. No
graph behavior or portfolio output changed.

The skill now names the host as reasoner/orchestrator, calls the lanes distinct
pressure products, scopes its dated model calibration honestly, marks optional
Step 7 as Claude Code-specific, removes unsupported project-local credential
discovery, replaces fixed latency and accuracy promises, and supplies the
missing normal-flow bridge before Observatory. These are contract truthfulness
repairs; no provider route or graph policy changed.

The generated final receipt now also states that reconsideration stayed in the
current conversation context and was not an external check. This closes the
old gap between the documented same-context limitation and the user-visible
process receipt.

The frozen 2026-07-13 active-route pricing date remains intact, but new usage
summaries now label its scope and separately carry the 2026-05-25 whole-table
verification date. Optional Step 7 Anthropic rates remain historical and are
not a current budgeting contract.

`requirements-dev.txt` and a provider-free GitHub Actions handoff gate make the
documented fresh-clone validation reproducible. The existing public validator
now reads the live skill and setup contract and checks sixteen cold-reader
questions instead of checking only the six root entrypoints and ten orientation
questions.

## Result

The repository is now a materially better self-contained handoff for further
development. It answers the sixteen questions in the V2 packet from current
entrypoints and live contracts, with source links and zero provider calls.

This is not independent human acceptance. It does not prove that an arbitrary
reader will never be confused, that the live skill is useful, that the Atlas is
publishable, or that a current provider route is safe and economical. Stage 1
Decision Trail truthfulness remains merely eligible; it is not authorized or
started by this review.
