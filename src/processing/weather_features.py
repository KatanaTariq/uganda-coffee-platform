import pandas as pd
import numpy as np


def load_era5(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=["date"])
    return df


def supply_risk_score(drought_flag: int, health_score: float) -> tuple:
    """
    Returns (score 0-2, label) based on combined weather signals.
    0 = Low, 1 = Moderate, 2 = Elevated
    """
    if drought_flag == 1 and health_score < 30:
        return 2, "Elevated — drought and low crop health"
    elif drought_flag == 1 or health_score < 30:
        return 1, "Moderate — one stress signal active"
    else:
        return 0, "Low — no stress signals detected"