import json

import httpx
from fastapi import Depends, APIRouter, status, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from app.dependency import get_current_user, get_job_by_uuid
import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db
from app.config import get_settings, Settings
from app.utility.platform_payment_utils import pay_plus_headers

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
    if db.scalars(
        select(m.PlatformPayment).where(
            m.PlatformPayment.job_id == job.id,
            m.PlatformPayment.user_id == user.id,
            m.PlatformPayment.status == s.enums.PlatformPaymentStatus.PAID,
        )
    ):
        log(log.INFO, "Job [%s] has already been paid", job.uuid)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job has already been paid",
        )
    request_data: s.PlatformPaymentLinkIn = s.PlatformPaymentLinkIn(
        payment_page_uid=settings.PAY_PLUS_PAYMENT_PAGE_ID,
        amount=job.payment * 0.009 * 1.17,
        more_info_1=json.dumps(
            dict(
                user_uuid=user.uuid,
                job_uuid=job.uuid,
            )
        ),
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

    return s.PlatformPaymentLinkOut(url=response.json()["data"]["payment_page_link"])


@payment_router.post("/webhook", status_code=status.HTTP_200_OK)
async def pay_platform_commission(
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        request_data = await request.json()
    except json.JSONDecodeError as e:
        log(log.ERROR, "Bad request data:\n%s", e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Not valid data",
        )
    if request_data.get("transaction_type") == "Charge":
        log(log.INFO, "transaction_type is  Charge")
        transaction = request_data["transaction"]
        status_code = transaction.get("status_code")
        log(log.INFO, "Status code [%s]", status_code)
        user_uuid: str = json.loads(transaction["more_info_1"])["user_uuid"]
        user: m.User | None = db.scalar(select(m.User).where(m.User.uuid == user_uuid))
        if not user:
            log(log.ERROR, "User [%s] was not found", user_uuid)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User was not found"
            )
        job_uuid: str = json.loads(transaction["more_info_1"])["job_uuid"]
        job: m.Job | None = db.scalar(select(m.Job).where(m.Job.uuid == job_uuid))
        if not job:
            log(log.ERROR, "Job [%s] was not found", job_uuid)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Job was not found"
            )
        payment = m.PlatformPayment(
            user_id=user.id, job_id=job.id, status=s.enums.PlatformPaymentStatus.PAID
        )
        db.add(payment)
        try:
            db.commit()
        except SQLAlchemyError as e:
            log(log.ERROR, "Error while storing payment details %s", e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error while storing payment details",
            )
        log(
            log.INFO,
            "Payment details has been successfully stored - [%s]",
            payment.uuid,
        )
