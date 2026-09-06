import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app, SAMPLE_EXCEL_PATH

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_species_search():
    response = client.get("/api/species/search?name=Textrix%20denticulata")
    assert response.status_code == 200
    data = response.json()
    assert "cd_nom" in data
    assert "taxonomy" in data
    assert data["taxonomy"]["family"] == "Agelenidae"
    assert "summary_text" in data

def test_sample_file_download():
    response = client.get("/api/analysis/sample")
    assert response.status_code == 200
    assert response.headers["content-type"] in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/octet-stream"
    ]

def test_analysis_upload():
    # Make sure sample excel file exists
    client.get("/api/analysis/sample")

    with open(SAMPLE_EXCEL_PATH, "rb") as f:
        files = {"file": ("test_inventory.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        response = client.post("/api/analysis/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert "summary_table" in data
    assert "diversity_table" in data
    assert "jaccard_matrix" in data
    assert "species_clusters" in data
    assert "habitat_clusters" in data
    assert "excel_file" in data
    assert "plots" in data

def test_download_result_excel():
    response = client.get("/api/analysis/download/resultats_analyse.xlsx")
    assert response.status_code == 200
