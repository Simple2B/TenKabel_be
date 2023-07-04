from datetime import datetime

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app import model as m
from app import schema as s
from app.config import Settings
from app.utility import pay_plus_headers
from app.logger import log


def create_payplus_customer(user: m.User, settings: Settings, db: Session) -> None:
    if user.payplus_customer_uid:
        log(
            log.INFO,
            "User [%s] payplus customer already exist - [%s]",
            user.id,
            user.payplus_customer_uid,
        )
        return
    if not user.email:
        log(log.INFO, "User [%s] has no email", user.id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Please,provide email"
        )
    if not (user.first_name or user.last_name):
        log(log.ERROR, "User [%s] has no name", user.id)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    request_data = s.PayplusCustomerIn(
        customer_name=user.first_name + (user.last_name if user.last_name else ""),
        email=user.email,
        phone=user.phone,
    )

    try:
        response = httpx.post(
            f"{settings.PAY_PLUS_API_URL}/Customers/Add",
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

    if response.status_code != status.HTTP_200_OK:
        log(log.ERROR, "Error sending request")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error sending request"
        )

    response_data = response.json()
    # TODO: pydantic
    user.payplus_customer_uid = response_data["data"]["customer_uid"]
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.ERROR, "Error post sign up user saving payplus uid \n%s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error storing user data"
        )

    log(
        log.INFO,
        "User [%s] payplus customer created and stored - [%s]",
        user.id,
        user.payplus_customer_uid,
    )


def create_payplus_token(
    card_data: s.CardIn, user: m.User, settings: Settings, db: Session
) -> None:
    if user.payplus_card_uid:
        log(log.INFO, "User [%s] payplus card already exist", user.id)
        log(log.INFO, "Continuing as card update")
        # return
    if type(card_data.card_date_mmyy) is datetime:
        iso_card_date: str = datetime.strftime(card_data.card_date_mmyy, "%m/%y")
    else:
        iso_card_date = card_data.card_date_mmyy
    request_data = s.PayplusCardIn(
        terminal_uid=settings.PAY_PLUS_TERMINAL_ID,
        customer_uid=user.payplus_customer_uid,
        credit_card_number=card_data.credit_card_number,
        card_date_mmyy=iso_card_date,
    )

    try:
        response = httpx.post(
            f"{settings.PAY_PLUS_API_URL}/Token/Add",
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

    if response.status_code != status.HTTP_200_OK:
        log(log.ERROR, "Error sending request")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error sending request"
        )

    response_data = response.json()
    # TODO: pydantic schema
    if response_data["results"]["status"] == "error":
        log(
            log.ERROR,
            "Error creating payplus card - %s"
            % response_data["results"]["description"],
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error creating payplus card - %s"
            % response_data["results"]["description"],
        )

    user.payplus_card_uid = response_data["data"]["card_uid"]
    user.card_name = card_data.card_name

    try:
        db.commit()
        db.refresh(user)
    except SQLAlchemyError as e:
        log(log.ERROR, "Error post sign up user saving payplus card uid \n%s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error storing user data"
        )

    log(
        log.INFO,
        "User [%s] payplus card uid created and stored",
        user.id,
    )


def payplus_periodic_charge(
    charge_data: s.PayPlusCharge,
    settings: Settings,
):
    try:
        httpx.post(
            f"{settings.PAY_PLUS_API_URL}/Transactions/Charge",
            headers=pay_plus_headers(settings),
            json=charge_data.dict(),
        )
    except httpx.RequestError as e:
        log(
            log.ERROR,
            "Error occured while charging for comissions:\n%s",
            e,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error occured while charging comission",
        )
