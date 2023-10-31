from sqladmin import ModelView

from app.model import Profession


class ProfessionsAdmin(ModelView, model=Profession):
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
    ]
    form_columns = [
        Profession.name_en,
        Profession.name_hebrew,
    ]
    # Pagination
    page_size = 25
    page_size_options = [25, 50, 100, 200]
