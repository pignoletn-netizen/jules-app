import os
import shutil
import tempfile
import streamlit as st
from services.video_editor_service import (
    build_full_montage,
    extract_text_from_video,
)

st.set_page_config(
    page_title="Studio Montage Vidéo & Voix Off IA",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .video-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #E2E8F0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# App directories
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "studio_montage_uploads")
OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "studio_montage_outputs")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# State initialization
if "video_list" not in st.session_state:
    st.session_state.video_list = []
if "extracted_texts" not in st.session_state:
    st.session_state.extracted_texts = {}
if "custom_texts" not in st.session_state:
    st.session_state.custom_texts = {}
if "video_effects" not in st.session_state:
    st.session_state.video_effects = {}
if "video_speeds" not in st.session_state:
    st.session_state.video_speeds = {}
if "keep_audios" not in st.session_state:
    st.session_state.keep_audios = {}
if "final_video_path" not in st.session_state:
    st.session_state.final_video_path = None

# Sidebar: Global Settings
with st.sidebar:
    st.header("⚙️ Paramètres Généraux")

    st.subheader("Voix de narration")
    VOICE_OPTIONS = {
        "Vivienne (Français - Naturel & Dynamique, Femme)": "fr-FR-VivienneNeural",
        "Henri (Français - Chaleureux & Posé, Homme)": "fr-FR-HenriNeural",
        "Remy (Français - Jeune & Dynamique, Homme)": "fr-FR-RemyMultilingualNeural",
        "Eloise (Français - Douce & Expressive, Femme)": "fr-FR-EloiseNeural",
        "Denise (Français - Professionnelle, Femme)": "fr-FR-DeniseNeural",
    }
    selected_voice_label = st.selectbox(
        "Voix Off principale :",
        list(VOICE_OPTIONS.keys()),
        index=0,
    )
    selected_voice = VOICE_OPTIONS[selected_voice_label]

    st.subheader("Format du Montage")
    format_option = st.selectbox(
        "Ratio d'affichage :",
        [
            "Format Réseaux Sociaux (9:16 Vertical - TikTok/Reels/Shorts)",
            "Format Classique (16:9 Horizontal - YouTube/Web)",
            "Conserver format original",
        ],
        index=0,
    )
    if "9:16" in format_option:
        target_aspect_ratio = "9:16"
    elif "16:9" in format_option:
        target_aspect_ratio = "16:9"
    else:
        target_aspect_ratio = None

    st.subheader("Musique de fond (Optionnel)")
    bg_music_file = st.file_uploader(
        "Ajouter une piste musicale (MP3/WAV)",
        type=["mp3", "wav", "m4a"],
        key="bg_music_uploader",
    )
    bg_music_vol = st.slider(
        "Volume de la musique de fond",
        min_value=0.0,
        max_value=0.5,
        value=0.10,
        step=0.02,
        format="%.2f",
    )

    st.divider()
    st.caption("💡 Cliquez sur '.bat' à tout moment sous Windows pour relancer.")

# Header
st.markdown('<div class="main-title">🎬 Studio de Montage Automatisé & Voix Off</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Importez vos vidéos, choisissez les effets visuels, et posez la voix off automatiquement (soit via détection de texte dans la vidéo, soit avec votre texte personnalisé).</div>',
    unsafe_allow_html=True,
)

# Upload Section
uploaded_files = st.file_uploader(
    "📥 Choisissez ou glissez vos vidéos ici (MP4, MOV, MKV, AVI, WEBM)",
    type=["mp4", "mov", "mkv", "avi", "webm"],
    accept_multiple_files=True,
    help="Vous pouvez sélectionner plusieurs vidéos d'un coup.",
)

# Process uploaded files
if uploaded_files:
    current_names = [f.name for f in uploaded_files]
    saved_list = []
    for file in uploaded_files:
        save_path = os.path.join(UPLOAD_DIR, file.name)
        if not os.path.exists(save_path):
            with open(save_path, "wb") as f:
                f.write(file.getbuffer())
        saved_list.append(save_path)
    st.session_state.video_list = saved_list

if not st.session_state.video_list:
    st.info("👈 Commencez par importer une ou plusieurs vidéos ci-dessus pour configurer votre montage.")
else:
    st.subheader(f"📋 Configuration des {len(st.session_state.video_list)} vidéos")
    st.caption("Pour chaque vidéo : choisissez le texte de voix off (auto via OCR ou saisi) et vos effets visuels.")

    configured_clips = []

    for idx, vid_path in enumerate(st.session_state.video_list):
        fname = os.path.basename(vid_path)
        with st.expander(f"Vidéo #{idx + 1} : {fname}", expanded=True):
            col_preview, col_text, col_effects = st.columns([1.2, 1.8, 1.2])

            with col_preview:
                st.video(vid_path)
                st.caption(f"Fichier : `{fname}`")

            with col_text:
                st.markdown("**🎙️ Voix Off sur cette vidéo**")
                text_mode = st.radio(
                    f"Origine de la voix ({fname}) :",
                    ["Texte personnalisé", "Extraire le texte de la vidéo (OCR)", "Aucune voix off (son original)"],
                    key=f"mode_{idx}",
                    horizontal=True,
                )

                if text_mode == "Extraire le texte de la vidéo (OCR)":
                    if st.button(f"🔍 Détecter le texte dans la vidéo #{idx + 1}", key=f"btn_ocr_{idx}"):
                        with st.spinner("Analyse OCR des images clés en cours..."):
                            extracted = extract_text_from_video(vid_path)
                            st.session_state.extracted_texts[vid_path] = extracted
                            if extracted:
                                st.success("Texte détecté avec succès !")
                            else:
                                st.warning("Aucun texte lisible détecté. Vous pouvez le saisir manuellement.")

                    current_ocr = st.session_state.extracted_texts.get(vid_path, "")
                    final_text = st.text_area(
                        "Texte extrait (modifiable avant génération) :",
                        value=current_ocr,
                        key=f"ocr_edit_{idx}",
                        height=100,
                    )
                elif text_mode == "Texte personnalisé":
                    final_text = st.text_area(
                        "Tapez le texte que la voix doit prononcer pour cette vidéo :",
                        value=st.session_state.custom_texts.get(vid_path, ""),
                        placeholder="Exemple : Découvrez cette nouvelle astuce incroyable pour réussir vos projets !",
                        key=f"text_custom_{idx}",
                        height=100,
                    )
                    st.session_state.custom_texts[vid_path] = final_text
                else:
                    final_text = ""
                    st.info("Cette vidéo conservera uniquement son son d'origine sans voix off ajoutée.")

            with col_effects:
                st.markdown("**🎨 Effets & Réglages**")
                effect_choice = st.selectbox(
                    "Filtre d'effet vidéo :",
                    [
                        "aucun",
                        "noir_et_blanc",
                        "sepia",
                        "vibrant",
                        "contraste",
                        "vintage",
                    ],
                    format_func=lambda x: {
                        "aucun": "Normal (Aucun filtre)",
                        "noir_et_blanc": "Noir & Blanc",
                        "sepia": "Effet Sépia",
                        "vibrant": "Couleurs Vibrantes",
                        "contraste": "Contraste Élevé",
                        "vintage": "Ambiance Vintage",
                    }.get(x, x),
                    key=f"effect_{idx}",
                )

                speed_val = st.select_slider(
                    "Vitesse de lecture :",
                    options=[0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
                    value=1.0,
                    format_func=lambda s: f"{s}x",
                    key=f"speed_{idx}",
                )

                keep_audio_choice = st.checkbox(
                    "Conserver l'audio d'origine en fond",
                    value=False if final_text else True,
                    key=f"keep_audio_{idx}",
                    help="Si la voix off est activée, l'audio d'origine est automatiquement réduit pour ne pas couvrir la voix.",
                )

            configured_clips.append(
                {
                    "video_path": vid_path,
                    "voiceover_text": final_text,
                    "effect": effect_choice,
                    "speed": speed_val,
                    "keep_original_audio": keep_audio_choice,
                    "voice": selected_voice,
                }
            )

    st.markdown("---")

    # Render Button
    col_btn, col_empty = st.columns([2, 3])
    with col_btn:
        generate_clicked = st.button(
            "🚀 Créer et Exporter le Montage Final",
            type="primary",
            use_container_width=True,
        )

    if generate_clicked:
        st.session_state.final_video_path = None
        output_filename = os.path.join(OUTPUT_DIR, "montage_final.mp4")

        # Background music file path if uploaded
        bg_path = None
        if bg_music_file:
            bg_path = os.path.join(UPLOAD_DIR, bg_music_file.name)
            with open(bg_path, "wb") as f:
                f.write(bg_music_file.getbuffer())

        progress_bar = st.progress(0.0)
        status_text = st.empty()

        def update_progress(pct: float, message: str):
            progress_bar.progress(pct)
            status_text.info(f"⏳ {message}")

        try:
            with st.spinner("Génération du montage en cours..."):
                final_path = build_full_montage(
                    clips_config=configured_clips,
                    output_path=output_filename,
                    target_aspect_ratio=target_aspect_ratio,
                    background_music_path=bg_path,
                    background_music_volume=bg_music_vol,
                    progress_callback=update_progress,
                )
                st.session_state.final_video_path = final_path
                status_text.success("🎉 Montage vidéo généré avec succès !")
        except Exception as e:
            status_text.error(f"❌ Une erreur est survenue lors de la création : {str(e)}")

# Display Final Result
if st.session_state.final_video_path and os.path.exists(st.session_state.final_video_path):
    st.markdown("---")
    st.subheader("🎥 Résultat Final du Montage")

    res_col1, res_col2 = st.columns([2, 1])
    with res_col1:
        st.video(st.session_state.final_video_path)

    with res_col2:
        st.success("Le rendu vidéo est prêt !")
        with open(st.session_state.final_video_path, "rb") as f:
            video_bytes = f.read()

        st.download_button(
            label="⬇️ Télécharger le fichier MP4 final",
            data=video_bytes,
            file_name="montage_video_complet.mp4",
            mime="video/mp4",
            type="primary",
            use_container_width=True,
        )

        st.info(f"📁 Fichier disponible localement à l'emplacement :\n`{st.session_state.final_video_path}`")
