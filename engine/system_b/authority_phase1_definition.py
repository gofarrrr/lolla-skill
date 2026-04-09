from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthorityPhase1SourceSet:
    doctrine_sources: tuple[str, ...]
    priority_model_sources: tuple[str, ...]
    expansion_model_sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class AuthorityPhase1Subpattern:
    subpattern_id: str
    description: str
    why_it_matters: str
    likely_core_models: tuple[str, ...] = ()
    likely_protocol_models: tuple[str, ...] = ()


@dataclass(frozen=True)
class AuthorityPhase1CaseExpectation:
    case_id: str
    why_in_subset: str
    packet_evidence: str
    preferred_subpatterns: tuple[str, ...] = ()
    acceptable_subpatterns: tuple[str, ...] = ()


@dataclass(frozen=True)
class AuthorityPhase1Definition:
    tendency_id: str
    objective: str
    architectural_contrast: str
    compiled_groundwork_core_models: tuple[str, ...]
    compiled_groundwork_related_dynamics: tuple[str, ...]
    compiled_groundwork_antidote_models: tuple[str, ...]
    source_set: AuthorityPhase1SourceSet
    subpatterns: tuple[AuthorityPhase1Subpattern, ...]
    acceptance_subset: tuple[AuthorityPhase1CaseExpectation, ...]


def default_authority_phase1_definition() -> AuthorityPhase1Definition:
    return AuthorityPhase1Definition(
        tendency_id="authority-misinfluence-tendency",
        objective=(
            "Prove that the RFC 0004 compiled-substrate pattern generalizes from forecast failure "
            "to social-epistemic failure without inventing authority-specific runtime logic."
        ),
        architectural_contrast=(
            "Overoptimism tested denominator, scenario, and reversal-condition failure. "
            "Authority tests borrowed conviction, protocol suspension, and verification collapse."
        ),
        compiled_groundwork_core_models=(
            "authority-bias",
            "power-dynamics",
            "information-asymmetry",
        ),
        compiled_groundwork_related_dynamics=(
            "social-proof",
            "elasticity",
            "signaling",
        ),
        compiled_groundwork_antidote_models=(
            "user-experience-research-methods",
            "psychological-safety",
            "intellectual-humility",
            "first-principles-thinking",
            "dialectical-reasoning",
            "latticework-of-mental-models",
            "self-organization-and-emergent-order",
        ),
        source_set=AuthorityPhase1SourceSet(
            doctrine_sources=(
                "The_Psychology_of_Human_Misjudgment.md",
                "munger_structural_mapping.md#authority-misinfluence-tendency",
            ),
            priority_model_sources=(
                "MM_CANONICAL_216/Authority_Bias_rag.md",
                "MM_CANONICAL_216/Information_Asymmetry_rag.md",
                "MM_CANONICAL_216/Power_Dynamics_rag.md",
                "MM_CANONICAL_216/Psychological_Safety_rag.md",
                "MM_CANONICAL_216/First_Principles_Thinking_rag.md",
                "MM_CANONICAL_216/Dialectical_Reasoning_rag.md",
                "MM_CANONICAL_216/User_Experience_Research_Methods_rag.md",
            ),
            expansion_model_sources=(
                "MM_CANONICAL_216/Signaling_rag.md",
                "MM_CANONICAL_216/Scientific_Method_Evidence_Testing_rag.md",
                "MM_CANONICAL_216/Latticework_Of_Mental_Models_rag.md",
                "MM_CANONICAL_216/Feynman_Technique_rag.md",
                "MM_CANONICAL_216/Chain_Of_Verification_rag.md",
            ),
        ),
        subpatterns=(
            AuthorityPhase1Subpattern(
                subpattern_id="prestige-cue-substitution",
                description=(
                    "Title, referral, brand, or visible expertise is treated as evidence of correctness."
                ),
                why_it_matters=(
                    "Tests whether the deterministic middle can model messenger-as-message failure "
                    "rather than forecast failure."
                ),
                likely_core_models=("authority-bias", "information-asymmetry"),
                likely_protocol_models=("first-principles-thinking", "dialectical-reasoning"),
            ),
            AuthorityPhase1Subpattern(
                subpattern_id="deference-overrides-verification",
                description=(
                    "The answer borrows judgment from an authority and skips independent evidence review or falsification."
                ),
                why_it_matters=(
                    "Tests whether the architecture can route from outsourced judgment into verification and adversarial-check lanes."
                ),
                likely_core_models=("authority-bias", "information-asymmetry"),
                likely_protocol_models=("dialectical-reasoning", "first-principles-thinking"),
            ),
            AuthorityPhase1Subpattern(
                subpattern_id="authority-overrides-protocol",
                description=(
                    "Status, urgency, or strategic importance causes standing controls or challenge rights to be bypassed."
                ),
                why_it_matters=(
                    "Tests whether the same compiled-substrate pattern handles hierarchy and control-boundary failure."
                ),
                likely_core_models=("power-dynamics", "authority-bias"),
                likely_protocol_models=("psychological-safety", "user-experience-research-methods"),
            ),
            AuthorityPhase1Subpattern(
                subpattern_id="knowledge-gap-elasticity",
                description=(
                    "A slight expertise edge is inflated into broad epistemic dominance, so others outsource judgment too widely."
                ),
                why_it_matters=(
                    "Tests whether the system can represent social-epistemic overextension without collapsing into a generic authority label."
                ),
                likely_core_models=("information-asymmetry", "authority-bias"),
                likely_protocol_models=("first-principles-thinking", "dialectical-reasoning"),
            ),
            AuthorityPhase1Subpattern(
                subpattern_id="general",
                description=(
                    "A real authority-misinfluence signal is present, but the narrower pilot routes are not yet clearly licensed."
                ),
                why_it_matters=(
                    "Preserves mixed-coverage honesty while the second tracer bullet is still being compiled."
                ),
                likely_core_models=("authority-bias",),
                likely_protocol_models=("first-principles-thinking",),
            ),
        ),
        acceptance_subset=(
            AuthorityPhase1CaseExpectation(
                case_id="hiring-rush-manager",
                why_in_subset=(
                    "Cleanest current authority case in the packet: trusted referral, charisma, and compressed hiring urgency."
                ),
                packet_evidence=(
                    "The saved threshold-2 audit already detects authority strongly and says referral-based validation substitutes for independent checks."
                ),
                preferred_subpatterns=("prestige-cue-substitution",),
                acceptable_subpatterns=("knowledge-gap-elasticity", "general"),
            ),
            AuthorityPhase1CaseExpectation(
                case_id="partnership-announcement",
                why_in_subset=(
                    "Stresses whether external brand prestige and implied seniority can displace verification before terms are finalized."
                ),
                packet_evidence=(
                    "Packet expectations include authority-misinfluence, but the saved threshold-2 lane currently resolves it through overoptimism instead."
                ),
                preferred_subpatterns=("deference-overrides-verification",),
                acceptable_subpatterns=("prestige-cue-substitution", "general"),
            ),
            AuthorityPhase1CaseExpectation(
                case_id="security-exception-fast-track",
                why_in_subset=(
                    "Stresses protocol override under enterprise pressure, deal urgency, and halo from a tier-one prospect."
                ),
                packet_evidence=(
                    "Packet expectations include authority-misinfluence, but the saved threshold-2 lane currently resolves the case through stress and overoptimism instead."
                ),
                preferred_subpatterns=("authority-overrides-protocol",),
                acceptable_subpatterns=("deference-overrides-verification", "general"),
            ),
        ),
    )
