"""Infer causal edges between factors.

The real implementation would use advanced statistics (Elastic Net, Granger
causality, transfer entropy, DTW). For the MVP we provide a lightweight
correlation-based approximation that returns the strongest lagged
correlation within a 180 day window.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd


class EdgeEstimate(dict):
    """Simple container for inferred edge parameters."""


def infer_edges(
    data: Dict[int, pd.Series], max_lag_days: int = 180
) -> List[EdgeEstimate]:
    """Infer connections between factors using lagged correlations.

    Parameters
    ----------
    data:
        Mapping of ``factor_id`` to time series (indexed by datetime).
    max_lag_days:
        Maximum lag (in days) to consider when searching for lead/lag
        relationships. Defaults to ``180``.

    Returns
    -------
    list[EdgeEstimate]
        List of inferred edges with beta, ``lag_days`` and ``confidence`` fields.
    """

    edges: List[EdgeEstimate] = []
    factors = list(data.items())
    for i, (src_id, src_series) in enumerate(factors):
        for dst_id, dst_series in factors[i + 1 :]:
            # Align series
            df = pd.concat([src_series, dst_series], axis=1).dropna()
            if df.empty:
                continue
            src = df.iloc[:, 0]
            dst = df.iloc[:, 1]
            # Compute cross-correlation to find lag
            corr = np.correlate(src - src.mean(), dst - dst.mean(), mode="full")
            lag = corr.argmax() - (len(dst) - 1)
            if lag > max_lag_days:
                lag = max_lag_days
            if lag < -max_lag_days:
                lag = -max_lag_days
            beta = float(np.corrcoef(src.shift(lag).dropna(), dst[lag:].dropna())[0, 1])
            confidence = abs(beta)
            edges.append(
                EdgeEstimate(
                    {
                        "src_factor": src_id,
                        "dst_factor": dst_id,
                        "beta": beta,
                        "lag_days": int(lag),
                        "confidence": confidence,
                    }
                )
            )
    return edges
