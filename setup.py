#!/usr/bin/env python3
"""
FX Exposure & Hedging Analytics Dashboard
Setup Script — Run this ONCE before opening Power BI

Usage: python setup.py
Output: All required CSV files in /data folder
"""

import pandas as pd
import numpy as np
import os

os.makedirs('data', exist_ok=True)
np.random.seed(42)

print("=" * 60)
print("  FX Exposure & Hedging Analytics — Data Generator")
print("=" * 60)

# ── 1. SYNTHETIC TRADE EXPOSURES ──────────────────────────────
print("\n[1/4] Generating fx_exposures.csv...")
n_trades = 1000
currencies = ['EURUSD', 'GBPUSD', 'JPYUSD', 'AUDUSD', 'CADUSD']
subsidiaries = ['Europe', 'Asia', 'Americas', 'UK']
counterparties = ['BankA', 'BankB', 'BankC']

directions = np.random.choice(['Long', 'Short'], n_trades)
notionals = np.random.uniform(1e6, 50e6, n_trades)
maturities = np.random.randint(1, 365, n_trades)

data = {
    'TradeID':      range(1, n_trades+1),
    'Currency':     np.random.choice(currencies, n_trades),
    'Subsidiary':   np.random.choice(subsidiaries, n_trades),
    'Counterparty': np.random.choice(counterparties, n_trades),
    'Notional':     notionals.round(2),
    'Direction':    directions,
    'Maturity_Days':maturities,
    'Type':         np.random.choice(['Spot','Forward','Swap'], n_trades, p=[0.4,0.4,0.2]),
    'Trade_Date':   pd.date_range('2024-01-01', periods=n_trades, freq='8h')[:n_trades].strftime('%Y-%m-%d'),
}
df = pd.DataFrame(data)
df['Exposure']   = df.apply(lambda r: r['Notional'] if r['Direction']=='Long' else -r['Notional'], axis=1)
df['Hedgeable']  = df.apply(lambda r: r['Exposure']*0.8 if r['Maturity_Days']<90 else 0, axis=1)
df['Hedge_Limit']= 100_000_000
df.to_csv('data/fx_exposures.csv', index=False)
print(f"   -> {len(df)} trades written to data/fx_exposures.csv")

# ── 2. ECB-STYLE FORWARDS & IMPLIED VOLS ──────────────────────
print("\n[2/4] Generating ecb_forwards.csv...")
dates = pd.date_range('2024-01-01','2024-12-31', freq='ME')
base_rates = {'EURUSD':1.085,'GBPUSD':1.265,'JPYUSD':0.0067,'AUDUSD':0.655,'CADUSD':0.740}
rows = []
for ccy, base in base_rates.items():
    for i, date in enumerate(dates):
        spot = base + np.random.normal(0, 0.005)*i
        rows.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Currency': ccy,
            'Spot_Rate': round(spot, 5),
            'Forward_1M': round(spot*(1+np.random.uniform(-0.003,0.003)), 5),
            'Forward_3M': round(spot*(1+np.random.uniform(-0.006,0.006)), 5),
            'Forward_6M': round(spot*(1+np.random.uniform(-0.010,0.010)), 5),
            'Implied_Vol_1M': round(np.random.uniform(0.06,0.18), 4),
            'Implied_Vol_3M': round(np.random.uniform(0.07,0.20), 4),
        })
fwd_df = pd.DataFrame(rows)
fwd_df.to_csv('data/ecb_forwards.csv', index=False)
print(f"   -> {len(fwd_df)} rows written to data/ecb_forwards.csv")

# ── 3. MONTE CARLO VAR RESULTS ────────────────────────────────
print("\n[3/4] Running Monte Carlo VaR (1000 sims × 3 scenarios)...")
exposure_vals = df['Exposure'].values
vols = {'EURUSD':0.09,'GBPUSD':0.10,'JPYUSD':0.11,'AUDUSD':0.12,'CADUSD':0.08}
df['Vol'] = df['Currency'].map(vols).fillna(0.10)
vol_arr = df['Vol'].values

var_rows = []
for scenario, shock in [('Base',1.0),('Stress',1.5),('Shock+10%',1.1)]:
    shocks = np.random.normal(0, vol_arr*shock, (1000, len(df)))
    pnl = np.sum(exposure_vals * shocks, axis=1)
    var_rows.append({
        'Scenario': scenario,
        'VaR_95': round(np.percentile(pnl, 5), 2),
        'VaR_99': round(np.percentile(pnl, 1), 2),
        'Expected_Loss': round(np.mean(pnl), 2),
        'Worst_Loss': round(np.min(pnl), 2),
    })
pd.DataFrame(var_rows).to_csv('data/var_results.csv', index=False)

# Save MC paths for Python visual
shocks_b = np.random.normal(0, vol_arr, (1000, len(df)))
pnl_b = np.sum(exposure_vals * shocks_b, axis=1)
pd.DataFrame({'Sim': range(1000), 'PnL': pnl_b.round(2)}).to_csv('data/mc_paths.csv', index=False)
print("   -> var_results.csv and mc_paths.csv written")

# ── 4. COUNTERPARTY SUMMARY ───────────────────────────────────
print("\n[4/4] Generating counterparty_limits.csv...")
cp = df.groupby('Counterparty').agg(Total_Exposure=('Exposure','sum')).reset_index()
cp['Limit']  = 100_000_000
cp['Breach'] = cp['Total_Exposure'].abs() > cp['Limit']
cp.to_csv('data/counterparty_limits.csv', index=False)
print(f"   -> {len(cp)} counterparties written")

# ── SUMMARY ───────────────────────────────────────────────────
print("\n" + "="*60)
print("  All data files generated in /data:")
for f in os.listdir('data'):
    size = os.path.getsize(f'data/{f}')
    print(f"    {f:<35} {size:>8,} bytes")
print("="*60)
print("\n  Next step: Open Power BI Desktop and import from /data/")
print("  See README.md for full setup instructions.\n")
