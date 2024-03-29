"""empty message

Revision ID: 5610196a54b9
Revises: 2d664ed19f64
Create Date: 2023-08-30 15:38:11.112302

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "5610196a54b9"
down_revision = "2d664ed19f64"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f("ix_applications_uuid"), "applications", ["uuid"], unique=True)
    op.create_index(op.f("ix_jobs_uuid"), "jobs", ["uuid"], unique=True)
    op.create_unique_constraint(op.f("uq_locations_uuid"), "locations", ["uuid"])
    op.create_unique_constraint(
        op.f("uq_notifications_uuid"), "notifications", ["uuid"]
    )
    op.create_unique_constraint(
        op.f("uq_platform_commissions_uuid"), "platform_commissions", ["uuid"]
    )
    op.create_unique_constraint(
        op.f("uq_platform_payments_uuid"), "platform_payments", ["uuid"]
    )
    op.create_unique_constraint(op.f("uq_professions_uuid"), "professions", ["uuid"])
    op.create_unique_constraint(op.f("uq_rate_uuid"), "rate", ["uuid"])
    op.drop_constraint("uq_superusers_email", "superusers", type_="unique")
    op.create_index(op.f("ix_superusers_email"), "superusers", ["email"], unique=True)
    op.create_unique_constraint(op.f("uq_superusers_uuid"), "superusers", ["uuid"])
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_unique_constraint(op.f("uq_users_uuid"), "users", ["uuid"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f("uq_users_uuid"), "users", type_="unique")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.drop_constraint(op.f("uq_superusers_uuid"), "superusers", type_="unique")
    op.drop_index(op.f("ix_superusers_email"), table_name="superusers")
    op.create_unique_constraint("uq_superusers_email", "superusers", ["email"])
    op.drop_constraint(op.f("uq_rate_uuid"), "rate", type_="unique")
    op.drop_constraint(op.f("uq_professions_uuid"), "professions", type_="unique")
    op.drop_constraint(
        op.f("uq_platform_payments_uuid"), "platform_payments", type_="unique"
    )
    op.drop_constraint(
        op.f("uq_platform_commissions_uuid"), "platform_commissions", type_="unique"
    )
    op.drop_constraint(op.f("uq_notifications_uuid"), "notifications", type_="unique")
    op.drop_constraint(op.f("uq_locations_uuid"), "locations", type_="unique")
    op.drop_index(op.f("ix_jobs_uuid"), table_name="jobs")
    op.drop_index(op.f("ix_applications_uuid"), table_name="applications")
    # ### end Alembic commands ###
