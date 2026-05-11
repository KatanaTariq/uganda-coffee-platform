import sys
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

sys.path.append("../src")

from processing.clean import load_coffee_prices, add_features
from models.risk import risk_summary
from models.simulator import simulate_revenue, run_scenarios
from models.forecast import train_and_forecast

st.set_page_config(
    page_title="Uganda Coffee Platform",
    page_icon="☕",
    layout="wide"
)

st.title("Uganda Coffee Price & Risk Platform")
st.caption("Commodity risk analytics for Uganda's coffee export market")

@st.cache_data
def load_data():
    df = load_coffee_prices("../data/raw/coffee_prices.xlsx")
    df = add_features(df)
    fx = pd.read_csv("../data/processed/ugx_usd_monthly.csv", parse_dates=["date"])
    df = df.merge(fx, on="date", how="left")
    df["arabica_ugx"] = df["arabica_usd"] * df["ugx_per_usd"]
    df["robusta_ugx"] = df["robusta_usd"] * df["ugx_per_usd"]
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
coffee_type = st.sidebar.selectbox("Coffee type", ["Arabica", "Robusta"])
year_range = st.sidebar.slider(
    "Year range",
    min_value=1960,
    max_value=2026,
    value=(2000, 2026)
)

col = "arabica" if coffee_type == "Arabica" else "robusta"
df_filtered = df[
    (df["date"].dt.year >= year_range[0]) &
    (df["date"].dt.year <= year_range[1])
]

# Row 1 — risk metrics
risk = risk_summary(df, col)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Current price (USD/kg)", f"${risk['current_price_usd']}")
m2.metric("Volatility", f"{risk['current_volatility_pct']}%")
m3.metric("95% VaR", f"{risk['var_95_pct']}%")
m4.metric("Max drawdown", f"{risk['max_drawdown_pct']}%")

st.divider()

# Row 2 — price chart
st.subheader("Price history")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_filtered["date"],
    y=df_filtered[f"{col}_usd"],
    name=coffee_type,
    line=dict(color="#8B4513", width=1.5)
))
fig.add_trace(go.Scatter(
    x=df_filtered["date"],
    y=df_filtered[f"{col}_ma3"],
    name="3M moving average",
    line=dict(color="#8B4513", dash="dot", width=1)
))
fig.update_layout(template="plotly_white", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Row 3 — volatility chart
st.subheader("Price volatility")
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df_filtered["date"],
    y=df_filtered[f"{col}_volatility"],
    name="12M rolling volatility",
    line=dict(color="#D2691E", width=1.5),
    fill="tozeroy",
    fillcolor="rgba(210,105,30,0.1)"
))
fig2.update_layout(
    template="plotly_white",
    yaxis_title="Volatility (%)",
    hovermode="x unified"
)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Row 4 — FX history
st.subheader("UGX/USD exchange rate history")

df_fx_chart = df.dropna(subset=["ugx_per_usd"])
current_fx = int(df_fx_chart["ugx_per_usd"].iloc[-1])

fig_fx = go.Figure()
fig_fx.add_trace(go.Scatter(
    x=df_fx_chart["date"],
    y=df_fx_chart["ugx_per_usd"],
    name="UGX per USD",
    line=dict(color="#534AB7", width=1.5),
    fill="tozeroy",
    fillcolor="rgba(83,74,183,0.08)"
))
fig_fx.update_layout(
    template="plotly_white",
    yaxis_title="UGX per 1 USD",
    hovermode="x unified"
)
st.plotly_chart(fig_fx, use_container_width=True)

fx1, fx2, fx3 = st.columns(3)
fx1.metric("Current rate", f"{current_fx:,} UGX")

rate_1yr_ago = df_fx_chart[df_fx_chart["date"] == "2025-04-01"]["ugx_per_usd"]
fx2.metric(
    "Rate 1 year ago",
    f"{int(rate_1yr_ago.values[0]):,} UGX" if len(rate_1yr_ago) > 0 else "N/A"
)

rate_2020 = df_fx_chart[df_fx_chart["date"] == "2020-01-01"]["ugx_per_usd"]
if len(rate_2020) > 0:
    change = ((current_fx / rate_2020.values[0]) - 1) * 100
    fx3.metric("UGX change vs 2020", f"{change:.1f}%")
else:
    fx3.metric("UGX change vs 2020", "N/A")

st.divider()

# Row 5 — revenue simulator
st.subheader("Revenue simulator")
s1, s2, s3 = st.columns(3)
price = s1.slider("Price (USD/kg)", 1.0, 10.0, float(round(risk["current_price_usd"], 2)), 0.05)
volume = s2.slider("Export volume (tonnes)", 100, 5000, 1000, 50)
fx = s3.slider("UGX per USD", 2500, 5000, current_fx, 10)

rev = simulate_revenue(price, volume, fx)
r1, r2, r3 = st.columns(3)
r1.metric("Revenue (USD)", f"${rev['revenue_usd']:,.0f}")
r2.metric("Revenue (UGX)", f"{rev['revenue_ugx']:,.0f}")
r3.metric("Per tonne (UGX)", f"{rev['revenue_per_tonne_ugx']:,.0f}")

st.divider()

# Row 6 — scenario analysis
st.subheader("Scenario analysis")
scenarios = run_scenarios(price, volume, fx)
scenario_df = pd.DataFrame([
    {
        "Scenario": name,
        "Revenue (UGX)": f"{data['revenue_ugx']:,.0f}",
        "Change": f"{data['pct_change']}%"
    }
    for name, data in scenarios.items()
])
st.dataframe(scenario_df, use_container_width=True, hide_index=True)

fig3 = go.Figure(go.Bar(
    x=list(scenarios.keys()),
    y=[v["revenue_ugx"] / 1e9 for v in scenarios.values()],
    marker_color=["#1D9E75", "#E24B4A", "#E24B4A", "#E24B4A", "#A32D2D"]
))
fig3.update_layout(
    template="plotly_white",
    yaxis_title="Revenue (Billion UGX)",
)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# Row 7 — price forecast
st.subheader("Price forecast")

with st.spinner("Training forecast model - please wait..."):
    forecast, metrics = train_and_forecast(df, col, periods=12)

m1, m2, m3 = st.columns(3)
m1.metric("MAE", f"${metrics['mae']}/kg")
m2.metric("RMSE", f"${metrics['rmse']}/kg")
m3.metric("MAPE", f"{metrics['mape']}%")

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=df_filtered["date"],
    y=df_filtered[f"{col}_usd"],
    name="Historical price",
    line=dict(color="#8B4513", width=1.5)
))
fig4.add_trace(go.Scatter(
    x=forecast["ds"],
    y=forecast["yhat"],
    name="Price forecast",
    line=dict(color="#1D9E75", width=2, dash="dot")
))
fig4.add_trace(go.Scatter(
    x=list(forecast["ds"]) + list(forecast["ds"][::-1]),
    y=list(forecast["yhat_upper"]) + list(forecast["yhat_lower"][::-1]),
    fill="toself",
    fillcolor="rgba(29,158,117,0.1)",
    line=dict(color="rgba(255,255,255,0)"),
    name="95% confidence interval"
))
fig4.update_layout(
    template="plotly_white",
    yaxis_title="Price (USD/kg)",
    hovermode="x unified",
    xaxis=dict(range=["2015-01-01", "2027-06-01"])
)
st.plotly_chart(fig4, use_container_width=True)

st.caption(
    "MAE = average error in USD/kg. "
    "RMSE = penalises large errors more heavily. "
    "MAPE = average error as a percentage of actual price. "
    "Wide confidence intervals reflect genuine commodity market uncertainty."
)