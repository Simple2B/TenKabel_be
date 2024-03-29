"""jobs_status_time

Revision ID: b6c87bbdd04d
Revises: 8af58fc33c5d
Create Date: 2023-09-18 16:29:03.690966

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b6c87bbdd04d"
down_revision = "15c918b416f4"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("jobs", sa.Column("pending_at", sa.DateTime(), nullable=True))
    op.add_column("jobs", sa.Column("approved_at", sa.DateTime(), nullable=True))
    op.add_column("jobs", sa.Column("in_progress_at", sa.DateTime(), nullable=True))
    op.add_column("jobs", sa.Column("job_is_finished_at", sa.DateTime(), nullable=True))
    op.add_column("jobs", sa.Column("payment_unpaid_at", sa.DateTime(), nullable=True))
    op.add_column("jobs", sa.Column("payment_paid_at", sa.DateTime(), nullable=True))
    op.add_column("jobs", sa.Column("commission_sent_at", sa.DateTime(), nullable=True))
    op.add_column(
        "jobs", sa.Column("commission_confirmation_at", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "jobs", sa.Column("commission_denied_at", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "jobs", sa.Column("commission_approved_at", sa.DateTime(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("jobs", "commission_approved_at")
    op.drop_column("jobs", "commission_denied_at")
    op.drop_column("jobs", "commission_confirmation_at")
    op.drop_column("jobs", "commission_sent_at")
    op.drop_column("jobs", "payment_paid_at")
    op.drop_column("jobs", "payment_unpaid_at")
    op.drop_column("jobs", "job_is_finished_at")
    op.drop_column("jobs", "in_progress_at")
    op.drop_column("jobs", "approved_at")
    op.drop_column("jobs", "pending_at")
    # ### end Alembic commands ###
