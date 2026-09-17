import asyncio
import io
import logging
import os
import tempfile
from typing import Any, Dict, List, Optional
import imageio_ffmpeg
import requests
from pydub import AudioSegment
from config import settings

logger = logging.getLogger(__name__)

# Configure pydub to use imageio_ffmpeg binary
try:
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    AudioSegment.converter = ffmpeg_exe
    AudioSegment.ffmpeg = ffmpeg_exe
except Exception as e:
    logger.warning(f"Could not set imageio_ffmpeg binary for pydub: {e}")


def _generate_elevenlabs_tts(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> Optional[bytes]:
    """
    Generates TTS audio using ElevenLabs API.
    """
    if not settings.ELEVENLABS_API_KEY or settings.ELEVENLABS_API_KEY.startswith("your_"):
        return None

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": settings.ELEVENLABS_API_KEY,
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.content
        else:
            logger.warning(
                f"ElevenLabs API returned status code {response.status_code}: {response.text}"
            )
    except Exception as e:
        logger.warning(f"ElevenLabs request failed: {e}")

    return None


async def _generate_edge_tts_async(text: str, voice: str = "fr-FR-VivienneNeural") -> bytes:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        await communicate.save(tmp_path)
        with open(tmp_path, "rb") as f:
            data = f.read()
        return data
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _generate_edge_tts(text: str, voice: str = "fr-FR-VivienneNeural") -> Optional[bytes]:
    """
    Generates TTS audio using Microsoft Edge TTS (free & unlimited).
    """
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import nest_asyncio

            nest_asyncio.apply()
            return loop.run_until_complete(_generate_edge_tts_async(text, voice))
        else:
            return asyncio.run(_generate_edge_tts_async(text, voice))
    except Exception as e:
        logger.warning(f"Edge TTS generation failed: {e}")
        return None


def _generate_synthetic_beep(duration_ms: int = 1000) -> AudioSegment:
    """
    Fallback silence/tone audio segment if no external audio decoder or TTS engines are available.
    """
    return AudioSegment.silent(duration=duration_ms)


def generate_tts_for_phrase(
    text: str, voice: str = "fr-FR-VivienneNeural"
) -> AudioSegment:
    """
    Attempts ElevenLabs first, then Edge TTS, then synthetic fallback.
    """
    # 1. ElevenLabs
    eleven_data = _generate_elevenlabs_tts(text)
    if eleven_data:
        try:
            return AudioSegment.from_file(io.BytesIO(eleven_data))
        except Exception as e:
            logger.warning(f"Failed to load ElevenLabs audio data: {e}")

    # 2. Edge TTS
    edge_data = _generate_edge_tts(text, voice=voice)
    if edge_data:
        try:
            return AudioSegment.from_file(io.BytesIO(edge_data))
        except Exception as e:
            logger.warning(f"Failed to load Edge TTS audio data: {e}")

    # 3. Fallback tone/silence based on text length (approx 80ms per char)
    approx_ms = max(1000, len(text) * 80)
    return _generate_synthetic_beep(duration_ms=approx_ms)


def generate_audio_for_script(
    segments: List[Dict[str, Any]],
    output_filename: str = "downloads/combined_audio.wav",
    voice: str = "fr-FR-VivienneNeural",
) -> Dict[str, Any]:
    """
    Generates speech for each segment, concatenates clips with pause_after_ms silences,
    exports final audio file, and tracks exact timings.
    """
    combined_audio = AudioSegment.empty()
    segment_timings = []
    current_time_ms = 0

    os.makedirs(os.path.dirname(output_filename) or ".", exist_ok=True)

    for idx, seg in enumerate(segments):
        phrase_text = seg.get("text", "")
        pause_ms = int(seg.get("pause_after_ms", 300))

        if not phrase_text:
            continue

        clip = generate_tts_for_phrase(phrase_text, voice=voice)
        clip_duration_ms = len(clip)

        start_ms = current_time_ms
        combined_audio += clip
        end_ms = start_ms + clip_duration_ms
        current_time_ms = end_ms

        # Add silence pause after phrase
        if pause_ms > 0:
            silence = AudioSegment.silent(duration=pause_ms)
            combined_audio += silence
            current_time_ms += pause_ms

        segment_timings.append(
            {
                "index": idx,
                "text": phrase_text,
                "start_ms": start_ms,
                "end_ms": end_ms,
                "duration_ms": clip_duration_ms,
                "pause_after_ms": pause_ms,
            }
        )

    # Export final audio file
    total_duration_ms = len(combined_audio)
    actual_output_filename = output_filename
    try:
        if actual_output_filename.endswith(".mp3"):
            combined_audio.export(actual_output_filename, format="mp3")
        else:
            combined_audio.export(actual_output_filename, format="wav")
    except Exception as e:
        logger.warning(f"Failed to export audio file, falling back to WAV: {e}")
        actual_output_filename = os.path.splitext(output_filename)[0] + ".wav"
        combined_audio.export(actual_output_filename, format="wav")

    return {
        "audio_path": actual_output_filename,
        "total_duration_ms": total_duration_ms,
        "total_duration_seconds": round(total_duration_ms / 1000.0, 2),
        "segment_timings": segment_timings,
    }
