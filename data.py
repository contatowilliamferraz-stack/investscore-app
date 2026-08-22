import pandas as pd
import yfinance as yf


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def get_data(ticker):
    stock = yf.Ticker(ticker)

    info = stock.info or {}

    fast = {}
    try:
        fast = stock.fast_info or {}
    except Exception:
        fast = {}

    hist = pd.DataFrame()
    try:
        hist = stock.history(period="10d", auto_adjust=False)
    except Exception:
        hist = pd.DataFrame()

    dividends = pd.Series(dtype=float)
    try:
        dividends = stock.dividends
    except Exception:
        dividends = pd.Series(dtype=float)

    dividendo_anual = 0.0
    try:
        if dividends is not None and not dividends.empty:
            dividends.index = pd.to_datetime(dividends.index).tz_localize(None)
            corte = pd.Timestamp.today().tz_localize(None) - pd.Timedelta(days=365)
            dividendo_anual = float(dividends[dividends.index >= corte].sum())
    except Exception:
        dividendo_anual = 0.0

    current_price = _safe_float(info.get("currentPrice", 0))
    previous_close = _safe_float(info.get("previousClose", 0))

    if not hist.empty and "Close" in hist.columns:
        try:
            hist = hist.copy()
            hist.index = pd.to_datetime(hist.index).tz_localize(None)
            closes = hist["Close"].dropna()
            if len(closes) >= 1 and current_price <= 0:
                current_price = _safe_float(closes.iloc[-1], 0)
            if len(closes) >= 2 and previous_close <= 0:
                previous_close = _safe_float(closes.iloc[-2], 0)
        except Exception:
            pass

    if current_price <= 0:
        current_price = _safe_float(fast.get("lastPrice", 0), 0)

    if previous_close <= 0:
        previous_close = _safe_float(fast.get("previousClose", 0), 0)

    info["currentPrice"] = current_price
    info["previousClose"] = previous_close
    info["dividendo_anual"] = dividendo_anual

    return info
