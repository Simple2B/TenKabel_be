"""empty message

Revision ID: f0ed80cb9b75
Revises: 988a940a67e2
Create Date: 2023-05-31 15:05:31.870527

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f0ed80cb9b75"
down_revision = "988a940a67e2"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("uq_superusers_username", "superusers", type_="unique")
    op.drop_constraint("uq_users_username", "users", type_="unique")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint("uq_users_username", "users", ["username"])
    op.create_unique_constraint("uq_superusers_username", "superusers", ["username"])
    # ### end Alembic commands ###
