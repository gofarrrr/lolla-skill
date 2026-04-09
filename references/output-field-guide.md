# Output Field Guide

Reference for all pipeline output fields. Read this when presenting results in Step 4 — it explains what each field means and how to use it.

---

## DeltaCard Fields

Each finding in `delta_card.top_findings` has:

| Field | What it means |
|-------|--------------|
| `tendency_name` | The cognitive tendency detected |
| `sub_pattern` | Specific sub-pattern within the tendency |
| `severity` | high / medium / low |
| `specific_passage` | Verbatim quote from the conversation that triggered detection |
| `challenge_statement` | A specific structural challenge — not generic advice |
| `next_move` | Concrete reversal trigger — a metric, date, or threshold |
| `intervention_hint` | Additional guidance on the corrective model — weave into the challenge naturally |
| `major_tensions` | Structural tensions (model pairs pulling in opposite directions) relevant to this detection |
| `is_trusted_surface` | If true, detection matched a curated sub-pattern (higher confidence). Use for your own weighting — don't flag to user |
| `selected_model_ids` | Corrective models routed to this finding |

### Compound Patterns

The system recognizes 6 named compound patterns — lollapalooza-style compounding where tendencies amplify each other:

| compound_id | Label | Description | Tendencies |
|-------------|-------|-------------|------------|
| `deadline-sanctioned-override` | Deadline-Sanctioned Override | Urgency creates permission while status removes resistance, making the exception path feel pre-cleared | stress-influence + authority-misinfluence |
| `halo-defended-escalation` | Halo-Defended Escalation | Borrowed status glow and threatened-loss pressure combine to make continuation feel safer than the substance warrants | mere-association + deprival-superreaction |
| `halo-carried-premature-commitment` | Halo-Carried Premature Commitment | A halo cue helps the team close over unresolved terms or unknowns instead of mapping them honestly | mere-association + doubt-avoidance |
| `salience-reinforced-optimism` | Salience-Reinforced Optimism | Vivid evidence is mistaken for a representative denominator, reinforcing an optimistic forward story | overoptimism + availability-misweighing |
| `borrowed-credibility-under-deadline` | Borrowed-Credibility Under Deadline | Urgency, rank, and borrowed halo combine to make the risky move feel pre-authorized before the substance earns it | authority + stress + mere-association *(cross-tier)* |
| `loss-justified-override` | Loss-Justified Override | Deadline pressure and authority create permission while threatened loss makes slowing down feel unacceptable | authority + stress + deprival-superreaction *(cross-tier)* |

Cross-tier compounds (3+ tendencies) are especially dangerous. Present the compound `description` as-is — it's curated.

### Secondary Findings

| Field | What it means |
|-------|--------------|
| `secondary_summarization_active` | If true, use the `secondary_additional_pressures_note` as a summary line |
| `secondary_additional_pressures_note` | Pre-written summary of secondary findings |
| `secondary_additional_pressure_count` | How many additional pressures were summarized |

---

## CompanionCheatSheet Fields

### Chunk Types

Each anchor's `chunks` array contains typed pieces of curated knowledge. There are 7 possible chunk types:

| chunk_type | What it means | Presentation label |
|------------|--------------|-------------------|
| `failure_mode` | Where this model breaks down; conditions under which it produces wrong answers | **Failure modes** |
| `premortem` | Questions this model would ask before proceeding; surfaces hidden assumptions | **Premortem questions** |
| `antagonist` | Models that create productive tension; where reasoning could be pulled differently | **Antagonists** |
| `ally` | Models that reinforce this one; shows the reasoning cluster being activated | **Allies** |
| `heuristic` | Operational rules of thumb; actionable shortcuts | **Heuristics** |
| `identity` | What this model IS, its core mechanism; helps the user recognize it | **Identity** |
| `prerequisite_gap` | A foundational model that should be in place BEFORE this one applies; flags missing prerequisites | **Prerequisite gap** |

Present whichever chunk types are present on the anchor. Not all 7 will appear on every anchor.

### Provenance

Each chunk has `provenance` with:
- `source_layer`: wave1 / wave2 / wave3 — which curation wave produced it
- `confidence`: high / medium / low
- `extraction_type`: explicit / normalized / unknown

You don't need to show provenance to the user, but use it for your own confidence weighting — high-confidence wave2 chunks are stronger signal than low-confidence ones.

### Sheet-Level Metadata

| Field | What it means |
|-------|--------------|
| `anti_echo_model_ids` | Models excluded because Lane 1 already covers them — prevents repetition |
| `reranker_active` | If true, embedding-based reranking was used to prioritize chunks by semantic relevance |
| `budget_max` | Maximum chunks allowed across all anchors |

---

## FramePressureCard Fields

### Element Types

Each `frame_element` has an `element_type` — three types, each revealing a different framing distortion:

| element_type | What it means |
|-------------|--------------|
| `assumption` | Something taken as true without examination; the reasoning depends on it but never tests it |
| `mutable_constraint` | Treated as fixed ("we can't change the timeline") but actually negotiable; the user may not realize this is a choice |
| `suppressed_counterfactual` | An alternative scenario that was never considered; the question was framed to exclude it |

### Element Metadata

| Field | Values | What it means |
|-------|--------|--------------|
| `frame_pattern` | string | From curated taxonomy — the named framing pattern |
| `fragility_signal` | string | What would break this element |
| `inquiry_stage` | why / what_if / how | Where in the reasoning chain: "why" probes foundations, "what_if" opens alternatives, "how" challenges implementation |
| `likely_default` | ego / social / inertia / emotion / none | What cognitive default probably anchored this frame element — explains WHY the framing happened |

### Reframe Move Types

Each `reframing` has a `reframe_move_type`:

| Move type | What it does |
|-----------|-------------|
| `inversion` | Flip the question ("instead of 'how do we grow faster', ask 'what would make us shrink'") |
| `perspective_shift` | Ask from a different stakeholder's viewpoint |
| `scope_expansion` | Widen the frame to include context that was excluded |
| `constraint_relaxation` | Remove a constraint treated as fixed and see what changes |

### Card-Level Metadata

| Field | What it means |
|-------|--------------|
| `anti_echo_model_ids` | Models excluded because Lane 1 already covers them |
| `overlap_flags` | Frame patterns that overlap Lane 1 at pressure-concept level |
