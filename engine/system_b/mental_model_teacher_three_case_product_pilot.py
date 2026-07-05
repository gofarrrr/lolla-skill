"""Three-case product pilot builder for Mental Model Teacher.

This PR-P9 retry builder translates checked-in Teacher source artifacts into
product-safe Teacher Lesson Product and Visual Graph objects. It does not call
providers, use embeddings, render browser graph UI, or wire runtime behavior.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from .mental_model_teacher_pilot_page_builder import REPO_ROOT
from .mental_model_teacher_product_contracts import (
    GRAPH_NON_CLAIMS,
    TEACHER_LESSON_SCHEMA_VERSION,
    TEACHER_NON_CLAIMS,
    VISUAL_GRAPH_SCHEMA_VERSION,
    validate_teacher_lesson,
    validate_visual_graph,
)


SOURCE_ROOT = (
    REPO_ROOT / "reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2"
)
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT / "docs/product/mental-model-teacher-three-case-product-pilot-v0"
)
THREE_CASE_PRODUCT_PILOT_MANIFEST_SCHEMA_VERSION = (
    "lolla.mental_model_teacher.three_case_product_pilot_manifest.v0"
)
CASE_IDS = (
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
)
HIGH_RISK_CASES = {"ceo-remove-founding-cofounder"}


class MentalModelTeacherThreeCaseProductPilotError(ValueError):
    """Raised when the three-case product pilot cannot be built safely."""


def build_three_case_product_pilot(
    root: Path | str | None = None,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    """Build and write the three-case product pilot package."""

    repo_root = Path(root) if root is not None else REPO_ROOT
    source_root = repo_root / "reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2"
    target_dir = Path(output_dir)
    cases = [load_case_source(case_id, source_root) for case_id in CASE_IDS]

    lesson_objects = [build_lesson_product(case) for case in cases]
    graphs = [
        build_lesson_graph(case, lesson)
        for case, lesson in zip(cases, lesson_objects, strict=True)
    ]

    _write(target_dir / "index.md", render_index(lesson_objects, graphs))

    pages: list[dict[str, Any]] = [{"page_type": "index", "path": "index.md"}]
    graph_entries: list[dict[str, Any]] = []
    object_entries: list[dict[str, Any]] = []
    for case, lesson, graph in zip(cases, lesson_objects, graphs, strict=True):
        object_path = target_dir / "objects" / f"{case['case_id']}.lesson.json"
        page_path = target_dir / "lessons" / f"{case['case_id']}.md"
        graph_path = target_dir / "graphs" / f"{case['case_id']}.graph.json"

        _write_json(object_path, lesson)
        _write(page_path, render_lesson_page(case, lesson, page_path))
        _write_json(graph_path, graph)

        object_entries.append(
            {
                "case_id": case["case_id"],
                "lesson_id": lesson["lesson_id"],
                "path": _rel(object_path, target_dir),
            }
        )
        pages.append(
            {
                "page_type": "teacher_lesson",
                "case_id": case["case_id"],
                "lesson_id": lesson["lesson_id"],
                "path": _rel(page_path, target_dir),
            }
        )
        graph_entries.append(
            {
                "case_id": case["case_id"],
                "graph_id": graph["graph_id"],
                "path": _rel(graph_path, target_dir),
                "node_count": len(graph["nodes"]),
                "edge_count": len(graph["edges"]),
            }
        )

    manifest = {
        "schema_version": THREE_CASE_PRODUCT_PILOT_MANIFEST_SCHEMA_VERSION,
        "builder": "engine.system_b.mental_model_teacher_three_case_product_pilot",
        "source_root": _repo_rel(source_root),
        "output_dir": _safe_display_path(target_dir),
        "status": "three_case_teacher_product_pilot_ready_for_review",
        "case_count": len(cases),
        "lesson_object_count": len(lesson_objects),
        "lesson_page_count": len(pages) - 1,
        "graph_count": len(graphs),
        "source_artifacts_used": True,
        "decision_work_artifacts_used_as_teacher_source": False,
        "provider_or_model_calls_used": False,
        "runtime_integration_authorized": False,
        "product_proof": False,
        "human_validated": False,
        "objects": object_entries,
        "pages": pages,
        "graphs": graph_entries,
        "high_risk_cases": sorted(HIGH_RISK_CASES),
        "missingness": {
            "status": "partial",
            "missing_fields": [
                "human_review",
                "full_model_product_pages",
                "full_relation_product_pages",
                "browser_graph_ui_review",
            ],
            "notes": [
                "This retry renders productized lesson pages and graph data, not PR-P10 UX review.",
                "Model and relation clickthroughs point to imported OKF source views until full product pages are built.",
            ],
        },
        "non_claims": {
            "product_proof": False,
            "human_validated": False,
            "answer_correctness": False,
            "advice_correctness": False,
            "runtime_integration_authorized": False,
            "graph_edges_are_proof": False,
            "embedding_similarity_is_validated_relation_semantics": False,
            "agent_or_automatic_action_authorized": False,
        },
        "stop_before": [
            "UX review packet",
            "human validation claim",
            "product readiness claim",
            "package gate",
            "browser graph UI",
            "full-corpus graph",
            "runtime integration",
            "provider or model calls",
        ],
    }
    _assert_no_local_paths(manifest)
    _write_json(target_dir / "manifest.json", manifest)
    return manifest


def load_case_source(case_id: str, source_root: Path = SOURCE_ROOT) -> dict[str, Any]:
    """Load the checked-in Teacher source files for one case."""

    case_dir = source_root / case_id
    if not case_dir.exists():
        raise MentalModelTeacherThreeCaseProductPilotError(
            f"missing Teacher source case directory: {case_id}"
        )
    lesson = _load_json(case_dir / "mental_model_teacher_lesson.json")
    relation = _load_json(case_dir / "mental_model_teacher_relation_deep_dive.json")
    model = _load_json(case_dir / "mental_model_teacher_model_deep_dive.json")
    practice = _load_json(case_dir / "mental_model_teacher_practice_lab.json")
    card_text = (case_dir / "mental_model_teacher_card.md").read_text(
        encoding="utf-8"
    )
    note_text = (case_dir / "mental_model_teacher.md").read_text(encoding="utf-8")
    if lesson.get("case_id") != case_id:
        raise MentalModelTeacherThreeCaseProductPilotError(
            f"lesson case_id mismatch: {case_id}"
        )
    return {
        "case_id": case_id,
        "case_dir": case_dir,
        "lesson": lesson,
        "relation": relation,
        "model": model,
        "practice": practice,
        "card_text": card_text,
        "note_text": note_text,
    }


def build_lesson_product(case: dict[str, Any]) -> dict[str, Any]:
    source_lesson = case["lesson"]["lesson"]
    model_stack = [
        {
            "model_id": item["model_id"],
            "role": item["role"],
            "teaching_name": item["teaching_name"],
            "teaching_note": item["what_it_adds"],
            "boundary": item["boundary"],
        }
        for item in source_lesson["model_stack"]
    ]
    source_refs = _case_source_refs(case)
    lesson = {
        "schema_version": TEACHER_LESSON_SCHEMA_VERSION,
        "lesson_id": case["case_id"],
        "case_id": case["case_id"],
        "case_anchor": source_lesson["case_anchor"],
        "thinking_move": source_lesson["dominant_thinking_move"],
        "model_stack": model_stack,
        "relation_story": source_lesson["relationship_story"],
        "model_links": [
            {
                "label": item["teaching_name"],
                "href": _okf_model_path(case["case_dir"], item["model_id"]),
            }
            for item in source_lesson["model_stack"]
        ],
        "relation_links": [
            {
                "label": _relation_label(case),
                "href": _okf_relation_path(case),
            }
        ],
        "practice_rep": _practice_rep(source_lesson),
        "do_not_overlearn": _do_not_overlearn(case, source_lesson),
        "source_refs": source_refs,
        "human_review_status": "pending",
        "product_proof": False,
        "runtime_integration_authorized": False,
        "missingness": {
            "status": "partial",
            "missing_fields": [
                "human_review",
                "full_model_product_pages",
                "full_relation_product_pages",
            ],
            "notes": [
                "Built from imported Teacher source artifacts after PR-P9 source-custody unblocker.",
                "Model and relation clickthroughs use imported OKF source views in this retry.",
            ],
        },
        "non_claims": sorted(TEACHER_NON_CLAIMS),
    }
    if case["case_id"] in HIGH_RISK_CASES:
        lesson["missingness"]["notes"].append(
            "High-risk case: preserve legal, HR, governance, interpersonal, answer, and advice non-claims."
        )
    return validate_teacher_lesson(lesson)


def build_lesson_graph(
    case: dict[str, Any],
    lesson: dict[str, Any],
) -> dict[str, Any]:
    relation = case["relation"]["relation"]
    nodes = []
    for item in lesson["model_stack"]:
        nodes.append(
            {
                "node_id": item["model_id"],
                "model_id": item["model_id"],
                "label": item.get("teaching_name") or _titleize_model_id(item["model_id"]),
                "node_type": "mental_model",
                "role": item["role"],
                "href": _relative_from_graph(case, _okf_model_path(case["case_dir"], item["model_id"])),
                "source_status": "source_artifact",
                "missingness_status": "partial",
            }
        )

    edge = {
        "edge_id": relation["relation_id"],
        "source_node_id": relation["source_model_id"],
        "target_node_id": relation["target_model_id"],
        "relation_id": relation["relation_id"],
        "relation_type": _normalize_relation_type(relation["relation_type"]),
        "label": _relation_label(case),
        "href": _relative_from_graph(case, _okf_relation_path(case)),
        "source_status": relation["provenance"]["status"],
        "missingness_status": "partial",
        "confidence": "medium",
    }
    graph = {
        "schema_version": VISUAL_GRAPH_SCHEMA_VERSION,
        "graph_id": f"lesson-neighborhood-{case['case_id']}",
        "graph_scope": "lesson_neighborhood",
        "lesson_id": lesson["lesson_id"],
        "case_id": case["case_id"],
        "nodes": nodes,
        "edges": [edge],
        "source_artifacts": [
            {
                "artifact_id": f"{case['case_id']}-lesson-source",
                "path": _repo_rel(case["case_dir"] / "mental_model_teacher_lesson.json"),
                "source_type": "teacher_lesson_source",
            },
            {
                "artifact_id": f"{case['case_id']}-relation-source",
                "path": _repo_rel(
                    case["case_dir"] / "mental_model_teacher_relation_deep_dive.json"
                ),
                "source_type": "teacher_relation_deep_dive_source",
            },
        ],
        "layout_hint": "small_neighborhood",
        "default_focus": lesson["model_stack"][0]["model_id"],
        "filters": {
            "relation_types": [_normalize_relation_type(relation["relation_type"])],
            "node_types": ["mental_model"],
            "max_nodes": 10,
        },
        "missingness": {
            "status": "partial",
            "missing_fields": [
                "browser_graph_ui",
                "full_model_product_pages",
                "full_relation_product_pages",
                "human_review",
            ],
            "notes": [
                "Graph data only; no browser graph UI is added in this PR-P9 retry.",
                "Edges come from imported Teacher relation deep-dive source and are navigation, not proof.",
            ],
        },
        "non_claims": sorted(GRAPH_NON_CLAIMS),
    }
    return validate_visual_graph(graph)


def render_index(
    lessons: list[dict[str, Any]],
    graphs: list[dict[str, Any]],
) -> str:
    graph_lookup = {graph["case_id"]: graph for graph in graphs}
    lines = [
        "# Mental Model Teacher Three-Case Product Pilot v0",
        "",
        "Status: PR-P9 retry product pilot ready for review.",
        "",
        "Product framing: case is the anchor; reasoning move is the subject; model relationship is the lesson; practice rep is the product value.",
        "",
        "This package translates imported Teacher source artifacts into productized lesson pages and small graph-neighborhood JSON. It does not claim product proof, human validation, answer correctness, advice correctness, runtime integration, or action authorization.",
        "",
        "## Lessons",
        "",
    ]
    for lesson in lessons:
        case_id = lesson["case_id"]
        graph = graph_lookup[case_id]
        lines.append(
            f"- [{_clean(lesson['thinking_move'])}](lessons/{case_id}.md) - [graph JSON](graphs/{case_id}.graph.json), `{len(graph['nodes'])}` nodes, `{len(graph['edges'])}` edge"
        )
    lines.extend(
        [
            "",
            "## Missingness",
            "",
            "- Human review is pending.",
            "- Full product model pages and relation pages for every case model are outside this PR.",
            "- Browser graph UI for these case neighborhoods is outside this PR.",
            "",
            "## Non-Claims",
            "",
            "- `not_product_proof`",
            "- `not_human_validation`",
            "- `not_answer_correctness`",
            "- `not_advice_correctness`",
            "- `not_runtime_integration`",
            "- `not_action_authorization`",
            "- `graph_edges_are_navigation_not_proof`",
        ]
    )
    return _finish(lines)


def render_lesson_page(
    case: dict[str, Any],
    lesson: dict[str, Any],
    page_path: Path,
) -> str:
    source_lesson = case["lesson"]["lesson"]
    relation = case["relation"]["relation"]
    worked_example = _worked_example(case["card_text"])
    lines = [
        f"# {_clean(lesson['thinking_move'])}",
        "",
        "Product framing: case is the anchor; reasoning move is the subject; model relationship is the lesson; practice rep is the product value.",
        "",
        f"Case: `{case['case_id']}`",
        "",
        "## Case Anchor",
        "",
        _clean(lesson["case_anchor"]),
        "",
        "## Thinking Move",
        "",
        _clean(lesson["thinking_move"]),
        "",
        "## Why This Move Mattered",
        "",
        _clean(source_lesson["why_this_move_mattered"]),
        "",
        "## Model Stack",
        "",
    ]
    for item in lesson["model_stack"]:
        href = _page_href(page_path, _okf_model_path(case["case_dir"], item["model_id"]))
        lines.append(
            f"- [{_clean(item['teaching_name'])}]({href}) - `{_clean(item['role'])}`: {_clean(item['teaching_note'])}"
        )
        lines.append(f"  Boundary: {_clean(item['boundary'])}")

    lines.extend(
        [
            "",
            "## Relation Story",
            "",
            _clean(lesson["relation_story"]),
            "",
            "## Relation Clickthrough",
            "",
            f"- [{_clean(_relation_label(case))}]({_page_href(page_path, _okf_relation_path(case))})",
            "",
            "## Worked Example",
            "",
        ]
    )
    lines.extend(worked_example or ["- No worked example was supplied in the source card."])
    lines.extend(
        [
            "",
            "## Practice Rep",
            "",
            f"- Prompt: {_clean(lesson['practice_rep']['prompt'])}",
            f"- User action: {_clean(lesson['practice_rep']['user_action'])}",
            "",
            "## Do Not Overlearn",
            "",
        ]
    )
    lines.extend([f"- {_clean(item)}" for item in lesson["do_not_overlearn"]])
    if case["case_id"] in HIGH_RISK_CASES:
        lines.extend(
            [
                "",
                "## High-Risk Case Caveat",
                "",
                "This case involves founder, governance, HR, legal, and interpersonal risk. This page teaches a reasoning move only; it does not imply the correct action, legal answer, HR answer, governance answer, interpersonal answer, advice correctness, or answer correctness.",
            ]
        )
    lines.extend(
        [
            "",
            "## Human Gate Status",
            "",
            f"- Human review status: `{lesson['human_review_status']}`",
            f"- Product proof: `{_bool_word(lesson['product_proof'])}`",
            f"- Runtime integration authorized: `{_bool_word(lesson['runtime_integration_authorized'])}`",
            "",
            "## Source Trail",
            "",
            f"- [Teacher card]({_page_href(page_path, _repo_rel(case['case_dir'] / 'mental_model_teacher_card.md'))})",
            f"- [Teacher note]({_page_href(page_path, _repo_rel(case['case_dir'] / 'mental_model_teacher.md'))})",
            f"- [Practice lab]({_page_href(page_path, _repo_rel(case['case_dir'] / 'mental_model_teacher_practice_lab.md'))})",
            f"- [Model deep dive]({_page_href(page_path, _repo_rel(case['case_dir'] / 'mental_model_teacher_model_deep_dive.md'))})",
            f"- [Relation deep dive]({_page_href(page_path, _repo_rel(case['case_dir'] / 'mental_model_teacher_relation_deep_dive.md'))})",
            "",
            "## Graph Neighborhood",
            "",
            f"- [Graph JSON](../graphs/{case['case_id']}.graph.json)",
            "",
            "## Non-Claims",
            "",
        ]
    )
    lines.extend([f"- `{item}`" for item in lesson["non_claims"]])
    lines.extend(
        [
            "- `graph_edges_are_navigation_not_proof`",
            "- `embedding_similarity_not_used`",
        ]
    )
    _assert_no_local_paths("\n".join(lines))
    _assert_no_forbidden_runtime_claims("\n".join(lines))
    _ = relation
    return _finish(lines)


def _case_source_refs(case: dict[str, Any]) -> list[dict[str, str]]:
    paths = [
        ("teacher_lesson_source", "mental_model_teacher_lesson.json"),
        ("teacher_card_source", "mental_model_teacher_card.md"),
        ("teacher_note_source", "mental_model_teacher.md"),
        ("teacher_model_deep_dive_source", "mental_model_teacher_model_deep_dive.json"),
        ("teacher_relation_deep_dive_source", "mental_model_teacher_relation_deep_dive.json"),
        ("teacher_practice_lab_source", "mental_model_teacher_practice_lab.json"),
    ]
    return [
        {
            "source_id": f"{case['case_id']}:{source_type}",
            "path": _repo_rel(case["case_dir"] / filename),
            "source_type": source_type,
        }
        for source_type, filename in paths
    ]


def _practice_rep(source_lesson: dict[str, Any]) -> dict[str, str]:
    practice = source_lesson["practice_reps"][0]
    return {
        "prompt": practice["title"],
        "user_action": " ".join(practice["steps"]),
    }


def _do_not_overlearn(
    case: dict[str, Any],
    source_lesson: dict[str, Any],
) -> list[str]:
    items = [
        source_lesson["do_not_overlearn"],
        source_lesson["where_the_lesson_stops"],
        "This product page is not a Decision Work brief and does not authorize action.",
    ]
    if case["case_id"] in HIGH_RISK_CASES:
        items.append(
            "High-risk caveat: do not infer legal, HR, governance, interpersonal, answer, or advice correctness from this lesson."
        )
    return items


def _worked_example(card_text: str) -> list[str]:
    lines = card_text.splitlines()
    try:
        start = lines.index("Worked example:") + 1
    except ValueError:
        return []
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("# "):
            end = index
            break
    return [_clean(line) for line in lines[start:end] if line.strip()]


def _relation_label(case: dict[str, Any]) -> str:
    relation = case["relation"]["relation"]
    source = _titleize_model_id(relation["source_model_id"])
    target = _titleize_model_id(relation["target_model_id"])
    relation_type = _normalize_relation_type(relation["relation_type"]).replace("_", " ")
    return f"{source} and {target} ({relation_type})"


def _normalize_relation_type(value: str) -> str:
    if value == "structured_tension":
        return "tension"
    return value


def _okf_model_path(case_dir: Path, model_id: str) -> str:
    return _repo_rel(case_dir / "okf/mental_model_teacher/models" / f"{model_id}.md")


def _okf_relation_path(case: dict[str, Any]) -> str:
    relation_id = case["relation"]["relation"]["relation_id"]
    return _repo_rel(
        case["case_dir"]
        / "okf/mental_model_teacher/relations"
        / f"{relation_id}.md"
    )


def _relative_from_graph(case: dict[str, Any], repo_relative_path: str) -> str:
    graph_path = DEFAULT_OUTPUT_DIR / "graphs" / f"{case['case_id']}.graph.json"
    return _page_href(graph_path, repo_relative_path)


def _page_href(page_path: Path, repo_relative_path: str) -> str:
    try:
        page_path.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        return repo_relative_path
    return os.path.relpath(REPO_ROOT / repo_relative_path, page_path.parent)


def _repo_rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise MentalModelTeacherThreeCaseProductPilotError(
            "path must stay inside the repository"
        ) from exc


def _safe_display_path(path: Path) -> str:
    try:
        return _repo_rel(path)
    except MentalModelTeacherThreeCaseProductPilotError:
        return path.name


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MentalModelTeacherThreeCaseProductPilotError(
            f"missing source JSON: {_repo_rel(path)}"
        ) from exc
    if not isinstance(payload, dict):
        raise MentalModelTeacherThreeCaseProductPilotError(
            f"source JSON root must be an object: {_repo_rel(path)}"
        )
    return payload


def _write(path: Path, text: str) -> None:
    _assert_no_local_paths(text)
    _assert_no_forbidden_runtime_claims(text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _assert_no_local_paths(payload)
    _assert_no_forbidden_runtime_claims(json.dumps(payload, sort_keys=True))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _finish(lines: list[str]) -> str:
    return "\n".join(_clean(line) for line in lines).rstrip() + "\n"


def _clean(text: Any) -> str:
    return str(text).replace("\r", " ").strip()


def _titleize_model_id(model_id: str) -> str:
    return " ".join(part.capitalize() for part in model_id.split("-"))


def _bool_word(value: bool) -> str:
    return "true" if value else "false"


def _assert_no_local_paths(payload: Any) -> None:
    rendered = json.dumps(payload, sort_keys=True) if not isinstance(payload, str) else payload
    markers = (
        "/" + "Users/",
        "Desktop/" + "Apps",
        "\\" + "Users\\",
    )
    if any(marker in rendered for marker in markers):
        raise MentalModelTeacherThreeCaseProductPilotError(
            "three-case product pilot contains a local path marker"
        )


def _assert_no_forbidden_runtime_claims(rendered: str) -> None:
    forbidden = (
        "product_proof\": true",
        "human_validated\": true",
        "runtime_integration_authorized\": true",
        "Product proof: `true`",
        "Runtime integration authorized: `true`",
    )
    if any(marker in rendered for marker in forbidden):
        raise MentalModelTeacherThreeCaseProductPilotError(
            "three-case product pilot contains a forbidden positive claim"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the Mental Model Teacher three-case product pilot.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    manifest = build_three_case_product_pilot(args.root, args.output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
