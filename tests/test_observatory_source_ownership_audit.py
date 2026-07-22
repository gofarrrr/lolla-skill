import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-source-ownership-audit-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-source-ownership-audit-v0/review.json"
)
SERVE_RESULT = REPO_ROOT / "observatory/serve_result.py"
LIVE_FLOW = REPO_ROOT / "docs/how-it-works/live-flow.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_source_ownership_doc_exists_and_is_indexed() -> None:
    assert DOC.exists()
    assert REVIEW.exists()

    readme = _read(README)
    assert "Observatory Source Ownership Audit" in readme
    assert "observatory-source-ownership-audit-v0.md" in readme


def test_source_ownership_doc_declares_hybrid_owner_decision() -> None:
    text = " ".join(_read(DOC).split())

    for phrase in [
        "Observatory is one portable skill-presentation product shell",
        "the Python server in this repo owns the active product direction",
        "not an external source dependency",
        "The source owner and current product direction are both repository-local",
        "The next PR should not be another UI patch and should not be a Svelte revival.",
        "proceed_to_observatory_portable_server_view_model_contracts",
    ]:
        assert phrase in text


def test_source_ownership_doc_records_local_repo_evidence() -> None:
    text = _read(DOC)

    for phrase in [
        "`observatory/serve_result.py`",
        "`observatory/render_schema.json`",
        "`observatory/build/index.html`",
        "`observatory/build/assets/*.js`",
        "`observatory/build/assets/*.css`",
        "no root `package.json`",
        "no `observatory/package.json`",
        "no `observatory/svelte-app/`",
        "no local `vite.config.*`",
        "no local `svelte.config.*`",
        "no local `tsconfig.json` for an Observatory app",
    ]:
        assert phrase in text


def test_current_repo_shape_matches_local_evidence() -> None:
    assert SERVE_RESULT.is_file()
    assert (REPO_ROOT / "observatory/render_schema.json").is_file()
    assert (REPO_ROOT / "observatory/build/index.html").is_file()

    source_markers = [
        REPO_ROOT / "package.json",
        REPO_ROOT / "observatory/package.json",
        REPO_ROOT / "observatory/svelte-app/package.json",
        REPO_ROOT / "vite.config.js",
        REPO_ROOT / "vite.config.ts",
        REPO_ROOT / "svelte.config.js",
        REPO_ROOT / "svelte.config.ts",
        REPO_ROOT / "tsconfig.json",
        REPO_ROOT / "observatory/vite.config.js",
        REPO_ROOT / "observatory/vite.config.ts",
        REPO_ROOT / "observatory/svelte.config.js",
        REPO_ROOT / "observatory/svelte.config.ts",
        REPO_ROOT / "observatory/tsconfig.json",
    ]
    assert all(not marker.exists() for marker in source_markers)


def test_server_source_and_docs_name_repository_local_portable_doctrine() -> None:
    serve_result = " ".join(_read(SERVE_RESULT).split())
    live_flow = " ".join(_read(LIVE_FLOW).split())

    for phrase in [
        "former source workspace is retired",
        "not a dependency or editing path",
        "repository-local source",
        "observatory/build/",
        "stay portable",
    ]:
        assert phrase in serve_result

    for phrase in [
        "scripts/skill/launch_observatory.py",
        "observatory/serve_result.py",
        "server-rendered HTML and works whether or not `observatory/build/`",
        "without a Node toolchain",
    ]:
        assert phrase in live_flow


def test_server_routes_show_portable_runtime_owns_new_product_surfaces() -> None:
    serve_result = _read(SERVE_RESULT)

    for phrase in [
        '("/workspace#learn", "Learn")',
        "/api/cases",
        'parts[4] == "teacher-learning"',
        'parts[4] == "decision-work"',
        'parts[5] == "prepare"',
        'path == "/teacher-learning"',
        "_redirect_response",
        'path.startswith("/api/model/")',
        'path == "/api/families"',
        "_inject_telemetry_fab",
        "data-lolla-prepare-process-brief",
    ]:
        assert phrase in serve_result


def test_source_ownership_doc_records_retired_source_and_local_rebuild_boundary() -> None:
    text = " ".join(_read(DOC).split())

    for phrase in [
        "Any former sibling frontend source is outside the current project boundary.",
        "neither an installation prerequisite nor a future editing location",
        "repository-local source",
        "reproducible artifact hashes",
        "There is no supported external rebuild path.",
        "do not direct a maintainer to another repository",
    ]:
        assert phrase in text


def test_source_ownership_doc_defines_port_readiness_and_sequence() -> None:
    text = _read(DOC)

    for phrase in [
        "product view model contracts",
        "one fixture or checked safe run payload",
        "server-rendered shell",
        "stable portable server adapters",
        "smoke tests against `observatory/serve_result.py`",
        "fallback policy",
        "Server-Rendered Global Workspace",
        "Legacy Root Bundle Bypass Or Retirement Plan",
        "Optional Repository-Local Bundle Source Decision",
    ]:
        assert phrase in text

    planned = re.findall(r"^### PR-SO\d+", text, flags=re.MULTILINE)
    assert planned == [
        "### PR-SO1",
        "### PR-SO2",
        "### PR-SO3",
        "### PR-SO4",
        "### PR-SO5",
        "### PR-SO6",
    ]


def test_review_json_records_decision_gate_evidence_and_non_claims() -> None:
    data = json.loads(_read(REVIEW))

    assert data["schema"] == "lolla.observatory_source_ownership_audit_review.v0"
    assert data["artifact"] == "docs/product/observatory-source-ownership-audit-v0.md"
    assert (
        data["decision_gate"]
        == "proceed_to_observatory_portable_server_view_model_contracts"
    )

    decision = data["source_ownership_decision"]
    assert decision["one_product_shell"] == "Observatory"
    assert decision["portable_runtime_owner"] == "observatory/serve_result.py"
    assert decision["active_product_surface_owner"] == "observatory/serve_result.py"
    assert (
        decision["current_rendering_direction"]
        == "portable_python_server_rendered_html"
    )
    assert decision["legacy_spa_source"] == "not_present_in_active_repository"
    assert decision["legacy_spa_is_future_product_owner_by_default"] is False
    assert decision["external_frontend_dependency"] is False
    assert decision["compiled_bundle_role"] == "distribution_artifact"
    assert decision["svelte_revival_authorized_now"] is False
    assert decision["global_shell_port_authorized_now"] is False
    assert decision["compiled_bundle_manual_editing_allowed"] is False

    local = data["local_repo_evidence"]
    assert local["serve_result_present"] is True
    assert local["compiled_bundle_present"] is True
    assert local["local_package_json_present"] is False
    assert local["local_observatory_svelte_app_present"] is False
    assert local["server_header_names_external_source"] is False
    assert local["server_header_declares_repository_local_authority"] is True

    retired = data["retired_source_boundary"]
    assert retired["active_dependency"] is False
    assert retired["editing_path"] is False
    assert retired["installation_requirement"] is False
    assert retired["repository_local_replacement_required"] is True

    bundle = data["bundle_provenance"]
    assert bundle["checked_in_distribution_artifact"] is True
    assert bundle["repository_local_authoring_source_present"] is False
    assert bundle["manual_editing_allowed"] is False
    assert bundle["replacement_requires_repository_local_source"] is True
    assert bundle["reproducible_build_contract_required"] is True

    requirements = data["portable_server_direction_requirements"]
    assert requirements["product_view_model_contracts"] is True
    assert requirements["portable_server_adapters"] is True
    assert requirements["serve_result_smoke_tests"] is True
    assert requirements["fallback_policy_when_bundle_absent"] is True

    boundary = data["boundary"]
    assert boundary["runs_lolla"] is False
    assert boundary["invokes_lolla_skill"] is False
    assert boundary["provider_or_model_calls"] is False
    assert boundary["runtime_behavior_changed"] is False
    assert boundary["compiled_js_or_css_edited"] is False
    assert boundary["other_repository_required"] is False
    assert boundary["bundle_copied"] is False
    assert boundary["svelte_revival_authorized"] is False

    non_claims = data["non_claims"]
    assert non_claims["product_proof"] is False
    assert non_claims["human_validated"] is False
    assert non_claims["answer_correctness"] is False
    assert non_claims["advice_correctness"] is False
    assert non_claims["action_authorized"] is False
    assert non_claims["graph_edges_are_proof"] is False


def test_markdown_links_resolve_for_source_ownership_doc() -> None:
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", _read(DOC))
    for link in links:
        if "://" in link or link.startswith("#"):
            continue
        assert (DOC.parent / link).exists(), link


def test_source_ownership_artifacts_have_no_absolute_paths_or_authority_claims() -> None:
    text = _read(DOC) + _read(REVIEW)

    for forbidden in [
        "/" + "Users/",
        "Desktop/" + "Apps",
        "product_proof\": true",
        "human_validated\": true",
        "answer_correctness\": true",
        "advice_correctness\": true",
        "action_authorized\": true",
        "runtime_behavior_changed\": true",
        "compiled_js_or_css_edited\": true",
        "external_repo_modified\": true",
        "bundle_copied\": true",
        "svelte_revival_authorized\": true",
    ]:
        assert forbidden not in text
