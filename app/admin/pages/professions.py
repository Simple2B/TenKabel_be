from sqladmin import ModelView, action
from fastapi.responses import RedirectResponse

from app.model import Profession


class ProfessionAdmin(ModelView, model=Profession):
    """Class for setting up the Admin panel for the User model"""

    # Metadata
    name = "Profession"
    name_plural = "Professions"
    icon = "fa-solid fa-user-tie"

    # Permission
    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True

    column_list = [
        Profession.id,
        Profession.name_en,
        Profession.name_hebrew,
        Profession.is_deleted,
    ]
    column_searchable_list = [
        Profession.id,
        Profession.name_en,
        Profession.name_hebrew,
    ]
    column_sortable_list = [
        Profession.id,
        Profession.name_en,
        Profession.name_hebrew,
    ]

    # Details
    column_details_list = [
        Profession.name_en,
        Profession.name_hebrew,
        Profession.is_deleted,
    ]
    form_columns = [
        Profession.name_en,
        Profession.name_hebrew,
    ]
    # Pagination
    page_size = 25
    page_size_options = [25, 50, 100, 200]

    @action(
        name="delete_profession",
        label="Mark as deleted",
        add_in_detail=True,
        add_in_list=True,
    )
    async def delete_profession(self, request) -> None:
        """set profession.is_deleted to True and don't delete the profession"""
        pks = request.query_params.get("pks", "").split(",")
        for pk in pks:
            model: Profession = await self.get_object_for_edit(pk)
            model.is_deleted = True

        session = self.session_maker()
        session.add(model)
        session.commit()

        referer = request.headers.get("Referer")
        if referer:
            return RedirectResponse(referer)
        return RedirectResponse(request.url_for("admin:list", identity=self.identity))
