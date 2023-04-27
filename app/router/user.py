import random
from fastapi import HTTPException, Depends, APIRouter, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.logger import log
import app.model as m
import app.schema as s
from app.dependency import get_current_user
from app.database import get_db

user_router = APIRouter(prefix="/user", tags=["Users"])


def generate_otp_code(user: m.User):
    # TODO integrate with UP send
    user.otp_code = "".join(random.choice("1234567890") for _ in range(4))


@user_router.post("/", status_code=201, response_model=s.User)
def create_user(user: s.User, db: Session = Depends(get_db)):
    new_user = m.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@user_router.get("/{id}", response_model=s.User)
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    user = db.query(m.User).get(id)

    if not user:
        raise HTTPException(status_code=404, detail="This user was not found")

    return user


@user_router.post("/phone-confirmation", status_code=status.HTTP_200_OK)
def update_user_phone(
    data: s.UserProfile,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):

    current_user.first_name = data.first_name
    current_user.last_name = data.last_name
    current_user.phone_number = data.phone_number
    current_user.password = data.password

    # TODO - sending SMS OTP
    generate_otp_code(current_user)
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error sending otp message - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error otp message"
        )
    log(log.INFO, "OTP CODE IS - %s", current_user.otp_code)
    return status.HTTP_200_OK


@user_router.post("/validate-otp/{otp_code}", status_code=status.HTTP_200_OK)
def validate_user_phone_number(
    otp_code: str,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    # TODO validate otp and set user as verified
    if not otp_code == current_user.otp_code:
        log(log.INFO, "OTP code %s is invalid", otp_code)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bad OTP code")
    current_user.is_verified = True

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error verifying user - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error otp message"
        )
    log(log.INFO, "User phone number verified")
    return status.HTTP_200_OK
