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


@dataclass
class AnswerMentionsFact(Evaluator[str, ChatResponse]):
    """Checks that the expected fact shows up in the response."""

    def evaluate(self, ctx: EvaluatorContext[str, ChatResponse]) -> bool:
        keywords = (ctx.metadata or {}).get("answer_keywords", [])
        haystack = " ".join(ctx.output.citations).lower()
        return any(k.lower() in haystack for k in keywords)


@dataclass
class AnswerIsSubstantial(Evaluator[str, ChatResponse]):
    """Checks that the assistant actually produced a real answer."""

    def evaluate(self, ctx: EvaluatorContext[str, ChatResponse]) -> bool:
        return len(ctx.output.answer.strip()) > 15
