import os
import pytest
from fastapi.testclient import TestClient
from main import app
from services.youtube_service import upload_video_to_youtube

client = TestClient(app)


def test_index_page_web_ui():
    response = client.get("/")
    assert response.status_code == 200
    assert "ShortsFactory" in response.text
    assert "Générer la vidéo Shorts" in response.text


def test_youtube_upload_endpoint_success():
    payload = {
        "video_path": "README.md",
        "title": "Mon premier Short AI",
        "description": "Test de publication",
        "privacy_status": "unlisted",
    }
    response = client.post("/api/v1/youtube/upload", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "youtube_url" in data
    assert "youtube.com/shorts/" in data["youtube_url"]


def test_youtube_upload_endpoint_file_not_found():
    payload = {
        "video_path": "downloads/non_existent_file_999.mp4",
        "title": "Test Error",
    }
    response = client.post("/api/v1/youtube/upload", json=payload)
    assert response.status_code == 404


def test_youtube_upload_endpoint_empty_path():
    payload = {"video_path": "   "}
    response = client.post("/api/v1/youtube/upload", json=payload)
    assert response.status_code == 400


def test_youtube_service_direct():
    res = upload_video_to_youtube(
        video_path="README.md",
        title="Direct Short Test",
        privacy_status="private",
    )
    assert res["success"] is True
    assert "youtube_url" in res
    assert res["privacy_status"] == "private"
    assert "#Shorts" in res["title"]
