from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class LandingPageGenerateRequest(BaseModel):
    product_id: int
    slug: str
    custom_instructions: Optional[str] = None

class LandingPageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    main_headline: str
    subheadline: str
    selling_points: list
    faq_list: list
    call_to_action: str
    click_count: int
    email_count: int
    product_id: int
    user_id: int
    created_at: datetime

class PublicLandingPageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    main_headline: str
    subheadline: str
    selling_points: list
    faq_list: list
    call_to_action: str
    click_count: int
    email_count: int

class IntentRegisterRequest(BaseModel):
    action_type: str
    email: Optional[str] = None

class IntentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    landing_page_id: int
    action_type: str
    email: Optional[str] = None
    created_at: datetime


class ComplianceCheckUpdate(BaseModel):
    ce_marking: Optional[bool] = None
    rohs_compliant: Optional[bool] = None
    mandatory_labeling: Optional[bool] = None
    eori_number: Optional[str] = None
    custom_rules: Optional[list] = None
    notes: Optional[str] = None

class ComplianceCheckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    category: str
    ce_marking: bool
    rohs_compliant: bool
    mandatory_labeling: bool
    eori_number: Optional[str] = None
    custom_rules: list
    notes: Optional[str] = None
    updated_at: datetime

class ImportDocumentCreate(BaseModel):
    product_id: int
    doc_type: str
    doc_name: str
    status: str = "Pending"
    file_url: Optional[str] = None

class ImportDocumentUpdate(BaseModel):
    status: Optional[str] = None
    file_url: Optional[str] = None

class ImportDocumentOut(ImportDocumentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
