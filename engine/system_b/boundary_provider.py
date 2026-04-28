from __future__ import annotations

import json
import logging
import os
import subprocess
import threading
import time
from dataclasses import asdict, dataclass
from typing import Mapping
from urllib import error, request


_LOGGER = logging.getLogger("system_b.boundary_provider")


@dataclass(frozen=True)
class BoundaryCallMetadata:
    provider_name: str = ""
    model: str = ""
    status: str = "not_called"
    finish_reason: str = ""
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
    model: str = ""
    status: str = "not_called"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    cache_write_tokens: int = 0
    reasoning_tokens: int = 0
    reasoning_disabled: bool = False
    reasoning_details_present: bool = False

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
        model=metadata.model,
        status=metadata.status,
        prompt_tokens=metadata.prompt_tokens,
        completion_tokens=metadata.completion_tokens,
        total_tokens=metadata.total_tokens,
        cached_tokens=metadata.cached_tokens,
        cache_write_tokens=metadata.cache_write_tokens,
        reasoning_tokens=metadata.reasoning_tokens,
        reasoning_disabled=metadata.reasoning_disabled,
        reasoning_details_present=metadata.reasoning_details_present,
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
        result, metadata = self._do_call(system_prompt, user_prompt)
        with self._call_log_lock:
            self.call_log.append(
                _record_from_metadata(metadata, stage=stage, tendency_id=tendency_id)
            )
        return result, metadata

    def _do_call(
        self, system_prompt: str, user_prompt: str
    ) -> tuple[dict[str, object], BoundaryCallMetadata]:
        if not self.api_key:
            return {}, BoundaryCallMetadata(
                provider_name=self.provider_name,
                model=self.model,
                status="missing_api_key",
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
        }
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
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            _LOGGER.warning("Boundary HTTP error %s: %s", exc.code, exc.reason)
            return {}, BoundaryCallMetadata(
                provider_name=self.provider_name,
                model=self.model,
                status=f"http_error_{exc.code}",
                reasoning_disabled=_reasoning_disabled(reasoning_config),
            )
        except error.URLError as exc:
            _LOGGER.warning("Boundary URL error: %s", exc.reason)
            return {}, BoundaryCallMetadata(
                provider_name=self.provider_name,
                model=self.model,
                status="url_error",
                reasoning_disabled=_reasoning_disabled(reasoning_config),
            )
        except TimeoutError:
            _LOGGER.warning("Boundary timeout after %.1fs", self.timeout)
            return {}, BoundaryCallMetadata(
                provider_name=self.provider_name,
                model=self.model,
                status="timeout",
                reasoning_disabled=_reasoning_disabled(reasoning_config),
            )
        except json.JSONDecodeError as exc:
            _LOGGER.warning("Boundary JSON error: %s", exc.msg)
            return {}, BoundaryCallMetadata(
                provider_name=self.provider_name,
                model=self.model,
                status="response_json_error",
                reasoning_disabled=_reasoning_disabled(reasoning_config),
            )

        choices = payload.get("choices", [])
        if not isinstance(choices, list) or not choices:
            return {}, _build_call_metadata(
                provider_name=self.provider_name,
                model=self.model,
                payload=payload,
                reasoning_config=reasoning_config,
                status="missing_choices",
                temperature=self.temperature,
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
        )
        return _extract_json_payload(raw_message_content), metadata

    def _reasoning_config(self) -> dict[str, object]:
        if _is_openrouter_grok_fast(self.provider_name, self.model):
            return {"effort": "none"}
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
        return cls(
            provider_name="openrouter",
            api_key=os.getenv("LOLLA_OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", "")),
            base_url=os.getenv("LOLLA_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            model=os.getenv("LOLLA_OPENROUTER_MODEL", "x-ai/grok-4.1-fast"),
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
                model=self.model,
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
                model=self.model,
                status="timeout",
            )
        except FileNotFoundError:
            _LOGGER.warning("Gemini CLI not found — is `gemini` on PATH?")
            return {}, BoundaryCallMetadata(
                provider_name=self.provider_name,
                model=self.model,
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
                model=self.model,
                status=f"cli_exit_{proc.returncode}",
            )

        return _extract_json_payload(proc.stdout or ""), BoundaryCallMetadata(
            provider_name=self.provider_name,
            model=self.model,
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


def _is_openrouter_grok_fast(provider_name: str, model: str) -> bool:
    normalized_provider = str(provider_name or "").strip().lower()
    normalized_model = str(model or "").strip().lower()
    return normalized_provider == "openrouter" and normalized_model.startswith("x-ai/grok-4.1-fast")


def _reasoning_disabled(reasoning_config: Mapping[str, object] | None) -> bool:
    if not reasoning_config:
        return False
    return str(reasoning_config.get("effort", "")).strip().lower() == "none"


def _usage_int(section: Mapping[str, object], key: str) -> int:
    try:
        return int(section.get(key, 0))
    except (TypeError, ValueError):
        return 0


def _build_call_metadata(
    *,
    provider_name: str,
    model: str,
    payload: Mapping[str, object],
    reasoning_config: Mapping[str, object] | None,
    status: str,
    temperature: float = 0.0,
    raw_message_content: str = "",
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
    reasoning_details_present = bool(message_map.get("reasoning")) or bool(message_map.get("reasoning_details"))
    finish_reason_raw = first_choice_map.get("finish_reason", "")
    finish_reason = str(finish_reason_raw) if finish_reason_raw is not None else ""
    return BoundaryCallMetadata(
        provider_name=provider_name,
        model=model,
        status=status,
        finish_reason=finish_reason,
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
    )
