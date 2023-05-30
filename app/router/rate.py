from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db


rate_router = APIRouter(prefix="/rate", tags=["Jobs"])


@rate_router.get("/{rate_uuid}", status_code=status.HTTP_200_OK, response_model=s.Rate)
def get_rate(
    rate_uuid: str,
    db: Session = Depends(get_db),
):
    rate: m.Rate | None = db.scalar(select(m.Rate).where(m.Rate.uuid == rate_uuid))
    if not rate:
        log(log.INFO, "Rate wasn`t found %s", rate_uuid)
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate not found",
        )
    return rate


@rate_router.put("/{uuid}", status_code=status.HTTP_201_CREATED)
def update_rate(
    uuid: str,
    rate_data: s.BaseRate,
    db: Session = Depends(get_db),
):
    rate: m.Rate | None = db.scalar(select(m.Rate).where(m.Rate.uuid == uuid))
    if not rate:
        log(log.INFO, "Rate wasn`t found %s", uuid)
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate not found",
        )

    rate.owner_id = rate_data.owner_id
    rate.worker_id = rate_data.worker_id
    rate.rate = s.BaseRate.RateStatus(rate_data.rate)

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while updatin rate - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating rate"
        )

    log(log.INFO, "Rate updated successfully - %s", rate.id)
    return status.HTTP_200_OK


@rate_router.post("", status_code=status.HTTP_201_CREATED)
def create_rate(
    rate_data: s.BaseRate,
    db: Session = Depends(get_db),
):
    new_rate: m.Rate = m.Rate(
        owner_id=rate_data.owner_id,
        worker_id=rate_data.worker_id,
        rate=s.BaseRate.RateStatus(rate_data.rate),
    )

    db.add(new_rate)
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.ERROR, "Error while creating new rate - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error creating new rate"
        )

    log(log.INFO, "Rate created successfully - %s", new_rate.id)
    return status.HTTP_201_CREATED
