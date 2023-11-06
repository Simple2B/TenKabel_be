"""regions

Revision ID: 2d664ed19f64
Revises: eb42b5cfec2c
Create Date: 2023-07-21 11:36:57.385264

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2d664ed19f64"
down_revision = "eb42b5cfec2c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("jobs", sa.Column("region", sa.String(length=64), nullable=True))
    # ### end Alembic commands ###
    op.execute("UPDATE jobs SET region = city")
    op.alter_column("jobs", "region", nullable=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("jobs", "region")
    # ### end Alembic commands ###
