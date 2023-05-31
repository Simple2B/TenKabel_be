"""empty message

Revision ID: 988a940a67e2
Revises: 32d3398aa9c1
Create Date: 2023-05-31 14:58:36.733845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "988a940a67e2"
down_revision = "32d3398aa9c1"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("worker_id", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "ACCEPTED", "DECLINED", name="status"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], name=op.f("fk_applications_job_id_jobs")
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["users.id"], name=op.f("fk_applications_owner_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["worker_id"], ["users.id"], name=op.f("fk_applications_worker_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_applications")),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("applications")
    # ### end Alembic commands ###
