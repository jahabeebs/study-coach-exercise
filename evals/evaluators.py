"""Evaluators for Study Coach.

Two kinds, used deliberately:

- Programmatic evaluators check properties that code CAN check — citation
  validity, grounding in what was actually retrieved, presence of known facts.
  They are deterministic: same output in, same verdict out.
- An LLM judge checks the one property code can't: whether the prose of the
  answer is faithful to the retrieved material. The judge sees the retrieved
  chunks (they are part of the task output), not its own world knowledge.
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from pydantic_evals.evaluators import Evaluator, EvaluatorContext, LLMJudge  # noqa: E402

from app.config import get_model_name  # noqa: E402
from app.models import ChatResponse  # noqa: E402
from app.retrieval import _tokenize  # noqa: E402


@dataclass
class CitationsGrounded(Evaluator[str, ChatResponse]):
    """Every citation must name a section the agent actually retrieved.

    This is the tests-vs-evals workhorse: a fabricated citation can look
    perfectly plausible to a reader, but it can never be a member of the
    set of sections the tools returned during this run.
    """

    def evaluate(self, ctx: EvaluatorContext[str, ChatResponse]) -> bool:
        out = ctx.output
        if not out.citations:
            return False
        return set(out.citations) <= set(out.retrieved_section_ids)


@dataclass
class ExpectedSectionCited(Evaluator[str, ChatResponse]):
    """The section that actually answers the question is among the citations."""

    def evaluate(self, ctx: EvaluatorContext[str, ChatResponse]) -> bool:
        expected = (ctx.metadata or {}).get("expected_section")
        return expected in ctx.output.citations if expected else False


@dataclass
class AnswerHasFact(Evaluator[str, ChatResponse]):
    """The answer states the known fact (any accepted phrasing)."""

    def evaluate(self, ctx: EvaluatorContext[str, ChatResponse]) -> bool:
        keywords = (ctx.metadata or {}).get("answer_keywords", [])
        answer = ctx.output.answer.lower()
        return any(k.lower() in answer for k in keywords)


@dataclass
class AnswerGroundedness(Evaluator[str, ChatResponse]):
    """Fraction of the answer's content words that appear in retrieved chunks.

    A score, not an assertion: paraphrase legitimately lowers it. Watch the
    trend, not any single case.
    """

    def evaluate(self, ctx: EvaluatorContext[str, ChatResponse]) -> float:
        answer_words = set(_tokenize(re.sub(r"[^ -~]", " ", ctx.output.answer)))
        if not answer_words:
            return 0.0
        chunk_words = set(_tokenize(" ".join(ctx.output.retrieved_chunks)))
        return len(answer_words & chunk_words) / len(answer_words)


def faithfulness_judge() -> LLMJudge:
    """LLM-as-judge for faithfulness of the prose to the retrieved material."""
    return LLMJudge(
        rubric=(
            "The output's `answer` must be fully supported by the text in the "
            "output's `retrieved_chunks`. It must not state facts that are "
            "absent from those chunks, even if they are true in the real "
            "world. An answer that says the material could not be found is "
            "acceptable only if `retrieved_chunks` genuinely does not answer "
            "the question."
        ),
        model=get_model_name(),
        include_input=True,
    )
