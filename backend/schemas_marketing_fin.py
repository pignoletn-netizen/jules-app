from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class MarketingGenerateRequest(BaseModel):
    product_id: int
    custom_angle: Optional[str] = None

class VideoScriptOut(BaseModel):
    hook: str
    problem: str
    solution: str
    cta: str

class AdCopiesOut(BaseModel):
    meta: str
    tiktok: str

class MarketingContentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    video_script: VideoScriptOut
    ad_copies: AdCopiesOut
    created_at: datetime


class MediaBuyingCheckitem(BaseModel):
    id: str
    step: str
    title: str
    description: str
    is_completed: bool = False


class SAVGenerateRequest(BaseModel):
    product_id: int
    inquiry_type: str
    customer_email: Optional[str] = None
    incoming_message: str

class SAVResponseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    inquiry_type: str
    customer_email: Optional[str] = None
    incoming_message: str
    generated_reply: str
    created_at: datetime


class FinancialCalculationRequest(BaseModel):
    selling_price: float
    cogs: float
    transport_customs: float
    cac_ads: float
    stripe_fee_rate: float = 0.015
    stripe_fee_fixed: float = 0.25
    social_contributions_rate: float = 0.123

class FinancialCalculationOut(BaseModel):
    selling_price: float
    cogs: float
    transport_customs: float
    cac_ads: float
    stripe_fee: float
    social_contributions: float
    total_costs: float
    net_margin_euro: float
    net_margin_percent: float
