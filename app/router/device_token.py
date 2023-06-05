from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db
from app.dependency import get_current_user


device_token_router = APIRouter(prefix="/device-token", tags=["Firebase Device Token"])


@device_token_router.post("/", status_code=status.HTTP_201_CREATED)
def get_device_token_router(
    data: s.BaseDeviceToken,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    device_token = m.DeviceToken(
        user_id=current_user.id,
        token=data.token,
    )
    db.add(device_token)
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while saving device token - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error while saving device token",
        )
    log(
        log.INFO,
        "Token %s for user %s has been created successfully",
        device_token.token,
        current_user.email,
    )
    return s.BaseDeviceToken(token=device_token.token)
