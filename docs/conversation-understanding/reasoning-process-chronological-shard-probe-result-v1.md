# Chronological shard probe result v1

Status: chronology improved recall; representative family gate failed  
Date: 2026-07-11

## What we tested

The failed global readers were replaced provider-free with three small
chronological shards per family. All 20 protected full-reader targets fit in one
focal shard, packets remained below 6.1 KB, and role-valid source custody passed.

We did not run a full nineteen-call case. We first called the smallest Case-05
evidence shard, then a frozen four-call representative batch covering:

- the same evidence failure on Case 01;
- Case-05 first-versus-final position;
- Case-05 late uncertainty;
- Case-05 early challenge and revision.

## Result

The smallest evidence probe recovered its exact target. In the representative
batch, Case-01 evidence and Case-05 challenge also recovered their complete
protected relationships in one record.

Position and uncertainty were only partial. Position cited good starting,
current, and qualification evidence but its prose described only the starting
position. Uncertainty recovered both protected source spans but split the
unresolved rule and deadline pressure across separate records. An additional
challenge record assigned valid source aliases to the wrong semantic roles.

This is the useful distinction:

- chronology improved which details the model noticed;
- strict schemas and aliases kept source custody reliable;
- one generic interpretation string still allowed the relationship itself to
  be incomplete or mislabeled.

## Accounting

- smallest probe: 1 request, 2 admitted records, $0.00101425;
- representative batch: 4 requests, 7 admitted records, $0.003996;
- representative protected targets: 2 supported, 2 partial;
- deterministic quarantines: 0;
- source-reviewed semantic-role mismatches: 2 records;
- automatic or semantic retries, fallbacks, evaluator, embedding, graph,
  pipeline, and runtime calls: zero.

## Decision

The full nineteen-call case is not authorized. Sharding alone is not the final
architecture.

The next provider-free change should make relationship meaning as explicit as
source roles:

- position: separate starting-position, current-position, and qualification
  interpretations instead of one generic sentence;
- uncertainty: separate unresolved-matter and preservation/reopen
  interpretations so the relation cannot disappear across records;
- challenge: review whether role-specific interpretations can expose reversed
  prior-frame/challenge assignments without adding brittle deterministic
  temporal gating;
- evidence: retain the current claim/boundary structure as the promising
  reference, but do not declare transfer from two target probes.

This remains a probabilistic semantic job. Deterministic code may validate
visible roles, source regions, identities, budgets, and custody; it may not
decide what the conversation means.

## Evidence

- provider-free design and practice check:
  `docs/conversation-understanding/reasoning-process-chronological-shards-design-v1.md`;
- smallest probe:
  `research/reasoning-process-chronological-shard-probe-2026-07-11/`;
- representative contract and calls:
  `research/reasoning-process-chronological-shard-family-batch-2026-07-11/` and
  `research/reasoning-process-chronological-shard-family-batch-run-2026-07-11/`.
