# Mental Model Teacher Product Surface Package Gate v0

Status: PR-P11 package gate
Date: 2026-07-05

Manifest:
[Mental Model Teacher product surface package manifest](mental-model-teacher-product-surface-package-manifest-v0.json)

## Purpose

PR-P11 packages the offline Mental Model Teacher product-surface pilot created across PR-P1 through PR-P10.

This is a package gate. It does not expand the corpus, wire runtime behavior, call providers or models, complete human review, claim product proof, claim answer correctness, claim advice correctness, certify output quality, or authorize action.

## Current State

- Pilot model pages: `3`.
- Pilot relation pages: `2`.
- Fixture Teacher lesson pages: `1`.
- Fixture graph data objects: `1`.
- Static graph prototype: `true` using `dependency_free_svg`.
- Three-case Teacher lesson pages: `3`.
- Three-case graph neighborhoods: `3`.
- UX review packet cases: `3`.
- Human review completed: `false`.
- Product proof claimed: `false`.
- Runtime integration authorized: `false`.

## What Is Functional

- Substrate inventory and exposure policy exist for existing model, graph, curation, embedding, affordance, and eval assets.
- Product-safe contracts exist for model pages, relation pages, Teacher lessons, and visual graphs.
- A small pilot has static model and relation pages rendered as readable Markdown.
- A fixture Teacher lesson, lesson graph data object, and local static graph prototype exist.
- Three imported Teacher cases now have productized lesson pages and graph-neighborhood JSON.
- A UX review packet compares productized lessons against raw Teacher cards, notes, relation source views, and graph JSON.
- A blank human review form exists with no positive defaults.

## What Remains Missing

- Human review is not completed and no human validation is claimed.
- Full model product pages and full relation product pages do not yet cover every real three-case model and relation.
- The graph prototype is local and static; it is not a full-corpus graph and not runtime UI.
- Relation source views in the three-case packet remain imported OKF source views, not full product relation pages for every case.
- The high-risk CEO case remains a teaching artifact with visible legal, HR, governance, interpersonal, answer-correctness, and advice-correctness caveats.
- PR-P12 full-corpus graph planning and PR-P13 full-corpus pilot remain deferred.

## Strongest Useful Signal

The offline product lane now connects case anchor, reasoning move, model relationship, practice rep, page clickthroughs, graph neighborhoods, source custody, missingness, and a blank human review packet without collapsing into runtime, Decision Work, Observatory, Product Delta, or proof language.

## Strongest Unresolved Risk

The pilot is reviewable but not validated: without completed human review and broader real-case model/relation product pages, expansion could overfit the three cases or make graph/source artifacts look more authoritative than the evidence supports.

## Validation Checklist

- `python3 -m py_compile engine/system_b/mental_model_teacher_product_surface_package_gate.py tests/test_mental_model_teacher_product_surface_package_gate.py`
- `PYTHONPATH=. pytest -q tests/test_mental_model_teacher_product_surface_package_gate.py`
- `PYTHONPATH=. pytest -q tests/test_mental_model_teacher*.py`
- `PYTHONPATH=. python3 -m engine.system_b.mental_model_teacher_product_surface_package_gate`
- `jq empty over package manifest and package review JSON`
- `Product Delta boundary lint over package doc, manifest, and review JSON`
- `Markdown local-link check over touched Markdown files`
- `trailing whitespace scan over touched files`
- `privacy/content marker scan over touched package files`
- `git diff --check`
- `git status --short -- SKILL.md scripts/skill scripts/archive_run.py`
- `git diff --cached --name-only empty after commit`

## Boundary And Non-Claims

- `not_product_proof`
- `not_human_validation`
- `not_answer_correctness`
- `not_advice_correctness`
- `not_runtime_integration`
- `not_action_authorization`
- `not_full_corpus_build`
- `not_customer_ready`
- `not_graph_edge_proof`
- `not_embedding_similarity_validation`
- `not_decision_work`
- `not_observatory`
- `not_product_delta`
- `not_lolla_skill_runtime`

## Decision Gate

Selected gate:

```text
needs_human_review_before_expansion
```

Recommended next action:

```text
collect_human_review_before_expansion_or_revision
```

PR-P12 and PR-P13 should remain deferred until a human review changes this gate or supplies concrete revision requirements.

## Suggested Staging Source

Use the package manifest as the staging source of truth. Do not stage broad directories or unrelated untracked plans/reviews.

```bash
git add -- $(python3 - <<'PY'
import json
from pathlib import Path

manifest_path = Path('docs/product/mental-model-teacher-product-surface-package-manifest-v0.json')
manifest = json.loads(manifest_path.read_text())
paths = []
for group in manifest['included_files'].values():
    paths.extend(group)
seen = set()
for path in paths:
    if path not in seen:
        seen.add(path)
        print(path)
PY
)
```
