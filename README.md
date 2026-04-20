
# FX Exposure & Hedging Analytics Dashboard

> A production-ready Power BI dashboard for treasury teams to monitor FX exposure, hedge effectiveness, and risk (VaR) across 5 currency pairs — built with free tools only.

![Page 1 Overview](screenshots/page1_overview.png)

---

## What This Demonstrates

| Skill | Implementation |
|---|---|
| **DAX** | 25+ measures: Net Exposure, Hedge Ratio, VaR, Scenario switching, KPI formatting |
| **Power Query / SQL** | M-code GROUP BY, JOINs, calculated columns, date dimension |
| **Python (Pandas/NumPy)** | Monte Carlo VaR simulation (1,000 paths × 3 scenarios) |
| **Python Visuals (Power BI)** | Matplotlib P&L histogram, implied vol chart, maturity profile |
| **Data Modelling** | Star schema: Exposure fact + Date/Currency/Scenario dimensions |
| **FX Domain Knowledge** | Forwards, implied vols, delta/gamma sensitivity, hedge ratios, VaR concepts |

---

## Dashboard Pages

### Page 1 — Overview
![Overview](screenshots/page1_overview.png)
- **4 KPI Cards**: Net Exposure, Hedge Ratio, VaR 95%, Limit Breach Count
- **Treemap / Bar**: Net exposure by currency (absolute values)
- **Gauge**: Coverage % vs 80% benchmark target
- **VaR by Scenario**: Base / Stress / Shock+10% comparison
- **Maturity Profile**: Exposure bucketed by 0–30d, 30–90d, 90–180d, 180–365d

### Page 2 — Drill-Through: Subsidiary & Counterparty
![Drill-Through](screenshots/page2_drillthrough.png)
- **Heatmap Matrix**: Net exposure per Subsidiary × Currency pair
- **Waterfall Chart**: Long positions → Short positions → Hedges → Net
- **Counterparty Breach Bars**: Utilization vs $100M limit; all 3 banks flagged as breach

### Page 3 — Risk: VaR & Volatility
![Risk](screenshots/page3_risk.png)
- **MC P&L Histogram**: 1,000 simulations; tail highlighted in red below VaR 95%
- **Implied Vol Chart**: 1M vs 3M vol by currency pair
- **Scenario Comparison**: VaR 95%/99% across Base / Stress / Shock

---


## Quick Start (15 minutes)

### Step 1 — Generate Data
```bash
pip install pandas numpy
python setup.py
# Creates all CSVs in /data
```

### Step 2 — Open Power BI Desktop
1. **Get Data → Text/CSV** → import all 4 files from `/data`
2. Apply the theme: **View → Browse for themes** → select `fx_treasury_theme.json`

### Step 3 — Power Query Setup
In Power Query Editor, for each table apply the relevant M code from `power_query_M_code.m`:
- `fx_exposures`: Add `IsHedgeable`, `Exposure_Base`, `Exposure_Stress`, `Exposure_Shock10`
- `ecb_forwards`: Add `Fwd_Spread_1M`, `Fwd_Spread_3M`
- `Aggregated`: Group by Currency/Subsidiary/Counterparty → add `Hedge_Ratio`
- `Date`: Full date dimension table (Year/Month/Quarter)

Also manually create a `Scenario` table:
```
Scenario
--------
Base
Stress
Shock+10%
```

### Step 4 — Relationships (Star Schema)
```
fx_exposures[Trade_Date]  →  Date[Date]
fx_exposures[Currency]    →  ecb_forwards[Currency]
var_results[Scenario]     →  Scenario[Scenario]
```

### Step 5 — DAX Measures
Open `dax_measures.dax` → paste each measure into **Home → New Measure**. Key measures:

```dax
Net Exposure = SUM(fx_exposures[Exposure])

Hedge Ratio = DIVIDE(SUM(fx_exposures[Hedgeable]), ABS([Net Exposure]), 0)

Scenario Multiplier =
    SWITCH(SELECTEDVALUE(Scenario[Scenario], "Base"),
        "Base", 1.0, "Stress", 1.5, "Shock+10%", 1.1, 1.0)

Scenario Net Exposure = [Net Exposure] * [Scenario Multiplier]

Scenario VaR 95 =
    SWITCH(SELECTEDVALUE(Scenario[Scenario], "Base"),
        "Base",      CALCULATE(MIN(var_results[VaR_95]), var_results[Scenario]="Base"),
        "Stress",    CALCULATE(MIN(var_results[VaR_95]), var_results[Scenario]="Stress"),
        "Shock+10%", CALCULATE(MIN(var_results[VaR_95]), var_results[Scenario]="Shock+10%"),
        CALCULATE(MIN(var_results[VaR_95]), var_results[Scenario]="Base"))

BankC Limit Utilization = DIVIDE(ABS([BankC Exposure]), 100000000, 0)
```

### Step 6 — Build Visuals

**Page 1 — Overview**
| Visual | Fields |
|---|---|
| Card × 4 | Net Exposure, Hedge Ratio %, Scenario VaR 95, Limit Breach Count |
| Bar Chart | Currency on Y-axis, Net Exposure Abs on X |
| Gauge | Hedge Ratio (Value), 0.8 (Target) |
| Bar Chart | Scenario (Axis), VaR 95 + VaR 99 (Values) |
| Python Visual | Maturity Profile (drag Maturity_Days, Exposure, Currency) |

**Page 2 — Drill-Through**
| Visual | Fields |
|---|---|
| Matrix | Rows: Subsidiary; Columns: Currency; Values: Net Exposure |
| Waterfall | Category: [Long, Short, Hedges, Net]; Values: measure |
| Bar Chart | Counterparty, exposure vs limit line |

**Page 3 — Risk**
| Visual | Fields |
|---|---|
| Python Visual | MC VaR histogram (drag Exposure) |
| Clustered Bar | Currency, Implied_Vol_1M, Implied_Vol_3M |
| Clustered Bar | Scenario, VaR_95, VaR_99 |

**Slicers (all pages):**
- Currency (multi-select)
- Subsidiary (hierarchy)
- Scenario (single: Base/Stress/Shock+10%)

### Step 7 — Python Visuals
1. Enable: **File → Options → Python scripting** → set your Python path
2. Insert Python Visual → drag required fields → paste code from `python_visuals_powerbi.py`
3. The MC histogram auto-updates when Currency/Subsidiary slicers change

### Step 8 — Polish
- Add **Bookmarks**: Base Scenario, Stress Scenario, BankC Filter
- Set **drill-through**: right-click subsidiary in Page 1 → drill to Page 2
- Export: **File → Export → PDF** for snapshot; or publish to Power BI Service (free)

---

## Key Metrics Explained

**Hedge Ratio** = Hedgeable Exposure / |Net Exposure| — target ≥ 80%

**VaR 95%** = 5th percentile of simulated P&L distribution (Monte Carlo, 1,000 paths, 1-day horizon) — stressed by multiplying vols by 1.5× for Stress scenario

**Counterparty Limit Breach** = |Total Exposure to Counterparty| > $100M limit

**Net Exposure** = Σ Long positions + Σ Short positions (signed sum)

---

## Skills Demonstrated

> Built for FX treasury risk management roles (e.g. Keridion Capital, hedge funds, bank treasury desks)

- **Power BI**: DAX, Power Query M, Python visuals, star schema, bookmarks, drill-through
- **Financial domain**: FX forwards, implied vol, delta sensitivity, hedge ratios, VaR methodology
- **Python**: Monte Carlo simulation (NumPy), Pandas data manipulation, Matplotlib visualisation
- **SQL concepts**: GROUP BY, JOIN, calculated columns in Power Query
- **Risk metrics**: VaR 95/99%, scenario analysis, counterparty limit monitoring

---
