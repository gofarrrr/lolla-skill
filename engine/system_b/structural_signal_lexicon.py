from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class SignalProfile:
    tendency_id: str
    subpattern_id: str
    signal_tags: tuple[str, ...] = ()
    cue_phrases: tuple[str, ...] = ()


class StructuralSignalLexicon:
    def __init__(
        self,
        *,
        operators: tuple[str, ...],
        stopwords: tuple[str, ...],
        profiles: dict[tuple[str, str], SignalProfile],
    ) -> None:
        self._operators = operators
        self._stopwords = stopwords
        self._profiles = profiles

    @classmethod
    def load(cls, root: Path) -> "StructuralSignalLexicon":
        root = Path(root)
        path = root / "build" / "curated" / "structural_signal_lexicon.json"
        if not path.exists():
            return cls(operators=(), stopwords=(), profiles={})
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return cls(operators=(), stopwords=(), profiles={})
        tendency_payloads = payload.get("tendencies", {})
        profiles: dict[tuple[str, str], SignalProfile] = {}
        if isinstance(tendency_payloads, dict):
            for tendency_id, tendency_payload in tendency_payloads.items():
                if not isinstance(tendency_payload, dict):
                    continue
                subpattern_payloads = tendency_payload.get("subpatterns", {})
                if not isinstance(subpattern_payloads, dict):
                    continue
                for subpattern_id, profile_payload in subpattern_payloads.items():
                    if not isinstance(profile_payload, dict):
                        continue
                    key = (_normalize(tendency_id), _normalize(subpattern_id))
                    profiles[key] = SignalProfile(
                        tendency_id=str(tendency_id),
                        subpattern_id=str(subpattern_id),
                        signal_tags=_parse_string_tuple(profile_payload.get("signal_tags")),
                        cue_phrases=_parse_string_tuple(profile_payload.get("cue_phrases")),
                    )
        return cls(
            operators=_parse_string_tuple(payload.get("operators")),
            stopwords=_parse_string_tuple(payload.get("stopwords")),
            profiles=profiles,
        )

    @property
    def operators(self) -> tuple[str, ...]:
        return self._operators

    @property
    def stopwords(self) -> tuple[str, ...]:
        return self._stopwords

    def profile_for(self, tendency_id: str, subpattern_id: str) -> SignalProfile | None:
        tendency_key = _normalize(tendency_id)
        subpattern_key = _normalize(subpattern_id)
        profile = self._profiles.get((tendency_key, subpattern_key))
        if profile is not None:
            return profile
        return self._profiles.get((tendency_key, "general"))


def _parse_string_tuple(payload: object) -> tuple[str, ...]:
    if not isinstance(payload, list):
        return ()
    values: list[str] = []
    for item in payload:
        value = str(item).strip()
        if value:
            values.append(value)
    return tuple(values)


def _normalize(value: object) -> str:
    return str(value or "").strip().replace("_", "-").lower()
