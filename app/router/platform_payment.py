import httpx
from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session

from app.dependency import get_current_user, get_job_by_uuid
import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db
from app.config import get_settings, Settings
from .platform_payment_utils import pay_plus_headers

payment_router = APIRouter(prefix="/payment", tags=["Payment"])


@payment_router.get(
    "/form-url/{job_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=s.PlatformPaymentLinkOut,
)
def get_url(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    user: m.User = Depends(get_current_user),
    job: m.Job = Depends(get_job_by_uuid),
):
    request_data: s.PlatformPaymentLinkIn = s.PlatformPaymentLinkIn(
        payment_page_uid=settings.PAY_PLUS_PAYMENT_PAGE_ID,
        amount=job.payment * 0.009 * 1.17,
        more_info_1=job.uuid,
        more_info_2=user.uuid,
    )
    try:
        response = httpx.post(
            f"{settings.PAY_PLUS_API_URL}/PaymentPages/generateLink",
            headers=pay_plus_headers(settings),
            json=request_data.dict(),
        )
    except httpx.RequestError as e:
        log(
            log.ERROR,
            "Error occured while sending request:\n%s",
            e,
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    except httpx.HTTPStatusError as e:
        log(
            log.ERROR,
            "Request failed:\n%s",
            e,
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return s.PlatformPaymentLinkOut(url=response["data"]["payment_page_link"])


@payment_router.get(
    "/webhook", status_code=status.HTTP_200_OK, response_model=s.PlatformPaymentLinkIn
)
def pay_platform_commission(
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    return
