# flake8: noqa
from datetime import datetime

from fastapi import status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import app.model as m
import app.schema as s
from app.logger import log
from app.utility.time_measurement import get_datetime_after_target_day_of_week


def create_platform_payment(db: Session, application: m.Application) -> None:
    # getting weekly platform payment
    # REDO
    # GET LATEST  PAID PlatformPayment - if not then create
    last_thursday = get_datetime_after_target_day_of_week(s.Weekday.THURSDAY)
    weekly_platform_payment: m.PlatformPayment = db.scalar(
        select(m.PlatformPayment).where(
            m.PlatformPayment.created_at >= last_thursday,
            m.PlatformPayment.created_at <= datetime.now(),
        )
    )
    if not weekly_platform_payment:
        log(log.INFO, "Creating weekly platform payment for upcoming week")
        weekly_platform_payment = m.PlatformPayment()
        db.add(weekly_platform_payment)
        try:
            db.commit()
            db.refresh(weekly_platform_payment)
        except SQLAlchemyError as e:
            log(log.ERROR, "Error while creating weekly platform payment - \n[%s]", e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error while creating weekly platform payment",
            )
        log(
            log.INFO,
            "Weekly platform - [%s] payment created successfully",
            weekly_platform_payment.id,
        )

        worker_comission = db.scalar(
            select(m.PlatformComission).where(
                m.PlatformComission.user_id == application.worker_id,
                m.PlatformComission.job_id == application.job_id,
            )
        )
        if not worker_comission:
            worker_comission = m.PlatformComission(
                user_id=application.worker_id,
                job_id=application.job_id,
                platform_payment_id=weekly_platform_payment.id,
            )
            db.add(worker_comission)
            try:
                db.commit()
                db.refresh(worker_comission)
            except SQLAlchemyError as e:
                log(log.ERROR, "Error while creating worker_comission \n[%s]", e)
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Error while creating weekly platform payment",
                )

        owner_comission = db.scalar(
            select(m.PlatformComission).where(
                m.PlatformComission.user_id == application.job.owner_id,
                m.PlatformComission.job_id == application.job_id,
            )
        )
        if not owner_comission:
            owner_comission = m.PlatformComission(
                user_id=application.job.owner_id,
                job_id=application.job_id,
                platform_payment_id=weekly_platform_payment.id,
            )
            db.add(owner_comission)
            try:
                db.commit()
                db.refresh(owner_comission)
            except SQLAlchemyError as e:
                log(log.ERROR, "Error while creating owner_comission \n[%s]", e)
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Error while creating weekly platform payment",
                )


def collect_fee():
    # Get all from platform payment all comissions and calculate fee

