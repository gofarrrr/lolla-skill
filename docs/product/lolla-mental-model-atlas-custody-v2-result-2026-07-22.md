# Mental Model Atlas custody V2 result

Date: 2026-07-22
Status: complete locally, provider-free
Decision: `adopt_versioned_current_custody_preserve_v1_exactly`
Provider calls: 0
Provider cost: `$0.00`

## Result

The Atlas active data path now uses repository-local custody without rewriting
its frozen evidence.

```text
immutable V1 packages
  -> exact SHA-256 preservation gate

current repository-local model manifest + recovered curation
  -> deterministic V2 package builders
  -> field-by-field V1/V2 comparison
  -> phase1-v2 / card-first-v2 / navigation-v2
  -> the same three browser fetch points
```

V1 remains the exact historical checkpoint. V2 is a custody republication of
the same semantic and interface records.

## Exact outcome

- frozen V1 identities checked: 6;
- V2 packages: 3;
- Phase 1 artifacts: 12;
- card-first artifacts: 1;
- navigation artifacts: 1;
- canonical models: 222;
- exact authored relations: 1,358;
- classified custody differences: 2,182;
- unexpected differences: 0;
- model and relation identity vectors equal: yes;
- layout coordinate hashes equal: yes;
- semantic and interface fields equal: yes.

The larger difference count than the earlier 520-leaf Phase 1 dry run is
expected: the final proof covers all three packages, their manifests, every
current curation reference, and the explicit V2 release markers.

## Browser change

Only three static asset paths changed:

- `data/phase1/` to `data/phase1-v2/`;
- `data/navigation-v1/neighborhood-index.json` to
  `data/navigation-v2/neighborhood-index.json`;
- `data/card-first-v1/pages/model-abstraction.json` to
  `data/card-first-v2/pages/model-abstraction.json`.

No extra request, fallback, state transition, component, render path, bundle
dependency, or semantic browser operation was added. Existing cached navigation
loading remains one request owned by the same module.

## Frozen V1 boundary

The migration refuses to run if any of these identities changes:

| Artifact | SHA-256 |
| --- | --- |
| Phase 1 manifest | `203999a61dbe9c2e943bbcb9f5b4dd87779d4557ea9fcfbd50b3e9d59e816c52` |
| Phase 1 Abstraction page | `8cc07cbbf68f399dcd5787df9067bd3a3646068b59ed691ca043ffc9e9ce406f` |
| Card-first V1 manifest | `41f4f19d98d94335993b28b734fae4100ad0dc5b622bd4f7bf93f037640dabdd` |
| Card-first V1 Abstraction page | `46a666bb276c1ebdcb6ecd4045cbb440fcb0538b5a0ca7d2abc813f113f4512d` |
| Navigation V1 manifest | `fcd2f994ea03221ceea31601c1e991e46750512154222bb5da536f866a24de62` |
| Navigation V1 index | `565ccef599ecc018f3501c36febadb9468ecaaaab310598d0c6e467ffd33417f` |

## Rebuild and validate

Write the deterministic packages:

```bash
PYTHONPATH=. python3 scripts/product/build_mental_model_atlas_custody_v2.py
```

Validate the checked-in packages without writing:

```bash
PYTHONPATH=. python3 scripts/product/build_mental_model_atlas_custody_v2.py --validate-only
PYTHONPATH=. pytest -q tests/test_mental_model_atlas_custody_v2.py
```

The machine-readable evidence is
`docs/evals/lolla-mental-model-atlas-custody-v2-evidence.json`.

## What this does not establish

- V2 custody is not new relation evidence.
- Equal identities do not prove that a relationship is true or useful.
- A passing browser build is not founder or native screen-reader acceptance.
- The migration does not clear source rights or authorize public deployment.
- Frozen V1 remains evidence, not a fallback runtime.
