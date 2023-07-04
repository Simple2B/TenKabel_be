"""empty message

Revision ID: 1e0914c9fd66
Revises: e7da53cf8928
Create Date: 2023-07-03 17:49:14.464678

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e0914c9fd66'
down_revision = 'e7da53cf8928'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('platform_payments', sa.Column('transaction_number', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('platform_payments', 'transaction_number')
    # ### end Alembic commands ###
