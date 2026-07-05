"""Pilot product-page data builder for Mental Model Teacher.

The builder reads existing checked-in substrate and emits a small, product-safe
JSON package for validation. It does not render pages, build graph UI, call
providers, use embeddings, or wire runtime behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .mental_model_teacher_product_contracts import (
    COMMON_NON_CLAIMS,
    MENTAL_MODEL_PAGE_SCHEMA_VERSION,
    RELATION_NON_CLAIMS,
    RELATION_PAGE_SCHEMA_VERSION,
    validate_mental_model_page,
    validate_relation_page,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_IDS = (
    "base-rates",
    "system-2",
    "scientific-method-evidence-testing",
)
PILOT_SCHEMA_VERSION = "lolla.mental_model_teacher.pilot_page_data.v0"


class MentalModelTeacherPilotBuilderError(ValueError):
    """Raised when pilot page data cannot be built safely."""


def build_pilot_page_data(
    root: Path | str | None = None,
    *,
    model_ids: tuple[str, ...] = DEFAULT_MODEL_IDS,
) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else REPO_ROOT
    manifest = _load_manifest(repo_root)
    model_pages = [
        _build_model_page(repo_root, model_id, manifest) for model_id in model_ids
    ]
    relation_pages = _build_relation_pages(repo_root, model_ids)

    package = {
        "schema_version": PILOT_SCHEMA_VERSION,
        "builder": "engine.system_b.mental_model_teacher_pilot_page_builder",
        "builder_mode": "deterministic_offline",
        "source_policy_ref": "docs/product/mental-model-teacher-substrate-exposure-contract-v0.json",
        "contract_refs": {
            "mental_model_page": MENTAL_MODEL_PAGE_SCHEMA_VERSION,
            "relation_page": RELATION_PAGE_SCHEMA_VERSION,
        },
        "pilot_scope": {
            "model_ids": list(model_ids),
            "selection_reason": (
                "Well-covered source, activation, intervention, and relation "
                "semantics; no Teacher case artifact is claimed."
            ),
        },
        "model_pages": model_pages,
        "relation_pages": relation_pages,
        "build_review": _build_review(model_pages, relation_pages),
        "non_claims": {
            "product_proof": False,
            "human_validated": False,
            "answer_correctness": False,
            "advice_correctness": False,
            "runtime_integration_authorized": False,
            "graph_edges_are_proof": False,
            "embedding_similarity_is_validated_relation_semantics": False,
        },
    }
    _assert_no_local_paths(package)
    return package


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a small Mental Model Teacher pilot page-data package.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--models",
        nargs="+",
        default=list(DEFAULT_MODEL_IDS),
        help="Pilot model ids. Defaults to the PR-P4 base-rates/System-2/scientific-method subset.",
    )
    args = parser.parse_args(argv)

    package = build_pilot_page_data(args.root, model_ids=tuple(args.models))
    rendered = json.dumps(package, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


def _build_model_page(
    root: Path,
    model_id: str,
    manifest: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    manifest_record = manifest.get(model_id)
    if not manifest_record:
        raise MentalModelTeacherPilotBuilderError(f"missing manifest record for {model_id}")

    curation_path = root / "data/curation" / f"{model_id}.json"
    intervention_path = root / "data/curation/intervention_semantics" / f"{model_id}.json"
    curation = _read_json_object(curation_path)
    intervention = _read_json_object(intervention_path)

    source_path = _safe_relative_path(manifest_record.get("path"))
    display_name = _display_name_from_source(manifest_record.get("filename"), model_id)
    select_when = _string_list(curation.get("select_when"))
    avoid_when = _string_list(curation.get("avoid_when"))
    input_type = _text(curation.get("input_type"))
    output_type = _text(curation.get("output_type"))
    failure_modes = _item_texts(intervention.get("failure_modes"))
    premortem_questions = _item_texts(intervention.get("premortem_questions"))
    heuristics = _item_texts(intervention.get("heuristics"))

    missing_fields: list[str] = []
    practice_prompts: list[str] = []
    common_misuse: list[str] = []
    if not common_misuse:
        missing_fields.append("common_misuse")
    if not practice_prompts:
        missing_fields.append("practice_prompts")

    page = {
        "schema_version": MENTAL_MODEL_PAGE_SCHEMA_VERSION,
        "model_id": model_id,
        "slug": model_id,
        "display_name": display_name,
        "one_sentence_meaning": _one_sentence_meaning(
            display_name,
            input_type=input_type,
            output_type=output_type,
        ),
        "helps_notice": select_when[:3],
        "use_when": select_when,
        "avoid_when": avoid_when,
        "common_misuse": common_misuse,
        "failure_modes": failure_modes,
        "premortem_questions": premortem_questions,
        "heuristics": heuristics,
        "practice_prompts": practice_prompts,
        "reasoning_types": _string_list(curation.get("reasoning_types")),
        "source_refs": [
            {
                "source_id": f"{model_id}-canonical-markdown",
                "path": source_path,
                "source_type": "canonical_markdown",
            },
            {
                "source_id": f"{model_id}-activation-curation",
                "path": _rel(curation_path, root),
                "source_type": "activation_curation",
            },
            {
                "source_id": f"{model_id}-intervention-semantics",
                "path": _rel(intervention_path, root),
                "source_type": "intervention_semantics",
            },
        ],
        "source_hashes": {
            source_path: _text(manifest_record.get("sha256")),
        },
        "curation_status": "draft",
        "missingness": {
            "status": "partial" if missing_fields else "complete",
            "missing_fields": missing_fields,
            "notes": [
                "Generated deterministically from existing source, activation curation, and intervention semantics.",
                "Empty product fields mean no source-backed field exists in PR-P4, not that the concept is absent.",
            ],
        },
        "non_claims": sorted(COMMON_NON_CLAIMS),
    }
    return validate_mental_model_page(page)


def _build_relation_pages(root: Path, model_ids: tuple[str, ...]) -> list[dict[str, Any]]:
    model_id_set = set(model_ids)
    pages: list[dict[str, Any]] = []
    for source_model_id in model_ids:
        relation_path = root / "data/curation/relation_semantics" / f"{source_model_id}.json"
        relation_doc = _read_json_object(relation_path)
        for relation_type, key in (
            ("ally", "allies"),
            ("antagonist", "antagonists"),
            ("tension", "structured_tensions"),
        ):
            for index, item in enumerate(_object_list(relation_doc.get(key))):
                target_model_id = _text(item.get("target_model_id"))
                if target_model_id not in model_id_set or target_model_id == source_model_id:
                    continue
                page = _build_relation_page(
                    root=root,
                    source_model_id=source_model_id,
                    relation_type=relation_type,
                    item=item,
                    relation_path=relation_path,
                    source_key=key,
                    source_index=index,
                )
                pages.append(validate_relation_page(page))
    return sorted(pages, key=lambda page: page["relation_id"])


def _build_relation_page(
    *,
    root: Path,
    source_model_id: str,
    relation_type: str,
    item: dict[str, Any],
    relation_path: Path,
    source_key: str,
    source_index: int,
) -> dict[str, Any]:
    target_model_id = _text(item.get("target_model_id"))
    relation_id = f"{source_model_id}__{relation_type}__{target_model_id}"
    story = _relation_story(item)
    missing_fields = [
        "source_specific_misread_risk",
        "source_specific_practice_prompt",
    ]
    page = {
        "schema_version": RELATION_PAGE_SCHEMA_VERSION,
        "relation_id": relation_id,
        "source_model_id": source_model_id,
        "target_model_id": target_model_id,
        "relation_type": relation_type,
        "plain_language_story": story,
        "why_it_matters": story,
        "misread_risk": (
            "No source-specific misread risk is present in PR-P4; treat this "
            "relation as a teaching aid, not proof that the models always move together."
        ),
        "practice_prompt": (
            "No source-specific relation practice prompt is present in PR-P4; "
            "use the relation page to ask what distinction the edge is teaching."
        ),
        "source_quote_or_ref": _text(item.get("source_quote"))
        or f"{_rel(relation_path, root)}:{source_key}[{source_index}]",
        "confidence": _confidence(item.get("confidence")),
        "curation_status": "draft",
        "missingness": {
            "status": "partial",
            "missing_fields": missing_fields,
            "notes": [
                "Relation story and confidence come from relation semantics.",
                "Misread risk and practice prompt are visible generic missingness boundaries until source-specific fields exist.",
            ],
        },
        "non_claims": sorted(RELATION_NON_CLAIMS),
    }
    return page


def _build_review(
    model_pages: list[dict[str, Any]],
    relation_pages: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "model_page_count": len(model_pages),
        "relation_page_count": len(relation_pages),
        "model_ids": [page["model_id"] for page in model_pages],
        "relation_ids": [page["relation_id"] for page in relation_pages],
        "missingness_summary": {
            page["model_id"]: page["missingness"]["missing_fields"]
            for page in model_pages
        },
        "relation_missingness_summary": {
            page["relation_id"]: page["missingness"]["missing_fields"]
            for page in relation_pages
        },
        "checked_in_teacher_artifacts_used": False,
        "embeddings_used": False,
        "runtime_integration_authorized": False,
        "product_proof": False,
    }


def _load_manifest(root: Path) -> dict[str, dict[str, Any]]:
    manifest = _read_json_object(root / "data/model_sources/manifest.json")
    files = manifest.get("files")
    if not isinstance(files, list):
        raise MentalModelTeacherPilotBuilderError("manifest files must be a list")
    records: dict[str, dict[str, Any]] = {}
    for item in files:
        if isinstance(item, dict) and isinstance(item.get("model_id"), str):
            records[item["model_id"]] = item
    return records


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MentalModelTeacherPilotBuilderError(
            f"required source file missing: {_rel(path, REPO_ROOT)}"
        ) from exc
    if not isinstance(payload, dict):
        raise MentalModelTeacherPilotBuilderError(
            f"required source file is not an object: {_rel(path, REPO_ROOT)}"
        )
    return payload


def _display_name_from_source(filename: Any, fallback: str) -> str:
    raw = _text(filename) or fallback
    stem = raw.removesuffix(".md").removesuffix("_rag")
    return stem.replace("_", " ").replace("-", " ").title()


def _one_sentence_meaning(
    display_name: str,
    *,
    input_type: str,
    output_type: str,
) -> str:
    if input_type and output_type:
        return f"{display_name} helps turn {input_type} into {output_type}."
    if input_type:
        return f"{display_name} helps examine {input_type}."
    if output_type:
        return f"{display_name} helps produce {output_type}."
    return f"{display_name} has no source-backed one-sentence meaning in PR-P4."


def _relation_story(item: dict[str, Any]) -> str:
    for key in ("rationale_text", "tension_text", "source_quote"):
        value = _text(item.get(key))
        if value:
            return value
    raise MentalModelTeacherPilotBuilderError("relation item lacks story text")


def _confidence(value: Any) -> str:
    text = _text(value).lower()
    return text if text in {"unknown", "low", "medium", "high"} else "unknown"


def _item_texts(value: Any) -> list[str]:
    texts: list[str] = []
    for item in _object_list(value):
        text = _text(item.get("text"))
        if text:
            texts.append(text)
    return texts


def _object_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _safe_relative_path(value: Any) -> str:
    text = _text(value)
    if not text or text.startswith("/"):
        raise MentalModelTeacherPilotBuilderError("source path must be repo-relative")
    return text


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _assert_no_local_paths(payload: Any) -> None:
    rendered = json.dumps(payload, sort_keys=True)
    markers = (
        "/" + "Users/",
        "Desktop/" + "Apps",
        "\\" + "Users\\",
    )
    if any(marker in rendered for marker in markers):
        raise MentalModelTeacherPilotBuilderError(
            "pilot page data contains a local path marker"
        )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
