from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompoundDefinition:
    compound_id: str
    label: str
    description: str
    member_tendency_ids: tuple[str, ...]
    cross_tier: bool = False


COMPOUND_CATALOG: tuple[CompoundDefinition, ...] = (
    CompoundDefinition(
        compound_id="deadline-sanctioned-override",
        label="Deadline-Sanctioned Override",
        description=(
            "Urgency creates permission while status removes resistance, making the exception path feel pre-cleared."
        ),
        member_tendency_ids=(
            "stress-influence-tendency",
            "authority-misinfluence-tendency",
        ),
    ),
    CompoundDefinition(
        compound_id="halo-defended-escalation",
        label="Halo-Defended Escalation",
        description=(
            "Borrowed status glow and threatened-loss pressure combine to make continuation feel safer than the substance warrants."
        ),
        member_tendency_ids=(
            "influence-from-mere-association-tendency",
            "deprival-superreaction-tendency",
        ),
    ),
    CompoundDefinition(
        compound_id="halo-carried-premature-commitment",
        label="Halo-Carried Premature Commitment",
        description=(
            "A halo cue helps the team close over unresolved terms or unknowns instead of mapping them honestly."
        ),
        member_tendency_ids=(
            "influence-from-mere-association-tendency",
            "doubt-avoidance-tendency",
        ),
    ),
    CompoundDefinition(
        compound_id="salience-reinforced-optimism",
        label="Salience-Reinforced Optimism",
        description=(
            "Vivid evidence is mistaken for a representative denominator, reinforcing an optimistic forward story."
        ),
        member_tendency_ids=(
            "overoptimism-tendency",
            "availability-misweighing-tendency",
        ),
    ),
    CompoundDefinition(
        compound_id="borrowed-credibility-under-deadline",
        label="Borrowed-Credibility Under Deadline",
        description=(
            "Urgency, rank, and borrowed halo combine to make the risky move feel pre-authorized before the substance earns it."
        ),
        member_tendency_ids=(
            "authority-misinfluence-tendency",
            "stress-influence-tendency",
            "influence-from-mere-association-tendency",
        ),
        cross_tier=True,
    ),
    CompoundDefinition(
        compound_id="loss-justified-override",
        label="Loss-Justified Override",
        description=(
            "Deadline pressure and authority create permission while threatened loss makes slowing down feel unacceptable."
        ),
        member_tendency_ids=(
            "authority-misinfluence-tendency",
            "stress-influence-tendency",
            "deprival-superreaction-tendency",
        ),
        cross_tier=True,
    ),
)
