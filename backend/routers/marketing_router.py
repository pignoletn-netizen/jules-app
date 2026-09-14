import json
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models, schemas_marketing_fin
from backend.routers.auth_router import get_current_user
from backend.ai_service import generate_ai_text

router = APIRouter(prefix="/api/marketing", tags=["Marketing & Publicité"])


DEFAULT_MEDIA_BUYING_GUIDE = [
    {
        "id": "pixel_meta",
        "step": "Étape 1",
        "title": "Configuration du Meta Pixel",
        "description": "Créez et intégrez le Pixel Facebook/Meta sur votre landing page pour suivre les événements PageView, Lead et InitiateCheckout.",
        "is_completed": False
    },
    {
        "id": "pixel_tiktok",
        "step": "Étape 2",
        "title": "Configuration du TikTok Pixel",
        "description": "Installez le Pixel TikTok avec l'Events API pour optimiser vos campagnes vidéo TikTok Ads.",
        "is_completed": False
    },
    {
        "id": "bm_setup",
        "step": "Étape 3",
        "title": "Business Manager & Domaine",
        "description": "Vérifiez votre nom de domaine personnalisé dans le Meta Business Manager et configurez la mesure des événements agrégés (AEM).",
        "is_completed": False
    },
    {
        "id": "campaign_structure",
        "step": "Étape 4",
        "title": "Structure des Campagnes ABO/CBO",
        "description": "Lancez 1 campagne CBO ou 3 adsets ABO ciblés avec 3 créatives vidéos testées en parallèle.",
        "is_completed": False
    }
]


@router.post("/generate", response_model=schemas_marketing_fin.MarketingContentOut, status_code=status.HTTP_201_CREATED)
def generate_marketing_content(
    req: schemas_marketing_fin.MarketingGenerateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    product = (
        db.query(models.Product)
        .filter(models.Product.id == req.product_id, models.Product.user_id == current_user.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    prompt = (
        f"Génère un script vidéo TikTok/Reels en 4 parties (hook, problem, solution, cta) "
        f"et deux Ad Copies (meta, tiktok) pour le produit: '{product.title}'. "
        f"Description: '{product.description}'. "
        f"Angle spécifique: '{req.custom_angle or 'Haute conversion et bénéfices client'}'. "
        f"Format JSON requis avec les clés: script_hook, script_problem, script_solution, script_cta, ad_copy_meta, ad_copy_tiktok."
    )

    ai_raw = generate_ai_text(prompt, system_prompt="Génère un JSON valide pour le marketing e-commerce.")

    try:
        match = re.search(r"\{.*\}", ai_raw, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
        else:
            data = json.loads(ai_raw)
    except Exception:
        data = {
            "script_hook": f"Ne commettez plus cette erreur avec votre {product.category} 🛑",
            "script_problem": "Vous en avez marre des produits inefficaces qui tombent en panne après 2 semaines ?",
            "script_solution": f"Découvrez notre {product.title}, conçu pour durer et vous faciliter la vie au quotidien !",
            "script_cta": "Lien en bio pour profiter de -30% immédiats aujourd'hui 🚀",
            "ad_copy_meta": f"🌟 OFFRE SPÉCIALE - {product.title}\nOffrez-vous la qualité supérieure avec notre nouveau {product.title}.\n✔️ Livraison 24/48h\n✔️ Garantie Satisfait ou Remboursé\n👉 Cliquez ici pour en profiter !",
            "ad_copy_tiktok": f"Ce {product.title} est enfin disponible ! 🔥 +10,000 clients déjà conquis. Ne ratez pas l'offre limitée !"
        }

    marketing = models.MarketingContent(
        product_id=product.id,
        script_hook=data.get("script_hook", ""),
        script_problem=data.get("script_problem", ""),
        script_solution=data.get("script_solution", ""),
        script_cta=data.get("script_cta", ""),
        ad_copy_meta=data.get("ad_copy_meta", ""),
        ad_copy_tiktok=data.get("ad_copy_tiktok", "")
    )
    db.add(marketing)
    db.commit()
    db.refresh(marketing)

    return schemas_marketing_fin.MarketingContentOut(
        id=marketing.id,
        product_id=marketing.product_id,
        video_script=schemas_marketing_fin.VideoScriptOut(
            hook=marketing.script_hook,
            problem=marketing.script_problem,
            solution=marketing.script_solution,
            cta=marketing.script_cta
        ),
        ad_copies=schemas_marketing_fin.AdCopiesOut(
            meta=marketing.ad_copy_meta,
            tiktok=marketing.ad_copy_tiktok
        ),
        created_at=marketing.created_at
    )


@router.get("/guide", response_model=List[schemas_marketing_fin.MediaBuyingCheckitem])
def get_media_buying_guide():
    return DEFAULT_MEDIA_BUYING_GUIDE
