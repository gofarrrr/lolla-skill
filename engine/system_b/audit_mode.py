"""Audit/risk mode normalization for Lolla runtime metadata."""
from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any, MutableMapping


AUDIT_MODE_ENV_VAR = "LOLLA_AUDIT_MODE"
DEFAULT_AUDIT_MODE = "standard"
VALID_AUDIT_MODES = ("quick", "standard", "deep", "high_stakes", "stability")


class AuditModeError(ValueError):
    """Raised when an explicit audit mode is not part of the public contract."""


def normalize_audit_mode(value: object, *, env_var: str = AUDIT_MODE_ENV_VAR) -> str:
    """Return a normalized audit mode or raise for invalid explicit values."""
    raw = "" if value is None else str(value).strip()
    if not raw:
        return DEFAULT_AUDIT_MODE
    mode = raw.lower()
    if mode in VALID_AUDIT_MODES:
        return mode
    expected = ", ".join(VALID_AUDIT_MODES)
    raise AuditModeError(
        f"FATAL: invalid {env_var} {raw!r}. Expected one of: {expected}."
    )


def audit_mode_from_env(
    environ: Mapping[str, str] | None = None,
    *,
    env_var: str = AUDIT_MODE_ENV_VAR,
) -> str:
    """Read and normalize the public audit-mode environment variable."""
    env = os.environ if environ is None else environ
    return normalize_audit_mode(env.get(env_var), env_var=env_var)


def risk_mode_from_result(result: Mapping[str, Any]) -> str:
    """Read the public artifact field, defaulting older artifacts to standard."""
    return normalize_audit_mode(result.get("risk_mode"), env_var="risk_mode")


def apply_risk_mode_metadata(
    result: MutableMapping[str, Any],
    risk_mode: object,
) -> MutableMapping[str, Any]:
    """Persist the normalized public risk-mode field onto a result payload."""
    result["risk_mode"] = normalize_audit_mode(risk_mode)
    return result
