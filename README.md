# Plateforme MVB (Mini-Market Validation Business)

Application web complète de gestion, sourcing, validation de marché, marketing IA, SAV automatique et suivi financier pour business MVB / Semi-Marque.

---

## 🚀 Architecture & Stack Technique

- **Backend** : FastAPI (Python 3.11+) + SQLAlchemy + Pydantic v2
- **Frontend** : Next.js 14 App Router (React, TypeScript, Tailwind CSS, Lucide React)
- **Base de données** : PostgreSQL (avec fallback automatique sur SQLite local `mvb.db` si PostgreSQL n'est pas détecté)
- **Authentification** : Tokens JWT (OAuth2 Bearer, hachage PBKDF2/Bcrypt)
- **Intelligence Artificielle** : Intégration modulaire OpenAI API / Gemini API avec fallbacks automatiques
- **Containerisation** : Docker & Docker Compose

---

## 🛠️ Modules Fonctionnels Implémentés

1. **Repérage Produits & Filtres Qualité (Product Hunting)**
   - Score de Viabilité automatique (0-100) basé sur la marge estimée, le volume de recherche, la concurrence et les pénalités de risque.
   - Filtres de risque (complexité, fragilité, note client).

2. **Sourcing & Vérification Fournisseurs Fiables**
   - Annuaire dynamique (Alibaba, Grossistes, Agents).
   - Algorithme Badge "Fiable" (Ancienneté ≥ 3 ans, Verified Supplier, Taux de réponse > 90%).
   - Tableau comparatif : Prix unitaire, MOQ, Frais de port, Délais et Coût de personnalisation.

3. **Validation de Marché (MVB Core) & Landing Page**
   - Générateur de structure de Landing Page haute conversion par IA (titres, arguments de vente, FAQ, CTA).
   - Compteur d'intention d'achat en temps réel (suivi des clics CTA & e-mails capturés sur `/p/[slug]`).

4. **Conformité & Normes Européennes**
   - Checklist réglementaire automatique selon la catégorie de produit (Marquage CE, RoHS, étiquetage en français).
   - Suivi des documents d'importation (Certificats, numéro EORI, factures douanières).

5. **Marketing & Publicité (Génération IA)**
   - Scripts Vidéo TikTok / Reels / Shorts en 4 parties (Hook, Problème, Solution, CTA).
   - Textes publicitaires (Meta Ads & TikTok Ads).
   - Guide Media-Buying : Checklist interactive pas-à-pas pour la configuration des Pixels et du Business Manager.

6. **SAV & Gestion Client**
   - Générateur de réponses automatiques IA aux e-mails clients récurrents (livraison, retours, remboursements, questions).
   - Historique des réponses par produit.

7. **Dashboard Financier & Calculateur de Marge Nette**
   - Formule en temps réel :
     `Marge Nette = Prix Vente - (COGS + Transport/Douane + CAC/Pub + Frais Stripe/PayPal + Cotisations Sociales 12.3%)`

---

## 📦 1. Installation Locale Standard

### Prérequis
- Python 3.11+
- Node.js 18+ / npm

### Étape 1 : Backend (FastAPI)
```bash
# Se placer à la racine du projet
cp .env.example .env

# Installer les dépendances Python
pip install -r backend/requirements.txt

# Lancer le serveur backend
python3 -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
L'API Swagger interactive est disponible sur : `http://localhost:8000/docs`

### Étape 2 : Frontend (Next.js)
```bash
# Se placer dans le dossier frontend
cd frontend

# Installer les dépendances Node.js
npm install

# Lancer le serveur de développement Next.js
npm run dev
```
L'application web est accessible sur : `http://localhost:3000`

---

## 🌱 2. Procédure d'exécution du Script `seed.py`

Le script `seed.py` permet d'alimenter immédiatement la base de données avec 3 produits réels complets, leurs fournisseurs associés, checklists de conformité, scripts marketing et données financières.

```bash
# Exécuter depuis la racine du projet
PYTHONPATH=. python3 seed.py
```

### Identifiants du Compte Démo :
- **E-mail** : `admin@mvb-platform.com`
- **Mot de passe** : `admin123456`

---

## 🐳 3. Exécution avec Docker Compose

Pour orchestrer le Backend FastAPI, le Frontend Next.js et la Base de Données PostgreSQL en une seule commande :

```bash
# Lancer l'ensemble des conteneurs
docker-compose up --build
```

L'application sera opérationnelle sur :
- **Frontend Next.js** : `http://localhost:3000`
- **Backend FastAPI** : `http://localhost:8000`
- **Documentation Swagger** : `http://localhost:8000/docs`
- **PostgreSQL** : `localhost:5432`

---

## 🧪 Exécution des Tests Automatisés

```bash
# Lancer la suite de tests unitaires backend (pytest)
PYTHONPATH=. python3 -m pytest backend/tests/

# Lancer la vérification de build frontend
cd frontend && npm run build
```
