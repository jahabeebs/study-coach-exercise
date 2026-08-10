"""Study Coach API.

Local development tool — runs on localhost for a single user. Not hardened for
public deployment; do not expose it to untrusted networks as-is.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic_ai.exceptions import ModelAPIError, UnexpectedModelBehavior

from .agent import ask
from .models import (
    ChatRequest,
    ChatResponse,
    QuizRequest,
    QuizResponse,
    SuggestResponse,
)
from .quiz import UnsupportedQuizTopic, generate_quiz
from .retrieval import MATERIALS_DIR, best_section, load_sections

app = FastAPI(title="Study Coach")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "sections": len(load_sections())}


@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    return await ask(request.message)


@app.post("/api/quiz")
async def quiz(request: QuizRequest) -> QuizResponse:
    try:
        return await generate_quiz(request.topic)
    except UnsupportedQuizTopic as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (UnexpectedModelBehavior, ModelAPIError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Quiz generation failed. Please try again.",
        ) from exc


@app.get("/api/suggest")
def suggest(topic: str) -> SuggestResponse:
    """The single best section to study for a topic."""
    section = best_section(topic)
    if section is None:
        raise HTTPException(status_code=404, detail="No matching course material.")
    return SuggestResponse(
        section_id=section.id, title=section.title, source_file=section.source_file
    )


@app.get("/api/materials")
def list_materials() -> list[str]:
    return sorted(p.name for p in MATERIALS_DIR.glob("*.md"))


@app.get("/api/materials/{name:path}")
def get_material(name: str) -> dict:
    materials_root = MATERIALS_DIR.resolve()
    try:
        path = (materials_root / name).resolve()
        path.relative_to(materials_root)
    except (OSError, RuntimeError, ValueError):
        raise HTTPException(status_code=404, detail="Unknown material.") from None

    if path.suffix.lower() != ".md" or not path.is_file():
        raise HTTPException(status_code=404, detail="Unknown material.")
    return {"name": name, "content": path.read_text()}
