import json

from fastapi import status, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import app.model as m
import app.schema as s
from app.logger import log
from .payplus import payplus_periodic_charge


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
            log(log.ERROR, "Error while creating platform payment - \n[%s]", e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error while creating platform payment",
            )
        log(
            log.INFO,
            "Weekly platform - [%s] payment created successfully",
            unpaid_platform_payment.id,
        )
    return unpaid_platform_payment


def create_platform_commission(
    db: Session,
    platform_payment: m.PlatformPayment,
    user_id: int,
    job_id: int,
) -> m.PlatformCommission:
    user_commission = db.scalar(
        select(m.PlatformCommission).where(
            m.PlatformCommission.user_id == user_id,
            m.PlatformCommission.job_id == job_id,
        )
    )
    if not user_commission:
        user_commission = m.PlatformCommission(
            user_id=user_id,
            job_id=job_id,
            platform_payment_id=platform_payment.id,
        )
        db.add(user_commission)
        try:
            db.commit()
            db.refresh(user_commission)
        except SQLAlchemyError as e:
            log(
                log.ERROR,
                "Error while creating user [%s] commission for job [%s]:\n[%s]",
                user_id,
                job_id,
                e,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error while creating platform commission",
            )
    return user_commission


def create_application_payments(db: Session, application: m.Application):
    user_ids = [application.worker_id, application.owner_id]
    for user_id in user_ids:
        platform_payment = create_platform_payment(
            db=db,
            user_id=user_id,
        )
        create_platform_commission(
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


def collect_fee():
    from app.database import get_db
    from app.config import get_settings

    settings = get_settings()
    with get_db().__next__() as db:
        log(log.INFO, "Collecting fee")

        platform_payments: list[m.PlatformPayment] = db.scalars(
            select(m.PlatformPayment).where(
                or_(
                    m.PlatformPayment.status == s.enums.PlatformPaymentStatus.UNPAID,
                    m.PlatformPayment.status == s.enums.PlatformPaymentStatus.REJECTED,
                )
            )
        ).all()
        if not platform_payments:
            log(log.INFO, "No fee to collect")
            return

        for platform_payment in platform_payments:
            log(
                log.INFO,
                "Collecting fee for platform payment - [%s]",
                platform_payment.id,
            )
            commission_amount: list = []  # list of commission amounts
            platform_payment.status = (
                s.enums.PlatformPaymentStatus.PROGRESS
            )  # settings status to progress
            platform_commissions: list[m.PlatformCommission] = db.scalars(
                select(m.PlatformCommission).where(
                    m.PlatformCommission.platform_payment_id == platform_payment.id,
                )
            ).all()  # getting all platform comissions for this platform payment
            for pc in platform_commissions:
                commission_amount.append(
                    pc.job.payment
                    * settings.VAT_COEFFICIENT
                    * settings.COMMISSION_COEFFICIENT
                )  # calculating commission amount

            payplus_charge_data: s.PayPlusCharge = s.PayPlusCharge(
                terminal_uid=settings.PAY_PLUS_TERMINAL_ID,
                cashier_uid=settings.PAY_PLUS_CASHIERS_ID,
                amount=sum(commission_amount),
                currency_code=settings.PAYPLUS_CURRENCY_CODE,
                use_token=True,
                token=platform_payment.user.payplus_card_uid,
                more_info_1=json.dumps(
                    {"platform_payment_uuid": platform_payment.uuid}
                ),
                customer_uid=platform_payment.user.payplus_customer_uid,
            )

            payplus_periodic_charge(
                payplus_charge_data,
                platform_payment.uuid,
                db,
                settings,
            )

        log(log.INFO, "Fee collected successfully")
