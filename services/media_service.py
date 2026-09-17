import logging
import os
from typing import Any, Dict, List, Optional
import requests
from config import settings

logger = logging.getLogger(__name__)


def _download_url_to_file(url: str, target_path: str) -> bool:
    """
    Downloads content from a URL to a local file path.
    """
    os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
    try:
        response = requests.get(url, stream=True, timeout=15)
        if response.status_code == 200:
            with open(target_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            logger.warning(
                f"Download failed with status {response.status_code} for URL: {url}"
            )
    except Exception as e:
        logger.warning(f"Failed to download file from {url}: {e}")
    return False


def search_pexels_vertical_video(keyword: str) -> Optional[Dict[str, Any]]:
    """
    Searches Pexels for a 9:16 portrait vertical video matching keyword.
    """
    if not settings.PEXELS_API_KEY or settings.PEXELS_API_KEY.startswith("your_"):
        return None

    headers = {"Authorization": settings.PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={keyword}&orientation=portrait&per_page=5"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            videos = data.get("videos", [])
            if videos:
                first_video = videos[0]
                # Pick best vertical HD file
                video_files = first_video.get("video_files", [])
                hd_file = None
                for vf in video_files:
                    if vf.get("height", 0) > vf.get("width", 0):
                        hd_file = vf.get("link")
                        break
                if not hd_file and video_files:
                    hd_file = video_files[0].get("link")

                if hd_file:
                    return {
                        "id": first_video.get("id"),
                        "download_url": hd_file,
                        "source": "pexels",
                        "duration": first_video.get("duration"),
                    }
    except Exception as e:
        logger.warning(f"Pexels search failed for keyword '{keyword}': {e}")

    return None


def search_pixabay_vertical_video(keyword: str) -> Optional[Dict[str, Any]]:
    """
    Searches Pixabay for a vertical video matching keyword as fallback.
    """
    if not settings.PIXABAY_API_KEY or settings.PIXABAY_API_KEY.startswith("your_"):
        return None

    url = f"https://pixabay.com/api/videos/?key={settings.PIXABAY_API_KEY}&q={keyword}&orientation=vertical"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            hits = data.get("hits", [])
            if hits:
                first_hit = hits[0]
                videos_dict = first_hit.get("videos", {})
                medium_vid = videos_dict.get("medium") or videos_dict.get("small") or videos_dict.get("large")
                if medium_vid and medium_vid.get("url"):
                    return {
                        "id": first_hit.get("id"),
                        "download_url": medium_vid.get("url"),
                        "source": "pixabay",
                        "duration": first_hit.get("duration"),
                    }
    except Exception as e:
        logger.warning(f"Pixabay search failed for keyword '{keyword}': {e}")

    return None


def fetch_background_music(output_dir: str = "downloads") -> Dict[str, Any]:
    """
    Downloads a royalty-free ambient music track.
    """
    music_file_path = os.path.join(output_dir, "background_music.mp3")
    sample_music_url = "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3"

    if os.path.exists(music_file_path):
        return {
            "music_path": music_file_path,
            "title": "Ambient Royalty Free Track",
            "source": "pixabay_audio",
        }

    success = _download_url_to_file(sample_music_url, music_file_path)
    if not success:
        # Create dummy music file if download fails or offline
        with open(music_file_path, "wb") as f:
            f.write(b"MOCK_BACKGROUND_MUSIC_DATA")

    return {
        "music_path": music_file_path,
        "title": "Ambient Royalty Free Track",
        "source": "pixabay_audio" if success else "mock_audio",
    }


def fetch_media_for_script(
    segments: List[Dict[str, Any]], output_dir: str = "downloads"
) -> Dict[str, Any]:
    """
    Fetches portrait vertical video clips for each segment and background music track.
    """
    os.makedirs(output_dir, exist_ok=True)
    downloaded_clips = []

    for idx, seg in enumerate(segments):
        keyword = seg.get("search_keyword_en", "viral motivation").strip()
        filename = f"clip_seg_{idx+1}_{keyword.replace(' ', '_')}.mp4"
        target_path = os.path.join(output_dir, filename)

        # 1. Search Pexels
        media_info = search_pexels_vertical_video(keyword)

        # 2. Search Pixabay fallback
        if not media_info:
            media_info = search_pixabay_vertical_video(keyword)

        download_success = False
        source = "mock"
        duration = 10

        if media_info and media_info.get("download_url"):
            source = media_info.get("source", "external")
            duration = media_info.get("duration", 10)
            download_success = _download_url_to_file(
                media_info["download_url"], target_path
            )

        if not download_success:
            # Create placeholder video file for test/offline resilience
            with open(target_path, "wb") as f:
                f.write(
                    f"MOCK_PORTRAIT_VIDEO_DATA_FOR_KEYWORD_{keyword}".encode("utf-8")
                )

        downloaded_clips.append(
            {
                "segment_index": idx,
                "keyword": keyword,
                "video_path": target_path,
                "source": source,
                "duration": duration,
            }
        )

    # Download background music
    bg_music = fetch_background_music(output_dir=output_dir)

    return {
        "downloaded_clips": downloaded_clips,
        "background_music": bg_music,
    }
