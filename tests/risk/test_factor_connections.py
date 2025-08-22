from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import pytest

from risk_engine.edges import infer_edges


def test_infer_edges_basic() -> None:
    """Edges are inferred with sensible beta, lag, and confidence."""
    idx = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(5)]
    src = pd.Series([1, 2, 3, 4, 5], index=idx)
    dst = src.copy()  # perfectly correlated, zero lag
    edges = infer_edges({1: src, 2: dst}, max_lag_days=10)
    assert len(edges) == 1
    edge = edges[0]
    assert edge["src_factor"] == 1
    assert edge["dst_factor"] == 2
    assert edge["lag_days"] == 0
    assert pytest.approx(edge["beta"], rel=1e-6) == 1.0
    assert pytest.approx(edge["confidence"], rel=1e-6) == 1.0
