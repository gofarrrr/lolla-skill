"""Deterministic substrate inventory for the Mental Model Teacher product lane.

This module reads the PR-P2 exposure policy and reports only safe metadata:
presence, counts, coarse JSON shapes, and missingness. It does not build product
page contracts, render pages, call providers, or wire runtime behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_PATH = (
    REPO_ROOT / "docs/product/mental-model-teacher-substrate-exposure-contract-v0.json"
)

ALLOWED_CLASSIFICATIONS = {
    "product-safe",
    "product-safe-after-translation",
    "internal-only",
    "future/suggestion-only",
}

LOCAL_PATH_MARKERS = (
    "/" + "Users/",
    "Desktop/" + "Apps",
    "\\" + "Users\\",
)

TEACHER_ARTIFACT_DIRS = (
    "data/teacher",
    "data/teacher_artifacts",
    "docs/teacher",
    "reviews/teacher",
    "build/teacher",
)


class SubstrateInventoryError(ValueError):
    """Raised when the exposure policy is malformed."""


def build_inventory(
    root: Path | str | None = None,
    policy_path: Path | str | None = None,
) -> dict[str, Any]:
    """Return a deterministic, product-safe inventory summary.

    The returned object intentionally avoids raw source bodies, raw vectors,
    local absolute paths, provider/model text, and page-rendering contracts.
    """

    repo_root = Path(root) if root is not None else REPO_ROOT
    policy_file = Path(policy_path) if policy_path is not None else DEFAULT_POLICY_PATH
    policy = _read_json(policy_file)
    _validate_policy(policy)

    inventory_assets = []
    for asset in policy["assets"]:
        discovered = _discover_asset(asset["asset_id"], repo_root)
        inventory_assets.append(
            {
                "asset_id": asset["asset_id"],
                "display_name": asset["display_name"],
                "asset_ref": asset["asset_ref"],
                "required": asset["required"],
                "classification": asset["classification"],
                "powers_surfaces": asset["powers_surfaces"],
                "product_safe_use": asset["product_safe_use"],
                "translation_rule": asset["translation_rule"],
                "do_not_expose": asset["do_not_expose"],
                "discovered": discovered,
            }
        )

    missing_required = [
        asset["asset_id"]
        for asset in inventory_assets
        if asset["required"] and asset["discovered"]["status"] != "present"
    ]
    missing_optional = [
        asset["asset_id"]
        for asset in inventory_assets
        if not asset["required"] and asset["discovered"]["status"] != "present"
    ]

    classification_counts = {
        classification: sum(
            1 for asset in inventory_assets if asset["classification"] == classification
        )
        for classification in sorted(ALLOWED_CLASSIFICATIONS)
    }

    return {
        "schema": "lolla.mental_model_teacher.substrate_inventory_summary.v0",
        "generated_by": "engine.system_b.mental_model_teacher_substrate_inventory",
        "policy_schema": policy["schema"],
        "product_lane": policy["product_lane"],
        "decision_gate": policy["decision_gate"],
        "asset_count": len(inventory_assets),
        "classification_counts": classification_counts,
        "missing_required_asset_ids": missing_required,
        "missing_optional_asset_ids": missing_optional,
        "non_claims": policy["non_claims"],
        "assets": inventory_assets,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Summarize Mental Model Teacher substrate exposure inventory.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY_PATH)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    summary = build_inventory(root=args.root, policy_path=args.policy)
    rendered = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


def _validate_policy(policy: dict[str, Any]) -> None:
    if policy.get("schema") != "lolla.mental_model_teacher.substrate_exposure_policy.v0":
        raise SubstrateInventoryError("unexpected policy schema")

    assets = policy.get("assets")
    if not isinstance(assets, list) or not assets:
        raise SubstrateInventoryError("policy assets must be a non-empty list")

    seen: set[str] = set()
    for asset in assets:
        if not isinstance(asset, dict):
            raise SubstrateInventoryError("each policy asset must be an object")
        asset_id = _required_string(asset, "asset_id")
        if asset_id in seen:
            raise SubstrateInventoryError(f"duplicate asset_id: {asset_id}")
        seen.add(asset_id)
        classification = _required_string(asset, "classification")
        if classification not in ALLOWED_CLASSIFICATIONS:
            raise SubstrateInventoryError(
                f"unsupported classification for {asset_id}: {classification}"
            )
        for key in (
            "display_name",
            "asset_ref",
            "product_safe_use",
            "translation_rule",
        ):
            _required_string(asset, key)
        if not isinstance(asset.get("required"), bool):
            raise SubstrateInventoryError(f"{asset_id}.required must be a boolean")
        for key in ("powers_surfaces", "do_not_expose"):
            value = asset.get(key)
            if not isinstance(value, list) or not all(
                isinstance(item, str) for item in value
            ):
                raise SubstrateInventoryError(f"{asset_id}.{key} must be string list")


def _required_string(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SubstrateInventoryError(f"missing required string: {key}")
    return value


def _discover_asset(asset_id: str, root: Path) -> dict[str, Any]:
    if asset_id == "canonical_model_markdown":
        files = _glob(root, "data/model_sources/*.md")
        return _present_counts(files, {"markdown_files": len(files)})

    if asset_id in {"model_source_manifest", "model_source_hashes"}:
        path = root / "data/model_sources/manifest.json"
        if not path.exists():
            return _missing(path)
        data = _read_json(path)
        files = data.get("files", [])
        if not isinstance(files, list):
            files = []
        return {
            "status": "present",
            "relative_path": _rel(path, root),
            "counts": {
                "manifest_files": len(files),
            },
            "hash_algorithm": str(data.get("hash_algorithm", "")),
            "raw_contains_local_path_marker": _contains_local_path_marker(data),
        }

    if asset_id == "activation_curation":
        files = _glob(root, "data/curation/*.json")
        return _present_counts(files, {"direct_json_files": len(files)})

    if asset_id == "intervention_semantics":
        files = _glob(root, "data/curation/intervention_semantics/*.json")
        return _present_counts(files, {"json_files": len(files)})

    if asset_id == "relation_semantics":
        files = _glob(root, "data/curation/relation_semantics/*.json")
        return _present_counts(files, {"json_files": len(files)})

    if asset_id == "knowledge_graph":
        path = root / "data/knowledge_graph.json"
        if not path.exists():
            return _missing(path)
        data = _read_json(path)
        return {
            "status": "present",
            "relative_path": _rel(path, root),
            "counts": {
                "models": _len_mapping(data.get("models")),
                "tendencies": _len_mapping(data.get("tendencies")),
                "edges": _len_sequence(data.get("edges")),
                "prerequisite_edges": _len_sequence(data.get("prerequisite_edges")),
            },
            "top_level_keys": sorted(str(key) for key in data.keys()),
        }

    if asset_id == "relationship_graph":
        path = root / "data/relationship_graph.json"
        if not path.exists():
            return _missing(path)
        data = _read_json(path)
        edges = data if isinstance(data, list) else data.get("edges", [])
        edge_types = sorted(
            {
                str(edge.get("edge_type", "")).strip()
                for edge in edges
                if isinstance(edge, dict) and edge.get("edge_type")
            }
        )
        curated_edges = sum(
            1 for edge in edges if isinstance(edge, dict) and edge.get("curated") is True
        )
        return {
            "status": "present",
            "relative_path": _rel(path, root),
            "counts": {
                "edges": len(edges) if isinstance(edges, list) else 0,
                "curated_edges": curated_edges,
            },
            "edge_types": edge_types,
        }

    if asset_id == "embeddings_db":
        path = root / "data/embeddings.db"
        if not path.exists():
            return _missing(path)
        return {
            "status": "present",
            "relative_path": _rel(path, root),
            "counts": {
                "bytes": path.stat().st_size,
            },
        }

    if asset_id == "curated_chunks":
        files = _glob(root, "data/curated/*.json")
        return _present_counts(
            files,
            {"json_files": len(files)},
            names=[path.name for path in files],
        )

    if asset_id == "family_semantics":
        files = _glob(root, "data/family_semantics/*.json")
        return _present_counts(files, {"json_files": len(files)})

    if asset_id == "v60_model_affordances":
        path = root / "data/compiled/model_affordances/affordances_v60.json"
        if not path.exists():
            return _missing(path)
        data = _read_json(path)
        return {
            "status": "present",
            "relative_path": _rel(path, root),
            "counts": {
                "model_records": _len_sequence(data.get("model_records")),
                "affordances": _len_sequence(data.get("affordances")),
                "absence_records": _len_sequence(data.get("absence_records")),
            },
            "status_field": str(data.get("status", "")),
        }

    if asset_id == "relation_graph_code":
        return _file_presence(root, "engine/system_b/relation_graph.py")

    if asset_id == "activation_matcher_code":
        return _file_presence(root, "engine/system_b/activation_matcher.py")

    if asset_id == "model_affordance_validation_code":
        return _file_presence(root, "engine/system_b/model_affordance_validation.py")

    if asset_id == "graph_survival_eval_artifacts":
        code = root / "engine/system_b/graph_survival_report.py"
        test = root / "tests/test_graph_survival_report.py"
        eval_files = _glob(root, "data/evaluations/**/*.json")
        status = "present" if code.exists() and test.exists() else "missing"
        return {
            "status": status,
            "relative_paths": [
                _rel(path, root) for path in (code, test) if path.exists()
            ],
            "counts": {
                "evaluation_json_files": len(eval_files),
                "required_code_files_present": int(code.exists()) + int(test.exists()),
            },
        }

    if asset_id == "teacher_artifacts":
        files: list[Path] = []
        existing_dirs: list[Path] = []
        for raw in TEACHER_ARTIFACT_DIRS:
            directory = root / raw
            if directory.exists():
                existing_dirs.append(directory)
                files.extend(path for path in directory.rglob("*") if path.is_file())
        return {
            "status": "present" if files else "missing_optional",
            "relative_paths": [_rel(path, root) for path in existing_dirs],
            "counts": {
                "artifact_files": len(files),
                "artifact_dirs_present": len(existing_dirs),
            },
            "missingness": (
                "No checked-in Teacher artifact directory is present in this worktree."
                if not files
                else ""
            ),
        }

    raise SubstrateInventoryError(f"unknown policy asset_id: {asset_id}")


def _file_presence(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    if not path.exists():
        return _missing(path)
    return {
        "status": "present",
        "relative_path": _rel(path, root),
        "counts": {
            "bytes": path.stat().st_size,
        },
    }


def _present_counts(
    files: list[Path],
    counts: dict[str, int],
    *,
    names: list[str] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": "present" if files else "missing",
        "counts": counts,
    }
    if names is not None:
        payload["file_names"] = names
    return payload


def _missing(path: Path) -> dict[str, Any]:
    return {
        "status": "missing",
        "relative_path": path.as_posix(),
        "counts": {},
    }


def _glob(root: Path, pattern: str) -> list[Path]:
    return sorted(root.glob(pattern), key=lambda path: path.as_posix())


def _read_json(path: Path) -> dict[str, Any] | list[Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _len_mapping(value: Any) -> int:
    return len(value) if isinstance(value, dict) else 0


def _len_sequence(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def _contains_local_path_marker(value: Any) -> bool:
    if isinstance(value, str):
        return any(marker in value for marker in LOCAL_PATH_MARKERS)
    if isinstance(value, list):
        return any(_contains_local_path_marker(item) for item in value)
    if isinstance(value, dict):
        return any(
            _contains_local_path_marker(key) or _contains_local_path_marker(item)
            for key, item in value.items()
        )
    return False


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
