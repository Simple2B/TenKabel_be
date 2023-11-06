from sqladmin import ModelView

from app.model import Job


class JobAdmin(ModelView, model=Job):
    """Class for setting up the Admin panel for the User model"""

    # Metadata
    name = "Job"
    name_plural = "Jobs"
    icon = "fa-solid fa-briefcase"

    # Permission
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True

    column_list = [
        Job.id,
        Job.name,
        Job.description,
        Job.owner,
        Job.worker,
        Job.profession,
        Job.status,
        Job.city,
        Job.formatted_time,
        Job.is_asap,
        Job.frame_time,
        Job.payment_status,
        Job.commission_status,
        Job.who_pays,
        Job.created_at,
        Job.is_deleted,
    ]
    column_searchable_list = [
        Job.id,
        Job.name,
        Job.description,
        Job.status,
        Job.customer_first_name,
        Job.customer_last_name,
        Job.customer_phone,
        Job.customer_street_address,
        Job.city,
    ]
    column_sortable_list = []

    # Details
    column_details_list = [
        Job.id,
        Job.name,
        Job.description,
        Job.owner,
        Job.worker,
        Job.profession,
        Job.status,
        Job.customer_first_name,
        Job.customer_last_name,
        Job.customer_phone,
        Job.customer_street_address,
        Job.payment,
        Job.commission,
        Job.commission_symbol,
        Job.city,
        Job.formatted_time,
        Job.is_asap,
        Job.frame_time,
        Job.payment_status,
        Job.commission_status,
        Job.who_pays,
        Job.created_at,
        Job.is_deleted,
    ]

    # Pagination
    page_size = 25
    page_size_options = [25, 50, 100, 200]
