from sqladmin import ModelView

from app.model import User


class UserAdmin(ModelView, model=User):
    """Class for setting up the Admin panel for the User model"""

    # Metadata
    name = "User Model"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    # Permission
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True

    column_list = [
        User.id,
        User.email,
        User.username,
        User.phone,
        User.first_name,
        User.last_name,
        User.is_deleted,
        User.is_verified,
        User.created_at,
    ]
    column_searchable_list = [
        User.id,
        User.email,
        User.first_name,
        User.last_name,
        User.phone,
    ]
    column_sortable_list = [
        User.id,
        User.email,
        User.first_name,
        User.last_name,
        User.phone,
        User.is_verified,
        User.created_at,
        User.is_deleted,
    ]

    # Details
    column_details_list = [
        User.id,
        User.email,
        User.username,
        User.phone,
        User.is_deleted,
        User.is_verified,
        User.created_at,
    ]

    # Pagination
    page_size = 25
    page_size_options = [25, 50, 100, 200]
