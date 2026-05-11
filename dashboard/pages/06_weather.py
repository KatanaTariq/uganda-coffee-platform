import sys
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

sys.path.append("../../src")

st.set_page_config(page_title="Weather & Crop Health", layout="wide")
st.title("Weather & Crop Health")
st.caption("ERA5 satellite climate data for Uganda's coffee growing regions")

@st.cache_data
def load():
    df = pd.read_csv("../data/processed/master_dataset.csv", parse_dates=["date"])
    return df.dropna(subset=["rainfall_mm"])

df = load()

# Current signals
latest = df.iloc[-1]
drought = int(latest["drought_flag"])
health = float(latest["health_score"])

if drought == 1 and health < 30:
    risk_score, risk_label = 2, "Elevated"
    risk_color = "inverse"
elif drought == 1 or health < 30:
    risk_score, risk_label = 1, "Moderate"
    risk_color = "off"
else:
    risk_score, risk_label = 0, "Low"
    risk_color = "normal"

m1, m2, m3, m4 = st.columns(4)
m1.metric("Supply risk", risk_label)
m2.metric("Crop health score", f"{health:.1f}/100")
m3.metric("Drought flag", "Active" if drought else "Clear")
m4.metric("Avg temp (Uganda)", f"{latest['temp_celsius']:.1f} C")

st.divider()

# Dual axis chart — rainfall vs coffee price
st.subheader("Rainfall vs Arabica price")
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Bar(
    x=df["date"], y=df["rainfall_mm"],
    name="Rainfall (mm/month)",
    marker_color="rgba(53,130,220,0.5)"
), secondary_y=False)

fig.add_trace(go.Scatter(
    x=df["date"], y=df["arabica_usd"],
    name="Arabica price (USD/kg)",
    line=dict(color="#8B4513", width=2)
), secondary_y=True)

# Shade drought periods
for _, row in df[df["drought_flag"] == 1].iterrows():
    fig.add_vrect(
        x0=row["date"], x1=row["date"] + pd.DateOffset(months=1),
        fillcolor="rgba(226,75,74,0.15)", line_width=0
    )

fig.update_layout(template="plotly_white", hovermode="x unified")
fig.update_yaxes(title_text="Rainfall (mm)", secondary_y=False)
fig.update_yaxes(title_text="Price (USD/kg)", secondary_y=True)
st.plotly_chart(fig, use_container_width=True)
st.caption("Red shaded areas = drought months (rainfall below 10th percentile)")

st.divider()

# Crop health score over time
st.subheader("Soil moisture & crop health score")
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df["date"], y=df["health_score"],
    name="Crop health score",
    line=dict(color="#1D9E75", width=2),
    fill="tozeroy",
    fillcolor="rgba(29,158,117,0.1)"
))
fig2.add_hline(y=30, line_dash="dot", line_color="#E24B4A",
               annotation_text="Stress threshold (30)")
fig2.update_layout(
    template="plotly_white",
    yaxis_title="Health score (0-100)",
    hovermode="x unified"
)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Temperature trend
st.subheader("Average temperature trend (Uganda)")
fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=df["date"], y=df["temp_celsius"],
    name="Temperature (C)",
    line=dict(color="#D2691E", width=1.5)
))
fig3.add_trace(go.Scatter(
    x=df["date"],
    y=df["temp_celsius"].rolling(12).mean(),
    name="12M average",
    line=dict(color="#8B4513", width=2, dash="dot")
))
fig3.update_layout(
    template="plotly_white",
    yaxis_title="Temperature (C)",
    hovermode="x unified"
)
st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.subheader("What these signals mean for coffee prices")
st.info(
    "Rainfall 6 to 9 months before harvest is the strongest natural predictor of coffee supply. "
    "A drought event today suggests reduced crop yields in 6 to 9 months, "
    "which typically pushes prices upward as supply tightens. "
    "The crop health score combines soil moisture data from ERA5 satellite measurements "
    "averaged across Uganda's main coffee growing regions."
)