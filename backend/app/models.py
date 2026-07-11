"""Pydantic schemas shared by the API, the agent, and the evals."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class StudyAnswer(BaseModel):
    """The agent's structured output."""

    answer: str = Field(description="The answer to the student's question.")
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


class SuggestResponse(BaseModel):
    section_id: str
    title: str
    source_file: str
