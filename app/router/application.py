from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db
from app.dependency import get_current_user


application_router = APIRouter(prefix="/application", tags=["Application"])


@application_router.post("", status_code=status.HTTP_201_CREATED)
def create_application(
    application_data: s.BaseApplication,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    ...


@application_router.put("", status_code=status.HTTP_201_CREATED)
def update_application(
    application_data: s.BaseApplication,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    ...
