"""Tests for Bullshit Index partial-failure observability."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.bullshit_index import evaluate_passage  # noqa: E402


class _EmptyBoundary:
    def run_json_with_metadata(self, *args, **kwargs):  # noqa: ANN002, ANN003
        return {}, object()


class _FailingBoundary:
    def run_json_with_metadata(self, *args, **kwargs):  # noqa: ANN002, ANN003
        raise RuntimeError("connection reset")


def test_empty_bi_result_records_evaluation_error():
    result = evaluate_passage("This is a passage.", _EmptyBoundary())

    assert result.evaluation_error == "empty_result"


def test_failed_bi_result_records_evaluation_error():
    result = evaluate_passage("This is a passage.", _FailingBoundary())

    assert "connection reset" in result.evaluation_error
