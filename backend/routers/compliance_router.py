from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models, schemas_mvb
from backend.routers.auth_router import get_current_user

router = APIRouter(prefix="/api/compliance", tags=["Conformité & Normes Européennes"])


def generate_default_category_rules(category: str) -> dict:
    cat_lower = category.lower()

    ce_default = False
    rohs_default = False
    labeling_default = True
    custom_rules = []

    if any(k in cat_lower for k in ["électronique", "electronique", "tech", "gadget", "smart", "appareil"]):
        ce_default = True
        rohs_default = True
        custom_rules = [
            "Directive Compatibilité Électromagnétique (CEM 2014/30/UE)",
            "Directive Basse Tension (LVD 2014/35/UE) si >50V AC",
            "Conformité RoHS (Restriction des substances dangereuses)",
            "Recyclage DEEE (Symbole poubelle barrée obligatoire)"
        ]
    elif any(k in cat_lower for k in ["jouet", "enfant", "bébé"]):
        ce_default = True
        custom_rules = [
            "Norme EN 71-1, EN 71-2, EN 71-3 (Sécurité des jouets)",
            "Avertissements d'âge obligatoires (0-3 ans)",
            "Marquage CE lisible sur produit et emballage"
        ]
    elif any(k in cat_lower for k in ["cosmétique", "beauté", "soin"]):
        custom_rules = [
            "Dossier d'Information sur le Produit (DIP)",
            "Notification sur le Portail CPNP européen",
            "Liste INCI des ingrédients complète"
        ]
    elif any(k in cat_lower for k in ["alimentaire", "cuisine", "gourde", "bouteille"]):
        custom_rules = [
            "Règlement CE 1935/2004 (Matériaux au contact des aliments)",
            "Pictogramme 'Verre et Fourchette' obligatoire",
            "Sans BPA / sans phtalates vérifié par laboratoire"
        ]
    else:
        custom_rules = [
            "Directive Générale sur la Sécurité des Produits (DSGP)",
            "Étiquetage obligatoire en langue française (Nom, Adresse Importateur EU)"
        ]

    return {
        "ce_marking": ce_default,
        "rohs_compliant": rohs_default,
        "mandatory_labeling": labeling_default,
        "custom_rules": custom_rules
    }


@router.get("/{product_id}", response_model=schemas_mvb.ComplianceCheckOut)
def get_or_create_compliance(
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

    compliance = db.query(models.ComplianceCheck).filter(models.ComplianceCheck.product_id == product_id).first()
    if not compliance:
        rules = generate_default_category_rules(product.category)
        compliance = models.ComplianceCheck(
            product_id=product.id,
            category=product.category,
            ce_marking=rules["ce_marking"],
            rohs_compliant=rules["rohs_compliant"],
            mandatory_labeling=rules["mandatory_labeling"],
            custom_rules=rules["custom_rules"],
            eori_number=None,
            notes=f"Checklist générée automatiquement pour la catégorie: {product.category}"
        )
        db.add(compliance)
        db.commit()
        db.refresh(compliance)

    return compliance


@router.put("/{product_id}", response_model=schemas_mvb.ComplianceCheckOut)
def update_compliance(
    product_id: int,
    update_data: schemas_mvb.ComplianceCheckUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    compliance = get_or_create_compliance(product_id, db, current_user)
    data = update_data.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(compliance, k, v)
    db.commit()
    db.refresh(compliance)
    return compliance


@router.post("/documents", response_model=schemas_mvb.ImportDocumentOut, status_code=status.HTTP_201_CREATED)
def create_import_document(
    doc_in: schemas_mvb.ImportDocumentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    product = (
        db.query(models.Product)
        .filter(models.Product.id == doc_in.product_id, models.Product.user_id == current_user.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    doc = models.ImportDocument(**doc_in.model_dump())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/documents/{product_id}", response_model=List[schemas_mvb.ImportDocumentOut])
def get_import_documents(
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

    return db.query(models.ImportDocument).filter(models.ImportDocument.product_id == product_id).all()


@router.put("/documents/{doc_id}", response_model=schemas_mvb.ImportDocumentOut)
def update_import_document(
    doc_id: int,
    update_in: schemas_mvb.ImportDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    doc = (
        db.query(models.ImportDocument)
        .join(models.Product, models.ImportDocument.product_id == models.Product.id)
        .filter(models.ImportDocument.id == doc_id, models.Product.user_id == current_user.id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Import document not found")

    data = update_in.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(doc, k, v)

    db.commit()
    db.refresh(doc)
    return doc
