"""Package gate builder for the Mental Model Teacher product surface pilot.

This PR-P11 builder summarizes checked-in PR-P1 through PR-P10 artifacts. It
does not run Lolla, call providers, wire runtime behavior, or fill human review.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from .mental_model_teacher_pilot_page_builder import REPO_ROOT


PACKAGE_MANIFEST_SCHEMA_VERSION = (
    "lolla.mental_model_teacher.product_surface_package_manifest.v0"
)
PACKAGE_REVIEW_SCHEMA_VERSION = (
    "lolla.mental_model_teacher.product_surface_package_gate_review.v0"
)
PACKAGE_DATE = "2026-07-05"
PACKAGE_DOC_PATH = (
    REPO_ROOT / "docs/product/mental-model-teacher-product-surface-package-gate-v0.md"
)
PACKAGE_MANIFEST_PATH = (
    REPO_ROOT / "docs/product/mental-model-teacher-product-surface-package-manifest-v0.json"
)
PACKAGE_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-product-surface-package-gate-v0/review.json"
)

PILOT_RENDER_MANIFEST = (
    REPO_ROOT / "docs/product/mental-model-teacher-pilot-render-v0/manifest.json"
)
LESSON_RENDER_MANIFEST = (
    REPO_ROOT / "docs/product/mental-model-teacher-lesson-render-v0/manifest.json"
)
LESSON_GRAPH_MANIFEST = (
    REPO_ROOT / "docs/product/mental-model-teacher-lesson-graph-v0/manifest.json"
)
VISUAL_GRAPH_MANIFEST = (
    REPO_ROOT / "docs/product/mental-model-teacher-visual-graph-prototype-v0/manifest.json"
)
THREE_CASE_MANIFEST = (
    REPO_ROOT / "docs/product/mental-model-teacher-three-case-product-pilot-v0/manifest.json"
)
UX_PACKET_MANIFEST = (
    REPO_ROOT / "docs/product/mental-model-teacher-ux-review-packet-v0/manifest.json"
)
UX_FORM_JSON = (
    REPO_ROOT / "docs/product/mental-model-teacher-ux-review-packet-v0/human-review-form.json"
)

CASE_IDS = (
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
)

RELATION_SOURCE_FILES = {
    "launch-public-enterprise-beta": (
        "okf/mental_model_teacher/relations/"
        "authority-bias__first-principles-thinking__antagonist.md"
    ),
    "deploy-assisted-intake-routing": (
        "okf/mental_model_teacher/relations/"
        "cognitive-load-theory__optionality__structured_tension.md"
    ),
    "ceo-remove-founding-cofounder": (
        "okf/mental_model_teacher/relations/inversion__premortem__ally.md"
    ),
}


class MentalModelTeacherProductSurfacePackageGateError(ValueError):
    """Raised when the package gate cannot be rendered safely."""


def build_product_surface_package_gate(
    root: Path | str | None = None,
    package_doc_path: Path | str = PACKAGE_DOC_PATH,
    package_manifest_path: Path | str = PACKAGE_MANIFEST_PATH,
    package_review_path: Path | str = PACKAGE_REVIEW_PATH,
) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else REPO_ROOT
    doc_path = Path(package_doc_path)
    manifest_path = Path(package_manifest_path)
    review_path = Path(package_review_path)

    source_manifests = _source_manifests(repo_root)
    current_state = _current_state(source_manifests)
    included_files = _included_files()
    manifest = _package_manifest(
        current_state=current_state,
        included_files=included_files,
        package_doc_path=doc_path,
        package_manifest_path=manifest_path,
        package_review_path=review_path,
    )
    review = _review_json(manifest)

    _write_json(manifest_path, manifest)
    _write(doc_path, render_package_gate_doc(manifest))
    _write_json(review_path, review)
    return manifest


def render_package_gate_doc(manifest: dict[str, Any]) -> str:
    state = manifest["current_state"]
    lines = [
        "# Mental Model Teacher Product Surface Package Gate v0",
        "",
        "Status: PR-P11 package gate",
        f"Date: {PACKAGE_DATE}",
        "",
        "Manifest:",
        _md_link(
            "Mental Model Teacher product surface package manifest",
            manifest["package_manifest"],
            PACKAGE_DOC_PATH,
        ),
        "",
        "## Purpose",
        "",
        "PR-P11 packages the offline Mental Model Teacher product-surface pilot created across PR-P1 through PR-P10.",
        "",
        "This is a package gate. It does not expand the corpus, wire runtime behavior, call providers or models, complete human review, claim product proof, claim answer correctness, claim advice correctness, certify output quality, or authorize action.",
        "",
        "## Current State",
        "",
        f"- Pilot model pages: `{state['pilot_model_pages']}`.",
        f"- Pilot relation pages: `{state['pilot_relation_pages']}`.",
        f"- Fixture Teacher lesson pages: `{state['fixture_lesson_pages']}`.",
        f"- Fixture graph data objects: `{state['fixture_graphs']}`.",
        f"- Static graph prototype: `{_bool_text(state['static_graph_prototype'])}` using `{state['static_graph_renderer']}`.",
        f"- Three-case Teacher lesson pages: `{state['three_case_lesson_pages']}`.",
        f"- Three-case graph neighborhoods: `{state['three_case_graphs']}`.",
        f"- UX review packet cases: `{state['ux_review_case_count']}`.",
        f"- Human review completed: `{_bool_text(state['human_review_completed'])}`.",
        f"- Product proof claimed: `{_bool_text(state['product_proof'])}`.",
        f"- Runtime integration authorized: `{_bool_text(state['runtime_integration_authorized'])}`.",
        "",
        "## What Is Functional",
        "",
    ]
    for item in manifest["functional_surface"]:
        lines.append(f"- {item}")
    lines.extend(["", "## What Remains Missing", ""])
    for item in manifest["missing_or_incomplete"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Strongest Useful Signal",
            "",
            manifest["strongest_useful_signal"],
            "",
            "## Strongest Unresolved Risk",
            "",
            manifest["strongest_unresolved_risk"],
            "",
            "## Validation Checklist",
            "",
        ]
    )
    for item in manifest["validation_checklist"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Boundary And Non-Claims",
            "",
        ]
    )
    for claim in manifest["explicit_non_claims"]:
        lines.append(f"- `{claim}`")
    lines.extend(
        [
            "",
            "## Decision Gate",
            "",
            "Selected gate:",
            "",
            "```text",
            manifest["decision_gate"],
            "```",
            "",
            "Recommended next action:",
            "",
            "```text",
            manifest["recommended_next_action"],
            "```",
            "",
            "PR-P12 and PR-P13 should remain deferred until a human review changes this gate or supplies concrete revision requirements.",
            "",
            "## Suggested Staging Source",
            "",
            "Use the package manifest as the staging source of truth. Do not stage broad directories or unrelated untracked plans/reviews.",
            "",
            "```bash",
            "git add -- $(python3 - <<'PY'",
            "import json",
            "from pathlib import Path",
            "",
            f"manifest_path = Path('{manifest['package_manifest']}')",
            "manifest = json.loads(manifest_path.read_text())",
            "paths = []",
            "for group in manifest['included_files'].values():",
            "    paths.extend(group)",
            "seen = set()",
            "for path in paths:",
            "    if path not in seen:",
            "        seen.add(path)",
            "        print(path)",
            "PY",
            ")",
            "```",
        ]
    )
    return _finish(lines)


def _source_manifests(repo_root: Path) -> dict[str, dict[str, Any]]:
    return {
        "pilot_render": _load_json(repo_root / _repo_rel(PILOT_RENDER_MANIFEST)),
        "lesson_render": _load_json(repo_root / _repo_rel(LESSON_RENDER_MANIFEST)),
        "lesson_graph": _load_json(repo_root / _repo_rel(LESSON_GRAPH_MANIFEST)),
        "visual_graph": _load_json(repo_root / _repo_rel(VISUAL_GRAPH_MANIFEST)),
        "three_case": _load_json(repo_root / _repo_rel(THREE_CASE_MANIFEST)),
        "ux_packet": _load_json(repo_root / _repo_rel(UX_PACKET_MANIFEST)),
        "ux_form": _load_json(repo_root / _repo_rel(UX_FORM_JSON)),
    }


def _current_state(source_manifests: dict[str, dict[str, Any]]) -> dict[str, Any]:
    pilot_render = source_manifests["pilot_render"]
    lesson_render = source_manifests["lesson_render"]
    lesson_graph = source_manifests["lesson_graph"]
    visual_graph = source_manifests["visual_graph"]
    three_case = source_manifests["three_case"]
    ux_packet = source_manifests["ux_packet"]
    ux_form = source_manifests["ux_form"]
    return {
        "pilot_model_pages": pilot_render["model_page_count"],
        "pilot_relation_pages": pilot_render["relation_page_count"],
        "fixture_lesson_pages": lesson_render["lesson_count"],
        "fixture_graphs": lesson_graph["graph_count"],
        "static_graph_prototype": visual_graph["prototype_status"]
        == "static_visual_graph_prototype_ready_for_review",
        "static_graph_renderer": visual_graph["implementation"]["renderer"],
        "static_graph_external_network_required": visual_graph["implementation"][
            "external_network_required"
        ],
        "three_case_teacher_cases": three_case["case_count"],
        "three_case_lesson_pages": three_case["lesson_page_count"],
        "three_case_graphs": three_case["graph_count"],
        "three_case_high_risk_cases": three_case["high_risk_cases"],
        "ux_review_case_count": ux_packet["case_count"],
        "human_review_form_blank": ux_form["status"] == "blank_pending_human_review",
        "human_review_completed": ux_form["human_review_completed"],
        "human_validated": ux_form["human_validated"],
        "product_proof": ux_form["product_proof"],
        "runtime_integration_authorized": ux_form["non_claims"][
            "runtime_integration_authorized"
        ],
        "provider_or_model_calls": 0,
        "model_calls": 0,
        "archive_mutated": False,
        "source_package_present": True,
        "full_corpus_graph_built": False,
        "runtime_wiring_added": False,
    }


def _package_manifest(
    *,
    current_state: dict[str, Any],
    included_files: dict[str, list[str]],
    package_doc_path: Path,
    package_manifest_path: Path,
    package_review_path: Path,
) -> dict[str, Any]:
    manifest_ref = _safe_ref(package_manifest_path)
    doc_ref = _safe_ref(package_doc_path)
    review_ref = _safe_ref(package_review_path)
    included_files = dict(included_files)
    included_files["package_gate_files"] = [doc_ref, manifest_ref, review_ref]
    return {
        "schema_version": PACKAGE_MANIFEST_SCHEMA_VERSION,
        "package_status": "product_surface_pilot_packaged_for_human_review",
        "package_date": PACKAGE_DATE,
        "product_lane": "Mental Model Teacher Product Surface And Visual Library",
        "package_manifest": manifest_ref,
        "package_gate_doc": doc_ref,
        "package_review": review_ref,
        "decision_gate": "needs_human_review_before_expansion",
        "recommended_next_action": "collect_human_review_before_expansion_or_revision",
        "roadmap_scope": "PR-P1 through PR-P10 packaged; PR-P11 selects the next gate",
        "current_state": current_state,
        "roadmap_slices": _roadmap_slices(),
        "included_files": included_files,
        "teacher_source_package": _teacher_source_package(),
        "excluded_paths": [
            "SKILL.md",
            "scripts/skill/*",
            "scripts/archive_run.py",
            "plans/*",
            "reviews/synthetic/*",
            "docs/lolla-*",
            "docs/semantica-*",
            "docs/thoughtbox-*",
            "data/embeddings.db raw embedding index",
            "archive/*",
            "archives/*",
            "runs/*",
            "runtime hooks",
        ],
        "functional_surface": [
            "Substrate inventory and exposure policy exist for existing model, graph, curation, embedding, affordance, and eval assets.",
            "Product-safe contracts exist for model pages, relation pages, Teacher lessons, and visual graphs.",
            "A small pilot has static model and relation pages rendered as readable Markdown.",
            "A fixture Teacher lesson, lesson graph data object, and local static graph prototype exist.",
            "Three imported Teacher cases now have productized lesson pages and graph-neighborhood JSON.",
            "A UX review packet compares productized lessons against raw Teacher cards, notes, relation source views, and graph JSON.",
            "A blank human review form exists with no positive defaults.",
        ],
        "missing_or_incomplete": [
            "Human review is not completed and no human validation is claimed.",
            "Full model product pages and full relation product pages do not yet cover every real three-case model and relation.",
            "The graph prototype is local and static; it is not a full-corpus graph and not runtime UI.",
            "Relation source views in the three-case packet remain imported OKF source views, not full product relation pages for every case.",
            "The high-risk CEO case remains a teaching artifact with visible legal, HR, governance, interpersonal, answer-correctness, and advice-correctness caveats.",
            "PR-P12 full-corpus graph planning and PR-P13 full-corpus pilot remain deferred.",
        ],
        "strongest_useful_signal": (
            "The offline product lane now connects case anchor, reasoning move, "
            "model relationship, practice rep, page clickthroughs, graph "
            "neighborhoods, source custody, missingness, and a blank human review "
            "packet without collapsing into runtime, Decision Work, Observatory, "
            "Product Delta, or proof language."
        ),
        "strongest_unresolved_risk": (
            "The pilot is reviewable but not validated: without completed human "
            "review and broader real-case model/relation product pages, expansion "
            "could overfit the three cases or make graph/source artifacts look more "
            "authoritative than the evidence supports."
        ),
        "validation_checklist": [
            "python3 -m py_compile engine/system_b/mental_model_teacher_product_surface_package_gate.py tests/test_mental_model_teacher_product_surface_package_gate.py",
            "PYTHONPATH=. pytest -q tests/test_mental_model_teacher_product_surface_package_gate.py",
            "PYTHONPATH=. pytest -q tests/test_mental_model_teacher*.py",
            "PYTHONPATH=. python3 -m engine.system_b.mental_model_teacher_product_surface_package_gate",
            "jq empty over package manifest and package review JSON",
            "Product Delta boundary lint over package doc, manifest, and review JSON",
            "Markdown local-link check over touched Markdown files",
            "trailing whitespace scan over touched files",
            "privacy/content marker scan over touched package files",
            "git diff --check",
            "git status --short -- SKILL.md scripts/skill scripts/archive_run.py",
            "git diff --cached --name-only empty after commit",
        ],
        "explicit_non_claims": [
            "not_product_proof",
            "not_human_validation",
            "not_answer_correctness",
            "not_advice_correctness",
            "not_runtime_integration",
            "not_action_authorization",
            "not_full_corpus_build",
            "not_customer_ready",
            "not_graph_edge_proof",
            "not_embedding_similarity_validation",
            "not_decision_work",
            "not_observatory",
            "not_product_delta",
            "not_lolla_skill_runtime",
        ],
        "non_claims": {
            "product_proof": False,
            "human_validated": False,
            "answer_correctness": False,
            "advice_correctness": False,
            "runtime_integration_authorized": False,
            "graph_edges_are_proof": False,
            "embedding_similarity_is_validated_relation_semantics": False,
            "agent_or_automatic_action_authorized": False,
            "full_corpus_build": False,
            "customer_ready": False,
        },
        "model_calls": 0,
        "provider_or_model_calls": 0,
        "archive_mutated": False,
        "runtime_invoked": False,
        "skill_invoked": False,
        "stop_before": [
            "full corpus build",
            "runtime integration",
            "provider or model calls",
            "product readiness claim",
            "human validation claim",
            "answer or advice correctness claim",
            "automatic action authorization",
        ],
    }


def _review_json(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": PACKAGE_REVIEW_SCHEMA_VERSION,
        "status": manifest["package_status"],
        "product_lane": manifest["product_lane"],
        "decision_gate": manifest["decision_gate"],
        "recommended_next_action": manifest["recommended_next_action"],
        "package_manifest": manifest["package_manifest"],
        "package_gate_doc": manifest["package_gate_doc"],
        "current_state": manifest["current_state"],
        "strongest_useful_signal": manifest["strongest_useful_signal"],
        "strongest_unresolved_risk": manifest["strongest_unresolved_risk"],
        "non_claims": manifest["non_claims"],
        "human_review": {
            "form_exists": True,
            "completed": False,
            "human_validated": False,
            "prefilled_positive": False,
        },
        "optional_later": {
            "pr_p12_full_corpus_graph_plan": "deferred_until_human_review_gate_changes",
            "pr_p13_full_corpus_library_pilot": "deferred_until_package_gate_allows_expansion",
        },
        "stop_before": manifest["stop_before"],
    }


def _roadmap_slices() -> list[dict[str, Any]]:
    return [
        _slice("PR-P1", 252, "Product Surface PRD And Reference Audit", "published"),
        _slice("PR-P2", 253, "Current Substrate Inventory And Exposure Contract", "published"),
        _slice("PR-P3", 254, "User-Facing Model And Relation Contracts", "published"),
        _slice("PR-P4", 255, "Pilot Model And Relation Page Data Builder", "published"),
        _slice("PR-P5", 256, "Static Model And Relation Page Renderer", "published"),
        _slice("PR-P6", 257, "Teacher Lesson Product Renderer", "published"),
        _slice("PR-P7", 258, "Lesson Neighborhood Graph Data Builder", "published"),
        _slice("PR-P8", 259, "Static Visual Graph Prototype", "published"),
        _slice("PR-P9", 260, "Three-Case Teacher Product Pilot Deferred Packet", "published"),
        _slice("PR-P9-support", 261, "Three-Case Teacher Source Package Import", "published"),
        _slice("PR-P9-retry", 262, "Three-Case Teacher Product Pilot", "published"),
        _slice("PR-P10", 263, "UX Review Packet And Human Review Form", "published"),
        _slice("PR-P11", None, "Product Surface Package Gate", "this_pr"),
    ]


def _slice(slice_id: str, pr_number: int | None, title: str, status: str) -> dict[str, Any]:
    return {
        "slice_id": slice_id,
        "github_pr": pr_number,
        "title": title,
        "status": status,
    }


def _included_files() -> dict[str, list[str]]:
    return {
        "planning_and_inventory_docs": [
            "docs/product/README.md",
            "docs/product/mental-model-teacher-product-surface-and-visual-library-prd-v0.md",
            "docs/product/mental-model-teacher-current-substrate-inventory-v0.md",
            "docs/product/mental-model-teacher-product-surface-reference-patterns-v0.md",
            "docs/product/mental-model-teacher-substrate-exposure-contract-v0.md",
            "docs/product/mental-model-teacher-substrate-exposure-contract-v0.json",
        ],
        "contract_and_builder_docs": [
            "docs/product/mental-model-teacher-product-contracts-v0.md",
            "docs/product/mental-model-teacher-product-contract-examples-v0.json",
            "docs/product/mental-model-teacher-pilot-page-data-builder-v0.md",
            "docs/product/mental-model-teacher-static-page-renderer-v0.md",
            "docs/product/mental-model-teacher-lesson-product-renderer-v0.md",
            "docs/product/mental-model-teacher-lesson-graph-data-builder-v0.md",
            "docs/product/mental-model-teacher-static-visual-graph-prototype-v0.md",
        ],
        "pilot_model_relation_render": [
            "docs/product/mental-model-teacher-pilot-render-v0/index.md",
            "docs/product/mental-model-teacher-pilot-render-v0/manifest.json",
            "docs/product/mental-model-teacher-pilot-render-v0/models/base-rates.md",
            "docs/product/mental-model-teacher-pilot-render-v0/models/scientific-method-evidence-testing.md",
            "docs/product/mental-model-teacher-pilot-render-v0/models/system-2.md",
            "docs/product/mental-model-teacher-pilot-render-v0/relations/base-rates__ally__scientific-method-evidence-testing.md",
            "docs/product/mental-model-teacher-pilot-render-v0/relations/base-rates__ally__system-2.md",
        ],
        "fixture_lesson_graph_and_visual_prototype": [
            "docs/product/mental-model-teacher-lesson-render-v0/index.md",
            "docs/product/mental-model-teacher-lesson-render-v0/lessons/contract-fixture-base-rates-system-2.md",
            "docs/product/mental-model-teacher-lesson-render-v0/manifest.json",
            "docs/product/mental-model-teacher-lesson-graph-v0/contract-fixture-base-rates-system-2.graph.json",
            "docs/product/mental-model-teacher-lesson-graph-v0/manifest.json",
            "docs/product/mental-model-teacher-visual-graph-prototype-v0/index.html",
            "docs/product/mental-model-teacher-visual-graph-prototype-v0/manifest.json",
        ],
        "three_case_teacher_product_pilot": [
            "docs/product/mental-model-teacher-three-case-product-pilot-v0.md",
            "docs/product/mental-model-teacher-three-case-source-package-v0.md",
            "docs/product/mental-model-teacher-three-case-product-pilot-retry-v0.md",
            "docs/product/mental-model-teacher-three-case-product-pilot-v0/index.md",
            "docs/product/mental-model-teacher-three-case-product-pilot-v0/manifest.json",
            *[
                f"docs/product/mental-model-teacher-three-case-product-pilot-v0/lessons/{case_id}.md"
                for case_id in CASE_IDS
            ],
            *[
                f"docs/product/mental-model-teacher-three-case-product-pilot-v0/objects/{case_id}.lesson.json"
                for case_id in CASE_IDS
            ],
            *[
                f"docs/product/mental-model-teacher-three-case-product-pilot-v0/graphs/{case_id}.graph.json"
                for case_id in CASE_IDS
            ],
        ],
        "teacher_source_required_artifacts": _teacher_source_required_files(),
        "ux_review_packet": [
            "docs/product/mental-model-teacher-ux-review-packet-v0.md",
            "docs/product/mental-model-teacher-ux-review-packet-v0/index.md",
            "docs/product/mental-model-teacher-ux-review-packet-v0/human-review-form.md",
            "docs/product/mental-model-teacher-ux-review-packet-v0/human-review-form.json",
            "docs/product/mental-model-teacher-ux-review-packet-v0/manifest.json",
        ],
        "engine_modules": [
            "engine/system_b/mental_model_teacher_substrate_inventory.py",
            "engine/system_b/mental_model_teacher_product_contracts.py",
            "engine/system_b/mental_model_teacher_pilot_page_builder.py",
            "engine/system_b/mental_model_teacher_static_renderer.py",
            "engine/system_b/mental_model_teacher_lesson_renderer.py",
            "engine/system_b/mental_model_teacher_lesson_graph_builder.py",
            "engine/system_b/mental_model_teacher_three_case_product_pilot.py",
            "engine/system_b/mental_model_teacher_ux_review_packet.py",
            "engine/system_b/mental_model_teacher_product_surface_package_gate.py",
        ],
        "tests": [
            "tests/test_mental_model_teacher_product_surface_visual_library_prd.py",
            "tests/test_mental_model_teacher_substrate_exposure_contract.py",
            "tests/test_mental_model_teacher_product_contracts.py",
            "tests/test_mental_model_teacher_pilot_page_builder.py",
            "tests/test_mental_model_teacher_static_renderer.py",
            "tests/test_mental_model_teacher_lesson_renderer.py",
            "tests/test_mental_model_teacher_lesson_graph_builder.py",
            "tests/test_mental_model_teacher_static_visual_graph_prototype.py",
            "tests/test_mental_model_teacher_three_case_product_pilot.py",
            "tests/test_mental_model_teacher_three_case_source_package.py",
            "tests/test_mental_model_teacher_three_case_product_pilot_retry.py",
            "tests/test_mental_model_teacher_ux_review_packet.py",
            "tests/test_mental_model_teacher_product_surface_package_gate.py",
        ],
        "review_artifacts": [
            "reviews/codex-assisted/mental-model-teacher-product-surface-and-visual-library-prd-v0/review.json",
            "reviews/codex-assisted/mental-model-teacher-substrate-exposure-contract-v0/review.json",
            "reviews/codex-assisted/mental-model-teacher-product-contracts-v0/review.json",
            "reviews/codex-assisted/mental-model-teacher-pilot-page-data-builder-v0/review.json",
            "reviews/codex-assisted/mental-model-teacher-static-page-renderer-v0/review.json",
            "reviews/codex-assisted/mental-model-teacher-lesson-product-renderer-v0/review.json",
            "reviews/codex-assisted/mental-model-teacher-lesson-graph-data-builder-v0/review.json",
            "reviews/codex-assisted/mental-model-teacher-static-visual-graph-prototype-v0/review.json",
            "reviews/codex-assisted/mental-model-teacher-three-case-product-pilot-v0/review.json",
            "reviews/codex-assisted/mental-model-teacher-three-case-source-package-v0/review.json",
            "reviews/codex-assisted/mental-model-teacher-three-case-product-pilot-retry-v0/review.json",
            "reviews/codex-assisted/mental-model-teacher-ux-review-packet-v0/review.json",
            "reviews/codex-assisted/mental-model-teacher-product-surface-package-gate-v0/review.json",
        ],
    }


def _teacher_source_package() -> dict[str, Any]:
    return {
        "root": "reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2",
        "case_count": len(CASE_IDS),
        "case_ids": list(CASE_IDS),
        "required_artifacts_listed_in_manifest": True,
        "top_level_human_review_artifacts_imported": False,
        "decision_work_artifacts_used_as_teacher_source": False,
    }


def _teacher_source_required_files() -> list[str]:
    files: list[str] = []
    for case_id in CASE_IDS:
        root = f"reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2/{case_id}"
        files.extend(
            [
                f"{root}/case_review.json",
                f"{root}/mental_model_teacher_card.md",
                f"{root}/mental_model_teacher.md",
                f"{root}/mental_model_teacher_lesson.json",
                f"{root}/mental_model_teacher_okf_manifest.json",
                f"{root}/{RELATION_SOURCE_FILES[case_id]}",
            ]
        )
    return files


def _safe_ref(path: Path) -> str:
    try:
        return _repo_rel(path)
    except MentalModelTeacherProductSurfacePackageGateError:
        return path.name


def _repo_rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise MentalModelTeacherProductSurfacePackageGateError(
            "path must stay inside the repository"
        ) from exc


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise MentalModelTeacherProductSurfacePackageGateError(
            "JSON root must be an object"
        )
    return payload


def _write(path: Path, text: str) -> None:
    _assert_no_local_paths(text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _assert_no_local_paths(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _finish(lines: list[str]) -> str:
    return "\n".join(str(line).rstrip() for line in lines).rstrip() + "\n"


def _md_link(label: str, repo_relative_path: str, from_path: Path) -> str:
    return f"[{label}]({_relative_link(from_path, repo_relative_path)})"


def _relative_link(from_path: Path, repo_relative_path: str) -> str:
    try:
        from_path.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        return repo_relative_path
    return os.path.relpath(REPO_ROOT / repo_relative_path, from_path.parent)


def _bool_text(value: Any) -> str:
    return "true" if value is True else "false"


def _assert_no_local_paths(payload: Any) -> None:
    rendered = json.dumps(payload, sort_keys=True) if not isinstance(payload, str) else payload
    markers = (
        "/" + "Users/",
        "Desktop/" + "Apps",
        "\\" + "Users\\",
    )
    if any(marker in rendered for marker in markers):
        raise MentalModelTeacherProductSurfacePackageGateError(
            "package gate contains a local path marker"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the Mental Model Teacher product surface package gate.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--package-doc-path", type=Path, default=PACKAGE_DOC_PATH)
    parser.add_argument("--package-manifest-path", type=Path, default=PACKAGE_MANIFEST_PATH)
    parser.add_argument("--package-review-path", type=Path, default=PACKAGE_REVIEW_PATH)
    args = parser.parse_args(argv)

    manifest = build_product_surface_package_gate(
        root=args.root,
        package_doc_path=args.package_doc_path,
        package_manifest_path=args.package_manifest_path,
        package_review_path=args.package_review_path,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
