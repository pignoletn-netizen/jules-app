from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.audio_service import generate_audio_for_script
from services.media_service import fetch_media_for_script
from services.text_service import ScriptSegment, restructure_text_with_pacing
from services.trend_service import generate_script_from_trend

app = FastAPI(
    title="ShortsFactory API",
    description="Application d'analyse de tendances YouTube, de génération de scripts, moteur TTS audio et médias visuels.",
    version="2.0.0",
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
        "downloads/combined_audio.mp3", description="Chemin d'export du fichier audio"
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
            output_filename=payload.output_filename or "downloads/combined_audio.mp3",
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
