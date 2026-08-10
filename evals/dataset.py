"""Eval cases for the Study Coach Q&A agent.

Each case pins the section that actually answers the question
(`expected_section`) and grouped accepted phrasings of required facts
(`answer_keyword_groups`). Both are used by programmatic evaluators.
"""

from pydantic_evals import Case, Dataset

from evaluators import (
    AnswerGroundedness,
    AnswerHasFact,
    CitationsGrounded,
    ExpectedSectionCited,
    faithfulness_judge,
)

CASES = [
    Case(
        name="byte_values",
        inputs="How many different values can one byte represent?",
        metadata={
            "expected_section": "lesson-02-data-and-binary#bits-and-bytes",
            "answer_keyword_groups": [["256"]],
        },
    ),
    Case(
        name="eniac_year",
        inputs="When was ENIAC completed, and why does it matter?",
        metadata={
            "expected_section": "lesson-01-history-of-computing#the-electronic-era",
            "answer_keyword_groups": [["1945"]],
        },
    ),
    Case(
        name="compiler_vs_interpreter",
        inputs="What is the difference between a compiler and an interpreter?",
        metadata={
            "expected_section": "lesson-05-programming-languages#compilers",
            "answer_keyword_groups": [
                ["before"],
                ["line by line", "line-by-line"],
            ],
        },
    ),
    Case(
        name="binary_search_sorted",
        inputs="Why does binary search need the list to be sorted?",
        metadata={
            "expected_section": "lesson-04-algorithms#binary-search",
            "answer_keyword_groups": [["half", "halv*", "middle"]],
        },
    ),
    Case(
        name="dns_purpose",
        inputs="What does the Domain Name System actually do?",
        metadata={
            "expected_section": "lesson-06-networks#the-domain-name-system",
            "answer_keyword_groups": [["ip address"]],
        },
    ),
    Case(
        name="moores_law",
        inputs="What is Moore's law?",
        metadata={
            "expected_section": "lesson-03-hardware#moores-law",
            "answer_keyword_groups": [["transistor"]],
        },
    ),
    Case(
        name="ascii_capital_a",
        inputs="What number represents the capital letter A in ASCII?",
        metadata={
            "expected_section": "lesson-02-data-and-binary#representing-text",
            "answer_keyword_groups": [["65"]],
        },
    ),
    Case(
        name="ram_vs_ssd",
        inputs="What is the difference between RAM and an SSD?",
        metadata={
            "expected_section": "lesson-03-hardware#memory-and-the-storage-hierarchy",
            "answer_keyword_groups": [
                ["volatile", "lost"],
                ["persistent", "retains", "without power"],
            ],
        },
    ),
    Case(
        name="first_programmer",
        inputs="Who is often called the first computer programmer?",
        metadata={
            "expected_section": "lesson-01-history-of-computing#the-mechanical-era",
            "answer_keyword_groups": [["lovelace"]],
        },
    ),
    Case(
        name="https_protection",
        inputs="What protection does HTTPS give you that plain HTTP doesn't?",
        metadata={
            "expected_section": "lesson-06-networks#encryption-and-https",
            "answer_keyword_groups": [["encrypt*"]],
        },
    ),
]


def build_dataset(include_judge: bool = True) -> Dataset:
    evaluators = [
        CitationsGrounded(),
        ExpectedSectionCited(),
        AnswerHasFact(),
        AnswerGroundedness(),
    ]
    if include_judge:
        evaluators.append(faithfulness_judge())
    return Dataset(name="study-coach-qa", cases=CASES, evaluators=evaluators)
