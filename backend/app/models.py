"""Pydantic schemas shared by the API, the agent, and the evals."""

import re
import unicodedata
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, field_validator


NonBlankText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
ChatMessage = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=2000),
]
QuizTopic = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
]


def normalize_quiz_display_text(text: str) -> str:
    """Normalize case, spacing, and punctuation for quiz-text comparisons."""
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(re.sub(r"[\W_]+", " ", normalized).split())


class ChatRequest(BaseModel):
    message: ChatMessage


class StudyAnswer(BaseModel):
    """The agent's structured output."""

    answer: NonBlankText = Field(description="The answer to the student's question.")
    supported: bool = Field(
        description=(
            "True only when retrieved course material directly supports the "
            "answer; false when the assistant must abstain."
        )
    )
    citations: list[str] = Field(
        description=(
            "IDs of the course-material sections that support the answer, "
            "e.g. 'lesson-02-data-and-binary#binary-numbers'. Cite only "
            "sections that were actually retrieved."
        )
    )


class ChatResponse(BaseModel):
    """API response; also the output contract the evals evaluate against.

    `retrieved_section_ids` and `retrieved_chunks` record what the agent's
    tools actually returned during this run, so evaluators can check that
    citations and answer content are grounded in retrieved material.
    """

    answer: str
    citations: list[str]
    retrieved_section_ids: list[str]
    retrieved_chunks: list[str]


class QuizRequest(BaseModel):
    """A student's requested practice-quiz topic."""

    topic: QuizTopic


class QuizQuestion(BaseModel):
    """One multiple-choice item rendered by the existing QuizView."""

    question: NonBlankText
    options: list[NonBlankText] = Field(
        min_length=4,
        max_length=4,
        description="Exactly four answer choices, with no indication of the correct one.",
    )
    correct_index: int = Field(ge=0, le=3)
    citation: NonBlankText = Field(
        description="ID of the retrieved course-material section supporting this item.",
    )

    @field_validator("options")
    @classmethod
    def options_must_be_distinct(cls, options: list[str]) -> list[str]:
        normalized = [normalize_quiz_display_text(option) for option in options]
        if any(not option for option in normalized):
            raise ValueError("answer choices must contain letters or numbers")
        if len(set(normalized)) != len(options):
            raise ValueError("answer choices must be distinct")
        return options


class QuizResponse(BaseModel):
    """Generated quiz plus the retrieval evidence used by the evals."""

    topic: QuizTopic
    questions: list[QuizQuestion] = Field(
        min_length=5,
        max_length=5,
        description="Five multiple-choice questions about the requested topic.",
    )
    retrieved_section_ids: list[str]
    retrieved_chunks: list[str]


class SuggestResponse(BaseModel):
    section_id: str
    title: str
    source_file: str
