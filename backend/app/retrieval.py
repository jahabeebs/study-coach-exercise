"""Keyword retrieval over the course materials.

The unit of retrieval is a *section*: every `##` heading in every materials
file becomes one section, identified as "<file-stem>#<heading-slug>", e.g.
"lesson-02-data-and-binary#binary-numbers". Scoring is a small BM25-style
formula — deterministic, no embeddings, no external services.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

MATERIALS_DIR = Path(__file__).resolve().parents[2] / "materials"

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does",
    "for", "from", "how", "in", "is", "it", "its", "of", "on", "or", "such",
    "that", "the", "this", "to", "was", "what", "when", "which", "why", "with",
}


def _tokenize(text: str) -> list[str]:
    return [w for w in _WORD.findall(text.replace("'", "").lower()) if w not in _STOPWORDS]


def _slugify(heading: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", heading.replace("'", "").lower()).strip("-")


@dataclass(frozen=True)
class Section:
    id: str
    title: str
    source_file: str
    text: str


@dataclass(frozen=True)
class SearchResult:
    section: Section
    score: float


@lru_cache(maxsize=1)
def load_sections(materials_dir: str = str(MATERIALS_DIR)) -> tuple[Section, ...]:
    """Parse every materials file into sections, keyed by `##` headings."""
    sections: list[Section] = []
    for path in sorted(Path(materials_dir).glob("*.md")):
        current_title: str | None = None
        current_lines: list[str] = []

        def flush() -> None:
            if current_title and current_lines:
                sections.append(
                    Section(
                        id=f"{path.stem}#{_slugify(current_title)}",
                        title=current_title,
                        source_file=path.name,
                        text="\n".join(current_lines).strip(),
                    )
                )

        for line in path.read_text().splitlines():
            if line.startswith("## "):
                flush()
                current_title = line[3:].strip()
                current_lines = []
            elif current_title:
                current_lines.append(line)
        flush()
    return tuple(sections)


def search(query: str, k: int = 4) -> list[SearchResult]:
    """Top-k sections for a query, best match first."""
    sections = load_sections()
    query_terms = _tokenize(query)
    if not query_terms:
        return []

    doc_tokens = {s.id: _tokenize(s.title + " " + s.text) for s in sections}
    avg_len = sum(len(t) for t in doc_tokens.values()) / len(sections)

    results = []
    for section in sections:
        tokens = doc_tokens[section.id]
        score = 0.0
        for term in set(query_terms):
            tf = tokens.count(term)
            if tf == 0:
                continue
            df = sum(1 for t in doc_tokens.values() if term in t)
            idf = math.log(1 + (len(sections) - df + 0.5) / (df + 0.5))
            score += idf * (tf / (tf + 1.0 + len(tokens) / avg_len))
        if score > 0:
            results.append(SearchResult(section=section, score=score))

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:k]


def best_section(query: str) -> Section | None:
    """The single most relevant section for a query, if any."""
    results = search(query, k=len(load_sections()))
    return results[0].section if results else None
