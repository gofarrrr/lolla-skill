#!/usr/bin/env python3
"""Phase 2b ablation: isolate architecture-vs-volume on classification.

Runs the new-path question_classification N=3 times with a TRIMMED
user-prompt body:
  - CONTEXT reduced to `synthesized_position[:500]` only (matches old-path
    vanilla_answer[:1000] preamble volume)
  - SOURCE = user turns verbatim (the architectural feature)

If qtype still shifts to `action-planning` on friendship_money, the
architectural feature (user-turn SOURCE) is doing work independently of
content volume. If qtype reverts to `decision-evaluation`, volume was the
mechanism. Either answer resolves the open question.

Caveat (per PM guardrail): this is one-case evidence. friendship_money has
unusually clear user intent ("I'm going to say no"). Other corpus cases
have more ambiguous framing and would need their own ablation to claim
corpus-level architectural isolation.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "engine"))

# Load env from .env so OPENROUTER_API_KEY is available
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
from system_b.structural_coverage import (
    _QUESTION_CLASSIFICATION_SYSTEM_FROM_CONTEXT,
    _format_classification_from_context_user_prompt,
)


def trimmed_prompt(context) -> str:
    """Ablation user-prompt: SOURCE kept (architecture), CONTEXT volume-matched to old-path."""
    parts: list[str] = [
        "CONTEXT (scaffolding — classify the user's actual question, not this summary):",
    ]
    # Trimmed: ONLY synthesized_position (≤500 chars) — matches the volume that
    # old-path's vanilla_answer[:1000] carries for classification. Drop
    # decision_situation, original_framing, constraints, dropped_threads,
    # assistant replies — all of which are extra content in the full prompt.
    synthesized = context.extraction.synthesized_position or ""
    if synthesized:
        parts.append(f"- Synthesized position: {synthesized[:500]}")
    parts.append("")
    parts.append(
        "SOURCE (the user's actual turns — first user turn is the canonical question anchor):"
    )
    for t in context.turns:
        if t.speaker == "user":
            parts.append(f"[Turn {t.turn_index}] USER:")
            parts.append(t.text)
            parts.append("")
    return "\n".join(parts)


def main() -> int:
    ext_path = REPO_ROOT / "research/test-cases/phase2b-lane4-equivalence-2026-04-23/_scratch/friendship_money_extraction.json"
    conv_path = REPO_ROOT / "research/test-cases/case_friendship_money_conversation.txt"
    ctx = load_conversation_context(ext_path, conv_path)

    full_prompt = _format_classification_from_context_user_prompt(ctx)
    trimmed = trimmed_prompt(ctx)

    print("=== friendship_money — ablation setup ===")
    print(f"  full new-path prompt length: {len(full_prompt)} chars")
    print(f"  trimmed ablation prompt length: {len(trimmed)} chars")
    print(f"  old-path classifier volume (query + va[:1000]): ~1839 chars")
    print()

    boundary = load_boundary_client_from_env("openrouter")

    print("=== ablation runs (N=3, new-path system prompt + trimmed user prompt) ===")
    results: list[str] = []
    for i in range(3):
        raw = boundary.run_json(_QUESTION_CLASSIFICATION_SYSTEM_FROM_CONTEXT, trimmed)
        qtype = str(raw.get("question_type", "")).strip()
        results.append(qtype)
        print(f"  run {i+1}: question_type = {qtype!r}")
    print()

    print("=== interpretation ===")
    print(f"  ablation results: {results}")
    print(f"  old-path full run (observed): ['decision-evaluation'] × 3")
    print(f"  new-path full run (observed): ['action-planning'] × 3")
    print()
    stable = len(set(results)) == 1
    if not stable:
        print("  RESULT: classification unstable in ablation — can't conclude")
        return 1
    ablation_qtype = results[0]
    if ablation_qtype == "action-planning":
        print("  RESULT: architecture wins — SOURCE (user turns) alone produces")
        print("          action-planning classification even with minimal CONTEXT volume.")
        print("          The architectural feature is load-bearing independently of volume.")
    elif ablation_qtype == "decision-evaluation":
        print("  RESULT: volume wins — with CONTEXT trimmed, qtype reverts to")
        print("          decision-evaluation. The full-prompt's shift was driven by")
        print("          content volume, not by the SOURCE-section architectural feature.")
    else:
        print(f"  RESULT: unexpected qtype {ablation_qtype!r} — investigate")

    return 0


if __name__ == "__main__":
    sys.exit(main())
