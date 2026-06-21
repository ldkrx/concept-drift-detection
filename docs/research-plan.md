## Deep Research Planning Guide: Concept Drift Detection in Financial Time Series and Evaluation of Rolling Retraining Strategies

This guide serves as a standard operational compass for carrying out proceedings research comprehensively and systematically. Each work phase is designed in detail, balancing scientific contribution (novelty) and technical efficiency without relying on subjective assumptions.

## I. Research Identity and Orientation

- Research Title: Concept Drift Detection in Financial Time Series and Evaluation of Rolling Retraining Strategies
- Main Topic: Explicit analysis of data distribution changes (concept drift) in financial time series data and their impact on adaptive model retraining efficiency.
- Primary Dataset: Historical data of the Indonesia Composite Index (IHSG) with ticker ^JKSE sourced from Yahoo Finance, covering a chronological range since 2010.
- Main Focus & Novelty Twist: Using quantitative data distribution shifts as an explicit trigger for model retraining (drift-driven retraining), replacing fixed-interval retraining which is inefficient in dynamic exchange environments.

## II. Theoretical Foundation and Key References

This research is supported by several important theoretical pillars drawn from indexed literature:

1. The Window Dilemma (Gower-Winter et al., 2026): A critical foundation highlighting the challenge that drift perception is often a product of how the data window size is determined, rather than solely the original distribution change.
2. Explicit Drift Detection in Finance (Cavalcante et al.; Pluzyan & Hovakimyan): Primary references for implementing ADWIN, KSWIN, and Page Hinkley algorithms on financial streaming data, as well as their integration with sequential models.
3. Incremental Learning (DoubleAdapt; CORAL): Supporting theory on how to efficiently adapt model parameters under distribution shifts in exchange rate time series.

## III. Actual Results of Phase 1: Data Preprocessing

Phase 1 has been completed, yielding clean, stationary data ready for sequential processing in Phase 2. Here is a summary of the features:

- Target Transformation: Conversion of absolute closing prices into daily logarithmic returns (Log_Return) to normalize financial distributions.
- Rolling Volatility Features: Volatility within 20-day (Vol_20d) and 60-day (Vol_60d) time windows.
- Momentum & Trend Indicators: 5-day Exponential Moving Average (EMA_5d), 5-day Bollinger Bands (BB_Mid, BB_Upper, BB_Lower), and 5-day (Momentum_5d) and 20-day (Momentum_20d) directional trend momentum accumulation.
- Initial History Cleaning: Removal of the first 60 rows due to the lag effect of rolling window calculations. Clean data effectively starts from March 31, 2010.

## IV. Work Plan Details for Phase 2: Implementation of Concept Drift Detectors

In this phase, concept drift detection is designed to empirically evaluate the impact of the Window Dilemma while comparing the efficiency of streaming-based detectors with batch rolling window-based detectors.

### A. Global Architecture & Decision Rules

To avoid subjective assumptions and ensure test validity on historical IHSG data, the technical work of Phase 2 must comply with the following three architectural pillars:

#### 1. Multivariate Consensus Scheme (Voting Mechanism)

**Decision:** Detection is performed on all features extracted in Phase 1 (not just the univariate Log_Return).

**Implementation:** A global drift signal in the system will only be declared active (triggered) and initiate retraining if at least 30% of all total features simultaneously detect drift within a single chronological time unit. This step is crucial to minimize false alarm explosion.

#### 2. Adjacent Sliding Windows Scheme

**Decision:** Non-stream statistical testing requires two dynamic comparison distributions.

**Implementation:** For each evaluation point $t$ with window size $W$, the Current Window is defined over the range $[t - W, t]$. This window will be directly compared to the Baseline Window immediately preceding it, over the range $[t - 2W, t - W]$.

#### 3. Paradigm Reconciliation (Streaming vs Batch Windowing)

**Decision:** Alignment of the inherent nature of detector libraries with the window size strategy.

**Implementation:**
- **Window-Based Detectors (Batch):** The Statistical group (Priority 1) and Proposed Metrics group (Priority 3) must be tested using a rigid Multi-Window Strategy: Quarterly Window (60 Trading Days) for short shocks and Semester Window (120 Trading Days) for macro regime shifts.
- **Streaming-Based Detectors (Stream):** The Data Stream group (Priority 2) from the `river` library runs naturally (incrementally, one data point at a time) without forcing rigid window boundaries, thus acting as a pure stream baseline.

### B. Coding Priority Matrix

#### Priority 1: Basic & Financial Statistics (MINPS/mySD & Kolmogorov-Smirnov)

Difficulty Level: Low

1. **MINPS/mySD** — Implemented as a Moving Average & Standard Deviation Control Chart Baseline. Signal is active if:
   $$\vert \mu_{\text{current}} - \mu_{\text{reference}} \vert > k \cdot \sigma_{\text{reference}}$$
   (with $k = 2.5$).

2. **Kolmogorov-Smirnov (KS-Test)** — Compares empirical cumulative distribution functions (CDFs) using `scipy.stats.ks_2samp`. Drift is active if p-value $< 0.05$.

#### Priority 2: Standard Data Stream Detectors (ADWIN, KSWIN, Page Hinkley)

Difficulty Level: Medium

Uses built-in implementations from the Python `river` library. The algorithms process data sequentially in chronological order, row by row. The main challenge lies in tuning sensitivity hyperparameters ($\alpha$ for KSWIN and $\delta$ for ADWIN) to align with IHSG volatility levels.

#### Priority 3: Domain-Specific Proposed Metrics (Population Stability Index & Wasserstein Distance)

Difficulty Level: High

1. **Population Stability Index (PSI)** — Uses Quantile Binning (Equal-Frequency) with 10 bins (deciles) formed from the Baseline Window distribution. This approach is mandatory for capturing the heavy-tailed nature of financial data without the risk of division-by-zero errors. Drift is active if $PSI > 0.25$.

2. **Wasserstein Distance** — Implements sequential Earth Mover's Distance, referencing the geometric visualization of inter-distribution distances.

### C. Testing Procedure and Phase 2 Outputs

Before proceeding to prediction model development in Phase 3, Phase 2 must produce an internal comparison document including:
- **Chronological Drift Point Map:** A record of effective date indices (starting March 31, 2010) where each algorithm detects drift based on the 30% feature consensus rule.
- **Window Sensitivity Analysis:** Visual and tabular evaluation of differences in the number of drift points captured by 60-day versus 120-day trading windows, as an empirical contribution to addressing The Window Dilemma.

## V. Work Plan Details for Phase 3: Prediction Model Development

To demonstrate the effectiveness of drift triggers across different model paradigms, the experiment is limited to two main models with contrasting computational characteristics:

1. **XGBoost (Batch Learner):** Represents a conventional high-accuracy model that requires substantial computational cost as it must retrain from scratch (cold restart) using an expanding/rolling window each time a drift trigger is activated.

2. **OS-ELM (Online Sequential Extreme Learning Machine — Online Learner):** Represents a modern adaptive model capable of incrementally updating its network weights using only incoming new data without retraining from scratch, thus saving significant time.

## VI. Work Plan Details for Phase 4: Performance and Computational Evaluation

Evaluation is conducted using a real-time data stream simulation with a prequential (test-then-train) scheme. Assessment metrics are divided into two main categories:

- **Prediction Accuracy Metrics:** Using Mean Absolute Percentage Error (MAPE) and Root Mean Square Error (RMSE) to evaluate IHSG trend prediction performance before and after drift occurs.
- **Computational Efficiency Metrics:** Measuring total processing time, frequency or number of drift points identified by each detector, and the rate of accuracy degradation when retraining is delayed (drift robustness).

## VII. Work Plan Details for Phase 5: Result Analysis and Proceedings Writing

The final experimental results will be compiled into a scientific publication manuscript adhering directly to the formatting guidelines of Jurnal Informatik IFTK:

- **Computational ROI Analysis:** Critical discussion of the computational resource savings ratio achieved by explicit drift trigger schemes compared to blind daily/periodic retraining.
- **Window Case Reflection:** Presenting empirical arguments on how window size (60 vs 120 days) affects drift visualization sensitivity, contributing to solving the theoretical dilemma of time series data streams.
- **IFTK Format Compliance:** Preparation of abstracts sized 70--150 words (9-point font, special 1.0 cm left margin), maximum 4 keywords, formula writing, data tables, and citation/referencing style strictly adhering to the uploaded IFTK journal template.
