# ShortsFactory - Générateur Automatique de YouTube Shorts

**ShortsFactory** est une application Python / FastAPI complète conçue pour générer automatiquement des YouTube Shorts viraux au format vertical 9:16 (1080x1920) avec sous-titres dynamiques et publication sur YouTube.

---

## 🎬 Fonctionnalités Principales (Phases 1 à 4)

1. **Phase 1 - Analyse de Tendances & Restructuration** :
   - Recherche des top 5 Shorts YouTube les plus vus via `yt-dlp`.
   - Génération de scripts viraux de moins de 60 secondes avec Groq (Llama 3.3 70B) ou Gemini (Gemini 1.5 Flash).
   - Découpage du script en tableau JSON structuré (phrases, pauses en ms, mots-clés de recherche en anglais).

2. **Phase 2 - Moteur TTS & Médias Visuels Gratuits** :
   - Génération audio de voix off synthétique via l'API ElevenLabs avec fallback gratuit et illimité via `edge-tts` (Microsoft Edge TTS).
   - Assemblage des extraits audio avec pauses réglables via `pydub`.
   - Récupération automatique de clips vidéos HD au format portrait 9:16 via Pexels API (avec fallback Pixabay API).
   - Téléchargement d'une piste de musique d'ambiance libre de droits.

3. **Phase 3 - Montage Vidéo & Sous-titres Dynamiques** :
   - Génération de sous-titres dynamiques au format `.ASS` (1 à 3 mots par apparition, style TikTok / Shorts : police jaune/blanche avec bordure noire centré en bas).
   - Redimensionnement et recadrage vertical 1080x1920.
   - Mixage audio de la voix off principale et de la musique de fond ajustée à -22dB.
   - Incrustation des sous-titres dynamiques et rendu MP4 via FFmpeg.

4. **Phase 4 - Interface Web & Publication YouTube API** :
   - Dashboard web interactif servi directement par FastAPI sur `http://localhost:8000/`.
   - Publication directe sur YouTube via l'API YouTube Data v3 (OAuth2) avec titre optimisé et hashtags (`#Shorts`).

---

## ⚙️ Prérequis & Installation

### Prérequis Système
- Python 3.11+
- FFmpeg (embarqué automatiquement via la dépendance Python `imageio-ffmpeg` ou installé sur le système)

### Installation des Dépendances
```bash
# Copier le fichier de configuration d'environnement
cp .env.example .env

# Installer les dépendances Python
pip install -r requirements.txt
```

---

## 🔑 Configuration des Clés API (`.env`)

Renseignez vos clés d'API dans le fichier `.env` :

```env
GROQ_API_KEY=votre_cle_groq
GEMINI_API_KEY=votre_cle_gemini
ELEVENLABS_API_KEY=votre_cle_elevenlabs
PEXELS_API_KEY=votre_cle_pexels
PIXABAY_API_KEY=votre_cle_pixabay
```

*Note : ShortsFactory fonctionne également en mode démo avec des fallbacks automatiques si certaines clés ne sont pas renseignées.*

---

## 🚀 Lancement de l'Application

Pour démarrer le serveur FastAPI et l'interface Web :

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Accédez ensuite aux interfaces :
- **Dashboard Web** : `http://localhost:8000/`
- **Documentation API Interactive (Swagger)** : `http://localhost:8000/docs`

---

## 📡 Endpoints FastAPI Récapitulatifs

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/` | Dashboard Web interactif |
| `POST` | `/api/v1/script/from-trend` | Recherche YouTube & génération de script AI |
| `POST` | `/api/v1/script/process-text` | Découpe de texte en JSON (phrases + pauses + keywords) |
| `POST` | `/api/v1/audio/generate` | Génération de la piste audio combinée avec silences |
| `POST` | `/api/v1/media/fetch` | Récupération des vidéos portrait 9:16 et de la musique |
| `POST` | `/api/v1/video/generate-full` | Orchestration complète (Script -> Audio -> Médias -> Montage MP4) |
| `POST` | `/api/v1/youtube/upload` | Publication de la vidéo MP4 sur YouTube |

---

## 🧪 Exécution des Tests Automatisés

```bash
# Lancer les tests unitaires ShortsFactory
python3 -m pytest tests/

# Lancer l'ensemble des tests (ShortsFactory + Plateforme MVB)
python3 -m pytest tests/ backend/tests/
```
