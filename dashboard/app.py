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

UG_BLACK = "#1a1a1a"
UG_YELLOW = "#FCDC04"
UG_RED = "#D90000"

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
.scenario-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    background: var(--secondary-background-color);
    border-radius: 8px;
    margin-bottom: 5px;
}}
.scenario-name {{
    font-size: 13px;
    flex: 1;
    color: var(--text-color);
}}
.scenario-value {{
    font-size: 13px;
    font-weight: 600;
    color: var(--text-color);
}}
</style>
""", unsafe_allow_html=True)


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

st.sidebar.markdown("**Filters**")
st.sidebar.caption("Adjust these to explore different views of the data")
st.sidebar.markdown("**Coffee type**")
st.sidebar.caption("Uganda exports both — Robusta is ~80% of total volume")
coffee_type = st.sidebar.selectbox("", ["Arabica", "Robusta"])
st.sidebar.markdown("**Year range**")
st.sidebar.caption("Drag to zoom into a specific period")
year_range = st.sidebar.slider("", min_value=1960, max_value=2026, value=(2000, 2026))
st.sidebar.divider()
st.sidebar.markdown("**Data sources**")
st.sidebar.caption("ICO / World Bank — coffee prices")
st.sidebar.caption("Bank of Uganda — UGX/USD rates")
st.sidebar.caption("Copernicus ERA5 — satellite climate")
st.sidebar.divider()
st.sidebar.caption("Built by Katana Imran · Aston University · 2026")

col = "arabica" if coffee_type == "Arabica" else "robusta"
df_filtered = df[
    (df["date"].dt.year >= year_range[0]) &
    (df["date"].dt.year <= year_range[1])
]

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
    <p style="color:{UG_YELLOW};font-weight:600;font-size:20px;margin:0">Uganda Coffee Price & Risk Platform</p>
    <p style="color:#888780;font-size:12px;margin:4px 0 0">Real-time commodity analytics · ICO prices · Bank of Uganda FX · ERA5 satellite climate data</p>
</div>
""", unsafe_allow_html=True)

# Risk metrics
risk = risk_summary(df, col)
df_fx_chart = df.dropna(subset=["ugx_per_usd"])
current_fx = int(df_fx_chart["ugx_per_usd"].iloc[-1])

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card" style="border-top:3px solid {UG_YELLOW}">'
                f'<p class="metric-label">Current price</p>'
                f'<p class="metric-value">${risk["current_price_usd"]}</p>'
                f'<p class="metric-sub">What coffee sells for today (USD/kg)</p></div>',
                unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card" style="border-top:3px solid #888780">'
                f'<p class="metric-label">Monthly price swing</p>'
                f'<p class="metric-value">{risk["current_volatility_pct"]}%</p>'
                f'<p class="metric-sub">How unpredictable prices are right now</p></div>',
                unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card" style="border-top:3px solid {UG_RED}">'
                f'<p class="metric-label">Worst monthly drop</p>'
                f'<p class="metric-value">{risk["var_95_pct"]}%</p>'
                f'<p class="metric-sub">5% chance of losing this in a month</p></div>',
                unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card" style="border-top:3px solid #1D9E75">'
                f'<p class="metric-label">Biggest historical crash</p>'
                f'<p class="metric-value">{risk["max_drawdown_pct"]}%</p>'
                f'<p class="metric-sub">Largest ever peak-to-trough fall</p></div>',
                unsafe_allow_html=True)

st.markdown("")
st.divider()

# Price history
st.subheader("Price history")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_filtered["date"], y=df_filtered[f"{col}_usd"],
    name=coffee_type, line=dict(color=UG_RED, width=2)
))
fig.add_trace(go.Scatter(
    x=df_filtered["date"], y=df_filtered[f"{col}_ma3"],
    name="3M moving average", line=dict(color=UG_YELLOW, dash="dot", width=1.5)
))
fig.update_layout(template="plotly_white", hovermode="x unified",
                  yaxis_title="Price (USD/kg)")
st.plotly_chart(fig, use_container_width=True)
st.markdown("""<div class="explain-yellow">
<p class="explain-title">What you are looking at</p>
<p class="explain-body">This shows the price of coffee per kilogram in US dollars over time. The red line is the actual price — the yellow dotted line smooths out short-term noise to reveal the bigger trend. Prices spike when harvests fail and fall when global supply is high. Higher prices mean more income for Ugandan farmers and exporters.</p>
</div>""", unsafe_allow_html=True)

st.divider()

# Volatility
st.subheader("Price volatility")
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df_filtered["date"], y=df_filtered[f"{col}_volatility"],
    name="12M rolling volatility",
    line=dict(color=UG_RED, width=2),
    fill="tozeroy", fillcolor="rgba(217,0,0,0.08)"
))
fig2.add_hline(y=10, line_dash="dot", line_color=UG_YELLOW,
               annotation_text="Caution zone", annotation_position="top left")
fig2.update_layout(template="plotly_white", yaxis_title="Volatility (%)",
                   hovermode="x unified")
st.plotly_chart(fig2, use_container_width=True)
st.markdown("""<div class="explain-red">
<p class="explain-title">What you are looking at</p>
<p class="explain-body">Volatility measures how wildly prices are jumping around — think of it as a risk speedometer. When the line rises above the yellow caution line, prices are swinging so unpredictably that it becomes very difficult for farmers to plan their income or for exporters to sign contracts with confidence.</p>
</div>""", unsafe_allow_html=True)

st.divider()

# FX History
st.subheader("UGX/USD exchange rate history")
fig_fx = go.Figure()
fig_fx.add_trace(go.Scatter(
    x=df_fx_chart["date"], y=df_fx_chart["ugx_per_usd"],
    name="UGX per USD",
    line=dict(color="#534AB7", width=2),
    fill="tozeroy", fillcolor="rgba(83,74,183,0.08)"
))
fig_fx.update_layout(template="plotly_white", yaxis_title="UGX per 1 USD",
                     hovermode="x unified")
st.plotly_chart(fig_fx, use_container_width=True)

fx1, fx2, fx3 = st.columns(3)
fx1.metric("Current rate", f"{current_fx:,} UGX")
rate_1yr = df_fx_chart[df_fx_chart["date"] == "2025-04-01"]["ugx_per_usd"]
fx2.metric("Rate 1 year ago",
           f"{int(rate_1yr.values[0]):,} UGX" if len(rate_1yr) > 0 else "N/A")
rate_2020 = df_fx_chart[df_fx_chart["date"] == "2020-01-01"]["ugx_per_usd"]
if len(rate_2020) > 0:
    change = ((current_fx / rate_2020.values[0]) - 1) * 100
    fx3.metric("UGX change vs 2020", f"{change:.1f}%")

st.markdown("""<div class="explain-black">
<p class="explain-title">What you are looking at</p>
<p class="explain-body">This shows how many Ugandan shillings you get for one US dollar over time. Coffee is priced in dollars globally but Ugandan exporters spend in shillings. When this line rises — more shillings per dollar — exporters earn more in local currency even if the dollar price stays flat. The shilling has weakened significantly since 2005, which has actually benefited exporters in UGX terms.</p>
</div>""", unsafe_allow_html=True)

st.divider()

# Revenue simulator
st.subheader("Revenue simulator")
st.caption("Drag the sliders below to model different export scenarios and see how revenue changes in real time.")

s1, s2, s3 = st.columns(3)
price = s1.slider("Coffee price (USD/kg)", 1.0, 10.0,
                  float(round(risk["current_price_usd"], 2)), 0.05)
volume = s2.slider("Export volume (tonnes)", 100, 5000, 1000, 50)
fx = s3.slider("UGX per USD (exchange rate)", 2500, 5000, current_fx, 10)

rev = simulate_revenue(price, volume, fx)
r1, r2, r3 = st.columns(3)
r1.metric("Revenue (USD)", f"${rev['revenue_usd']:,.0f}")
r2.metric("Revenue (UGX)", f"{rev['revenue_ugx']:,.0f}")
r3.metric("Per tonne (UGX)", f"{rev['revenue_per_tonne_ugx']:,.0f}")

st.markdown("""<div class="explain-yellow">
<p class="explain-title">How to use this</p>
<p class="explain-body">Revenue = price × volume × exchange rate. Try lowering the exchange rate slider — even if the coffee price stays the same in dollars, you earn fewer shillings. This is called currency risk. Now try lowering both the price and the exchange rate together to see how quickly revenue collapses when two risks hit at once.</p>
</div>""", unsafe_allow_html=True)

st.divider()

# Scenario analysis
st.subheader("Scenario analysis")
st.caption("Each scenario answers a 'what if' question using your slider values above as the starting point.")

scenarios = run_scenarios(price, volume, fx)
for name, data in scenarios.items():
    pct = data["pct_change"]
    colour = "#1D9E75" if pct == 0 else (UG_RED if pct < -15 else UG_YELLOW)
    badge_bg = "rgba(29,158,117,0.15)" if pct == 0 else \
               ("rgba(217,0,0,0.15)" if pct < -15 else "rgba(252,220,4,0.15)")
    badge_col = "#1D9E75" if pct == 0 else (UG_RED if pct < -15 else "#854F0B")
    border = f"border:1px solid {UG_RED};" if name == "Combined stress" else ""
    st.markdown(
        f'<div class="scenario-row" style="{border}">'
        f'<span style="width:10px;height:10px;border-radius:2px;'
        f'background:{colour};flex-shrink:0"></span>'
        f'<span class="scenario-name">{name}</span>'
        f'<span class="scenario-value">{data["revenue_ugx"]/1e9:.2f}B UGX</span>'
        f'<span style="font-size:11px;padding:2px 8px;border-radius:4px;'
        f'background:{badge_bg};color:{badge_col};font-weight:500">{pct}%</span>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("""<div class="explain-red">
<p class="explain-title">What you are looking at</p>
<p class="explain-body">Each row shows what total export revenue would look like if one bad thing happened. The "Combined stress" row is the most important — it shows what happens when a price drop, currency weakening, and volume fall all arrive at the same time. In real commodity markets, bad events tend to cluster together. A 27% revenue drop in a single season is often the difference between a profitable and a loss-making year.</p>
</div>""", unsafe_allow_html=True)

st.divider()

# Price forecast
st.subheader("Price forecast")
st.caption("A machine learning model trained on historical price patterns predicts where prices may go over the next 12 months.")

with st.spinner("Training forecast model - please wait..."):
    forecast, metrics = train_and_forecast(df, col, periods=12)

m1, m2, m3 = st.columns(3)
m1.metric("Average error (MAE)", f"${metrics['mae']}/kg")
m2.metric("Error (RMSE)", f"${metrics['rmse']}/kg")
m3.metric("Error as % of price (MAPE)", f"{metrics['mape']}%")

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=df_filtered["date"], y=df_filtered[f"{col}_usd"],
    name="Historical price", line=dict(color=UG_RED, width=2)
))
fig4.add_trace(go.Scatter(
    x=forecast["ds"], y=forecast["yhat"],
    name="Forecast", line=dict(color="#1D9E75", width=2, dash="dot")
))
fig4.add_trace(go.Scatter(
    x=list(forecast["ds"]) + list(forecast["ds"][::-1]),
    y=list(forecast["yhat_upper"]) + list(forecast["yhat_lower"][::-1]),
    fill="toself", fillcolor="rgba(29,158,117,0.1)",
    line=dict(color="rgba(255,255,255,0)"),
    name="95% confidence range"
))
fig4.update_layout(
    template="plotly_white", yaxis_title="Price (USD/kg)",
    hovermode="x unified",
    xaxis=dict(range=["2015-01-01", "2027-06-01"])
)
st.plotly_chart(fig4, use_container_width=True)
st.markdown("""<div class="explain-black">
<p class="explain-title">What you are looking at</p>
<p class="explain-body">The green dotted line is what the model predicts prices will do over the next 12 months. The shaded green band is the confidence range — the model is saying the price will likely land somewhere in this band. A wide band means high uncertainty, which is honest. The model learns from 65 years of price history but cannot predict unexpected events like a drought or a frost in Brazil.</p>
</div>""", unsafe_allow_html=True)