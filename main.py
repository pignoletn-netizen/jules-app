import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.audio_service import generate_audio_for_script
from services.media_service import fetch_media_for_script
from services.subtitle_service import generate_ass_subtitles
from services.text_service import ScriptSegment, restructure_text_with_pacing
from services.trend_service import generate_script_from_trend
from services.video_service import render_final_video

app = FastAPI(
    title="ShortsFactory API",
    description="Application d'analyse de tendances YouTube, de génération de scripts, moteur TTS audio, médias visuels et montage vidéo autonome.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Phase 1 Schemas ---


class TrendScriptRequest(BaseModel):
    topic: str = Field(..., description="Le sujet pour la recherche de tendances YouTube")
    provider: Optional[str] = Field(
        None, description="Fournisseur LLM facultatif ('groq' ou 'gemini')"
    )


class AnalyzedTrend(BaseModel):
    id: Optional[str] = None
    title: str
    url: str
    view_count: int
    duration: Optional[int] = None
    description: Optional[str] = None


class TrendScriptResponse(BaseModel):
    topic: str
    analyzed_trends: List[AnalyzedTrend]
    script: str


class ProcessTextRequest(BaseModel):
    text: str = Field(..., description="Texte brut du script à restructurer")
    provider: Optional[str] = Field(
        None, description="Fournisseur LLM facultatif ('groq' ou 'gemini')"
    )


# --- Phase 2 Schemas ---


class AudioGenerateRequest(BaseModel):
    segments: List[ScriptSegment] = Field(
        ..., description="Liste des segments structurés (phrases + pauses)"
    )
    voice: Optional[str] = Field(
        "fr-FR-VivienneNeural", description="Voix TTS Edge / ElevenLabs"
    )
    output_filename: Optional[str] = Field(
        "downloads/combined_audio.wav", description="Chemin d'export du fichier audio"
    )


class SegmentTiming(BaseModel):
    index: int
    text: str
    start_ms: int
    end_ms: int
    duration_ms: int
    pause_after_ms: int


class AudioGenerateResponse(BaseModel):
    audio_path: str
    total_duration_ms: int
    total_duration_seconds: float
    segment_timings: List[SegmentTiming]


class MediaFetchRequest(BaseModel):
    segments: List[ScriptSegment] = Field(
        ..., description="Liste des segments structurés avec mots-clés"
    )
    output_dir: Optional[str] = Field(
        "downloads", description="Dossier de destination pour les fichiers"
    )


class DownloadedClip(BaseModel):
    segment_index: int
    keyword: str
    video_path: str
    source: str
    duration: float


class BackgroundMusicInfo(BaseModel):
    music_path: str
    title: str
    source: str


class MediaFetchResponse(BaseModel):
    downloaded_clips: List[DownloadedClip]
    background_music: BackgroundMusicInfo


# --- Phase 3 Schemas ---


class GenerateFullVideoRequest(BaseModel):
    topic: Optional[str] = Field(
        None, description="Sujet de recherche YouTube (optionnel si texte fourni)"
    )
    text: Optional[str] = Field(
        None, description="Texte brut du script (optionnel si sujet fourni)"
    )
    provider: Optional[str] = Field(
        None, description="Fournisseur LLM ('groq' ou 'gemini')"
    )
    voice: Optional[str] = Field(
        "fr-FR-VivienneNeural", description="Voix TTS Edge / ElevenLabs"
    )
    output_dir: Optional[str] = Field(
        "downloads", description="Dossier de destination"
    )


class GenerateFullVideoResponse(BaseModel):
    video_path: str
    topic_or_text: str
    script: str
    duration_seconds: float
    resolution: str
    audio_path: str
    subtitles_path: str
    segment_count: int


# --- Endpoints ---


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "ShortsFactory API"}


# Phase 1 Endpoints
@app.post(
    "/api/v1/script/from-trend",
    response_model=TrendScriptResponse,
    status_code=status.HTTP_200_OK,
    summary="Génère un script viral basé sur une recherche de tendances YouTube Shorts",
)
def create_script_from_trend(payload: TrendScriptRequest):
    if not payload.topic or not payload.topic.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le paramètre 'topic' ne peut pas être vide.",
        )

    try:
        result = generate_script_from_trend(
            topic=payload.topic.strip(), provider=payload.provider
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération du script : {str(e)}",
        )


@app.post(
    "/api/v1/script/process-text",
    response_model=List[ScriptSegment],
    status_code=status.HTTP_200_OK,
    summary="Découpe un texte brut en tableau JSON structuré (phrases + pauses + keywords anglais)",
)
def process_text_script(payload: ProcessTextRequest):
    if not payload.text or not payload.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le texte d'entrée ne peut pas être vide.",
        )

    try:
        segments = restructure_text_with_pacing(
            text=payload.text, provider=payload.provider
        )
        return segments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la restructuration du texte : {str(e)}",
        )


# Phase 2 Endpoints
@app.post(
    "/api/v1/audio/generate",
    response_model=AudioGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Génère l'audio combiné avec silences à partir de la structure JSON",
)
def generate_audio_endpoint(payload: AudioGenerateRequest):
    if not payload.segments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La liste de segments ne peut pas être vide.",
        )

    try:
        dict_segments = [s.model_dump() for s in payload.segments]
        result = generate_audio_for_script(
            segments=dict_segments,
            output_filename=payload.output_filename or "downloads/combined_audio.wav",
            voice=payload.voice or "fr-FR-VivienneNeural",
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération audio : {str(e)}",
        )


@app.post(
    "/api/v1/media/fetch",
    response_model=MediaFetchResponse,
    status_code=status.HTTP_200_OK,
    summary="Télécharge les vidéos portrait HD (Pexels/Pixabay) et la musique libre de droits",
)
def fetch_media_endpoint(payload: MediaFetchRequest):
    if not payload.segments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La liste de segments ne peut pas être vide.",
        )

    try:
        dict_segments = [s.model_dump() for s in payload.segments]
        result = fetch_media_for_script(
            segments=dict_segments, output_dir=payload.output_dir or "downloads"
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des médias : {str(e)}",
        )


# Phase 3 Orchestration Endpoint
@app.post(
    "/api/v1/video/generate-full",
    response_model=GenerateFullVideoResponse,
    status_code=status.HTTP_200_OK,
    summary="Orchestre la chaîne complète (Script -> Audio -> Médias -> Montage + Sous-titres)",
)
def generate_full_video_endpoint(payload: GenerateFullVideoRequest):
    if not payload.topic and not payload.text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veuillez fournir au moins un 'topic' ou un 'text'.",
        )

    out_dir = payload.output_dir or "downloads"
    os.makedirs(out_dir, exist_ok=True)

    try:
        # 1. Script Generation / Choice
        if payload.text and payload.text.strip():
            script = payload.text.strip()
            topic_or_text = script[:30] + "..."
        else:
            trend_res = generate_script_from_trend(
                topic=payload.topic.strip(), provider=payload.provider
            )
            script = trend_res["script"]
            topic_or_text = payload.topic.strip()

        # 2. Text Restructuring & Pacing
        segments = restructure_text_with_pacing(text=script, provider=payload.provider)

        # 3. Audio TTS Generation
        audio_out_path = os.path.join(out_dir, "voice_audio.wav")
        audio_res = generate_audio_for_script(
            segments=segments,
            output_filename=audio_out_path,
            voice=payload.voice or "fr-FR-VivienneNeural",
        )

        # 4. Media Fetching (Pexels / Pixabay)
        media_res = fetch_media_for_script(segments=segments, output_dir=out_dir)

        # 5. Dynamic ASS Subtitles Generation
        ass_out_path = os.path.join(out_dir, "subtitles.ass")
        subtitles_path = generate_ass_subtitles(
            segment_timings=audio_res["segment_timings"],
            output_filename=ass_out_path,
        )

        # 6. Video Rendering & Assembly
        final_mp4_path = os.path.join(out_dir, "final_short.mp4")
        video_res = render_final_video(
            clips_info=media_res["downloaded_clips"],
            voice_audio_path=audio_res["audio_path"],
            bg_music_path=media_res["background_music"]["music_path"],
            subtitle_ass_path=subtitles_path,
            segment_timings=audio_res["segment_timings"],
            output_mp4_path=final_mp4_path,
        )

        return {
            "video_path": video_res["video_path"],
            "topic_or_text": topic_or_text,
            "script": script,
            "duration_seconds": video_res["duration_seconds"],
            "resolution": video_res["resolution"],
            "audio_path": audio_res["audio_path"],
            "subtitles_path": subtitles_path,
            "segment_count": len(segments),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération complète de la vidéo : {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
