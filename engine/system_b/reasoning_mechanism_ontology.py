"""Research-only operational ontology for joint-process reasoning mechanisms."""
from __future__ import annotations

ONTOLOGY_SCHEMA = "lolla.reasoning_mechanism_ontology.v1"

# These are interpretation instructions, not deterministic recognition rules.
MECHANISMS = {
    "status_signal_used_as_evidence": {
        "definition": "A status, prestige, authority, popularity, or affiliation signal substitutes for evidence about the claim or choice.",
        "requires": "The reasoning relies on the signal as support, not merely mentions it.",
        "excludes": "Do not use when authority is relevant evidence and its limits are examined, or when status is only context.",
        "near_neighbor": "ambiguous_signal_treated_as_commitment concerns over-reading an uncertain indication; this mechanism concerns status as proof.",
    },
    "ambiguous_signal_treated_as_commitment": {
        "definition": "An uncertain, preliminary, conditional, or nonbinding indication is treated as if it settled future behavior or commitment.",
        "requires": "The conclusion is stronger than the signal warrants and remains consequential.",
        "excludes": "Do not use for an explicit commitment with materially examined conditions.",
        "near_neighbor": "criteria_defined_after_commitment concerns moving or late criteria, not over-reading the commitment signal itself.",
    },
    "acknowledged_constraint_not_gated": {
        "definition": "A material constraint is recognized but is not converted into a decision gate, safeguard, threshold, or action condition.",
        "requires": "The constraint is acknowledged and the current path can proceed without satisfying it.",
        "excludes": "Do not use when the constraint has an operative gate, even if the gate may later prove imperfect.",
        "near_neighbor": "counterpressure_acknowledged_not_integrated is broader competing evidence; this mechanism specifically requires a missing operational gate.",
    },
    "criteria_defined_after_commitment": {
        "definition": "Evaluation criteria, success conditions, or evidence standards are set or changed only after practical or psychological commitment.",
        "requires": "Commitment precedes the criteria, creating room to rationalize the chosen path.",
        "excludes": "Do not use when criteria preceded commitment or were transparently updated because genuinely new information changed the question.",
        "near_neighbor": "initial_frame_persists_after_question_change concerns an obsolete frame, not post-commitment criteria.",
    },
    "initial_frame_persists_after_question_change": {
        "definition": "The reasoning continues to optimize or argue inside an initial frame after the underlying question, objective, or decision boundary materially changes.",
        "requires": "The changed question is evidenced and the old frame still shapes the current reasoning.",
        "excludes": "Do not infer persistence merely because the starting and current positions differ or share a topic.",
        "near_neighbor": "criteria_defined_after_commitment changes standards after commitment; this mechanism retains an outdated problem definition.",
    },
    "counterpressure_acknowledged_not_integrated": {
        "definition": "Material contrary evidence, objection, uncertainty, or downside is noticed but does not alter the active reasoning, safeguards, confidence, or decision conditions.",
        "requires": "Both acknowledgement and failure to integrate are supported.",
        "excludes": "Do not use when the counterpressure changes the plan, confidence, test, boundary, or explicit condition.",
        "near_neighbor": "acknowledged_constraint_not_gated is the narrower case where the missing integration should be an operational gate.",
    },
    "reversible_path_not_considered": {
        "definition": "A materially more reversible, staged, experimental, or option-preserving path is available in the reasoning space but is not considered.",
        "requires": "The records support both meaningful lock-in risk and the relevance of a less irreversible path.",
        "excludes": "Do not invent an alternative from general world knowledge or use when reversible options were considered and rejected with reasons.",
        "near_neighbor": "missing_reversal_condition concerns when to stop or reverse an adopted path; this concerns failure to consider a more reversible path initially.",
    },
    "upside_downside_evidence_asymmetry": {
        "definition": "Evidence favorable to a path receives materially easier admission, stronger weight, or less scrutiny than unfavorable evidence.",
        "requires": "The records support unequal treatment of opposing evidence, not merely the existence of both upside and downside.",
        "excludes": "Do not use solely because the conclusion is optimistic, risky, or incomplete.",
        "near_neighbor": "counterpressure_acknowledged_not_integrated concerns a known contrary pressure left unused; this requires asymmetric evidence standards or weighting.",
    },
    "missing_reversal_condition": {
        "definition": "An adopted or advancing path lacks a bounded condition that would trigger stopping, reversing, or materially reconsidering it.",
        "requires": "The captured records show meaningful commitment or path dependence and bounded inspection finds no operative reversal condition.",
        "excludes": "Do not use merely because uncertainty remains, because a reversible alternative was not considered, or when an operative stop/review condition exists.",
        "near_neighbor": "reversible_path_not_considered concerns option design before commitment; this concerns an exit or reconsideration rule for the current path.",
    },
}

JOINT_STATUSES = {
    "unresolved": "The mechanism remains operative after the latest captured reasoning and may deserve active pressure.",
    "resolved_in_conversation": "The mechanism appeared, but later reasoning materially repaired it; preserve for audit and do not route.",
    "ambiguous": "The bounded records support competing interpretations; preserve compactly and do not route.",
    "not_observed": "The bounded records do not support the mechanism; this is not a claim about reality outside the capture.",
}

LEGACY_SCOPE = {
    "user": "An actor-local observation attributable to user reasoning; audit-only unless the final joint trajectory remains affected.",
    "assistant": "An actor-local observation attributable to assistant reasoning; audit-only unless the final joint trajectory remains affected.",
    "joint_process": "A property of the reasoning trajectory after considering both sides and later repairs; the only scope eligible for this interpreter's active routing.",
}

LEGACY_STATE = {
    "present": "A positively exhibited mechanism; does not say whether later conversation repaired it.",
    "missing_protection": "A boundedly inspected safeguard is not observed; absence outside the capture is not implied.",
    "tension": "Competing readings remain; it is not a low-confidence synonym for present.",
}


def ontology_packet() -> dict:
    return {
        "schema_version": ONTOLOGY_SCHEMA,
        "target": "unresolved_weakness_in_final_joint_reasoning_trajectory",
        "mechanisms": MECHANISMS,
        "joint_statuses": JOINT_STATUSES,
        "legacy_scope_semantics": LEGACY_SCOPE,
        "legacy_state_semantics": LEGACY_STATE,
        "routing_rule": "Only joint status unresolved is routing eligible.",
        "other_review_required": "Escape hatch for a supported out-of-vocabulary hypothesis; audit-only and never routes.",
    }
