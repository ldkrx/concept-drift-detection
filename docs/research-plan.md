## Deep Research Planning Guide: Concept Drift Detection in Financial Time Series and Evaluation of Rolling Retraining Strategies

This guide serves as a standard operational compass for carrying out proceedings research comprehensively and systematically. Each work phase is designed in detail, balancing scientific contribution (novelty) and technical efficiency without relying on subjective assumptions.

## I. Research Identity and Orientation

- Research Title: Concept Drift Detection in Financial Time Series and Evaluation of Rolling Retraining Strategies
- Main Topic: Explicit analysis of data distribution changes (concept drift) in financial time series data and their impact on adaptive model retraining efficiency.
- Primary Dataset: Historical data of the Indonesia Composite Index (IHSG) with ticker ^JKSE sourced from Yahoo Finance, covering a chronological range since 2010.
- Main Focus & Novelty Twist: Using quantitative data distribution shifts as an explicit trigger for model retraining (drift-driven retraining), replacing fixed-interval retraining which is inefficient in dynamic exchange environments.

## II. Theoretical Foundation and Key References

This research is supported by several important theoretical pillars drawn from indexed literature:

1. The Window Dilemma (Gower-Winter et al., 2026): A critical foundation highlighting the challenge that drift perception is often a product of how the data window size is determined, rather than solely the original distribution change. Full citation: Gower-Winter et al. (2026), *Advances in Intelligent Data Analysis XXIV* (IDA 2026), Springer LNCS vol. 16513, DOI: 10.1007/978-3-032-23833-7_27.
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

**Implementation:** A global drift signal in the system will only be declared active (triggered) and initiate retraining if at least 1/3 (33.3%, i.e., at least 3 of 9 features) simultaneously detect drift within a single chronological time unit. This step is crucial to minimize false alarm explosion.

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
- **Chronological Drift Point Map:** A record of effective date indices (starting March 31, 2010) where each algorithm detects drift based on the ≥ 1/3 (33.3%, at least 3 of 9 features) consensus rule.
- **Window Sensitivity Analysis:** Visual and tabular evaluation of differences in the number of drift points captured by 60-day versus 120-day trading windows, as an empirical contribution to addressing The Window Dilemma.

## **V. Work Plan Details for Phase 3: Prediction Model Building & Rolling Retraining Pipeline**

Phase 3 is designed to build a real-time data stream simulation system using a prequential (test-then-train) scheme to test the effectiveness of explicit drift-driven retraining triggers. This experiment confronts two models with contrasting computational philosophies: XGBoost as a representation of a conventional high-performance batch learner, and OS-ELM as a representation of a resource-efficient adaptive online learner.

## **A. Global Architecture & Data Discipline Regulations**

To lock in scientific validity and ensure experimental fairness (ceteris paribus), the processing pipeline in Phase 3 must comply with the following structural constraints:

1. **Target Variable Definition ($y$):** The prediction target is absolutely locked to the next day's Log\_Return value ($t+1$). This choice aligns with the Phase 1 preprocessing step to maintain stationarity of the financial time series target.  
2. **Input Feature Matrix ($X$):** The model purely uses the 9 multivariate features extracted in Phase 1: Log\_Return, Vol\_20d, Vol\_60d, EMA\_5, BB\_Middle, BB\_Upper, BB\_Lower, Momentum\_5d, and Momentum\_20d.  
3. **Warm-Up Period & Simulation Start Boundary:** Rows $0$ through $240$ of the clean chronological dataset are allocated purely as initial warm-up training data. This rule locks uniformity of the accuracy race starting point, given that the largest test window in Phase 2 (WASSERSTEIN\_120) requires a buffer of $2W = 240$ rows to legally trigger its first signal. The upstream-downstream daily simulation will run synchronously starting from integer row 241 to the last row (June 19, 2026). The Phase 2 Wasserstein counts of 273/312 reflect the full detector evaluation window; the Phase 3--4 retraining counts of 271/311 reflect the trimmed simulation zone after target-lag trimming and warm-up exclusion.  
4. **Total Isolation of Trigger Scenarios:** In accordance with Phase 2 regulatory decisions, PSI and KS-Test methods are completely eliminated from the retraining control pipeline. Full control of retraining rotation is purely delegated to the 3 healthy scenarios:  
   * **Scenario A (Quarterly Batch):** Global retraining commands are commanded by the active trigger date set from WASSERSTEIN\_60.  
   * **Scenario B (Semester Batch):** Global retraining commands are commanded by the active trigger date set from WASSERSTEIN\_120.  
   * **Scenario C (Pure Stream):** Global retraining commands are commanded by the active trigger date set from ADWIN (river).

## **B. Technical Specifications of Algorithms & Model Hyperparameters**

### **1\. XGBoost (Batch Learner Representation)**

* **Adaptation Philosophy:** When the trigger date coordinate for a scenario is active on day $t$, the XGBoost model undergoes a cold restart (destroyed and retrained from scratch).  
* **Window Strategy:** Uses a **Fixed Rolling Window of 250 trading days** backward from point $t$. This step cuts off stale market distribution memory so the model focuses on learning the latest data structure post-market shock.  
* **Hyperparameter Configuration:**  
  * n\_estimators: 100  
  * max\_depth: 3 (Limits tree depth to prevent absorbing high daily market noise)  
  * learning\_rate: 0.05  
  * subsample: 0.8

### **2\. OS-ELM (Online Sequential Extreme Learning Machine)**

* **Adaptation Philosophy:** When the trigger date coordinate is active, OS-ELM does not retrain from scratch. The model updates its output weights instantly using a purely sequential matrix-based recursive analytical formula, only utilizing incoming new data.  
* **Hyperparameter Configuration:**  
  * n\_hidden\_neurons: 100 (Provides ample hidden dimension space to map non-linear relationships of the 9 financial input features)  
  * activation\_function: 'sigmoid'

## **C. Empirical Work Steps for Phase 3 (Modular Execution Guide)**

### **Step 1: Lag Target Pair Engineering & Evaluation Matrix Initialization**

The initial operational step to form feature-target pairs for the future target ($y\_{t+1}$) and lock memory allocation for daily prediction value arrays for Phase 4 accuracy metrics.

* **Input:** Main DataFrame from Phase 1 cleaning (3,930 rows $\\times$ 14 columns).  
* **Code Logic:**  
  1. Create a new target column Target\_Log\_Return by shifting the Log\_Return column up by one row (df['Log_Return'].shift(-1)).  
  2. Drop the last row of the dataset due to the loss of target value from the shift.  
  3. Split the dataset into matrix $X$ (9 input features) and vector $y$ (Target\_Log\_Return).  
  4. Provide empty arrays or new columns named Pred\_XGB\_ScenarioA, Pred\_OSELM\_ScenarioA, etc. (total 6 daily prediction projection columns) starting from integer row index 241 to the end.  
* **Outputs to Report:**  
  1. Confirmation of the final dimensions of matrix $X$ and vector $y$ after row trimming due to target lag shifting.  
  2. Proof via a data snippet of the initial row at index 241 to ensure no look-ahead bias.

### **Step 2: Prequential Simulation Scenario A (WASSERSTEIN\_60 Control)**

Executing a sequential daily chronological loop from row 241 to the final row under the control of WASSERSTEIN\_60 triggers.

* **Input:** WASSERSTEIN\_60 time series signal vector from Phase 2, data $X$ and $y$, and initial model instances of XGBoost and OS-ELM trained on the first 240 rows.  
* **Loop Logic (Day $t$):**  
  1. **Test Phase:** Use the current XGBoost and OS-ELM models to predict $y\_t$ with input $X\_t$. Record predictions in the Scenario A scoreboard.  
  2. **Train Phase (Sensor Check):** Check WASSERSTEIN\_60 status on day $t$.  
     * *If Status = 0 (Normal):* Models are unchanged. For OS-ELM specifically, accumulate streaming data memory block without updating the main weight matrix.  
     * *If Status = 1 (Drift Detected):* Trigger Retraining instruction:  
       * **XGBoost:** Slice rows $[t - 250 : t]$. Refit a new XGBoost model object using that rolling slice data (cold restart).  
       * **OS-ELM:** Call the .slearn() function or incremental update step to update the internal weight matrix analytically using only data blocks since the last drift.  
* **Outputs to Report:**  
  1. Record of the frequency of retraining actions successfully executed throughout the timeline for XGBoost and OS-ELM in Scenario A.

### **Step 3: Prequential Simulation Scenario B (WASSERSTEIN\_120 Control)**

Executing a daily sequential loop mechanism identical to Step 2, but full control of model rotation triggering is handed over to the medium-term crisis scoreboard WASSERSTEIN\_120.

* **Input:** WASSERSTEIN\_120 time series signal vector, data $X$ and $y$, and initial model objects.  
* **Loop Logic:** Follows the daily test-then-train protocol with retraining interruptions strictly regulated by active WASSERSTEIN\_120 signal dates.  
* **Outputs to Report:**  
  1. Record of the frequency of retraining actions successfully triggered throughout the Scenario B timeline.

### **Step 4: Prequential Simulation Scenario C (ADWIN river Library Control)**

Executing a daily sequential loop mechanism with retraining trigger interruptions commanded by a pure, highly conservative data stream sensor, namely ADWIN.

* **Input:** ADWIN time series signal vector from Phase 2, data $X$ and $y$, and initial model objects.  
* **Loop Logic:** Follows the daily test-then-train protocol with retraining interruptions strictly regulated by active ADWIN global drift signal dates.  
* **Outputs to Report:**  
  1. Record of the frequency of retraining actions successfully triggered throughout the Scenario C timeline.

### **Step 5: Projection Results Data Consolidation & Computational Time Profiling**

Combining all projection result arrays from the three scenarios above into a single comprehensive summary DataFrame and recording the total runtime processing time of each model to test the computational ROI claim.

* **Input:** Prediction record arrays from Steps 2, 3, and 4, along with execution time records (time.time()) per scenario.  
* **Outputs to Report:**  
  1. Final dimension profile of the prediction recap DataFrame (must be synchronized from integer row index 241 to the last row).  
  2. Table of total processing time duration between XGBoost vs OS-ELM models for the three test scenarios (Scenarios A, B, and C).

## VI. Work Plan Details for Phase 4: Comprehensive Metric Evaluation & Computational ROI Analysis

Phase 4 is not merely a routine of calculating statistical error metrics; it aims to gather **empirical ammunition** to quantitatively prove our originality claim: that drift-driven retraining strategy can drastically cut computational costs (approaching the Static Model lower bound) while maintaining high accuracy (approaching the Daily Retraining upper bound).

### A. Detailed Work Step Protocol

#### Step 1: Accuracy Formulation & Diagnostic Stress Test (MAE, RMSE & $\epsilon$-MAPE)

- **Simulation Zone Isolation Rule:** All accuracy metric calculations must be strictly truncated to the **Active Simulation Zone**, i.e., integer row indices 241 to 3928. Data from the Warm-up Zone (rows 0–240) must be discarded entirely from calculations to avoid evaluation bias.
- **Epsilon Protection Mechanism ($\epsilon$-MAPE):** Because our target data is Log_Return (daily return percentage) which takes very small values ($0.00\times$) and often hits absolute $0.0$ when the market is stagnant, standard library MAPE functions (e.g., scikit-learn) will suffer from ZeroDivisionError or produce Infinity values. The custom $\epsilon = 10^{-8}$ calculation is retained as a diagnostic stress test, not as the final performance metric, to demonstrate whether naive epsilon protection is safe in this near-zero financial target regime.
- **Rigorous Mathematical Formulation:**
  $$\epsilon\text{-MAPE} = \frac{1}{n} \sum_{i=241}^{3928} \left| \frac{y_i - \hat{y}_i}{|y_i| + 10^{-8}} \right| \times 100\%$$
  $$\text{MAE} = \frac{1}{n} \sum_{i=241}^{3928} |y_i - \hat{y}_i|$$
  $$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=241}^{3928} (y_i - \hat{y}_i)^2}$$
- **Result Container Structure (metrics_accuracy_df):** Calculation results must be summarized into a single comparative DataFrame of size 10 rows (5 Scenarios $\times$ 2 Models) to serve as the main table in the experimental results section of the paper.

#### Step 2: Computational ROI Analysis & Trade-off

This step marries accuracy performance data (Step 1) with real computational runtime operational data locked from Phase 3.

- **Extreme Boundary Anchor Consolidation:** Insert real runtime data from Phase 3 into the comparison matrix:
  1. *Static Model*: 0 retrain | Runtime: **14.34s**
  2. *Scenario C (ADWIN Stream)*: 34 retrain | Runtime: **19.21s**
  3. *Scenario B (Wasserstein 120)*: 311 retrain | Runtime: **95.37s**
  4. *Scenario A (Wasserstein 60)*: 271 retrain | Runtime: **127.62s**
  5. *Daily Retraining*: 3688 retrain | Runtime: **501.90s**
- **Relative Resource Savings Calculation:** Compute the runtime efficiency percentage of drift-driven strategies (A, B, C) relative to Daily Retraining as the system load upper bound:
  $$\text{Computational Efficiency (\%)} = \left( 1 - \frac{\text{Runtime}_{\text{Drift}}}{\text{Runtime}_{\text{Daily}}} \right) \times 100\%$$

#### Step 3: Quantitative Extraction for Theoretical Discussion Material

To meet the analytical depth standards of Jurnal IFTK, this guide mandates the extraction of two scientific anomalies discovered in Phase 3:

- **Quantification of OS-ELM Plasticity Death:** Take the standard deviation ($\sigma$) of Pred_OSELM_Static ($\sigma = 0.000000$) and demonstrate its prediction paralysis frozen at a constant $+0.001090$. Compare this with the healthy $\sigma$ spike of Pred_OSELM_Daily ($0.001486$) to prove the risk of sigmoid function over-regularization if not refreshed.
- **Window Dilemma Paradox:** Present empirical evidence of why Scenario B (120-day window) triggers more alarms (**311 times**) compared to Scenario A (60-day window — **271 times**). Frame this as consistent with and extending the Gower-Winter et al. (2026) Window Dilemma thesis; the structural-distortion accumulation mechanism is our empirical interpretation from this study.

#### Step 4: IFTK Journal-Standard Graphic Visualization Standardization

To prevent rejection from reviewers due to confusing chart layouts, visualization rules are locked to the following protocol:

- **Visual Decoupling:** It is forbidden to stack all 10 prediction columns in a single chart. Plots must be separated into two main figures: one dedicated graph for the XGBoost model group (5 scenarios), and one dedicated graph for the OS-ELM model group (5 scenarios).
- **Technical Image Specifications:** Graphs must be saved at a minimum resolution of **300 DPI**. Use high-contrast colors that are grayscale-friendly for print, with a combination of different line types/markers for each scenario.
- **Drift Overlay (Interruption Line Annotation):** On the horizontal timeline axis, thin dashed vertical gray lines (alpha=0.4) must be placed precisely at the chronological dates where global drift alarms were triggered. This aims to provide readers with a dramatic visualization of how model accuracy is directly corrected positively immediately after retraining is triggered by the detector.

### B. Phase 4 Entry Gate Validation Checklist

Before Phase 4 code is executed, confirm the availability of the following data in your working memory/directory:

1. Is the consolidated file `predictions_step6.csv` containing 11 columns (1 y_true column + 10 prediction columns from Step 2 through Step 6) ready to be loaded?

## VII. Work Plan Details for Phase 5: Result Analysis and Proceedings Writing

The final experimental results will be compiled into a scientific publication manuscript adhering directly to the formatting guidelines of Jurnal Informatik IFTK:

- **Computational ROI Analysis:** Critical discussion of the computational resource savings ratio achieved by explicit drift trigger schemes compared to blind daily/periodic retraining.
- **Window Case Reflection:** Presenting empirical arguments on how window size (60 vs 120 days) affects drift visualization sensitivity, contributing to solving the theoretical dilemma of time series data streams.
- **IFTK Format Compliance:** Preparation of abstracts sized 70--150 words (9-point font, special 1.0 cm left margin), maximum 4 keywords, formula writing, data tables, and citation/referencing style strictly adhering to the uploaded IFTK journal template.
