import pandas as pd


def load_coffee_prices(filepath: str) -> pd.DataFrame:
    """Load and clean World Bank Pink Sheet coffee price data."""
    df = pd.read_excel(
        filepath,
        sheet_name="Monthly Prices",
        skiprows=4
    )

    df = df[["Unnamed: 0", "Coffee, Arabica", "Coffee, Robusta"]].copy()
    df.columns = ["date_raw", "arabica_usd", "robusta_usd"]
    df = df.dropna(subset=["date_raw"])

    df["date"] = pd.to_datetime(
        df["date_raw"].astype(str).str.replace("M", "-"),
        format="%Y-%m"
    )

    df = df.dropna(subset=["arabica_usd", "robusta_usd"], how="all")
    df = df.sort_values("date").reset_index(drop=True)
    df = df[["date", "arabica_usd", "robusta_usd"]]

    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add rolling averages, returns and volatility columns."""
    df = df.copy()

    df["arabica_ma3"] = df["arabica_usd"].rolling(3).mean()
    df["robusta_ma3"] = df["robusta_usd"].rolling(3).mean()

    df["arabica_pct_change"] = df["arabica_usd"].pct_change() * 100
    df["robusta_pct_change"] = df["robusta_usd"].pct_change() * 100

    df["arabica_volatility"] = df["arabica_pct_change"].rolling(12).std()
    df["robusta_volatility"] = df["robusta_pct_change"].rolling(12).std()

    return df