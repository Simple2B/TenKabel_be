# flake8: noqa
from datetime import datetime

from fastapi import status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import app.model as m
import app.schema as s
from app.logger import log


def create_platform_payment(
    db: Session,
    user_id: int,
) -> m.PlatformPayment:
    # getting weekly platform payment
    unpaid_platform_payment: m.PlatformPayment = db.scalar(
        select(m.PlatformPayment).where(
            m.PlatformPayment.status == s.enums.PlatformPaymentStatus.UNPAID,
            m.PlatformPayment.user_id == user_id,
        )
    )
    if not unpaid_platform_payment:
        log(log.INFO, "Creating weekly platform payment for upcoming week")
        unpaid_platform_payment = m.PlatformPayment(user_id=user_id)
        db.add(unpaid_platform_payment)
        try:
            db.commit()
            db.refresh(unpaid_platform_payment)
        except SQLAlchemyError as e:
            log(log.ERROR, "Error while creating weekly platform payment - \n[%s]", e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error while creating weekly platform payment",
            )
        log(
            log.INFO,
            "Weekly platform - [%s] payment created successfully",
            unpaid_platform_payment.id,
        )
    return unpaid_platform_payment


def create_platform_comission(
    db: Session,
    platform_payment: m.PlatformPayment,
    user_id: int,
    job_id: int,
) -> m.PlatformComission:
    user_comission = db.scalar(
        select(m.PlatformComission).where(
            m.PlatformComission.user_id == user_id,
            m.PlatformComission.job_id == job_id,
        )
    )
    if not user_comission:
        user_comission = m.PlatformComission(
            user_id=user_id,
            job_id=job_id,
            platform_payment_id=platform_payment.id,
        )
        db.add(user_comission)
        try:
            db.commit()
            db.refresh(user_comission)
        except SQLAlchemyError as e:
            log(log.ERROR, "Error while creating user comission \n[%s]", e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error while creating platform comission",
            )
    return user_comission


def create_application_payments(db: Session, application: m.Application):
    user_ids = [application.worker_id, application.owner_id]
    for user_id in user_ids:
        platform_payment = create_platform_payment(
            db=db,
            user_id=user_id,
        )
        create_platform_comission(
            db=db,
            user_id=user_id,
            job_id=application.job_id,
            platform_payment=platform_payment,
        )
    log(
        log.INFO,
        "Application payments created successfully for job - [%s]",
        application.job_id,
    )


def collect_fee(
    db: Session,
):
    ...
