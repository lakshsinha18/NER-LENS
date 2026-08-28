from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from fastapi.testclient import TestClient
from app.main import app


def test_health_and_demo_zones():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        response = client.get("/api/risk/zones")
        assert response.status_code == 200
        assert len(response.json()["zones"]) >= 8
