import sys
from pathlib import Path

import pytest
from pydantic_evals.evaluators import EvaluatorContext

EVALS_DIR = Path(__file__).resolve().parents[2] / "evals"
sys.path.insert(0, str(EVALS_DIR))

from app.models import ChatResponse  # noqa: E402
from hard_dataset import build_hard_dataset  # noqa: E402
from hard_evaluators import AnswerMentionsFact  # noqa: E402


def _context(
    answer: str,
    *,
    keywords: list[str],
    citations: list[str] | None = None,
) -> EvaluatorContext:
    citations = citations or []
    return EvaluatorContext(
        name="synthetic",
        inputs="synthetic question",
        metadata={"answer_keywords": keywords},
        expected_output=None,
        output=ChatResponse(
            answer=answer,
            citations=citations,
            retrieved_section_ids=citations,
            retrieved_chunks=["synthetic evidence"] * len(citations),
        ),
        duration=0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


@pytest.mark.parametrize(
    ("answer", "keywords"),
    [
        ("1945", ["1945"]),
        ("A byte represents 256 distinct values.", ["256"]),
        ("The count doubled roughly every two years.", ["doubl"]),
        ("A pixel can represent about 16.7 million colors.", ["16.7"]),
        ("A pixel can represent 16777216 colors.", ["16,777,216"]),
    ],
)
def test_fact_evaluator_accepts_concise_and_normalized_correct_answers(
    answer, keywords
):
    assert AnswerMentionsFact().evaluate(_context(answer, keywords=keywords))


@pytest.mark.parametrize(
    ("answer", "keywords", "citations"),
    [
        (
            "This is a long response that never states which component replaced tubes.",
            ["transistor"],
            ["lesson-01#transistor"],
        ),
        ("The old text standard used 165 for capital A.", ["65"], []),
        ("This answer is comfortably longer than fifteen characters.", ["128"], []),
    ],
)
def test_fact_evaluator_rejects_slug_only_numeric_substrings_and_long_nonsense(
    answer, keywords, citations
):
    assert not AnswerMentionsFact().evaluate(
        _context(answer, keywords=keywords, citations=citations)
    )


def test_hard_suite_uses_only_meaningful_signals():
    evaluator_names = {
        type(evaluator).__name__ for evaluator in build_hard_dataset().evaluators
    }
    assert evaluator_names == {
        "CitationsGrounded",
        "ExpectedSectionCited",
        "AnswerMentionsFact",
    }
