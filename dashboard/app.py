import sys
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

sys.path.append("../src")

from processing.clean import load_coffee_prices, add_features
from models.risk import risk_summary
from models.simulator import simulate_revenue, run_scenarios

st.set_page_config(
    page_title="Uganda Coffee Platform",
    page_icon="☕",
    layout="wide"
)

st.title("Uganda Coffee Price & Risk Platform")
st.caption("Commodity risk analytics for Uganda's coffee export market")

# Load data
@st.cache_data
def load_data():
    df = load_coffee_prices("../data/raw/coffee_prices.xlsx")
    df = add_features(df)
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

# Row 4 — revenue simulator
st.subheader("Revenue simulator")
s1, s2, s3 = st.columns(3)
price = s1.slider("Price (USD/kg)", 1.0, 10.0, float(round(risk["current_price_usd"], 2)), 0.05)
volume = s2.slider("Export volume (tonnes)", 100, 5000, 1000, 50)
fx = s3.slider("UGX per USD", 2500, 5000, 3700, 10)

rev = simulate_revenue(price, volume, fx)
r1, r2, r3 = st.columns(3)
r1.metric("Revenue (USD)", f"${rev['revenue_usd']:,.0f}")
r2.metric("Revenue (UGX)", f"{rev['revenue_ugx']:,.0f}")
r3.metric("Per tonne (UGX)", f"{rev['revenue_per_tonne_ugx']:,.0f}")

st.divider()

# Row 5 — scenario analysis
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