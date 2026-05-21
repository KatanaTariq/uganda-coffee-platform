import sys
import os
import streamlit as st
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from data.farm_listings import FARM_LISTINGS
from models.investment import get_current_price, calculate_projected_revenue

UG_BLACK = "#1a1a1a"
UG_YELLOW = "#FCDC04"
UG_RED = "#D90000"

st.set_page_config(page_title="Investment Marketplace", layout="wide")

st.markdown(f"""
<style>
.farm-card{{
    background:var(--color-background-primary);
    border:0.5px solid var(--color-border-tertiary);
    border-radius:12px;
    padding:16px 18px;
    margin-bottom:12px;
}}
.farm-name{{font-size:15px;font-weight:500;color:var(--color-text-primary);margin:0 0 2px}}
.farm-sub{{font-size:12px;color:var(--color-text-secondary);margin:0}}
.lbl{{font-size:11px;color:var(--color-text-tertiary);margin:0 0 2px}}
.val{{font-size:14px;font-weight:500;color:var(--color-text-primary);margin:0}}
.val-sm{{font-size:11px;color:var(--color-text-secondary);margin:2px 0 0}}
.badge{{display:inline-block;font-size:10px;padding:2px 8px;border-radius:4px;font-weight:500}}
.prog-wrap{{height:6px;background:var(--color-background-secondary);border-radius:3px;overflow:hidden;margin-top:4px}}
</style>
""", unsafe_allow_html=True)

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
    <p style="color:{UG_YELLOW};font-weight:600;font-size:20px;margin:0">Investment Marketplace</p>
    <p style="color:#888780;font-size:12px;margin:4px 0 0">Browse Ugandan coffee farm investment opportunities · Simulation only · Not a real investment product</p>
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

st.sidebar.markdown("**Filter listings**")
type_filter = st.sidebar.selectbox(
    "Coffee type", ["All", "Arabica", "Robusta"]
)
risk_filter = st.sidebar.selectbox(
    "Risk level", ["All", "Low", "Moderate"]
)
st.sidebar.divider()
st.sidebar.markdown(f"""
<div style="background:rgba(252,220,4,0.1);border:0.5px solid {UG_YELLOW};
    border-radius:8px;padding:10px 12px">
    <p style="font-size:12px;font-weight:500;color:var(--color-text-primary);margin:0 0 4px">
    How it works</p>
    <p style="font-size:11px;color:var(--color-text-secondary);margin:0;line-height:1.6">
    Browse farm listings, click a farm to view the full analysis, then use
    the return calculator to model your projected returns across three
    price scenarios.</p>
</div>
""", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.caption("Built by Katana Imran · Aston University · 2026")

# Load price data
@st.cache_data
def load_prices():
    base = os.path.join(os.path.dirname(__file__), "..", "..")
    return pd.read_csv(
        os.path.join(base, "data", "processed", "master_dataset.csv"),
        parse_dates=["date"]
    )

df = load_prices()
arabica_price = get_current_price(df, "arabica")
robusta_price = get_current_price(df, "robusta")

# Summary metrics
total = len(FARM_LISTINGS)
total_rev = sum(
    calculate_projected_revenue(
        f["yield_tonnes"],
        arabica_price if f["coffee_type"] == "arabica" else robusta_price
    )
    for f in FARM_LISTINGS
)
low_risk = sum(1 for f in FARM_LISTINGS if f["risk_level"] == "Low")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Active listings", total)
m2.metric("Total projected revenue", f"${total_rev/1e6:.1f}M")
m3.metric("Low risk listings", f"{low_risk} of {total}")
m4.metric("Live Arabica price", f"${arabica_price:.2f}/kg")

st.caption("Projected revenues are calculated using live price data from the platform and update automatically.")
st.divider()

# Filter farms
farms = FARM_LISTINGS
if type_filter != "All":
    farms = [f for f in farms if f["coffee_type"] == type_filter.lower()]
if risk_filter != "All":
    farms = [f for f in farms if f["risk_level"] == risk_filter]

st.subheader(f"Available opportunities ({len(farms)} listings)")

for farm in farms:
    price = arabica_price if farm["coffee_type"] == "arabica" else robusta_price
    proj_rev = calculate_projected_revenue(farm["yield_tonnes"], price)

    risk_col = "#1D9E75" if farm["risk_level"] == "Low" else UG_YELLOW
    risk_bg = "rgba(29,158,117,0.12)" if farm["risk_level"] == "Low" \
              else "rgba(252,220,4,0.12)"
    risk_txt = "#27500A" if farm["risk_level"] == "Low" else "#633806"

    drought_warn = ""
    if farm["drought_flag"]:
        drought_warn = (f'<span class="badge" style="background:rgba(217,0,0,0.1);'
                        f'color:#D90000;margin-left:6px">Drought signal</span>')

    funded_col = "#1D9E75" if farm["funded_pct"] > 70 else \
                 (UG_YELLOW if farm["funded_pct"] > 30 else "#888780")

    st.markdown(f"""
    <div class="farm-card">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:12px">
        <div style="display:flex;align-items:center;gap:10px">
          <div style="width:38px;height:38px;border-radius:50%;background:{UG_BLACK};
              display:flex;align-items:center;justify-content:center;flex-shrink:0">
            <i class="ti ti-plant" style="font-size:17px;color:{UG_YELLOW}"></i>
          </div>
          <div>
            <p class="farm-name">{farm["name"]} {drought_warn}</p>
            <p class="farm-sub">{farm["region"]} · {farm["coffee_type"].capitalize()} · Harvest {farm["harvest_date"]}</p>
          </div>
        </div>
        <span class="badge" style="background:{risk_bg};color:{risk_txt}">
            {farm["risk_level"]} risk · {farm["risk_score"]}/100
        </span>
      </div>
      <div style="display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin-bottom:12px">
        <div><p class="lbl">Yield</p><p class="val">{farm["yield_tonnes"]} t</p></div>
        <div><p class="lbl">Proj. revenue</p><p class="val">${proj_rev/1e3:.0f}K</p><p class="val-sm">at ${price:.2f}/kg live</p></div>
        <div><p class="lbl">Stake available</p><p class="val">{farm["stake_available_pct"]}%</p></div>
        <div><p class="lbl">Min. investment</p><p class="val">${farm["min_investment"]:,}</p></div>
        <div><p class="lbl">Crop health</p><p class="val">{farm["crop_health"]}/100</p></div>
      </div>
      <div style="margin-bottom:12px">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px">
          <span style="font-size:11px;color:var(--color-text-tertiary)">Funding progress</span>
          <span style="font-size:11px;font-weight:500;color:{funded_col}">{farm["funded_pct"]}% funded</span>
        </div>
        <div class="prog-wrap">
          <div style="width:{farm["funded_pct"]}%;height:100%;background:{funded_col};border-radius:3px"></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"View opportunity — {farm['name']}", key=farm["id"]):
        st.session_state["selected_farm"] = farm["id"]
        st.switch_page("pages/09_opportunity.py")