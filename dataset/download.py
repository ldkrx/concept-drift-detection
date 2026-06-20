import argparse
import logging
import os
from dataclasses import dataclass

from pandas import DataFrame
import yfinance as yf

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)


@dataclass
class Config:
    ticker: str = "^JKSE"
    start: str = "2010-01-01"
    end: str = "2026-06-20"
    output_path: str = "original/jkse.csv"


def download_data(ticker: str, start: str, end: str) -> DataFrame | None:
    log.info("Downloading %s from %s to %s", ticker, start, end)
    return yf.download(ticker, start=start, end=end)


def save_data(df: DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    df.to_csv(path)
    log.info("Saved %d rows to %s", len(df), path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download JKSE market data")
    parser.add_argument("--ticker", default="^JKSE")
    parser.add_argument("--start", default="2010-01-01")
    parser.add_argument("--end", default="2026-06-20")
    parser.add_argument("--output", default="original/jkse.csv")
    args = parser.parse_args()

    cfg = Config(
        ticker=args.ticker,
        start=args.start,
        end=args.end,
        output_path=args.output,
    )

    data = download_data(cfg.ticker, cfg.start, cfg.end)
    if data is None or data.empty:
        log.error("Failed to download data for %s", cfg.ticker)
        return

    save_data(data, cfg.output_path)

    log.info("Columns: %s", list(data.columns))


if __name__ == "__main__":
    main()
