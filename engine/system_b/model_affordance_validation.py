from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable


ALLOWED_STATUS = frozenset(
    {
        "supported",
        "weak_support",
        "not_supported_by_source",
        "source_too_thin",
        "duplicate_of_existing_field",
        "deferred_for_review",
    }
)
ABSENCE_STATUS = frozenset({"not_supported_by_source", "source_too_thin"})
ALLOWED_CONFIDENCE = frozenset({"high", "medium", "weak", "not_applicable"})
ALLOWED_EXTRACTION_TYPE = frozenset(
    {"explicit", "normalized", "not_supported_by_source", "review_note"}
)
ALLOWED_RUNTIME_POLICY = frozenset(
    {"do_not_promote", "observatory_only", "defer_for_review", "available_for_review"}
)
MIN_AFFORDANCE_NAME_LENGTH = 24
MIN_AFFORDANCE_MECHANISM_LENGTH = 40
TOP_LEVEL_FIELDS = frozenset(
    {
        "model_id",
        "source_file",
        "status",
        "affordances",
        "absence_records",
        "source_evidence",
        "review_notes",
    }
)
AFFORDANCE_FIELDS = frozenset(
    {
        "affordance_id",
        "status",
        "name",
        "mechanism",
        "activation_shape",
        "treatment_requirements",
        "diagnostic_questions",
        "misuse_guards",
        "source_evidence",
        "confidence",
        "review_notes",
    }
)
ACTIVATION_SHAPE_FIELDS = frozenset(
    {"use_when", "do_not_use_when", "case_evidence_needed"}
)
TREATMENT_FIELDS = frozenset(
    {"requirement_id", "description", "evidence_required", "good_output_shape"}
)
EVIDENCE_FIELDS = frozenset(
    {"source_file", "source_quote", "section_hint", "extraction_type", "confidence"}
)
ABSENCE_FIELDS = frozenset(
    {"attempted_field", "status", "reason", "runtime_policy", "source_evidence"}
)
REVIEW_NOTE_FIELDS = frozenset(
    {"normalization_note", "dropped_material", "open_questions", "review_status"}
)
GENERIC_FRAGMENTS = (
    "careful thinking",
    "think more carefully",
    "think carefully",
    "consider the problem",
    "consider the risks",
    "use this model",
    "apply this model",
    "analyze the situation",
    "make a better decision",
    "improve the reasoning",
    "look at the bigger picture",
    "be more thoughtful",
)
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
AFFORDANCE_ID_RE = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+(?:-[a-z0-9]+)*)+$"
)
SOURCE_FILE_RE = re.compile(r"^[A-Za-z0-9_\- ]+\.md$")


class ModelAffordanceValidationError(ValueError):
    pass


def load_model_affordance_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ModelAffordanceValidationError(f"{path}: payload must be an object")
    return payload


def validate_model_affordance_file(
    path: Path,
    *,
    source_roots: Iterable[Path] = (),
) -> None:
    validate_model_affordance_payload(
        load_model_affordance_payload(path),
        path=Path(path),
        source_roots=source_roots,
    )


def validate_model_affordance_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    source_roots: Iterable[Path] = (),
) -> None:
    errors = list(
        iter_model_affordance_errors(payload, path=Path(path), source_roots=source_roots)
    )
    if errors:
        raise ModelAffordanceValidationError("; ".join(errors))


def iter_model_affordance_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    source_roots: Iterable[Path] = (),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return

    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    required = (
        "model_id",
        "source_file",
        "status",
        "affordances",
        "absence_records",
        "source_evidence",
        "review_notes",
    )
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    model_id = _string(payload.get("model_id"))
    if not SLUG_RE.match(model_id):
        yield f"{path}: model_id must be a lowercase slug"

    source_file = _string(payload.get("source_file"))
    if not SOURCE_FILE_RE.match(source_file):
        yield f"{path}: source_file must be a markdown filename"

    status = _string(payload.get("status"))
    if status not in ALLOWED_STATUS:
        yield f"{path}: unknown status '{status}'"

    affordances = payload.get("affordances")
    if not isinstance(affordances, list):
        yield f"{path}: affordances must be a list"
        affordances = []

    absence_records = payload.get("absence_records")
    if not isinstance(absence_records, list):
        yield f"{path}: absence_records must be a list"
        absence_records = []

    if status in ABSENCE_STATUS and affordances:
        yield f"{path}: status '{status}' must not carry affordances"

    if status in {"supported", "weak_support"} and not affordances and not absence_records:
        yield (
            f"{path}: {status} record with zero affordances needs an explicit "
            "absence record"
        )

    evidence_cache: dict[str, str | None] = {}
    yield from _validate_evidence_list(
        payload.get("source_evidence"),
        path=path / "source_evidence",
        source_roots=source_roots,
        evidence_cache=evidence_cache,
    )
    yield from _validate_review_notes(payload.get("review_notes"), path=path / "review_notes")

    seen_affordance_ids: set[str] = set()
    for index, affordance in enumerate(affordances):
        item_path = path / f"affordances[{index}]"
        if not isinstance(affordance, dict):
            yield f"{item_path}: affordance must be an object"
            continue
        affordance_id = _string(affordance.get("affordance_id"))
        if affordance_id and not affordance_id.startswith(f"{model_id}."):
            yield f"{item_path}: affordance_id must start with model_id '{model_id}.'"
        if affordance_id in seen_affordance_ids:
            yield f"{item_path}: duplicate affordance_id '{affordance_id}'"
        seen_affordance_ids.add(affordance_id)
        yield from _validate_affordance(
            affordance,
            path=item_path,
            source_roots=source_roots,
            evidence_cache=evidence_cache,
        )

    for index, absence in enumerate(absence_records):
        item_path = path / f"absence_records[{index}]"
        if not isinstance(absence, dict):
            yield f"{item_path}: absence record must be an object"
            continue
        yield from _validate_absence_record(
            absence,
            path=item_path,
            source_roots=source_roots,
            evidence_cache=evidence_cache,
        )


def _validate_affordance(
    affordance: dict[str, object],
    *,
    path: Path,
    source_roots: Iterable[Path],
    evidence_cache: dict[str, str | None],
) -> Iterable[str]:
    required = (
        "affordance_id",
        "status",
        "name",
        "mechanism",
        "activation_shape",
        "treatment_requirements",
        "diagnostic_questions",
        "misuse_guards",
        "source_evidence",
        "confidence",
    )
    yield from _unknown_fields(affordance, AFFORDANCE_FIELDS, path)
    yield from _missing_fields(affordance, required, path)
    if any(field not in affordance for field in required):
        return

    affordance_id = _string(affordance.get("affordance_id"))
    if not AFFORDANCE_ID_RE.match(affordance_id):
        yield f"{path}: affordance_id must be '<model-id>.<slug>'"

    status = _string(affordance.get("status"))
    if status not in ALLOWED_STATUS:
        yield f"{path}: unknown status '{status}'"
    if status in ABSENCE_STATUS:
        yield f"{path}: absence status belongs in absence_records, not affordances"

    for field in ("name", "mechanism"):
        text = _string(affordance.get(field))
        if not text:
            yield f"{path}: {field} must be a non-empty string"
        if field == "name" and len(text) < MIN_AFFORDANCE_NAME_LENGTH:
            yield (
                f"{path}: name must be at least "
                f"{MIN_AFFORDANCE_NAME_LENGTH} characters"
            )
        if field == "mechanism" and len(text) < MIN_AFFORDANCE_MECHANISM_LENGTH:
            yield (
                f"{path}: mechanism must be at least "
                f"{MIN_AFFORDANCE_MECHANISM_LENGTH} characters"
            )
        yield from _boilerplate_phrase_errors(text, path=path / field)

    activation = affordance.get("activation_shape")
    if not isinstance(activation, dict):
        yield f"{path}: activation_shape must be an object"
    else:
        yield from _unknown_fields(activation, ACTIVATION_SHAPE_FIELDS, path / "activation_shape")
        for field in ("use_when", "do_not_use_when", "case_evidence_needed"):
            yield from _validate_string_list(
                activation.get(field),
                path=path / f"activation_shape.{field}",
            )

    treatments = affordance.get("treatment_requirements")
    if not isinstance(treatments, list) or not treatments:
        yield f"{path}: treatment_requirements must be a non-empty list"
    else:
        seen_requirement_ids: set[str] = set()
        for index, treatment in enumerate(treatments):
            item_path = path / f"treatment_requirements[{index}]"
            if not isinstance(treatment, dict):
                yield f"{item_path}: treatment requirement must be an object"
                continue
            yield from _unknown_fields(treatment, TREATMENT_FIELDS, item_path)
            yield from _missing_fields(
                treatment,
                ("requirement_id", "description", "evidence_required", "good_output_shape"),
                item_path,
            )
            requirement_id = _string(treatment.get("requirement_id"))
            if requirement_id in seen_requirement_ids:
                yield f"{item_path}: duplicate requirement_id '{requirement_id}'"
            seen_requirement_ids.add(requirement_id)
            if not SLUG_RE.match(requirement_id):
                yield f"{item_path}: requirement_id must be a lowercase slug"
            yield from _validate_string_list(
                treatment.get("evidence_required"),
                path=item_path / "evidence_required",
            )
            yield from _validate_string_list(
                treatment.get("good_output_shape"),
                path=item_path / "good_output_shape",
            )

    for field in ("diagnostic_questions", "misuse_guards"):
        yield from _validate_string_list(affordance.get(field), path=path / field)

    evidence = affordance.get("source_evidence")
    if not isinstance(evidence, list) or not evidence:
        yield f"{path}: source_evidence must be a non-empty list"
    else:
        yield from _validate_evidence_list(
            evidence,
            path=path / "source_evidence",
            source_roots=source_roots,
            evidence_cache=evidence_cache,
        )

    confidence = _string(affordance.get("confidence"))
    if confidence not in ALLOWED_CONFIDENCE:
        yield f"{path}: unknown confidence '{confidence}'"

    if "review_notes" in affordance:
        yield from _validate_review_notes(
            affordance.get("review_notes"), path=path / "review_notes"
        )


def _validate_absence_record(
    absence: dict[str, object],
    *,
    path: Path,
    source_roots: Iterable[Path],
    evidence_cache: dict[str, str | None],
) -> Iterable[str]:
    yield from _unknown_fields(absence, ABSENCE_FIELDS, path)
    yield from _missing_fields(absence, ("attempted_field", "status", "reason", "runtime_policy"), path)
    status = _string(absence.get("status"))
    if status not in ALLOWED_STATUS:
        yield f"{path}: unknown status '{status}'"
    if status == "supported":
        yield f"{path}: absence record status cannot be supported"
    if _string(absence.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path}: unknown runtime_policy '{_string(absence.get('runtime_policy'))}'"
    if len(_string(absence.get("reason"))) < 20:
        yield f"{path}: reason must explain the absence"
    if "source_evidence" in absence:
        yield from _validate_evidence_list(
            absence.get("source_evidence"),
            path=path / "source_evidence",
            source_roots=source_roots,
            evidence_cache=evidence_cache,
        )


def _validate_evidence_list(
    evidence_list: object,
    *,
    path: Path,
    source_roots: Iterable[Path],
    evidence_cache: dict[str, str | None],
) -> Iterable[str]:
    if not isinstance(evidence_list, list):
        yield f"{path}: source_evidence must be a list"
        return
    for index, evidence in enumerate(evidence_list):
        item_path = path / f"[{index}]"
        if not isinstance(evidence, dict):
            yield f"{item_path}: source evidence must be an object"
            continue
        yield from _unknown_fields(evidence, EVIDENCE_FIELDS, item_path)
        yield from _missing_fields(
            evidence,
            ("source_file", "source_quote", "section_hint", "extraction_type", "confidence"),
            item_path,
        )
        source_file = _string(evidence.get("source_file"))
        source_quote = _string(evidence.get("source_quote"))
        if not SOURCE_FILE_RE.match(source_file):
            yield f"{item_path}: source_file must be a markdown filename"
        if len(source_quote) < 8:
            yield f"{item_path}: source_quote must be a meaningful exact quote"
        if _string(evidence.get("extraction_type")) not in ALLOWED_EXTRACTION_TYPE:
            yield f"{item_path}: unknown extraction_type '{_string(evidence.get('extraction_type'))}'"
        if _string(evidence.get("confidence")) not in ALLOWED_CONFIDENCE:
            yield f"{item_path}: unknown confidence '{_string(evidence.get('confidence'))}'"
        if source_file and source_quote and source_roots:
            source_text = _source_text_for(source_file, source_roots, evidence_cache)
            if source_text is None:
                yield f"{item_path}: source file not found under source_roots: {source_file}"
            elif source_quote not in source_text:
                yield f"{item_path}: source_quote is not an exact substring of {source_file}"


def _validate_review_notes(notes: object, *, path: Path) -> Iterable[str]:
    if not isinstance(notes, dict):
        yield f"{path}: review_notes must be an object"
        return
    yield from _unknown_fields(notes, REVIEW_NOTE_FIELDS, path)
    for field in ("dropped_material", "open_questions"):
        if field in notes and not isinstance(notes[field], list):
            yield f"{path}: {field} must be a list"
    if "review_status" in notes and _string(notes["review_status"]) not in {
        "fixture",
        "draft",
        "reviewed",
        "needs_review",
    }:
        yield f"{path}: unknown review_status '{_string(notes['review_status'])}'"


def _source_text_for(
    source_file: str,
    source_roots: Iterable[Path],
    evidence_cache: dict[str, str | None],
) -> str | None:
    if source_file in evidence_cache:
        return evidence_cache[source_file]
    for root in source_roots:
        candidate = Path(root) / source_file
        if candidate.exists():
            text = candidate.read_text(encoding="utf-8")
            evidence_cache[source_file] = text
            return text
    evidence_cache[source_file] = None
    return None


def _validate_string_list(value: object, *, path: Path) -> Iterable[str]:
    if not isinstance(value, list) or not value:
        yield f"{path}: must be a non-empty list"
        return
    for index, item in enumerate(value):
        text = _string(item)
        if len(text) < 8:
            yield f"{path}[{index}]: must be a meaningful string"


def _boilerplate_phrase_errors(text: str, *, path: Path) -> Iterable[str]:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    if not normalized:
        return
    for fragment in GENERIC_FRAGMENTS:
        if fragment in normalized:
            yield f"{path}: generic boilerplate is not a valid affordance field"


def _missing_fields(
    payload: dict[str, object],
    required: tuple[str, ...],
    path: Path,
) -> Iterable[str]:
    missing = [field for field in required if field not in payload]
    if missing:
        yield f"{path}: missing required fields: {', '.join(missing)}"


def _unknown_fields(
    payload: dict[str, object],
    allowed: frozenset[str],
    path: Path,
) -> Iterable[str]:
    unknown = sorted(set(payload).difference(allowed))
    if unknown:
        yield f"{path}: unknown fields: {', '.join(unknown)}"


def _string(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""
