# Conversation-state extraction probe v4

Status: closed; failed on the first semantic case. See `result.md` and
`decision.json`.

V3 proved that JSON wire mode reaches inference, but the formatting prompt did
not include the typed schema that provider-side enforcement had previously
carried. V4 adds that unchanged schema to the formatting prompt. The semantic
extraction instruction, cases, model, thresholds, and stop rule do not change.

V4 attempted to forbid the v3 custody defect where an invalid response's empty
packet was written as an observed artifact. The repair suppressed empty packets
but not non-empty invalid packets. The failed model packet therefore received an
observed path despite two validation errors. It is quarantined for postmortem,
not accepted as state; this implementation defect is preserved rather than
silently rewritten.
