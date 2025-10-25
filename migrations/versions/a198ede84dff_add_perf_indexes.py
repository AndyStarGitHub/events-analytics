from alembic import op

revision = "a198ede84dff"
down_revision = "db1fd24928c7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE INDEX IF NOT EXISTS ix_events_occurred_at_brin ON events USING BRIN (occurred_at)")
    op.create_index("ix_events_event_type", "events", ["event_type"], unique=False, if_not_exists=True)
    op.create_index("ix_events_user_id", "events", ["user_id"], unique=False, if_not_exists=True)

def downgrade() -> None:
    op.drop_index("ix_events_user_id", table_name="events", if_exists=True)
    op.drop_index("ix_events_event_type", table_name="events", if_exists=True)
    op.execute("DROP INDEX IF EXISTS ix_events_occurred_at_brin")
