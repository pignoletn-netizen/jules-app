from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models, schemas_marketing_fin
from backend.routers.auth_router import get_current_user
from backend.ai_service import generate_ai_text

router = APIRouter(prefix="/api/sav", tags=["SAV & Gestion Client"])


@router.post("/generate", response_model=schemas_marketing_fin.SAVResponseOut, status_code=status.HTTP_201_CREATED)
def generate_sav_reply(
    req: schemas_marketing_fin.SAVGenerateRequest,
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
        f"Rédige une réponse courtoise, professionnelle et rassurante en français pour un service client e-commerce. "
        f"Produit: '{product.title}'. "
        f"Type de demande: '{req.inquiry_type}'. "
        f"Message reçu du client: '{req.incoming_message}'. "
        f"La réponse doit inclure une solution claire, des remerciements et une formule de politesse."
    )

    generated_reply = generate_ai_text(
        prompt,
        system_prompt="Vous êtes un responsable SAV e-commerce haut de gamme spécialisé dans la fidélisation client."
    )

    template = models.CustomerSupportTemplate(
        product_id=product.id,
        inquiry_type=req.inquiry_type,
        customer_email=req.customer_email,
        incoming_message=req.incoming_message,
        generated_reply=generated_reply
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/history/{product_id}", response_model=List[schemas_marketing_fin.SAVResponseOut])
def get_sav_history(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id, models.Product.user_id == current_user.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return (
        db.query(models.CustomerSupportTemplate)
        .filter(models.CustomerSupportTemplate.product_id == product_id)
        .all()
    )
