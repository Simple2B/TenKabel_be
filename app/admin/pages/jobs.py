from sqladmin import ModelView, action
from fastapi.responses import RedirectResponse

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

    @action(
        name="delete_job",
        label="Mark as deleted",
        add_in_detail=True,
        add_in_list=True,
    )
    async def delete_job(self, request) -> None:
        """set job.is_deleted to True and don't delete the job"""
        pks = request.query_params.get("pks", "").split(",")
        for pk in pks:
            model: Job = await self.get_object_for_edit(pk)
            model.is_deleted = True

        session = self.session_maker()
        session.add(model)
        session.commit()

        referer = request.headers.get("Referer")
        if referer:
            return RedirectResponse(referer)
        return RedirectResponse(request.url_for("admin:list", identity=self.identity))
