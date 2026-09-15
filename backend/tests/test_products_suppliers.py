import pytest
import uuid
from fastapi.testclient import TestClient
from fastapi import FastAPI
from backend.database import Base, engine
from backend.routers import auth_router, products_router, suppliers_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router.router)
app.include_router(products_router.router)
app.include_router(suppliers_router.router)

client = TestClient(app)


def get_auth_token():
    email = f"prod_test_{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "full_name": "Test User"}
    )
    res = client.post(
        "/api/auth/token",
        data={"username": email, "password": "password123"}
    )
    return res.json()["access_token"]


def test_products_and_suppliers_flow():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    prod_payload = {
        "title": "Correcteur de Posture Ergonomique",
        "category": "Santé & Bien-être",
        "description": "Correcteur de posture ajustable pour le dos et les épaules.",
        "selling_price": 39.99,
        "estimated_cogs": 8.50,
        "estimated_shipping": 4.00,
        "estimated_cac": 10.00,
        "search_volume": 12000,
        "competition_level": "Medium",
        "complexity_score": 1,
        "fragility_score": 1,
        "customer_rating": 4.8
    }
    create_res = client.post("/api/products", json=prod_payload, headers=headers)
    assert create_res.status_code == 201
    prod_data = create_res.json()
    product_id = prod_data["id"]

    sup_reliable = {
        "name": "Shenzhen Health Tech Co., Ltd",
        "platform": "Alibaba",
        "years_in_business": 5,
        "is_verified": True,
        "response_rate": 96.5,
        "unit_price": 6.20,
        "min_order_quantity": 100,
        "shipping_cost": 2.30,
        "lead_time_days": 10,
        "customization_cost": 0.50,
        "product_id": product_id
    }
    sup_res = client.post("/api/suppliers", json=sup_reliable, headers=headers)
    assert sup_res.status_code == 201
    assert sup_res.json()["is_reliable"] is True
