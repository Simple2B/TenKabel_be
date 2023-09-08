"""init

Revision ID: 07aad891086b
Revises: 
Create Date: 2023-07-04 16:35:16.813510

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "07aad891086b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("name_en", sa.String(length=64), nullable=False),
        sa.Column("name_hebrew", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_locations")),
    )
    op.create_table(
        "professions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("name_en", sa.String(length=64), nullable=False),
        sa.Column("name_hebrew", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_professions")),
    )
    op.create_table(
        "superusers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=128), nullable=True),
        sa.Column("username", sa.String(length=128), nullable=False),
        sa.Column("google_openid_key", sa.String(length=64), nullable=True),
        sa.Column("picture", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("country_code", sa.String(length=32), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_superusers")),
        sa.UniqueConstraint("email", name=op.f("uq_superusers_email")),
    )
    op.create_table(
        "users",
        sa.Column("phone", sa.String(length=128), nullable=True),
        sa.Column("first_name", sa.String(length=64), nullable=False),
        sa.Column("last_name", sa.String(length=64), nullable=False),
        sa.Column("notification_profession_flag", sa.Boolean(), nullable=False),
        sa.Column("notification_locations_flag", sa.Boolean(), nullable=False),
        sa.Column("notification_job_status", sa.Boolean(), nullable=False),
        sa.Column("payplus_customer_uid", sa.String(length=36), nullable=True),
        sa.Column("payplus_card_uid", sa.String(length=64), nullable=True),
        sa.Column("card_name", sa.String(length=64), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=128), nullable=True),
        sa.Column("username", sa.String(length=128), nullable=False),
        sa.Column("google_openid_key", sa.String(length=64), nullable=True),
        sa.Column("picture", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("country_code", sa.String(length=32), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("payplus_card_uid", name=op.f("uq_users_payplus_card_uid")),
        sa.UniqueConstraint("phone", name=op.f("uq_users_phone")),
    )
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("push_token", sa.String(length=256), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_devices_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_devices")),
        sa.UniqueConstraint("uuid", name=op.f("uq_devices_uuid")),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("worker_id", sa.Integer(), nullable=True),
        sa.Column("profession_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "APPROVED",
                "IN_PROGRESS",
                "JOB_IS_FINISHED",
                name="jobstatus",
            ),
            nullable=False,
        ),
        sa.Column("customer_first_name", sa.String(length=64), nullable=False),
        sa.Column("customer_last_name", sa.String(length=64), nullable=False),
        sa.Column("customer_phone", sa.String(length=64), nullable=False),
        sa.Column("customer_street_address", sa.String(length=128), nullable=False),
        sa.Column("payment", sa.Integer(), nullable=False),
        sa.Column("commission", sa.Float(), nullable=False),
        sa.Column("city", sa.String(length=64), nullable=False),
        sa.Column("formatted_time", sa.String(length=64), nullable=False),
        sa.Column(
            "payment_status",
            sa.Enum("PAID", "UNPAID", name="paymentstatus"),
            nullable=False,
        ),
        sa.Column(
            "commission_status",
            sa.Enum(
                "paid",
                "unpaid",
                "requested",
                "deny",
                "confirm",
                name="commissionstatus",
            ),
            nullable=False,
        ),
        sa.Column("who_pays", sa.Enum("ME", "CLIENT", name="whopays"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["users.id"], name=op.f("fk_jobs_owner_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["profession_id"],
            ["professions.id"],
            name=op.f("fk_jobs_profession_id_professions"),
        ),
        sa.ForeignKeyConstraint(
            ["worker_id"], ["users.id"], name=op.f("fk_jobs_worker_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_jobs")),
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "JOB_CREATED",
                "JOB_STARTED",
                "JOB_DONE",
                "JOB_CANCELED",
                "JOB_PAID",
                "COMMISSION_REQUESTED",
                "COMMISSION_PAID",
                "MAX_JOB_TYPE",
                "APPLICATION_CREATED",
                "APPLICATION_ACCEPTED",
                "APPLICATION_REJECTED",
                "MAX_APPLICATION_TYPE",
                name="notificationtype",
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_notifications_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notifications")),
    )
    op.create_table(
        "platform_payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("transaction_number", sa.String(length=64), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PAID", "UNPAID", "REJECTED", "PROGRESS", name="platformpaymentstatus"
            ),
            nullable=False,
        ),
        sa.Column("reject_reason", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_platform_payments_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_platform_payments")),
    )
    op.create_table(
        "users_locations",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
            name=op.f("fk_users_locations_location_id_locations"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_users_locations_user_id_users")
        ),
        sa.PrimaryKeyConstraint(
            "user_id", "location_id", name=op.f("pk_users_locations")
        ),
    )
    op.create_table(
        "users_notifications_locations",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
            name=op.f("fk_users_notifications_locations_location_id_locations"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_users_notifications_locations_user_id_users"),
        ),
        sa.PrimaryKeyConstraint(
            "user_id", "location_id", name=op.f("pk_users_notifications_locations")
        ),
    )
    op.create_table(
        "users_notifications_professions",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("profession_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["profession_id"],
            ["professions.id"],
            name=op.f("fk_users_notifications_professions_profession_id_professions"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_users_notifications_professions_user_id_users"),
        ),
        sa.PrimaryKeyConstraint(
            "user_id", "profession_id", name=op.f("pk_users_notifications_professions")
        ),
    )
    op.create_table(
        "users_professions",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("profession_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["profession_id"],
            ["professions.id"],
            name=op.f("fk_users_professions_profession_id_professions"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_users_professions_user_id_users")
        ),
        sa.PrimaryKeyConstraint(
            "user_id", "profession_id", name=op.f("pk_users_professions")
        ),
    )
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("worker_id", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "ACCEPTED", "DECLINED", name="applicationstatus"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("status_changed_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], name=op.f("fk_applications_job_id_jobs")
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["users.id"], name=op.f("fk_applications_owner_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["worker_id"], ["users.id"], name=op.f("fk_applications_worker_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_applications")),
    )
    op.create_table(
        "platform_commissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("platform_payment_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], name=op.f("fk_platform_commissions_job_id_jobs")
        ),
        sa.ForeignKeyConstraint(
            ["platform_payment_id"],
            ["platform_payments.id"],
            name=op.f("fk_platform_commissions_platform_payment_id_platform_payments"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_platform_commissions_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_platform_commissions")),
    )
    op.create_table(
        "rate",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("worker_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column(
            "rate",
            sa.Enum("POSITIVE", "NEGATIVE", "NEUTRAL", name="ratestatus"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], name=op.f("fk_rate_job_id_jobs")
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["users.id"], name=op.f("fk_rate_owner_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["worker_id"], ["users.id"], name=op.f("fk_rate_worker_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rate")),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("rate")
    op.drop_table("platform_commissions")
    op.drop_table("applications")
    op.drop_table("users_professions")
    op.drop_table("users_notifications_professions")
    op.drop_table("users_notifications_locations")
    op.drop_table("users_locations")
    op.drop_table("platform_payments")
    op.drop_table("notifications")
    op.drop_table("jobs")
    op.drop_table("devices")
    op.drop_table("users")
    op.drop_table("superusers")
    op.drop_table("professions")
    op.drop_table("locations")
    # ### end Alembic commands ###
