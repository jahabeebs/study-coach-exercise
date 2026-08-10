"""Evaluators for the hard suite (senior Part 3).

These were written in a hurry by the previous engineer and are used to score
the `--suite hard` run. Read them carefully before you trust their verdicts.
"""

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from pydantic_evals.evaluators import Evaluator, EvaluatorContext  # noqa: E402

from app.models import ChatResponse  # noqa: E402
from fact_matching import answer_satisfies_facts  # noqa: E402


@dataclass
class AnswerMentionsFact(Evaluator[str, ChatResponse]):
    """Checks the answer for an accepted fact without substring false positives."""

    def evaluate(self, ctx: EvaluatorContext[str, ChatResponse]) -> bool:
        return answer_satisfies_facts(ctx.output.answer, ctx.metadata)
