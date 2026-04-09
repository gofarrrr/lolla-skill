from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil

from .stress_phase1_definition import StressPhase1Definition, default_stress_phase1_definition


@dataclass(frozen=True)
class StressPhase1Artifacts:
    output_root: Path
    knowledge_graph_path: Path
    relationship_graph_path: Path
    subpattern_catalog_path: Path
    compiled_chunks_path: Path
    structural_signal_lexicon_path: Path
    case_expectations_path: Path
    quality_report_path: Path


class StressPhase1Builder:
    def __init__(self, source_root: Path, output_root: Path | None = None) -> None:
        self._source_root = Path(source_root)
        self._output_root = Path(output_root) if output_root is not None else self._source_root

    @classmethod
    def load(
        cls,
        source_root: Path,
        *,
        output_root: Path | None = None,
    ) -> "StressPhase1Builder":
        return cls(source_root=source_root, output_root=output_root)

    def compile(self) -> StressPhase1Artifacts:
        definition = default_stress_phase1_definition()
        knowledge_graph = json.loads(
            (self._source_root / "build" / "knowledge_graph.json").read_text(encoding="utf-8")
        )
        _require_stress_groundwork(knowledge_graph, definition)
        mapping_section = _read_stress_mapping_section(self._source_root / "munger_structural_mapping.md")
        psychology_text = (
            self._source_root / "The_Psychology_of_Human_Misjudgment.md"
        ).read_text(encoding="utf-8")

        build_dir = self._output_root / "build"
        curated_dir = build_dir / "curated"
        curated_dir.mkdir(parents=True, exist_ok=True)

        knowledge_graph_path = build_dir / "knowledge_graph.json"
        relationship_graph_path = build_dir / "relationship_graph.json"
        _copy_if_needed(self._source_root / "build" / "knowledge_graph.json", knowledge_graph_path)
        _copy_if_needed(self._source_root / "build" / "relationship_graph.json", relationship_graph_path)

        subpattern_catalog = _build_subpattern_catalog(
            knowledge_graph=knowledge_graph,
            definition=definition,
            mapping_section=mapping_section,
            psychology_text=psychology_text,
        )
        compiled_chunks = _build_compiled_chunks(
            knowledge_graph=knowledge_graph,
            mapping_section=mapping_section,
        )
        structural_signal_lexicon = _build_structural_signal_lexicon()
        _annotate_substrate_quality(
            subpattern_catalog=subpattern_catalog,
            compiled_chunks=compiled_chunks,
        )
        case_expectations = _build_case_expectations(knowledge_graph=knowledge_graph)
        quality_report = _build_quality_report(
            subpattern_catalog=subpattern_catalog,
            compiled_chunks=compiled_chunks,
        )

        subpattern_catalog_path = curated_dir / "subpattern_catalog.json"
        compiled_chunks_path = curated_dir / "compiled_chunks.json"
        structural_signal_lexicon_path = curated_dir / "structural_signal_lexicon.json"
        case_expectations_path = curated_dir / "stress_phase1_case_expectations.json"
        quality_report_path = curated_dir / "stress_phase1_quality_report.json"

        subpattern_catalog_path.write_text(
            json.dumps(subpattern_catalog, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        compiled_chunks_path.write_text(
            json.dumps(compiled_chunks, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        structural_signal_lexicon_path.write_text(
            json.dumps(structural_signal_lexicon, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        case_expectations_path.write_text(
            json.dumps(case_expectations, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        quality_report_path.write_text(
            json.dumps(quality_report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        return StressPhase1Artifacts(
            output_root=self._output_root,
            knowledge_graph_path=knowledge_graph_path,
            relationship_graph_path=relationship_graph_path,
            subpattern_catalog_path=subpattern_catalog_path,
            compiled_chunks_path=compiled_chunks_path,
            structural_signal_lexicon_path=structural_signal_lexicon_path,
            case_expectations_path=case_expectations_path,
            quality_report_path=quality_report_path,
        )


def _require_stress_groundwork(
    knowledge_graph: dict[str, object],
    definition: StressPhase1Definition,
) -> None:
    tendency = ((knowledge_graph.get("tendencies") or {}) if isinstance(knowledge_graph, dict) else {}).get(
        "stress-influence-tendency"
    )
    if not isinstance(tendency, dict):
        raise ValueError("knowledge_graph.json is missing stress-influence-tendency")
    models = knowledge_graph.get("models", {}) if isinstance(knowledge_graph, dict) else {}
    if not isinstance(models, dict):
        raise ValueError("knowledge_graph.json is missing models")
    required_model_ids = (
        *definition.compiled_groundwork_core_models,
        *definition.compiled_groundwork_antidote_models,
    )
    for model_id in required_model_ids:
        if model_id not in models:
            raise ValueError(f"knowledge_graph.json is missing required model '{model_id}'")


def _read_stress_mapping_section(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.find("### 17. Stress-Influence Tendency")
    end = text.find("\n### 18.", start)
    if start < 0:
        raise ValueError("Could not find stress section in munger_structural_mapping.md")
    section = text[start:end if end > start else None].strip()
    if "delays" not in section or "constructive-feedback-models" not in section:
        raise ValueError("Stress mapping section is missing expected curated model links")
    return section


def _build_subpattern_catalog(
    *,
    knowledge_graph: dict[str, object],
    definition: StressPhase1Definition,
    mapping_section: str,
    psychology_text: str,
) -> dict[str, object]:
    models = knowledge_graph["models"]
    model_source = lambda model_id: f"MM_CANONICAL_216/{models[model_id]['source_file']}"

    adrenaline_quote = _require_text(
        psychology_text,
        "sudden stress, for instance from a threat, will cause a rush of adrenaline in the human body, prompting faster and more extreme reaction.",
    )
    heavy_stress_quote = _require_text(
        psychology_text,
        "light stress can slightly improve performance",
    )
    pavlov_quote = _require_text(
        psychology_text,
        "The dog that formerly had liked his trainer now disliked him, for example.",
    )
    delays_quote = _require_text(
        mapping_section,
        "strategic pausing to allow stress hormones to clear and System 2 to re-engage",
    )
    emotional_quote = _require_text(
        mapping_section,
        'provides the "inner rudder" and self-mastery to prevent the emotional brain from taking control under severe stress',
    )
    feedback_quote = _require_text(
        mapping_section,
        "provides a concrete, non-punishing structure that prevents the provider and receiver's croc brain from hijacking under the stress of performance reviews",
    )
    self_control_quote = _require_text(
        mapping_section,
        "the conscious executive override that prevents the stressed 'Doer' from hijacking the long-term goals of the 'Planner'",
    )

    return {
        "version": "0.1",
        "tendencies": {
            "stress-influence-tendency": {
                "display_name": "Stress-Influence Tendency",
                "source_refs": [
                    {
                        "path": "munger_structural_mapping.md",
                        "quote": "### 17. Stress-Influence Tendency",
                        "extraction_type": "explicit",
                        "confidence": "high",
                    },
                    {
                        "path": "The_Psychology_of_Human_Misjudgment.md",
                        "quote": adrenaline_quote,
                        "extraction_type": "explicit",
                        "confidence": "high",
                    },
                    {
                        "path": "The_Psychology_of_Human_Misjudgment.md",
                        "quote": heavy_stress_quote,
                        "extraction_type": "explicit",
                        "confidence": "high",
                    },
                ],
                "subpatterns": [
                    {
                        "subpattern_id": "deadline-driven-shortcutting",
                        "display_name": "Deadline-Driven Shortcutting",
                        "description": definition.subpatterns[0].description,
                        "detectability": "high",
                        "signal_tags": ["deadline-pressure", "review-collapse"],
                        "primary_model_ids": ["delays"],
                        "supporting_model_ids": ["checklists", "self-control"],
                        "bindings": [
                            _binding(
                                model_id="delays",
                                role="primary",
                                activation_context=(
                                    "Use when quota, timing, or competitive pressure is compressing review and the safest"
                                    " first move is to create a pause before commitment."
                                ),
                                source_path="munger_structural_mapping.md",
                                source_quote=delays_quote,
                                confidence="high",
                            ),
                            _binding(
                                model_id="checklists",
                                role="supporting",
                                activation_context=(
                                    "Use when stress raises omission risk above invention risk and the missing move is"
                                    " to externalize the must-not-skip checks."
                                ),
                                source_path=model_source("checklists"),
                                source_quote=_first_list_item(models["checklists"]["select_when"], 0),
                                confidence="high",
                            ),
                            _binding(
                                model_id="self-control",
                                role="supporting",
                                activation_context=(
                                    "Use when people already know the right move, but pressure is pushing an impulsive"
                                    " shortcut ahead of the long-term rule."
                                ),
                                source_path="munger_structural_mapping.md",
                                source_quote=self_control_quote,
                                confidence="high",
                            ),
                        ],
                        "source_refs": [
                            {
                                "path": "The_Psychology_of_Human_Misjudgment.md",
                                "quote": adrenaline_quote,
                                "extraction_type": "explicit",
                                "confidence": "high",
                            },
                            {
                                "path": "munger_structural_mapping.md",
                                "quote": delays_quote,
                                "extraction_type": "explicit",
                                "confidence": "high",
                            },
                        ],
                    },
                    {
                        "subpattern_id": "load-collapse-and-omission",
                        "display_name": "Load Collapse And Omission",
                        "description": definition.subpatterns[1].description,
                        "detectability": "medium",
                        "signal_tags": ["load-omission", "hidden-dependencies"],
                        "primary_model_ids": ["checklists"],
                        "supporting_model_ids": ["scaffolding"],
                        "bindings": [
                            _binding(
                                model_id="checklists",
                                role="primary",
                                activation_context=(
                                    "Use when pressure and complexity are quietly deleting prerequisites, exceptions,"
                                    " or handoffs from view and the answer needs explicit omission control."
                                ),
                                source_path=model_source("checklists"),
                                source_quote=_first_list_item(models["checklists"]["select_when"], 0),
                                confidence="high",
                            ),
                            _binding(
                                model_id="scaffolding",
                                role="supporting",
                                activation_context=(
                                    "Use when complexity exceeds current capacity and the fix is staged support instead"
                                    " of more pressure."
                                ),
                                source_path=model_source("scaffolding"),
                                source_quote=_first_list_item(models["scaffolding"]["select_when"], 0),
                                confidence="high",
                            ),
                        ],
                        "source_refs": [
                            {
                                "path": "The_Psychology_of_Human_Misjudgment.md",
                                "quote": heavy_stress_quote,
                                "extraction_type": "explicit",
                                "confidence": "high",
                            }
                        ],
                    },
                    {
                        "subpattern_id": "feedback-threat-hijack",
                        "display_name": "Feedback Threat Hijack",
                        "description": definition.subpatterns[2].description,
                        "detectability": "medium",
                        "signal_tags": ["feedback-threat", "defensive-reversal"],
                        "primary_model_ids": ["constructive-feedback-models"],
                        "supporting_model_ids": ["emotional-intelligence", "self-control"],
                        "bindings": [
                            _binding(
                                model_id="constructive-feedback-models",
                                role="primary",
                                activation_context=(
                                    "Use when a correction or review is necessary, but the conversation will fail unless"
                                    " it stays concrete and non-punishing under pressure."
                                ),
                                source_path="munger_structural_mapping.md",
                                source_quote=feedback_quote,
                                confidence="high",
                            ),
                            _binding(
                                model_id="emotional-intelligence",
                                role="supporting",
                                activation_context=(
                                    "Use when trust, perceived fairness, or emotional tone will determine whether the"
                                    " corrective signal is even heard."
                                ),
                                source_path="munger_structural_mapping.md",
                                source_quote=emotional_quote,
                                confidence="high",
                            ),
                            _binding(
                                model_id="self-control",
                                role="supporting",
                                activation_context=(
                                    "Use when participants need an executive pause between emotional trigger and reactive"
                                    " response so the learning goal is not lost."
                                ),
                                source_path="munger_structural_mapping.md",
                                source_quote=self_control_quote,
                                confidence="high",
                            ),
                        ],
                        "source_refs": [
                            {
                                "path": "The_Psychology_of_Human_Misjudgment.md",
                                "quote": pavlov_quote,
                                "extraction_type": "explicit",
                                "confidence": "high",
                            },
                            {
                                "path": "munger_structural_mapping.md",
                                "quote": feedback_quote,
                                "extraction_type": "explicit",
                                "confidence": "high",
                            },
                        ],
                    },
                    {
                        "subpattern_id": "challenge-beyond-capacity",
                        "display_name": "Challenge Beyond Capacity",
                        "description": definition.subpatterns[3].description,
                        "detectability": "medium",
                        "signal_tags": ["productive-window-breached", "overwhelm-disguised-as-stretch"],
                        "primary_model_ids": ["desirable-difficulties"],
                        "supporting_model_ids": ["scaffolding", "delays"],
                        "bindings": [
                            _binding(
                                model_id="desirable-difficulties",
                                role="primary",
                                activation_context=(
                                    "Use when pressure keeps adding difficulty without enough structure or sequencing,"
                                    " and the task has moved past the productive challenge window."
                                ),
                                source_path=model_source("desirable-difficulties"),
                                source_quote=_first_list_item(models["desirable-difficulties"]["danger_when"], 0),
                                confidence="high",
                            ),
                            _binding(
                                model_id="scaffolding",
                                role="supporting",
                                activation_context=(
                                    "Use when the task still matters, but challenge must be decomposed into a sequence"
                                    " the learner or team can actually carry."
                                ),
                                source_path=model_source("scaffolding"),
                                source_quote=_first_list_item(models["scaffolding"]["select_when"], 0),
                                confidence="high",
                            ),
                            _binding(
                                model_id="delays",
                                role="supporting",
                                activation_context=(
                                    "Use when the immediate pace itself is worsening performance and the system needs a"
                                    " pause before difficulty is reintroduced."
                                ),
                                source_path="munger_structural_mapping.md",
                                source_quote=delays_quote,
                                confidence="high",
                            ),
                        ],
                        "source_refs": [
                            {
                                "path": "The_Psychology_of_Human_Misjudgment.md",
                                "quote": heavy_stress_quote,
                                "extraction_type": "explicit",
                                "confidence": "high",
                            }
                        ],
                    },
                    {
                        "subpattern_id": "general",
                        "display_name": "General Stress Signal",
                        "description": definition.subpatterns[4].description,
                        "detectability": "low",
                        "signal_tags": ["general-stress", "omission-risk"],
                        "primary_model_ids": ["checklists"],
                        "supporting_model_ids": ["delays"],
                        "bindings": [
                            _binding(
                                model_id="checklists",
                                role="primary",
                                activation_context=(
                                    "Use when stress is clearly present but the narrower reviewed shapes are not yet"
                                    " licensed, so explicit omission control is the safest first move."
                                ),
                                source_path=model_source("checklists"),
                                source_quote=_first_list_item(models["checklists"]["select_when"], 0),
                                confidence="high",
                            ),
                            _binding(
                                model_id="delays",
                                role="supporting",
                                activation_context=(
                                    "Use when a small pause is needed to keep pressure from turning into impulsive"
                                    " action before the missing checks are named."
                                ),
                                source_path="munger_structural_mapping.md",
                                source_quote=delays_quote,
                                confidence="high",
                            ),
                        ],
                        "source_refs": [
                            {
                                "path": "The_Psychology_of_Human_Misjudgment.md",
                                "quote": adrenaline_quote,
                                "extraction_type": "explicit",
                                "confidence": "high",
                            }
                        ],
                    },
                ],
            }
        },
    }


def _build_compiled_chunks(
    *,
    knowledge_graph: dict[str, object],
    mapping_section: str,
) -> dict[str, object]:
    models = knowledge_graph["models"]
    model_source = lambda model_id: f"MM_CANONICAL_216/{models[model_id]['source_file']}"
    delays_quote = _require_text(
        mapping_section,
        "strategic pausing to allow stress hormones to clear and System 2 to re-engage",
    )
    feedback_quote = _require_text(
        mapping_section,
        "provides a concrete, non-punishing structure that prevents the provider and receiver's croc brain from hijacking under the stress of performance reviews",
    )
    self_control_quote = _require_text(
        mapping_section,
        "the conscious executive override that prevents the stressed 'Doer' from hijacking the long-term goals of the 'Planner'",
    )
    emotional_quote = _require_text(
        mapping_section,
        'provides the "inner rudder" and self-mastery to prevent the emotional brain from taking control under severe stress',
    )

    return {
        "version": "0.1",
        "chunks": [
            _chunk(
                chunk_id="dl_diag_deadline",
                model_id="delays",
                chunk_type="diagnosis",
                text=(
                    "If deadline or quota pressure is being used to justify an exception, treat the rush itself as"
                    " evidence that review has collapsed before the decision is safe."
                ),
                source_file="munger_structural_mapping.md",
                source_quote=delays_quote,
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("deadline-driven-shortcutting",),
            ),
            _chunk(
                chunk_id="cl_challenge_deadline",
                model_id="checklists",
                chunk_type="challenge",
                text=(
                    "Which approval, precedent, or prerequisite check is being skipped because the team is treating"
                    " the clock as proof?"
                ),
                source_file=model_source("checklists"),
                source_quote=_first_list_item(models["checklists"]["select_when"], 0),
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("deadline-driven-shortcutting",),
            ),
            _chunk(
                chunk_id="sc_protocol_deadline",
                model_id="self-control",
                chunk_type="protocol",
                text=(
                    "Before committing, state the long-term rule that should still govern the move and hold that"
                    " line for one full review cycle."
                ),
                source_file="munger_structural_mapping.md",
                source_quote=self_control_quote,
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("deadline-driven-shortcutting",),
            ),
            _chunk(
                chunk_id="dl_guardrail_deadline",
                model_id="delays",
                chunk_type="tension",
                text=(
                    "If speed is becoming the reason to suspend scrutiny, assume stress is narrowing thought and"
                    " require a deliberate pause before action."
                ),
                source_file="munger_structural_mapping.md",
                source_quote=delays_quote,
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("deadline-driven-shortcutting",),
                guardrail_tags=("deadline-pressure", "review-collapse"),
            ),
            _chunk(
                chunk_id="cl_diag_load",
                model_id="checklists",
                chunk_type="diagnosis",
                text=(
                    "When pressure and complexity rise together, the likely failure is not slow execution but"
                    " missing steps, hidden dependencies, or forgotten handoffs."
                ),
                source_file=model_source("checklists"),
                source_quote=_first_list_item(models["checklists"]["select_when"], 0),
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("load-collapse-and-omission",),
            ),
            _chunk(
                chunk_id="sf_challenge_load",
                model_id="scaffolding",
                chunk_type="challenge",
                text=(
                    "What part of the task has outgrown current working-memory capacity, and what support or"
                    " sequencing is missing?"
                ),
                source_file=model_source("scaffolding"),
                source_quote=_first_list_item(models["scaffolding"]["select_when"], 0),
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("load-collapse-and-omission",),
            ),
            _chunk(
                chunk_id="sf_protocol_load",
                model_id="scaffolding",
                chunk_type="protocol",
                text=(
                    "Break the move into staged supports so each dependency is visible before the next one is"
                    " attempted."
                ),
                source_file=model_source("scaffolding"),
                source_quote=_first_list_item(models["scaffolding"]["select_when"], 0),
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("load-collapse-and-omission",),
            ),
            _chunk(
                chunk_id="cl_guardrail_load",
                model_id="checklists",
                chunk_type="tension",
                text=(
                    "If the plan sounds manageable only because details are being held implicitly, assume overload"
                    " is deleting important steps from view."
                ),
                source_file=model_source("checklists"),
                source_quote=_first_list_item(models["checklists"]["select_when"], 0),
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("load-collapse-and-omission",),
                guardrail_tags=("load-omission", "hidden-dependencies"),
            ),
            _chunk(
                chunk_id="cfm_diag_feedback",
                model_id="constructive-feedback-models",
                chunk_type="diagnosis",
                text=(
                    "When correction arrives under threat, the conversation can flip from learning to"
                    " self-protection before the facts are absorbed."
                ),
                source_file="munger_structural_mapping.md",
                source_quote=feedback_quote,
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("feedback-threat-hijack",),
            ),
            _chunk(
                chunk_id="ei_challenge_feedback",
                model_id="emotional-intelligence",
                chunk_type="challenge",
                text=(
                    "What about the timing, tone, or perceived fairness would make the receiver defend identity"
                    " instead of engaging the evidence?"
                ),
                source_file="munger_structural_mapping.md",
                source_quote=emotional_quote,
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("feedback-threat-hijack",),
            ),
            _chunk(
                chunk_id="sc_protocol_feedback",
                model_id="self-control",
                chunk_type="protocol",
                text=(
                    "Name the corrective point, lower the emotional temperature, and pause long enough that"
                    " reaction does not outrun the learning goal."
                ),
                source_file="munger_structural_mapping.md",
                source_quote=self_control_quote,
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("feedback-threat-hijack",),
            ),
            _chunk(
                chunk_id="cfm_guardrail_feedback",
                model_id="constructive-feedback-models",
                chunk_type="tension",
                text=(
                    "If the feedback channel feels punishing, expect reversal or shutdown rather than"
                    " improvement."
                ),
                source_file="munger_structural_mapping.md",
                source_quote=feedback_quote,
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("feedback-threat-hijack",),
                guardrail_tags=("feedback-threat", "defensive-reversal"),
            ),
            _chunk(
                chunk_id="dd_diag_capacity",
                model_id="desirable-difficulties",
                chunk_type="diagnosis",
                text=(
                    "When pressure keeps increasing difficulty past the useful challenge window, performance can"
                    " deteriorate even while everyone calls it stretch."
                ),
                source_file=model_source("desirable-difficulties"),
                source_quote=_first_list_item(models["desirable-difficulties"]["danger_when"], 0),
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("challenge-beyond-capacity",),
            ),
            _chunk(
                chunk_id="sf_challenge_capacity",
                model_id="scaffolding",
                chunk_type="challenge",
                text=(
                    "What support, sequencing, or skill-match evidence shows this challenge is still productive"
                    " rather than overwhelming?"
                ),
                source_file=model_source("scaffolding"),
                source_quote=_first_list_item(models["scaffolding"]["select_when"], 0),
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("challenge-beyond-capacity",),
            ),
            _chunk(
                chunk_id="dl_protocol_capacity",
                model_id="delays",
                chunk_type="protocol",
                text=(
                    "Reduce pace, reset the challenge window, and re-enter only after the task is back inside a"
                    " manageable difficulty band."
                ),
                source_file="munger_structural_mapping.md",
                source_quote=delays_quote,
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("challenge-beyond-capacity",),
            ),
            _chunk(
                chunk_id="dd_guardrail_capacity",
                model_id="desirable-difficulties",
                chunk_type="tension",
                text=(
                    "If more pressure is being treated as the answer to breakdown, assume the system has crossed"
                    " from productive stress into dysfunction."
                ),
                source_file=model_source("desirable-difficulties"),
                source_quote=_first_list_item(models["desirable-difficulties"]["danger_when"], 0),
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("challenge-beyond-capacity",),
                guardrail_tags=("productive-window-breached", "overwhelm-disguised-as-stretch"),
            ),
            _chunk(
                chunk_id="cl_diag_general",
                model_id="checklists",
                chunk_type="diagnosis",
                text=(
                    "When stress is clearly present but the narrower reviewed shape is not yet clean, start by"
                    " externalizing the must-not-skip steps."
                ),
                source_file=model_source("checklists"),
                source_quote=_first_list_item(models["checklists"]["select_when"], 0),
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("general",),
            ),
            _chunk(
                chunk_id="cl_challenge_general",
                model_id="checklists",
                chunk_type="challenge",
                text=(
                    "Which critical step would be easiest to forget if the team acted under today's pressure"
                    " without an explicit checklist?"
                ),
                source_file=model_source("checklists"),
                source_quote=_first_list_item(models["checklists"]["select_when"], 0),
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("general",),
            ),
            _chunk(
                chunk_id="dl_protocol_general",
                model_id="delays",
                chunk_type="protocol",
                text=(
                    "Pause just long enough to name the missing checks, the next safe step, and the trigger that"
                    " would justify escalation."
                ),
                source_file="munger_structural_mapping.md",
                source_quote=delays_quote,
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("general",),
            ),
            _chunk(
                chunk_id="cl_guardrail_general",
                model_id="checklists",
                chunk_type="tension",
                text=(
                    "If stress is present and nothing has been written down, treat omission as the default risk."
                ),
                source_file=model_source("checklists"),
                source_quote=_first_list_item(models["checklists"]["select_when"], 0),
                extraction_type="explicit",
                confidence="high",
                subpattern_ids=("general",),
                guardrail_tags=("general-stress", "omission-risk"),
            ),
        ],
    }


def _build_structural_signal_lexicon() -> dict[str, object]:
    return {
        "version": "0.1",
        "operators": [
            "if",
            "when",
            "before",
            "after",
            "because",
            "without",
            "instead",
            "until",
            "while",
        ],
        "stopwords": [
            "the",
            "and",
            "for",
            "that",
            "this",
            "with",
            "from",
            "into",
            "under",
            "your",
            "their",
            "they",
            "them",
            "just",
            "have",
            "will",
            "would",
            "should",
            "about",
            "there",
            "where",
        ],
        "tendencies": {
            "stress-influence-tendency": {
                "subpatterns": {
                    "deadline-driven-shortcutting": {
                        "signal_tags": ["deadline-pressure", "review-collapse"],
                        "cue_phrases": ["deadline", "quota", "competing offer", "rush", "shortcut"],
                    },
                    "load-collapse-and-omission": {
                        "signal_tags": ["load-omission", "hidden-dependencies"],
                        "cue_phrases": ["overloaded", "forgotten step", "handoff", "hidden dependency"],
                    },
                    "feedback-threat-hijack": {
                        "signal_tags": ["feedback-threat", "defensive-reversal"],
                        "cue_phrases": ["feedback", "defensive", "threat response", "punishing review"],
                    },
                    "challenge-beyond-capacity": {
                        "signal_tags": ["productive-window-breached", "overwhelm-disguised-as-stretch"],
                        "cue_phrases": ["overwhelmed", "too much pressure", "beyond capacity", "breakdown"],
                    },
                    "general": {
                        "signal_tags": ["general-stress", "omission-risk"],
                        "cue_phrases": ["stress", "pressure", "threat", "urgency"],
                    },
                }
            }
        },
    }


def _build_case_expectations(*, knowledge_graph: dict[str, object]) -> dict[str, object]:
    models = knowledge_graph["models"]
    return {
        "version": "0.1",
        "tendency_id": "stress-influence-tendency",
        "cases": {
            "security-exception-fast-track": {
                "preferred_subpatterns": ["deadline-driven-shortcutting"],
                "acceptable_subpatterns": ["general"],
                "notes": (
                    "The strongest current stress case: quarter-end pressure and deal-value threat are being used"
                    " to justify a live control exception."
                ),
                "lane_expectations": {
                    "required_lanes": ["diagnosis", "challenge", "protocol", "tension"],
                    "lane_backing": {
                        "diagnosis": {
                            "model_ids": ["delays"],
                            "source_files": ["munger_structural_mapping.md"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "challenge": {
                            "model_ids": ["checklists"],
                            "source_files": [f"MM_CANONICAL_216/{models['checklists']['source_file']}"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "protocol": {
                            "model_ids": ["self-control"],
                            "source_files": ["munger_structural_mapping.md"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "tension": {
                            "model_ids": ["delays"],
                            "source_files": ["munger_structural_mapping.md"],
                            "guardrail_tags": ["deadline-pressure", "review-collapse"],
                            "require_no_blocking_quality_flags": True,
                        },
                    },
                },
                "activation_context_contains_any": ["quota", "timing", "competitive pressure", "pause"],
                "activation_context_source_paths": ["munger_structural_mapping.md"],
                "require_no_activation_context_blocking_quality_flags": True,
            },
            "hiring-rush-manager": {
                "preferred_subpatterns": ["deadline-driven-shortcutting"],
                "acceptable_subpatterns": ["general"],
                "notes": (
                    "Competitive hiring pressure compresses evaluation and makes fast commitment sound like proof"
                    " rather than a stress response."
                ),
                "lane_expectations": {
                    "required_lanes": ["diagnosis", "challenge", "protocol", "tension"],
                    "lane_backing": {
                        "diagnosis": {
                            "model_ids": ["delays"],
                            "source_files": ["munger_structural_mapping.md"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "challenge": {
                            "model_ids": ["checklists"],
                            "source_files": [f"MM_CANONICAL_216/{models['checklists']['source_file']}"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "protocol": {
                            "model_ids": ["self-control"],
                            "source_files": ["munger_structural_mapping.md"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "tension": {
                            "model_ids": ["delays"],
                            "source_files": ["munger_structural_mapping.md"],
                            "guardrail_tags": ["deadline-pressure", "review-collapse"],
                            "require_no_blocking_quality_flags": True,
                        },
                    },
                },
                "activation_context_contains_any": ["timing", "competitive pressure", "pause"],
                "activation_context_source_paths": ["munger_structural_mapping.md"],
                "require_no_activation_context_blocking_quality_flags": True,
            },
        },
    }


def _annotate_substrate_quality(
    *,
    subpattern_catalog: dict[str, object],
    compiled_chunks: dict[str, object],
) -> None:
    tendencies = subpattern_catalog.get("tendencies", {})
    if isinstance(tendencies, dict):
        for tendency in tendencies.values():
            if not isinstance(tendency, dict):
                continue
            for subpattern in tendency.get("subpatterns", []):
                if not isinstance(subpattern, dict):
                    continue
                for binding in subpattern.get("bindings", []):
                    if not isinstance(binding, dict):
                        continue
                    quality = binding.setdefault("quality", {})
                    blocking_flags: list[str] = []
                    advisory_flags: list[str] = []
                    activation_context = str(binding.get("activation_context", "")).strip()
                    source_refs = binding.get("source_refs", [])
                    if not activation_context:
                        blocking_flags.append("missing-activation-context")
                    if len(activation_context.split()) < 8:
                        advisory_flags.append("thin-activation-context")
                    if not source_refs:
                        blocking_flags.append("missing-source-ref")
                    else:
                        first_ref = source_refs[0] if isinstance(source_refs[0], dict) else {}
                        if not str(first_ref.get("quote", "")).strip():
                            blocking_flags.append("missing-source-quote")
                    quality["blocking_flags"] = blocking_flags
                    quality["advisory_flags"] = advisory_flags

    raw_chunks = compiled_chunks.get("chunks", [])
    if isinstance(raw_chunks, list):
        for chunk in raw_chunks:
            if not isinstance(chunk, dict):
                continue
            quality = chunk.setdefault("quality", {})
            blocking_flags: list[str] = []
            advisory_flags: list[str] = []
            if not str(chunk.get("source_file", "")).strip():
                blocking_flags.append("missing-source-file")
            if not str(chunk.get("source_quote", "")).strip():
                blocking_flags.append("missing-source-quote")
            if not str(chunk.get("extraction_type", "")).strip():
                blocking_flags.append("missing-extraction-type")
            if not str(chunk.get("confidence", "")).strip():
                blocking_flags.append("missing-confidence")
            extraction_type = str(chunk.get("extraction_type", "")).strip().lower()
            confidence = str(chunk.get("confidence", "")).strip().lower()
            if extraction_type == "inferred":
                advisory_flags.append("inferred-only")
            if confidence == "medium":
                advisory_flags.append("low-confidence")
            if len(str(chunk.get("text", "")).split()) < 9:
                advisory_flags.append("weak-structural-shape")
            if chunk.get("chunk_type") == "tension" and not chunk.get("guardrail_tags"):
                advisory_flags.append("missing-guardrail-tags")
            quality["blocking_flags"] = blocking_flags
            quality["advisory_flags"] = advisory_flags


def _build_quality_report(
    *,
    subpattern_catalog: dict[str, object],
    compiled_chunks: dict[str, object],
) -> dict[str, object]:
    chunk_rows: list[dict[str, object]] = []
    binding_rows: list[dict[str, object]] = []
    chunks_with_blocking_flags = 0
    bindings_with_blocking_flags = 0
    for chunk in compiled_chunks.get("chunks", []):
        if not isinstance(chunk, dict):
            continue
        quality = chunk.get("quality", {}) if isinstance(chunk.get("quality"), dict) else {}
        blocking_flags = quality.get("blocking_flags", []) if isinstance(quality, dict) else []
        advisory_flags = quality.get("advisory_flags", []) if isinstance(quality, dict) else []
        if blocking_flags:
            chunks_with_blocking_flags += 1
        chunk_rows.append(
            {
                "chunk_id": chunk.get("chunk_id", ""),
                "blocking_flags": blocking_flags,
                "advisory_flags": advisory_flags,
            }
        )
    tendencies = subpattern_catalog.get("tendencies", {})
    if isinstance(tendencies, dict):
        for tendency_id, tendency in tendencies.items():
            if not isinstance(tendency, dict):
                continue
            for subpattern in tendency.get("subpatterns", []):
                if not isinstance(subpattern, dict):
                    continue
                for binding in subpattern.get("bindings", []):
                    if not isinstance(binding, dict):
                        continue
                    quality = binding.get("quality", {}) if isinstance(binding.get("quality"), dict) else {}
                    blocking_flags = quality.get("blocking_flags", []) if isinstance(quality, dict) else []
                    advisory_flags = quality.get("advisory_flags", []) if isinstance(quality, dict) else []
                    if blocking_flags:
                        bindings_with_blocking_flags += 1
                    binding_rows.append(
                        {
                            "tendency_id": tendency_id,
                            "subpattern_id": subpattern.get("subpattern_id", ""),
                            "model_id": binding.get("model_id", ""),
                            "blocking_flags": blocking_flags,
                            "advisory_flags": advisory_flags,
                        }
                    )
    return {
        "summary": {
            "total_chunks": len(chunk_rows),
            "total_bindings": len(binding_rows),
            "chunks_with_blocking_flags": chunks_with_blocking_flags,
            "bindings_with_blocking_flags": bindings_with_blocking_flags,
        },
        "chunks": chunk_rows,
        "bindings": binding_rows,
    }


def _binding(
    *,
    model_id: str,
    role: str,
    activation_context: str,
    source_path: str,
    source_quote: str,
    confidence: str,
) -> dict[str, object]:
    return {
        "model_id": model_id,
        "role": role,
        "activation_context": activation_context,
        "source_refs": [
            {
                "path": source_path,
                "quote": source_quote,
                "extraction_type": "explicit",
                "confidence": confidence,
            }
        ],
    }


def _chunk(
    *,
    chunk_id: str,
    model_id: str,
    chunk_type: str,
    text: str,
    source_file: str,
    source_quote: str,
    extraction_type: str,
    confidence: str,
    subpattern_ids: tuple[str, ...],
    guardrail_tags: tuple[str, ...] = (),
) -> dict[str, object]:
    return {
        "chunk_id": chunk_id,
        "model_id": model_id,
        "chunk_type": chunk_type,
        "text": text,
        "source_file": source_file,
        "source_quote": source_quote,
        "extraction_type": extraction_type,
        "confidence": confidence,
        "tendency_ids": ["stress-influence-tendency"],
        "subpattern_ids": list(subpattern_ids),
        "guardrail_tags": list(guardrail_tags),
    }


def _first_list_item(payload: object, index: int, field: str = "description") -> str:
    if not isinstance(payload, list) or index >= len(payload):
        raise ValueError(f"Missing list item {index}")
    value = payload[index]
    if isinstance(value, dict):
        result = str(value.get(field) or value.get("description") or value.get("mode") or "").strip()
    else:
        result = str(value).strip()
    if not result:
        raise ValueError(f"Missing non-empty list item {index}")
    return result


def _require_text(text: str, needle: str) -> str:
    target = str(needle).strip()
    if not target or target not in text:
        raise ValueError(f"Expected source text to contain: {target}")
    return target


def _copy_if_needed(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() == destination.resolve():
        return
    shutil.copyfile(source, destination)
