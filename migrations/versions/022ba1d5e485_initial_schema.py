"""create initial LMS schema

Revision ID: 022ba1d5e485
Revises:
Create Date: 2026-09-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "022ba1d5e485"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["teacher_id"], ["users.id"], name="fk_courses_teacher_id_users"),
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name="fk_subscriptions_student_id_users",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            name="fk_subscriptions_course_id_courses",
            ondelete="RESTRICT",
        ),
    )

    op.create_index(
        "uq_active_subscription_student_course",
        "subscriptions",
        ["student_id", "course_id"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )


def downgrade() -> None:
    op.drop_index("uq_active_subscription_student_course", table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_table("courses")
    op.drop_table("users")