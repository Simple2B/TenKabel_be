from fastapi import APIRouter, status, Depends

import app.model as m
import app.schema as s
from app.dependency import get_current_user

whoami_router = APIRouter(prefix="/whoami", tags=["Whoami"])


@whoami_router.get("/user", status_code=status.HTTP_200_OK, response_model=s.WhoAmIOut)
def whoami(current_user: m.User = Depends(get_current_user)):
    is_payplus_card_uid = False
    if current_user.payplus_card_uid:
        is_payplus_card_uid = True
    return s.WhoAmIOut(uuid=current_user.uuid, is_payplus_card_uid=is_payplus_card_uid)
