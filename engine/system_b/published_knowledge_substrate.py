"""Strict, read-only access to Lolla's published knowledge substrate.

This module owns publication loading, exact canonical identity, authored edge
direction, immutable indexes, release identity, and available source custody.
It does not compile, repair, normalize aliases, rank candidates, allocate a
pressure portfolio, rebuild embeddings, or call a provider.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any


LOAD_STATES = frozenset({"complete", "completed_zero", "partial", "failed", "missing"})


class PublishedSubstrateError(RuntimeError):
    """Raised when a caller requires a substrate state that is unavailable."""


@dataclass(frozen=True)
class ModelSourceCustody:
    path: str
    sha256: str
    bytes: int


@dataclass(frozen=True)
class PublishedModel:
    model_id: str
    source_order: int
    compiled_pointer: str
    payload: Mapping[str, Any]
    source_custody: ModelSourceCustody | None = None


@dataclass(frozen=True)
class RelationCustody:
    authoring_path: str
    authoring_family: str
    authoring_item_index: int
    compiled_pointer: str
    source_path: str
    source_sha256: str
    source_bytes: int
    source_anchor_state: str
    exact_span: Mapping[str, int] | None


@dataclass(frozen=True)
class PublishedRelation:
    relation_id: str
    source_model_id: str
    target_model_id: str
    edge_type: str
    source_order: int
    compiled_pointer: str
    payload: Mapping[str, Any]
    custody: RelationCustody | None = None


@dataclass(frozen=True)
class PublishedKnowledgeSnapshot:
    root: Path
    data_directory: Path
    release_id: str
    release_identity: Mapping[str, Any]
    coverage: Mapping[str, str]
    models: Mapping[str, PublishedModel]
    tendencies: Mapping[str, Mapping[str, Any]]
    relations: tuple[PublishedRelation, ...]
    _relations_by_id: Mapping[str, PublishedRelation]
    _outgoing: Mapping[str, tuple[PublishedRelation, ...]]
    _incoming: Mapping[str, tuple[PublishedRelation, ...]]
    _knowledge_payload: Mapping[str, Any]
    _relationship_payload: tuple[Any, ...]

    def model(self, model_id: str) -> PublishedModel:
        """Return an exact canonical model; never repair aliases or slugs."""

        return self.models[model_id]

    def relation(self, relation_id: str) -> PublishedRelation:
        return self._relations_by_id[relation_id]

    def outgoing(self, model_id: str) -> tuple[PublishedRelation, ...]:
        self.model(model_id)
        return self._outgoing.get(model_id, ())

    def incoming_references(self, model_id: str) -> tuple[PublishedRelation, ...]:
        """Return relations authored by other sources that point at model_id."""

        self.model(model_id)
        return self._incoming.get(model_id, ())

    def incident(self, model_id: str) -> tuple[PublishedRelation, ...]:
        """Return outgoing then incoming references without reversing either."""

        outgoing = self.outgoing(model_id)
        outgoing_ids = {relation.relation_id for relation in outgoing}
        return outgoing + tuple(
            relation
            for relation in self.incoming_references(model_id)
            if relation.relation_id not in outgoing_ids
        )

    def knowledge_graph_payload(self) -> dict[str, Any]:
        """Return an exact mutable copy for a time-bounded legacy adapter."""

        value = _thaw(self._knowledge_payload)
        if not isinstance(value, dict):
            raise PublishedSubstrateError("Published knowledge payload is not an object")
        return value

    def relationship_graph_payload(self) -> list[Any]:
        """Return an exact mutable copy for a time-bounded legacy adapter."""

        value = _thaw(self._relationship_payload)
        if not isinstance(value, list):
            raise PublishedSubstrateError("Published relationship payload is not an array")
        return value


@dataclass(frozen=True)
class PublishedSubstrateLoadResult:
    status: str
    coverage: Mapping[str, str]
    snapshot: PublishedKnowledgeSnapshot | None = None
    issues: tuple[str, ...] = ()
    provider_calls: int = 0
    runtime_generation_attempted: bool = False

    def __post_init__(self) -> None:
        if self.status not in LOAD_STATES:
            raise ValueError(f"Unknown published-substrate state: {self.status}")

    def require_snapshot(self, *, allow_partial: bool = False) -> PublishedKnowledgeSnapshot:
        allowed = {"complete", "completed_zero"}
        if allow_partial:
            allowed.add("partial")
        if self.status not in allowed or self.snapshot is None:
            detail = "; ".join(self.issues) or "no snapshot available"
            raise PublishedSubstrateError(
                f"Published knowledge substrate is {self.status}: {detail}"
            )
        return self.snapshot


class PublishedKnowledgeSubstrate:
    """Loader for one immutable publication snapshot."""

    @classmethod
    def open(cls, root: Path) -> PublishedSubstrateLoadResult:
        root = Path(root).resolve()
        data_directory = _resolve_data_directory(root)
        if data_directory is None:
            return _load_result(
                "missing",
                {"knowledge_graph": "missing", "relationship_graph": "missing"},
                issues=("neither root/build nor root/data exists",),
            )

        knowledge_path = data_directory / "knowledge_graph.json"
        relationship_path = data_directory / "relationship_graph.json"
        missing = [path.name for path in (knowledge_path, relationship_path) if not path.is_file()]
        if missing:
            return _load_result(
                "missing",
                {
                    "knowledge_graph": "complete" if knowledge_path.is_file() else "missing",
                    "relationship_graph": (
                        "complete" if relationship_path.is_file() else "missing"
                    ),
                },
                issues=("missing published artifact(s): " + ", ".join(missing),),
            )

        try:
            knowledge_payload = _load_json(knowledge_path)
            relationship_payload = _load_json(relationship_path)
        except (OSError, json.JSONDecodeError) as exc:
            return _load_result(
                "failed",
                {"knowledge_graph": "failed", "relationship_graph": "failed"},
                issues=(f"published artifact parse failed: {type(exc).__name__}",),
            )
        if not isinstance(knowledge_payload, dict) or not isinstance(relationship_payload, list):
            return _load_result(
                "failed",
                {"knowledge_graph": "failed", "relationship_graph": "failed"},
                issues=("published artifacts have invalid top-level shapes",),
            )

        raw_models = knowledge_payload.get("models")
        raw_tendencies = knowledge_payload.get("tendencies", {})
        if not isinstance(raw_models, dict) or not isinstance(raw_tendencies, dict):
            return _load_result(
                "failed",
                {"model_registry": "failed", "tendency_registry": "failed"},
                issues=("knowledge graph registries have invalid shapes",),
            )

        if not raw_models and not relationship_payload:
            snapshot = _empty_snapshot(root, data_directory, knowledge_payload)
            return _load_result(
                "completed_zero",
                snapshot.coverage,
                snapshot=snapshot,
            )

        coverage: dict[str, str] = {
            "knowledge_graph": "complete",
            "relationship_graph": "complete",
            "model_registry": "complete" if raw_models else "completed_zero",
            "tendency_registry": "complete" if raw_tendencies else "completed_zero",
            "relation_registry": "complete" if relationship_payload else "completed_zero",
        }
        issues: list[str] = []

        release_manifest = _optional_json(data_directory / "curation" / "published_substrate_release.json")
        release_id = "unregistered"
        release_identity: dict[str, Any] = {
            "knowledge_graph": _file_identity(knowledge_path, "data/knowledge_graph.json"),
            "relationship_graph": _file_identity(
                relationship_path, "data/relationship_graph.json"
            ),
        }
        if isinstance(release_manifest, dict):
            release_id = str(release_manifest.get("release_id", "")).strip() or "unregistered"
            release_identity["release_manifest"] = _file_identity(
                data_directory / "curation" / "published_substrate_release.json",
                "data/curation/published_substrate_release.json",
            )
            artifact_errors = _release_artifact_errors(
                release_manifest,
                data_directory,
            )
            if artifact_errors:
                return _load_result(
                    "failed",
                    {**coverage, "published_release_identity": "failed"},
                    issues=tuple(artifact_errors),
                )
            coverage["published_release_identity"] = "complete"
            custody_issues = _release_custody_issues(release_manifest, data_directory)
            if custody_issues:
                coverage["release_custody_inputs"] = "partial"
                issues.extend(custody_issues)
            else:
                coverage["release_custody_inputs"] = "complete"
        else:
            coverage["published_release_identity"] = "missing"
            coverage["release_custody_inputs"] = "missing"
            issues.append("published release manifest is missing or invalid")

        model_source_rows = _model_source_rows(data_directory)
        models: dict[str, PublishedModel] = {}
        for source_order, (model_id, raw_model) in enumerate(raw_models.items()):
            if not isinstance(raw_model, dict):
                return _load_result(
                    "failed",
                    {**coverage, "model_registry": "failed"},
                    issues=(f"model {model_id!r} is not an object",),
                )
            source_row = model_source_rows.get(str(model_id))
            source_custody = _model_source_custody(source_row)
            models[str(model_id)] = PublishedModel(
                model_id=str(model_id),
                source_order=source_order,
                compiled_pointer=f"data/knowledge_graph.json#/models/{model_id}",
                payload=_freeze(raw_model),
                source_custody=source_custody,
            )
        coverage["model_source_custody"] = (
            "complete"
            if len(model_source_rows) == len(models)
            and all(model.source_custody is not None for model in models.values())
            else "partial"
        )
        if coverage["model_source_custody"] == "partial":
            issues.append("model source custody does not exactly cover the model registry")

        anchor_rows = _relation_anchor_rows(data_directory)
        if anchor_rows is None:
            coverage["relation_source_custody"] = "missing"
            issues.append("relation source-anchor register is missing or invalid")
            anchor_rows = {}
        else:
            coverage["relation_source_custody"] = "complete"

        relations: list[PublishedRelation] = []
        relations_by_id: dict[str, PublishedRelation] = {}
        outgoing: dict[str, list[PublishedRelation]] = {}
        incoming: dict[str, list[PublishedRelation]] = {}
        canonical_ids = set(models)
        for source_order, raw_edge in enumerate(relationship_payload):
            if not isinstance(raw_edge, dict):
                return _load_result(
                    "failed",
                    {**coverage, "relation_registry": "failed"},
                    issues=(f"relationship row {source_order} is not an object",),
                )
            source = str(raw_edge.get("source_model_id", "")).strip()
            target = str(raw_edge.get("target_model_id", "")).strip()
            edge_type = str(raw_edge.get("edge_type", "")).strip()
            relation_id = "::".join((source, target, edge_type))
            if not source or not target or not edge_type:
                return _load_result(
                    "failed",
                    {**coverage, "relation_registry": "failed"},
                    issues=(f"relationship row {source_order} has an incomplete identity",),
                )
            if source not in canonical_ids or target not in canonical_ids:
                return _load_result(
                    "failed",
                    {**coverage, "relation_registry": "failed"},
                    issues=(f"relationship {relation_id} has a noncanonical endpoint",),
                )
            if relation_id in relations_by_id:
                return _load_result(
                    "failed",
                    {**coverage, "relation_registry": "failed"},
                    issues=(f"duplicate relationship identity {relation_id}",),
                )
            custody = _relation_custody(anchor_rows.get(relation_id), source_order)
            if anchor_rows and custody is None:
                coverage["relation_source_custody"] = "partial"
            relation = PublishedRelation(
                relation_id=relation_id,
                source_model_id=source,
                target_model_id=target,
                edge_type=edge_type,
                source_order=source_order,
                compiled_pointer=f"data/relationship_graph.json#/{source_order}",
                payload=_freeze(raw_edge),
                custody=custody,
            )
            relations.append(relation)
            relations_by_id[relation_id] = relation
            outgoing.setdefault(source, []).append(relation)
            incoming.setdefault(target, []).append(relation)

        if anchor_rows and (
            len(anchor_rows) != len(relations)
            or any(relation.custody is None for relation in relations)
        ):
            coverage["relation_source_custody"] = "partial"
            issues.append("relation source custody does not exactly cover published relations")

        status = "complete" if all(state in {"complete", "completed_zero"} for state in coverage.values()) else "partial"
        snapshot = PublishedKnowledgeSnapshot(
            root=root,
            data_directory=data_directory,
            release_id=release_id,
            release_identity=_freeze(release_identity),
            coverage=MappingProxyType(dict(coverage)),
            models=MappingProxyType(models),
            tendencies=MappingProxyType(
                {str(key): _freeze(value) for key, value in raw_tendencies.items() if isinstance(value, dict)}
            ),
            relations=tuple(relations),
            _relations_by_id=MappingProxyType(relations_by_id),
            _outgoing=MappingProxyType(
                {key: tuple(value) for key, value in outgoing.items()}
            ),
            _incoming=MappingProxyType(
                {key: tuple(value) for key, value in incoming.items()}
            ),
            _knowledge_payload=_freeze(knowledge_payload),
            _relationship_payload=_freeze(relationship_payload),
        )
        return _load_result(status, coverage, snapshot=snapshot, issues=tuple(issues))


def _resolve_data_directory(root: Path) -> Path | None:
    for candidate in (root / "build", root / "data"):
        if candidate.is_dir():
            return candidate
    return None


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _optional_json(path: Path) -> Any:
    try:
        return _load_json(path)
    except (OSError, json.JSONDecodeError):
        return None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_identity(path: Path, declared_path: str) -> dict[str, Any]:
    return {
        "path": declared_path,
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
    }


def _declared_path(data_directory: Path, value: object) -> Path:
    text = str(value or "")
    if text.startswith("data/"):
        return data_directory / text.removeprefix("data/")
    return data_directory.parent / text


def _release_artifact_errors(
    release_manifest: Mapping[str, Any],
    data_directory: Path,
) -> list[str]:
    errors: list[str] = []
    artifacts = release_manifest.get("artifacts")
    if not isinstance(artifacts, Mapping):
        return ["published release artifact registry is invalid"]
    for name in ("knowledge_graph", "relationship_graph"):
        row = artifacts.get(name)
        if not isinstance(row, Mapping):
            errors.append(f"published release artifact {name} is missing")
            continue
        path = _declared_path(data_directory, row.get("path"))
        if not path.is_file():
            errors.append(f"published release artifact {name} is unavailable")
            continue
        if _sha256(path) != str(row.get("sha256", "")) or path.stat().st_size != int(row.get("bytes", -1)):
            errors.append(f"published release artifact {name} identity drift")
    return errors


def _release_custody_issues(
    release_manifest: Mapping[str, Any],
    data_directory: Path,
) -> list[str]:
    issues: list[str] = []
    rows = release_manifest.get("custody_inputs")
    if not isinstance(rows, Mapping):
        return ["published release custody registry is invalid"]
    for name, row in rows.items():
        if not isinstance(row, Mapping):
            issues.append(f"release custody input {name} is invalid")
            continue
        path = _declared_path(data_directory, row.get("path"))
        if not path.is_file():
            issues.append(f"release custody input {name} is missing")
            continue
        if _sha256(path) != str(row.get("sha256", "")) or path.stat().st_size != int(row.get("bytes", -1)):
            issues.append(f"release custody input {name} identity drift")
    return issues


def _model_source_rows(data_directory: Path) -> dict[str, Mapping[str, Any]]:
    payload = _optional_json(data_directory / "model_sources" / "manifest.json")
    if not isinstance(payload, Mapping) or not isinstance(payload.get("files"), list):
        return {}
    return {
        str(row.get("model_id")): row
        for row in payload["files"]
        if isinstance(row, Mapping) and str(row.get("model_id", ""))
    }


def _model_source_custody(row: Mapping[str, Any] | None) -> ModelSourceCustody | None:
    if not isinstance(row, Mapping):
        return None
    try:
        return ModelSourceCustody(
            path=str(row["path"]),
            sha256=str(row["sha256"]),
            bytes=int(row["bytes"]),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _relation_anchor_rows(data_directory: Path) -> dict[str, Mapping[str, Any]] | None:
    payload = _optional_json(data_directory / "curation" / "relation_source_anchor_register.json")
    if not isinstance(payload, Mapping) or not isinstance(payload.get("relations"), list):
        return None
    rows: dict[str, Mapping[str, Any]] = {}
    for row in payload["relations"]:
        if not isinstance(row, Mapping):
            return None
        relation_id = str(row.get("relation_id", ""))
        if not relation_id or relation_id in rows:
            return None
        rows[relation_id] = row
    return rows


def _relation_custody(
    row: Mapping[str, Any] | None,
    expected_published_index: int,
) -> RelationCustody | None:
    if not isinstance(row, Mapping):
        return None
    authoring = row.get("authoring_pointer")
    published = row.get("published_pointer")
    source = row.get("source")
    if not isinstance(authoring, Mapping) or not isinstance(published, Mapping) or not isinstance(source, Mapping):
        return None
    try:
        if int(published["item_index"]) != expected_published_index:
            return None
        span = row.get("exact_span")
        return RelationCustody(
            authoring_path=str(authoring["path"]),
            authoring_family=str(authoring["family"]),
            authoring_item_index=int(authoring["item_index"]),
            compiled_pointer=f"data/relationship_graph.json#/{expected_published_index}",
            source_path=str(source["path"]),
            source_sha256=str(source["sha256"] or ""),
            source_bytes=int(source["bytes"] or 0),
            source_anchor_state=str(row["source_anchor_state"]),
            exact_span=_freeze(span) if isinstance(span, Mapping) else None,
        )
    except (KeyError, TypeError, ValueError):
        return None


def _empty_snapshot(
    root: Path,
    data_directory: Path,
    knowledge_payload: Mapping[str, Any],
) -> PublishedKnowledgeSnapshot:
    coverage = MappingProxyType(
        {
            "knowledge_graph": "complete",
            "relationship_graph": "completed_zero",
            "model_registry": "completed_zero",
            "tendency_registry": "completed_zero",
            "relation_registry": "completed_zero",
        }
    )
    empty_mapping: Mapping[str, Any] = MappingProxyType({})
    return PublishedKnowledgeSnapshot(
        root=root,
        data_directory=data_directory,
        release_id="completed-zero-unregistered",
        release_identity=empty_mapping,
        coverage=coverage,
        models=empty_mapping,
        tendencies=empty_mapping,
        relations=(),
        _relations_by_id=empty_mapping,
        _outgoing=empty_mapping,
        _incoming=empty_mapping,
        _knowledge_payload=_freeze(knowledge_payload),
        _relationship_payload=(),
    )


def _load_result(
    status: str,
    coverage: Mapping[str, str],
    *,
    snapshot: PublishedKnowledgeSnapshot | None = None,
    issues: tuple[str, ...] = (),
) -> PublishedSubstrateLoadResult:
    return PublishedSubstrateLoadResult(
        status=status,
        coverage=MappingProxyType(dict(coverage)),
        snapshot=snapshot,
        issues=issues,
        provider_calls=0,
        runtime_generation_attempted=False,
    )


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value
