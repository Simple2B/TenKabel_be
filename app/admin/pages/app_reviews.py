from sqladmin import ModelView

from app.model import AppReview


class RateAdmin(ModelView, model=AppReview):
    """Class for setting up the Admin panel for the User model"""

    # Metadata
    name = "App review"
    name_plural = "App reviews"
    icon = "fa-solid fa-star"
    # list_template: str = "list.html"
    # Permission
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True

    column_list = [
        AppReview.id,
        AppReview.stars_count,
        AppReview.user,
        AppReview.review,
        AppReview.created_at,
    ]
    column_searchable_list = [
        AppReview.id,
        AppReview.stars_count,
        AppReview.review,
        AppReview.created_at,
    ]
    column_sortable_list = [
        AppReview.id,
        AppReview.stars_count,
        AppReview.user_id,
        AppReview.review,
        AppReview.created_at,
    ]

    # Details
    column_details_list = []

    # Pagination
    page_size = 25
    page_size_options = [25, 50, 100, 200]
