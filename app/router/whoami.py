from fastapi import APIRouter, status, Depends

import app.model as m
import app.schema as s
from app.dependency import get_current_user
from app.logger import log
from app.config import get_settings, Settings


whoami_router = APIRouter(prefix="/whoami", tags=["Whoami"])

settings: Settings = get_settings()


@whoami_router.get("/user", status_code=status.HTTP_200_OK, response_model=s.WhoAmIOut)
def whoami(
    current_user: m.User = Depends(get_current_user),
    app_version: str | None = None,
):
    if app_version:
        log(
            log.INFO, "App version for user [%s]: [%s]", current_user.email, app_version
        )
    if settings.PAY_PLUS_DISABLED:
        return s.WhoAmIOut(
            uuid=current_user.uuid,
            has_payplus_card_uid=True,
            card_name=current_user.card_name or "",
            is_payment_method_invalid=False,
            is_auth_by_google=current_user.is_auth_by_google,
            is_auth_by_apple=current_user.is_auth_by_apple,
        )
    return s.WhoAmIOut(
        uuid=current_user.uuid,
        has_payplus_card_uid=bool(current_user.payplus_card_uid),
        card_name=current_user.card_name or "",
        is_payment_method_invalid=current_user.is_payment_method_invalid,
        is_auth_by_google=current_user.is_auth_by_google,
        is_auth_by_apple=current_user.is_auth_by_apple,
    )
