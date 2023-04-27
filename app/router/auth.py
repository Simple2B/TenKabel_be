# from shutil import unregister_archive_format
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

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
    user: m.User = m.User.authenticate(
        db,
        user_credentials.username,
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


@auth_router.post("/sign-up", status_code=status.HTTP_201_CREATED)
def sign_up(
    data: s.BaseUser,
    db: Session = Depends(get_db),
):
    user: m.User = m.User(
        username=data.username,
        email=data.email,
        password=data.password,
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
    return status.HTTP_201_CREATED


@auth_router.post("/google-oauth", status_code=status.HTTP_200_OK)
def google_auth(
    user_data: s.BaseUserGoogle,
    db: Session = Depends(get_db),
):
    user: m.User | None = db.query(m.User).filter_by(email=user_data.email).first()
    if not user:
        username = user_data.username if user_data.username else user_data.email
        user = m.User(
            email=user_data.email,
            username=username,
            password="*",
            google_openid=user_data.google_openid,
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
            "User [%s] has been created (via Google OAuth))",
            user.email,
        )
    user.is_verified = True
    db.commit()
    user.authenticate(db, user.username, user.password)
    log(log.INFO, "Authenticating user - [%s]", user.email)
    access_token = create_access_token(data={"user_id": user.id})
    return s.Token(
        access_token=access_token,
        token_type="Bearer",
    )
