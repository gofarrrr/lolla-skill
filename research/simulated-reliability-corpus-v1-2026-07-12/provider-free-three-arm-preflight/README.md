# Provider-free three-arm preflight

Status: pass; no provider calls; not runtime authorization  
Date: 2026-07-12

This preflight exercises the V1 experiment packager at both boundaries.

## Pressure sentinel

The `amb1-case01-product-scope` development fixture was packaged with two
controlled unresolved mechanisms. Deterministic routing produced six direct
candidates. One-hop graph custody found 47 eligible edges and 24 unique graph
targets, admitted three structurally diverse graph candidates, and preserved
the remaining 21 targets in the reserve. All three comparison arms require a
fresh call when the runtime contract is eventually authorized.

## Quiet sentinel

The `quiet-local-control` package used an empty controlled-mechanism result.
The transcript-only arm remains callable. Direct and graph pressure both end in
an explicit deterministic stand-down with `provider_attempted: false`; the
packager does not invent a graph call or public friction to fill the experiment.

## Local gates exercised

- canonical mechanism and model identity;
- complete direct provenance;
- deterministic mechanism-round-robin replay;
- direct overflow preservation without semantic rejection;
- complete one-hop graph edge custody;
- antagonist, tension, and ally structural slots;
- graph overflow and direct-duplicate preservation;
- identical direct candidates in direct and graph-expanded arms;
- graph additions capped at three and total active pressure capped at thirteen;
- accountable apply/reject/park response shape;
- exact source-turn custody and complete disposition coverage;
- empty-portfolio stand-down; and
- zero provider transport in the builder.

The focused implementation suite passes 20 tests. These fixtures prove local
contract behavior only. They do not prove provider compatibility, semantic
mechanism accuracy, graph usefulness, or transfer reliability.

