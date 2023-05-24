from fastapi import APIRouter, status, Depends

from app.dependency import get_current_user

whoami_router = APIRouter(prefix="/whoami", tags=["Whoami"])


@whoami_router.get("/user", status_code=status.HTTP_200_OK)
def whoami_student(current_student=Depends(get_current_user)):
    if current_student:
        return True
    return False
