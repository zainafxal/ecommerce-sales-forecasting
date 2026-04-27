# 🚀 E-Commerce Sales Forecasting API  
Production-ready FastAPI backend deployed on Hugging Face Spaces

---

## 🌐 Live Deployment

🔗 **Live API Base URL**  
https://zainafxal-ecommerce-sales-api.hf.space/

📘 **Interactive Swagger Documentation**  
https://zainafxal-ecommerce-sales-api.hf.space/docs

---

## 📌 Overview

This folder contains the FastAPI inference backend used by the React frontend and deployed on Hugging Face Spaces.

The API serves a trained XGBoost model for real-time sales forecasting and is structured using production-ready patterns including validation, rate limiting, and environment-based configuration.

---

## Responsibilities

- Load the trained XGBoost model
- Validate incoming prediction requests with Pydantic schemas
- Serve prediction responses through FastAPI
- Protect the public inference endpoint with rate limiting
- Support local model loading and Hugging Face Hub model downloads

## Main Files

- `main.py` - app bootstrap, middleware, CORS, root health route
- `api/router.py` - API routes including `health` and `predict`
- `core/config.py` - env-driven configuration
- `core/rate_limit.py` - shared limiter
- `services/model_service.py` - model loading and inference logic
- `schemas/prediction.py` - request and response models
- `Dockerfile` - Hugging Face Spaces Docker deployment
- `.dockerignore` - keeps the Docker build context lean

## Local Setup

```bash
cd backend
conda create -n sales-api-env python=3.10 -y
conda activate sales-api-env
pip install -r requirements.txt
uvicorn main:app --reload
```

Local API URLs:

- Root health: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- API health: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)
- Swagger docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Environment Variables

Copy `.env.example` to `.env` and adjust as needed.

| Variable | Purpose | Example |
|---|---|---|
| `IS_HF_SPACE` | Toggle Hugging Face mode | `False` |
| `HF_MODEL_REPO_ID` | Hugging Face model repository id | `zainafxal/ecommerce-sales-forecasting-model` |
| `HF_MODEL_FILENAME` | Model filename inside local folder or HF repo | `sales_forecaster_xgb_v1.0.pkl` |
| `API_RATE_LIMIT` | Per-IP limit for `/predict` | `10/minute` |
| `BACKEND_CORS_ORIGINS` | Comma-separated allowed local origins | `http://localhost:5173,http://127.0.0.1:5173` |
| `BACKEND_CORS_ORIGIN_REGEX` | Regex for cloud origins | `https://.*\.vercel\.app$|https://.*\.hf\.space$` |

## Rate Limiting

The prediction endpoint uses backend middleware and applies a per-IP policy:

- Route: `POST /api/v1/predict`
- Default limit: `10/minute`
- Response on abuse: HTTP `429 Too Many Requests`

This is especially useful when the API is public on Hugging Face Spaces.

## Request Queueing

No custom in-app request queue was added on purpose.

- FastAPI/Uvicorn already handles concurrent async request processing
- Hugging Face Spaces adds upstream queuing when traffic spikes

For this project, that is the right balance between reliability and simplicity.

## Model Loading Modes

### Local mode

- Set `IS_HF_SPACE=False`
- Store the model in `backend/model/`
- The API loads `backend/model/sales_forecaster_xgb_v1.0.pkl`

### Hugging Face mode

- Set `IS_HF_SPACE=True`
- Set `HF_MODEL_REPO_ID` to the actual repo id
- The API downloads the file at runtime using `hf_hub_download`

This keeps the Docker image smaller and avoids bundling large model files into the deployed container.

## Hugging Face Spaces Deployment

This folder includes a `Dockerfile` suitable for Docker Spaces.

Recommended Space variables:

```env
IS_HF_SPACE=True
HF_MODEL_REPO_ID=your-actual-model-repo
HF_MODEL_FILENAME=sales_forecaster_xgb_v1.0.pkl
API_RATE_LIMIT=10/minute
BACKEND_CORS_ORIGINS=https://your-vercel-app.vercel.app
BACKEND_CORS_ORIGIN_REGEX=https://.*\.vercel\.app$|https://.*\.hf\.space$
```

Notes:

- `.dockerignore` excludes `model/` so the Space image stays lean
- the backend should download the model from Hugging Face instead of baking it into the image
- this is better for storage limits and rebuild times

## Dependencies

`requirements.txt` pins the backend package versions so the local environment and deployment environment stay aligned with the trained model.
