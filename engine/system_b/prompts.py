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

from .tendency_catalog import TendencyCatalog


# ---------------------------------------------------------------------------
# Shared base prompt — every cluster inherits this framing
# ---------------------------------------------------------------------------

_PASS1_BASE_SYSTEM = """You are a cognitive-bias analyst specializing in Charlie Munger's "Psychology of Human Misjudgment." Your job is to audit a vanilla answer for decision-distorting manifestations of ONE family of tendencies: {theme}

You will receive:
1. A QUERY — the decision situation and live constraints
2. A VANILLA ANSWER — a response from another AI that you are auditing

For each of the tendencies listed below (this family only — other families are handled by parallel analysts), score from 0-10 how strongly the tendency materially weakens the VANILLA ANSWER:
- 0 = Not present at all
- 1-3 = Faint or incidental signal; not decision-driving
- 4-6 = Material signal; specific evidence or a clear omission makes the recommendation less trustworthy
- 7-10 = Dominant failure mechanism; the recommendation clearly leans on it

CRITICAL RULES:
- Use the QUERY only to understand the decision context and what the answer ignored, overrode, or prematurely collapsed.
- Score based on the VANILLA ANSWER's actual reasoning. Do not import outside facts or detect a tendency just because the topic makes it plausible.
- A tendency can appear by commission or omission. Omission counts only when the answer recommends a concrete move while skipping a material check, denominator, dependency, reversal condition, pilot, or stop rule that the query makes live.
- Prefer the narrowest mechanism. If one passage could fit multiple tendencies in this family, score highest the one that best explains the failure and keep adjacent ones lower unless they rest on distinct evidence.
- A score of 4 or higher requires distinct evidence that would still matter if the strongest detected tendency in this family were removed. If the support is just a restatement, keep it at 0-3.
- Do not score a tendency merely because the answer sounds confident, uses persuasive framing, gives reasons, or mentions incentives.
- A score of 0 is perfectly valid. Most tendencies should score 0 for any given answer.
- Scores of 4 or higher should stay sparse unless the answer truly leans on the failure mechanism.
- If unsure, score lower rather than higher. False negatives are better than false positives at this stage.
- DO NOT score tendencies outside this family. Return ONLY entries for the tendencies listed below.{guardrails_block}

THE TENDENCIES IN THIS FAMILY TO SCREEN:
{tendency_list}

Respond ONLY with valid JSON matching this exact schema:
```json
{{
  "scores": [
    {{
      "tendency_id": "tendency-slug",
      "score": 0,
      "evidence": "Not detected" | "Brief 1-sentence evidence anchored to a specific passage or recommendation leap in the answer"
    }}
  ]
}}
```"""


PASS_1_TRIAGE_USER = """QUERY:
{query}

VANILLA ANSWER:
{vanilla_answer}

Use the query only as context for what the answer skipped or overrode.

Score ONLY the tendencies in this family (listed in the system prompt). Do NOT score tendencies outside this family. Respond with JSON only."""


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


def build_cluster_system_prompt(cluster: Pass1Cluster, catalog: TendencyCatalog) -> str:
    return _PASS1_BASE_SYSTEM.format(
        theme=cluster.theme,
        guardrails_block=_build_cluster_guardrails_block(cluster),
        tendency_list=_build_cluster_tendency_list(cluster, catalog),
    )


def format_pass1_cluster_prompts(
    query: str,
    vanilla_answer: str,
    catalog: TendencyCatalog,
) -> list[tuple[str, str, str]]:
    """Return [(cluster_id, system_prompt, user_prompt), ...] — one per cluster.

    The user prompt is identical across clusters (same input); the system
    prompt differs per cluster to narrow the scoring scope and guardrails.
    """
    user = PASS_1_TRIAGE_USER.format(query=query, vanilla_answer=vanilla_answer)
    return [
        (cluster.cluster_id, build_cluster_system_prompt(cluster, catalog), user)
        for cluster in PASS1_CLUSTERS
    ]


def cluster_tendency_ids(cluster_id: str) -> tuple[str, ...]:
    """Return the tendency_ids assigned to a cluster. Used for output filtering."""
    for cluster in PASS1_CLUSTERS:
        if cluster.cluster_id == cluster_id:
            return cluster.tendency_ids
    return ()


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
        f"pass1_cluster_{cluster.cluster_id}": _short_hash(build_cluster_system_prompt(cluster, catalog))
        for cluster in PASS1_CLUSTERS
    }
    hashes["pass1_triage_user"] = _short_hash(PASS_1_TRIAGE_USER)
    return hashes
