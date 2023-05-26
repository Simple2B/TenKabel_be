"""empty message

Revision ID: f594f652107d
Revises: da7dfc8632c7
Create Date: 2023-05-26 17:28:13.933407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f594f652107d"
down_revision = "da7dfc8632c7"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "users", "phone", existing_type=sa.VARCHAR(length=128), nullable=True
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "users", "phone", existing_type=sa.VARCHAR(length=128), nullable=False
    )
    # ### end Alembic commands ###
