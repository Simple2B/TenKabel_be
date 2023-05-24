# from shutil import unregister_archive_format
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
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
    data: s.BaseUser,
    db: Session = Depends(get_db),
):
    # TODO twillio sign in
    user: m.User = m.User(
        username=data.username,
        email=data.email,
        password=data.password,
        phone=data.phone,
    )
    db.add(user)
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.ERROR, "Error signing up user - [%s]\n%s", data.email, e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error while signing up"
        )
    log(log.INFO, "User [%s] signed up", user.email)
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
    data: s.BaseUser,
    db: Session = Depends(get_db),
):
    user: m.User | None = db.query(m.User).filter_by(email=data.email).first()

    if not user:
        user: m.User = m.User(
            email=data.email,
            username=data.username,
            phone=data.phone,
            google_openid_key=data.google_openid_key,
            password=data.password,
            picture=data.picture,
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

    user.is_verified = True
    if data.picture:
        user.picture = data.picture
    db.commit()

    user: m.User = m.User.authenticate(
        db,
        data.username,
        data.password,
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
