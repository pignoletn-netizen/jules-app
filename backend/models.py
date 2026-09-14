from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="owner")
    landing_pages = relationship("LandingPage", back_populates="owner")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    selling_price = Column(Float, default=0.0)
    estimated_cogs = Column(Float, default=0.0)
    estimated_shipping = Column(Float, default=0.0)
    estimated_cac = Column(Float, default=0.0)

    search_volume = Column(Integer, default=0)
    competition_level = Column(String, default="Medium")

    complexity_score = Column(Integer, default=1)
    fragility_score = Column(Integer, default=1)
    customer_rating = Column(Float, default=4.5)

    viability_score = Column(Float, default=0.0)

    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="products")
    suppliers = relationship("Supplier", back_populates="product", cascade="all, delete-orphan")
    landing_pages = relationship("LandingPage", back_populates="product", cascade="all, delete-orphan")
    compliance = relationship("ComplianceCheck", back_populates="product", uselist=False, cascade="all, delete-orphan")
    documents = relationship("ImportDocument", back_populates="product", cascade="all, delete-orphan")
    marketing_contents = relationship("MarketingContent", back_populates="product", cascade="all, delete-orphan")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    platform = Column(String, default="Alibaba")
    years_in_business = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    response_rate = Column(Float, default=0.0)

    unit_price = Column(Float, default=0.0)
    min_order_quantity = Column(Integer, default=1)
    shipping_cost = Column(Float, default=0.0)
    lead_time_days = Column(Integer, default=14)
    customization_cost = Column(Float, default=0.0)

    is_reliable = Column(Boolean, default=False)

    product_id = Column(Integer, ForeignKey("products.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="suppliers")


class LandingPage(Base):
    __tablename__ = "landing_pages"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    main_headline = Column(String, nullable=False)
    subheadline = Column(Text, nullable=False)
    selling_points = Column(JSON, default=list)
    faq_list = Column(JSON, default=list)
    call_to_action = Column(String, default="Commander Maintenant")

    click_count = Column(Integer, default=0)
    email_count = Column(Integer, default=0)

    product_id = Column(Integer, ForeignKey("products.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="landing_pages")
    owner = relationship("User", back_populates="landing_pages")
    intents = relationship("PublicIntent", back_populates="landing_page", cascade="all, delete-orphan")


class PublicIntent(Base):
    __tablename__ = "public_intents"

    id = Column(Integer, primary_key=True, index=True)
    landing_page_id = Column(Integer, ForeignKey("landing_pages.id"))
    action_type = Column(String, nullable=False)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    landing_page = relationship("LandingPage", back_populates="intents")


class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)
    category = Column(String, nullable=False)
    ce_marking = Column(Boolean, default=False)
    rohs_compliant = Column(Boolean, default=False)
    mandatory_labeling = Column(Boolean, default=False)
    eori_number = Column(String, nullable=True)
    custom_rules = Column(JSON, default=list)
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="compliance")


class ImportDocument(Base):
    __tablename__ = "import_documents"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    doc_type = Column(String, nullable=False)
    doc_name = Column(String, nullable=False)
    status = Column(String, default="Pending")
    file_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="documents")


class MarketingContent(Base):
    __tablename__ = "marketing_contents"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    script_hook = Column(Text, nullable=True)
    script_problem = Column(Text, nullable=True)
    script_solution = Column(Text, nullable=True)
    script_cta = Column(Text, nullable=True)

    ad_copy_meta = Column(Text, nullable=True)
    ad_copy_tiktok = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="marketing_contents")


class CustomerSupportTemplate(Base):
    __tablename__ = "customer_support_templates"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    inquiry_type = Column(String, nullable=False)
    customer_email = Column(String, nullable=True)
    incoming_message = Column(Text, nullable=False)
    generated_reply = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
