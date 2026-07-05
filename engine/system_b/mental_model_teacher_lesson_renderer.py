"""Static Teacher lesson renderer for the Mental Model Teacher product lane.

This PR-P6 renderer writes lesson Markdown from an already validated Teacher
Lesson Product object. It does not invent real Teacher case artifacts, build
graphs, call providers, or wire runtime behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .mental_model_teacher_pilot_page_builder import REPO_ROOT
from .mental_model_teacher_product_contracts import validate_teacher_lesson


DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs/product/mental-model-teacher-lesson-render-v0"
LESSON_RENDER_MANIFEST_SCHEMA_VERSION = (
    "lolla.mental_model_teacher.lesson_render_manifest.v0"
)
EXAMPLES_PATH = REPO_ROOT / "docs/product/mental-model-teacher-product-contract-examples-v0.json"


class MentalModelTeacherLessonRendererError(ValueError):
    """Raised when lesson rendering cannot complete safely."""


def load_contract_fixture_lesson(root: Path | str | None = None) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else REPO_ROOT
    examples_path = repo_root / "docs/product/mental-model-teacher-product-contract-examples-v0.json"
    payload = json.loads(examples_path.read_text(encoding="utf-8"))
    lesson = payload.get("examples", {}).get("teacher_lesson")
    if not isinstance(lesson, dict):
        raise MentalModelTeacherLessonRendererError("teacher_lesson fixture missing")
    return validate_teacher_lesson(lesson)


def render_lesson_pages(
    lessons: list[dict[str, Any]],
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    target_dir = Path(output_dir)
    validated = [validate_teacher_lesson(lesson) for lesson in lessons]
    written: list[dict[str, str]] = []

    _write(target_dir / "index.md", render_lesson_index(validated))
    written.append({"page_type": "index", "path": "index.md"})

    for lesson in validated:
        path = target_dir / "lessons" / f"{lesson['lesson_id']}.md"
        _write(path, render_teacher_lesson_page(lesson))
        written.append(
            {
                "page_type": "teacher_lesson",
                "lesson_id": lesson["lesson_id"],
                "path": _rel(path, target_dir),
            }
        )

    manifest = {
        "schema_version": LESSON_RENDER_MANIFEST_SCHEMA_VERSION,
        "renderer": "engine.system_b.mental_model_teacher_lesson_renderer",
        "render_status": "fixture_lesson_render_ready_for_review",
        "output_dir": "docs/product/mental-model-teacher-lesson-render-v0",
        "lesson_count": len(validated),
        "pages": written,
        "teacher_artifacts_used": False,
        "real_teacher_case_claimed": False,
        "stop_before": [
            "graph data building",
            "graph UI",
            "runtime integration",
            "provider or model calls",
        ],
        "non_claims": {
            "product_proof": False,
            "human_validated": False,
            "answer_correctness": False,
            "advice_correctness": False,
            "runtime_integration_authorized": False,
            "agent_or_automatic_action_authorized": False,
            "real_teacher_case_artifact_claimed": False,
            "lesson_is_not_advice": True,
        },
    }
    _assert_no_local_paths(manifest)
    _write(target_dir / "manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def render_lesson_index(lessons: list[dict[str, Any]]) -> str:
    lines = [
        "# Mental Model Teacher Lesson Pilot v0",
        "",
        "Status: fixture lesson render for review.",
        "",
        "This render demonstrates only the lesson-page renderer shape. No checked-in Teacher case artifact is claimed, and no human validation, product proof, advice correctness, answer correctness, runtime integration, or action authorization is claimed.",
        "",
        "Product framing: case is the anchor; reasoning move is the subject; model relationship is the lesson; practice rep is the product value.",
        "",
        "## Lessons",
        "",
    ]
    for lesson in lessons:
        lines.append(
            f"- [{_clean(lesson['thinking_move'])}](lessons/{lesson['lesson_id']}.md)"
        )
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(
        [
            "- `not_product_proof`",
            "- `not_human_validation`",
            "- `not_answer_correctness`",
            "- `not_advice_correctness`",
            "- `not_runtime_integration`",
            "- `not_action_authorization`",
        ]
    )
    return _finish(lines)


def render_teacher_lesson_page(lesson: dict[str, Any]) -> str:
    model_labels = {
        Path(str(link["href"])).stem: _clean(str(link["label"]))
        for link in lesson["model_links"]
    }
    lines = [
        f"# {_clean(lesson['thinking_move'])}",
        "",
        "Product framing: case is the anchor; reasoning move is the subject; model relationship is the lesson; practice rep is the product value.",
        "",
        "## Case Anchor",
        "",
        _clean(lesson["case_anchor"]),
        "",
        "## Thinking Move",
        "",
        _clean(lesson["thinking_move"]),
        "",
        "## Model Stack",
        "",
    ]
    for item in lesson["model_stack"]:
        model_id = _clean(str(item.get("model_id", "")))
        role = _clean(str(item.get("role", "")))
        note = _clean(str(item.get("teaching_note", "")))
        link = _model_link(model_id, model_labels.get(model_id, model_id))
        lines.append(f"- {link} - `{role}`: {note}")

    lines.extend(
        [
            "",
            "## Relation Story",
            "",
            _clean(lesson["relation_story"]),
            "",
            "## Model Clickthroughs",
            "",
        ]
    )
    for link in lesson["model_links"]:
        lines.append(f"- [{_clean(link['label'])}]({_lesson_model_href(link['href'])})")

    lines.extend(["", "## Relation Clickthroughs", ""])
    if lesson["relation_links"]:
        for link in lesson["relation_links"]:
            lines.append(
                f"- [{_clean(link['label'])}]({_lesson_relation_href(link['href'])})"
            )
    else:
        lines.append("- No relation links supplied in this fixture.")

    lines.extend(
        [
            "",
            "## Worked Example",
            "",
            "This fixture applies the thinking move to the case anchor by asking the user to separate the local launch story from the outside-view prior before updating. It is not a completed real Teacher case artifact.",
            "",
            "## Practice Rep",
            "",
            f"- Prompt: {_clean(lesson['practice_rep']['prompt'])}",
            f"- User action: {_clean(lesson['practice_rep']['user_action'])}",
            "",
            "## Do Not Overlearn",
            "",
            *_bullet_lines(lesson["do_not_overlearn"]),
            "",
            "## Human Gate Status",
            "",
            f"- Human review status: `{_clean(lesson['human_review_status'])}`",
            f"- Product proof: `{_bool_word(lesson['product_proof'])}`",
            f"- Runtime integration authorized: `{_bool_word(lesson['runtime_integration_authorized'])}`",
            "",
            "## Missingness",
            "",
            *_missingness_lines(lesson["missingness"]),
            "",
            "## Source Refs",
            "",
            *_source_ref_lines(lesson["source_refs"]),
            "",
            "## Non-Claims",
            "",
            *_bullet_code_lines(lesson["non_claims"]),
        ]
    )
    return _finish(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render Mental Model Teacher fixture lesson pages.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    lesson = load_contract_fixture_lesson(args.root)
    manifest = render_lesson_pages([lesson], args.output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _lesson_model_href(href: str) -> str:
    return "../../mental-model-teacher-pilot-render-v0/models/" + _clean(href)


def _lesson_relation_href(href: str) -> str:
    return "../../mental-model-teacher-pilot-render-v0/relations/" + _clean(href)


def _model_link(model_id: str, label: str) -> str:
    return f"[{_clean(label)}]({_lesson_model_href(model_id + '.md')})"


def _bullet_lines(items: list[str]) -> list[str]:
    return [f"- {_clean(item)}" for item in items] if items else ["- None supplied."]


def _bullet_code_lines(items: list[str]) -> list[str]:
    return [f"- `{_clean(item)}`" for item in items] if items else ["- None supplied."]


def _missingness_lines(missingness: dict[str, Any]) -> list[str]:
    fields = missingness.get("missing_fields") or []
    notes = missingness.get("notes") or []
    lines = [f"- Status: `{_clean(str(missingness.get('status', 'unknown')))}`"]
    if fields:
        lines.append(
            "- Missing fields: "
            + ", ".join(f"`{_clean(str(field))}`" for field in fields)
        )
    else:
        lines.append("- Missing fields: none recorded.")
    for note in notes:
        lines.append(f"- {_clean(str(note))}")
    return lines


def _source_ref_lines(refs: list[dict[str, Any]]) -> list[str]:
    return [
        f"- `{_clean(ref['source_type'])}`: `{_clean(ref['path'])}` ({_clean(ref['source_id'])})"
        for ref in refs
    ]


def _write(path: Path, text: str) -> None:
    _assert_no_local_paths(text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _finish(lines: list[str]) -> str:
    return "\n".join(_clean(line) for line in lines).rstrip() + "\n"


def _clean(text: str) -> str:
    replacements = {
        "\u2014": " - ",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u00a0": " ",
    }
    cleaned = text
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    return " ".join(cleaned.split()) if "\n" not in cleaned else cleaned


def _bool_word(value: Any) -> str:
    return "true" if value is True else "false"


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _assert_no_local_paths(payload: Any) -> None:
    rendered = json.dumps(payload, sort_keys=True) if not isinstance(payload, str) else payload
    markers = (
        "/" + "Users/",
        "Desktop/" + "Apps",
        "\\" + "Users\\",
    )
    if any(marker in rendered for marker in markers):
        raise MentalModelTeacherLessonRendererError(
            "lesson render contains a local path marker"
        )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
