import json
import httpx

from app.logger import log
from app.config import get_settings, Settings

settings: Settings = get_settings()


API_KEY = settings.PAY_PLUS_API_KEY
SECRET_KEY = settings.PAY_PLUS_SECRET_KEY
API_URL = settings.PAY_PLUS_API_URL


def pay_plus_headers(settings: Settings):
    log(log.INFO, "set pay plus headers")
    auth = {
        "api_key": settings.PAY_PLUS_API_KEY,
        "secret_key": settings.PAY_PLUS_SECRET_KEY,
    }
    auth = json.dumps(auth)
    return {
        "Content-Type": "application/json",
        "Authorization": auth,
    }


def validate_response(res: httpx.Response) -> object:
    if res.status_code != 200:
        log(log.ERROR, "response not 200")
        return
    res_data = res.json()
    result = res_data.get("results")
    data = res_data.get("data")

    if not result or not data:
        log(log.ERROR, "can't get data from response")

        if result:
            log(log.ERROR, "Status: [%s]", result.get("status"))
            log(log.ERROR, "Info: [%s]", result.get("description"))
        return
    if result.get("status") != "success":
        log(log.ERROR, "response is not success")
        return
    return data
