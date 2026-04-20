
# =============================================
# PYTHON VISUALS FOR POWER BI
# Each block = one Python Visual on its own page
# In Power BI: Insert > Python visual, paste code below
# Dataset fields dragged in shown in comments
# =============================================

# ============================================================
# VISUAL 1: Monte Carlo VaR Paths  (Page 3 - Risk)
# Drag in: dataset field "Exposure" from fx_exposures table
# ============================================================

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)

# dataset comes from Power BI — use Exposure column
exposure_vals = dataset['Exposure'].values

# Volatilities (simplified flat 10%)
vols = np.full(len(exposure_vals), 0.10)

n_sims = 1000
shocks = np.random.normal(0, vols, (n_sims, len(exposure_vals)))
pnl = np.sum(exposure_vals * shocks, axis=1)

var_95 = np.percentile(pnl, 5)
var_99 = np.percentile(pnl, 1)

fig, ax = plt.subplots(figsize=(10, 5), facecolor='#0d1b2a')
ax.set_facecolor('#0d1b2a')

# Plot paths (sample 200 for performance)
sorted_pnl = np.sort(pnl)
colors = ['#ff4b4b' if v < var_95 else '#1a9e6e' for v in pnl[:200]]
ax.scatter(range(200), pnl[:200], c=colors, s=4, alpha=0.6)
ax.axhline(var_95, color='#ff8c00', linewidth=1.5, linestyle='--', label=f'VaR 95%: ${var_95/1e6:.1f}M')
ax.axhline(var_99, color='#ff2d55', linewidth=1.5, linestyle='--', label=f'VaR 99%: ${var_99/1e6:.1f}M')
ax.axhline(0, color='#ffffff', linewidth=0.5, alpha=0.3)

ax.set_title('Monte Carlo P&L Distribution (1000 Simulations)', color='white', fontsize=13, pad=15)
ax.set_xlabel('Simulation', color='#aaaaaa')
ax.set_ylabel('P&L (USD)', color='#aaaaaa')
ax.tick_params(colors='#aaaaaa')
for spine in ax.spines.values():
    spine.set_edgecolor('#333333')
ax.legend(facecolor='#1a2a3a', labelcolor='white', fontsize=9)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x/1e6:.0f}M'))

plt.tight_layout()
plt.show()


# ============================================================
# VISUAL 2: Exposure Waterfall BuildUp  (Page 2)
# Drag into this Python visual: Exposure, Hedgeable, Direction from fx_exposures
# ============================================================
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# dataset comes from Power BI
# Drag into this Python visual: Exposure, Hedgeable, Direction from fx_exposures

long_total  =  dataset.loc[dataset['Direction'] == 'Long',  'Exposure'].sum()
short_total =  dataset.loc[dataset['Direction'] == 'Short', 'Exposure'].sum()
hedges      = -dataset['Hedgeable'].sum()
net         =  long_total + short_total + hedges

labels = ['Long\nPositions', 'Short\nPositions', 'Hedges\nApplied', 'Net\nExposure']
values = [long_total, short_total, hedges, net]
colors = ['#1a9e6e', '#ff4b4b', '#ff8c00', '#3a7bd5']

# Running base for waterfall bars (last bar starts from 0)
bases  = [0, long_total, long_total + short_total, 0]

fig, ax = plt.subplots(figsize=(7, 5), facecolor='#0d1b2a')
ax.set_facecolor('#0d1b2a')

for i, (lbl, val, base, col) in enumerate(zip(labels, values, bases, colors)):
    ax.bar(i, val, bottom=base, color=col, alpha=0.88, width=0.55)
    label_y = base + val / 2
    ax.text(i, label_y, f'${val/1e6:.0f}M',
            ha='center', va='center', color='white', fontsize=9, fontweight='bold')

# Connector lines between bars
running = 0
for i in range(len(values) - 1):
    running += values[i]
    ax.plot([i + 0.28, i + 0.72], [running, running],
            color='#8ab4d4', linewidth=1, linestyle='--', alpha=0.6)

ax.axhline(0, color='white', linewidth=0.8, alpha=0.3)
ax.set_xticks(range(4))
ax.set_xticklabels(labels, color='white', fontsize=10)
ax.tick_params(axis='y', colors='#8ab4d4')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'${y/1e6:.0f}M'))
ax.set_title('Exposure Waterfall Build-Up', color='white', fontsize=13, pad=12)

for spine in ax.spines.values():
    spine.set_edgecolor('#1e3a5f')

plt.tight_layout()
plt.show()


# ============================================================
# VISUAL 3: Exposure Maturity Profile (Page 1)
# Drag in: Maturity_Days, Exposure, Currency from fx_exposures
# ============================================================
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Fields to drag into this Python visual from fx_exposures table:
# Maturity_Days, Exposure, Currency

df = dataset.copy()

# Safety check
if df.empty or 'Currency' not in df.columns:
    fig, ax = plt.subplots(facecolor='#0d1b2a')
    ax.text(0.5, 0.5, 'No data available', color='white', ha='center', transform=ax.transAxes)
    plt.show()
else:
    bins   = [0, 30, 90, 180, 365]
    labels = ['0-30d', '30-90d', '90-180d', '180-365d']
    df['Bucket'] = pd.cut(df['Maturity_Days'], bins=bins, labels=labels)

    bucketed = df.groupby(['Bucket', 'Currency'], observed=True)['Exposure'].sum().unstack(fill_value=0)

    ccy_colors = {
        'AUDUSD': '#3a7bd5',
        'CADUSD': '#1a9e6e',
        'EURUSD': '#ff8c00',
        'GBPUSD': '#ff4b4b',
        'JPYUSD': '#9b59b6'
    }

    currencies = [c for c in ccy_colors if c in bucketed.columns]

    # Safety check — need at least one currency
    if len(currencies) == 0:
        currencies = list(bucketed.columns)

    bucketed = bucketed[currencies]

    x = np.arange(len(bucketed))
    n_ccy = max(len(currencies), 1)  # prevent division by zero
    w = 0.75 / n_ccy

    fig, ax = plt.subplots(figsize=(10, 4), facecolor='#0d1b2a')
    ax.set_facecolor('#0d1b2a')

    for j, ccy in enumerate(currencies):
        offset = (j - n_ccy / 2 + 0.5) * w
        color = ccy_colors.get(ccy, '#3a7bd5')
        ax.bar(x + offset, bucketed[ccy].values / 1e6, w,
               label=ccy, color=color, alpha=0.85)

    ax.axhline(0, color='white', linewidth=0.8, alpha=0.3)
    ax.set_xticks(x)
    ax.set_xticklabels(bucketed.index.tolist(), color='white', fontsize=11)
    ax.tick_params(axis='y', colors='#8ab4d4')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'${y:.0f}M'))
    ax.set_title('Exposure by Maturity Bucket & Currency', color='white', fontsize=13, pad=12)
    ax.legend(facecolor='#1a2a3a', labelcolor='white', fontsize=9,
              ncol=5, loc='upper right', framealpha=0.8)

    for spine in ax.spines.values():
        spine.set_edgecolor('#1e3a5f')

    plt.tight_layout()
    plt.show()

# ============================================================
# VISUAL 4: VaR by Scenario (Page 3)
# Drag these fields into the Python visual: Scenario, VaR_95, VaR_99 from var_results table
# ============================================================

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# dataset comes from Power BI
# Drag these fields into the Python visual: Scenario, VaR_95, VaR_99 from var_results table

scenarios = dataset['Scenario'].tolist()
v95 = dataset['VaR_95'].abs().tolist()
v99 = dataset['VaR_99'].abs().tolist()

x = np.arange(len(scenarios))
width = 0.38

fig, ax = plt.subplots(figsize=(7, 5), facecolor='#0d1b2a')
ax.set_facecolor('#0d1b2a')

bars1 = ax.bar(x - width/2, v95, width, label='VaR 95%', color='#ff8c00', alpha=0.88)
bars2 = ax.bar(x + width/2, v99, width, label='VaR 99%', color='#ff4b4b', alpha=0.88)

# Value labels on top of each bar
for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
            f'${bar.get_height()/1e6:.0f}M', ha='center', va='bottom',
            color='white', fontsize=9, fontweight='bold')
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
            f'${bar.get_height()/1e6:.0f}M', ha='center', va='bottom',
            color='white', fontsize=9, fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels(scenarios, color='white', fontsize=11)
ax.tick_params(axis='y', colors='#8ab4d4')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'${y/1e6:.0f}M'))
ax.set_title('VaR by Scenario', color='white', fontsize=13, pad=12)
ax.legend(facecolor='#1a2a3a', labelcolor='white', fontsize=10)

for spine in ax.spines.values():
    spine.set_edgecolor('#1e3a5f')

plt.tight_layout()
plt.show()


# ============================================================
# VISUAL 5: Implied Volatility by Currency (Page 3)
# Drag these fields into the Python visual: Currency, Implied_Vol_1M, Implied_Vol_3M, Date
# ============================================================

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# dataset = ecb_forwards with Currency, Implied_Vol_1M, Implied_Vol_3M, Date
pivot = dataset.groupby('Currency')[['Implied_Vol_1M','Implied_Vol_3M']].mean()

fig, ax = plt.subplots(figsize=(8, 5), facecolor='#0d1b2a')
ax.set_facecolor('#0d1b2a')

x = np.arange(len(pivot.index))
width = 0.35
bars1 = ax.bar(x - width/2, pivot['Implied_Vol_1M'], width, label='1M Vol', color='#1a9e6e', alpha=0.85)
bars2 = ax.bar(x + width/2, pivot['Implied_Vol_3M'], width, label='3M Vol', color='#3a7bd5', alpha=0.85)

ax.set_title('Implied Volatility by Currency', color='white', fontsize=13, pad=12)
ax.set_xticks(x)
ax.set_xticklabels(pivot.index, color='white', fontsize=10)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
ax.tick_params(colors='#aaaaaa')
ax.set_facecolor('#0d1b2a')
for spine in ax.spines.values():
    spine.set_edgecolor('#333333')
ax.legend(facecolor='#1a2a3a', labelcolor='white')
for bar in bars1:
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.001, f'{bar.get_height():.1%}',
            ha='center', va='bottom', color='white', fontsize=8)

plt.tight_layout()
plt.show()
