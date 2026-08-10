"""Evaluators for the hard suite (senior Part 3).

These were written in a hurry by the previous engineer and are used to score
the `--suite hard` run. Read them carefully before you trust their verdicts.
"""

import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from pydantic_evals.evaluators import Evaluator, EvaluatorContext  # noqa: E402

from app.models import ChatResponse  # noqa: E402


_WORD = re.compile(r"[a-z0-9]+")


@dataclass
class AnswerMentionsFact(Evaluator[str, ChatResponse]):
    """Checks the answer for an accepted fact without substring false positives."""

    def evaluate(self, ctx: EvaluatorContext[str, ChatResponse]) -> bool:
        keywords = (ctx.metadata or {}).get("answer_keywords", [])
        answer_tokens = _fact_tokens(ctx.output.answer)
        return any(_matches_keyword(answer_tokens, keyword) for keyword in keywords)


def _fact_tokens(text: str) -> list[str]:
    """Normalize prose while keeping numeric tokens separate and exact."""
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = re.sub(r"(?<=\d),(?=\d)", "", normalized)
    return [token for token in _WORD.findall(normalized) if token]


def _matches_keyword(answer_tokens: list[str], keyword: str) -> bool:
    """Match phrases exactly and allow an intentional one-word text stem.

    Numeric tokens are compared as whole tokens, so ``65`` cannot match
    ``165``. A single alphabetic keyword may be a documented stem such as
    ``doubl`` and therefore matches ``double``, ``doubled``, or ``doubling``.
    """
    keyword_tokens = _fact_tokens(str(keyword))
    if not keyword_tokens:
        return False
    if len(keyword_tokens) == 1 and keyword_tokens[0].isalpha():
        stem = keyword_tokens[0]
        return any(token.startswith(stem) for token in answer_tokens)

    width = len(keyword_tokens)
    return any(
        answer_tokens[index : index + width] == keyword_tokens
        for index in range(len(answer_tokens) - width + 1)
    )
