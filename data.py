import time
import pandas as pd
import yfinance as yf


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _com_retry(func, tentativas=3, espera_inicial=1.5):
    """
    O Yahoo Finance bloqueia temporariamente pedidos em rajada (erro 429,
    "too many requests"), o que acontece com mais frequência em serviços
    de alojamento partilhado como o Streamlit Community Cloud — onde
    muitos projetos diferentes de pessoas diferentes partilham o mesmo
    intervalo de IPs, e por isso o "orçamento" de pedidos por IP esgota-se
    mais depressa do que aconteceria a correr isto localmente.

    Esta função tenta de novo, com espera crescente entre tentativas
    (1.5s, depois 3s, depois 6s), antes de desistir e deixar o erro
    subir para quem chamou.
    """
    ultimo_erro = None
    for tentativa in range(tentativas):
        try:
            return func()
        except Exception as e:
            ultimo_erro = e
            if tentativa < tentativas - 1:
                time.sleep(espera_inicial * (2 ** tentativa))
    raise ultimo_erro


def get_data(ticker):
    stock = yf.Ticker(ticker)

    try:
        info = _com_retry(lambda: stock.info or {})
    except Exception:
        info = {}

    fast = {}
    try:
        fast = _com_retry(lambda: stock.fast_info or {})
    except Exception:
        fast = {}

    hist = pd.DataFrame()
    try:
        hist = _com_retry(lambda: stock.history(period="10d", auto_adjust=False))
    except Exception:
        hist = pd.DataFrame()

    dividends = pd.Series(dtype=float)
    try:
        dividends = _com_retry(lambda: stock.dividends)
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
