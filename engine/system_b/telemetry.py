from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import statistics
from typing import TYPE_CHECKING, Mapping, Sequence
import uuid

from .testing_harness import normalize_text, summarize_boundary_calls

if TYPE_CHECKING:
    from .pipeline import CritiqueRequest, PipelineConfig, PipelineResult


_BOUNDARY_FAILURE_STATUSES = frozenset({"timeout", "error", "not_called"})
_REGRESSION_METRICS = (
    "process.structural.boundary_health",
    "process.structural.route_completeness_ratio",
    "process.structural.trusted_surface_ratio",
    "novelty.delta_novelty",
    "novelty.composite_novelty",
    "novelty.companion_additive_value",
    "novelty.frame_novelty_ratio",
    "complementarity.independence_ratio",
    "frame.element_count",
    "frame.reframing_count",
    "frame.overlap_flag_count",
    "influence.challenge_adoption_rate",
)


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    timestamp: str
    request_hash: str
    config_snapshot: dict[str, object]
    process_metrics: dict[str, object]
    structural_pressure_metrics: dict[str, object]
    companion_metrics: dict[str, object] | None = None
    frame_pressure_metrics: dict[str, object] | None = None
    lane_complementarity: dict[str, object] | None = None
    novelty: dict[str, object] | None = None
    influence: dict[str, object] | None = None
    warnings: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "request_hash": self.request_hash,
            "config_snapshot": dict(self.config_snapshot),
            "process_metrics": dict(self.process_metrics),
            "structural_pressure_metrics": dict(self.structural_pressure_metrics),
            "companion_metrics": dict(self.companion_metrics) if self.companion_metrics is not None else None,
            "frame_pressure_metrics": dict(self.frame_pressure_metrics) if self.frame_pressure_metrics is not None else None,
            "lane_complementarity": dict(self.lane_complementarity or {}),
            "novelty": dict(self.novelty or {}),
            "influence": dict(self.influence or {}) if self.influence is not None else None,
            "warnings": list(self.warnings),
            "tags": list(self.tags),
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> "RunRecord":
        return cls(
            run_id=str(payload.get("run_id", "")).strip(),
            timestamp=str(payload.get("timestamp", "")).strip(),
            request_hash=str(payload.get("request_hash", "")).strip(),
            config_snapshot=_mapping(payload.get("config_snapshot")),
            process_metrics=_mapping(payload.get("process_metrics")),
            structural_pressure_metrics=_mapping(payload.get("structural_pressure_metrics")),
            companion_metrics=_optional_mapping(payload.get("companion_metrics")),
            frame_pressure_metrics=_optional_mapping(payload.get("frame_pressure_metrics")),
            lane_complementarity=_optional_mapping(payload.get("lane_complementarity")) or {},
            novelty=_optional_mapping(payload.get("novelty")) or {},
            influence=_optional_mapping(payload.get("influence")),
            warnings=_string_tuple(payload.get("warnings")),
            tags=_string_tuple(payload.get("tags")),
        )


@dataclass(frozen=True)
class AggregateReport:
    run_count: int
    since: str = ""
    until: str = ""
    process_quality: dict[str, object] | None = None
    novelty: dict[str, object] | None = None
    influence: dict[str, object] | None = None
    lane_complementarity: dict[str, object] | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "run_count": self.run_count,
            "since": self.since,
            "until": self.until,
            "process_quality": dict(self.process_quality or {}),
            "novelty": dict(self.novelty or {}),
            "influence": dict(self.influence or {}),
            "lane_complementarity": dict(self.lane_complementarity or {}),
        }


@dataclass(frozen=True)
class RegressionAlert:
    run_id: str
    timestamp: str
    metric: str
    observed: float
    rolling_mean: float
    rolling_std: float

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class TendencyStats:
    tendency_id: str
    run_count: int = 0
    trusted_surface_ratio: float = 0.0
    average_specificity: float = 0.0

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ModelStats:
    model_id: str
    structural_count: int = 0
    companion_count: int = 0
    total_count: int = 0

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CompanionLaneStats:
    run_count: int
    detection_model_count_avg: float = 0.0
    expansion_count_avg: float = 0.0
    failure_hint_count_avg: float = 0.0
    overlap_ratio_avg: float = 0.0
    relation_type_distribution: dict[str, int] | None = None
    recall_source_distribution: dict[str, int] | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "run_count": self.run_count,
            "detection_model_count_avg": self.detection_model_count_avg,
            "expansion_count_avg": self.expansion_count_avg,
            "failure_hint_count_avg": self.failure_hint_count_avg,
            "overlap_ratio_avg": self.overlap_ratio_avg,
            "relation_type_distribution": dict(self.relation_type_distribution or {}),
            "recall_source_distribution": dict(self.recall_source_distribution or {}),
        }


@dataclass(frozen=True)
class ComplementarityStats:
    run_count: int
    overlap_ratio_avg: float = 0.0
    independence_ratio_avg: float = 0.0
    combined_novelty_avg: float = 0.0

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


class TelemetryStore:
    def __init__(self, db_path: Path) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    @property
    def db_path(self) -> Path:
        return self._db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    request_hash TEXT NOT NULL,
                    payload JSON NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON runs(timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runs_request_hash ON runs(request_hash)"
            )

    def record_run(self, run_record: RunRecord) -> None:
        payload = json.dumps(run_record.to_payload(), ensure_ascii=False, sort_keys=True)
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO runs(run_id, timestamp, request_hash, payload) VALUES (?, ?, ?, ?)",
                    (run_record.run_id, run_record.timestamp, run_record.request_hash, payload),
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError(f"run_id already exists: {run_record.run_id}") from exc

    def get_run(self, run_id: str) -> RunRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload FROM runs WHERE run_id = ?",
                (str(run_id).strip(),),
            ).fetchone()
        if row is None:
            return None
        return RunRecord.from_payload(json.loads(str(row["payload"])))

    def list_runs(
        self,
        *,
        since: str = "",
        until: str = "",
        tags: Sequence[str] = (),
        request_hash: str = "",
    ) -> list[RunRecord]:
        clauses: list[str] = []
        params: list[object] = []
        if normalize_text(since):
            clauses.append("timestamp >= ?")
            params.append(str(since).strip())
        if normalize_text(until):
            clauses.append("timestamp <= ?")
            params.append(str(until).strip())
        if normalize_text(request_hash):
            clauses.append("request_hash = ?")
            params.append(str(request_hash).strip())
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT payload FROM runs {where} ORDER BY timestamp ASC"
            , params).fetchall()
        records = [RunRecord.from_payload(json.loads(str(row["payload"]))) for row in rows]
        normalized_tags = {normalize_text(tag) for tag in list(tags or []) if normalize_text(tag)}
        if not normalized_tags:
            return records
        return [
            record
            for record in records
            if normalized_tags.issubset({normalize_text(tag) for tag in record.tags})
        ]


def default_telemetry_db_path(root: Path) -> Path:
    return Path(root) / "build" / "runs.db"


def build_run_record(
    *,
    request: "CritiqueRequest",
    result: "PipelineResult",
    config: "PipelineConfig",
    tags: Sequence[str] = (),
    timings: Mapping[str, object] | None = None,
    companion_candidates: Sequence[Mapping[str, object]] = (),
    influence_report: Mapping[str, object] | None = None,
    run_id: str = "",
    timestamp: str = "",
) -> RunRecord:
    from .novelty_scorer import score_novelty

    normalized_timestamp = str(timestamp).strip() or datetime.now(timezone.utc).isoformat()
    resolved_run_id = str(run_id).strip() or str(uuid.uuid4())
    boundary_summary = summarize_boundary_calls(result.audit.boundary_calls)
    llm_triggered = tuple(
        score.tendency_id
        for score in result.audit.triage_scores
        if int(score.score or 0) >= int(config.triage_threshold)
    )
    structural_metrics = _build_structural_pressure_metrics(result=result, llm_triggered=llm_triggered)
    companion_metrics = _build_companion_metrics(
        result=result,
        companion_candidates=companion_candidates,
    )
    lane_complementarity = _build_lane_complementarity(result)
    frame_pressure_metrics = _build_frame_pressure_metrics(result)
    novelty_report = score_novelty(
        vanilla_answer=request.vanilla_answer,
        delta_card=result.delta_card,
        companion_card=result.companion_card,
        frame_pressure_card=result.frame_pressure_card,
    ).to_payload()

    record = RunRecord(
        run_id=resolved_run_id,
        timestamp=normalized_timestamp,
        request_hash=build_request_hash(request.query, request.vanilla_answer),
        config_snapshot=asdict(config),
        process_metrics={
            "boundary_summary": boundary_summary,
            "timings": dict(timings or {}),
            "overall_boundary_health": _boundary_health(result.audit.boundary_calls),
            "structural_boundary_health": _boundary_health(
                [call for call in result.audit.boundary_calls if call.stage in {"pass1", "pass2"}]
            ),
            "companion_boundary_health": _boundary_health(
                [call for call in result.audit.boundary_calls if str(call.stage).startswith("companion_")]
            ),
        },
        structural_pressure_metrics=structural_metrics,
        companion_metrics=companion_metrics,
        frame_pressure_metrics=frame_pressure_metrics,
        lane_complementarity=lane_complementarity,
        novelty=novelty_report,
        influence=dict(influence_report or {}) if influence_report is not None else None,
        warnings=tuple(str(item) for item in result.audit.warnings if normalize_text(item)),
        tags=tuple(str(item).strip() for item in list(tags or []) if str(item).strip()),
    )
    return replace(
        record,
        process_metrics={
            **record.process_metrics,
            "quality": process_quality_score(record),
        },
    )


def record_pipeline_run(
    *,
    store: TelemetryStore,
    request: "CritiqueRequest",
    result: "PipelineResult",
    config: "PipelineConfig",
    tags: Sequence[str] = (),
    timings: Mapping[str, object] | None = None,
    companion_candidates: Sequence[Mapping[str, object]] = (),
    influence_report: Mapping[str, object] | None = None,
) -> RunRecord:
    run_record = build_run_record(
        request=request,
        result=result,
        config=config,
        tags=tags,
        timings=timings,
        companion_candidates=companion_candidates,
        influence_report=influence_report,
    )
    store.record_run(run_record)
    return run_record


def build_request_hash(query: str, vanilla_answer: str) -> str:
    payload = "\x1f".join((normalize_text(query), normalize_text(vanilla_answer)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def process_quality_score(run_record: RunRecord) -> dict[str, object]:
    structural = _mapping(run_record.structural_pressure_metrics.get("detection_metrics"))
    routing = _mapping(run_record.structural_pressure_metrics.get("routing_metrics"))
    delta = _mapping(run_record.structural_pressure_metrics.get("delta_card_metrics"))
    companion = run_record.companion_metrics or {}
    companion_detection = _mapping(companion.get("detection_metrics"))
    companion_candidates = _mapping(companion.get("candidate_metrics"))
    companion_gathering = _mapping(companion.get("gathering_metrics"))
    companion_selection = _mapping(companion.get("selection_metrics"))
    companion_anti_echo = _mapping(companion.get("anti_echo_metrics"))
    timings = _mapping(run_record.process_metrics.get("timings"))
    complementarity = run_record.lane_complementarity or {}
    return {
        "structural": {
            "boundary_health": float(run_record.process_metrics.get("structural_boundary_health") or 0.0),
            "cache_efficiency": _safe_ratio(
                _as_float(_mapping(run_record.process_metrics.get("boundary_summary")).get("cached_tokens_total")),
                _as_float(_mapping(run_record.process_metrics.get("boundary_summary")).get("prompt_tokens_total")),
            ),
            "detection_breadth": _as_float(structural.get("triggered_count")),
            "embedding_additions": _as_float(structural.get("embedding_only_triggered_count")),
            "sub_pattern_depth": float(structural.get("sub_pattern_depth") or 0.0),
            "route_completeness_ratio": float(routing.get("route_completeness_ratio") or 0.0),
            "trusted_surface_ratio": float(delta.get("trusted_surface_ratio") or 0.0),
        },
        "companion": (
            {
                "boundary_health": float(run_record.process_metrics.get("companion_boundary_health") or 0.0),
                "fingerprint_validation_rate": float(companion_detection.get("quote_validation_rate") or 0.0),
                "verification_precision": float(companion_detection.get("verification_precision") or 0.0),
                "candidate_count": _as_float(companion_candidates.get("candidate_count")),
                "selection_efficiency": float(companion_selection.get("detected_model_budget_utilization") or 0.0),
                "failure_hint_utilization": float(companion_selection.get("failure_hint_budget_utilization") or 0.0),
                "expansion_utilization": float(companion_selection.get("expansion_budget_utilization") or 0.0),
                "anti_echo_overlap_ratio": float(companion_anti_echo.get("overlap_ratio") or 0.0),
                "gathered_surface_items": _as_float(companion_gathering.get("total_surface_items")),
            }
            if companion
            else None
        ),
        "cross_lane": {
            "total_seconds": float(timings.get("total_seconds") or 0.0),
            "pass1_seconds": float(timings.get("pass1_seconds") or 0.0),
            "pass2_seconds": float(timings.get("pass2_seconds") or 0.0),
            "companion_seconds": float(timings.get("companion_seconds") or 0.0),
            "lane_overlap_ratio": float(complementarity.get("overlap_ratio") or 0.0),
            "independence_ratio": float(complementarity.get("independence_ratio") or 0.0),
        },
    }


def aggregate_runs(runs: Sequence[RunRecord]) -> AggregateReport:
    items = list(runs or [])
    if not items:
        return AggregateReport(run_count=0)
    process_rows = [process_quality_score(run) for run in items]
    return AggregateReport(
        run_count=len(items),
        since=items[0].timestamp,
        until=items[-1].timestamp,
        process_quality={
            "structural": {
                "boundary_health_avg": _mean(row["structural"]["boundary_health"] for row in process_rows),
                "route_completeness_ratio_avg": _mean(
                    row["structural"]["route_completeness_ratio"] for row in process_rows
                ),
                "trusted_surface_ratio_avg": _mean(
                    row["structural"]["trusted_surface_ratio"] for row in process_rows
                ),
            },
            "companion": {
                "boundary_health_avg": _mean(
                    row["companion"]["boundary_health"]
                    for row in process_rows
                    if isinstance(row.get("companion"), Mapping)
                ),
                "verification_precision_avg": _mean(
                    row["companion"]["verification_precision"]
                    for row in process_rows
                    if isinstance(row.get("companion"), Mapping)
                ),
            },
            "cross_lane": {
                "total_seconds_avg": _mean(row["cross_lane"]["total_seconds"] for row in process_rows),
                "independence_ratio_avg": _mean(
                    row["cross_lane"]["independence_ratio"] for row in process_rows
                ),
            },
        },
        novelty={
            "delta_novelty_avg": _mean(_metric_value(run, "novelty.delta_novelty") for run in items),
            "composite_novelty_avg": _mean(_metric_value(run, "novelty.composite_novelty") for run in items),
            "combined_novelty_avg": _mean(_metric_value(run, "novelty.combined_novelty") for run in items),
            "companion_additive_value_avg": _mean(
                _metric_value(run, "novelty.companion_additive_value") for run in items
            ),
        },
        influence={
            "challenge_adoption_rate_avg": _mean(
                _metric_value(run, "influence.challenge_adoption_rate") for run in items
            ),
            "structural_change_count_avg": _mean(
                len(list((_optional_mapping(run.influence) or {}).get("structural_changes", []) or []))
                for run in items
                if run.influence is not None
            ),
        },
        lane_complementarity={
            "overlap_ratio_avg": _mean(_metric_value(run, "complementarity.overlap_ratio") for run in items),
            "independence_ratio_avg": _mean(
                _metric_value(run, "complementarity.independence_ratio") for run in items
            ),
            "combined_novelty_avg": _mean(_metric_value(run, "novelty.combined_novelty") for run in items),
        },
    )


def detect_regressions(runs: Sequence[RunRecord], window: int = 20) -> list[RegressionAlert]:
    items = list(runs or [])
    if window <= 0:
        return []
    alerts: list[RegressionAlert] = []
    for index, run in enumerate(items):
        history = items[max(0, index - window) : index]
        if len(history) < 5:
            continue
        for metric in _REGRESSION_METRICS:
            history_values = [value for value in (_metric_value(item, metric) for item in history) if value is not None]
            observed = _metric_value(run, metric)
            if observed is None or len(history_values) < 5:
                continue
            mean = statistics.fmean(history_values)
            std = statistics.pstdev(history_values)
            threshold = mean - (2 * std)
            if observed < threshold:
                alerts.append(
                    RegressionAlert(
                        run_id=run.run_id,
                        timestamp=run.timestamp,
                        metric=metric,
                        observed=round(observed, 3),
                        rolling_mean=round(mean, 3),
                        rolling_std=round(std, 3),
                    )
                )
    return alerts


def breakdown_by_tendency(runs: Sequence[RunRecord]) -> dict[str, TendencyStats]:
    buckets: dict[str, dict[str, list[float] | int]] = {}
    for run in list(runs or []):
        specificity_breakdown = {
            str(item.get("tendency_id", "")).strip(): float(item.get("specificity_score", 0.0) or 0.0)
            for item in list(_optional_mapping(run.novelty).get("specificity_breakdown", []) or [])
            if isinstance(item, Mapping) and str(item.get("tendency_id", "")).strip()
        }
        trusted_ids = {
            str(item).strip()
            for item in list(_mapping(run.structural_pressure_metrics.get("delta_card_metrics")).get("trusted_surface_tendency_ids", []) or [])
            if str(item).strip()
        }
        for tendency_id in list(_mapping(run.structural_pressure_metrics.get("detection_metrics")).get("detected_tendency_ids", []) or []):
            key = str(tendency_id).strip()
            if not key:
                continue
            bucket = buckets.setdefault(
                key,
                {"count": 0, "trusted": [], "specificity": []},
            )
            bucket["count"] = int(bucket["count"]) + 1
            cast_trusted = bucket["trusted"]
            cast_specificity = bucket["specificity"]
            assert isinstance(cast_trusted, list)
            assert isinstance(cast_specificity, list)
            cast_trusted.append(1.0 if key in trusted_ids else 0.0)
            cast_specificity.append(specificity_breakdown.get(key, 0.0))
    return {
        tendency_id: TendencyStats(
            tendency_id=tendency_id,
            run_count=int(values["count"]),
            trusted_surface_ratio=round(_mean(values["trusted"]), 3),
            average_specificity=round(_mean(values["specificity"]), 3),
        )
        for tendency_id, values in sorted(buckets.items())
    }


def breakdown_by_model(runs: Sequence[RunRecord]) -> dict[str, ModelStats]:
    buckets: dict[str, dict[str, int]] = {}
    for run in list(runs or []):
        structural_ids = _string_tuple(
            _mapping(run.structural_pressure_metrics.get("routing_metrics")).get("selected_model_ids", [])
        )
        companion_ids = _string_tuple(
            _optional_mapping(run.companion_metrics).get("all_model_ids", [])
        )
        for model_id in structural_ids:
            bucket = buckets.setdefault(model_id, {"structural": 0, "companion": 0})
            bucket["structural"] += 1
        for model_id in companion_ids:
            bucket = buckets.setdefault(model_id, {"structural": 0, "companion": 0})
            bucket["companion"] += 1
    return {
        model_id: ModelStats(
            model_id=model_id,
            structural_count=counts["structural"],
            companion_count=counts["companion"],
            total_count=counts["structural"] + counts["companion"],
        )
        for model_id, counts in sorted(buckets.items())
    }


def breakdown_companion_lane(runs: Sequence[RunRecord]) -> CompanionLaneStats:
    items = [run for run in list(runs or []) if run.companion_metrics]
    if not items:
        return CompanionLaneStats(run_count=0)
    relation_types: dict[str, int] = {}
    recall_sources: dict[str, int] = {}
    for run in items:
        gathering = _mapping(_optional_mapping(run.companion_metrics).get("gathering_metrics"))
        candidate_metrics = _mapping(_optional_mapping(run.companion_metrics).get("candidate_metrics"))
        for key, value in _mapping(gathering.get("relation_type_distribution")).items():
            relation_types[str(key)] = relation_types.get(str(key), 0) + int(value or 0)
        for key, value in _mapping(candidate_metrics.get("recall_source_distribution")).items():
            recall_sources[str(key)] = recall_sources.get(str(key), 0) + int(value or 0)
    return CompanionLaneStats(
        run_count=len(items),
        detection_model_count_avg=round(
            _mean(
                _as_float(_mapping(_optional_mapping(run.companion_metrics).get("detection_metrics")).get("detected_model_count"))
                for run in items
            ),
            3,
        ),
        expansion_count_avg=round(
            _mean(
                _as_float(_mapping(_optional_mapping(run.companion_metrics).get("gathering_metrics")).get("expansion_count"))
                for run in items
            ),
            3,
        ),
        failure_hint_count_avg=round(
            _mean(
                _as_float(_mapping(_optional_mapping(run.companion_metrics).get("gathering_metrics")).get("failure_hint_count"))
                for run in items
            ),
            3,
        ),
        overlap_ratio_avg=round(
            _mean(
                _as_float(_mapping(_optional_mapping(run.companion_metrics).get("anti_echo_metrics")).get("overlap_ratio"))
                for run in items
            ),
            3,
        ),
        relation_type_distribution=relation_types,
        recall_source_distribution=recall_sources,
    )


def breakdown_lane_complementarity(runs: Sequence[RunRecord]) -> ComplementarityStats:
    items = list(runs or [])
    if not items:
        return ComplementarityStats(run_count=0)
    return ComplementarityStats(
        run_count=len(items),
        overlap_ratio_avg=round(_mean(_metric_value(run, "complementarity.overlap_ratio") for run in items), 3),
        independence_ratio_avg=round(
            _mean(_metric_value(run, "complementarity.independence_ratio") for run in items),
            3,
        ),
        combined_novelty_avg=round(
            _mean(_metric_value(run, "novelty.combined_novelty") for run in items),
            3,
        ),
    )


def _build_structural_pressure_metrics(
    *,
    result: "PipelineResult",
    llm_triggered: Sequence[str],
) -> dict[str, object]:
    deep_detected = [item for item in result.audit.deep_check_results if bool(item.detected)]
    routes = list(result.routes)
    trusted_ids = [finding.tendency_id for finding in result.delta_card.findings if finding.is_trusted_surface]
    general_count = sum(
        1
        for item in deep_detected
        if str(item.sub_pattern or "").strip().replace("_", "-").lower() in {"", "general"}
    )
    specific_passage_count = sum(1 for finding in result.delta_card.findings if normalize_text(finding.specific_passage))
    return {
        "detection_metrics": {
            "triage_triggered_count": len(list(llm_triggered)),
            "triggered_count": len(result.audit.triggered_tendencies),
            "embedding_only_triggered_count": max(len(result.audit.triggered_tendencies) - len(list(llm_triggered)), 0),
            "detected_count": len(deep_detected),
            "detected_tendency_ids": [item.tendency_id for item in deep_detected],
            "specific_sub_pattern_count": len(deep_detected) - general_count,
            "general_sub_pattern_count": general_count,
            "sub_pattern_depth": _safe_ratio(len(deep_detected) - general_count, len(deep_detected)),
        },
        "routing_metrics": {
            "route_count": len(routes),
            "routed_with_primary_model_count": sum(1 for route in routes if normalize_text(route.primary_model_id)),
            "route_completeness_ratio": _safe_ratio(
                sum(1 for route in routes if normalize_text(route.primary_model_id)),
                len(deep_detected),
            ),
            "supporting_model_count": sum(len(route.supporting_model_ids) for route in routes),
            "risk_model_count": sum(len(route.risk_model_ids) for route in routes),
            "selected_model_ids": list(result.delta_card.selected_model_ids),
        },
        "delta_card_metrics": {
            "finding_count": len(result.delta_card.findings),
            "top_findings_count": len(result.delta_card.top_findings),
            "secondary_findings_count": len(result.delta_card.secondary_findings),
            "compound_group_count": len(result.delta_card.compound_groups),
            "specific_passage_count": specific_passage_count,
            "trusted_surface_ratio": _safe_ratio(len(trusted_ids), len(result.delta_card.findings)),
            "trusted_surface_tendency_ids": trusted_ids,
            "generic_finding_count": sum(
                1
                for finding in result.delta_card.findings
                if not finding.is_trusted_surface
                and not normalize_text(finding.specific_passage)
                and str(finding.sub_pattern or "").strip().replace("_", "-").lower() in {"", "general"}
            ),
        },
    }


def _build_companion_metrics(
    *,
    result: "PipelineResult",
    companion_candidates: Sequence[Mapping[str, object]],
) -> dict[str, object] | None:
    card = result.companion_card
    if card is None and not result.audit.companion_fingerprint_raw and not list(companion_candidates or []):
        return None
    detected_models = list(card.detected_models) if card is not None else []
    expansions = list(card.expansions) if card is not None else []
    failure_hints = list(card.failure_hints) if card is not None else []
    heuristic_hints = list(card.heuristic_hints) if card is not None else []
    premortem_hints = list(card.premortem_hints) if card is not None else []
    identity_chunks = list(card.identity_chunks) if card is not None else []
    candidate_rows = list(companion_candidates or [])
    raw_fingerprint_count = len(result.audit.companion_fingerprint_raw)
    validated_fingerprint_count = len(result.audit.companion_fingerprint_validated)
    detected_model_ids = [item.model_id for item in detected_models]
    expansion_model_ids = [item.model_id for item in expansions]
    all_model_ids = list(dict.fromkeys([*detected_model_ids, *expansion_model_ids]))
    overlap_model_ids = sorted(set(all_model_ids) & set(result.delta_card.selected_model_ids))
    relation_type_distribution: dict[str, int] = {}
    for expansion in expansions:
        relation_type_distribution[expansion.relation_type] = relation_type_distribution.get(expansion.relation_type, 0) + 1
    recall_source_distribution: dict[str, int] = {}
    for row in candidate_rows:
        source = normalize_text(row.get("recall_source", "keyword_recall")) or "keyword_recall"
        recall_source_distribution[source] = recall_source_distribution.get(source, 0) + 1
    detected_count = len(detected_models)
    return {
        "detection_metrics": {
            "raw_fingerprint_count": raw_fingerprint_count,
            "validated_fingerprint_count": validated_fingerprint_count,
            "dropped_fingerprint_count": len(result.audit.companion_fingerprint_dropped),
            "quote_validation_rate": _safe_ratio(validated_fingerprint_count, raw_fingerprint_count),
            "detected_model_count": detected_count,
            "rejected_model_count": len(result.audit.companion_rejected_models),
            "verification_precision": _safe_ratio(
                detected_count,
                detected_count + len(result.audit.companion_rejected_models),
            ),
            "presence_mode_distribution": _count_strings(model.presence_mode for model in detected_models),
        },
        "candidate_metrics": {
            "candidate_count": len(candidate_rows),
            "recall_source_distribution": recall_source_distribution,
        },
        "gathering_metrics": {
            "expansion_count": len(expansions),
            "failure_hint_count": len(failure_hints),
            "heuristic_hint_count": len(heuristic_hints),
            "premortem_hint_count": len(premortem_hints),
            "identity_chunk_count": len(identity_chunks),
            "total_surface_items": detected_count + len(expansions) + len(failure_hints) + len(heuristic_hints) + len(premortem_hints) + len(identity_chunks),
            "chunk_type_count": sum(1 for lst in [detected_models, expansions, failure_hints, heuristic_hints, premortem_hints, identity_chunks] if lst),
            "relation_type_distribution": relation_type_distribution,
        },
        "selection_metrics": {
            "detected_model_budget_utilization": _safe_ratio(detected_count, 5),
            "expansion_budget_utilization": _safe_ratio(len(expansions), max(detected_count * 3, 1)),
            "failure_hint_budget_utilization": _safe_ratio(len(failure_hints), max(detected_count * 2, 1)),
            "heuristic_hint_budget_utilization": _safe_ratio(len(heuristic_hints), max(detected_count * 2, 1)),
            "premortem_hint_budget_utilization": _safe_ratio(len(premortem_hints), max(detected_count * 2, 1)),
        },
        "anti_echo_metrics": {
            "anti_echo_available": bool(getattr(result, "companion_cheat_sheet", None) is not None),
            "overlap_model_ids": overlap_model_ids,
            "overlap_count": len(overlap_model_ids),
            "overlap_ratio": _safe_ratio(len(overlap_model_ids), len(all_model_ids)),
        },
        "all_model_ids": all_model_ids,
        "cheat_sheet_metrics": _build_cheat_sheet_metrics(result),
    }


def _build_cheat_sheet_metrics(result: "PipelineResult") -> dict[str, object] | None:
    cs = getattr(result, "companion_cheat_sheet", None)
    if cs is None:
        return None
    chunk_types: set[str] = set()
    for anchor in cs.anchors:
        for chunk in anchor.chunks:
            chunk_types.add(chunk.chunk_type)
    metrics: dict[str, object] = {
        "total_chunk_count": cs.total_chunk_count,
        "budget_max": cs.budget_max,
        "budget_utilization": _safe_ratio(cs.total_chunk_count, cs.budget_max),
        "anchor_count": len(cs.anchors),
        "type_diversity": len(chunk_types),
        "chunk_type_distribution": {t: sum(1 for a in cs.anchors for c in a.chunks if c.chunk_type == t) for t in sorted(chunk_types)},
        "anti_echo_model_count": len(cs.anti_echo_model_ids),
    }
    # Reranker metrics (present only when reranker was active)
    if getattr(cs, "reranker_active", False):
        metrics["reranker"] = {
            "active": True,
            "chunks_above_relevance_floor": getattr(cs, "chunks_above_relevance_floor", 0),
            "mean_relevance_score": round(getattr(cs, "mean_relevance_score", 0.0), 4),
        }
    # Mitigation coverage: fraction of failure_mode chunks (all curated failure modes
    # carry mitigations since the 2026-04-03 enrichment; this metric guards against
    # regression if new un-mitigated failure modes are added).
    failure_mode_count = sum(
        1 for a in cs.anchors for c in a.chunks if c.chunk_type == "failure_mode"
    )
    if failure_mode_count > 0:
        metrics["failure_mode_chunk_count"] = failure_mode_count
    return metrics


def _build_lane_complementarity(result: "PipelineResult") -> dict[str, object]:
    companion_ids = []
    if result.companion_card is not None:
        companion_ids.extend(item.model_id for item in result.companion_card.detected_models)
        companion_ids.extend(item.model_id for item in result.companion_card.expansions)
    structural_ids = list(result.delta_card.selected_model_ids)
    companion_unique = list(dict.fromkeys(item for item in companion_ids if normalize_text(item)))
    overlap_ids = sorted(set(structural_ids) & set(companion_unique))
    union_count = len(set(structural_ids) | set(companion_unique))
    overlap_ratio = _safe_ratio(len(overlap_ids), union_count)
    return {
        "structural_model_ids": structural_ids,
        "companion_model_ids": companion_unique,
        "overlap_model_ids": overlap_ids,
        "overlap_ratio": overlap_ratio,
        "independence_ratio": round(1.0 - overlap_ratio, 3),
    }


def _build_frame_pressure_metrics(result: "PipelineResult") -> dict[str, object] | None:
    card = result.frame_pressure_card
    if card is None:
        return None
    elements = list(card.frame_elements)
    pattern_ids = [el.frame_pattern for el in elements]
    element_types: dict[str, int] = {}
    for el in elements:
        element_types[el.element_type] = element_types.get(el.element_type, 0) + 1
    return {
        "element_count": len(elements),
        "pattern_ids": pattern_ids,
        "element_type_distribution": element_types,
        "overlap_flag_count": len(card.overlap_flags),
        "overlap_flags": list(card.overlap_flags),
        "anti_echo_model_count": len(card.anti_echo_model_ids),
        "reframing_count": len(card.reframings),
        "fired": len(elements) > 0,
    }


def _metric_value(run: RunRecord, metric: str) -> float | None:
    if metric == "process.structural.boundary_health":
        return float(_mapping(process_quality_score(run).get("structural")).get("boundary_health") or 0.0)
    if metric == "process.structural.route_completeness_ratio":
        return float(_mapping(process_quality_score(run).get("structural")).get("route_completeness_ratio") or 0.0)
    if metric == "process.structural.trusted_surface_ratio":
        return float(_mapping(process_quality_score(run).get("structural")).get("trusted_surface_ratio") or 0.0)
    if metric == "novelty.delta_novelty":
        return round(1.0 - float(_optional_mapping(run.novelty).get("passage_overlap_ratio") or 0.0), 3)
    if metric == "novelty.composite_novelty":
        return float(_optional_mapping(run.novelty).get("composite_novelty_score") or 0.0)
    if metric == "novelty.combined_novelty":
        combined = _optional_mapping(_optional_mapping(run.novelty).get("combined_novelty"))
        if not combined:
            return None
        return round(1.0 - float(combined.get("lane_overlap_ratio") or 0.0), 3)
    if metric == "novelty.companion_additive_value":
        companion = _optional_mapping(_optional_mapping(run.novelty).get("companion_novelty"))
        if not companion:
            return None
        return round(1.0 - float(companion.get("chunk_overlap_vs_delta") or 0.0), 3)
    if metric == "complementarity.overlap_ratio":
        return float(_optional_mapping(run.lane_complementarity).get("overlap_ratio") or 0.0)
    if metric == "complementarity.independence_ratio":
        return float(_optional_mapping(run.lane_complementarity).get("independence_ratio") or 0.0)
    if metric == "novelty.frame_novelty_ratio":
        frame_nov = _optional_mapping(_optional_mapping(run.novelty).get("frame_novelty"))
        if not frame_nov:
            return None
        return float(frame_nov.get("frame_novelty_ratio") or 0.0)
    if metric == "frame.element_count":
        fp = _optional_mapping(run.frame_pressure_metrics)
        if not fp:
            return None
        return float(fp.get("element_count") or 0)
    if metric == "frame.reframing_count":
        fp = _optional_mapping(run.frame_pressure_metrics)
        if not fp:
            return None
        return float(fp.get("reframing_count") or 0)
    if metric == "frame.overlap_flag_count":
        fp = _optional_mapping(run.frame_pressure_metrics)
        if not fp:
            return None
        return float(fp.get("overlap_flag_count") or 0)
    if metric == "influence.challenge_adoption_rate":
        influence = _optional_mapping(run.influence)
        if not influence:
            return None
        return float(influence.get("challenge_adoption_rate") or 0.0)
    return None


def _boundary_health(boundary_calls: Sequence[object]) -> float:
    calls = list(boundary_calls or [])
    if not calls:
        return 0.0
    success_count = 0
    for call in calls:
        status = normalize_text(getattr(call, "status", ""))
        if status and status not in _BOUNDARY_FAILURE_STATUSES:
            success_count += 1
    return round(success_count / len(calls), 3)


def _count_strings(values: Sequence[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        normalized = normalize_text(value)
        if not normalized:
            continue
        counts[normalized] = counts.get(normalized, 0) + 1
    return counts


def _mean(values) -> float:
    materialized = [float(value) for value in list(values) if value is not None]
    if not materialized:
        return 0.0
    return round(statistics.fmean(materialized), 3)


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return round(float(numerator) / float(denominator), 3)


def _as_float(value: object) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _mapping(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, Mapping) else {}


def _optional_mapping(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, Mapping) else {}


def _string_tuple(value: object) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)):
        normalized = normalize_text(value)
        return (normalized,) if normalized else ()
    if not isinstance(value, Sequence):
        return ()
    items: list[str] = []
    for item in value:
        normalized = normalize_text(item)
        if normalized:
            items.append(normalized)
    return tuple(items)
