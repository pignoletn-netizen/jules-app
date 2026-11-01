import os
import tempfile
import numpy as np
from PIL import Image, ImageDraw
import pytest
from moviepy import ColorClip, ImageClip
from services.video_editor_service import (
    apply_color_effect,
    build_full_montage,
    extract_text_from_video,
    process_video_segment,
)


def _generate_test_video(path: str, duration: float = 1.0, text: str = ""):
    """Helper creating a simple test video with optional text drawn onto frames."""
    # Create an image with text
    img = Image.new("RGB", (320, 240), color=(73, 109, 137))
    if text:
        draw = ImageDraw.Draw(img)
        draw.text((30, 100), text, fill=(255, 255, 255))

    frame_np = np.array(img)
    clip = ImageClip(frame_np, duration=duration)
    clip.write_videofile(
        path,
        fps=12,
        codec="libx264",
        audio=False,
        preset="ultrafast",
        logger=None,
    )
    clip.close()


def test_apply_color_effects():
    # Test all color effects on a dummy RGB numpy array
    dummy_frame = np.ones((50, 50, 3), dtype=np.uint8) * 120

    bw = apply_color_effect(dummy_frame, "noir_et_blanc")
    assert bw.shape == (50, 50, 3)
    # in B&W all 3 channels should be identical
    assert np.array_equal(bw[..., 0], bw[..., 1])
    assert np.array_equal(bw[..., 1], bw[..., 2])

    sepia = apply_color_effect(dummy_frame, "sepia")
    assert sepia.shape == (50, 50, 3)

    vibrant = apply_color_effect(dummy_frame, "vibrant")
    assert vibrant.shape == (50, 50, 3)

    contraste = apply_color_effect(dummy_frame, "contraste")
    assert contraste.shape == (50, 50, 3)

    vintage = apply_color_effect(dummy_frame, "vintage")
    assert vintage.shape == (50, 50, 3)

    none = apply_color_effect(dummy_frame, "aucun")
    assert np.array_equal(dummy_frame, none)


def test_extract_text_from_video():
    with tempfile.TemporaryDirectory() as tmpdir:
        vid_path = os.path.join(tmpdir, "test_ocr.mp4")
        _generate_test_video(vid_path, duration=0.8, text="HELLO WORLD")

        # Extract text via OCR
        extracted = extract_text_from_video(vid_path, max_frames=2)
        # Check extraction returns a string (Tesseract can recognize HELLO or WORLD)
        assert isinstance(extracted, str)


def test_process_video_segment():
    with tempfile.TemporaryDirectory() as tmpdir:
        vid_path = os.path.join(tmpdir, "test_clip.mp4")
        _generate_test_video(vid_path, duration=1.0)

        # Process segment with voiceover and sepia effect
        res = process_video_segment(
            video_path=vid_path,
            voiceover_text="Bonjour le monde",
            effect="sepia",
            speed=1.0,
            keep_original_audio=False,
            voice="fr-FR-VivienneNeural",
            target_aspect_ratio="9:16",
        )

        assert "clip" in res
        assert "temp_files" in res
        clip = res["clip"]
        assert clip.duration > 0
        assert clip.size == (1080, 1920)

        # Clean clip & temp files
        clip.close()
        for f in res["temp_files"]:
            if os.path.exists(f):
                os.remove(f)


def test_build_full_montage():
    with tempfile.TemporaryDirectory() as tmpdir:
        vid1 = os.path.join(tmpdir, "clip1.mp4")
        vid2 = os.path.join(tmpdir, "clip2.mp4")
        output = os.path.join(tmpdir, "final_montage.mp4")

        _generate_test_video(vid1, duration=0.6)
        _generate_test_video(vid2, duration=0.6)

        clips_config = [
            {
                "video_path": vid1,
                "voiceover_text": "Premier extrait",
                "effect": "noir_et_blanc",
                "speed": 1.0,
                "keep_original_audio": False,
            },
            {
                "video_path": vid2,
                "voiceover_text": "Deuxième extrait",
                "effect": "vintage",
                "speed": 1.25,
                "keep_original_audio": False,
            },
        ]

        progress_calls = []

        def on_progress(pct, msg):
            progress_calls.append((pct, msg))

        final_path = build_full_montage(
            clips_config=clips_config,
            output_path=output,
            target_aspect_ratio="16:9",
            progress_callback=on_progress,
        )

        assert os.path.exists(final_path)
        assert os.path.getsize(final_path) > 0
        assert len(progress_calls) > 0
