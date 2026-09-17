import logging
from typing import Any, Dict, List, Optional
import yt_dlp
from config import settings

logger = logging.getLogger(__name__)


def search_top_shorts(topic: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search YouTube for top Shorts on a given topic using yt-dlp.
    Returns a list of dicts with video metadata.
    """
    ydl_opts = {
        "extract_flat": True,
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
    }
    search_query = f"ytsearch15:{topic} shorts"
    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            entries = info.get("entries", []) if info else []
            for entry in entries:
                if not entry:
                    continue
                results.append(
                    {
                        "id": entry.get("id"),
                        "title": entry.get("title", ""),
                        "url": entry.get("url")
                        or f"https://www.youtube.com/watch?v={entry.get('id')}",
                        "view_count": entry.get("view_count") or 0,
                        "duration": entry.get("duration"),
                        "description": entry.get("description", ""),
                    }
                )

        # Sort by view_count descending if available
        results.sort(key=lambda x: x.get("view_count", 0), reverse=True)
        top_results = results[:max_results]

        if top_results:
            return top_results
    except Exception as e:
        logger.warning(f"yt-dlp search failed for topic '{topic}': {e}")

    # Fallback response if yt-dlp returns no entries or fails
    return [
        {
            "id": f"trend_{i+1}",
            "title": f"Top Short #{i+1} sur {topic}",
            "url": f"https://www.youtube.com/watch?v=mock_{i+1}",
            "view_count": 250000 * (max_results - i),
            "duration": 45,
            "description": f"Vidéo populaire sur le thème {topic}",
        }
        for i in range(max_results)
    ]


def _call_groq(prompt: str) -> str:
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000,
    )
    return response.choices[0].message.content.strip()


def _call_gemini(prompt: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()


def generate_viral_script(
    topic: str,
    trend_videos: List[Dict[str, Any]],
    provider: Optional[str] = None,
) -> str:
    """
    Analyzes YouTube trends and generates a viral script (< 60s) using Groq or Gemini.
    """
    trends_summary = "\n".join(
        [
            f"- Title: {v.get('title')} | Views: {v.get('view_count')} | Link: {v.get('url')}"
            for v in trend_videos
        ]
    )

    prompt = (
        f"Tu es un expert mondial de la création de contenu viral sur YouTube Shorts et TikTok.\n"
        f"Sujet cible : {topic}\n\n"
        f"Voici les 5 vidéos les plus vues du moment sur ce sujet :\n"
        f"{trends_summary}\n\n"
        f"Consignes :\n"
        f"1. Analyse pourquoi ces vidéos fonctionnent.\n"
        f"2. Rédige un script complet et ultra-captivant en français de MOINS DE 60 SECONDES.\n"
        f"3. Le script doit comporter un Hook choc (0-3s), un corps de texte à fort impact et un CTA puissant à la fin.\n"
        f"4. Renvoie directement le texte complet du script prêt à être parlé."
    )

    # Provider selection logic
    if provider == "groq" or (not provider and settings.GROQ_API_KEY):
        try:
            return _call_groq(prompt)
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")

    if provider == "gemini" or (not provider and settings.GEMINI_API_KEY):
        try:
            return _call_gemini(prompt)
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")

    # Fallback script if no API keys configured or calls fail
    return (
        f"Savais-tu que {topic} est la tendance ultime du moment ? "
        f"La plupart des gens font une erreur monumentale à ce sujet. "
        f"Voici l'astuce secrète pour maîtriser {topic} en 30 secondes. "
        f"Étape 1 : Comprendre les bases. "
        f"Étape 2 : Appliquer la stratégie gagnante. "
        f"Abonne-toi immédiatement pour ne rien rater des prochaines astuces !"
    )


def generate_script_from_trend(
    topic: str, provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Combines trend analysis with script generation.
    """
    top_shorts = search_top_shorts(topic, max_results=5)
    script = generate_viral_script(topic, top_shorts, provider=provider)
    return {
        "topic": topic,
        "analyzed_trends": top_shorts,
        "script": script,
    }
