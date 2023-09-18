from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.oauth2 import verify_access_token, INVALID_CREDENTIALS_EXCEPTION
from app.database import get_db
from app.logger import log
from app.config import get_settings, Settings
import app.model as m
import app.schema as s

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
settings: Settings = get_settings()


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> m.User:
    """Raises an exception if the current user is not authenticated"""
    token: s.TokenData = verify_access_token(token, INVALID_CREDENTIALS_EXCEPTION)
    user = db.query(m.User).filter_by(id=token.user_id).first()
    if not user:
        log(log.INFO, "User wasn`t authorized")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User wasn`t authorized",
        )
    if user.is_deleted:
        log(log.INFO, "User wasn't found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User wasn't found",
        )
    return user


def get_user(request: Request, db: Session = Depends(get_db)) -> m.User | None:
    """Raises an exception if the current user is authenticated"""
    auth_header: str = request.headers.get("Authorization")
    if auth_header:
        # Assuming the header value is in the format "Bearer <token>"
        token: s.TokenData = verify_access_token(
            auth_header.split(" ")[1], INVALID_CREDENTIALS_EXCEPTION
        )
        user = db.scalar(
            select(m.User).where(
                m.User.id == token.user_id,
                m.User.is_deleted.is_(False),
            )
        )
        return user


def get_payplus_verified_user(
    db: Session = Depends(get_db), current_user: m.User = Depends(get_current_user)
) -> m.User:
    """Raises an exception if the current user is not authenticated in payplus"""
    # Don`t check payplus if it`s disabled
    if settings.PAY_PLUS_DISABLED:
        return current_user

    if (not current_user.payplus_card_uid) or current_user.is_payment_method_invalid:
        log(log.INFO, "User [%s] doesn`t have payplus customer uid", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User doesn`t have payplus customer uid",
        )
    return current_user
