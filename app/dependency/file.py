from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.logger import log
from app.model.user import User
from app.model.file import File
from .user import get_current_user


def get_current_file(
    file_uuid: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file: File = db.scalars(select(File).where(File.uuid == file_uuid)).first()
    if not file:
        log(log.INFO, "File not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    if file.user.uuid != user.uuid:
        log(log.INFO, "File %s not belongs to user %", file_uuid, user.uuid)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    return file
