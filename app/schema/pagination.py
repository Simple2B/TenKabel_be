from pydantic import BaseModel


class Pagination(BaseModel):
    """Pagination data"""

    page: int  # current page number
    total: int  # total items
    query: BaseModel | None  # query string
    per_page: int  # number items on the page
    skip: int  # number items on all previous pages
    pages: int  # total pages
