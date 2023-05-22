# flake8: noqa F401
from fastapi import APIRouter, Request

from .auth import auth_router
from .user import user_router
from .job import job_router
from .profession import profession_router
from .location import location_router


router = APIRouter(prefix="/api", tags=["API"])

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(job_router)
router.include_router(profession_router)
router.include_router(location_router)


@router.get("/list-endpoints/")
def list_endpoints(request: Request):
    url_list = [
        {"path": route.path, "name": route.name} for route in request.app.routes
    ]
    return url_list
