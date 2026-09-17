from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.text_service import ScriptSegment, restructure_text_with_pacing
from services.trend_service import generate_script_from_trend

app = FastAPI(
    title="ShortsFactory API",
    description="Application d'analyse de tendances YouTube et de génération de YouTube Shorts.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request & Response Schemas ---


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


# --- Endpoints ---


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "ShortsFactory API"}


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
