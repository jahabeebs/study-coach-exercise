from collections.abc import Callable

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic_ai import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from app.main import app, get_material
from app.quiz import (
    UnsupportedQuizTopic,
    generate_quiz,
    quiz_agent,
    resolve_quiz_sections,
)


client = TestClient(app)
VALID_CITATION = "lesson-04-algorithms#binary-search"


def _questions(citation: str) -> list[dict]:
    return [
        {
            "question": "What condition must be true before binary search begins?",
            "options": [
                "The list must be sorted",
                "The list must contain strings",
                "The list must be stored on an SSD",
                "The list must have an even length",
            ],
            "correct_index": 0,
            "citation": citation,
        },
        {
            "question": "Which item does binary search compare with the target first?",
            "options": [
                "The final item",
                "The middle item",
                "A random item",
                "Every item simultaneously",
            ],
            "correct_index": 1,
            "citation": citation,
        },
        {
            "question": "What does each comparison eliminate in binary search?",
            "options": [
                "One item",
                "Only duplicate items",
                "Half of the remaining range",
                "The entire list",
            ],
            "correct_index": 2,
            "citation": citation,
        },
        {
            "question": "About how many comparisons can search a sorted million-item list?",
            "options": ["About five", "About ten", "About fifteen", "About twenty"],
            "correct_index": 3,
            "citation": citation,
        },
        {
            "question": "Where does binary search continue when the target is smaller?",
            "options": [
                "In the left half",
                "In the right half",
                "At the final item",
                "In an unsorted copy",
            ],
            "correct_index": 0,
            "citation": citation,
        },
    ]


def _scripted_quiz_model(
    citation_for_attempt: Callable[[int], str] = lambda _attempt: VALID_CITATION,
) -> tuple[FunctionModel, list[int]]:
    calls: list[int] = []

    def run(_messages, info: AgentInfo) -> ModelResponse:
        calls.append(len(calls) + 1)
        output_tool = info.output_tools[0]
        return ModelResponse(
            parts=[
                ToolCallPart(
                    output_tool.name,
                    {"questions": _questions(citation_for_attempt(len(calls)))},
                )
            ]
        )

    return FunctionModel(run), calls


@pytest.mark.parametrize(
    ("topic", "source_file"),
    [
        ("week 3", "lesson-03-hardware.md"),
        ("computer hardware", "lesson-03-hardware.md"),
        ("binary search", "lesson-04-algorithms.md"),
        ("history", "lesson-01-history-of-computing.md"),
    ],
)
def test_topic_resolution_selects_one_course_lesson(topic, source_file):
    sections = resolve_quiz_sections(topic)
    assert len(sections) == 6
    assert {section.source_file for section in sections} == {source_file}


@pytest.mark.parametrize(
    "topic",
    ["photosynthesis and chlorophyll", "food storage", "memory cakes", "week 99"],
)
def test_topic_resolution_rejects_unsupported_or_weak_match(topic):
    with pytest.raises(UnsupportedQuizTopic):
        resolve_quiz_sections(topic)


async def test_generate_quiz_attaches_application_owned_evidence():
    model, calls = _scripted_quiz_model()
    with quiz_agent.override(model=model):
        response = await generate_quiz("  binary   search  ")

    assert calls == [1]
    assert response.topic == "binary search"
    assert len(response.questions) == 5
    assert len(response.retrieved_section_ids) == 6
    assert len(response.retrieved_chunks) == len(response.retrieved_section_ids)
    assert all(
        question.citation in response.retrieved_section_ids
        for question in response.questions
    )


async def test_invalid_citation_is_retried_with_exact_provenance():
    model, calls = _scripted_quiz_model(
        lambda attempt: "syllabus#grading" if attempt == 1 else VALID_CITATION
    )
    with quiz_agent.override(model=model):
        response = await generate_quiz("binary search")

    assert calls == [1, 2]
    assert {question.citation for question in response.questions} == {
        VALID_CITATION
    }


async def test_answer_position_bias_is_retried():
    calls: list[int] = []

    def position_model(_messages, info: AgentInfo) -> ModelResponse:
        calls.append(len(calls) + 1)
        questions = _questions(VALID_CITATION)
        if len(calls) == 1:
            for question in questions:
                question["correct_index"] = 0
        output_tool = info.output_tools[0]
        return ModelResponse(
            parts=[ToolCallPart(output_tool.name, {"questions": questions})]
        )

    with quiz_agent.override(model=FunctionModel(position_model)):
        response = await generate_quiz("binary search")

    assert calls == [1, 2]
    assert len({question.correct_index for question in response.questions}) >= 3


async def test_unsupported_topic_never_calls_the_model():
    def fail_if_called(_messages, _info):
        raise AssertionError("model should not run for an unsupported topic")

    with quiz_agent.override(model=FunctionModel(fail_if_called)):
        with pytest.raises(UnsupportedQuizTopic):
            await generate_quiz("photosynthesis and chlorophyll")


def test_quiz_api_returns_the_frontend_and_eval_contract():
    model, _calls = _scripted_quiz_model()
    with quiz_agent.override(model=model):
        response = client.post("/api/quiz", json={"topic": "binary search"})

    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == "binary search"
    assert len(body["questions"]) == 5
    assert set(body["questions"][0]) == {
        "question",
        "options",
        "correct_index",
        "citation",
    }
    assert body["questions"][0]["citation"] in body["retrieved_section_ids"]
    assert all(len(question["options"]) == 4 for question in body["questions"])
    assert all(0 <= question["correct_index"] <= 3 for question in body["questions"])
    assert len(body["retrieved_chunks"]) == len(body["retrieved_section_ids"])


def test_quiz_api_rejects_blank_topic():
    response = client.post("/api/quiz", json={"topic": "   "})
    assert response.status_code == 422


def test_quiz_api_rejects_overlong_topic():
    response = client.post("/api/quiz", json={"topic": "x" * 201})
    assert response.status_code == 422


def test_quiz_api_fails_safely_for_malformed_model_output():
    def malformed_model(_messages, info: AgentInfo) -> ModelResponse:
        output_tool = info.output_tools[0]
        return ModelResponse(
            parts=[
                ToolCallPart(
                    output_tool.name,
                    {"questions": _questions(VALID_CITATION)[:1]},
                )
            ]
        )

    safe_client = TestClient(app, raise_server_exceptions=False)
    with quiz_agent.override(model=FunctionModel(malformed_model)):
        response = safe_client.post("/api/quiz", json={"topic": "binary search"})

    assert response.status_code == 500
    assert response.text == "Internal Server Error"


def test_quiz_api_returns_404_for_unsupported_topic():
    response = client.post(
        "/api/quiz", json={"topic": "photosynthesis and chlorophyll"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == (
        "No course lesson contains enough material for that topic."
    )


@pytest.mark.parametrize("name", ["../README.md", "../.env", "/etc/passwd"])
def test_material_handler_rejects_paths_outside_materials(name):
    with pytest.raises(HTTPException) as exc_info:
        get_material(name)
    assert exc_info.value.status_code == 404


def test_material_api_rejects_encoded_path_traversal():
    response = client.get("/api/materials/..%2FREADME.md")
    assert response.status_code == 404
