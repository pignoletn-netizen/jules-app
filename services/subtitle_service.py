import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def format_ass_time(ms: int) -> str:
    """
    Formats milliseconds into ASS timestamp format: H:MM:SS.cs
    """
    total_seconds = max(0, ms) / 1000.0
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    cs = int(round((total_seconds - int(total_seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{hours}:{minutes:02d}:{seconds:02d}.{cs:02d}"


def chunk_phrase_into_words(text: str, max_words: int = 3) -> List[str]:
    """
    Splits text into chunks containing 1 to max_words words.
    """
    words = text.strip().split()
    if not words:
        return []

    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i : i + max_words])
        chunks.append(chunk)

    return chunks


def generate_ass_subtitles(
    segment_timings: List[Dict[str, Any]],
    output_filename: str = "downloads/subtitles.ass",
    font_name: str = "Arial",
    font_size: int = 72,
) -> str:
    """
    Generates an Advanced SubStation Alpha (.ASS) subtitle file styled for Shorts/TikTok:
    - Bold Impact/Arial font
    - Bright Yellow text (&H0000FFFF in BGR) with 2-3px black outline (&H00000000)
    - Centered bottom-middle screen alignment
    - 1 to 3 words per subtitle box for high retention
    """
    os.makedirs(os.path.dirname(output_filename) or ".", exist_ok=True)

    header = f"""[Script Info]
Title: ShortsFactory Dynamic Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ShortsStyle,{font_name},{font_size},&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,50,50,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []

    for seg in segment_timings:
        text = seg.get("text", "").strip()
        start_ms = seg.get("start_ms", 0)
        end_ms = seg.get("end_ms", start_ms + 1000)

        if not text:
            continue

        word_chunks = chunk_phrase_into_words(text, max_words=3)
        if not word_chunks:
            continue

        seg_duration = max(200, end_ms - start_ms)
        chunk_duration = seg_duration / len(word_chunks)

        for idx, chunk in enumerate(word_chunks):
            chunk_start = start_ms + int(idx * chunk_duration)
            chunk_end = start_ms + int((idx + 1) * chunk_duration)

            start_str = format_ass_time(chunk_start)
            end_str = format_ass_time(chunk_end)

            # Uppercase for Shorts/TikTok dynamic style
            display_text = f"{{\\b1}}{chunk.upper()}{{\\b0}}"
            line = f"Dialogue: 0,{start_str},{end_str},ShortsStyle,,0,0,0,,{display_text}"
            events.append(line)

    content = header + "\n".join(events) + "\n"

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    return output_filename
