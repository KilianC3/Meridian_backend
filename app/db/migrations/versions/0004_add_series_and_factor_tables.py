from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "series",
        sa.Column("series_id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("unit", sa.String(), nullable=True),
        sa.Column("frequency", sa.String(), nullable=True),
        sa.Column("geography", sa.String(), nullable=True),
        sa.Column("sector", sa.String(), nullable=True),
        sa.Column("transform", sa.String(), nullable=True),
        sa.Column("first_ts", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_ts", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "observations",
        sa.Column(
            "series_id",
            sa.String(),
            sa.ForeignKey("series.series_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("ts", sa.DateTime(timezone=True), primary_key=True),
        sa.Column("value", sa.Float(), nullable=True),
    )
    op.create_table(
        "factors",
        sa.Column("factor_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "series_id", sa.String(), sa.ForeignKey("series.series_id"), nullable=True
        ),
        sa.Column("note", sa.Text(), nullable=True),
    )
    op.create_table(
        "factor_edges",
        sa.Column("edge_id", sa.Integer(), primary_key=True),
        sa.Column(
            "src_factor",
            sa.Integer(),
            sa.ForeignKey("factors.factor_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "dst_factor",
            sa.Integer(),
            sa.ForeignKey("factors.factor_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sign", sa.Integer(), nullable=True),
        sa.Column("lag_days", sa.Integer(), nullable=True),
        sa.Column("beta", sa.Float(), nullable=True),
        sa.Column("p_value", sa.Float(), nullable=True),
        sa.Column("transfer_entropy", sa.Float(), nullable=True),
        sa.Column("method", sa.String(), nullable=True),
        sa.Column("regime", sa.String(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("sample_start", sa.Date(), nullable=True),
        sa.Column("sample_end", sa.Date(), nullable=True),
        sa.Column("evidence_count", sa.Integer(), nullable=True),
    )
    op.create_table(
        "evidence_links",
        sa.Column("link_id", sa.Integer(), primary_key=True),
        sa.Column(
            "factor_id",
            sa.Integer(),
            sa.ForeignKey("factors.factor_id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "edge_id",
            sa.Integer(),
            sa.ForeignKey("factor_edges.edge_id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("mongo_doc_id", sa.String(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=True),
    )
    op.create_table(
        "risk_metrics",
        sa.Column("entity_id", sa.String(), primary_key=True),
        sa.Column("metric", sa.String(), primary_key=True),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_table(
        "risk_snapshots",
        sa.Column(
            "factor_id",
            sa.Integer(),
            sa.ForeignKey("factors.factor_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("ts", sa.DateTime(timezone=True), primary_key=True),
        sa.Column("node_vol", sa.Float(), nullable=True),
        sa.Column("node_shock_sigma", sa.Float(), nullable=True),
        sa.Column("impact_pct", sa.Float(), nullable=True),
        sa.Column("systemic_contrib", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("risk_snapshots")
    op.drop_table("risk_metrics")
    op.drop_table("evidence_links")
    op.drop_table("factor_edges")
    op.drop_table("factors")
    op.drop_table("observations")
    op.drop_table("series")
