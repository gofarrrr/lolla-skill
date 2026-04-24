#!/usr/bin/env python3
"""Phase 2c ablation: architecture vs volume on Marcus Pass 1 triage.

Mirrors Phase 2b's ablation approach. Tests whether the architectural feature
(SOURCE = assistant turns verbatim with turn structure) is load-bearing for
Lane 1 detection, independent of content volume.

Setup:
  - Full new-path prompt = CONTEXT (extraction summaries + user turns +
    assistant turns as CONTEXT) + SOURCE (assistant turns verbatim).
  - Ablation prompt = CONTEXT trimmed to synthesized_position[:500] only
    (matches old-path vanilla_answer[:1000] preamble volume). SOURCE
    unchanged — assistant turns verbatim.
  - Old-path full prompt = query + vanilla_answer[:40K].

Target case: Marcus. Full new-path detects {availability, deprival-superreaction,
contrast-misreaction}. Old path detects {availability, inconsistency-avoidance}.
If ablation still triggers deprival + contrast → the SOURCE architectural
feature (turn-structured assistant text) is doing the work. If ablation
reverts to old-path-like detections → volume was the mechanism.

Caveat (PM guardrail): this is one-case evidence. Marcus's reasoning uses
specific numerical passages ($11M vs $5M) that are well-preserved in
turn-structured SOURCE; other cases may depend differently on CONTEXT.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "engine"))

# Load .env for OPENROUTER_API_KEY + embedding keys
for line in (REPO_ROOT / ".env").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    if line.startswith("export "):
        line = line[7:].strip()
    k, _, v = line.partition("=")
    k = k.strip()
    v = v.strip().strip('"').strip("'")
    if k and k not in os.environ:
        os.environ[k] = v

from system_b.boundary_provider import load_boundary_client_from_env
from system_b.conversation_loader import load_conversation_context
from system_b.prompts import (
    PASS1_CLUSTERS,
    build_cluster_system_prompt_from_context,
    _format_pass1_from_context_user_prompt,
)
from system_b.tendency_catalog import TendencyCatalog


def _trimmed_pass1_user(context) -> str:
    """Ablation user-prompt: SOURCE kept (architecture), CONTEXT volume-matched
    to old-path vanilla_answer preamble."""
    parts: list[str] = [
        "CONTEXT (scaffolding — audit the assistant's reasoning in SOURCE):",
    ]
    synthesized = context.extraction.synthesized_position or ""
    if synthesized:
        parts.append(f"- Synthesized position: {synthesized[:500]}")
    parts.append("")
    parts.append(
        "SOURCE (PRIMARY AUDIT TARGET — assistant turns verbatim; score tendencies against commissions or omissions visible here):"
    )
    for t in context.turns:
        if t.speaker == "assistant":
            parts.append(f"[Turn {t.turn_index}] ASSISTANT:")
            parts.append(t.text)
            parts.append("")
    parts.append(
        "Score ONLY the tendencies in this family (listed in the system prompt). Respond with JSON only."
    )
    return "\n".join(parts)


def main() -> int:
    ext_path = REPO_ROOT / "research/test-cases/phase2c-marcus-controlled-comparison-2026-04-24/marcus_fresh_extraction.json"
    conv_path = REPO_ROOT / "research/test-cases/phase2c-marcus-controlled-comparison-2026-04-24/lolla_20260422T155622Z_conversation.txt"
    ctx = load_conversation_context(ext_path, conv_path)

    full_user = _format_pass1_from_context_user_prompt(ctx)
    trimmed = _trimmed_pass1_user(ctx)

    print("=== Marcus — Phase 2c Pass 1 ablation setup ===")
    print(f"  full new-path user prompt length: {len(full_user)} chars")
    print(f"  trimmed ablation user prompt length: {len(trimmed)} chars")
    print()

    catalog = TendencyCatalog.load(REPO_ROOT)
    boundary = load_boundary_client_from_env("openrouter")

    # Run all 6 clusters with the ablation prompt
    print("=== ablation Pass 1 runs (6 clusters, trimmed CONTEXT) ===")
    triggered_ids: list[str] = []
    for cluster in PASS1_CLUSTERS:
        system_prompt = build_cluster_system_prompt_from_context(cluster, catalog)
        raw = boundary.run_json(system_prompt, trimmed)
        scores = raw.get("scores") or []
        non_zero = [(s.get("tendency_id"), s.get("score", 0)) for s in scores if s.get("score", 0) >= 4]
        print(f"  cluster={cluster.cluster_id}: scored≥4 → {non_zero}")
        triggered_ids.extend(tid for tid, _ in non_zero if tid)

    print()
    print("=== interpretation ===")
    print(f"  ablation triggered (≥4): {sorted(set(triggered_ids))}")
    print(f"  full new-path detected (from Marcus A/B): ['deprival-superreaction-tendency', 'availability-misweighing-tendency', 'contrast-misreaction-tendency']")
    print(f"  old-path detected (from Marcus A/B): ['availability-misweighing-tendency', 'inconsistency-avoidance-tendency']")

    ablation_set = set(triggered_ids)
    new_set = {"deprival-superreaction-tendency", "availability-misweighing-tendency", "contrast-misreaction-tendency"}
    old_set = {"availability-misweighing-tendency", "inconsistency-avoidance-tendency"}

    if "deprival-superreaction-tendency" in ablation_set or "contrast-misreaction-tendency" in ablation_set:
        print("  RESULT: architecture wins — SOURCE (assistant turns verbatim) alone is")
        print("          sufficient to surface the financial-framing tendencies (deprival/contrast)")
        print("          that old-path misses. The architectural feature is load-bearing independently of volume.")
    elif ablation_set & old_set == old_set or "inconsistency-avoidance-tendency" in ablation_set:
        print("  RESULT: volume wins — with CONTEXT trimmed, detection reverts toward old-path shape.")
        print("          The full-prompt's new tendency set was driven by CONTEXT content volume,")
        print("          not by the SOURCE-section architectural feature.")
    else:
        print(f"  RESULT: ambiguous — ablation set differs from both full new and old.")
        print(f"          new∩ablation: {ablation_set & new_set}")
        print(f"          old∩ablation: {ablation_set & old_set}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
