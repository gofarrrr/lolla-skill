from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.product.build_mental_model_atlas_custody_v2 import (
    ACTIVE_ROUTE_CONTRACT,
    FROZEN_V1_HASHES,
    build_atlas_custody_v2,
    canonical_json_bytes,
)


ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_frozen_v1_packages_remain_byte_identical() -> None:
    assert {
        path: _sha256(ROOT / path)
        for path in sorted(FROZEN_V1_HASHES)
    } == FROZEN_V1_HASHES


def test_custody_v2_packages_rebuild_byte_for_byte() -> None:
    release = build_atlas_custody_v2(ROOT)

    for package in release["packages"].values():
        output = ROOT / package["output"]
        for relative_path, payload in package["artifacts"].items():
            assert (output / relative_path).read_bytes() == canonical_json_bytes(
                payload
            )
        assert (output / "manifest.json").read_bytes() == canonical_json_bytes(
            package["manifest"]
        )


def test_v2_changes_custody_but_not_semantics_or_interface_fields() -> None:
    evidence = build_atlas_custody_v2(ROOT)["evidence"]

    assert evidence["schema_version"] == "lolla.atlas_custody_migration.v2"
    assert evidence["status"] == "complete"
    assert evidence["provider_calls"] == 0
    assert evidence["provider_cost_usd"] == 0.0
    assert evidence["v1_preservation"]["status"] == "complete"
    assert evidence["equivalence"]["semantic_and_interface_fields_equal"] is True
    assert evidence["equivalence"]["unexpected_difference_count"] == 0
    assert evidence["equivalence"]["custody_difference_count"] > 0
    assert evidence["equivalence"]["layout_hashes_equal"] is True
    assert evidence["equivalence"]["model_and_relation_identity_equal"] is True
    assert evidence["current_source_custody"]["source_authority"] == (
        "repository_local"
    )


def test_active_routes_use_v2_and_never_fall_back_to_v1() -> None:
    for source_path, route in ACTIVE_ROUTE_CONTRACT.items():
        source = (ROOT / source_path).read_text(encoding="utf-8")
        assert route["required"] in source
        for forbidden in route["forbidden"]:
            assert forbidden not in source


def test_checked_in_evidence_matches_current_rebuild() -> None:
    rebuilt = build_atlas_custody_v2(ROOT)["evidence"]
    checked_in = json.loads(
        (
            ROOT
            / "docs/evals/lolla-mental-model-atlas-custody-v2-evidence.json"
        ).read_text(encoding="utf-8")
    )
    assert checked_in == rebuilt
