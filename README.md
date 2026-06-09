# ☸️ Kubernetes ML Platform

![CI](https://github.com/jumma786/mlops-k8s-platform/actions/workflows/k8s.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Kubernetes](https://img.shields.io/badge/Kubernetes-ready-326CE5)
![Prometheus](https://img.shields.io/badge/Prometheus-metrics-E6522C)
![Helm](https://img.shields.io/badge/Helm-chart-0F1689)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> **Part of the [MLOps Portfolio Series](https://github.com/jumma786/mlops-portfolio)** — Project 10 of 10  
> Production Kubernetes platform for the XGBoost prediction API — K8s manifests, Helm chart, Prometheus metrics, HPA autoscaling, and liveness/readiness/startup probes.

---

## 📂 Project Resources

| Resource | Link |
|---|---|
| 🚀 FastAPI + Metrics | [src/api/app.py](src/api/app.py) |
| ☸️ K8s Deployment | [k8s/base/deployment.yaml](k8s/base/deployment.yaml) |
| ☸️ K8s Service | [k8s/base/service.yaml](k8s/base/service.yaml) |
| ☸️ HPA Autoscaler | [k8s/base/hpa.yaml](k8s/base/hpa.yaml) |
| 📊 Prometheus Monitor | [k8s/monitoring/prometheus.yaml](k8s/monitoring/prometheus.yaml) |
| ⎈ Helm Chart | [helm/mlops-platform/](helm/mlops-platform/) |
| 🐳 Dockerfile | [Dockerfile](Dockerfile) |
| 🧪 Tests | [tests/test_k8s_api.py](tests/test_k8s_api.py) |

---

## 🎯 What This Project Does

Deploys the XGBoost prediction API as a production-grade Kubernetes workload:

1. **K8s probes** — liveness, readiness, startup endpoints
2. **Prometheus metrics** — request count, latency histogram, model AUC gauge
3. **HPA autoscaling** — scales 2→10 pods on CPU/memory
4. **Rolling deployment** — zero-downtime updates
5. **Helm chart** — parameterised deployment

---

## 📐 Architecture

```
Internet → Ingress → Service (ClusterIP) → Deployment (2-10 pods)
                                                    ↓
                                            Prometheus ← /metrics
                                            Grafana   ← dashboards
```

---

## 🔌 Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health/live` | K8s liveness probe |
| `GET /health/ready` | K8s readiness probe |
| `GET /health/startup` | K8s startup probe |
| `GET /metrics` | Prometheus metrics |
| `POST /predict` | XGBoost prediction |
| `GET /model-info` | Model metadata |

---

## 📊 Prometheus Metrics

| Metric | Type | Description |
|---|---|---|
| `prediction_requests_total` | Counter | Total requests by status |
| `prediction_latency_seconds` | Histogram | Request latency |
| `positive_predictions_total` | Counter | Positive prediction count |
| `model_auc` | Gauge | Current model AUC |

---

## 🚀 Quick Start

```bash
git clone https://github.com/jumma786/mlops-k8s-platform.git
cd mlops-k8s-platform
pip install -r requirements.txt
python src/api/train.py --data-path data/bank-additional-full.csv
make test

# Docker
make docker-build
make docker-run

# Kubernetes (requires kubectl + cluster)
make k8s-apply
make k8s-status
```

---

## 🔗 Complete MLOps Portfolio

| # | Project | Repo | Status |
|---|---|---|---|
| 1 | Multi-Model Tournament | [mlops-model-tournament](https://github.com/jumma786/mlops-model-tournament) | ✅ |
| 2 | Scheduled Retraining | [mlops-retraining-pipeline](https://github.com/jumma786/mlops-retraining-pipeline) | ✅ |
| 3 | Feature Engineering | [mlops-feature-pipeline](https://github.com/jumma786/mlops-feature-pipeline) | ✅ |
| 4 | Hyperparameter Tuning | [mlops-hyperparameter-tuning](https://github.com/jumma786/mlops-hyperparameter-tuning) | ✅ |
| 5 | Model Serving | [mlops-model-serving](https://github.com/jumma786/mlops-model-serving) | ✅ |
| 6 | Feature Store | [mlops-feature-store](https://github.com/jumma786/mlops-feature-store) | ✅ |
| 7 | Model Monitoring | [mlops-model-monitoring](https://github.com/jumma786/mlops-model-monitoring) | ✅ |
| 8 | A/B Testing | [mlops-ab-testing](https://github.com/jumma786/mlops-ab-testing) | ✅ |
| 9 | Airflow Pipeline | [mlops-airflow-pipeline](https://github.com/jumma786/mlops-airflow-pipeline) | ✅ |
| **10** | **Kubernetes Platform** | [mlops-k8s-platform](https://github.com/jumma786/mlops-k8s-platform) | ✅ This repo |

---

## 👤 Author

**Jumma Mohammad Teli** — Data Analyst & ML Engineer  
📍 Birmingham, UK  
📧 [jummamohammad477@gmail.com](mailto:jummamohammad477@gmail.com)  
🔗 [LinkedIn](https://linkedin.com/in/jumma-mohammad) | [GitHub](https://github.com/jumma786)

---

*Project 10 of 10 — MLOps Portfolio Series complete.*
