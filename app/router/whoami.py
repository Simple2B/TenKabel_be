from fastapi import APIRouter, status, Depends

import app.model as m
from app.dependency import get_current_user

whoami_router = APIRouter(prefix="/whoami", tags=["Whoami"])


@whoami_router.get("/user", status_code=status.HTTP_200_OK)
def whoami(current_user: m.User = Depends(get_current_user)):
    if current_user:
        return True
    return False
