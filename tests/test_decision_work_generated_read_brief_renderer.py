from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from engine.system_b.decision_work_generated_read_brief_renderer import (
    DecisionWorkGeneratedReadBriefRendererError,
    load_generated_read_brief_supply,
    render_generated_read_brief_markdown,
    validate_generated_read_brief_supply,
)
from engine.system_b.decision_work_generated_read_brief_supply import (
    build_generated_read_brief_supply,
    render_generated_read_brief_supply_json,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json"
)
INTAKE_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/intake.json"
)
SCRIPT_PATH = REPO_ROOT / "scripts/evals/render_decision_work_generated_read_brief.py"
FORBIDDEN_STRINGS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _supply() -> dict[str, Any]:
    return build_generated_read_brief_supply(
        read_path=READ_PATH,
        intake_path=INTAKE_PATH,
        created_at="2026-07-03T00:00:00Z",
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        render_generated_read_brief_supply_json(payload, pretty=True),
        encoding="utf-8",
    )


def test_renderer_renders_required_reader_facing_sections() -> None:
    markdown = render_generated_read_brief_markdown(
        supply=_supply(),
        case_id="launch-public-enterprise-beta",
    )

    assert markdown.startswith("# Decision Work Generated Read Brief")
    for heading in (
        "## The decision",
        "## What the generated interpretation adds",
        "## What changed for action",
        "## What still might be wrong",
        "## What this does not prove",
        "## Evidence and limits",
    ):
        assert heading in markdown
    assert "launch-public-enterprise-beta" in markdown
    assert "Uncertainty: medium." in markdown
    assert "Source references" in markdown
    assert "Privacy limit:" in markdown
    assert "Runtime sidecar update allowed: no" in markdown
    assert "Agent action authorization: no" in markdown
    assert "Answer-quality scoring: no" in markdown
    assert "Product proof: no" in markdown
    assert "Human validation: no" in markdown


def test_renderer_preserves_refs_uncertainty_and_excludes_evidence_only_fields() -> None:
    markdown = render_generated_read_brief_markdown(
        supply=_supply(),
        case_id="launch-public-enterprise-beta",
    )

    assert "docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md" in markdown
    assert "reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json" in markdown
    assert "checked_in_safe_summary_only" in markdown
    assert "Evidence-only fields excluded" in markdown
    assert "`lost_value`" in markdown
    assert "`safe_for_agent_inspection_only`" in markdown


def test_renderer_rejects_non_ready_supply() -> None:
    supply = _supply()
    supply["supply_status"] = "blocked_missing_source_refs"

    with pytest.raises(DecisionWorkGeneratedReadBriefRendererError, match="not ready"):
        validate_generated_read_brief_supply(supply)


def test_renderer_rejects_missing_uncertainty_or_source_refs() -> None:
    supply = _supply()
    del supply["allowed_brief_feed"][0]["uncertainty"]
    with pytest.raises(DecisionWorkGeneratedReadBriefRendererError, match="uncertainty"):
        validate_generated_read_brief_supply(supply)

    supply = _supply()
    supply["allowed_brief_feed"][0]["source_refs"] = []
    with pytest.raises(DecisionWorkGeneratedReadBriefRendererError, match="source refs"):
        validate_generated_read_brief_supply(supply)


def test_renderer_rejects_sidecar_quality_and_action_permissions() -> None:
    for key in (
        "can_update_sidecar",
        "can_authorize_agent_action",
        "can_be_used_as_quality_label",
    ):
        supply = _supply()
        supply["downstream_allowed"][key] = True
        with pytest.raises(DecisionWorkGeneratedReadBriefRendererError, match="unsafe"):
            validate_generated_read_brief_supply(supply)


def test_renderer_rejects_custody_authority_claims() -> None:
    for key in (
        "product_proof",
        "human_validated",
        "answer_quality_scored",
        "agent_action_authorized",
        "automatic_action_authorized",
    ):
        supply = _supply()
        supply["custody_flags"][key] = True
        with pytest.raises(DecisionWorkGeneratedReadBriefRendererError, match="unsafe"):
            validate_generated_read_brief_supply(supply)


def test_renderer_cli_writes_markdown(tmp_path: Path) -> None:
    supply_path = tmp_path / "supply.json"
    out_path = tmp_path / "brief.md"
    _write_json(supply_path, _supply())

    subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--supply",
            str(supply_path),
            "--case-id",
            "launch-public-enterprise-beta",
            "--out",
            str(out_path),
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    markdown = out_path.read_text(encoding="utf-8")
    assert "Decision Work Generated Read Brief" in markdown
    assert "What changed for action" in markdown
    assert "can_update_sidecar" not in markdown


def test_load_rejects_privacy_markers(tmp_path: Path) -> None:
    supply = _supply()
    supply["allowed_brief_feed"][0]["value"] = "SEC" + "RET"
    supply_path = tmp_path / "supply.json"
    _write_json(supply_path, supply)

    with pytest.raises(DecisionWorkGeneratedReadBriefRendererError, match="privacy"):
        load_generated_read_brief_supply(supply_path)


def test_renderer_does_not_modify_source_supply() -> None:
    supply = _supply()
    before = copy.deepcopy(supply)
    render_generated_read_brief_markdown(
        supply=supply,
        case_id="launch-public-enterprise-beta",
    )
    assert supply == before


def test_rendered_markdown_contains_no_forbidden_markers() -> None:
    markdown = render_generated_read_brief_markdown(
        supply=_supply(),
        case_id="launch-public-enterprise-beta",
    )
    for marker in FORBIDDEN_STRINGS:
        assert marker not in markdown
