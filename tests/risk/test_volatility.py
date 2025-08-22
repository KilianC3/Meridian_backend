from __future__ import annotations

import pandas as pd

from risk_engine.volatility import ewma_volatility


def test_ewma_volatility() -> None:
    series = pd.Series([100.0, 101.0, 102.0, 101.0, 103.0])
    vol = ewma_volatility(series, span=2)
    assert vol >= 0
