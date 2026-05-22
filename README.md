# Uganda Coffee Price & Risk Platform

A quantitative analytics and fintech simulation platform for Uganda's coffee export market — built as a portfolio project by a Computer Science undergraduate at Aston University.

**Live demo:** https://uganda-coffee-platform.streamlit.app

---

## What it does

Uganda exports over $500M of coffee annually. The farmers and exporters behind that market have almost no access to price analytics, risk tools, or investment infrastructure. This platform is a proof of concept for what that infrastructure could look like.

It combines five data sources into a single dashboard:

- **Price analytics** — 65 years of Arabica and Robusta price history from the ICO and World Bank, with volatility modelling, rolling averages, and drawdown analysis
- **FX risk analysis** — real UGX/USD exchange rate data from the Bank of Uganda, showing how currency movements affect exporter revenue in shillings
- **Price forecasting** — a Prophet time-series model trained on historical price patterns, producing 12-month forecasts with 95% confidence intervals and MAE/RMSE/MAPE evaluation metrics
- **Weather and crop health** — ERA5 satellite climate data from the European Centre for Medium-Range Weather Forecasts, including monthly rainfall, temperature, soil moisture, drought detection, and a crop health score derived from NASA satellite imagery
- **Market recommendation engine** — a signal-based scoring system that synthesises price trend, volatility, FX movement, drought signals, and crop health into three actionable recommendations: pricing, FX conversion, and export volume
- **Investment marketplace** — a simulated fractional crop revenue investment platform where users can browse Ugandan coffee farm listings, view full due diligence analytics, and model projected returns across optimistic, baseline, and stressed price scenarios

---

## Platform pages

| Page | Description |
|---|---|
| Main dashboard | Price history, volatility, FX rates, revenue simulator, scenario analysis, price forecast |
| Weather & crop health | ERA5 rainfall, temperature, soil moisture, drought flags, crop health score |
| Recommendations | Signal-based market scoring with three action recommendations |
| Investment marketplace | Browse six simulated farm listings with live projected revenues |
| Opportunity detail | Full analytical suite per farm — forecast, volatility, weather signals, return calculator |

---

## Tech stack

| Layer | Tools |
|---|---|
| Data processing | Python, Pandas, NumPy |
| Forecasting | Prophet (Meta), Scikit-learn |
| Risk modelling | Custom scoring engine — volatility, VaR, drawdown, signal weighting |
| Climate data | XArray, NetCDF4, Copernicus CDS API |
| Visualisation | Plotly |
| Dashboard | Streamlit |
| Version control | Git, GitHub |

---

## Data sources

| Source | Data |
|---|---|
| ICO / World Bank Pink Sheet | Monthly Arabica and Robusta prices (1960–2026) |
| Bank of Uganda | Daily UGX/USD exchange rates (2005–2026) |
| Copernicus ERA5 | Monthly rainfall, temperature, soil moisture — Uganda bounding box |
| NASA MODIS | Crop health index (NDVI-derived) |

---

## Project structure
uganda-coffee-platform/
├── data/
│   ├── raw/                    # Source data files
│   └── processed/              # Cleaned and merged datasets
├── src/
│   ├── processing/             # Data loading and feature engineering
│   │   ├── clean.py
│   │   ├── features.py
│   │   └── weather_features.py
│   ├── models/                 # Quantitative model modules
│   │   ├── forecast.py         # Prophet time-series forecasting
│   │   ├── risk.py             # Volatility, VaR, drawdown
│   │   ├── simulator.py        # Revenue and scenario simulation
│   │   ├── recommendation.py   # Signal-based scoring engine
│   │   └── investment.py       # Return calculator for marketplace
│   └── data/
│       └── farm_listings.py    # Simulated farm investment data
├── dashboard/
│   ├── app.py                  # Main dashboard
│   └── pages/
│       ├── 06_weather.py       # Weather and crop health
│       ├── 07_recommendations.py
│       ├── 08_marketplace.py   # Investment marketplace
│       └── 09_opportunity.py   # Farm opportunity detail
├── notebooks/
│   └── 01_eda.ipynb            # Exploratory analysis
└── requirements.txt
---

## Financial concepts covered

- **Spot price and basis risk** — global benchmark vs local farmgate price
- **FX exposure** — how UGX/USD movements affect shilling-denominated revenue
- **Volatility** — 12-month rolling standard deviation of monthly returns
- **Value at Risk (VaR)** — historical simulation at 95% confidence
- **Maximum drawdown** — largest peak-to-trough price decline
- **Time-series forecasting** — Prophet model with seasonality and trend decomposition
- **Scenario stress testing** — named and combined adverse scenarios
- **Leading indicators** — lagged rainfall and crop health as supply-side price signals
- **Fractional revenue participation** — simulated crop investment with return modelling

---

## Why Uganda's coffee market

Uganda is Africa's largest coffee exporter and the crop supports approximately 1.7 million smallholder farming households. Despite the market's scale, the people closest to it — farmers, cooperatives, small exporters — have almost no access to the kind of price analytics and risk tools that commodity traders in London and New York use daily. This project is an attempt to build that infrastructure and understand what it would take to make it real.

---

## Built by

**Katana Imran** — BSc Computer Science, Aston University (predicted First Class)

- GitHub: [github.com/KatanaTariq](https://github.com/KatanaTariq)
- LinkedIn: [linkedin.com/in/katana-tariq](https://linkedin.com/in/katana-tariq)
- Email: katanaimran79@gmail.com

*Built as a portfolio project exploring quantitative development, commodity risk analytics, and fintech product design. Not a real investment product.*