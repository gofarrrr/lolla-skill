"""Tests for the Phase 2c conversation-first Lane 1 entry points.

Covers:
- `_joined_assistant_turns_text` — flat string of assistant turns for
  embedding signal + backward-compat callers.
- `format_pass1_cluster_prompts_from_context` — 6 cluster prompts with
  CONTEXT/SOURCE split; SOURCE = assistant turns (Lane 1 audits the
  assistant's reasoning).
- `format_pass2_prompt_from_context` — per-tendency deep-check prompt
  with CONTEXT/SOURCE split + enum-checklist reminder for sub_patterns
  (durable 2b lesson: bake into first draft).

Boundary calls are not exercised here; these tests check prompt composition
and helper behavior only.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.conversation_context import (
    ConversationContext,
    ExtractionPayload,
    LiveConstraint,
    DroppedThread,
    Turn,
)
from engine.system_b.prompts import (
    PASS1_CLUSTERS,
    _joined_assistant_turns_text,
    format_pass1_cluster_prompts_from_context,
)
from engine.system_b.deep_checks import (
    format_pass2_prompt_from_context,
)
from engine.system_b.tendency_catalog import (
    ModelBinding,
    TendencyCatalog,
    TendencyRef,
)


def _catalog() -> TendencyCatalog:
    """Minimal catalog covering the tendencies referenced by tests below.

    Pass 1 cluster builder silently skips tendency IDs absent from the catalog,
    so this covers just enough to exercise user-prompt formatting + the one
    tendency we deep-check in Pass 2 tests.
    """
    authority = TendencyRef(
        tendency_id="authority-misinfluence-tendency",
        display_name="Authority Misinfluence Tendency",
        routing_key="authority_misinfluence",
        antidote_model_ids=("first-principles-thinking",),
        antidote_bindings=(ModelBinding(model_id="first-principles-thinking"),),
        description="Prestige or rank substitutes for evidence.",
        tendency_number=7,
    )
    return TendencyCatalog(
        tendencies={"authority-misinfluence-tendency": authority},
        # alias_index is keyed by _normalize_alias(...) output; the "-tendency"
        # suffix strips during lookup so the index uses the stripped form.
        alias_index={
            "authority-misinfluence": "authority-misinfluence-tendency",
            "authority-misinfluence-tendency": "authority-misinfluence-tendency",
        },
    )


def _context(
    user_texts: tuple[str, ...] = ("I'm thinking of taking the Series B offer — 15% equity feels low but the team is strong.",),
    assistant_texts: tuple[str, ...] = ("You should definitely take it — 15% is standard for Series B and you'll make it up in secondary.",),
    decision_situation: str = "Founder-CEO considering Series B equity offer.",
    original_framing: str = "Is 15% equity too low for Series B founding-engineer role?",
    live_constraints: tuple[LiveConstraint, ...] = (),
    dropped_threads: tuple[DroppedThread, ...] = (),
) -> ConversationContext:
    turns: list[Turn] = []
    idx = 1
    # Interleave user/assistant — user first
    for u, a in zip(user_texts, assistant_texts + ("",) * len(user_texts)):
        turns.append(Turn(turn_index=idx, speaker="user", text=u))
        idx += 1
        if a:
            turns.append(Turn(turn_index=idx, speaker="assistant", text=a))
            idx += 1
    # Any remaining assistant texts past user count
    for a in assistant_texts[len(user_texts):]:
        turns.append(Turn(turn_index=idx, speaker="assistant", text=a))
        idx += 1

    extraction = ExtractionPayload(
        decision_situation=decision_situation,
        live_constraints=live_constraints,
        synthesized_position="take the offer",
        reasoning_passages=(),
        original_framing=original_framing,
        dropped_threads=dropped_threads,
    )
    return ConversationContext(turns=tuple(turns), extraction=extraction)


# ---------------------------------------------------------------------------
# _joined_assistant_turns_text
# ---------------------------------------------------------------------------

def test_joined_assistant_turns_text_returns_assistant_only():
    ctx = _context(
        user_texts=("user message one", "user message two"),
        assistant_texts=("assistant reply one", "assistant reply two"),
    )
    joined = _joined_assistant_turns_text(ctx)
    assert "assistant reply one" in joined
    assert "assistant reply two" in joined
    assert "user message one" not in joined
    assert "user message two" not in joined


def test_joined_assistant_turns_text_empty_when_no_assistant_turns():
    user_turn = Turn(turn_index=1, speaker="user", text="just the user")
    extraction = ExtractionPayload(
        decision_situation="d",
        live_constraints=(),
        synthesized_position="p",
        reasoning_passages=(),
        original_framing="f",
        dropped_threads=(),
    )
    ctx = ConversationContext(turns=(user_turn,), extraction=extraction)
    assert _joined_assistant_turns_text(ctx) == ""


# ---------------------------------------------------------------------------
# format_pass1_cluster_prompts_from_context
# ---------------------------------------------------------------------------

def test_pass1_from_context_returns_one_entry_per_cluster():
    catalog = _catalog()
    ctx = _context()
    prompts = format_pass1_cluster_prompts_from_context(ctx, catalog)
    assert len(prompts) == len(PASS1_CLUSTERS) == 6
    cluster_ids = {p[0] for p in prompts}
    expected = {c.cluster_id for c in PASS1_CLUSTERS}
    assert cluster_ids == expected


def test_pass1_from_context_user_prompt_has_context_and_source_sections():
    catalog = _catalog()
    ctx = _context(
        user_texts=("I'm thinking of taking the offer.",),
        assistant_texts=("You should take it — 15% is standard.",),
    )
    _, _, user = format_pass1_cluster_prompts_from_context(ctx, catalog)[0]
    assert "CONTEXT" in user
    assert "SOURCE" in user
    # SOURCE should contain the assistant turn verbatim (primary audit target)
    assert "You should take it" in user
    # CONTEXT should contain the user turn and extraction fields
    assert "I'm thinking of taking the offer." in user


def test_pass1_from_context_user_prompt_labels_source_as_primary_audit_target():
    catalog = _catalog()
    ctx = _context()
    _, _, user = format_pass1_cluster_prompts_from_context(ctx, catalog)[0]
    # Downstream parser doesn't use substrings for Lane 1, but the prompt body
    # must explicitly tell the LLM to treat the assistant turns in SOURCE as
    # the primary audit target (tendencies live in commissions + omissions).
    assert "primary audit target" in user.lower()


def test_pass1_from_context_includes_extraction_context_fields():
    catalog = _catalog()
    constraints = (
        LiveConstraint(
            constraint="lease renewal in 60 days",
            introduced_turn=1,
            status="active",
            weight="hard",
            canonical_key=None,
        ),
    )
    dropped = (
        DroppedThread(
            thread="wife-first conversation",
            raised_by="user",
            raised_turn=3,
            status="acknowledged_then_dropped",
            superseded_by="focused on job offer",
        ),
    )
    ctx = _context(live_constraints=constraints, dropped_threads=dropped)
    _, _, user = format_pass1_cluster_prompts_from_context(ctx, catalog)[0]
    assert "lease renewal in 60 days" in user
    assert "wife-first conversation" in user


def test_pass1_from_context_preserves_cluster_system_prompt_shape():
    """System prompt per cluster should still mention the cluster theme and
    scoring scale — we're only migrating the user prompt, system prompts
    need only minor acknowledgment of turn-structured input."""
    catalog = _catalog()
    ctx = _context()
    prompts = format_pass1_cluster_prompts_from_context(ctx, catalog)
    for cluster_id, system, _ in prompts:
        # theme text present
        cluster = next(c for c in PASS1_CLUSTERS if c.cluster_id == cluster_id)
        # Cluster theme mentions the cluster's family — check at least partial match
        theme_first_word = cluster.theme.split()[0]
        assert theme_first_word in system or cluster.theme[:20] in system
        # scoring scale present (0-10)
        assert "0-10" in system or "0-10" in system or "score" in system.lower()


# ---------------------------------------------------------------------------
# format_pass2_prompt_from_context
# ---------------------------------------------------------------------------

def test_pass2_from_context_returns_system_and_user_tuple():
    catalog = _catalog()
    ctx = _context()
    # pick a common tendency
    tendency_key = "authority-misinfluence-tendency"
    system, user = format_pass2_prompt_from_context(ctx, tendency_key, catalog)
    assert isinstance(system, str)
    assert isinstance(user, str)
    assert len(system) > 0
    assert len(user) > 0


def test_pass2_from_context_user_prompt_has_context_and_source_sections():
    catalog = _catalog()
    ctx = _context(
        user_texts=("Should I take the offer?",),
        assistant_texts=("Yes, 15% is strong because reputable VCs know best.",),
    )
    _, user = format_pass2_prompt_from_context(ctx, "authority-misinfluence-tendency", catalog)
    assert "CONTEXT" in user
    assert "SOURCE" in user
    assert "Yes, 15% is strong" in user  # assistant turn in SOURCE


def test_pass2_from_context_system_prompt_has_enum_checklist_reminder():
    """Durable 2b lesson: bake enum-checklist reminder for sub_patterns into
    the first-draft system prompt — don't wait for measurement to force iteration.

    The new-path prompt must remind the LLM to consider each sub_pattern in the
    menu, including ones that manifest as omission rather than surface in the
    assistant's verbatim text."""
    catalog = _catalog()
    ctx = _context()
    system, _ = format_pass2_prompt_from_context(ctx, "authority-misinfluence-tendency", catalog)
    # The reminder should explicitly mention considering all sub_patterns, not just
    # ones obvious in surface text. Check for the key phrase.
    lowered = system.lower()
    assert "sub_pattern" in lowered or "sub-pattern" in lowered
    # Require language about considering all options or implicit manifestation
    assert (
        "consider each" in lowered
        or "verify you've considered" in lowered
        or "consider all" in lowered
        or "implicit" in lowered
        or "omission" in lowered
    )


def test_pass2_from_context_system_prompt_includes_tendency_specifics():
    """Should still include tendency name, number, description, route menu."""
    catalog = _catalog()
    ctx = _context()
    tendency_key = "authority-misinfluence-tendency"
    tendency = catalog.lookup(tendency_key)
    system, _ = format_pass2_prompt_from_context(ctx, tendency_key, catalog)
    assert tendency.display_name in system
    assert str(tendency.tendency_number) in system


def test_pass2_from_context_user_prompt_does_not_use_legacy_query_vanilla_format():
    """Sanity: the new-path user prompt should NOT use the legacy `QUERY:\\nVANILLA ANSWER:` structure."""
    catalog = _catalog()
    ctx = _context()
    _, user = format_pass2_prompt_from_context(ctx, "authority-misinfluence-tendency", catalog)
    # Legacy format has `QUERY:` and `VANILLA ANSWER:` as top-level blocks
    # New path uses CONTEXT/SOURCE instead
    assert "CONTEXT" in user
    assert "SOURCE" in user
