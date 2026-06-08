"""
Test suite for mlops-k8s-platform.
Run: pytest tests/ -v --cov=src
"""

import pytest
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if not os.path.exists("artifacts/model.json"):
    from src.api.train import train
    train()

from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

SAMPLE = {
    "age": 42, "job": "admin.", "marital": "married",
    "education": "university.degree", "default": "no",
    "housing": "yes", "loan": "no", "contact": "cellular",
    "month": "may", "day_of_week": "mon", "campaign": 2,
    "pdays": 999, "previous": 0, "poutcome": "nonexistent",
    "emp.var.rate": 1.1, "cons.price.idx": 93.994,
    "cons.conf.idx": -36.4, "euribor3m": 4.857, "nr.employed": 5191.0
}


class TestHealthProbes:
    def test_liveness(self):
        r = client.get("/health/live")
        assert r.status_code == 200
        assert r.json()["status"] == "alive"

    def test_readiness(self):
        r = client.get("/health/ready")
        assert r.status_code == 200
        assert r.json()["status"] == "ready"

    def test_startup(self):
        r = client.get("/health/startup")
        assert r.status_code == 200
        assert r.json()["status"] == "started"

    def test_liveness_uptime(self):
        r = client.get("/health/live")
        assert "uptime_seconds" in r.json()


class TestMetrics:
    def test_metrics_endpoint(self):
        r = client.get("/metrics")
        assert r.status_code == 200

    def test_metrics_contains_predictions(self):
        client.post("/predict", json=SAMPLE)
        r = client.get("/metrics")
        assert "prediction_requests_total" in r.text

    def test_metrics_contains_latency(self):
        client.post("/predict", json=SAMPLE)
        r = client.get("/metrics")
        assert "prediction_latency_seconds" in r.text

    def test_metrics_contains_auc(self):
        r = client.get("/metrics")
        assert "model_auc" in r.text


class TestPredict:
    def test_predict_200(self):
        r = client.post("/predict", json=SAMPLE)
        assert r.status_code == 200

    def test_predict_schema(self):
        r = client.post("/predict", json=SAMPLE)
        data = r.json()
        assert "prediction" in data
        assert "probability" in data
        assert "latency_ms" in data

    def test_predict_latency_tracked(self):
        r = client.post("/predict", json=SAMPLE)
        assert r.json()["latency_ms"] >= 0

    def test_model_info(self):
        r = client.get("/model-info")
        assert r.status_code == 200
        assert "auc" in r.json()
