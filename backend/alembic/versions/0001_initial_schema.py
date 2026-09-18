"""Initial schema: boards, tasks, and the triggers that guard soft delete

Revision ID: 0001
Revises:
Create Date: 2026-09-18
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


BLOCK_TRASH_BOARD_FUNCTION = """
CREATE FUNCTION block_trash_board_with_active_tasks() RETURNS trigger AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM tasks
        WHERE board_id = NEW.id AND deleted_at IS NULL
    ) THEN
        RAISE EXCEPTION 'board % still has active tasks', NEW.id
            USING ERRCODE = 'restrict_violation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

BLOCK_TASK_ON_TRASHED_BOARD_FUNCTION = """
CREATE FUNCTION block_active_task_on_trashed_board() RETURNS trigger AS $$
DECLARE
    board_deleted_at timestamptz;
BEGIN
    SELECT deleted_at INTO board_deleted_at
    FROM boards WHERE id = NEW.board_id FOR SHARE;

    IF board_deleted_at IS NOT NULL THEN
        RAISE EXCEPTION 'board % is in trash', NEW.board_id
            USING ERRCODE = 'restrict_violation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    op.create_table(
        "boards",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(r"name ~ '\S'", name="name_not_blank"),
        sa.PrimaryKeyConstraint("id", name="pk_boards"),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_boards_name_active ON boards (lower(name)) "
        "WHERE deleted_at IS NULL"
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("board_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.String(length=20), server_default=sa.text("'TODO'"), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(r"title ~ '\S'", name="title_not_blank"),
        sa.CheckConstraint(
            "status IN ('TODO', 'IN_PROGRESS', 'DONE')", name="status_valid"
        ),
        sa.ForeignKeyConstraint(
            ["board_id"],
            ["boards.id"],
            name="fk_tasks_board_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_tasks"),
    )
    op.create_index("ix_tasks_board_id_status", "tasks", ["board_id", "status"])

    op.execute(BLOCK_TRASH_BOARD_FUNCTION)
    op.execute(
        """
        CREATE TRIGGER trg_boards_block_trash_with_active_tasks
        BEFORE UPDATE OF deleted_at ON boards
        FOR EACH ROW
        WHEN (OLD.deleted_at IS NULL AND NEW.deleted_at IS NOT NULL)
        EXECUTE FUNCTION block_trash_board_with_active_tasks();
        """
    )

    op.execute(BLOCK_TASK_ON_TRASHED_BOARD_FUNCTION)
    op.execute(
        """
        CREATE TRIGGER trg_tasks_block_inactive_board
        BEFORE INSERT OR UPDATE OF board_id, deleted_at ON tasks
        FOR EACH ROW
        WHEN (NEW.deleted_at IS NULL)
        EXECUTE FUNCTION block_active_task_on_trashed_board();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_tasks_block_inactive_board ON tasks")
    op.execute("DROP FUNCTION IF EXISTS block_active_task_on_trashed_board()")
    op.execute("DROP TRIGGER IF EXISTS trg_boards_block_trash_with_active_tasks ON boards")
    op.execute("DROP FUNCTION IF EXISTS block_trash_board_with_active_tasks()")
    op.drop_index("ix_tasks_board_id_status", table_name="tasks")
    op.drop_table("tasks")
    op.execute("DROP INDEX IF EXISTS uq_boards_name_active")
    op.drop_table("boards")
