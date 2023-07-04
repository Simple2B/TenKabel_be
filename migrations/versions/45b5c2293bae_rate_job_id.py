"""rate_job_id

Revision ID: 45b5c2293bae
Revises: 75feeaf44f89
Create Date: 2023-07-04 09:26:50.899229

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "45b5c2293bae"
down_revision = "75feeaf44f89"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("rate", sa.Column("job_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        op.f("fk_rate_job_id_jobs"), "rate", "jobs", ["job_id"], ["id"]
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f("fk_rate_job_id_jobs"), "rate", type_="foreignkey")
    op.drop_column("rate", "job_id")
    # ### end Alembic commands ###
