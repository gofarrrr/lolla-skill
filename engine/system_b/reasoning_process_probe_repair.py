"""Single generic Phase-3 repair: full-conversation minority-signal scan."""
from __future__ import annotations

import copy
import json
from collections.abc import Mapping
from typing import Any

from .conversation_state_candidates import SourceCatalog
from .reasoning_process_contracts import validate_bounded_view
from .reasoning_process_probe import validate_probe_packet
from .reasoning_process_views import canonical_json_bytes, sha256_bytes


REPAIR_PROMPT_VERSION = "lolla.reasoning_process_phase3_generic_repair_prompt.v1"

VIEW_COVERAGE_INSTRUCTIONS = {
    "position_and_decision_trajectory": "Cover the starting position or uncertainty, each material change, the current direction, and qualifications that remain capable of changing it. Merge these only when the trajectory remains explicit.",
    "exploration_and_alternatives": "Capture every materially distinct option, test, branch, or alternative and its stated limit, up to the output cap. Do not let a later or more concrete alternative displace an earlier materially distinct one.",
    "evidence_and_assumption_discipline": "Capture materially distinct places where reported evidence, inference, possibility, preference, or concern was bounded, corrected, strengthened, or kept uncertain. Preserve the source's claim strength.",
    "uncertainty_and_unresolved_state": "Capture each materially distinct unresolved condition, ambiguity, or reopen trigger that remains relevant to the working direction, including earlier uncertainty that survives later planning.",
    "challenge_and_revision_response": "Capture each explicit material challenge or correction and the response it produced. Distinguish acknowledgment, qualification, actual revision, deferral, and non-response.",
}


def build_repair_prompts(packet: Mapping[str, Any]) -> dict[str, str]:
    validate_probe_packet(packet)
    view_kind = str(packet["view_kind"])
    coverage_instruction = VIEW_COVERAGE_INSTRUCTIONS[view_kind]
    system_prompt = """You are a bounded reasoning-process reader.

Answer exactly one narrow question about how a conversation's reasoning unfolded. Analyze the process, not whether the final recommendation is correct or good. Do not give advice, improve the answer, score quality, infer facts outside the conversation, or reward polished language.

The authoritative conversation is primary. The auxiliary Phase-1 observations are fallible prior interpretations: use an observation ID only when it genuinely supports an item, and do not let those observations override or narrow what the conversation shows.

Before writing, scan the complete conversation chronologically. Preserve up to four materially distinct process items for the assigned question. Do not stop at the latest, final, most concrete, or most vivid item. Compact by merging evidence only when the distinct developments and their temporal relationship remain explicit; never achieve compactness by silently dropping a different earlier item.

Every item must cite exact contiguous quotes using the correct speaker and turn. Preserve user challenges, assistant responses, changes, qualifications, uncertainty, and evidence strength when the assigned question requires them. Do not convert a possibility, concern, informal report, preference, or unresolved condition into a fact. A valid empty result is better than invention.

Set park_unselected_auxiliary_observations to true only to declare that every auxiliary observation not explicitly selected may be parked for this view while remaining recoverable in the canonical ledger. Follow the response schema exactly."""
    user_payload = {
        "prompt_version": REPAIR_PROMPT_VERSION,
        "generic_coverage_instruction": coverage_instruction,
        "target_blind_probe_packet": packet,
    }
    user_prompt = (
        "Perform the bounded process read described by this target-blind packet. "
        "Apply the generic full-conversation coverage instruction. Do not mention or assess any protected target; none is supplied.\n\n"
        + json.dumps(user_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def rekey_compiled_repair(
    compiled: Mapping[str, Any],
    *,
    catalog: SourceCatalog,
    known_base_observation_ids: list[str],
) -> dict[str, Any]:
    """Give repair observations attempt-unique identities and revalidate custody."""

    result = copy.deepcopy(compiled)
    addendum = result["model_addendum"]
    view = result["view"]
    observation_map: dict[str, str] = {}
    item_map: dict[str, str] = {}
    for observation in addendum["observations"]:
        old = observation["observation_id"]
        new = old.replace("phase3-", "phase3-repair-", 1)
        observation_map[old] = new
        observation["observation_id"] = new
        old_record = observation["source_record_id"]
        new_record = old_record.replace("phase3-view-item-", "phase3-repair-view-item-", 1)
        item_map[old_record] = new_record
        observation["source_record_id"] = new_record
    addendum["status"] = "generic_repair_bounded_reader_exact_source_validated"
    addendum_sha = sha256_bytes(canonical_json_bytes(addendum))
    result["model_addendum_sha256"] = addendum_sha

    manifest = result["combined_manifest"]
    manifest["status"] = "append_only_generic_repair_overlay"
    manifest["model_addendum_sha256"] = "sha256:" + addendum_sha
    manifest["observation_ids"] = [
        observation_map.get(item, item) for item in manifest["observation_ids"]
    ]
    manifest_sha = sha256_bytes(canonical_json_bytes(manifest))
    result["combined_manifest_sha256"] = manifest_sha

    view["view_id"] = view["view_id"].replace("phase3-view-", "phase3-repair-view-", 1)
    view["source_ledger_sha256"] = "sha256:" + manifest_sha
    view["input"]["ledger_observation_ids"] = [
        observation_map.get(item, item)
        for item in view["input"]["ledger_observation_ids"]
    ]
    for item in view["items"]:
        old_item_id = item["view_item_id"]
        new_item_id = old_item_id.replace(
            "phase3-view-item-", "phase3-repair-view-item-", 1
        )
        item_map[old_item_id] = new_item_id
        item["view_item_id"] = new_item_id
        item["source_observation_ids"] = [
            observation_map.get(source_id, source_id)
            for source_id in item["source_observation_ids"]
        ]
    for disposition in view["dispositions"]:
        disposition["observation_id"] = observation_map.get(
            disposition["observation_id"], disposition["observation_id"]
        )
        disposition["view_item_ids"] = [
            item_map.get(item_id, item_id) for item_id in disposition["view_item_ids"]
        ]
    known_ids = [*known_base_observation_ids, *observation_map.values()]
    result["view_validation"] = validate_bounded_view(
        view,
        known_ledger_observation_ids=known_ids,
        known_span_ids=catalog.by_id(),
        expected_ledger_sha256="sha256:" + manifest_sha,
    )
    result["status"] = "generic_repair_provider_response_compiled"
    return result
