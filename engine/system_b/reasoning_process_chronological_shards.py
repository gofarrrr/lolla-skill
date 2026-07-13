"""Provider-free chronological shard packets for four reasoning-process families."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .conversation_state_candidates import build_source_catalog
from .reasoning_process_view_specific import VIEW_QUESTIONS, ViewSpecificInterfaceError
from .reasoning_process_view_specific_v3 import SUPPORTED_VIEWS
from .reasoning_process_views import canonical_json_bytes, sha256_bytes

PACKET_SCHEMA = "lolla.reasoning_process_chronological_shard_packet.v1"
CONTIGUOUS_SHARDS = ((1, 2, 3), (4, 5), (6, 7))
POSITION_SHARDS = ((1, 7), (2, 3, 4), (5, 6))
MAX_RECORDS_PER_SHARD = 2


def _annotated_turns(catalog, span_to_alias: Mapping[str, str], turns: Sequence[int]) -> tuple[str, list[str]]:
    lines: list[str] = []
    aliases: list[str] = []
    for turn in turns:
        for speaker in ("user", "assistant"):
            spans = [
                span
                for span in catalog.spans
                if span.kind == "sentence" and span.turn_index == turn and span.speaker == speaker
            ]
            if not spans:
                continue
            lines.append(f"[Turn {turn} {speaker.upper()}]")
            for span in spans:
                alias = span_to_alias[span.span_id]
                lines.append(f"{alias}\t{span.text}")
                aliases.append(alias)
    return "\n".join(lines), aliases


def build_chronological_shard_packets(
    *,
    case_id: str,
    source_path: str,
    source_text: str,
    global_alias_map: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    catalog = build_source_catalog(source_text=source_text, source_path=source_path)
    span_to_alias = {str(item["span_id"]): str(item["alias"]) for item in global_alias_map}
    sentence_spans = [span for span in catalog.spans if span.kind == "sentence"]
    if set(span_to_alias) != {span.span_id for span in sentence_spans}:
        raise ViewSpecificInterfaceError("shard alias map and source sentences differ")
    observed_turns = sorted({span.turn_index for span in catalog.spans if span.kind == "turn"})
    if observed_turns != list(range(1, 8)):
        raise ViewSpecificInterfaceError("v1 chronological shards require seven user-assistant pairs")
    packets: list[dict[str, Any]] = []
    for view_kind in SUPPORTED_VIEWS:
        shard_turns = POSITION_SHARDS if view_kind == "position_and_decision_trajectory" else CONTIGUOUS_SHARDS
        family_focal_aliases: list[str] = []
        for shard_index, turns in enumerate(shard_turns, start=1):
            focal_text, focal_aliases = _annotated_turns(catalog, span_to_alias, turns)
            prior_turn = min(turns) - 1 if min(turns) > 1 else None
            context_text, context_aliases = (
                _annotated_turns(catalog, span_to_alias, (prior_turn,))
                if prior_turn is not None
                else ("", [])
            )
            family_focal_aliases.extend(focal_aliases)
            endpoint = view_kind == "position_and_decision_trajectory" and shard_index == 1
            packet = {
                "schema_version": PACKET_SCHEMA,
                "status": "target_blind_provider_free_chronological_shard",
                "case_id": case_id,
                "shard_id": f"{case_id}-{view_kind}-shard-{shard_index:02d}",
                "view_kind": view_kind,
                "question": VIEW_QUESTIONS[view_kind],
                "shard_kind": "position_endpoint_comparison" if endpoint else "contiguous_chronological_shard",
                "focal_turn_indices": list(turns),
                "source": {
                    "source_path": source_path,
                    "source_sha256": "sha256:" + sha256_bytes(source_text.encode("utf-8")),
                    "conversation_message_count": catalog.message_count,
                },
                "prior_context": {
                    "included": bool(context_aliases),
                    "annotated_sentence_text": context_text,
                    "evidence_aliases": context_aliases,
                    "general_citation_allowed": False,
                    "role_limited_citation_policy": (
                        "prior_claim_or_frame_only"
                        if view_kind == "challenge_and_revision_response" and context_aliases
                        else "starting_state_only"
                        if view_kind == "position_and_decision_trajectory" and context_aliases
                        else "none"
                    ),
                },
                "focal_region": {
                    "citation_allowed": True,
                    "annotated_sentence_text": focal_text,
                    "evidence_aliases": focal_aliases,
                },
                "response_contract": {
                    "maximum_records": MAX_RECORDS_PER_SHARD,
                    "valid_empty_output_allowed": True,
                    "relationship_roles_unchanged_from_v3": True,
                    "free_form_source_quotes_allowed": False,
                    "auxiliary_observation_ids_allowed": False,
                    "global_synthesis_requested": False,
                },
                "boundary": {
                    "protected_target_included": False,
                    "source_review_fixture_included": False,
                    "auxiliary_ledger_included": False,
                    "semantic_prefilter_performed": False,
                    "deterministic_semantic_gate_performed": False,
                    "global_synthesis_requested": False,
                    "direct_graph_routing_allowed": False,
                },
            }
            wrapper = {
                "packet": packet,
                "focal_alias_map": [item for item in global_alias_map if item["alias"] in focal_aliases],
                "context_alias_map": [item for item in global_alias_map if item["alias"] in context_aliases],
                "metrics": {
                    "input_utf8_bytes": len(canonical_json_bytes(packet)),
                    "focal_sentence_count": len(focal_aliases),
                    "context_sentence_count": len(context_aliases),
                    "future_max_records": MAX_RECORDS_PER_SHARD,
                },
            }
            validate_chronological_shard_packet(wrapper, source_text=source_text)
            packets.append(wrapper)
        expected = [str(item["alias"]) for item in global_alias_map]
        if len(family_focal_aliases) != len(set(family_focal_aliases)) or set(family_focal_aliases) != set(expected):
            raise ViewSpecificInterfaceError(f"{view_kind} focal shards do not partition source aliases")
    return packets


def validate_chronological_shard_packet(wrapper: Mapping[str, Any], *, source_text: str) -> dict[str, Any]:
    packet = wrapper.get("packet")
    if not isinstance(packet, Mapping) or packet.get("schema_version") != PACKET_SCHEMA:
        raise ViewSpecificInterfaceError("invalid chronological shard packet")
    if packet.get("view_kind") not in SUPPORTED_VIEWS:
        raise ViewSpecificInterfaceError("unsupported chronological shard family")
    if packet.get("source", {}).get("source_sha256") != "sha256:" + sha256_bytes(source_text.encode("utf-8")):
        raise ViewSpecificInterfaceError("chronological shard source hash drifted")
    focal = packet.get("focal_region")
    context = packet.get("prior_context")
    if not isinstance(focal, Mapping) or not isinstance(context, Mapping):
        raise ViewSpecificInterfaceError("chronological shard regions are missing")
    focal_aliases = focal.get("evidence_aliases")
    context_aliases = context.get("evidence_aliases")
    if not isinstance(focal_aliases, list) or not focal_aliases or not isinstance(context_aliases, list):
        raise ViewSpecificInterfaceError("chronological shard aliases are invalid")
    if set(focal_aliases) & set(context_aliases):
        raise ViewSpecificInterfaceError("chronological shard focal and context aliases overlap")
    if {item["alias"] for item in wrapper.get("focal_alias_map", [])} != set(focal_aliases):
        raise ViewSpecificInterfaceError("chronological shard focal map drifted")
    if {item["alias"] for item in wrapper.get("context_alias_map", [])} != set(context_aliases):
        raise ViewSpecificInterfaceError("chronological shard context map drifted")
    policy = context.get("role_limited_citation_policy")
    allowed = {"none", "prior_claim_or_frame_only", "starting_state_only"}
    if policy not in allowed or (not context_aliases and policy != "none"):
        raise ViewSpecificInterfaceError("chronological shard context policy is invalid")
    if context.get("general_citation_allowed") is not False or focal.get("citation_allowed") is not True:
        raise ViewSpecificInterfaceError("chronological shard citation authority drifted")
    if len(canonical_json_bytes(packet)) > 12000:
        raise ViewSpecificInterfaceError("chronological shard exceeds byte budget")
    return {
        "status": "chronological_shard_packet_valid",
        "case_id": packet["case_id"],
        "view_kind": packet["view_kind"],
        "shard_id": packet["shard_id"],
        "input_utf8_bytes": len(canonical_json_bytes(packet)),
        "semantic_adequacy_validated": False,
    }
