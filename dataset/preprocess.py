import argparse
import logging
import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)


@dataclass
class Config:
    vol_windows: list[int] = field(default_factory=lambda: [20, 60])
    bb_window: int = 5
    ema_span: int = 5
    momentum_windows: list[int] = field(default_factory=lambda: [5, 20])
    input_path: str = "original/jkse.csv"
    output_path: str = "processed/jkse_preprocessed.csv"


def load_data(path: str) -> pd.DataFrame:
    log.info("Loading data from %s", path)
    return pd.read_csv(path, skiprows=[1, 2])


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Cleaning data")
    df = df.rename(columns={"Price": "Date"})
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date").sort_index()
    df = df.ffill()
    log.info("Date range: %s to %s", df.index.min(), df.index.max())
    return df


def add_features(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    log.info("Adding features")

    df["Log_Return"] = np.log(df["Close"] / df["Close"].shift(1))

    for w in cfg.vol_windows:
        df[f"Vol_{w}d"] = df["Log_Return"].rolling(w).std()

    df["EMA_5"] = df["Close"].ewm(span=cfg.ema_span).mean()

    df["BB_Middle"] = df["Close"].rolling(cfg.bb_window).mean()
    df["BB_Upper"] = df["BB_Middle"] + 2 * df["Close"].rolling(cfg.bb_window).std()
    df["BB_Lower"] = df["BB_Middle"] - 2 * df["Close"].rolling(cfg.bb_window).std()

    for w in cfg.momentum_windows:
        df[f"Momentum_{w}d"] = df["Log_Return"].rolling(w).sum()

    return df


def finalize(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.dropna()
    after = len(df)
    log.info("Dropped %d NaN rows (kept %d)", before - after, after)
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess JKSE market data")
    parser.add_argument("--input", default="original/jkse.csv")
    parser.add_argument("--output", default="processed/jkse_preprocessed.csv")
    args = parser.parse_args()

    cfg = Config(input_path=args.input, output_path=args.output)

    os.makedirs(os.path.dirname(cfg.output_path) or ".", exist_ok=True)

    df = load_data(cfg.input_path)
    df = clean_data(df)
    df = add_features(df, cfg)
    df = finalize(df)

    df.to_csv(cfg.output_path)
    log.info("Saved %d rows to %s", len(df), cfg.output_path)
    log.info("Columns: %s", list(df.columns))


if __name__ == "__main__":
    main()
