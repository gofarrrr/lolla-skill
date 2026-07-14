# Reasoning-process stance-object v4.1 contract

Status: provider-free design input  
Date: 2026-07-12

## Purpose

V4 represented stance objects correctly provider-free but its nested component
evidence array produced a depth-11 schema that Google rejected before
inference. V4.1 preserves the semantic design while making every component
atomic and shallower.

## Atomic component

Position records retain the existing starting, current, qualification, and
trajectory interpretations and their role evidence arrays. On the provider
wire they add five bounded, index-aligned arrays plus one
`stance_object_fidelity_note`:

- `stance_temporal_roles`;
- `stance_object_kinds`;
- `stance_object_interpretations`;
- `stance_expression_kinds`;
- `stance_source_evidence_ids`.

Index `i` across the five arrays is one atomic component containing:

- `temporal_role`: `starting`, `current`, or `qualification`;
- `stance_object_kind`: belief/assessment, action/proposal, intended
  outcome/policy, acceptance/willingness, reported position landscape, or
  unclear;
- `stance_object_interpretation`: one concise source-faithful object;
- `stance_expression_kind`: the categorical stance toward that object;
- `source_evidence_id`: exactly one alias from the parent role.

The deterministic compiler requires equal array lengths and immediately
reconstructs ordinary stance-component objects for custody and downstream
inspection. It does not infer or repair semantic alignment.

If an object needs two source aliases, the model emits two atomic components.
If one sentence carries stances toward two objects, the model emits two
components that may share the same alias. This avoids a nested evidence array
without losing inspectable source custody.

Expression kinds remain the v4 categorical vocabulary. They are descriptions,
not scores, confidence levels, or an ordinal ladder.

## Semantic responsibilities

The model must:

- identify the object before classifying the stance expression;
- keep belief intensity distinct from a chosen action or outcome;
- separate a proposal action from willingness to accept its result;
- represent reported positions without inventing user endorsement;
- preserve uncertainty, conditions, provisionality, and counterpressure;
- split components rather than combining multiple aliases or objects into one;
- explain the decomposition in `stance_object_fidelity_note`.

## Deterministic responsibilities

Code may enforce:

- exact fields, enums, string bounds, total bounds, and per-role counts;
- exactly one component source alias;
- component alias membership in the existing validated parent evidence role;
- exact duplicate rejection;
- starting component presence matching starting-role presence;
- existing hashes, packet identity, call budgets, and recordwise custody.

Code may not infer semantic object or expression labels, enforce an
object/expression compatibility matrix, compare strength, scan prose for stance
keywords, semantically merge components, or score quality.

## Compatibility target

- V4.1 adds only documented basic schema types, object properties, required
  fields, descriptions, enums, and bounded arrays/strings.
- It adds no nested component array, `oneOf`, conditional schema, `$ref`,
  `pattern`, or `uniqueItems` keyword.
- The wire adds no nested object or nested evidence array; the parallel columns
  keep the schema in the previously served depth class.
- Inherited v2 role evidence keywords remain because that exact interface was
  previously served successfully; deterministic validation remains
  authoritative.
- Maximum response schema target: less than 4,000 bytes and depth at most 9.
- Provider-free conformance is still not provider compatibility or semantic
  correctness.

## Prospective boundary

All amb1 position cases are closed. The three new amb2 conversations are frozen
before model use. Protected fixtures and case semantics are not included in
prompts. A single probe case may be selected only by the predeclared SHA-256
rule after all three cases exist and local gates pass. No same-case retry,
fallback, response healing, evaluator, graph, or runtime call is authorized.
