# Designed ambiguous conversation corpus result

Status: **five development cases ready; not a clean holdout**  
Date: 2026-07-10

The independent source-model call exceeded its frozen outer wall ceiling and
was stopped without a retry. Because the runner had not written its attempted-
call sidecar before blocking on the response stream, usage, cost, served model,
and provider output remain unknown. That failure is preserved.

We then used the founder-authorized provider-free fallback and wrote five
development conversations directly. Each contains seven user/assistant turn
pairs and roughly 1,150–1,190 words. They deliberately resemble real difficult
conversations rather than benchmark prompts:

- important information arrives late;
- the user resists or corrects the assistant more than once;
- both sides of the decision retain legitimate value;
- the assistant is helpful but does not resolve every frame cleanly;
- endings are provisional or explicitly unresolved;
- no Lolla, graph, mental-model, expected-pressure, or gold-answer language is
  present.

The cases cover product scope, nonprofit expansion, creative partnership,
research-tool release, and a family archive. All five pass provider-free source
shape and same-session safety/realism review.

The pre-ranked first development case is
`amb1-case02-nonprofit-scale`. It was not chosen for likely Lolla or graph
activation. Because Codex in this same project session designed and authored
the corpus, it is a development fixture—not a clean causal holdout.

The next safe step is to freeze a bounded Stage A development contract for that
case. No Stage A or downstream provider call is authorized yet.
