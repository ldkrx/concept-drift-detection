## OFFICIAL EXECUTION REPORT PHASE 1: DATA COLLECTION AND PREPROCESSING

## I. Dataset Acquisition & Cleaning

- **Primary Dataset Selection:** We agreed to use the historical data of the Indonesia Stock Exchange (IHSG) Composite Index with the ticker ^JKSE sourced from Yahoo Finance, covering the period from 2010 onwards. The use of this local market index is intended to provide strong novelty value for the National Seminar publication target.
- **Format and Missing Data Cleaning:** Raw data has been cleaned by removing unnecessary header rows and setting the Date column as a Datetime-formatted index. Missing values, such as those on market holidays, have been handled using the forward-fill (ffill) method to maintain time series continuity without introducing future information bias.
- **Stationarity Transformation:** Absolute closing prices have been converted into daily logarithmic returns (Log_Return). This step is crucial for normalizing the distribution of financial data.

## II. Feature Engineering & Transformation

- **Volatility Feature Extraction (Rolling Volatility):** We have calculated and added rolling standard deviation features to monitor market fluctuations, namely volatility within 20-day (Vol_20d) and 60-day (Vol_60d) windows.
- **Technical Indicators and Momentum Calculation:** To capture trend movement signals and short-term price dynamics, the dataset has been enriched with:
  - 5-day Exponential Moving Average (EMA_5d).
  - Three 5-day Bollinger Bands boundaries, consisting of the middle band (BB_Mid), upper band (BB_Upper), and lower band (BB_Lower).
  - Trend direction momentum based on cumulative log-return calculations over 5 days (Momentum_5d) and 20 days (Momentum_20d).

## III. Final Dataset Profile

- **Final Cleaning (Dropna):** The first 60 rows containing NaN values (due to side effects from the 60-day rolling window calculations) have been successfully removed. The clean, ready-to-use data now effectively starts from March 31, 2010 with proportional metric values.
- **Data Dimensions:** 3,930 rows × 14 columns (after cleaning and feature engineering).

## IV. Handover to Phase 2

With the completion of the above steps, the IHSG historical data is now fully prepared for use in Phase 2, namely the implementation and comparison stage of concept drift detection algorithms (both standard baselines and our proposed metrics).
