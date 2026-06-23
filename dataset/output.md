# Dataset Notebook — Execution Output

## Data Loading
- **Source:** `dataset/processed/jkse_preprocessed.csv`
- **Rows:** 3930
- **Columns:** 14
- **Date range:** 2010-03-31 to 2026-06-19
- **Index type:** `datetime64[us]` — unique, sorted
- **Missing values:** 0 (all NaN rows dropped)

## Features (9 + 5 auxiliary)
| Feature | Description |
|---|---|
| `Log_Return` | Daily logarithmic return of IHSG close price |
| `Vol_20d` | 20-day rolling volatility (std of Log_Return) |
| `Vol_60d` | 60-day rolling volatility (std of Log_Return) |
| `EMA_5` | 5-day exponential moving average of close price |
| `BB_Middle` | Bollinger Band middle (20d SMA) |
| `BB_Upper` | Bollinger Band upper (middle + 2×20d std) |
| `BB_Lower` | Bollinger Band lower (middle − 2×20d std) |
| `Momentum_5d` | 5-day cumulative log return |
| `Momentum_20d` | 20-day cumulative log return |

## Feature Summary Statistics
| Feature | Mean | Std | Min | 25% | 50% | 75% | Max |
|---|---|---|---|---|---|---|---|
| Log_Return | 0.000201 | 0.010921 | −0.092997 | −0.004761 | 0.000787 | 0.005850 | 0.097042 |
| Vol_20d | 0.009599 | 0.005051 | 0.003133 | 0.006534 | 0.008272 | 0.010679 | 0.042301 |
| Vol_60d | 0.009857 | 0.004299 | 0.003955 | 0.006932 | 0.008532 | 0.011226 | 0.027811 |
| EMA_5 | 5615.94 | 1293.54 | 2625.64 | 4589.90 | 5773.50 | 6661.95 | 9071.28 |
| BB_Middle | 5615.91 | 1294.08 | 2627.49 | 4586.58 | 5763.98 | 6662.24 | 9077.38 |
| BB_Upper | 5709.86 | 1307.19 | 2777.32 | 4704.03 | 5850.92 | 6742.26 | 9453.33 |
| BB_Lower | 5521.97 | 1285.03 | 2450.22 | 4487.97 | 5647.31 | 6563.32 | 8963.43 |
| Momentum_5d | 0.001006 | 0.024432 | −0.176059 | −0.009310 | 0.002655 | 0.013967 | 0.157750 |
| Momentum_20d | 0.004101 | 0.047435 | −0.385058 | −0.015626 | 0.009183 | 0.031409 | 0.154075 |

## Correlation Highlights
- **High positive:** Vol_20d ↔ Vol_60d (0.77), EMA_5 ↔ BB_Middle (0.9999)
- **Moderate positive:** Log_Return ↔ Momentum_5d (0.43), Momentum_5d ↔ Momentum_20d (0.48)
- **Weak/Negative:** Volatility vs price-level features (−0.23 to −0.36), Log_Return vs Momentum_20d (0.21)
- **Memory usage:** 307.0 KB
