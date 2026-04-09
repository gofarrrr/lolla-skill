from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil

from .authority_phase1_definition import AuthorityPhase1Definition, default_authority_phase1_definition


@dataclass(frozen=True)
class AuthorityPhase1Artifacts:
    output_root: Path
    knowledge_graph_path: Path
    relationship_graph_path: Path
    subpattern_catalog_path: Path
    compiled_chunks_path: Path
    structural_signal_lexicon_path: Path
    case_expectations_path: Path
    quality_report_path: Path


class AuthorityPhase1Builder:
    def __init__(self, source_root: Path, output_root: Path | None = None) -> None:
        self._source_root = Path(source_root)
        self._output_root = Path(output_root) if output_root is not None else self._source_root

    @classmethod
    def load(
        cls,
        source_root: Path,
        *,
        output_root: Path | None = None,
    ) -> "AuthorityPhase1Builder":
        return cls(source_root=source_root, output_root=output_root)

    def compile(self) -> AuthorityPhase1Artifacts:
        definition = default_authority_phase1_definition()
        knowledge_graph = json.loads((self._source_root / "build" / "knowledge_graph.json").read_text(encoding="utf-8"))
        _require_authority_groundwork(knowledge_graph, definition)
        mapping_section = _read_authority_mapping_section(self._source_root / "munger_structural_mapping.md")
        psychology_text = (self._source_root / "The_Psychology_of_Human_Misjudgment.md").read_text(encoding="utf-8")

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
        signal_lexicon = _build_structural_signal_lexicon()
        _annotate_substrate_quality(subpattern_catalog=subpattern_catalog, compiled_chunks=compiled_chunks)
        case_expectations = _build_case_expectations()
        quality_report = _build_quality_report(
            subpattern_catalog=subpattern_catalog,
            compiled_chunks=compiled_chunks,
        )

        subpattern_catalog_path = curated_dir / "subpattern_catalog.json"
        compiled_chunks_path = curated_dir / "compiled_chunks.json"
        structural_signal_lexicon_path = curated_dir / "structural_signal_lexicon.json"
        case_expectations_path = curated_dir / "authority_phase1_case_expectations.json"
        quality_report_path = curated_dir / "authority_phase1_quality_report.json"

        subpattern_catalog_path.write_text(
            json.dumps(subpattern_catalog, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        compiled_chunks_path.write_text(
            json.dumps(compiled_chunks, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        structural_signal_lexicon_path.write_text(
            json.dumps(signal_lexicon, ensure_ascii=False, indent=2) + "\n",
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

        return AuthorityPhase1Artifacts(
            output_root=self._output_root,
            knowledge_graph_path=knowledge_graph_path,
            relationship_graph_path=relationship_graph_path,
            subpattern_catalog_path=subpattern_catalog_path,
            compiled_chunks_path=compiled_chunks_path,
            structural_signal_lexicon_path=structural_signal_lexicon_path,
            case_expectations_path=case_expectations_path,
            quality_report_path=quality_report_path,
        )


def _require_authority_groundwork(
    knowledge_graph: dict[str, object],
    definition: AuthorityPhase1Definition,
) -> None:
    tendency = ((knowledge_graph.get("tendencies") or {}) if isinstance(knowledge_graph, dict) else {}).get(
        "authority-misinfluence-tendency"
    )
    if not isinstance(tendency, dict):
        raise ValueError("knowledge_graph.json is missing authority-misinfluence-tendency")
    models = knowledge_graph.get("models", {}) if isinstance(knowledge_graph, dict) else {}
    if not isinstance(models, dict):
        raise ValueError("knowledge_graph.json is missing models")
    required_model_ids = (
        *definition.compiled_groundwork_core_models,
        *definition.compiled_groundwork_antidote_models[:5],
    )
    for model_id in required_model_ids:
        if model_id not in models:
            raise ValueError(f"knowledge_graph.json is missing required model '{model_id}'")


def _read_authority_mapping_section(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.find("### 22. Authority-Misinfluence Tendency")
    end = text.find("\n### 23.", start)
    if start < 0:
        raise ValueError("Could not find authority section in munger_structural_mapping.md")
    section = text[start:end if end > start else None].strip()
    if "authority-bias" not in section or "power-dynamics" not in section or "information-asymmetry" not in section:
        raise ValueError("Authority mapping section is missing expected curated model links")
    return section


def _build_subpattern_catalog(
    *,
    knowledge_graph: dict[str, object],
    definition: AuthorityPhase1Definition,
    mapping_section: str,
    psychology_text: str,
) -> dict[str, object]:
    models = knowledge_graph["models"]
    return {
        "version": "0.1",
        "tendencies": {
            "authority-misinfluence-tendency": {
                "display_name": "Authority-Misinfluence Tendency",
                "source_refs": [
                    {
                        "path": "munger_structural_mapping.md",
                        "quote": "### 22. Authority-Misinfluence Tendency",
                        "extraction_type": "explicit",
                        "confidence": "high",
                    },
                    {
                        "path": "The_Psychology_of_Human_Misjudgment.md",
                        "quote": _require_text(
                            psychology_text,
                            "man was born mostly to follow leaders, with only a few people doing the leading",
                        ),
                        "extraction_type": "explicit",
                        "confidence": "high",
                    },
                ],
                "subpatterns": [
                    {
                        "subpattern_id": "prestige-cue-substitution",
                        "display_name": "Prestige Cue Substitution",
                        "description": "Title, referral, brand, or visible expertise is treated as evidence of correctness.",
                        "detectability": "high",
                        "signal_tags": ["prestige-as-proof", "credential-halo"],
                        "primary_model_ids": ["first-principles-thinking"],
                        "supporting_model_ids": ["authority-bias"],
                        "bindings": [
                            _binding(
                                model_id="first-principles-thinking",
                                role="primary",
                                activation_context=(
                                    "Use when title, referral, or visible expertise is being treated as proof before the facts are independently checked."
                                ),
                                source_path=f"MM_CANONICAL_216/{models['authority-bias']['source_file']}",
                                source_quote=_first_list_item(models["authority-bias"]["danger_when"], 0),
                                confidence="high",
                            ),
                            _binding(
                                model_id="authority-bias",
                                role="supporting",
                                activation_context=(
                                    "Use when the recommendation inherits credibility from status signals rather than from explicit evidence testing."
                                ),
                                source_path=f"MM_CANONICAL_216/{models['authority-bias']['source_file']}",
                                source_quote=_first_list_item(models["authority-bias"]["select_when"], 0),
                                confidence="high",
                            ),
                        ],
                        "source_refs": [
                            {
                                "path": f"MM_CANONICAL_216/{models['authority-bias']['source_file']}",
                                "quote": _first_list_item(models["authority-bias"]["danger_when"], 0),
                                "extraction_type": "explicit",
                                "confidence": "high",
                            },
                            {
                                "path": f"MM_CANONICAL_216/{models['first-principles-thinking']['source_file']}",
                                "quote": _first_list_item(models["first-principles-thinking"]["select_when"], 1),
                                "extraction_type": "explicit",
                                "confidence": "high",
                            },
                        ],
                    },
                    {
                        "subpattern_id": "deference-overrides-verification",
                        "display_name": "Deference Overrides Verification",
                        "description": "Borrowed judgment from an authority displaces independent checking, rival explanation, or evidence review.",
                        "detectability": "high",
                        "signal_tags": ["borrowed-conviction", "falsification-skipped"],
                        "primary_model_ids": ["dialectical-reasoning"],
                        "supporting_model_ids": ["authority-bias", "first-principles-thinking", "information-asymmetry"],
                        "bindings": [
                            _binding(
                                model_id="dialectical-reasoning",
                                role="primary",
                                activation_context=(
                                    "Use when a credible source has supplied the thesis and the missing move is to force that thesis through an explicit antithesis."
                                ),
                                source_path="munger_structural_mapping.md",
                                source_quote=_require_text(
                                    mapping_section,
                                    "forces the authority's thesis to face an antithesis, breaking the halo effect and demanding rigorous proof over rank",
                                ),
                                confidence="high",
                            ),
                            _binding(
                                model_id="authority-bias",
                                role="supporting",
                                activation_context=(
                                    "Use when borrowed conviction from rank or polish is replacing falsification and independent evidence review."
                                ),
                                source_path=f"MM_CANONICAL_216/{models['authority-bias']['source_file']}",
                                source_quote=_first_list_item(models["authority-bias"]["danger_when"], 0),
                                confidence="high",
                            ),
                        ],
                        "source_refs": [
                            {
                                "path": "munger_structural_mapping.md",
                                "quote": _require_text(
                                    mapping_section,
                                    "forces the authority's thesis to face an antithesis, breaking the halo effect and demanding rigorous proof over rank",
                                ),
                                "extraction_type": "explicit",
                                "confidence": "high",
                            },
                            {
                                "path": f"MM_CANONICAL_216/{models['dialectical-reasoning']['source_file']}",
                                "quote": _first_list_item(models["dialectical-reasoning"]["select_when"], 1),
                                "extraction_type": "explicit",
                                "confidence": "high",
                            },
                        ],
                    },
                    {
                        "subpattern_id": "authority-overrides-protocol",
                        "display_name": "Authority Overrides Protocol",
                        "description": "Status, urgency, or strategic importance causes standing controls or challenge rights to be bypassed.",
                        "detectability": "high",
                        "signal_tags": ["rank-bypasses-control", "challenge-rights-suppressed"],
                        "primary_model_ids": ["psychological-safety"],
                        "supporting_model_ids": ["power-dynamics", "user-experience-research-methods"],
                        "bindings": [
                            _binding(
                                model_id="psychological-safety",
                                role="primary",
                                activation_context=(
                                    "Use when local knowledge needs permission to challenge upward because rank or urgency is suppressing the normal correction loop."
                                ),
                                source_path=f"MM_CANONICAL_216/{models['psychological-safety']['source_file']}",
                                source_quote=_first_list_item(models["psychological-safety"]["select_when"], 0),
                                confidence="high",
                            ),
                            _binding(
                                model_id="power-dynamics",
                                role="supporting",
                                activation_context=(
                                    "Use when the apparent authority of the request is suspending controls that should survive deal pressure or hierarchy."
                                ),
                                source_path="munger_structural_mapping.md",
                                source_quote=_require_text(
                                    mapping_section,
                                    "following the instructions of an authority figure even when it causes harm or contradicts common sense",
                                ),
                                confidence="medium",
                            ),
                        ],
                        "source_refs": [
                            {
                                "path": "munger_structural_mapping.md",
                                "quote": _require_text(
                                    mapping_section,
                                    "following the instructions of an authority figure even when it causes harm or contradicts common sense",
                                ),
                                "extraction_type": "explicit",
                                "confidence": "high",
                            },
                            {
                                "path": f"MM_CANONICAL_216/{models['psychological-safety']['source_file']}",
                                "quote": _first_list_item(models["psychological-safety"]["select_when"], 0),
                                "extraction_type": "explicit",
                                "confidence": "high",
                            },
                        ],
                    },
                    {
                        "subpattern_id": "knowledge-gap-elasticity",
                        "display_name": "Knowledge Gap Elasticity",
                        "description": "A slight expertise edge is inflated into broad epistemic dominance, so others outsource judgment too widely.",
                        "detectability": "medium",
                        "signal_tags": ["guru-overreach", "outsourced-judgment"],
                        "primary_model_ids": ["first-principles-thinking"],
                        "supporting_model_ids": ["information-asymmetry", "authority-bias", "dialectical-reasoning"],
                        "bindings": [
                            _binding(
                                model_id="first-principles-thinking",
                                role="primary",
                                activation_context=(
                                    "Use when a narrow expertise edge is being overgeneralized and the team needs to restate what facts actually justify deference."
                                ),
                                source_path=f"MM_CANONICAL_216/{models['information-asymmetry']['source_file']}",
                                source_quote=_first_list_item(models["information-asymmetry"]["heuristics"], 1),
                                confidence="high",
                            ),
                            _binding(
                                model_id="information-asymmetry",
                                role="supporting",
                                activation_context=(
                                    "Use when a modest information gap is being stretched into guru status across domains the evidence does not license."
                                ),
                                source_path=f"MM_CANONICAL_216/{models['information-asymmetry']['source_file']}",
                                source_quote=_first_list_item(models["information-asymmetry"]["heuristics"], 1),
                                confidence="high",
                            ),
                        ],
                        "source_refs": [
                            {
                                "path": "munger_structural_mapping.md",
                                "quote": _require_text(
                                    mapping_section,
                                    'knowledge gap elasticity," where a slight informational advantage triggers a massive, unwarranted authority assumption in others',
                                ),
                                "extraction_type": "explicit",
                                "confidence": "high",
                            },
                            {
                                "path": f"MM_CANONICAL_216/{models['information-asymmetry']['source_file']}",
                                "quote": _first_list_item(models["information-asymmetry"]["heuristics"], 1),
                                "extraction_type": "explicit",
                                "confidence": "high",
                            },
                        ],
                    },
                    {
                        "subpattern_id": "general",
                        "display_name": "General Authority-Misinfluence",
                        "description": "A real authority signal is present, but the narrower pilot routes are not yet clearly licensed.",
                        "detectability": "medium",
                        "signal_tags": ["general-authority"],
                        "primary_model_ids": ["first-principles-thinking"],
                        "supporting_model_ids": ["authority-bias", "dialectical-reasoning"],
                        "bindings": [
                            _binding(
                                model_id="first-principles-thinking",
                                role="primary",
                                activation_context=(
                                    "Use when rank is shaping the answer and the first corrective move is to separate the claim from the status of the person making it."
                                ),
                                source_path=f"MM_CANONICAL_216/{models['first-principles-thinking']['source_file']}",
                                source_quote=_first_list_item(models["first-principles-thinking"]["select_when"], 0),
                                confidence="medium",
                            ),
                        ],
                        "source_refs": [
                            {
                                "path": "The_Psychology_of_Human_Misjudgment.md",
                                "quote": _require_text(
                                    psychology_text,
                                    "man is often destined to suffer greatly when the leader is wrong",
                                ),
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
    chunks = [
        _chunk(
            chunk_id="ab_diag_prestige",
            model_id="authority-bias",
            chunk_type="diagnosis",
            text="Title, referral, brand, or visible expertise is being treated as evidence that the recommendation is correct.",
            source_file=f"MM_CANONICAL_216/{models['authority-bias']['source_file']}",
            source_quote=_first_list_item(models["authority-bias"]["danger_when"], 0),
            extraction_type="inferred",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("prestige-cue-substitution",),
        ),
        _chunk(
            chunk_id="ab_challenge_prestige",
            model_id="authority-bias",
            chunk_type="premortem_question",
            text=_first_list_item(models["authority-bias"]["premortem_questions"], 0),
            source_file=f"MM_CANONICAL_216/{models['authority-bias']['source_file']}",
            source_quote=_first_list_item(models["authority-bias"]["premortem_questions"], 0),
            extraction_type="explicit",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("prestige-cue-substitution",),
        ),
        _chunk(
            chunk_id="fpt_protocol_prestige",
            model_id="first-principles-thinking",
            chunk_type="protocol",
            text="Strip the recommendation down to facts, constraints, and falsifiable claims before giving status any weight.",
            source_file=f"MM_CANONICAL_216/{models['first-principles-thinking']['source_file']}",
            source_quote=_first_list_item(models["first-principles-thinking"]["select_when"], 1),
            extraction_type="inferred",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("prestige-cue-substitution",),
        ),
        _chunk(
            chunk_id="ab_guardrail_prestige",
            model_id="authority-bias",
            chunk_type="guardrail",
            text=_first_list_item(models["authority-bias"]["danger_when"], 0),
            source_file=f"MM_CANONICAL_216/{models['authority-bias']['source_file']}",
            source_quote=_first_list_item(models["authority-bias"]["danger_when"], 0),
            extraction_type="explicit",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("prestige-cue-substitution",),
            guardrail_tags=("prestige-as-proof", "credential-halo"),
        ),
        _chunk(
            chunk_id="ab_diag_deference",
            model_id="authority-bias",
            chunk_type="diagnosis",
            text="Borrowed conviction from a credible source is replacing independent checking or falsification.",
            source_file=f"MM_CANONICAL_216/{models['authority-bias']['source_file']}",
            source_quote=_first_list_item(models["authority-bias"]["danger_when"], 0),
            extraction_type="inferred",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("deference-overrides-verification",),
        ),
        _chunk(
            chunk_id="dr_challenge_deference",
            model_id="dialectical-reasoning",
            chunk_type="challenge",
            text=_first_list_item(models["dialectical-reasoning"]["premortem_questions"], 0),
            source_file=f"MM_CANONICAL_216/{models['dialectical-reasoning']['source_file']}",
            source_quote=_first_list_item(models["dialectical-reasoning"]["premortem_questions"], 0),
            extraction_type="explicit",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("deference-overrides-verification",),
        ),
        _chunk(
            chunk_id="fpt_protocol_deference",
            model_id="first-principles-thinking",
            chunk_type="protocol",
            text="List the facts that would still hold if the authority were wrong, then test the thesis against those facts before escalating commitment.",
            source_file=f"MM_CANONICAL_216/{models['first-principles-thinking']['source_file']}",
            source_quote=_first_list_item(models["first-principles-thinking"]["premortem_questions"], 0),
            extraction_type="inferred",
            confidence="medium",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("deference-overrides-verification",),
        ),
        _chunk(
            chunk_id="ab_guardrail_deference",
            model_id="authority-bias",
            chunk_type="guardrail",
            text=_first_list_item(models["authority-bias"]["danger_when"], 0),
            source_file=f"MM_CANONICAL_216/{models['authority-bias']['source_file']}",
            source_quote=_first_list_item(models["authority-bias"]["danger_when"], 0),
            extraction_type="explicit",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("deference-overrides-verification",),
            guardrail_tags=("borrowed-conviction", "falsification-skipped"),
        ),
        _chunk(
            chunk_id="pd_diag_protocol",
            model_id="power-dynamics",
            chunk_type="diagnosis",
            text="Rank, urgency, or deal pressure is being treated as sufficient reason to bypass standing controls.",
            source_file="munger_structural_mapping.md",
            source_quote=_require_text(
                mapping_section,
                "following the instructions of an authority figure even when it causes harm or contradicts common sense",
            ),
            extraction_type="inferred",
            confidence="medium",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("authority-overrides-protocol",),
        ),
        _chunk(
            chunk_id="ps_challenge_protocol",
            model_id="psychological-safety",
            chunk_type="challenge",
            text=_first_list_item(models["psychological-safety"]["premortem_questions"], 0),
            source_file=f"MM_CANONICAL_216/{models['psychological-safety']['source_file']}",
            source_quote=_first_list_item(models["psychological-safety"]["premortem_questions"], 0),
            extraction_type="explicit",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("authority-overrides-protocol",),
        ),
        _chunk(
            chunk_id="uxrm_protocol_authority",
            model_id="user-experience-research-methods",
            chunk_type="protocol",
            text="Require direct user or operating evidence before granting an authority figure permission to bypass the normal control path.",
            source_file="munger_structural_mapping.md",
            source_quote=_require_text(
                mapping_section,
                "forces the organization to place empirical evidence from actual user behavior above the rank or intuition of authority figures",
            ),
            extraction_type="inferred",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("authority-overrides-protocol",),
        ),
        _chunk(
            chunk_id="ps_guardrail_protocol",
            model_id="psychological-safety",
            chunk_type="guardrail",
            text=_first_list_item(models["psychological-safety"]["failure_modes"], 0),
            source_file=f"MM_CANONICAL_216/{models['psychological-safety']['source_file']}",
            source_quote=_first_list_item(models["psychological-safety"]["failure_modes"], 0),
            extraction_type="explicit",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("authority-overrides-protocol",),
            guardrail_tags=("rank-bypasses-control", "challenge-rights-suppressed"),
        ),
        _chunk(
            chunk_id="ia_diag_gap",
            model_id="information-asymmetry",
            chunk_type="diagnosis",
            text="A slight expertise edge is being stretched into broad epistemic dominance, so judgment is being outsourced too widely.",
            source_file=f"MM_CANONICAL_216/{models['information-asymmetry']['source_file']}",
            source_quote=_first_list_item(models["information-asymmetry"]["heuristics"], 1),
            extraction_type="inferred",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("knowledge-gap-elasticity",),
        ),
        _chunk(
            chunk_id="fpt_challenge_gap",
            model_id="first-principles-thinking",
            chunk_type="challenge",
            text=_first_list_item(models["first-principles-thinking"]["premortem_questions"], 0),
            source_file=f"MM_CANONICAL_216/{models['first-principles-thinking']['source_file']}",
            source_quote=_first_list_item(models["first-principles-thinking"]["premortem_questions"], 0),
            extraction_type="explicit",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("knowledge-gap-elasticity",),
        ),
        _chunk(
            chunk_id="dr_protocol_gap",
            model_id="dialectical-reasoning",
            chunk_type="protocol",
            text="Force the expert thesis to face a real antithesis before letting a narrow knowledge edge dictate the whole decision.",
            source_file="munger_structural_mapping.md",
            source_quote=_require_text(
                mapping_section,
                "forces the authority's thesis to face an antithesis, breaking the halo effect and demanding rigorous proof over rank",
            ),
            extraction_type="inferred",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("knowledge-gap-elasticity",),
        ),
        _chunk(
            chunk_id="ia_guardrail_gap",
            model_id="information-asymmetry",
            chunk_type="guardrail",
            text=_first_list_item(models["information-asymmetry"]["danger_when"], 0),
            source_file=f"MM_CANONICAL_216/{models['information-asymmetry']['source_file']}",
            source_quote=_first_list_item(models["information-asymmetry"]["danger_when"], 0),
            extraction_type="explicit",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("knowledge-gap-elasticity",),
            guardrail_tags=("knowledge-gap-overreach", "incentive-blindness"),
        ),
        _chunk(
            chunk_id="ab_diag_general",
            model_id="authority-bias",
            chunk_type="diagnosis",
            text="The answer is giving rank or expertise too much evidential weight without defining what proof would overrule it.",
            source_file=f"MM_CANONICAL_216/{models['authority-bias']['source_file']}",
            source_quote=_first_list_item(models["authority-bias"]["select_when"], 0),
            extraction_type="inferred",
            confidence="medium",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("general",),
        ),
        _chunk(
            chunk_id="fpt_challenge_general",
            model_id="first-principles-thinking",
            chunk_type="challenge",
            text=_first_list_item(models["first-principles-thinking"]["premortem_questions"], 0),
            source_file=f"MM_CANONICAL_216/{models['first-principles-thinking']['source_file']}",
            source_quote=_first_list_item(models["first-principles-thinking"]["premortem_questions"], 0),
            extraction_type="explicit",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("general",),
        ),
        _chunk(
            chunk_id="dr_protocol_general",
            model_id="dialectical-reasoning",
            chunk_type="protocol",
            text="Write down the authority thesis, its strongest rival explanation, and the evidence that would favor one over the other.",
            source_file=f"MM_CANONICAL_216/{models['dialectical-reasoning']['source_file']}",
            source_quote=_first_list_item(models["dialectical-reasoning"]["select_when"], 1),
            extraction_type="inferred",
            confidence="medium",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("general",),
        ),
        _chunk(
            chunk_id="ab_guardrail_general",
            model_id="authority-bias",
            chunk_type="guardrail",
            text=_first_list_item(models["authority-bias"]["danger_when"], 0),
            source_file=f"MM_CANONICAL_216/{models['authority-bias']['source_file']}",
            source_quote=_first_list_item(models["authority-bias"]["danger_when"], 0),
            extraction_type="explicit",
            confidence="high",
            tendency_ids=("authority-misinfluence-tendency",),
            subpattern_ids=("general",),
            guardrail_tags=("authority-untested", "status-over-proof"),
        ),
    ]
    return {"version": "0.1", "chunks": chunks}


def _build_structural_signal_lexicon() -> dict[str, object]:
    return {
        "version": "0.1",
        "operators": [
            "treats",
            "borrows",
            "instead of",
            "without",
            "replaces",
            "bypasses",
            "because",
            "before",
        ],
        "stopwords": [
            "the",
            "and",
            "for",
            "with",
            "from",
            "into",
            "this",
            "that",
            "they",
            "them",
            "their",
            "what",
            "when",
            "where",
            "which",
            "while",
            "would",
            "could",
            "should",
            "have",
            "has",
            "had",
            "are",
            "was",
            "were",
            "been",
            "being",
            "about",
            "across",
            "after",
            "before",
            "because",
        ],
        "tendencies": {
            "authority-misinfluence-tendency": {
                "subpatterns": {
                    "prestige-cue-substitution": {
                        "signal_tags": ["prestige-as-proof", "credential-halo"],
                        "cue_phrases": ["title", "referral", "brand", "prestige"],
                    },
                    "deference-overrides-verification": {
                        "signal_tags": ["borrowed-conviction", "falsification-skipped"],
                        "cue_phrases": ["independent check", "verification", "falsification", "credible source"],
                    },
                    "authority-overrides-protocol": {
                        "signal_tags": ["rank-bypasses-control", "challenge-rights-suppressed"],
                        "cue_phrases": ["protocol", "exception", "urgency", "senior"],
                    },
                    "knowledge-gap-elasticity": {
                        "signal_tags": ["guru-overreach", "outsourced-judgment"],
                        "cue_phrases": ["knowledge gap", "guru", "expert edge", "too widely"],
                    },
                    "general": {
                        "signal_tags": ["general-authority"],
                        "cue_phrases": ["authority", "rank", "expertise", "proof"],
                    },
                }
            }
        },
    }


def _build_case_expectations() -> dict[str, object]:
    return {
        "version": "0.1",
        "tendency_id": "authority-misinfluence-tendency",
        "cases": {
            "hiring-rush-manager": {
                "preferred_subpatterns": ["prestige-cue-substitution"],
                "acceptable_subpatterns": ["knowledge-gap-elasticity", "general"],
                "notes": "Trusted referral and visible expertise are the primary authority signal in the pilot slice.",
                "lane_expectations": {
                    "required_lanes": ["diagnosis", "challenge", "protocol", "tension"],
                    "lane_backing": {
                        "diagnosis": {
                            "model_ids": ["authority-bias"],
                            "source_files": ["MM_CANONICAL_216/Authority_Bias_rag.md"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "challenge": {
                            "model_ids": ["authority-bias"],
                            "source_files": ["MM_CANONICAL_216/Authority_Bias_rag.md"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "protocol": {
                            "model_ids": ["first-principles-thinking"],
                            "source_files": ["MM_CANONICAL_216/First_Principles_Thinking_rag.md"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "tension": {
                            "model_ids": ["authority-bias"],
                            "source_files": ["MM_CANONICAL_216/Authority_Bias_rag.md"],
                            "guardrail_tags": ["prestige-as-proof", "credential-halo"],
                            "require_no_blocking_quality_flags": True,
                        },
                    },
                },
                "activation_context_contains_any": ["title", "referral", "expertise", "proof"],
                "activation_context_source_paths": ["MM_CANONICAL_216/Authority_Bias_rag.md"],
                "require_no_activation_context_blocking_quality_flags": True,
            },
            "partnership-announcement": {
                "preferred_subpatterns": ["deference-overrides-verification"],
                "acceptable_subpatterns": ["prestige-cue-substitution", "general"],
                "notes": "The strongest authority read is borrowed confidence from credible parties displacing real verification.",
                "lane_expectations": {
                    "required_lanes": ["diagnosis", "challenge", "protocol", "tension"],
                    "lane_backing": {
                        "diagnosis": {
                            "model_ids": ["authority-bias"],
                            "source_files": ["MM_CANONICAL_216/Authority_Bias_rag.md"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "challenge": {
                            "model_ids": ["dialectical-reasoning"],
                            "source_files": ["MM_CANONICAL_216/Dialectical_Reasoning_rag.md"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "protocol": {
                            "model_ids": ["first-principles-thinking"],
                            "source_files": ["MM_CANONICAL_216/First_Principles_Thinking_rag.md"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "tension": {
                            "model_ids": ["authority-bias"],
                            "source_files": ["MM_CANONICAL_216/Authority_Bias_rag.md"],
                            "guardrail_tags": ["borrowed-conviction", "falsification-skipped"],
                            "require_no_blocking_quality_flags": True,
                        },
                    },
                },
                "activation_context_contains_any": ["authority", "thesis", "antithesis", "proof"],
                "activation_context_source_paths": ["munger_structural_mapping.md"],
                "require_no_activation_context_blocking_quality_flags": True,
            },
            "security-exception-fast-track": {
                "preferred_subpatterns": ["authority-overrides-protocol"],
                "acceptable_subpatterns": ["deference-overrides-verification", "general"],
                "notes": "The strongest authority read is status-driven suspension of controls under urgency.",
                "lane_expectations": {
                    "required_lanes": ["diagnosis", "challenge", "protocol", "tension"],
                    "lane_backing": {
                        "diagnosis": {
                            "model_ids": ["power-dynamics"],
                            "source_files": ["munger_structural_mapping.md"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "challenge": {
                            "model_ids": ["psychological-safety"],
                            "source_files": ["MM_CANONICAL_216/Psychological_Safety_rag.md"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "protocol": {
                            "model_ids": ["user-experience-research-methods"],
                            "source_files": ["munger_structural_mapping.md"],
                            "require_no_blocking_quality_flags": True,
                        },
                        "tension": {
                            "model_ids": ["psychological-safety"],
                            "source_files": ["MM_CANONICAL_216/Psychological_Safety_rag.md"],
                            "guardrail_tags": ["rank-bypasses-control", "challenge-rights-suppressed"],
                            "require_no_blocking_quality_flags": True,
                        },
                    },
                },
                "activation_context_contains_any": ["local knowledge", "challenge", "upward", "rank"],
                "activation_context_source_paths": ["MM_CANONICAL_216/Psychological_Safety_rag.md"],
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
            if chunk.get("chunk_type") == "guardrail" and not chunk.get("guardrail_tags"):
                advisory_flags.append("missing-guardrail-tags")
            quality["blocking_flags"] = blocking_flags
            quality["advisory_flags"] = advisory_flags


def _build_quality_report(
    *,
    subpattern_catalog: dict[str, object],
    compiled_chunks: dict[str, object],
) -> dict[str, object]:
    chunk_rows: list[dict[str, object]] = []
    chunks_with_blocking_flags = 0
    for chunk in compiled_chunks.get("chunks", []):
        if not isinstance(chunk, dict):
            continue
        quality = chunk.get("quality", {}) if isinstance(chunk.get("quality", {}), dict) else {}
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

    binding_rows: list[dict[str, object]] = []
    bindings_with_blocking_flags = 0
    tendency_payloads = subpattern_catalog.get("tendencies", {})
    if isinstance(tendency_payloads, dict):
        for tendency_id, tendency in tendency_payloads.items():
            if not isinstance(tendency, dict):
                continue
            for subpattern in tendency.get("subpatterns", []):
                if not isinstance(subpattern, dict):
                    continue
                for binding in subpattern.get("bindings", []):
                    if not isinstance(binding, dict):
                        continue
                    quality = binding.get("quality", {}) if isinstance(binding.get("quality", {}), dict) else {}
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
    tendency_ids: tuple[str, ...],
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
        "tendency_ids": list(tendency_ids),
        "subpattern_ids": list(subpattern_ids),
        "guardrail_tags": list(guardrail_tags),
    }


def _first_list_item(payload: object, index: int) -> str:
    if not isinstance(payload, list) or index >= len(payload):
        raise ValueError(f"Missing list item {index}")
    value = payload[index]
    if isinstance(value, dict):
        return str(value.get("description") or value.get("mode") or "").strip()
    text = str(value).strip()
    if not text:
        raise ValueError(f"Missing text at index {index}")
    return text


def _require_text(text: str, needle: str) -> str:
    normalized_text = str(text)
    idx = normalized_text.lower().find(needle.lower())
    if idx < 0:
        raise ValueError(f"Could not find expected text fragment: {needle}")
    return normalized_text[idx : idx + len(needle)]


def _copy_if_needed(source: Path, destination: Path) -> None:
    source = Path(source)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() == destination.resolve():
        return
    shutil.copy2(source, destination)
