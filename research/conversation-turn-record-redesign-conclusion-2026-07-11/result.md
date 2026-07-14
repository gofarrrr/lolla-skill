# Conversation turn-record redesign conclusion

Status: material product decision required  
Date: 2026-07-11

## Conclusion

Neither tested architecture should advance.

The representation itself works: both architectures preserved all reviewed
material provider-free across five cases and compiled valid, graph-isolated
handoffs. Actual model behavior did not reproduce that representation. The
single reader either filled its available capacity or, after compression
instructions, lost important reviewed signals. The three-lens consolidator was
smaller but added malformed outputs, incomplete input custody, and the same
thread and claim-strength losses.

After the one allowed generic repair, Architecture A met count and byte budgets
but recovered only one-third of reviewed moves and threads and one-fifth of
reviewed claim-plus-strength targets. Architecture B exceeded the count target,
quarantined one window, and recovered only one-third of reviewed threads and
one-fifth of claim-plus-strength targets.

No transfer or global synthesis was run.

## What this changes

The conflict is now explicit:

- an accountability artifact should preserve broad conversational material,
  including minority signals and apparent noise;
- a reasoning handoff must be compact enough for reliable fresh-context
  synthesis;
- making one normalized record satisfy both caused either overload or loss.

The recommended product boundary is two linked artifacts:

1. an append-only broad audit ledger with exact source and complete custody;
2. a separately evaluated compact reasoning handoff selected probabilistically,
   with lineage to every included or excluded audit item.

Deterministic code would still own identity, lineage, budgets, and quarantine—not
semantic selection.

This is a founder-level product decision because it changes what the receipt and
reasoning input promise to be. It should be decided before another technical
architecture or provider experiment.
