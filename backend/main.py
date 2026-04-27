from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.router import api_router
from core.config import settings
from core.rate_limit import InMemoryRateLimiter
from services.model_service import model_service

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

predict_rate_limiter = InMemoryRateLimiter(settings.API_RATE_LIMIT)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.BACKEND_CORS_ORIGIN_REGEX,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.middleware("http")
async def rate_limit_predict_endpoint(request: Request, call_next):
    if request.url.path == "/api/v1/predict":
        client_ip = request.client.host if request.client else "unknown"
        allowed, retry_after = predict_rate_limiter.check(client_ip)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        f"Rate limit exceeded. Please try again in {retry_after} seconds."
                    )
                },
                headers={"Retry-After": str(retry_after)},
            )

    return await call_next(request)


@app.get("/")
def health_check():
    return {
        "status": "ok" if model_service.model is not None else "degraded",
        "message": f"{settings.APP_NAME} is running",
        "version": settings.APP_VERSION,
        "model": model_service.status(),
        "rate_limit": settings.API_RATE_LIMIT,
        "request_queueing": (
            "Uvicorn handles async request processing and Hugging Face Spaces adds upstream queuing."
        ),
    }
