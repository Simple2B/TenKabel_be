"""job_status

Revision ID: 3169bfc78721
Revises: d4fa2e9e3520
Create Date: 2023-09-21 15:08:37.652864

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "3169bfc78721"
down_revision = "d4fa2e9e3520"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    job_status = sa.dialects.postgresql.ENUM(
        "PENDING",
        "APPROVED",
        "IN_PROGRESS",
        "JOB_IS_FINISHED",
        name="jobstatus",
        create_type=False,
    )
    op.create_table(
        "job_statuses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            job_status,
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], name=op.f("fk_job_statuses_job_id_jobs")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job_statuses")),
    )
    op.create_index(op.f("ix_job_statuses_uuid"), "job_statuses", ["uuid"], unique=True)
    op.drop_column("jobs", "job_is_finished_at")
    op.drop_column("jobs", "in_progress_at")
    op.drop_column("jobs", "pending_at")
    op.drop_column("jobs", "approved_at")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "jobs",
        sa.Column(
            "approved_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "jobs",
        sa.Column(
            "pending_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "jobs",
        sa.Column(
            "in_progress_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "jobs",
        sa.Column(
            "job_is_finished_at",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_index(op.f("ix_job_statuses_uuid"), table_name="job_statuses")
    op.drop_table("job_statuses")
    # ### end Alembic commands ###
