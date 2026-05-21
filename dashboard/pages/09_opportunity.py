import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from data.farm_listings import FARM_LISTINGS, get_farm_by_id
from models.investment import (
    get_current_price,
    calculate_projected_revenue,
    calculate_returns
)
from models.forecast import train_and_forecast
from models.risk import risk_summary

UG_BLACK = "#1a1a1a"
UG_YELLOW = "#FCDC04"
UG_RED = "#D90000"

st.set_page_config(page_title="Opportunity Detail", layout="wide")

st.markdown(f"""
<style>
.card{{background:var(--color-background-primary);border:0.5px solid
    var(--color-border-tertiary);border-radius:12px;padding:14px 16px;margin-bottom:12px}}
.lbl{{font-size:11px;color:var(--color-text-tertiary);margin:0 0 2px}}
.val{{font-size:14px;font-weight:500;color:var(--color-text-primary);margin:0}}
.val-sm{{font-size:11px;color:var(--color-text-secondary);margin:2px 0 0}}
.badge{{display:inline-block;font-size:10px;padding:2px 8px;border-radius:4px;font-weight:500}}
.metric-card{{background:var(--color-background-secondary);border-radius:8px;padding:10px 12px}}
.explain{{border-left:3px solid {UG_YELLOW};background:var(--color-background-secondary);
    padding:10px 13px;border-radius:0 6px 6px 0;margin-bottom:12px}}
.explain p{{font-size:12px;color:var(--color-text-secondary);margin:0;line-height:1.6}}
.explain-red{{border-left:3px solid {UG_RED};background:var(--color-background-secondary);
    padding:10px 13px;border-radius:0 6px 6px 0;margin-bottom:12px}}
.explain-red p{{font-size:12px;color:var(--color-text-secondary);margin:0;line-height:1.6}}
.return-box{{background:var(--color-background-secondary);border-radius:8px;
    padding:10px 12px;text-align:center}}
</style>
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

st.sidebar.markdown("**Select farm**")
farm_names = {f["id"]: f["name"] for f in FARM_LISTINGS}
default_id = st.session_state.get("selected_farm", FARM_LISTINGS[0]["id"])
default_idx = list(farm_names.keys()).index(default_id)
selected_id = st.sidebar.selectbox(
    "", list(farm_names.values()),
    index=default_idx
)
farm = get_farm_by_id(
    [k for k, v in farm_names.items() if v == selected_id][0]
)

st.sidebar.divider()
st.sidebar.caption("Projected revenues use live price data and update automatically.")
st.sidebar.caption("This is a simulation — not a real investment product.")
st.sidebar.divider()
st.sidebar.caption("Built by Katana Imran · Aston University · 2026")

# Load data
@st.cache_data
def load_data():
    base = os.path.join(os.path.dirname(__file__), "..", "..")
    return pd.read_csv(
        os.path.join(base, "data", "processed", "master_dataset.csv"),
        parse_dates=["date"]
    )

@st.cache_data
def load_forecast(coffee_type):
    base = os.path.join(os.path.dirname(__file__), "..", "..")
    df = pd.read_csv(
        os.path.join(base, "data", "processed", "master_dataset.csv"),
        parse_dates=["date"]
    )
    forecast, metrics = train_and_forecast(df, coffee_type, periods=12)
    return forecast, metrics

df = load_data()
col = farm["coffee_type"]
current_price = get_current_price(df, col)
proj_rev = calculate_projected_revenue(farm["yield_tonnes"], current_price)
risk = risk_summary(df, col)

risk_col = "#1D9E75" if farm["risk_level"] == "Low" else UG_YELLOW
risk_bg = "rgba(29,158,117,0.12)" if farm["risk_level"] == "Low" \
          else "rgba(252,220,4,0.12)"
risk_txt = "#27500A" if farm["risk_level"] == "Low" else "#633806"

# Header
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
    <p style="color:{UG_YELLOW};font-weight:600;font-size:20px;margin:0">{farm["name"]}</p>
    <p style="color:#888780;font-size:12px;margin:4px 0 0">
        {farm["region"]} · {farm["coffee_type"].capitalize()} ·
        Harvest {farm["harvest_date"]} · Payment {farm["payment_date"]}
    </p>
</div>
""", unsafe_allow_html=True)

# Farm overview
funded_col = "#1D9E75" if farm["funded_pct"] > 70 else \
             (UG_YELLOW if farm["funded_pct"] > 30 else "#888780")

st.markdown(f"""
<div class="card" style="border-left:4px solid {risk_col};border-radius:0 12px 12px 0">
  <div style="display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin-bottom:12px">
    <div class="metric-card">
      <p class="lbl">Projected revenue</p>
      <p class="val">${proj_rev/1e3:.0f}K</p>
      <p class="val-sm">at ${current_price:.2f}/kg live</p>
    </div>
    <div class="metric-card">
      <p class="lbl">Yield</p>
      <p class="val">{farm["yield_tonnes"]} tonnes</p>
      <p class="val-sm">{farm["coffee_type"].capitalize()} grade</p>
    </div>
    <div class="metric-card">
      <p class="lbl">Risk score</p>
      <p class="val" style="color:{risk_col}">{farm["risk_score"]}/100 {farm["risk_level"]}</p>
      <p class="val-sm">recommendation engine</p>
    </div>
    <div class="metric-card">
      <p class="lbl">Crop health</p>
      <p class="val">{farm["crop_health"]}/100</p>
      <p class="val-sm">ERA5 satellite signal</p>
    </div>
    <div class="metric-card">
      <p class="lbl">Stake available</p>
      <p class="val">{farm["stake_available_pct"]}%</p>
      <p class="val-sm">Min. ${farm["min_investment"]:,}</p>
    </div>
  </div>
  <div style="margin-bottom:10px">
    <div style="display:flex;justify-content:space-between;margin-bottom:4px">
      <span style="font-size:11px;color:var(--color-text-tertiary)">Funding progress</span>
      <span style="font-size:11px;font-weight:500;color:{funded_col}">{farm["funded_pct"]}% funded</span>
    </div>
    <div style="height:6px;background:var(--color-background-secondary);border-radius:3px;overflow:hidden">
      <div style="width:{farm["funded_pct"]}%;height:100%;background:{funded_col};border-radius:3px"></div>
    </div>
  </div>
  <p style="font-size:13px;color:var(--color-text-secondary);margin:0;line-height:1.65">{farm["description"]}</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Price forecast
st.subheader("Price forecast")
st.caption(f"12-month {farm['coffee_type'].capitalize()} price forecast — powered by the platform's live model")

with st.spinner("Loading forecast..."):
    forecast, metrics = load_forecast(col)

m1, m2, m3 = st.columns(3)
m1.metric("Current price", f"${current_price:.2f}/kg")
m2.metric("Forecast price (12M avg)",
          f"${forecast['yhat'].tail(12).mean():.2f}/kg")
m3.metric("Model error (MAPE)", f"{metrics['mape']}%")

fig = go.Figure()
df_recent = df[df["date"].dt.year >= 2018]
fig.add_trace(go.Scatter(
    x=df_recent["date"], y=df_recent[f"{col}_usd"],
    name="Historical price", line=dict(color=UG_RED, width=2)
))
fig.add_trace(go.Scatter(
    x=forecast["ds"], y=forecast["yhat"],
    name="Forecast", line=dict(color="#1D9E75", width=2, dash="dot")
))
fig.add_trace(go.Scatter(
    x=list(forecast["ds"]) + list(forecast["ds"][::-1]),
    y=list(forecast["yhat_upper"]) + list(forecast["yhat_lower"][::-1]),
    fill="toself", fillcolor="rgba(29,158,117,0.1)",
    line=dict(color="rgba(255,255,255,0)"),
    name="95% confidence range"
))
fig.update_layout(
    template="plotly_white", yaxis_title="Price (USD/kg)",
    hovermode="x unified",
    xaxis=dict(range=["2018-01-01", "2027-06-01"])
)
st.plotly_chart(fig, use_container_width=True)
st.markdown("""<div class="explain">
<p>This is the same forecast model that powers the main dashboard — trained on 65 years of price history. The green dotted line is the predicted price path. The shaded band is the 95% confidence range. A wide band means genuine uncertainty — coffee prices are notoriously hard to predict. The return calculator below uses three fixed price scenarios so you can model outcomes across the realistic range.</p>
</div>""", unsafe_allow_html=True)

st.divider()

# Volatility
st.subheader("Price volatility")
fig2 = go.Figure()
df_recent2 = df[df["date"].dt.year >= 2015].dropna(subset=[f"{col}_volatility"])
fig2.add_trace(go.Scatter(
    x=df_recent2["date"], y=df_recent2[f"{col}_volatility"],
    name="12M rolling volatility",
    line=dict(color=UG_RED, width=2),
    fill="tozeroy", fillcolor="rgba(217,0,0,0.07)"
))
fig2.add_hline(y=10, line_dash="dot", line_color=UG_YELLOW,
               annotation_text="Caution zone",
               annotation_position="top left")
fig2.update_layout(
    template="plotly_white",
    yaxis_title="Volatility (%)",
    hovermode="x unified"
)
st.plotly_chart(fig2, use_container_width=True)
st.markdown(f"""<div class="explain">
<p>Current volatility is {risk["current_volatility_pct"]}%. When volatility is high the gap between your optimistic and stressed returns widens significantly — the same investment amount produces a much wider range of possible outcomes. Monitor this before committing capital.</p>
</div>""", unsafe_allow_html=True)

st.divider()

# Weather signals
st.subheader("Crop and weather signals")
st.caption(f"ERA5 satellite data for the {farm['region']} region")

df_weather = df.dropna(subset=["rainfall_mm"])

w1, w2, w3, w4 = st.columns(4)
drought_col2 = UG_RED if farm["drought_flag"] else "#888780"
supply_col = UG_RED if (farm["drought_flag"] and farm["crop_health"] < 30) else \
             (UG_YELLOW if (farm["drought_flag"] or farm["crop_health"] < 30) else "#1D9E75")
supply_label = "Elevated" if (farm["drought_flag"] and farm["crop_health"] < 30) else \
               ("Moderate" if (farm["drought_flag"] or farm["crop_health"] < 30) else "Low")

with w1:
    st.markdown(f'<div class="metric-card" style="border-top:3px solid {supply_col}">'
                f'<p class="lbl">Supply risk</p>'
                f'<p class="val" style="color:{supply_col}">{supply_label}</p>'
                f'<p class="val-sm">Combined signal</p></div>',
                unsafe_allow_html=True)
with w2:
    st.markdown(f'<div class="metric-card" style="border-top:3px solid #1D9E75">'
                f'<p class="lbl">Crop health</p>'
                f'<p class="val">{farm["crop_health"]}/100</p>'
                f'<p class="val-sm">NASA satellite</p></div>',
                unsafe_allow_html=True)
with w3:
    st.markdown(f'<div class="metric-card" style="border-top:3px solid {drought_col2}">'
                f'<p class="lbl">Drought flag</p>'
                f'<p class="val">{"Active" if farm["drought_flag"] else "Clear"}</p>'
                f'<p class="val-sm">Rainfall signal</p></div>',
                unsafe_allow_html=True)
with w4:
    st.markdown(f'<div class="metric-card" style="border-top:3px solid {UG_YELLOW}">'
                f'<p class="lbl">Temperature</p>'
                f'<p class="val">{farm["temp_celsius"]}°C</p>'
                f'<p class="val-sm">Monthly average</p></div>',
                unsafe_allow_html=True)

st.markdown("")

fig3 = make_subplots(specs=[[{"secondary_y": True}]])
fig3.add_trace(go.Bar(
    x=df_weather["date"], y=df_weather["rainfall_mm"],
    name="Rainfall (mm/month)",
    marker_color="rgba(53,130,220,0.4)"
), secondary_y=False)
fig3.add_trace(go.Scatter(
    x=df_weather["date"], y=df_weather[f"{col}_usd"],
    name=f"{farm['coffee_type'].capitalize()} price",
    line=dict(color=UG_RED, width=2)
), secondary_y=True)
for _, row in df_weather[df_weather["drought_flag"] == 1].iterrows():
    fig3.add_vrect(
        x0=row["date"],
        x1=row["date"] + pd.DateOffset(months=1),
        fillcolor="rgba(217,0,0,0.1)", line_width=0
    )
fig3.update_layout(template="plotly_white", hovermode="x unified")
fig3.update_yaxes(title_text="Rainfall (mm/month)", secondary_y=False)
fig3.update_yaxes(title_text="Price (USD/kg)", secondary_y=True)
st.plotly_chart(fig3, use_container_width=True)

if farm["drought_flag"]:
    st.markdown("""<div class="explain-red">
    <p>A drought signal is currently active in this region. This may affect the harvest yield in 6 to 9 months. The stressed return scenario accounts for a potential supply reduction. Monitor crop health scores closely before committing capital.</p>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown("""<div class="explain">
    <p>No drought is currently active. Rainfall levels are within the normal historical range for this region. This is a positive signal for harvest yield stability — one less risk factor to price into your return expectations.</p>
    </div>""", unsafe_allow_html=True)

st.divider()

# Return calculator
st.subheader("Return calculator")
st.caption("Model your projected returns across three price scenarios.")

inv_amount = st.slider(
    "Investment amount (USD)",
    min_value=farm["min_investment"],
    max_value=50000,
    value=max(farm["min_investment"], 5000),
    step=250
)

returns = calculate_returns(inv_amount, proj_rev)

r1, r2, r3 = st.columns(3)
with r1:
    st.markdown(f"""<div class="return-box">
    <p class="lbl">Optimistic return</p>
    <p style="font-size:18px;font-weight:500;color:#1D9E75;margin:2px 0">${returns['optimistic']:,.0f}</p>
    <p style="font-size:11px;color:var(--color-text-tertiary);margin:0">Price +15% · ROI {returns['optimistic_roi']:+.1f}%</p>
    </div>""", unsafe_allow_html=True)
with r2:
    base_col = "#1D9E75" if returns["baseline_roi"] >= 0 else UG_RED
    st.markdown(f"""<div class="return-box" style="border:0.5px solid var(--color-border-secondary)">
    <p class="lbl">Baseline return</p>
    <p style="font-size:18px;font-weight:500;color:{base_col};margin:2px 0">${returns['baseline']:,.0f}</p>
    <p style="font-size:11px;color:var(--color-text-tertiary);margin:0">Forecast price · ROI {returns['baseline_roi']:+.1f}%</p>
    </div>""", unsafe_allow_html=True)
with r3:
    st.markdown(f"""<div class="return-box">
    <p class="lbl">Stressed return</p>
    <p style="font-size:18px;font-weight:500;color:{UG_RED};margin:2px 0">${returns['stressed']:,.0f}</p>
    <p style="font-size:11px;color:var(--color-text-tertiary);margin:0">Price -25% · ROI {returns['stressed_roi']:+.1f}%</p>
    </div>""", unsafe_allow_html=True)

st.markdown(f"""
<div style="background:rgba(252,220,4,0.08);border-left:3px solid {UG_YELLOW};
    border-radius:0 6px 6px 0;padding:10px 13px;margin-top:12px">
    <p style="font-size:12px;color:var(--color-text-secondary);margin:0;line-height:1.6">
    Your ${inv_amount:,} buys a {returns['stake_pct']:.3f}% stake in this farm's projected revenue of
    ${proj_rev:,.0f}. Returns are paid when the harvest sells in {farm["payment_date"]}.
    The baseline uses the current price forecast. Optimistic assumes prices hold at today's
    level. Stressed models a 25% price decline — a realistic scenario given current all-time highs.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

st.markdown(f"""
<div style="background:var(--color-background-secondary);border-radius:8px;padding:12px 14px">
    <p style="font-size:12px;font-weight:500;color:var(--color-text-primary);margin:0 0 4px">
    Simulation disclaimer</p>
    <p style="font-size:11px;color:var(--color-text-secondary);margin:0;line-height:1.6">
    This is a simulated investment platform built as a portfolio project. No real money
    is involved. Farm listings, yields, and funding progress are illustrative. Price data,
    forecasts, weather signals, and risk scores are real and powered by live platform data.
    This is not financial advice.
    </p>
</div>
""", unsafe_allow_html=True)