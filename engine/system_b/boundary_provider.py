from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
import threading
import time
import uuid
from dataclasses import asdict, dataclass, replace
from datetime import date
from typing import Mapping
from urllib import error, request

from .live_pricing import PRICES_LAST_VERIFIED
from .pricing import estimate_chat_cost_usd, lookup_chat_price
from .provider_budget import (
    ProviderBudgetExceeded,
    budget_limits_from_env,
    finalize_provider_call,
    reserve_provider_call,
)


# Stable namespace for deriving x-grok-conv-id from $LOLLA_RUN_ID.
# Random uuid generated once and frozen here so all boundary client
# instances in any future run derive identical conv_ids from the same
# run_id (uuid5 is deterministic given a fixed namespace).
_LOLLA_CONV_ID_NAMESPACE = uuid.UUID("c0c4c1d2-1010-4011-8a1a-15b1ab2c5d57")


_LOGGER = logging.getLogger("system_b.boundary_provider")

DEFAULT_OPENROUTER_MODEL = "google/gemini-3.1-flash-lite"

_STAGE_MAX_OUTPUT_TOKENS = {
    "extraction": 5000,
    "extraction_retry": 5000,
    "pass2": 1800,
    "companion_fingerprint": 1800,
    "companion_verification": 3200,
    "frame_extraction": 2400,
    "frame_reframing": 2400,
    "structural_coverage_classification": 1800,
    "structural_coverage_detection": 1800,
    "structural_coverage_gap_questions": 2200,
    "bullshit_index": 1600,
    "revision": 5000,
    "stakeholder_assumption_check": 1800,
}
DEFAULT_STAGE_MAX_OUTPUT_TOKENS = 2500


@dataclass(frozen=True)
class BoundaryCallMetadata:
    provider_name: str = ""
    served_provider_name: str = ""
    requested_model: str = ""
    served_model: str = ""
    model: str = ""
    model_attribution_status: str = "not_observed"
    status: str = "not_called"
    finish_reason: str = ""
    provider_error_source: str = ""
    provider_error_type: str = ""
    provider_error_code: str = ""
    provider_error_provider_code: str = ""
    provider_error_message_sha256: str = ""
    retry_after_seconds: float | None = None
    raw_message_content: str = ""
    temperature: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    cache_write_tokens: int = 0
    reasoning_tokens: int = 0
    reasoning_disabled: bool = False
    reasoning_details_present: bool = False
    provider_attempted: bool = False
    response_id: str = ""
    exact_cost_usd: float | None = None
    request_max_output_tokens: int = 0
    request_max_price_prompt: float = 0.0
    request_max_price_completion: float = 0.0
    request_provider_order: tuple[str, ...] = ()
    request_allow_fallbacks: bool = False
    request_require_parameters: bool = False
    request_data_collection: str = ""
    request_zdr: bool = False
    run_max_provider_calls: int = 0
    run_max_cost_usd: float = 0.0
    maximum_call_cost_usd: float = 0.0
    budget_reservation_id: str = ""
    pricing_table_version: str = PRICES_LAST_VERIFIED
    pricing_table_stale: bool = False


@dataclass(frozen=True)
class BoundaryCallRecord:
    """Per-call record auto-appended to ``BoundaryClient.call_log``.

    Captures the same fields as ``BoundaryCallMetadata`` plus the stage label
    that the call was made under. Stage is passed per-call (not per-instance)
    so parallel callers on the same client never clobber each other.
    """

    stage: str = "unlabeled"
    tendency_id: str = ""
    provider_name: str = ""
    served_provider_name: str = ""
    requested_model: str = ""
    served_model: str = ""
    model: str = ""
    model_attribution_status: str = "not_observed"
    status: str = "not_called"
    finish_reason: str = ""
    provider_error_source: str = ""
    provider_error_type: str = ""
    provider_error_code: str = ""
    provider_error_provider_code: str = ""
    provider_error_message_sha256: str = ""
    retry_after_seconds: float | None = None
    raw_message_content: str = ""
    temperature: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    cache_write_tokens: int = 0
    reasoning_tokens: int = 0
    reasoning_disabled: bool = False
    reasoning_details_present: bool = False
    provider_attempted: bool = False
    response_id: str = ""
    exact_cost_usd: float | None = None
    request_max_output_tokens: int = 0
    request_max_price_prompt: float = 0.0
    request_max_price_completion: float = 0.0
    request_provider_order: tuple[str, ...] = ()
    request_allow_fallbacks: bool = False
    request_require_parameters: bool = False
    request_data_collection: str = ""
    request_zdr: bool = False
    run_max_provider_calls: int = 0
    run_max_cost_usd: float = 0.0
    maximum_call_cost_usd: float = 0.0
    budget_reservation_id: str = ""
    pricing_table_version: str = PRICES_LAST_VERIFIED
    pricing_table_stale: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _record_from_metadata(
    metadata: BoundaryCallMetadata,
    *,
    stage: str,
    tendency_id: str,
) -> BoundaryCallRecord:
    return BoundaryCallRecord(
        stage=stage or "unlabeled",
        tendency_id=tendency_id,
        provider_name=metadata.provider_name,
        served_provider_name=metadata.served_provider_name,
        requested_model=metadata.requested_model,
        served_model=metadata.served_model,
        model=metadata.model,
        model_attribution_status=metadata.model_attribution_status,
        status=metadata.status,
        finish_reason=metadata.finish_reason,
        provider_error_source=metadata.provider_error_source,
        provider_error_type=metadata.provider_error_type,
        provider_error_code=metadata.provider_error_code,
        provider_error_provider_code=metadata.provider_error_provider_code,
        provider_error_message_sha256=metadata.provider_error_message_sha256,
        retry_after_seconds=metadata.retry_after_seconds,
        raw_message_content=metadata.raw_message_content,
        temperature=metadata.temperature,
        prompt_tokens=metadata.prompt_tokens,
        completion_tokens=metadata.completion_tokens,
        total_tokens=metadata.total_tokens,
        cached_tokens=metadata.cached_tokens,
        cache_write_tokens=metadata.cache_write_tokens,
        reasoning_tokens=metadata.reasoning_tokens,
        reasoning_disabled=metadata.reasoning_disabled,
        reasoning_details_present=metadata.reasoning_details_present,
        provider_attempted=metadata.provider_attempted,
        response_id=metadata.response_id,
        exact_cost_usd=metadata.exact_cost_usd,
        request_max_output_tokens=metadata.request_max_output_tokens,
        request_max_price_prompt=metadata.request_max_price_prompt,
        request_max_price_completion=metadata.request_max_price_completion,
        request_provider_order=metadata.request_provider_order,
        request_allow_fallbacks=metadata.request_allow_fallbacks,
        request_require_parameters=metadata.request_require_parameters,
        request_data_collection=metadata.request_data_collection,
        request_zdr=metadata.request_zdr,
        run_max_provider_calls=metadata.run_max_provider_calls,
        run_max_cost_usd=metadata.run_max_cost_usd,
        maximum_call_cost_usd=metadata.maximum_call_cost_usd,
        budget_reservation_id=metadata.budget_reservation_id,
        pricing_table_version=metadata.pricing_table_version,
        pricing_table_stale=metadata.pricing_table_stale,
    )


def _provider_timeout() -> float:
    raw = os.getenv("LOLLA_LLM_TIMEOUT", "45")
    try:
        value = float(raw)
    except ValueError:
        value = 45.0
    return max(1.0, min(value, 120.0))


def _extract_json_payload(text: str) -> dict[str, object]:
    raw = text.strip()
    if not raw:
        return {}
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines).strip()
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
        return {}
    except json.JSONDecodeError:
        pass

    left = raw.find("{")
    right = raw.rfind("}")
    if left >= 0 and right > left:
        try:
            parsed = json.loads(raw[left : right + 1])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return {}
    return {}


def build_provider_request_policy(
    *, provider_name: str, model: str, stage: str
) -> dict[str, object]:
    """Return the explicit provider/cost/privacy envelope for one call."""

    normalized_stage = str(stage or "unlabeled").strip().lower().replace("-", "_")
    env_suffix = re_safe_env_suffix(normalized_stage)
    default_output = _STAGE_MAX_OUTPUT_TOKENS.get(
        normalized_stage, DEFAULT_STAGE_MAX_OUTPUT_TOKENS
    )
    max_output_tokens = _positive_int_env(
        f"LOLLA_MAX_OUTPUT_TOKENS_{env_suffix}", default_output
    )
    max_prompt_price = _positive_float_env("LOLLA_OPENROUTER_MAX_PROMPT_PRICE", 0.30)
    max_completion_price = _positive_float_env(
        "LOLLA_OPENROUTER_MAX_COMPLETION_PRICE", 1.60
    )
    known_price = lookup_chat_price(provider_name, model)
    if str(provider_name).strip().lower() != "openrouter" and known_price is not None:
        max_prompt_price = max(max_prompt_price, known_price.input_usd_per_mtok)
        max_completion_price = max(max_completion_price, known_price.output_usd_per_mtok)
    maximum_calls, maximum_run_cost = budget_limits_from_env()
    order_raw = str(os.getenv("LOLLA_OPENROUTER_PROVIDER_ORDER", "")).strip()
    if not order_raw and str(model).startswith(DEFAULT_OPENROUTER_MODEL):
        order_raw = "google-vertex/global"
    provider_order = tuple(item.strip() for item in order_raw.split(",") if item.strip())
    is_openrouter = str(provider_name).strip().lower() == "openrouter"
    data_collection = (
        str(os.getenv("LOLLA_OPENROUTER_DATA_COLLECTION", "deny")).strip().lower()
        if is_openrouter
        else ""
    )
    if is_openrouter and data_collection not in {"allow", "deny"}:
        data_collection = "deny"
    return {
        "stage": normalized_stage or "unlabeled",
        "max_output_tokens": max_output_tokens,
        "max_price_prompt": max_prompt_price,
        "max_price_completion": max_completion_price,
        "provider_order": provider_order if is_openrouter else (),
        "allow_fallbacks": (
            _is_truthy_env("LOLLA_OPENROUTER_ALLOW_FALLBACKS") if is_openrouter else False
        ),
        "require_parameters": (
            not _is_falsey_env("LOLLA_OPENROUTER_REQUIRE_PARAMETERS")
            if is_openrouter
            else False
        ),
        "data_collection": data_collection,
        "zdr": _is_truthy_env("LOLLA_OPENROUTER_REQUIRE_ZDR") if is_openrouter else False,
        "maximum_provider_calls": maximum_calls,
        "maximum_run_cost_usd": maximum_run_cost,
        "pricing_table_version": PRICES_LAST_VERIFIED,
        "pricing_table_stale": _pricing_table_is_stale(),
    }


def _maximum_call_cost_usd(
    *, system_prompt: str, user_prompt: str, policy: Mapping[str, object]
) -> float:
    # UTF-8 bytes / 3 is a deliberately conservative prompt-token estimate for
    # budget admission. The provider still reports actual tokens and exact cost.
    prompt_tokens = max(
        1,
        (len(system_prompt.encode("utf-8")) + len(user_prompt.encode("utf-8")) + 2) // 3,
    )
    return round(
        (
            prompt_tokens * float(policy["max_price_prompt"])
            + int(policy["max_output_tokens"]) * float(policy["max_price_completion"])
        )
        / 1_000_000,
        9,
    )


def _positive_int_env(name: str, default: int) -> int:
    try:
        value = int(str(os.getenv(name, "")))
    except ValueError:
        value = default
    return value if value > 0 else default


def _positive_float_env(name: str, default: float) -> float:
    try:
        value = float(str(os.getenv(name, "")))
    except ValueError:
        value = default
    return value if value > 0 else default


def _is_falsey_env(name: str) -> bool:
    return str(os.getenv(name, "")).strip().lower() in {"0", "false", "no", "off"}


def re_safe_env_suffix(value: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in value).upper() or "UNLABELED"


def _pricing_table_is_stale() -> bool:
    try:
        verified = date.fromisoformat(PRICES_LAST_VERIFIED)
    except ValueError:
        return True
    return (date.today() - verified).days > 31


class OpenAICompatibleBoundaryClient:
    supports_parallel_calls = True

    def __init__(
        self,
        *,
        provider_name: str,
        api_key: str,
        base_url: str,
        model: str,
        extra_headers: Mapping[str, str] | None = None,
        temperature: float = 0.2,
    ) -> None:
        self.provider_name = provider_name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.extra_headers = dict(extra_headers or {})
        self.temperature = temperature
        self.timeout = _provider_timeout()
        self._budget_run_id = str(os.getenv("LOLLA_RUN_ID", "")).strip() or f"adhoc_{uuid.uuid4().hex}"
        self.last_call_metadata = BoundaryCallMetadata(
            provider_name=self.provider_name,
            model=self.model,
        )
        self.call_log: list[BoundaryCallRecord] = []
        self._call_log_lock = threading.Lock()

    def run_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        stage: str = "unlabeled",
        tendency_id: str = "",
    ) -> dict[str, object]:
        result, metadata = self.run_json_with_metadata(
            system_prompt, user_prompt, stage=stage, tendency_id=tendency_id
        )
        self.last_call_metadata = metadata
        if metadata.reasoning_disabled and metadata.reasoning_details_present:
            _LOGGER.warning(
                "Boundary response for %s returned reasoning details despite reasoning being disabled",
                self.model,
            )
        return result

    def run_json_with_metadata(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        stage: str = "unlabeled",
        tendency_id: str = "",
    ) -> tuple[dict[str, object], BoundaryCallMetadata]:
        """Thread-safe variant: returns (result, metadata) without side effects.

        Every call (success or failure) is auto-appended to ``self.call_log``
        with the supplied stage label, so no caller needs to remember a
        separate recording hook.
        """
        try:
            result, metadata = self._do_call(system_prompt, user_prompt, stage=stage)
        except Exception:
            # A provider-bound operation is still an attempted call when an
            # unexpected transport/parser exception escapes _do_call. Preserve
            # that fact before re-raising so the extraction layer can persist
            # a truthful terminal sidecar instead of reporting zero calls.
            policy = build_provider_request_policy(
                provider_name=self.provider_name,
                model=self.model,
                stage=stage,
            )
            maximum_call_cost = _maximum_call_cost_usd(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                policy=policy,
            )
            metadata = self._metadata_with_policy(
                BoundaryCallMetadata(
                provider_name=self.provider_name,
                requested_model=self.model,
                model=self.model,
                model_attribution_status="not_observed",
                status="unexpected_error",
                temperature=self.temperature,
                reasoning_disabled=_reasoning_disabled(self._reasoning_config()),
                provider_attempted=True,
                ),
                policy=policy,
                maximum_call_cost_usd=maximum_call_cost,
            )
            with self._call_log_lock:
                self.call_log.append(
                    _record_from_metadata(
                        metadata,
                        stage=stage,
                        tendency_id=tendency_id,
                    )
                )
            raise
        with self._call_log_lock:
            self.call_log.append(
                _record_from_metadata(metadata, stage=stage, tendency_id=tendency_id)
            )
        return result, metadata

    def _do_call(
        self, system_prompt: str, user_prompt: str, *, stage: str = "unlabeled"
    ) -> tuple[dict[str, object], BoundaryCallMetadata]:
        policy = build_provider_request_policy(
            provider_name=self.provider_name,
            model=self.model,
            stage=stage,
        )
        maximum_call_cost = _maximum_call_cost_usd(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            policy=policy,
        )
        if not self.api_key:
            return {}, self._metadata_with_policy(
                BoundaryCallMetadata(
                    provider_name=self.provider_name,
                    requested_model=self.model,
                    model=self.model,
                    model_attribution_status="not_observed",
                    status="missing_api_key",
                ),
                policy=policy,
                maximum_call_cost_usd=maximum_call_cost,
            )

        maximum_calls = int(policy["maximum_provider_calls"])
        maximum_run_cost = float(policy["maximum_run_cost_usd"])
        try:
            reservation_id, _ = reserve_provider_call(
                run_id=self._budget_run_id,
                stage=str(policy["stage"]),
                requested_model=self.model,
                maximum_call_cost_usd=maximum_call_cost,
                maximum_calls=maximum_calls,
                maximum_run_cost_usd=maximum_run_cost,
            )
        except ProviderBudgetExceeded as exc:
            _LOGGER.warning("Provider call blocked before request: %s", exc)
            return {}, self._metadata_with_policy(
                BoundaryCallMetadata(
                    provider_name=self.provider_name,
                    requested_model=self.model,
                    model=self.model,
                    model_attribution_status="not_observed",
                    status="budget_blocked_preflight",
                ),
                policy=policy,
                maximum_call_cost_usd=maximum_call_cost,
            )

        url = f"{self.base_url}/chat/completions"
        body: dict[str, object] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": self.temperature,
            "max_tokens": int(policy["max_output_tokens"]),
        }
        if str(self.provider_name).strip().lower() == "openrouter":
            provider_preferences: dict[str, object] = {
                "allow_fallbacks": bool(policy["allow_fallbacks"]),
                "require_parameters": bool(policy["require_parameters"]),
                "data_collection": str(policy["data_collection"]),
                "max_price": {
                    "prompt": float(policy["max_price_prompt"]),
                    "completion": float(policy["max_price_completion"]),
                },
            }
            if policy["provider_order"]:
                provider_preferences["order"] = list(policy["provider_order"])
            if policy["zdr"]:
                provider_preferences["zdr"] = True
            body["provider"] = provider_preferences
        reasoning_config = self._reasoning_config()
        if reasoning_config:
            body["reasoning"] = reasoning_config
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        headers.update(self.extra_headers)

        req = request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        retry_after_seconds: float | None = None
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                response_headers = getattr(response, "headers", {})
                retry_after_seconds = _retry_after_seconds(
                    response_headers.get("Retry-After")
                    if hasattr(response_headers, "get")
                    else None
                )
                payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            _LOGGER.warning("Boundary HTTP error %s: %s", exc.code, exc.reason)
            error_payload: Mapping[str, object] = {}
            try:
                decoded = json.loads(exc.read().decode("utf-8"))
                if isinstance(decoded, Mapping):
                    error_payload = decoded
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                error_payload = {}
            metadata = _build_call_metadata(
                provider_name=self.provider_name,
                model=self.model,
                payload=error_payload,
                reasoning_config=reasoning_config,
                status=f"http_error_{exc.code}",
                temperature=self.temperature,
                retry_after_seconds=_retry_after_seconds(
                    exc.headers.get("Retry-After") if exc.headers else None
                ),
            )
            return {}, self._finalize_metadata(
                metadata,
                policy=policy,
                maximum_call_cost_usd=maximum_call_cost,
                reservation_id=reservation_id,
            )
        except error.URLError as exc:
            _LOGGER.warning("Boundary URL error: %s", exc.reason)
            return {}, self._finalize_metadata(
                BoundaryCallMetadata(
                provider_name=self.provider_name,
                requested_model=self.model,
                model=self.model,
                model_attribution_status="not_observed",
                status="url_error",
                reasoning_disabled=_reasoning_disabled(reasoning_config),
                provider_attempted=True,
                ),
                policy=policy,
                maximum_call_cost_usd=maximum_call_cost,
                reservation_id=reservation_id,
            )
        except TimeoutError:
            _LOGGER.warning("Boundary timeout after %.1fs", self.timeout)
            return {}, self._finalize_metadata(
                BoundaryCallMetadata(
                provider_name=self.provider_name,
                requested_model=self.model,
                model=self.model,
                model_attribution_status="not_observed",
                status="timeout",
                reasoning_disabled=_reasoning_disabled(reasoning_config),
                provider_attempted=True,
                ),
                policy=policy,
                maximum_call_cost_usd=maximum_call_cost,
                reservation_id=reservation_id,
            )
        except json.JSONDecodeError as exc:
            _LOGGER.warning("Boundary JSON error: %s", exc.msg)
            return {}, self._finalize_metadata(
                BoundaryCallMetadata(
                provider_name=self.provider_name,
                requested_model=self.model,
                model=self.model,
                model_attribution_status="not_observed",
                status="response_json_error",
                reasoning_disabled=_reasoning_disabled(reasoning_config),
                provider_attempted=True,
                ),
                policy=policy,
                maximum_call_cost_usd=maximum_call_cost,
                reservation_id=reservation_id,
            )
        except Exception as exc:
            _LOGGER.warning("Boundary unexpected error: %s", exc)
            return {}, self._finalize_metadata(
                BoundaryCallMetadata(
                    provider_name=self.provider_name,
                    requested_model=self.model,
                    model=self.model,
                    model_attribution_status="not_observed",
                    status="unexpected_error",
                    reasoning_disabled=_reasoning_disabled(reasoning_config),
                    provider_attempted=True,
                ),
                policy=policy,
                maximum_call_cost_usd=maximum_call_cost,
                reservation_id=reservation_id,
            )

        choices = payload.get("choices", [])
        if not isinstance(choices, list) or not choices:
            metadata = _build_call_metadata(
                provider_name=self.provider_name,
                model=self.model,
                payload=payload,
                reasoning_config=reasoning_config,
                status="missing_choices",
                temperature=self.temperature,
                retry_after_seconds=retry_after_seconds,
            )
            return {}, self._finalize_metadata(
                metadata,
                policy=policy,
                maximum_call_cost_usd=maximum_call_cost,
                reservation_id=reservation_id,
            )

        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, list):
            parts = [
                str(part.get("text", ""))
                for part in content
                if isinstance(part, dict)
            ]
            content = "\n".join(part for part in parts if part.strip())
        raw_message_content = str(content)
        metadata = _build_call_metadata(
            provider_name=self.provider_name,
            model=self.model,
            payload=payload,
            reasoning_config=reasoning_config,
            status="ok",
            temperature=self.temperature,
            raw_message_content=raw_message_content,
            retry_after_seconds=retry_after_seconds,
        )
        metadata = self._finalize_metadata(
            metadata,
            policy=policy,
            maximum_call_cost_usd=maximum_call_cost,
            reservation_id=reservation_id,
        )
        return _extract_json_payload(raw_message_content), metadata

    def _metadata_with_policy(
        self,
        metadata: BoundaryCallMetadata,
        *,
        policy: Mapping[str, object],
        maximum_call_cost_usd: float,
        reservation_id: str = "",
    ) -> BoundaryCallMetadata:
        return replace(
            metadata,
            request_max_output_tokens=int(policy["max_output_tokens"]),
            request_max_price_prompt=float(policy["max_price_prompt"]),
            request_max_price_completion=float(policy["max_price_completion"]),
            request_provider_order=tuple(policy["provider_order"]),
            request_allow_fallbacks=bool(policy["allow_fallbacks"]),
            request_require_parameters=bool(policy["require_parameters"]),
            request_data_collection=str(policy["data_collection"]),
            request_zdr=bool(policy["zdr"]),
            run_max_provider_calls=int(policy["maximum_provider_calls"]),
            run_max_cost_usd=float(policy["maximum_run_cost_usd"]),
            maximum_call_cost_usd=maximum_call_cost_usd,
            budget_reservation_id=reservation_id,
            pricing_table_version=str(policy["pricing_table_version"]),
            pricing_table_stale=bool(policy["pricing_table_stale"]),
        )

    def _finalize_metadata(
        self,
        metadata: BoundaryCallMetadata,
        *,
        policy: Mapping[str, object],
        maximum_call_cost_usd: float,
        reservation_id: str,
    ) -> BoundaryCallMetadata:
        decorated = self._metadata_with_policy(
            metadata,
            policy=policy,
            maximum_call_cost_usd=maximum_call_cost_usd,
            reservation_id=reservation_id,
        )
        price = lookup_chat_price(
            decorated.provider_name,
            decorated.model or decorated.requested_model,
        )
        estimated_cost = None
        if price is not None and (decorated.prompt_tokens or decorated.completion_tokens):
            estimated_cost = estimate_chat_cost_usd(
                price=price,
                prompt_tokens=decorated.prompt_tokens,
                completion_tokens=decorated.completion_tokens,
                cached_tokens=decorated.cached_tokens,
            )
        finalize_provider_call(
            run_id=self._budget_run_id,
            reservation_id=reservation_id,
            status=decorated.status,
            response_id=decorated.response_id,
            exact_cost_usd=decorated.exact_cost_usd,
            estimated_cost_usd=estimated_cost,
            maximum_calls=int(policy["maximum_provider_calls"]),
            maximum_run_cost_usd=float(policy["maximum_run_cost_usd"]),
        )
        return decorated

    def _reasoning_config(self) -> dict[str, object]:
        if (
            _is_truthy_env("LOLLA_OPENROUTER_DISABLE_REASONING")
            and str(self.provider_name).strip().lower() == "openrouter"
        ):
            return {"enabled": False}
        if _openrouter_disables_reasoning_by_default(self.provider_name, self.model):
            # ``enabled: false`` is the provider-level off switch.  It remains
            # valid for models whose current effort vocabulary omits ``none``
            # (for example Gemini 3.1 Flash Lite), while ``effort: none`` can
            # be rejected before inference by those same models.
            return {"enabled": False}
        return {}

    @classmethod
    def openai_from_env(cls) -> "OpenAICompatibleBoundaryClient":
        return cls(
            provider_name="openai",
            api_key=os.getenv("LOLLA_OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", "")),
            base_url=os.getenv("LOLLA_OPENAI_BASE_URL", "https://api.openai.com/v1"),
            model=os.getenv("LOLLA_OPENAI_MODEL", "gpt-4o"),
        )

    @classmethod
    def openrouter_from_env(cls) -> "OpenAICompatibleBoundaryClient":
        referer = os.getenv("LOLLA_OPENROUTER_HTTP_REFERER", os.getenv("LOLLA_OPENROUTER_SITE_URL", ""))
        title = os.getenv("LOLLA_OPENROUTER_X_TITLE", os.getenv("LOLLA_OPENROUTER_APP_NAME", ""))
        headers: dict[str, str] = {}
        if referer:
            headers["HTTP-Referer"] = referer
        if title:
            headers["X-Title"] = title

        model = os.getenv("LOLLA_OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)

        # Cache stickiness for xAI Grok models: x-grok-conv-id pins all
        # requests in a single Lolla run to the same xAI backend server,
        # which maximizes the chance that a cache built by call N is still
        # there for call N+1. xAI documents this header at
        # docs.x.ai/developers/advanced-api-usage/prompt-caching/how-it-works
        # and recommends a uuid4 — we derive a deterministic uuid5 from
        # $LOLLA_RUN_ID so every BoundaryClient instance spawned during the
        # same run (pipeline + BI + revision + extraction) emits the same
        # conv_id and lands on the same backend. Falls back to a fresh
        # uuid4 per process when LOLLA_RUN_ID is unset (e.g., ad-hoc
        # scripts and tests).
        if model.startswith("x-ai/grok"):
            run_id = os.getenv("LOLLA_RUN_ID", "")
            if run_id:
                conv_id = str(uuid.uuid5(_LOLLA_CONV_ID_NAMESPACE, run_id))
            else:
                conv_id = str(uuid.uuid4())
            headers["x-grok-conv-id"] = conv_id

        return cls(
            provider_name="openrouter",
            api_key=os.getenv("LOLLA_OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", "")),
            base_url=os.getenv("LOLLA_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            model=model,
            extra_headers=headers,
        )


class GeminiCliBoundaryClient:
    """Thin subprocess wrapper around the local Gemini CLI.

    Follows the same ``run_json(system_prompt, user_prompt)`` contract as
    ``OpenAICompatibleBoundaryClient`` so the pipeline can swap providers
    without any other changes.
    """

    def __init__(self, *, model: str = "", timeout: float = 90.0) -> None:
        self.provider_name = "gemini_cli"
        self.model = str(model or os.getenv("LOLLA_GEMINI_MODEL", "")).strip()
        self.timeout = max(10.0, min(float(timeout), 300.0))
        self.last_call_metadata = BoundaryCallMetadata(
            provider_name=self.provider_name,
            model=self.model,
        )
        self.call_log: list[BoundaryCallRecord] = []
        self._call_log_lock = threading.Lock()

    def run_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        stage: str = "unlabeled",
        tendency_id: str = "",
    ) -> dict[str, object]:
        result, metadata = self.run_json_with_metadata(
            system_prompt, user_prompt, stage=stage, tendency_id=tendency_id
        )
        self.last_call_metadata = metadata
        return result

    def run_json_with_metadata(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        stage: str = "unlabeled",
        tendency_id: str = "",
    ) -> tuple[dict[str, object], BoundaryCallMetadata]:
        """Thread-safe variant: returns (result, metadata) without side effects.

        Every call (success or failure) is auto-appended to ``self.call_log``
        with the supplied stage label.
        """
        result, metadata = self._do_call(system_prompt, user_prompt)
        with self._call_log_lock:
            self.call_log.append(
                _record_from_metadata(metadata, stage=stage, tendency_id=tendency_id)
            )
        return result, metadata

    def _do_call(
        self, system_prompt: str, user_prompt: str
    ) -> tuple[dict[str, object], BoundaryCallMetadata]:
        combined = "\n\n".join(
            part.strip()
            for part in (str(system_prompt or ""), str(user_prompt or ""))
            if str(part or "").strip()
        )
        if not combined:
            return {}, BoundaryCallMetadata(
                provider_name=self.provider_name,
                requested_model=self.model,
                model=self.model,
                served_model=self.model,
                model_attribution_status="matched",
                status="empty_prompt",
            )

        cmd = ["gemini"]
        if self.model:
            cmd.extend(["-m", self.model])
        cmd.extend(["-p", combined, "--output-format", "text", "--yolo"])

        started = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                timeout=self.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            _LOGGER.warning("Gemini CLI timeout after %.1fs", self.timeout)
            return {}, BoundaryCallMetadata(
                provider_name=self.provider_name,
                requested_model=self.model,
                model=self.model,
                served_model=self.model,
                model_attribution_status="matched",
                status="timeout",
            )
        except FileNotFoundError:
            _LOGGER.warning("Gemini CLI not found — is `gemini` on PATH?")
            return {}, BoundaryCallMetadata(
                provider_name=self.provider_name,
                requested_model=self.model,
                model=self.model,
                served_model=self.model,
                model_attribution_status="matched",
                status="cli_not_found",
            )

        duration = round(time.monotonic() - started, 3)
        if proc.returncode != 0:
            _LOGGER.warning(
                "Gemini CLI exited %s after %.1fs: %s",
                proc.returncode,
                duration,
                (proc.stderr or "")[:200],
            )
            return {}, BoundaryCallMetadata(
                provider_name=self.provider_name,
                requested_model=self.model,
                model=self.model,
                served_model=self.model,
                model_attribution_status="matched",
                status=f"cli_exit_{proc.returncode}",
            )

        return _extract_json_payload(proc.stdout or ""), BoundaryCallMetadata(
            provider_name=self.provider_name,
            requested_model=self.model,
            model=self.model,
            served_model=self.model,
            model_attribution_status="matched",
            status="ok",
        )

    @classmethod
    def from_env(cls) -> "GeminiCliBoundaryClient":
        raw_timeout = os.getenv("LOLLA_GEMINI_TIMEOUT", "90")
        try:
            timeout = float(raw_timeout)
        except ValueError:
            timeout = 90.0
        return cls(
            model=os.getenv("LOLLA_GEMINI_MODEL", ""),
            timeout=timeout,
        )


def load_boundary_client_from_env(provider_name: str = "openrouter") -> OpenAICompatibleBoundaryClient | GeminiCliBoundaryClient:
    normalized = str(provider_name).strip().lower()
    if normalized == "openai":
        return OpenAICompatibleBoundaryClient.openai_from_env()
    if normalized == "gemini_cli":
        return GeminiCliBoundaryClient.from_env()
    return OpenAICompatibleBoundaryClient.openrouter_from_env()


def _openrouter_disables_reasoning_by_default(provider_name: str, model: str) -> bool:
    normalized_provider = str(provider_name or "").strip().lower()
    normalized_model = str(model or "").strip().lower()
    if normalized_provider != "openrouter":
        return False
    return normalized_model.startswith(
        (
            DEFAULT_OPENROUTER_MODEL,
            "deepseek/deepseek-v4-pro",
            "qwen/qwen3.5-flash-02-23",
            "google/gemini-3.1-flash-lite",
            "moonshotai/kimi-k2.6",
            "x-ai/grok-4.1-fast",
            "x-ai/grok-4.3",
        )
    )


def _is_truthy_env(name: str) -> bool:
    return str(os.getenv(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def _reasoning_disabled(reasoning_config: Mapping[str, object] | None) -> bool:
    if not reasoning_config:
        return False
    if reasoning_config.get("enabled") is False:
        return True
    return str(reasoning_config.get("effort", "")).strip().lower() == "none"


def _model_attribution_status(*, requested_model: str, served_model: str, status: str) -> str:
    normalized_status = str(status or "")
    served_was_observed_during_provider_failure = (
        normalized_status == "provider_finish_error" and bool(str(served_model or "").strip())
    )
    if not normalized_status.startswith("ok") and not served_was_observed_during_provider_failure:
        return "not_observed"
    requested = str(requested_model or "").strip()
    served = str(served_model or "").strip()
    if not requested and not served:
        return "not_observed"
    if not requested:
        return "requested_model_missing"
    if not served:
        return "served_model_missing"
    if requested == served:
        return "matched"
    if served.startswith(f"{requested}-") or requested.startswith(f"{served}-"):
        return "served_version_alias"
    return "mismatch"


def _usage_int(section: Mapping[str, object], key: str) -> int:
    try:
        return int(section.get(key, 0))
    except (TypeError, ValueError):
        return 0


def _usage_float_or_none(section: Mapping[str, object], key: str) -> float | None:
    raw = section.get(key)
    if raw is None:
        return None
    try:
        return max(0.0, float(raw))
    except (TypeError, ValueError):
        return None


def _build_call_metadata(
    *,
    provider_name: str,
    model: str,
    payload: Mapping[str, object],
    reasoning_config: Mapping[str, object] | None,
    status: str,
    temperature: float = 0.0,
    raw_message_content: str = "",
    retry_after_seconds: float | None = None,
) -> BoundaryCallMetadata:
    usage = payload.get("usage", {})
    usage_map = usage if isinstance(usage, Mapping) else {}
    prompt_details = usage_map.get("prompt_tokens_details", {})
    prompt_details_map = prompt_details if isinstance(prompt_details, Mapping) else {}
    completion_details = usage_map.get("completion_tokens_details", {})
    if not isinstance(completion_details, Mapping):
        completion_details = usage_map.get("output_tokens_details", {})
    completion_details_map = completion_details if isinstance(completion_details, Mapping) else {}
    choices = payload.get("choices", [])
    first_choice = choices[0] if isinstance(choices, list) and choices else {}
    first_choice_map = first_choice if isinstance(first_choice, Mapping) else {}
    message = first_choice_map.get("message", {})
    message_map = message if isinstance(message, Mapping) else {}
    reasoning_details_present = _reasoning_details_include_content(message_map)
    finish_reason_raw = first_choice_map.get("finish_reason", "")
    finish_reason = str(finish_reason_raw) if finish_reason_raw is not None else ""
    effective_status = str(status or "")
    if effective_status.startswith("ok") and finish_reason.strip().lower() == "error":
        effective_status = "provider_finish_error"
    provider_error = _provider_error_diagnostics(payload)
    requested_model = str(model or "").strip()
    served_model = str(payload.get("model", "") or "").strip()
    model_for_billing = served_model or requested_model
    return BoundaryCallMetadata(
        provider_name=provider_name,
        served_provider_name=str(payload.get("provider", "") or "").strip(),
        requested_model=requested_model,
        served_model=served_model,
        model=model_for_billing,
        model_attribution_status=_model_attribution_status(
            requested_model=requested_model,
            served_model=served_model,
            status=effective_status,
        ),
        status=effective_status,
        finish_reason=finish_reason,
        provider_error_source=provider_error["source"],
        provider_error_type=provider_error["error_type"],
        provider_error_code=provider_error["code"],
        provider_error_provider_code=provider_error["provider_code"],
        provider_error_message_sha256=provider_error["message_sha256"],
        retry_after_seconds=retry_after_seconds,
        raw_message_content=raw_message_content,
        temperature=temperature,
        prompt_tokens=_usage_int(usage_map, "prompt_tokens"),
        completion_tokens=_usage_int(usage_map, "completion_tokens"),
        total_tokens=_usage_int(usage_map, "total_tokens"),
        cached_tokens=_usage_int(prompt_details_map, "cached_tokens"),
        cache_write_tokens=_usage_int(prompt_details_map, "cache_write_tokens"),
        reasoning_tokens=_usage_int(completion_details_map, "reasoning_tokens"),
        reasoning_disabled=_reasoning_disabled(reasoning_config),
        reasoning_details_present=reasoning_details_present,
        provider_attempted=True,
        response_id=str(payload.get("id", "") or ""),
        exact_cost_usd=_usage_float_or_none(usage_map, "cost"),
    )


def _provider_error_diagnostics(payload: Mapping[str, object]) -> dict[str, str]:
    """Return privacy-safe provider error fields from OpenAI-style envelopes.

    OpenRouter may return a top-level ``error`` object or place an ``error``
    beside a partially generated choice. The raw message can contain upstream
    details, so custody keeps only stable type/code fields and a SHA-256 digest.
    """

    source = ""
    error_value: object = None
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, Mapping) and isinstance(first.get("error"), Mapping):
            source = "choice"
            error_value = first.get("error")
    if error_value is None and isinstance(payload.get("error"), Mapping):
        source = "top_level"
        error_value = payload.get("error")
    if not isinstance(error_value, Mapping):
        return {
            "source": "",
            "error_type": "",
            "code": "",
            "provider_code": "",
            "message_sha256": "",
        }

    metadata_value = error_value.get("metadata")
    metadata = metadata_value if isinstance(metadata_value, Mapping) else {}
    message = str(error_value.get("message", "") or "")
    return {
        "source": source,
        "error_type": str(
            metadata.get("error_type")
            or error_value.get("type")
            or ""
        ),
        "code": str(error_value.get("code", "") or ""),
        "provider_code": str(metadata.get("provider_code", "") or ""),
        "message_sha256": (
            hashlib.sha256(message.encode("utf-8")).hexdigest() if message else ""
        ),
    }


def _retry_after_seconds(raw_value: object) -> float | None:
    try:
        value = float(str(raw_value or "").strip())
    except ValueError:
        return None
    return max(0.0, value)


def _reasoning_details_include_content(message: Mapping[str, object]) -> bool:
    """Return true only when provider reasoning details include content.

    Some providers, notably Gemini through OpenRouter, may return a
    ``reasoning_details`` block that only carries signature/format metadata
    even when reasoning tokens are zero. Treating that structural container as
    leaked reasoning makes otherwise clean runs look degraded. Content-bearing
    reasoning fields still remain a boundary warning.
    """

    reasoning = message.get("reasoning")
    if bool(reasoning):
        return True

    details = message.get("reasoning_details")
    if isinstance(details, Mapping):
        return _reasoning_detail_item_includes_content(details)
    if isinstance(details, list):
        return any(
            _reasoning_detail_item_includes_content(item)
            for item in details
            if isinstance(item, Mapping)
        )
    return bool(details)


def _reasoning_detail_item_includes_content(item: Mapping[str, object]) -> bool:
    for key in ("text", "summary", "data", "content", "reasoning"):
        if bool(item.get(key)):
            return True
    return False
