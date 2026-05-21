import pandas as pd


def get_current_price(df: pd.DataFrame, coffee_type: str) -> float:
    col = f"{coffee_type}_usd"
    return float(df[col].dropna().iloc[-1])


def calculate_projected_revenue(
    yield_tonnes: float,
    current_price_usd: float
) -> float:
    return yield_tonnes * 1000 * current_price_usd


def calculate_returns(
    investment: float,
    projected_revenue: float,
    optimistic_multiplier: float = 1.15,
    stressed_multiplier: float = 0.75
) -> dict:
    stake_pct = investment / projected_revenue

    base_return = stake_pct * projected_revenue
    opt_return = stake_pct * projected_revenue * optimistic_multiplier
    stress_return = stake_pct * projected_revenue * stressed_multiplier

    return {
        "stake_pct": round(stake_pct * 100, 3),
        "baseline": round(base_return, 2),
        "optimistic": round(opt_return, 2),
        "stressed": round(stress_return, 2),
        "baseline_roi": round((base_return - investment) / investment * 100, 1),
        "optimistic_roi": round((opt_return - investment) / investment * 100, 1),
        "stressed_roi": round((stress_return - investment) / investment * 100, 1),
    }