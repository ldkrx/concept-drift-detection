# Dataset — Coding Conventions & Project Structure

## Project Structure

```
dataset/
├── download.py          # Download raw market data via yfinance → original/
├── preprocess.py        # Feature engineering pipeline → processed/
├── requirements.txt     # Pinned Python dependencies
├── original/            # Raw CSVs (gitignored)
└── processed/           # Enriched CSVs (gitignored)
```

Data flows one-way: `download.py` → `original/*.csv` → `preprocess.py` → `processed/*.csv`.

## Coding Conventions

### File structure (entry-point scripts)

```python
import argparse
import logging
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)


@dataclass
class Config:
    ...


def main() -> None:
    parser = argparse.ArgumentParser(...)
    args = parser.parse_args()
    cfg = Config(field=args.field)
    ...


if __name__ == "__main__":
    main()
```

### Rules

| Rule | Convention |
|---|---|
| **Logging** | Module-level `basicConfig`; `log = logging.getLogger(__name__)` |
| **Config** | `@dataclass` class `Config` with defaults matching argparse defaults |
| **argparse** | `--kebab-case` flags, mapped via `Config(field=args.field)` |
| **Functions** | Type-hinted, pure-ish (no side effects beyond logging), composed linearly in `main()` |
| **Naming** | `snake_case` for functions/vars, `PascalCase` for classes |
| **Imports** | stdlib → blank line → third-party; shared local modules allowed (import from sibling) |
| **Output dirs** | `os.makedirs(os.path.dirname(path) or ".", exist_ok=True)` |
