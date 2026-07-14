# Conversation-State Handoff v1

Status: research shadow; extraction probe closed failed; runtime dormant  
Date: 2026-07-11

## Purpose

This contract preserves the smallest case-local state needed before Lolla
abstracts reasoning patterns:

- who originated, developed, qualified, challenged, or accepted a position;
- whether the current position is proposed, conditional, accepted, rejected,
  deferred, or unresolved;
- whether a thread is open and unaddressed, substantively addressed but still
  unresolved, resolved, superseded, genuinely dropped, or unclear;
- which load-bearing constraints remain active and how strongly the source
  actually states them;
- exact source quotes and turn references for every item.

It does not replace the full conversation, the Conversation IR, the fact-free
reasoning-pattern packet, the deterministic graph, or the pressure handoff.

## Why a separate shadow contract

The current monolithic extraction asks for the AI's final recommendation. That
field cannot express a plan supplied by the user and then qualified by the
assistant. Its dropped-thread field also assumes a topic was dropped before
later code validates only quotation and shape.

The existing IR can store stance and issue events, but its generic status field
does not record whether a response was superficial, substantive, or resolving.
Adding those meanings directly to live runtime types before they are tested
would blur research with integration. The v1 handoff remains a separate packet
until automatic extraction quality is measured.

## Division of labor

An LLM or human decides the semantic content:

- ownership and contribution roles;
- position state;
- thread disposition and engagement type;
- constraint wording, state, and claim mode.

Deterministic code checks:

- exact packet shape and unique IDs;
- controlled vocabularies;
- source hashes, message counts, turn identities, and character-exact quotes;
- structural consistency, such as requiring both speakers for joint ownership;
- that a resolved thread has resolution evidence;
- that a genuinely dropped thread has no substantive or resolving response;
- that superseded threads name their replacement;
- that every case-local item is ineligible for direct graph routing.

Deterministic code does not decide that a response was substantive, a position
was jointly owned, or a claim was merely possible. Source grounding makes those
interpretations auditable; it does not make them true.

## Source-strength modes

| mode | intended use |
| --- | --- |
| `stated_condition` | The speaker states the condition as present. |
| `reported_statement` | The speaker reports another person's statement or position. |
| `possibility` | The source says may, might, could, or otherwise remains contingent. |
| `preference` | The source expresses a want or value, not an objective condition. |
| `concern` | The source expresses worry or feared consequence. |
| `inference` | The item is explicitly an interpretation rather than a source assertion. |
| `mixed` | One atomic source passage contains materially different strengths that must not be flattened. |

`mixed` is a warning to preserve the actual language, not permission to merge
unrelated constraints.

## Graph boundary

The state packet contains facts, entities, dates, preferences, and case-local
language. None of it can seed the graph. The deterministic projection is empty:

```text
conversation-state packet (case context)
  -> separate probabilistic reasoning-pattern abstraction required
  -> deterministic validation of fact-free pattern packet
  -> deterministic graph recall
```

An empty projection is not a semantic stand-down. It means the required
abstraction has not yet occurred.

## Five-case replay

The provider-free replay encoded all five ambiguous development conversations:

- 5 jointly developed current positions;
- 4 addressed-but-unresolved threads and 1 resolved thread;
- 43 reviewed constraints;
- 88 exact source references;
- 0 direct graph seeds;
- 0 runtime modifications and 0 provider calls.

This demonstrates representational capacity only. It does not show that the
production extractor can populate the packet, that the semantic labels are
independent gold, that the packet helps a reasoner, or that the graph adds value.

## Extraction-probe status

The bounded two-case extraction-only probe is now frozen and preflight-passed.
It selects the only reviewed resolved-thread case plus the addressed-unresolved
case where a false old label materially propagated downstream. One prompt, one
typed schema, exact source and code hashes, zero retries, a $0.02 ceiling, and
source-first axis scoring are locked. The dry run made zero calls; the full
non-network suite passed 4,113 tests, 1 skip, and 93 subtests.

The execution lineage is now closed. Two provider-schema attempts failed before
inference. JSON wire mode then reached inference; after the typed schema was
made visible in the formatting prompt, Case 03 returned a complete packet but
failed ownership custody and exact quote grounding. Source-first postmortem also
found the focal resolved thread absent, source-strength flattening, at most 3/8
reviewed constraints represented, and no assistant Turn 7 trajectory evidence.
The stop rule prevented Case 04. No full pipeline, graph, evaluator, downstream
answer, or runtime integration is authorized. The representation-capacity
result still stands; automatic population remains unproven and currently failed.
