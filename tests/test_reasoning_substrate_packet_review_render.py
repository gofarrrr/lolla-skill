from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_substrate_packet_review import (
    render_reasoning_substrate_packet_comparison_markdown,
    render_reasoning_substrate_packet_review_markdown,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PR27_FIXTURE = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "reasoning_substrate_packet"
    / "pr27_mixed_packet_review.json"
)
PR29_FIXTURE = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "reasoning_substrate_packet"
    / "pr29_v5_mixed_packet_review.json"
)
PR27_RENDER = (
    REPO_ROOT / "research" / "reasoning-substrate-packet-pr27-review-render-2026-05-07.md"
)
PR29_RENDER = (
    REPO_ROOT / "research" / "reasoning-substrate-packet-pr29-review-render-2026-05-07.md"
)
COMPARISON_RENDER = (
    REPO_ROOT / "research" / "reasoning-substrate-packet-comparison-render-2026-05-07.md"
)
LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)


def test_review_render_makes_v5_packet_inspectable_without_product_copy() -> None:
    markdown = render_reasoning_substrate_packet_review_markdown(_load(PR29_FIXTURE))

    assert markdown.startswith("# Reasoning Substrate Packet Review")
    assert "`pr29-v5-mixed-packet-depth-review`" in markdown
    assert "| Candidate cards | 7 |" in markdown
    assert "| Reviewed cards | 7 |" in markdown
    assert "| Graph-only cards | 0 |" in markdown
    assert "chain-of-verification" in markdown
    assert "make-or-break" in markdown
    assert "reviewed_affordance_available" in markdown
    assert "repo_source_custodied" in markdown
    assert "Suppressed Candidates" in markdown
    assert "duplicate_model_id" in markdown

    forbidden_fragments = (
        "<html",
        "rendered_html",
        "memo copy",
        "user-facing prose",
        "Pressure:",
        "What to verify:",
        "Dismiss if:",
        "Tripwire",
    )
    lower_markdown = markdown.lower()
    assert all(fragment.lower() not in lower_markdown for fragment in forbidden_fragments)


def test_review_render_keeps_graph_only_cards_honest() -> None:
    markdown = render_reasoning_substrate_packet_review_markdown(_load(PR27_FIXTURE))

    assert "| Reviewed cards | 3 |" in markdown
    assert "| Graph-only cards | 4 |" in markdown
    assert "step-back" in markdown
    assert "graph_only_runtime_card" in markdown
    assert "No reviewed affordance record is available" in markdown
    assert "Graph-only recall material" in markdown


def test_comparison_render_shows_depth_delta_not_final_selection() -> None:
    markdown = render_reasoning_substrate_packet_comparison_markdown(
        before_packet=_load(PR27_FIXTURE),
        after_packet=_load(PR29_FIXTURE),
    )

    assert markdown.startswith("# Reasoning Substrate Packet Comparison")
    assert "| Reviewed cards | 3 | 7 | +4 |" in markdown
    assert "| Graph-only cards | 4 | 0 | -4 |" in markdown
    assert "`chain-of-verification`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "`constraints`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "Compare handoff usefulness only" in markdown
    assert "Do not answer the user case" in markdown
    assert "Do not choose user-visible output" in markdown
    assert "Pressure:" not in markdown
    assert "best pressure" not in markdown.lower()


def test_checked_in_review_renders_match_deterministic_renderer() -> None:
    pr27_packet = _load(PR27_FIXTURE)
    pr29_packet = _load(PR29_FIXTURE)

    assert PR27_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_review_markdown(pr27_packet)
    )
    assert PR29_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_review_markdown(pr29_packet)
    )
    assert COMPARISON_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_comparison_markdown(
            before_packet=pr27_packet,
            after_packet=pr29_packet,
        )
    )


def test_review_render_rejects_non_dormant_packets() -> None:
    packet = _load(PR29_FIXTURE)
    packet["runtime_policy"] = "live_runtime"

    with pytest.raises(ValueError, match="runtime_dormant"):
        render_reasoning_substrate_packet_review_markdown(packet)


def test_review_renderer_is_not_imported_by_live_runtime_paths() -> None:
    forbidden_fragments = (
        "reasoning_substrate_packet_review",
        "render_reasoning_substrate_packet_review_markdown",
        "render_reasoning_substrate_packet_comparison_markdown",
    )

    for path in LIVE_RUNTIME_PATHS:
        text = path.read_text(encoding="utf-8")
        assert all(fragment not in text for fragment in forbidden_fragments)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))
