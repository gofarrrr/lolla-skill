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
  work into PR113-PR152 so the next steps stay grounded in the existing
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

The core board-level message is:

> Lolla is not only trying to produce a better answer. It is trying to preserve,
> challenge, and inspect the path to the answer so serious AI-assisted decisions
> are less likely to hide weak assumptions inside fluent prose.
