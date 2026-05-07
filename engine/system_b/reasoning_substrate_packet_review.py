from __future__ import annotations

from typing import Any, Mapping


REVIEW_TITLE = "Reasoning Substrate Packet Review"
COMPARISON_TITLE = "Reasoning Substrate Packet Comparison"
EXPECTED_STATUS = "draft_review_only"
EXPECTED_RUNTIME_POLICY = "runtime_dormant"
MAX_CARD_DETAIL_ITEMS = 1
MAX_REASON_ITEMS = 1
MAX_SUPPRESSED_ITEMS = 8


def render_reasoning_substrate_packet_review_markdown(packet: Mapping[str, Any]) -> str:
    """Render a dormant reasoning substrate packet for reviewer inspection only."""

    _assert_review_only_packet(packet)

    lines: list[str] = [f"# {REVIEW_TITLE}", ""]
    lines.extend(_packet_identity_lines(packet))
    lines.extend(["", "## Review Boundary", ""])
    lines.extend(
        [
            "- Review-only handoff material.",
            "- Compare candidate shelf usefulness; do not answer the user case.",
            "- Do not choose user-visible output or final wording.",
            "- Deterministic code labels, caps, references, and reports; the LLM/reviewer reasons.",
        ]
    )
    lines.extend(["", "## Packet Counts", ""])
    lines.extend(_counts_table(_summary(packet)))
    lines.extend(["", "## Candidate Cards", ""])

    for card in _list(packet.get("candidate_cards")):
        lines.extend(_render_card(_mapping(card)))
        lines.append("")

    lines.extend(["## Suppressed Candidates", ""])
    suppressed = _list(packet.get("suppressed_candidates"))
    if not suppressed:
        lines.append("- None")
    else:
        for item in suppressed[:MAX_SUPPRESSED_ITEMS]:
            candidate = _mapping(item)
            lines.append(
                "- "
                f"`{_text(candidate.get('model_id'))}` "
                f"({ _text(candidate.get('suppression_reason')) }; "
                f"{ _text(candidate.get('coverage_status')) })"
            )

    lines.extend(["", "## Blocked Surfaces", ""])
    for surface in _strings(packet.get("blocked_surfaces")):
        lines.append(f"- `{surface}`")

    return "\n".join(lines).rstrip() + "\n"


def render_reasoning_substrate_packet_comparison_markdown(
    *,
    before_packet: Mapping[str, Any],
    after_packet: Mapping[str, Any],
) -> str:
    """Render a deterministic reviewer comparison of two dormant packet fixtures."""

    _assert_review_only_packet(before_packet)
    _assert_review_only_packet(after_packet)

    before_summary = _summary(before_packet)
    after_summary = _summary(after_packet)
    before_cards = _cards_by_model(before_packet)
    after_cards = _cards_by_model(after_packet)

    lines: list[str] = [f"# {COMPARISON_TITLE}", ""]
    lines.extend(
        [
            "Compare handoff usefulness only.",
            "",
            "- Do not answer the user case.",
            "- Do not choose user-visible output.",
            "- Do not rank final wisdom.",
            "- Review whether the later packet improves activation, evidence, dismissal, misuse, treatment, absence, and burden.",
            "",
            "## Compared Packets",
            "",
            f"- Before: `{_text(before_packet.get('packet_id'))}`",
            f"- After: `{_text(after_packet.get('packet_id'))}`",
            "",
            "## Count Delta",
            "",
            "| Measure | Before | After | Delta |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for key, label in (
        ("candidate_card_count", "Candidate cards"),
        ("reviewed_card_count", "Reviewed cards"),
        ("graph_only_card_count", "Graph-only cards"),
        ("missing_reviewed_record_count", "Missing reviewed records"),
        ("absence_only_card_count", "Absence-only cards"),
        ("source_too_thin_count", "Source-too-thin cards"),
        ("conflicting_or_weak_support_count", "Weak/conflicting cards"),
    ):
        before_value = int(before_summary.get(key, 0) or 0)
        after_value = int(after_summary.get(key, 0) or 0)
        lines.append(
            f"| {label} | {before_value} | {after_value} | {_signed(after_value - before_value)} |"
        )

    lines.extend(["", "## Coverage Changes", ""])
    changed_rows = _coverage_changes(before_cards, after_cards)
    if not changed_rows:
        lines.append("- No card-level coverage status changes.")
    else:
        for row in changed_rows:
            lines.append(row)

    lines.extend(["", "## Reviewer Rubric", ""])
    lines.extend(
        [
            "- Activation clarity: worse / same / better",
            "- Evidence-needed clarity: worse / same / better",
            "- Do-not-use clarity: worse / same / better",
            "- Misuse-guard usefulness: worse / same / better",
            "- Treatment usefulness: worse / same / better",
            "- Absence/overclaim protection: worse / same / better",
            "- Packet burden: lighter / acceptable / too heavy",
            "- Net handoff judgment: no added depth / useful depth / useful depth but too bulky",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def _packet_identity_lines(packet: Mapping[str, Any]) -> list[str]:
    return [
        f"- Packet: `{_text(packet.get('packet_id'))}`",
        f"- Version: `{_text(packet.get('packet_version'))}`",
        f"- Status: `{_text(packet.get('status'))}`",
        f"- Runtime policy: `{_text(packet.get('runtime_policy'))}`",
        f"- Source artifacts: {', '.join(f'`{item}`' for item in _strings(packet.get('source_artifacts')))}",
    ]


def _counts_table(summary: Mapping[str, Any]) -> list[str]:
    rows = [
        ("Candidate cards", summary.get("candidate_card_count", 0)),
        ("Reviewed cards", summary.get("reviewed_card_count", 0)),
        ("Graph-only cards", summary.get("graph_only_card_count", 0)),
        ("Missing reviewed records", summary.get("missing_reviewed_record_count", 0)),
        ("Absence-only cards", summary.get("absence_only_card_count", 0)),
        ("Source-too-thin cards", summary.get("source_too_thin_count", 0)),
        ("Weak/conflicting cards", summary.get("conflicting_or_weak_support_count", 0)),
    ]
    lines = ["| Measure | Count |", "| --- | ---: |"]
    lines.extend(f"| {label} | {int(value or 0)} |" for label, value in rows)
    return lines


def _render_card(card: Mapping[str, Any]) -> list[str]:
    coverage_status = _text(card.get("coverage_status"))
    lines = [
        f"### `{_text(card.get('model_id'))}`",
        "",
        f"- Coverage: `{coverage_status}`",
        f"- Pulled by: {', '.join(f'`{item}`' for item in _strings(card.get('pulled_by')))}",
    ]
    source_custody = _mapping(card.get("source_custody"))
    lines.append(
        "- Source custody: "
        f"`{_text(source_custody.get('custody_status'))}`"
        f" / reviewed record: `{str(bool(source_custody.get('reviewed_record_available'))).lower()}`"
    )

    why_pulled = _list(card.get("why_pulled"))
    if why_pulled:
        lines.append("- Why pulled:")
        for item in why_pulled[:MAX_REASON_ITEMS]:
            reason = _mapping(item)
            evidence = _text(reason.get("evidence_quote"))
            suffix = f" Evidence: \"{evidence}\"" if evidence else ""
            lines.append(
                f"  - {_text(reason.get('source'))}: {_text(reason.get('reason'))}{suffix}"
            )

    if coverage_status == "graph_only_runtime_card":
        lines.append("- Graph-only recall material:")
        lines.extend(_graph_only_lines(card))
    else:
        lines.append("- Reviewed handoff signals:")
        lines.extend(_reviewed_signal_lines(card))

    overclaims = _strings(card.get("do_not_overclaim"))
    if overclaims:
        lines.append("- Do not overclaim:")
        for item in overclaims[:MAX_CARD_DETAIL_ITEMS]:
            lines.append(f"  - {item}")

    return lines


def _graph_only_lines(card: Mapping[str, Any]) -> list[str]:
    graph = _mapping(card.get("runtime_graph_fields"))
    lines: list[str] = []
    for field in ("select_when", "danger_when", "failure_modes", "premortem_questions"):
        item = _first_graph_item(graph.get(field))
        if item:
            lines.append(f"  - {field}: {item}")
    return lines or ["  - No compact graph fields available."]


def _reviewed_signal_lines(card: Mapping[str, Any]) -> list[str]:
    reviewed = _mapping(card.get("reviewed_affordance_fields"))
    lines: list[str] = []
    for field in (
        "affordance_ids",
        "use_when",
        "case_evidence_needed",
        "do_not_use_when",
        "misuse_guards",
        "source_evidence",
    ):
        item = _first_reviewed_item(reviewed.get(field))
        if item:
            lines.append(f"  - {field}: {item}")
    treatment = _first_treatment(reviewed.get("treatment_requirements"))
    if treatment:
        lines.append(f"  - treatment_requirements: {treatment}")
    absence = _first_absence(card.get("absence_records"))
    if absence:
        lines.append(f"  - absence_record: {absence}")
    return lines or ["  - No compact reviewed fields available."]


def _first_graph_item(value: Any) -> str:
    values = _list(value)
    if not values:
        return ""
    first = values[0]
    if isinstance(first, Mapping):
        return _text(first.get("description") or first.get("source_quote") or first)
    return _text(first)


def _first_reviewed_item(value: Any) -> str:
    values = _list(value)
    if not values:
        return ""
    first = values[0]
    if isinstance(first, Mapping):
        quote = _text(
            first.get("source_quote")
            or first.get("quote")
            or first.get("text")
            or first.get("excerpt")
        )
        affordance_id = _text(first.get("affordance_id"))
        if quote and affordance_id:
            return f"{affordance_id}: \"{quote}\""
        return _text(first)
    return _text(first)


def _first_treatment(value: Any) -> str:
    values = _list(value)
    if not values:
        return ""
    first = _mapping(values[0])
    description = _text(first.get("description"))
    requirement_id = _text(first.get("requirement_id"))
    if requirement_id and description:
        return f"{requirement_id}: {description}"
    return description or _text(first)


def _first_absence(value: Any) -> str:
    values = _list(value)
    if not values:
        return ""
    first = _mapping(values[0])
    attempted_field = _text(first.get("attempted_field"))
    status = _text(first.get("status"))
    if attempted_field and status:
        return f"{attempted_field} ({status})"
    return attempted_field or status or _text(first)


def _summary(packet: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(packet.get("coverage_summary"))


def _cards_by_model(packet: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        _text(card.get("model_id")): _mapping(card)
        for card in _list(packet.get("candidate_cards"))
        if _text(_mapping(card).get("model_id"))
    }


def _coverage_changes(
    before_cards: Mapping[str, Mapping[str, Any]],
    after_cards: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    rows: list[str] = []
    for model_id in sorted(set(before_cards) | set(after_cards)):
        before_status = _text(before_cards.get(model_id, {}).get("coverage_status"))
        after_status = _text(after_cards.get(model_id, {}).get("coverage_status"))
        if before_status == after_status:
            continue
        rows.append(f"- `{model_id}`: `{before_status}` -> `{after_status}`")
    return rows


def _assert_review_only_packet(packet: Mapping[str, Any]) -> None:
    if _text(packet.get("status")) != EXPECTED_STATUS:
        raise ValueError(f"expected {EXPECTED_STATUS} packet")
    if _text(packet.get("runtime_policy")) != EXPECTED_RUNTIME_POLICY:
        raise ValueError(f"expected {EXPECTED_RUNTIME_POLICY} packet")


def _signed(value: int) -> str:
    return f"+{value}" if value > 0 else str(value)


def _strings(value: Any) -> list[str]:
    return [_text(item) for item in _list(value) if _text(item)]


def _text(value: Any) -> str:
    return str(value or "").strip().replace("\n", " ")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
