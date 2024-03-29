"""empty message

Revision ID: b1af44a0d0ec
Revises: 325132677a15
Create Date: 2023-10-24 17:10:35.588944

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b1af44a0d0ec"
down_revision = "325132677a15"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE TYPE commissionsymbol AS ENUM ('PERCENT', 'SHEKEL')")
    op.add_column(
        "jobs",
        sa.Column(
            "commission_symbol",
            sa.Enum("PERCENT", "SHEKEL", name="commissionsymbol", schema="public"),
            server_default="PERCENT",
        ),
    )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("jobs", "commission_symbol")
    # ### end Alembic commands ###
