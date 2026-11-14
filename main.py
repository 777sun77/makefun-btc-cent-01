"""Deterministic, offline BTC four-hour point forecast."""

import json
import math
import os
from pathlib import Path


def price5(value):
    return round(min(9_999_999.99999, max(0.00001, value)), 5)


def forecast(prices):
    if not prices:
        raise ValueError("empty price history")
    last = float(prices[-1])
    if not math.isfinite(last):
        raise ValueError("invalid last price")
    # A small pull toward the recent four-hour mean scored better than
    # persistence in the rolling BTC/USDT proxy backtest. Keep the adjustment
    # deliberately modest because short-horizon BTC prices are noisy.
    recent = [float(x) for x in prices[-240:]]
    anchor = sum(recent) / len(recent)
    return price5(last + 0.10 * (anchor - last))


def main():
    input_dir = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(input_dir.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        if len(case.get("markets", [])) != 1:
            raise ValueError(f"{path.name} must contain one market")
        prices = case["markets"][0].get("prices", [])
        result = {"forecasts": [{"case": path.stem, "price": forecast(prices)}]}
        (output_dir / f"{path.stem}.out").write_text(
            json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
