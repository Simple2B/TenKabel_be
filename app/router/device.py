from fastapi import Depends, APIRouter, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.dependency import get_current_user
import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db


device_router = APIRouter(prefix="/device", tags=["Devices"])


@device_router.post("", status_code=status.HTTP_200_OK, response_model=None)
def add_device_to_user(
    device: s.DeviceIn,
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
):
    current_device = db.scalar(
        select(m.Device).where(
            and_(
                m.Device.uuid == device.uuid,
                m.Device.user_id == user.id,
            )
        )
    )

    if current_device:
        log(log.INFO, f"Device already exists for user: {user.id}")
        current_device.push_token = device.push_token
        db.commit()
        return

    db.add(
        m.Device(
            uuid=device.uuid,
            push_token=device.push_token,
            user_id=user.id,
        )
    )
    db.commit()

    log(log.INFO, f"Device added to user: {user.id}")
