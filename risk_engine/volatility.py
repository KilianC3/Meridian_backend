"""Volatility computations for risk engine."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


def ewma_volatility(values: Iterable[float], span: int = 30) -> float:
    """Compute exponentially weighted moving volatility on log returns.

    Parameters
    ----------
    values:
        Iterable of price or index levels ordered by time.
    span:
        Span for the exponential weighting; defaults to 30.

    Returns
    -------
    float
        The latest EWMA volatility. Returns ``0.0`` if insufficient data.
    """
    series = pd.Series(list(values))
    if series.size < 2:
        return 0.0
    log_returns = np.log(series).diff()
    vol = log_returns.ewm(span=span).std().iloc[-1]
    if pd.isna(vol):
        return 0.0
    return float(vol)
