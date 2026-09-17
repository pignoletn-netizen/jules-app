import pytest
from fastapi.testclient import TestClient
from main import app
from services.text_service import restructure_text_with_pacing
from services.trend_service import generate_script_from_trend, search_top_shorts

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ShortsFactory" in data["app"]


def test_from_trend_success():
    payload = {"topic": "intelligence artificielle", "provider": "groq"}
    response = client.post("/api/v1/script/from-trend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "intelligence artificielle"
    assert isinstance(data["analyzed_trends"], list)
    assert len(data["analyzed_trends"]) > 0
    assert "script" in data
    assert isinstance(data["script"], str)


def test_from_trend_empty_topic():
    payload = {"topic": "   "}
    response = client.post("/api/v1/script/from-trend", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_process_text_success():
    raw_text = (
        "Voici 3 clés pour réussir en ligne. La première clé est la constance! "
        "Deuxièmement, privilégie la qualité. Et enfin, n'abandonne jamais."
    )
    payload = {"text": raw_text}
    response = client.post("/api/v1/script/process-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    for segment in data:
        assert "text" in segment
        assert "pause_after_ms" in segment
        assert "search_keyword_en" in segment
        assert isinstance(segment["pause_after_ms"], int)
        assert isinstance(segment["search_keyword_en"], str)


def test_process_text_empty_text():
    payload = {"text": ""}
    response = client.post("/api/v1/script/process-text", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_trend_service_direct():
    trends = search_top_shorts("crypto", max_results=3)
    assert isinstance(trends, list)
    assert len(trends) <= 3
    if len(trends) > 0:
        assert "title" in trends[0]
        assert "url" in trends[0]

    result = generate_script_from_trend("crypto")
    assert result["topic"] == "crypto"
    assert len(result["analyzed_trends"]) <= 5
    assert len(result["script"]) > 0


def test_text_service_direct():
    segments = restructure_text_with_pacing("Savais-tu que le Bitcoin augmente ? Acheter maintenant!")
    assert isinstance(segments, list)
    assert len(segments) >= 1
    assert segments[0]["text"] == "Savais-tu que le Bitcoin augmente ?"
    assert segments[0]["pause_after_ms"] == 500
    assert "crypto" in segments[0]["search_keyword_en"]
