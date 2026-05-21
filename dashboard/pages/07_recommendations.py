import sys
import streamlit as st
import pandas as pd

import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from models.recommendation import compute_signals, generate_recommendations

UG_BLACK = "#1a1a1a"
UG_YELLOW = "#FCDC04"
UG_RED = "#D90000"

st.set_page_config(page_title="Recommendations", layout="wide")

st.markdown(f"""
<style>
.rec-card {{
    border-radius: 10px;
    border: 0.5px solid rgba(128,128,128,0.2);
    padding: 16px 18px;
    margin-bottom: 12px;
    background: var(--secondary-background-color);
}}
.rec-label {{
    font-size: 11px;
    color: var(--text-color);
    opacity: 0.6;
    margin: 0 0 3px;
}}
.rec-action {{
    font-size: 16px;
    font-weight: 600;
    margin: 0 0 10px;
    color: var(--text-color);
}}
.rec-reason {{
    font-size: 13px;
    color: var(--text-color);
    opacity: 0.85;
    line-height: 1.65;
    margin: 0;
    border-top: 0.5px solid rgba(128,128,128,0.2);
    padding-top: 10px;
}}
.signal-name {{
    font-size: 12px;
    color: var(--text-color);
    opacity: 0.7;
    width: 180px;
    flex-shrink: 0;
}}
.disclaimer {{
    font-size: 11px;
    color: var(--text-color);
    opacity: 0.6;
    background: var(--secondary-background-color);
    border-radius: 8px;
    padding: 10px 13px;
    line-height: 1.6;
    margin-top: 14px;
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
    <p style="color:{UG_YELLOW};font-weight:600;font-size:20px;margin:0">Market Recommendation Engine</p>
    <p style="color:#888780;font-size:12px;margin:4px 0 0">Signal-based scoring across price, FX, weather and volatility · computed from latest data</p>
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

st.sidebar.markdown("**Coffee type**")
coffee_type = st.sidebar.selectbox("", ["Arabica", "Robusta"])
st.sidebar.divider()
st.sidebar.caption("Recommendations update automatically when you switch coffee type.")
st.sidebar.caption("All signals are computed from the latest row in the master dataset.")
st.sidebar.divider()
st.sidebar.caption("Built by Katana Imran · Aston University · 2026")


@st.cache_data
def load():
    base = os.path.join(os.path.dirname(__file__), "..", "..")
    return pd.read_csv(
        os.path.join(base, "data", "processed", "master_dataset.csv"),
        parse_dates=["date"]
    )

df = load()
col = "arabica" if coffee_type == "Arabica" else "robusta"
signals = compute_signals(df, col)
recs = generate_recommendations(signals)

score = recs["overall_score"]
label = recs["overall_label"]
colour = recs["overall_colour"]

# Overall score
st.markdown(f"""
<div style="display:flex;align-items:center;gap:20px;
    background:var(--secondary-background-color);
    border-radius:10px;padding:16px 20px;margin-bottom:20px;
    border-left:4px solid {colour}">
    <div>
        <p style="font-size:11px;color:var(--text-color);opacity:0.6;margin:0">Overall market score</p>
        <p style="font-size:40px;font-weight:600;color:{colour};margin:0;line-height:1">
            {score}<span style="font-size:18px;color:var(--text-color);opacity:0.5">/100</span>
        </p>
    </div>
    <div style="flex:1">
        <p style="font-size:18px;font-weight:600;color:var(--text-color);margin:0">{label}</p>
        <p style="font-size:13px;color:var(--text-color);opacity:0.75;margin:4px 0 0">
            Based on {coffee_type} price trend, volatility, UGX/USD rate,
            drought signal and crop health score. Updated with latest available data.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# Signal breakdown
st.subheader("Signal breakdown")
st.caption("Each signal is scored 0 to 100 and weighted to produce the overall score above.")

signals_display = [
    ("Price vs 12M average",
     f"{signals['price_vs_avg_pct']:+.1f}%",
     signals["price_score"],
     "Bullish" if signals["price_score"] > 65 else
     ("Moderate" if signals["price_score"] > 40 else "Bearish"),
     "#1D9E75" if signals["price_score"] > 65 else
     (UG_YELLOW if signals["price_score"] > 40 else UG_RED)),
    ("Volatility level",
     f"{signals['current_volatility']}%",
     signals["vol_score"],
     "Low risk" if signals["vol_score"] > 65 else
     ("Moderate" if signals["vol_score"] > 40 else "High risk"),
     "#1D9E75" if signals["vol_score"] > 65 else
     (UG_YELLOW if signals["vol_score"] > 40 else UG_RED)),
    ("UGX/USD trend (3M)",
     f"{signals['fx_trend_pct']:+.1f}%",
     signals["fx_score"],
     "Weak shilling" if signals["fx_trend_pct"] > 0 else "Strong shilling",
     "#1D9E75" if signals["fx_score"] > 65 else
     (UG_YELLOW if signals["fx_score"] > 40 else UG_RED)),
    ("Drought flag",
     "Active" if signals["drought_flag"] else "Clear",
     signals["drought_score"],
     "Risk active" if signals["drought_flag"] else "No risk",
     UG_RED if signals["drought_flag"] else "#1D9E75"),
    ("Crop health score",
     f"{signals['health_score']}/100",
     signals["health_score_val"],
     "Healthy" if signals["health_score_val"] > 65 else
     ("Moderate" if signals["health_score_val"] > 40 else "Stressed"),
     "#1D9E75" if signals["health_score_val"] > 65 else
     (UG_YELLOW if signals["health_score_val"] > 40 else UG_RED)),
]

for name, val, score_val, tag, bar_col in signals_display:
    badge_bg = "rgba(29,158,117,0.15)" if bar_col == "#1D9E75" else \
               ("rgba(252,220,4,0.15)" if bar_col == UG_YELLOW else "rgba(217,0,0,0.15)")
    badge_col = "#1D9E75" if bar_col == "#1D9E75" else \
                (UG_YELLOW if bar_col == UG_YELLOW else UG_RED)
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;padding:9px 0;'
        f'border-bottom:0.5px solid rgba(128,128,128,0.15)">'
        f'<span class="signal-name">{name}</span>'
        f'<div style="flex:1;height:6px;background:rgba(128,128,128,0.15);'
        f'border-radius:3px;overflow:hidden">'
        f'<div style="width:{score_val}%;height:100%;background:{bar_col};'
        f'border-radius:3px"></div></div>'
        f'<span style="font-size:12px;font-weight:500;color:var(--text-color);'
        f'width:52px;text-align:right">{val}</span>'
        f'<span style="font-size:10px;padding:2px 8px;border-radius:4px;'
        f'background:{badge_bg};color:{badge_col};font-weight:500;white-space:nowrap">'
        f'{tag}</span></div>',
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)
st.divider()

# Three action cards
st.subheader("Action recommendations")
st.caption("Three decisions every coffee exporter faces — answered by the data.")


def conf_dots(n, dot_colour):
    dots = ""
    for i in range(5):
        c = dot_colour if i < n else "rgba(128,128,128,0.25)"
        dots += (f'<div style="width:9px;height:9px;border-radius:50%;'
                 f'background:{c}"></div>')
    label = ["", "Very low", "Low", "Medium", "High", "Very high"][n]
    return (f'<div style="display:flex;gap:4px;align-items:center">{dots}'
            f'<span style="font-size:11px;color:var(--text-color);opacity:0.5;'
            f'margin-left:4px">{label} confidence</span></div>')


cards = [
    ("Pricing decision", "ti-currency-dollar",
     "rgba(252,220,4,0.15)", "#854F0B", UG_YELLOW, recs["pricing"]),
    ("FX decision", "ti-arrows-exchange",
     "rgba(217,0,0,0.15)", UG_RED, UG_RED, recs["fx"]),
    ("Volume decision", "ti-truck",
     "rgba(29,158,117,0.15)", "#1D9E75", "#1D9E75", recs["volume"]),
]

for card_label, icon, icon_bg, icon_col, conf_col, rec in cards:
    st.markdown(f"""
    <div class="rec-card">
      <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:10px">
        <div style="width:34px;height:34px;border-radius:8px;background:{icon_bg};
            display:flex;align-items:center;justify-content:center;flex-shrink:0">
          <i class="ti {icon}" style="font-size:18px;color:{icon_col}"></i>
        </div>
        <div style="flex:1">
          <p class="rec-label">{card_label}</p>
          <p class="rec-action">{rec['action']}</p>
          {conf_dots(rec['confidence'], conf_col)}
        </div>
      </div>
      <p class="rec-reason">{rec['reason']}</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.markdown(f"""
<div style="background:rgba(252,220,4,0.08);border:0.5px solid {UG_YELLOW};
    border-radius:10px;padding:14px 16px">
    <p style="font-size:13px;font-weight:500;color:var(--color-text-primary);margin:0 0 4px">
    Ready to put capital to work in this market?</p>
    <p style="font-size:12px;color:var(--color-text-secondary);margin:0 0 10px;line-height:1.6">
    The Investment Marketplace lets you browse Ugandan coffee farm opportunities
    and model your projected returns across optimistic, baseline, and stressed scenarios
    — powered by the same live data and forecasts you just reviewed.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer">
    This is a quantitative signal, not financial advice. Recommendations are
    generated from historical data patterns and weighted scoring rules. They
    should be used as one input among many. Market conditions can change
    rapidly due to geopolitical events, global weather shocks, or policy
    changes that no model can predict in advance.
</div>
""", unsafe_allow_html=True)