# HTML Case Learning Artifact Examples

Generated with:

```bash
python3 scripts/render_case_learning_html.py --result <archived-result.json> --output <example>.html
```

Examples:

- `solo-founder-pivot-20260511T143033Z.html` — newer run with memo fields,
  private enrichment, valid ledger, and degraded live-output health.
- `third-year-phd-student-20260430T140800Z.html` — newer run with memo fields
  and richer model-card material.
- `mother-deciding-protect-year-20260428T093545Z.html` — older archived run
  without the upgraded memo fields, exercising fallback behavior.

These files are review artifacts for the first HTML-renderer slice. They are
not canonical run outputs; regenerate them from the archived `result.json`
files when the renderer changes.
