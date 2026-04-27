from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from core.config import settings


class ModelService:
    def __init__(self):
        self.model: Any | None = None
        self.model_source = "uninitialized"
        self.model_path: str | None = None
        self.load_error: str | None = None
        self.load_model()

    def _resolve_model_path(self) -> tuple[Path, str]:
        if settings.IS_HF_SPACE:
            from huggingface_hub import hf_hub_download

            downloaded_path = hf_hub_download(
                repo_id=settings.HF_MODEL_REPO_ID,
                filename=settings.HF_MODEL_FILENAME,
            )
            return Path(downloaded_path), "huggingface-hub"

        local_model_path = settings.local_model_path
        if not local_model_path.exists():
            raise FileNotFoundError(
                f"Local model file not found at '{local_model_path}'."
            )
        return local_model_path, "local"

    def load_model(self) -> None:
        try:
            model_path, model_source = self._resolve_model_path()
            self.model = joblib.load(str(model_path))
            self.model_path = str(model_path)
            self.model_source = model_source
            self.load_error = None
        except Exception as exc:
            self.model = None
            self.model_path = None
            self.model_source = "unavailable"
            self.load_error = str(exc)

    def status(self) -> dict[str, Any]:
        return {
            "model_loaded": self.model is not None,
            "model_source": self.model_source,
            "model_path": self.model_path,
            "load_error": self.load_error,
        }

    def predict(self, data: dict) -> float:
        if self.model is None:
            if self.load_error:
                raise RuntimeError(f"Model is not loaded. {self.load_error}")
            raise RuntimeError("Model is not loaded.")

        # Replicate Streamlit logic for auto-calculating time features
        date_obj = data['sale_date']
        invoice_year = date_obj.year
        invoice_month = date_obj.month
        invoice_day = date_obj.day
        invoice_dayofweek = date_obj.weekday()  # Monday=0
        invoice_weekofyear = date_obj.isocalendar()[1]
        invoice_quarter = (date_obj.month - 1) // 3 + 1
        is_weekend = 1 if invoice_dayofweek >= 5 else 0

        # Replicate customer features
        unitprice = data['unitprice']
        if data['customer_type'] == "Guest":
            is_guest = 1
            recency = 30
            frequency = 1
            monetary = unitprice
        else:
            is_guest = 0
            recency = 10
            frequency = 5
            monetary = unitprice * 5

        # Replicate product features
        product_total_qty = 100
        product_avg_price = unitprice
        product_sales_count = 10

        # Prepare input DataFrame
        input_data = [{
            'StockCode': data['stockcode'],
            'UnitPrice': unitprice,
            'Country': data['country'],
            'InvoiceYear_pipe': invoice_year,
            'InvoiceMonth_pipe': invoice_month,
            'InvoiceDay_pipe': invoice_day,
            'InvoiceDayOfWeek_pipe': invoice_dayofweek,
            'InvoiceHour_pipe': data['hour'],
            'InvoiceWeekOfYear_pipe': invoice_weekofyear,
            'InvoiceQuarter_pipe': invoice_quarter,
            'IsWeekend_pipe': is_weekend,
            'Recency_pipe': recency,
            'Frequency_pipe': frequency,
            'Monetary_pipe': monetary,
            'ProductTotalQuantity_pipe': product_total_qty,
            'ProductAverageUnitPrice_pipe': product_avg_price,
            'ProductSalesCount_pipe': product_sales_count,
            'IsGuest_pipe': is_guest
        }]
        
        input_df = pd.DataFrame(input_data)
        
        # Categorical columns explicitly cast like in Streamlit app
        input_df['StockCode'] = input_df['StockCode'].astype('category')
        input_df['Country'] = input_df['Country'].astype('category')

        # Predict
        pred_log = self.model.predict(input_df)[0]
        pred_quantity = np.expm1(pred_log)
        
        return float(pred_quantity)

model_service = ModelService()
