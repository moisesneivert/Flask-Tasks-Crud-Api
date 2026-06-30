"""Create tasks table.

Revision ID: 20260630_0001
Revises:
Create Date: 2026-06-30 15:00:00
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260630_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.String(length=10), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="ck_tasks_priority",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed')",
            name="ck_tasks_status",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.create_index(batch_op.f("ix_tasks_due_date"), ["due_date"], unique=False)
        batch_op.create_index(batch_op.f("ix_tasks_priority"), ["priority"], unique=False)
        batch_op.create_index(batch_op.f("ix_tasks_status"), ["status"], unique=False)
        batch_op.create_index(batch_op.f("ix_tasks_title"), ["title"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.drop_index(batch_op.f("ix_tasks_title"))
        batch_op.drop_index(batch_op.f("ix_tasks_status"))
        batch_op.drop_index(batch_op.f("ix_tasks_priority"))
        batch_op.drop_index(batch_op.f("ix_tasks_due_date"))
    op.drop_table("tasks")
