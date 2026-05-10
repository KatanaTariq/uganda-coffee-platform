def simulate_revenue(
    price_usd_per_kg: float,
    volume_tonnes: float,
    ugx_per_usd: float
) -> dict:
    """
    Calculate export revenue in USD and UGX.
    price_usd_per_kg : global coffee price
    volume_tonnes    : export volume in tonnes
    ugx_per_usd      : exchange rate
    """
    volume_kg = volume_tonnes * 1000
    revenue_usd = price_usd_per_kg * volume_kg
    revenue_ugx = revenue_usd * ugx_per_usd
    revenue_per_tonne_ugx = revenue_ugx / volume_tonnes

    return {
        "revenue_usd": round(revenue_usd, 2),
        "revenue_ugx": round(revenue_ugx, 2),
        "revenue_per_tonne_ugx": round(revenue_per_tonne_ugx, 2)
    }


def run_scenarios(
    base_price: float,
    base_volume: float,
    base_fx: float
) -> dict:
    """
    Run five named stress scenarios against a baseline.
    Returns revenue impact in UGX and percentage change for each.
    """
    scenarios = {
        "Baseline":        (base_price,        base_volume,        base_fx),
        "UGX weakens 5%":  (base_price,        base_volume,        base_fx * 0.95),
        "Price drops 10%": (base_price * 0.90, base_volume,        base_fx),
        "Volume falls 15%":(base_price,        base_volume * 0.85, base_fx),
        "Combined stress": (base_price * 0.90, base_volume * 0.85, base_fx * 0.95),
    }

    baseline_ugx = simulate_revenue(*scenarios["Baseline"])["revenue_ugx"]
    results = {}

    for name, (p, v, f) in scenarios.items():
        r = simulate_revenue(p, v, f)
        r["pct_change"] = round(
            (r["revenue_ugx"] - baseline_ugx) / baseline_ugx * 100, 2
        )
        results[name] = r

    return results