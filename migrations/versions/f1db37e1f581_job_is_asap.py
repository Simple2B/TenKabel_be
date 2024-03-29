"""job_is_asap

Revision ID: f1db37e1f581
Revises: a7237d02af08
Create Date: 2023-09-14 15:14:36.051211

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f1db37e1f581"
down_revision = "a7237d02af08"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("jobs", sa.Column("is_asap", sa.Boolean(), nullable=True))
    op.execute("UPDATE jobs SET is_asap = false")
    op.alter_column("jobs", "is_asap", nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("jobs", "is_asap")
    # ### end Alembic commands ###
