# Prerequisite Semantics (Wave 6 — Prerequisite Chains)

Curated dependency edges discovered by latticework graph analysis and validated against canonical articles.

Each file captures a single A → B prerequisite: model A must be understood or active for model B to function properly. These are **depend-on** edges that the existing relationship graph (allies/antagonists/tensions) does not capture.

## Methodology

1. **Discovery**: `scripts/build_latticework.py` extracted candidate prerequisite chains from article content (explicit "requires", "foundation for", "prerequisite" language).
2. **Validation**: Each chain was validated by reading both canonical articles,
   now held in `data/model_sources/`, and making a semantic judgment on whether
   the dependency is real.
3. **Curation**: Validated chains written as per-dependent-model JSON with source quotes and confidence levels.

## Schema

```json
{
  "model_id": "dependent-model",
  "source_file": "Dependent_Model_rag.md",
  "prerequisites": [
    {
      "prerequisite_model_id": "prerequisite-model",
      "dependency_type": "requires | foundation-for | applied-form-of",
      "rationale_text": "Why B requires A",
      "source_quote": "Direct quote from canonical article",
      "source_article": "Which article the quote comes from",
      "extraction_type": "explicit | normalized",
      "confidence": "high | medium",
      "validation_status": "confirmed | questionable | rejected"
    }
  ],
  "curation_notes": {}
}
```

## Status

- 16 candidate chains from latticework discovery
- 15 confirmed, 1 downgraded to "strong ally" (first-principles-thinking → inversion)
- Validated 2026-04-07
