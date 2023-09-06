"""job_location

Revision ID: 9b0757283a5b
Revises: 3a29707fb19e
Create Date: 2023-09-06 12:21:10.375460

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9b0757283a5b"
down_revision = "3a29707fb19e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "jobs_locations",
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], name=op.f("fk_jobs_locations_job_id_jobs")
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
            name=op.f("fk_jobs_locations_location_id_locations"),
        ),
        sa.PrimaryKeyConstraint(
            "job_id", "location_id", name=op.f("pk_jobs_locations")
        ),
    )
    op.drop_column("jobs", "region")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "jobs",
        sa.Column("region", sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    )
    op.drop_table("jobs_locations")
    # ### end Alembic commands ###
