#!/usr/bin/env python3
"""Build the provider-free Atlas custody V2 packages.

V1 remains immutable historical evidence. V2 republishes the same semantic and
interface records with the repository-local source manifest and recovered
curation hashes, then proves that every non-custody field is unchanged.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from scripts.product.build_mental_model_atlas_card_first_repair import (
    build_card_first_package,
)
from scripts.product.build_mental_model_atlas_navigation_index import (
    build_navigation_package,
)
from scripts.product.build_mental_model_atlas_phase1_projection import (
    EXPECTED_SOURCE_HASHES,
    build_phase1_package,
    canonical_json_bytes,
)


SCHEMA_VERSION = "lolla.atlas_custody_migration.v2"
RELEASE_ID = "lolla.mental_model_atlas.custody_v2"
CREATED_DATE = "2026-07-22"

CURRENT_SOURCE_HASHES = {
    **EXPECTED_SOURCE_HASHES,
    "data/model_sources/manifest.json": (
        "ac9c07ae82f5f6686390de1eaefc69a29491062cf66a48fb71a80e101bae7c83"
    ),
}

FROZEN_V1_HASHES = {
    "apps/mental-model-atlas/public/data/phase1/manifest.json": (
        "203999a61dbe9c2e943bbcb9f5b4dd87779d4557ea9fcfbd50b3e9d59e816c52"
    ),
    "apps/mental-model-atlas/public/data/phase1/pages/model-abstraction.json": (
        "8cc07cbbf68f399dcd5787df9067bd3a3646068b59ed691ca043ffc9e9ce406f"
    ),
    "apps/mental-model-atlas/public/data/card-first-v1/manifest.json": (
        "41f4f19d98d94335993b28b734fae4100ad0dc5b622bd4f7bf93f037640dabdd"
    ),
    "apps/mental-model-atlas/public/data/card-first-v1/pages/model-abstraction.json": (
        "46a666bb276c1ebdcb6ecd4045cbb440fcb0538b5a0ca7d2abc813f113f4512d"
    ),
    "apps/mental-model-atlas/public/data/navigation-v1/manifest.json": (
        "fcd2f994ea03221ceea31601c1e991e46750512154222bb5da536f866a24de62"
    ),
    "apps/mental-model-atlas/public/data/navigation-v1/neighborhood-index.json": (
        "565ccef599ecc018f3501c36febadb9468ecaaaab310598d0c6e467ffd33417f"
    ),
}

ACTIVE_ROUTE_CONTRACT = {
    "apps/mental-model-atlas/src/projection.ts": {
        "required": "data/phase1-v2/",
        "forbidden": ["data/phase1/"],
    },
    "apps/mental-model-atlas/src/navigation.ts": {
        "required": "data/navigation-v2/neighborhood-index.json",
        "forbidden": ["data/navigation-v1/neighborhood-index.json"],
    },
    "apps/mental-model-atlas/src/cardFirstModelPage.ts": {
        "required": "data/card-first-v2/pages/model-abstraction.json",
        "forbidden": ["data/card-first-v1/pages/model-abstraction.json"],
    },
}

OUTPUTS = {
    "phase1": "apps/mental-model-atlas/public/data/phase1-v2",
    "card_first": "apps/mental-model-atlas/public/data/card-first-v2",
    "navigation": "apps/mental-model-atlas/public/data/navigation-v2",
}

EVIDENCE_PATH = "docs/evals/lolla-mental-model-atlas-custody-v2-evidence.json"


class AtlasCustodyV2Error(ValueError):
    pass


def build_atlas_custody_v2(root: Path) -> dict[str, Any]:
    root = root.resolve()
    _verify_frozen_v1(root)
    _verify_current_sources(root)

    phase1 = build_phase1_custody_v2_package(root)
    card_first = build_card_first_custody_v2_package(root)
    navigation = build_navigation_custody_v2_package(root)

    packages = {
        "phase1": {
            "output": OUTPUTS["phase1"],
            "artifacts": phase1["artifacts"],
            "manifest": phase1["manifest"],
        },
        "card_first": {
            "output": OUTPUTS["card_first"],
            "artifacts": card_first["artifacts"],
            "manifest": card_first["manifest"],
        },
        "navigation": {
            "output": OUTPUTS["navigation"],
            "artifacts": {
                "neighborhood-index.json": navigation["index"],
            },
            "manifest": navigation["manifest"],
        },
    }
    evidence = _build_evidence(root, packages)
    return {"packages": packages, "evidence": evidence}


def build_phase1_custody_v2_package(root: Path) -> dict[str, Any]:
    return _annotate_phase1(
        build_phase1_package(
            root,
            source_hashes=CURRENT_SOURCE_HASHES,
            source_authority="repository_local",
            canonical_data_commit=None,
        )
    )


def build_card_first_custody_v2_package(root: Path) -> dict[str, Any]:
    return _annotate_card_first(build_card_first_package(root))


def build_navigation_custody_v2_package(root: Path) -> dict[str, Any]:
    return _annotate_navigation(
        build_navigation_package(
            root,
            source_hashes=CURRENT_SOURCE_HASHES,
            source_authority="repository_local",
            canonical_data_commit=None,
        )
    )


def write_atlas_custody_v2(root: Path) -> dict[str, Any]:
    release = build_atlas_custody_v2(root)
    for package in release["packages"].values():
        output = root / package["output"]
        output.mkdir(parents=True, exist_ok=True)
        for relative_path, payload in package["artifacts"].items():
            target = output / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(canonical_json_bytes(payload))
        (output / "manifest.json").write_bytes(
            canonical_json_bytes(package["manifest"])
        )
    evidence_path = root / EVIDENCE_PATH
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_bytes(canonical_json_bytes(release["evidence"]))
    return release


def validate_checked_in_atlas_custody_v2(root: Path) -> dict[str, Any]:
    release = build_atlas_custody_v2(root)
    for package in release["packages"].values():
        output = root / package["output"]
        for relative_path, payload in package["artifacts"].items():
            path = output / relative_path
            if not path.is_file() or path.read_bytes() != canonical_json_bytes(payload):
                raise AtlasCustodyV2Error(f"V2 artifact drift: {path}")
        manifest_path = output / "manifest.json"
        if (
            not manifest_path.is_file()
            or manifest_path.read_bytes()
            != canonical_json_bytes(package["manifest"])
        ):
            raise AtlasCustodyV2Error(f"V2 manifest drift: {manifest_path}")
    evidence_path = root / EVIDENCE_PATH
    if (
        not evidence_path.is_file()
        or evidence_path.read_bytes()
        != canonical_json_bytes(release["evidence"])
    ):
        raise AtlasCustodyV2Error(f"V2 evidence drift: {evidence_path}")
    return release


def _release_marker() -> dict[str, Any]:
    return {
        "release_id": RELEASE_ID,
        "custody_version": 2,
        "predecessor_semantics": "atlas_v1_exact_records",
        "source_authority": "repository_local",
        "semantic_change": False,
        "interface_change": False,
        "provider_calls": 0,
    }


def _annotate_phase1(package: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(package)
    for payload in result["artifacts"].values():
        payload["custody_release"] = _release_marker()
    by_path = {item["path"]: item for item in result["manifest"]["artifacts"]}
    for path, payload in result["artifacts"].items():
        by_path[path]["sha256"] = _sha256(canonical_json_bytes(payload))
    result["manifest"]["custody_release"] = _release_marker()
    return result


def _annotate_card_first(package: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(package)
    for payload in result["artifacts"].values():
        payload["custody_release"] = _release_marker()
    by_path = {item["path"]: item for item in result["manifest"]["artifacts"]}
    for path, payload in result["artifacts"].items():
        by_path[path]["sha256"] = _sha256(canonical_json_bytes(payload))
    result["manifest"]["custody_release"] = _release_marker()
    return result


def _annotate_navigation(package: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(package)
    result["index"]["custody_release"] = _release_marker()
    result["manifest"]["index"]["sha256"] = _sha256(
        canonical_json_bytes(result["index"])
    )
    result["manifest"]["custody_release"] = _release_marker()
    return result


def _build_evidence(
    root: Path,
    packages: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    v1_packages = _load_v1_packages(root)
    custody_differences: list[str] = []
    unexpected_differences: list[str] = []
    for package_name, current in packages.items():
        frozen = v1_packages[package_name]
        pairs = {
            "manifest.json": (frozen["manifest"], current["manifest"]),
            **{
                path: (frozen["artifacts"][path], payload)
                for path, payload in current["artifacts"].items()
            },
        }
        for relative_path, (left, right) in pairs.items():
            for path in _difference_paths(left, right):
                qualified = f"{package_name}/{relative_path}{path}"
                if _is_custody_path(path):
                    custody_differences.append(qualified)
                else:
                    unexpected_differences.append(qualified)
            if _semantic_view(left) != _semantic_view(right):
                unexpected_differences.append(
                    f"{package_name}/{relative_path}/semantic_view"
                )

    v1_navigation = v1_packages["navigation"]["artifacts"][
        "neighborhood-index.json"
    ]
    v2_navigation = packages["navigation"]["artifacts"][
        "neighborhood-index.json"
    ]
    v1_layout_hashes = _phase1_layout_hashes(v1_packages["phase1"]["artifacts"])
    v2_layout_hashes = _phase1_layout_hashes(packages["phase1"]["artifacts"])
    evidence = {
        "schema_version": SCHEMA_VERSION,
        "created_date": CREATED_DATE,
        "status": "complete" if not unexpected_differences else "failed",
        "release_id": RELEASE_ID,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "v1_preservation": {
            "status": "complete",
            "frozen_hashes": dict(sorted(FROZEN_V1_HASHES.items())),
        },
        "current_source_custody": {
            "source_authority": "repository_local",
            "source_hashes": dict(sorted(CURRENT_SOURCE_HASHES.items())),
            "canonical_markdown_count": 222,
        },
        "packages": {
            name: {
                "output": package["output"],
                "artifact_count": len(package["artifacts"]),
                "manifest_sha256": _sha256(
                    canonical_json_bytes(package["manifest"])
                ),
            }
            for name, package in sorted(packages.items())
        },
        "equivalence": {
            "semantic_and_interface_fields_equal": not unexpected_differences,
            "model_and_relation_identity_equal": (
                _identity_vector(v1_navigation) == _identity_vector(v2_navigation)
            ),
            "layout_hashes_equal": v1_layout_hashes == v2_layout_hashes,
            "custody_difference_count": len(set(custody_differences)),
            "unexpected_difference_count": len(set(unexpected_differences)),
            "unexpected_differences": sorted(set(unexpected_differences)),
            "allowed_difference_classes": [
                "source_custody",
                "custody_release",
                "sha256_reference",
            ],
        },
        "active_routes": copy.deepcopy(ACTIVE_ROUTE_CONTRACT),
        "non_claims": [
            "custody_republication_is_not_semantic_regeneration",
            "identity_equivalence_is_not_relation_truth_proof",
            "route_migration_is_not_atlas_publication_clearance",
            "v2_does_not_authorize_teacher_runtime_or_deployment",
        ],
    }
    if unexpected_differences:
        raise AtlasCustodyV2Error(
            "unexpected V1/V2 differences: "
            + ", ".join(sorted(set(unexpected_differences))[:10])
        )
    return evidence


def _load_v1_packages(root: Path) -> dict[str, Any]:
    phase1_dir = root / "apps/mental-model-atlas/public/data/phase1"
    phase1_manifest = _load_json(phase1_dir / "manifest.json")
    phase1_artifacts = {
        item["path"]: _load_json(phase1_dir / item["path"])
        for item in phase1_manifest["artifacts"]
    }
    card_dir = root / "apps/mental-model-atlas/public/data/card-first-v1"
    card_manifest = _load_json(card_dir / "manifest.json")
    card_artifacts = {
        item["path"]: _load_json(card_dir / item["path"])
        for item in card_manifest["artifacts"]
    }
    navigation_dir = root / "apps/mental-model-atlas/public/data/navigation-v1"
    navigation_manifest = _load_json(navigation_dir / "manifest.json")
    return {
        "phase1": {"manifest": phase1_manifest, "artifacts": phase1_artifacts},
        "card_first": {
            "manifest": card_manifest,
            "artifacts": card_artifacts,
        },
        "navigation": {
            "manifest": navigation_manifest,
            "artifacts": {
                "neighborhood-index.json": _load_json(
                    navigation_dir / "neighborhood-index.json"
                )
            },
        },
    }


def _difference_paths(left: Any, right: Any, path: str = "") -> list[str]:
    if type(left) is not type(right):
        return [path or "/"]
    if isinstance(left, dict):
        differences: list[str] = []
        for key in sorted(set(left) | set(right)):
            child = f"{path}/{key}"
            if key not in left or key not in right:
                differences.append(child)
            else:
                differences.extend(_difference_paths(left[key], right[key], child))
        return differences
    if isinstance(left, list):
        if len(left) != len(right):
            return [f"{path}/length"]
        differences: list[str] = []
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            differences.extend(
                _difference_paths(left_item, right_item, f"{path}/{index}")
            )
        return differences
    return [] if left == right else [path or "/"]


def _is_custody_path(path: str) -> bool:
    parts = [part for part in path.split("/") if part]
    return bool(
        "source_custody" in parts
        or "custody_release" in parts
        or (parts and parts[-1] == "sha256")
    )


def _semantic_view(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _semantic_view(item)
            for key, item in value.items()
            if key not in {"source_custody", "custody_release", "sha256"}
        }
    if isinstance(value, list):
        return [_semantic_view(item) for item in value]
    return value


def _phase1_layout_hashes(artifacts: Mapping[str, Any]) -> dict[str, str]:
    return {
        path: payload["layout"]["coordinate_sha256"]
        for path, payload in artifacts.items()
        if payload.get("schema_version") == "lolla.atlas_projection.v1"
    }


def _identity_vector(index: Mapping[str, Any]) -> dict[str, list[str]]:
    return {
        "models": [str(item["model_id"]) for item in index["models"]],
        "relations": [str(item["relation_id"]) for item in index["relations"]],
    }


def _verify_frozen_v1(root: Path) -> None:
    for relative_path, expected in FROZEN_V1_HASHES.items():
        path = root / relative_path
        if not path.is_file() or _sha256(path.read_bytes()) != expected:
            raise AtlasCustodyV2Error(f"frozen V1 drift: {relative_path}")


def _verify_current_sources(root: Path) -> None:
    for relative_path, expected in CURRENT_SOURCE_HASHES.items():
        path = root / relative_path
        if not path.is_file() or _sha256(path.read_bytes()) != expected:
            raise AtlasCustodyV2Error(f"current source drift: {relative_path}")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AtlasCustodyV2Error(f"expected JSON object: {path}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    release = (
        validate_checked_in_atlas_custody_v2(root)
        if args.validate_only
        else write_atlas_custody_v2(root)
    )
    print(
        json.dumps(
            {
                "release_id": RELEASE_ID,
                "status": "valid" if args.validate_only else "written",
                "package_count": len(release["packages"]),
                "custody_difference_count": release["evidence"]["equivalence"][
                    "custody_difference_count"
                ],
                "unexpected_difference_count": release["evidence"][
                    "equivalence"
                ]["unexpected_difference_count"],
                "provider_calls": 0,
                "provider_cost_usd": 0.0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
