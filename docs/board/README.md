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
  work into PR113-PR118 so the next steps stay grounded in the existing
  receipt, Decision Trail, Product Delta, and lint machinery.

The core board-level message is:

> Lolla is not only trying to produce a better answer. It is trying to preserve,
> challenge, and inspect the path to the answer so serious AI-assisted decisions
> are less likely to hide weak assumptions inside fluent prose.
