# HTML Case Learning Artifact

## Product Job

The HTML artifact is not a prettier Markdown memo and not a portable copy of
the Observatory.

Its job is to turn one Lolla run into a compact learning surface:

1. What changed in the advice?
2. What reasoning pattern made the change necessary?
3. Which few mental models are worth learning from this case?
4. What should the user still check?
5. How can an operator inspect the process if needed?

The first screen stays decision-first. The middle becomes educational. The
trace stays collapsed.

## Surface Relationship

| Surface | Primary job |
| --- | --- |
| Chat | Live reconsideration in the conversation |
| Markdown memo | Portable decision note and plain-text fallback |
| HTML artifact | Personalized reasoning explainer |
| Observatory | Full instrument panel and audit trace |

## Default Structure

1. **Decision opening** — title, run-health strip, orientation note.
2. **What Changed** — up to four concrete shifts from `memo_what_changed`.
3. **What This Case Teaches** — observed pattern, reasoning pressure, reusable
   check.
4. **Mental Models Worth Learning** — up to four selected model cards. Each card
   must explain why the model activated, what it changed, a reusable question,
   and a guardrail.
5. **Questions Still Open** — capped structural gap questions.
6. **Alternative Frames** — reframings when present.
7. **Technical Trace** — collapsed by default; contains run health, private
   enrichment summary, cost, and pressure-check status.

## Constraints

- Keep `result.json` as the source of truth.
- Render deterministically; no LLM call in the renderer.
- Cap every section. The HTML artifact earns its value by selecting and
  arranging, not by dumping the full run.
- Escape all interpolated content.
- Do not put lane names, card names, chunk/ledger language, or candidate counts
  above the collapsed technical trace.
- Keep Observatory as the full-detail surface. If the user needs every
  candidate, route, chunk, and raw audit panel, send them there.

## CLI

```bash
python3 scripts/render_case_learning_html.py \
  --result /tmp/lolla_${LOLLA_RUN_ID}_result.json \
  --output /tmp/lolla_${LOLLA_RUN_ID}_memo.html
```

The artifact is a single HTML file and opens directly in a browser.
