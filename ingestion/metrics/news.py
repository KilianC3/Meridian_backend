from __future__ import annotations

from typing import Any


def update_density(conn: Any) -> None:
    """Update evidence_density on factors based on recent news mentions."""
    cur = conn.cursor()
    cur.execute(
        """
        WITH counts AS (
            SELECT factor_id, COUNT(*)::float AS cnt
            FROM news_mentions
            WHERE factor_id IS NOT NULL
              AND published_at >= NOW() - INTERVAL '90 days'
            GROUP BY factor_id
        )
        UPDATE factors f
        SET evidence_density = c.cnt
        FROM counts c
        WHERE f.factor_id = c.factor_id;
        """
    )
    conn.commit()
