import json
import sys
from collections.abc import Callable
from pathlib import Path

import pytest
from pydantic import ValidationError
from pydantic_ai import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import EvaluatorContext

EVALS_DIR = Path(__file__).resolve().parents[2] / "evals"
sys.path.insert(0, str(EVALS_DIR))

from app.models import QuizQuestion, QuizResponse  # noqa: E402
from quiz_evaluators import (  # noqa: E402
    QUIZ_EVIDENCE_INSTRUCTIONS,
    QuizAnswerPositionsVaried,
    QuizOptionEvidence,
    quiz_item_review_agent,
    quiz_quality_judge,
)


def _context(positions: list[int]) -> EvaluatorContext:
    questions = []
    section_ids = []
    chunks = []
    for question_index, position in enumerate(positions):
        section_id = f"lesson#section-{question_index}"
        options = [
            f"Choice {question_index}-{option_index}" for option_index in range(4)
        ]
        statements = [
            (
                f"{option} is the correct answer."
                if option_index == position
                else f"{option} is not the correct answer."
            )
            for option_index, option in enumerate(options)
        ]
        questions.append(
            QuizQuestion(
                question=f"Question {question_index}?",
                options=options,
                correct_index=position,
                citation=section_id,
            )
        )
        section_ids.append(section_id)
        chunks.append(" ".join(statements))

    return EvaluatorContext(
        name="synthetic",
        inputs="topic",
        metadata={"expected_question_count": 5},
        expected_output=None,
        output=QuizResponse(
            topic="topic",
            questions=questions,
            retrieved_section_ids=section_ids,
            retrieved_chunks=chunks,
        ),
        duration=0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def _valid_evidence(positions: list[int]) -> dict:
    return {
        "items": [
                {
                    "question_index": question_index,
                    "topic_relevant": True,
                    "topic_relevance_explanation": (
                        "The question directly tests the requested topic."
                    ),
                    "options": [
                    {
                        "option_index": option_index,
                        "ruling": (
                            "supported"
                            if option_index == correct_index
                            else "contradicted"
                        ),
                        "evidence_quote": (
                            f"Choice {question_index}-{option_index} is the correct answer."
                            if option_index == correct_index
                            else (
                                f"Choice {question_index}-{option_index} is not "
                                "the correct answer."
                            )
                        ),
                        "explanation": "The cited sentence directly gives this ruling.",
                    }
                    for option_index in range(4)
                ],
            }
            for question_index, correct_index in enumerate(positions)
        ]
    }


def _evidence_model(
    evidence: dict,
    inspect_prompt: Callable[[dict], None] | None = None,
) -> FunctionModel:
    def run(messages, info: AgentInfo) -> ModelResponse:
        prompt_parts = [
            part.content
            for message in messages
            for part in message.parts
            if type(part).__name__ == "UserPromptPart"
        ]
        assert len(prompt_parts) == 1
        prompt = json.loads(prompt_parts[0])
        if inspect_prompt:
            inspect_prompt(prompt)
        question_index = prompt["question"]["question_index"]
        output_tool = info.output_tools[0]
        return ModelResponse(
            parts=[ToolCallPart(output_tool.name, evidence["items"][question_index])]
        )

    return FunctionModel(run)


def test_answer_positions_require_all_four_indices():
    evaluator = QuizAnswerPositionsVaried()
    assert evaluator.evaluate(_context([0, 1, 2, 3, 0]))
    assert not evaluator.evaluate(_context([1, 2, 3, 1, 2]))


async def test_typed_quiz_judge_accepts_complete_cited_evidence():
    positions = [0, 1, 2, 3, 0]
    context = _context(positions)

    observed_indices: list[int] = []

    def inspect_prompt(prompt: dict) -> None:
        assert set(prompt) == {"question"}
        item = prompt["question"]
        question_index = item["question_index"]
        observed_indices.append(question_index)
        assert "retrieved_chunks" not in item
        assert item["cited_chunk"] == context.output.retrieved_chunks[question_index]

    with quiz_item_review_agent.override(
        model=_evidence_model(_valid_evidence(positions), inspect_prompt)
    ):
        result = await quiz_quality_judge().evaluate(context)

    assert result.value is True
    reason = json.loads(result.reason)
    assert reason["passed"] is True
    assert reason["errors"] == []
    assert len(reason["evidence"]["items"]) == 5
    assert sorted(observed_indices) == list(range(5))


@pytest.mark.parametrize(
    "mutate",
    [
        lambda evidence: evidence["items"][0]["options"][1].update(
            ruling="supported"
        ),
        lambda evidence: evidence["items"][0]["options"][1].update(
            evidence_quote="This sentence was never in the cited chunk."
        ),
        lambda evidence: evidence["items"][0].update(
            topic_relevant=False,
            topic_relevance_explanation=(
                "This question tests a different topic than the request."
            ),
        ),
        lambda evidence: evidence["items"][4].update(question_index=0),
        lambda evidence: evidence["items"][0]["options"][3].update(option_index=2),
    ],
    ids=[
        "distractor-also-supported",
        "invented-quote",
        "topic-drift",
        "missing-question-index",
        "missing-option-index",
    ],
)
async def test_typed_quiz_judge_rejects_incomplete_or_unverifiable_evidence(
    mutate: Callable[[dict], None],
):
    positions = [0, 1, 2, 3, 0]
    evidence = _valid_evidence(positions)
    mutate(evidence)

    with quiz_item_review_agent.override(model=_evidence_model(evidence)):
        result = await quiz_quality_judge().evaluate(_context(positions))

    assert result.value is False
    reason = json.loads(result.reason)
    assert reason["passed"] is False
    assert reason["errors"]


async def test_typed_quiz_judge_allows_an_unsupported_distractor():
    """A choice absent from evidence is wrong, not a second defensible answer."""
    positions = [0, 1, 2, 3, 0]
    evidence = _valid_evidence(positions)
    evidence["items"][0]["options"][1]["ruling"] = "not_proven"

    with quiz_item_review_agent.override(model=_evidence_model(evidence)):
        result = await quiz_quality_judge().evaluate(_context(positions))

    assert result.value is True


def test_quiz_judge_instructions_forbid_absence_and_outside_knowledge():
    assert "Mere absence is always `not_proven`" in QUIZ_EVIDENCE_INSTRUCTIONS
    assert "do not use" in QUIZ_EVIDENCE_INSTRUCTIONS
    assert "general knowledge" in QUIZ_EVIDENCE_INSTRUCTIONS


def test_typed_quiz_judge_rejects_trivial_evidence_quote():
    with pytest.raises(ValidationError):
        QuizOptionEvidence(
            option_index=0,
            ruling="supported",
            evidence_quote="the",
            explanation="This token is too weak to support a semantic ruling.",
        )


def test_typed_quiz_judge_is_runner_compatible():
    positions = [0, 1, 2, 3, 0]
    context = _context(positions)
    dataset = Dataset(
        name="synthetic-quiz",
        cases=[
            Case(
                name="synthetic",
                inputs=context.inputs,
                metadata=context.metadata,
            )
        ],
        evaluators=[quiz_quality_judge()],
    )

    with quiz_item_review_agent.override(
        model=_evidence_model(_valid_evidence(positions))
    ):
        report = dataset.evaluate_sync(lambda _topic: context.output)

    assertion = report.cases[0].assertions["QuizEvidenceJudge"]
    assert assertion.value is True
    assert json.loads(assertion.reason)["passed"] is True
