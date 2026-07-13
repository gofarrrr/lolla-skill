import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "research/minimum-viable-loop-receipt-2026-07-12/goal-completion-audit.json"


def test_goal_audit_covers_every_requirement_with_existing_evidence():
    audit = json.loads(AUDIT.read_text())
    assert audit["objective_scope_preserved"] is True
    assert len(audit["requirements"]) == 11
    assert all(row["status"] == "proved" for row in audit["requirements"])
    for row in audit["requirements"]:
        assert row["evidence"]
        for path in row["evidence"]:
            assert (ROOT / path).is_file(), (row["requirement"], path)


def test_goal_completion_does_not_authorize_forbidden_claims():
    audit = json.loads(AUDIT.read_text())
    completion = audit["completion_read"]
    assert completion["goal_achieved"] is True
    assert completion["requirements_incomplete"] == 0
    assert completion["requirements_missing"] == 0
    assert completion["runtime_integration_authorized"] is False
    assert completion["production_claim_authorized"] is False
    assert completion["human_usefulness_proven"] is False
