from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "E-Commerce Sales Forecasting API"
    APP_VERSION: str = "1.1.0"
    APP_DESCRIPTION: str = (
        "FastAPI backend for forecasting e-commerce sales quantities with XGBoost."
    )

    IS_HF_SPACE: bool = False
    HF_MODEL_REPO_ID: str = "zainafxal/ecommerce-sales-forecasting-model"
    HF_MODEL_FILENAME: str = "sales_forecaster_xgb_v1.0.pkl"
    LOCAL_MODEL_DIR: Path = BACKEND_DIR / "model"

    API_RATE_LIMIT: str = "10/minute"
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    BACKEND_CORS_ORIGIN_REGEX: str = r"https://.*\.vercel\.app$|https://.*\.hf\.space$"

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def local_model_path(self) -> Path:
        return self.LOCAL_MODEL_DIR / self.HF_MODEL_FILENAME


settings = Settings()
