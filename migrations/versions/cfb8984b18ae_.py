"""empty message

Revision ID: cfb8984b18ae
Revises: 50550206c693
Create Date: 2023-10-31 15:00:55.300989

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cfb8984b18ae"
down_revision = "50550206c693"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("superusers", sa.Column("last_login", sa.DateTime(), nullable=True))
    op.drop_column("superusers", "is_deleted")
    op.drop_column("superusers", "is_verified")
    op.drop_column("superusers", "picture")
    op.drop_column("superusers", "google_openid_key")
    op.drop_column("superusers", "country_code")
    op.drop_column("superusers", "apple_uid")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "superusers",
        sa.Column(
            "apple_uid", sa.VARCHAR(length=64), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "superusers",
        sa.Column(
            "country_code", sa.VARCHAR(length=32), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "superusers",
        sa.Column(
            "google_openid_key",
            sa.VARCHAR(length=64),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "superusers",
        sa.Column("picture", sa.TEXT(), autoincrement=False, nullable=False),
    )
    op.add_column(
        "superusers",
        sa.Column("is_verified", sa.BOOLEAN(), autoincrement=False, nullable=False),
    )
    op.add_column(
        "superusers",
        sa.Column("is_deleted", sa.BOOLEAN(), autoincrement=False, nullable=False),
    )
    op.drop_column("superusers", "last_login")
    # ### end Alembic commands ###
