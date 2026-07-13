"""Prospective reasoning-content exclusion inspection for R3 experiments.

This module does not interpret reasoning, model quality, or answer semantics.
It only distinguishes returned reasoning content from empty or metadata-only
provider envelopes. Malformed or unknown shapes fail closed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


MESSAGE_CONTENT_FIELDS = ("reasoning", "reasoning_content")
DETAIL_CONTENT_FIELDS = ("text", "summary", "data", "content", "reasoning")
DETAIL_METADATA_FIELDS = ("type", "id", "format", "index", "signature")
KNOWN_DETAIL_TYPES = (
    "reasoning.text",
    "reasoning.summary",
    "reasoning.encrypted",
)


@dataclass(frozen=True)
class ReasoningExclusionInspection:
    """Value-free result of inspecting one assistant message envelope."""

    status: str
    exclusion_satisfied: bool
    content_present: bool
    metadata_only: bool
    malformed: bool
    detail_count: int
    content_locations: tuple[str, ...]
    metadata_locations: tuple[str, ...]
    malformed_locations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a commit-safe representation without provider values."""

        return {
            "status": self.status,
            "exclusion_satisfied": self.exclusion_satisfied,
            "content_present": self.content_present,
            "metadata_only": self.metadata_only,
            "malformed": self.malformed,
            "detail_count": self.detail_count,
            "content_locations": list(self.content_locations),
            "metadata_locations": list(self.metadata_locations),
            "malformed_locations": list(self.malformed_locations),
            "provider_values_included": False,
        }


def _inspect_text_field(
    value: object,
    *,
    path: str,
    content_locations: list[str],
    malformed_locations: list[str],
) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        malformed_locations.append(path)
        return
    if value.strip():
        content_locations.append(path)


def _inspect_metadata_field(
    key: str,
    value: object,
    *,
    path: str,
    metadata_locations: list[str],
    malformed_locations: list[str],
) -> None:
    if key == "type":
        if not isinstance(value, str) or value not in KNOWN_DETAIL_TYPES:
            malformed_locations.append(path)
            return
    elif key == "index":
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            malformed_locations.append(path)
            return
    elif value is not None and not isinstance(value, str):
        malformed_locations.append(path)
        return
    if value not in (None, ""):
        metadata_locations.append(path)


def inspect_reasoning_exclusion(
    message: Mapping[str, object],
) -> ReasoningExclusionInspection:
    """Inspect whether a message satisfies a no-returned-reasoning contract.

    Empty and null content fields are clean. A documented detail record that
    carries only type/format/id/index/signature metadata is also clean. Any
    non-empty reasoning content, malformed container, malformed field type, or
    unknown detail field blocks the exclusion gate.
    """

    content_locations: list[str] = []
    metadata_locations: list[str] = []
    malformed_locations: list[str] = []
    reasoning_surface_present = False

    for field in MESSAGE_CONTENT_FIELDS:
        if field not in message:
            continue
        reasoning_surface_present = True
        _inspect_text_field(
            message.get(field),
            path=f"/message/{field}",
            content_locations=content_locations,
            malformed_locations=malformed_locations,
        )

    detail_count = 0
    if "reasoning_details" in message:
        reasoning_surface_present = True
        details = message.get("reasoning_details")
        if details is None:
            pass
        elif not isinstance(details, list):
            malformed_locations.append("/message/reasoning_details")
        else:
            detail_count = len(details)
            for index, item in enumerate(details):
                item_path = f"/message/reasoning_details/{index}"
                if not isinstance(item, Mapping):
                    malformed_locations.append(item_path)
                    continue
                unknown_fields = sorted(
                    set(item) - set(DETAIL_CONTENT_FIELDS) - set(DETAIL_METADATA_FIELDS)
                )
                malformed_locations.extend(
                    f"{item_path}/{field}" for field in unknown_fields
                )
                if "type" not in item:
                    malformed_locations.append(f"{item_path}/type")
                for key in DETAIL_METADATA_FIELDS:
                    if key in item:
                        _inspect_metadata_field(
                            key,
                            item.get(key),
                            path=f"{item_path}/{key}",
                            metadata_locations=metadata_locations,
                            malformed_locations=malformed_locations,
                        )
                for key in DETAIL_CONTENT_FIELDS:
                    if key in item:
                        _inspect_text_field(
                            item.get(key),
                            path=f"{item_path}/{key}",
                            content_locations=content_locations,
                            malformed_locations=malformed_locations,
                        )

    content = tuple(sorted(set(content_locations)))
    metadata = tuple(sorted(set(metadata_locations)))
    malformed = tuple(sorted(set(malformed_locations)))
    if content:
        status = "reasoning_content_present"
    elif malformed:
        status = "reasoning_shape_malformed"
    elif metadata:
        status = "reasoning_metadata_only"
    elif reasoning_surface_present:
        status = "reasoning_empty"
    else:
        status = "reasoning_absent"
    exclusion_satisfied = not content and not malformed
    return ReasoningExclusionInspection(
        status=status,
        exclusion_satisfied=exclusion_satisfied,
        content_present=bool(content),
        metadata_only=status == "reasoning_metadata_only",
        malformed=bool(malformed),
        detail_count=detail_count,
        content_locations=content,
        metadata_locations=metadata,
        malformed_locations=malformed,
    )
