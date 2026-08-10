"""Evaluators for generated practice quizzes.

The deterministic checks cover properties that should not require another
model: the display contract, retrieval provenance, and accidental answer-key
leakage. The judge is reserved for semantic questions such as whether an item
has exactly one course-supported answer.
"""

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from pydantic_evals.evaluators import Evaluator, EvaluatorContext, LLMJudge  # noqa: E402

from app.config import get_model_name  # noqa: E402
from app.models import QuizResponse, normalize_quiz_display_text  # noqa: E402


@dataclass
class QuizShapeValid(Evaluator[str, QuizResponse]):
    """The quiz matches the five-question, four-choice UI contract."""

    def evaluate(self, ctx: EvaluatorContext[str, QuizResponse]) -> bool:
        expected_count = (ctx.metadata or {}).get("expected_question_count", 5)
        questions = ctx.output.questions
        if len(questions) != expected_count:
            return False

        normalized_stems: list[str] = []
        for item in questions:
            stem = normalize_quiz_display_text(item.question)
            options = [normalize_quiz_display_text(option) for option in item.options]
            if not stem or not item.citation.strip():
                return False
            if len(options) != 4 or any(not option for option in options):
                return False
            if len(set(options)) != len(options):
                return False
            if not 0 <= item.correct_index < len(options):
                return False
            normalized_stems.append(stem)

        return len(set(normalized_stems)) == len(normalized_stems)


@dataclass
class QuizCitationsGrounded(Evaluator[str, QuizResponse]):
    """Every item cites a nonempty chunk retrieved during this run."""

    def evaluate(self, ctx: EvaluatorContext[str, QuizResponse]) -> bool:
        out = ctx.output
        section_ids = out.retrieved_section_ids
        chunks = out.retrieved_chunks
        if not section_ids or len(section_ids) != len(chunks):
            return False
        if len(section_ids) != len(set(section_ids)):
            return False
        if any(not section_id.strip() for section_id in section_ids):
            return False
        if any(not chunk.strip() for chunk in chunks):
            return False
        retrieved = set(section_ids)
        return bool(out.questions) and all(
            item.citation in retrieved for item in out.questions
        )


@dataclass
class QuizDoesNotRevealAnswers(Evaluator[str, QuizResponse]):
    """Generated display text must not mark which option is correct."""

    markers: tuple[str, ...] = (
        "✓",
        "✅",
        "☑",
        "[correct]",
        "(correct)",
        "correct answer:",
    )

    def evaluate(self, ctx: EvaluatorContext[str, QuizResponse]) -> bool:
        for item in ctx.output.questions:
            for display_text in (item.question, *item.options):
                normalized = display_text.casefold()
                if any(marker in normalized for marker in self.markers):
                    return False
        return True


def quiz_quality_judge() -> LLMJudge:
    """Judge semantic grounding and whether each item has one valid answer."""
    return LLMJudge(
        rubric=(
            "The input is the student's requested quiz topic. Evaluate every "
            "question using only the output's retrieved course material; the "
            "entries in `retrieved_section_ids` correspond by position to "
            "`retrieved_chunks`. Pass only if every question is relevant to "
            "the requested topic, its own `citation` identifies a retrieved "
            "chunk that supports the question, and the option identified by "
            "`correct_index` is the one answer supported by that cited chunk. "
            "The other three options must not also be correct. Fail the entire "
            "quiz if any item is ambiguous, the indexed answer is wrong, any "
            "claim is unsupported, or an item depends on outside knowledge."
        ),
        model=get_model_name(),
        include_input=True,
    )
