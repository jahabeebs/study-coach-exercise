from app.retrieval import best_section, load_sections, search


def test_sections_load_with_stable_ids():
    sections = load_sections()
    assert len(sections) > 20
    ids = [s.id for s in sections]
    assert "lesson-02-data-and-binary#binary-numbers" in ids
    assert "lesson-04-algorithms#binary-search" in ids
    assert len(ids) == len(set(ids)), "section IDs must be unique"


def test_search_ranks_most_relevant_section_first():
    results = search("How does binary search work on a sorted list?")
    assert results, "expected at least one result"
    assert results[0].section.id == "lesson-04-algorithms#binary-search"


def test_search_scores_descend():
    results = search("compiler interpreter machine code")
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True), "results must be best-first"


def test_search_respects_k():
    assert len(search("computer", k=2)) <= 2


def test_search_empty_query_returns_nothing():
    assert search("") == []
    assert search("the and of") == []


def test_best_section_returns_top_match():
    section = best_section("What does DNS do?")
    assert section is not None
    assert section.id == "lesson-06-networks#the-domain-name-system"


def test_best_section_no_match():
    assert best_section("zzzz qqqq xxxx") is None
