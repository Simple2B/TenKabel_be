# flake8: noqa F401
from fastapi import APIRouter, Request

from .auth import auth_router
from .user import user_router
from .job import job_router
from .profession import profession_router
from .location import location_router
from .whoami import whoami_router
from .rate import rate_router
from .application import application_router
from .device import device_router
from .notification import notification_router
from .platform_payment import payment_router
from .option import options_router
from .attachment import attachment_router
from .file import file_router
from .review import review_router
from .tag import tag_router
from .app_review import app_review_router

# from .notify import notification_test_router


router = APIRouter(prefix="/api", tags=["API"])

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(job_router)
router.include_router(profession_router)
router.include_router(location_router)
router.include_router(whoami_router)
router.include_router(rate_router)
router.include_router(application_router)
router.include_router(device_router)
router.include_router(notification_router)
router.include_router(payment_router)
router.include_router(options_router)
router.include_router(attachment_router)
router.include_router(file_router)
router.include_router(review_router)
router.include_router(tag_router)
router.include_router(app_review_router)


@router.get("/list-endpoints/")
def list_endpoints(request: Request):
    url_list = [
        {"path": route.path, "name": route.name} for route in request.app.routes
    ]
    return url_list
