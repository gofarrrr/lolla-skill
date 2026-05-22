from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_cleaning_evidence_surface import (  # noqa: E402
    build_cleaning_evidence_surface,
    render_cleaning_evidence_surface_markdown,
    validate_cleaning_evidence_surface,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_cleaning_evidence_surface_is_human_curation_not_auto_graduation() -> None:
    surface = build_cleaning_evidence_surface(root=REPO_ROOT)

    validate_cleaning_evidence_surface(surface)

    assert surface["schema_version"] == "pre_step6_cleaning_evidence_surface.v1"
    assert surface["runtime_policy"] == "runtime_dormant"
    assert surface["promotion_effect"] == "none_research_only"
    assert surface["principles"] == {
        "code_may_nominate": True,
        "humans_decide": True,
        "automatic_graduation_allowed": False,
        "runtime_visibility_change_allowed": False,
    }
    assert surface["global_read"]["evidence_surface_ready"] is True
    assert surface["global_read"]["runtime_promotion"] == "blocked"
    assert surface["global_read"]["skill_update"] == "blocked"


def test_cleaning_evidence_surface_nominates_consultant_without_promoting_phd() -> None:
    surface = build_cleaning_evidence_surface(root=REPO_ROOT)

    candidates = surface["graduation_candidates"]
    assert candidates == [
        {
            "case_id": "mid-level-consultant-report-2",
            "pressure_atom_id": "reversibility_until_counsel_boundary_card",
            "pressure_atom_text": "keep the first moves reversible until counsel guides the next action",
            "basis": "4/6 additive before anchor patch; 1/6 additive after patched anchor; protected payload preserved 6/6",
            "status": "human_review_required",
            "next_investigation": "synthesis",
        }
    ]

    phd_bounded = next(
        row
        for row in surface["atom_rows"]
        if row["case_id"] == "third-year-phd-student.v2.v60-off"
        and row["pressure_atom_id"] == "bounded_probe_not_commitment_card"
    )
    assert phd_bounded["additive_count"] == 4
    assert phd_bounded["evidence_read"] == "distributed_pressure_atom"
    assert phd_bounded["nomination"] == "watch_not_graduate"


def test_cleaning_evidence_surface_markdown_is_readable() -> None:
    surface = build_cleaning_evidence_surface(root=REPO_ROOT)

    markdown = render_cleaning_evidence_surface_markdown(surface)

    assert "Cleaning Evidence Surface" in markdown
    assert "Code may nominate; humans decide." in markdown
    assert "mid-level-consultant-report-2" in markdown
    assert "third-year-phd-student.v2.v60-off" in markdown
    assert "watch_not_graduate" in markdown
