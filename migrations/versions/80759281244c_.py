"""empty message

Revision ID: 80759281244c
Revises: 9dfb2c46291d
Create Date: 2023-06-13 16:32:57.635671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "80759281244c"
down_revision = "9dfb2c46291d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("jobs", "time", "formated_time")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("jobs", "formated_time", "time")
    # ### end Alembic commands ###
