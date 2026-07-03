# Lolla Progress Report

Status: Living PM report
Last updated: 2026-07-03

This file tracks where Lolla stands against the big-picture product direction in
`docs/lolla-reasoning-audit-harness-prd.md`.

Use it after each PR to answer four questions:

1. What changed?
2. Which PRD item did it move?
3. What did it deliberately not change?
4. Did it preserve the product boundary?

## Big-Picture Anchor

Lolla is evolving from a human-triggered skill into a local, inspectable,
agent-callable reasoning-audit harness.

Core thesis:

> Lolla lets LLMs do semantic judgment, but surrounds that judgment with
> deterministic custody: fixed steps, structured artifacts, validation gates,
> run health, telemetry, archive, replay, and eventually evaluation.

Product boundary:

> Lolla asks whether the reasoning that led to an answer or action deserves
> trust.

Lolla is not:

- a generic guardrail,
- a sandbox,
- an HTTP proxy or firewall,
- an identity broker,
- a policy engine,
- a domain expert,
- a fact-checking engine,
- a naive LLM judge.

The practical product loop we are improving first:

```text
call Lolla manually
-> produce revised answer and memo
-> archive the run
-> inspect health, trace, and custody
-> decide what to trust
```

The broader harness loop remains:

```text
conversation or agent run
-> reasoning audit
-> machine-readable result
-> risk/mode metadata
-> local artifact custody
-> evaluation
-> optional control-plane integration
```

## Fresh-Session Handoff: 2026-07-01

Current handoff state:

```text
PR216 merged the Decision Work Brief Runtime-Attached Internal v1 package into
main. The runtime-attached path is now functional as an internal, default-off,
post-archive sidecar system when resolver-approved safe refs exist. It can
defer, block, fail closed, render short receipts, and produce agent handoff
packets without changing live answer generation.

The key remaining product gap is automatic semantic supply for arbitrary new
completed runs. Prepared safe refs and checked-in registry examples work, but a
new run normally defers until the missing semantic artifacts exist. The next
planning spine is
docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md.
That PRD defines the path from completed archive to deterministic packet,
offline interpretation queue, bounded LLM/Codex interpretation read,
validation, brief/enriched brief, triage, resolver-approved refs, and sidecar
update. It explicitly keeps direct runtime interpretation, default-on behavior,
model calls from runtime, product proof, scoring, human-validation claims, and
action authorization out of scope.

The first contract slice after that PRD is
docs/conversation-understanding/decision-work-offline-interpretation-queue-contract-v0.md.
It defines offline queue item/result vocabulary only and gates to the next
deterministic packet-builder slice.

The deterministic packet-builder slice is
docs/conversation-understanding/decision-work-offline-interpretation-queue-builder-v0.md.
It can prepare checked-in-safe queue items from completed run refs and optional
PR130 packet refs while leaving semantic fields empty and preserving non-claims.

The bounded operator/Codex handoff packet is
docs/conversation-understanding/decision-work-operator-codex-interpretation-prompt-packet-v0.md.
It defines the future prompt/input envelope for filling a PR133 interpretation
read, then stops before generated-read intake.

The generated interpretation read intake validator is
docs/conversation-understanding/decision-work-generated-interpretation-read-intake-v0.md.
It accepts externally supplied Decision Work interpretation reads only after
strict schema, source-ref, uncertainty, privacy, custody, and non-claim checks.
It does not generate reads, render briefs, enrich briefs, create triage, update
resolver refs, update sidecars, call models, prove product value, validate
advice correctness, or authorize action. The next conservative slice is a
three-case intake review, not a broad regeneration or runtime sidecar update.

The three-case intake review is
docs/conversation-understanding/decision-work-generated-interpretation-read-intake-review-v0.md.
It reviews the PR182 validator against the three existing checked-in reads and
temporary synthetic rejection cases, confirms the no-sidecar/no-action boundary,
and selects a single bounded operator/Codex generated-read pilot next.

The one-case operator/Codex generated-read pilot is
docs/conversation-understanding/decision-work-operator-codex-generated-read-pilot-v0.md.
It creates a checked-in-safe launch-beta generated-read candidate and PR182
intake result, proves the validator accepts the artifact for later offline
planning, and still stops before brief rendering, enrichment, triage, resolver
approval, runtime sidecar update, model calls, proof claims, scoring, or action
authorization. The next conservative slice is a generated-read-to-brief supply
plan, not runtime wiring.

The generated-read-to-brief supply plan is
docs/conversation-understanding/decision-work-generated-read-to-brief-supply-plan-v0.md.
It defines which accepted generated-read fields may feed future offline brief
supply, which fields must remain evidence-only, what source refs, uncertainty,
privacy limits, and non-claims must travel forward, and what must block. It
still does not generate a brief, enrich a brief, generate triage, mark resolver
refs usable, update sidecars, call models, score advice, claim proof, or
authorize action. It selects a deterministic brief-supply adapter next.

The Decision Work Generated Read Brief Supply Adapter is
docs/conversation-understanding/decision-work-generated-read-brief-supply-adapter-v0.md.
It adds PR186's deterministic adapter and CLI for accepted PR182 generated-read
intake results. It emits safe brief-supply packets with allowed copied fields,
source refs, uncertainty, blocker status, custody flags, and non-claims, while
still stopping before brief rendering, enrichment, triage, resolver ref use,
runtime sidecar update, model calls, proof claims, scoring, or action
authorization. It selects a one-case generated-read brief rendering pilot next.

The Decision Work Generated Read Brief Rendering Pilot is
docs/conversation-understanding/decision-work-generated-read-brief-rendering-pilot-v0.md.
It adds PR187's one-case launch-beta Markdown render from a ready PR186 supply
packet. The rendered brief preserves source refs, uncertainty, privacy limits,
custody flags, and non-claims, while still stopping before enrichment, triage,
resolver ref use, runtime sidecar update, model calls, proof claims, scoring,
or action authorization. It selects a generated-read brief versus existing
brief review next.

The Decision Work Generated Read Brief vs Existing Brief Review is
docs/conversation-understanding/decision-work-generated-read-brief-vs-existing-brief-review-v0.md.
It adds PR188's docs/review/tests-only comparison between the generated-read
launch-beta brief and the existing rendered and enriched launch-beta briefs.
The review finds the generated-read brief preserves the core decision/action
consequence and boundaries, but is thinner than the enriched brief. It selects a
second generated-read brief rendering pilot next, while still stopping before
enrichment, triage, resolver ref use, runtime sidecar update, model calls,
proof claims, scoring, or action authorization.

The Decision Work Generated Read Second Brief Rendering Pilot is
docs/conversation-understanding/decision-work-generated-read-second-brief-rendering-pilot-v0.md.
It adds PR189's deploy-intake second-case generated-read rendering pilot using a
checked-in-safe generated read, PR182 intake, PR186 supply, and the existing
PR187 renderer. The rendered brief keeps compliance/workflow caveats, source
refs, uncertainty, privacy limits, custody flags, and non-claims visible while
still stopping before enrichment, triage, resolver ref use, runtime sidecar
update, model calls, proof claims, scoring, or action authorization. It selects
a two-case generated-read brief pattern review next.

The Decision Work Generated Read Brief Two-Case Pattern Review is
docs/conversation-understanding/decision-work-generated-read-brief-two-case-pattern-review-v0.md.
It adds PR190's docs/review/tests-only comparison of the launch-beta and
deploy-intake generated-read-rendered briefs. The review finds the path
preserves action consequence, source refs, uncertainty, privacy limits,
evidence-only exclusions, and non-claims across two decision families, while
remaining too thin for triage generation or runtime sidecar use. It selects a
generated-read triage supply plan next.

The Decision Work Generated Read Triage Supply Plan is
docs/conversation-understanding/decision-work-generated-read-triage-supply-plan-v0.md.
It adds PR191's docs/review/tests-only plan for turning generated-read artifacts
into future triage supply. The plan defines allowed inputs, routing fields,
evidence-only fields, blocked fields, statuses, route categories, custody
requirements, and forbidden quality/authority route concepts while still
stopping before triage generation, resolver ref use, runtime sidecar update,
model calls, proof claims, scoring, or action authorization. It selects a
deterministic generated-read triage supply adapter next.

The Decision Work Generated Read Triage Supply Adapter is
docs/conversation-understanding/decision-work-generated-read-triage-supply-adapter-v0.md.
It adds PR192's deterministic adapter and CLI for preparing
`lolla.decision_work_generated_read_triage_supply.v0` packets from generated
read, intake, brief-supply, and rendered-brief refs. Launch-beta and
deploy-intake artifacts can now produce ready-for-offline-triage-generation
supply packets, while rejected intake, non-ready supply, missing refs,
missing uncertainty, privacy risk, authority claims, resolver ref use, runtime
sidecar update, model calls, proof claims, scoring, and action authorization
remain blocked. It selects a generated-read triage generation pilot next.

The Decision Work Generated Read Triage Generation Pilot is
docs/conversation-understanding/decision-work-generated-read-triage-generation-pilot-v0.md.
It adds PR193's first checked-in-safe generated triage read for
`launch-public-enterprise-beta`. The read routes attention to ordinary
caveated offline brief candidacy, source-depth limits, private-context need,
overtrust risk, and runtime attachment blocking without grading answer
quality, claiming correctness or proof, marking resolver refs usable, updating
sidecars, calling models, or authorizing action. It selects a review-only
triage pilot review next before any second case.

The Decision Work Generated Read Triage Pilot Review is
docs/conversation-understanding/decision-work-generated-read-triage-pilot-review-v0.md.
It adds PR194's docs/review/tests-only review of the first generated triage
read. The review finds the launch-beta route vocabulary stays in
attention-routing territory and is safe enough to try deploy-intake next, while
still not creating a second triage read, marking resolver refs usable, updating
sidecars, wiring runtime, calling models, scoring, proving, or authorizing
action.

The Decision Work Generated Read Second Triage Pilot is
docs/conversation-understanding/decision-work-generated-read-second-triage-pilot-v0.md.
It adds PR195's checked-in-safe generated triage read for
`deploy-assisted-intake-routing`. The read routes attention to source-depth
limits, private-context need, high overtrust risk, domain review,
legal/compliance review, agent inspection, user-surface blocking, and runtime
attachment blocking. It does not grade answer quality, claim operational,
legal, compliance, or clinical clearance, mark resolver refs usable, update
sidecars, wire runtime, call models, prove value, or authorize action. It
selects a two-case generated-read triage pattern review next.

The Decision Work Generated Read Triage Two-Case Pattern Review is
docs/conversation-understanding/decision-work-generated-read-triage-two-case-pattern-review-v0.md.
It adds PR196's docs/review/tests-only comparison of the launch-beta and
deploy-intake generated triage reads. The review finds the route vocabulary can
distinguish lower-risk caveated offline candidacy from higher-risk
domain/compliance inspection while preserving source-depth, overtrust, runtime,
resolver, and action boundaries. It selects a generated-read resolver supply
plan next, not resolver approval, sidecar update, runtime wiring, scoring,
proof, or action authorization.

The Decision Work Generated Read Resolver Supply Plan is
docs/conversation-understanding/decision-work-generated-read-resolver-supply-plan-v0.md.
It adds PR197's docs/review/tests-only plan for turning generated-read
artifacts and generated triage reads into future resolver-supply candidates.
The plan defines allowed inputs, safe ref candidates, evidence-only fields,
blocked fields, required source refs, route effects, candidate statuses,
custody requirements, non-claims, and the hard boundary between resolver
supply and resolver approval. It selects a deterministic resolver-supply
adapter next while still stopping before resolver approval, sidecar update,
runtime wiring, model calls, scoring, proof claims, or action authorization.

The Decision Work Generated Read Resolver Supply Adapter is
docs/conversation-understanding/decision-work-generated-read-resolver-supply-adapter-v0.md.
It adds PR198's deterministic adapter and CLI for preparing
`lolla.decision_work_generated_read_resolver_supply.v0` candidate packets from
generated-read, intake, brief-supply, rendered-brief, triage-supply, and
generated-triage refs. Launch-beta can produce a resolver-candidate packet;
deploy-intake produces a candidate packet that preserves runtime/user-surface
blocking because of domain/compliance and agent-inspection routes. The adapter
still does not approve refs, mark refs usable, update sidecars, wire runtime,
call models, score answer quality, prove value, validate advice correctness,
or authorize action. It selects a generated-read resolver-supply review next.

The Decision Work Generated Read Resolver Supply Review is
docs/conversation-understanding/decision-work-generated-read-resolver-supply-review-v0.md.
It adds PR199's docs/review/tests-only pass over launch-beta and deploy-intake
resolver-supply candidate packets. The review confirms the packets preserve
source refs, uncertainty, privacy limits, route-specific blockers, custody
flags, and non-claims while remaining candidates rather than resolver
approval, runtime sidecar permission, user-surface readiness, quality labels,
proof, or action authorization. It selects a pre-runtime v1 package gate next.

The Decision Work Automatic Semantic Supply Pre-Runtime v1 Package Gate is
docs/conversation-understanding/decision-work-automatic-semantic-supply-pre-runtime-v1-package-gate-v0.md.
It adds PR200's package gate and manifest for PR178-PR199. The package claim
is narrow: an offline, checked-in-safe, pre-runtime chain from generated
interpretation reads to resolver-supply candidate packets, with validation,
rendering, triage, and resolver-boundary safeguards. It still excludes runtime
attachment, resolver approval, sidecar updates, runtime wiring, default-on
behavior, arbitrary-run production automation, scoring, proof claims, human
validation, advice correctness, and action authorization.

The Decision Work Resolver Candidate Sidecar Update Plan is
docs/conversation-understanding/decision-work-resolver-candidate-sidecar-update-plan-v0.md.
It adds PR201's docs/review/tests-only plan for a future offline sidecar update
packet. The plan defines what can move from a resolver-supply candidate into a
proposed packet, how launch-beta and deploy-intake should behave, and which
statuses should exist, while still forbidding actual sidecar writes, archive
mutation, resolver approval, runtime wiring, model calls, scoring, proof
claims, advice-correctness claims, and action authorization.

The Decision Work Resolver Candidate Sidecar Update Packet Adapter is
docs/conversation-understanding/decision-work-resolver-candidate-sidecar-update-packet-adapter-v0.md.
It adds PR202's deterministic adapter and CLI for offline proposed sidecar
update packets. The adapter emits
`lolla.decision_work_resolver_candidate_sidecar_update_packet.v0` from PR198
resolver-supply candidate packets. Launch-beta produces a ready proposed packet
and deploy-intake preserves runtime/user-surface blocking, while no actual
sidecar write, archive mutation, resolver approval, runtime wiring, model
call, quality label, proof claim, advice-correctness claim, or action
authorization occurs.

The Decision Work Sidecar Update Packet Review is
docs/conversation-understanding/decision-work-sidecar-update-packet-review-v0.md.
It adds PR203's docs/review/tests-only pass over launch-beta and deploy-intake
sidecar update packets. The review confirms proposed packets remain offline
artifacts, not actual sidecar writes, archive mutation, resolver approval,
runtime wiring, user-surface readiness, quality labels, proof claims, or action
authorization. It selects a pre-write package gate next.
```

```text
PR177 Decision Work Brief Runtime-Attached Internal v1 Package Refresh v0 is
the latest Decision Work Brief runtime-attachment slice recorded in this
working tree. It packages PR160-PR176 as an internal, default-off,
post-archive sidecar path for completed runs when safe refs are supplied
manually or through checked-in-safe registry fixtures. The refresh manifest
includes the runtime attachment contracts, sidecar contract, manual bundle,
eligibility gate, receipt renderer, agent handoff, default-off hook, safe
supply resolver, checked-in-safe case registry, resolver and registry fixture
reviews, runtime modules, CLIs, and tests. It preserves the limits that the
hook is not default-on, production hook registry lookup is not first-class,
arbitrary completed runs normally defer without safe semantic refs, and the
package is not customer readiness, human validation, product proof,
answer-quality scoring, advice correctness, or action authorization. PR176
reviews temp hook fixtures where the PR175 checked-in-safe registry supplies
launch-beta, deploy-intake, and cofounder refs through the PR171 resolver and
PR172 resolver-aware bundle seam. The registry-backed fixtures produce
generated sidecars, available receipts, and agent handoff packets without
checked-in sidecar outputs, while still recording that the production hook has
no first-class registry case-key input and arbitrary completed runs normally
defer without safe semantic refs. PR176 selects
`runtime_attached_v1_package_refresh`. PR175 adds a deterministic
checked-in-safe case registry for the three known Decision Work Brief examples,
plus a loader and CLI that validate relative safe refs before handing them to
the PR171 resolver in `checked_in_safe_case_registry` mode. The resolver can
now feed the PR172 bundle from registry refs without manual env refs, while the
runtime hook remains unchanged and default-off. PR174 reviews the PR173 hook sidecar outputs
across flag-off, deferred/no-safe-inputs, safe-ref generated, safe-brief-only
agent-inspection, direct-runtime-interpretation-blocked, privacy-blocked, and
failed-closed fixture states. It checks in only review conclusions and tests,
not runtime sidecar fixtures, and selects `checked_in_safe_case_registry`
because useful available states still depend on explicit safe refs. PR173 wires
the existing default-off post-archive hook behind
`LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE` to build PR171 resolver output, pass
that output into the PR172 resolver-aware bundle, and write a concrete
`decision_work/` sidecar state: available, agent-only/caveated, deferred,
blocked, or failed-closed. The hook remains default-off, post-archive,
non-blocking, fail-closed, model-call-free, and unable to interpret messy
conversation meaning, score answer quality, claim product proof or human
validation, or authorize action. PR172 teaches the
manual PR162 runtime bundle generator to consume PR171 resolver output via
`--resolver-output`, copy only resolver-approved safe refs, preserve resolver
status in attachment status and agent handoff, and produce available,
agent-only/caveated, deferred, queued, local-private-required, or blocked
receipts. PR171 implements a deterministic
resolver and CLI that read the PR170 contract, validate explicit safe refs,
redact local paths in resolver output, exclude unsafe inputs, and emit
resolved/deferred/blocked/feedability status without interpreting conversation
meaning or changing the runtime hook. PR170 defined the resolver modes,
statuses, input types, unsafe exclusions, output shape, custody flags, and
non-claims needed before implementation. PR169
classified the runtime-attached path's required inputs and selected
`build_safe_brief_supply_resolver_contract` because PR160-PR168 show a safe
default-off hook but no general safe run-specific brief/enriched/triage supply
path. PR168 reviewed PR160-PR167 and chose `safe_brief_supply_planning`
because the default-off post-archive hook is mechanically attached but still
cannot supply run-specific safe brief, enriched brief, and triage inputs on its
own. PR160-PR167 follow the merged Offline v1 package and PR159 runtime
attachment PRD: they define the runtime attachment contract, sidecar shape,
manual bundle generator, eligibility gate, short receipt renderer, agent
handoff packet, and a default-off post-archive hook in `scripts/archive_run.py`
behind `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE`. The hook is sidecar-only,
post-archive, non-blocking, fail-closed, and product-useful only when safe
brief inputs are supplied. It does not touch `SKILL.md` or `scripts/skill/*`,
does not call models, does not change prompts, does not make runtime
attachment default-on, and does not claim product proof, human validation,
answer-quality scoring, advice correctness, or action authorization. PR158
Decision Work Brief Offline v1 Package Gate v0 is the
latest packaged offline/evidence slice. PR159 recorded the planning bridge for
the flagged post-archive path. PR113
introduced the product-facing brief target and corrected the receipt debug
summary back to an internal maintainer layer. PR114 added the machine-readable
brief schema. PR115 added the read-only local packet builder. PR116 added the
first one-case Codex-assisted provisional draft. PR117 added a deterministic
Markdown renderer and checked-in-safe rendered example. PR118 reviewed that
first rendered brief and chose `proceed_to_tiny_second_case`. PR119 added the
second `launch-public-enterprise-beta` case and chose
`proceed_to_small_pattern_review`. PR120 compared the two-case pattern and chose
`proceed_to_third_diversity_case`. PR121A adds exactly one third diversity case,
`deploy-assisted-intake-routing/20260627T130339Z_4cd3cb`, and gates to
`proceed_to_three_case_pattern_review`. PR122 reviews the three checked-in-safe
rendered briefs together, finds a consistent action-consequence signal, and
chooses `proceed_to_plain_language_renderer_patch` because the rendered surface
still reads too much like internal machinery for a board/customer reader. PR123
patches the renderer so the main body uses plain-language decision-brief
headings and moves source refs, uncertainty, custody flags, and non-claims into
a compact "Evidence and limits" section. It regenerates the three existing
rendered examples. PR124 rereviews those examples and chooses
`proceed_to_local_private_adequacy_check`. PR125 completes one read-only
local-private shadow review for `launch-public-enterprise-beta` and records
`adequate_but_missing_private_nuance`. PR126 selects
`run_more_local_private_adequacy_checks`, not runtime attachment. PR127 reframes
the source-depth question into a conversation interpretation gap map across the
three cases and gates to `define_interpretation_target_contract`. PR128 defines
`lolla.decision_work_conversation_interpretation_contract.v0` as a future-facing
contract for the conversation fields, custody statuses, interpretation
ownership, privacy handling, and handoff shape that later work may preserve. It
does not add runtime extraction. PR129 compares that PR128 contract against the
current completed-run artifact and Decision Work Brief packet surface, finds
that source/status carriage exists but field-grouped contract interpretation
inputs are still missing, and chooses `build_offline_interpretation_packet`. It
does not add runtime extraction. PR130 adds the offline packet builder for
`lolla.decision_work_conversation_interpretation_packets.v0`: a deterministic,
read-only dossier over completed-run artifacts, the PR115 packet surface, and
the PR128 contract field groups. It records source refs, source status,
private/redacted availability, field policies, future interpretation questions,
custody flags, and non-claims, but fills no semantic fields. It does not add
runtime extraction, model-call code, prompt changes, archive mutation,
answer-quality scoring, product proof, human validation, new cases, broad
batching, customer marketing copy, or agent action authorization. PR131 uses
exactly one fresh local PR130 checked-in-safe packet for
`launch-public-enterprise-beta/20260627T104146Z_7bfe79` and checks in a tiny
Codex-assisted provisional read over 11 PR128 fields. It interprets the
decision question, action consequence, live options, thresholds, evidence
gates, useful/noisy friction risk, and non-proof boundary while marking
starting direction, abandoned options, and lost value as partial or
insufficient-context. It does not check in the generated source packet or raw
private content, and it recommends `run_second_tiny_offline_read` before any
schema formalization or runtime plan. PR132 repeats the same tiny read on
`deploy-assisted-intake-routing/20260627T130339Z_4cd3cb`; the field set still
works across a healthcare operations/deployment decision, with starting
direction, abandoned options, and lost value still source-limited. It gates to
`define_interpretation_read_schema`. PR133 defines
`lolla.decision_work_conversation_interpretation_read.v0` as the reusable schema
for future provisional offline interpretation reads: source refs, uncertainty,
privacy limits, human-review flags, custody flags, non-claims, and
`must_not_be_used_as_quality_label` are required, while runtime extraction,
model calls, product proof, answer-quality scoring, and agent authorization
remain out of scope. PR134 compares the PR131 and PR132 reads through the PR133
schema shape, finds stable useful fields for decision question, action
consequence, thresholds, evidence gates, useful friction, and non-proof
boundaries, and chooses `proceed_to_brief_enrichment_test`. It does not create
a third read, enrich a brief, patch the packet builder, change runtime, or
claim product proof. PR135 creates one separate enriched
`launch-public-enterprise-beta` brief from the PR131 read, leaving the original
rendered brief untouched, and gates to `proceed_to_original_vs_enriched_review`.
PR136 compares the original and enriched launch-beta briefs and gates to
`proceed_to_second_enriched_brief_test`. PR137 creates one separate enriched
`deploy-assisted-intake-routing` brief from the PR132 read and gates to
`proceed_to_enriched_brief_pattern_review`. PR138 compares the two enriched
briefs, finds the enrichment pattern useful enough to formalize rules, and
chooses `proceed_to_enrichment_rules_contract` while explicitly not
implementing PR139. PR139 defines
`lolla.decision_work_brief_enrichment_rules_contract.v0`: a conservative
contract for which interpretation fields may enter the user-facing brief, which
must remain evidence-only, which concepts are forbidden, and what any offline
builder must preserve. PR140 adds that deterministic offline builder and CLI,
generating separate checked-in-safe builder outputs for launch-beta and
intake-routing without overwriting the original or hand-built enriched briefs.
PR141 compares the builder outputs against the hand-built examples, finds the
useful signal and rules compliance survived but the generated language is still
too templated, and chooses `proceed_to_builder_rule_patch`, not a third builder
case or runtime planning. PR142 patches the deterministic builder wording and
regenerates the two builder-enriched examples so the interpretation section is
less repetitive while preserving PR139 rules, uncertainty, source limits, and
non-claims. PR143 reviews those patched outputs and chooses
`proceed_to_offline_system_closure_gate`. PR144 decides the offline Decision
Work Brief surface is coherent enough to package and selects
`package_pr114_pr144`, still without runtime integration or product-readiness
claims. PR145 creates the PR114-PR144 package manifest and packaging gate:
explicit package scope, file groups, useful signal, unresolved risk, validation
checklist, staging list, do-not-stage warnings, suggested commit message, and
suggested PR description. The enrichment-system sequence still adds no runtime
integration, model call, new interpretation read, archive mutation, product
proof, human validation, answer-quality scoring, or agent action
authorization. PR146 performs two more read-only local-private adequacy checks
on the cofounder and intake-routing cases, records only safe conclusions, finds
the checked-in-safe briefs adequate with private nuance, and recommends
`proceed_to_third_builder_case` before any runtime-attachment plan. PR147 then
tests whether the cofounder case can become the third deterministic
builder-enriched example, and blocks the output because there is no
builder-compatible PR133-shaped cofounder interpretation read. It chooses
`create_third_interpretation_read_first`, not a schema workaround, builder run,
or runtime plan. PR147A creates that missing cofounder read using the formal
`lolla.decision_work_conversation_interpretation_read.v0` schema, keeps the
same tiny field subset as the first two reads, marks starting direction,
abandoned/rejected options, and lost value as source-limited, and gates to
`test_brief_enrichment_from_interpretation` for a future deterministic builder
output PR. PR148 runs the deterministic offline enriched-brief builder on the
cofounder rendered brief using the PR147A read and PR139 rules contract,
creating a third builder-generated enriched example while preserving
uncertainty, source limits, field exclusions, and non-claims. It finds the
output readable enough for pattern review, notes a mild deterministic-template
weakness in the first enrichment paragraph, and chooses
`proceed_to_three_builder_case_pattern_review`, not runtime integration,
product proof, or human validation. PR149 compares all three builder-generated
enriched briefs across launch timing, healthcare deployment controls, and
founder governance. It finds the builder stable enough to preserve the useful
action-consequence signal while keeping uncertainty, source limits,
evidence-only exclusions, and non-claims visible. Its decision gate is
`proceed_to_human_review_intake_plan`, because the next meaningful risk is
human usefulness and source-depth review rather than another deterministic
builder case or runtime attachment. PR150 defines the human-review intake plan
for those three builder outputs, including reviewer questions, stop
conditions, allowed outcomes, and a `run_human_review_pilot` gate without
claiming completed human review. PR151 creates the blank human-review pilot
scaffold and response template, making the pilot runnable without filling any
human fields. PR152 records that the pilot packet is ready to run but not
complete: no human response has been collected, no human validation has
happened, runtime/customer-facing use remains blocked, and the next evidence
step requires a real human reviewer. PR153 records that no real human response
exists yet, so the lane is paused until human review capacity returns rather
than substituting Codex-filled answers. PR154 reframes human review as a
calibration layer, not the future normal operating model, and defines
`lolla.decision_work_automatic_triage_contract.v0` for a future automatic
routing layer that can route briefs toward user surface, agent inspection,
source-depth blocking, private-context needs, domain/human calibration, or
runtime blocking without scoring answer quality or authorizing action. PR155
adds the deterministic checked-in-safe automatic triage packet builder over the
three existing builder-enriched cases, carrying refs, custody flags, triage
field policy, future tasks, and known limits while filling no semantic triage
fields. PR156 uses one PR155 packet shape to create a Codex-assisted
provisional triage read that routes the three cases differently: launch-beta is
the closest normal caveated brief candidate, deploy-intake requires
domain/compliance caution, and the cofounder/governance case remains the
highest overtrust and human/domain-calibration risk. PR157 closes the chain as
functional offline v1 with explicit limitations: the system can preserve
source/custody status, render and enrich briefs, prepare triage packets, and
create provisional triage reads, but it is not runtime-integrated, customer
ready, human validated, product proof, answer-quality scoring, or action
authorization. PR158 packages Offline v1 by referencing the PR145 base package
and listing PR145-PR157 additions, while keeping human calibration deferred and
runtime/customer-facing use blocked. PR159 is the follow-on runtime attachment
PRD: it recommends post-archive, non-blocking, flagged generation on completed
clean runs only, with a short user receipt, full brief/evidence link, structured
agent handoff by source refs and privacy boundaries, and blocked/deferred states
for incomplete artifacts, failed hygiene, missing revised answer, source-depth
thinness, overtrust risk, and domain/legal escalation. It does not implement the
runtime hook. PR104
remains the latest
Decision Trail human-review intake slice; PR85 remains the latest packaged
product-evidence eval-lane slice; PR70
remains the audit/accountability machinery closure gate; PR48 remains the
high-stakes evidence gate; PR54 remains the paused v0 values/priorities
worksheet gate. Use git log for the exact current commit hash.
```

Current Decision Trail standing:

```text
The live Lolla skill still produces audited answers and archived artifacts.
The Decision Trail lane is an offline reader/packetizer over completed runs.
PR86-PR89 built the sparse report shell, exporter, fixture review, and
interpretation-gap decision. PR90-PR95 built narrow specialist contracts,
checked-in-safe packets, traps, a discipline dry run, a path decision, and
local-private packet mode. PR96 smoke-reviewed that packet mode locally. PR97
filled a tiny one-case local-private specialist-output pilot. PR98 reviewed
that pilot and blocked broadening until a contract/packet patch. PR99 applies
that patch. PR100 uses the patched shape for one more local-private pilot.
PR101 compares PR97 and PR100 before any broadening. PR102 uses one
deployment-controls contrast case and stops the pilot-expansion momentum.

What works now: an operator can use a CLI to build checked-in-safe packet
fixtures or local-private packets for completed run directories. PR96 shows
metadata-only local-private packets work on two real completed runs without
copying raw/private content, and include-text local packets work mechanically
with unsafe-for-commit marking. PR97 shows a local-private include-text packet
can support bounded, contract-shaped specialist outputs for conversation
shape, likely action, friction/lost value, and conservative fan-in. PR98 shows
the useful path is real, but the contracts need a small patch before reuse.
PR99 adds that patch: vanilla-overlap read, lost-value severity read,
assistant-influence source status, source-scope/truncation impact, fan-in
downgrade triggers, and local-private retention policy metadata.
PR100 then exercises those fields on the `accept-founding-engineer-role` case.
The strongest useful signal is that `vanilla_overlap_read` downgrades the net
read to partial usefulness because the vanilla conversation already contained
much of the visible action sequence. PR102 adds a different deployment-controls
case and shows useful friction can also mean reducing noisy gate bloat while
preserving operating stop conditions.

What does not work yet: the specialist-output lane is local-private,
Codex-assisted, unvalidated, and not automatic in `$lolla`. PR102 brings the
specialist-output pilot count to three one-case pilots. It still does not prove
that the contracts are final, that broader batches are safe, that Lolla
improved the decision, or that agents may act.

PR103 now closes the one-case pilot phase. PR104 packages PR97, PR100, and
PR102 into a future-human-review intake packet with blank correction fields.
It creates no new specialist outputs, reads no new local-private packet
content, and leaves the correct next state as pause until human review capacity
returns.
```

Documentation alignment note:

```text
The GitHub front door now separates normal Lolla runtime use from the offline
Product Delta eval lane. README.md points to docs/evals/README.md, which maps
what the eval lane studies, how to run the safe read-only tools, what to
inspect, and what not to infer. This is documentation alignment only: it adds
no new evidence, runtime behavior, model calls, archive mutation, scoring,
automatic labels, or agent approval.
```

Decision Work Receipt standing note:

```text
docs/conversation-understanding/decision-work-receipt-prd-v0.md defines the
work-trail wrapper product direction: final AI outputs are cheap, but the
process evidence behind them should be inspectable.

PR105 through PR111 built and reviewed the sparse offline Decision Work
Receipt: schema, source inventory, deterministic process map, challenge
coverage, composed exporter, fixture review, and decision gate. The selected
decision remains Outcome A: keep the Work Receipt as a sparse wrapper, not a
parallel semantic interpretation system.

PR112 reopens the lane only for a narrow concrete bridge found by real-run
smoke testing. Completed archives can show good challenged-process evidence
while Decision Trail/Product Delta summaries stay not_supplied because those
reports are usually generated outside archive run folders. The receipt CLI can
now accept --decision-trail-report and --product-delta-report paths, record
sanitized source metadata, and raise review readiness without copying report
content, local paths, or semantic conclusions.

The Decision Work Receipt Debug Summary renderer is an internal maintainer
layer over those artifacts. It turns a receipt plus optional Decision Trail
report into a Markdown packet for status, missingness, and custody inspection.
The checked-in launch-public-enterprise-beta example shows the current debug
shape: multi-turn process evidence, visible challenge surfaces, linked Decision
Trail field status, private/missing distinctions, explicit non-claims, and a
clear list of semantic fields still requiring LLM or human interpretation. It
also preserves metadata awkwardness instead of smoothing it away, such as
inconsistent turn count totals.

This is not the customer-facing decision story. The user-facing target is now
the Decision Work Brief: a plain-language artifact that explains what decision
was being made, what Lolla pressed on, what changed, what remains unresolved,
and what the audit must not claim. See
docs/conversation-understanding/decision-work-brief-prd-v0.md. That PRD now
nests the product claim into the existing codebase and lays out PR113-PR131:
schema, local-private packet builder, Codex-assisted draft pilot, Markdown
renderer, usefulness gate, second tiny case pilot, small pattern review, and
third diversity case pilot, three-case pattern review, plain-language renderer
patch, local-private adequacy, conversation interpretation gap mapping,
contract definition, contract packet review, the offline interpretation packet
builder, and the first tiny offline interpretation read.

PR114 implements the schema/docs/test contract for that target:
docs/conversation-understanding/decision-work-brief-v0.json and
docs/conversation-understanding/decision-work-brief-schema-v0.md now define
`lolla.decision_work_brief.v0` as a user-facing, evidence-backed, lower-claim
brief shape. The schema requires the decision-story sections, source refs,
source status, interpreter, uncertainty, human-validation state, custody flags,
and explicit non-claims. It remains a contract only: no generator, packet
builder, renderer, runtime integration, model calls, archive mutation, or
semantic inference.

PR115 through PR154 keep the brief lane offline and downstream. Maintainers can
prepare metadata-only packets from completed runs, inspect provisional
Codex-assisted checked-in-safe drafts, render existing brief JSON to Markdown,
and now inspect three tiny cases: `ceo-remove-founding-cofounder`,
`launch-public-enterprise-beta`, and `deploy-assisted-intake-routing` rendered
with plain-language headings. PR124 confirms the surface is readable enough for
source-depth comparison. PR125 completes one launch-beta local-private shadow
review and records `adequate_but_missing_private_nuance`. PR126 chooses
`run_more_local_private_adequacy_checks`. PR127-PR129 then map the richer
conversation interpretation gap, define a future target contract, and decide
that the current source/status scaffolding is ready for an offline
interpretation packet. PR130 builds that packet shape without filling semantic
fields. PR131 then runs one tiny provisional read against a bounded launch-beta
packet and keeps several fields partial or insufficient-context. PR132 repeats
that read on the deploy-assisted-intake-routing case, and PR133 formalizes the
shared read schema before any additional reads or brief-enrichment work. PR134
compares the two reads and decides the next useful test is not another backend
read but one narrow Decision Work Brief enrichment test.

PR135 through PR145 then test, review, formalize, build, patch, close, and
package the offline enrichment surface. PR146 returns to the source-depth risk
by checking the remaining two preferred package cases against local-private
context in read-only mode. It records no private content and finds no major
contradiction, but keeps starting-direction overlap, lost-value severity,
stakeholder nuance, and legal or compliance constraints as human-review risks.
PR147 tries to start the third builder case on the cofounder decision and stops
cleanly when it finds the missing prerequisite: a builder-compatible cofounder
interpretation read. The recommended next slice is a bounded PR147A third tiny
offline interpretation read before any cofounder builder output. PR147A adds
that read, does not create a builder output, and recommends a separate PR148
builder-output slice. PR148 then creates the cofounder builder-enriched output,
finds the action consequence readable but still source-depth-sensitive, and
recommends PR149 Decision Work Brief Three Builder Case Pattern Review v0.
PR149 compares the three builder-generated enriched briefs and recommends
PR150 Decision Work Brief Human Review Intake Plan v0, not another builder
case, builder patch, local-private check, or runtime plan. PR150 turns that
gate into a human-review intake plan over the three builder-generated enriched
briefs. It defines reviewer questions, case review forms, source-depth checks,
overtrust checks, private-context questions, stop conditions, and allowed
future human-review outcomes, while preserving `human_validated: false`,
`human_review_completed: false`, `product_proof: false`, `model_calls: 0`, and
no runtime, skill, archive, scoring, or agent-action authority. PR150
recommends PR151 Decision Work Brief Human Review Pilot v0. PR151 creates the
pilot scaffold for that step: reviewer instructions, a three-case packet scope,
a blank response template, stop conditions, allowed pilot outcomes, and a
`ready_to_run_human_review` gate. It does not fill any human-review answers,
complete human validation, score answer quality, authorize agent action, or
attach the brief to runtime. PR151 recommends PR152 Decision Work Brief Human
Review Pilot Readiness Gate v0. PR152 adds the readiness gate for that pilot:
scaffold and template exist, exactly three enriched briefs are in scope, the
template is still blank, and the correct next step is
`collect_real_human_review_response`, not Codex-filled review or runtime use.
PR153 records the awaiting-response state: no real human response exists yet,
so the current gate is `pause_until_human_review_capacity` and the next
unblocked evidence step is a real human-filled response template. PR154 then
defines the automatic triage contract: LLM interpretation may own messy
semantic routing judgments, deterministic code must preserve custody/source
refs/missingness/privacy/non-claims, and human review calibrates the router
rather than becoming the per-run operating layer.

This remains offline/eval-side machinery. It does not run $lolla, invoke the
skill, call providers, mutate archives, change prompts, touch SKILL.md, score
answer quality, create automatic labels, authorize agent action, recommend
runtime integration, or treat three clean briefs as product proof.
```

Decision Trail framing note:

```text
docs/lolla-decision-trail-web-page-v0.md gives a customer-facing draft for the
answer-plus-process value proposition. It explains that serious AI advice needs
the revised answer plus the process trail: what conversation produced it, what
was challenged, what changed, what remains missing, and what must not be
overclaimed.

docs/conversation-understanding/decision-trail-readiness-audit-v0.md is the
internal counterweight. It says the direction is right, but the first-class
Decision Trail report is not live yet. Current Lolla captures and preserves
important primitives, while live extraction is still too compact for the full
decision-story surface. The recommended next product-shaped move is a
docs/schema-only Decision Trail report PRD before exporter work or runtime
integration.

docs/conversation-understanding/decision-trail-pr86-pr89-prd-v0.md turns that
audit into a staged PR86-PR89 sequence: report schema, read-only exporter,
fixture review, and interpretation-gap decision. Its core implementation rule
is that LLMs handle messy conversation interpretation while deterministic code
preserves custody, source refs, field status, missingness, validation, and
non-claims.

docs/conversation-understanding/decision-trail-pr86-goal-prompt-v0.md is a
ready-to-paste `/goal` handoff for a fresh coder session to implement PR86
only. It deliberately stops before exporter code, runtime integration, model
calls, archive mutation, or specialist enrichment.

docs/conversation-understanding/decision-trail-report-prd-v0.md and
docs/conversation-understanding/decision-trail-report-v0.json now define PR86's
`lolla.decision_trail_report.v0` contract. The report is designed as an offline
reader/reporting surface over completed artifacts. It preserves source refs,
custody, status, redaction/missingness distinctions, field ownership, optional
future trace compatibility, and non-claims without implementing the PR87
exporter or changing runtime behavior.

docs/conversation-understanding/decision-trail-pr87-goal-prompt-v0.md is the
ready-to-paste `/goal` handoff that scoped PR87 Decision Trail Read-Only
Exporter v0. That handoff kept the exporter read-only and deterministic, with
no `$lolla`, skill invocation, provider calls, archive mutation, runtime
changes, or semantic inference from messy prose.

engine/system_b/decision_trail_report.py and
scripts/evals/build_decision_trail_report.py now implement PR87's checked-in
safe exporter. The exporter reads only structured JSON artifacts by default,
records redaction/private-availability for raw/private artifacts without
reading them, emits sparse `lolla.decision_trail_report.v0` JSON to an
explicit output path outside the run directory, and preserves messy semantic
fields as missing or requiring interpretation instead of guessing.

docs/conversation-understanding/decision-trail-readonly-exporter-v0.md records
the implementation and points the next slice to PR88 fixture review.

docs/conversation-understanding/decision-trail-pr88-goal-prompt-v0.md is the
ready-to-paste `/goal` handoff for PR88 Decision Trail Fixture Review v0. It
keeps PR88 as an offline review of generated reports for usefulness,
missingness, readability, and overtrust risk, with no runtime invocation,
provider calls, archive mutation, exporter rewrite, scoring, or automatic
labels.

docs/conversation-understanding/decision-trail-export-fixture-review-v0.md and
reviews/codex-assisted/decision-trail-fixture-review-v0/review.json now record
PR88's safe-fixture-only review. The review found the PR87 report useful as a
custody and missingness shell, but too sparse for the full Decision Trail
product without later bounded interpretation. No local-private shadow review
was run, so PR89 must treat this as safe-fixture-only evidence.

docs/conversation-understanding/decision-trail-interpretation-gap-decision-v0.md
now records PR89's decision gate. PR89 selects narrow offline LLM specialist
enrichment as the next path. It keeps the deterministic Decision Trail shell,
rejects runtime integration and broad IR work for now, and recommends PR90
Decision Trail Interpretation Specialist Contracts v0.

docs/conversation-understanding/decision-trail-pr90-goal-prompt-v0.md is the
ready-to-paste `/goal` handoff for PR90. It scopes the next slice to
docs/schema contracts for four narrow offline Decision Trail interpretation
specialists: conversation shape, likely actions, friction/lost value, and
conservative fan-in. It explicitly forbids packet builders, model calls,
specialist review outputs, runtime integration, scoring, judging, automatic
labels, and archive mutation.

docs/conversation-understanding/decision-trail-specialist-contracts-v0.md and
docs/conversation-understanding/decision-trail-specialist-contracts-v0.json now
define PR90's contract surface. PR90 adds docs/schema contracts and focused
tests for four narrow offline Decision Trail specialist roles:
conversation-shape, likely-action, friction/lost-value, and conservative
fan-in. It prepares PR91 packet building without running specialists, calling
models, integrating runtime, mutating archives, scoring, judging, or creating
automatic labels.

docs/conversation-understanding/decision-trail-specialist-packet-builder-v0.md
and reviews/codex-assisted/decision-trail-specialist-packets-v0/packets.json
now record PR91's read-only packetization surface. PR91 adds deterministic
packet-building code, a CLI, and focused tests for shaping PR88 fixture-review
context into checked-in-safe input packets for the four PR90 specialist
contracts. It does not run specialists, call models, execute fan-in, integrate
runtime, mutate archives, score, judge, or create automatic labels.

docs/conversation-understanding/decision-trail-specialist-trap-set-v0.md and
docs/conversation-understanding/decision-trail-specialist-trap-set-v0.json now
record PR92's checked-in-safe trap fixture layer. PR92 adds ten trap families
for testing whether future Decision Trail specialist passes resist
over-inference, overtrust from clean custody, likely-action guessing, lost-value
blindness, local-private context collapse, and fan-in smoothing. It does not
run specialists, call models, execute fan-in, integrate runtime, mutate
archives, score, judge, or create automatic labels.

docs/conversation-understanding/decision-trail-specialist-dry-run-v0.md and
reviews/codex-assisted/decision-trail-specialist-dry-run-v0/review.json now
record PR93's Codex-assisted provisional dry run over PR92 traps and the tiny
PR91 packet surface. PR93 checks whether the specialist setup resists obvious
over-inference and overtrust before filling messy interpretation fields. It
creates no contract-conforming specialist outputs, executes no fan-in, calls no
models, integrates no runtime, mutates no archives, scores nothing, judges
nothing, and creates no automatic labels.

docs/conversation-understanding/decision-trail-specialist-path-decision-v0.md
now records PR94's docs-only path decision. PR94 selects PR95 Decision Trail
Local-Private Packet Mode v0 as the next slice. It rejects a broader
checked-in-safe specialist batch for now because PR88, PR91, and PR93 already
show that current safe fixtures are too thin. It also keeps runtime
integration, broad conversation IR, scoring, judging, automatic labels, and
agent authorization rejected.

docs/conversation-understanding/decision-trail-local-private-packet-mode-v0.md,
engine/system_b/decision_trail_specialist_packets.py, and
scripts/evals/build_decision_trail_specialist_packets.py now implement PR95's
explicit local-private packet mode. PR95 lets an operator build local-only
Decision Trail specialist packets from selected completed run directories,
with required `--mode local_private_mode`, required explicit output path,
output rejection inside the repo or selected run directory, metadata-only and
include-text policies, a local artifact read manifest, truthful private-content
metadata, and unsafe-for-commit marking. Post-review alignment clarified that
the PR88 fixture-review input is lineage-only in local-private mode, not a
semantic source; raw transcript/revised/memo booleans now describe actual
included artifacts; local-private fixture/schema inputs must be repo-local to
avoid path leaks; and the builder docstring now reflects the real
checked-in-safe versus local-private read behavior. PR95 still creates no
specialist outputs, calls no models, invokes no runtime, mutates no archives,
scores nothing, judges nothing, and creates no automatic labels.

docs/conversation-understanding/decision-trail-local-private-packet-smoke-review-v0.md
and
reviews/codex-assisted/decision-trail-local-private-packet-smoke-review-v0/review.json
now record PR96's local smoke/review. PR96 generated metadata-only packets for
two real completed local runs and a local-only include-text packet for one real
run, plus a synthetic include-text guardrail output. The real include-text
output was deleted after structural summary capture. The checked-in review
records source availability, packet roles, guardrails, privacy posture, and
thinness without raw/private content, specialist outputs, fan-in, model calls,
runtime invocation, archive mutation, scoring, judging, or automatic labels.

docs/conversation-understanding/decision-trail-local-private-specialist-output-pilot-v0.md
and
reviews/codex-assisted/decision-trail-local-private-specialist-output-pilot-v0/review.json
now record PR97's tiny local-private specialist-output pilot. PR97 used one
operator-selected completed run and a local-only include-text packet to fill
the four PR90 specialist roles by checked-in summary only. It shows the
Decision Trail can carry more concrete candidate interpretation when private
source access is available, but it remains one-case, Codex-assisted,
human-unvalidated, unsafe to broaden without review, and outside runtime.

docs/conversation-understanding/decision-trail-specialist-output-pilot-review-v0.md
and
reviews/codex-assisted/decision-trail-specialist-output-pilot-review-v0/review.json
now record PR98's review of that pilot. PR98 keeps the useful signal but blocks
broader use until PR90 contracts and PR95 packet metadata are patched for
vanilla overlap, lost-value severity, assistant-influence source status,
truncation/source-scope impact, fan-in downgrade triggers, and local-private
retention/deletion status.
```

Current product state:

> Lolla now has the local reasoning-audit harness skeleton, deterministic run
> custody, evaluation receipts, review-corpus scaffolding, extraction adequacy
> reporting, semantic coverage reporting, offline specialist probe evidence,
> a clean six-case complex conversation baseline, and a first human/product
> review seed over those six complex runs. The risk-mode track now has policy,
> fixtures, fixture review, a pre-code implementation plan, contract-lock tests,
> deterministic evaluation-artifact clarity for high-stakes reliance, and a
> review-corpus surface and manifest counts for that reliance caveat. PR45 adds
> a compact anti-drift handoff so fresh sessions do not confuse fixture-backed
> readiness with real high-stakes archive evidence. PR46 adds the docs-only
> approval and custody plan for creating high-stakes evidence later without
> running cases now. PR47 adds paraphrase-only fixtures so reviewers can test
> high-stakes expectations before real runs exist. PR48 adds the read-only
> manifest analyzer that says whether a review-corpus manifest actually contains
> high-stakes reliance-present archive evidence. PR49 through PR54 complete
> the v0 user-values/priorities worksheet lane as a human-owned review surface
> and pause it before extraction, runtime integration, automatic labels, memory,
> or judging. PR55 lands the Semantica-inspired accountability PRD as a
> docs-only plan: borrow accountability primitives, not Semantica's graph,
> memory, policy, compliance, judge, or scoring platform. PR56 adds the
> docs-only Lolla Doctor / Preflight plan for a future read-only, local,
> deterministic, model-call-free readiness command. PR57 implements that
> command as a read-only local CLI without running `$lolla`, calling models,
> mutating archives, or approving high-stakes use. PR58 designs
> `lolla.audit_decision_record.v0` as a paraphrase-only accountability
> projection over existing artifacts and PR31 labels without implementing an
> exporter, judge, score, memory layer, or conversation-understanding IR. PR59
> reviews six paraphrase-only decision-record fixtures and finds the shape
> understandable enough for a future exporter design prototype, with no
> exporter, runtime integration, automatic labels, scoring, or judge. PR60
> designs `lolla.provenance_map.v0` as a local artifact-lineage map without
> implementing an exporter, archive reading, runtime integration, RDF/W3C
> compliance, graph DB, memory, labels, scoring, or judge. PR61 designs
> `lolla.review_conflict_register.v0` as a human-review-owned conflict surface
> without conflict resolution, severity automation, policy enforcement,
> labels, scoring, or judge. PR62 designs `lolla.case_graph.v0` as a future
> run-local case graph export/view shape without implementing an exporter,
> reading archives, adding graph DB, adding memory, adding GraphRAG, adding
> entity resolution, labels, scoring, or judge. PR63 adds three
> paraphrase-only accountability-view fixture bundles across audit decision
> record, provenance map, review conflict register, and case graph views, with
> no exporter, archive reading, runtime behavior, labels, scoring, or judge.
> PR64 reviews all three bundles, marks all three pass as useful inspection
> evidence, recommends only `audit_decision_record` for a later exporter-design
> decision, keeps provenance and conflict-register views in more-fixture status,
> and holds case graph before implementation.
> PR65 chooses outcome A as a docs-only decision: recommend a future PR66 Audit
> Decision Record Read-Only Exporter v0. PR65 does not implement the exporter,
> start PR66, read archives, call models, mutate archives, add labels, score
> answers, or change runtime behavior. PR66 implements that exporter as a
> read-only local CLI/helper that emits `lolla.audit_decision_record.v0` from
> structured/custody-safe run artifacts to an explicit external output path. It
> refuses output inside the run directory, keeps raw transcript/memo/
> revised-answer/provider/private content out, preserves `model_calls: 0` and
> `archive_mutated: false`, and does not infer labels, score advice, approve
> recommendations, or change runtime behavior. PR67 reviews six exporter smoke
> records from four existing reviewed archives and two fixture-backed temp runs.
> It finds the records useful, custody-safe, and clear about limitations, while
> recommending PR68 schema/exporter refinement before archive integration or
> automatic generation because empty PR31 buckets are only partly clear as
> "not supplied / not inferred" non-claims. PR68 refines the same
> `lolla.audit_decision_record.v0` schema and exporter output with
> `actionable_deltas.population_policy`, per-bucket status, nested buckets, and
> semantic-field status/empty-meaning metadata. It keeps the exporter
> deterministic, read-only, model-call-free, archive-mutation-free, and outside
> runtime integration, scoring, judging, automatic labels, and prose inference.
> PR69 re-runs the smoke review against refined PR68 output. Seven reviewed
> records pass: four existing reviewed archive exports, two fixture-backed
> temp-run exports, and one optional review-json-supplied fixture. Empty PR31
> bucket clarity improves to seven `clear_non_claim`, semantic empty-field
> clarity is seven `clear_non_claim`, raw content safety remains safe, and no
> reviewer needs docs to avoid the basic non-claim misread.
> PR70 closes the audit/accountability machinery lane as done enough for now.
> It does not add archive integration or new machinery. The next phase is
> Product Delta Evidence: prove whether Lolla materially improves actual
> strong-model conversations before action.
> PR71-PR74 add the lower-claim Codex-assisted provisional scaffold for that
> phase: thesis, protocol/schema, eight-case dry run, and provisional failure
> taxonomy. These are not human review, ground truth, judge calibration data,
> product proof, or agent approval.
> PR75 turns that scaffold into a runnable read-only eval lane over existing
> cases. It finds 12 ready cases, one private-content-only partial case, and
> one degraded-run block, and emits PR72-shaped shells without semantic product
> judgment.
> PR76 fills the 12 ready shells with Codex-assisted provisional semantic
> reads. The distribution is intentionally mixed: 6 material improvement
> candidates, 4 partial improvement candidates, 1 no-material-change candidate,
> and 1 inconclusive case. These are not human labels, ground truth, judge
> calibration data, product proof, or agent approval.
> PR77 summarizes PR75 and PR76 as one provisional state-of-evidence report:
> readiness, candidate distribution, recurring structural deltas, lost-value
> risks, interpretation-adequacy concerns, human-review priorities, and
> falsification tests. It is still not human validation, product proof, judge
> calibration data, scoring, automatic labels, runtime integration, or agent
> approval.
> PR78 adds deterministic Product Delta evidence-boundary lint. It blocks
> unsafe lower-claim metadata, authority/scoring fields, taxonomy score drift,
> missing PR72 review-case boundary fields, and privacy markers in supplied
> artifacts. It is still not semantic judgment, a judge, a score, human
> validation, product proof, runtime integration, archive mutation, or agent
> approval.
> PR79 defines the context-engineered provisional specialist-review
> architecture. It rejects a broad judge, decomposes future LLM-assisted review
> into bounded specialist reads, requires deterministic packetization,
> typed outputs, PR78 lint, disagreement-preserving fan-in, and later human
> validation. It is docs/design only: no schemas, packet builder, model calls,
> review run, runtime integration, archive mutation, scoring, automatic labels,
> or agent approval.
> PR80 defines the typed specialist-review contracts for that architecture.
> It adds a combined JSON schema and guide for conversation interpretation,
> vanilla likely action, Lolla likely action, structural delta, useful/noisy
> friction and lost value, interpretation adequacy, advisory overclaim, and
> conservative fan-in reads. It is docs/schema/tests only: no packet builder,
> generated review output, model calls, review batch, fan-in execution, runtime
> integration, archive mutation, scoring, automatic labels, or agent approval.
> PR81 implements the deterministic packetization stage for those contracts.
> It adds a read-only module/CLI that builds checked-in-safe per-specialist
> input packets from existing Product Delta artifacts, plus a compact two-case
> packet fixture. It does not fill specialist answers, call models, mutate
> archives, change runtime, score advice, create labels, or authorize agent
> action.
> PR82 adds a small provisional reviewer trap set before any real specialist
> batch. The ten paraphrase-only traps test whether future specialist-review
> setup resists thin context, length bias, caution without leverage, repeated
> vanilla gates, lost options, buried ambition, assistant-influence blindness,
> disagreement smoothing, clean-artifact authority leakage, and hardened
> provisional language. It is contract expectation material, not human labels,
> product proof, judge calibration data, scoring, automatic labels, runtime
> integration, or agent approval.
> PR83 runs the first Codex-assisted specialist-review batch against the PR82
> traps and the two-case PR81 packet fixture. It records eight of ten trap
> behaviors as met and two as partly met, fills eight specialist reads for each
> real case, preserves lost-value and interpretation-adequacy concerns in both
> cases, and downgrades `accept-operations-role-startup` from PR76's material
> candidate to a partial candidate. It is review-discipline evidence, not
> human validation, product proof, judge calibration data, scoring, automatic
> labels, runtime integration, or agent approval.

What this means in plain terms:

- Normal `$lolla` is still the product surface.
- The current harness can capture a serious conversation, extract decision
  structure, run the audit, produce a revised answer and memo, archive the run,
  emit `agent_result.json`, `evaluation.json`, `reasoning_trace.json`, and
  expose deterministic health/custody signals.
- The six complex test conversations all completed with full 12-user /
  12-assistant capture, healthy run state, clean provider-boundary state, clean
  product output, zero quote-fabrication, and `caller_action:
  use_revised_answer`.
- The revised answers were not just smoother. They repeatedly changed action
  shape: added gates, narrowed claims, corrected over-clean frames, exposed
  capacity and stakeholder constraints, and rejected checklist theater.
- Risk-mode implementation is test-locked at the contract level,
  `evaluation.json` surfaces high-stakes reliance caveats explicitly, and
  review-corpus records now expose those caveats as compact
  `risk_mode_reliance` metadata. PR43 verified the surface with fixtures after
  a read-only local export found zero real high-stakes reliance-present archive
  records. PR44 now adds manifest-level aggregate visibility for that absence
  without runtime enforcement.
- The current real local review-corpus evidence is 80 records, all
  `risk_mode: standard`; `risk_mode_reliance_present_counts` is `false: 80` and
  `true: 0`.
- PR46 defines allowed, excluded, and domain-review-required high-stakes
  scenario categories for a future approved seed, but it does not create any
  real high-stakes records.
- PR47 adds six paraphrase-only high-stakes evidence fixtures; they are not
  archive outcome evidence, human labels, judge calibration truth, or runtime
  enforcement.
- PR48 reads only review-corpus manifest JSON and reports
  `no_high_stakes_reliance_evidence`, `has_high_stakes_reliance_evidence`, or
  `insufficient_manifest_fields`; it does not read raw archives, call models,
  judge answer quality, or approve real high-stakes runs.
- PR49 through PR54 complete the v0 user-values/priorities worksheet lane as a
  human-owned review surface: plan, fixtures, fixture review, blank export,
  human pilot, and pilot review. That lane is now paused before extraction,
  runtime integration, automatic labels, memory, or judging.
- PR55 records the Semantica-inspired accountability plan. It preserves a queue
  for local decision records, provenance maps, review conflict registers,
  doctor/preflight, and run-local case graph views while explicitly rejecting
  graph DBs, embeddings, chunking, global memory, policy engines, compliance
  platforms, generic agent safety layers, domain authority, LLM judges,
  answer-quality scoring, automatic labels, and runtime behavior changes.
- PR56 records the Lolla Doctor / Preflight plan. It defines a future
  read-only doctor report for local runtime discovery, archive-root discovery,
  helper script availability, provider/cost readiness, review-manifest
  visibility, high-stakes evidence absence/presence, output-path safety, and
  privacy-safe reporting without adding the CLI.
- PR57 implements the smallest read-only doctor CLI and JSON contract. It
  checks local runtime wiring, archive-root shape, helper availability,
  provider credential presence, cost-table readiness, optional review-corpus
  manifest counts, high-stakes evidence visibility, output-path safety,
  repo/runtime boundary state, and privacy flags without running `$lolla`,
  calling models, or mutating archives.
- PR58 designs `lolla.audit_decision_record.v0` as a local accountability
  projection over existing artifacts. It summarizes the audited decision,
  original/revised recommendation shape, PR31 actionable deltas, unresolved
  conflicts/questions, source artifact refs, review refs, custody flags, and
  limitations without copying raw content or judging answer quality.
- PR59 creates six paraphrase-only audit decision record fixtures and a
  human-owned fixture review. All six pass, PR31 mapping is useful in all six,
  reviewer use without raw content is `yes` in all six, and the review marks
  the shape ready for a future read-only exporter design prototype with
  caveats.
- PR60 designs `lolla.provenance_map.v0` as a local artifact-lineage map across
  run and review artifacts. It borrows entity/activity/agent vocabulary without
  claiming PROV-O/W3C compliance, requiring RDF, adding graph DB, adding memory,
  implementing an exporter, reading archives, or judging answer quality.
- PR61 designs `lolla.review_conflict_register.v0` as a human-review-owned
  register of unresolved values, stakeholder, action, reliance, artifact,
  provenance, and review conflicts. It preserves conflicts for review without
  resolving them, scoring severity into actions, enforcing policy, or creating
  labels.
- PR62 designs `lolla.case_graph.v0` as a future run-local case graph
  export/view shape. It shows how decision, delta, artifact, provenance,
  conflict, doctor, and review nodes can relate without implementing an
  exporter, reading archives, adding graph DB, memory, GraphRAG, entity
  resolution, labels, scoring, or judging.
- PR63 creates three accountability-view fixture bundles from checked-in
  reviewed summaries. Each bundle includes audit decision record, provenance
  map, review conflict register, and case graph views, but remains
  paraphrase-only docs/JSON with placeholder hashes and relative artifact refs.

Primary evidence notes to read first in a fresh session:

- `docs/conversation-understanding/complex-conversation-baseline-v0.md`
- `docs/evals/README.md`
- `docs/evals/complex-baseline-human-review-v0.md`
- `docs/evals/evaluation-flywheel-action-plan-v0.md`
- `docs/evals/current-system-capabilities-v0.md`
- `docs/evals/product-delta-evidence-and-interpretation-adequacy-v0.md`
- `docs/evals/product-delta-evidence-thesis-v0.md`
- `docs/evals/vanilla-vs-lolla-provisional-review-protocol-v0.md`
- `docs/evals/vanilla-vs-lolla-provisional-review-v0.json`
- `docs/evals/codex-assisted-paired-review-dry-run-v0.md`
- `reviews/codex-assisted/paired-review-dry-run-v0/review.json`
- `docs/evals/provisional-product-delta-failure-taxonomy-v0.md`
- `docs/evals/provisional-product-delta-failure-taxonomy-v0.json`
- `docs/evals/product-delta-seed-cases-v0.json`
- `docs/evals/product-delta-eval-readiness-and-provisional-run-v0.md`
- `reviews/codex-assisted/product-delta-provisional-run-v0/review.json`
- `docs/evals/codex-assisted-product-delta-batch-v0.md`
- `reviews/codex-assisted/product-delta-batch-v0/review.json`
- `docs/evals/product-delta-provisional-report-v0.md`
- `docs/evals/product-delta-evidence-boundary-lint-v0.md`
- `docs/evals/context-engineered-provisional-review-architecture-v0.md`
- `docs/evals/product-delta-specialist-review-contracts-v0.md`
- `docs/evals/product-delta-specialist-review-contracts-v0.json`
- `docs/evals/product-delta-specialist-packet-builder-v0.md`
- `reviews/codex-assisted/product-delta-specialist-packets-v0/packets.json`
- `engine/system_b/product_delta_boundary_lint.py`
- `scripts/evals/lint_product_delta_evidence.py`
- `tests/test_product_delta_boundary_lint.py`
- `tests/test_product_delta_specialist_contracts.py`
- `engine/system_b/product_delta_specialist_packets.py`
- `scripts/evals/build_product_delta_specialist_packets.py`
- `tests/test_product_delta_specialist_packets.py`
- `tests/test_product_delta_batch_fixture.py`
- `engine/system_b/product_delta_readiness.py`
- `scripts/evals/build_product_delta_provisional_review.py`
- `tests/test_product_delta_readiness.py`
- `docs/evals/current-state-anti-drift-handoff-v0.md`
- `docs/evals/high-stakes-evidence-seed-plan-v0.md`
- `docs/evals/high-stakes-evidence-fixtures-v0.md`
- `docs/evals/high-stakes-evidence-fixtures-v0.json`
- `docs/evals/review-corpus-evidence-readiness-v0.md`
- `docs/evals/user-values-priorities-worksheet-plan-v0.md`
- `docs/evals/user-values-priorities-worksheet-fixtures-v0.md`
- `docs/evals/user-values-priorities-worksheet-fixture-review-v0.md`
- `docs/evals/user-values-priorities-blank-worksheet-export-v0.md`
- `docs/evals/user-values-priorities-worksheet-human-pilot-v0.md`
- `docs/evals/user-values-priorities-pilot-review-v0.md`
- `docs/conversation-understanding/semantica-inspired-accountability-prd-v0.md`
- `docs/conversation-understanding/audit-decision-record-v0.md`
- `docs/conversation-understanding/audit-decision-record-v0.json`
- `docs/evals/audit-decision-record-fixtures-v0.md`
- `docs/evals/audit-decision-record-fixtures-v0.json`
- `reviews/human/audit-decision-record-fixture-review-v0/review.json`
- `docs/conversation-understanding/provenance-map-v0.md`
- `docs/conversation-understanding/provenance-map-v0.json`
- `docs/evals/review-conflict-register-v0.md`
- `docs/evals/review-conflict-register-v0.json`
- `docs/conversation-understanding/case-graph-export-v0.md`
- `docs/conversation-understanding/case-graph-export-v0.json`
- `docs/evals/accountability-view-fixtures-v0.md`
- `docs/evals/accountability-view-fixtures-v0.json`
- `docs/evals/accountability-view-fixture-review-v0.md`
- `reviews/human/accountability-view-fixture-review-v0/review.json`
- `docs/evals/accountability-implementation-decision-gate-v0.md`
- `docs/evals/lolla-doctor-preflight-plan-v0.md`
- `docs/evals/lolla-doctor-readonly-cli-v0.md`
- `engine/system_b/lolla_doctor.py`
- `scripts/lolla_doctor.py`
- `tests/test_lolla_doctor.py`
- `reviews/human/user-values-priorities-worksheet-pilot-v0/worksheets.json`
- `reviews/human/user-values-priorities-pilot-review-v0/review.json`
- `engine/system_b/review_corpus_evidence_readiness.py`
- `scripts/analyze_review_corpus_evidence_readiness.py`
- `tests/test_review_corpus_evidence_readiness.py`
- `docs/conversation-understanding/broader-specialist-evidence-gate-v0.md`
- `docs/conversation-understanding/specialist-runtime-design-without-integration-v0.md`
- `docs/conversation-understanding/research-and-design-v0.md`
- `docs/conversation-understanding/decision-trail-report-prd-v0.md`
- `docs/conversation-understanding/decision-trail-report-v0.json`
- `docs/conversation-understanding/decision-trail-readonly-exporter-v0.md`
- `engine/system_b/decision_trail_report.py`
- `scripts/evals/build_decision_trail_report.py`
- `tests/test_decision_trail_report.py`
- `docs/lolla-evaluation-methodology.md`
- `docs/lolla-reasoning-audit-harness-prd.md`
- `docs/evals/risk-mode-implementation-plan-v0.md`
- `tests/test_risk_mode_contract.py`
- `tests/test_evaluation_artifact.py`
- `tests/test_review_corpus_export.py`

Current stop rule:

> Do not run more random smokes by default. We have enough complex-run evidence
> to pause and turn toward evaluation.

Latest completed slice:

```text
PR138 Decision Work Brief Enriched Pattern Review v0
```

Result:

- lands `docs/conversation-understanding/decision-work-brief-enriched-pattern-review-v0.md`;
- lands `reviews/codex-assisted/decision-work-brief-enriched-pattern-review-v0/review.json`;
- lands `tests/test_decision_work_brief_enriched_pattern_review.py`;
- compares the two enriched briefs from PR135 and PR137;
- finds the stable enrichment fields are decision question, likely starting
  direction with uncertainty, action consequence, thresholds, evidence gates,
  useful friction as descriptive language, and non-proof boundaries;
- keeps live options, abandoned or rejected options, noisy friction, lost
  value, values, stakeholder obligations, and assistant influence evidence-only
  or unresolved;
- chooses `proceed_to_enrichment_rules_contract`;
- explicitly does not implement PR139;
- still creates no runtime extractor, prompt change, live skill change, model
  call, archive mutation, graph/memory system, product proof, human validation,
  broad judge, customer marketing copy, or agent action authorization.

Recommended next slice: PR139 Decision Work Brief Enrichment Rules Contract v0.

Previous Decision Work Brief enrichment sequence:

- PR135 Decision Work Brief Interpretation Enrichment Test v0;
- lands `docs/conversation-understanding/decision-work-brief-enriched-launch-public-enterprise-beta-v0.md`;
- lands `docs/conversation-understanding/decision-work-brief-interpretation-enrichment-test-v0.md`;
- lands `reviews/codex-assisted/decision-work-brief-interpretation-enrichment-test-v0/review.json`;
- lands `tests/test_decision_work_brief_interpretation_enrichment_test.py`;
- adds one separate enriched launch-beta example and gates to
  `proceed_to_original_vs_enriched_review`;
- PR136 Original vs Enriched Brief Review v0 compares the original and enriched
  launch-beta briefs and gates to `proceed_to_second_enriched_brief_test`;
- PR137 Second Enriched Brief Test v0 adds one separate enriched
  intake-routing example and gates to `proceed_to_enriched_brief_pattern_review`;
- all three slices preserve checked-in-safe boundaries, non-claims, and original
  rendered examples.

Previous Decision Work conversation interpretation read comparison slice:

- PR134 Decision Work Conversation Interpretation Read Comparison v0;
- lands `docs/conversation-understanding/decision-work-conversation-interpretation-read-comparison-v0.md`;
- lands `reviews/codex-assisted/decision-work-conversation-interpretation-read-comparison-v0/review.json`;
- lands `tests/test_decision_work_conversation_interpretation_read_comparison.py`;
- compares PR131 and PR132 and chooses `proceed_to_brief_enrichment_test`.

Previous Decision Work conversation interpretation read-schema slice:

- PR133 Decision Work Conversation Interpretation Read Schema v0;
- lands `docs/conversation-understanding/decision-work-conversation-interpretation-read-schema-v0.md`;
- lands `docs/conversation-understanding/decision-work-conversation-interpretation-read-v0.json`;
- lands `tests/test_decision_work_conversation_interpretation_read_schema.py`;
- follows PR132's `define_interpretation_read_schema` gate;
- defines `lolla.decision_work_conversation_interpretation_read.v0` as the
  shared schema for future offline provisional interpretation reads;
- requires source refs, source status, uncertainty, privacy limits,
  human-review requirements, brief/agent-inspection handoff flags, and
  `must_not_be_used_as_quality_label` for every interpreted field;
- constrains custody to `human_validated: false`, `product_proof: false`,
  `model_calls: 0`, `runtime_invoked: false`, `skill_invoked: false`,
  `answer_quality_scored: false`, and `agent_action_authorized: false`;
- still creates no interpreter, runtime extractor, prompt change, live skill
  change, model call, archive mutation, graph/memory system, product proof,
  human validation, broad batch, customer marketing copy, or agent action
  authorization.

Previous Decision Work conversation interpretation second-read slice:

- PR132 Decision Work Conversation Interpretation Second Tiny Offline Read v0;
- lands `docs/conversation-understanding/decision-work-conversation-interpretation-second-tiny-offline-read-v0.md`;
- lands `reviews/codex-assisted/decision-work-conversation-interpretation-second-tiny-offline-read-v0/read.json`;
- lands `tests/test_decision_work_conversation_interpretation_second_tiny_offline_read.py`;
- follows PR131's `run_second_tiny_offline_read` gate;
- uses exactly one generated local PR130 checked-in-safe packet for
  `deploy-assisted-intake-routing/20260627T130339Z_4cd3cb`;
- checks in no source packet fixture, raw/private content, provider text,
  private ledger content, or local absolute paths;
- fills only the same tiny PR128 subset used in PR131 and leaves the rest
  uninterpreted;
- finds the same field shape works outside enterprise GTM, with action
  consequence, thresholds, evidence gates, useful/noisy friction, and non-proof
  boundaries useful, while starting direction, abandoned options, and lost value
  remain source-limited;
- selects `define_interpretation_read_schema`.

Previous Decision Work conversation interpretation first-read slice:

- PR131 Decision Work Conversation Interpretation Tiny Offline Read v0;
- lands `docs/conversation-understanding/decision-work-conversation-interpretation-tiny-offline-read-v0.md`;
- lands `reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json`;
- lands `tests/test_decision_work_conversation_interpretation_tiny_offline_read.py`;
- follows PR130's offline packet builder with exactly one generated local
  checked-in-safe packet for `launch-public-enterprise-beta`;
- checks in no source packet fixture, raw/private content, provider text,
  private ledger content, or local absolute paths;
- fills only the tiny PR128 subset selected for PR131 and leaves the rest
  uninterpreted;
- keeps every interpreted field source-bound, provisional, non-human-validated,
  and barred from quality-label use;
- records `lost_value` as insufficient context and keeps starting direction and
  abandoned options partial;
- selects `run_second_tiny_offline_read`;
- still creates no runtime extractor, prompt change, live skill change, model
  call, archive mutation, graph/memory system, answer-quality scoring, product
  proof, human validation, customer marketing copy, broad batch, or agent
  action authorization.

Previous Decision Work conversation interpretation offline packet slice:

- PR130 Decision Work Conversation Interpretation Offline Packet v0;
- lands `engine/system_b/decision_work_conversation_interpretation_packets.py`;
- lands `scripts/evals/build_decision_work_conversation_interpretation_packets.py`;
- lands `tests/test_decision_work_conversation_interpretation_packets.py`;
- lands `docs/conversation-understanding/decision-work-conversation-interpretation-offline-packet-v0.md`;
- follows PR129's `build_offline_interpretation_packet` recommendation;
- emits `lolla.decision_work_conversation_interpretation_packets.v0`;
- reuses the PR115 metadata-only packet builder to collect source refs and
  artifact status without copying raw/private text;
- maps the PR128 contract field groups into status-only field packets with
  future interpretation questions, required output refs, known limits, and the
  rule that every field is unfilled;
- supports `checked_in_safe` and `local_private_metadata` modes, both without
  include-text behavior;
- rejects output paths inside the source run directory;
- still creates no runtime extractor, prompt change, live skill change, model
  call, archive mutation, graph/memory system, answer-quality scoring, product
  proof, human validation, customer marketing copy, semantic interpretation, or
  agent action authorization.

Previous Decision Work conversation interpretation packet-review slice:

- PR129 Decision Work Conversation Interpretation Contract Packet Review v0;
- lands `docs/conversation-understanding/decision-work-conversation-interpretation-contract-packet-review-v0.md`;
- lands `reviews/codex-assisted/decision-work-conversation-interpretation-contract-packet-review-v0/review.json`;
- lands `tests/test_decision_work_conversation_interpretation_contract_packet_review.py`;
- follows the PR128 target contract;
- reviews the cofounder, launch-beta, and intake-routing cases against the
  current packet/artifact surface;
- confirms that current PR115 metadata-only packets can carry source
  availability, redaction/private status, missingness, custody flags, and
  section-level source refs;
- finds that the PR128 contract needs a field-grouped offline interpretation
  packet before any LLM/human interpretation or runtime extraction plan;
- selects `build_offline_interpretation_packet`;
- still creates no runtime extractor, prompt change, live skill change, model
  call, archive mutation, graph/memory system, answer-quality scoring, product
  proof, human validation, customer marketing copy, or agent action
  authorization.

Previous Decision Work conversation interpretation target-contract slice:

- PR128 Decision Work Conversation Interpretation Target Contract v0;
- lands `docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.md`;
- lands `docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json`;
- lands `tests/test_decision_work_conversation_interpretation_contract.py`;
- follows PR127's `define_interpretation_target_contract` gate;
- defines future conversation interpretation field groups for decision shape,
  options and paths, conversation process, provided context, stakeholders and
  values, constraints and unknowns, audit pressure and change, losses and
  overcorrection, evidence and custody, and brief/agent handoffs;
- separates LLM/human interpretation ownership from deterministic custody
  ownership;
- keeps the contract docs/schema/tests only;
- still creates no runtime extractor, prompt change, live skill change, model
  call, archive mutation, graph/memory system, answer-quality scoring, product
  proof, human validation, customer marketing copy, or agent action
  authorization.

Previous Decision Work conversation interpretation gap-map slice:

- PR127 Decision Work Brief Conversation Interpretation Gap Map v0;
- lands `docs/conversation-understanding/decision-work-brief-conversation-interpretation-gap-map-v0.md`;
- lands `reviews/codex-assisted/decision-work-brief-conversation-interpretation-gap-map-v0/review.json`;
- lands `tests/test_decision_work_brief_conversation_interpretation_gap_map.py`;
- reviews the cofounder, launch-beta, and intake-routing Decision Work Brief
  cases;
- maps which desired conversation fields are clear, partial, local-private
  only, not currently captured, LLM-interpretable, or human-review-dependent;
- selects `define_interpretation_target_contract`;
- still checks in no raw conversation, raw revised answer, raw memo, provider
  text, private ledgers, local absolute paths, secrets, runtime integration,
  product proof, human validation, answer-quality scoring, or agent action
  authorization.

Previous Decision Work expansion/runtime decision-gate slice:

- PR126 Decision Work Brief Expansion / Runtime Attachment Decision Gate v0;
- lands `docs/conversation-understanding/decision-work-brief-expansion-runtime-decision-gate-v0.md`;
- lands `reviews/codex-assisted/decision-work-brief-expansion-runtime-decision-gate-v0/review.json`;
- lands `tests/test_decision_work_brief_expansion_runtime_decision_gate.py`;
- uses PR124 readability and PR125 local-private adequacy evidence to choose
  the next Decision Work Brief phase;
- selects `run_more_local_private_adequacy_checks`, not runtime attachment;
- records that runtime integration is premature because the lane remains
  offline, Codex-assisted, non-human-validated, source-depth-limited, and
  tested against local-private context in only one case;
- still creates no new cases, five-case batch, runtime integration, archive
  mutation, model-call code, answer-quality scoring, automatic labels, product
  proof, human validation, customer marketing copy, or agent action
  authorization.

Previous Decision Work Brief local-private adequacy slice:

- PR125 Decision Work Brief Local-Private Adequacy Check v0;
- lands `docs/conversation-understanding/decision-work-brief-local-private-adequacy-check-v0.md`;
- lands `reviews/codex-assisted/decision-work-brief-local-private-adequacy-check-v0/review.json`;
- lands `tests/test_decision_work_brief_local_private_adequacy_check.py`;
- follows PR124's `proceed_to_local_private_adequacy_check` gate;
- selects exactly one existing case:
  `launch-public-enterprise-beta/20260627T104146Z_7bfe79`;
- completes a read-only local-private shadow review and checks in only safe
  conclusions;
- records `adequate_but_missing_private_nuance`;
- gates to `proceed_to_expansion_or_runtime_decision_gate`;
- still checks in no raw conversation, raw revised answer, raw memo, provider
  text, private ledgers, local absolute paths, secrets, runtime integration,
  product proof, human validation, answer-quality scoring, or agent action
  authorization.

Previous Decision Work Brief plain-language rereview slice:

- PR124 Plain-Language Brief Re-Review v0;
- lands `docs/conversation-understanding/decision-work-brief-plain-language-rereview-v0.md`;
- lands `reviews/codex-assisted/decision-work-brief-plain-language-rereview-v0/review.json`;
- lands `tests/test_decision_work_brief_plain_language_rereview.py`;
- reviews exactly the three PR123 regenerated rendered briefs;
- finds the plain-language surface good enough for local-private adequacy
  comparison;
- records the main remaining blocker as source depth/private context, not
  renderer language;
- chooses `proceed_to_local_private_adequacy_check`;
- still creates no new cases, renderer changes, local-private checked-in text,
  runtime integration, product proof, human validation, answer-quality scoring,
  or agent action authorization.

Previous Decision Work Brief plain-language renderer slice:

- PR123 Decision Work Brief Plain-Language Renderer Patch v0;
- patches `engine/system_b/decision_work_brief_renderer.py`;
- updates `tests/test_decision_work_brief_renderer.py`;
- lands `tests/test_decision_work_brief_plain_language_renderer_patch.py`;
- lands `docs/conversation-understanding/decision-work-brief-plain-language-renderer-patch-v0.md`;
- updates `docs/conversation-understanding/decision-work-brief-renderer-v0.md`;
- regenerates the three existing checked-in examples:
  `decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md`,
  `decision-work-brief-rendered-launch-public-enterprise-beta-v0.md`, and
  `decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md`;
- maps the eight `lolla.decision_work_brief.v0` sections into six
  plain-language headings;
- moves source refs, section uncertainty, custody flags, and non-claims into a
  compact "Evidence and limits" section;
- keeps PR116, PR119, and PR121A review-wrapper rendering support;
- still creates no new cases, five-case batch, runtime integration, archive
  mutation, model-call code, answer-quality scoring, automatic labels, product
  proof, human validation, or agent action authorization.

Previous Decision Work Brief three-case pattern review slice:

- PR122 Decision Work Brief Three-Case Pattern Review v0;
- lands `docs/conversation-understanding/decision-work-brief-three-case-pattern-review-v0.md`;
- lands `reviews/codex-assisted/decision-work-brief-three-case-pattern-review-v0/review.json`;
- lands `tests/test_decision_work_brief_three_case_pattern_review.py`;
- reviews exactly three checked-in-safe rendered Decision Work Brief cases:
  `ceo-remove-founding-cofounder`, `launch-public-enterprise-beta`, and
  `deploy-assisted-intake-routing`;
- records the pattern read `useful_but_language_too_internal`;
- finds the strongest useful signal is consistent action consequence across
  founder governance, enterprise launch, and healthcare operations/deployment;
- records the strongest missingness/thinness risk that checked-in-safe context
  cannot verify private nuance, original/revised overlap, user intent, lost
  value, buyer reality, or compliance tolerance;
- records the strongest overclaim risk that clean brief prose can create false
  confidence before human validation or local-private adequacy checks;
- records the strongest product-language risk that current Markdown still
  exposes field labels, status vocabulary, source refs, and custody machinery
  too prominently in the main reading flow;
- chooses `proceed_to_plain_language_renderer_patch`;
- still creates no fourth case, five-case batch, runtime integration, customer
  marketing copy, answer-quality scoring, automatic labels, product proof,
  human validation, local-private checked-in text, or agent action
  authorization.

Previous Decision Work Brief third-diversity slice:

- PR121A Decision Work Brief Third Diversity Case Pilot v0;
- lands `docs/conversation-understanding/decision-work-brief-third-diversity-case-pilot-v0.md`;
- lands `reviews/codex-assisted/decision-work-brief-third-diversity-case-pilot-v0/review.json`;
- lands `docs/conversation-understanding/decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md`;
- lands `tests/test_decision_work_brief_third_diversity_case_pilot.py`;
- follows PR120's clear `proceed_to_third_diversity_case` gate and implements
  no other PR121 path;
- selects `deploy-assisted-intake-routing/20260627T130339Z_4cd3cb`, a third
  decision family covering healthcare workflow deployment, compliance,
  staff-capacity, sales, and patient-risk constraints;
- uses locally generated PR115 metadata-only packets and local metadata-only
  Decision Trail/Decision Work Receipt support artifacts as bounded
  source/custody context;
- checks in only sanitized review JSON and rendered Markdown, with no
  local-private text;
- records a concrete action-consequence read: run a 48-hour backlog diagnostic,
  compress nine gates into four must-pass operating gates, define hard pause
  triggers, and narrow what the pilot proves;
- compares the third case against the cofounder and launch-beta cases;
- chooses `proceed_to_three_case_pattern_review`;
- still creates no runtime integration, customer marketing copy, broad batch,
  answer-quality scoring, automatic labels, product proof, human validation, or
  agent action authorization.

Previous Decision Work Brief small-pattern review slice:

- PR120 Decision Work Brief Small Pattern Review v0;
- lands `docs/conversation-understanding/decision-work-brief-small-pattern-review-v0.md`;
- lands `reviews/codex-assisted/decision-work-brief-small-pattern-review-v0/review.json`;
- lands `tests/test_decision_work_brief_small_pattern_review.py`;
- compares the first two checked-in-safe rendered Decision Work Brief cases;
- finds both cases name concrete action consequences and preserve uncertainty;
- records the strongest risk that clean brief prose can create false confidence
  before human validation or local-private adequacy checks;
- chooses `proceed_to_third_diversity_case`;
- still creates no runtime integration, customer marketing copy, broad batch,
  answer-quality scoring, automatic labels, product proof, human validation, or
  agent action authorization.

Previous Decision Work Brief second-case slice:

- PR119 Decision Work Brief Second Tiny Case Pilot v0;
- lands `docs/conversation-understanding/decision-work-brief-second-tiny-case-pilot-v0.md`;
- lands `reviews/codex-assisted/decision-work-brief-second-tiny-case-pilot-v0/review.json`;
- lands `docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md`;
- lands `tests/test_decision_work_brief_second_tiny_case_pilot.py`;
- selects `launch-public-enterprise-beta/20260627T104146Z_7bfe79`, a different
  decision family from the first cofounder case;
- uses locally generated PR115 metadata-only packets and local metadata-only
  Decision Trail/Decision Work Receipt support artifacts as bounded
  source/custody context;
- checks in only sanitized review JSON and rendered Markdown, with no
  local-private text;
- records a concrete action-consequence read: do not default to the larger-logo
  prospect or public launch; give both prospects the same paid/scoped private
  pilot offer and choose based on buyer behavior plus tripwire gates;
- compares the second launch-beta case against the first
  `ceo-remove-founding-cofounder` case;
- chooses `proceed_to_small_pattern_review`;
- still creates no runtime integration, customer marketing copy, broad batch,
  answer-quality scoring, automatic labels, product proof, human validation, or
  agent action authorization.

Previous Decision Work Brief usefulness-review slice:

- PR118 Decision Work Brief Usefulness Review And Delivery Gate v0;
- lands `docs/conversation-understanding/decision-work-brief-usefulness-review-v0.md`;
- lands `reviews/codex-assisted/decision-work-brief-usefulness-review-v0/review.json`;
- lands `tests/test_decision_work_brief_usefulness_review.py`;
- reviews the receipt/debug-summary layer, the PR116 structured draft, and the
  PR117 rendered Markdown brief;
- decides the rendered brief partly answers the user-facing question:
  "what did this process make me see or do differently?";
- records the strongest useful signal: the rendered brief names action
  consequence more clearly than receipt inventory;
- records the strongest missingness/thinness risk: one Codex-assisted
  checked-in-safe case cannot establish starting direction, vanilla overlap,
  user intent, or lost-value severity;
- records the strongest overclaim risk: clean Markdown may make a provisional
  one-case read feel more complete than the source boundary permits;
- chooses `proceed_to_tiny_second_case`;
- still creates no runtime integration, customer marketing copy, broad batch,
  answer-quality scoring, automatic labels, product proof, human validation, or
  agent action authorization.

Previous Decision Work Brief renderer slice:

- PR117 Decision Work Brief Markdown Renderer v0;
- lands `engine/system_b/decision_work_brief_renderer.py`;
- lands `scripts/evals/render_decision_work_brief.py`;
- lands `tests/test_decision_work_brief_renderer.py`;
- lands `docs/conversation-understanding/decision-work-brief-renderer-v0.md`;
- lands
  `docs/conversation-understanding/decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md`;
- renders existing `lolla.decision_work_brief.v0` JSON to Markdown without
  generating or inferring missing content;
- supports rendering an embedded PR116 pilot-review brief by index;
- keeps the decision story before evidence receipt and custody appendix;
- renders status, source status, uncertainty, source refs, human-validation
  state, custody flags, and non-claims;
- still creates no semantic generator, runtime integration, model-call code,
  archive mutation, answer-quality scoring, product proof, human validation, or
  agent action authorization.

Previous Decision Work Brief draft-pilot slice:

- PR116 Codex-Assisted Brief Draft Pilot v0;
- lands `reviews/codex-assisted/decision-work-brief-draft-pilot-v0/review.json`;
- lands `docs/conversation-understanding/decision-work-brief-draft-pilot-v0.md`;
- lands `tests/test_decision_work_brief_draft_pilot.py`;
- uses a locally generated PR115 metadata-only packet for one completed run;
- embeds one provisional `lolla.decision_work_brief.v0` draft in checked-in-safe
  review JSON;
- records the case as
  `ceo-remove-founding-cofounder/20260627T093131Z_59d153`;
- keeps raw conversation, raw memo, raw revised answer, provider text, private
  ledgers, and local absolute paths out of checked-in artifacts;
- marks the draft as Codex-assisted, provisional, not human validated, not
  product proof, not answer-quality scoring, and not agent action authorization;
- preserves action consequence, human follow-up questions, uncertainty,
  missingness, lost-value or overcorrection risk, source refs, custody flags,
  and non-claims;
- still creates no renderer, customer board demo, broad batch, runtime
  integration, model-call code, archive mutation, product-proof claim, or
  agent-action authorization.

Previous Decision Work Brief packet-builder slice:

- PR115 Decision Work Brief Local Packet Builder v0;
- lands `engine/system_b/decision_work_brief_packets.py`;
- lands `scripts/evals/build_decision_work_brief_packets.py`;
- lands `tests/test_decision_work_brief_packets.py`;
- lands `docs/conversation-understanding/decision-work-brief-packet-builder-v0.md`;
- builds `lolla.decision_work_brief_packets.v0` as an offline packet contract
  over completed run directories;
- preserves source refs, source availability, missingness, redaction/private
  availability, custody flags, and non-claims for all eight future brief
  sections;
- supports default metadata-only output and explicit local-private include-text
  output marked unsafe for commit;
- links optional Decision Work Receipt, Decision Trail, and Product Delta
  reports by safe metadata only;
- still creates no populated brief, renderer, runtime integration, model calls,
  archive mutation, answer-quality scoring, automatic labels, product proof, or
  agent action authorization.

Previous Decision Work Brief schema slice:

- PR114 Decision Work Brief Schema v0;
- lands `docs/conversation-understanding/decision-work-brief-v0.json`;
- lands `docs/conversation-understanding/decision-work-brief-schema-v0.md`;
- lands `tests/test_decision_work_brief_schema.py`;
- updates the Decision Work Brief PRD to mark PR114 as implemented and point
  next to PR115 Decision Work Brief Local Packet Builder v0;
- makes the Decision Work Brief a first-class schema contract with required
  user-facing sections for the decision, starting direction, what Lolla pressed
  on, what changed, action consequence, remaining uncertainty, non-proof, and
  evidence receipt;
- requires per-section status, source status, source refs, interpreter,
  uncertainty, human-validation state, value, and empty meaning;
- requires conservative custody flags and explicit non-claims;
- creates no generator, packet builder, renderer, populated brief, runtime
  integration, model calls, archive mutation, semantic inference, answer
  quality scoring, automatic labels, product proof, or agent action
  authorization.

Previous Decision Trail human-review intake slice:

- lands `docs/conversation-understanding/decision-trail-human-review-intake-packet-v0.md`;
- lands `reviews/human/decision-trail-human-review-intake-packet-v0/intake.json`;
- lands `tests/test_decision_trail_human_review_intake_packet.py`;
- packages PR97, PR100, and PR102 into a compact future-human-review queue;
- preserves candidate useful signals, limits, vanilla-overlap questions,
  lost-value questions, and overtrust questions for each case;
- leaves all human correction fields blank and `human_fields_filled: false`;
- recommends pausing until human review capacity returns;
- creates no new specialist outputs, reads no new local-private packet content,
  creates no fourth pilot, creates no broad batch, invokes no runtime, calls no
  providers, mutates no archives, measures no answer quality, creates no
  automatic labels, and authorizes no agent action.

Previous Decision Trail specialist pilot phase closure gate:

- lands `docs/conversation-understanding/decision-trail-specialist-pilot-phase-closure-gate-v0.md`;
- lands `reviews/codex-assisted/decision-trail-specialist-pilot-phase-closure-gate-v0/report.json`;
- lands `tests/test_decision_trail_specialist_pilot_phase_closure_gate.py`;
- compares PR97, PR100, and PR102 by checked-in summaries only;
- records no new local-private packet reads and no new specialist outputs;
- closes the one-case local-private specialist-output pilot phase after three
  pilots;
- blocks a fourth one-case pilot and broad specialist-output batch;
- recommends PR104 Decision Trail Human Review Intake Packet v0, or pause if
  human review capacity is unavailable;
- calls no providers or external model APIs, invokes no runtime, mutates no
  archives, measures no answer quality, creates no automatic labels, and
  authorizes no agent action.

Previous Decision Trail diversity pilot:

- lands `docs/conversation-understanding/decision-trail-third-one-case-diversity-pilot-v0.md`;
- lands `reviews/codex-assisted/decision-trail-third-one-case-diversity-pilot-v0/review.json`;
- lands `tests/test_decision_trail_third_one_case_diversity_pilot.py`;
- runs the diversity-targeted one-case local-private specialist-output pilot
  allowed by PR101, by checked-in summary only;
- selects `deploy-assisted-intake-routing/20260627T130339Z_4cd3cb` before
  reading local-private packet content because it is a deployment-controls
  contrast to PR97 and PR100;
- records local temp packet deletion and keeps private packet content out of
  the repo;
- preserves material vanilla overlap while surfacing a different useful signal:
  the revised answer reduces noisy gate bloat and treats admin operating load
  as part of safety;
- recommends closure rather than a fourth one-case pilot or broad batch.

Previous Decision Trail specialist pilot comparison gate:

- lands `docs/conversation-understanding/decision-trail-specialist-pilot-comparison-gate-v0.md`;
- lands `reviews/codex-assisted/decision-trail-specialist-pilot-comparison-gate-v0/report.json`;
- lands `tests/test_decision_trail_specialist_pilot_comparison_gate.py`;
- compares PR97 and PR100 using checked-in summary artifacts only;
- records no new local-private packets and no new specialist outputs;
- keeps the strongest useful signal from PR100: the patched shape downgraded
  the read when vanilla overlap was material;
- decides broad specialist-output batches are not ready;
- allows at most one diversity-targeted third one-case pilot before stopping,
  simplifying, or preparing human-review intake;
- calls no providers or external model APIs, invokes no runtime, mutates no
  archives, measures no answer quality, creates no automatic labels, and
  authorizes no agent action.

Previous Decision Trail second one-case specialist pilot:

- lands `docs/conversation-understanding/decision-trail-second-one-case-specialist-pilot-v0.md`;
- lands `reviews/codex-assisted/decision-trail-second-one-case-specialist-pilot-v0/review.json`;
- lands `tests/test_decision_trail_second_one_case_specialist_pilot.py`;
- runs a second one-case local-private specialist-output pilot by checked-in
  summary only over `accept-founding-engineer-role/20260627T073034Z_a7c221`;
- records local temp packet deletion and keeps private packet content out of
  the repo;
- exercises all PR99 fields: assistant-influence source status,
  vanilla-overlap read, lost-value severity read, severity source status,
  source-scope/truncation impact, fan-in downgrade triggers, and not-ready
  reason;
- records the strongest useful signal: `vanilla_overlap_read` forces a
  partial-usefulness net read because the vanilla conversation already
  contained much of the visible action sequence;
- recommends PR101 Decision Trail Specialist Pilot Comparison Gate v0 before
  any third pilot or broad batch;
- calls no providers or external model APIs, invokes no runtime, mutates no
  archives, measures no answer quality, creates no automatic labels, and
  authorizes no agent action.

Previous Decision Trail specialist contract/packet patch:

- lands `docs/conversation-understanding/decision-trail-specialist-contract-and-packet-patch-v0.md`;
- patches `docs/conversation-understanding/decision-trail-specialist-contracts-v0.md`;
- patches `docs/conversation-understanding/decision-trail-specialist-contracts-v0.json`;
- patches `engine/system_b/decision_trail_specialist_packets.py`;
- regenerates `reviews/codex-assisted/decision-trail-specialist-packets-v0/packets.json`;
- updates packet/contract tests for PR99-required fields;
- adds role-readable source-scope, truncation, and local-private retention
  metadata to future specialist packets;
- keeps the schema families stable and additive:
  `lolla.decision_trail_specialist_contracts.v0` and
  `lolla.decision_trail_specialist_packets.v0`;
- creates no new specialist outputs, runs no providers or models, invokes no
  runtime, mutates no archives, measures no answer quality, creates no
  automatic labels, and authorizes no agent action.

Previous Decision Trail specialist-output pilot review:

- lands `docs/conversation-understanding/decision-trail-specialist-output-pilot-review-v0.md`;
- lands `reviews/codex-assisted/decision-trail-specialist-output-pilot-review-v0/review.json`;
- lands `tests/test_decision_trail_specialist_output_pilot_review.py`;
- reviews PR97's one-case local-private specialist-output pilot without
  creating new specialist outputs or reading local-private packet text;
- keeps PR97 as useful enough to continue but blocks a broad batch;
- requires contract patches for vanilla overlap, lost-value severity,
  assistant-influence source status, source/truncation impact, and fan-in
  downgrade triggers;
- requires packet metadata patches for artifact source scope, truncation
  summary, and local-private retention/deletion status;
- recommends PR99 Decision Trail Specialist Contract And Packet Patch v0 before
  a second one-case pilot;
- calls no providers or models, invokes no runtime, mutates no archives,
  measures no answer quality, creates no automatic labels, and authorizes no
  agent action.

Previous Decision Trail local-private specialist-output pilot:

- lands `docs/conversation-understanding/decision-trail-local-private-specialist-output-pilot-v0.md`;
- lands `reviews/codex-assisted/decision-trail-local-private-specialist-output-pilot-v0/review.json`;
- lands `tests/test_decision_trail_local_private_specialist_output_pilot.py`;
- uses a PR95 local-private include-text packet under `/tmp` only and checks in
  summary-level specialist outputs, not raw/private packet content;
- fills all four PR90 roles for
  `ceo-remove-founding-cofounder/20260627T093131Z_59d153`:
  conversation shape, likely action, friction/lost value, and conservative
  fan-in;
- finds the useful signal that private source access makes the decision shape,
  likely-action delta, lost-value risk, and fan-in tension more concrete than
  the sparse checked-in-safe shell;
- records the main unresolved risk: one case only, private packet truncation,
  candidate-only Codex-assisted reads, and no human validation;
- recommends PR98 Decision Trail Specialist Output Pilot Review / Contract
  Revision v0 before any broad specialist batch;
- calls no providers or models, invokes no runtime, mutates no archives, scores
  nothing, judges nothing, creates no automatic labels, and authorizes no
  agent action.

Previous Decision Trail local-private packet smoke-review slice:

- lands `docs/conversation-understanding/decision-trail-local-private-packet-smoke-review-v0.md`;
- lands `reviews/codex-assisted/decision-trail-local-private-packet-smoke-review-v0/review.json`;
- lands `tests/test_decision_trail_local_private_packet_smoke_review.py`;
- uses PR95 CLI outputs under `/tmp` only;
- metadata-only smoke over two real completed runs confirms four PR90 role
  packets and 16 artifact records per run without raw/private content;
- real include-text smoke over one completed run confirms private-content path,
  truncation, unsafe-for-commit marking, and then deletes the private output;
- synthetic include-text smoke preserves a repeatable safe guardrail surface;
- confirms local-private output is rejected inside the repo and inside the
  selected run directory;
- recommends only a tiny PR97 local-private specialist-output pilot, not a
  broad batch;
- creates no specialist outputs, executes no fan-in, calls no providers or
  models, invokes no runtime, mutates no archives, scores nothing, judges
  nothing, and creates no automatic labels.

Previous Decision Trail local-private packet-mode slice:

- lands `docs/conversation-understanding/decision-trail-local-private-packet-mode-v0.md`;
- extends `engine/system_b/decision_trail_specialist_packets.py`;
- extends `scripts/evals/build_decision_trail_specialist_packets.py`;
- lands `tests/test_decision_trail_local_private_packets.py`;
- keeps checked-in-safe packet behavior as the default;
- adds explicit `local_private_mode` for operator-selected run directories;
- requires local-private output outside both the repo and the selected run
  directory;
- supports `metadata_only` and `include_text` content policies;
- records local artifact read manifests, private-content inclusion metadata,
  and unsafe-for-commit status;
- treats the PR88 fixture-review input as lineage-only in `local_private_mode`
  while selected run artifacts and the PR90 schema define packet content;
- derives `raw_transcripts_included`, `raw_revised_answers_included`, and
  `raw_memos_included` from actual included artifacts rather than from the
  `include_text` mode alone;
- requires local-private fixture-review and contract-schema inputs to be
  repo-local so local absolute paths do not leak into packet references;
- creates no specialist outputs, executes no fan-in, calls no providers or
  models, invokes no runtime, mutates no archives, scores nothing, judges
  nothing, and creates no automatic labels.

Previous Decision Trail path-decision slice:

- lands `docs/conversation-understanding/decision-trail-specialist-path-decision-v0.md`;
- lands `tests/test_decision_trail_specialist_path_decision.py`;
- selects **Outcome A: implement local-private Decision Trail packet mode next**;
- recommends PR95 Decision Trail Local-Private Packet Mode v0;
- rejects a tiny checked-in-safe specialist batch for now because it would
  mostly repeat known blocked/thin evidence;
- rejects simplification, pause, runtime integration, and broad conversation IR
  for now;
- preserves the core bottleneck: source access is now the limiting factor, not
  contract shape;
- keeps the next work offline, explicit, local-private, non-runtime,
  non-judging, non-scoring, and non-claiming.

Previous Decision Trail dry-run slice:

- lands `docs/conversation-understanding/decision-trail-specialist-dry-run-v0.md`;
- lands `reviews/codex-assisted/decision-trail-specialist-dry-run-v0/review.json`;
- lands `tests/test_decision_trail_specialist_dry_run.py`;
- runs a Codex-assisted provisional discipline dry run over all ten PR92 trap
  families;
- records trap behavior counts: seven met, three partly met, zero missed, zero
  inconclusive;
- inspects the two PR91 packet targets without filling PR90 specialist output
  fields;
- finds the structured fixture useful for gap preservation but not semantic
  interpretation;
- finds the sparse fixture diagnostic only;
- preserves the main bottleneck: checked-in-safe fixture surfaces can test
  discipline, but they cannot prove real conversation interpretation adequacy;
- preserves no model calls, no specialist outputs, no fan-in execution, no
  runtime integration, no archive mutation, no scoring, no judging, and no
  automatic labels.

Previous Decision Trail trap-set slice:

- lands `docs/conversation-understanding/decision-trail-specialist-trap-set-v0.md`;
- lands `docs/conversation-understanding/decision-trail-specialist-trap-set-v0.json`;
- lands `tests/test_decision_trail_specialist_trap_set.py`;
- creates ten checked-in-safe trap families for the four PR90 specialist roles;
- tests future review discipline around thin safe fixtures, clean custody,
  structural-delta overtrust, missing generated report JSON, likely-action
  over-inference, option-status collapse, assistant-influence absence,
  lost-value blindness, fan-in smoothing, and local-private context need;
- preserves no model calls, no specialist reads, no fan-in execution, no
  runtime integration, no archive mutation, no scoring, no judging, and no
  automatic labels.

Previous Decision Trail packet-builder slice:

- lands `engine/system_b/decision_trail_specialist_packets.py`;
- lands `scripts/evals/build_decision_trail_specialist_packets.py`;
- lands `tests/test_decision_trail_specialist_packets.py`;
- lands `docs/conversation-understanding/decision-trail-specialist-packet-builder-v0.md`;
- lands `reviews/codex-assisted/decision-trail-specialist-packets-v0/packets.json`;
- builds checked-in-safe input packets for the two PR88 report-review targets;
- gives every report target the four PR90 specialist packet shells:
  conversation-shape, likely-action, friction/lost-value, and conservative
  fan-in;
- records that PR88 generated reports were not checked in, so packet evidence
  remains fixture-review-only and thin;
- preserves no model calls, no specialist reads, no fan-in execution, no
  runtime integration, no archive mutation, no scoring, no judging, and no
  automatic labels.

Previous Decision Trail contract slice:

- lands `docs/conversation-understanding/decision-trail-specialist-contracts-v0.md`;
- lands `docs/conversation-understanding/decision-trail-specialist-contracts-v0.json`;
- lands `tests/test_decision_trail_specialist_contracts.py`;
- defines the four narrow offline specialist roles selected by PR89:
  conversation shape, likely actions, friction/lost value, and conservative
  fan-in;
- defines input-mode vocabulary for checked-in safe mode, local private mode,
  and future runtime mode without implementing local private or runtime modes;
- requires source refs, source status, uncertainty, evidence strength,
  limitations, non-claims, and lower-claim boundary metadata;
- forbids fan-in voting, averaging, scoring, certification, approval, winner
  selection, correctness from agreement, and decision-quality claims;
- preserves no packet builder, no model calls, no specialist outputs, no fan-in
  execution, no runtime integration, no archive mutation, no scoring, no
  judging, and no automatic labels.

Previous Decision Trail decision-gate slice:

- lands `docs/conversation-understanding/decision-trail-interpretation-gap-decision-v0.md`;
- selects Outcome B from the PR86-PR89 PRD: add narrow offline LLM specialist
  enrichment;
- keeps PR87/PR88 as the custody and missingness shell;
- confirms the shell is useful but not enough for the full Decision Trail
  product surface;
- names the missing product-load-bearing fields: likely next actions, live
  options and option status, stakeholders, values/priorities, assistant
  influence, useful/noisy friction, and lost value;
- rejects runtime integration, broad `conversation_understanding_ir.v0`,
  extraction expansion, stopping/simplification, judging, scoring, automatic
  labels, and graph/memory work for now;
- recommends PR90 Decision Trail Interpretation Specialist Contracts v0 as a
  docs/schema-only next slice.

Previous Decision Trail fixture-review slice:

- lands `docs/conversation-understanding/decision-trail-export-fixture-review-v0.md`;
- lands `reviews/codex-assisted/decision-trail-fixture-review-v0/review.json`;
- lands `tests/test_decision_trail_fixture_review.py`;
- reviews PR87 generated report behavior in checked-in-safe fixture mode;
- confirms no local-private shadow review was run;
- treats PR89 evidence as safe-fixture-only;
- finds the report useful for custody, source refs, missingness, redaction, and
  non-claims;
- finds the report too sparse for the full Decision Trail product because live
  options, likely next actions, stakeholders, values/priorities, assistant
  influence, useful/noisy friction, and lost value still require interpretation;
- preserves the main overtrust risk: a populated `structural_delta` can look
  more semantically complete than the report really is.

Previous Decision Trail exporter slice:

- lands `engine/system_b/decision_trail_report.py`;
- lands `scripts/evals/build_decision_trail_report.py`;
- lands `tests/test_decision_trail_report.py`;
- lands `docs/conversation-understanding/decision-trail-readonly-exporter-v0.md`;
- implements a deterministic read-only exporter for
  `lolla.decision_trail_report.v0`;
- accepts an archived run directory and explicit output path outside that run
  directory;
- supports `checked_in_safe_mode` only, with local private mode deferred;
- reads structured JSON artifacts only by default: `evaluation.json`,
  `agent_result.json`, `reasoning_trace.json`,
  `extraction_adequacy_report.json`, `extraction.json`, and `result.json`;
- records raw/private artifacts as redacted/private-available or missing
  without reading `conversation.txt`, `memo.md`, `revised.txt`,
  `live_transcript.txt`, `operator.log`, private tables, or private ledgers;
- populates deterministic artifact health, custody flags, report metadata,
  decision question, conversation-understanding summary, constraints, audit
  pressure summary, structural delta, unresolved questions, and trace context
  only when safe structured sources exist;
- preserves vanilla likely next action, revised likely next action, option map,
  stakeholders, values/priorities, assistant influence, useful/noisy friction,
  and lost value as `requires_llm_interpretation` unless a later safe review
  artifact supplies them;
- preserves no `$lolla` run, no Lolla skill invocation, no model calls, no
  archive mutation, no runtime integration, no prompt change, no `SKILL.md`
  change, no `scripts/skill/*` change, no labels, no scoring, no judge, no
  automatic verdict, no agent action authorization, no fixture review, and no
  product-proof claim.

Previous completed slice:

```text
PR86 Decision Trail Report PRD And Schema v0
```

Result:

- lands `docs/conversation-understanding/decision-trail-report-prd-v0.md`;
- lands `docs/conversation-understanding/decision-trail-report-v0.json`;
- lands `tests/test_decision_trail_report_schema.py`;
- defines `lolla.decision_trail_report.v0` as an offline report contract over
  completed Lolla artifacts;
- defines shared semantic section metadata: `status`, `source_status`,
  `source_refs`, `value` or `items`, `empty_meaning`, `owner`,
  `requires_llm_interpretation`, and `exporter_inferred_from_prose`;
- distinguishes checked-in safe mode, local private mode, and a reserved future
  runtime mode that is not implemented;
- preserves redaction versus missingness distinctions and optional
  future-compatible trace fields without adding trace dependencies;
- records that deterministic code may preserve custody/status/source refs and
  must not infer messy semantic fields from prose;
- preserves no `$lolla` run, no Lolla skill invocation, no model calls, no
  archive mutation, no exporter code, no runtime integration, no prompt change,
  no `SKILL.md` change, no labels, no scoring, no judge, no automatic verdict,
  no agent action authorization, and no product-proof claim.

Previous completed slice:

```text
PR85 Product Delta PR71-PR84 Packaging Gate v0
```

Result:

- lands `docs/evals/product-delta-pr71-pr84-packaging-gate-v0.md`;
- lands `docs/evals/product-delta-pr71-pr84-package-manifest-v0.json`;
- lands `tests/test_product_delta_pr71_pr84_package_gate.py`;
- adds a static package manifest for the PR71-PR84 Product Delta Evidence
  surface, grouped by docs, JSON artifacts, review fixtures, read-only code,
  scripts, and tests;
- verifies that PR71 through PR84 are represented exactly and that obvious
  unrelated untracked docs, plans, and synthetic-review folders are excluded;
- records the strongest useful signal: `accept-operations-role-startup`
  downgraded from `material_improvement_candidate` to
  `partial_improvement_candidate`;
- records the strongest unresolved risk: PR83/PR84 cover only two
  prior-positive real cases, with no human validation and no real-case
  no-change/noise/worse/inconclusive outcome;
- adds tests for conservative boundary metadata, PR84 static-report constraints,
  PR83 actual shape paths, PR78 lint coverage, privacy hygiene, and
  source-reference path/JSON-pointer resolution;
- preserves no `$lolla` run, no Lolla skill invocation, no model calls, no
  archive mutation, no runtime integration, no prompt change, no `SKILL.md`
  change, no labels, no scoring, no judge, no automatic verdict, no
  agent approval, and no product-proof claim.

Stop point:

```text
Do not start real high-stakes run work without explicit maintainer approval.
PR48 remains the high-stakes evidence gate.
The separate user-values/priorities lane is now paused at PR54 unless a later
implementation gate is explicitly approved.
PR85 is a packaging gate over the PR71-PR84 Product Delta Evidence phase. It
authorizes package coherence checks, not human labels, judge calibration data,
product proof, product approval, runtime integration, archive mutation,
automatic generation inside archives, graph DB, embeddings, memory, GraphRAG,
automatic labels, or agent approval. PR78 lint remains the evidence-boundary
seatbelt for Product Delta artifacts. The next recommended move is to stop and
decide whether to stage/package PR71-PR85 explicitly, or pause until human
review capacity returns.
```

The broader action map for this next phase is:

`docs/evals/evaluation-flywheel-action-plan-v0.md`

Non-goals for the next slice:

- no generic LLM judge;
- no answer-quality score;
- no automatic human-review labels;
- no approved high-stakes run batch without explicit product approval;
- no prompt rewrite;
- no runtime behavior change unless explicitly scoped as a later phase;
- no `SKILL.md` change;
- no quote-validation repair;
- no specialist runtime/archive integration;
- no review batch or fan-in report unless explicitly scoped in a later PR;
- no `conversation_understanding_ir.v0`;
- no graph DB, embeddings, chunking, or memory layer.
- no Semantica-style policy engine, compliance platform, generic agent safety
  layer, domain authority, answer-quality score, automatic labels, LLM judge, or
  PR58+ implementation.

## PRD Checkpoint: Built, Missing, Opportunities

### Built

- [x] Agent-facing result contract: `agent_result.json` /
  `lolla_agent_result.v1`.
- [x] Risk-mode metadata propagation.
- [x] Optional control-plane sidecars: `control_input.json` /
  `control_result.json`.
- [x] Capture adequacy metadata and evaluation checks.
- [x] Deterministic `evaluation.json` run-readiness receipt.
- [x] Reasoning trace custody and archive artifact indexing.
- [x] Observatory custody parity for current/archived sidecars.
- [x] Provider-boundary classification and signature-only metadata filtering.
- [x] Review corpus export with local-only scope and blank human-review fields.
- [x] Human-review taxonomy and workflow v0.
- [x] Synthetic-review boundary, prompt, and validator.
- [x] Review-readiness tiers.
- [x] Extraction adequacy report, corpus export, findings drilldown, and quote
  validation diagnostics.
- [x] Modern quote-validation baseline: no runtime quote repair justified.
- [x] Semantic coverage report and corpus survey.
- [x] Specialist extractor fake-boundary and real-boundary probe harnesses.
- [x] Broader mixed-custody specialist evidence gate.
- [x] Six clean complex conversation baseline.
- [x] PR30 human/product review seed over the six complex baseline runs.
- [x] PR31 actionable-delta rubric.
- [x] PR32 adversarial pair fixture seed set.
- [x] PR33 broader human-review corpus batch.
- [x] PR34 first-class user-values/priorities design.
- [x] PR35 live-output hygiene decision.
- [x] PR36 risk-mode behavior plan.
- [x] PR37 risk-mode fixture matrix.
- [x] PR38 risk-mode fixture review.
- [x] PR39 risk-mode implementation plan.
- [x] PR40 risk-mode contract-lock tests.
- [x] PR41 risk-mode evaluation-artifact clarity.
- [x] PR42 risk-mode review-surface integration.
- [x] PR43 fixture-backed risk-mode reliance review batch.
- [x] PR44 review-corpus reliance manifest counts.
- [x] PR45 current-state anti-drift handoff.
- [x] PR46 approved high-stakes evidence seed plan.
- [x] PR47 high-stakes evidence fixture pack.
- [x] PR48 review-corpus evidence readiness analyzer.
- [x] PR49 user-values/priorities worksheet plan.
- [x] PR50 user-values/priorities worksheet fixture pack.
- [x] PR51 user-values/priorities worksheet fixture review.
- [x] PR52 user-values/priorities blank worksheet export.
- [x] PR53 user-values/priorities worksheet human pilot.
- [x] PR54 user-values/priorities pilot review / v0 decision.
- [x] PR55 Semantica-inspired accountability PRD / comparative architecture
  note.
- [x] PR56 Lolla Doctor / Preflight plan.
- [x] PR57 Lolla Doctor Read-Only CLI.
- [x] PR58 Audit Decision Record Design.
- [x] PR59 Audit Decision Record Fixture Review.
- [x] PR60 Provenance Map Design.
- [x] PR61 Review Conflict Register Design.
- [x] PR62 Case Graph Export Design.
- [x] PR63 Accountability View Fixture Pack.
- [x] PR64 Accountability View Fixture Review.
- [x] PR65 Accountability Implementation Decision Gate.
- [x] PR66 Audit Decision Record Read-Only Exporter.
- [x] PR67 Audit Decision Record Export Smoke / Review.
- [x] PR68 Audit Decision Record Schema / Exporter Refinement.
- [x] PR69 Audit Decision Record Export Review Re-Run.
- [x] PR70 Audit / Accountability Machinery Closure Gate.
- [x] Current system capabilities explainer, grounded in recorded cases.
- [x] Public pitch/docs refreshed around Lolla as a reasoning-audit harness.

### Missing / Not Done

- [ ] Human labels on 50-100 archive/corpus records.
- [ ] Calibrated binary subjective judges.
- [ ] Agent trigger-policy docs for external builders.
- [ ] Behavioral risk-mode enforcement; PR36 is design-only, PR37 is fixture
  work, PR38 is fixture review, PR39 is a pre-code implementation plan, PR40 is
  a contract-lock test slice, PR41 only clarifies `evaluation.json`, PR42 only
  exposes that caveat in review-corpus records, PR43 only validates reviewer
  interpretation with fixtures, PR44 only adds manifest counts, PR45 only
  documents the current state, PR46 only plans future approved high-stakes
  evidence, PR47 only adds paraphrase-only high-stakes evidence fixtures, PR48
  only analyzes review-corpus manifests for evidence readiness, PR49 only
  plans a human values/priorities worksheet, PR50 only adds paraphrase-only
  worksheet fixtures, PR51 only reviews those fixtures, PR52 only creates blank
  deterministic worksheet structure, and PR53 only pilots human-filled
  worksheets from already-reviewed summaries. PR54 only reviews that pilot and
  pauses the lane at v0 for human-owned review.
  Current pipeline behavior is still mostly metadata-first.
- [ ] Decision-aware capture for long conversations and middle-turn hinges.
- [ ] First-class user-values/priorities extraction or offline report; PR34 is
  design-only, PR49 is worksheet planning only, PR50 is fixture-only, PR51 is
  fixture-review-only, PR52 is blank-template-only, and PR53 is
  human-pilot-only. PR54 is pilot-review-only and explicitly pauses before
  extraction or runtime integration.
- [ ] Span-grounded runtime/archive semantic coverage.
- [ ] Runtime or archive integration for specialist extractors.
- [ ] `conversation_understanding_ir.v0` or persisted conversation-understanding
  projection.
- [ ] Semantica-inspired accountability primitives beyond the first safe
  surfaces. PR55 is the docs-only accountability roadmap, PR56 is the docs-only
  doctor/preflight plan, PR57 implements only the read-only doctor CLI, PR58
  designs only `lolla.audit_decision_record.v0`, and PR59 only reviews
  paraphrase-only decision-record fixtures. PR60 designs only
  `lolla.provenance_map.v0`; PR61 designs only
  `lolla.review_conflict_register.v0`; PR62 designs only
  `lolla.case_graph.v0`; PR63 only creates paraphrase-only accountability-view
  fixtures; PR64 only reviews those fixtures and recommends a later
  decision-record exporter-design gate; PR65 only chooses that future
  decision-record exporter as a recommendation; PR66 implements only that
  read-only decision-record exporter; PR67 only reviews exporter smoke output
  and recommends a small schema/exporter refinement; PR68 only implements that
  field-population clarity refinement; PR69 only reviews refined exporter
  output and recommends a future decision gate; PR70 closes the machinery lane
  and redirects to Product Delta Evidence. No archive integration, batch
  export, automatic generation, provenance exporter, conflict-register
  exporter, case-graph exporter, graph DB, memory, GraphRAG, labels, scoring,
  judges, or runtime integration is implemented.
- [ ] Live-output hygiene implementation beyond conservative `not_checked`;
  PR35 is decision-only.
- [ ] Run-to-run stability workflow for repeated conversations.
- [ ] Optional human capability surface: "What To Learn From This Audit."
- [ ] Selected archived dashboard render/readback stabilization beyond the
  custody-panel bridge.

### Opportunities To Make The Machine Work Better

1. **Approved high-stakes evidence seed, only with explicit approval.** PR44
   makes the current absence visible and PR48 makes the readiness read explicit;
   real high-stakes reliance-present archive evidence should be created only
   from approved cases, not by default.
2. **User-values/priorities worksheet v0 is paused after review.** PR34 designs the signal,
   PR49 plans the human worksheet, PR50 adds paraphrase-only fixtures, PR51
   reviews those fixtures, PR52 creates blank worksheet structure, and PR53
   pilots four human-filled local review worksheets. PR54 reviews that pilot,
   marks the v0 worksheet surface complete for human-owned review, and pauses
   before any populated extraction, automatic label, runtime integration,
   memory, or judge.
3. **PR85 packaging gate is done.** PR85 records the PR71-PR84 Product Delta
   surface in a package manifest, checks source references and boundary
   metadata, preserves the `accept-operations-role-startup` downgrade as the
   strongest useful signal, and keeps the two-case prior-positive thinness as
   the strongest unresolved risk. The next conservative move is explicit
   packaging/staging or a pause for human-review capacity, not more automatic
   evidence expansion.
4. **PR86 Decision Trail report contract is done.** PR86 defines the
   `lolla.decision_trail_report.v0` PRD/schema and confirms the next move is a
   deterministic read-only exporter, not runtime integration or new
   interpretation machinery.
5. **PR87 Decision Trail read-only exporter is done.** PR87 generates a sparse
   checked-in-safe report from structured artifacts only. The next conservative
   move is PR88 fixture review to test whether the report is understandable,
   too thin, confusing, or overclaim-prone before adding interpretation
   machinery.
6. **PR88 Decision Trail fixture review is done.** PR88 says the report is
   useful as a custody and missingness shell, but checked-in-safe evidence is
   too thin for the full answer-plus-process product without later bounded
   interpretation. The next conservative move is PR89: decide whether to pursue
   narrow offline LLM specialist enrichment, local-private review,
   simplification, or a pause.
7. **PR89 Decision Trail interpretation gap decision is done.** PR89 selects
   narrow offline LLM specialist contracts as the next path. The next
   conservative move is PR90 docs/schema-only contracts for conversation shape,
   likely actions, friction/lost value, and conservative fan-in.
8. **PR90 Decision Trail specialist contracts are done.** PR90 defines the
   four narrow offline contracts and stops before packets, model calls,
   specialist outputs, fan-in execution, runtime integration, or archive
   mutation. The next conservative move is PR91 Specialist Packet Builder v0.
9. **PR91 Decision Trail specialist packets are done.** PR91 turns PR88
   fixture-review context into checked-in-safe input scaffolds for the four
   PR90 contracts. It still stops before specialist reads, model calls, fan-in
   execution, runtime integration, or archive mutation. The next conservative
   move is PR92 Decision Trail Specialist Trap Set v0.
10. **PR92 Decision Trail specialist traps are done.** PR92 adds checked-in-safe
   trap fixtures before any specialist review batch. The next conservative move
   is PR93 Decision Trail Specialist Dry Run v0 over traps and a tiny PR91
   packet surface, still without runtime integration or provider/API calls.
11. **PR93 Decision Trail specialist dry run is done.** PR93 shows the setup can
   mostly resist the trap surface and preserve packet thinness, but it also
   confirms that checked-in-safe fixture surfaces cannot prove interpretation
   adequacy. The next conservative move is PR94 Decision Trail Specialist Path
   Decision v0: decide between local-private packets, a tiny blocked specialist
   batch, simplification, or pausing for human review.
12. **PR94 Decision Trail specialist path decision is done.** PR94 selects PR95
   local-private packet mode as the next slice. The next implementation should
   build explicit local-private packets using synthetic temp fixtures and local
   outputs only, while keeping checked-in artifacts raw/private-free and
   runtime untouched.
13. **PR95 Decision Trail local-private packet mode is done.** PR95 adds
   explicit local-private packet generation for operator-selected completed
   run directories. It keeps checked-in-safe mode as the default, rejects
   local-private output inside the repo or run directory, records read
   manifests and private-content metadata, treats PR88 fixture review as
   lineage-only in local-private mode, derives raw-content booleans from
   actual included artifacts, requires repo-local schema/fixture refs, and
   still stops before specialist outputs, fan-in, runtime integration,
   provider/API calls, archive mutation, scoring, judging, or automatic labels.
   The next conservative move is a local-private packet smoke/review, not a
   specialist-output batch.
14. **PR96 Decision Trail local-private packet smoke review is done.** PR96
   confirms metadata-only local-private packets are usable for source
   availability over two real completed runs and confirms the include-text path
   mechanically on one real run without checking in private output. It still
   does not prove interpretation adequacy. The next conservative move is a
   tiny PR97 local-private specialist-output pilot over one or two runs, not a
   broad batch or runtime integration.
15. **PR97 Decision Trail local-private specialist-output pilot is done.** PR97
   fills all four PR90 specialist roles for one local-private completed run and
   keeps private packet content out of the repo. It shows the shape can produce
   more concrete candidate reads, but remains one-case, Codex-assisted,
   unvalidated, and not automatic. The now-complete PR98 review/revision gate
   checked the contracts and packet shape before any broader batch.
16. **PR98 Decision Trail specialist-output pilot review is done.** PR98 keeps
   PR97's useful signal but blocks broadening until the contracts and packet
   metadata are patched. The next conservative move is PR99 Decision Trail
   Specialist Contract And Packet Patch v0, not another specialist run.
17. **PR99 Decision Trail specialist contract/packet patch is done.** PR99 adds
   the PR98-required contract fields and packet metadata for vanilla overlap,
   lost-value severity, assistant-influence source status,
   source-scope/truncation impact, fan-in downgrade triggers, and local-private
   retention policy. PR100 has now used that patched shape on one more
   local-private specialist-output pilot instead of broadening directly.
18. **PR100 Decision Trail second one-case specialist pilot is done.** PR100
   uses the patched PR99 shape on
   `accept-founding-engineer-role/20260627T073034Z_a7c221`. It records a
   partial-usefulness read because vanilla overlap is material: the revised
   answer sharpened thresholds, evidence gates, and stop rules, but much of
   the visible action sequence was already present. PR101 has now compared
   PR97 and PR100 before any third pilot or broad batch.
19. **PR101 Decision Trail specialist pilot comparison gate is done.** PR101
   compares PR97 and PR100 using checked-in summaries only. It keeps the
   useful signal that PR99 fields forced downgrade pressure in PR100, but says
   broad specialist-output batches are still not ready. The only allowed
   continuation is at most one diversity-targeted third one-case pilot in a
   different decision family; otherwise pause or simplify.
20. **PR102 Decision Trail third one-case diversity pilot is done.** PR102 uses
   `deploy-assisted-intake-routing/20260627T130339Z_4cd3cb` as the
   deployment-controls contrast case allowed by PR101. It records another
   partial-usefulness read, but with a different useful signal: Lolla reduced
   noisy gate bloat and added an operating-load/backlog-diagnosis precondition
   while the core narrow-launch action already overlapped materially with the
   vanilla conversation. The next move is PR103: close the one-case pilot phase
   before any fourth pilot or broad batch.
21. **PR103 Decision Trail specialist pilot phase closure gate is done.**
   PR103 compares PR97, PR100, and PR102 using checked-in summaries only. It
   closes the local-only one-case specialist-output pilot phase, blocks a
   fourth pilot and broad specialist-output batch, and recommends PR104 Human
   Review Intake Packet v0 or a pause if human review capacity is unavailable.
   This is a stop line, not product proof.
22. **PR104 Decision Trail human review intake packet is done.** PR104 packages
   PR97, PR100, and PR102 for future human correction. It keeps all human
   fields blank, preserves candidate-useful-signal and lost-value questions,
   and makes the next state pause until a human reviewer can fill or reject the
   packet. It is not completed human review.
23. **Live-output hygiene implementation.** PR35 keeps `not_checked` honest and
   defines a trusted-transcript path; later work can implement only when needed.
24. **Span-grounded semantic enrichment.** Existing specialists help with live
   constraints, dropped threads, and stance lineage, but integration remains
   blocked until a clean 15-20 full-modern sample and provider-boundary behavior
   are settled.
25. **Human capability surface.** Later, add a compact memo/Observatory section
   that teaches the user what reasoning pattern the audit caught.

## Current Pause: Specialist Integration Track

Status: paused as of `origin/main`
`43e15841a88b114c3186dc6b55f1f9bc322d7863`.

Product read:

> Existing specialists are useful as an offline/deep-review direction, but
> runtime and archive integration remain blocked.

What the evidence now says:

- PR29B showed the existing specialists can improve semantic coverage on four
  full-modern runs.
- The broader evidence gate showed 56 of 57 target semantic elements improved
  across 19 mixed-custody runs.
- The broader sample did not clear the full-modern gate: only four sampled
  archives had the complete modern artifact chain, while 15 were
  legacy-limited reasoning-trace runs.
- Provider-boundary warnings occurred on 57 of 57 broader-probe calls.
- The stance specialist had 12 validation drops and one non-improving run.
- `user_values_or_priorities_signal` remains unsolved by the current
  specialists.
- After the signature-only metadata filter, normal complex `$lolla` runs are
  provider-boundary clean; specialist probe provider-boundary behavior remains
  a separate explicit-model-call issue.

Boundaries held:

- normal `$lolla` remains unchanged;
- runtime specialist integration remains blocked;
- archive integration remains blocked;
- no `SKILL.md` changes;
- no prompt changes;
- no `archive_run.py` changes;
- no semantic coverage archive integration;
- no `conversation_understanding_ir.v0`;
- no user-values extractor;
- no graph DB, embeddings, chunking, memory layer, LLM judge,
  answer-quality scoring, provider-boundary policy change, or automatic
  human-review labels.

Next evidence gate:

- Do not build specialist runtime integration until there are 15-20
  full-modern archives.
- Re-run the broader specialist gate only when that clean full-modern sample
  exists and provider-boundary behavior is understood.
- Until then, treat specialists as preserved offline/research machinery, not
  product runtime behavior.

## Current PRD Progress

Sequence note: the PRD's original order put trigger-policy and control-plane
docs earlier. We intentionally pulled R10 Observatory parity forward because the
current product loop is manual: run Lolla, open Observatory, inspect the local
archive, then decide what to trust. That is a sequencing choice, not a product
boundary change.

| PRD item | Status | Current read |
|---|---:|---|
| R1: Agent-Facing Result Contract | Done | `agent_result.json` / `lolla_agent_result.v1` exists, is archived, copied to `/tmp`, indexed in `reasoning_trace.json`, documented, tested, and smoke-tested. |
| R2: Risk Modes | Metadata plus policy/fixture/plan/tests/eval/review clarity done | `LOLLA_AUDIT_MODE` accepts `quick`, `standard`, `deep`, `high_stakes`, and `stability`; normalized value persists as `risk_mode`; invalid explicit values fail before model calls. The pipeline remains mostly metadata-first. The agent-result contract already keeps otherwise clean `high_stakes` runs conservative with `caller_action: ask_user_first`. PR36 documents policy, PR37 adds fixtures, PR38 reviews them, PR39 plans high-stakes reliance/readiness tightening, PR40 locks the current conservative contract in tests, PR41 adds deterministic `evaluation.json` reliance-policy clarity, PR42 exposes that caveat in review-corpus records, PR43 validates reviewer interpretation with fixtures, PR44 adds manifest counts, PR45 records the anti-drift handoff, PR46 plans future approved high-stakes evidence, PR47 adds high-stakes evidence fixtures, and PR48 adds a manifest-only evidence-readiness analyzer without implementing enforcement. |
| R3: Trigger Policy For Agents | Deferred | Not urgent for current manual workflow. Keep for later external agent-builder docs. |
| R4: Control-Plane Integration Contract | Done | `lolla_control_input.v1` and `lolla_control_result.v1` now exist as optional local sidecars. External trace/action/approval metadata can be preserved and summarized without changing ordinary `$lolla` runs or making Lolla an approval/sandbox/policy system. |
| R5: Capture Adequacy Upgrade | Done | `capture_adequacy` / `lolla.capture_adequacy.v0` now makes capture shape, omitted windows, and critical capture problems visible across extraction, run health, agent result, reasoning trace, and evaluation. It does not reconstruct omitted turns or change capture strategy. Real `$lolla` smoke passed with full capture. |
| R6: Evaluation Methodology And Failure Taxonomy | Human-review v0 done; PR30-PR70 eval/design/test/docs seeds done | `docs/lolla-evaluation-methodology.md`, `docs/evals/lolla-human-review-v0.json`, `docs/evals/lolla-failure-taxonomy.md`, and `docs/evals/human-review-workflow.md` exist. PR14 added the human-owned label contract. PR15 added a synthetic-review boundary so subagents can help without becoming ground truth. PR16 added a validator and prompt so synthetic candidate outputs must match the human-review schema without becoming human labels. PR30 added the first human/product review seed over the six complex baseline runs. PR31 added the human-owned actionable-delta rubric. PR32 added seed adversarial pair fixtures. PR33 added a 14-record broader human-review corpus batch with 12 counted positives, one partial boundary record, and one degraded exclusion. PR34 designed the first-class user-values/priorities signal without implementing extraction. PR35 documented live-output hygiene policy without runtime changes. PR36 documented risk-mode behavior policy without runtime changes. PR37 added risk-mode fixture examples without runtime changes. PR38 reviewed those fixtures and added the high-stakes values-conflict fixture without runtime changes. PR39 planned the high-stakes reliance/readiness implementation path without runtime changes. PR40 added contract-lock tests without runtime changes. PR41 added deterministic evaluation-artifact clarity without runtime enforcement. PR42 added review-corpus surface integration without runtime enforcement. PR43 and PR44 verified reviewer interpretation and manifest visibility without runtime enforcement. PR45 records the current state and decision gates. PR46 plans future approved high-stakes evidence without running cases. PR47 adds paraphrase-only high-stakes evidence fixtures. PR48 adds a read-only manifest analyzer for high-stakes evidence readiness. PR49 plans a human-owned values/priorities worksheet without extraction, exports, runtime behavior, or judging. PR50 adds paraphrase-only worksheet fixtures without extraction, export code, runtime behavior, automatic labels, or judging. PR51 reviews those fixtures without code, extraction, automatic labels, runtime behavior, or judging. PR52 adds blank worksheet export structure without reading archives, extracting values, populating labels, changing runtime behavior, or judging. PR53 pilots human-filled worksheets on existing reviewed summaries without raw content, extraction, automatic labels, runtime behavior, or judging. PR54 reviews the pilot, marks the v0 worksheet lane complete for human-owned review, and pauses before extraction, memory, runtime integration, automatic labels, or judging. PR55 lands a Semantica-inspired accountability plan without implementing doctor/preflight, decision records, provenance maps, conflict registers, case graph exports, graph DBs, embeddings, memory, policy engines, automatic labels, answer-quality scoring, or judges. PR56 plans a future read-only doctor/preflight command without implementing the CLI, running `$lolla`, calling models, mutating archives, changing prompts, changing `SKILL.md`, or changing runtime behavior. PR57 implements the smallest read-only doctor CLI without running `$lolla`, calling models, mutating archives, changing prompts, changing `SKILL.md`, changing provider-boundary policy, approving high-stakes use, or judging answer quality. PR58 designs `lolla.audit_decision_record.v0` as a paraphrase-only local accountability projection without implementing an exporter, runtime integration, automatic labels, answer-quality scoring, or judges. PR59 reviews six paraphrase-only decision-record fixtures and marks the shape ready for a future read-only exporter design prototype with caveats, without implementing that exporter. PR60 designs `lolla.provenance_map.v0` as a local artifact-lineage shape without implementing a provenance exporter, archive reading, runtime integration, graph DB, memory, compliance claims, scoring, or judges. PR61 designs `lolla.review_conflict_register.v0` as a human-review-owned conflict surface without implementing an exporter, resolving conflicts, automating severity, enforcing policy, scoring, labeling, or judging. PR62 designs `lolla.case_graph.v0` as a future run-local case graph export/view shape without implementing an exporter, archive reading, runtime integration, graph DB, memory, GraphRAG, entity resolution, scoring, labeling, or judging. PR63 creates three paraphrase-only accountability-view fixture bundles without implementing exporters, reading archives, changing runtime behavior, scoring, labeling, or judging. PR64 reviews all three bundles, marks them pass, recommends only `audit_decision_record` for a later exporter-design decision, and still implements no exporter, runtime behavior, scoring, labeling, or judging. PR65 chooses that direction as a docs-only decision and recommends future PR66 without implementing it. PR66 implements the read-only audit decision record exporter without raw content, labels, scoring, judges, graph DB, memory, or runtime integration. PR67 reviews six smoke exports and recommends schema/exporter refinement for clearer empty PR31 bucket semantics before archive integration or automatic generation. PR68 implements that narrow refinement with population policy, per-bucket statuses, nested buckets, and semantic-field empty-meaning metadata without adding scoring, labels, judges, archive integration, or runtime behavior. PR69 re-runs the exporter review against refined output and confirms empty fields read as clear non-claims. PR70 closes the audit/accountability machinery lane as done enough for now and redirects the next phase to Product Delta Evidence. |
| R7: Deterministic Evaluation Artifact v0 | Done | `evaluation.json` / `lolla.evaluation.v0` is generated, copied to `/tmp`, indexed in `reasoning_trace.json`, and exposed through Observatory custody. It checks artifacts, schemas, custody, health, hygiene, and caller-policy consistency without judging advice quality. |
| R8: Calibrated Subjective Judges | Not started | Correctly deferred. Generic LLM judges may punish useful friction. PR30 supplies a six-run human-reviewed seed, PR31 defines actionable delta, PR32 supplies seed adversarial fixtures, PR33 broadens the human-reviewed corpus batch, PR34 designs values/priorities review context, PR35 keeps live-output hygiene honest, PR36 defines risk-mode reliance policy, PR37 adds risk-mode fixtures, PR38 reviews those fixtures, PR39 plans contract-first high-stakes reliance tightening, PR40 locks the current contract in tests, PR41 clarifies high-stakes evaluation artifacts, PR42 exposes the caveat to review-corpus records, PR43 validates reviewer interpretation with fixtures, PR44 makes aggregate absence/presence visible, PR45 records the anti-drift handoff, PR46 plans future high-stakes evidence creation without running it, PR47 adds paraphrase-only high-stakes fixtures, PR48 adds deterministic evidence-readiness analysis, PR49 makes values/priorities reviewable by humans before extraction, PR50 tests that worksheet with paraphrase-only fixtures, PR51 reviews fixture quality, PR52 adds blank deterministic worksheet structure, PR53 pilots human-filled worksheets, PR54 closes the worksheet lane at human-owned v0, PR55 records accountability primitives as inspectability aids rather than judge/scoring surfaces, PR56 plans a deterministic doctor/preflight readiness report, PR57 implements that report as a read-only CLI, PR58 designs a decision-delta record, PR59 reviews six paraphrase-only fixtures, PR60 designs a provenance map, PR61 designs a review conflict register, PR62 designs a case graph export/view shape, PR63 creates combined accountability-view fixtures, PR64 reviews those fixtures without creating a judge, labeler, score, exporter, graph DB, or runtime feature, PR65 recommends only a future decision-record exporter without starting it, PR66 implements that exporter without labels, scoring, judges, graph DB, memory, or runtime integration, PR67 reviews smoke outputs without adding a judge or score, PR68 clarifies field population without adding a judge, score, or labeler, PR69 reviews refined outputs without adding a judge, score, or labeler, and PR70 closes the machinery lane without adding a judge, score, or labeler. Judge automation remains deferred. |
| R9: Archive Corpus And Stability Workflow | Corpus/readiness/extraction/semantic surveys done | PR13 adds deterministic JSONL corpus + manifest export around `agent_result.json`, `evaluation.json`, capture adequacy, run health, provider-boundary status, usage/model metadata, artifact availability, and optional control-plane summaries. PR15 adds deterministic review-readiness tiers and batch recommendations. Later work added extraction adequacy corpus export, semantic coverage corpus export, and local findings analyzers. |
| R10: Observatory Parity | Done for current custody loop | Archive parity audit, selected archived sidecar APIs, selected-run custody UI, active-run custody sidecar parity, and evaluation custody parity are landed. Remaining known gap: selected archived dashboard render/readback can still hang after the full case payload resolves. |
| R11: Human Capability Surface | Not started | Later: optional "what to learn from this audit" surface. |
| R12: Public Docs Update | Strong progress | README, HOW_IT_WORKS, pitch, PRD, eval methodology, control-layer integration, agent-result contract, and archive parity docs now exist or have been updated. |

## Completed / Merged Foundation

Merged stack now on `origin/main`:

```text
407cc2c Agent result contract
30e9ad0 / 502e3c0 Risk mode metadata
bbdbed3 Observatory archive parity audit
b1ff0ad Selected archive sidecar APIs
25ddf45 Observatory selected-run custody panel
23672b4 Active-run custody sidecar parity
57b47ff Provider-boundary health classification
adfa9fa Provider-boundary conservative reclassification
af31e4a Deterministic evaluation artifact v0
070be72 Evaluation custody Observatory parity
9e499ff Capture adequacy metadata
385019a Evaluation contained-provider degraded policy
10397f4 SKILL.md conductor artifact-chain refresh
b196714 Control-plane integration contract
116507b Archive review corpus export
de08812 Human review taxonomy workflow
2b833d0 Review readiness tiers and synthetic review boundary
18d044b Synthetic review validator and prompt
```

### PR 1: Agent Result Contract

Commit:

- `407cc2c Add agent-facing Lolla result contract`

What changed:

- Added `agent_result.json` as `lolla_agent_result.v1`.
- Wrote it into archived runs.
- Copied it to `/tmp/lolla_<run_id>_agent_result.json`.
- Indexed it in `reasoning_trace.json` as `agent_facing_result`.
- Added public docs in `docs/lolla-agent-result-contract.md`.

Why it matters:

- Agents and future callers no longer need to parse the memo or Observatory to
  know the run status, `caller_action`, core deltas, human questions, artifact
  pointers, and usage summary.

Did not change:

- audit prompts,
- Step 6 reasoning,
- model calls,
- cost,
- Step 7 behavior,
- high-stakes policy,
- evaluation behavior.

Validation:

- Focused tests passed.
- A real `$lolla` smoke produced `lolla_agent_result.v1`.
- Partial run health mapped conservatively to
  `caller_action: "do_not_use_run_degraded"`.

### PR 2: Risk Mode Metadata

Commits:

- `30e9ad0 Add Lolla audit mode metadata`
- `502e3c0 Clarify risk mode metadata scope`

What changed:

- Added normalized `LOLLA_AUDIT_MODE`.
- Accepted values:
  - `quick`
  - `standard`
  - `deep`
  - `high_stakes`
  - `stability`
- Missing or empty mode defaults to `standard`.
- Invalid explicit mode fails before model calls.
- Persisted `risk_mode` into:
  - `result.json`,
  - `agent_result.json`,
  - `reasoning_trace.json`,
  - archive metadata,
  - run-event metadata.

Why it matters:

- The harness can now record caller/operator intent without pretending behavior
  has changed.

Did not change:

- prompts,
- cost,
- Step 7 behavior,
- high-stakes warnings,
- evaluation strictness,
- capture strictness,
- replay/comparison behavior.

Validation:

- Focused tests passed.
- Invalid mode was verified to fail before model calls.

### PR 3: Observatory Archive Parity Audit

Commit:

- `bbdbed3 Audit Observatory archive parity`

What changed:

- Added a small Observatory risk-mode surfacing fix.
- Added `docs/observatory-archive-parity-audit.md`.
- Confirmed archive discovery works.
- Identified the real parity gap:

```text
The SPA can list/load archived runs, but deeper /audit/* telemetry pages are
still scoped to the active served run.
```

Why it matters:

- The problem became precise. "Local history is broken" is now more accurately:

```text
local history can find archived runs, but full custody inspection does not yet
follow the selected archived run.
```

Did not change:

- Observatory UI design,
- audit behavior,
- model calls,
- artifact generation,
- evaluation behavior.

Validation:

- Focused Observatory tests passed.
- Real archive endpoint smoke confirmed `risk_mode`, run health, and usage data
  surfaced.

### PR 4: Selected Archived Sidecar APIs

Commit:

- `b1ff0ad Add selected archive sidecar APIs`

What changed:

- Added read-only selected-archive sidecar endpoints:
  - `/api/case/<id>/agent-result`
  - `/api/case/<id>/reasoning-trace`
  - `/api/case/<id>/events`
  - `/api/case/<id>/memo`
  - `/api/case/<id>/graph-survival`
- Kept sidecar resolution fixed to known filenames inside the selected run
  directory.
- Added missing-sidecar 404 behavior.
- Added archive-path escape tests.
- Bound the Observatory server to `127.0.0.1` so the "local-only" claim is
  technically true.

Why it matters:

- Selected archived run custody artifacts are now reachable without pretending
  the `/audit/*` pages already follow SPA selection.

Did not change:

- UI design,
- audit behavior,
- model calls,
- artifact generation,
- evaluation behavior,
- control-plane schema,
- replay behavior,
- Step 7 behavior.

Validation:

- Focused tests passed.
- Real archive smoke confirmed all new sidecar endpoints returned expected
  payloads.

### PR 5: Observatory Selected-Run Custody Panel

Commit:

- `25ddf45 Add Observatory selected-run custody panel`

What changed:

- Consume the selected archived sidecar APIs in the Observatory SPA.
- When an archived case is selected, show a compact custody/inspection panel for:
  - `agent_result.json`,
  - `reasoning_trace.json`,
  - `run_events.json`,
  - `memo.md`,
  - `graph_survival_report.*`.

Expected behavior:

- Available artifacts show status, links, or lightweight previews.
- Missing artifacts show "unavailable" rather than broken UI.
- Selected archived run B must show B's sidecars, not active run A's.
- The custody panel can render as a compact floating panel when the selected
  archived dashboard/sidebar is stuck on `Loading...`, then relocate into the
  sidebar if the sidebar later appears.

Non-goals:

- no Observatory redesign,
- no `/audit/*` selected-run rewrite yet,
- no eval artifact,
- no new artifact generation,
- no model calls,
- no Step 7 behavior,
- no risk-mode behavior,
- no control-plane schema.

Why it matters:

- It completes the current manual inspection loop:

```text
run Lolla manually
-> open Observatory
-> select local history item
-> inspect selected run custody artifacts
```

PM read:

- Product alignment is good.
- Scope is appropriately boring: no redesign, no audit behavior, no model calls,
  no eval, no new artifact generation.
- The implementation uses the sidecar APIs from PR 4 instead of pretending the
  deeper `/audit/*` pages already follow selected archived runs.
- This moves R10 but does not expand Lolla into a guardrail, sandbox, policy
  engine, fact-checker, or generic judge.

SKILL.md alignment:

- Do not add selected-run custody-panel mechanics to `SKILL.md`.
- `SKILL.md` is already doing the right job as a conductor surface: it mentions
  audit-mode setup, the durable artifact chain, Observatory, archive, agent
  result, and reasoning trace.
- R10 implementation details belong in `docs/how-it-works/live-flow.md`,
  `docs/observatory-archive-parity-audit.md`, and this progress report.
- Keeping PR 5 out of `SKILL.md` preserves the Track 1 defragmenting direction
  and avoids making the executable instruction file large again.

Verification already run:

```bash
PYTHONPATH=. pytest -q \
  tests/test_pr3_observatory_panels.py \
  tests/test_audit_mode.py \
  tests/test_agent_result.py \
  tests/test_reasoning_trace_archive.py \
  tests/test_skill_contract.py \
  tests/test_archive_run_case_identity.py \
  tests/test_archive_run_v60_telemetry.py \
  tests/test_finalize_trusted_transcript.py

python3 -m py_compile observatory/serve_result.py
git diff --check origin/main..HEAD
```

Result:

```text
102 passed
compile clean
diff check clean
```

Real browser/server smoke evidence:

- Active served run A:
  `<archive-root>/accept-founding-engineer-role/20260624T125142Z_2aa96f/result.json`
- Selected archived run B:
  `archive:founder-months-runway-flat:20260624T192039Z_c6c235`
- After selecting B, server logs showed selected-run sidecar requests with
  encoded archive id and `200` responses for:
  - `/agent-result`
  - `/reasoning-trace`
  - `/events`
  - `/memo`
  - `/graph-survival`
- An older real archived run,
  `archive:mid-level-consultant-report-2:20260624T133814Z_b4a2dd`, returned
  `404` for missing `agent_result.json` and `200` for sidecars that existed.
  That supports the "unavailable rather than broken" path.
- Stronger Playwright proof passed:
  - performed the real click on the founder archive case,
  - deliberately delayed the heavy selected `/api/case/archive:...` response,
  - inspected only `.lolla-custody-panel`, avoiding the known selected
    dashboard render/readback hang.
- The clicked archive produced a floating panel with:
  - 5 rows,
  - `agent_result.json` with `lolla_agent_result.v1`, `status partial`,
    `caller do_not_use_run_degraded`, `mode standard`,
  - `reasoning_trace.json` with 19 artifacts,
  - `run_events.json`,
  - `memo.md`,
  - `graph_survival_report.*`,
  - 5 selected-archive links,
  - 0 `lolla-audit` links.

Merge read:

- PR 5 was mergeable and has been fast-forwarded to `origin/main`.
- The custody panel works from the real archived-case click path and stays
  available even when the main selected dashboard is stuck on `Loading...`.
- The remaining selected dashboard render/readback instability still exists
  after the full selected-case payload resolves, but it is no longer a blocker
  for this custody-panel bridge.

Follow-up issue after merge:

- Stabilize selected archived dashboard render/inspection so the main selected
  case view itself can be read/screenshot reliably after the full payload
  resolves. Keep that as a separate small Observatory lifecycle PR.

### PR 6: Active-Run Custody Sidecar Parity

Commit:

- `23672b4 Fix active-run custody sidecar resolution`

Why it exists:

- The 2026-06-25 real `$lolla` smoke showed the artifact chain was healthy
  enough to inspect:
  - `agent_result.json` existed,
  - `reasoning_trace.json` indexed the agent result,
  - `run_events.json` recorded the archive path,
  - the archive held the expected sidecars.
- But active `lolla-audit` custody endpoints returned `404`:
  - `/api/case/lolla-audit/agent-result`
  - `/api/case/lolla-audit/reasoning-trace`
  - `/api/case/lolla-audit/events`
  - `/api/case/lolla-audit/memo`
  - `/api/case/lolla-audit/graph-survival`
- Selected archived custody endpoints already worked. The bug was active-run
  sidecar resolution, not artifact generation.

What changed:

- Selected-case sidecar APIs now branch on whether the case is the active
  current `lolla-audit` run or a selected archived run.
- For active `lolla-audit`, sidecar lookup supports:
  - prefixed `/tmp/lolla_<run_id>_<filename>` files,
  - archive fallback through
    `run_events.json -> archive_completed.details.archive_path`,
  - same-directory fixed filenames for archive-style active result layouts.
- For selected archived runs, behavior remains strict:
  - fixed known filenames,
  - inside the selected archive directory,
  - no broad path lookup.
- The route layer now passes `is_current` from `_load_case_result(case_id)` into
  the sidecar helpers.

Why it matters:

- The custody panel can now inspect the run the user just finished, not only
  older archived runs.
- This completes the current manual inspection path at the sidecar/API level:

```text
finish Lolla run
-> open Observatory
-> inspect active lolla-audit custody artifacts
-> select older archive
-> inspect archived custody artifacts
```

Non-goals preserved:

- no `SKILL.md` changes,
- no audit behavior changes,
- no prompt changes,
- no model calls,
- no provider-boundary health policy,
- no risk-mode behavior changes,
- no eval artifact,
- no control-plane schema,
- no UI redesign.

Validation:

- Focused Observatory tests:

```text
70 passed
```

- Full focused suite:

```text
107 passed
compile clean
diff check clean
```

- Live endpoint smoke against
  `/tmp/lolla_20260625T081013Z_9580b5_result.json` confirmed:
  - active `lolla-audit` returns `200` for all five custody endpoints,
  - selected archived founder run still returns `200` for all five custody
    endpoints.

PM read:

- PR 6 was mergeable and has been fast-forwarded to `origin/main`.
- It fixes a crisp inspection-loop bug without expanding product scope.
- The security posture looks preserved because selected archived runs still use
  strict archive-directory containment, and active runs only gain fixed
  known-filename lookup plus archive fallback from local run events.

### PR 7A: Provider-Boundary Health Classification

Branch:

- `pr/provider-boundary-health-policy`

Commit:

- `57b47ff Classify provider-boundary health metadata`

Why it exists:

- Real runs frequently show `vendor_boundary_reasoning_leak` because the model
  provider returned reasoning details despite reasoning being disabled.
- Before changing `caller_action` or `run_health.overall`, we need to know
  whether this is:
  - a provider-boundary warning only,
  - product-output contamination,
  - live-output contamination,
  - archive/custody contamination.

What changed:

- Added `provider_boundary_health` metadata with explicit statuses:
  - `clean`,
  - `warning_unknown_persistence`,
  - `warning_contained`,
  - `confirmed_contamination`.
- Attached the metadata to `run_health.provider_boundary_health`.
- Refreshes the classification after product/live hygiene, so pipeline-time
  state can be `warning_unknown_persistence` and archive-time state can become
  `warning_contained` or `confirmed_contamination`.
- Exposes a compact summary in `agent_result.json`.
- Carries enriched health through `reasoning_trace.json`.
- Updates public docs for agent-result and pipeline-lane health fields.

What it deliberately does not change:

- `caller_action`,
- `run_health.overall`,
- prompts,
- model routing,
- Step 7,
- risk-mode behavior,
- eval artifacts,
- control-plane schema,
- Observatory UI,
- `SKILL.md`.

Validation:

```text
142 passed
compile clean
diff check clean
```

Additional real-run sanity check:

- Rebuilding the agent result from the 2026-06-25 smoke archive returns:
  - `status: partial`,
  - `caller_action: do_not_use_run_degraded`,
  - `provider_boundary_health.status: warning_contained`.

PM read:

- PR 7A was mergeable and has been fast-forwarded to `origin/main`.
- It is the right first move: classify and expose the provider-boundary issue
  without weakening the conservative caller contract.
- It should not be followed by an automatic green-light change until we decide
  the exact PR7B policy.

## Recent Foundation PRs

### PR 7B: Provider-Boundary Conservative Reclassification

Branch:

- `pr/provider-boundary-reclassification-decision`

Commit:

- `adfa9fa Keep contained provider-boundary warnings conservative`

Policy choice:

- Keep contained provider-boundary warnings conservative.
- Do not add a new caller action.
- Do not introduce `ok_with_warnings`.
- Do not change `run_health.overall`.
- Do not change `caller_action`.

What changed:

- Pure contained provider-boundary warnings now get a more specific
  `status_reason`:

```text
provider-boundary warning is contained; conservative policy still requires inspection
```

- Pure contained provider-boundary warnings also get a more specific note in
  `agent_result.json`.
- The special case only applies when the contained provider-boundary warning is
  the only partial/degraded/critical cause.
- Runs with another partial issue, such as `bullshit_index_partial`, stay on
  the generic partial reason.

What it deliberately does not change:

- `caller_action`,
- `run_health.overall`,
- `provider_boundary_health` classification,
- prompts,
- model routing,
- Step 7,
- risk-mode behavior,
- eval artifacts,
- control-plane schema,
- Observatory UI,
- `SKILL.md`.

Validation:

```text
48 passed
compile clean
diff check clean
```

Additional real-run sanity check:

- Rebuilding the agent result from the 2026-06-25 smoke archive returns:
  - `status: partial`,
  - `status_reason: run_health.overall is partial`,
  - `caller_action: do_not_use_run_degraded`,
  - `provider_boundary_health.status: warning_contained`.
- This is correct because that real run also has another partial cause, so
  provider-boundary is not the only reason for partial health.

PM read:

- PR 7B has landed on `origin/main`.
- It makes the policy decision explicit while preserving conservative caller
  behavior.
- This closes the immediate provider-boundary health-policy loop. A future
  warning-bearing usable action can still be designed later, but it is no
  longer the next necessary PR.

### PR 8: Deterministic Evaluation Artifact v0

Branch:

- `pr/deterministic-evaluation-artifact-v0`

Commit:

- `af31e4a Add deterministic evaluation artifact`

What changed:

- Added `evaluation.json` with schema `lolla.evaluation.v0`.
- Generates it during archive creation after `agent_result.json` and the first
  `reasoning_trace.json` exist.
- Writes `/tmp/lolla_<run_id>_evaluation.json` as a convenience copy.
- Regenerates `reasoning_trace.json` so `evaluation.json` is indexed as
  `deterministic_evaluation`.
- Checks deterministic run-readiness only:
  - required artifact presence,
  - schema versions,
  - agent-result caller policy,
  - reasoning-trace custody,
  - artifact hashes,
  - product/live hygiene states,
  - provider-boundary policy consistency,
  - archive readiness.

What it deliberately does not change:

- no LLM judge,
- no advice-quality scoring,
- no helpfulness/coherence/correctness scoring,
- no model calls,
- no prompt changes,
- no Step 7 changes,
- no risk-mode behavior changes,
- no control-plane schema,
- no Observatory redesign,
- no `SKILL.md`.

Validation:

```text
148 passed
compile clean
diff check clean
```

Additional real-run sanity check:

- Building an evaluation for the older 2026-06-25 smoke archive returns:
  - `schema_version: lolla.evaluation.v0`,
  - `overall: warn`,
  - `caller_readiness: do_not_use`.
- The warnings are reasonable for that older archive:
  - provider-boundary metadata was not present yet,
  - live output was `not_checked`,
  - provider-boundary policy was therefore `unknown`.

PM read:

- PR 8 has landed on `origin/main`.
- It lands the correct kind of first eval: a deterministic envelope/readiness
  receipt, not a subjective judge.
- The next narrow follow-up should expose `evaluation.json` through the same
  Observatory custody path as the other run artifacts.

### PR 9: Evaluation Custody Observatory Parity

Branch:

- `pr/evaluation-custody-observatory-parity`

Commit:

- `070be72 Expose evaluation artifact in Observatory custody`

What changed:

- Added read-only selected-case endpoint:

```text
/api/case/<id>/evaluation
```

- Reuses the existing sidecar resolver:
  - active `lolla-audit` can resolve `/tmp/lolla_<run_id>_evaluation.json`,
  - active `lolla-audit` can fall back through
    `run_events.json -> archive_completed.details.archive_path`,
  - selected archived runs resolve fixed `evaluation.json` inside the selected
    archive directory only,
  - missing `evaluation.json` returns `404`,
  - archive escape protection remains in force.
- Adds `evaluation.json` to the selected-run custody panel with compact preview:

```text
lolla.evaluation.v0 · overall <status> · readiness <caller_readiness>
```

What it deliberately does not change:

- no evaluation schema changes,
- no new evaluation checks,
- no archive-generation changes,
- no model calls,
- no LLM judge,
- no advice-quality scoring,
- no `/audit/*` selected-run rewrite,
- no Observatory redesign,
- no `SKILL.md`.

Validation:

```text
148 passed
compile clean
diff check clean
```

Additional live-route sanity check:

- Against older pre-PR8 archives, `/api/case/<id>/evaluation` returns clean
  `404` with a sidecar-missing message. This is acceptable legacy behavior and
  should render as unavailable rather than broken.
- Tests cover `200` behavior for active tmp, active archive fallback, selected
  archived run, missing sidecar, archive escape, and custody-panel injection.

### PR 10: Capture Adequacy Manifest Upgrade

Branch:

- `pr/capture-adequacy-manifest-upgrade`

Commit:

- `9e499ff Add capture adequacy metadata`

Why it exists:

- The manual inspection loop can now expose the run's artifacts, health,
  evaluation, and trace.
- The next weakest point is upstream: whether Lolla captured enough of the
  conversation for the audit to deserve trust.
- Long conversations can preserve opening/recent turns while omitting middle
  turns that may contain constraints, reversals, stakeholder facts, or dropped
  threads.

What changed:

- Added deterministic capture adequacy metadata with schema
  `lolla.capture_adequacy.v0`.
- `run_extract.py` emits `capture_adequacy`.
- `run_pipeline.py` carries it into `result.run_health`.
- `agent_result.json` exposes a compact summary without raw transcript text.
- `reasoning_trace.json` includes capture adequacy in its capture section.
- `evaluation.json` checks capture adequacy deterministically:
  - missing metadata warns for older archives,
  - warning-level capture warns,
  - critical capture is blocking.

Important policy nuance:

- PR10 makes capture loss visible. It does not make capture smarter yet.
- Ordinary first-N-plus-last-N truncation can warn in metadata/evaluation
  without necessarily degrading the whole run-health state.
- Critical capture problems stay conservative and can block caller readiness.

What it deliberately does not change:

- no `SKILL.md`,
- no model calls,
- no LLM judge,
- no advice-quality scoring,
- no long-conversation summarizer,
- no decision-aware capture rewrite,
- no Observatory redesign,
- no control-plane schema.

Validation:

```text
226 passed
compile clean
diff checks clean
```

Additional legacy-archive sanity check:

- Building `evaluation.json` against the older 2026-06-25 smoke archive returns:
  - `overall: warn`,
  - `caller_readiness: do_not_use`,
  - capture adequacy checks warning that metadata is missing.
- Building `agent_result.json` for the same older archive returns:
  - `capture_adequacy.status: unknown`.
- This is correct backwards compatibility: older archives warn instead of
  crashing or pretending capture adequacy was known.

PM read:

- PR10 has landed on `origin/main`.
- It is the right boring version of capture adequacy: first make omitted capture
  visible, then decide whether to change capture strategy.
- Real `$lolla` smoke confirmed the new capture metadata survives extraction,
  result health, agent result, reasoning trace, archive, evaluation, and active
  Observatory custody.

Real smoke:

- Run id: `20260625T125625Z_aae54e`
- Archive:
  `<archive-root>/prioritize-control-plane-contract/20260625T125625Z_aae54e`
- Capture adequacy:
  - `schema_version: lolla.capture_adequacy.v0`
  - `status: good`
  - `capture_strategy: full`
  - `declared_turn_count: 4`
  - `captured_turn_count: 4`
  - `omitted_turn_count: 0`
  - `omitted_windows: []`
  - `risk_flags: []`
- Evaluation capture checks:
  - `capture_adequacy_schema_version: pass`
  - `capture_adequacy_status: pass`
- Active Observatory custody returned `200` for:
  - `/agent-result`
  - `/reasoning-trace`
  - `/events`
  - `/memo`
  - `/graph-survival`
  - `/evaluation`

Smoke note:

- `/tmp/lolla_<run_id>_reasoning_trace.json` is still not emitted as a temp
  convenience copy. The archived `reasoning_trace.json` exists and active
  Observatory serves it correctly. Track this as minor artifact-parity polish,
  not a PR10 blocker.

### PR 10b: Evaluation Contained-Provider Degraded Policy

Branch:

- `pr/evaluation-contained-provider-degraded-policy`

Commit:

- `385019a Fix contained provider-boundary evaluation policy`

Why it exists:

- The PR10 real smoke exposed a deterministic-evaluation false fail.
- `provider_boundary_contained_policy` failed when provider-boundary health was
  `warning_contained` but the run was already `degraded` for another
  conservative reason.
- That is too strict: exact `partial` should be required for pure
  provider-boundary-only partial runs, not for runs that are degraded/incomplete
  for additional causes while still keeping `caller_action` conservative.

What changed:

- For pure contained provider-boundary-only runs, the evaluation still expects:
  - `status: partial`,
  - `caller_action: do_not_use_run_degraded`.
- For contained provider-boundary warnings plus other conservative run-health
  causes, the evaluation now accepts:
  - `status: partial`,
  - `status: degraded`,
  - or `status: incomplete`,
  - as long as `caller_action: do_not_use_run_degraded`.
- Added a regression test for warning-contained plus `no_fingerprint` degraded
  health.

What it deliberately does not change:

- no `caller_action` relaxation,
- no `run_health.overall` relaxation,
- no provider-boundary classification change,
- no model calls,
- no LLM judge,
- no advice-quality scoring,
- no Observatory changes,
- no `SKILL.md`.

Validation:

```text
32 passed
compile clean
diff checks clean
```

Real-archive rebuild after the fix:

```text
schema_version: lolla.evaluation.v0
overall: warn
caller_readiness: do_not_use
capture_adequacy_schema_version: pass
capture_adequacy_status: pass
provider_boundary_contained_policy: pass
provider_boundary_policy: warn
```

PM read:

- PR10b has landed on `origin/main`.
- It fixes an evaluation-policy false fail without weakening the conservative
  machine-caller contract.
- The deterministic eval no longer false-fails a conservative degraded run, but
  still leaves that run non-actionable for machine callers.

## Latest Landed PR

### PR 12: Control-Plane Integration Contract v0

Branch:

- `pr/control-plane-integration-contract-v0`

Commit:

- `b196714 Add control-plane integration contract`

Why it exists:

- R4 asks Lolla to fit beside external agent frameworks, approvals, proxies,
  sandboxes, identity scopes, and trace stores without becoming any of them.
- The goal is optional metadata preservation and handoff, not enforcement.

What changed:

- Adds `engine/system_b/control_plane.py`.
- Defines:
  - `lolla_control_input.v1`,
  - `lolla_control_result.v1`,
  - caller-action to control-plane outcome mappings,
  - compact control metadata summaries.
- Archive now preserves optional `/tmp/lolla_<run_id>_control_input.json` as
  `control_input.json`.
- Archive generates `control_result.json` only when control input exists.
- Archive writes `/tmp/lolla_<run_id>_control_result.json` as a convenience copy
  only when generated.
- `agent_result.json` adds optional `control_context` only when control input
  exists.
- `reasoning_trace.json` indexes:
  - `control_input.json` as `control_plane_input`,
  - `control_result.json` as `control_plane_result`,
  - compact `process.control_plane` metadata when supplied.

Boundary and privacy posture:

- Ordinary `$lolla` runs remain unaffected.
- Lolla does not approve actions, enforce approvals, sandbox execution, proxy
  traffic, grant credentials, or replace policy engines.
- Raw proposed-action argument values are preserved only in local
  `control_input.json`; public/agent-facing summaries expose argument keys, not
  values.

What it deliberately does not change:

- no auto-triggering,
- no approval enforcement,
- no sandboxing,
- no proxy behavior,
- no tool execution,
- no model calls,
- no prompt changes,
- no risk-mode behavior,
- no eval judges.

Validation:

```text
157 passed
compile clean
diff checks clean
```

PM read:

- PR12 has landed on `origin/main`.
- It implements the PRD's R4 v0 correctly: optional, vendor-neutral,
  local-first, additive, and non-enforcing.
- The main operational caveat is expected and documented: raw external
  proposed-action metadata lives in `control_input.json`, so that artifact must
  be treated as local/sensitive.

Next PRD-backed choices after PR12:

- R6: evaluation methodology human-review pack and first failure taxonomy.
- R9: archive corpus/stability export expansion around `agent_result.json`,
  `evaluation.json`, capture adequacy, control metadata, and repeated-run
  grouping.
- R10 polish: selected archived dashboard lifecycle stabilization.
- R3 trigger policy docs only if external agent-builder onboarding becomes
  urgent.

Research/backlog note:

- The human-exception / omitted-hinge idea is not currently an implementation
  item in this PRD. It can inform future thinking or a PRD revision, but the
  current R11 "Human Capability Surface" is narrower: an optional compact
  "What To Learn From This Audit" memo/Observatory section.

## Current Product Work

### Synthetic Review Pilot After PR15

Pilot folder:

- `reviews/synthetic/pr15-modern-batch-2026-06-26/`

Why it exists:

- R9 now has a corpus export, but not every archive is equally reviewable.
- R6 now has a human-owned review taxonomy, but we want to use subagents as
  review aids without confusing their output with `lolla.human_review.v0`.
- The first synthetic rehearsal showed that older archives can support
  answer-level practice, but most do not support full custody review.

What PR15 changed:

- Adds deterministic review-readiness fields to each corpus record:
  - `review_readiness_tier`,
  - `content_review`,
  - `custody_review`,
  - `batch_recommendation`.
- Adds manifest aggregate counts for those fields.
- Defines four tiers:
  - `full_modern_reviewable`,
  - `modern_partial_reviewable`,
  - `legacy_content_reviewable`,
  - `not_reviewable`.
- Defines batch recommendations:
  - `recommended_modern_review_batch`,
  - `recommended_legacy_rehearsal_batch`,
  - `exclude_or_needs_backfill`.
- Adds `docs/evals/lolla-synthetic-review-v0.json` as the tiny boundary schema
  for subagent/synthetic review notes.
- Updates evaluation docs so synthetic notes may propose candidate labels but
  may not populate `lolla.human_review.v0` without human ratification.

Boundary and privacy posture:

- No model calls.
- No LLM judge.
- No advice-quality score.
- No approval decision.
- No automatic agent-readiness label.
- No capture/chunking redesign.
- No human-exception / omitted-hinge implementation.
- No runtime `$lolla` behavior change.
- Human review stays human-owned. Subagents can produce rehearsal notes,
  candidate labels, QA notes, or disagreement reports.

PR15 validation:

```text
43 focused tests passed locally during PM review
compile clean
JSON schema docs parse cleanly
diff checks clean
no SKILL.md diff
real local export produced 63 records
```

Real local export counts:

```text
full_modern_reviewable: 1
modern_partial_reviewable: 14
legacy_content_reviewable: 46
not_reviewable: 2

content_review_available_count: 61
custody_review_available_count: 1

recommended_modern_review_batch: 15
recommended_legacy_rehearsal_batch: 46
exclude_or_needs_backfill: 2
```

Pilot read:

- PR15 is merged.
- The first 15-record synthetic pilot ran with three independent subagents.
- Subagents broadly agreed that Lolla added useful friction across the batch.
- The pilot exposed two next-step issues:
  - the synthetic prompt used a wrong severity vocabulary before correction,
  - the workflow needs a clearer rule for answer-level pass versus
    run-envelope/live-output failure.

Implemented follow-up:

```text
PR16: Synthetic Review Output Validator + Pilot Prompt Fix
```

PR16 validated synthetic outputs against `lolla.human_review.v0` allowed values
when they include `candidate_human_review`, added a corrected synthetic-review
prompt/template, and clarified that synthetic outputs are not human-review
ground truth.

### Validated Synthetic Pilot After PR16

Pilot folder:

- `reviews/synthetic/pr16-validated-modern-batch-2026-06-26/`

Status:

```text
completed
```

What PR16 changed:

- Added `engine/system_b/synthetic_review.py`.
- Added validation for `lolla.synthetic_review.v0`.
- Required synthetic `candidate_human_review` labels to validate against
  `lolla.human_review.v0`.
- Rejected invalid severity values such as `minor`, `material`, and `unclear`.
- Rejected blank candidate labels in completed synthetic output.
- Added `docs/evals/synthetic-review-prompt-template.md`.

What the validated pilot showed:

- Three independent subagents completed the same 15-record modern batch.
- All three reported validator-passing outputs.
- The PR15 severity-vocabulary problem did not recur.
- Lolla's useful-friction signal remained strong across the batch.
- No reviewer treated the batch as autonomous-agent-ready.
- The main remaining disagreement is review-surface policy, not schema
  validity.

Findings:

- `reviews/synthetic/pr16-validated-modern-batch-2026-06-26/findings.md`

Stable disagreements to resolve:

- Records 13 and 15: saved answer usefulness versus live-output machinery leak.
- Record 1: degraded/eval-fail run envelope versus answer-level usefulness.
- Record 7: degraded envelope and quote-fabrication validation caveat.
- Record 8: high-stakes unsupported legal/domain claim risk.

Recommended next PR:

```text
PR17: Review Surface Policy + Validated Pilot Findings
```

Preferred shape:

- docs/workflow first,
- no runtime behavior,
- no LLM judge,
- no capture/chunking change,
- no human-exception implementation.

Clarify:

- answer-level review,
- run-envelope/custody review,
- live-output hygiene review,
- agent-readiness review.

If docs-only clarification is not enough for future corpus analysis, consider a
tiny additive schema field such as `review_surface` or `surface_findings`, but
do not start there unless the ambiguity blocks validation.

### PR17: Review Surface Policy + Validated Pilot Findings

Branch:

- `pr/review-surface-policy-validated-pilot`

Commit reviewed:

- `d07c2f86 Clarify review surface policy for synthetic pilots`

Status:

```text
merged to origin/main; Pilot 3 completed
```

What changed:

- `docs/evals/human-review-workflow.md` now explicitly separates:
  - answer-level review,
  - run-envelope/custody review,
  - live-output hygiene review,
  - agent-readiness review.
- `docs/evals/synthetic-review-prompt-template.md` now uses the same review
  surface language and asks synthetic reviewers to summarize surface conflicts
  in `qa_notes`.
- `docs/evals/pr16-validated-synthetic-pilot-findings.md` captures the
  validated Pilot 2 findings in checked-in docs.
- `docs/lolla-evaluation-methodology.md` links the finding and names review
  surface ambiguity as the lesson.

Boundary preserved:

- no `SKILL.md` change,
- no `$lolla` runtime change,
- no schema fields added,
- no model calls,
- no LLM judge,
- no automatic `human_review`,
- no automatic agent-readiness label,
- no capture/chunking work,
- no Observatory work.

Verification:

```text
19 focused tests passed
JSON docs parse cleanly
diff checks clean
docs-only PR
```

PM read:

- PR17 does the right small thing.
- It names the ambiguity before we build machinery on top of it.
- Pilot 3 showed the docs-only surface clarification was enough for the old
  Records 13/15 dispute.
- Do not add `surface_findings` yet.
- The next remaining policy issue is narrower: when should the
  agent-readiness label be `no` versus `with_human_review` for high-stakes,
  degraded, or custody-limited runs?

### Pilot 3: Disputed Surface Rehearsal After PR17

Pilot folder:

- `reviews/synthetic/pr17-disputed-surface-pilot-2026-06-26/`

Scope:

```text
five disputed records from the PR16 validated modern batch
```

Validation:

```text
reviewer-a.json PASS
reviewer-b.json PASS
reviewer-c.json PASS
```

What changed:

- The old disagreement on records 13 and 15 collapsed into a shared surface
  summary:

```text
answer=pass; envelope=warn/degraded; live_output=fail; agent=with_human_review
```

- Record 1 became cleanly separable:

```text
answer=pass; envelope=fail; agent=no
```

- Record 8 became a true answer-level failure:

```text
unsupported_new_claim; agent=no
```

Remaining disagreement:

- Record 7 still split on the agent-readiness label:
  - one reviewer chose `no`,
  - two reviewers chose `with_human_review`.

PM read:

- PR17 worked.
- The surface policy is now good enough without schema changes.
- PR18 implements the tiny docs-only clarification for agent-readiness labels.

```text
When does degraded/high-stakes/custody-limited mean no rather than
with_human_review?
```

### PR18: Agent-Readiness Label Policy v0

Branch:

- `pr/agent-readiness-label-policy-v0`

Commit reviewed:

- `37ab38f Clarify agent readiness review labels`

Status:

```text
merged to origin/main
```

What changed:

- `docs/evals/human-review-workflow.md` clarifies the agent-readiness values
  `yes | with_human_review | no | unclear`.
- `docs/evals/synthetic-review-prompt-template.md` mirrors the same
  agent-readiness policy.
- `docs/evals/pr17-disputed-surface-pilot-findings.md` records the Pilot 3
  evidence behind the cleanup.

Boundary preserved:

- no `SKILL.md` change,
- no `$lolla` runtime change,
- no schema fields added,
- no model calls,
- no LLM judge,
- no automatic `human_review`,
- no automatic agent-readiness label,
- no capture/chunking work,
- no Observatory work.

Verification:

```text
19 focused tests passed
JSON docs parse cleanly
diff checks clean
docs-only PR
```

PM read:

- PR18 is merged.
- It resolves the Record 7-style label ambiguity without adding machinery.
- After PR18, pause eval PRs unless a real review batch shows a new blocker.

## Drift Checks For Every PR

Before approving or merging a PR, check:

1. Does it move a named PRD item or a clearly justified operational blocker?
2. Does it preserve the distinction between shipped behavior and roadmap?
3. Does it keep Lolla as a reasoning-audit harness rather than:
   - guardrail,
   - sandbox,
   - firewall,
   - identity broker,
   - policy engine,
   - fact checker,
   - generic judge?
4. Does it avoid exposing private machinery in ordinary user-facing output?
5. Does it avoid adding LLM judges before deterministic and human-review
   foundations exist?
6. Does it keep high-stakes mode honest: stricter metadata or routing is not
   domain assurance?
7. Does it add or preserve tests for the changed artifact path?
8. Does it keep local artifacts local by default?
9. Does it avoid broad UI redesign when a narrow custody/API fix would do?
10. Does it leave `SKILL.md` as a conductor surface, with details in linked docs?

## Verification Habit

Prefer focused tests tied to the changed path, plus compile checks for edited
Python modules.

Recent focused verification sets have included:

```bash
python3 -m py_compile \
  engine/system_b/audit_mode.py \
  engine/system_b/agent_result.py \
  engine/system_b/reasoning_trace.py \
  scripts/archive_run.py \
  scripts/run_extract.py \
  scripts/run_pipeline.py \
  scripts/skill/validate_audit_mode.py \
  observatory/serve_result.py

PYTHONPATH=. pytest -q \
  tests/test_audit_mode.py \
  tests/test_agent_result.py \
  tests/test_reasoning_trace_archive.py \
  tests/test_skill_contract.py \
  tests/test_archive_run_case_identity.py \
  tests/test_archive_run_v60_telemetry.py \
  tests/test_finalize_trusted_transcript.py \
  tests/test_pr3_observatory_panels.py
```

For real-run smoke tests, inspect:

```bash
jq '{schema_version,status,caller_action,risk_mode}' \
  /path/to/archive/run/agent_result.json

jq '.process.risk_mode' \
  /path/to/archive/run/reasoning_trace.json

jq '.artifacts[] | select(.path | endswith("agent_result.json"))' \
  /path/to/archive/run/reasoning_trace.json
```

## Current Big-Picture Read

Harness foundation completion:

```text
about 65%
```

Manual inspection loop completion:

```text
about 90%
```

Reason:

- Lolla can already run, revise, memoize, archive, and expose machine-readable
  custody.
- Active and archived custody sidecar APIs now work, and the custody UI bridge
  has real-click Playwright proof.
- Provider-boundary health is now structured enough to support a policy
  decision instead of a blunt partial-health blob.
- Deterministic evaluation v0 is implemented as a run-readiness receipt.
- Evaluation custody surfacing has landed through PR9.
- Capture adequacy has landed and passed a real `$lolla` smoke.
- Evaluation-policy correction PR10b has landed.
- Control-plane contract v0 has landed, giving external agent/control systems a
  local metadata contract without making Lolla an enforcement layer.
- Archive corpus export, human-review taxonomy/workflow, review-readiness
  tiers, and the synthetic-review validator have landed.
- The validated PR16 pilot shows the next eval-methodology issue is review
  surface policy, not judge implementation.

The current strategy is still sound:

```text
custody first
-> inspection
-> deterministic evaluation
-> control-plane metadata contract
-> archive corpus and human-review workflow
-> calibrated subjective evaluation only later
-> deeper vendor-specific integration only after the local contract is stable
```
