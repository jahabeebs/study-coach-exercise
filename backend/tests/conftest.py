"""Test configuration.

The whole suite runs without any API key: agent tests override the model with
pydantic-ai test models, and ALLOW_MODEL_REQUESTS=False guarantees nothing in
the suite can reach a real model by accident.
"""

import pytest
from pydantic_ai import ModelResponse, ToolCallPart, models
from pydantic_ai.models.function import AgentInfo, FunctionModel

from app.agent import study_agent

models.ALLOW_MODEL_REQUESTS = False


def scripted_model(query: str = "binary numbers base two") -> FunctionModel:
    """A model that searches with a real query, then answers citing what it saw.

    TestModel invents minimal tool args (query='a'), which retrieval treats as
    a stopword — fine for plumbing tests, useless for grounded-path tests.
    This scripted model behaves like a well-behaved real model.
    """

    def run(messages, info: AgentInfo) -> ModelResponse:
        if len(messages) == 1:
            return ModelResponse(
                parts=[ToolCallPart("search_materials", {"query": query})]
            )
        tool_return = messages[-1].parts[0].content
        first_id = tool_return.split("]")[0].lstrip("[") if "[" in tool_return else ""
        output_tool = info.output_tools[0]
        return ModelResponse(
            parts=[
                ToolCallPart(
                    output_tool.name,
                    {
                        "answer": "Binary is a base-2 number system.",
                        "citations": [first_id] if first_id else [],
                    },
                )
            ]
        )

    return FunctionModel(run)


def abstaining_model() -> FunctionModel:
    """A model that searches, finds no evidence, and abstains cleanly."""

    def run(messages, info: AgentInfo) -> ModelResponse:
        if len(messages) == 1:
            return ModelResponse(
                parts=[ToolCallPart("search_materials", {"query": "zzzz qqqq"})]
            )
        output_tool = info.output_tools[0]
        return ModelResponse(
            parts=[
                ToolCallPart(
                    output_tool.name,
                    {
                        "answer": "I couldn't find that in the course materials.",
                        "citations": [],
                    },
                )
            ]
        )

    return FunctionModel(run)


@pytest.fixture
def grounded_agent():
    """study_agent wired to the scripted model."""
    with study_agent.override(model=scripted_model()):
        yield


@pytest.fixture
def abstaining_agent():
    """study_agent wired to a model that performs a no-match search."""
    with study_agent.override(model=abstaining_model()):
        yield
