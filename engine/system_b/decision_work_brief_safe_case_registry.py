"""Checked-in-safe case registry for Decision Work Brief runtime supply.

The registry maps known case keys to already-reviewed checked-in-safe Decision
Work Brief artifacts. It supplies refs only; it does not interpret
conversation meaning, call models, mutate archives, score advice, or authorize
action.
"""
from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any


REGISTRY_SCHEMA_VERSION = (
    "lolla.decision_work_brief_runtime_checked_in_safe_case_registry.v0"
)
REGISTRY_ENTRY_SCHEMA_VERSION = (
    "lolla.decision_work_brief_runtime_checked_in_safe_case_registry_entry.v0"
)
DEFAULT_REGISTRY_RELPATH = (
    "docs/conversation-understanding/"
    "decision-work-brief-runtime-checked-in-safe-case-registry-v0.json"
)
REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_PRIVATE_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
SAFE_ARTIFACT_REF_FIELDS = {
    "decision_work_brief_json_ref": {
        "resolver_kwarg": "brief_json_path",
        "suffix": ".json",
        "schema_versions": {"lolla.decision_work_brief.v0"},
    },
    "rendered_brief_markdown_ref": {
        "resolver_kwarg": "brief_markdown_path",
        "suffix": ".md",
        "schema_versions": set(),
    },
    "enriched_brief_markdown_ref": {
        "resolver_kwarg": "enriched_brief_path",
        "suffix": ".md",
        "schema_versions": set(),
    },
    "interpretation_read_json_ref": {
        "resolver_kwarg": "interpretation_read_path",
        "suffix": ".json",
        "schema_versions": {
            "lolla.decision_work_conversation_interpretation_tiny_offline_read.v0",
            "lolla.decision_work_conversation_interpretation_second_tiny_offline_read.v0",
            "lolla.decision_work_conversation_interpretation_read.v0",
        },
    },
    "automatic_triage_packet_json_ref": {
        "resolver_kwarg": "triage_packet_path",
        "suffix": ".json",
        "schema_versions": {"lolla.decision_work_automatic_triage_packets.v0"},
    },
    "automatic_triage_read_json_ref": {
        "resolver_kwarg": "triage_read_path",
        "suffix": ".json",
        "schema_versions": {
            "lolla.decision_work_automatic_triage_provisional_read.v0"
        },
    },
}
REQUIRED_FALSE_FLAGS = (
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
)
REQUIRED_NON_CLAIMS = {
    "not_customer_readiness",
    "not_product_proof",
    "not_human_validation",
    "not_advice_correctness",
    "not_answer_quality_scoring",
    "not_agent_action_authorization",
    "not_general_arbitrary_run_solution",
}


class DecisionWorkBriefSafeCaseRegistryError(ValueError):
    """Sanitized checked-in-safe registry input error."""


def load_safe_case_registry(
    registry_path: Path | str = DEFAULT_REGISTRY_RELPATH,
) -> dict[str, Any]:
    """Load and validate the checked-in-safe case registry."""

    registry = _load_json_object(registry_path, description="safe case registry JSON")
    if registry.get("schema_version") != REGISTRY_SCHEMA_VERSION:
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case registry schema version was unsupported"
        )
    entries = registry.get("entries")
    if not isinstance(entries, list) or not entries:
        raise DecisionWorkBriefSafeCaseRegistryError("safe case registry had no entries")
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise DecisionWorkBriefSafeCaseRegistryError(
                "safe case registry entry was not an object"
            )
        _validate_entry(entry)
        for key in _entry_keys(entry):
            if key in seen:
                raise DecisionWorkBriefSafeCaseRegistryError(
                    "safe case registry contained a duplicate case key"
                )
            seen.add(key)
    return registry


def resolve_safe_case_registry_entry(
    *,
    case_key: str,
    registry_path: Path | str = DEFAULT_REGISTRY_RELPATH,
) -> dict[str, Any]:
    """Return one validated registry entry by case key."""

    normalized = _safe_slug(case_key)
    if not normalized:
        raise DecisionWorkBriefSafeCaseRegistryError("case key was empty")
    registry = load_safe_case_registry(registry_path)
    for entry in _entries(registry):
        if normalized in _entry_keys(entry):
            return {
                "schema_version": REGISTRY_ENTRY_SCHEMA_VERSION,
                "registry_ref": _safe_registry_ref(registry_path),
                "registry_schema_version": registry["schema_version"],
                "case_key": normalized,
                "entry": dict(entry),
                "safe_artifact_refs": dict(entry.get("safe_artifact_refs", {})),
                "resolver_mode": "checked_in_safe_case_registry",
                "custody_flags": _custody_flags(),
                "non_claims": _registry_non_claims(registry),
            }
    raise DecisionWorkBriefSafeCaseRegistryError("safe case registry entry was not found")


def resolver_kwargs_from_case_registry(
    *,
    case_key: str,
    registry_path: Path | str = DEFAULT_REGISTRY_RELPATH,
) -> dict[str, Path]:
    """Return resolver kwargs for a checked-in-safe case registry entry."""

    resolved = resolve_safe_case_registry_entry(
        case_key=case_key,
        registry_path=registry_path,
    )
    refs = _mapping(resolved["entry"].get("safe_artifact_refs"))
    kwargs: dict[str, Path] = {}
    for ref_name, ref in refs.items():
        spec = SAFE_ARTIFACT_REF_FIELDS.get(ref_name)
        if spec is None or ref in (None, ""):
            continue
        kwargs[spec["resolver_kwarg"]] = _repo_ref_to_path(_text(ref))
    return kwargs


def render_safe_case_registry_entry_json(
    entry: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """Render one resolved registry entry as JSON."""

    indent = 2 if pretty else None
    return json.dumps(entry, indent=indent, sort_keys=True) + "\n"


def _validate_entry(entry: Mapping[str, Any]) -> None:
    case_id = _text(entry.get("case_id"))
    if not case_id:
        raise DecisionWorkBriefSafeCaseRegistryError("safe case entry was missing case_id")
    if entry.get("allowed_resolver_mode") != "checked_in_safe_case_registry":
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case entry had unsupported resolver mode"
        )
    for flag in REQUIRED_FALSE_FLAGS:
        if entry.get(flag) is not False:
            raise DecisionWorkBriefSafeCaseRegistryError(
                "safe case entry had non-conservative custody flags"
            )
    non_claims = set(_string_list(entry.get("non_claims")))
    if not REQUIRED_NON_CLAIMS <= non_claims:
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case entry was missing required non-claims"
        )
    refs = entry.get("safe_artifact_refs")
    if not isinstance(refs, Mapping):
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case entry was missing safe artifact refs"
        )
    if not (
        _text(refs.get("rendered_brief_markdown_ref"))
        or _text(refs.get("enriched_brief_markdown_ref"))
    ):
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case entry did not include a brief ref"
        )
    if not _text(refs.get("automatic_triage_read_json_ref")):
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case entry did not include a triage read ref"
        )
    for ref_name, ref in refs.items():
        if ref in (None, ""):
            continue
        _validate_safe_artifact_ref(ref_name=ref_name, ref=_text(ref))


def _validate_safe_artifact_ref(*, ref_name: str, ref: str) -> None:
    spec = SAFE_ARTIFACT_REF_FIELDS.get(ref_name)
    if spec is None:
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case registry contained an unsupported ref field"
        )
    if _contains_private_marker(ref):
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case registry ref contained a private marker"
        )
    path = Path(ref)
    if path.is_absolute() or ".." in path.parts:
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case registry refs must be relative repo refs"
        )
    full_path = _repo_ref_to_path(ref)
    if not full_path.exists() or not full_path.is_file():
        raise DecisionWorkBriefSafeCaseRegistryError("safe case registry ref was missing")
    if full_path.suffix != spec["suffix"]:
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case registry ref had unsupported suffix"
        )
    try:
        text = full_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case registry ref was unreadable"
        ) from exc
    if _contains_private_marker(text):
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case registry ref contained private-marker content"
        )
    _validate_schema(ref_name=ref_name, text=text, expected=spec["schema_versions"])


def _validate_schema(*, ref_name: str, text: str, expected: set[str]) -> None:
    if not expected:
        return
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case registry JSON ref was malformed"
        ) from exc
    if not isinstance(payload, Mapping):
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case registry JSON ref root was not an object"
        )
    schema = payload.get("schema_version")
    if schema not in expected:
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case registry JSON ref schema was unsupported"
        )


def _repo_ref_to_path(ref: str) -> Path:
    full_path = (REPO_ROOT / ref).resolve(strict=False)
    try:
        full_path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise DecisionWorkBriefSafeCaseRegistryError(
            "safe case registry ref escaped the repo"
        ) from exc
    return full_path


def _safe_registry_ref(path: Path | str) -> str:
    candidate = Path(path).expanduser()
    try:
        return str(candidate.resolve(strict=False).relative_to(REPO_ROOT))
    except ValueError:
        return candidate.name


def _entry_keys(entry: Mapping[str, Any]) -> set[str]:
    keys = {
        _safe_slug(_text(entry.get("case_id"))),
        _safe_slug(_text(entry.get("run_case_key"))),
        _safe_slug(_text(entry.get("archive_case_slug"))),
    }
    aliases = entry.get("aliases")
    if isinstance(aliases, list):
        keys.update(_safe_slug(alias) for alias in aliases if isinstance(alias, str))
    return {key for key in keys if key}


def _entries(registry: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    entries = registry.get("entries")
    return [entry for entry in entries if isinstance(entry, Mapping)] if isinstance(entries, list) else []


def _registry_non_claims(registry: Mapping[str, Any]) -> list[str]:
    non_claims = _string_list(registry.get("non_claims"))
    return non_claims or sorted(REQUIRED_NON_CLAIMS)


def _custody_flags() -> dict[str, Any]:
    return {
        "human_validated": False,
        "product_proof": False,
        "model_calls": 0,
        "runtime_behavior_changed": False,
        "skill_invoked": False,
        "archive_mutated": False,
        "prompt_changed": False,
        "skill_files_changed": False,
        "answer_quality_scored": False,
        "agent_action_authorized": False,
        "automatic_action_authorized": False,
    }


def _load_json_object(path: Path | str, *, description: str) -> dict[str, Any]:
    input_path = Path(path).expanduser()
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DecisionWorkBriefSafeCaseRegistryError(
            f"{description} was not found"
        ) from exc
    except json.JSONDecodeError as exc:
        raise DecisionWorkBriefSafeCaseRegistryError(
            f"{description} was malformed"
        ) from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkBriefSafeCaseRegistryError(
            f"{description} was not valid UTF-8"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkBriefSafeCaseRegistryError(
            f"{description} root was not an object"
        )
    return payload


def _contains_private_marker(text: str) -> bool:
    return any(marker in text for marker in RAW_PRIVATE_MARKERS)


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.=-]+", "-", value).strip("-")
    return slug


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _text(value: Any, fallback: str = "") -> str:
    return value if isinstance(value, str) and value else fallback
