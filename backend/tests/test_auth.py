import pytest
import uuid
from fastapi.testclient import TestClient
from fastapi import FastAPI
from backend.database import Base, engine
from backend.routers import auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router.router)

client = TestClient(app)

def test_register_and_login():
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    register_res = client.post(
        "/api/auth/register",
        json={"email": unique_email, "password": "password123", "full_name": "Test User"}
    )
    assert register_res.status_code == 201

    login_res = client.post(
        "/api/auth/token",
        data={"username": unique_email, "password": "password123"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == unique_email
