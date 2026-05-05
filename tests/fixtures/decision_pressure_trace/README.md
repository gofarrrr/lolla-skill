# Decision Pressure Trace Fixtures

These fixtures are reviewed trace artifacts, not generated runtime outputs.

Current fixture:

- `gate4_3case_pr18_valid.json`

The fixture represents the PR18 static Observatory prototype under the PR19
`decision_pressure_trace.v1` contract. It preserves:

- the three PR13/PR14 selected pressure clusters;
- PR17 v4 support without changing selection;
- source-affordance references checked against `affordances_v4.json`;
- suppressed candidates as audit information;
- the PhD competitive-dynamics coverage blank;
- `status: draft_review_only`;
- `runtime_policy: runtime_dormant`.

Future fixture-only adapters may validate, normalize, package, or report on
these fixtures. They must not select pressures semantically, generate new
pressure copy, render live Observatory UI, or make the trace user-facing.
