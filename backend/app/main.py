"""Study Coach API.

Local development tool — runs on localhost for a single user. Not hardened for
public deployment; do not expose it to untrusted networks as-is.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agent import ask
from .models import ChatRequest, ChatResponse, SuggestResponse
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
    path = MATERIALS_DIR / name
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Unknown material.")
    return {"name": name, "content": path.read_text()}
