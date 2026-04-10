"""Compute SHA-256 hashes of prompt template strings for reproducibility stamping.

Each pipeline output carries a ``prompt_versions`` mapping so that any result
can be tied back to the exact prompt templates that produced it.
"""

from __future__ import annotations

import hashlib


def _short_hash(text: str, length: int = 12) -> str:
    """Return the first *length* hex characters of the SHA-256 of *text*."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def compute_prompt_versions() -> dict[str, str]:
    """Return a mapping of boundary name → short SHA-256 hex for each prompt template.

    Covers all 5 LLM prompt boundaries:
      1. pass1_triage         — system_b/prompts.py
      2. pass2_deep_check     — system_b/deep_checks.py
      3. companion_fingerprint — system_b/companion_routing.py
      4. companion_verification — system_b/companion_routing.py
      5. frame_extraction     — system_b/frame_pressure.py
    """
    from .companion_routing import get_prompt_templates as companion_templates
    from .deep_checks import PASS_2_DEEP_CHECK_SYSTEM
    from .frame_pressure import get_prompt_template as frame_template
    from .prompts import PASS_1_TRIAGE_SYSTEM

    companion = companion_templates()

    return {
        "pass1_triage": _short_hash(PASS_1_TRIAGE_SYSTEM),
        "pass2_deep_check": _short_hash(PASS_2_DEEP_CHECK_SYSTEM),
        "companion_fingerprint": _short_hash(companion["companion_fingerprint"]),
        "companion_verification": _short_hash(companion["companion_verification"]),
        "frame_extraction": _short_hash(frame_template()),
    }
