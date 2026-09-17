import os
import pytest
from fastapi.testclient import TestClient
from main import app
from services.subtitle_service import format_ass_time, generate_ass_subtitles
from services.video_service import render_final_video

client = TestClient(app)


def test_generate_full_video_with_topic():
    payload = {
        "topic": "crypto trading",
        "output_dir": "downloads",
    }
    response = client.post("/api/v1/video/generate-full", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "video_path" in data
    assert os.path.exists(data["video_path"])
    assert data["duration_seconds"] > 0
    assert "resolution" in data
    assert data["resolution"] == "1080x1920"
    assert "subtitles_path" in data
    assert os.path.exists(data["subtitles_path"])


def test_generate_full_video_with_text():
    payload = {
        "text": "Voici une astuce secrète pour réussir en 2026. La constance bat le talent !",
        "output_dir": "downloads",
    }
    response = client.post("/api/v1/video/generate-full", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "video_path" in data
    assert os.path.exists(data["video_path"])
    assert data["segment_count"] >= 1


def test_generate_full_video_missing_params():
    payload = {}
    response = client.post("/api/v1/video/generate-full", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_subtitle_service_direct():
    timings = [
        {"text": "Savais-tu que le Bitcoin augmente ?", "start_ms": 0, "end_ms": 1500},
        {"text": "Acheter maintenant sans tarder.", "start_ms": 1800, "end_ms": 3200},
    ]
    out_ass = generate_ass_subtitles(
        segment_timings=timings,
        output_filename="downloads/test_sub_direct.ass",
    )
    assert os.path.exists(out_ass)
    with open(out_ass, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Savais-tu" in content or "SAVAIS-TU" in content
    assert "ShortsStyle" in content


def test_format_ass_time():
    assert format_ass_time(0) == "0:00:00.00"
    assert format_ass_time(1250) == "0:00:01.25"
    assert format_ass_time(61500) == "0:01:01.50"


def test_video_service_direct():
    res = render_final_video(
        clips_info=[],
        voice_audio_path="downloads/voice_audio.wav",
        bg_music_path="downloads/background_music.mp3",
        subtitle_ass_path="downloads/subtitles.ass",
        segment_timings=[{"start_ms": 0, "end_ms": 2000, "pause_after_ms": 300}],
        output_mp4_path="downloads/test_video_direct.mp4",
    )
    assert os.path.exists(res["video_path"])
    assert res["duration_seconds"] > 0
    assert res["resolution"] == "1080x1920"
