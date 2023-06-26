from fastapi import Depends, APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependency import get_current_user
import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db
from app.config import get_settings, Settings


# TERMINAL_ID = settings.PAY_PLUS_TERMINAL_ID
# CASHIERS_ID = settings.PAY_PLUS_CASHIERS_ID
# PAYMENT_PAGE_ID = settings.PAY_PLUS_PAYMENT_PAGE_ID


payment_router = APIRouter(prefix="/payment", tags=["Payment"])


@payment_router.get(
    "/form-url/{job_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=s.PlatformPaymentLinkOut,
)
def get_url(
    job_uuid: str,
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    job: m.Job | None = db.scalars(select(m.Job).where(m.Job.uuid == job_uuid)).first()

    request_data: s.PlatformPaymentLinkIn = {}
    return


@payment_router.get(
    "/webhook", status_code=status.HTTP_200_OK, response_model=s.PlatformPaymentLinkIn
)
def pay_platform_commission(
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    return
