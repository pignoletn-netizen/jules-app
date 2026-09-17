import json
import logging
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from config import settings

logger = logging.getLogger(__name__)


class ScriptSegment(BaseModel):
    text: str = Field(..., description="La phrase courte à prononcer")
    pause_after_ms: int = Field(
        ..., description="Temps de pause conseillé après la phrase en ms"
    )
    search_keyword_en: str = Field(
        ...,
        description="2-3 mots-clés EN ANGLAIS pour chercher une vidéo d'arrière-plan sur Pexels/Pixabay",
    )


def _clean_json_string(raw_response: str) -> str:
    """
    Cleans markdown formatting backticks from LLM output.
    """
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    # Regex extraction if JSON array is embedded inside extra text
    match = re.search(r"\[\s*\{.*\}\s*\]", cleaned, re.DOTALL)
    if match:
        return match.group(0)

    return cleaned


def _call_groq_json(prompt: str) -> str:
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500,
    )
    return response.choices[0].message.content.strip()


def _call_gemini_json(prompt: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()


def _fallback_process_text(text: str) -> List[Dict[str, Any]]:
    """
    Fallback deterministic text chunker with pacing and keywords.
    """
    raw_sentences = [
        s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()
    ]
    if not raw_sentences:
        raw_sentences = [text.strip()] if text.strip() else ["Bienvenue dans ce Short."]

    results = []
    for sentence in raw_sentences:
        pause_ms = 500 if sentence.endswith(("?", "!")) else 300
        # Simple heuristic keyword generation based on sentence content
        words = re.findall(r"\w+", sentence.lower())
        keywords = "trending viral footage"
        if any(w in words for w in ["crypto", "bitcoin", "argent", "finance", "investir"]):
            keywords = "crypto chart finance"
        elif any(w in words for w in ["travail", "bureau", "motivation", "succès", "travailler"]):
            keywords = "dark office motivation"
        elif any(w in words for w in ["technologie", "ia", "futur", "code", "ordinateur"]):
            keywords = "technology cyber future"

        results.append(
            {
                "text": sentence,
                "pause_after_ms": pause_ms,
                "search_keyword_en": keywords,
            }
        )

    return results


def restructure_text_with_pacing(
    text: str, provider: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Restructures raw script text into a JSON array of objects with text, pause_after_ms, and search_keyword_en.
    """
    if not text or not text.strip():
        return []

    prompt = (
        f"Tu es un monteur vidéo expert en découpage de voix off pour YouTube Shorts.\n"
        f"Prends le texte suivant et découpe-le en une liste JSON d'objets.\n\n"
        f"Chaque objet doit comporter exactement ces 3 clés :\n"
        f'- "text": La phrase courte à prononcer.\n'
        f'- "pause_after_ms": Le temps de pause conseillé en millisecondes après la phrase (ex: 300, 500).\n'
        f'- "search_keyword_en": 2 ou 3 mots-clés EN ANGLAIS pour chercher une vidéo d\'arrière-plan sur Pexels/Pixabay (ex: "dark office motivation", "crypto chart").\n\n'
        f"Format de réponse attendu : UNIQUEMENT un tableau JSON valide sans autre commentaire.\n\n"
        f"Texte à découper :\n{text}"
    )

    raw_response = None

    if provider == "groq" or (not provider and settings.GROQ_API_KEY):
        try:
            raw_response = _call_groq_json(prompt)
        except Exception as e:
            logger.error(f"Groq text restructuring failed: {e}")

    if not raw_response and (
        provider == "gemini" or (not provider and settings.GEMINI_API_KEY)
    ):
        try:
            raw_response = _call_gemini_json(prompt)
        except Exception as e:
            logger.error(f"Gemini text restructuring failed: {e}")

    if raw_response:
        try:
            cleaned_str = _clean_json_string(raw_response)
            parsed_data = json.loads(cleaned_str)

            if isinstance(parsed_data, list):
                validated_data = []
                for item in parsed_data:
                    if isinstance(item, dict) and "text" in item:
                        validated_data.append(
                            {
                                "text": str(item.get("text", "")).strip(),
                                "pause_after_ms": int(
                                    item.get("pause_after_ms", 300)
                                ),
                                "search_keyword_en": str(
                                    item.get("search_keyword_en", "viral video")
                                ).strip(),
                            }
                        )
                if validated_data:
                    return validated_data
        except Exception as e:
            logger.warning(f"Failed to parse LLM JSON output: {e}")

    # Fallback if no LLM configured or parsing failed
    return _fallback_process_text(text)
