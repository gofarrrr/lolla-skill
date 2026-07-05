import json
import re
from pathlib import Path
from typing import Any

from engine.system_b.mental_model_teacher_product_surface_package_gate import (
    PACKAGE_MANIFEST_SCHEMA_VERSION,
    PACKAGE_REVIEW_SCHEMA_VERSION,
    build_product_surface_package_gate,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DOC = (
    REPO_ROOT / "docs/product/mental-model-teacher-product-surface-package-gate-v0.md"
)
PACKAGE_MANIFEST = (
    REPO_ROOT / "docs/product/mental-model-teacher-product-surface-package-manifest-v0.json"
)
PACKAGE_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-product-surface-package-gate-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"

CASE_IDS = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
}
FORBIDDEN_PREFIXES = (
    "scripts/skill/",
    "plans/",
    "reviews/synthetic/",
    "docs/lolla-",
    "docs/semantica-",
    "docs/thoughtbox-",
    "archive/",
    "archives/",
    "runs/",
)
FORBIDDEN_EXACT = {"SKILL.md", "scripts/archive_run.py"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest_files(manifest: dict[str, Any]) -> list[str]:
    files: list[str] = []
    for group in manifest["included_files"].values():
        files.extend(group)
    return files


def test_builder_writes_package_gate_to_temp_paths(tmp_path: Path) -> None:
    manifest_path = tmp_path / "package-manifest.json"
    doc_path = tmp_path / "package-gate.md"
    review_path = tmp_path / "review.json"

    manifest = build_product_surface_package_gate(
        REPO_ROOT,
        package_doc_path=doc_path,
        package_manifest_path=manifest_path,
        package_review_path=review_path,
    )

    assert manifest["schema_version"] == PACKAGE_MANIFEST_SCHEMA_VERSION
    assert manifest["package_status"] == "product_surface_pilot_packaged_for_human_review"
    assert manifest["decision_gate"] == "needs_human_review_before_expansion"
    assert manifest["recommended_next_action"] == (
        "collect_human_review_before_expansion_or_revision"
    )
    assert manifest["current_state"]["three_case_teacher_cases"] == 3
    assert manifest["current_state"]["human_review_completed"] is False
    assert manifest["non_claims"]["product_proof"] is False
    assert manifest["non_claims"]["runtime_integration_authorized"] is False
    assert manifest_path.exists()
    assert doc_path.exists()
    assert review_path.exists()


def test_checked_in_manifest_schema_gate_and_current_state() -> None:
    manifest = _load_json(PACKAGE_MANIFEST)
    state = manifest["current_state"]

    assert manifest["schema_version"] == PACKAGE_MANIFEST_SCHEMA_VERSION
    assert manifest["package_status"] == "product_surface_pilot_packaged_for_human_review"
    assert manifest["product_lane"] == (
        "Mental Model Teacher Product Surface And Visual Library"
    )
    assert manifest["decision_gate"] == "needs_human_review_before_expansion"
    assert manifest["roadmap_scope"] == (
        "PR-P1 through PR-P10 packaged; PR-P11 selects the next gate"
    )
    assert state["pilot_model_pages"] == 3
    assert state["pilot_relation_pages"] == 2
    assert state["fixture_lesson_pages"] == 1
    assert state["fixture_graphs"] == 1
    assert state["static_graph_prototype"] is True
    assert state["static_graph_renderer"] == "dependency_free_svg"
    assert state["static_graph_external_network_required"] is False
    assert state["three_case_teacher_cases"] == 3
    assert state["three_case_lesson_pages"] == 3
    assert state["three_case_graphs"] == 3
    assert state["three_case_high_risk_cases"] == ["ceo-remove-founding-cofounder"]
    assert state["ux_review_case_count"] == 3
    assert state["human_review_form_blank"] is True
    assert state["human_review_completed"] is False
    assert state["human_validated"] is False
    assert state["product_proof"] is False
    assert state["runtime_integration_authorized"] is False
    assert state["provider_or_model_calls"] == 0
    assert state["model_calls"] == 0
    assert state["archive_mutated"] is False
    assert state["full_corpus_graph_built"] is False
    assert state["runtime_wiring_added"] is False


def test_manifest_includes_required_package_files_and_all_exist() -> None:
    manifest = _load_json(PACKAGE_MANIFEST)
    files = set(_manifest_files(manifest))

    required = {
        "docs/product/mental-model-teacher-product-surface-and-visual-library-prd-v0.md",
        "docs/product/mental-model-teacher-substrate-exposure-contract-v0.md",
        "docs/product/mental-model-teacher-product-contracts-v0.md",
        "docs/product/mental-model-teacher-pilot-render-v0/models/base-rates.md",
        "docs/product/mental-model-teacher-pilot-render-v0/relations/base-rates__ally__system-2.md",
        "docs/product/mental-model-teacher-lesson-render-v0/lessons/contract-fixture-base-rates-system-2.md",
        "docs/product/mental-model-teacher-visual-graph-prototype-v0/index.html",
        "docs/product/mental-model-teacher-three-case-product-pilot-v0/lessons/launch-public-enterprise-beta.md",
        "docs/product/mental-model-teacher-three-case-product-pilot-v0/graphs/ceo-remove-founding-cofounder.graph.json",
        "docs/product/mental-model-teacher-ux-review-packet-v0/human-review-form.json",
        "engine/system_b/mental_model_teacher_product_surface_package_gate.py",
        "tests/test_mental_model_teacher_product_surface_package_gate.py",
        "reviews/codex-assisted/mental-model-teacher-product-surface-package-gate-v0/review.json",
        "docs/product/mental-model-teacher-product-surface-package-gate-v0.md",
        "docs/product/mental-model-teacher-product-surface-package-manifest-v0.json",
    }

    assert required <= files
    for ref in sorted(files):
        assert (REPO_ROOT / ref).exists(), ref


def test_manifest_excludes_unrelated_and_runtime_paths() -> None:
    manifest = _load_json(PACKAGE_MANIFEST)
    files = _manifest_files(manifest)

    assert "SKILL.md" in manifest["excluded_paths"]
    assert "scripts/skill/*" in manifest["excluded_paths"]
    assert "scripts/archive_run.py" in manifest["excluded_paths"]
    assert "plans/*" in manifest["excluded_paths"]
    assert "reviews/synthetic/*" in manifest["excluded_paths"]
    assert "data/embeddings.db raw embedding index" in manifest["excluded_paths"]
    for ref in files:
        assert ref not in FORBIDDEN_EXACT
        assert not any(ref.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)
        assert "scripts/archive_run.py" not in ref
        assert "data/embeddings.db" not in ref


def test_roadmap_slices_cover_pr_p1_through_pr_p11_without_expansion() -> None:
    manifest = _load_json(PACKAGE_MANIFEST)
    slices = {item["slice_id"]: item for item in manifest["roadmap_slices"]}

    for slice_id in [f"PR-P{index}" for index in range(1, 12)]:
        assert slice_id in slices
    assert slices["PR-P1"]["github_pr"] == 252
    assert slices["PR-P10"]["github_pr"] == 263
    assert slices["PR-P11"]["github_pr"] is None
    assert slices["PR-P11"]["status"] == "this_pr"
    assert slices["PR-P9-support"]["github_pr"] == 261
    assert slices["PR-P9-retry"]["github_pr"] == 262
    assert manifest["stop_before"] == [
        "full corpus build",
        "runtime integration",
        "provider or model calls",
        "product readiness claim",
        "human validation claim",
        "answer or advice correctness claim",
        "automatic action authorization",
    ]


def test_teacher_source_package_and_human_gate_stay_conservative() -> None:
    manifest = _load_json(PACKAGE_MANIFEST)
    source = manifest["teacher_source_package"]
    source_files = manifest["included_files"]["teacher_source_required_artifacts"]

    assert source["root"] == (
        "reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2"
    )
    assert source["case_count"] == 3
    assert set(source["case_ids"]) == CASE_IDS
    assert source["required_artifacts_listed_in_manifest"] is True
    assert source["top_level_human_review_artifacts_imported"] is False
    assert source["decision_work_artifacts_used_as_teacher_source"] is False
    assert len(source_files) == 18
    for case_id in CASE_IDS:
        joined = "\n".join(source_files)
        assert f"{case_id}/mental_model_teacher_card.md" in joined
        assert f"{case_id}/mental_model_teacher_lesson.json" in joined

    assert manifest["current_state"]["human_review_completed"] is False
    assert manifest["decision_gate"] == "needs_human_review_before_expansion"
    assert manifest["recommended_next_action"] == (
        "collect_human_review_before_expansion_or_revision"
    )


def test_package_doc_and_review_record_signal_risk_and_non_claims() -> None:
    manifest = _load_json(PACKAGE_MANIFEST)
    review = _load_json(PACKAGE_REVIEW)
    doc = PACKAGE_DOC.read_text(encoding="utf-8")
    normalized_doc = " ".join(doc.split())

    assert review["schema_version"] == PACKAGE_REVIEW_SCHEMA_VERSION
    assert review["status"] == manifest["package_status"]
    assert review["decision_gate"] == "needs_human_review_before_expansion"
    assert review["human_review"]["form_exists"] is True
    assert review["human_review"]["completed"] is False
    assert review["human_review"]["human_validated"] is False
    assert review["human_review"]["prefilled_positive"] is False
    assert review["optional_later"]["pr_p12_full_corpus_graph_plan"] == (
        "deferred_until_human_review_gate_changes"
    )
    assert review["optional_later"]["pr_p13_full_corpus_library_pilot"] == (
        "deferred_until_package_gate_allows_expansion"
    )

    assert "## Strongest Useful Signal" in doc
    assert "## Strongest Unresolved Risk" in doc
    assert "## Validation Checklist" in doc
    assert "## Boundary And Non-Claims" in doc
    assert "needs_human_review_before_expansion" in doc
    assert "PR-P12 and PR-P13 should remain deferred" in doc
    assert "not_product_proof" in doc
    assert "not_human_validation" in doc
    assert "not_answer_correctness" in doc
    assert "not_advice_correctness" in doc
    assert "not_runtime_integration" in doc
    assert "not_action_authorization" in doc
    assert "case anchor, reasoning move, model relationship" in normalized_doc
    assert "without completed human review" in normalized_doc


def test_non_claims_and_boundary_flags_are_false() -> None:
    manifest = _load_json(PACKAGE_MANIFEST)
    review = _load_json(PACKAGE_REVIEW)

    for payload in [manifest, review]:
        non_claims = payload["non_claims"]
        assert non_claims["product_proof"] is False
        assert non_claims["human_validated"] is False
        assert non_claims["answer_correctness"] is False
        assert non_claims["advice_correctness"] is False
        assert non_claims["runtime_integration_authorized"] is False
        assert non_claims["graph_edges_are_proof"] is False
        assert non_claims["embedding_similarity_is_validated_relation_semantics"] is False
        assert non_claims["agent_or_automatic_action_authorized"] is False
    assert manifest["model_calls"] == 0
    assert manifest["provider_or_model_calls"] == 0
    assert manifest["archive_mutated"] is False
    assert manifest["runtime_invoked"] is False
    assert manifest["skill_invoked"] is False


def test_package_markdown_links_and_manifest_json_paths_resolve() -> None:
    missing = []
    for path in [PACKAGE_DOC, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    manifest = _load_json(PACKAGE_MANIFEST)
    for ref in _manifest_files(manifest):
        if not (REPO_ROOT / ref).exists():
            missing.append(ref)

    assert "mental-model-teacher-product-surface-package-gate-v0.md" in (
        README.read_text(encoding="utf-8")
    )
    assert "mental-model-teacher-product-surface-package-manifest-v0.json" in (
        README.read_text(encoding="utf-8")
    )
    assert missing == []


def test_product_delta_boundary_lint_accepts_package_gate_artifacts() -> None:
    report = lint_product_delta_paths([PACKAGE_DOC, PACKAGE_MANIFEST, PACKAGE_REVIEW])

    assert report["summary"]["blocking_error_count"] == 0
    assert report["summary"]["warning_count"] == 0
    assert report["summary"]["info_count"] == 0


def test_package_artifacts_have_no_local_paths_or_positive_claim_markers() -> None:
    rendered = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [PACKAGE_DOC, PACKAGE_MANIFEST, PACKAGE_REVIEW]
    )

    assert "/" + "Users/" not in rendered
    assert "Desktop/" + "Apps" not in rendered
    assert "product_proof\": true" not in rendered
    assert "human_validated\": true" not in rendered
    assert "human_review_completed\": true" not in rendered
    assert "runtime_integration_authorized\": true" not in rendered
    assert "answer_correctness\": true" not in rendered
    assert "advice_correctness\": true" not in rendered
    assert "Product proof: `true`" not in rendered
    assert "Runtime integration authorized: `true`" not in rendered
    assert "\"embedding_similarity\":" not in rendered
    assert "\"affinity\"" not in rendered
    assert "\"rank\"" not in rendered
    assert "\"score\"" not in rendered
