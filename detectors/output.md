# Detectors Notebook — Execution Output

## Phase 2: Concept Drift Detectors — Step 1 Data Initialization & Scoreboard Creation

### Configuration
| Parameter | Value |
|---|---|
| Data path | `../dataset/processed/jkse_preprocessed.csv` |
| Features | Log_Return, Vol_20d, Vol_60d, EMA_5, BB_Middle, BB_Upper, BB_Lower, Momentum_5d, Momentum_20d |
| Batch algorithms | mysd, ks, psi, wasserstein |
| Batch windows | 60, 120 |
| Stream algorithms | adwin, kswin, ph |
| Stream warm-up | 60 rows |
| Consensus threshold | 1/3 (≈33.3%) |

### Scoreboards Created (11 total)
All 11 scoreboards are DataFrames with shape (3930, 9), one per feature column, initialized to NaN during warm-up and 0.0 thereafter.

| Key | Shape | NaN rows |
|---|---|---|
| `mysd_60` | (3930, 9) | 120 |
| `mysd_120` | (3930, 9) | 240 |
| `ks_60` | (3930, 9) | 120 |
| `ks_120` | (3930, 9) | 240 |
| `psi_60` | (3930, 9) | 120 |
| `psi_120` | (3930, 9) | 240 |
| `wasserstein_60` | (3930, 9) | 120 |
| `wasserstein_120` | (3930, 9) | 240 |
| `adwin` | (3930, 9) | 60 |
| `kswin` | (3930, 9) | 60 |
| `ph` | (3930, 9) | 60 |

### Persisted Files
Saved 11 CSV files to `../dataset/processed/scoreboard_{key}.csv` (174–179 KB each).

---

## Step 2-n (detector algorithm cells): Global Drift Signal Summary

### Global Drift Trigger Frequency (over 3810 active evaluation days)

| Paradigm | Variant | Drift Days | Status |
|---|---|---|---|
| Batch 60 | MYSD_60 | 1,476 | Eligible (local mean) |
| Batch 120 | MYSD_120 | 1,159 | Eligible (local mean) |
| Batch 60 | KS_60 | 3,802 | Defective/degenerate |
| Batch 120 | KS_120 | 3,690 | Defective/degenerate |
| Batch 60 | PSI_60 | 3,810 | Defective/degenerate |
| Batch 120 | PSI_120 | 3,690 | Defective/degenerate |
| Batch 60 | WASSERSTEIN_60 | 273 | Highly ideal (geometric) |
| Batch 120 | WASSERSTEIN_120 | 312 | Highly ideal (geometric) |
| Stream | ADWIN | 36 | Very conservative |
| Stream | KSWIN | 7 | Conservative |
| Stream | Page Hinkley | 1 | Extremely strict |

### Key Scientific Findings
1. **KS/PSI degeneration** — PSI triggered 100% of trading days; KS triggered 99.8%. Both fail to distinguish nominal price trends from structural shocks.
2. **Wasserstein geometric superiority** — Running Wasserstein with adaptive thresholding captures purely structural shifts (273 triggers on 60d window).
3. **Streaming robustness** — ADWIN (36), KSWIN (7), PH (1) are steadfast crisis indicators; incremental Z-score dampens daily noise.
4. **Window Dilemma evidence** — KS_60 and Wasserstein_60 both triggered first alarms at end of Sept 2010 (when 2W buffer expired), consistent with Gower-Winter et al. (2026).

### Phase 3 Gateway Filter
- **Eliminated:** PSI, KS-Test (false alarm degeneration)
- **Selected scenarios:**
  - Scenario A — WASSERSTEIN_60 (quarterly batch, 271 trimmed simulation-zone triggers; 273 full Phase 2 detector-window triggers)
  - Scenario B — WASSERSTEIN_120 (semester batch, 311 trimmed simulation-zone triggers; 312 full Phase 2 detector-window triggers)
  - Scenario C — ADWIN (pure stream, 36 triggers)
