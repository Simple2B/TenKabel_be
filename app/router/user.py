from fastapi import HTTPException, Depends, APIRouter, status

from sqlalchemy import select
from sqlalchemy.orm import Session

import app.model as m
import app.schema as s
from app.logger import log
from app.dependency import get_current_user
from app.database import get_db

user_router = APIRouter(prefix="/user", tags=["Users"])


@user_router.post("/", status_code=201, response_model=s.User)
def create_user(user: s.User, db: Session = Depends(get_db)):
    new_user = m.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@user_router.get("", response_model=s.User)
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    return current_user


@user_router.get("/{user_uuid}", response_model=s.User)
def get_user_profile(
    user_uuid: str,
    db: Session = Depends(get_db),
):
    user: m.User = db.scalars(select(m.User).where(m.User.uuid == user_uuid)).first()
    if not user:
        log(
            log.ERROR,
            "User %s not found",
            user_uuid,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
