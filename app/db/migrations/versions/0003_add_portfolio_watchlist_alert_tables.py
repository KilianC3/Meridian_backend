from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "portfolios",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_table(
        "portfolio_holdings",
        sa.Column(
            "portfolio_id",
            sa.UUID(),
            sa.ForeignKey("portfolios.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("symbol", sa.String(), primary_key=True),
        sa.Column("as_of", sa.Date(), primary_key=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("shares", sa.Float(), nullable=True),
    )
    op.create_table(
        "watchlists",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
    )
    op.create_table(
        "watchlist_items",
        sa.Column(
            "watchlist_id",
            sa.UUID(),
            sa.ForeignKey("watchlists.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("ref_id", sa.String(), primary_key=True),
        sa.Column("label", sa.String(), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
    )
    op.create_table(
        "alert_rules",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("rule_json", sa.JSON(), nullable=False),
        sa.Column(
            "enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column("cooldown_s", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_table(
        "alert_deliveries",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "rule_id",
            sa.UUID(),
            sa.ForeignKey("alert_rules.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("target", sa.String(), nullable=False),
        sa.Column("secret", sa.String(), nullable=True),
        sa.Column(
            "active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
    )
    op.create_table(
        "alert_events",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "rule_id",
            sa.UUID(),
            sa.ForeignKey("alert_rules.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "fired_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("dedupe_key", sa.String(), nullable=False),
        sa.Column(
            "delivered", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_error", sa.String(), nullable=True),
    )
    op.create_unique_constraint(
        "uq_alert_events_rule_dedupe",
        "alert_events",
        ["rule_id", "dedupe_key"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_alert_events_rule_dedupe", "alert_events", type_="unique")
    op.drop_table("alert_events")
    op.drop_table("alert_deliveries")
    op.drop_table("alert_rules")
    op.drop_table("watchlist_items")
    op.drop_table("watchlists")
    op.drop_table("portfolio_holdings")
    op.drop_table("portfolios")
