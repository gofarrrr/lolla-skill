# Phase 1 shim equivalence — 10-case corpus results

Evidence that `_context_to_critique(ctx)` produces a CritiqueRequest
bit-identical to `_map_to_critique_request(extraction_dict, assistant_text)`
when exercised against real corpus conversation text.

**Note on scope:** the task-file 6.0 text describes pipeline-level
output comparison. The pipeline uses `temperature=0.2`, so it is
non-deterministic by design — pipeline-output diffs would conflate
shim bugs with LLM noise. This check operates at the architectural
boundary the shim actually owns (`CritiqueRequest` construction),
which is LLM-independent and therefore cleanly testable.

| case | query | vanilla_answer | query length (legacy → shim) | vanilla length (legacy → shim) |
|------|-------|----------------|------------------------------|-------------------------------|
| friendship_money | match | match | 535 → 535 | 7197 → 7197 |
| messy_three_problems | match | match | 535 → 535 | 9829 → 9829 |
| multi_offer | match | match | 535 → 535 | 11671 → 11671 |
| oncologist | match | match | 535 → 535 | 9622 → 9622 |
| parenting_teen | match | match | 535 → 535 | 14954 → 14954 |
| phd_research | match | match | 535 → 535 | 21538 → 21538 |
| real_estate | match | match | 535 → 535 | 4949 → 4949 |
| startup_pivot | match | match | 535 → 535 | 6030 → 6030 |
| user_has_plan | match | match | 535 → 535 | 7257 → 7257 |
| whistleblower | match | match | 535 → 535 | 13951 → 13951 |

**Result: 10/10 cases match bit-for-bit on both `query` and `vanilla_answer`.**

