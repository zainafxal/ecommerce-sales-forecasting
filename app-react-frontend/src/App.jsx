import React, { useEffect, useState } from 'react';
import { getApiHealth, predictSales } from './services/api';
import './index.css';

const PRODUCT_CODES = ["85123A", "85099B", "22423", "47566", "20725", "other"];
const CURRENCIES = ["GBP (British Pound)", "PKR (Pakistani Rupee)", "USD (US Dollar)", "EUR (Euro)", "Other"];
const COUNTRIES = ["united kingdom", "france", "germany", "spain", "netherlands", "switzerland", "portugal", "italy", "norway", "other"];

const WAKING_TOAST = {
  variant: "warming",
  title: "Waking backend",
  message: "The hosted API is starting up. This can take a short while on free infrastructure.",
};

function App() {
  const [stockcodeSelect, setStockcodeSelect] = useState(PRODUCT_CODES[0]);
  const [stockcodeOther, setStockcodeOther] = useState("");
  const [currency, setCurrency] = useState(CURRENCIES[0]);
  const [unitPriceInput, setUnitPriceInput] = useState(2.55);
  const [exchangeRate, setExchangeRate] = useState("");
  const [country, setCountry] = useState(COUNTRIES[0]);
  const [saleDate, setSaleDate] = useState("2011-12-01");
  const [hour, setHour] = useState(8);
  const [customerType, setCustomerType] = useState("Registered");

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState("checking");
  const [showDisclaimer, setShowDisclaimer] = useState(false);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    let isMounted = true;
    let wakeRetryTimeout;
    let healthPollInterval;
    let successToastTimeout;
    let wakeModeActive = false;

    const clearToast = () => {
      if (isMounted) {
        setToast(null);
      }
    };

    const showWakeToast = () => {
      if (isMounted) {
        setToast(WAKING_TOAST);
      }
    };

    const showReadyToast = () => {
      if (!isMounted) {
        return;
      }

      setToast({
        variant: "success",
        title: "Backend ready",
        message: "The API is online and ready for live predictions.",
      });

      window.clearTimeout(successToastTimeout);
      successToastTimeout = window.setTimeout(() => {
        if (isMounted) {
          setToast(null);
        }
      }, 3200);
    };

    const markAsWaking = () => {
      if (!isMounted) {
        return;
      }

      wakeModeActive = true;
      setBackendStatus("waking");
      showWakeToast();
    };

    const checkStatus = async ({ initial = false } = {}) => {
      try {
        const health = await getApiHealth({ timeoutMs: initial ? 4500 : 6000 });
        if (!isMounted) {
          return false;
        }

        if (health.model_loaded) {
          setBackendStatus("online");
          if (wakeModeActive) {
            wakeModeActive = false;
            showReadyToast();
          } else {
            clearToast();
          }
          return true;
        }

        if (initial || wakeModeActive) {
          markAsWaking();
          return false;
        }

        setBackendStatus("offline");
        return false;
      } catch (healthError) {
        if (!isMounted) {
          return false;
        }

        if (initial || wakeModeActive) {
          markAsWaking();
          return false;
        }

        setBackendStatus("offline");
        return false;
      }
    };

    const startWakeLoop = () => {
      markAsWaking();

      const wakeLoop = async () => {
        const isOnline = await checkStatus();
        if (!isMounted || isOnline) {
          return;
        }

        wakeRetryTimeout = window.setTimeout(wakeLoop, 5000);
      };

      wakeRetryTimeout = window.setTimeout(wakeLoop, 2500);
    };

    const bootstrapHealthCheck = async () => {
      const isOnline = await checkStatus({ initial: true });
      if (!isMounted || isOnline) {
        return;
      }

      startWakeLoop();
    };

    bootstrapHealthCheck();

    healthPollInterval = window.setInterval(() => {
      checkStatus();
    }, 30000);

    return () => {
      isMounted = false;
      window.clearInterval(healthPollInterval);
      window.clearTimeout(wakeRetryTimeout);
      window.clearTimeout(successToastTimeout);
    };
  }, []);

  const finalStockcode = stockcodeSelect === "other" ? stockcodeOther : stockcodeSelect;

  let finalUnitPrice = unitPriceInput;
  if (currency !== "GBP (British Pound)" && exchangeRate.trim() !== "") {
    const rate = parseFloat(exchangeRate);
    if (!Number.isNaN(rate) && rate > 0) {
      finalUnitPrice = unitPriceInput / rate;
    }
  }

  const handlePredict = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    if (!finalStockcode) {
      setError("Please select or enter a product code.");
      setLoading(false);
      return;
    }

    try {
      const payload = {
        stockcode: finalStockcode,
        unitprice: finalUnitPrice,
        country,
        sale_date: saleDate,
        hour: parseInt(hour, 10),
        customer_type: customerType,
      };

      const data = await predictSales(payload);
      setResult(data);
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    } catch (predictionError) {
      setError(predictionError.message || "An error occurred during prediction.");
    } finally {
      setLoading(false);
    }
  };

  const statusLabel = backendStatus === "checking"
    ? "Checking API..."
    : backendStatus === "waking"
      ? "Waking Backend..."
      : backendStatus === "online"
        ? "API Online"
        : "API Offline";

  const buttonLabel = loading
    ? "Predicting..."
    : backendStatus === "waking"
      ? "Waking backend..."
      : backendStatus === "offline"
        ? "⚠️ API Offline - Check Backend"
        : "🔮 Predict Sales Quantity";

  return (
    <div className="app-container">
      {toast && (
        <div className={`status-toast ${toast.variant}`} role="status" aria-live="polite">
          <div className="status-toast-title">{toast.title}</div>
          <p>{toast.message}</p>
        </div>
      )}

      <header className="header">
        <div className="header-titles">
          <h1><span className="emoji">🛒</span> <span className="title-text">E-Commerce Sales Forecasting</span></h1>
          <p>Predict expected sales quantity with an intelligent XGBoost model.</p>
        </div>
        <div className="status-indicator">
          <div className={`status-dot ${backendStatus}`}></div>
          {statusLabel}
        </div>
      </header>

      <form onSubmit={handlePredict}>
        <div className="form-grid">
          <div className="glass-card">
            <h2 className="section-title">📦 Product Info</h2>
            <div className="form-group">
              <label>Product Code (SKU)</label>
              <select
                value={stockcodeSelect}
                onChange={(event) => setStockcodeSelect(event.target.value)}
              >
                {PRODUCT_CODES.map((code) => <option key={code} value={code}>{code}</option>)}
              </select>
            </div>

            {stockcodeSelect === "other" && (
              <div className="form-group" style={{ animation: 'fadeInDown 0.3s' }}>
                <label>Enter Product Code</label>
                <input
                  type="text"
                  value={stockcodeOther}
                  onChange={(event) => setStockcodeOther(event.target.value)}
                  placeholder="e.g. 12345C"
                  required
                />
              </div>
            )}

            <h2 className="section-title" style={{ marginTop: '1.5rem' }}>👤 Customer Info</h2>
            <div className="form-group">
              <label>Customer Type</label>
              <div className="radio-group">
                <label className="radio-label">
                  <input
                    type="radio"
                    name="customerType"
                    value="Registered"
                    checked={customerType === "Registered"}
                    onChange={(event) => setCustomerType(event.target.value)}
                  />
                  Registered
                </label>
                <label className="radio-label">
                  <input
                    type="radio"
                    name="customerType"
                    value="Guest"
                    checked={customerType === "Guest"}
                    onChange={(event) => setCustomerType(event.target.value)}
                  />
                  Guest
                </label>
              </div>
            </div>
          </div>

          <div className="glass-card">
            <h2 className="section-title">💱 Pricing</h2>
            <div className="form-group">
              <label>Currency</label>
              <select value={currency} onChange={(event) => setCurrency(event.target.value)}>
                {CURRENCIES.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Unit Price ({currency.split(' ')[0]})</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={unitPriceInput}
                onChange={(event) => setUnitPriceInput(parseFloat(event.target.value) || 0)}
                required
              />
            </div>

            {currency !== "GBP (British Pound)" && (
              <div className="form-group" style={{ animation: 'fadeInDown 0.3s' }}>
                <label>Exchange Rate (1 GBP = ? {currency.split(' ')[0]})</label>
                <input
                  type="number"
                  step="0.001"
                  value={exchangeRate}
                  onChange={(event) => setExchangeRate(event.target.value)}
                  placeholder="e.g. 1.25"
                />
                <span className="help-text" style={{ fontSize: '0.75rem' }}>
                  {exchangeRate
                    ? `Conv. Unit Price: ${(unitPriceInput / parseFloat(exchangeRate)).toFixed(4)} GBP`
                    : "If left blank, input price will be used as GBP."}
                </span>
              </div>
            )}
          </div>

          <div className="glass-card">
            <h2 className="section-title">🌍 Transaction Details</h2>
            <div className="form-group">
              <label>Country of Sale</label>
              <select value={country} onChange={(event) => setCountry(event.target.value)}>
                {COUNTRIES.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Sale Date</label>
              <input
                type="date"
                value={saleDate}
                onChange={(event) => setSaleDate(event.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Hour of Sale: <span className="slider-value">{hour}:00</span></label>
              <div className="slider-container">
                <span style={{ color: 'var(--text-muted)' }}>0h</span>
                <input
                  type="range"
                  min="0"
                  max="23"
                  value={hour}
                  onChange={(event) => setHour(event.target.value)}
                  className="slider"
                />
                <span style={{ color: 'var(--text-muted)' }}>23h</span>
              </div>
            </div>
          </div>
        </div>

        <button
          type="submit"
          className="btn-primary"
          disabled={loading || backendStatus === 'offline' || backendStatus === 'waking'}
        >
          {loading ? (
            <><div className="spinner"></div> {buttonLabel}</>
          ) : (
            buttonLabel
          )}
        </button>
      </form>

      {error && (
        <div className="glass-card full-width" style={{ marginTop: '1.5rem', borderColor: 'var(--danger)' }}>
          <h3 style={{ color: 'var(--danger)', marginBottom: '0.5rem' }}>⚠️ Error</h3>
          <p>{error}</p>
        </div>
      )}

      {result && !error && (
        <div className="glass-card result-card full-width" style={{ marginTop: '1.5rem' }}>
          <div className="metric-label">Predicted Sales Quantity</div>
          <div className="metric-value">{result.predicted_quantity.toFixed(2)}</div>

          <div className="progress-container">
            <div
              className="progress-bar"
              style={{ width: `${Math.min(result.predicted_quantity, 100)}%` }}
            ></div>
          </div>

          <div className="badge">
            {result.demand_level}
          </div>

          <div className="info-box">
            This <strong>{result.predicted_quantity.toFixed(2)}</strong> is the expected number of units you are likely to sell for the given product and transaction details. For example, if the predicted quantity is 8.5, it means you can expect to sell around 8 or 9 units in this scenario.
          </div>
        </div>
      )}

      <div className="disclaimer-section">
        <div className="accordion">
          <button
            className="accordion-header"
            onClick={() => setShowDisclaimer(!showDisclaimer)}
            type="button"
          >
            <span>⚠️ Model Limitations & Important Notes</span>
            <span>{showDisclaimer ? '▲' : '▼'}</span>
          </button>

          {showDisclaimer && (
            <div className="accordion-content">
              <ul>
                <li>Trained on 2010-2011 e-commerce data (mostly UK sales).</li>
                <li>May be less accurate for other countries or recent years.</li>
                <li>Does not account for promotions, holidays, or external events.</li>
                <li>Best for products/customers similar to the training data.</li>
              </ul>
              <p style={{ marginTop: '1rem', fontStyle: 'italic', fontSize: '0.85rem' }}>
                Disclaimer: Results are for informational purposes. For real-world deployment, please validate the model on your own data.
              </p>
            </div>
          )}
        </div>

        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <a
            href="https://github.com/zainafxal/ecommerce-sales-forecasting/tree/main/notebooks"
            target="_blank"
            rel="noreferrer"
            className="btn-notebook"
          >
            📓 View Data Science Notebooks
          </a>
        </div>

        <div className="footer-text">
          Created by <strong>Muhammad Zain</strong> | Data Scientist & Applied ML Developer
          <div className="footer-links">
            <a href="https://github.com/zainafxal" target="_blank" rel="noreferrer">GitHub</a>
            <span style={{ color: 'var(--text-muted)' }}>|</span>
            <a href="https://www.linkedin.com/in/zainafxal/" target="_blank" rel="noreferrer">LinkedIn</a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
