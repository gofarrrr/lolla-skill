# Qualitative spot-check — post-ship canonical_key outputs

**Date:** 2026-04-22
**Scope:** 3 of the post-ship extractions — one from Mode C (drift0), one from the newest cross-capture (20260422T155622Z), one from the oldest cross-capture (20260421T144534Z).

## Observed pattern

Every canonical_key produced by the new extractor passes the format validator (invalid_key_rate = 0.000 on all 14 runs). The slugs are well-formed, short, and readable. **But the LLM oscillates between multiple valid slugs for the same concept.** Three clusters of near-matches show up repeatedly:

### Cluster 1 — Marcus's compensation (1 concept, 3 slugs)

| Slug | Seen in |
|---|---|
| `marcus-comp` | Mode C runs 0, 1, 3, 4; cross-capture 100308Z, 130506Z |
| `marcus-comp-below-market` | Cross-capture 144534Z, 162225Z, 091837Z |
| `marcus-comp-undermarket` | Mode C run 2; cross-capture 172513Z, 113930Z, 123205Z, 155622Z |

All three name the same constraint. Exact-text Jaccard counts them as three distinct items.

### Cluster 2 — Retention risk if Marcus leaves (1 concept, 5 slugs)

| Slug | Seen in |
|---|---|
| `talent-retention-risk` | Mode C runs 0, 1 |
| `marcus-retention-risk` | Mode C run 3; cross-capture runs 144534Z, 162225Z, 172513Z, 091837Z, 100308Z, 113930Z, 130506Z |
| `team-retention-risk` | Mode C run 4 |
| `engineer-retention-risk` | Cross-capture 155622Z |
| `engineer-flight-risk` | Mode C run 2 |

The disagreement is on WHO the retention subject is — Marcus himself, the engineers who follow him, the team, or "talent" generically. This is actually a substantive ambiguity in the Marcus conversation that the slug rule doesn't resolve.

### Cluster 3 — Platform / prototype (1 concept, 3 slugs)

| Slug | Seen in |
|---|---|
| `platform-prototype` | Mode C all 5 runs; cross-capture 8 of 9 |
| `platform-productization` | Cross-capture 091837Z |
| `platform-idea` | Cross-capture 155622Z |

Mostly stable (9/14 use `platform-prototype`), but two runs pick different subject words.

## Read

**The slug format is working; the slug identity is not.** The prompt tells the LLM to "name the subject, not the sentence" and gives examples, but doesn't force a single canonical answer when the constraint has multiple plausible subjects (e.g., "is this about Marcus or about the engineers who follow him?"). Different samples resolve the same ambiguity differently.

Two characteristics of the failure:

1. **The near-matches are often 2 of 3 tokens apart.** `marcus-retention-risk` vs `team-retention-risk` share 2 tokens and differ on the first. Fuzzy matching or token-overlap scoring would rate these as ~66% similar; exact-set Jaccard treats them as disjoint.
2. **Some of the "drift" is a real ambiguity, not a phrasing artifact.** Cluster 2 in particular — whether the retention concern is about Marcus or about the engineers he'd take with him — is a substantive disagreement that the slug can't finesse. The constraint text itself phrases this ambiguously in the conversation.

## What this does NOT rule out

- The slug format rule itself is sound (0% invalid keys across 14 runs).
- The ≤120-char `constraint` canonical-form rule tightened exact-text Jaccard materially (0.000 → 0.330 Mode C; 0.010 → 0.064 cross-capture). This side-effect improvement is real and would likely persist with any further canonical_key iteration.
- The same concept-level agreement exists — eyes can cluster the 14 runs' constraints into roughly the same 5-6 subject groups. The measurement metric just doesn't count near-matches.
