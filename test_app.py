import pytest
from fastapi.testclient import TestClient
from app import app, sanitize_filename

client = TestClient(app)

def test_sanitize_filename():
    assert sanitize_filename("Video: Test / Name?") == "Video Test  Name"
    assert sanitize_filename("A" * 300) == "A" * 200
    assert sanitize_filename("") == "video"

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "<title>VideoDown - Baixar Vídeos de Qualquer Site</title>" in response.text

def test_info_invalid_url():
    response = client.post("/api/info", json={"url": ""})
    assert response.status_code == 400

def test_info_youtube():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    response = client.post("/api/info", json={"url": url})
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "Rick Astley" in data["title"]
    assert len(data["formats"]) > 0

def test_download_endpoint_validation():
    response = client.get("/api/download?url=")
    assert response.status_code == 400
