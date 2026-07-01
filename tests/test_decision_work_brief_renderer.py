from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from engine.system_b.decision_work_brief_renderer import (
    DECISION_WORK_BRIEF_SCHEMA_VERSION,
    DecisionWorkBriefRendererInputError,
    extract_brief_from_pilot_review,
    load_json_object,
    render_decision_work_brief_markdown,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PILOT_REVIEW_PATH = (
    REPO_ROOT
    / "reviews"
    / "codex-assisted"
    / "decision-work-brief-draft-pilot-v0"
    / "review.json"
)
SECOND_CASE_REVIEW_PATH = (
    REPO_ROOT
    / "reviews"
    / "codex-assisted"
    / "decision-work-brief-second-tiny-case-pilot-v0"
    / "review.json"
)
THIRD_CASE_REVIEW_PATH = (
    REPO_ROOT
    / "reviews"
    / "codex-assisted"
    / "decision-work-brief-third-diversity-case-pilot-v0"
    / "review.json"
)
RENDERER_DOC_PATH = (
    REPO_ROOT / "docs/conversation-understanding/decision-work-brief-renderer-v0.md"
)
RENDERED_EXAMPLE_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md"
)
BRIEF_SCHEMA_PATH = (
    REPO_ROOT / "docs/conversation-understanding/decision-work-brief-v0.json"
)
PRIVACY_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
FORBIDDEN_FIELD_NAMES = {
    "safe_for_" + "agent_use",
    "approved",
    "certified",
    "pass_fail",
    "winner",
    "quality_score",
    "improvement_score",
    "judge_score",
    "answer_quality_score",
    "product_score",
    "correctness_score",
    "rating",
}
BRIEF_SECTIONS = (
    "The decision",
    "What changed",
    "What this means for action",
    "What still might be wrong",
    "What this does not prove",
    "Evidence and limits",
)
INTERNAL_MAIN_BODY_STRINGS = (
    "source_status:",
    "human_validated:",
    "product_proof:",
    "agent_action_authorized:",
    "schema_version",
    "artifact family",
    "custody machinery",
)


def _pilot_review() -> dict[str, Any]:
    return json.loads(PILOT_REVIEW_PATH.read_text(encoding="utf-8"))


def _brief() -> dict[str, Any]:
    return extract_brief_from_pilot_review(pilot_review=_pilot_review())


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _walk_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key))
            keys.extend(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(_walk_keys(child))
    return keys


def test_renderer_accepts_decision_work_brief_schema_and_starts_with_story() -> None:
    markdown = render_decision_work_brief_markdown(brief=_brief())

    assert markdown.startswith("# Decision Work Brief\n\n")
    assert "provisional, non-human-validated Decision Work Brief" in markdown
    assert "It is not proof that the final answer is correct." in markdown
    assert markdown.index("## The decision") < markdown.index("## What changed")
    assert markdown.index("## What this means for action") < markdown.index(
        "## Evidence and limits"
    )
    assert markdown.index("## What this does not prove") < markdown.index(
        "## Evidence and limits"
    )


def test_plain_language_sections_render_before_evidence_and_limits() -> None:
    markdown = render_decision_work_brief_markdown(brief=_brief())

    for section in BRIEF_SECTIONS:
        assert f"## {section}" in markdown
    assert "## Starting Direction" not in markdown
    assert "## What Lolla Pressed On" not in markdown
    assert "## Evidence Receipt" not in markdown
    assert "Uncertainty: high." in markdown
    assert "Source references" in markdown


def test_custody_flags_and_non_claims_render_visibly() -> None:
    markdown = render_decision_work_brief_markdown(brief=_brief())

    assert "## Evidence and limits" in markdown
    assert "### Non-claims" in markdown
    assert "`not_correctness_proof`" in markdown
    assert "`not_answer_quality_score`" in markdown
    assert "`not_agent_action_authorization`" in markdown
    assert "Human validation: no" in markdown
    assert "Product proof: no" in markdown
    assert "Answer-quality scoring: no" in markdown
    assert "Agent action authorization: no" in markdown
    assert "Runtime invoked: no" in markdown
    assert "Skill invoked: no" in markdown
    assert "Archive mutated: no" in markdown
    assert "Model calls: 0" in markdown
    assert "Private/raw content included: no" in markdown
    assert "Provider text included: no" in markdown


def test_missing_or_review_required_sections_render_plain_status_without_invention() -> None:
    brief = _brief()
    section = brief["sections"]["starting_direction"]
    section["status"] = "requires_human_review"
    section["uncertainty"] = "high"
    section["value"] = None
    section["empty_meaning"] = "Human review is needed before filling this section."

    markdown = render_decision_work_brief_markdown(brief=brief)

    assert "This part is marked `requires_human_review`" in markdown
    assert "Value not supplied." in markdown
    assert "Human review is needed before filling this section." in markdown
    assert "The renderer is not filling or smoothing" in markdown
    assert "candidate_starting_direction" not in markdown


def test_main_body_does_not_foreground_internal_status_or_source_vocabulary() -> None:
    markdown = render_decision_work_brief_markdown(brief=_brief())
    main_body = markdown.split("## Evidence and limits", 1)[0]

    for forbidden in INTERNAL_MAIN_BODY_STRINGS:
        assert forbidden not in main_body
    assert "source status:" not in main_body.lower()
    assert "packet" not in main_body.lower()


def test_renderer_rejects_unsupported_schema_version() -> None:
    brief = _brief()
    brief["schema_version"] = "unsupported"

    with pytest.raises(DecisionWorkBriefRendererInputError, match="schema version"):
        render_decision_work_brief_markdown(brief=brief)


def test_renderer_rejects_missing_required_sections() -> None:
    brief = _brief()
    del brief["sections"]["decision"]

    with pytest.raises(DecisionWorkBriefRendererInputError, match="required sections"):
        render_decision_work_brief_markdown(brief=brief)


def test_load_json_object_rejects_malformed_and_non_object_json(tmp_path: Path) -> None:
    malformed_path = tmp_path / "malformed.json"
    non_object_path = tmp_path / "non-object.json"
    malformed_path.write_text("{", encoding="utf-8")
    non_object_path.write_text("[]", encoding="utf-8")

    with pytest.raises(DecisionWorkBriefRendererInputError, match="malformed"):
        load_json_object(malformed_path)
    with pytest.raises(DecisionWorkBriefRendererInputError, match="root was not an object"):
        load_json_object(non_object_path)


def test_cli_renders_from_pilot_review_wrapper(tmp_path: Path) -> None:
    output_path = tmp_path / "brief.md"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/render_decision_work_brief.py",
            "--pilot-review",
            str(PILOT_REVIEW_PATH),
            "--brief-index",
            "0",
            "--out",
            str(output_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    markdown = output_path.read_text(encoding="utf-8")
    assert markdown.startswith("# Decision Work Brief")
    assert "## The decision" in markdown
    assert "## Evidence and limits" in markdown


def test_cli_renders_from_second_and_third_case_review_wrappers(tmp_path: Path) -> None:
    for review_path, name in (
        (SECOND_CASE_REVIEW_PATH, "second.md"),
        (THIRD_CASE_REVIEW_PATH, "third.md"),
    ):
        output_path = tmp_path / name
        result = subprocess.run(
            [
                sys.executable,
                "scripts/evals/render_decision_work_brief.py",
                "--pilot-review",
                str(review_path),
                "--brief-index",
                "0",
                "--out",
                str(output_path),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        assert result.returncode == 0, result.stderr
        markdown = output_path.read_text(encoding="utf-8")
        assert markdown.startswith("# Decision Work Brief")
        assert "## The decision" in markdown
        assert "## Evidence and limits" in markdown


def test_cli_renders_from_brief_json_file(tmp_path: Path) -> None:
    brief_path = tmp_path / "brief.json"
    output_path = tmp_path / "brief.md"
    _write_json(brief_path, _brief())

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/render_decision_work_brief.py",
            "--brief",
            str(brief_path),
            "--out",
            str(output_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert output_path.read_text(encoding="utf-8").startswith("# Decision Work Brief")


def test_cli_rejects_unsupported_schema_with_sanitized_error(tmp_path: Path) -> None:
    bad_path = tmp_path / "brief.json"
    output_path = tmp_path / "brief.md"
    bad_brief = _brief()
    bad_brief["schema_version"] = "wrong"
    _write_json(bad_path, bad_brief)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/render_decision_work_brief.py",
            "--brief",
            str(bad_path),
            "--out",
            str(output_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "schema version was unsupported" in result.stderr
    assert str(tmp_path) not in result.stderr


def test_checked_in_rendered_example_is_safe_if_present() -> None:
    if not RENDERED_EXAMPLE_PATH.exists():
        pytest.skip("PR117 checked-in rendered example was not created")

    text = RENDERED_EXAMPLE_PATH.read_text(encoding="utf-8")
    assert text.startswith("# Decision Work Brief")
    assert "## The decision" in text
    assert "## What changed" in text
    assert "## Evidence and limits" in text
    for marker in PRIVACY_MARKERS:
        assert marker not in text
    assert "/tmp/" not in text
    assert not (FORBIDDEN_FIELD_NAMES & set(_walk_keys({"rendered_markdown": text})))


def test_renderer_artifacts_pass_product_delta_boundary_lint() -> None:
    paths = [RENDERER_DOC_PATH]
    if RENDERED_EXAMPLE_PATH.exists():
        paths.append(RENDERED_EXAMPLE_PATH)

    report = lint_product_delta_paths(paths)

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_schema_version_constant_matches_schema_file() -> None:
    schema = json.loads(BRIEF_SCHEMA_PATH.read_text(encoding="utf-8"))

    assert schema["properties"]["schema_version"]["const"] == (
        DECISION_WORK_BRIEF_SCHEMA_VERSION
    )
