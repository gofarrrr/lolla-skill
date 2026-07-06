import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/mental-model-teacher-observatory-native-learn-tab-v0.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-observatory-native-learn-tab-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"


def _install_launch_case() -> None:
    serve_result._RESULT = {"usage_summary": {"run_id": "20260627T104146Z_7bfe79"}}
    serve_result._RESULT_PATH = None
    serve_result._CASE_ID = "lolla-audit"
    serve_result._CASE_NAME = "Lolla Audit"


def test_native_learn_page_borrows_observatory_visual_system() -> None:
    _install_launch_case()

    html = serve_result._render_workspace_html("lolla-audit")

    assert "--bg: #060761" in html
    assert "--teal: #41FFA7" in html
    assert "JetBrains Mono" in html
    assert 'class="workspace-page"' in html
    assert 'class="status-bar workspace-statusbar"' in html
    assert 'class="workspace-layout"' in html
    assert 'class="workspace-sidebar"' in html
    assert 'class="teacher-shell"' not in html
    assert 'class="teacher-sidebar"' not in html
    assert 'class="tab-btn tab-btn--active"' not in html
    assert ">Outcome</a>" in html
    status_bar = html.split('data-observatory-status-bar>', 1)[1].split("</nav>", 1)[0]
    assert "Advanced Audit" not in status_bar


def test_workspace_learn_links_models_to_product_pages_without_drawers() -> None:
    _install_launch_case()

    html = serve_result._render_workspace_html("lolla-audit")
    detail = serve_result._render_workspace_model_detail_html(
        "authority-bias",
        "lolla-audit",
    )

    assert 'href="/models/authority-bias?case_id=lolla-audit"' in html
    assert 'id="model-authority-bias"' in html
    assert "Model index" in html
    assert "Use when" in html
    assert "When it misleads" in html
    assert "What This Model Helps You See" in detail
    assert "Helps notice" in detail
    assert "Avoid when" in detail
    assert "Failure modes" in detail
    assert "Source, status, and boundaries" in detail
    assert "data/model_sources/Authority_Bias_rag.md" in detail
    assert "teacher-detail" not in html
    assert "drawer-panel" not in html
    assert html.index("Test The Authority, Not The Aura") < html.index("<h2>Models</h2>")
    assert 'id="model-test-the-authority-not-the-aura"' not in html


def test_workspace_learn_links_relations_after_plain_story() -> None:
    _install_launch_case()

    html = serve_result._render_workspace_html("lolla-audit")
    detail = serve_result._render_workspace_relation_detail_html(
        "authority-bias__first-principles-thinking__antagonist",
        "lolla-audit",
    )

    relation_anchor = (
        "relation-authority-bias__first-principles-thinking__antagonist"
    )
    assert (
        f'href="/relations/{relation_anchor.removeprefix("relation-")}?case_id=lolla-audit"'
        in html
    )
    assert f'id="{relation_anchor}"' in html
    assert "Relation story" in html
    assert "Why it matters" in html
    assert "Misread risk" in html
    assert "Practice prompt:" in html
    assert "Plain Language Story" in detail
    assert "Why It Matters" in detail
    assert "Misread Risk" in detail
    assert "confidence is not certification" in detail
    assert detail.index("First principles thinking strips away inherited doctrine") < (
        detail.index("confidence: medium")
    )


def test_native_learn_page_keeps_telemetry_and_receipts_secondary() -> None:
    _install_launch_case()

    html = serve_result._render_workspace_html("lolla-audit")

    assert "What can I trust or inspect?" in html
    assert "Use Receipts to understand what exists for this run" in html
    assert "Technical inspection" in html
    assert "Source and missingness details" in html
    assert "artifact_refs" not in html
    assert "usage_summary" not in html
    assert "audit_summary" not in html
    assert "not_answer_correctness" in html
    assert "not_advice_correctness" in html


def test_native_learn_docs_review_and_readme_capture_gate_and_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    readme = README.read_text(encoding="utf-8")

    assert "mental-model-teacher-observatory-native-learn-tab-v0.md" in readme
    assert review["decision_gate"] == "proceed_to_interactive_observatory_teacher_graph"
    assert review["ux_guards"]["observatory_aesthetics_reused"] is True
    assert review["ux_guards"]["clickable_model_detail_drawers"] is True
    assert review["ux_guards"]["clickable_relation_detail_drawers"] is True
    assert review["product_decision"]["compiled_spa_changed"] is False
    for phrase in [
        "deep indigo Observatory shell",
        "clickable mental model detail drawers",
        "clickable relation detail drawers",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "proceed_to_interactive_observatory_teacher_graph",
    ]:
        assert phrase in doc


def test_native_learn_docs_and_review_are_clean() -> None:
    text = DOC.read_text(encoding="utf-8") + REVIEW.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
