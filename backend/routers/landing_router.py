import json
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models, schemas_mvb
from backend.routers.auth_router import get_current_user
from backend.ai_service import generate_ai_text

router = APIRouter(prefix="/api/landing-pages", tags=["Landing Page & MVB Validation"])


@router.post("/generate", response_model=schemas_mvb.LandingPageOut, status_code=status.HTTP_201_CREATED)
def generate_landing_page(
    req: schemas_mvb.LandingPageGenerateRequest,
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

    existing_slug = db.query(models.LandingPage).filter(models.LandingPage.slug == req.slug).first()
    if existing_slug:
        raise HTTPException(status_code=400, detail="Slug already exists. Choose a unique slug.")

    prompt = f"Génère la structure JSON d'une landing page haute conversion pour le produit: '{product.title}'. Description: '{product.description}'. Catégorie: '{product.category}'."
    if req.custom_instructions:
        prompt += f" Instructions supplémentaires: {req.custom_instructions}"

    ai_raw = generate_ai_text(prompt, system_prompt="Génère un JSON valide contenant main_headline, subheadline, selling_points (liste), faq_list (liste d'objets {question, answer}), call_to_action.")

    try:
        match = re.search(r"\{.*\}", ai_raw, re.DOTALL)
        if match:
            content = json.loads(match.group(0))
        else:
            content = json.loads(ai_raw)
    except Exception:
        content = {
            "main_headline": f"Découvrez {product.title}",
            "subheadline": product.description or "La solution idéale pour vos besoins au quotidien.",
            "selling_points": ["Produit testé et approuvé", "Livraison rapide et sécurisée", "Satisfait ou remboursé sous 30 jours"],
            "faq_list": [{"question": "Quand vais-je recevoir ma commande ?", "answer": "Livraison en 24h à 48h."}],
            "call_to_action": "Valider mon offre"
        }

    landing = models.LandingPage(
        slug=req.slug,
        title=f"Landing - {product.title}",
        main_headline=content.get("main_headline", f"Découvrez {product.title}"),
        subheadline=content.get("subheadline", product.description or "Offre exclusive"),
        selling_points=content.get("selling_points", []),
        faq_list=content.get("faq_list", []),
        call_to_action=content.get("call_to_action", "Commander"),
        click_count=0,
        email_count=0,
        product_id=product.id,
        user_id=current_user.id,
    )
    db.add(landing)
    db.commit()
    db.refresh(landing)
    return landing


@router.get("", response_model=List[schemas_mvb.LandingPageOut])
def get_landing_pages(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.LandingPage).filter(models.LandingPage.user_id == current_user.id).all()


@router.get("/public/{slug}", response_model=schemas_mvb.PublicLandingPageOut)
def get_public_landing_page(
    slug: str,
    db: Session = Depends(get_db)
):
    landing = db.query(models.LandingPage).filter(models.LandingPage.slug == slug).first()
    if not landing:
        raise HTTPException(status_code=404, detail="Landing page non trouvée")
    return landing


@router.post("/public/{slug}/intent", response_model=schemas_mvb.IntentOut, status_code=status.HTTP_201_CREATED)
def register_public_intent(
    slug: str,
    intent_req: schemas_mvb.IntentRegisterRequest,
    db: Session = Depends(get_db)
):
    landing = db.query(models.LandingPage).filter(models.LandingPage.slug == slug).first()
    if not landing:
        raise HTTPException(status_code=404, detail="Landing page non trouvée")

    if intent_req.action_type == "click":
        landing.click_count += 1
    elif intent_req.action_type == "email_signup":
        landing.email_count += 1

    intent = models.PublicIntent(
        landing_page_id=landing.id,
        action_type=intent_req.action_type,
        email=intent_req.email
    )
    db.add(intent)
    db.commit()
    db.refresh(intent)
    return intent
