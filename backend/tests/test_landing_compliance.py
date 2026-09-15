import pytest
import uuid
from fastapi.testclient import TestClient
from fastapi import FastAPI
from backend.database import Base, engine
from backend.routers import auth_router, products_router, landing_router, compliance_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router.router)
app.include_router(products_router.router)
app.include_router(landing_router.router)
app.include_router(compliance_router.router)

client = TestClient(app)


def get_auth_token():
    email = f"landing_test_{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "full_name": "Test User"}
    )
    res = client.post(
        "/api/auth/token",
        data={"username": email, "password": "password123"}
    )
    return res.json()["access_token"]


def test_landing_and_compliance_flow():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    prod_payload = {
        "title": "Ecouteurs Bluetooth Sport",
        "category": "Électronique",
        "description": "Écouteurs sans fil étanches IPX7 avec réduction de bruit.",
        "selling_price": 49.99,
        "estimated_cogs": 9.00,
        "estimated_shipping": 3.00,
        "search_volume": 15000,
        "competition_level": "Medium"
    }
    create_res = client.post("/api/products", json=prod_payload, headers=headers)
    assert create_res.status_code == 201
    prod_id = create_res.json()["id"]

    slug = f"ecouteurs-bluetooth-{uuid.uuid4().hex[:6]}"
    landing_req = {
        "product_id": prod_id,
        "slug": slug,
        "custom_instructions": "Accentuer la résistance à l'eau."
    }
    landing_res = client.post("/api/landing-pages/generate", json=landing_req, headers=headers)
    assert landing_res.status_code == 201

    pub_res = client.get(f"/api/landing-pages/public/{slug}")
    assert pub_res.status_code == 200

    intent_click = client.post(
        f"/api/landing-pages/public/{slug}/intent",
        json={"action_type": "click"}
    )
    assert intent_click.status_code == 201

    comp_res = client.get(f"/api/compliance/{prod_id}", headers=headers)
    assert comp_res.status_code == 200
    assert comp_res.json()["ce_marking"] is True
