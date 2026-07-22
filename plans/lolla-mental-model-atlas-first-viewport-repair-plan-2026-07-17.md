# Mental Model Atlas first-viewport repair plan

Date: 2026-07-17

Status: implemented provider-free; verification recorded in the paired result.

## Falsifiable question

Can a first-time visitor choose a named canonical model, use search, and see the
selected model's meaning and next action without scrolling at representative
laptop and mobile viewports?

## One causal change

Replace the explanatory-first Atlas entry with an action-first entry while
preserving the canonical graph, identities, relations, source custody, and
complete-versus-summary-only page boundary.

## Allowed work

- compact the existing Atlas, Library, and Abstraction opening geometry;
- expose deterministic named model actions from the loaded projection;
- make exact text-search matches directly selectable by click or Enter;
- show selected-model feedback before the graph in document order;
- make displayed connection counts act as relationship filters;
- progressively disclose relationship grammar;
- preserve mobile list access and the visual-map alternative;
- add local interaction tests and browser screenshots.

## Forbidden work

- provider calls or generated meaning;
- new models, relations, summaries, teaching pages, or inferred search matches;
- relationship ranking or importance claims;
- Phase 2, Teacher revival, deployment, runtime integration, or product-value
  claims;
- changes to frozen historical evidence.

## Acceptance checks

At `1280x720` and `390x844`, without scrolling:

1. at least one named model action is visible;
2. searching for `abstraction` exposes a selectable exact match;
3. Enter selects that match and clears the filtering query;
4. the selected name, summary, and full-page action are visible;
5. non-actionable opening counts do not displace the task;
6. the Abstraction chapter navigation is fully visible at `1280x720`.

Mechanical checks and screenshots are local structural evidence. They do not
establish native screen-reader acceptance, publication rights, learning value,
or real-user usefulness.
