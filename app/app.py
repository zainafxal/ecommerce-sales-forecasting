import os
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import zipfile
from datetime import datetime

# --- Load Model ---
@st.cache_resource
def load_model():
    model_path = "sales_forecaster_xgb_v1.0.pkl"
    zip_path = "sales_forecaster_xgb_v1.0.zip"
    # If Model file (.pkl) file dosen't exist, extract from zip
    if not os.path.exists(model_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
    return joblib.load(model_path)

model = load_model()

st.title("🛒E-Commerce Sales Forecasting App")

st.markdown("""
This app predicts the expected sales quantity for a product based on your input.
**Only a few fields are required. All other features are handled automatically for you!**
""")

# --- Product Info Section ---
st.header("1️⃣ Product Information")
product_codes = [
    "85123A", "85099B", "22423", "47566", "20725", "other"
]
stockcode = st.selectbox(
    "Product Code",
    product_codes,
    help="Select the product code (SKU). If not listed, choose 'other' and enter manually below."
)
if stockcode == "other":
    stockcode = st.text_input("Enter Product Code", "")

# --- Currency Conversion Section ---
st.markdown("**Currency Options (Optional):**")
currency = st.selectbox(
    "Select the currency you are entering the price in:",
    ["GBP (British Pound)", "PKR (Pakistani Rupee)", "USD (US Dollar)", "EUR (Euro)", "Other"]
)
unitprice_input = st.number_input(
    f"Unit Price (per unit, in {currency.split()[0]})",
    min_value=0.01,
    value=2.55,
    help=f"Enter the selling price per unit of the product in {currency.split()[0]}."
)

# --- Show exchange rate field only if currency is not GBP ---
if currency != "GBP (British Pound)":
    exchange_rate = st.text_input(
        f"Current exchange rate: 1 GBP = ? {currency.split()[0]}",
        value="",
        help="If you entered price in a currency other than GBP, enter the current exchange rate here. For example, if 1 GBP = 350 PKR, enter 350."
    )
else:
    exchange_rate = ""

# --- Convert to GBP if needed and show live info ---
if exchange_rate.strip() and currency != "GBP (British Pound)":
    try:
        rate = float(exchange_rate)
        unitprice = unitprice_input / rate
        st.success(f"Converted Unit Price for model: **{unitprice:.4f} GBP**")
    except:
        st.warning("Please enter a valid exchange rate (number). Using input price as GBP.")
        unitprice = unitprice_input
else:
    unitprice = unitprice_input
    if currency != "GBP (British Pound)" and exchange_rate.strip() == "":
        st.info("No exchange rate entered. Price will be used as GBP.")

# --- Transaction Info Section ---
st.header("2️⃣ Transaction Details")
country = st.selectbox(
    "Country of Sale",
    [
        "united kingdom", "france", "germany", "spain", "netherlands", "switzerland", "portugal", "italy", "norway", "other"
    ],
    help="Select the country where the sale is made."
)

date = st.date_input(
    "Sale Date",
    datetime(2011, 12, 1),
    help="Date when the product was sold."
)

hour = st.slider(
    "Hour of Sale (0-23)",
    min_value=0,
    max_value=23,
    value=8,
    help="Hour of the day when the sale occurred (0 = midnight, 23 = 11pm)."
)

# --- Customer Info Section ---
st.header("3️⃣ Customer Information")
customer_type = st.radio(
    "Customer Type",
    ["Registered", "Guest"],
    help="Is the customer a registered user or a guest?"
)

# --- Auto-calculate Time Features ---
invoice_year = date.year
invoice_month = date.month
invoice_day = date.day
invoice_dayofweek = date.weekday()  # Monday=0
invoice_weekofyear = date.isocalendar()[1]
invoice_quarter = (date.month - 1) // 3 + 1
is_weekend = 1 if invoice_dayofweek >= 5 else 0

# --- Customer Features (Default/Average) ---
if customer_type == "Guest":
    is_guest = 1
    recency = 30      # average recency in days
    frequency = 1     # guest, so 1
    monetary = unitprice
else:
    is_guest = 0
    recency = 10      # recent customer
    frequency = 5     # average frequency
    monetary = unitprice * 5  # average spend

# --- Product Features (Default/Average) ---
product_total_qty = 100      # average product total quantity
product_avg_price = unitprice  # use input price
product_sales_count = 10     # average sales count

# --- Prepare Input DataFrame ---
input_df = pd.DataFrame([{
    'StockCode': stockcode,
    'UnitPrice': unitprice,
    'Country': country,
    'InvoiceYear_pipe': invoice_year,
    'InvoiceMonth_pipe': invoice_month,
    'InvoiceDay_pipe': invoice_day,
    'InvoiceDayOfWeek_pipe': invoice_dayofweek,
    'InvoiceHour_pipe': hour,
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
}])

# --- Prediction ---
if st.button("🔮 Predict Sales Quantity"):
    input_df['StockCode'] = input_df['StockCode'].astype('category')
    input_df['Country'] = input_df['Country'].astype('category')
    pred_log = model.predict(input_df)[0]
    pred_quantity = np.expm1(pred_log)

    st.metric(label="Predicted Sales Quantity", value=f"{pred_quantity:.2f}")

    # Progress bar (max 100 for demo)
    max_qty = 100
    percent = min(pred_quantity / max_qty, 1.0)
    st.progress(percent)

    # Badge
    if pred_quantity < 10:
        badge = "🔴 Low Demand"
    elif pred_quantity < 50:
        badge = "🟡 Medium Demand"
    else:
        badge = "🟢 High Demand"
    st.markdown(f"**Demand Level:** {badge}")

    st.markdown(
        f"""
            <div style="background-color:#d4edda; padding:15px; border-radius:5px; border-left:5px solid #28a745;">
                <small>This {pred_quantity:.2f} is the expected number of units you are likely to sell for the given product and transaction details.<br>
                For example, if the predicted quantity is 8.5, it means you can expect to sell around 8 or 9 units in this scenario.</small>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.info(
        "ℹ️ **Note:** Some features are set to average/default values for a smooth user experience. "
        "For more accurate predictions, connect to your database for real customer/product stats."
    )

    st.markdown("---")
    st.markdown("**Inputs Used for Prediction:**")
    st.dataframe(input_df)

st.markdown("""
---
**Tips for Best Results:**
- Use real product codes and prices for your business.
- Sale date should be the actual date of transaction.
- For advanced use, connect your app to your product/customer database.
""")

# --- Model Limitations Section ---
with st.expander("⚠️ Model Limitations & Important Notes (click to expand)"):
    st.markdown("""
- Trained on 2010-2011 e-commerce data (mostly UK sales).
- May be less accurate for other countries or recent years.
- Does not account for promotions, holidays, or external events.
- Best for products/customers similar to the training data.
    """)

st.caption("Disclaimer: Results are for informational purposes. For real-world deployment, please validate the model on your own data.")


st.markdown("""
---
<div style='text-align:center; font-size: 0.95em;'>
Created by <b>Muhammad Zain</b> | Data Scientist & Applied ML Developer<br>
<a href='https://github.com/zainafxal' target='_blank'>GitHub</a> | 
<a href='https://www.linkedin.com/in/zainafxal/' target='_blank'>LinkedIn</a>
</div>
""", unsafe_allow_html=True)