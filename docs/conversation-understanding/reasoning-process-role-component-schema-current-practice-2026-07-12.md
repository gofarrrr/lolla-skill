# Role-component schema current-practice check

Status: supports provider-free nested-component amendment; no call authorized  
Date: 2026-07-12

## Exact local signature

V2.1 recovered one coherent qualification record and protected e056, but
returned four expression/source entries and only three object entries across
parallel arrays. Deterministic custody correctly quarantined the record because
there is no unambiguous way to reconstruct which attributes belong together.

This is not a missing-meaning problem and must not be repaired by truncating,
padding, guessing, or matching prose in code.

## Current practice

OpenRouter's current structured-output guidance supports strict JSON Schema,
recommends clear property descriptions, and requires checking model/operator
parameter support with `require_parameters: true`. It also offers response
healing, which Lolla continues to disable because healing would obscure the
original failure and add an uncontrolled repair boundary. See
[OpenRouter structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs).

JSON Schema natively represents repeated related values as an array whose
items are objects. That representation makes each component's object kind,
interpretation, expression, and source alias structurally inseparable, rather
than relying on equal positions across parallel arrays. See
[JSON Schema arrays of objects](https://tour.json-schema.org/content/01-Getting-Started/06-Array-of-Objects).

This does not prove that a particular provider will accept Lolla's nested
schema or that the model will choose correct semantics. It does establish that
an array of component objects is the direct schema representation of the
identity Lolla needs.

## Adopted provider-free amendment

- Keep the v2.1 endpoint, coherent-record, coverage, and speaker-ownership
  prompt contract.
- Replace four parallel stance columns with one bounded `stance_components`
  array.
- Each component contains exactly one object kind, object interpretation,
  expression kind, and source alias.
- Keep component cardinality, exact parent-evidence restriction, duplicate
  rejection, and record-level custody.
- Keep the relation contract and four-call ceiling unchanged.
- Measure schema depth, bytes, prompt size, and reviewed-fixture replay before
  any provider call.

## Rejected

- No array truncation or padding.
- No deterministic semantic pairing or keyword repair.
- No response healing, retry, fallback, or judge.
- No provider call on the exposed succession case.
- No return to the large combined v4 nested contract; this amendment nests
  only the components inside one already-small fixed-role task.
