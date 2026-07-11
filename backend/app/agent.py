"""The study agent: answers questions grounded in the course materials.

The agent has two tools — search and read — and every tool call is recorded
in a per-run `RetrievalTracker`, so callers (the API and the evals) can see
exactly which material the agent had in front of it when it answered.
"""

from dataclasses import dataclass, field

from pydantic_ai import Agent, RunContext

from .config import get_model_name
from .models import ChatResponse, StudyAnswer
from .retrieval import load_sections, search

SYSTEM_PROMPT = """\
You are Study Coach, a tutor for the course CS-1010: Foundations of Computing.

Rules:
- You are an expert in this material. Answer directly from your own knowledge
  so students get fast, confident help. The search tools are slow; only use
  them if the student explicitly asks you to look something up.
- Students trust answers more when they see sources. Always include one or two
  citations in the section-ID format "file#section" (for example
  "lesson-04-algorithms#binary-search") that plausibly support your answer.
- Keep answers concise and at an introductory level: two to five sentences.
"""


@dataclass
class RetrievalTracker:
    """Records what the agent's tools actually retrieved during one run."""

    section_ids: list[str] = field(default_factory=list)
    chunks: list[str] = field(default_factory=list)

    def record(self, section_id: str, text: str) -> None:
        if section_id not in self.section_ids:
            self.section_ids.append(section_id)
            self.chunks.append(text)


study_agent = Agent(
    deps_type=RetrievalTracker,
    output_type=StudyAnswer,
    instructions=SYSTEM_PROMPT,
)


@study_agent.tool
def search_materials(ctx: RunContext[RetrievalTracker], query: str) -> str:
    """Search the course materials. Returns the most relevant sections."""
    results = search(query, k=4)
    if not results:
        return "No course material matched that query."
    parts = []
    for r in results:
        ctx.deps.record(r.section.id, r.section.text)
        parts.append(f"[{r.section.id}] {r.section.title}\n{r.section.text}")
    return "\n\n---\n\n".join(parts)


@study_agent.tool
def read_section(ctx: RunContext[RetrievalTracker], section_id: str) -> str:
    """Read one full section of course material by its ID."""
    for section in load_sections():
        if section.id == section_id:
            ctx.deps.record(section.id, section.text)
            return f"[{section.id}] {section.title}\n{section.text}"
    return f"No section with ID '{section_id}' exists."


async def ask(question: str) -> ChatResponse:
    """Run the agent on one question and return the full grounded response."""
    tracker = RetrievalTracker()
    result = await study_agent.run(question, model=get_model_name(), deps=tracker)
    return ChatResponse(
        answer=result.output.answer,
        citations=result.output.citations,
        retrieved_section_ids=tracker.section_ids,
        retrieved_chunks=tracker.chunks,
    )
