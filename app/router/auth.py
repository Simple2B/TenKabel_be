# from shutil import unregister_archive_format
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.dependency import get_current_user
from app.database import get_db
import app.model as m
import app.schema as s
from app.oauth2 import create_access_token
from app.logger import log

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/login", response_model=s.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user: m.User = m.User.authenticate_with_phone(
        db,
        user_credentials.username.strip(),
        user_credentials.password,
    )

    if not user:
        log(log.ERROR, "User [%s] was not authenticated", user_credentials.username)
        raise HTTPException(status_code=403, detail="Invalid credentials")

    access_token = create_access_token(data={"user_id": user.id})

    return s.Token(
        access_token=access_token,
        token_type="Bearer",
    )


@auth_router.post(
    "/sign-up", status_code=status.HTTP_201_CREATED, response_model=s.User
)
def sign_up(
    data: s.UserSignUp,
    db: Session = Depends(get_db),
):
    user: m.User = m.User(
        first_name=data.first_name,
        last_name=data.last_name,
        password=data.password,
        phone=data.phone,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except SQLAlchemyError as e:
        log(log.ERROR, "Error signing up user - [%s]\n%s", data.phone, e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error while signing up"
        )
    log(log.INFO, "User [%s] signed up", user.phone)
    # Creating data about user
    profession: m.Profession | None = db.scalar(
        select(m.Profession).where(m.Profession.id == data.profession_id)
    )
    if not profession:
        # add logs
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location was not found"
        )
    db.add(
        m.UserProfession(
            user_id=user.id,
            profession_id=profession.id,
        )
    )
    locations: list[m.Location] = [
        location
        for location in db.scalars(
            select(m.Location).where(m.Location.id.in_(data.locations))
        )
    ]
    for location in locations:
        db.add(m.UserLocation(user_id=user.id, location_id=location.id))
        db.flush()
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.ERROR, "Error post sign up user - [%s]\n%s", data.email, e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error storing user data"
        )
    log(log.INFO, "User [%s] COMPLETELY signed up", user.email)
    return user


@auth_router.put("/verify", status_code=status.HTTP_200_OK)
def verify(
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    current_user.is_verified = True

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.ERROR, "Error signing up user - ", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error while signing up"
        )

    log(log.INFO, "User [%s] is verified", current_user.email)

    return status.HTTP_200_OK


@auth_router.post("/google", status_code=status.HTTP_200_OK, response_model=s.Token)
def google_auth(
    data: s.GoogleAuthUser,
    db: Session = Depends(get_db),
):
    user: m.User | None = db.query(m.User).filter_by(email=data.email).first()
    password = "*"

    if not user:
        if not data.display_name:
            first_name = ""
            last_name = ""
        else:
            first_name, last_name = data.display_name.split(" ")

        user: m.User = m.User(
            email=data.email,
            first_name=first_name,
            last_name=last_name,
            username=data.email,
            google_openid_key=data.uid,
            password=password,
            is_verified=True,
        )
        db.add(user)
        try:
            db.commit()
        except SQLAlchemyError as e:
            log(log.INFO, "Error - [%s]", e)
            raise HTTPException(
                status=status.HTTP_409_CONFLICT,
                detail="Error while saving creating a user",
            )
        log(
            log.INFO,
            "User [%s] has been created (via Google account))",
            user.email,
        )
    if data.photo_url:
        user.picture = data.photo_url
    db.commit()

    user: m.User = m.User.authenticate(
        db,
        user.email,
        password,
    )

    if not user:
        log(log.ERROR, "User [%s] was not authenticated", data.username)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )

    access_token = create_access_token(data={"user_id": user.id})

    return s.Token(
        access_token=access_token,
        token_type="Bearer",
    )
