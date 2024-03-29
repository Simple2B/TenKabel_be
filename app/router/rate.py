from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db
from app.controller import create_rate_controller
from app.dependency import get_current_user


rate_router = APIRouter(prefix="/rates", tags=["Rate"])


@rate_router.get("/{rate_uuid}", status_code=status.HTTP_200_OK, response_model=s.Rate)
def get_rate(
    rate_uuid: str,
    db: Session = Depends(get_db),
):
    rate: m.Rate | None = db.scalar(select(m.Rate).where(m.Rate.uuid == rate_uuid))
    if not rate:
        log(log.INFO, "Rate [%s] wasn`t found", rate_uuid)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate not found",
        )

    log(log.INFO, "Rate [%s] info", rate_uuid)
    return rate


@rate_router.post("", status_code=status.HTTP_201_CREATED, response_model=s.Rate)
def create_rate(
    rate_data: s.BaseRate,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    rate = create_rate_controller(rate_data, db)
    return rate


@rate_router.put("/{uuid}", status_code=status.HTTP_201_CREATED, response_model=s.Rate)
def update_rate(
    uuid: str,
    rate_data: s.BaseRate,
    db: Session = Depends(get_db),
):
    rate: m.Rate | None = db.scalar(select(m.Rate).where(m.Rate.uuid == uuid))
    if not rate:
        log(log.INFO, "Rate [%s] wasn`t found ", uuid)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate not found",
        )

    owner: m.User | None = db.scalar(
        select(m.User).where(m.User.id == rate_data.owner_id)
    )
    if not owner or owner.is_deleted:
        log(log.INFO, "Owner [%s] wasn`t found ", rate_data.owner_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Owner not found",
        )

    worker: m.User | None = db.scalar(
        select(m.User).where(m.User.id == rate_data.worker_id)
    )
    if not worker or worker.is_deleted:
        log(log.INFO, "Worker [%s] wasn`t found ", rate_data.worker_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Worker not found",
        )

    rate.owner_id = rate_data.owner_id
    rate.worker_id = rate_data.worker_id
    rate.rate = s.BaseRate.RateStatus(rate_data.rate)

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while updating rate [%s] - %s", uuid, e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating rate"
        )

    log(log.INFO, "Rate [%s] updated successfully", rate.id)
    return rate


@rate_router.patch(
    "/{uuid}", status_code=status.HTTP_201_CREATED, response_model=s.Rate
)
def patch_rate(
    uuid: str,
    rate_data: s.RatePatch,
    db: Session = Depends(get_db),
):
    rate: m.Rate | None = db.scalar(select(m.Rate).where(m.Rate.uuid == uuid))
    if not rate:
        log(log.INFO, "Rate [%s] wasn`t found ", uuid)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate not found",
        )

    if rate_data.owner_id:
        owner: m.User | None = db.scalar(
            select(m.User).where(m.User.id == rate_data.owner_id)
        )
        if not owner or owner.is_deleted:
            log(log.INFO, "Owner [%s] wasn`t found ", rate_data.owner_id)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Owner not found",
            )

        rate.owner_id = rate_data.owner_id
    if rate_data.worker_id:
        worker: m.User | None = db.scalar(
            select(m.User).where(m.User.id == rate_data.worker_id)
        )
        if not worker or worker.is_deleted:
            log(log.INFO, "Worker [%s] wasn`t found ", rate_data.worker_id)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Worker not found",
            )
        rate.worker_id = rate_data.worker_id

    if rate_data.rate:
        rate.rate = s.BaseRate.RateStatus(rate_data.rate)

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while patching rate [%s] - %s", uuid, e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error patching rate"
        )

    log(log.INFO, "Rate [%s] patched successfully", rate.id)
    return rate
