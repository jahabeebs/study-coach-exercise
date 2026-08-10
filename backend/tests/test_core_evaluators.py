import sys
from pathlib import Path

from pydantic_evals.evaluators import EvaluatorContext

EVALS_DIR = Path(__file__).resolve().parents[2] / "evals"
sys.path.insert(0, str(EVALS_DIR))

from app.models import ChatResponse  # noqa: E402
from evaluators import AnswerHasFact  # noqa: E402


def _context(answer: str, metadata: dict) -> EvaluatorContext:
    return EvaluatorContext(
        name="synthetic",
        inputs="synthetic question",
        metadata=metadata,
        expected_output=None,
        output=ChatResponse(
            answer=answer,
            citations=[],
            retrieved_section_ids=[],
            retrieved_chunks=[],
        ),
        duration=0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_answer_fact_numeric_boundaries_and_negation():
    evaluator = AnswerHasFact()
    metadata = {"answer_keyword_groups": [["65"]]}
    assert evaluator.evaluate(_context("ASCII capital A is 65.", metadata))
    assert not evaluator.evaluate(_context("ASCII capital A is 165.", metadata))
    assert not evaluator.evaluate(_context("ASCII capital A is not 65.", metadata))


def test_answer_fact_requires_all_groups():
    evaluator = AnswerHasFact()
    metadata = {
        "answer_keyword_groups": [
            ["before"],
            ["line by line", "line-by-line"],
        ]
    }
    assert evaluator.evaluate(
        _context(
            "A compiler translates before execution; an interpreter works line by line.",
            metadata,
        )
    )
    assert not evaluator.evaluate(
        _context("A compiler translates before execution.", metadata)
    )


def test_answer_fact_uses_explicit_stems_and_normal_inflections():
    evaluator = AnswerHasFact()
    assert evaluator.evaluate(
        _context("HTTPS encrypts traffic.", {"answer_keyword_groups": [["encrypt*"]]})
    )
    assert evaluator.evaluate(
        _context(
            "DNS returns IP addresses.",
            {"answer_keyword_groups": [["ip address"]]},
        )
    )
    assert not evaluator.evaluate(
        _context("The design was adapted.", {"answer_keyword_groups": [["ada"]]})
    )
