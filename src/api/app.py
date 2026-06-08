"""
Production FastAPI App for Kubernetes
=======================================
Extends Project 5 model serving with:
- Prometheus metrics endpoint (/metrics)
- Kubernetes liveness probe (/health/live)
- Kubernetes readiness probe (/health/ready)
- Graceful shutdown handling
- Request counting and latency tracking
"""

import os
import json
import time
import logging
import numpy as np
import pandas as pd
import xgboost as xgb
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ARTIFACTS_DIR = os.getenv("ARTIFACTS_DIR", "artifacts")

# Prometheus metrics
REQUEST_COUNT    = Counter("prediction_requests_total", "Total prediction requests", ["variant", "status"])
REQUEST_LATENCY  = Histogram("prediction_latency_seconds", "Prediction latency", ["variant"])
POSITIVE_PREDS   = Counter("positive_predictions_total", "Total positive predictions")
MODEL_AUC        = Gauge("model_auc", "Current model AUC")
APP_INFO         = Gauge("app_info", "App info", ["version", "model"])


def load_artifacts():
    model = xgb.XGBClassifier()
    model.load_model(os.path.join(ARTIFACTS_DIR, "model.json"))
    with open(os.path.join(ARTIFACTS_DIR, "feature_order.json")) as f:
        feature_order = json.load(f)
    with open(os.path.join(ARTIFACTS_DIR, "encoders.json")) as f:
        encoders = json.load(f)
    with open(os.path.join(ARTIFACTS_DIR, "model_info.json")) as f:
        model_info = json.load(f)
    logger.info(f"Model loaded | AUC: {model_info['auc']}")
    MODEL_AUC.set(model_info["auc"])
    APP_INFO.labels(version="1.0.0", model="XGBoost").set(1)
    return model, feature_order, encoders, model_info


model, feature_order, encoders, model_info = load_artifacts()
startup_time = time.time()

app = FastAPI(
    title="MLOps K8s Platform — Prediction API",
    description="Production ML serving with K8s health probes, Prometheus metrics, and graceful shutdown.",
    version="1.0.0",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class CustomerFeatures(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    age:             int   = Field(..., ge=18, le=95)
    job:             str
    marital:         str
    education:       str
    default:         str
    housing:         str
    loan:            str
    contact:         str
    month:           str
    day_of_week:     str
    campaign:        int
    pdays:           int
    previous:        int
    poutcome:        str
    emp_var_rate:    float = Field(..., alias="emp.var.rate")
    cons_price_idx:  float = Field(..., alias="cons.price.idx")
    cons_conf_idx:   float = Field(..., alias="cons.conf.idx")
    euribor3m:       float
    nr_employed:     float = Field(..., alias="nr.employed")


class PredictionResponse(BaseModel):
    prediction:    int
    probability:   float
    label:         str
    latency_ms:    float


def preprocess(customer: CustomerFeatures) -> pd.DataFrame:
    data = customer.model_dump(by_alias=True)
    row = {}
    for col in feature_order:
        val = data.get(col, 0)
        if isinstance(val, str):
            row[col] = int(encoders.get(col, {}).get(val, -1))
        else:
            row[col] = float(val) if val is not None else 0.0
    df = pd.DataFrame([row])
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df[feature_order]


@app.get("/")
def root():
    return {"service": "MLOps K8s Platform", "version": "1.0.0", "docs": "/docs"}


# Kubernetes probes
@app.get("/health/live")
def liveness():
    """Kubernetes liveness probe — is the app alive?"""
    return {"status": "alive", "uptime_seconds": round(time.time() - startup_time, 1)}


@app.get("/health/ready")
def readiness():
    """Kubernetes readiness probe — is the app ready to serve traffic?"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready", "model": "loaded", "auc": model_info["auc"]}


@app.get("/health/startup")
def startup_probe():
    """Kubernetes startup probe — has the app finished initializing?"""
    return {"status": "started", "startup_time": startup_time}


@app.get("/model-info")
def get_model_info():
    return model_info


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    """Prometheus metrics endpoint."""
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/predict", response_model=PredictionResponse)
def predict(customer: CustomerFeatures, request: Request):
    """Make a prediction with Prometheus tracking."""
    start = time.time()
    try:
        df   = preprocess(customer)
        prob = float(model.predict_proba(df)[0][1])
        pred = int(prob >= 0.5)
        label = "Yes — will subscribe" if pred == 1 else "No — will not subscribe"
        latency = (time.time() - start) * 1000

        REQUEST_COUNT.labels(variant="xgboost", status="success").inc()
        REQUEST_LATENCY.labels(variant="xgboost").observe(latency / 1000)
        if pred == 1:
            POSITIVE_PREDS.inc()

        return PredictionResponse(
            prediction=pred, probability=round(prob, 4),
            label=label, latency_ms=round(latency, 2)
        )
    except Exception as e:
        REQUEST_COUNT.labels(variant="xgboost", status="error").inc()
        raise HTTPException(status_code=422, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=False)
