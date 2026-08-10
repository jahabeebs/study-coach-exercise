from fastapi.testclient import TestClient
from tests.conftest import scripted_model

from app.agent import study_agent
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_returns_contract_fields():
    with study_agent.override(model=scripted_model()):
        response = client.post("/api/chat", json={"message": "What is a bit?"})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"answer", "citations", "retrieved_section_ids", "retrieved_chunks"}
    assert body["retrieved_section_ids"]


def test_chat_rejects_empty_message():
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_rejects_whitespace_only_message():
    response = client.post("/api/chat", json={"message": "   "})
    assert response.status_code == 422


def test_suggest_returns_best_section():
    response = client.get("/api/suggest", params={"topic": "how DNS translates names"})
    assert response.status_code == 200
    assert response.json()["section_id"] == "lesson-06-networks#the-domain-name-system"


def test_suggest_no_match_is_404():
    response = client.get("/api/suggest", params={"topic": "zzzz qqqq"})
    assert response.status_code == 404


def test_list_materials():
    response = client.get("/api/materials")
    assert response.status_code == 200
    assert "syllabus.md" in response.json()


def test_get_material_by_name():
    response = client.get("/api/materials/glossary.md")
    assert response.status_code == 200
    assert "Glossary" in response.json()["content"]


def test_get_material_unknown_is_404():
    response = client.get("/api/materials/nope.md")
    assert response.status_code == 404
