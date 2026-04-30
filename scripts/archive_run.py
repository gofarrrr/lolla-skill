#!/usr/bin/env python3
"""Archive a completed Lolla run from /tmp into the long-term runs directory.

Reads the run's core artifacts from /tmp/lolla_{RUN_ID}_*, computes a case
fingerprint from extraction.decision_situation, finds or creates the matching
case folder under the archive root, and copies the artifacts in.

Case matching (the "which case is this?" problem):
- Fingerprint = decision_situation first 120 chars, lowercased, stripped of
  punctuation, whitespace collapsed. Same conversation → same fingerprint.
- Each case folder has .case-manifest.json with the canonical fingerprint(s).
- Matching scans MANIFESTS, not folder names — user renames of case folders
  do not break matching.
- First run of a new case auto-creates the folder with a slug derived from
  the first few significant words of decision_situation.
- $LOLLA_CASE_ID override: if set, archive into that exact folder name
  (sanitized), skipping fingerprint match. The new fingerprint is added to
  the folder's manifest as an alias.

Archive root: $LOLLA_ARCHIVE_DIR or ~/.local/share/lolla/runs/

Files archived (8 core):
  conversation.txt, extraction.json, result.json, revised.txt, memo.md,
  memo_note.json, gapcheck.txt, gapcheck_lanes.json. Missing files are skipped gracefully
  (e.g., if Step 6b was not executed by a weaker orchestrator).

Orchestrator scratch files (preamble.json, lane*.json) are NOT archived
— they are regenerable from result.json if ever needed.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import sys
from pathlib import Path

DEFAULT_ARCHIVE_ROOT = Path.home() / ".local" / "share" / "lolla" / "runs"

# Files to archive, in order. Missing files are skipped.
CORE_FILES = (
    "conversation.txt",
    "extraction.json",
    "result.json",
    "revised.txt",
    "memo.md",
    "memo_note.json",
    "gapcheck.txt",
    "gapcheck_lanes.json",
)

# Stopwords dropped when generating an auto-slug from decision_situation.
# Keep this list small — we want readable slugs, not semantic stripping.
_STOPWORDS = frozenset({
    "a", "an", "and", "the", "of", "to", "in", "on", "for", "with", "is",
    "are", "was", "were", "be", "been", "being", "or", "but", "if", "then",
    "else", "when", "where", "what", "which", "who", "how", "why", "that",
    "this", "these", "those", "there", "at", "by", "from", "up", "down",
    "over", "under", "it", "its", "his", "her", "their",
    "whether", "should", "would", "could", "significant",
})

_RUN_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


# ---------------------------------------------------------------------------
# Fingerprint + slug helpers
# ---------------------------------------------------------------------------

def _normalize_fingerprint(text: str) -> str:
    """Normalize decision_situation into a stable case fingerprint.

    Lowercase, strip non-alphanumeric to spaces, collapse whitespace, take
    first 120 chars. Two runs with the same decision_situation produce the
    same fingerprint even if the raw text has minor punctuation differences.
    """
    text = (text or "").lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:120]


def _auto_slug(decision_situation: str, max_words: int = 4) -> str:
    """Generate a readable folder slug from decision_situation.

    Drops stopwords, keeps first N significant words, joins with hyphens.
    E.g., "Whether to grant significant equity (15%), partnership status..."
    → ``grant-equity-partnership-status``.
    """
    text = (decision_situation or "").lower()
    text = re.sub(r"[^\w\s]", " ", text)
    words = text.split()
    significant = [w for w in words if w not in _STOPWORDS and len(w) >= 3]
    picked = significant[:max_words] or (words[:max_words] or ["untagged"])
    slug = "-".join(picked)
    return _sanitize_folder(slug)


def _sanitize_folder(name: str) -> str:
    """Make a string safe as a folder name (alphanumeric + hyphen only)."""
    name = re.sub(r"[^\w-]", "-", (name or "").lower())
    name = re.sub(r"-+", "-", name).strip("-")
    return name[:60] or "untagged"


# ---------------------------------------------------------------------------
# Case discovery + manifest
# ---------------------------------------------------------------------------

def _token_jaccard(a: str, b: str) -> float:
    """Token-set Jaccard similarity. Handles extractor paraphrase drift that
    exact-text matching misses (same decision rephrased slightly = same case)."""
    tokens_a = set(a.split())
    tokens_b = set(b.split())
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


# Token-set Jaccard threshold for considering two fingerprints the same case.
# 0.80 was calibrated against observed drift on Marcus runs: two extractions
# of the same conversation produced fingerprints with 17/21 shared tokens
# (Jaccard 0.81). Drop below 0.80 only if drift is larger than that in practice.
FINGERPRINT_MATCH_THRESHOLD = 0.80


def _find_matching_case(archive_root: Path, fingerprint: str) -> Path | None:
    """Scan case folders' manifests for a fingerprint match.

    Matches in two stages:
      1. Exact — fingerprint present in manifest.fingerprints[].
      2. Fuzzy — token-set Jaccard ≥ FINGERPRINT_MATCH_THRESHOLD against any
         stored fingerprint. Handles extractor paraphrase drift.

    Returns the matching case folder, or None if no case is similar enough.
    """
    if not fingerprint or not archive_root.exists():
        return None
    for case_dir in sorted(archive_root.iterdir()):
        if not case_dir.is_dir():
            continue
        manifest_path = case_dir / ".case-manifest.json"
        if not manifest_path.exists():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        fingerprints = list(manifest.get("fingerprints") or [])
        # Back-compat: older manifests might have a single "fingerprint" key.
        legacy = manifest.get("fingerprint")
        if legacy and legacy not in fingerprints:
            fingerprints.append(legacy)

        # Stage 1: exact match
        if fingerprint in fingerprints:
            return case_dir
        # Stage 2: fuzzy (token-set Jaccard)
        for stored in fingerprints:
            if _token_jaccard(fingerprint, stored) >= FINGERPRINT_MATCH_THRESHOLD:
                return case_dir
    return None


def _write_manifest(
    case_dir: Path,
    fingerprint: str,
    run_id: str,
) -> dict:
    """Create or update the case manifest. Returns the written manifest dict."""
    manifest_path = case_dir / ".case-manifest.json"
    now_iso = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            manifest = {}
    else:
        manifest = {}

    # Initialize fields for fresh manifest
    manifest.setdefault("case_id", case_dir.name)
    manifest.setdefault("created_at", now_iso)
    manifest.setdefault("first_run_id", run_id)
    manifest.setdefault("fingerprints", [])
    manifest.setdefault("runs", [])

    # Migrate legacy single-fingerprint field if present
    if "fingerprint" in manifest and manifest.get("fingerprint"):
        legacy = manifest.pop("fingerprint")
        if legacy not in manifest["fingerprints"]:
            manifest["fingerprints"].append(legacy)

    if fingerprint and fingerprint not in manifest["fingerprints"]:
        manifest["fingerprints"].append(fingerprint)
    if run_id not in manifest["runs"]:
        manifest["runs"].append(run_id)

    # Always refresh these fields (track latest state + folder renames)
    manifest["case_id"] = case_dir.name
    manifest["last_run_id"] = run_id
    manifest["last_archived_at"] = now_iso
    manifest["run_count"] = len(manifest["runs"])

    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    return manifest


# ---------------------------------------------------------------------------
# Main archival routine
# ---------------------------------------------------------------------------

def archive_run(
    run_id: str,
    archive_root: Path = DEFAULT_ARCHIVE_ROOT,
    tmp_dir: Path = Path("/tmp"),
    override_case_id: str | None = None,
) -> dict:
    """Archive a completed run. Returns a result dict describing what happened.

    Raises:
        ValueError: run_id is not safe as a folder component.
        FileNotFoundError: extraction.json is missing — can't fingerprint.
    """
    if not _RUN_ID_RE.match(run_id):
        raise ValueError(
            f"Invalid run_id: {run_id!r}. Expected alphanumeric + underscore/hyphen only."
        )

    extraction_path = tmp_dir / f"lolla_{run_id}_extraction.json"
    if not extraction_path.exists():
        raise FileNotFoundError(
            f"Extraction not found at {extraction_path}. "
            f"Cannot archive without decision_situation — did extraction complete?"
        )

    extraction_json = json.loads(extraction_path.read_text(encoding="utf-8"))
    decision_situation = (
        extraction_json.get("extraction", {}).get("decision_situation", "") or ""
    )
    fingerprint = _normalize_fingerprint(decision_situation)

    archive_root.mkdir(parents=True, exist_ok=True)

    # Resolve case folder: explicit override → existing fingerprint match → new case.
    if override_case_id:
        case_dir = archive_root / _sanitize_folder(override_case_id)
        case_dir.mkdir(exist_ok=True)
        how_matched = "env_override"
    else:
        matched = _find_matching_case(archive_root, fingerprint)
        if matched is not None:
            case_dir = matched
            how_matched = "fingerprint_match"
        else:
            slug = _auto_slug(decision_situation)
            # Prevent collisions with unrelated cases that happened to slug the same way.
            base, suffix = slug, 1
            while (archive_root / slug).exists():
                slug = f"{base}-{suffix}"
                suffix += 1
            case_dir = archive_root / slug
            case_dir.mkdir()
            how_matched = "new_case"

    run_dir = case_dir / run_id
    run_dir.mkdir(exist_ok=True)

    copied: list[str] = []
    missing: list[str] = []
    for fname in CORE_FILES:
        src = tmp_dir / f"lolla_{run_id}_{fname}"
        if src.exists():
            shutil.copy2(src, run_dir / fname)
            copied.append(fname)
        else:
            missing.append(fname)

    manifest = _write_manifest(case_dir, fingerprint, run_id)

    return {
        "case_dir": str(case_dir),
        "run_dir": str(run_dir),
        "case_id": case_dir.name,
        "how_matched": how_matched,
        "fingerprint": fingerprint,
        "files_copied": copied,
        "files_missing": missing,
        "run_count": manifest["run_count"],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--run-id", required=True, help="Run ID (e.g., 20260422T155622Z)")
    ap.add_argument(
        "--archive-root", default=None,
        help=(
            "Override archive root. Falls back to $LOLLA_ARCHIVE_DIR, then "
            f"{DEFAULT_ARCHIVE_ROOT}."
        ),
    )
    ap.add_argument(
        "--case-id", default=None,
        help=(
            "Force a specific case folder name (skips fingerprint match). "
            "Falls back to $LOLLA_CASE_ID if unset."
        ),
    )
    ap.add_argument("--quiet", action="store_true", help="Only print errors.")
    args = ap.parse_args()

    if args.archive_root:
        archive_root = Path(args.archive_root).expanduser()
    elif os.environ.get("LOLLA_ARCHIVE_DIR"):
        archive_root = Path(os.environ["LOLLA_ARCHIVE_DIR"]).expanduser()
    else:
        archive_root = DEFAULT_ARCHIVE_ROOT

    override = args.case_id or os.environ.get("LOLLA_CASE_ID") or None

    try:
        result = archive_run(args.run_id, archive_root, override_case_id=override)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Archive failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Archive failed (unexpected): {exc}", file=sys.stderr)
        return 1

    if args.quiet:
        return 0

    print(f"Archived run {args.run_id}")
    print(f"  case:   {result['case_id']} ({result['how_matched']}; {result['run_count']} runs total)")
    print(f"  path:   {result['run_dir']}")
    print(f"  files:  {len(result['files_copied'])} copied"
          + (f", {len(result['files_missing'])} missing" if result['files_missing'] else ""))
    if result['files_missing']:
        print(f"  missing: {', '.join(result['files_missing'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
