import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


class TestStarshipEndpoints:

    def test_fetch_uss_enterprise(self):
        res = client.post("/starship", json={"id": 1})
        assert res.status_code == 200
        assert res.json()["id"] == 1
        assert res.json()["name"] == "USS Enterprise"

    def test_fetch_millennium_falcon(self):
        res = client.post("/starship", json={"id": 2})
        assert res.status_code == 200
        assert res.json()["id"] == 2
        assert res.json()["name"] == "Millennium Falcon"

    def test_fetch_serenity(self):
        res = client.post("/starship", json={"id": 3})
        assert res.status_code == 200
        assert res.json()["id"] == 3
        assert res.json()["name"] == "Serenity"

    def test_fetch_nostromo(self):
        res = client.post("/starship", json={"id": 4})
        assert res.status_code == 200
        assert res.json()["id"] == 4
        assert res.json()["name"] == "Nostromo"

    def test_fetch_battlestar_galactica(self):
        res = client.post("/starship", json={"id": 5})
        assert res.status_code == 200
        assert res.json()["id"] == 5
        assert res.json()["name"] == "Battlestar Galactica"

    def test_fetch_heart_of_gold(self):
        res = client.post("/starship", json={"id": 6})
        assert res.status_code == 200
        assert res.json()["id"] == 6
        assert res.json()["name"] == "Heart of Gold"

    def test_fetch_rocinante(self):
        res = client.post("/starship", json={"id": 7})
        assert res.status_code == 200
        assert res.json()["id"] == 7
        assert res.json()["name"] == "Rocinante"

    def test_fetch_event_horizon(self):
        res = client.post("/starship", json={"id": 8})
        assert res.status_code == 200
        assert res.json()["id"] == 8
        assert res.json()["name"] == "Event Horizon"

    def test_starship_not_found(self):
        res = client.post("/starship", json={"id": 99})
        assert res.status_code == 200
        assert res.json() is None


class TestOtherEndpoints:

    def test_os_endpoint(self):
        res = client.get("/os")
        assert res.status_code == 200
        assert "os" in res.json()
        assert "env" in res.json()

    def test_liveness_endpoint(self):
        res = client.get("/live")
        assert res.status_code == 200
        assert res.json()["status"] == "live"

    def test_readiness_endpoint(self):
        res = client.get("/ready")
        assert res.status_code == 200
        assert res.json()["status"] == "ready"

    def test_metrics_endpoint(self):
        res = client.get("/metrics")
        assert res.status_code == 200
        assert b"starship_requests_total" in res.content or b"http_request_duration" in res.content
