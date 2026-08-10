"""Eval cases for practice-quiz generation.

The topics intentionally avoid reproducing the provided sample quiz. Together
they exercise two broad course areas and one narrow concept, so improvements
must generalize beyond a single lesson or phrasing.
"""

from pydantic_evals import Case, Dataset

from quiz_evaluators import (
    QuizCitationsGrounded,
    QuizDoesNotRevealAnswers,
    QuizShapeValid,
    quiz_quality_judge,
)


QUIZ_CASES = [
    Case(
        name="computer_hardware",
        inputs="computer hardware",
        metadata={"expected_question_count": 5},
    ),
    Case(
        name="networks_and_internet",
        inputs="networks and the internet",
        metadata={"expected_question_count": 5},
    ),
    Case(
        name="binary_search",
        inputs="binary search",
        metadata={"expected_question_count": 5},
    ),
]


def build_quiz_dataset(include_judge: bool = True) -> Dataset:
    evaluators = [
        QuizShapeValid(),
        QuizCitationsGrounded(),
        QuizDoesNotRevealAnswers(),
    ]
    if include_judge:
        evaluators.append(quiz_quality_judge())
    return Dataset(name="study-coach-quiz", cases=QUIZ_CASES, evaluators=evaluators)
