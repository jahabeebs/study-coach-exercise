# pydantic-ai / pydantic-evals crib sheet

You don't need prior experience with these libraries. Everything this codebase
does with them fits on this page. (Full docs: https://ai.pydantic.dev)

## pydantic-ai in this codebase

An `Agent` bundles a system prompt, tools, and a typed output. Ours is in
`backend/app/agent.py`:

```python
from pydantic_ai import Agent, RunContext

study_agent = Agent(
    deps_type=RetrievalTracker,     # per-run state passed to every tool
    output_type=StudyAnswer,        # a pydantic model — the LLM must return this shape
    instructions=SYSTEM_PROMPT,
)

@study_agent.tool
def search_materials(ctx: RunContext[RetrievalTracker], query: str) -> str:
    """The docstring and signature become the tool's spec for the LLM."""
    ...  # whatever you return is what the LLM sees

# Running it (model resolved at call time from env config):
result = await study_agent.run("question", model=get_model_name(), deps=tracker)
result.output          # -> StudyAnswer instance, validated
```

**Testing without an API key** (`backend/tests/conftest.py`): wrap calls in
`study_agent.override(model=...)` using `TestModel()` (calls each tool with
minimal args, then returns schema-valid output) or `FunctionModel(fn)` (you
script exactly what the "model" does — see `scripted_model`).
`models.ALLOW_MODEL_REQUESTS = False` makes any accidental real call an error.

## pydantic-evals in this codebase

A `Dataset` is cases + evaluators; you evaluate a *task function*
(`evals/run_evals.py` runs it against the real agent):

```python
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext, LLMJudge

case = Case(
    name="byte_values",
    inputs="How many values can one byte represent?",
    metadata={"expected_section": "lesson-02-data-and-binary#bits-and-bytes",
              "answer_keywords": ["256"]},
)

class CitationsGrounded(Evaluator[str, ChatResponse]):
    def evaluate(self, ctx: EvaluatorContext[str, ChatResponse]) -> bool:
        # return bool -> shows as a pass/fail "assertion"
        # return float -> shows as a 0..1 "score"
        # read ctx.inputs / ctx.output / ctx.metadata
        return set(ctx.output.citations) <= set(ctx.output.retrieved_section_ids)

judge = LLMJudge(                       # LLM-as-judge, for what code can't check
    rubric="The answer must be fully supported by retrieved_chunks…",
    model=get_model_name(),
    include_input=True,
)

dataset = Dataset(name="qa", cases=[case], evaluators=[CitationsGrounded(), judge])
report = dataset.evaluate_sync(task_fn)   # task_fn(inputs) -> ChatResponse
```

**The data contract that makes grounding checkable:** the task's output
(`ChatResponse`) carries `retrieved_section_ids` and `retrieved_chunks` —
what the agent's tools actually returned during that run. Evaluators compare
the answer and citations against *that*, not against the whole corpus.

## Commands

| Command | What | Needs key? |
|---|---|---|
| `make test` | pytest suite | no |
| `make evals` | eval suite, writes `evals/reports/*.json` — **commit these** | yes |
| `make evals -- --no-judge`* | deterministic evaluators only | yes |
| `make dev-backend` / `make dev-frontend` | run the app | yes (chat) |

*or `cd backend && uv run python ../evals/run_evals.py --no-judge`
