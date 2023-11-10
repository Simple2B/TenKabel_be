"""job_frame_time

Revision ID: a7237d02af08
Revises: 563d3e4f8ef0
Create Date: 2023-09-14 14:58:35.266399

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a7237d02af08"
down_revision = "563d3e4f8ef0"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("jobs", sa.Column("frame_time", sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("jobs", "frame_time")
    # ### end Alembic commands ###
