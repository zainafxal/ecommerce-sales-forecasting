from fastapi import APIRouter, HTTPException

from core.config import settings
from schemas.prediction import PredictionRequest, PredictionResponse
from services.model_service import model_service

api_router = APIRouter()


@api_router.get("/health")
def api_health():
    return {
        "status": "ok" if model_service.model is not None else "degraded",
        "rate_limit": settings.API_RATE_LIMIT,
        "request_queueing": (
            "Handled by FastAPI/Uvicorn async processing and upstream platform proxy."
        ),
        **model_service.status(),
    }


@api_router.post("/predict", response_model=PredictionResponse)
def predict_sales(payload: PredictionRequest):
    try:
        data = payload.model_dump()
        predicted_quantity = model_service.predict(data)
        
        if predicted_quantity < 10:
            demand_level = "🔴 Low Demand"
        elif predicted_quantity < 50:
            demand_level = "🟡 Medium Demand"
        else:
            demand_level = "🟢 High Demand"
            
        return PredictionResponse(
            predicted_quantity=predicted_quantity,
            demand_level=demand_level,
            message="Prediction successful."
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Prediction failed: {str(exc)}",
        ) from exc
