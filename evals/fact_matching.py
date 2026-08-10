"""Deterministic matching for answer facts used across eval suites.

Metadata may provide either legacy ``answer_keywords`` (one OR group) or
``answer_keyword_groups`` (an AND of OR groups). A keyword ending in ``*`` is
an explicit prefix stem; complete words otherwise match only ordinary
inflections, never arbitrary prefixes.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping, Sequence
from typing import Any

_WORD = re.compile(r"[a-z0-9]+")
_NEGATIONS = frozenset(
    {"false", "incorrect", "never", "no", "not", "without", "wrong"}
)


def answer_satisfies_facts(answer: str, metadata: Mapping[str, Any] | None) -> bool:
    """Return whether an answer satisfies every required fact group."""
    groups = _fact_groups(metadata or {})
    if not groups:
        return False
    answer_tokens = _fact_tokens(answer)
    return all(
        alternatives
        and any(_matches_keyword(answer_tokens, keyword) for keyword in alternatives)
        for alternatives in groups
    )


def _fact_groups(metadata: Mapping[str, Any]) -> list[list[str]]:
    grouped = metadata.get("answer_keyword_groups")
    if grouped is not None:
        if not isinstance(grouped, Sequence) or isinstance(grouped, (str, bytes)):
            return []
        return [
            [str(keyword) for keyword in group]
            if isinstance(group, Sequence) and not isinstance(group, (str, bytes))
            else []
            for group in grouped
        ]

    keywords = metadata.get("answer_keywords", [])
    if not isinstance(keywords, Sequence) or isinstance(keywords, (str, bytes)):
        return []
    return [[str(keyword) for keyword in keywords]]


def _fact_tokens(text: str) -> list[str]:
    """Normalize prose while keeping numeric tokens separate and exact."""
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = re.sub(r"n['’]t\b", " not", normalized)
    normalized = re.sub(r"(?<=\d),(?=\d)", "", normalized)
    return [token for token in _WORD.findall(normalized) if token]


def _matches_keyword(answer_tokens: list[str], keyword: str) -> bool:
    """Match a fact phrase outside a nearby negation."""
    raw_keyword = unicodedata.normalize("NFKC", str(keyword)).strip().casefold()
    explicit_stem = raw_keyword.endswith("*")
    if explicit_stem:
        raw_keyword = raw_keyword[:-1]
    keyword_tokens = _fact_tokens(raw_keyword)
    if not keyword_tokens:
        return False
    if explicit_stem and (len(keyword_tokens) != 1 or not keyword_tokens[0].isalpha()):
        return False

    width = len(keyword_tokens)
    for index in range(len(answer_tokens) - width + 1):
        candidate = answer_tokens[index : index + width]
        if explicit_stem:
            matched = candidate[0].startswith(keyword_tokens[0])
        else:
            matched = all(
                _word_matches(expected, actual, is_last=offset == width - 1)
                for offset, (expected, actual) in enumerate(
                    zip(keyword_tokens, candidate, strict=True)
                )
            )
        if matched and not _is_negated(answer_tokens, index):
            return True
    return False


def _word_matches(expected: str, actual: str, *, is_last: bool) -> bool:
    if expected == actual:
        return True
    if not is_last or not expected.isalpha():
        return False
    variants = {
        f"{expected}s",
        f"{expected}es",
        f"{expected}ed",
        f"{expected}ing",
    }
    if expected.endswith("e"):
        variants.update({f"{expected}d", f"{expected[:-1]}ing"})
    if expected.endswith("y") and len(expected) > 1:
        variants.add(f"{expected[:-1]}ies")
    return actual in variants


def _is_negated(answer_tokens: list[str], match_start: int) -> bool:
    preceding = answer_tokens[max(0, match_start - 3) : match_start]
    return any(token in _NEGATIONS for token in preceding)
