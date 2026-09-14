import pytest
import uuid
from fastapi.testclient import TestClient
from fastapi import FastAPI
from backend.database import Base, engine
from backend.routers import auth_router, products_router, marketing_router, sav_router, financials_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router.router)
app.include_router(products_router.router)
app.include_router(marketing_router.router)
app.include_router(sav_router.router)
app.include_router(financials_router.router)

client = TestClient(app)


def get_auth_token():
    email = f"mkt_test_{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "full_name": "Test User"}
    )
    res = client.post(
        "/api/auth/token",
        data={"username": email, "password": "password123"}
    )
    return res.json()["access_token"]


def test_marketing_sav_financials_flow():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    prod_payload = {
        "title": "Mangeoire Intelligente pour Chat",
        "category": "Animalerie",
        "description": "Mangeoire automatique programmable avec caméra HD et application mobile.",
        "selling_price": 89.99,
        "estimated_cogs": 22.00,
        "estimated_shipping": 6.50,
        "estimated_cac": 18.00,
        "search_volume": 8500,
        "competition_level": "Low"
    }
    create_res = client.post("/api/products", json=prod_payload, headers=headers)
    assert create_res.status_code == 201
    prod_id = create_res.json()["id"]

    mkt_req = {"product_id": prod_id, "custom_angle": "Tranquillité d'esprit pendant les vacances"}
    mkt_res = client.post("/api/marketing/generate", json=mkt_req, headers=headers)
    assert mkt_res.status_code == 201

    calc_req = {
        "selling_price": 89.99,
        "cogs": 22.00,
        "transport_customs": 6.50,
        "cac_ads": 18.00,
        "stripe_fee_rate": 0.015,
        "stripe_fee_fixed": 0.25,
        "social_contributions_rate": 0.123
    }
    calc_res = client.post("/api/financials/calculate", json=calc_req)
    assert calc_res.status_code == 200
    calc_data = calc_res.json()
    assert calc_data["net_margin_euro"] > 0
