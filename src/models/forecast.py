import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error


def prepare_prophet_df(df, coffee_type="arabica"):
    col = f"{coffee_type}_usd"
    prophet_df = df[["date", col]].copy()
    prophet_df.columns = ["ds", "y"]
    prophet_df = prophet_df.dropna()
    return prophet_df


def train_and_forecast(df, coffee_type="arabica", periods=12):
    prophet_df = prepare_prophet_df(df, coffee_type)

    train = prophet_df.iloc[:-12]
    test = prophet_df.iloc[-12:]

    model = Prophet(
        interval_width=0.95,
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode="multiplicative"
    )
    model.fit(train)

    future = model.make_future_dataframe(periods=12 + periods, freq="MS")
    forecast = model.predict(future)

    test_forecast = forecast[
        forecast["ds"].isin(test["ds"])
    ][["ds", "yhat"]].reset_index(drop=True)
    test_actual = test.reset_index(drop=True)

    mae = mean_absolute_error(test_actual["y"], test_forecast["yhat"])
    rmse = np.sqrt(mean_squared_error(test_actual["y"], test_forecast["yhat"]))
    mape = float(
        np.mean(
            np.abs(
                (test_actual["y"].values - test_forecast["yhat"].values)
                / test_actual["y"].values
            )
        ) * 100
    )

    metrics = {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mape": round(mape, 2)
    }

    return forecast, metrics