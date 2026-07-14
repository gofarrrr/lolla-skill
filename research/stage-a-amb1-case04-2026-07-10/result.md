# Ambiguous development Case 04 — Stage A result

Date: 2026-07-10  
Status: full run completed; formal gate failed; no rerun

## Simple result

This was the first designed ambiguous conversation to complete the full current
Lolla machinery. It preserved all 14 messages, six exact reasoning passages,
direct OpenAI embeddings, full model and usage custody, a private pressure
table, and V60 selection. The run took about 35 seconds, used 35 OpenRouter
calls and seven direct OpenAI calls, cost an estimated `$0.036504`, and made no
revision call or experiment retry.

The formal Stage A result is still **failed**. The only failed gate was an
inherited sub-budget of 22 core calls; this case used 27 because the current
pipeline made 13 fixed calls plus one Pass-2 call for each of 14 triggered
tendencies. Total calls, cost, timeouts, model attribution, capture, quotes, and
all other frozen gates passed. We preserve the failure instead of changing the
contract after seeing the result.

## What the pressure told us

The raw artifacts contain useful material. The strongest candidates are:

1. Define the workshop preview as a real experiment: name its hypothesis,
   success/failure/inconclusive thresholds, and the public-beta decision that
   changes for each result.
2. Make the support trade-off concrete: state what work or quality is displaced
   by eight weeks of office hours, who owns the allocation during the
   maintainer's leave, and what is deliberately not done.
3. Define observable signs that the preview has become a de facto durable
   release, then precommit what changes when those signs appear.

But the noise is substantial. The system wrongly diagnosed doubt avoidance,
prescribed an arbitrary three-option procedure, repeated incentives the
assistant had already named, asked for unsupported software base rates,
repeated the already-rejected wider private-beta path, suggested assigning the
volunteer installer to support, and invented a public no-support agreement with
the two labs.

## The most important defect found

Eight V60 cards were selected, but the actual Step-6 private table included only
five. More seriously, it carried their names and selection reasons but none of
their operational mechanisms. The renderer expected legacy `text` fields while
the current records store content in `mechanism` and guardrails in `reason`.
Therefore the strongest raw candidates existed in the artifact but were not
actually delivered to the reconsiderer.

That transport defect is now repaired without adding model calls. The repaired
table renders the selected mechanism and absence guardrail, records exact
selected/presented/omitted counts and IDs, and visibly discloses the five-card
section cap. Fifty-five focused tests pass.

## What we know now

Lolla can run end to end on realistic ambiguity and can retrieve genuinely
interesting pressure. It is not yet reliable enough to claim that the second
thinker receives a clean, complete, well-calibrated packet. Extraction errors
can propagate into false pressure, the companion lane can fail malformed, and
the deterministic transport can silently drop the very chunk content that
justified selection.

The next work is therefore not another paid run. It is to repair the call-budget
contract, make companion failure custody truthful, and measure extraction
provenance/source-strength/thread-status quality across the full five-case
development corpus. Downstream answer comparison and graph attribution remain
unauthorized.
