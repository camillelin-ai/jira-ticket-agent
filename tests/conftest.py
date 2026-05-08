import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sprint_2026_19_text():
    return (FIXTURES / "sprint_2026_19.txt").read_text()


@pytest.fixture
def sprint_2026_17_text():
    return (FIXTURES / "sprint_2026_17.txt").read_text()


@pytest.fixture
def full_doc_text(sprint_2026_19_text, sprint_2026_17_text):
    """Simulate a doc with multiple sprint sections (later sprints appear first)."""
    return sprint_2026_19_text + "\n\n" + sprint_2026_17_text
