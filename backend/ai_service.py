import os
import json
import requests

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def generate_ai_text(prompt: str, system_prompt: str = "Vous êtes un expert e-commerce et marketing MVB.") -> str:
    if AI_PROVIDER == "openai" and OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=10)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"OpenAI API call error: {e}")

    if (AI_PROVIDER == "gemini" or GEMINI_API_KEY) and GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
            data = {
                "contents": [{"parts": [{"text": f"{system_prompt}\n\n{prompt}"}]}]
            }
            res = requests.post(url, json=data, timeout=10)
            if res.status_code == 200:
                return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"Gemini API call error: {e}")

    return generate_fallback_content(prompt)


def generate_fallback_content(prompt: str) -> str:
    lower_prompt = prompt.lower()
    if "landing" in lower_prompt or "structure" in lower_prompt:
        return json.dumps({
            "main_headline": "Transformez Votre Quotidien Avec Notre Solution Innovante",
            "subheadline": "Découvrez le produit révolutionnaire conçu pour allier confort, efficacité et élégance.",
            "selling_points": [
                "🚀 Innovation brevetée garantie résultats immédiats",
                "🌿 Matériaux haute qualité éco-responsables et durables",
                "🛡️ Garantie satisfaction ou remboursement sous 30 jours",
                "🚚 Livraison express sécurisée offerte dès aujourd'hui"
            ],
            "faq_list": [
                {
                    "question": "Quels sont les délais de livraison ?",
                    "answer": "Expédition sous 24h/48h avec numéro de suivi en direct."
                },
                {
                    "question": "Puis-je retourner le produit s'il ne me convient pas ?",
                    "answer": "Absolument, vous disposez de 30 jours pour nous retourner l'article sans frais."
                },
                {
                    "question": "Le produit est-il garanti ?",
                    "answer": "Oui, tous nos produits bénéficient d'une garantie constructeur de 2 ans."
                }
            ],
            "call_to_action": "Profiter de l'Offre Limitée (-40%)"
        })
    elif "script" in lower_prompt or "video" in lower_prompt or "tiktok" in lower_prompt:
        return json.dumps({
            "script_hook": "Stop ! Ne faites plus JAMAIS cette erreur au quotidien 🛑",
            "script_problem": "Marre d'essayer des méthodes qui ne marchent pas et de perdre votre temps précieux ?",
            "script_solution": "Voici enfin la solution ultime testée et approuvée par plus de 10 000 utilisateurs !",
            "script_cta": "Cliquez rapidement sur le lien en bio pour bénéficier de -30% aujourd'hui seulement !"
        })
    elif "ad copy" in lower_prompt or "publicité" in lower_prompt or "meta" in lower_prompt:
        return json.dumps({
            "ad_copy_meta": "🌟 DÉCOUVREZ L'INNOVATION DE L'ANNÉE !\nVous cherchez un moyen simple et efficace d'améliorer votre confort ? Notre produit vedette est enfin disponible !\n\n✔️ Qualité Supérieure\n✔️ +10 000 clients satisfaits\n✔️ Stock très limité\n\n👉 Profitez de 30% de réduction aujourd'hui seulement !",
            "ad_copy_tiktok": "Attends, tu connais ce produit viral ? 🔥 Tout le monde en parle sur TikTok ! Obtiens le tien avant la rupture de stock 📦 Link in bio !"
        })
    elif "sav" in lower_prompt or "support" in lower_prompt or "email" in lower_prompt:
        return "Bonjour,\n\nMerci de nous avoir contactés ! Nous avons bien pris en compte votre demande. Notre équipe logistique traite actuellement votre dossier et nous vous recontacterons sous 24h avec toutes les précisions requises.\n\nCordialement,\nL'équipe Support Clients"
    else:
        return "Contenu optimisé généré automatiquement pour votre produit MVB."
