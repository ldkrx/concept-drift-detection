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

## **V. Work Plan Details for Phase 3: Prediction Model Building & Rolling Retraining Pipeline**

Phase 3 is designed to build a real-time data stream simulation system using a prequential (test-then-train) scheme to test the effectiveness of explicit drift-driven retraining triggers. This experiment confronts two models with contrasting computational philosophies: XGBoost as a representation of a conventional high-performance batch learner, and OS-ELM as a representation of a resource-efficient adaptive online learner.

## **A. Global Architecture & Data Discipline Regulations**

To lock in scientific validity and ensure experimental fairness (ceteris paribus), the processing pipeline in Phase 3 must comply with the following structural constraints:

1. **Target Variable Definition ($y$):** The prediction target is absolutely locked to the next day's Log\_Return value ($t+1$). This choice aligns with the Phase 1 preprocessing step to maintain stationarity of the financial time series target.  
2. **Input Feature Matrix ($X$):** The model purely uses the 9 multivariate features extracted in Phase 1: Log\_Return, Vol\_20d, Vol\_60d, EMA\_5, BB\_Middle, BB\_Upper, BB\_Lower, Momentum\_5d, and Momentum\_20d.  
3. **Warm-Up Period & Simulation Start Boundary:** Rows $0$ through $240$ of the clean chronological dataset are allocated purely as initial warm-up training data. This rule locks uniformity of the accuracy race starting point, given that the largest test window in Phase 2 (WASSERSTEIN\_120) requires a buffer of $2W = 240$ rows to legally trigger its first signal. The upstream-downstream daily simulation will run synchronously starting from integer row 241 to the last row (June 19, 2026).  
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

## VI. Work Plan Details for Phase 4: Performance and Computational Evaluation

Evaluation is conducted using a real-time data stream simulation with a prequential (test-then-train) scheme. Assessment metrics are divided into two main categories:

- **Prediction Accuracy Metrics:** Using Mean Absolute Percentage Error (MAPE) and Root Mean Square Error (RMSE) to evaluate IHSG trend prediction performance before and after drift occurs.
- **Computational Efficiency Metrics:** Measuring total processing time, frequency or number of drift points identified by each detector, and the rate of accuracy degradation when retraining is delayed (drift robustness).

## VII. Work Plan Details for Phase 5: Result Analysis and Proceedings Writing

The final experimental results will be compiled into a scientific publication manuscript adhering directly to the formatting guidelines of Jurnal Informatik IFTK:

- **Computational ROI Analysis:** Critical discussion of the computational resource savings ratio achieved by explicit drift trigger schemes compared to blind daily/periodic retraining.
- **Window Case Reflection:** Presenting empirical arguments on how window size (60 vs 120 days) affects drift visualization sensitivity, contributing to solving the theoretical dilemma of time series data streams.
- **IFTK Format Compliance:** Preparation of abstracts sized 70--150 words (9-point font, special 1.0 cm left margin), maximum 4 keywords, formula writing, data tables, and citation/referencing style strictly adhering to the uploaded IFTK journal template.
