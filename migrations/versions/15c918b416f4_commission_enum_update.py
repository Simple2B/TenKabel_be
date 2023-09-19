"""commission_enum_update

Revision ID: 15c918b416f4
Revises: 8af58fc33c5d
Create Date: 2023-09-19 14:14:02.719644

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "15c918b416f4"
down_revision = "8af58fc33c5d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TYPE commissionstatus ADD VALUE 'SENT' AFTER 'PAID';")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    """remove from commissionstatus enum values: DENY, CONFIRM, REQUESTED"""
    op.execute("ALTER TYPE commissionstatus RENAME TO sommissionstatus_old")
    op.execute(
        "CREATE TYPE commissionstatus AS ENUM ('REQUESTED', 'UNPAID', 'DENY', 'CONFIRM', 'PAID')"
    )
    op.execute(
        "ALTER TABLE job ALTER COLUMN commission_status TYPE commissionstatus USING commission_status::text::commissionstatus"
    )
    op.execute("DROP TYPE commissionstatus_old")
    # ### end Alembic commands ###
