import pandas as pd
import numpy as np


def calculate_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """
    Historical Value at Risk.
    Returns the loss not exceeded with the given confidence level.
    """
    return float(np.percentile(returns.dropna(), (1 - confidence) * 100))


def calculate_max_drawdown(prices: pd.Series) -> float:
    """
    Maximum peak-to-trough percentage drop in price history.
    """
    rolling_max = prices.cummax()
    drawdown = (prices - rolling_max) / rolling_max * 100
    return float(drawdown.min())


def risk_summary(df: pd.DataFrame, coffee_type: str = "arabica") -> dict:
    """
    Returns a full risk summary for a given coffee type.
    coffee_type: 'arabica' or 'robusta'
    """
    price_col = f"{coffee_type}_usd"
    vol_col = f"{coffee_type}_volatility"
    pct_col = f"{coffee_type}_pct_change"

    current_price = df[price_col].iloc[-1]
    current_volatility = df[vol_col].iloc[-1]
    var_95 = calculate_var(df[pct_col])
    max_drawdown = calculate_max_drawdown(df[price_col])

    if current_volatility < 5:
        risk_level = "Low"
    elif current_volatility < 10:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    return {
        "coffee_type": coffee_type.capitalize(),
        "current_price_usd": round(current_price, 4),
        "current_volatility_pct": round(current_volatility, 2),
        "var_95_pct": round(var_95, 2),
        "max_drawdown_pct": round(max_drawdown, 2),
        "risk_level": risk_level
    }