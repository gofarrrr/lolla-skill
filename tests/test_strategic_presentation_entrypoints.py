from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_public_entrypoints_share_the_product_contract() -> None:
    readme = _text(README_PATH)
    how_it_works = _text(HOW_IT_WORKS_PATH)

    assert "A reasoning-pressure layer for serious AI conversations." in readme
    assert "Lolla slows down the moment a fluent AI answer starts to feel like certainty." in readme
    assert "preserve → pressure → reconsider → record" in readme

    for expected in (
        "The graph introduces pressure; it does not certify relevance.",
        "The receipt proves what process occurred, not that the result is wise.",
        "The human owns the decision and its consequences.",
    ):
        assert expected in how_it_works


def test_public_entrypoints_link_to_dedicated_history_and_evaluation_indexes() -> None:
    for path in (README_PATH, HOW_IT_WORKS_PATH):
        text = _text(path)
        assert "docs/board/README.md" in text
        assert "docs/evals/README.md" in text


def test_public_entrypoints_do_not_duplicate_the_historical_milestone_catalog() -> None:
    historical_milestone = "Decision Work Generated Read Brief Rendering Pilot"

    assert historical_milestone not in _text(README_PATH)
    assert historical_milestone not in _text(HOW_IT_WORKS_PATH)
