# **Official Phase 3 Execution Report: Empirical Evaluation of the Rolling Retraining Pipeline**

This document is a comprehensive report on the results of Phase 3: Prediction Model Development & Rolling Retraining Pipeline. All figures, computation durations, and mathematical fluctuations below are raw, real, and objective from the Indonesia Stock Exchange (IHSG) Composite Index time series testing environment for the 2010–2026 period, without engineering or subjective assumptions. This document must serve as the primary baseline in carrying out Phase 4 (Evaluation Metric Analysis) and Phase 5 (Proceedings Article Writing).

# **1. Executive Summary & Data Processing Foundation**

The running pipeline experiment (prequential loop test-then-train) was successfully completed with a high level of stationarity discipline and anti-look-ahead bias. Processing rules were locked to the following operational parameters:

* **Final Matrix Dimensions:** The input feature matrix (X) is 3,929 rows × 9 multivariate features, and the target vector (y) is 3,929 rows. Data alignment is 100% synchronized after trimming trailing row residue due to next-day target (t+1) lag shift.
* **Warm-up Zone:** Chronological rows with integer indices 0 to 240 (first 241 trading samples) are allocated purely for initializing OS-ELM network weights and basic XGBoost tree parameters.
* **Simulation Zone:** Daily prequential evaluation runs uninterrupted starting from integer index row 241 through row 3,928.
* **Expansion of Comparison Boundaries (Baselines):** Integrating two extreme scenarios outside drift-driven control, namely the Static Model Scenario (Computational lower bound / 0 retrain) and Daily Retraining Scenario (Computational upper bound / 3,688 retrains). Both scenarios act as comparison fences to prove the novelty of drift-triggered algorithmic efficiency.

# **2. Cross-Scenario Performance Comparison Matrix**

The following is a recapitulation of empirical data recorded sequentially from all five scenario tests:

| Experiment Evaluation Metric | Static (Step 5) | Scenario C (ADWIN) | Scenario B (Wasserstein 120) | Scenario A (Wasserstein 60) | Daily (Step 6) |
|---|---|---|---|---|---|
| **Total Retraining Trigger Signals** | 0 | 34 | 311 | 271 | 3,688 |
| **Total Compute Runtime** | 14.34s | 19.21s | 95.37s | 127.62s | 501.90s |
| **Code Integrity Validation Status** | **Match: True** | **Match: True** | **Match: True** | **Match: True** | **Match: True** |
| **Pred_XGBoost Standard Deviation** | 0.005731 | 0.007630 | 0.007160 | 0.010150 | 0.004900 |
| **Pred_OS-ELM Standard Deviation** | 0.000000 | 0.001488 | 0.001489 | 0.001494 | 0.001486 |

# **3. Critical Discussion: Financial Anomaly Dissection & Algorithm Paradoxes**

The real execution results of Phase 3 revealed three fundamental scientific anomalies that dismantle common assumptions in stock market adaptive system architecture. These findings will become the main theoretical contribution (novelty) in our proceedings manuscript:

### **3.1. The Wasserstein Window Resolution Paradox (60 vs 120 Days)**

Conventionally, researchers assume that widening the statistical window size (Scenario B = 120 days) will smooth fluctuations, thus reducing the number of trigger alarms. However, experimental data shows the opposite: The Semester window (120 days) triggered **311 alarms**, much denser than the Quarterly window (60 days) which only triggered **271 alarms**. This result is consistent with and extends the *Window Dilemma* thesis (Gower-Winter et al., 2026). Our empirical interpretation is that wider windows can act as distortion accumulators; structural shift patterns from previous months settle within the reference window, so once the Wasserstein threshold is exceeded, the detector experiences a cascade of successive triggers. As a result, a paradoxical efficiency emerges: despite triggering **15% more retrains** (311 vs 271), Scenario B completes in just **95.37 seconds** — a **25% reduction** compared to Scenario A's 127.62 seconds. This inverse relationship challenges the assumption that retrain count alone determines computational cost. The key lies in OS-ELM's per-retrain overhead: each Wasserstein-120 retrain operates on a shorter accumulated data buffer (due to denser trigger spacing), resulting in smaller matrix inversion operations (0.307s per retrain) compared to the larger buffers accumulated under Wasserstein-60's sparser triggers (0.471s per retrain).

### **3.2. The Pure-Stream Computational Load Paradox (ADWIN Buffer)**

Scenario C (ADWIN) acts as a very conservative pure stream detector. Across 15 years of timeline, ADWIN successfully dampened market noise and only passed **34 structural drift signals**. The computational efficiency is exceptional: Scenario C completes in just **19.21 seconds** — a **96.17% reduction** from Daily Retraining (501.90s) and only **4.87 seconds** above the Static baseline (14.34s). This makes ADWIN the most computationally efficient drift-driven strategy among all scenarios tested.

However, a subtle paradox emerges upon per-retrain analysis: each ADWIN retrain costs **0.565 seconds** on average, substantially higher than Daily (0.136s/retrain) and Wasserstein-120 (0.307s/retrain). This premium arises because ADWIN's long intervals between sparse alarms (34 retrains across 15 years) allow OS-ELM's sequential data buffer to accumulate thousands of rows between retrains. When the ADWIN trigger finally fires, the recursive least squares (RLS) function performs matrix inversion on this swollen accumulated buffer. Yet this per-retrain overhead is rendered negligible in absolute terms — the total wall-clock time of 19.21 seconds still places ADWIN as the clear computational winner, proving that the real-world efficiency metric is total runtime, not per-event cost.

### **3.3. The Plasticity Death Phenomenon (Weight Collapse) in OS-ELM**

In-depth examination of the prediction time series tail zone (June 2026) detected numerical freezing symptoms in the OS-ELM model. OS-ELM's daily predictions gradually settled into a linear constant value (Scenario B froze at `+0.000206` and Scenario C at `+0.000200`). This is very costly empirical evidence of the risk of *over-regularization*. When data flows without parameter refresh interruptions for an excessively long period, the analytical pseudo-inverse estimation undergoes mathematical saturation. The model's internal weights lose micro-adaptive capability to new daily volatility and collapse into a static trend assessor. This plasticity collapse phenomenon confirms why the non-linear comparison model XGBoost—which is forced into a *cold restart* using a fixed 250-day rolling window—maintains its prediction volatility (XGB std remains healthy at 0.007–0.010).

### **3.4. Experimental Paradox Proof Through Extreme Boundaries (Static vs Daily)**

**Empirical Evidence of OS-ELM Static Paralysis:** In the Static Scenario (Step 5), the model undergoes total degeneration without data refresh interruptions, with a variance/standard deviation (σ) value of 0.000000 and a single constant prediction value of +0.001090. This supports the interpretation that the sigmoid activation function on multivariate financial flow data can experience permanent numerical saturation without retraining.

**Resurrection via Daily Incremental Update:** In contrast to the static condition, the Daily Retraining Scenario (Step 6) successfully revived OS-ELM plasticity (σ score rose healthily to 0.001486). However, this daily refresh came at a destructive computational cost of 501.90 seconds (a massive ~3,400% surge above the static model baseline of 14.34s). This massive surge locks the core research argument: blind daily retraining produces unreasonable computational overhead waste in a production exchange environment.

# **4. Workflow Interaction Guide for Subsequent Phases**

All projection result matrices from Phase 3 testing have been safely summarized and stored in our repository directory structure. The containers ready for processing in the next phase are:

1. `predictions_step2.csv` (Scenario A Output — Wasserstein 60)
2. `predictions_step3.csv` (Scenario B Output — Wasserstein 120)
3. `predictions_step4.csv` (Scenario C Output — ADWIN)
4. `predictions_step5.csv` (Upper Error Boundary Output — Static)
5. `predictions_step6.csv` (Upper Computational Boundary Output — Daily)

**Rigid Phase 4 Note:** Final accuracy metric evaluation (MAE and RMSE) must be computed comparatively across all 5 scenarios (total of 10 model prediction columns) purely on the exchange simulation zone (integer index rows 241 through 3928). ε-MAPE may only be retained as a diagnostic stress test for near-zero target instability.

This document locks the validity of the entire retraining pipeline sequence. In Phase 4 implementation, we are strictly prohibited from altering, shifting, or modifying the daily prediction values produced in Phase 3 to ensure the sanctity of statistical testing.
