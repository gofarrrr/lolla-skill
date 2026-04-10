"""Lightweight schema validation for LLM JSON parsing boundaries.

All functions follow warn-and-default semantics: log a warning when the
payload doesn't match expectations, but return a usable default rather
than crashing.  The only exception is ``require_field`` which raises
``BoundaryValidationError`` when a truly required field is missing or
has the wrong type — callers decide whether to catch or propagate.
"""

from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)


class BoundaryValidationError(Exception):
    """Raised when a required field fails validation at an LLM boundary."""

    def __init__(self, boundary: str, field: str, expected: str, received: str) -> None:
        self.boundary = boundary
        self.field = field
        self.expected = expected
        self.received = received
        super().__init__(
            f"[{boundary}] field '{field}': expected {expected}, got {received}"
        )


def require_field(
    payload: dict,
    field: str,
    expected_type: type,
    boundary: str,
) -> object:
    """Return *payload[field]* if present and of *expected_type*, else raise."""
    if field not in payload:
        raise BoundaryValidationError(
            boundary=boundary,
            field=field,
            expected=expected_type.__name__,
            received="<missing>",
        )
    value = payload[field]
    if not isinstance(value, expected_type):
        raise BoundaryValidationError(
            boundary=boundary,
            field=field,
            expected=expected_type.__name__,
            received=type(value).__name__,
        )
    return value


def optional_field(
    payload: dict,
    field: str,
    expected_type: type,
    default: object,
    boundary: str,
) -> object:
    """Return *payload[field]* if present and of *expected_type*.

    If missing, return *default* silently.
    If present but wrong type, log a warning and return *default*.
    """
    if field not in payload:
        return default
    value = payload[field]
    if not isinstance(value, expected_type):
        _LOGGER.warning(
            "[%s] field '%s': expected %s, got %s — using default",
            boundary,
            field,
            expected_type.__name__,
            type(value).__name__,
        )
        return default
    return value


def require_list_of_dicts(
    payload: dict,
    field: str,
    boundary: str,
) -> list[dict]:
    """Return *payload[field]* validated as ``list[dict]``.

    - Missing field → empty list + warning.
    - Wrong top-level type → empty list + warning.
    - Non-dict items inside the list are silently dropped.
    """
    raw = payload.get(field)
    if raw is None:
        _LOGGER.warning(
            "[%s] field '%s': expected list[dict], got <missing> — returning []",
            boundary,
            field,
        )
        return []
    if not isinstance(raw, list):
        _LOGGER.warning(
            "[%s] field '%s': expected list[dict], got %s — returning []",
            boundary,
            field,
            type(raw).__name__,
        )
        return []
    return [item for item in raw if isinstance(item, dict)]


def coerce_str(value: object, default: str = "") -> str:
    """Coerce *value* to str, returning *default* on None."""
    if value is None:
        return default
    return str(value)


def coerce_int(value: object, default: int = 0) -> int:
    """Coerce *value* to int, returning *default* on failure."""
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def coerce_float(value: object, default: float = 0.0) -> float:
    """Coerce *value* to float, returning *default* on failure."""
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
