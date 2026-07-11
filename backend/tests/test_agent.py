from app.agent import RetrievalTracker, ask, search_materials, study_agent


async def test_ask_returns_grounded_response(grounded_agent):
    response = await ask("What is binary?")
    assert response.retrieved_section_ids
    assert len(response.retrieved_chunks) == len(response.retrieved_section_ids)
    assert response.answer
    # The scripted model cites the first section it retrieved.
    assert response.citations
    assert set(response.citations) <= set(response.retrieved_section_ids)


async def test_ask_completes_even_if_model_skips_tools(test_model_agent):
    response = await ask("What is a byte?")
    assert isinstance(response.answer, str)
    assert isinstance(response.retrieved_section_ids, list)


async def test_tracker_records_each_section_once():
    tracker = RetrievalTracker()
    tracker.record("a#b", "text")
    tracker.record("a#b", "text")
    tracker.record("c#d", "other")
    assert tracker.section_ids == ["a#b", "c#d"]


def test_search_materials_tool_formats_and_records():
    class FakeCtx:
        deps = RetrievalTracker()

    output = search_materials(FakeCtx(), "binary search sorted list")
    # Formatting and tracking only — ranking quality is covered in test_retrieval.
    assert output.startswith("[lesson-") or output.startswith("[glossary") or output.startswith("[syllabus") or output.startswith("[sample")
    assert FakeCtx.deps.section_ids, "retrieved sections must be recorded"
    assert len(FakeCtx.deps.chunks) == len(FakeCtx.deps.section_ids)


def test_agent_has_expected_tools():
    tool_names = set(study_agent._function_toolset.tools)  # noqa: SLF001
    assert {"search_materials", "read_section"} <= tool_names
