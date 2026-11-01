import logging
import os
import re
import tempfile
from typing import Any, Callable, Dict, List, Optional
import numpy as np
from PIL import Image
import pytesseract
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    VideoFileClip,
    concatenate_audioclips,
    concatenate_videoclips,
)
from services.audio_service import generate_tts_for_phrase

logger = logging.getLogger(__name__)


def extract_text_from_video(
    video_path: str,
    max_frames: int = 5,
    lang: str = "fra+eng",
) -> str:
    """
    Extracts text detected in keyframes of the video using Tesseract OCR.
    Iterates evenly across the video duration to capture subtitles, titles, or on-screen text.
    """
    if not os.path.exists(video_path):
        return ""

    extracted_lines = []
    seen = set()

    try:
        with VideoFileClip(video_path) as clip:
            duration = clip.duration or 1.0
            # Sample frames at regular timestamps
            sample_times = [
                (i + 0.5) * (duration / max_frames) for i in range(max_frames)
            ]

            for t in sample_times:
                t = min(t, max(0.0, duration - 0.1))
                frame = clip.get_frame(t)
                img = Image.fromarray(frame)

                try:
                    text = pytesseract.image_to_string(img, lang=lang)
                except Exception:
                    # Fallback to default english if fra is missing or failing
                    try:
                        text = pytesseract.image_to_string(img)
                    except Exception as e:
                        logger.warning(f"OCR failed for timestamp {t}: {e}")
                        text = ""

                for raw_line in text.split("\n"):
                    clean = raw_line.strip()
                    # Filter out noise or very short strings
                    if len(clean) >= 3 and clean.lower() not in seen:
                        # Skip pure special characters
                        if re.search(r"[a-zA-Z0-9À-ÿ]", clean):
                            extracted_lines.append(clean)
                            seen.add(clean.lower())

    except Exception as e:
        logger.error(f"Error extracting text from video {video_path}: {e}")

    return " ".join(extracted_lines).strip()


def apply_color_effect(frame: np.ndarray, effect_name: str) -> np.ndarray:
    """
    Applies visual color/style transformations to a numpy frame.
    Supported: 'noir_et_blanc', 'sepia', 'vibrant', 'contraste', 'vintage'.
    """
    if effect_name == "noir_et_blanc":
        # Luminance greyscale converted back to 3 channels RGB
        grey = np.dot(frame[..., :3], [0.2989, 0.5870, 0.1140])
        return np.stack((grey, grey, grey), axis=-1).astype(np.uint8)

    elif effect_name == "sepia":
        # Standard Sepia color matrix transformation
        r = frame[..., 0]
        g = frame[..., 1]
        b = frame[..., 2]
        tr = np.clip(0.393 * r + 0.769 * g + 0.189 * b, 0, 255)
        tg = np.clip(0.349 * r + 0.686 * g + 0.168 * b, 0, 255)
        tb = np.clip(0.272 * r + 0.534 * g + 0.131 * b, 0, 255)
        return np.stack((tr, tg, tb), axis=-1).astype(np.uint8)

    elif effect_name == "vibrant":
        # Boost saturation/vibrancy
        f = frame.astype(np.float32)
        mean_val = np.mean(f, axis=-1, keepdims=True)
        vibrant = np.clip(mean_val + 1.4 * (f - mean_val), 0, 255)
        return vibrant.astype(np.uint8)

    elif effect_name == "contraste":
        # S-curve style contrast boost
        f = frame.astype(np.float32)
        contrasted = np.clip(128.0 + 1.35 * (f - 128.0), 0, 255)
        return contrasted.astype(np.uint8)

    elif effect_name == "vintage":
        # Vintage / warm tone with reduced blue
        f = frame.astype(np.float32)
        r = np.clip(f[..., 0] * 1.15, 0, 255)
        g = np.clip(f[..., 1] * 1.02, 0, 255)
        b = np.clip(f[..., 2] * 0.85, 0, 255)
        return np.stack((r, g, b), axis=-1).astype(np.uint8)

    return frame


def process_video_segment(
    video_path: str,
    voiceover_text: Optional[str] = None,
    effect: str = "aucun",
    speed: float = 1.0,
    keep_original_audio: bool = False,
    voice: str = "fr-FR-VivienneNeural",
    target_aspect_ratio: Optional[str] = None,  # '9:16', '16:9', or None
) -> Dict[str, Any]:
    """
    Processes a single video segment:
    1. Loads video clip.
    2. Generates TTS speech audio from voiceover_text if provided.
    3. Adjusts video duration/speed to fit speech if required.
    4. Applies color effects (B&W, sepia, etc.).
    5. Sets audio (voiceover + optional muted/reduced original audio).
    6. Formats dimensions (cropping/scaling) if aspect ratio requested.
    Returns processed clip and temporary files to clean later.
    """
    temp_files = []
    clip = VideoFileClip(video_path)

    # 1. Apply speed modifier if different from 1.0
    if abs(speed - 1.0) > 0.05:
        clip = clip.with_speed_scaled(speed)

    # 2. Apply color effect
    if effect and effect != "aucun":
        effect_func = lambda frame: apply_color_effect(frame, effect)
        clip = clip.image_transform(effect_func)

    # 3. Handle Voiceover & Audio
    speech_audio_clip = None
    if voiceover_text and voiceover_text.strip():
        # Generate TTS audio
        audio_seg = generate_tts_for_phrase(voiceover_text.strip(), voice=voice)
        tmp_voice_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        audio_seg.export(tmp_voice_file.name, format="mp3")
        temp_files.append(tmp_voice_file.name)
        speech_audio_clip = AudioFileClip(tmp_voice_file.name)

        # If speech is longer than video clip, loop or extend video to match speech
        speech_duration = speech_audio_clip.duration
        if speech_duration > clip.duration:
            # Loop clip to match speech duration
            n_loops = int(np.ceil(speech_duration / clip.duration))
            subclips = [clip]
            for _ in range(n_loops - 1):
                subclips.append(VideoFileClip(video_path))
            combined_loop = concatenate_videoclips(subclips)
            clip = combined_loop.subclipped(0, speech_duration)

    # Audio combination
    if speech_audio_clip:
        if keep_original_audio and clip.audio is not None:
            # Lower original audio volume to 15% and mix with speech
            orig_audio = clip.audio.with_volume_scaled(0.15)
            # Ensure audio duration matches clip
            orig_audio = orig_audio.subclipped(0, min(orig_audio.duration, clip.duration))
            final_audio = CompositeAudioClip([speech_audio_clip, orig_audio])
        else:
            final_audio = speech_audio_clip

        # Sync audio with clip duration
        clip = clip.with_audio(final_audio)
    else:
        if not keep_original_audio:
            clip = clip.without_audio()

    # 4. Aspect Ratio formatting if requested
    if target_aspect_ratio in ["9:16", "16:9"]:
        w, h = clip.size
        if target_aspect_ratio == "9:16":
            target_w, target_h = 1080, 1920
        else:
            target_w, target_h = 1920, 1080

        # Resize preserving aspect ratio then crop to center
        ratio = max(target_w / w, target_h / h)
        new_w, new_h = int(w * ratio), int(h * ratio)
        clip = clip.resized((new_w, new_h))
        # Center crop
        x1 = (new_w - target_w) // 2
        y1 = (new_h - target_h) // 2
        clip = clip.cropped(x1=x1, y1=y1, width=target_w, height=target_h)

    return {"clip": clip, "temp_files": temp_files}


def build_full_montage(
    clips_config: List[Dict[str, Any]],
    output_path: str,
    target_aspect_ratio: Optional[str] = "9:16",
    background_music_path: Optional[str] = None,
    background_music_volume: float = 0.10,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> str:
    """
    Assembles multiple video clips with effects, voiceovers, transitions, and optional background music.
    clips_config format:
    [
      {
        "video_path": "path/to/clip.mp4",
        "voiceover_text": "Texte lu pour cette vidéo",
        "effect": "noir_et_blanc" | "sepia" | "vibrant" | "contraste" | "aucun",
        "speed": 1.0,
        "keep_original_audio": False,
        "voice": "fr-FR-VivienneNeural"
      },
      ...
    ]
    """
    if not clips_config:
        raise ValueError("Aucune vidéo fournie pour le montage.")

    all_temp_files = []
    processed_clips = []

    total_steps = len(clips_config) + 2
    step = 0

    try:
        for idx, item in enumerate(clips_config):
            step += 1
            if progress_callback:
                pct = step / total_steps
                progress_callback(pct, f"Traitement de la vidéo {idx + 1}/{len(clips_config)}...")

            res = process_video_segment(
                video_path=item["video_path"],
                voiceover_text=item.get("voiceover_text"),
                effect=item.get("effect", "aucun"),
                speed=float(item.get("speed", 1.0)),
                keep_original_audio=bool(item.get("keep_original_audio", False)),
                voice=item.get("voice", "fr-FR-VivienneNeural"),
                target_aspect_ratio=target_aspect_ratio,
            )
            processed_clips.append(res["clip"])
            all_temp_files.extend(res["temp_files"])

        step += 1
        if progress_callback:
            progress_callback(step / total_steps, "Concaténation des séquences vidéo...")

        # Concatenate clips sequentially
        final_video = concatenate_videoclips(processed_clips, method="compose")

        # Add background music if provided
        if background_music_path and os.path.exists(background_music_path):
            try:
                bg_music = AudioFileClip(background_music_path)
                # Loop background music if shorter than video
                if bg_music.duration < final_video.duration:
                    n_loops = int(np.ceil(final_video.duration / bg_music.duration))
                    bg_music = concatenate_audioclips([bg_music] * n_loops)
                bg_music = bg_music.subclipped(0, final_video.duration)
                bg_music = bg_music.with_volume_scaled(background_music_volume)

                if final_video.audio is not None:
                    final_audio = CompositeAudioClip([final_video.audio, bg_music])
                else:
                    final_audio = bg_music

                final_video = final_video.with_audio(final_audio)
            except Exception as e:
                logger.warning(f"Impossible d'ajouter la musique de fond: {e}")

        # Render final file
        if progress_callback:
            progress_callback(0.95, "Encodage du montage final (MP4)...")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        final_video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=24,
            preset="ultrafast",
            threads=2,
            logger=None,
        )

        # Close final clip
        final_video.close()

    finally:
        # Cleanup temporary files
        for f in all_temp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass
        for c in processed_clips:
            try:
                c.close()
            except Exception:
                pass

    if progress_callback:
        progress_callback(1.0, "Montage terminé avec succès !")

    return output_path
