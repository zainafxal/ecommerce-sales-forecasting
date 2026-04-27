from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class PredictionRequest(BaseModel):
    stockcode: str = Field(..., description="Product Code (SKU)")
    unitprice: float = Field(..., description="Unit price in GBP")
    country: str = Field(..., description="Country of Sale")
    sale_date: date = Field(..., description="Date of the sale")
    hour: int = Field(..., ge=0, le=23, description="Hour of the sale (0-23)")
    customer_type: str = Field(..., description="Either 'Registered' or 'Guest'")

class PredictionResponse(BaseModel):
    predicted_quantity: float
    demand_level: str
    message: str
