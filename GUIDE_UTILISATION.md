# 🎬 Studio de Montage Vidéo Automatisé & Voix Off IA

Bienvenue dans votre studio de montage vidéo automatisé avec voix off intelligente.

---

## ⚡ Démarrage Rapide (En 1 clic)

1. **Double-cliquez sur `lancer_application.bat`**
2. Le script vérifie Python, installe les dépendances nécessaires et ouvre automatiquement l'application dans votre navigateur web (`http://localhost:8501`).

*(Optionnel) Si c'est la toute première fois, vous pouvez aussi double-cliquer sur `installer.bat` pour préparer l'environnement.*

---

## 🚀 Fonctionnalités Clés

### 1. 📥 Importation de vidéos multiples
- Déposez plusieurs vidéos en même temps (formats supportés : `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`).
- L'application prévisualise chaque vidéo dans l'ordre de votre choix.

### 2. 🎙️ Voix off sur mesure pour chaque vidéo
Pour chaque vidéo ajoutée, vous avez 3 choix :
- **Texte personnalisé** : tapez librement ce que la voix off doit dire pendant la vidéo.
- **Extraire le texte de la vidéo (OCR)** : cliquez sur le bouton de détection. Le système analyse les images clés de votre vidéo, extrait automatiquement les textes/titres/panneaux incrustés, et pré-remplit la boîte de texte que vous pouvez réviser.
- **Aucune voix off** : conserve le son original de la vidéo sans voix artificielle.

### 3. 🎨 Choix des effets visuels et réglages par vidéo
- **Filtres de couleur** :
  - Normal (aucun filtre)
  - Noir & Blanc artistique
  - Sépia cinéma
  - Couleurs Vibrantes (boost de saturation)
  - Contraste Élevé
  - Ambiance Vintage
- **Vitesse de lecture** : ajustez de `0.5x` (ralenti) à `2.0x` (accéléré).
- **Gestion du son d'origine** : possibilité de couper complètement le son ou de le conserver en fond sonore léger derrière la voix off.

### 4. ⚙️ Paramètres généraux du montage
- **Choix de la voix IA** : Vivienne (femme dynamique), Henri (homme chaleureux), Remy, Eloise, Denise.
- **Format de sortie vidéo** :
  - **9:16 Vertical** : Parfait pour TikTok, YouTube Shorts et Instagram Reels.
  - **16:9 Horizontal** : Idéal pour YouTube classique et présentations.
  - **Original** : Conserve la résolution de base.
- **Musique de fond (BGM)** : possibilité d'importer une musique de fond MP3/WAV avec réglage du volume.

### 5. ⬇️ Rendu et Téléchargement
- Cliquez sur **"Créer et Exporter le Montage Final"**.
- Une barre de progression suit le traitement en temps réel.
- Le lecteur vous montre directement le résultat final.
- Cliquez sur **"Télécharger le fichier MP4 final"** pour enregistrer votre vidéo prête à l'emploi.

---

## 🛠️ Configuration & Prérequis
- **Python 3.10+** (assurez-vous de cocher *"Add Python to PATH"* lors de l'installation).
- **Tesseract OCR (recommandé pour la détection automatique de texte)** :
  - Sous Windows : installez le programme d'installation Tesseract (ex. `UB-Mannheim/tesseract/wiki`).
  - L'application fonctionne parfaitement même sans Tesseract en utilisant la saisie manuelle de texte.
