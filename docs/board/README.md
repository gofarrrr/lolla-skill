# Board Product Briefs

Status: board-facing reading index
Date: 2026-06-30

These documents explain Lolla's current product direction in simple language.
They are meant for board/customer-style discussion, not implementation handoff.

Recommended reading order:

1. [Lolla Board Product Understanding](lolla-board-product-understanding-v0.md)

   The overall product story: what problem Lolla solves, what users should get,
   where the alpha is, what exists now, and what is still unproven.

2. [Lolla Conversation Interpretation Product Brief](lolla-board-conversation-interpretation-v0.md)

   The Decision Trail story: how Lolla is learning to explain the process behind
   a revised AI answer, what is interpreted by LLMs, what is preserved by
   deterministic custody, what the pilots found, and what users could eventually
   receive.

3. [Lolla Product Evals Board Brief](lolla-board-evals-product-brief-v0.md)

   The Product Delta story: how Lolla compares the original strong-model answer
   with the revised answer without using a naive judge or score, what the current
   non-human evidence suggests, and what still requires human review.

4. [Decision Work Brief Offline v1 Demo Narrative](decision-work-brief-offline-v1-demo-narrative.md)

   A plain-language walkthrough of the Offline v1 evidence surface: how a
   completed Lolla run becomes a readable Decision Work Brief, what bounded
   interpretation and triage add, and what the system still refuses to claim.

Follow-up implementation planning:

- [Decision Work Receipt PRD](../conversation-understanding/decision-work-receipt-prd-v0.md)

  Actionable PRD for the missing product layer: source/context inventory,
  conversation process map, challenge coverage, and the future receipt that
  explains the work trail behind a serious AI-assisted output.

- [Decision Work Receipt Schema](../conversation-understanding/decision-work-receipt-v0.json)

  PR105's machine-readable contract for the future receipt. It defines the
  shape only; exporter behavior and runtime integration remain out of scope.

- [Decision Work Receipt Source Inventory](../conversation-understanding/decision-work-receipt-source-inventory-v0.md)

  PR106's first read-only implementation slice. It inventories source/context
  artifacts over completed run directories and leaves later work-trail
  interpretation fields sparse.

- [Decision Work Receipt Conversation Process Map](../conversation-understanding/decision-work-receipt-conversation-process-map-v0.md)

  PR107's second read-only implementation slice. It records deterministic
  process-shape metadata, such as turn counts and one-shot versus multi-turn
  evidence, without deciding whether the process was good.

- [Decision Work Receipt Challenge Coverage Map](../conversation-understanding/decision-work-receipt-challenge-coverage-map-v0.md)

  PR108's third read-only implementation slice. It records which Lolla
  challenge surfaces and run-health caveats are visible from completed
  artifacts, without deciding whether the challenge was good.

- [Decision Work Receipt Exporter](../conversation-understanding/decision-work-receipt-exporter-v0.md)

  PR109's composed read-only receipt slice. It brings the inventory, process
  shape, challenge coverage, optional Decision Trail/Product Delta references,
  readiness label, missingness, and non-claims into one sparse work-trail
  artifact.

- [Decision Work Receipt Fixture Review](../conversation-understanding/decision-work-receipt-fixture-review-v0.md)

  PR110's checked-in-safe review of that sparse receipt. It finds the receipt
  useful as a work-trail shell, still too thin to explain the messy semantic
  story, and risky if readiness labels are read as approval.

- [Decision Work Receipt Decision Gate](../conversation-understanding/decision-work-receipt-decision-gate-v0.md)

  PR111's closure decision. Keep the sparse receipt as an internal/workflow
  wrapper, do not build a parallel Work Receipt interpretation system yet, and
  let Decision Trail/Product Delta artifacts supply semantic interpretation
  when that work is justified.

- [Decision Work Receipt Debug Summary](../conversation-understanding/decision-work-receipt-debug-summary-v0.md)

  An internal Markdown renderer that turns a Decision Work Receipt and optional
  Decision Trail report into a maintainer-readable debug packet. It is useful
  for checking artifact status and missingness, but it is not the customer
  proof-of-work story.

- [Decision Work Brief PRD](../conversation-understanding/decision-work-brief-prd-v0.md)

  The product-facing target for the missing layer: a plain-language brief that
  explains what decision was being made, what Lolla pressed on, what changed,
  what remains unresolved, and what the audit must not claim. It also nests the
  work into PR113-PR158 so the next steps stay grounded in the existing
  receipt, Decision Trail, Product Delta, lint, interpretation, and custody
  machinery.

- [Decision Work Brief Schema](../conversation-understanding/decision-work-brief-v0.json)

  PR114's machine-readable contract for the future user-facing brief. It
  defines the required decision-story sections, source refs, custody flags,
  uncertainty, human-validation state, and non-claims without adding a
  generator, renderer, runtime integration, product proof, or agent action
  authorization.

- [Decision Work Brief Schema Guide](../conversation-understanding/decision-work-brief-schema-v0.md)

  Plain-language guide to the PR114 boundary: the brief tells the decision
  story, the receipt backs the story, populated semantic sections require LLM
  or human interpretation, and the schema must not certify correctness.

- [Decision Work Brief Packet Builder](../conversation-understanding/decision-work-brief-packet-builder-v0.md)

  PR115's offline packet builder for preparing Decision Work Brief inputs from
  completed runs. It records source refs, missingness, redaction/private
  availability, custody flags, and non-claims for later interpretation without
  generating the brief or changing runtime behavior.

- [Decision Work Brief Draft Pilot](../conversation-understanding/decision-work-brief-draft-pilot-v0.md)

  PR116's one-case Codex-assisted provisional draft pilot. It embeds one
  checked-in-safe `lolla.decision_work_brief.v0` draft from a locally generated
  PR115 metadata-only packet, preserving uncertainty, source refs, human
  follow-up questions, and non-claims without adding a renderer, runtime
  integration, product proof, or agent action authorization.

- [Decision Work Brief Renderer](../conversation-understanding/decision-work-brief-renderer-v0.md)

  PR117's deterministic Markdown renderer for existing
  `lolla.decision_work_brief.v0` JSON. PR123 patches it so the main body uses
  plain-language decision headings before the compact Evidence and limits
  appendix.

- [Decision Work Brief Rendered Example](../conversation-understanding/decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md)

  A checked-in-safe PR117 rendered example from the PR116 cofounder draft. It is
  kept in conversation-understanding, not promoted as a board/customer demo.

- [Decision Work Brief Usefulness Review](../conversation-understanding/decision-work-brief-usefulness-review-v0.md)

  PR118's Codex-assisted usefulness and delivery gate. It finds the rendered
  brief promising but thin, chooses `proceed_to_tiny_second_case`, and does not
  declare product readiness.

- [Decision Work Brief Second Tiny Case Pilot](../conversation-understanding/decision-work-brief-second-tiny-case-pilot-v0.md)

  PR119's second checked-in-safe pilot on `launch-public-enterprise-beta`. It
  compares a different go-to-market decision type against the first cofounder
  case, finds another concrete action-consequence read, and chooses
  `proceed_to_small_pattern_review`, not runtime integration.

- [Decision Work Brief Rendered Launch-Beta Example](../conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md)

  A checked-in-safe PR119 rendered example from the launch-beta second case. It
  is still kept in conversation-understanding, not promoted as a board/customer
  demo.

- [Decision Work Brief Small Pattern Review](../conversation-understanding/decision-work-brief-small-pattern-review-v0.md)

  PR120's two-case pattern review over the cofounder and launch-beta briefs. It
  finds the action-consequence pattern promising enough for one third diversity
  case and chooses `proceed_to_third_diversity_case`, not runtime integration.

- [Decision Work Brief Third Diversity Case Pilot](../conversation-understanding/decision-work-brief-third-diversity-case-pilot-v0.md)

  PR121A's checked-in-safe third pilot on `deploy-assisted-intake-routing`.
  It follows PR120's gate, adds a healthcare operations deployment case, and
  chooses `proceed_to_three_case_pattern_review`.

- [Decision Work Brief Rendered Intake-Routing Example](../conversation-understanding/decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md)

  A checked-in-safe PR121A rendered example from the intake-routing third case.
  It is still kept in conversation-understanding, not promoted as a
  board/customer demo.

- [Decision Work Brief Three-Case Pattern Review](../conversation-understanding/decision-work-brief-three-case-pattern-review-v0.md)

  PR122's pattern review across the cofounder, launch-beta, and intake-routing
  briefs. It finds the strongest useful signal is concrete action consequence
  across three decision families, but chooses
  `proceed_to_plain_language_renderer_patch` because the rendered Markdown still
  feels too field-label-heavy and internal for a board/customer reader.

- [Decision Work Brief Plain-Language Renderer Patch](../conversation-understanding/decision-work-brief-plain-language-renderer-patch-v0.md)

  PR123's renderer patch regenerates all three existing examples with
  plain-language main headings and moves source refs, section uncertainty,
  custody flags, and non-claims into a compact Evidence and limits section.
  It does not add new cases or product-readiness claims.

- [Decision Work Brief Plain-Language Re-Review](../conversation-understanding/decision-work-brief-plain-language-rereview-v0.md)

  PR124 reviews the three regenerated examples and finds the surface readable
  enough for local-private adequacy comparison. It gates to
  `proceed_to_local_private_adequacy_check`, not runtime integration.

- [Decision Work Brief Local-Private Adequacy Check](../conversation-understanding/decision-work-brief-local-private-adequacy-check-v0.md)

  PR125 performs one read-only local-private shadow review on
  `launch-public-enterprise-beta` and checks in only safe conclusions. It
  records `adequate_but_missing_private_nuance`.

- [Decision Work Brief Expansion / Runtime Attachment Decision Gate](../conversation-understanding/decision-work-brief-expansion-runtime-decision-gate-v0.md)

  PR126 decides the next phase after PR124/PR125. It selects
  `run_more_local_private_adequacy_checks`, not runtime attachment or product
  readiness.

- [Decision Work Brief Conversation Interpretation Gap Map](../conversation-understanding/decision-work-brief-conversation-interpretation-gap-map-v0.md)

  PR127 maps the richer conversation information the brief lane eventually
  needs to preserve. It classifies fields as clear, partial, local-private-only,
  LLM-interpretable, human-review-dependent, or not currently captured, then
  gates to a target contract instead of runtime extraction.

- [Decision Work Conversation Interpretation Contract](../conversation-understanding/decision-work-conversation-interpretation-contract-v0.md)

  PR128 defines the future `lolla.decision_work_conversation_interpretation_contract.v0`
  target: field groups, ownership, source status, privacy handling,
  deterministic custody, non-claims, and handoff shape. It is not an extractor,
  judge, product proof, runtime change, or agent authorization.

- [Decision Work Conversation Interpretation Contract Schema](../conversation-understanding/decision-work-conversation-interpretation-contract-v0.json)

  Machine-readable PR128 contract schema for future interpretation/custody work.
  It defines target fields and vocabularies, not populated case data.

- [Decision Work Conversation Interpretation Contract Packet Review](../conversation-understanding/decision-work-conversation-interpretation-contract-packet-review-v0.md)

  PR129 compares the PR128 contract against the current completed-run artifact
  and PR115 packet surface. It finds the system can carry source/status
  metadata now, but needs a field-grouped offline interpretation packet before
  any LLM/human interpretation test or runtime extraction plan.

- [Decision Work Conversation Interpretation Offline Packet](../conversation-understanding/decision-work-conversation-interpretation-offline-packet-v0.md)

  PR130 adds that field-grouped offline packet builder. It prepares a safe
  source/status dossier for future interpretation against the PR128 contract,
  without filling semantic fields, copying raw/private content, running Lolla,
  calling models, changing runtime extraction, proving product value, or
  authorizing agent action.

- [Decision Work Conversation Interpretation Tiny Offline Read](../conversation-understanding/decision-work-conversation-interpretation-tiny-offline-read-v0.md)

  PR131 adds the first tiny provisional read over one generated PR130 packet
  for `launch-public-enterprise-beta`. It fills only a small PR128 field subset,
  keeps source-depth uncertainty visible, checks in no source packet or private
  text, and recommends one second tiny offline read before any durable schema or
  runtime plan.

- [Decision Work Conversation Interpretation Second Tiny Offline Read](../conversation-understanding/decision-work-conversation-interpretation-second-tiny-offline-read-v0.md)

  PR132 repeats the tiny read on `deploy-assisted-intake-routing`, a healthcare
  operations/deployment decision. The same field set remains useful for action
  consequence, thresholds, evidence gates, useful/noisy friction, and non-proof
  boundaries while keeping starting direction, abandoned options, and lost value
  source-limited.

- [Decision Work Conversation Interpretation Read Schema](../conversation-understanding/decision-work-conversation-interpretation-read-schema-v0.md)

  PR133 defines `lolla.decision_work_conversation_interpretation_read.v0` as the
  reusable contract for future offline interpretation reads. It requires source
  refs, uncertainty, privacy limits, human-review flags, non-claims, and no
  quality-label use without adding an interpreter, runtime extractor, product
  proof, or agent authorization.

- [Decision Work Conversation Interpretation Read Comparison](../conversation-understanding/decision-work-conversation-interpretation-read-comparison-v0.md)

  PR134 compares the launch-beta and intake-routing reads through the PR133
  schema shape. It finds the action-consequence pattern useful enough for one
  narrow brief-enrichment test, while keeping lost value, rejected options,
  source depth, human validation, product proof, and runtime integration out of
  scope.

- [Decision Work Brief Interpretation Enrichment Test](../conversation-understanding/decision-work-brief-interpretation-enrichment-test-v0.md)

  PR135 creates a separate enriched launch-beta brief from the PR131 read. It
  uses only the conservative feed-now fields and leaves the original rendered
  brief untouched.

- [Decision Work Brief Original vs Enriched Review](../conversation-understanding/decision-work-brief-original-vs-enriched-review-v0.md)

  PR136 compares the original and enriched launch-beta briefs and gates to one
  second enrichment test, not a rules contract or runtime integration.

- [Decision Work Brief Second Enrichment Test](../conversation-understanding/decision-work-brief-second-enrichment-test-v0.md)

  PR137 creates a separate enriched intake-routing brief from the PR132 read,
  with the same field exclusions and non-claims.

- [Decision Work Brief Enriched Pattern Review](../conversation-understanding/decision-work-brief-enriched-pattern-review-v0.md)

  PR138 compares the two enriched briefs and recommends a future enrichment
  rules contract. It explicitly does not implement PR139 or attach enrichment
  to runtime.

- [Decision Work Brief Enrichment Rules Contract](../conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.md)

  PR139 defines which interpretation fields may enter the user-facing brief,
  which fields must stay evidence-only, and which proof/score/approval concepts
  remain forbidden.

- [Decision Work Brief Offline Enriched Builder](../conversation-understanding/decision-work-brief-offline-enriched-builder-v0.md)

  PR140 adds a deterministic offline CLI that creates separate enriched
  Markdown from an original rendered brief, an interpretation read, and the
  PR139 rules contract. It does not call models or change runtime behavior.

- [Decision Work Brief Enriched Builder Output Review](../conversation-understanding/decision-work-brief-enriched-builder-output-review-v0.md)

  PR141 compares the builder-generated outputs against the hand-built enriched
  examples. It finds the useful signal survived, but selects
  `proceed_to_builder_rule_patch` because the generated language is still too
  templated.

- [Decision Work Brief Enrichment Builder Rule Patch](../conversation-understanding/decision-work-brief-enrichment-builder-rule-patch-v0.md)

  PR142 patches the deterministic builder wording and regenerates the two
  builder-enriched examples with less repetitive prose while preserving field
  limits, uncertainty, source limits, and non-claims.

- [Decision Work Brief Builder Patch Review](../conversation-understanding/decision-work-brief-enrichment-builder-rule-patch-review-v0.md)

  PR143 reviews the patched builder outputs and selects
  `proceed_to_offline_system_closure_gate`, not another builder case or runtime
  integration.

- [Decision Work Brief Offline System Closure Gate](../conversation-understanding/decision-work-brief-offline-system-closure-gate-v0.md)

  PR144 decides the offline Decision Work Brief surface is coherent enough to
  package, while explicitly preserving no product proof, no human validation,
  and no runtime attachment.

- [Decision Work Brief PR114-PR144 Packaging Gate](../conversation-understanding/decision-work-brief-pr114-pr144-packaging-gate-v0.md)

  PR145 packages the offline evidence surface with a manifest, file groups,
  staging list, do-not-stage warnings, validation checklist, useful signal, and
  unresolved risk.

- [Decision Work Brief Additional Local-Private Adequacy Checks](../conversation-understanding/decision-work-brief-additional-local-private-adequacy-checks-v0.md)

  PR146 checks the cofounder and intake-routing cases against richer
  local-private completed-run context, records only safe conclusions, and
  recommends a third builder case before any runtime-attachment plan.

- [Decision Work Brief Third Builder Case](../conversation-understanding/decision-work-brief-third-builder-case-v0.md)

  PR147 tests whether the cofounder case is ready for deterministic
  builder-enrichment. It blocks the output because the case lacks a
  builder-compatible interpretation read, preserving the evidence boundary.

- [Decision Work Conversation Interpretation Third Tiny Offline Read](../conversation-understanding/decision-work-conversation-interpretation-third-tiny-offline-read-v0.md)

  PR147A adds the missing formal-schema cofounder interpretation read so a
  later PR can run the deterministic builder without a schema workaround.

- [Decision Work Brief Third Builder Case Output](../conversation-understanding/decision-work-brief-third-builder-case-output-v0.md)

  PR148 runs the deterministic builder on the cofounder case using the PR147A
  read and PR139 rules. It creates the third builder-enriched brief, keeps the
  output source-limited and non-overclaiming, and recommends a three-builder
  case pattern review.

- [Decision Work Brief Three Builder Case Pattern Review](../conversation-understanding/decision-work-brief-three-builder-case-pattern-review-v0.md)

  PR149 compares the three builder-generated enriched briefs across launch,
  healthcare operations, and founder governance. It finds the builder stable
  enough for offline review and recommends a human-review intake plan before
  any runtime attachment.

- [Decision Work Brief Human Review Intake Plan](../conversation-understanding/decision-work-brief-human-review-intake-plan-v0.md)

  PR150 defines the future human-review intake plan for the three
  builder-generated enriched briefs. It names the usefulness, action
  consequence, uncertainty, source-depth, private-context, overtrust, and
  runtime-blocker questions reviewers must answer before the surface can claim
  anything stronger than useful-but-not-validated offline evidence.

- [Decision Work Brief Human Review Pilot Scaffold](../conversation-understanding/decision-work-brief-human-review-pilot-scaffold-v0.md)

  PR151 turns the intake plan into runnable but blank pilot materials. It
  provides reviewer instructions and a response template for the three enriched
  briefs, but keeps human-review answers unfilled until a real reviewer uses
  the template.

- [Decision Work Brief Human Review Pilot Readiness Gate](../conversation-understanding/decision-work-brief-human-review-pilot-readiness-gate-v0.md)

  PR152 records that the pilot packet is ready to run but has not run. It keeps
  runtime and customer-facing use blocked until a real human reviewer fills the
  PR151 response template.

- [Decision Work Brief Human Review Awaiting Response Gate](../conversation-understanding/decision-work-brief-human-review-awaiting-response-gate-v0.md)

  PR153 records the honest pause state after PR152: no real human response
  exists yet, Codex must not fill the template, and runtime/customer-facing use
  remains blocked until a human reviewer responds.

- [Decision Work Automatic Triage Contract](../conversation-understanding/decision-work-automatic-triage-contract-v0.md)

  PR154 defines the future automatic triage contract for routing attention
  between brief surface, agent inspection, source-depth blocking, escalation,
  and runtime-blocking states. It treats human review as calibration, not as
  the normal operating layer.

- [Decision Work Automatic Triage Packet Builder](../conversation-understanding/decision-work-automatic-triage-packet-builder-v0.md)

  PR155 adds the deterministic checked-in-safe packet builder for future
  automatic triage. It carries refs, custody flags, field policy, future tasks,
  and known limits across the three builder-enriched cases without filling
  semantic triage fields.

- [Decision Work Automatic Triage Provisional Read](../conversation-understanding/decision-work-automatic-triage-provisional-read-v0.md)

  PR156 adds a Codex-assisted provisional triage read over the three cases. It
  routes attention differently for launch, healthcare operations, and founder
  governance while preserving that the read is not scoring, approval, product
  proof, human validation, or action authorization.

- [Decision Work Brief Offline v1 Closure Gate](../conversation-understanding/decision-work-brief-offline-v1-closure-gate-v0.md)

  PR157 selects `package_offline_v1`: the system is functional as an offline
  evidence chain with limitations, not runtime-integrated, customer-ready,
  human-validated, product-proof, answer-quality-scored, or action-authorizing.

- [Decision Work Brief Offline v1 Package Gate](../conversation-understanding/decision-work-brief-offline-v1-package-gate-v0.md)

  PR158 packages Offline v1 by referencing the PR114-PR144 base package and
  explicitly adding PR145-PR157 human-calibration, third-case,
  automatic-triage, closure, and package-gate artifacts.

- [Decision Work Brief Runtime Attachment PRD](../conversation-understanding/decision-work-brief-runtime-attachment-prd-v0.md)

  Planning bridge after Offline v1. It decides from first principles when a
  future brief should run, what the user sees, what another agent sees, what
  blocks generation, and why the first runtime-safe slice should be a flagged
  post-archive attachment path rather than full automation.

- [Decision Work Brief Runtime-Attached Internal v1 Package Gate](../conversation-understanding/decision-work-brief-runtime-attached-v1-package-gate-v0.md)

  PR167's internal runtime package gate. It explains the first default-off,
  post-archive attachment path: completed run archives may get a
  `decision_work/` sidecar with status, short receipt, and agent handoff when
  `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE` is explicitly enabled. It is not
  customer readiness, human validation, product proof, advice correctness, or
  action authorization.

- [Decision Work Brief Runtime-Attached Internal v1 Follow-up Plan](../conversation-understanding/decision-work-brief-runtime-attached-v1-followup-plan-v0.md)

  PR168's follow-up choice gate. It says the runtime hook is mechanically
  attached, default-off, and fail-closed, but still input-supply-limited until
  the repo plans how safe run-specific brief, enriched brief, and triage inputs
  reach the hook without exposing private content.

- [Decision Work Brief Runtime Safe Brief Supply Plan](../conversation-understanding/decision-work-brief-runtime-safe-brief-supply-plan-v0.md)

  PR169's supply plan. It classifies which inputs can come from completed-run
  artifacts, existing offline builders, checked-in-safe examples, manual refs,
  local-private mode, or future interpretation, and recommends a safe resolver
  contract before adding more runtime behavior.

- [Decision Work Brief Runtime Safe Supply Resolver Contract](../conversation-understanding/decision-work-brief-runtime-safe-supply-resolver-contract-v0.md)

  PR170's resolver contract. It defines the modes, statuses, input types,
  unsafe exclusions, bundle feedability output, custody flags, and non-claims
  for a future deterministic resolver, while keeping direct runtime
  interpretation and default-on behavior out of scope.

- [Decision Work Brief Runtime Safe Supply Resolver](../conversation-understanding/decision-work-brief-runtime-safe-supply-resolver-v0.md)

  PR171's resolver implementation. It validates explicit safe refs, excludes
  unsafe inputs, redacts local paths in output, and tells the manual runtime
  bundle whether it has enough safe material to proceed, partially proceed,
  defer, queue, or block. It is not interpretation and does not change the
  runtime hook.

- [Decision Work Brief Runtime Bundle Resolver Integration](../conversation-understanding/decision-work-brief-runtime-bundle-resolver-integration-v0.md)

  PR172's manual bundle bridge. It lets the bundle generator consume
  `--resolver-output`, carry resolver feedability through attachment status,
  receipt, and agent handoff, and still keeps the default-off runtime hook
  unchanged.

- [Decision Work Brief Runtime Hook Resolver Wiring](../conversation-understanding/decision-work-brief-runtime-hook-resolver-wiring-v0.md)

  PR173's default-off hook bridge. When
  `LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE` is enabled, the post-archive hook
  now calls the resolver-aware bundle chain and writes an available,
  agent-only, deferred, blocked, or failed-closed sidecar while still making no
  product-proof, human-validation, scoring, or action-authorization claim.

- [Decision Work Brief Runtime Hook Resolver Fixture Review](../conversation-understanding/decision-work-brief-runtime-hook-resolver-fixture-review-v0.md)

  PR174's review-only pass over the concrete hook sidecar states. It confirms
  flag-off, deferred, available, agent-only, blocked, privacy-blocked, and
  failed-closed behavior, then selects a checked-in-safe case registry so demos
  and tests can use stable safe refs without implying arbitrary live runs are
  automatically interpreted.

- [Decision Work Brief Runtime Checked-In Safe Case Registry](../conversation-understanding/decision-work-brief-runtime-checked-in-safe-case-registry-v0.md)

  PR175's deterministic registry for the three known Decision Work Brief
  examples. It lets resolver mode `checked_in_safe_case_registry` feed the
  manual bundle without manual env refs, but it is curated-example supply only,
  not a general live-run interpretation path.

- [Decision Work Brief Runtime Hook Registry Fixture Review](../conversation-understanding/decision-work-brief-runtime-hook-registry-fixture-review-v0.md)

  PR176's review-only pass over registry-backed hook fixtures. It confirms the
  launch, deploy-intake, and cofounder registry entries can generate temp
  sidecars through the resolver-aware hook seam, while keeping arbitrary-run
  semantic supply out of scope.

- [Decision Work Brief Runtime-Attached Internal v1 Package Refresh](../conversation-understanding/decision-work-brief-runtime-attached-internal-v1-package-refresh-v0.md)

  PR177's package refresh for PR160-PR176. It packages the internal,
  default-off, post-archive sidecar path for maintainer review when safe refs
  are supplied manually or through registry fixtures, while keeping customer
  presentation and arbitrary-run semantic supply out of scope.

- [Decision Work Automatic Semantic Supply PRD](../conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md)

  PR178's product roadmap after runtime-attached internal v1. It defines the
  missing bridge from a newly completed Lolla run to safe interpreted Decision
  Work artifacts through an offline queue, validation, brief rendering, triage,
  and resolver-approved sidecar update.

- [Decision Work Offline Interpretation Queue Contract](../conversation-understanding/decision-work-offline-interpretation-queue-contract-v0.md)

  PR179's first contract slice for that bridge. It defines queue item/result
  shapes, statuses, privacy modes, custody flags, validation requirements, and
  non-claims without creating generated reads, queue workers, runtime behavior,
  model calls, or sidecar updates.

- [Decision Work Offline Interpretation Queue Builder](../conversation-understanding/decision-work-offline-interpretation-queue-builder-v0.md)

  PR180's deterministic queue-item preparation layer. It turns completed run
  refs and optional PR130 packet refs into checked-in-safe queue items without
  filling interpretation fields, calling models, mutating archives, or updating
  runtime sidecars.

- [Decision Work Operator/Codex Interpretation Prompt Packet](../conversation-understanding/decision-work-operator-codex-interpretation-prompt-packet-v0.md)

  PR181's bounded handoff packet for a future operator or Codex session. It
  explains what may be filled in a PR133 interpretation read and what must
  remain forbidden, while stopping before generated-read intake.

- [Decision Work Generated Interpretation Read Intake](../conversation-understanding/decision-work-generated-interpretation-read-intake-v0.md)

  PR182's strict intake validator for externally supplied interpretation reads.
  It accepts only schema-compatible, source-referenced, uncertainty-bearing,
  privacy-bounded, non-overclaiming reads for later offline use; it does not
  generate reads, update sidecars, score advice, validate correctness, or
  authorize action.

- [Decision Work Generated Interpretation Read Intake Review](../conversation-understanding/decision-work-generated-interpretation-read-intake-review-v0.md)

  PR183's review-only pass over the validator. It confirms the three existing
  checked-in reads are accepted, synthetic unsafe cases are rejected or repaired,
  and intake acceptance still means structural/custody eligibility only, not
  semantic correctness, product proof, human validation, or action clearance.

- [Decision Work Operator/Codex Generated Read Pilot](../conversation-understanding/decision-work-operator-codex-generated-read-pilot-v0.md)

  PR184's one-case launch-beta generated-read pilot. It checks in a tiny
  source-refed candidate read and PR182 intake result, accepts it only for later
  offline planning, and still does not render briefs, generate triage, update
  resolver refs or sidecars, call models, score advice, prove product value, or
  authorize action.

- [Decision Work Generated Read To Brief Supply Plan](../conversation-understanding/decision-work-generated-read-to-brief-supply-plan-v0.md)

  PR185's plan for the next deterministic adapter. It defines the allowed
  generated-read fields, evidence-only fields, blockers, required source refs,
  uncertainty, privacy limits, non-claims, and adapter boundaries before any
  brief rendering or runtime sidecar work.

- [Decision Work Generated Read Brief Supply Adapter](../conversation-understanding/decision-work-generated-read-brief-supply-adapter-v0.md)

  PR186's deterministic adapter and CLI for accepted generated reads. It emits
  safe brief-supply packets with copied allowed fields, source refs,
  uncertainty, blocker status, custody flags, and non-claims while still
  stopping before brief rendering, enrichment, triage, resolver ref use,
  runtime sidecar update, model calls, scoring, proof claims, or action
  authorization.

- [Decision Work Generated Read Brief Rendering Pilot](../conversation-understanding/decision-work-generated-read-brief-rendering-pilot-v0.md)

  PR187's one-case launch-beta Markdown rendering pilot. It consumes a ready
  PR186 supply packet and writes a reader-facing generated-read brief while
  preserving source refs, uncertainty, privacy limits, custody flags, and
  non-claims. It still does not enrich, generate triage, mark resolver refs
  usable, update sidecars, call models, score, prove, or authorize action.

- [Decision Work Generated Read Brief vs Existing Brief Review](../conversation-understanding/decision-work-generated-read-brief-vs-existing-brief-review-v0.md)

  PR188's docs/review/tests-only comparison between the generated-read
  launch-beta brief and the existing rendered and enriched launch-beta briefs.
  It finds the generated-read brief preserves the core decision and action
  consequence while staying thinner than the enriched brief, and gates to a
  second generated-read rendering pilot without enrichment, triage, resolver ref
  use, runtime sidecar update, model calls, proof claims, scoring, or action
  authorization.

- [Decision Work Generated Read Second Brief Rendering Pilot](../conversation-understanding/decision-work-generated-read-second-brief-rendering-pilot-v0.md)

  PR189's deploy-intake second-case rendering pilot. It validates a
  checked-in-safe generated read, builds PR186 supply, and renders a second
  generated-read brief with compliance/workflow caveats, source refs,
  uncertainty, privacy limits, custody flags, and non-claims intact. It still
  does not enrich, generate triage, mark resolver refs usable, update sidecars,
  call models, score, prove, or authorize action.

- [Decision Work Generated Read Brief Two-Case Pattern Review](../conversation-understanding/decision-work-generated-read-brief-two-case-pattern-review-v0.md)

  PR190's docs/review/tests-only comparison of the launch-beta and deploy-intake
  generated-read-rendered briefs. It finds the path stable enough to plan
  generated-read triage supply, while keeping triage generation, resolver ref
  use, runtime sidecar update, model calls, proof claims, scoring, and action
  authorization out of scope.

- [Decision Work Generated Read Triage Supply Plan](../conversation-understanding/decision-work-generated-read-triage-supply-plan-v0.md)

  PR191's docs/review/tests-only plan for future generated-read triage supply.
  It defines allowed inputs, routing fields, evidence-only fields, blocked
  fields, statuses, route categories, custody requirements, and forbidden
  quality/authority route concepts while still stopping before triage
  generation, resolver ref use, runtime sidecar update, model calls, scoring,
  proof claims, or action authorization.

- [Decision Work Generated Read Triage Supply Adapter](../conversation-understanding/decision-work-generated-read-triage-supply-adapter-v0.md)

  PR192's deterministic adapter and CLI for future generated-read triage
  supply. It emits ready, deferred, or blocked
  `lolla.decision_work_generated_read_triage_supply.v0` packets from
  generated-read, intake, brief-supply, and rendered-brief refs while still not
  generating triage, marking resolver refs usable, updating sidecars, calling
  models, scoring, proving, or authorizing action.

- [Decision Work Generated Read Triage Generation Pilot](../conversation-understanding/decision-work-generated-read-triage-generation-pilot-v0.md)

  PR193's first checked-in-safe generated triage read for launch beta. It
  routes attention to caveated offline brief candidacy, source-depth limits,
  private-context need, overtrust risk, and runtime attachment blocking while
  still not grading answer quality, marking resolver refs usable, updating
  sidecars, calling models, proving, or authorizing action.

- [Decision Work Generated Read Triage Pilot Review](../conversation-understanding/decision-work-generated-read-triage-pilot-review-v0.md)

  PR194's docs/review/tests-only review of the first generated triage read. It
  confirms launch-beta route vocabulary stays attention-routing rather than
  answer grading or action permission, and gates to a deploy-intake second
  triage pilot without creating that second case yet.

- [Decision Work Generated Read Second Triage Pilot](../conversation-understanding/decision-work-generated-read-second-triage-pilot-v0.md)

  PR195's checked-in-safe generated triage read for deploy-intake. It routes
  the healthcare workflow case to source-depth limits, private-context need,
  high overtrust risk, domain review, legal/compliance review, agent
  inspection, user-surface blocking, and runtime attachment blocking without
  grading advice, clearing deployment, marking resolver refs usable, updating
  sidecars, calling models, proving, or authorizing action.

- [Decision Work Generated Read Triage Two-Case Pattern Review](../conversation-understanding/decision-work-generated-read-triage-two-case-pattern-review-v0.md)

  PR196's docs/review/tests-only comparison of the launch-beta and
  deploy-intake generated triage reads. It finds the route vocabulary stable
  enough to plan generated-read resolver supply while keeping route categories
  separate from answer-quality scoring, resolver approval, sidecar update,
  runtime wiring, proof claims, and action authorization.

- [Decision Work Generated Read Resolver Supply Plan](../conversation-understanding/decision-work-generated-read-resolver-supply-plan-v0.md)

  PR197's docs/review/tests-only plan for future generated-read resolver
  supply. It defines resolver-supply candidates and candidate packet statuses
  while preserving that supply is not approval, runtime sidecar permission,
  user-surface readiness, product proof, scoring, or action authorization.

- [Decision Work Generated Read Resolver Supply Adapter](../conversation-understanding/decision-work-generated-read-resolver-supply-adapter-v0.md)

  PR198's deterministic adapter and CLI for future generated-read resolver
  supply candidates. It can prepare launch-beta and deploy-intake candidate
  packets while keeping deploy-intake runtime/user-surface blocked and while
  still not approving refs, updating sidecars, wiring runtime, scoring,
  proving, or authorizing action.

- [Decision Work Generated Read Resolver Supply Review](../conversation-understanding/decision-work-generated-read-resolver-supply-review-v0.md)

  PR199's docs/review/tests-only pass over launch-beta and deploy-intake
  resolver-supply candidate packets. It confirms candidate packets stay
  separate from resolver approval, runtime sidecar permission, user-surface
  readiness, quality labels, proof claims, and action authorization.

- [Decision Work Automatic Semantic Supply Pre-Runtime v1 Package Gate](../conversation-understanding/decision-work-automatic-semantic-supply-pre-runtime-v1-package-gate-v0.md)

  PR200's package gate and manifest for PR178-PR199. It packages the offline
  pre-runtime chain through resolver-supply candidate packets while keeping
  runtime attachment, resolver approval, sidecar updates, runtime wiring,
  production automation, proof claims, scoring, and action authorization out
  of scope.

- [Decision Work Resolver Candidate Sidecar Update Plan](../conversation-understanding/decision-work-resolver-candidate-sidecar-update-plan-v0.md)

  PR201's docs/review/tests-only plan for future sidecar update packets. It
  keeps proposed packet creation separate from actual `decision_work/` writes,
  archive mutation, resolver approval, runtime wiring, quality labels, proof
  claims, and action authorization.

- [Decision Work Resolver Candidate Sidecar Update Packet Adapter](../conversation-understanding/decision-work-resolver-candidate-sidecar-update-packet-adapter-v0.md)

  PR202's deterministic adapter and CLI for offline proposed sidecar update
  packets. It can prepare launch/deploy packet artifacts while still refusing
  actual sidecar writes, archive mutation, resolver approval, runtime wiring,
  quality labels, proof claims, and action authorization.

- [Decision Work Sidecar Update Packet Review](../conversation-understanding/decision-work-sidecar-update-packet-review-v0.md)

  PR203's docs/review/tests-only review of launch/deploy proposed sidecar
  update packets. It confirms packets remain offline artifacts, not real
  sidecar writes, archive mutation, resolver approval, runtime wiring,
  user-surface readiness, quality labels, proof claims, or action
  authorization.

- [Decision Work Sidecar Update Packet Pre-Write Package Gate](../conversation-understanding/decision-work-sidecar-update-packet-prewrite-package-gate-v0.md)

  PR204's package gate and manifest for PR201-PR203. It packages the offline
  proposed sidecar update packet layer while still excluding actual sidecar
  writes, archive mutation, runtime wiring, resolver approval, default-on
  behavior, proof claims, scoring, and action authorization.

- [Decision Work Runtime Sidecar Write Plan](../conversation-understanding/decision-work-runtime-sidecar-write-plan-v0.md)

  PR205's docs/review/tests-only plan for the first actual sidecar-write
  implementation. It keeps implementation out of scope and selects a future
  default-off dry-run adapter, not a live write.

- [Decision Work Sidecar Write Dry-Run Adapter](../conversation-understanding/decision-work-sidecar-write-dry-run-adapter-v0.md)

  PR206's deterministic dry-run adapter and CLI for sidecar update packets. It
  can produce dry-run result JSON and optional preview files under an explicit
  safe output directory while still not writing `decision_work/`, mutating
  archives, approving resolver refs, wiring runtime, scoring, proving, or
  authorizing action.

- [Decision Work Sidecar Write Dry-Run Review](../conversation-understanding/decision-work-sidecar-write-dry-run-review-v0.md)

  PR207's docs/review/tests-only review of launch/deploy dry-run outputs. It
  confirms preview files stay temp/output-only, deploy preserves runtime
  blocking, and actual sidecar writes, archive mutation, resolver approval,
  runtime wiring, quality labels, proof claims, and action authorization remain
  closed.

- [Decision Work Sidecar Write Dry-Run Package Gate](../conversation-understanding/decision-work-sidecar-write-dry-run-package-gate-v0.md)

  PR208's package gate and manifest for PR206-PR207. It packages the offline
  dry-run preview layer while still excluding actual sidecar writes, archive
  mutation, runtime wiring, resolver approval, default-on behavior, proof
  claims, scoring, and action authorization.

- [Decision Work Runtime Sidecar Write Contract](../conversation-understanding/decision-work-runtime-sidecar-write-contract-v0.md)

  PR209's contract/docs/schema/tests-only gate for a future explicit operator
  sidecar write adapter. It defines input schemas, dry-run preconditions, write
  modes, statuses, allowed files, forbidden content, path safety, and receipt
  requirements while still not writing sidecars, mutating archives, wiring
  runtime, approving resolver refs, scoring, proving, or authorizing action.

- [Decision Work Explicit Operator Sidecar Write Adapter](../conversation-understanding/decision-work-explicit-operator-sidecar-write-adapter-v0.md)

  PR210's deterministic fixture-only explicit operator write adapter and CLI.
  It can write sidecar-shaped files only into safe caller-supplied temp/output
  `decision_work` directories and emits a fixture-only receipt while still not
  writing real archives, wiring runtime, approving resolver refs, scoring,
  proving, or authorizing action.

- [Decision Work Explicit Operator Sidecar Write Review](../conversation-understanding/decision-work-explicit-operator-sidecar-write-review-v0.md)

  PR211's docs/review/tests-only review of launch/deploy fixture writes. It
  confirms fixture-only status, deploy runtime blocking, path safety, and no
  real archive mutation, runtime wiring, resolver approval, scoring, proof
  claims, or action authorization before a package gate.

- [Decision Work Explicit Operator Sidecar Write Package Gate](../conversation-understanding/decision-work-explicit-operator-sidecar-write-package-gate-v0.md)

  PR212's package gate and manifest for PR210-PR211. It packages controlled
  explicit operator sidecar write v1 for safe fixture/operator target dirs
  while still excluding real archive mutation as normal behavior, runtime
  wiring, resolver approval, proof, scoring, certification, and action
  authorization.

- [Decision Work Controlled Archive Sidecar Write Fixture Plan](../conversation-understanding/decision-work-controlled-archive-sidecar-write-fixture-plan-v0.md)

  PR213's docs/review/tests-only plan for synthetic archive-shaped fixture
  writes. It keeps real completed-run archives, historical archive mutation,
  archive-hook edits, runtime wiring, resolver approval, proof, scoring, and
  action authorization forbidden while gating to a controlled fixture adapter.

- [Decision Work Controlled Archive Sidecar Write Fixture Adapter](../conversation-understanding/decision-work-controlled-archive-sidecar-write-fixture-adapter-v0.md)

  PR214's deterministic adapter and CLI for synthetic archive-shaped fixture
  writes. It writes only under explicit safe temp/operator archive-like roots,
  preserves deploy blocked state, and still refuses real archive paths,
  existing historical archive paths, repo/runtime paths, resolver approval,
  proof, scoring, and action authorization.

- [Decision Work Controlled Archive Sidecar Write Fixture Review](../conversation-understanding/decision-work-controlled-archive-sidecar-write-fixture-review-v0.md)

  PR215's docs/review/tests-only review of launch/deploy synthetic
  archive-shaped fixture writes. It confirms deploy blocking, unsafe
  path/source rejection, and no real archive mutation, archive-hook edit,
  runtime wiring, resolver approval, proof, scoring, or action authorization
  before a package gate.

- [Decision Work Controlled Archive Sidecar Write Fixture Package Gate](../conversation-understanding/decision-work-controlled-archive-sidecar-write-fixture-package-gate-v0.md)

  PR216's package gate and manifest for PR213-PR215. It packages synthetic
  archive-shaped fixture write v1 while still excluding real archive mutation,
  archive-hook integration, runtime wiring, resolver approval, proof, scoring,
  certification, and action authorization.

- [Decision Work Sidecar Internal v1 Completion PRD](../conversation-understanding/decision-work-sidecar-internal-v1-completion-prd-v0.md)

  PR217's current-state and finish-line PRD before real archive mutation. It
  defines Internal v1 as complete only when an operator can validate safe
  generated Decision Work artifacts, dry-run the sidecar, and explicitly write
  a `decision_work/` sidecar into a real completed-run archive with receipts
  and hard non-claims. It records a six-PR ballpark path from PR218 through
  PR223 and recommends PR218 Real Archive Sidecar Write Plan v0 next.

- [Decision Work Real Archive Sidecar Write Plan](../conversation-understanding/decision-work-real-archive-sidecar-write-plan-v0.md)

  PR218's plan gate for the first controlled real archive sidecar write
  boundary. It defines explicit operator confirmation, archive marker
  requirements, matching packet/dry-run preconditions, no-overwrite policy,
  receipt semantics, blocked-state deploy handling, and refusal rules before
  PR219 implements a command-only adapter.

- [Decision Work Real Archive Sidecar Write Adapter](../conversation-understanding/decision-work-real-archive-sidecar-write-adapter-v0.md)

  PR219's command-only adapter and CLI for explicit operator-confirmed writes
  into archive-markered completed-run directories. It writes only the allowed
  `decision_work/` file set, preserves deploy blocked state, refuses unsafe
  targets and existing sidecars, and still does not wire runtime, edit archive
  hooks, approve resolver refs, score, prove, or authorize action.

- [Decision Work Real Archive Sidecar Write Review](../conversation-understanding/decision-work-real-archive-sidecar-write-review-v0.md)

  PR220's review gate over fresh launch/deploy synthetic completed-run archive
  writes. It confirms allowed files, no-overwrite and unsafe-input refusals,
  deploy blocked-state preservation, and no runtime wiring, archive-hook edit,
  resolver approval, default-on behavior, scoring, proof, or action
  authorization before a package gate.

- [Decision Work Real Archive Sidecar Write Package Gate](../conversation-understanding/decision-work-real-archive-sidecar-write-package-gate-v0.md)

  PR221's package gate and manifest for PR218-PR220. It packages command-only
  real archive sidecar write v1 for explicit operator-confirmed, no-overwrite
  writes validated against synthetic completed-run archive dirs, while still
  excluding runtime wiring, archive-hook integration, default-on behavior,
  resolver approval, proof, scoring, certification, and action authorization.

- [Decision Work Sidecar Internal v1 Operator Runbook](../conversation-understanding/decision-work-sidecar-internal-v1-operator-runbook-v0.md)

  PR222's operator runbook for the Internal v1 command flow from generated read
  intake through sidecar write receipt inspection. It uses placeholders, keeps
  blocked/deferred handling explicit, and still does not add runtime wiring,
  archive-hook integration, resolver approval, proof, scoring, or action
  authorization.

- [Decision Work Sidecar Internal v1 Current State](decision-work-sidecar-internal-v1-current-state.md)

  PR223's closeout narrative for the internal sidecar-write phase. It explains
  what the command-only sidecar pipeline can now do, why blocked-state sidecars
  matter, and why Internal v1 is not customer-ready automation, default-on
  runtime behavior, resolver approval, product proof, scoring, or action
  authorization.

- [Decision Work Sidecar Automation Readiness PRD](../conversation-understanding/decision-work-sidecar-automation-readiness-prd-v0.md)

  PR224's phase anchor after Internal v1. It keeps the next phase offline and
  operator-directed, defines sidecar-ready, blocked, deferred, and rejected
  states for newly completed runs, and recommends an offline operator runner
  plan without adding a runner, queue worker, runtime hook, resolver approval,
  proof, scoring, or action authorization.

- [Decision Work Offline Operator Runner Plan](../conversation-understanding/decision-work-offline-operator-runner-plan-v0.md)

  PR225's plan-only first slice for automation readiness. It defines a future
  one-shot command runner that orchestrates existing CLIs from explicit paths,
  emits a runner summary, preserves blocked-state outcomes, and keeps write
  mode optional/default-off without adding a queue worker, runtime hook,
  semantic interpretation, resolver approval, proof, scoring, or action
  authorization.

- [Decision Work Offline Operator Runner Adapter](../conversation-understanding/decision-work-offline-operator-runner-adapter-v0.md)

  PR226's runner adapter executes that one-shot command flow through dry-run
  readiness only. It preserves missingness and blockers in `runner_summary.json`
  and stops before any real archive write, even when write flags are supplied.

- [Decision Work Offline Operator Runner Fixture Review](../conversation-understanding/decision-work-offline-operator-runner-fixture-review-v0.md)

  PR227 reviews the runner over controlled launch/deploy and blocker fixtures.
  It confirms readiness, blocked-state readiness, defer/block behavior, and the
  no-write/no-runtime/no-approval boundary before any non-curated pilot plan.

- [Decision Work Non-Curated Completed-Run Pilot Plan](../conversation-understanding/decision-work-non-curated-completed-run-pilot-plan-v0.md)

  PR228 plans the first non-curated completed-run pilot. It keeps the next step
  fixture/sanitized by default, explicit-input-only, temp-output-only, and still
  outside semantic generation, queue workers, runtime wiring, resolver
  approval, sidecar writes, proof, scoring, and action authorization.

The core board-level message is:

> Lolla is not only trying to produce a better answer. It is trying to preserve,
> challenge, and inspect the path to the answer so serious AI-assisted decisions
> are less likely to hide weak assumptions inside fluent prose.
