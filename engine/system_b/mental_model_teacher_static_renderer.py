"""Static Markdown renderer for Mental Model Teacher pilot pages.

This PR-P5 renderer consumes PR-P4 product-page data and writes readable
Markdown pages. It does not render Teacher lessons, build graph data, create
graph UI, call providers, use embeddings, or wire runtime behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .mental_model_teacher_pilot_page_builder import (
    REPO_ROOT,
    build_pilot_page_data,
)
from .mental_model_teacher_product_contracts import (
    validate_mental_model_page,
    validate_relation_page,
)


DEFAULT_RENDER_DIR = REPO_ROOT / "docs/product/mental-model-teacher-pilot-render-v0"
RENDER_MANIFEST_SCHEMA_VERSION = (
    "lolla.mental_model_teacher.static_page_render_manifest.v0"
)


class MentalModelTeacherStaticRendererError(ValueError):
    """Raised when static page rendering cannot complete safely."""


def render_pilot_pages(
    package: dict[str, Any],
    output_dir: Path | str = DEFAULT_RENDER_DIR,
) -> dict[str, Any]:
    """Render model and relation pages to Markdown and return a manifest."""

    target_dir = Path(output_dir)
    model_pages = [validate_mental_model_page(page) for page in package["model_pages"]]
    relation_pages = [
        validate_relation_page(page) for page in package["relation_pages"]
    ]
    model_lookup = {page["model_id"]: page for page in model_pages}
    relation_lookup = _relations_by_model(relation_pages)

    written: list[dict[str, str]] = []
    _write(target_dir / "index.md", render_index_page(package, model_pages, relation_pages))
    written.append({"page_type": "index", "path": "index.md"})

    for page in model_pages:
        path = target_dir / "models" / f"{page['slug']}.md"
        _write(path, render_model_page(page, relation_lookup.get(page["model_id"], []), model_lookup))
        written.append({"page_type": "model", "model_id": page["model_id"], "path": _rel(path, target_dir)})

    for page in relation_pages:
        path = target_dir / "relations" / f"{page['relation_id']}.md"
        _write(path, render_relation_page(page, model_lookup))
        written.append({"page_type": "relation", "relation_id": page["relation_id"], "path": _rel(path, target_dir)})

    manifest = {
        "schema_version": RENDER_MANIFEST_SCHEMA_VERSION,
        "renderer": "engine.system_b.mental_model_teacher_static_renderer",
        "source_package_schema": package.get("schema_version", ""),
        "render_status": "pilot_render_ready_for_review",
        "output_dir": "docs/product/mental-model-teacher-pilot-render-v0",
        "model_page_count": len(model_pages),
        "relation_page_count": len(relation_pages),
        "pages": written,
        "stop_before": [
            "Teacher lesson rendering",
            "graph data building",
            "graph UI",
            "runtime integration",
            "provider or model calls",
        ],
        "non_claims": package["non_claims"],
    }
    _assert_no_local_paths(manifest)
    _write(target_dir / "manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def render_index_page(
    package: dict[str, Any],
    model_pages: list[dict[str, Any]],
    relation_pages: list[dict[str, Any]],
) -> str:
    lines = [
        "# Mental Model Teacher Pilot Pages v0",
        "",
        "Status: static pilot render for review.",
        "",
        "These pages are generated from checked-in source, curation, intervention semantics, and relation semantics. They are product-surface previews, not product proof, human validation, answer correctness, advice correctness, runtime integration, or action authorization.",
        "",
        "## Model Pages",
        "",
    ]
    for page in model_pages:
        lines.append(f"- [{_display(page)}](models/{page['slug']}.md)")
    lines.extend(["", "## Relation Pages", ""])
    for page in relation_pages:
        lines.append(
            f"- [{_relation_title(page, model_pages)}](relations/{page['relation_id']}.md)"
        )
    lines.extend(
        [
            "",
            "## Build Review",
            "",
            f"- Model pages: {package['build_review']['model_page_count']}",
            f"- Relation pages: {package['build_review']['relation_page_count']}",
            f"- Embeddings used: {_bool_word(package['build_review']['embeddings_used'])}",
            f"- Teacher artifacts used: {_bool_word(package['build_review']['checked_in_teacher_artifacts_used'])}",
            f"- Runtime integration authorized: {_bool_word(package['build_review']['runtime_integration_authorized'])}",
            "",
            "## Non-Claims",
            "",
        ]
    )
    lines.extend(_non_claim_lines(package["non_claims"]))
    return _finish(lines)


def render_model_page(
    page: dict[str, Any],
    relations: list[dict[str, Any]],
    model_lookup: dict[str, dict[str, Any]],
) -> str:
    lines = [
        f"# {_display(page)}",
        "",
        _clean(page["one_sentence_meaning"]),
        "",
        "## Helps Notice",
        "",
        *_bullet_lines(page["helps_notice"]),
        "",
        "## Use When",
        "",
        *_bullet_lines(page["use_when"]),
        "",
        "## Avoid When",
        "",
        *_bullet_lines(page["avoid_when"], empty="No source-backed avoid-when items in this pilot."),
        "",
        "## Failure Modes",
        "",
        *_bullet_lines(page["failure_modes"], empty="No source-backed failure modes in this pilot."),
        "",
        "## Premortem Questions",
        "",
        *_bullet_lines(page["premortem_questions"], empty="No source-backed premortem questions in this pilot."),
        "",
        "## Heuristics",
        "",
        *_bullet_lines(page["heuristics"], empty="No source-backed heuristics in this pilot."),
        "",
        "## Common Misuse",
        "",
        *_bullet_lines(page["common_misuse"], empty="Missing in PR-P4 source-backed product fields."),
        "",
        "## Practice Prompts",
        "",
        *_bullet_lines(page["practice_prompts"], empty="Missing in PR-P4 source-backed product fields."),
        "",
        "## Relations In This Pilot",
        "",
    ]
    if relations:
        for relation in relations:
            other_id = (
                relation["target_model_id"]
                if relation["source_model_id"] == page["model_id"]
                else relation["source_model_id"]
            )
            other = model_lookup.get(other_id, {"display_name": other_id})
            lines.append(
                f"- [{_relation_title(relation, list(model_lookup.values()))}](../relations/{relation['relation_id']}.md), with {_display(other)}"
            )
    else:
        lines.append("- No in-subset relation pages for this pilot model.")

    lines.extend(
        [
            "",
            "## Missingness",
            "",
            *_missingness_lines(page["missingness"]),
            "",
            "## Source Custody",
            "",
            *_source_ref_lines(page["source_refs"]),
            *_source_hash_lines(page["source_hashes"]),
            "",
            "## Non-Claims",
            "",
            *_non_claim_lines(page["non_claims"]),
        ]
    )
    return _finish(lines)


def render_relation_page(
    page: dict[str, Any],
    model_lookup: dict[str, dict[str, Any]],
) -> str:
    source = model_lookup.get(page["source_model_id"], {"display_name": page["source_model_id"], "slug": page["source_model_id"]})
    target = model_lookup.get(page["target_model_id"], {"display_name": page["target_model_id"], "slug": page["target_model_id"]})
    lines = [
        f"# {_relation_title(page, list(model_lookup.values()))}",
        "",
        "## Plain-Language Story",
        "",
        _clean(page["plain_language_story"]),
        "",
        "## Why It Matters",
        "",
        _clean(page["why_it_matters"]),
        "",
        "## Practice Prompt",
        "",
        _clean(page["practice_prompt"]),
        "",
        "## Misread Risk",
        "",
        _clean(page["misread_risk"]),
        "",
        "## Model Links",
        "",
        f"- Source model: [{_display(source)}](../models/{source['slug']}.md)",
        f"- Target model: [{_display(target)}](../models/{target['slug']}.md)",
        "",
        "## Taxonomy And Source",
        "",
        f"- Relation type: `{_clean(page['relation_type'])}`",
        f"- Confidence: `{_clean(page['confidence'])}`",
        f"- Curation status: `{_clean(page['curation_status'])}`",
        f"- Source quote or ref: {_code(page['source_quote_or_ref'])}",
        "",
        "## Missingness",
        "",
        *_missingness_lines(page["missingness"]),
        "",
        "## Non-Claims",
        "",
        *_non_claim_lines(page["non_claims"]),
    ]
    return _finish(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render Mental Model Teacher pilot model/relation pages.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RENDER_DIR)
    args = parser.parse_args(argv)

    package = build_pilot_page_data(args.root)
    manifest = render_pilot_pages(package, args.output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _relations_by_model(
    relation_pages: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for page in relation_pages:
        result.setdefault(page["source_model_id"], []).append(page)
        result.setdefault(page["target_model_id"], []).append(page)
    return result


def _write(path: Path, text: str) -> None:
    _assert_no_local_paths(text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _relation_title(page: dict[str, Any], model_pages: list[dict[str, Any]]) -> str:
    names = {item["model_id"]: _display(item) for item in model_pages}
    source = names.get(page["source_model_id"], page["source_model_id"])
    target = names.get(page["target_model_id"], page["target_model_id"])
    return f"{source} and {target}"


def _display(page: dict[str, Any]) -> str:
    return _clean(str(page.get("display_name") or page.get("model_id") or "Unknown"))


def _bullet_lines(items: list[str], *, empty: str = "None recorded.") -> list[str]:
    if not items:
        return [f"- {_clean(empty)}"]
    return [f"- {_clean(item)}" for item in items]


def _missingness_lines(missingness: dict[str, Any]) -> list[str]:
    fields = missingness.get("missing_fields") or []
    notes = missingness.get("notes") or []
    lines = [f"- Status: `{_clean(str(missingness.get('status', 'unknown')))}`"]
    if fields:
        lines.append("- Missing fields: " + ", ".join(f"`{_clean(str(field))}`" for field in fields))
    else:
        lines.append("- Missing fields: none recorded.")
    for note in notes:
        lines.append(f"- {_clean(str(note))}")
    return lines


def _source_ref_lines(refs: list[dict[str, Any]]) -> list[str]:
    lines = []
    for ref in refs:
        lines.append(
            f"- `{_clean(ref['source_type'])}`: `{_clean(ref['path'])}` ({_clean(ref['source_id'])})"
        )
    return lines


def _source_hash_lines(hashes: dict[str, str]) -> list[str]:
    return [f"- Source hash `{_clean(path)}`: `{_clean(digest)}`" for path, digest in hashes.items()]


def _non_claim_lines(non_claims: list[str] | dict[str, bool]) -> list[str]:
    if isinstance(non_claims, dict):
        return [f"- `{_clean(key)}`: `{_bool_word(value)}`" for key, value in non_claims.items()]
    return [f"- `{_clean(item)}`" for item in non_claims]


def _code(value: str) -> str:
    return f"`{_clean(value)}`"


def _bool_word(value: Any) -> str:
    return "true" if value is True else "false"


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
        raise MentalModelTeacherStaticRendererError(
            "rendered output contains a local path marker"
        )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
