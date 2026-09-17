import os
import pytest
from fastapi.testclient import TestClient
from main import app
from services.audio_service import generate_audio_for_script
from services.media_service import fetch_media_for_script

client = TestClient(app)


def test_generate_audio_endpoint_success():
    payload = {
        "segments": [
            {
                "text": "Bonjour tout le monde.",
                "pause_after_ms": 400,
                "search_keyword_en": "nature landscape",
            },
            {
                "text": "Aujourd'hui nous parlons de technologie.",
                "pause_after_ms": 300,
                "search_keyword_en": "technology cyber",
            },
        ],
        "output_filename": "downloads/test_audio_endpoint.wav",
    }
    response = client.post("/api/v1/audio/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "audio_path" in data
    assert os.path.exists(data["audio_path"])
    assert data["total_duration_ms"] > 0
    assert len(data["segment_timings"]) == 2


def test_generate_audio_endpoint_empty_segments():
    payload = {"segments": []}
    response = client.post("/api/v1/audio/generate", json=payload)
    assert response.status_code == 400


def test_fetch_media_endpoint_success():
    payload = {
        "segments": [
            {
                "text": "Short 1",
                "pause_after_ms": 300,
                "search_keyword_en": "dark office motivation",
            },
            {
                "text": "Short 2",
                "pause_after_ms": 500,
                "search_keyword_en": "crypto chart",
            },
        ],
        "output_dir": "downloads",
    }
    response = client.post("/api/v1/media/fetch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "downloaded_clips" in data
    assert len(data["downloaded_clips"]) == 2
    for clip in data["downloaded_clips"]:
        assert os.path.exists(clip["video_path"])
    assert "background_music" in data
    assert os.path.exists(data["background_music"]["music_path"])


def test_fetch_media_endpoint_empty_segments():
    payload = {"segments": []}
    response = client.post("/api/v1/media/fetch", json=payload)
    assert response.status_code == 400


def test_audio_service_direct():
    segs = [
        {"text": "Test phrase 1", "pause_after_ms": 200},
        {"text": "Test phrase 2", "pause_after_ms": 200},
    ]
    res = generate_audio_for_script(segs, output_filename="downloads/test_direct.wav")
    assert os.path.exists(res["audio_path"])
    assert res["total_duration_ms"] > 0


def test_media_service_direct():
    segs = [{"search_keyword_en": "fitness workout"}]
    res = fetch_media_for_script(segs, output_dir="downloads")
    assert len(res["downloaded_clips"]) == 1
    assert os.path.exists(res["downloaded_clips"][0]["video_path"])
    assert os.path.exists(res["background_music"]["music_path"])
