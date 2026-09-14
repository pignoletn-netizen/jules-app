from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models, schemas
from backend.routers.auth_router import get_current_user

router = APIRouter(prefix="/api/products", tags=["Product Hunting"])


def calculate_viability_score(p: schemas.ProductBase) -> float:
    score = 0.0

    total_cost = p.estimated_cogs + p.estimated_shipping
    if p.selling_price > 0:
        margin_pct = ((p.selling_price - total_cost) / p.selling_price) * 100.0
    else:
        margin_pct = 0.0

    if margin_pct >= 60.0:
        score += 35.0
    elif margin_pct >= 40.0:
        score += 25.0
    elif margin_pct >= 20.0:
        score += 15.0
    else:
        score += max(0.0, margin_pct * 0.25)

    if p.search_volume >= 20000:
        score += 25.0
    elif p.search_volume >= 10000:
        score += 20.0
    elif p.search_volume >= 3000:
        score += 15.0
    elif p.search_volume >= 1000:
        score += 10.0
    else:
        score += 5.0

    comp = p.competition_level.lower()
    if comp == "low":
        score += 20.0
    elif comp == "medium":
        score += 12.0
    else:
        score += 5.0

    rating_score = min(5.0, max(1.0, p.customer_rating)) * 4.0
    score += rating_score

    complexity_penalty = (max(1, min(5, p.complexity_score)) - 1) * 2.5
    fragility_penalty = (max(1, min(5, p.fragility_score)) - 1) * 2.5

    score -= (complexity_penalty + fragility_penalty)

    return round(max(0.0, min(100.0, score)), 1)


@router.post("", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    viability = calculate_viability_score(product_in)
    product = models.Product(
        **product_in.model_dump(),
        viability_score=viability,
        user_id=current_user.id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("", response_model=List[schemas.ProductOut])
def get_products(
    category: Optional[str] = None,
    min_viability: Optional[float] = None,
    max_complexity: Optional[int] = None,
    max_fragility: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Product).filter(models.Product.user_id == current_user.id)
    if category:
        query = query.filter(models.Product.category == category)
    if min_viability is not None:
        query = query.filter(models.Product.viability_score >= min_viability)
    if max_complexity is not None:
        query = query.filter(models.Product.complexity_score <= max_complexity)
    if max_fragility is not None:
        query = query.filter(models.Product.fragility_score <= max_fragility)
    return query.all()


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(
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
    return product


@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
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

    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    temp_base = schemas.ProductBase(
        title=product.title,
        category=product.category,
        description=product.description,
        selling_price=product.selling_price,
        estimated_cogs=product.estimated_cogs,
        estimated_shipping=product.estimated_shipping,
        estimated_cac=product.estimated_cac,
        search_volume=product.search_volume,
        competition_level=product.competition_level,
        complexity_score=product.complexity_score,
        fragility_score=product.fragility_score,
        customer_rating=product.customer_rating,
    )
    product.viability_score = calculate_viability_score(temp_base)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
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
    db.delete(product)
    db.commit()
