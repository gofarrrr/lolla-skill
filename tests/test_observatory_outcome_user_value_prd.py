from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


DOC = REPO_ROOT / "docs/product/observatory-outcome-user-value-prd-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-outcome-user-value-prd-v0/review.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_outcome_user_value_prd_records_browser_grounded_problem() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = _load_json(REVIEW)

    assert "Observatory Outcome User Value PRD" in readme
    assert "observatory-outcome-user-value-prd-v0.md" in readme
    assert review["decision_gate"] == "proceed_to_outcome_user_value_redesign"
    assert review["browser_grounded"] is True

    for phrase in [
        "Outcome is not an orientation page.",
        "Outcome should be the user's result page.",
        "top navigation repeats the same six surfaces",
        "left sidebar repeats the same six surfaces",
        "center page repeats the same reading path again",
        "the outcome text is truncated with ellipses",
        "the strongest pressure is hidden",
        "two identical `Open model cards` links",
        "full outcome headline with no ellipsis",
        "Why this answer changed",
        "What would change confidence",
        "center reading-path/start panel",
        "details should not be the only place where the useful result appears",
        "proceed_to_outcome_user_value_redesign",
    ]:
        assert phrase in doc

    assert review["observed_problem"]["outcome_first_viewport_overloaded_with_navigation"] is True
    assert review["observed_problem"]["center_navigation_duplicates_sidebar"] is True
    assert review["observed_problem"]["primary_outcome_text_truncated"] is True
    assert review["observed_problem"]["duplicate_visible_action_labels_found"] is True
    assert review["prd_requires"]["full_outcome_answer_without_ellipsis"] is True
    assert review["prd_requires"]["no_center_six_card_reading_path_on_outcome"] is True
    assert review["prd_requires"]["no_duplicate_visible_action_labels"] is True


def test_outcome_user_value_prd_preserves_boundaries_and_nonclaims() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = _load_json(REVIEW)

    for phrase in [
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not create a new run",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not touch `SKILL.md`",
        "does not touch `scripts/skill/*`",
        "does not touch `scripts/archive_run.py`",
        "does not claim product proof",
        "does not claim human validation",
        "does not claim answer correctness",
        "does not claim advice correctness",
        "does not authorize automatic action",
        "does not treat graph edges as proof",
    ]:
        assert phrase in doc

    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["creates_new_run"] is False
    assert review["boundary"]["wires_skill_runtime_behavior"] is False
    assert review["boundary"]["touches_skill_md"] is False
    assert review["boundary"]["touches_scripts_skill"] is False
    assert review["boundary"]["touches_archive_run"] is False
    assert review["boundary"]["touches_compiled_spa_bundle"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_outcome_user_value_prd_links_are_local() -> None:
    missing = []
    for path in [DOC, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).exists():
                missing.append((path.name, clean))
    assert missing == []
