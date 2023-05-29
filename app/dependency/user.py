from fastapi import Depends, HTTPException, status
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
    token: s.TokenData = verify_access_token(token, INVALID_CREDENTIALS_EXCEPTION)
    user = db.query(m.User).filter_by(id=token.user_id).first()
    if not user:
        log(log.INFO, "User wasn`t authtorized")
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User wasn`t authtorized",
        )
    return user
