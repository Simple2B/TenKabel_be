import httpx
from fastapi import Depends, APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependency import get_current_user, get_job_by_uuid
import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db
from app.config import get_settings, Settings
from .platform_payment_utils import pay_plus_headers


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
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    user: m.User = Depends(get_current_user),
    job: m.Job = Depends(get_job_by_uuid),
):
    # /PaymentPages/generateLink
    request_data: s.PlatformPaymentLinkIn = s.PlatformPaymentLinkIn(
        payment_page_uid=settings.PAY_PLUS_PAYMENT_PAGE_ID,
        amount=job.payment * 0.009 * 1.17,
        # refURL_success: str | None
        # refURL_failure: str | None
        # refURL_cancel: str | None
        # refURL_callback: str | None
        more_info_1=job.uuid,
        more_info_2=user.uuid,
    )

    try:
        # Send a POST request with headers and JSON payload
        response = httpx.post(
            f"{settings.PAY_PLUS_API_URL}/PaymentPages/generateLink",
            headers=pay_plus_headers(),
            json=request_data.dict(),
        )

        # Check the response status code
        if response.status_code == 200:
            print("Request was successful!")
        else:
            print(f"Request failed with status code: {response.status_code}")

        # Print the response content
        print(response.text)

    except httpx.RequestError as e:
        print(f"An error occurred while sending the request: {str(e)}")

    except httpx.HTTPStatusError as e:
        print(f"Request failed with HTTP status code: {e.response.status_code}")
        print(f"Response content: {e.response.text}")

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


@payment_router.get(
    "/webhook", status_code=status.HTTP_200_OK, response_model=s.PlatformPaymentLinkIn
)
def pay_platform_commission(
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    return
