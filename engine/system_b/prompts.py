"""Pass 1 triage prompts — family-clustered.

Track B (Cycle-1 step 4) refactor: the single 25-tendency monolithic triage
prompt is replaced by six family-clustered specialists that run in parallel.
Each cluster scores only its 4-5 assigned tendencies with cluster-relevant
confusion guardrails, cutting obligation-load per LLM call while preserving
the full 25-tendency coverage through parallel fan-out.

Lollapalooza is deliberately unassigned: per the handover, it is not a
cluster-triageable tendency — the deterministic compound detection in
``pipeline._build_compound_groups`` surfaces lollapalooza-style compound
patterns from Pass 2 findings instead.
"""
from __future__ import annotations

from dataclasses import dataclass

from .conversation_context import ConversationContext
from .tendency_catalog import TendencyCatalog


# ---------------------------------------------------------------------------
# Shared base prompt — every cluster inherits this framing.
#
# Lane 1 audits the assistant's reasoning. SOURCE holds assistant turns
# verbatim (primary audit target — tendencies live here as commissions or
# omissions). CONTEXT holds user turns + extraction summaries
# (scaffolding for understanding what the user made live; not the primary
# scoring target).
# ---------------------------------------------------------------------------

_PASS1_BASE_SYSTEM_FROM_CONTEXT = """You are a cognitive-bias analyst specializing in Charlie Munger's "Psychology of Human Misjudgment." Your job is to audit a piece of AI reasoning for decision-distorting manifestations of ONE family of tendencies: {theme}

You will receive the user prompt in two sections:
- CONTEXT: the decision situation, framing, live constraints, dropped threads, and the user's own turns. Background only — NOT the primary audit target.
- SOURCE: the assistant's turns verbatim. This is the PRIMARY AUDIT TARGET. Tendencies live here, as commissions (what the assistant said) or omissions (what the assistant skipped given what the CONTEXT made live).

For each of the tendencies listed below (this family only — other families are handled by parallel analysts), score from 0-10 how strongly the tendency materially weakens the assistant's reasoning in SOURCE:
- 0 = Not present at all
- 1-3 = Faint or incidental signal; not decision-driving
- 4-6 = Material signal; specific evidence or a clear omission makes the recommendation less trustworthy
- 7-10 = Dominant failure mechanism; the recommendation clearly leans on it

CRITICAL RULES:
- Score the ASSISTANT's reasoning as shown in SOURCE. Use CONTEXT to understand what the decision required the assistant to address (constraints, live risks, what the user made vivid, what was dropped).
- A tendency can fire in three shapes, all grounded in the assistant's reasoning in SOURCE:
  (1) COMMISSION — the assistant explicitly says something that exhibits the tendency.
  (2) OMISSION — the assistant commits to a move while skipping a material check, denominator, dependency, reversal condition, pilot, or stop rule that CONTEXT made live. Hedging, caveating, or staging the answer in steps does NOT neutralize an omission: a structured multi-step plan that commits to a path without ever naming a reversal trigger or stop condition still carries the tendency.
  (3) UNCRITICAL ACCEPTANCE — the assistant recycles vivid or authoritative CONTEXT material as decision-driving without testing it. Tendencies like availability-misweighing, social-proof, and authority-misinfluence frequently fire in this shape: the evidence of the tendency is the assistant's HANDLING of user-provided vividness, not the user's text itself.
- Do not import outside facts or detect a tendency just because the topic makes it plausible.
- Prefer the narrowest mechanism. If one passage could fit multiple tendencies in this family, score highest the one that best explains the failure and keep adjacent ones lower unless they rest on distinct evidence.
- A score of 4 or higher requires distinct evidence that would still matter if the strongest detected tendency in this family were removed. If the support is just a restatement, keep it at 0-3.
- Do not score a tendency merely because the assistant sounds confident, uses persuasive framing, gives reasons, or mentions incentives.
- Symmetrically: do NOT score a tendency at 0 merely because the assistant is hedged, structured, caveated, or shows multi-step reasoning. Tendencies frequently fire INSIDE careful framing. The test is whether the recommendation depends on a specific bias mechanism (commission, omission, or uncritical acceptance), not whether the prose sounds careful. A confident-sounding paragraph and a 14-turn structured plan that both skip the same reversal trigger fire the same tendency.
- When SOURCE spans multiple assistant turns, evaluate the cumulative reasoning trajectory, not just any single turn. A tendency may fire across the sequence (e.g., the assistant progressively commits to a plan without ever naming the conditions under which it would pull back) even when no single turn is reckless on its own.
- A score of 0 is perfectly valid. Most tendencies should score 0 for any given answer.
- Scores of 4 or higher should stay sparse unless the assistant's reasoning truly leans on the failure mechanism.
- If unsure, score lower rather than higher. False negatives are better than false positives — but a long, well-structured answer that commits to an irreversible move without naming the reversal triggers CONTEXT made live is not an "unsure" case; it is an omission worth scoring.
- DO NOT score tendencies outside this family. Return ONLY entries for the tendencies listed below.
- ENUM CHECKLIST: Before finalizing your scores, verify you've considered EACH tendency in this family individually — not just the ones that surface verbatim in SOURCE. Some tendencies manifest as omission (the assistant skipping a check CONTEXT made live) rather than as explicit claims. Return 0 when genuinely absent; do not skip a tendency just because it is not visible at surface level.{guardrails_block}

THE TENDENCIES IN THIS FAMILY TO SCREEN:
{tendency_list}

Respond ONLY with valid JSON matching this exact schema:
```json
{{
  "scores": [
    {{
      "tendency_id": "tendency-slug",
      "score": 0,
      "evidence": "Not detected" | "Brief 1-sentence evidence anchored to a specific assistant passage or reasoning leap in SOURCE"
    }}
  ]
}}
```"""


# Template-only hash surface for prompt versioning. The rendered user prompt
# is built dynamically from the conversation, but the stable section labels and
# instructions still deserve a reproducibility stamp.
PASS_1_TRIAGE_USER_FROM_CONTEXT_TEMPLATE = """CONTEXT (background for understanding what the user made live — NOT the primary audit target):
- Decision situation: {decision_situation}
- Framing (how the user posed the question): {original_framing}
- Live constraints:
{live_constraints}
- Dropped threads:
{dropped_threads}
- User turns (CONTEXT only — what the user made live; not the primary scoring target):
{user_turns}

SOURCE (the PRIMARY AUDIT TARGET — assistant turns verbatim; score tendencies against commissions or omissions visible here):
{assistant_turns}

Score ONLY the tendencies in this family (listed in the system prompt). Respond with JSON only."""


# ---------------------------------------------------------------------------
# Confusion guardrails — shared library, keyed by short name
# Verbatim from the pre-refactor monolithic PASS_1_TRIAGE_SYSTEM.
# ---------------------------------------------------------------------------

_CONFUSION_GUARDRAILS: dict[str, str] = {
    "authority": "Authority Misinfluence: prestige, executive confidence, a trusted referral, brand status, strategic seniority, or the status of a prestigious customer/prospect is treated as proof or as license to bypass standing controls, policy, or challenge rights. Keep this in play when the answer grants a one-time exception because the customer, executive, or sponsor is too important to force through the normal control path.",
    "social_proof": "Social Proof: peer behavior, market legitimacy, portfolio track records, advisory council consensus, \"others are doing it,\" or the visible success of a small peer group is treated as proof that the decision is correct. Keep this in play when the consensus pool is self-selecting (e.g., an advisory council of power users, a VC's own portfolio), when dissent is structurally muted, or when what a visible peer group did replaces independent analysis of whether it applies here.",
    "mere_association": "Influence-from-Mere-Association: a superficial halo, label, or status marker stands in for evidence.",
    "availability": "Availability Misweighing: vivid recent metrics, anecdotes, a single conversation, or a narrow visible operational slice crowd out denominators or base rates. Keep this in play when the answer treats a visible usage rate, ticket burden, or local maintenance cost as enough to deprecate, reallocate, or accelerate without checking broader denominators, dependency chains, migration burden, or concentration risk.",
    "doubt_avoidance": "Doubt Avoidance: the answer closes uncertainty early to avoid delay or ambiguity; decisiveness alone is not enough.",
    "deprival": "Deprival Superreaction: threatened loss or near-miss drives the reasoning; not every downside, friction, or customer dislike counts.",
    "liking_loving": "Liking/Loving: charisma, familiarity, or admiration causes faults or checks to be ignored.",
    "stress": "Stress Influence: time, quota, or crisis pressure itself distorts cognition. Keep this in play when the answer uses a looming deadline, quarter-end target, rush, or crisis cadence to justify compressing review, bypassing normal verification, or granting a one-time shortcut \"just for now.\" Stress can coexist with incentives or threatened loss when the clock itself is the reason normal scrutiny gets thinner.",
    "reward_punishment": "Reward and Punishment Superresponse: incentives are the causal driver, not just generic upside or downside. If status or strategic importance is being used to override policy, especially through a one-time exception to standing controls, keep authority in play rather than collapsing everything into incentives.",
    "inconsistency_avoidance": "Inconsistency Avoidance: commitment to the current path or status quo drives the answer; not every rollout plan counts.",
    "reciprocation": "Reciprocation: returning a favor, concession, or endorsement drives the answer; not simply trusting someone's opinion.",
}


# ---------------------------------------------------------------------------
# Cluster definitions (Phase 1 research: research/track-b-pass1-clustering-phase1.md)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Pass1Cluster:
    cluster_id: str
    theme: str
    tendency_ids: tuple[str, ...]
    guardrail_keys: tuple[str, ...]


PASS1_CLUSTERS: tuple[Pass1Cluster, ...] = (
    Pass1Cluster(
        cluster_id="authority",
        theme="Authority and Social Influence — judgment distorted by prestige, peer behavior, halo, affection, or favor.",
        tendency_ids=(
            "authority-misinfluence-tendency",
            "social-proof-tendency",
            "influence-from-mere-association-tendency",
            "liking-loving-tendency",
            "reciprocation-tendency",
        ),
        guardrail_keys=("authority", "social_proof", "mere_association", "liking_loving", "reciprocation"),
    ),
    Pass1Cluster(
        cluster_id="closure",
        theme="Closure Under Pressure — time, threatened loss, or prior commitment driving premature closure of uncertainty.",
        tendency_ids=(
            "doubt-avoidance-tendency",
            "inconsistency-avoidance-tendency",
            "deprival-superreaction-tendency",
            "stress-influence-tendency",
        ),
        guardrail_keys=("doubt_avoidance", "deprival", "stress", "inconsistency_avoidance"),
    ),
    Pass1Cluster(
        cluster_id="incentive",
        theme="Reward, Incentive, and Fairness Norm — motivational forces as the causal mechanism driving the claim.",
        tendency_ids=(
            "reward-and-punishment-superresponse-tendency",
            "envy-jealousy-tendency",
            "kantian-fairness-tendency",
        ),
        guardrail_keys=("reward_punishment",),
    ),
    Pass1Cluster(
        cluster_id="availability",
        theme="Availability and Denominator Errors — vivid recent evidence or extreme anchors crowding out base rates.",
        tendency_ids=(
            "availability-misweighing-tendency",
            "contrast-misreaction-tendency",
        ),
        guardrail_keys=("availability",),
    ),
    Pass1Cluster(
        cluster_id="self_regard",
        theme="Self-Regard and Emotion — self-referential filters distorting the reasoning toward a preferred answer.",
        tendency_ids=(
            "overoptimism-tendency",
            "excessive-self-regard-tendency",
            "simple-pain-avoiding-psychological-denial",
            "disliking-hating-tendency",
            "reason-respecting-tendency",
        ),
        guardrail_keys=(),
    ),
    Pass1Cluster(
        cluster_id="residual",
        theme="Quirky Residual — tendencies that don't fit the standard failure-mode taxonomy (Munger's quirky chapters).",
        tendency_ids=(
            "curiosity-tendency",
            "use-it-or-lose-it-tendency",
            "drug-misinfluence-tendency",
            "senescence-misinfluence-tendency",
            "twaddle-tendency",
        ),
        guardrail_keys=(),
    ),
)


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def _build_cluster_tendency_list(cluster: Pass1Cluster, catalog: TendencyCatalog) -> str:
    """Return the `N. [id] Display Name: Description` block for a cluster's tendencies."""
    lines: list[str] = []
    for tendency_id in cluster.tendency_ids:
        try:
            tendency = catalog.lookup(tendency_id)
        except KeyError:
            # Skip silently — catalog mismatches would have been warned at load time.
            continue
        lines.append(
            f"{tendency.tendency_number}. [{tendency.tendency_id}] "
            f"{tendency.display_name}: {tendency.description}"
        )
    return "\n".join(lines)


def _build_cluster_guardrails_block(cluster: Pass1Cluster) -> str:
    """Return a `\n\nCOMMON CONFUSION GUARDRAILS:\n- ...` block, or empty string if none apply."""
    if not cluster.guardrail_keys:
        return ""
    lines = ["", "", "COMMON CONFUSION GUARDRAILS (this family):"]
    for key in cluster.guardrail_keys:
        if key in _CONFUSION_GUARDRAILS:
            lines.append(f"- {_CONFUSION_GUARDRAILS[key]}")
    return "\n".join(lines)


def cluster_tendency_ids(cluster_id: str) -> tuple[str, ...]:
    """Return the tendency_ids assigned to a cluster. Used for output filtering."""
    for cluster in PASS1_CLUSTERS:
        if cluster.cluster_id == cluster_id:
            return cluster.tendency_ids
    return ()


def _joined_assistant_turns_text(context: ConversationContext) -> str:
    """Join all assistant-turn text. Empty string if no assistant turns.

    Used by Pass 2 context formatting, embedding signal, and any caller that
    needs a flattened view of the assistant reasoning under the new contract.
    """
    return "\n\n".join(t.text for t in context.turns if t.speaker == "assistant")


def build_cluster_system_prompt_from_context(cluster: Pass1Cluster, catalog: TendencyCatalog) -> str:
    """Build the per-cluster system prompt for the conversation-first path."""
    return _PASS1_BASE_SYSTEM_FROM_CONTEXT.format(
        theme=cluster.theme,
        guardrails_block=_build_cluster_guardrails_block(cluster),
        tendency_list=_build_cluster_tendency_list(cluster, catalog),
    )


def _format_pass1_from_context_user_prompt(context: ConversationContext) -> str:
    """Build the CONTEXT/SOURCE-labelled Pass 1 user prompt body.

    CONTEXT carries extraction summaries + user turns (scaffolding for
    understanding what was live). SOURCE carries the assistant turns verbatim
    (the primary audit target for Lane 1)."""
    ext = context.extraction
    parts: list[str] = [
        "CONTEXT (background for understanding what the user made live — NOT the primary audit target):",
    ]
    if ext.decision_situation:
        parts.append(f"- Decision situation: {ext.decision_situation}")
    if ext.original_framing:
        parts.append(f"- Framing (how the user posed the question): {ext.original_framing}")
    if ext.live_constraints:
        parts.append("- Live constraints:")
        for c in ext.live_constraints:
            status = (c.status or "active").upper()
            weight = (c.weight or "situational").upper()
            tag = status if status == "ACTIVE" else f"{status}/{weight}"
            parts.append(f"  - [{tag}] {c.constraint} (turn {c.introduced_turn})")
    if ext.dropped_threads:
        parts.append("- Dropped threads:")
        for d in ext.dropped_threads:
            line = (
                f"  - {d.thread} (raised by {d.raised_by or '?'} turn {d.raised_turn}, "
                f"status: {d.status or '?'})"
            )
            if d.superseded_by:
                line += f", superseded_by: {d.superseded_by}"
            parts.append(line)

    user_turns = [t for t in context.turns if t.speaker == "user"]
    if user_turns:
        parts.append("- User turns (CONTEXT only — what the user made live; not the primary scoring target):")
        for t in user_turns:
            parts.append(f"  [Turn {t.turn_index}] USER: {t.text}")

    parts.append("")
    parts.append(
        "SOURCE (the PRIMARY AUDIT TARGET — assistant turns verbatim; score tendencies against commissions or omissions visible here):"
    )
    assistant_turns = [t for t in context.turns if t.speaker == "assistant"]
    if not assistant_turns:
        parts.append("(no assistant turns present)")
    else:
        for t in assistant_turns:
            parts.append(f"[Turn {t.turn_index}] ASSISTANT:")
            parts.append(t.text)
            parts.append("")

    parts.append(
        "Score ONLY the tendencies in this family (listed in the system prompt). Respond with JSON only."
    )
    return "\n".join(parts)


def format_pass1_cluster_prompts_from_context(
    context: ConversationContext,
    catalog: TendencyCatalog,
) -> list[tuple[str, str, str]]:
    """Phase 2c conversation-first entry point for Pass 1.

    Returns [(cluster_id, system_prompt, user_prompt), ...] — one per cluster.
    User prompt is shared across clusters (same input); system prompt differs
    per cluster to narrow scope and confusion guardrails.
    """
    user = _format_pass1_from_context_user_prompt(context)
    return [
        (cluster.cluster_id, build_cluster_system_prompt_from_context(cluster, catalog), user)
        for cluster in PASS1_CLUSTERS
    ]


def compute_cluster_prompt_hashes(catalog: TendencyCatalog) -> dict[str, str]:
    """Return a mapping of cluster_id → short SHA-256 hex for each cluster's system prompt.

    Used by prompt_versioning to stamp every pipeline result with the exact
    cluster prompt hashes in effect. The user prompt is shared and captured
    by a single `pass1_triage_user` hash for completeness.
    """
    import hashlib

    def _short_hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]

    hashes = {
        f"pass1_cluster_{cluster.cluster_id}": _short_hash(
            build_cluster_system_prompt_from_context(cluster, catalog)
        )
        for cluster in PASS1_CLUSTERS
    }
    hashes["pass1_triage_user"] = _short_hash(PASS_1_TRIAGE_USER_FROM_CONTEXT_TEMPLATE)
    return hashes
