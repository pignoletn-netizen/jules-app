from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models, schemas_marketing_fin
from backend.routers.auth_router import get_current_user

router = APIRouter(prefix="/api/financials", tags=["Dashboard Financier & Calculateur de Marge Nette"])


def calculate_financials(
    selling_price: float,
    cogs: float,
    transport_customs: float,
    cac_ads: float,
    stripe_rate: float = 0.015,
    stripe_fixed: float = 0.25,
    social_rate: float = 0.123
) -> schemas_marketing_fin.FinancialCalculationOut:
    if selling_price > 0:
        stripe_fee = (selling_price * stripe_rate) + stripe_fixed
        social_contributions = selling_price * social_rate
    else:
        stripe_fee = 0.0
        social_contributions = 0.0

    total_costs = cogs + transport_customs + cac_ads + stripe_fee + social_contributions
    net_margin_euro = selling_price - total_costs
    net_margin_percent = (net_margin_euro / selling_price * 100.0) if selling_price > 0 else 0.0

    return schemas_marketing_fin.FinancialCalculationOut(
        selling_price=round(selling_price, 2),
        cogs=round(cogs, 2),
        transport_customs=round(transport_customs, 2),
        cac_ads=round(cac_ads, 2),
        stripe_fee=round(stripe_fee, 2),
        social_contributions=round(social_contributions, 2),
        total_costs=round(total_costs, 2),
        net_margin_euro=round(net_margin_euro, 2),
        net_margin_percent=round(net_margin_percent, 1)
    )


@router.post("/calculate", response_model=schemas_marketing_fin.FinancialCalculationOut)
def calculate_margin(req: schemas_marketing_fin.FinancialCalculationRequest):
    return calculate_financials(
        selling_price=req.selling_price,
        cogs=req.cogs,
        transport_customs=req.transport_customs,
        cac_ads=req.cac_ads,
        stripe_rate=req.stripe_fee_rate,
        stripe_fixed=req.stripe_fee_fixed,
        social_rate=req.social_contributions_rate
    )


@router.get("/summary/{product_id}", response_model=schemas_marketing_fin.FinancialCalculationOut)
def get_product_financial_summary(
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

    return calculate_financials(
        selling_price=product.selling_price,
        cogs=product.estimated_cogs,
        transport_customs=product.estimated_shipping,
        cac_ads=product.estimated_cac
    )
