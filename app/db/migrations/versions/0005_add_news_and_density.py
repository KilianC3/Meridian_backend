from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("factors", sa.Column("evidence_density", sa.Float(), nullable=True))
    op.add_column(
        "factor_edges", sa.Column("evidence_density", sa.Float(), nullable=True)
    )
    op.create_table(
        "news_mentions",
        sa.Column("mention_id", sa.Integer(), primary_key=True),
        sa.Column(
            "factor_id",
            sa.Integer(),
            sa.ForeignKey("factors.factor_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("source_id", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("snippet", sa.Text(), nullable=True),
        sa.Column("raw", sa.JSON(), nullable=True),
        sa.UniqueConstraint("source", "source_id"),
    )

    factors_table = sa.table(
        "factors",
        sa.column("factor_id", sa.Integer()),
        sa.column("name", sa.String()),
        sa.column("series_id", sa.String()),
        sa.column("note", sa.Text()),
        sa.column("evidence_density", sa.Float()),
    )
    op.bulk_insert(
        factors_table,
        [
            {
                "factor_id": 1,
                "name": "Oil Prices",
                "series_id": None,
                "note": None,
                "evidence_density": 0.0,
            },
            {
                "factor_id": 2,
                "name": "Inflation",
                "series_id": None,
                "note": None,
                "evidence_density": 0.0,
            },
        ],
    )

    edges_table = sa.table(
        "factor_edges",
        sa.column("edge_id", sa.Integer()),
        sa.column("src_factor", sa.Integer()),
        sa.column("dst_factor", sa.Integer()),
        sa.column("sign", sa.Integer()),
        sa.column("lag_days", sa.Integer()),
        sa.column("beta", sa.Float()),
        sa.column("confidence", sa.Float()),
        sa.column("evidence_count", sa.Integer()),
        sa.column("evidence_density", sa.Float()),
    )
    op.bulk_insert(
        edges_table,
        [
            {
                "edge_id": 1,
                "src_factor": 1,
                "dst_factor": 2,
                "sign": 1,
                "lag_days": 30,
                "beta": 0.8,
                "confidence": 1.0,
                "evidence_count": 1,
                "evidence_density": 0.0,
            }
        ],
    )

    links_table = sa.table(
        "evidence_links",
        sa.column("factor_id", sa.Integer()),
        sa.column("mongo_doc_id", sa.String()),
        sa.column("weight", sa.Float()),
    )
    op.bulk_insert(
        links_table,
        [
            {"factor_id": 1, "mongo_doc_id": "sample_doc", "weight": 1.0},
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM evidence_links WHERE mongo_doc_id='sample_doc'")
    op.execute("DELETE FROM factor_edges WHERE edge_id=1")
    op.execute("DELETE FROM factors WHERE factor_id IN (1,2)")
    op.drop_table("news_mentions")
    op.drop_column("factor_edges", "evidence_density")
    op.drop_column("factors", "evidence_density")
