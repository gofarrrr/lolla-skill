"""Build the learner-first Mental Model Teacher static prototype.

This slice uses existing three-case Teacher lesson and graph artifacts to render
a browser-visible learning surface. It keeps review/custody data behind an
explicit Review mode and receipts details. It does not run Lolla, call provider
or model APIs, create new Lolla runs, wire runtime behavior, or claim proof.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from .mental_model_teacher_pilot_page_builder import REPO_ROOT


LEARNER_EXPERIENCE_SCHEMA_VERSION = (
    "lolla.mental_model_teacher.learner_experience_prototype.v0"
)
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT / "docs/product/mental-model-teacher-learner-experience-prototype-v0"
)
PILOT_DIR = REPO_ROOT / "docs/product/mental-model-teacher-three-case-product-pilot-v0"
CASE_IDS = (
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
)
MODE_IDS = ("learn", "models", "relations", "map", "review")
CANONICAL_SECTION_MAX_CHARS = 3200
CASE_PRESENTATION = {
    "launch-public-enterprise-beta": {
        "label": "Launch beta",
        "short_title": "Enterprise beta pressure",
        "situation": (
            "A recommendation looked credible because the enterprise signal felt "
            "impressive."
        ),
        "trap": (
            "Prestige can make confidence look like evidence. The learner has to "
            "separate authority from the facts that would still matter without it."
        ),
    },
    "deploy-assisted-intake-routing": {
        "label": "Deploy routing",
        "short_title": "Assisted intake routing",
        "situation": (
            "One large recommendation risked treating unlike decision types as if "
            "they needed the same rule."
        ),
        "trap": (
            "A single answer can flatten reversible experiments, irreversible "
            "commitments, and routing buckets into one undifferentiated choice."
        ),
    },
    "ceo-remove-founding-cofounder": {
        "label": "Founder/cofounder",
        "short_title": "Removing a founding cofounder",
        "situation": (
            "A high-pressure leadership situation mixed emotion, governance, trust, "
            "and decision standards."
        ),
        "trap": (
            "The emotion in the room can either dominate the rule or get ignored. "
            "The move is to name it, then keep the decision rule separate."
        ),
    },
}
HIGH_RISK_CASES = {"ceo-remove-founding-cofounder"}
NON_CLAIMS = {
    "product_proof": False,
    "human_validated": False,
    "answer_correctness": False,
    "advice_correctness": False,
    "runtime_integration_authorized": False,
    "graph_edges_are_proof": False,
    "embedding_similarity_is_validated_relation_semantics": False,
    "agent_or_automatic_action_authorized": False,
}


class MentalModelTeacherLearnerExperienceError(ValueError):
    """Raised when the learner-first prototype cannot be rendered safely."""


def build_learner_experience_prototype(
    root: Path | str | None = None,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    """Build and write the learner-first static prototype."""

    repo_root = Path(root) if root is not None else REPO_ROOT
    target_dir = Path(output_dir)
    cases = [_case_payload(repo_root, case_id, target_dir) for case_id in CASE_IDS]
    models = _model_catalog(cases, repo_root, target_dir)
    relations = _relation_catalog(cases)
    data = {
        "schema_version": LEARNER_EXPERIENCE_SCHEMA_VERSION,
        "product_lane": "Mental Model Teacher Product Surface And Visual Library",
        "status": "learner_first_static_prototype",
        "default_mode": "learn",
        "modes": [
            {
                "id": mode_id,
                "label": {
                    "learn": "Learn",
                    "models": "Models",
                    "relations": "Relations",
                    "map": "Map",
                    "review": "Review",
                }[mode_id],
            }
            for mode_id in MODE_IDS
        ],
        "visibility_tiers": [
            "primary",
            "context",
            "receipts",
            "internal_hidden_from_learner",
        ],
        "cases": cases,
        "models": models,
        "relations": relations,
        "search_index": _search_index(cases, models, relations),
        "non_claims": NON_CLAIMS,
    }
    html_text = render_learner_experience(data)
    manifest = {
        "schema_version": LEARNER_EXPERIENCE_SCHEMA_VERSION,
        "builder": "engine.system_b.mental_model_teacher_learner_experience",
        "status": "learner_first_static_prototype",
        "output_dir": _safe_display_path(target_dir),
        "entrypoint": "index.html",
        "embedded_data": True,
        "external_network_required": False,
        "provider_or_model_calls_used": False,
        "lolla_skill_invoked": False,
        "runtime_integration_authorized": False,
        "human_review_completed": False,
        "human_validated": False,
        "product_proof": False,
        "default_mode": "learn",
        "mode_ids": list(MODE_IDS),
        "case_count": len(cases),
        "model_count": len(models),
        "canonical_model_source_count": sum(
            1 for model in models if model["canonical"]["status"] == "available"
        ),
        "relation_count": len(relations),
        "search_result_types": ["lesson", "model", "relation", "practice"],
        "learner_first_rules": {
            "learn_mode_default": True,
            "raw_source_snapshots_hidden_from_learn_mode": True,
            "review_controls_separate_from_learn_mode": True,
            "receipts_collapsed_by_default": True,
            "graph_is_secondary_map_mode": True,
            "typed_search_present": True,
            "model_backlinks_present": True,
            "relation_backlinks_present": True,
            "canonical_model_detail_present": True,
            "model_click_opens_product_detail": True,
        },
        "source_packages": [
            "data/model_sources",
            "data/model_sources/manifest.json",
            "data/curation",
            "data/curation/intervention_semantics",
            "data/curation/relation_semantics",
            "docs/product/mental-model-teacher-three-case-product-pilot-v0/objects",
            "docs/product/mental-model-teacher-three-case-product-pilot-v0/graphs",
        ],
        "non_claims": NON_CLAIMS,
        "stop_before": [
            "full corpus graph",
            "runtime integration",
            "provider or model calls",
            "human validation claim",
            "product proof claim",
            "answer correctness claim",
            "advice correctness claim",
        ],
    }
    _write(target_dir / "index.html", html_text)
    _write_json(target_dir / "manifest.json", manifest)
    return manifest


def render_learner_experience(data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True)
    payload = payload.replace("</", "<\\/")
    return _finish(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>Mental Model Teacher Learner Prototype</title>",
            "  <style>",
            _CSS,
            "  </style>",
            "</head>",
            "<body>",
            '  <div id="app" class="app-shell"></div>',
            f'  <script id="learner-data" type="application/json">{payload}</script>',
            "  <script>",
            _JS,
            "  </script>",
            "</body>",
            "</html>",
        ]
    )


def _case_payload(repo_root: Path, case_id: str, output_dir: Path) -> dict[str, Any]:
    lesson_path = PILOT_DIR / "objects" / f"{case_id}.lesson.json"
    graph_path = PILOT_DIR / "graphs" / f"{case_id}.graph.json"
    lesson = _load_json(repo_root / _repo_rel(lesson_path))
    graph = _load_json(repo_root / _repo_rel(graph_path))
    presentation = CASE_PRESENTATION[case_id]
    edge = graph["edges"][0]
    source_model = _node_by_id(graph, edge["source_node_id"])
    target_model = _node_by_id(graph, edge["target_node_id"])
    model_links = {item["label"]: item["href"] for item in lesson["model_links"]}
    relation_href = lesson["relation_links"][0]["href"]

    return {
        "case_id": case_id,
        "label": presentation["label"],
        "short_title": presentation["short_title"],
        "situation": presentation["situation"],
        "trap": presentation["trap"],
        "case_anchor": lesson["case_anchor"],
        "thinking_move": lesson["thinking_move"],
        "why_this_helps": _why_this_helps(lesson["relation_story"]),
        "relation_story": lesson["relation_story"],
        "relation": {
            "relation_id": edge["relation_id"],
            "label": edge["label"],
            "relation_type": edge["relation_type"],
            "confidence": edge.get("confidence", "missing"),
            "source_model_id": edge["source_node_id"],
            "source_model_label": source_model["label"],
            "target_model_id": edge["target_node_id"],
            "target_model_label": target_model["label"],
            "href": _relative_link(output_dir / "index.html", _repo_rel_from_link(relation_href)),
        },
        "model_stack": [
            {
                **model,
                "href": _relative_link(
                    output_dir / "index.html",
                    _repo_rel_from_link(model_links.get(model["teaching_name"], "")),
                ),
                "appears_in": [case_id],
            }
            for model in lesson["model_stack"]
        ],
        "practice_rep": lesson["practice_rep"],
        "do_not_overlearn": lesson["do_not_overlearn"],
        "human_review_status": lesson["human_review_status"],
        "product_proof": lesson["product_proof"],
        "runtime_integration_authorized": lesson["runtime_integration_authorized"],
        "missingness": lesson["missingness"],
        "non_claims": lesson["non_claims"],
        "source_refs": lesson["source_refs"],
        "links": {
            "lesson_page": _relative_link(
                output_dir / "index.html",
                f"docs/product/mental-model-teacher-three-case-product-pilot-v0/lessons/{case_id}.md",
            ),
            "lesson_object": _relative_link(
                output_dir / "index.html",
                f"docs/product/mental-model-teacher-three-case-product-pilot-v0/objects/{case_id}.lesson.json",
            ),
            "graph_object": _relative_link(
                output_dir / "index.html",
                f"docs/product/mental-model-teacher-three-case-product-pilot-v0/graphs/{case_id}.graph.json",
            ),
        },
        "graph": {
            "graph_id": graph["graph_id"],
            "default_focus": graph["default_focus"],
            "nodes": [
                {
                    **node,
                    "href": _relative_link(
                        output_dir / "index.html",
                        _repo_rel((graph_path.parent / node["href"]).resolve()),
                    ),
                }
                for node in graph["nodes"]
            ],
            "edges": [
                {
                    **edge_item,
                    "href": _relative_link(
                        output_dir / "index.html",
                        _repo_rel((graph_path.parent / edge_item["href"]).resolve()),
                    ),
                }
                for edge_item in graph["edges"]
            ],
            "missingness": graph["missingness"],
            "non_claims": graph["non_claims"],
        },
        "high_risk": case_id in HIGH_RISK_CASES,
    }


def _model_catalog(
    cases: list[dict[str, Any]],
    repo_root: Path,
    output_dir: Path,
) -> list[dict[str, Any]]:
    models: dict[str, dict[str, Any]] = {}
    for case in cases:
        for model in case["model_stack"]:
            entry = models.setdefault(
                model["model_id"],
                {
                    "model_id": model["model_id"],
                    "display_name": model["teaching_name"],
                    "summary": model["teaching_note"],
                    "boundary": model["boundary"],
                    "roles": [],
                    "appears_in": [],
                    "href": model["href"],
                },
            )
            if model["role"] not in entry["roles"]:
                entry["roles"].append(model["role"])
            if case["case_id"] not in entry["appears_in"]:
                entry["appears_in"].append(case["case_id"])
    for model in models.values():
        model["canonical"] = _canonical_model_detail(
            repo_root=repo_root,
            output_dir=output_dir,
            model_id=model["model_id"],
        )
        if model["canonical"]["source_href"]:
            model["href"] = model["canonical"]["source_href"]
    return sorted(models.values(), key=lambda item: item["display_name"].lower())


def _canonical_model_detail(
    repo_root: Path,
    output_dir: Path,
    model_id: str,
) -> dict[str, Any]:
    manifest_entry = _canonical_manifest(repo_root).get(model_id)
    curation = _load_json_optional(repo_root / "data/curation" / f"{model_id}.json")
    intervention = _load_json_optional(
        repo_root / "data/curation/intervention_semantics" / f"{model_id}.json"
    )
    relation_semantics = _load_json_optional(
        repo_root / "data/curation/relation_semantics" / f"{model_id}.json"
    )
    if not manifest_entry:
        return {
            "status": "missing_canonical_source",
            "source_path": "",
            "source_href": "",
            "source_hash": "",
            "source_bytes": 0,
            "overview": "",
            "sections": [],
            "curation": _curation_payload(curation),
            "intervention": _intervention_payload(intervention),
            "relation_semantics": _relation_semantics_payload(relation_semantics),
            "missingness": {
                "status": "partial",
                "missing_fields": ["canonical_markdown"],
            },
        }

    source_path = repo_root / manifest_entry["path"]
    source_text = source_path.read_text(encoding="utf-8")
    overview, sections = _canonical_sections(source_text)
    return {
        "status": "available",
        "source_path": manifest_entry["path"],
        "source_href": _relative_link(output_dir / "index.html", manifest_entry["path"]),
        "source_hash": manifest_entry.get("sha256", ""),
        "source_bytes": manifest_entry.get("bytes", 0),
        "overview": overview,
        "sections": sections,
        "curation": _curation_payload(curation),
        "intervention": _intervention_payload(intervention),
        "relation_semantics": _relation_semantics_payload(relation_semantics),
        "missingness": {
            "status": "complete_for_prototype",
            "missing_fields": [],
        },
    }


_MANIFEST_CACHE: dict[Path, dict[str, dict[str, Any]]] = {}


def _canonical_manifest(repo_root: Path) -> dict[str, dict[str, Any]]:
    manifest_path = repo_root / "data/model_sources/manifest.json"
    if manifest_path not in _MANIFEST_CACHE:
        payload = _load_json(manifest_path)
        _MANIFEST_CACHE[manifest_path] = {
            item["model_id"]: item for item in payload.get("files", [])
        }
    return _MANIFEST_CACHE[manifest_path]


def _canonical_sections(markdown: str) -> tuple[str, list[dict[str, str]]]:
    lines = markdown.splitlines()
    first_heading_index = len(lines)
    for index, line in enumerate(lines):
        if _looks_like_source_heading(line):
            first_heading_index = index
            break

    overview = _clean_source_block("\n".join(lines[:first_heading_index]))
    sections: list[dict[str, str]] = []
    current_title = ""
    current_body: list[str] = []
    for line in lines[first_heading_index:]:
        if _looks_like_source_heading(line):
            if current_title and current_body:
                sections.append(
                    {
                        "title": current_title,
                        "body": _trim_section(_clean_source_block("\n".join(current_body))),
                    }
                )
            current_title = _clean_heading(line)
            current_body = []
        else:
            current_body.append(line)
    if current_title and current_body:
        sections.append(
            {
                "title": current_title,
                "body": _trim_section(_clean_source_block("\n".join(current_body))),
            }
        )
    if not overview and sections:
        overview = sections[0]["body"]
    return _trim_section(overview, max_chars=1200), sections


def _looks_like_source_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 110:
        return False
    if stripped.startswith(("•", "-", "|", "◦", ">", "```")):
        return False
    if stripped.endswith(":"):
        return True
    if stripped.startswith("#"):
        return True
    return False


def _clean_heading(line: str) -> str:
    stripped = line.strip().strip("#").strip()
    return stripped[:-1] if stripped.endswith(":") else stripped


def _clean_source_block(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    return text


def _trim_section(text: str, *, max_chars: int = CANONICAL_SECTION_MAX_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _curation_payload(curation: dict[str, Any] | None) -> dict[str, Any]:
    if not curation:
        return {
            "status": "missing",
            "select_when": [],
            "avoid_when": [],
            "input_type": "",
            "output_type": "",
            "reasoning_types": [],
        }
    return {
        "status": "available",
        "select_when": curation.get("select_when", []),
        "avoid_when": curation.get("avoid_when", []),
        "input_type": curation.get("input_type", ""),
        "output_type": curation.get("output_type", ""),
        "reasoning_types": curation.get("reasoning_types", []),
    }


def _intervention_payload(intervention: dict[str, Any] | None) -> dict[str, Any]:
    if not intervention:
        return {
            "status": "missing",
            "failure_modes": [],
            "premortem_questions": [],
            "heuristics": [],
        }
    return {
        "status": "available",
        "failure_modes": [
            {
                "text": item.get("text", ""),
                "mitigation": item.get("mitigation", ""),
                "confidence": item.get("confidence", ""),
            }
            for item in intervention.get("failure_modes", [])
        ],
        "premortem_questions": [
            {
                "text": item.get("text", ""),
                "confidence": item.get("confidence", ""),
            }
            for item in intervention.get("premortem_questions", [])
        ],
        "heuristics": [
            {
                "text": item.get("text", ""),
                "confidence": item.get("confidence", ""),
            }
            for item in intervention.get("heuristics", [])
        ],
    }


def _relation_semantics_payload(
    relation_semantics: dict[str, Any] | None,
) -> dict[str, Any]:
    if not relation_semantics:
        return {
            "status": "missing",
            "allies": [],
            "antagonists": [],
            "structured_tensions": [],
        }
    return {
        "status": "available",
        "allies": _relation_semantic_items(relation_semantics.get("allies", [])),
        "antagonists": _relation_semantic_items(
            relation_semantics.get("antagonists", [])
        ),
        "structured_tensions": _relation_semantic_items(
            relation_semantics.get("structured_tensions", [])
        ),
    }


def _relation_semantic_items(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized = []
    for item in items[:5]:
        normalized.append(
            {
                "target_model_id": item.get("target_model_id", ""),
                "text": item.get("rationale_text")
                or item.get("tension_text")
                or item.get("source_quote", ""),
                "confidence": item.get("confidence", ""),
            }
        )
    return normalized


def _relation_catalog(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    relations: list[dict[str, Any]] = []
    for case in cases:
        relation = case["relation"]
        relations.append(
            {
                "relation_id": relation["relation_id"],
                "display_name": relation["label"],
                "relation_type": relation["relation_type"],
                "story": case["relation_story"],
                "source_model_id": relation["source_model_id"],
                "source_model_label": relation["source_model_label"],
                "target_model_id": relation["target_model_id"],
                "target_model_label": relation["target_model_label"],
                "confidence": relation["confidence"],
                "used_in": [case["case_id"]],
                "href": relation["href"],
            }
        )
    return relations


def _search_index(
    cases: list[dict[str, Any]],
    models: list[dict[str, Any]],
    relations: list[dict[str, Any]],
) -> list[dict[str, str]]:
    index: list[dict[str, str]] = []
    for case in cases:
        index.append(
            {
                "type": "lesson",
                "id": case["case_id"],
                "title": case["thinking_move"],
                "subtitle": case["short_title"],
                "mode": "learn",
                "case_id": case["case_id"],
            }
        )
        index.append(
            {
                "type": "practice",
                "id": f"{case['case_id']}:practice",
                "title": case["practice_rep"]["prompt"],
                "subtitle": case["practice_rep"]["user_action"],
                "mode": "learn",
                "case_id": case["case_id"],
            }
        )
    for model in models:
        index.append(
            {
                "type": "model",
                "id": model["model_id"],
                "title": model["display_name"],
                "subtitle": model["summary"],
                "mode": "models",
                "case_id": model["appears_in"][0],
            }
        )
    for relation in relations:
        index.append(
            {
                "type": "relation",
                "id": relation["relation_id"],
                "title": relation["display_name"],
                "subtitle": relation["story"],
                "mode": "relations",
                "case_id": relation["used_in"][0],
            }
        )
    return index


def _why_this_helps(relation_story: str) -> str:
    sentences = [part.strip() for part in relation_story.split(".") if part.strip()]
    if len(sentences) <= 2:
        return relation_story
    return ". ".join(sentences[:2]) + "."


def _node_by_id(graph: dict[str, Any], node_id: str) -> dict[str, Any]:
    for node in graph["nodes"]:
        if node["node_id"] == node_id:
            return node
    raise MentalModelTeacherLearnerExperienceError(f"missing graph node: {node_id}")


def _repo_rel_from_link(value: str) -> str:
    if not value:
        return ""
    if value.startswith(("http://", "https://", "#")):
        raise MentalModelTeacherLearnerExperienceError(
            "learner prototype expects local checked-in links"
        )
    return value


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise MentalModelTeacherLearnerExperienceError("JSON root must be an object")
    return payload


def _load_json_optional(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _load_json(path)


def _repo_rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise MentalModelTeacherLearnerExperienceError(
            "path must stay inside the repository"
        ) from exc


def _safe_display_path(path: Path) -> str:
    try:
        return _repo_rel(path)
    except MentalModelTeacherLearnerExperienceError:
        return path.name


def _relative_link(from_path: Path, repo_relative_path: str) -> str:
    if not repo_relative_path:
        return ""
    try:
        from_path.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        return repo_relative_path
    return os.path.relpath(REPO_ROOT / repo_relative_path, from_path.parent)


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


def _assert_no_local_paths(payload: Any) -> None:
    rendered = json.dumps(payload, sort_keys=True) if not isinstance(payload, str) else payload
    markers = (
        "/" + "Users/",
        "Desktop/" + "Apps",
        "\\" + "Users\\",
    )
    if any(marker in rendered for marker in markers):
        raise MentalModelTeacherLearnerExperienceError(
            "learner prototype contains a local path marker"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the learner-first Mental Model Teacher static prototype.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    manifest = build_learner_experience_prototype(args.root, args.output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


_CSS = r"""
:root {
  color-scheme: light;
  --bg: #f7f8f5;
  --surface: #ffffff;
  --surface-soft: #f0f5f6;
  --ink: #172025;
  --muted: #657078;
  --line: #d9e0df;
  --teal: #0f766e;
  --teal-soft: #ddf3ef;
  --blue: #315a96;
  --blue-soft: #e3edf9;
  --amber: #a8641f;
  --amber-soft: #fff1dd;
  --rose: #8a4960;
  --rose-soft: #f7e6ed;
  --green: #487448;
  --green-soft: #e6f2e4;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  background: var(--bg);
  color: var(--ink);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 14px;
  line-height: 1.45;
}

a {
  color: var(--blue);
  font-weight: 700;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

button,
input,
textarea {
  font: inherit;
}

button {
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--surface);
  color: var(--ink);
  cursor: pointer;
}

button:hover,
button.is-active {
  border-color: var(--teal);
  background: var(--teal-soft);
}

button:focus-visible,
a:focus-visible,
input:focus-visible,
textarea:focus-visible,
.node-button:focus-visible,
.edge-button:focus-visible {
  outline: 3px solid rgba(15, 118, 110, 0.22);
  outline-offset: 2px;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: grid;
  grid-template-columns: minmax(220px, 1fr) auto minmax(220px, 360px);
  gap: 14px;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(10px);
}

.brand h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0;
}

.brand p {
  margin: 2px 0 0;
  color: var(--muted);
  font-size: 12px;
}

.mode-tabs {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface-soft);
}

.mode-tabs button {
  min-height: 32px;
  padding: 0 10px;
  white-space: nowrap;
}

.search-box {
  position: relative;
}

.search-box input {
  width: 100%;
  min-height: 38px;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0 11px;
  background: #fbfcfd;
  color: var(--ink);
}

.search-results {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  max-height: 340px;
  overflow: auto;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
  box-shadow: 0 18px 34px rgba(31, 45, 49, 0.16);
  display: none;
}

.search-results.is-open {
  display: block;
}

.search-result {
  width: 100%;
  min-height: 64px;
  padding: 10px 12px;
  border: 0;
  border-bottom: 1px solid var(--line);
  border-radius: 0;
  text-align: left;
  background: var(--surface);
}

.result-type {
  display: inline-block;
  margin-right: 6px;
  color: var(--teal);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.result-title {
  font-weight: 780;
}

.result-subtitle {
  margin-top: 3px;
  color: var(--muted);
  font-size: 12px;
}

.shell-body {
  min-height: 0;
  display: grid;
  grid-template-columns: 250px minmax(0, 1fr);
}

.sidebar {
  border-right: 1px solid var(--line);
  background: var(--surface);
  padding: 14px;
}

.sidebar h2 {
  margin: 0 0 10px;
  font-size: 13px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0;
}

.case-list {
  display: grid;
  gap: 8px;
}

.case-button {
  width: 100%;
  min-height: 84px;
  padding: 10px;
  text-align: left;
}

.case-label {
  display: block;
  font-weight: 800;
}

.case-move {
  display: block;
  margin-top: 5px;
  color: var(--muted);
  font-size: 12px;
}

.main {
  min-width: 0;
  overflow: auto;
}

.mode-view {
  display: none;
}

.mode-view.is-active {
  display: block;
}

.learn-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 18px;
  padding: 18px;
}

.lesson-hero,
.panel,
.card {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
}

.lesson-hero {
  padding: 22px;
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--teal);
  font-size: 12px;
  font-weight: 850;
  text-transform: uppercase;
}

.lesson-hero h2 {
  max-width: 880px;
  margin: 0;
  font-size: 30px;
  line-height: 1.12;
  letter-spacing: 0;
}

.lesson-hero .situation {
  max-width: 820px;
  margin: 13px 0 0;
  color: var(--muted);
  font-size: 16px;
}

.story-steps {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.story-step {
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr);
  gap: 12px;
  align-items: start;
  padding: 13px 0;
  border-top: 1px solid var(--line);
}

.story-step h3 {
  margin: 0;
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0;
}

.story-step p {
  margin: 0;
}

.relation-strip {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  gap: 10px;
  align-items: center;
  margin-top: 16px;
  padding: 12px;
  border: 1px solid #b5ddd7;
  border-radius: 8px;
  background: var(--teal-soft);
}

.relation-node {
  min-width: 0;
  font-weight: 820;
}

.relation-type {
  padding: 5px 8px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--surface);
  color: var(--teal);
  font-size: 12px;
  font-weight: 850;
  white-space: nowrap;
}

.practice-box {
  margin-top: 18px;
  padding: 14px;
  border-radius: 8px;
  background: var(--amber-soft);
  border: 1px solid #efcaab;
}

.practice-box h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.practice-box p {
  margin: 0;
}

.context-column {
  display: grid;
  gap: 14px;
  align-content: start;
}

.panel-header {
  padding: 12px 14px;
  border-bottom: 1px solid var(--line);
  background: #fbfcfd;
}

.panel-header h3 {
  margin: 0;
  font-size: 15px;
}

.panel-body {
  padding: 14px;
}

.model-mini-list,
.object-grid,
.relation-list {
  display: grid;
  gap: 10px;
}

.model-mini {
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fbfcfd;
}

.model-mini h4,
.card h3 {
  margin: 0 0 5px;
  font-size: 15px;
}

.model-mini p,
.card p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}

.mode-page {
  padding: 18px;
}

.page-head {
  max-width: 900px;
  margin-bottom: 16px;
}

.page-head h2 {
  margin: 0 0 6px;
  font-size: 26px;
  letter-spacing: 0;
}

.page-head p {
  margin: 0;
  color: var(--muted);
}

.object-grid {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.model-layout {
  display: grid;
  grid-template-columns: minmax(250px, 0.38fr) minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.model-list {
  display: grid;
  gap: 10px;
}

.card {
  padding: 14px;
}

.card-button,
.model-link-button {
  width: 100%;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  text-align: left;
}

.card-button:hover,
.model-link-button:hover {
  background: transparent;
}

.model-link-button {
  color: var(--blue);
  font-weight: 800;
}

.model-detail {
  display: grid;
  gap: 14px;
}

.model-detail-hero {
  padding: 18px;
}

.model-detail-hero h3 {
  margin: 0 0 8px;
  font-size: 26px;
  letter-spacing: 0;
}

.model-section {
  padding: 14px;
}

.model-section h4 {
  margin: 0 0 10px;
  font-size: 16px;
}

.section-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}

.text-list {
  margin: 0;
  padding-left: 18px;
}

.text-list li + li {
  margin-top: 7px;
}

.source-block {
  display: grid;
  gap: 8px;
}

.source-block p {
  margin: 0;
}

.source-line {
  margin: 0 0 8px;
}

.canonical-sections {
  display: grid;
  gap: 10px;
}

.canonical-text {
  white-space: pre-wrap;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 10px 0 0;
}

.chip {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 7px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--surface-soft);
  color: var(--ink);
  font-size: 12px;
  font-weight: 750;
}

.map-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 16px;
}

.map-canvas {
  min-height: 440px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: linear-gradient(180deg, #fbfcfd, #eef3f4);
  overflow: hidden;
}

.map-svg {
  display: block;
  width: 100%;
  min-height: 440px;
}

.graph-edge {
  stroke: #66757f;
  stroke-width: 3;
}

.graph-edge.is-selected {
  stroke: var(--teal);
  stroke-width: 4;
}

.graph-node {
  fill: var(--surface);
  stroke: var(--blue);
  stroke-width: 2;
}

.graph-node.is-selected {
  fill: var(--teal-soft);
  stroke: var(--teal);
  stroke-width: 3;
}

.node-label {
  fill: var(--ink);
  font-size: 13px;
  font-weight: 760;
  pointer-events: none;
}

.node-button,
.edge-button {
  cursor: pointer;
}

.review-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 0.7fr);
  gap: 16px;
}

details {
  margin-top: 14px;
  border-top: 1px solid var(--line);
  padding-top: 12px;
}

summary {
  cursor: pointer;
  color: var(--blue);
  font-weight: 800;
}

.receipt-list,
.boundary-list {
  margin: 10px 0 0;
  padding-left: 18px;
}

.boundary-callout {
  margin-top: 14px;
  padding: 12px;
  border-left: 4px solid var(--amber);
  background: var(--amber-soft);
  color: #59402a;
}

.review-only {
  border-left: 4px solid var(--rose);
  background: var(--rose-soft);
}

@media (max-width: 980px) {
  .topbar,
  .shell-body,
  .learn-grid,
  .model-layout,
  .map-layout,
  .review-layout {
    grid-template-columns: 1fr;
  }

  .topbar {
    position: static;
  }

  .sidebar {
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .case-list {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }
}

@media (max-width: 640px) {
  .lesson-hero h2 {
    font-size: 24px;
  }

  .story-step,
  .relation-strip {
    grid-template-columns: 1fr;
  }
}
"""


_JS = r"""
const data = JSON.parse(document.getElementById("learner-data").textContent);
const state = {
  mode: data.default_mode,
  caseId: data.cases[0].case_id,
  selectedEdgeId: data.cases[0].graph.edges[0].edge_id,
  selectedModelId: data.models[0].model_id,
  query: "",
};

const app = document.getElementById("app");

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function currentCase() {
  return data.cases.find((item) => item.case_id === state.caseId) || data.cases[0];
}

function currentModel() {
  return data.models.find((item) => item.model_id === state.selectedModelId) || data.models[0];
}

function setMode(mode) {
  state.mode = mode;
  render();
}

function setCase(caseId) {
  state.caseId = caseId;
  const selected = currentCase();
  state.selectedEdgeId = selected.graph.edges[0].edge_id;
  render();
}

function openModel(modelId) {
  state.selectedModelId = modelId;
  state.mode = "models";
  render();
}

function openSearchResult(resultId) {
  const result = data.search_index.find((item) => item.id === resultId);
  if (!result) return;
  state.mode = result.mode;
  state.caseId = result.case_id;
  if (result.type === "model") {
    state.selectedModelId = result.id;
  }
  state.query = "";
  const search = document.getElementById("search");
  if (search) search.value = "";
  render();
}

function render() {
  const selected = currentCase();
  app.innerHTML = `
    <header class="topbar">
      <div class="brand">
        <h1>Mental Model Teacher</h1>
        <p>Case anchor -> reasoning move -> model relation -> practice rep</p>
      </div>
      <nav class="mode-tabs" aria-label="Product modes">
        ${data.modes.map((mode) => `
          <button type="button" class="${state.mode === mode.id ? "is-active" : ""}" onclick="setMode('${mode.id}')">${esc(mode.label)}</button>
        `).join("")}
      </nav>
      <div class="search-box">
        <input id="search" type="search" placeholder="Search lessons, models, relations, practice" value="${esc(state.query)}" oninput="onSearchInput(this.value)" autocomplete="off">
        <div id="search-results" class="search-results"></div>
      </div>
    </header>
    <div class="shell-body">
      <aside class="sidebar">
        <h2>Cases</h2>
        <div class="case-list">
          ${data.cases.map((item) => `
            <button type="button" class="case-button ${state.caseId === item.case_id ? "is-active" : ""}" onclick="setCase('${item.case_id}')">
              <span class="case-label">${esc(item.label)}</span>
              <span class="case-move">${esc(item.thinking_move)}</span>
            </button>
          `).join("")}
        </div>
      </aside>
      <main class="main">
        ${renderActiveMode(selected)}
      </main>
    </div>
  `;
  if (state.query) {
    onSearchInput(state.query);
  }
}

function onSearchInput(value) {
  state.query = value;
  const target = document.getElementById("search-results");
  if (!target) return;
  const query = value.trim().toLowerCase();
  if (!query) {
    target.className = "search-results";
    target.innerHTML = "";
    return;
  }
  const results = data.search_index
    .filter((item) => `${item.type} ${item.title} ${item.subtitle}`.toLowerCase().includes(query))
    .slice(0, 10);
  target.className = "search-results is-open";
  target.innerHTML = results.length
    ? results.map((item) => `
      <button type="button" class="search-result" onclick="openSearchResult('${esc(item.id)}')">
        <span class="result-type">${esc(item.type)}</span>
        <span class="result-title">${esc(item.title)}</span>
        <span class="result-subtitle">${esc(item.subtitle)}</span>
      </button>
    `).join("")
    : '<div class="search-result"><span class="result-title">No matching learner objects</span></div>';
}

function renderActiveMode(selected) {
  if (state.mode === "models") return renderModelsMode();
  if (state.mode === "relations") return renderRelationsMode();
  if (state.mode === "map") return renderMapMode(selected);
  if (state.mode === "review") return renderReviewMode(selected);
  return renderLearnMode(selected);
}

function renderLearnMode(selected) {
  return `
    <section class="mode-view is-active">
      <div class="learn-grid">
        <article class="lesson-hero">
          <p class="eyebrow">Learn the move</p>
          <h2>${esc(selected.thinking_move)}</h2>
          <p class="situation">${esc(selected.situation)}</p>
          <div class="story-steps">
            <div class="story-step">
              <h3>The trap</h3>
              <p>${esc(selected.trap)}</p>
            </div>
            <div class="story-step">
              <h3>The move</h3>
              <p>${esc(selected.thinking_move)}</p>
            </div>
            <div class="story-step">
              <h3>Why it helps</h3>
              <p>${esc(selected.why_this_helps)}</p>
            </div>
          </div>
          <div class="relation-strip" role="button" tabindex="0" onclick="setMode('relations')">
            <div class="relation-node">${esc(selected.relation.source_model_label)}</div>
            <div class="relation-type">${esc(selected.relation.relation_type)}</div>
            <div class="relation-node">${esc(selected.relation.target_model_label)}</div>
          </div>
          <div class="practice-box">
            <h3>Practice rep</h3>
            <p><strong>${esc(selected.practice_rep.prompt)}.</strong> ${esc(selected.practice_rep.user_action)}</p>
          </div>
          <div class="boundary-callout">
            ${esc(selected.do_not_overlearn[1] || selected.do_not_overlearn[0])}
          </div>
          ${renderReceipts(selected)}
        </article>
        <aside class="context-column">
          <section class="panel">
            <div class="panel-header"><h3>You are learning</h3></div>
            <div class="panel-body">
              <p><strong>${esc(selected.relation.label)}</strong></p>
              <p>${esc(selected.relation_story)}</p>
              <p><button type="button" onclick="setMode('map')">Open map</button> <button type="button" onclick="setMode('relations')">Open relation</button></p>
            </div>
          </section>
          <section class="panel">
            <div class="panel-header"><h3>Models in this lesson</h3></div>
            <div class="panel-body model-mini-list">
              ${selected.model_stack.map((model) => `
                <div class="model-mini">
                  <h4><button type="button" class="model-link-button" onclick="openModel('${esc(model.model_id)}')">${esc(model.teaching_name)}</button></h4>
                  <p>${esc(model.teaching_note)}</p>
                </div>
              `).join("")}
            </div>
          </section>
        </aside>
      </div>
    </section>
  `;
}

function renderModelsMode() {
  const selectedModel = currentModel();
  return `
    <section class="mode-page">
      <div class="page-head">
        <h2>Models</h2>
        <p>Reusable reasoning lenses. Click a model to open the formatted canonical page, sourced from model Markdown, curation, intervention semantics, and relation semantics.</p>
      </div>
      <div class="model-layout">
        <div class="model-list">
          ${data.models.map((model) => `
            <article class="card ${selectedModel.model_id === model.model_id ? "is-active" : ""}">
              <button type="button" class="card-button" onclick="openModel('${esc(model.model_id)}')">
                <h3>${esc(model.display_name)}</h3>
                <p>${esc(model.summary)}</p>
              </button>
              <div class="card-meta">
                ${model.roles.map((role) => `<span class="chip">${esc(role)}</span>`).join("")}
                ${model.appears_in.map((caseId) => `<button type="button" class="chip" onclick="setCase('${caseId}'); setMode('learn')">Appears in ${esc(caseLabel(caseId))}</button>`).join("")}
              </div>
            </article>
          `).join("")}
        </div>
        ${renderModelDetail(selectedModel)}
      </div>
    </section>
  `;
}

function renderModelDetail(model) {
  const canonical = model.canonical;
  return `
    <article class="model-detail">
      <section class="panel model-detail-hero">
        <p class="eyebrow">Mental model</p>
        <h3>${esc(model.display_name)}</h3>
        <p>${esc(model.summary)}</p>
        <div class="boundary-callout">${esc(model.boundary)}</div>
        <div class="card-meta">
          ${model.roles.map((role) => `<span class="chip">${esc(role)}</span>`).join("")}
          <span class="chip">canonical: ${esc(canonical.status)}</span>
          ${canonical.curation.reasoning_types.map((item) => `<span class="chip">${esc(item)}</span>`).join("")}
        </div>
      </section>
      <section class="panel model-section">
        <h4>Canonical overview</h4>
        <div class="source-block">${renderTextBlock(canonical.overview)}</div>
      </section>
      <section class="section-grid">
        <div class="panel model-section">
          <h4>Use when</h4>
          ${renderTextList(canonical.curation.select_when)}
        </div>
        <div class="panel model-section">
          <h4>Be careful when</h4>
          ${renderTextList(canonical.curation.avoid_when)}
        </div>
      </section>
      <section class="section-grid">
        <div class="panel model-section">
          <h4>Failure modes</h4>
          ${renderFailureModes(canonical.intervention.failure_modes)}
        </div>
        <div class="panel model-section">
          <h4>Premortem questions</h4>
          ${renderTextList(canonical.intervention.premortem_questions.map((item) => item.text))}
        </div>
      </section>
      <section class="panel model-section">
        <h4>Heuristics</h4>
        ${renderTextList(canonical.intervention.heuristics.map((item) => item.text))}
      </section>
      <section class="section-grid">
        <div class="panel model-section">
          <h4>Appears in lessons</h4>
          <div class="card-meta">
            ${model.appears_in.map((caseId) => `<button type="button" class="chip" onclick="setCase('${caseId}'); setMode('learn')">${esc(caseLabel(caseId))}</button>`).join("")}
          </div>
        </div>
        <div class="panel model-section">
          <h4>Connected relations</h4>
          ${renderModelRelations(model)}
        </div>
      </section>
      <section class="panel model-section">
        <h4>Canonical source sections</h4>
        <div class="canonical-sections">
          ${canonical.sections.map((section) => `
            <details>
              <summary>${esc(section.title)}</summary>
              <div class="canonical-text">${renderTextBlock(section.body)}</div>
            </details>
          `).join("")}
        </div>
      </section>
      <section class="panel model-section">
        <h4>Receipts</h4>
        <ul class="receipt-list">
          <li>Canonical source: <a href="${esc(canonical.source_href)}">${esc(canonical.source_path)}</a></li>
          <li>Source hash: <code>${esc(canonical.source_hash)}</code></li>
          <li>Activation curation: ${esc(canonical.curation.status)}</li>
          <li>Intervention semantics: ${esc(canonical.intervention.status)}</li>
          <li>Relation semantics: ${esc(canonical.relation_semantics.status)}</li>
        </ul>
      </section>
    </article>
  `;
}

function renderFailureModes(items) {
  if (!items.length) return '<p class="muted">No source-backed failure modes are present.</p>';
  return `
    <ul class="text-list">
      ${items.map((item) => `
        <li>
          ${esc(item.text)}
          ${item.mitigation ? `<br><span class="muted">Mitigation: ${esc(item.mitigation)}</span>` : ""}
        </li>
      `).join("")}
    </ul>
  `;
}

function renderModelRelations(model) {
  const relations = data.relations.filter((relation) =>
    relation.source_model_id === model.model_id || relation.target_model_id === model.model_id
  );
  const semantic = model.canonical.relation_semantics;
  return `
    ${relations.length ? relations.map((relation) => `
      <p class="source-line"><button type="button" class="model-link-button" onclick="setCase('${relation.used_in[0]}'); setMode('relations')">${esc(relation.display_name)}</button></p>
    `).join("") : '<p class="muted">No pilot relation page uses this model yet.</p>'}
    <details>
      <summary>Canonical relation semantics</summary>
      <h4>Allies</h4>
      ${renderSemanticList(semantic.allies)}
      <h4>Antagonists</h4>
      ${renderSemanticList(semantic.antagonists)}
      <h4>Structured tensions</h4>
      ${renderSemanticList(semantic.structured_tensions)}
    </details>
  `;
}

function renderSemanticList(items) {
  if (!items.length) return '<p class="muted">No source-backed entries in this category.</p>';
  return `
    <ul class="text-list">
      ${items.map((item) => `<li><strong>${esc(item.target_model_id)}</strong>: ${esc(item.text)}</li>`).join("")}
    </ul>
  `;
}

function renderTextList(items) {
  const cleanItems = items.filter(Boolean);
  if (!cleanItems.length) return '<p class="muted">No source-backed entries are present.</p>';
  return `<ul class="text-list">${cleanItems.map((item) => `<li>${esc(item)}</li>`).join("")}</ul>`;
}

function renderTextBlock(text) {
  if (!text) return '<p class="muted">No canonical text is present for this section.</p>';
  const paragraphs = String(text)
    .split(/\n{2,}/)
    .map((part) => part.trim())
    .filter(Boolean);
  return paragraphs.map((part) => `<p>${esc(part)}</p>`).join("");
}

function renderRelationsMode() {
  return `
    <section class="mode-page">
      <div class="page-head">
        <h2>Relations</h2>
        <p>Model pairs are first-class teaching objects. The relation story comes before the taxonomy label.</p>
      </div>
      <div class="relation-list">
        ${data.relations.map((relation) => `
          <article class="card">
            <h3><a href="${esc(relation.href)}">${esc(relation.display_name)}</a></h3>
            <p>${esc(relation.story)}</p>
            <div class="card-meta">
              <span class="chip">${esc(relation.relation_type)}</span>
              <span class="chip">confidence: ${esc(relation.confidence)}</span>
              ${relation.used_in.map((caseId) => `<button type="button" class="chip" onclick="setCase('${caseId}'); setMode('learn')">Used in ${esc(caseLabel(caseId))}</button>`).join("")}
              <button type="button" class="chip" onclick="setCase('${relation.used_in[0]}'); setMode('map')">Open in map</button>
            </div>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderMapMode(selected) {
  const edge = selected.graph.edges[0];
  const relation = selected.relation;
  return `
    <section class="mode-page">
      <div class="page-head">
        <h2>Map</h2>
        <p>A focused lesson neighborhood. Nodes are models; the selected edge opens as a relation, not proof.</p>
      </div>
      <div class="map-layout">
        <div class="map-canvas">
          ${renderGraphSvg(selected)}
        </div>
        <aside class="panel">
          <div class="panel-header"><h3>Selected relation</h3></div>
          <div class="panel-body">
            <p><strong>${esc(edge.label)}</strong></p>
            <p>${esc(selected.relation_story)}</p>
            <p><span class="chip">${esc(edge.relation_type)}</span> <span class="chip">edge is navigation</span></p>
            <p><a href="${esc(relation.href)}">Open relation page</a></p>
            <details>
              <summary>Graph boundary</summary>
              <ul class="boundary-list">
                ${selected.graph.non_claims.map((item) => `<li>${esc(item)}</li>`).join("")}
              </ul>
            </details>
          </div>
        </aside>
      </div>
    </section>
  `;
}

function renderGraphSvg(selected) {
  const nodes = selected.graph.nodes;
  const edge = selected.graph.edges[0];
  const positions = [
    { x: 160, y: 110 },
    { x: 420, y: 250 },
    { x: 680, y: 110 },
  ];
  const positionById = {};
  nodes.forEach((node, index) => {
    positionById[node.node_id] = positions[index] || { x: 160 + index * 180, y: 180 };
  });
  const source = positionById[edge.source_node_id];
  const target = positionById[edge.target_node_id];
  return `
    <svg class="map-svg" viewBox="0 0 840 440" role="img" aria-label="Focused lesson graph">
      <line class="graph-edge is-selected edge-button" x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}" onclick="setMode('relations')" />
      <text x="${(source.x + target.x) / 2 - 46}" y="${(source.y + target.y) / 2 - 10}" class="node-label">${esc(edge.relation_type)}</text>
      ${nodes.map((node) => {
        const pos = positionById[node.node_id];
        return `
          <g class="node-button" onclick="openModel('${esc(node.node_id)}')">
            <circle class="graph-node ${node.node_id === selected.graph.default_focus ? "is-selected" : ""}" cx="${pos.x}" cy="${pos.y}" r="52" />
            <text class="node-label" x="${pos.x - 70}" y="${pos.y + 76}">${esc(node.label)}</text>
          </g>
        `;
      }).join("")}
    </svg>
  `;
}

function renderReviewMode(selected) {
  return `
    <section class="mode-page">
      <div class="page-head">
        <h2>Review mode</h2>
        <p>This mode is for source fidelity, missingness, and boundary checks. It is deliberately separate from Learn mode.</p>
      </div>
      <div class="review-layout">
        <article class="panel">
          <div class="panel-header"><h3>Product object under review</h3></div>
          <div class="panel-body">
            <p><strong>${esc(selected.thinking_move)}</strong></p>
            <p>${esc(selected.case_anchor)}</p>
            <div class="review-only boundary-callout">Human review status: ${esc(selected.human_review_status)}. Product proof: false. Runtime integration: false.</div>
            <details open>
              <summary>Missingness</summary>
              <ul class="receipt-list">
                ${selected.missingness.missing_fields.map((item) => `<li>${esc(item)}</li>`).join("")}
              </ul>
            </details>
          </div>
        </article>
        <aside class="panel">
          <div class="panel-header"><h3>Receipts</h3></div>
          <div class="panel-body">
            <ul class="receipt-list">
              ${selected.source_refs.map((ref) => `<li><code>${esc(ref.source_type)}</code>: ${esc(ref.path)}</li>`).join("")}
            </ul>
            <p><a href="${esc(selected.links.lesson_page)}">Rendered lesson page</a></p>
            <p><a href="${esc(selected.links.lesson_object)}">Lesson JSON</a></p>
            <p><a href="${esc(selected.links.graph_object)}">Graph JSON</a></p>
          </div>
        </aside>
      </div>
    </section>
  `;
}

function renderReceipts(selected) {
  return `
    <details>
      <summary>Receipts and boundaries</summary>
      <ul class="receipt-list">
        <li>Human review: ${esc(selected.human_review_status)}</li>
        <li>Product proof: false</li>
        <li>Runtime integration authorized: false</li>
        <li>Missingness: ${esc(selected.missingness.status)}</li>
      </ul>
      <ul class="boundary-list">
        ${selected.non_claims.map((item) => `<li>${esc(item)}</li>`).join("")}
      </ul>
    </details>
  `;
}

function caseLabel(caseId) {
  const item = data.cases.find((candidate) => candidate.case_id === caseId);
  return item ? item.label : caseId;
}

window.setMode = setMode;
window.setCase = setCase;
window.openModel = openModel;
window.onSearchInput = onSearchInput;
window.openSearchResult = openSearchResult;

render();
"""


if __name__ == "__main__":
    raise SystemExit(main())
