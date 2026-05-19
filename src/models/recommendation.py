import pandas as pd
import numpy as np


def compute_signals(df: pd.DataFrame, coffee_type: str = "arabica") -> dict:
    """
    Extract all signals needed for recommendations from the master dataset.
    Returns a dict of signal values and their scores (0-100).
    """
    col = f"{coffee_type}_usd"
    df = df.dropna(subset=[col]).copy()

    current_price = df[col].iloc[-1]
    ma_12 = df[col].rolling(12).mean().iloc[-1]
    price_vs_avg = ((current_price - ma_12) / ma_12) * 100

    current_vol = df[f"{col.replace('_usd','')}_volatility"].iloc[-1]

    df_fx = df.dropna(subset=["ugx_per_usd"])
    current_fx = df_fx["ugx_per_usd"].iloc[-1]
    fx_3m_ago = df_fx["ugx_per_usd"].iloc[-3] if len(df_fx) >= 3 else current_fx
    fx_trend = ((current_fx - fx_3m_ago) / fx_3m_ago) * 100

    drought = int(df.dropna(subset=["drought_flag"])["drought_flag"].iloc[-1])
    health = float(df.dropna(subset=["health_score"])["health_score"].iloc[-1])

    # Score each signal 0-100
    # Price vs average: above average is good for selling
    if price_vs_avg > 30:
        price_score = 90
    elif price_vs_avg > 15:
        price_score = 75
    elif price_vs_avg > 0:
        price_score = 55
    elif price_vs_avg > -15:
        price_score = 35
    else:
        price_score = 15

    # Volatility: lower is better for planning
    if current_vol < 5:
        vol_score = 85
    elif current_vol < 8:
        vol_score = 65
    elif current_vol < 12:
        vol_score = 45
    else:
        vol_score = 20

    # FX trend: rising rate (weaker shilling) benefits exporters now
    if fx_trend > 2:
        fx_score = 80
    elif fx_trend > 0:
        fx_score = 65
    elif fx_trend > -2:
        fx_score = 45
    else:
        fx_score = 25

    # Drought: no drought is good
    drought_score = 20 if drought == 1 else 85

    # Crop health: higher is better
    if health > 70:
        health_score_val = 85
    elif health > 50:
        health_score_val = 65
    elif health > 30:
        health_score_val = 40
    else:
        health_score_val = 15

    # Weights
    weights = {
        "price": 0.30,
        "volatility": 0.20,
        "fx": 0.20,
        "drought": 0.15,
        "health": 0.15
    }

    overall = (
        price_score * weights["price"] +
        vol_score * weights["volatility"] +
        fx_score * weights["fx"] +
        drought_score * weights["drought"] +
        health_score_val * weights["health"]
    )

    return {
        "overall_score": round(overall),
        "current_price": round(current_price, 4),
        "price_vs_avg_pct": round(price_vs_avg, 1),
        "price_score": price_score,
        "current_volatility": round(current_vol, 2),
        "vol_score": vol_score,
        "fx_rate": round(current_fx),
        "fx_trend_pct": round(fx_trend, 1),
        "fx_score": fx_score,
        "drought_flag": drought,
        "drought_score": drought_score,
        "health_score": round(health, 1),
        "health_score_val": health_score_val,
    }


def generate_recommendations(signals: dict) -> dict:
    """
    Generate three action recommendations from signal scores.
    Returns pricing, FX, and volume recommendations.
    """
    score = signals["overall_score"]
    price_vs_avg = signals["price_vs_avg_pct"]
    vol = signals["current_volatility"]
    fx_trend = signals["fx_trend_pct"]
    drought = signals["drought_flag"]
    health = signals["health_score"]

    # Overall label
    if score >= 75:
        overall_label = "Strongly favourable"
        overall_colour = "#1D9E75"
    elif score >= 60:
        overall_label = "Moderately favourable"
        overall_colour = "#FCDC04"
    elif score >= 45:
        overall_label = "Neutral"
        overall_colour = "#888780"
    else:
        overall_label = "Unfavourable"
        overall_colour = "#D90000"

    # Pricing recommendation
    if price_vs_avg > 20 and vol < 10:
        price_action = "Consider selling now"
        price_conf = 4
        price_reason = (
            f"Prices are {price_vs_avg:.1f}% above the 12-month average with "
            f"relatively low volatility ({vol:.1f}%). Historically, selling above "
            f"the annual average has yielded better returns than waiting. "
            f"The forecast model suggests prices may soften in the coming months."
        )
    elif price_vs_avg > 20 and vol >= 10:
        price_action = "Consider selling in tranches"
        price_conf = 3
        price_reason = (
            f"Prices are {price_vs_avg:.1f}% above average but volatility is high "
            f"({vol:.1f}%). Splitting your sale across several weeks reduces the "
            f"risk of selling everything at a temporary peak."
        )
    elif price_vs_avg < -10:
        price_action = "Consider holding — prices below average"
        price_conf = 3
        price_reason = (
            f"Prices are {abs(price_vs_avg):.1f}% below the 12-month average. "
            f"Unless you have urgent cash flow needs, waiting for a recovery "
            f"towards the historical mean may yield better returns."
        )
    else:
        price_action = "No strong signal — monitor weekly"
        price_conf = 2
        price_reason = (
            f"Prices are close to the 12-month average ({price_vs_avg:+.1f}%). "
            f"There is no compelling reason to rush a sale or delay. "
            f"Watch the forecast and volatility trends over the next 2 to 4 weeks."
        )

    # FX recommendation
    if fx_trend > 1.5:
        fx_action = "Convert USD earnings to UGX promptly"
        fx_conf = 4
        fx_reason = (
            f"The shilling has weakened {fx_trend:.1f}% against the dollar over "
            f"the past 3 months, meaning each USD converts to more shillings today "
            f"than recently. Holding earnings in USD carries the risk of the rate "
            f"reversing before you convert."
        )
    elif fx_trend < -1.5:
        fx_action = "Consider holding earnings in USD"
        fx_conf = 3
        fx_reason = (
            f"The shilling has strengthened {abs(fx_trend):.1f}% against the dollar "
            f"recently, meaning you would receive fewer shillings per dollar today "
            f"than 3 months ago. If this trend continues, waiting to convert "
            f"may yield a better UGX return."
        )
    else:
        fx_action = "No strong FX signal — convert as normal"
        fx_conf = 2
        fx_reason = (
            f"The UGX/USD rate has been relatively stable over the past 3 months "
            f"(change: {fx_trend:+.1f}%). There is no compelling reason to time "
            f"your currency conversion differently from your usual pattern."
        )

    # Volume recommendation
    if drought == 1 and health < 30:
        vol_action = "Increase exports now before supply tightens"
        vol_conf = 4
        vol_reason = (
            f"Both a drought flag and low crop health ({health:.1f}/100) are active "
            f"simultaneously. This combination suggests the harvest in 6 to 9 months "
            f"will be smaller. Exporting available stock now — before supply tightens "
            f"and buyers shift to other origins — is prudent."
        )
    elif drought == 1 or health < 30:
        vol_action = "Monitor supply — one stress signal active"
        vol_conf = 3
        vol_reason = (
            f"One weather stress signal is active "
            f"({'drought' if drought else f'crop health at {health:.1f}/100'}). "
            f"This may affect the harvest in 6 to 9 months. Watch for the second "
            f"signal to confirm before adjusting export volumes significantly."
        )
    elif health > 70:
        vol_action = "Maintain current export volume"
        vol_conf = 3
        vol_reason = (
            f"No drought is active and crop health is strong at {health:.1f}/100. "
            f"Supply looks stable for the coming season. There is no weather-based "
            f"reason to rush exports or hold them back."
        )
    else:
        vol_action = "Maintain current volume — neutral signals"
        vol_conf = 2
        vol_reason = (
            f"Weather signals are mixed. Crop health is at {health:.1f}/100 — "
            f"not alarming but worth monitoring. No drought is currently active. "
            f"Maintain normal export patterns and review again next month."
        )

    return {
        "overall_score": score,
        "overall_label": overall_label,
        "overall_colour": overall_colour,
        "pricing": {
            "action": price_action,
            "confidence": price_conf,
            "reason": price_reason
        },
        "fx": {
            "action": fx_action,
            "confidence": fx_conf,
            "reason": fx_reason
        },
        "volume": {
            "action": vol_action,
            "confidence": vol_conf,
            "reason": vol_reason
        }
    }