from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StressPhase1SourceSet:
    doctrine_sources: tuple[str, ...]
    priority_model_sources: tuple[str, ...]
    expansion_model_sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class StressPhase1Subpattern:
    subpattern_id: str
    description: str
    why_it_matters: str
    likely_core_models: tuple[str, ...] = ()
    likely_protocol_models: tuple[str, ...] = ()


@dataclass(frozen=True)
class StressPhase1CaseExpectation:
    case_id: str
    why_in_subset: str
    packet_evidence: str
    preferred_subpatterns: tuple[str, ...] = ()
    acceptable_subpatterns: tuple[str, ...] = ()


@dataclass(frozen=True)
class StressPhase1Definition:
    tendency_id: str
    objective: str
    architectural_contrast: str
    compiled_groundwork_core_models: tuple[str, ...]
    compiled_groundwork_related_dynamics: tuple[str, ...]
    compiled_groundwork_antidote_models: tuple[str, ...]
    source_set: StressPhase1SourceSet
    subpatterns: tuple[StressPhase1Subpattern, ...]
    acceptance_subset: tuple[StressPhase1CaseExpectation, ...]


def default_stress_phase1_definition() -> StressPhase1Definition:
    return StressPhase1Definition(
        tendency_id="stress-influence-tendency",
        objective=(
            "Prove that the RFC 0004 compiled-substrate pattern can separate distinct"
            " stress-failure shapes instead of collapsing all pressure into one generic"
            " 'slow down' route."
        ),
        architectural_contrast=(
            "Overoptimism tested forecast structure, authority tested borrowed judgment,"
            " and availability tested evidence weighting. Stress tests whether the compiled"
            " middle can distinguish urgent-reaction failure, overload-driven omission,"
            " and threat-hijacked correction without inventing runtime psychology."
        ),
        compiled_groundwork_core_models=(
            "cognitive-load-theory",
            "flow",
            "evolutionary-pressure",
        ),
        compiled_groundwork_related_dynamics=(
            "resilience",
            "antifragility",
            "information-asymmetry",
        ),
        compiled_groundwork_antidote_models=(
            "checklists",
            "scaffolding",
            "desirable-difficulties",
            "delays",
            "emotional-intelligence",
            "constructive-feedback-models",
            "self-control",
        ),
        source_set=StressPhase1SourceSet(
            doctrine_sources=(
                "The_Psychology_of_Human_Misjudgment.md",
                "munger_structural_mapping.md#stress-influence-tendency",
                "plans/stress-influence-review-no-change.md",
            ),
            priority_model_sources=(
                "MM_CANONICAL_216/Cognitive_Load_Theory_rag.md",
                "MM_CANONICAL_216/Flow_rag.md",
                "MM_CANONICAL_216/Evolutionary_Pressure_rag.md",
                "MM_CANONICAL_216/checklists_rag.md",
                "MM_CANONICAL_216/Scaffolding_rag.md",
                "MM_CANONICAL_216/Desirable_Difficulties_rag.md",
                "MM_CANONICAL_216/Delays_rag.md",
                "MM_CANONICAL_216/Emotional_Intelligence_rag.md",
                "MM_CANONICAL_216/Constructive_Feedback_Models_rag.md",
                "MM_CANONICAL_216/Self_Control_rag.md",
            ),
            expansion_model_sources=(
                "MM_CANONICAL_216/Resilience_rag.md",
                "MM_CANONICAL_216/Antifragility_rag.md",
                "MM_CANONICAL_216/Information_Asymmetry_rag.md",
                "MM_CANONICAL_216/Scaffolding_Educational_rag.md",
            ),
        ),
        subpatterns=(
            StressPhase1Subpattern(
                subpattern_id="deadline-driven-shortcutting",
                description=(
                    "Quota, time, or competitive pressure collapses normal review and pushes an"
                    " immediate move before the required checks are complete."
                ),
                why_it_matters=(
                    "This is the cleanest currently observed stress shape in the packet and the"
                    " easiest proof that one generic stress route is too coarse."
                ),
                likely_core_models=("evolutionary-pressure", "cognitive-load-theory"),
                likely_protocol_models=("delays", "checklists", "self-control"),
            ),
            StressPhase1Subpattern(
                subpattern_id="load-collapse-and-omission",
                description=(
                    "The answer is operating under enough pressure or complexity that critical"
                    " dependencies, conditions, or coordination steps quietly disappear."
                ),
                why_it_matters=(
                    "Tests whether the compiled middle can route from overload into explicit"
                    " structure and memory support instead of treating all stress as mere urgency."
                ),
                likely_core_models=("cognitive-load-theory",),
                likely_protocol_models=("checklists", "scaffolding"),
            ),
            StressPhase1Subpattern(
                subpattern_id="feedback-threat-hijack",
                description=(
                    "A correction, review, or performance conversation is likely to trigger"
                    " threat response and defensive reversal instead of learning."
                ),
                why_it_matters=(
                    "Tests whether the system can treat stress as an interaction failure mode,"
                    " not only as solo deadline pressure."
                ),
                likely_core_models=("evolutionary-pressure",),
                likely_protocol_models=(
                    "constructive-feedback-models",
                    "emotional-intelligence",
                    "self-control",
                ),
            ),
            StressPhase1Subpattern(
                subpattern_id="challenge-beyond-capacity",
                description=(
                    "Challenge has moved past the useful stress window, so the answer behaves as"
                    " if more pressure itself will improve performance."
                ),
                why_it_matters=(
                    "Preserves Munger's light-stress versus heavy-stress distinction and stops"
                    " the engine from flattening all performance pressure into one diagnosis."
                ),
                likely_core_models=("flow", "cognitive-load-theory"),
                likely_protocol_models=(
                    "desirable-difficulties",
                    "scaffolding",
                    "delays",
                ),
            ),
            StressPhase1Subpattern(
                subpattern_id="general",
                description=(
                    "A real stress-influence signal is present, but the narrower reviewed routes"
                    " are not yet clearly licensed."
                ),
                why_it_matters=(
                    "Preserves honesty while stress remains the first subpatterning tracer"
                    " bullet rather than a fully compiled tendency lane."
                ),
                likely_core_models=("evolutionary-pressure",),
                likely_protocol_models=("checklists",),
            ),
        ),
        acceptance_subset=(
            StressPhase1CaseExpectation(
                case_id="security-exception-fast-track",
                why_in_subset=(
                    "Best current stress case: quota pressure and a valuation threat are used to"
                    " justify a policy exception on a live enterprise deal."
                ),
                packet_evidence=(
                    "The saved teacher-pack run already detects stress here and routes it through"
                    " `delays`, while the threshold-3 canonical run misses stress entirely."
                ),
                preferred_subpatterns=("deadline-driven-shortcutting",),
                acceptable_subpatterns=("general",),
            ),
            StressPhase1CaseExpectation(
                case_id="hiring-rush-manager",
                why_in_subset=(
                    "Useful second stress case: competitive hiring pressure compresses evaluation"
                    " and turns referral-based comfort into a reason to move immediately."
                ),
                packet_evidence=(
                    "The saved teacher-pack run already detects stress here and also routes it"
                    " through `delays`, which is useful evidence that the current single route is"
                    " carrying multiple deadline-pressure cases."
                ),
                preferred_subpatterns=("deadline-driven-shortcutting",),
                acceptable_subpatterns=("general",),
            ),
        ),
    )
