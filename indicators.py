def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def calculate_indicators(data):
    return {
        "DividendYield": _safe_float(data.get("dividendYield", 0)),
        "ROE": _safe_float(data.get("returnOnEquity", 0)),
        "Margin": _safe_float(data.get("profitMargins", 0)),
        "Debt": _safe_float(data.get("debtToEquity", 0)),
        "Growth": _safe_float(data.get("earningsGrowth", data.get("revenueGrowth", 0))),
        "CurrentPrice": _safe_float(data.get("currentPrice", 0)),
        "PreviousClose": _safe_float(data.get("previousClose", 0)),
        "AnnualDividend": _safe_float(data.get("dividendo_anual", 0)),
    }
