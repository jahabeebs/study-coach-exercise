"""Evaluators for generated practice quizzes.

The deterministic checks cover properties that should not require another
model: the display contract, retrieval provenance, and accidental answer-key
leakage. The semantic judge returns typed, quote-backed evidence for every
option, which is then validated programmatically against each item's own cited
chunk.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from pydantic_evals.evaluators import (  # noqa: E402
    EvaluationReason,
    Evaluator,
    EvaluatorContext,
)

from app.config import get_model_name  # noqa: E402
from app.models import QuizResponse, normalize_quiz_display_text  # noqa: E402
from app.quiz_review import (  # noqa: E402
    QUIZ_EVIDENCE_INSTRUCTIONS,
    QuizEvidence,
    QuizOptionEvidence,
    QuizReviewQuestion,
    quiz_review_agent as quiz_evidence_agent,
    validate_quiz_evidence as _validate_quiz_evidence,
)


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
class QuizAnswerPositionsVaried(Evaluator[str, QuizResponse]):
    """Avoid a learnable answer-position cue within a short quiz."""

    required_positions: frozenset[int] = frozenset(range(4))

    def evaluate(self, ctx: EvaluatorContext[str, QuizResponse]) -> bool:
        positions = {item.correct_index for item in ctx.output.questions}
        return self.required_positions <= positions


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


def _judge_payload(
    ctx: EvaluatorContext[str, QuizResponse],
) -> tuple[list[QuizReviewQuestion], list[str]]:
    """Build isolated per-item payloads and report invalid provenance."""
    output = ctx.output
    errors: list[str] = []
    if len(output.retrieved_section_ids) != len(output.retrieved_chunks):
        return [], ["retrieved section IDs and chunks have different lengths"]
    if len(set(output.retrieved_section_ids)) != len(output.retrieved_section_ids):
        return [], ["retrieved section IDs are not unique"]

    chunks_by_id = dict(
        zip(output.retrieved_section_ids, output.retrieved_chunks, strict=True)
    )
    payload: list[QuizReviewQuestion] = []
    for question_index, item in enumerate(output.questions):
        chunk = chunks_by_id.get(item.citation)
        if chunk is None:
            errors.append(
                f"question {question_index} cites unretrieved section {item.citation!r}"
            )
            continue
        payload.append(
            {
                "question_index": question_index,
                "requested_topic": ctx.inputs,
                "question": item.question,
                "options": item.options,
                "correct_index": item.correct_index,
                "citation": item.citation,
                # Deliberately include only this item's cited excerpt. The
                # application-wide retrieval list is not exposed to the judge.
                "cited_chunk": chunk,
            }
        )
    return payload, errors


@dataclass
class QuizEvidenceJudge(Evaluator[str, QuizResponse]):
    """LLM semantic audit with programmatically verified item-level evidence."""

    async def evaluate(
        self, ctx: EvaluatorContext[str, QuizResponse]
    ) -> EvaluationReason:
        payload, errors = _judge_payload(ctx)
        expected_count = (ctx.metadata or {}).get("expected_question_count", 5)
        if len(payload) != expected_count:
            errors.append(
                f"judge expected {expected_count} grounded question payloads, "
                f"got {len(payload)}"
            )

        evidence: QuizEvidence | None = None
        if not errors:
            result = await quiz_evidence_agent.run(
                json.dumps({"questions": payload}, ensure_ascii=False),
                model=get_model_name(),
            )
            evidence = result.output
            errors.extend(_validate_quiz_evidence(evidence, payload))

        reason = json.dumps(
            {
                "passed": not errors,
                "errors": errors,
                "evidence": evidence.model_dump(mode="json") if evidence else None,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        return EvaluationReason(value=not errors, reason=reason)


def quiz_quality_judge() -> QuizEvidenceJudge:
    """Build the typed, evidence-validating semantic quiz judge."""
    return QuizEvidenceJudge()
