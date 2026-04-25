from __future__ import annotations

from dataclasses import dataclass

from .boundary_validation import coerce_float, coerce_int, coerce_str
from .conversation_context import ConversationContext
from .packet_builders.lane4 import Lane4Packet
from .tendency_catalog import ModelBinding, TendencyCatalog


_TENDENCY_SPECIFIC_GUIDANCE: dict[str, str] = {
    "authority-misinfluence-tendency": (
        "Detect when prestige, executive confidence, a trusted referral, or brand status is"
        " treated as proof that substitutes for independent evidence, or when status,"
        " strategic importance, seniority, or a prestigious customer/prospect is used as"
        " license to bypass standing controls, policy, or challenge rights. Keep this label"
        " in play when the answer grants a one-time exception because the counterparty,"
        " sponsor, or executive is treated as too important for the normal control path."
        " Do not use this label when the reasoning is mainly imitation of peers, a generic"
        " halo effect, or pure incentive pressure with no deference-to-rank mechanism."
    ),
    "availability-misweighing-tendency": (
        "Detect when recent, vivid, salient, or single-source evidence substitutes for"
        " denominators or base rates. Do not use this label if no such salient evidence is"
        " doing the work."
    ),
    "doubt-avoidance-tendency": (
        "Detect premature closure used to escape uncertainty, delay, ambiguity, or"
        " puzzlement itself. Keep this label in play when the reasoning prefers any"
        " conclusion over no conclusion because ambiguity feels intolerable. Mere"
        " decisiveness, urgency, or a concrete recommendation is not enough."
    ),
    "deprival-superreaction-tendency": (
        "Detect only when threatened loss, near-miss, or loss of something already enjoyed is"
        " driving the leap. Do not use this label for ordinary downside, friction, or generic"
        " customer resistance."
    ),
    "liking-loving-tendency": (
        "Detect only when admiration, charisma, familiarity, or affection toward a person or"
        " institution causes faults or missing checks to be ignored. Generic positive framing is"
        " not enough."
    ),
    "stress-influence-tendency": (
        "Detect only when time pressure, quota pressure, or crisis pressure is itself causing"
        " cognitive simplification or reversal. Keep this label in play when the answer uses"
        " a looming deadline, quarter-end target, rush, or crisis tempo to compress review,"
        " bypass normal verification, or approve a one-time shortcut. Stress can coexist with"
        " incentives or threatened loss when the clock itself is what makes scrutiny thinner."
        " High stakes alone are not enough."
    ),
    "social-proof-tendency": (
        "Detect when peer behavior, portfolio track records, advisory council consensus, market"
        " adoption, or what a visible peer group did is used as proof that the decision is correct."
        " Keep this label in play when the consensus pool is self-selecting (e.g., advisory councils"
        " of power users, a VC's own portfolio companies, early adopters who are not representative),"
        " when dissent is structurally muted, or when disconfirming search is replaced by community"
        " agreement. Also watch for inaction as social proof: when nobody raises an issue, the"
        " absence of challenge can be read as confirmation that doing nothing is correct."
        " IMPORTANT: Social-proof and authority-misinfluence can coexist. Use authority-misinfluence"
        " when personal rank or prestige substitutes for evidence. Use social-proof when the"
        " behavior or outcomes of OTHERS (portfolio companies, peer firms, council members) is"
        " treated as proof. Both can fire on the same passage if both signals are present."
    ),
    "influence-from-mere-association-tendency": (
        "Detect when a superficial halo, label, status marker, or association is used as proof."
        " Do not use this label if the main driver is authority, social imitation, or explicit"
        " incentives."
    ),
    "reward-and-punishment-superresponse-tendency": (
        "Detect when incentive structure, reward, punishment, or compensation mechanics are the"
        " causal driver. Do not use this label for generic upside, PR benefit, or reputational"
        " gain unless incentives themselves are doing the work."
    ),
    "inconsistency-avoidance-tendency": (
        "Detect when the answer is protecting the current path, prior commitment, or familiar"
        " setup from change. Keep this label in play when public signaling, identity,"
        " social posting, or visible prior commitments make reversal feel reputationally"
        " costly. Do not use this label for a new rollout plan unless status-quo"
        " protection is actually the reason."
    ),
    "reciprocation-tendency": (
        "Detect when returning a favor, concession, or endorsement is doing the work. Mere trust"
        " in a referral or recommendation is not enough."
    ),
    "overoptimism-tendency": (
        "Detect optimistic probability claims, downside dismissal, or wishful assumptions about"
        " success. Do not use this label for every positive recommendation. Prefer the"
        " 'premortem' route hint only when the quoted passage itself pushes a concrete move"
        " forward despite unresolved prerequisites, unresolved terms, missing stop rules, or"
        " missing reversal triggers that would block or reverse the move. Do not choose"
        " 'premortem' just because a plan could fail or execution risk exists. Prefer"
        " 'base_rates' when the answer is mainly an inside-view forecast, expansion story, or"
        " upside case without a reference class, historical odds, or denominator. If"
        " unresolved terms or reversal conditions are the main omitted check in the quoted"
        " passage, do not default to 'base_rates' merely because probabilities are also"
        " unquantified. IMPORTANT: Do NOT fire this tendency when the answer already provides"
        " explicit verification conditions, go/no-go criteria, or structured risk analysis"
        " with concrete mitigation steps. Exploratory alternatives presented within a"
        " conditional framework ('consider X,' 'explore whether Y') are not optimistic"
        " predictions — they are options to investigate. Only fire when the answer treats an"
        " uncertain outcome as likely or dismisses a concrete downside, not when it frames"
        " options inside a decision structure that already includes stop rules."
    ),
    "reason-respecting-tendency": (
        "Detect when the answer accepts a narrative, plausible assertion, correlation, or"
        " surface explanation as a sufficient 'why' without requiring verifiable logical steps,"
        " root-cause tracing, or structural grounding. This tendency is so strong that even"
        " reasons with the grammatical structure of explanation but no actual content ('because"
        " we need growth,' 'because it's strategic') still satisfy it — look for structural"
        " reason-giving with empty payload. Do not use this label when the driver is deference"
        " to an authority figure (prefer authority-misinfluence) or rushing to escape"
        " uncertainty (prefer doubt-avoidance). The core signal is that a coherent-sounding"
        " reason has closed the inquiry that should have demanded structural proof."
    ),
    "contrast-misreaction-tendency": (
        "Detect when a relative comparison frame is DISTORTING judgment — making something"
        " look acceptable that would fail an absolute test. The key question is: would the"
        " decision change if the comparison object disappeared? Keep this label in play when"
        " a price, risk, or concession looks acceptable ONLY because it sits next to something"
        " much larger or worse, when distorted peer sets or inflated comparables replace absolute"
        " judgment, or when small consecutive steps toward a bad outcome each look harmless"
        " compared to the last step. IMPORTANT: Do NOT fire this tendency on standard cost-benefit"
        " analysis where the answer compares costs to benefits, alternatives to each other, or"
        " risk to reward using quantitative reasoning — that is sound analytical method, not a"
        " distortion. SPECIFICITY REQUIREMENT: When firing this tendency, you MUST name the"
        " specific absolute standard or threshold that the comparison frame is hiding. Your"
        " challenge_statement must state what absolute question should govern the decision once"
        " the comparison frame is removed. If you cannot name a concrete absolute standard that"
        " is being obscured, do not fire this tendency. Do not use this label when the"
        " main driver is a single salient anchor (prefer availability-misweighing) or explicit"
        " loss aversion (prefer deprival-superreaction)."
    ),
    "curiosity-tendency": (
        "Detect when innate curiosity, the drive to explore, or intellectual openness is acting"
        " as a preventative force against other biases — or when its absence is allowing"
        " premature closure or shallow analysis. This tendency is unusual: it is primarily"
        " protective, not distortive. Flag it when the reasoning would benefit from deeper"
        " inquiry that curiosity would naturally provoke but that is being skipped. Do not use"
        " this label when the main issue is rushing to decide (prefer doubt-avoidance) or"
        " accepting a surface explanation (prefer reason-respecting)."
    ),
    "disliking-hating-tendency": (
        "Detect when animosity, distrust, or hostility toward a person, group, or institution"
        " is causing the reasoning to ignore virtues, distort facts, or reject proposals on"
        " personal grounds rather than merit. Keep this label in play when the answer dismisses"
        " an option because of who proposed it rather than what it contains. Do not use this"
        " label when the main driver is deference to an admired figure (prefer liking-loving)"
        " or competitive incentive dynamics (prefer reward-and-punishment-superresponse)."
    ),
    "drug-misinfluence-tendency": (
        "Detect when chemical dependency, substance use, or physiological impairment is"
        " degrading cognitive function or judgment in the scenario. This tendency is narrow:"
        " it applies only when substance-related impairment is a factor in the reasoning"
        " failure. Do not use this label for metaphorical addiction to a strategy or habit"
        " (prefer inconsistency-avoidance) or for stress-driven shortcuts (prefer"
        " stress-influence)."
    ),
    "envy-jealousy-tendency": (
        "Detect when comparison with what others possess, earn, or achieve is driving the"
        " reasoning — especially when the answer frames a situation as unfair primarily because"
        " someone else has more. Keep this label in play when competitive resentment, pay"
        " comparison, or status rivalry is distorting an otherwise rational evaluation. Do not"
        " use this label when the main driver is a sense of procedural fairness being violated"
        " (prefer kantian-fairness) or explicit loss of something already held"
        " (prefer deprival-superreaction)."
    ),
    "excessive-self-regard-tendency": (
        "Detect when overvaluation of one's own ideas, competence, possessions, or past"
        " decisions is distorting the reasoning. Keep this label in play when the answer assumes"
        " the decision-maker's judgment is uniquely reliable, when the endowment effect inflates"
        " the value of what is already owned, or when the analysis dismisses outside perspectives"
        " because the insider 'knows better.' Do not use this label for generic optimism about"
        " outcomes (prefer overoptimism) or for defending a prior commitment against change"
        " (prefer inconsistency-avoidance)."
    ),
    "kantian-fairness-tendency": (
        "Detect when an expectation of reciprocal courtesy, equal treatment, or fair-sharing is"
        " assumed without examining actual leverage, power asymmetry, or enforcement mechanisms."
        " Keep this label in play when the answer expects cooperation or good faith from a"
        " counterparty simply because 'it's the right thing' rather than because structural"
        " incentives support it. Do not use this label when the main driver is envy of what"
        " others have (prefer envy-jealousy) or returning a specific favor"
        " (prefer reciprocation)."
    ),
    "lollapalooza-tendency": (
        "Detect when multiple psychological tendencies are acting in concert to produce an"
        " extreme outcome that no single tendency would explain alone. Keep this label in play"
        " when the reasoning shows two or more biases reinforcing each other — for example,"
        " authority plus social proof plus incentives all pushing in the same direction. The"
        " core signal is confluence and compounding, not any single bias. Do not use this label"
        " for a scenario dominated by one strong tendency; use the specific tendency instead."
    ),
    "senescence-misinfluence-tendency": (
        "Detect when age-related cognitive decline, institutional decay, or organizational"
        " senescence is contributing to degraded judgment or outdated reasoning. This tendency"
        " is narrow and applies when the scenario involves long-tenured decision-makers or"
        " legacy processes whose effectiveness has eroded over time. Do not use this label for"
        " generic status-quo bias (prefer inconsistency-avoidance) or for skill atrophy from"
        " disuse (prefer use-it-or-lose-it)."
    ),
    "simple-pain-avoiding-psychological-denial": (
        "Detect when the reasoning distorts, minimizes, or refuses to acknowledge a painful"
        " reality. Keep this label in play when the answer avoids confronting bad news, sunk"
        " losses, or an uncomfortable truth by rationalizing it away, filtering out"
        " disconfirming evidence, or simply not addressing it. The tendency is self-sealing:"
        " once denial activates, the subject's capacity for self-correction is itself"
        " degraded — look for situations where what is obvious to outsiders is invisible to"
        " the decision-maker. The core signal is that the reality is too painful to face, so"
        " the facts are bent until bearable. Do not use this label for generic optimism"
        " (prefer overoptimism) or for defending a prior commitment"
        " (prefer inconsistency-avoidance)."
    ),
    "twaddle-tendency": (
        "Detect when the reasoning is consumed by meaningless elaboration, busywork,"
        " administrative noise, or low-value detail that crowds out the substantive issue."
        " Keep this label in play when the answer spends its analytical budget on trivial"
        " procedure, jargon, or tangential discussion rather than addressing the core problem."
        " Do not use this label when the main issue is accepting a surface explanation"
        " (prefer reason-respecting) or premature closure (prefer doubt-avoidance)."
    ),
    "use-it-or-lose-it-tendency": (
        "Detect when skill atrophy, knowledge decay, or lack of practice is contributing to"
        " degraded reasoning or poor judgment. Keep this label in play when the scenario"
        " involves a capability that was once strong but has deteriorated from disuse —"
        " whether an individual's rusty expertise or an organization's abandoned process."
        " Do not use this label for age-related decline (prefer senescence-misinfluence) or"
        " for never having had the skill in the first place (prefer excessive-self-regard)."
    ),
}


PASS_2_DEEP_CHECK_SYSTEM = """You are performing a focused analysis of one specific cognitive tendency in a piece of reasoning. You have deep expertise in this single tendency and in the corrective models that challenge it.

CRITICAL: You are checking for ONE tendency ONLY. Do not analyze any other tendency. Your entire focus is on determining whether the tendency described below is genuinely present in the reasoning.

THE TENDENCY YOU ARE CHECKING:
Name: {tendency_name}
Number: {tendency_number}
Description: {tendency_description}

TENDENCY-SPECIFIC CALIBRATION:
{tendency_guidance}

ROUTE HINT MENU:
If you detect the tendency, choose the single menu item that best points to the corrective model that should challenge this failure mechanism. Use "general" only when the tendency is real but no more specific route hint clearly fits.
{sub_pattern_menu}

RULES:
1. Detect only decision-distorting manifestations of this tendency. Incidental tone, generic confidence, persuasive wording, or adjacent vocabulary are not enough.
2. Use the QUERY to understand what constraints, downside, dependencies, denominators, or reversal conditions were live.
3. Look for specific evidence in the vanilla answer, not generic vibes.
4. Omission-based detection is valid only when the answer commits to a move without a necessary check, denominator, dependency treatment, reversal condition, pilot, or stop rule that this tendency would predictably require.
5. If the tendency is genuinely present, cite the exact passage that proves it. For omission-based cases, quote the action sentence that exposes the unjustified leap.
6. If you cannot point to a specific passage, the tendency is not detected.
7. Prefer the narrowest mechanism. If another tendency would explain the issue better, return not detected.
8. If your evidence is only generic missing downside, urgency, or confidence that would fit several tendencies equally well, return not detected for this tendency.
9. The sub_pattern must come from the menu above. It is a route hint, not a free-text diagnosis.
10. Severity levels: "low", "medium", or "high"

Respond ONLY with valid JSON matching this exact schema:

If DETECTED:
```json
{{
  "tendency_id": "{tendency_id}",
  "tendency_number": {tendency_number},
  "detected": true,
  "confidence": 0.0,
  "evidence": "1-2 sentence explanation",
  "sub_pattern": "exact sub-pattern slug from the menu above",
  "specific_passage": "Exact quote from the vanilla answer",
  "severity": "low"
}}
```

If NOT DETECTED:
```json
{{
  "tendency_id": "{tendency_id}",
  "tendency_number": {tendency_number},
  "detected": false,
  "confidence": 0.0,
  "reason": "Brief reason this tendency does not apply here"
}}
```"""


PASS_2_DEEP_CHECK_USER = """QUERY:
{query}

VANILLA ANSWER:
{vanilla_answer}

Use the query only as context for what the answer skipped or overrode.

Analyze this answer for the presence of {tendency_name} ONLY. Respond with JSON only."""


# ---------------------------------------------------------------------------
# Phase 2c: conversation-first Pass 2 — CONTEXT / SOURCE split + enum-checklist.
#
# The system prompt is rebuilt to:
#   1. Replace "QUERY / VANILLA ANSWER" language with CONTEXT / SOURCE, where
#      SOURCE = assistant turns verbatim (primary audit target for this tendency).
#   2. Add an ENUM CHECKLIST REMINDER for sub_pattern selection (durable 2b
#      lesson: the LLM under-surfaces sub_patterns that manifest as omission
#      or implicit bias rather than verbatim claims; prompt it to explicitly
#      walk the menu before committing).
# ---------------------------------------------------------------------------

PASS_2_DEEP_CHECK_SYSTEM_FROM_CONTEXT = """You are performing a focused analysis of one specific cognitive tendency in a piece of AI reasoning. You have deep expertise in this single tendency and in the corrective models that challenge it.

CRITICAL: You are checking for ONE tendency ONLY. Do not analyze any other tendency. Your entire focus is on determining whether the tendency described below is genuinely present in the assistant's reasoning.

You will receive the user prompt in two sections:
- CONTEXT: the decision situation, framing, live constraints, dropped threads, and the user's turns. Background for understanding what was live. NOT the primary audit target.
- SOURCE: the assistant's turns verbatim. This IS the primary audit target. The tendency (if present) manifests here as commission (what the assistant said) or omission (what the assistant skipped given CONTEXT).

THE TENDENCY YOU ARE CHECKING:
Name: {tendency_name}
Number: {tendency_number}
Description: {tendency_description}

TENDENCY-SPECIFIC CALIBRATION:
{tendency_guidance}

ROUTE HINT MENU:
If you detect the tendency, choose the single menu item that best points to the corrective model that should challenge this failure mechanism. Use "general" only when the tendency is real but no more specific route hint clearly fits.
{sub_pattern_menu}

ENUM CHECKLIST REMINDER (sub_pattern selection):
Before finalizing your sub_pattern choice, verify you've considered EACH option in the menu — not just the ones that surface verbatim in SOURCE. Some sub_patterns manifest as omission (the assistant skipping a check or reversal condition) or implicit bias (reasoning leaning on the failure mechanism without stating it) rather than as explicit claims. Walk the menu and ask, for each sub_pattern, whether the evidence in SOURCE + the omissions highlighted by CONTEXT fit. Choose the single best match. Use "general" only if no menu item clearly applies to the detected tendency.

RULES:
1. Detect only decision-distorting manifestations of this tendency. Incidental tone, generic confidence, persuasive wording, or adjacent vocabulary are not enough.
2. Use CONTEXT to understand what constraints, downside, dependencies, denominators, or reversal conditions were live — especially for omission-based detection.
3. Look for specific evidence in the assistant's turns (SOURCE). Generic vibes are not enough.
4. Omission-based detection is valid only when the assistant commits to a move without a necessary check, denominator, dependency treatment, reversal condition, pilot, or stop rule that this tendency would predictably require AND that CONTEXT made live.
5. If the tendency is genuinely present, cite the exact passage from an assistant turn in SOURCE. For omission-based cases, quote the assistant's action sentence that exposes the unjustified leap.
6. If you cannot point to a specific passage in SOURCE, the tendency is not detected.
7. Prefer the narrowest mechanism. If another tendency would explain the issue better, return not detected.
8. If your evidence is only generic missing downside, urgency, or confidence that would fit several tendencies equally well, return not detected for this tendency.
9. The sub_pattern must come from the menu above. It is a route hint, not a free-text diagnosis.
10. Severity levels: "low", "medium", or "high"

Respond ONLY with valid JSON matching this exact schema:

If DETECTED:
```json
{{
  "tendency_id": "{tendency_id}",
  "tendency_number": {tendency_number},
  "detected": true,
  "confidence": 0.0,
  "evidence": "1-2 sentence explanation",
  "sub_pattern": "exact sub-pattern slug from the menu above",
  "specific_passage": "Exact quote from an assistant turn in SOURCE",
  "severity": "low"
}}
```

If NOT DETECTED:
```json
{{
  "tendency_id": "{tendency_id}",
  "tendency_number": {tendency_number},
  "detected": false,
  "confidence": 0.0,
  "reason": "Brief reason this tendency does not apply here"
}}
```"""


@dataclass(frozen=True)
class DeepCheckResult:
    tendency_id: str
    tendency_name: str
    tendency_number: int
    detected: bool
    confidence: float = 0.0
    evidence: str = ""
    sub_pattern: str = ""
    specific_passage: str = ""
    severity: str = ""
    reason: str = ""


def build_sub_pattern_menu(bindings: tuple[ModelBinding, ...]) -> str:
    if not bindings:
        return "- [general]: General manifestation of this tendency"

    lines = [
        "- [general]: General manifestation of this tendency when no more specific route hint clearly fits."
    ]
    for binding in bindings:
        slug = binding.model_id.replace("-", "_")
        description = (
            binding.activation_context
            or f"Route to the '{binding.model_id}' corrective lens if it best challenges the failure mechanism."
        )
        lines.append(f"- [{slug}]: {description}")
    return "\n".join(lines)


def build_tendency_guidance(tendency_id: str) -> str:
    guidance = _TENDENCY_SPECIFIC_GUIDANCE.get(
        tendency_id,
        "Prefer not detected if the evidence fits a narrower adjacent tendency better.",
    )
    return f"- {guidance}"


def format_pass2_prompt(
    query: str,
    vanilla_answer: str,
    tendency_key: str,
    catalog: TendencyCatalog,
) -> tuple[str, str]:
    tendency = catalog.lookup(tendency_key)
    sub_pattern_menu = build_sub_pattern_menu(tendency.antidote_bindings)
    system = PASS_2_DEEP_CHECK_SYSTEM.format(
        tendency_name=tendency.display_name,
        tendency_number=tendency.tendency_number,
        tendency_description=tendency.description,
        tendency_id=tendency.tendency_id,
        tendency_guidance=build_tendency_guidance(tendency.tendency_id),
        sub_pattern_menu=sub_pattern_menu,
    )
    user = PASS_2_DEEP_CHECK_USER.format(
        query=query,
        vanilla_answer=vanilla_answer,
        tendency_name=tendency.display_name,
    )
    return system, user


def _format_pass2_from_context_user_prompt(
    context: ConversationContext,
    tendency_name: str,
) -> str:
    """Build the CONTEXT/SOURCE Pass 2 user body for one tendency.

    CONTEXT: extraction summaries + user turns (background).
    SOURCE: assistant turns verbatim (primary audit target).
    """
    ext = context.extraction
    parts: list[str] = [
        "CONTEXT (background — what the user made live; NOT the primary audit target):",
    ]
    if ext.decision_situation:
        parts.append(f"- Decision situation: {ext.decision_situation}")
    if ext.original_framing:
        parts.append(f"- Framing: {ext.original_framing}")
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
        parts.append("- User turns (CONTEXT only):")
        for t in user_turns:
            parts.append(f"  [Turn {t.turn_index}] USER: {t.text}")

    parts.append("")
    parts.append(
        "SOURCE (PRIMARY AUDIT TARGET — assistant turns verbatim; the tendency lives here as commission or omission):"
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
        f"Analyze SOURCE for the presence of {tendency_name} ONLY. Respond with JSON only."
    )
    return "\n".join(parts)


def format_pass2_prompt_from_context(
    context: ConversationContext,
    tendency_key: str,
    catalog: TendencyCatalog,
) -> tuple[str, str]:
    """Phase 2c conversation-first entry point for Pass 2.

    Returns (system_prompt, user_prompt) for one tendency. The system prompt
    uses CONTEXT/SOURCE language and carries the enum-checklist reminder for
    sub_pattern selection (2b durable lesson).
    """
    tendency = catalog.lookup(tendency_key)
    sub_pattern_menu = build_sub_pattern_menu(tendency.antidote_bindings)
    system = PASS_2_DEEP_CHECK_SYSTEM_FROM_CONTEXT.format(
        tendency_name=tendency.display_name,
        tendency_number=tendency.tendency_number,
        tendency_description=tendency.description,
        tendency_id=tendency.tendency_id,
        tendency_guidance=build_tendency_guidance(tendency.tendency_id),
        sub_pattern_menu=sub_pattern_menu,
    )
    user = _format_pass2_from_context_user_prompt(context, tendency.display_name)
    return system, user


# ---------------------------------------------------------------------------
# Phase 4c: packet-driven Lane 1 Pass 2 (mirrors _from_context shape)
# ---------------------------------------------------------------------------
# Same byte-equivalence-on-active-constraints discipline as Lane 4. The IR
# does not carry `weight` (Phase 1 design); when status != "active", the
# packet path emits "[STATUS]" while context emits "[STATUS/WEIGHT]".


def _format_pass2_from_packet_user_prompt(
    packet: Lane4Packet,
    tendency_name: str,
) -> str:
    """Packet-driven counterpart to `_format_pass2_from_context_user_prompt`."""
    parts: list[str] = [
        "CONTEXT (background — what the user made live; NOT the primary audit target):",
    ]
    if packet.decision_situation:
        parts.append(f"- Decision situation: {packet.decision_situation.text}")
    if packet.original_framing:
        parts.append(f"- Framing: {packet.original_framing.text}")
    if packet.constraints:
        parts.append("- Live constraints:")
        for c in packet.constraints:
            status = (c.status or "active").upper()
            tag = status  # weight not in IR; only matters for non-active
            parts.append(f"  - [{tag}] {c.text} (turn {c.introduced_at_turn})")
    if packet.issues:
        parts.append("- Dropped threads:")
        for i in packet.issues:
            line = (
                f"  - {i.text} (raised by {i.raised_by} turn {i.introduced_at_turn}, "
                f"status: {i.status or '?'})"
            )
            if i.superseded_by:
                line += f", superseded_by: {i.superseded_by}"
            parts.append(line)

    user_turns = [t for t in packet.turns if t.speaker == "user"]
    if user_turns:
        parts.append("- User turns (CONTEXT only):")
        for t in user_turns:
            parts.append(f"  [Turn {t.turn_index}] USER: {t.text}")

    parts.append("")
    parts.append(
        "SOURCE (PRIMARY AUDIT TARGET — assistant turns verbatim; the tendency lives here as commission or omission):"
    )
    assistant_turns = [t for t in packet.turns if t.speaker == "assistant"]
    if not assistant_turns:
        parts.append("(no assistant turns present)")
    else:
        for t in assistant_turns:
            parts.append(f"[Turn {t.turn_index}] ASSISTANT:")
            parts.append(t.text)
            parts.append("")

    parts.append(
        f"Analyze SOURCE for the presence of {tendency_name} ONLY. Respond with JSON only."
    )
    return "\n".join(parts)


def format_pass2_prompt_from_packet(
    packet: Lane4Packet,
    tendency_key: str,
    catalog: TendencyCatalog,
) -> tuple[str, str]:
    """Packet-driven entry point for Pass 2. Returns (system, user)."""
    tendency = catalog.lookup(tendency_key)
    sub_pattern_menu = build_sub_pattern_menu(tendency.antidote_bindings)
    system = PASS_2_DEEP_CHECK_SYSTEM_FROM_CONTEXT.format(
        tendency_name=tendency.display_name,
        tendency_number=tendency.tendency_number,
        tendency_description=tendency.description,
        tendency_id=tendency.tendency_id,
        tendency_guidance=build_tendency_guidance(tendency.tendency_id),
        sub_pattern_menu=sub_pattern_menu,
    )
    user = _format_pass2_from_packet_user_prompt(packet, tendency.display_name)
    return system, user


def parse_pass2_result(
    payload: dict[str, object],
    requested_tendency_key: str,
    catalog: TendencyCatalog,
) -> DeepCheckResult:
    requested_tendency = catalog.lookup(requested_tendency_key)
    tendency = requested_tendency
    payload_tendency_key = coerce_str(payload.get("tendency_id")).strip()
    if payload_tendency_key:
        try:
            tendency = catalog.lookup(payload_tendency_key)
        except KeyError:
            tendency = requested_tendency

    return DeepCheckResult(
        tendency_id=tendency.tendency_id,
        tendency_name=tendency.display_name,
        tendency_number=coerce_int(payload.get("tendency_number"), tendency.tendency_number),
        detected=bool(payload.get("detected", False)),
        confidence=coerce_float(payload.get("confidence")),
        evidence=coerce_str(payload.get("evidence")),
        sub_pattern=coerce_str(payload.get("sub_pattern")),
        specific_passage=coerce_str(payload.get("specific_passage")),
        severity=coerce_str(payload.get("severity")),
        reason=coerce_str(payload.get("reason")),
    )
