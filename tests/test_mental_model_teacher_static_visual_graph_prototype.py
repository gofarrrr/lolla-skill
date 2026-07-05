import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE_DIR = REPO_ROOT / "docs/product/mental-model-teacher-visual-graph-prototype-v0"
HTML = PROTOTYPE_DIR / "index.html"
MANIFEST = PROTOTYPE_DIR / "manifest.json"
SOURCE_GRAPH = (
    REPO_ROOT
    / "docs/product/mental-model-teacher-lesson-graph-v0/contract-fixture-base-rates-system-2.graph.json"
)
DOC = REPO_ROOT / "docs/product/mental-model-teacher-static-visual-graph-prototype-v0.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-static-visual-graph-prototype-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"


def _embedded_graph() -> dict:
    text = HTML.read_text(encoding="utf-8")
    match = re.search(
        r'<script id="graph-data" type="application/json">\s*(.*?)\s*</script>',
        text,
        re.S,
    )
    assert match is not None
    return json.loads(match.group(1))


def test_prototype_manifest_matches_static_html_entrypoint() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == (
        "lolla.mental_model_teacher.static_visual_graph_prototype_manifest.v0"
    )
    assert manifest["prototype_status"] == "static_visual_graph_prototype_ready_for_review"
    assert manifest["entrypoint"].endswith(
        "mental-model-teacher-visual-graph-prototype-v0/index.html"
    )
    assert manifest["implementation"]["renderer"] == "dependency_free_svg"
    assert manifest["implementation"]["external_network_required"] is False
    assert manifest["implementation"]["provider_or_model_calls_used"] is False
    assert manifest["features"]["selected_node_panel"] is True
    assert manifest["features"]["selected_edge_panel"] is True
    assert manifest["features"]["relation_type_filters"] is True
    assert manifest["features"]["search"] is True


def test_embedded_graph_data_matches_pr_p7_graph_identity_and_counts() -> None:
    embedded = _embedded_graph()
    source = json.loads(SOURCE_GRAPH.read_text(encoding="utf-8"))

    assert embedded["schema_version"] == source["schema_version"]
    assert embedded["graph_id"] == source["graph_id"]
    assert embedded["lesson_id"] == source["lesson_id"]
    assert embedded["default_focus"] == "base-rates"
    assert len(embedded["nodes"]) == 2
    assert len(embedded["edges"]) == 1
    assert {node["node_id"] for node in embedded["nodes"]} == {
        "base-rates",
        "system-2",
    }
    assert embedded["edges"][0]["edge_id"] == "base-rates__ally__system-2"


def test_html_contains_required_interactive_controls_and_panels() -> None:
    text = HTML.read_text(encoding="utf-8")

    for marker in [
        'id="graph-canvas"',
        'id="graph-search"',
        'id="relation-filters"',
        'id="reset-view"',
        'id="selected-node-panel"',
        'id="selected-edge-panel"',
        "addEventListener",
        "selectNode",
        "selectEdge",
        "Open model page",
        "Open relation page",
    ]:
        assert marker in text


def test_prototype_has_no_external_network_dependencies() -> None:
    text = HTML.read_text(encoding="utf-8")
    text_without_svg_namespace = text.replace("http://www.w3.org/2000/svg", "")

    assert "http://" not in text_without_svg_namespace
    assert "https://" not in text_without_svg_namespace
    assert "cdn" not in text.lower()
    assert "<script src=" not in text
    assert "<link rel=\"stylesheet\"" not in text
    assert "fetch(" not in text


def test_graph_links_resolve_from_prototype_directory() -> None:
    embedded = _embedded_graph()
    missing = []

    for node in embedded["nodes"]:
        if not (PROTOTYPE_DIR / node["href"]).resolve().exists():
            missing.append(node["href"])
    for edge in embedded["edges"]:
        if not (PROTOTYPE_DIR / edge["href"]).resolve().exists():
            missing.append(edge["href"])

    assert missing == []


def test_static_markdown_and_html_links_resolve() -> None:
    files = [HTML, DOC, README]
    missing = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".html":
            targets = re.findall(r'href="([^"]+)"', text)
        else:
            targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
        for target in targets:
            if (
                target.startswith("#")
                or re.match(r"^[a-z]+:", target)
                or target.startswith("{")
                or target.startswith("${")
            ):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    assert missing == []


def test_prototype_preserves_non_claim_boundaries() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [HTML, MANIFEST, REVIEW]
    )

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "\"affinity\"" not in text
    assert "\"rank\"" not in text
    assert "\"score\"" not in text
    assert "\"embedding_similarity\":" not in text


def test_doc_and_review_preserve_pr_p8_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    index = README.read_text(encoding="utf-8")

    assert "mental-model-teacher-static-visual-graph-prototype-v0.md" in index
    assert "mental-model-teacher-visual-graph-prototype-v0/index.html" in index
    assert review["decision_gate"] == "proceed_to_three_case_teacher_product_pilot"
    assert review["implementation"]["renderer"] == "dependency_free_svg"
    assert review["implementation"]["external_network_required"] is False
    assert review["graph_counts"]["nodes"] == 2
    assert review["graph_counts"]["edges"] == 1

    for phrase in [
        "does not build a full-corpus graph",
        "does not use embeddings",
        "does not expose relationship-graph affinity or rank",
        "does not call providers or model APIs",
        "does not wire runtime",
        "Cytoscape.js remains the preferred renderer",
    ]:
        assert phrase in doc
