"""Compute SHA-256 hashes of prompt template strings for reproducibility stamping.

Each pipeline output carries a ``prompt_versions`` mapping so that any result
can be tied back to the exact prompt templates that produced it.
"""

from __future__ import annotations

import hashlib


def _short_hash(text: str, length: int = 12) -> str:
    """Return the first *length* hex characters of the SHA-256 of *text*."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def compute_prompt_versions(catalog=None) -> dict[str, str]:
    """Return a mapping of boundary name → short SHA-256 hex for each prompt template.

    Covers all LLM prompt boundaries in effect:
      - Pass 1: six cluster specialists (authority, closure, incentive,
        availability, self_regard, residual) + the shared user prompt
      - pass2_deep_check            — system_b/deep_checks.py
      - companion_fingerprint       — system_b/companion_routing.py
      - companion_verification      — system_b/companion_routing.py
      - frame_extraction            — system_b/frame_pressure.py

    ``catalog`` is a loaded ``TendencyCatalog`` used to render per-cluster
    prompts with actual tendency descriptions. When omitted, cluster hashes
    are computed against an empty catalog — the template structure is still
    captured, but per-tendency descriptions are not. Production callers (the
    pipeline) should always pass the real catalog.
    """
    from .companion_routing import get_prompt_templates as companion_templates
    from .deep_checks import PASS_2_DEEP_CHECK_SYSTEM_FROM_CONTEXT
    from .frame_pressure import get_prompt_template as frame_template
    from .prompts import compute_cluster_prompt_hashes
    from .tendency_catalog import TendencyCatalog

    companion = companion_templates()

    versions: dict[str, str] = {
        "pass2_deep_check": _short_hash(PASS_2_DEEP_CHECK_SYSTEM_FROM_CONTEXT),
        "companion_fingerprint": _short_hash(companion["companion_fingerprint"]),
        "companion_verification": _short_hash(companion["companion_verification"]),
        "frame_extraction": _short_hash(frame_template()),
    }

    if catalog is None:
        catalog = TendencyCatalog(tendencies={}, alias_index={})
    versions.update(compute_cluster_prompt_hashes(catalog))

    return versions
