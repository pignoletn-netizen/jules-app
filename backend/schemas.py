from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ProductBase(BaseModel):
    title: str
    category: str
    description: Optional[str] = None
    selling_price: float = 0.0
    estimated_cogs: float = 0.0
    estimated_shipping: float = 0.0
    estimated_cac: float = 0.0
    search_volume: int = 0
    competition_level: str = "Medium"
    complexity_score: int = 1
    fragility_score: int = 1
    customer_rating: float = 4.5

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    selling_price: Optional[float] = None
    estimated_cogs: Optional[float] = None
    estimated_shipping: Optional[float] = None
    estimated_cac: Optional[float] = None
    search_volume: Optional[int] = None
    competition_level: Optional[str] = None
    complexity_score: Optional[int] = None
    fragility_score: Optional[int] = None
    customer_rating: Optional[float] = None

class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    viability_score: float
    user_id: int
    created_at: datetime


class SupplierBase(BaseModel):
    name: str
    platform: str = "Alibaba"
    years_in_business: int = 0
    is_verified: bool = False
    response_rate: float = 0.0
    unit_price: float = 0.0
    min_order_quantity: int = 1
    shipping_cost: float = 0.0
    lead_time_days: int = 14
    customization_cost: float = 0.0
    product_id: int

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    platform: Optional[str] = None
    years_in_business: Optional[int] = None
    is_verified: Optional[bool] = None
    response_rate: Optional[float] = None
    unit_price: Optional[float] = None
    min_order_quantity: Optional[int] = None
    shipping_cost: Optional[float] = None
    lead_time_days: Optional[int] = None
    customization_cost: Optional[float] = None

class SupplierOut(SupplierBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_reliable: bool
    created_at: datetime
