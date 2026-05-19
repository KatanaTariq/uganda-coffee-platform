import sys
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

UG_BLACK = "#1a1a1a"
UG_YELLOW = "#FCDC04"
UG_RED = "#D90000"

st.set_page_config(page_title="Weather & Crop Health", layout="wide")

st.markdown(f"""
<style>
.explain-yellow {{
    border-left: 3px solid {UG_YELLOW};
    background: var(--secondary-background-color);
    padding: 12px 14px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 6px;
}}
.explain-red {{
    border-left: 3px solid {UG_RED};
    background: var(--secondary-background-color);
    padding: 12px 14px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 6px;
}}
.explain-black {{
    border-left: 3px solid #888780;
    background: var(--secondary-background-color);
    padding: 12px 14px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 6px;
}}
.explain-green {{
    border-left: 3px solid #1D9E75;
    background: var(--secondary-background-color);
    padding: 12px 14px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 6px;
}}
.explain-title {{
    font-size: 13px;
    font-weight: 600;
    margin: 0 0 4px 0;
    color: var(--text-color);
}}
.explain-body {{
    font-size: 13px;
    margin: 0;
    line-height: 1.6;
    color: var(--text-color);
    opacity: 0.85;
}}
.metric-card {{
    background: var(--secondary-background-color);
    border-radius: 8px;
    padding: 12px;
}}
.metric-label {{
    font-size: 11px;
    color: var(--text-color);
    opacity: 0.6;
    margin: 0 0 3px;
}}
.metric-value {{
    font-size: 22px;
    font-weight: 600;
    margin: 2px 0;
    color: var(--text-color);
}}
.metric-sub {{
    font-size: 11px;
    color: var(--text-color);
    opacity: 0.6;
    margin: 0;
}}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="background:{UG_BLACK};padding:18px 24px;border-radius:12px;margin-bottom:16px">
    <div style="height:4px;display:flex;margin-bottom:12px;border-radius:2px;overflow:hidden">
        <div style="flex:1;background:{UG_BLACK}"></div>
        <div style="flex:1;background:{UG_YELLOW}"></div>
        <div style="flex:1;background:{UG_RED}"></div>
        <div style="flex:1;background:{UG_BLACK}"></div>
        <div style="flex:1;background:{UG_YELLOW}"></div>
        <div style="flex:1;background:{UG_RED}"></div>
    </div>
    <p style="color:{UG_YELLOW};font-weight:600;font-size:20px;margin:0">Weather & Crop Health</p>
    <p style="color:#888780;font-size:12px;margin:4px 0 0">ERA5 satellite climate data for Uganda's coffee growing regions · Copernicus / ECMWF</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown(f"""
<div style="background:{UG_BLACK};padding:14px 16px;border-radius:8px;margin-bottom:16px">
    <div style="height:4px;display:flex;margin-bottom:10px;border-radius:2px;overflow:hidden">
        <div style="flex:1;background:{UG_BLACK}"></div>
        <div style="flex:1;background:{UG_YELLOW}"></div>
        <div style="flex:1;background:{UG_RED}"></div>
        <div style="flex:1;background:{UG_BLACK}"></div>
        <div style="flex:1;background:{UG_YELLOW}"></div>
        <div style="flex:1;background:{UG_RED}"></div>
    </div>
    <p style="color:{UG_YELLOW};font-weight:600;font-size:14px;margin:0">Uganda Coffee Platform</p>
    <p style="color:#888780;font-size:11px;margin:3px 0 0">Commodity risk analytics</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("**Weather & Crop Health**")
st.sidebar.caption("ERA5 satellite climate data from the European Centre for Medium-Range Weather Forecasts covering Uganda's coffee growing regions from 2005 to 2026.")
st.sidebar.divider()
st.sidebar.markdown("**Data sources**")
st.sidebar.caption("Copernicus ERA5 — rainfall, temperature, soil moisture")
st.sidebar.caption("Bank of Uganda — UGX/USD rates")
st.sidebar.divider()
st.sidebar.caption("Built by Katana Imran · Aston University · 2026")


@st.cache_data
def load():
    df = pd.read_csv("../data/processed/master_dataset.csv", parse_dates=["date"])
    return df.dropna(subset=["rainfall_mm"])


df = load()
latest = df.iloc[-1]
drought = int(latest["drought_flag"])
health = float(latest["health_score"])

if drought == 1 and health < 30:
    risk_label, risk_colour = "Elevated", UG_RED
elif drought == 1 or health < 30:
    risk_label, risk_colour = "Moderate", UG_YELLOW
else:
    risk_label, risk_colour = "Low", "#1D9E75"

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="metric-card" style="border-top:3px solid {risk_colour}">'
                f'<p class="metric-label">Supply risk</p>'
                f'<p class="metric-value" style="color:{risk_colour}">{risk_label}</p>'
                f'<p class="metric-sub">Combined weather signal</p></div>',
                unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card" style="border-top:3px solid #1D9E75">'
                f'<p class="metric-label">Crop health score</p>'
                f'<p class="metric-value">{health:.1f}/100</p>'
                f'<p class="metric-sub">From NASA satellite imagery</p></div>',
                unsafe_allow_html=True)
with m3:
    drought_col = UG_RED if drought else "#888780"
    st.markdown(f'<div class="metric-card" style="border-top:3px solid {drought_col}">'
                f'<p class="metric-label">Drought flag</p>'
                f'<p class="metric-value">{"Active" if drought else "Clear"}</p>'
                f'<p class="metric-sub">Rainfall vs historical 10th percentile</p></div>',
                unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="metric-card" style="border-top:3px solid {UG_YELLOW}">'
                f'<p class="metric-label">Avg temperature</p>'
                f'<p class="metric-value">{latest["temp_celsius"]:.1f}°C</p>'
                f'<p class="metric-sub">Uganda-wide monthly average</p></div>',
                unsafe_allow_html=True)

st.markdown("")
st.divider()

# Rainfall vs price
st.subheader("Rainfall vs Arabica price")
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(
    x=df["date"], y=df["rainfall_mm"],
    name="Rainfall (mm/month)",
    marker_color="rgba(53,130,220,0.4)"
), secondary_y=False)
fig.add_trace(go.Scatter(
    x=df["date"], y=df["arabica_usd"],
    name="Arabica price (USD/kg)",
    line=dict(color=UG_RED, width=2)
), secondary_y=True)
for _, row in df[df["drought_flag"] == 1].iterrows():
    fig.add_vrect(
        x0=row["date"],
        x1=row["date"] + pd.DateOffset(months=1),
        fillcolor="rgba(217,0,0,0.12)", line_width=0
    )
fig.update_layout(template="plotly_white", hovermode="x unified")
fig.update_yaxes(title_text="Rainfall (mm/month)", secondary_y=False)
fig.update_yaxes(title_text="Arabica price (USD/kg)", secondary_y=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown("""<div class="explain-yellow">
<p class="explain-title">What you are looking at</p>
<p class="explain-body">The blue bars show monthly rainfall across Uganda's coffee growing regions. The red line shows the Arabica price. Red shaded areas are drought months. Coffee plants need rain at the right time — too little during flowering (March to April) and the harvest 9 months later will be smaller, pushing prices upward. Look for red shaded months followed by price rises 6 to 9 months later.</p>
</div>""", unsafe_allow_html=True)

st.divider()

# Crop health
st.subheader("Crop health score")
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df["date"], y=df["health_score"],
    name="Crop health score",
    line=dict(color="#1D9E75", width=2),
    fill="tozeroy", fillcolor="rgba(29,158,117,0.1)"
))
fig2.add_hline(y=30, line_dash="dot", line_color=UG_RED,
               annotation_text="Stress threshold (30)",
               annotation_position="top left")
fig2.update_layout(
    template="plotly_white",
    yaxis_title="Health score (0 to 100)",
    hovermode="x unified"
)
st.plotly_chart(fig2, use_container_width=True)
st.markdown("""<div class="explain-green">
<p class="explain-title">What you are looking at</p>
<p class="explain-body">This number comes from satellite images of Uganda taken every 16 days by NASA. It measures how green and healthy the coffee plants look from space — 100 means thriving, below 30 means the plants are under serious stress and yields are likely to fall. When the score drops below the red dotted line it is a warning that the upcoming harvest may be smaller, which tends to push prices higher.</p>
</div>""", unsafe_allow_html=True)

st.divider()

# Temperature
st.subheader("Temperature trend")
fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=df["date"], y=df["temp_celsius"],
    name="Monthly temperature",
    line=dict(color=UG_YELLOW, width=1.5)
))
fig3.add_trace(go.Scatter(
    x=df["date"], y=df["temp_celsius"].rolling(12).mean(),
    name="12-month average",
    line=dict(color=UG_RED, width=2, dash="dot")
))
fig3.update_layout(
    template="plotly_white",
    yaxis_title="Temperature (°C)",
    hovermode="x unified"
)
st.plotly_chart(fig3, use_container_width=True)
st.markdown("""<div class="explain-black">
<p class="explain-title">What you are looking at</p>
<p class="explain-body">This shows the average temperature across Uganda's coffee growing regions. The yellow line is the monthly reading, the red dotted line is the 12-month trend. Coffee grows best between 18°C and 24°C — sustained temperatures above 30°C stress the plants and reduce yield quality. A gradual upward trend over decades signals long-term climate change affecting Uganda's growing conditions.</p>
</div>""", unsafe_allow_html=True)

st.divider()

st.subheader("How weather connects to coffee prices")
st.markdown("""<div class="explain-red">
<p class="explain-title">The 6 to 9 month lag — the most important concept on this page</p>
<p class="explain-body">Weather affects coffee prices with a delay. A drought or heat stress today damages the crop currently flowering or developing. That smaller harvest hits the market 6 to 9 months later, reducing supply and pushing prices upward. This means the weather data here is a leading indicator — it gives you a signal about where prices are likely to go before the price chart itself shows it. That is why combining weather data with price history makes the forecast significantly more accurate.</p>
</div>""", unsafe_allow_html=True)