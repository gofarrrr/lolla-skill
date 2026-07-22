from __future__ import annotations

from pathlib import Path

from scripts.evals.validate_repository_local_authority import (
    DEFAULT_REGISTER,
    build_repository_local_authority_register,
    main,
)


ROOT = Path(__file__).resolve().parents[1]


def test_current_project_surfaces_have_repository_local_authority() -> None:
    result = build_repository_local_authority_register(ROOT)

    assert result["status"] == "complete"
    assert result["authority"] == {
        "repository_role": "sole_active_project_authority",
        "other_repository_required": False,
        "machine_specific_project_path_allowed": False,
    }
    assert result["active_scan"]["violation_count"] == 0
    assert result["active_scan"]["violations"] == []


def test_only_hash_locked_current_artifact_exception_is_classified() -> None:
    result = build_repository_local_authority_register(ROOT)
    exceptions = result["frozen_artifact_exceptions"]

    assert len(exceptions) == 1
    assert exceptions[0]["path"] == (
        "data/compiled/model_affordances/affordances_v60.json"
    )
    assert exceptions[0]["active_dependency"] is False
    assert exceptions[0]["retirement_phase"] == (
        "phase_6_repository_local_skill_packaging"
    )


def test_repository_local_authority_register_matches_current_scan() -> None:
    register = ROOT / DEFAULT_REGISTER
    assert main(["--root", str(ROOT), "--register", str(register), "--validate-only"]) == 0
