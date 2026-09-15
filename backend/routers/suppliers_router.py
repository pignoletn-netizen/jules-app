from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models, schemas
from backend.routers.auth_router import get_current_user

router = APIRouter(prefix="/api/suppliers", tags=["Sourcing & Fournisseurs"])


def compute_reliability(years: int, is_verified: bool, response_rate: float) -> bool:
    return years >= 3 and is_verified and response_rate > 90.0


@router.post("", response_model=schemas.SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(
    supplier_in: schemas.SupplierCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    product = (
        db.query(models.Product)
        .filter(models.Product.id == supplier_in.product_id, models.Product.user_id == current_user.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Associated product not found")

    is_reliable = compute_reliability(
        supplier_in.years_in_business, supplier_in.is_verified, supplier_in.response_rate
    )

    supplier = models.Supplier(
        **supplier_in.model_dump(),
        is_reliable=is_reliable,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("", response_model=List[schemas.SupplierOut])
def get_suppliers(
    product_id: Optional[int] = None,
    reliable_only: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = (
        db.query(models.Supplier)
        .join(models.Product, models.Supplier.product_id == models.Product.id)
        .filter(models.Product.user_id == current_user.id)
    )

    if product_id:
        query = query.filter(models.Supplier.product_id == product_id)
    if reliable_only:
        query = query.filter(models.Supplier.is_reliable == True)

    return query.all()


@router.put("/{supplier_id}", response_model=schemas.SupplierOut)
def update_supplier(
    supplier_id: int,
    supplier_update: schemas.SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    supplier = (
        db.query(models.Supplier)
        .join(models.Product, models.Supplier.product_id == models.Product.id)
        .filter(models.Supplier.id == supplier_id, models.Product.user_id == current_user.id)
        .first()
    )
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    update_data = supplier_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(supplier, key, value)

    supplier.is_reliable = compute_reliability(
        supplier.years_in_business, supplier.is_verified, supplier.response_rate
    )

    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    supplier = (
        db.query(models.Supplier)
        .join(models.Product, models.Supplier.product_id == models.Product.id)
        .filter(models.Supplier.id == supplier_id, models.Product.user_id == current_user.id)
        .first()
    )
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(supplier)
    db.commit()
