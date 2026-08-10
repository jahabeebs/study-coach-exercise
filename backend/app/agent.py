"""The study agent: answers questions grounded in the course materials.

The agent has two tools — search and read — and every tool call is recorded
in a per-run `RetrievalTracker`, so callers (the API and the evals) can see
exactly which material the agent had in front of it when it answered.
"""

from dataclasses import dataclass, field

from pydantic_ai import Agent, ModelRetry, RunContext

from .config import get_model_name
from .models import ChatResponse, StudyAnswer
from .retrieval import load_sections, search

SYSTEM_PROMPT = """\
You are Study Coach, a tutor for the course CS-1010: Foundations of Computing.

Rules:
- Search the course materials before answering every course-content question.
- You may use your own knowledge to translate casual wording into useful
  search terms, but never use it as evidence for an answer.
- If the first search results do not answer the question, reformulate the
  query and search again or read a likely section.
- Answer only from text returned by the tools. Cite one or two exact section
  IDs that were retrieved and directly support the answer, and set
  `supported=true`.
- Do not add plausible implications, causes, historical framing, or background
  unless the retrieved text states them explicitly.
- Preserve the material's exact scope and strength. Do not introduce stronger
  quantifiers or absolutes such as "all," "every," "always," "first," or
  "millions" unless that wording is explicitly supported by the retrieved text.
- Prefer the shortest direct answer that resolves the question; omit extra
  scale, examples, and framing that the student did not ask for.
- If the course materials do not support an answer, say so plainly and return
  no citations with `supported=false` — even if the search returned material
  that shares words with the question but does not answer it. Never invent a
  citation or an unsupported fact.
- Keep answers concise and at an introductory level: two to five sentences.
"""


@dataclass
class RetrievalTracker:
    """Records what the agent's tools actually retrieved during one run."""

    section_ids: list[str] = field(default_factory=list)
    chunks: list[str] = field(default_factory=list)
    search_queries: list[str] = field(default_factory=list)

    def record_search(self, query: str) -> None:
        self.search_queries.append(query)

    def record(self, section_id: str, text: str) -> None:
        if section_id not in self.section_ids:
            self.section_ids.append(section_id)
            self.chunks.append(text)


study_agent = Agent(
    deps_type=RetrievalTracker,
    output_type=StudyAnswer,
    instructions=SYSTEM_PROMPT,
)


@study_agent.output_validator
def validate_grounded_output(
    ctx: RunContext[RetrievalTracker], output: StudyAnswer
) -> StudyAnswer:
    """Reject final answers that violate the run's retrieval provenance."""
    if not ctx.deps.search_queries:
        raise ModelRetry(
            "Search the course materials before answering. Use search_materials now."
        )

    retrieved = set(ctx.deps.section_ids)
    cited = set(output.citations)
    unknown = cited - retrieved
    if unknown:
        valid = ", ".join(ctx.deps.section_ids) or "none"
        raise ModelRetry(
            f"Citations must be exact IDs retrieved in this run. "
            f"Invalid: {', '.join(sorted(unknown))}. Retrieved IDs: {valid}."
        )
    if output.supported and not retrieved:
        raise ModelRetry(
            "Set supported=true only when course material was retrieved and "
            "directly supports the answer. Otherwise abstain with supported=false."
        )
    if output.supported and not cited:
        raise ModelRetry(
            "The retrieved material supports the answer; cite one or two exact "
            "retrieved section IDs."
        )
    if not output.supported and cited:
        raise ModelRetry(
            "An unsupported answer must abstain and return no citations."
        )
    return output


@study_agent.tool
def search_materials(ctx: RunContext[RetrievalTracker], query: str) -> str:
    """Search the course materials. Returns the most relevant sections."""
    ctx.deps.record_search(query)
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
