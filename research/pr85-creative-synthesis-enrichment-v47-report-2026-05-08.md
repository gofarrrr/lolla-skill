# PR85 Creative/Synthesis Enrichment v47 Report

Date: 2026-05-08

## Verdict

PR85 enriches the dormant reviewed affordance substrate without changing live runtime pickup.

The audit target was the creative/synthesis ring: records where the source material may contain multiple downstream-relevant reasoning moves, but where indiscriminate splitting would create bloat. The strict criterion was:

> Add a separate affordance only when the source supports a distinct receiver transaction with different activation, evidence, misuse guards, treatment requirements, or use/reject/defer behavior.

Outcome:

- Add 4 source-backed affordances.
- Add 3 narrow absence rails.
- Keep adjacent creative/synthesis records compressed when the source changes examples or techniques but not the receiver transaction.
- Compile `model_affordances_v47` as dormant `draft_review_only` substrate.

## Added Affordances

### `association.schema-bridge-for-usable-context`

Why split:

The existing `association.structural-association-test` checks whether an analogy or linked pattern has causal/structural fit before transfer. The source also supports a different transaction: connect an unfamiliar idea to a known schema so it becomes quickly usable for a specific audience.

This changes the receiver action from "test the structure before transfer" to "make a new idea usable through a schema bridge, while keeping proof separate."

Primary source support:

- `Association_rag.md`: "instant context and understanding"
- `Association_rag.md`: "new idea becomes valuable only after it connects to an existing structure"
- `Association_rag.md`: "communication needs instant context without long explanation"
- `Association_rag.md`: "high-concept pitch"

Guard added:

- `schema-bridge-without-audience-action`

This blocks associations that are accurate or clever but do not create action, prediction, or decision usefulness for the receiver.

### `abstraction.abductive-hypothesis-framing-check`

Why split:

The existing `abstraction.evidence-anchored-compression-check` compresses concrete detail into a usable model and then regrounds it. The source also supports using abstraction as an abductive early hypothesis from limited observations, where the next move is focused evidence gathering or disconfirmation.

This changes the receiver action from "compress and reground" to "frame a provisional hypothesis and test it."

Primary source support:

- `abstraction_rag.md`: "Abstraction is vital for abductive reasoning"
- `abstraction_rag.md`: "limited set of observations"
- `abstraction_rag.md`: "formulating a hypothesis"
- `abstraction_rag.md`: "dictates the structure of the data gathering and analysis"
- `abstraction_rag.md`: "prove or disprove a hypothesis"

No new absence was added because the existing abstraction absences already cover map-as-reality and accuracy-without-action; the new affordance carries its own hypothesis-not-confirmed misuse guard.

### `mental-simulation.persona-fidelity-role-play`

Why split:

`mental-simulation` already had two real transactions: scenario rehearsal with thresholds and skill rehearsal/response preparation. The source separately supports persona/digital-twin simulation, where the receiver must define actor fidelity, behavior, decision rules, context, and validation checks.

This changes the receiver action from "compare futures" or "practice a response" to "model actor/workflow behavior with explicit fidelity and validation."

Primary source support:

- `Mental_Simulation_rag.md`: "digital twin creator"
- `Mental_Simulation_rag.md`: "carefully crafted AI persona, grounded in data"
- `Mental_Simulation_rag.md`: "Explicit Persona Definition"
- `Mental_Simulation_rag.md`: "Behavioral Tendencies and Personality"
- `Mental_Simulation_rag.md`: "Decision-Making Framework"
- `Mental_Simulation_rag.md`: "Validate AI simulations"

Guard added:

- `demographic-only-persona-simulation`

This blocks persona simulation that relies on surface demographics alone, because the source explicitly warns this can cause stereotyping and inaccurate behavioral predictions.

### `analogies-and-metaphors.generative-analogy-search`

Why split:

The existing `analogies-and-metaphors.structural-fit-transfer-test` is mainly about safe explanation and transfer. The source also supports analogies as generators of novel thinking: search remote domains, transfer mechanisms, create candidate options or hypotheses, then bound them with counterexamples.

This changes the receiver action from "make the target idea understandable with tested fit" to "generate and bound new candidate options."

Primary source support:

- `Analogies_And_Metaphors_rag.md`: "Analogies can be generative"
- `Analogies_And_Metaphors_rag.md`: "platforms for novel thinking"
- `Analogies_And_Metaphors_rag.md`: "wide-ranging analogical thinking"
- `Analogies_And_Metaphors_rag.md`: "remote domains"
- `Analogies_And_Metaphors_rag.md`: "counterexamples"

No new absence was added because the existing analogy absences already block analogy-as-proof and map-substitution.

## Added Absence Rail

### `divergent-vs-convergent-thinking.superficial-divergence-volume-without-variety`

Why not split:

The source names "superficial divergence" as high volume but low variety. That is not a new positive affordance; it is a quality guard on the existing divergence/convergence cycle.

This absence prevents the packet from treating many same-shaped ideas as genuine option widening.

## Compression-OK Decisions

The following records were audited and intentionally not expanded:

- `brainstorming`
- `lateral-thinking`
- `curiosity`
- `variation-and-selection`
- `adaptation`
- `branch-solve-merge`
- `creative-destruction`
- `synthesis-and-integration`
- `simplification`
- `narratives`

Reason:

Their sources contain rich examples and techniques, but those examples do not require separate receiver transactions under the strict PR55/PR85 criterion. Splitting them now would mostly create method-name bloat rather than better use/reject/defer behavior.

## Compile Result

Artifact:

- `data/compiled/model_affordances/affordances_v47.json`
- `data/compiled/model_affordances/quality_report_v47.md`

Compiled metadata:

- Artifact: `model_affordances_v47`
- Status: `draft_review_only`
- Records: `222`
- Affordances: `291`
- Absence records: `558`
- Schema-validation failures: `0`
- Source-hash failures: `0`
- Source-quote rejections: `0`

Delta from v46:

- Affordances: `+4`
- Absence records: `+3`

## Runtime Boundary

PR85 does not wire v47 into `/lolla`, lane adapters, packet rendering, prompts, or runtime pickup.

The live runtime guard remains:

- no `affordances_v47` reference in live runtime paths;
- no `model_affordances_v47` reference in live runtime paths;
- compiled artifact remains dormant reviewed substrate.

## Product Interpretation

PR85 is not "more extraction by default." It is a transaction-identity enrichment pass.

The important shift is preserving cognitive affordances that are easy to flatten:

- schema bridge versus structural association proof;
- abstraction as compression versus abstraction as abductive hypothesis;
- mental simulation as scenario rehearsal versus skill rehearsal versus persona-fidelity role-play;
- analogy as explanation versus analogy as candidate generator.

These are the kinds of distinctions that matter for a future receiver ledger. They help the LLM consider a card without being forced to use it, and they make rejection/defer decisions more auditable because each card has its own activation, evidence requirements, and misuse guards.
