from app import schema as s
from app.config import get_settings, Settings

settings: Settings = get_settings()


def create_pagination(total: int, page_size: int = 0, page: int = 1) -> s.Pagination:
    """create instance Pagination for current request"""
    page_size = page_size or settings.DEFAULT_PAGE_SIZE
    pages = total // page_size + 1 if total % page_size else total // page_size

    return s.Pagination(
        # items=query
        page=page,
        pages=pages,
        total=total,
        per_page=page_size,
        skip=(page - 1) * page_size,
    )
