from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.oauth2 import verify_access_token, INVALID_CREDENTIALS_EXCEPTION
from app.database import get_db
import app.model as m
import app.schema as s
from app.logger import log

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> m.User:
    """Raises an exception if the current user is not authenticated"""
    token: s.TokenData = verify_access_token(token, INVALID_CREDENTIALS_EXCEPTION)
    user = db.query(m.User).filter_by(id=token.user_id).first()
    if not user:
        log(log.INFO, "User wasn`t authtorized")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User wasn`t authtorized",
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
        user = db.query(m.User).filter_by(id=token.user_id).first()
        return user
    return None


def get_payplus_verified_user(
    db: Session = Depends(get_db), current_user: m.User = Depends(get_current_user)
) -> m.User:
    """Raises an exception if the current user is not authenticated in payplus"""
    if not current_user.payplus_card_uid:
        log(log.INFO, "User [%s] doesn`t have payplus customer uid", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User doesn`t have payplus customer uid",
        )
    return current_user
